#!/usr/bin/env python

""" Redis Enterprise Cluster log collector script.
Creates a directory with output of kubectl for
several API objects and for pods logs unless pass a -n
parameter will run on current namespace. Run with -h to see options
"""
import argparse
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from collections import OrderedDict
from multiprocessing import Process

RLEC_CONTAINER_NAME = "redis-enterprise-node"
OPERATOR_LABEL = "app=redis-enterprise"
MODE_RESTRICTED = "restricted"
MODE_ALL = "all"
FIRST_VERSION_SUPPORTING_RESTRICTED = "6.2.18-3"
HELM = "helm"

MIN_KUBECTL_VERSION_SUPPORT_RETRIES = "1.23"
MIN_OC_VERSION_SUPPORT_RETRIES = "4.10"
DEFAULT_KUBECTL_VERSION = "1.22"
DEFAULT_OC_VERSION = "4.9"

RS_LOG_FOLDER_PATH = "/var/opt/redislabs/log"
LOGGER_OUTPUT_FILE = "output.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
LOGGER_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT)
VERSION_LOG_COLLECTOR = "7.22.0-18"

TIME_FORMAT = time.strftime("%Y%m%d-%H%M%S")

KUBCTL_DESCRIBE_RETRIES = 3
KUBCTL_GET_YAML_RETRIES = 3
DEBUG_INFO_PACKAGE_RETRIES = 3
COLLECT_RS_POD_LOGS_RETRIES = 10
HELM_RETRIES = 3

TIMEOUT = 180

KUBECTL_K8S_CLI = "kubectl"
OC_K8S_CLI = "oc"

OPERATOR_CUSTOM_RESOURCE_DEFINITION_NAMES = [
    "redisenterpriseclusters.app.redislabs.com",
    "redisenterprisedatabases.app.redislabs.com",
    "redisenterpriseremoteclusters.app.redislabs.com",
    "redisenterpriseactiveactivedatabases.app.redislabs.com"
]

# Resources that aren't created by the operator,
# and hence don't have the 'app: redis-enterprise' label.
# For these resources, we avoid using a label selector.
NON_LABELED_RESOURCES = [
    "RedisEnterpriseCluster",
    "RedisEnterpriseDatabase",
    "RedisEnterpriseRemoteCluster",
    "RedisEnterpriseActiveActiveDatabase",
    "VolumeAttachment",
    "NetworkPolicy",
]

RESTRICTED_MODE_API_RESOURCES = [
    "RedisEnterpriseCluster",
    "RedisEnterpriseDatabase",
    "RedisEnterpriseRemoteCluster",
    "RedisEnterpriseActiveActiveDatabase",
    "StatefulSet",
    "Deployment",
    "ReplicaSet",
    "Service",
    "ConfigMap",
    "Route",
    "Ingress",
    "Role",
    "RoleBinding",
    "ClusterRole",
    "ClusterRoleBinding",
    "PersistentVolume",
    "PersistentVolumeClaim",
    "PodDisruptionBudget",
    "Endpoints",
    "Pod",
    "CustomResourceDefinition",
    "ValidatingWebhookConfiguration",
    "Namespace",
    "Job",
    "NetworkPolicy",
    "CronJob"
]

OLM_RESOURCES = [
    "Role",
    "RoleBinding",
    "Service",
    "Endpoints",
]

ALL_ONLY_API_RESOURCES = [
    "Node",
    "ResourceQuota",
    "CertificateSigningRequest",
    "ClusterServiceVersion",
    "Subscription",
    "InstallPlan",
    "CatalogSource",
    "StorageClass",
    "VolumeAttachment",
    "gateways.networking.istio.io",
    "VirtualService",
]

RBAC_RESOURCES = [
    "RedisEnterpriseACL",
    "RedisEnterpriseUser",
    "RedisEnterpriseClusterRole",
    "RedisEnterpriseClusterRoleBinding",
    "RedisEnterpriseDatabaseRole",
    "RedisEnterpriseDatabaseRoleBinding",
]

SHA_DIGESTS_BEFORE_RESTRICTED_MODE_SUPPORT = [
    "0f144922ea1e2d4ea72affb36238258c9f21c39d6ba9ad73da79278dde1eed37",
    "97ffbde86f27810b1a5e6fee7ec53683f49b650cc33c327696be66d04e10bf31",
    "53b008cecf3807d51f027f21029b63dc5ad8c002c5278554ce79c008f1b97bbb",
    "b771ef87bf211c17c37df028c202aac97170fb6d7d5d49b3ccb3410deb8212f6",
    "2a033d4a4ccabb4963116add69fc8e91770ee627f6b974879d8dd7ddddebce47"
]

MISSING_RESOURCE = "no resources found in"
UNRECOGNIZED_RESOURCE = "error: the server doesn't have a resource type"
OLM_LABEL = "operators.coreos.com/redis-enterprise-operator-cert.%s"


def set_file_logger(output_dir):
    """
        add a file handler to the logger
    """
    path = os.path.join(output_dir, LOGGER_OUTPUT_FILE)
    # verify handler is not exist
    for handler in list(logger.handlers):
        try:
            if handler.__class__.__name__ == 'FileHandler':
                if handler.baseFilename == path:
                    # handler already exist - continue
                    return
        except NameError:
            continue
        except AttributeError:
            continue
    logger_file_handler = logging.FileHandler(path)
    logger_file_handler.setLevel(logging.INFO)
    logger_file_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
    logger.addHandler(logger_file_handler)


def make_dir(directory):
    """
        Create an directory if not exists
    """
    if not os.path.exists(directory):
        # noinspection PyBroadException
        try:
            os.mkdir(directory)
        except OSError as ex:
            logger.warning("Failed to create directory %s: %s", directory, ex)
            sys.exit()


def _get_namespaces_to_run_on(namespace, k8s_cli):
    if not namespace:
        config_namespace = get_namespace_from_config(k8s_cli)
        if not config_namespace:
            return ["default"]
        return [config_namespace]

    # comma separated string
    namespaces = namespace.split(',')
    return namespaces


# pylint: disable=R0913
def collect_k8s_version_info(ns_output_dir, k8s_cli):
    """
    Collects kubectl/oc version and cluster's k8s version
    """
    cmd = f"{k8s_cli} version -o yaml"
    collect_helper(ns_output_dir, cmd, "Version.yaml", "Version")


def collect_from_ns(namespace, output_dir, api_resources, logs_from_all_pods=False, k8s_cli_input="",
                    mode=MODE_RESTRICTED, skip_support_package=False, collect_empty_files=False, helm_release_name=""):
    "Collect the context of a specific namespace. Typically runs in parallel processes."
    set_file_logger(output_dir)
    k8s_cli = detect_k8s_cli(k8s_cli_input)
    k8s_cli_version = detect_k8s_cli_version(k8s_cli)
    logger.info("Started collecting from namespace '%s'", namespace)
    ns_output_dir = os.path.join(output_dir, namespace)
    make_dir(ns_output_dir)

    selector = ""
    if mode == MODE_RESTRICTED:
        selector = selector_flag(OPERATOR_LABEL)
    collect_k8s_version_info(ns_output_dir, k8s_cli)
    collect_connectivity_check(namespace, ns_output_dir, k8s_cli)
    get_redis_enterprise_debug_info(namespace, ns_output_dir, k8s_cli, mode, skip_support_package, k8s_cli_version)
    collect_pod_rs_logs(namespace, ns_output_dir, k8s_cli, mode, k8s_cli_version)
    collect_resources_list(namespace, ns_output_dir, k8s_cli, mode)
    collect_events(namespace, ns_output_dir, k8s_cli, mode)
    collect_api_resources(namespace, ns_output_dir, k8s_cli, api_resources, selector, collect_empty_files)
    collect_olm_auto_generated_resources(namespace, ns_output_dir, k8s_cli)
    collect_api_resources_description(namespace, ns_output_dir, k8s_cli, api_resources, selector, collect_empty_files)
    collect_olm_auto_generated_resources_description(namespace, ns_output_dir, k8s_cli)
    collect_pods_logs(namespace, ns_output_dir, k8s_cli, logs_from_all_pods)
    collect_helm_output(namespace, ns_output_dir, helm_release_name)


# pylint: disable=R0913
def collect_resources(namespace, output_dir, api_resources, k8s_cli_input="", selector=""):
    """
    Collect specific resources from specific namespace. Not meant to be used to collect RS pod logs.
    """
    set_file_logger(output_dir)
    k8s_cli = detect_k8s_cli(k8s_cli_input)
    ns_output_dir = os.path.join(output_dir, namespace)
    make_dir(ns_output_dir)
    collect_api_resources(namespace, ns_output_dir, k8s_cli, api_resources, selector)
    collect_api_resources_description(namespace, ns_output_dir, k8s_cli, api_resources, selector)
    collect_pods_logs(namespace, ns_output_dir, k8s_cli, logs_from_all_pods=True)


def collect_helm_output(namespace, output_dir, helm_release_name):
    """
        Collect info related to helm chart
    :param namespace: namespace to collect helm resources from
    :param output_dir: helm output directory
    :param helm_release_name: helm release name to collect its information
    :return:
    """
    if not helm_release_name:
        return
    helm_output_dir = os.path.join(output_dir, HELM)
    make_dir(helm_output_dir)

    logger.info("Namespace '%s': Collecting Helm output", namespace)

    cmd = "helm list --filter {} -n {}".format(helm_release_name, namespace)
    get_helm_output(namespace, cmd, helm_output_dir, "helm_list")

    cmd = "helm get all {} -n {}".format(helm_release_name, namespace)
    get_helm_output(namespace, cmd, helm_output_dir, "helm_all")

    cmd = "helm status {} --show-resources --show-desc -n {}".format(helm_release_name, namespace)
    get_helm_output(namespace, cmd, helm_output_dir, "helm_status")


def get_helm_output(namespace, cmd, helm_output_dir, file_name):
    """
    Get output related to helm by the release name given.
    """
    error_template = "Namespace '{}': Failed to get Helm output, command: {}.".format(namespace, cmd)
    output = run_shell_command_with_retries(cmd, HELM_RETRIES, error_template)
    if output:
        with open(os.path.join(helm_output_dir, file_name), "w+", encoding='UTF-8') as file_handle:
            file_handle.write(output)


def is_openshift(k8s_cli):
    """
    Detect whether the target cluster is OpenShift.
    The detection is based on a simple heuristic -
    whether there are any API groups with "openshift" in them.
    """
    api_versions_command = "{} api-versions".format(k8s_cli)
    return_code, output = run_shell_command(api_versions_command)
    if return_code:
        logger.info("Failed to run cmd %s", api_versions_command)
        return False

    return output is not None and "openshift" in output


def detect_k8s_cli(k8s_cli_input=""):
    """Choose k8s CLI (kubectl/oc) based on availability and target cluster"""

    if k8s_cli_input and k8s_cli_input != "auto-detect":
        logger.info("Using k8s CLI: %s", k8s_cli_input)
        return k8s_cli_input

    # auto detect mode
    has_kubectl = run_shell_command_is_success("{} help".format(KUBECTL_K8S_CLI))
    has_oc = run_shell_command_is_success("{} help".format(OC_K8S_CLI))

    # if both kubectl and oc are available, choose based on the cluster type
    if has_kubectl and has_oc:
        k8s_cli = OC_K8S_CLI if is_openshift(KUBECTL_K8S_CLI) else KUBECTL_K8S_CLI
    elif has_kubectl:
        k8s_cli = KUBECTL_K8S_CLI
    elif has_oc:
        k8s_cli = OC_K8S_CLI
    else:
        logger.error("No k8s CLI found - please install kubectl (or oc for OpenShift) and rerun")
        sys.exit(1)

    logger.info("Using k8s CLI: %s", k8s_cli)
    return k8s_cli


def detect_k8s_cli_version(k8s_cli):  # noqa: C901
    """
        detect kubectl/oc version
    """
    get_k8s_cli_version_cmd = "{} version -o json".format(k8s_cli)

    is_oc = k8s_cli.endswith(OC_K8S_CLI)
    version = DEFAULT_OC_VERSION if is_oc else DEFAULT_KUBECTL_VERSION

    return_code, output = run_shell_command(get_k8s_cli_version_cmd, include_std_err=False)

    if return_code:
        logger.warning("Failed in shell command: %s, error code: %s",
                       get_k8s_cli_version_cmd, return_code)
        return version

    if output:
        try:
            version = get_cli_version(output, is_oc)
        # pylint: disable=W0703
        except Exception:
            logger.exception("Failed to detect k8s cli version")
            return version
    return version


def parse_operator_deployment(k8s_cli, namespaces):
    """
        Compare operator version with the current log_collector version.
    """
    for namespace in namespaces:
        try:
            cmd = "{} get deployment redis-enterprise-operator -o jsonpath=" \
                  "\"{{.spec.template.spec.containers[0].image}}\" -n {}".format(k8s_cli, namespace)
            return_code, out = run_shell_command(cmd)
            if return_code or not out:
                continue

            uses_sha = "@sha256" in out

            operator_version = str.split(out, ":")
            if len(operator_version) == 2:
                logger.info("running with operator version: %s and log collector version: %s",
                            operator_version[1], VERSION_LOG_COLLECTOR)
                return operator_version[1], uses_sha
        # pylint: disable=W0703
        except Exception:
            logger.info("Failed to parse operator deployment, ignoring ns %s", namespace)
    logger.info("could not find operator version")
    return "", False


def detect_helm(k8s_cli, namespaces):
    """
        Detect if helm was used by the deployment annotations.
    """
    for namespace in namespaces:
        try:
            cmd = "{} get deployment redis-enterprise-operator -o json -n {}".format(k8s_cli, namespace)
            return_code, out = run_shell_command(cmd, include_std_err=False)
            if not return_code and out:
                parsed = try_load_json("".join(out))
                if parsed and "meta.helm.sh/release-name" in parsed["metadata"]["annotations"]:
                    release_name = parsed["metadata"]["annotations"]["meta.helm.sh/release-name"]
                    logger.info("detected operator was installed using helm. Helm release name is %s", release_name)
                    return release_name
        # pylint: disable=W0703
        except Exception:
            logger.info("Failed to detect if helm was used, ignoring ns %s", namespace)
    return ""


def validate_mode(mode, operator_tag, is_sha_digest):
    """
       for old versions there is no way to use restricted because resources are missing labels
    """
    version_supports_restricted = check_if_tag_supports_restricted(operator_tag, is_sha_digest)
    if mode == MODE_RESTRICTED and not version_supports_restricted:
        raise ValueError("{} is not supported for this version, please use {}".format(MODE_RESTRICTED, MODE_ALL))


def is_old_sha(operator_tag):
    """
    Check if the sha of the operator is older than the first that supports restricted
    Note - we only started using digests recently so there is no need to list all of them
    """
    return operator_tag in SHA_DIGESTS_BEFORE_RESTRICTED_MODE_SUPPORT


def check_if_tag_supports_restricted(operator_tag, is_sha_digest):
    """
    Handle both sha tags and versions and check if they support restricted
    """
    version_supports_restricted = True
    if is_sha_digest:
        if is_old_sha(operator_tag):
            version_supports_restricted = False
    else:
        version_supports_restricted = check_if_version_supports_restricted(operator_tag)
    return version_supports_restricted


def check_if_version_supports_restricted(operator_version):
    """
    Compare the version to 6.2.18-3 which is the first version supporting restricted
    Note - apparently there is no function in Python that is built in and supports that
    """
    try:
        the_version = operator_version.split("-")[0]

        parts = the_version.split(".")
        if int(parts[0]) < 6:
            return False
        if int(parts[0]) >= 7:
            return True
        if int(parts[1]) > 2:
            return True
        if int(parts[1]) < 2:
            return False
        return int(parts[2]) >= 18
    # pylint: disable=W0703
    except Exception:
        logger.info("issues parsing version %s", operator_version)
        return True


def compare_versions(current_version, supported_version):
    """
    Compare between the current version and the version that is supported
    check if the current version is supported (current >= supported)
    the versions convention is x.y
    """
    try:
        current = current_version.split(".")
        supported = supported_version.split(".")

        if int(current[0]) < int(supported[0]):
            return False
        if int(current[0]) > int(supported[0]):
            return True
        return int(current[1]) >= int(supported[1])
    # pylint: disable=W0703
    except Exception:
        logger.info("issues parsing version")
        return False


def determine_default_mode(operator_tag, is_sha_digest):
    """
    determine the default mode based on the version/sha digest
    """
    version_supports_restricted = check_if_tag_supports_restricted(operator_tag, is_sha_digest)
    if operator_tag == "" or version_supports_restricted:
        return MODE_RESTRICTED

    return MODE_ALL


def run(results):
    """
        Collect logs
    """
    output_file_name = "redis_enterprise_k8s_debug_info_{}".format(TIME_FORMAT)
    output_dir = results.output_dir
    if not output_dir:
        output_dir = os.getcwd()
    output_dir = os.path.join(output_dir, output_file_name)
    make_dir(output_dir)

    with open(os.path.join(output_dir, LOGGER_OUTPUT_FILE), "x"):
        logger.info("Created %s file in %s", LOGGER_OUTPUT_FILE, output_dir)

    set_file_logger(output_dir)
    logger.info("Started Redis Enterprise k8s log collector")
    start_time = time.time()
    k8s_cli = detect_k8s_cli(results.k8s_cli)

    namespaces = _get_namespaces_to_run_on(results.namespace, k8s_cli)

    # pylint: disable=global-statement, invalid-name
    global TIMEOUT
    # pylint: disable=locally-disabled, invalid-name
    TIMEOUT = results.timeout

    mode = results.mode
    operator_tag, is_sha_digest = parse_operator_deployment(k8s_cli, namespaces)
    if mode:
        validate_mode(mode, operator_tag, is_sha_digest)
    else:
        mode = determine_default_mode(operator_tag, is_sha_digest)

    helm_release_name = results.helm_release_name or detect_helm(k8s_cli, namespaces)

    api_resources = RESTRICTED_MODE_API_RESOURCES
    if mode == MODE_ALL:
        api_resources = api_resources + ALL_ONLY_API_RESOURCES

    collect_rbac = results.collect_rbac_resources
    if collect_rbac:
        api_resources = api_resources + RBAC_RESOURCES

    processes = []
    for namespace in namespaces:
        proc = Process(target=collect_from_ns,
                       args=[namespace, output_dir, api_resources, results.logs_from_all_pods,
                             k8s_cli, mode, results.skip_support_package, results.collect_empty_files,
                             helm_release_name])
        proc.start()
        processes.append(proc)

    if results.collect_istio:
        proc = Process(
            target=collect_resources,
            args=["istio-system", output_dir, ["Pod", "Service", "ConfigMap", "Deployment", "ReplicaSet"]]
        )
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()

    create_collection_report(output_dir, output_file_name, k8s_cli, namespaces, start_time, mode)

    archive_files(output_dir, output_file_name)
    logger.info("Finished Redis Enterprise log collector")
    logger.info("--- Run time: %d minutes ---", round(((time.time() - start_time) / 60), 3))


def create_collection_report(output_dir, output_file_name, k8s_cli, namespaces, start_time, mode):
    """
        create a file with some data about the collection
    """

    with open(os.path.join(output_dir, 'collection_report.json'), "w") as output_fh:
        json.dump({
            "output_file_name": output_file_name,
            "k8s_cli": k8s_cli,
            "namespaces": namespaces,
            "start_time": start_time,
            "mode": mode,
            "log_collector_version": VERSION_LOG_COLLECTOR
        }, output_fh)


def get_selector(mode):
    """
        selector of rs pods
    """
    selector = 'redis.io/role=node'
    if mode == MODE_RESTRICTED:
        selector = '{},{}'.format(selector, OPERATOR_LABEL)
    return selector


def collect_pod_rs_logs(namespace, output_dir, k8s_cli, mode, k8s_cli_version):
    """
    Collect logs from Redis Enterprise pods
    """
    rs_pod_logs_dir = os.path.join(output_dir, "rs_pod_logs")
    selector = get_selector(mode)
    rs_pod_names = get_pod_names(namespace=namespace, k8s_cli=k8s_cli, selector=selector)
    if not rs_pod_names:
        logger.warning("Namespace '%s' Could not get rs pods list - "
                       "skipping rs pods logs collection", namespace)
        return
    make_dir(rs_pod_logs_dir)
    for rs_pod_name in rs_pod_names:
        pod_log_dir = os.path.join(rs_pod_logs_dir, rs_pod_name)
        make_dir(pod_log_dir)
        cmd = "cd \"{}\" && {} -n {} cp {}:{} ./ -c {}".format(pod_log_dir,
                                                               k8s_cli,
                                                               namespace,
                                                               rs_pod_name,
                                                               RS_LOG_FOLDER_PATH,
                                                               RLEC_CONTAINER_NAME)
        cmd = add_retries_if_supported(cmd, k8s_cli_version, k8s_cli)
        return_code, out = run_shell_command(cmd)
        if return_code:
            logger.warning("Failed to copy rs logs from pod '%s' to output directory, output: %s",
                           rs_pod_name, out)
        else:
            logger.info("Namespace '%s': Collected rs logs from pod: %s", namespace, rs_pod_name)

        pod_config_dir = os.path.join(pod_log_dir, "config")
        make_dir(pod_config_dir)
        cmd = "cd \"{}\" && {} -n {} cp {}:{} ./ -c {}".format(pod_config_dir,
                                                               k8s_cli,
                                                               namespace,
                                                               rs_pod_name,
                                                               "/opt/redislabs/config",
                                                               RLEC_CONTAINER_NAME)
        cmd = add_retries_if_supported(cmd, k8s_cli_version, k8s_cli)
        return_code, out = run_shell_command(cmd)
        if return_code:
            logger.warning("Failed to copy rs config from pod '%s' to output directory, output: %s",
                           rs_pod_name, out)
        else:
            logger.info("Namespace '%s': Collected rs config from pod: %s", namespace, rs_pod_name)


def create_debug_info_package_on_pod(namespace, pod_name, attempt, k8s_cli):
    """
    Execute the rladmin command to get debug info on a specific pod.
    Returns: a tuple of the form (file_path, file_name) in case of success
    and None otherwise.
    """
    prog = "/opt/redislabs/bin/rladmin"
    cmd = "{} -n {} exec {} -c {} -- {} cluster debug_info path /tmp" \
        .format(k8s_cli, namespace, pod_name, RLEC_CONTAINER_NAME, prog)
    return_code, out = run_shell_command(cmd)
    if return_code != 0 or "Downloading complete" not in out:
        logger.warning("Failed to collect debug_info from pod: %s. (Attempt %d) "
                       "If the issue persists, consider using the --skip_support_package flag "
                       "to skip collecting the debug info package.", pod_name, attempt)
        return None

    # get the debug file name
    match = re.search(r'File (/tmp/(.*\.gz))', out)
    if match:
        debug_file_path = match.group(1)
        debug_file_name = match.group(2)
        logger.info("Namespace '%s': debug info created on pod %s in path %s",
                    namespace, pod_name, debug_file_path)
        return (debug_file_path, debug_file_name)

    logger.warning(
        "Failed to extract debug info name from output (attempt %d for pod %s) - (%s)",
        attempt, pod_name, out)
    return None


def download_debug_info_package_from_pod(  # pylint: disable=R0913
        namespace, output_dir, pod_name, attempt, k8s_cli, debug_file_path, debug_file_name, k8s_cli_version
):
    """
    This function attempt to download debug info package from a given pod.
    It should only be called once the package is created.
    """
    cmd = "cd \"{}\" && {} -n {} cp {}:{} ./{}".format(output_dir,
                                                       k8s_cli,
                                                       namespace,
                                                       pod_name,
                                                       debug_file_path,
                                                       debug_file_name,
                                                       )
    cmd = add_retries_if_supported(cmd, k8s_cli_version, k8s_cli, attempt)

    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.info("Unable to copy debug info from pod %s"
                    "to output directory, output: %s \n Retrying from different pod",
                    pod_name, out)
        return False

    # all is well
    return True


def get_min_cli_version_supporting_retries(k8s_cli):
    """
    Get the minimum kubectl/oc version which supports the '--retries' flag
    """
    return MIN_OC_VERSION_SUPPORT_RETRIES if (k8s_cli and k8s_cli.endswith(OC_K8S_CLI)) \
        else MIN_KUBECTL_VERSION_SUPPORT_RETRIES


def add_retries_if_supported(cmd, k8s_cli_version, k8s_cli, attempt=COLLECT_RS_POD_LOGS_RETRIES):
    """
    Add the '--retries' flag to the command if the kubectl/oc version supports it
    """
    if compare_versions(k8s_cli_version, get_min_cli_version_supporting_retries(k8s_cli)):
        cmd = "{} --retries={}".format(cmd, attempt)
    return cmd


def get_cli_version(output, is_oc):
    """
        Get the client version from the version output command
    """
    parsed = try_load_json("".join(output))
    if is_oc:
        client_version = parsed['releaseClientVersion']
        logger.info("OC Client Version: %s", client_version)
        return client_version
    major = parsed['clientVersion']['major']
    minor = parsed['clientVersion']['minor']
    client_version = "{}.{}".format(major, minor)
    logger.info("Kubectl version found: %s", client_version)
    return client_version


def create_and_download_debug_info_package_from_pod(
        namespace, pod_name, output_dir, k8s_cli, k8s_cli_version
):
    """
    This function attempts to create a debug info package on a pod and if debug
    info package creation was successful, attempts downloading it.
    """
    debug_info_path_and_name = None
    for attempt in range(DEBUG_INFO_PACKAGE_RETRIES):
        debug_info_path_and_name = create_debug_info_package_on_pod(namespace, pod_name, attempt + 1, k8s_cli)
        if debug_info_path_and_name is not None:
            # We managed to create the debug info package.
            break
        time.sleep(1)

    # If we fail creating a debug info package, there is nothing to download, so we move on to the next pod.
    if debug_info_path_and_name is None:
        logger.info("Namespace: %s: Failed creating debug info package on pod: %s", namespace, pod_name)
        return False

    (debug_info_path, debug_info_file_name) = debug_info_path_and_name
    for attempt in range(DEBUG_INFO_PACKAGE_RETRIES):
        if download_debug_info_package_from_pod(
                namespace, output_dir, pod_name, attempt + 1, k8s_cli, debug_info_path, debug_info_file_name,
                k8s_cli_version
        ):
            logger.info(
                "Namespace '%s': Collected Redis Enterprise cluster debug package from pod: %s",
                namespace,
                pod_name
            )
            return True
        time.sleep(1)

    # In case of a failure to fully download the archive from the pod. Make sure that partially downloaded
    # archive is deleted.
    file_to_delete = "{}/{}".format(output_dir, debug_info_file_name)
    logger.info(
        "Namespace: %s: Deleting possible partially downloaded debug package: %s",
        namespace,
        file_to_delete
    )
    cmd = "rm {}".format(file_to_delete)
    run_shell_command(cmd)
    return False


def get_redis_enterprise_debug_info(namespace, output_dir, k8s_cli, mode, skip_support_package, k8s_cli_version):
    """
        Connects to an RS cluster node,
        creates and copies debug info package from a pod, preferably one that passes readiness probe
    """
    selector = get_selector(mode)
    rs_pods = get_pods(namespace, k8s_cli, selector=selector)
    if not rs_pods:
        logger.info("Namespace '%s': Cannot find redis enterprise pod", namespace)
        return

    pod_names = []
    for pod in rs_pods:
        if 'containerStatuses' in pod['status'] and all(
                container_status['ready'] for container_status in pod['status']['containerStatuses']):
            pod_names.append(pod['metadata']['name'])
    if not pod_names:
        logger.warning("Cannot find a ready redis enterprise pod, will use a non-ready pod")
        pod_names = [pod['metadata']['name'] for pod in rs_pods]

    if not skip_support_package:
        logger.info("Trying to extract debug info from RS pods: {%s}", pod_names)
        for pod_name in pod_names:
            if create_and_download_debug_info_package_from_pod(namespace, pod_name, output_dir,
                                                               k8s_cli, k8s_cli_version):
                break


def collect_resources_list(namespace, output_dir, k8s_cli, mode):
    """
        Prints the output of kubectl get all to a file
    """
    selector = ""
    if mode == MODE_RESTRICTED:
        selector = selector_flag(OPERATOR_LABEL)
    collect_helper(output_dir,
                   cmd=f"{k8s_cli} get pod,service,deployment,replicaset,statefulset -o wide -n {namespace} {selector}",
                   file_name="resources_list",
                   resource_name="resources list",
                   namespace=namespace)


def collect_events(namespace, output_dir, k8s_cli, mode=MODE_RESTRICTED):
    """
        Prints the output of kubectl get events -o wide and
        kubectl get event -o yaml
    """
    if mode != MODE_ALL:
        logger.warning('Cannot collect events in "restricted" mode - skipping events collection')
        return
    # events need -n parameter in kubectl
    if not namespace:
        logger.warning("Cannot collect events without namespace - "
                       "skipping events collection")
        return
    cmd = "{} get events -n {} -o wide".format(k8s_cli, namespace)
    collect_helper(output_dir, cmd=cmd,
                   file_name="events", resource_name="events", namespace=namespace)

    # We get the events in YAML format as well since in YAML format they are a bit more informative.
    output = run_get_resource_yaml(namespace, "Event", k8s_cli)
    with open(os.path.join(output_dir, "Event.yaml"), "w+", encoding='UTF-8') as file_handle:
        file_handle.write(output)


def check_empty_yaml_file(out):
    """
    given an output of kubectl get command in yaml format, checks whether the items list is empty
    """
    for line in out.split("\n"):
        if line.startswith("items"):
            return line.split(":")[1].strip() == '[]'
    return False


def detect_if_olm_deployed(namespace, k8s_cli):
    """
    detect if operator was deployed using OLM
    """
    cmd = f"{k8s_cli} get operators/redis-enterprise-operator-cert.{namespace} -n {namespace}"
    code, _ = run_shell_command(cmd)
    return code == 0


def collect_olm_auto_generated_resources(namespace, ns_output_dir, k8s_cli):
    """
        Creates file for each of the OLM autogenerated resources and aggregate them in their own folder
        with the output of kubectl get <resource> -o yaml
    """
    if not detect_if_olm_deployed(namespace, k8s_cli):
        return
    olm_output_dir = os.path.join(ns_output_dir, "OLM")
    make_dir(olm_output_dir)
    selector = f"--selector={OLM_LABEL % namespace}"
    logger.info("Namespace '%s': Collecting OLM autogenerated resources", namespace)
    resources_out = OrderedDict()
    for resource in OLM_RESOURCES:
        output = run_get_resource_yaml(namespace, resource, k8s_cli, selector)
        if output:
            resources_out[resource] = output
            log_resource_collected(namespace, resource)
    for entry, out in resources_out.items():
        with open(os.path.join(olm_output_dir,
                               "{}.yaml".format(entry)), "w+", encoding='UTF-8') as file_handle:
            file_handle.write(out)


def collect_olm_auto_generated_resources_description(namespace, ns_output_dir, k8s_cli):
    """
        Creates file for each of the OLM autogenerated resources and aggregate them in their own folder
        with the output of kubectl get <resource> -o yaml
    """
    if not detect_if_olm_deployed(namespace, k8s_cli):
        return
    olm_output_dir = os.path.join(ns_output_dir, "OLM")
    make_dir(olm_output_dir)
    selector = f"--selector={OLM_LABEL % namespace}"
    logger.info("Namespace '%s': Collecting OLM autogenerated resources description", namespace)
    resources_out = OrderedDict()
    for resource in OLM_RESOURCES:
        output = describe_resource(namespace, resource, k8s_cli, selector)
        if output:
            resources_out[resource] = output
            log_resource_collected(namespace, resource)
    for entry, out in resources_out.items():
        with open(os.path.join(olm_output_dir,
                               "{}.txt".format(entry)), "w+", encoding='UTF-8') as file_handle:
            file_handle.write(out)


def collect_api_resources(namespace, output_dir, k8s_cli, api_resources, selector="", collect_empty_files=False):
    """
        Creates file for each of the API resources
        with the output of kubectl get <resource> -o yaml
    """
    logger.info("Namespace '%s': Collecting API resources", namespace)
    resources_out = OrderedDict()
    message = f"Namespace '{namespace}': No resources of type %s are found" if not selector else \
        f"Namespace '{namespace}': no {extract_label(selector)} labeled resources of type %s are found"

    message = f"{message}, skip collecting empty log file"
    for resource in api_resources:
        if resource == "Namespace":
            output = run_get_resource_yaml(namespace, resource, k8s_cli,
                                           resource_names=[namespace])
        elif resource == "CustomResourceDefinition":
            output = run_get_resource_yaml(namespace, resource, k8s_cli,
                                           resource_names=OPERATOR_CUSTOM_RESOURCE_DEFINITION_NAMES)
        # We use this fully qualified resource kind to avoid potential clashes with Gateway API if it’s installed
        elif resource == "gateways.networking.istio.io":
            output = run_get_resource_yaml(namespace, resource, k8s_cli)
            resource = "Gateways"
        elif resource in NON_LABELED_RESOURCES:
            output = run_get_resource_yaml(namespace, resource, k8s_cli)
        else:
            output = run_get_resource_yaml(namespace, resource, k8s_cli, selector)
        if output:
            if check_empty_yaml_file(output) and not collect_empty_files:
                logger.info(message, resource)
            else:
                resources_out[resource] = output
                log_resource_collected(namespace, resource)
    if selector:
        # collect PV resource
        collect_persistent_volume(namespace, k8s_cli, resources_out, "get", KUBCTL_GET_YAML_RETRIES)
    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.yaml".format(entry)), "w+", encoding='UTF-8') as file_handle:
            file_handle.write(out)


def check_empty_desc_file(out):
    """
    check if output of kubectl describe resource is empty
    """
    return MISSING_RESOURCE in out.lower()


def extract_label(selector):
    """given a selector, extract the label itself"""
    return selector.split('=')[-1][:-1]


def collect_api_resources_description(namespace, output_dir, k8s_cli, api_resources, selector="",
                                      collect_empty_files=False):
    """
        Creates file for each of the API resources
        with the output of kubectl describe <resource>
    """
    logger.info("Namespace '%s': Collecting API resources description", namespace)
    resources_out = OrderedDict()
    message = f"Namespace '{namespace}': No resources of type %s are found" if not selector else \
        f"Namespace '{namespace}': no {extract_label(selector)} labeled resources of type %s are found"

    message = f"{message}, skip collecting empty log file"
    for resource in api_resources:
        if resource == "Namespace":
            output = describe_resource(namespace, resource, k8s_cli,
                                       resource_names=[namespace])
        elif resource == "CustomResourceDefinition":
            output = describe_resource(namespace, resource, k8s_cli,
                                       resource_names=OPERATOR_CUSTOM_RESOURCE_DEFINITION_NAMES)
        elif resource == "gateways.networking.istio.io":
            output = describe_resource(namespace, resource, k8s_cli)
            resource = "Gateways"
        elif resource in NON_LABELED_RESOURCES:
            output = describe_resource(namespace, resource, k8s_cli)
        else:
            output = describe_resource(namespace, resource, k8s_cli, selector)
        if output:
            if check_empty_desc_file(output) and not collect_empty_files:
                logger.info(message, resource)
            else:
                resources_out[resource] = output
                log_resource_collected(namespace, resource)
    if selector:
        # collect PV resource
        collect_persistent_volume_description(namespace, k8s_cli, resources_out, KUBCTL_DESCRIBE_RETRIES)
    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.txt".format(entry)), "w+", encoding='UTF-8') as file_handle:
            file_handle.write(out)


def collect_persistent_volume(namespace, k8s_cli, resources_out, collect_func, retries):
    """
        Collect PersistentVolume resource
        get volumes names of the PersistentVolumeClaim with operator label
    """
    resource = "PersistentVolume"
    output = collect_pv_by_pvc_names(namespace, k8s_cli, collect_func, retries)
    if output:
        resources_out["PersistentVolume"] = output
        log_resource_collected(namespace, resource)


def collect_persistent_volume_description(namespace, k8s_cli, resources_out, retries):
    """
        Collect PersistentVolume resource
        get volumes names of the PersistentVolumeClaim with operator label
    """
    resource = "PersistentVolume"
    output = collect_pv_by_pvc_name_description(namespace, k8s_cli, retries)
    if output:
        resources_out["PersistentVolume"] = output
        log_resource_collected(namespace, resource)


def get_pv_names(k8s_cli, namespace, error_template):
    """
        get volumes names from the PersistentVolumeClaim
    """
    cmd = "{} get -n {} PersistentVolumeClaim --selector={} -o=custom-columns=VOLUME:.spec.volumeName --no-headers" \
        .format(k8s_cli, namespace, OPERATOR_LABEL)
    missing_resource_template = f"Namespace '{namespace}': Skip collecting information for PersistentVolumeClaim. " \
                                f"Server has no resource of type PersistentVolumeClaim"
    output = run_shell_command_with_retries(cmd, KUBCTL_GET_YAML_RETRIES, error_template, missing_resource_template)
    return output.split()


def collect_pv_by_pvc_names(namespace, k8s_cli, collect_func, retries):
    """
        Collect PersistentVolume resource (get/describe - collect_func) when use restricted mode
    """
    pv_output = ""
    error_template = failed_to_get_resource_error(namespace, "PersistentVolumeClaim")
    volumes_names = get_pv_names(k8s_cli, namespace, error_template)
    for volume in volumes_names:
        if volume == "<none>":
            logger.info('skipping nameless pvc')
            continue
        cmd = "{} {} -n {} {} --field-selector=metadata.name={} -o yaml".format(k8s_cli, collect_func,
                                                                                namespace,
                                                                                "PersistentVolume",
                                                                                volume)
        missing_resource_template = f"Namespace '{namespace}': Skip collecting information for" \
                                    f" PersistentVolume - {volume}. " \
                                    f"Server has no resource of type PersistentVolume - {volume}"
        output = run_shell_command_with_retries(cmd, retries, error_template, missing_resource_template)
        pv_output = pv_output + output
    return pv_output


def collect_pv_by_pvc_name_description(namespace, k8s_cli, retries):
    """
        Collect PersistentVolume resource description
    """
    pv_output = ""
    error_template = failed_to_get_resource_error(namespace, "PersistentVolumeClaim")
    volumes_names = get_pv_names(k8s_cli, namespace, error_template)
    for volume in volumes_names:
        if volume == "<none>":
            logger.info('skipping nameless pvc')
            continue
        # get the PV name and then run with describe
        cmd = "{} get -n {} {} --field-selector=metadata.name={} -o=name".format(k8s_cli, namespace, "PersistentVolume",
                                                                                 volume)
        missing_resource_template = f"Namespace '{namespace}': Skip collecting information for PersistentVolume - " \
                                    f"{volume}. Server has no resource of type PersistentVolume - {volume}"
        pv_name = run_shell_command_with_retries(cmd, retries, error_template, missing_resource_template)
        cmd = "{} describe -n {} {}".format(k8s_cli, namespace, pv_name)
        missing_resource_template = f"Namespace '{namespace}': Skip collecting description for PersistentVolume - " \
                                    f"{volume}. Server has no resource of type PersistentVolume - {volume}"
        output = run_shell_command_with_retries(cmd, retries, error_template, missing_resource_template)
        pv_output = pv_output + output
    return pv_output


def collect_pods_logs(namespace, output_dir, k8s_cli, logs_from_all_pods=False):
    """
        Collects all the pods logs from given namespace
    """
    logger.info("Namespace '%s': Collecting pods' logs:", namespace)
    logs_dir = os.path.join(output_dir, "pods")

    if logs_from_all_pods:
        pods = get_pod_names(namespace, k8s_cli)
    else:
        pods = []
        for selector in ["app=redis-enterprise", "name=redis-enterprise-operator"]:
            pods.extend(get_pod_names(namespace, k8s_cli, selector))

    if not pods:
        logger.warning("Namespace '%s' Could not get pods list - "
                       "skipping pods logs collection", namespace)
        return

    make_dir(logs_dir)

    for pod in pods:
        collect_logs_from_pod(namespace, pod, logs_dir, k8s_cli)


def collect_connectivity_check(namespace, output_dir, k8s_cli):
    """
        Collect connectivity checks to files (using certain ns).
    """
    # Verify with curl.
    if sys.platform != 'win32':
        cmd = "{} config view --minify -o ".format(k8s_cli) + "jsonpath='{.clusters[0].cluster.server}'"
        _, api_server = run_shell_command(cmd)
        if api_server:
            collect_helper(output_dir,
                           cmd="curl -k -v {}/api/".format(api_server),
                           file_name="connectivity_check_via_curl",
                           resource_name="connectivity check via curl")
    # Verify with kubectl.
    collect_helper(output_dir,
                   cmd=f"{k8s_cli} version --v=9",
                   file_name="connectivity_check_via_k8s_cli",
                   resource_name="connectivity check via k8s cli",
                   namespace=namespace)


def archive_files(output_dir, output_dir_name):
    """
        Create a compressed tar out of the debug file collection
    """

    file_name = output_dir + ".tar.gz"

    logger.info("Archiving files into %s", file_name)
    with tarfile.open(file_name, "w|gz") as tar:
        tar.add(output_dir, arcname=output_dir_name)
    logger.info("Archived files into %s", file_name)

    try:
        shutil.rmtree(output_dir)
    except OSError as ex:
        logger.warning("Failed to delete directory after archiving: %s", ex)


def get_pods(namespace, k8s_cli, selector=""):
    """
    Returns list of pods
    """
    if selector:
        selector = selector_flag(selector)
    cmd = '{} get pod -n {} {} -o json '.format(k8s_cli, namespace, selector)
    return_code, out = run_shell_command(cmd, include_std_err=False)
    if return_code:
        logger.warning("Failed to get pods: %s", out)
        return None

    loaded_json = try_load_json(out)
    items_key = 'items'

    if not loaded_json or items_key not in loaded_json:
        logger.warning("Failed to get pods - no items key in json: %s", out)
        return None

    return loaded_json[items_key]


def get_list_of_containers_from_pod(namespace, pod_name, k8s_cli):
    """
        Returns list of containers from a given pod
    """
    cmd = "{} get pod {} -o jsonpath=\"{{.spec.containers[*].name}}\" -n {}".format(k8s_cli, pod_name, namespace)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get containers from pod: %s", out)
        return None
    return out.split()


def get_list_of_init_containers_from_pod(namespace, pod_name, k8s_cli):
    """
        Returns a list of init containers from a given pod.
    """
    cmd = "{} get pod {} -o jsonpath=\"{{.spec.initContainers[*].name}}\" -n {}".format(k8s_cli, pod_name, namespace)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get init containers from pod: %s", out)
        return None
    return out.split()


def collect_logs_from_pod(namespace, pod, logs_dir, k8s_cli):
    """
        Helper function getting logs of a pod
    """
    containers = get_list_of_containers_from_pod(namespace, pod, k8s_cli)
    init_containers = get_list_of_init_containers_from_pod(namespace, pod, k8s_cli)
    containers.extend(init_containers)
    if containers is None:
        logger.warning("Namespace '%s' Could not get containers for pod: %s list - "
                       "skipping pods logs collection", namespace, pod)
        return
    for container in containers:
        cmd = "{} logs -c {} -n  {} {}" \
            .format(k8s_cli, container, namespace, pod)
        with open(os.path.join(logs_dir, "{}-{}.log".format(pod, container)),
                  "w+", encoding='UTF-8') as file_handle:
            _, output = run_shell_command(cmd)
            file_handle.write(output)

        # operator and admission containers restart after changing the operator-environment-configmap
        # getting the logs of the containers before the restart can help us with debugging potential bugs
        get_logs_before_restart_cmd = "{} logs -c {} -n  {} {} -p" \
            .format(k8s_cli, container, namespace, pod)
        err_code, output = run_shell_command(get_logs_before_restart_cmd)
        container_log_before_restart_file = os.path.join(logs_dir,
                                                         '{}-{}-instance-before-restart.log'.format(pod, container))
        if err_code == 0:  # Previous container instance found; did restart.
            with open(container_log_before_restart_file, "w+", encoding='UTF-8') as file_handle:
                file_handle.write(output)

            logger.info("Namespace '%s':  + %s-%s", namespace, pod, container)


def get_pod_names(namespace, k8s_cli, selector=""):
    """
        Returns list of pod names
    """
    pods = get_pods(namespace, k8s_cli, selector)
    if not pods:
        logger.info("Namespace '%s': Cannot find pods", namespace)
        return []
    return [pod['metadata']['name'] for pod in pods]


def get_namespace_from_config(k8s_cli):
    """
        Returns the namespace from current context if one is set OW None
    """
    # find namespace from config file
    cmd = "{} config view -o json".format(k8s_cli)
    return_code, out = run_shell_command(cmd, include_std_err=False)
    if return_code:
        return None

    config = try_load_json(out)
    if not config:
        return None

    current_context = config.get('current-context')
    if not current_context:
        return None

    for context in config.get('contexts', []):
        if context['name'] == current_context:
            if context['context'].get("namespace"):
                return context['context']["namespace"]
            break
    return None


def collect_helper(output_dir, cmd, file_name, resource_name, namespace=None):
    """
        Runs command, write output to file_name, logs the resource_name
    """
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Error when running %s: %s", cmd, out)
        return
    path = os.path.join(output_dir, file_name)
    with open(path, "w+", encoding='UTF-8') as file_handle:
        file_handle.write(out)
    log_resource_collected(namespace, resource_name)


def native_string(input_var):
    """
        Decode a variable to utf-8 if it is not a string
    """
    if isinstance(input_var, str):
        return input_var

    return input_var.decode('utf-8', 'replace')


def run_get_resource_yaml(namespace, resource_type, k8s_cli, selector="", resource_names=None):
    """
        Runs kubectl get command with yaml format
    """
    resource_name_args = " ".join(resource_names) if resource_names else ""
    cmd = "{} get -n {} {} {} {} -o yaml".format(k8s_cli, namespace, resource_type, resource_name_args, selector)
    error_template = failed_to_get_resource_error(namespace, resource_type)
    missing_resource_template = f"Namespace '{namespace}': Skip collecting information for {resource_type}. " \
                                f"Server has no resource of type {resource_type}"
    return run_shell_command_with_retries(cmd, KUBCTL_GET_YAML_RETRIES, error_template, missing_resource_template)


def handle_unsuccessful_cmd(out, error_template, missing_resource_template):
    """
    function to choose whether to log in info or in warning according to output
    """
    if MISSING_RESOURCE in out.lower() or UNRECOGNIZED_RESOURCE in out.lower():
        logger.info(missing_resource_template)
    else:
        logger.warning(error_template.format(out.rstrip()))


def run_shell_command_is_success(args):
    """
        Run a shell command, and returns whether the execution was successful (exit code 0).
    """
    return_code, _ = run_shell_command(args)
    return return_code == 0


def run_shell_command_with_retries(args, retries, error_template, missing_resource_template=""):
    """
        Run a shell command, retrying up to <retries> attempts.
        When the command fails with a non-zero exit code, the output is printed
        using the provided <error_template> string ('{}'-style template).
        Repeated error messages are supressed.
    """
    prev_out = None
    for _ in range(retries):
        return_code, out = run_shell_command(args)
        if return_code == 0:
            return out
        if out is not None and out != prev_out:
            handle_unsuccessful_cmd(out, error_template, missing_resource_template)
        prev_out = out
    return None


def run_shell_command(args, include_std_err=True):
    """
        Run a shell command
    """
    logger.info("Running shell command: %s", args)

    # to allow timeouts to work in windows,
    # would need to find another mechanism that signal.alarm based
    if sys.platform == 'win32' or TIMEOUT == 0:
        return run_shell_command_regular(args, include_std_err)

    return run_shell_command_timeout(args, include_std_err=include_std_err)


def run_shell_command_regular(args, include_std_err=True):
    """
        Returns a tuple of the shell exit code, output
    """
    err_output = None
    try:
        piped_process = subprocess.Popen(args,  # pylint: disable=R1732
                                         shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT if include_std_err else subprocess.PIPE)
        output, err_output = piped_process.communicate()
    except subprocess.CalledProcessError as ex:
        logger.warning("Failed in shell command: %s, output: %s",
                       args, ex.output)
        return ex.returncode, native_string(ex.output)
    finally:
        if not include_std_err and err_output:
            logger.warning("stderr output: %s", native_string(err_output))

    return 0, native_string(output)


def run_shell_command_timeout(args, cwd=None, shell=True, env=None, include_std_err=True):
    """
        Utility function to run a shell command with a timeout
    """

    def get_process_children(parent):
        piped_process = subprocess.Popen('ps --no-headers -o pid '  # pylint: disable=R1732
                                         '--ppid %d' % parent,
                                         shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        stdout, _ = piped_process.communicate()
        return [int(proc) for proc in stdout.split()]

    # no need for pass here:
    # https://github.com/PyCQA/pylint/issues/2616#issuecomment-442738701
    # do not remove the doc string - code would break
    class Alarm(Exception):
        """
            Custom alarm exception
        """

    def alarm_handler(_, __):
        raise Alarm

    piped_process = subprocess.Popen(args,  # pylint: disable=R1732
                                     shell=shell,
                                     cwd=cwd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT if include_std_err else subprocess.PIPE,
                                     env=env)
    if TIMEOUT != 0:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(TIMEOUT)
    try:
        output, err_output = piped_process.communicate()
        # disable alarm after process returns
        signal.alarm(0)
    except Alarm:
        logger.warning("cmd: %s timed out", args)
        pids = [piped_process.pid]
        pids.extend(get_process_children(piped_process.pid))
        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        return -9, "cmd: %s timed out" % args

    if not include_std_err and err_output:
        logger.warning("stderr output: %s", native_string(err_output))

    return piped_process.returncode, native_string(output)


def describe_resource(namespace, resource_type, k8s_cli, selector="", resource_names=None):
    """
        Runs kubectl describe command
    """
    resource_name_args = " ".join(resource_names) if resource_names else ""
    cmd = "{} describe -n {} {} {} {}".format(k8s_cli, namespace, resource_type, resource_name_args, selector)
    error_template = failed_to_get_resource_error(namespace, resource_type)
    missing_resource_template = f"Namespace '{namespace}': Skip collecting description for {resource_type}. " \
                                f"Server has no resource of type {resource_type}"
    return run_shell_command_with_retries(cmd, KUBCTL_GET_YAML_RETRIES, error_template, missing_resource_template)


def check_not_negative(value):
    """
        Validate a numeric option is not negative
    """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s can't be less than 0" % value)
    return ivalue


def log_resource_collected(namespace, resource):
    """
    Helper function to log that a resource was collected
    """
    logger.info("Namespace '%s': Collected %s", namespace, resource)


def failed_to_get_resource_error(namespace, resource):
    """
    Helper function to log failure in getting a resource
    """
    return "Namespace '{}': Failed to get resource: {}.".format(namespace, resource)


def selector_flag(selector):
    """
    Helper function to format a selector for kubectl/oc
    """
    return '--selector={}'.format(selector)


def try_load_json(json_str):
    """
    Try to load a string as json
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        logger.error("Failed to load string as json: %s", json_str)

    return None


if __name__ == "__main__":
    # pylint: disable=locally-disabled, invalid-name
    parser = argparse.ArgumentParser(description='Redis Enterprise Log Collector for Kubernetes\n\n'
                                                 'For additional details and usage instructions, see '
                                                 'https://redis.io/docs/latest/operate/kubernetes/logs/collect-logs/',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-n', '--namespace', action="store", type=str,
                        help="Sets the namespace(s) to collect from.\n"
                             "Can be set to a single namespace, or multiple namespaces (comma-separated).\n"
                             "When left empty, will use the current context's namespace from kubeconfig.")
    parser.add_argument('-o', '--output_dir', action="store", type=str,
                        help="Sets the output directory.\n"
                             "Defaults to current working directory.")
    parser.add_argument('-a', '--logs_from_all_pods', action="store_true",
                        help="Collect logs from all pods in the selected namespace(s),\n"
                             "and otherwise collect only from the operator and pods run by the operator.")
    parser.add_argument('-t', '--timeout', action="store",
                        type=check_not_negative, default=TIMEOUT,
                        help="Time to wait for external commands to finish execution (Linux only).\n"
                             "Default to 180s. Specify 0 to disable timeout.")
    parser.add_argument('--k8s_cli', action="store", type=str,
                        help="The K8s cli client to use (kubectl/oc/auto-detect).\n"
                             "Defaults to auto-detect (chooses between 'kubectl' and 'oc').\n"
                             "Full paths can also be used.")
    parser.add_argument('-m', '--mode', action="store", type=str,
                        choices=[MODE_RESTRICTED, MODE_ALL],
                        help="Controls which resources are collected:\n"
                             "In 'restricted' mode, only resources associated with the operator "
                             "and have the label 'app=redis-enterprise' are collected.\n"
                             "In 'all' mode, all resources are collected.\n"
                             "Defaults to 'restricted' mode.")
    parser.add_argument('--collect_istio', action="store_true",
                        help="Collect data from istio-system namespace to debug potential\n"
                             "problems related to istio ingress method.")
    parser.add_argument('--skip_support_package', action="store_true",
                        help="Disable collection of RS support package from Redis Enterprise nodes.")
    parser.add_argument('--collect_empty_files', action="store_true",
                        help='Collect empty log files for missing resources.')
    parser.add_argument('--helm_release_name', action="store", type=str,
                        help='Collect resources related to the given Helm release name.')
    # Notice! This configuration is temporary once RBAC API is fully implemented and released,
    # the log collector will collect RBAC API resources by default.
    parser.add_argument('--collect_rbac_resources', action="store_true",
                        help='Temporary development flag. '
                             'Collect all role based access control related custom resources.')
    parser.set_defaults(collect_istio=False, collect_rbac_resources=False)
    run(parser.parse_args())
