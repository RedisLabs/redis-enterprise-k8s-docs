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

RS_LOG_FOLDER_PATH = "/var/opt/redislabs/log"
logger = logging.getLogger(__name__)

TIME_FORMAT = time.strftime("%Y%m%d-%H%M%S")

KUBCTL_DESCRIBE_RETRIES = 3
KUBCTL_GET_YAML_RETRIES = 3
DEBUG_INFO_PACKAGE_RETRIES = 3

TIMEOUT = 180

DEFAULT_K8S_CLI = "kubectl"
OC_K8S_CLI = "oc"

API_RESOURCES = [
    "RedisEnterpriseCluster",
    "RedisEnterpriseDatabase",
    "RedisEnterpriseRemoteCluster",
    "StatefulSet",
    "Deployment",
    "Service",
    "ConfigMap",
    "Route",
    "Ingress",
    "Role",
    "RoleBinding",
    "PersistentVolume",
    "PersistentVolumeClaim",
    "Node",
    "PodDisruptionBudget",
    "ResourceQuota",
    "Endpoints",
    "Pod",
    "NetworkPolicy",
    "CustomResourceDefinition",
    "CertificateSigningRequest",
    "ValidatingWebhookConfiguration",
    "NamespacedValidatingType",
    "NamespacedValidatingRule",
    "ClusterRole",
    "ClusterRoleBinding",
    "ClusterServiceVersion",
    "Subscription",
    "InstallPlan",
    "CatalogSource",
    "PodSecurityPolicy",
    "ReplicaSet",
    "StorageClass",
]


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


def _filter_non_existing_namespaces(namespaces, k8s_cli):
    """
        Filter non-existing namespaces from user's input
    """
    return_code, out = run_shell_command(
        "{} get ns -o=custom-columns='DATA:metadata.name' --no-headers=true".format(k8s_cli))
    if return_code:
        return []
    res = []
    existing_namespaces = set(out.split())
    for namespace in namespaces:
        if namespace in existing_namespaces:
            res.append(namespace)
        else:
            logger.warning("Namespace %s doesn't exist - Skipping", namespace)
    return res


def _get_namespaces_to_run_on(namespace, k8s_cli):
    def _get_namespace_from_config():
        config_namespace = get_namespace_from_config(k8s_cli)
        if not config_namespace:
            return ["default"]
        return [config_namespace]

    if not namespace:
        return _get_namespace_from_config()

    if namespace == 'all':
        return_code, out = run_shell_command(
            "{} get ns -o=custom-columns='DATA:metadata.name' --no-headers=true".format(k8s_cli))
        if return_code:
            logger.warning("Failed to parse namespace list - will use namespace from config: %s", out)
            return _get_namespace_from_config()
        return out.split()

    # comma separated string
    namespaces = namespace.split(',')
    existing_namespaces = _filter_non_existing_namespaces(namespaces, k8s_cli)
    if not existing_namespaces:
        logger.warning("Input doesn't contain an existing namespace - will use namespace from config")
        return _get_namespace_from_config()
    return existing_namespaces


def collect_from_ns(namespace, output_dir, logs_from_all_pods=False, k8s_cli_input=""):
    "Collect the context of a specific namespace. Typically runs in parallel processes."
    k8s_cli = detect_k8s_cli(k8s_cli_input)
    logger.info("Started collecting from namespace '%s'", namespace)
    ns_output_dir = os.path.join(output_dir, namespace)
    make_dir(ns_output_dir)

    collect_connectivity_check(namespace, ns_output_dir, k8s_cli)
    get_redis_enterprise_debug_info(namespace, ns_output_dir, k8s_cli)
    collect_pod_rs_logs(namespace, ns_output_dir, k8s_cli)
    collect_resources_list(namespace, ns_output_dir, k8s_cli)
    collect_events(namespace, ns_output_dir, k8s_cli)
    collect_api_resources(namespace, ns_output_dir, k8s_cli)
    collect_api_resources_description(namespace, ns_output_dir, k8s_cli)
    collect_pods_logs(namespace, ns_output_dir, k8s_cli, logs_from_all_pods)


def detect_k8s_cli(k8s_cli_input=""):
    "Check whether the kubernetes is openshift and use oc as needed"
    if k8s_cli_input and k8s_cli_input != "auto-detect":
        logger.info("Using cli-client %s", k8s_cli_input)
        return k8s_cli_input

    # auto detect mode
    get_nodes_cmd = "{} get nodes -o json".format(DEFAULT_K8S_CLI)
    return_code, output = run_shell_command(get_nodes_cmd)
    if return_code:
        logger.info("Failed to run cmd %s", get_nodes_cmd)
        return DEFAULT_K8S_CLI

    if output:
        try:
            parsed = json.loads("".join(output))
            if "items" in parsed and len(parsed["items"]) and \
                    ("machine.openshift.io/machine" in parsed["items"][0]["metadata"]["annotations"] or
                     "node.openshift.io/os_id" in parsed["items"][0]["metadata"]["labels"]):
                # this is an openshift
                logger.info(
                    "Auto detected OpenShift, will use oc as cli tool "
                    "(this can be overriden using the --k8s_cli argument)")
                return OC_K8S_CLI
        except json.JSONDecodeError:
            logger.exception(
                "Failed to detect the relevant client for Kubernetes "
                "(failed to parse kubectl command) will keep the default")
            return DEFAULT_K8S_CLI
    return DEFAULT_K8S_CLI


def run(namespace_input, output_dir, logs_from_all_pods=False, k8s_cli_input=""):
    """
        Collect logs
    """
    start_time = time.time()
    k8s_cli = detect_k8s_cli(k8s_cli_input)
    namespaces = _get_namespaces_to_run_on(namespace_input, k8s_cli)

    output_file_name = "redis_enterprise_k8s_debug_info_{}".format(TIME_FORMAT)
    if not output_dir:
        # if not specified, use cwd
        output_dir = os.getcwd()
    output_dir = os.path.join(output_dir, output_file_name)
    make_dir(output_dir)
    collect_cluster_info(output_dir, k8s_cli)

    processes = []
    for namespace in namespaces:
        proc = Process(target=collect_from_ns, args=[namespace, output_dir, logs_from_all_pods, k8s_cli_input])
        proc.start()
        processes.append(proc)

    for proc in processes:
        proc.join()

    create_collection_report(output_dir, output_file_name, k8s_cli, namespaces, start_time)

    archive_files(output_dir, output_file_name)
    logger.info("Finished Redis Enterprise log collector")
    logger.info("--- Run time: %d minutes ---", round(((time.time() - start_time) / 60), 3))


def create_collection_report(output_dir, output_file_name, k8s_cli, namespaces, start_time):
    """
        create a file with some data about the collection
    """

    with open(os.path.join(output_dir, 'collection_report.json'), "w") as output_fh:
        json.dump({
            "output_file_name": output_file_name,
            "k8s_cli": k8s_cli,
            "namespaces": namespaces,
            "start_time": start_time
        }, output_fh)


def get_non_ready_rs_pod_names(namespace, k8s_cli):
    """
        get names of rs pods that are not ready
    """
    pod_names = []
    rs_pods = get_pods(namespace, k8s_cli, selector='redis.io/role=node')
    if not rs_pods:
        logger.info("Namespace '%s': cannot find redis enterprise pods", namespace)
        return []

    for rs_pod in rs_pods:
        pod_name = rs_pod['metadata']['name']
        if "status" in rs_pod and "containerStatuses" in rs_pod["status"]:
            for container_status_entry in rs_pod["status"]["containerStatuses"]:
                container_name = container_status_entry['name']
                is_ready = container_status_entry["ready"]
                if container_name == RLEC_CONTAINER_NAME and not is_ready:
                    pod_names.append(pod_name)

    return pod_names


def collect_pod_rs_logs(namespace, output_dir, k8s_cli):
    """
        get logs from rs pods that are not ready
    """
    rs_pod_logs_dir = os.path.join(output_dir, "rs_pod_logs")
    rs_pod_names = get_pod_names(namespace=namespace, k8s_cli=k8s_cli, selector='redis.io/role=node')
    if not rs_pod_names:
        logger.warning("Namespace '%s' Could not get rs pods list - "
                       "skipping rs pods logs collection", namespace)
        return
    make_dir(rs_pod_logs_dir)
    # TODO restore usage of get_non_ready_rs_pod_names once RS bug is resolved (RED-51857) # pylint: disable=W0511
    for rs_pod_name in rs_pod_names:
        pod_log_dir = os.path.join(rs_pod_logs_dir, rs_pod_name)
        make_dir(pod_log_dir)
        cmd = "cd \"{}\" && {} -n {} cp {}:{} ./ -c {}".format(pod_log_dir,
                                                               k8s_cli,
                                                               namespace,
                                                               rs_pod_name,
                                                               RS_LOG_FOLDER_PATH,
                                                               RLEC_CONTAINER_NAME)
        return_code, out = run_shell_command(cmd)
        if return_code:
            logger.warning("Failed to copy rs logs from pod "
                           "to output directory, output:%s", out)

        else:
            logger.info("Namespace '%s': "
                        "Collected rs logs from pod marked as not ready, pod name: %s", namespace, rs_pod_name)

        pod_config_dir = os.path.join(pod_log_dir, "config")
        make_dir(pod_config_dir)
        cmd = "cd \"{}\" && {} -n {} cp {}:{} ./ -c {}".format(pod_config_dir,
                                                               k8s_cli,
                                                               namespace,
                                                               rs_pod_name,
                                                               "/opt/redislabs/config",
                                                               RLEC_CONTAINER_NAME)
        return_code, out = run_shell_command(cmd)
        if return_code:
            logger.warning("Failed to copy rs config from pod "
                           "to output directory, output:%s", out)

        else:
            logger.info("Collected rs config from pod marked as not ready, pod name: %s", rs_pod_name)


def create_debug_info_package_on_pod(namespace, pod_name, attempt, k8s_cli):
    """
    Execute the rladmin command to get debug info on a specific pod.
    Returns: a tuple of the form (file_path, file_name) in case of success
    and None otherwise.
    """
    prog = "/opt/redislabs/bin/rladmin"
    cmd = "{} -n {} exec {} -c {} {} cluster debug_info path /tmp" \
        .format(k8s_cli, namespace, pod_name, RLEC_CONTAINER_NAME, prog)
    return_code, out = run_shell_command(cmd)
    if return_code != 0 or "Downloading complete" not in out:
        logger.warning("Failed running rladmin command in pod: %s (attempt %d)",
                       out.rstrip(), attempt)
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


def download_debug_info_package_from_pod(       # pylint: disable=R0913
    namespace, output_dir, pod_name, attempt, k8s_cli, debug_file_path, debug_file_name
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
                                                       debug_file_name)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to copy debug info from pod "
                       "to output directory (attempt %d for pod %s), output:%s",
                       attempt, pod_name, out)
        return False

    # all is well
    return True


def create_and_download_debug_info_package_from_pod(
    namespace, pod_name, output_dir, k8s_cli
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
            namespace, output_dir, pod_name, attempt + 1, k8s_cli, debug_info_path, debug_info_file_name
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


def get_redis_enterprise_debug_info(namespace, output_dir, k8s_cli):
    """
        Connects to an RS cluster node,
        creates and copies debug info package from a pod, preferably one that passes readiness probe
    """
    rs_pods = get_pods(namespace, k8s_cli, selector='redis.io/role=node')
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

    logger.info("Trying to extract debug info from RS pods: {%s}", pod_names)
    for pod_name in pod_names:
        if create_and_download_debug_info_package_from_pod(namespace, pod_name, output_dir, k8s_cli):
            break


def collect_resources_list(namespace, output_dir, k8s_cli):
    """
        Prints the output of kubectl get all to a file
    """
    collect_helper(output_dir,
                   cmd="{} get all -o wide -n {}".format(k8s_cli, namespace),
                   file_name="resources_list",
                   resource_name="resources list",
                   namespace=namespace)


def collect_cluster_info(output_dir, k8s_cli):
    """
        Prints the output of kubectl cluster-info to a file
    """
    collect_helper(output_dir, cmd="{} cluster-info".format(k8s_cli),
                   file_name="cluster_info", resource_name="cluster-info")


def collect_events(namespace, output_dir, k8s_cli):
    """
        Prints the output of kubectl cluster-info to a file
    """
    # events need -n parameter in kubectl
    if not namespace:
        logger.warning("Cannot collect events without namespace - "
                       "skipping events collection")
        return
    cmd = "{} get events -n {} -o wide".format(k8s_cli, namespace)
    collect_helper(output_dir, cmd=cmd,
                   file_name="events", resource_name="events", namespace=namespace)


def collect_api_resources(namespace, output_dir, k8s_cli):
    """
        Creates file for each of the API resources
        with the output of kubectl get <resource> -o yaml
    """
    logger.info("Namespace '%s': Collecting API resources", namespace)
    resources_out = OrderedDict()
    for resource in API_RESOURCES:
        output = run_get_resource_yaml(namespace, resource, k8s_cli)
        if output:
            resources_out[resource] = output
            logger.info("Namespace '%s':   + Collected %s", namespace, resource)
    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.yaml".format(entry)), "w+") as file_handle:
            file_handle.write(out)


def collect_api_resources_description(namespace, output_dir, k8s_cli):
    """
        Creates file for each of the API resources
        with the output of kubectl describe <resource>
    """
    logger.info("Namespace '%s': Collecting API resources description", namespace)
    resources_out = OrderedDict()
    for resource in API_RESOURCES:
        output = describe_resource(namespace, resource, k8s_cli)
        if output:
            resources_out[resource] = output
            logger.info("Namespace: '%s' + Collected %s", namespace, resource)

    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.txt".format(entry)), "w+") as file_handle:
            file_handle.write(out)


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
                   cmd="{} get all -v=6 -n {}".format(k8s_cli, namespace),
                   file_name="connectivity_check_via_k8s_cli",
                   resource_name="connectivity check via k8s cli",
                   namespace=namespace)


def archive_files(output_dir, output_dir_name):
    """
        Create a compressed tar out of the debug file collection
    """

    file_name = output_dir + ".tar.gz"

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
        selector = '--selector="{}"'.format(selector)
    cmd = '{} get pod -n {} {} -o json '.format(k8s_cli, namespace, selector)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get pods: %s", out)
        return None
    return json.loads(out)['items']


def get_list_of_containers_from_pod(namespace, pod_name, k8s_cli):
    """
        Returns list of containers from a given pod
    """
    cmd = "{} get pod {} -o jsonpath='{{.spec.containers[*].name}}' -n {}".format(k8s_cli, pod_name, namespace)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get containers from pod: %s", out)
        return None
    return out.replace("'", "").split()


def get_list_of_init_containers_from_pod(namespace, pod_name, k8s_cli):
    """
        Returns a list of init containers from a given pod.
    """
    cmd = "{} get pod {} -o jsonpath='{{.spec.initContainers[*].name}}' -n {}".format(k8s_cli, pod_name, namespace)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get init containers from pod: %s", out)
        return None
    return out.replace("'", "").split()


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
                  "w+") as file_handle:
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
            with open(container_log_before_restart_file, "w+") as file_handle:
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
    return_code, out = run_shell_command(cmd)
    if return_code:
        return None
    config = json.loads(out)
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
    with open(path, "w+") as file_handle:
        file_handle.write(out)
    logger.info("Namespace '%s': Collected %s", namespace, resource_name)


def native_string(input_var):
    """
        Decode a variable to utf-8 if it is not a string
    """
    if isinstance(input_var, str):
        return input_var

    return input_var.decode('utf-8', 'replace')


def run_get_resource_yaml(namespace, resource_type, k8s_cli):
    """
        Runs kubectl get command with yaml format
    """
    cmd = "{} get -n {} {} -o yaml".format(k8s_cli, namespace, resource_type)
    error_template = "Namespace '{}': Failed to get {} resource: {{}}.".format(namespace, resource_type)
    return run_shell_command_with_retries(cmd, KUBCTL_GET_YAML_RETRIES, error_template)


def run_shell_command_with_retries(cmd, retries, error_template):
    """
        Run a shell command, retrying up to <retries> attempts.
        When the command fails with a non-zero exit code, the output is printed
        using the provided <error_template> string ('{}'-style template).
        Repeated error messages are supressed.
    """
    prev_out = None
    for _ in range(retries):
        return_code, out = run_shell_command(cmd)
        if return_code == 0:
            return out
        if out is not None and out != prev_out:
            logger.warning(error_template.format(out.rstrip()))
        prev_out = out
    return None


def run_shell_command(args):
    """
        Run a shell command
    """
    # to allow timeouts to work in windows,
    # would need to find another mechanism that signal.alarm based
    if sys.platform == 'win32' or TIMEOUT == 0:
        return run_shell_command_regular(args)

    return run_shell_command_timeout(args)


def run_shell_command_regular(args):
    """
        Returns a tuple of the shell exit code, output
    """
    try:
        output = subprocess.check_output(args,
                                         shell=True,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        logger.warning("Failed in shell command: %s, output: %s",
                       args, ex.output)
        return ex.returncode, native_string(ex.output)

    return 0, native_string(output)


def run_shell_command_timeout(args, cwd=None, shell=True, env=None):
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
                                     stderr=subprocess.STDOUT,
                                     env=env)
    if TIMEOUT != 0:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(TIMEOUT)
    try:
        output, _ = piped_process.communicate()
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

    return piped_process.returncode, native_string(output)


def describe_resource(namespace, resource_type, k8s_cli):
    """
        Runs kubectl describe command
    """
    cmd = "{} describe -n {} {}".format(k8s_cli, namespace, resource_type)
    error_template = "Namespace '{}': Failed to describe {} resource: {{}}.".format(namespace, resource_type)
    return run_shell_command_with_retries(cmd, KUBCTL_DESCRIBE_RETRIES, error_template)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    # pylint: disable=locally-disabled, invalid-name
    parser = argparse.ArgumentParser(description='Redis Enterprise'
                                                 ' K8s log collector')

    parser.add_argument('-n', '--namespace', action="store", type=str,
                        help="pass namespace name or comma separated list or 'all' "
                             "when left empty will use namespace from kube config")
    parser.add_argument('-o', '--output_dir', action="store", type=str)
    parser.add_argument('-a', '--logs_from_all_pods', action="store_true",
                        help="collect logs from all pods, not only the operator and pods run by the operator")
    parser.add_argument('-t', '--timeout', action="store",
                        type=int, default=TIMEOUT,
                        help="time to wait for external commands to "
                             "finish execution "
                             "(default: 180s, specify 0 to not timeout) "
                             "(Linux only)")
    parser.add_argument('--k8s_cli', action="store", type=str,
                        help="Which K8s cli client to use (kubectl/oc/auto-detect). "
                             "Defaults to auto-detect (chooses between \"kubectl\" and \"oc\"). "
                             "Full paths can also be used.")

    # pylint: disable=locally-disabled, invalid-name
    results = parser.parse_args()

    # pylint: disable=locally-disabled, invalid-name
    TIMEOUT = results.timeout
    if TIMEOUT < 0:
        logger.error("timeout can't be less than 0")
        sys.exit(1)

    logger.info("Started Redis Enterprise k8s log collector")
    run(results.namespace, results.output_dir, results.logs_from_all_pods, results.k8s_cli)
