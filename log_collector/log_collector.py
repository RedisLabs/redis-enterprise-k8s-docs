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
# pylint: disable=locally-disabled, invalid-name
logger = logging.getLogger("log collector")

TIME_FORMAT = time.strftime("%Y%m%d-%H%M%S")

timeout = 180

API_RESOURCES = [
    "RedisEnterpriseCluster",
    "RedisEnterpriseDatabase",
    "StatefulSet",
    "Deployment",
    "Service",
    "ConfigMap",
    "Routes",
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
    "Installplan",
    "CatalogSource"
    "PodSecurityPolicy",
    "ReplicaSet",
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


def _filter_non_existing_namespaces(namespaces):
    """
        Filter non-existing namespaces from user's input
    """
    return_code, out = run_shell_command("kubectl get ns -o=custom-columns='DATA:metadata.name' --no-headers=true")
    if return_code:
        return []
    res = []
    existing_namespaces = set(out.split())
    for ns in namespaces:
        if ns in existing_namespaces:
            res.append(ns)
        else:
            logger.warning("Namespace %s doesn't exist - Skipping", ns)
    return res


def _get_namespaces_to_run_on(namespace):
    def _get_namespace_from_config():
        config_namespace = get_namespace_from_config()
        if not config_namespace:
            return ["default"]
        return [config_namespace]

    if not namespace:
        return _get_namespace_from_config()

    if namespace == 'all':
        return_code, out = run_shell_command("kubectl get ns -o=custom-columns='DATA:metadata.name' --no-headers=true")
        if return_code:
            logger.warning("Failed to parse namespace list - will use namespace from config: %s", out)
            return _get_namespace_from_config()
        return out.split()

    # comma separated string
    namespaces = namespace.split(',')
    existing_namespaces = _filter_non_existing_namespaces(namespaces)
    if not existing_namespaces:
        logger.warning("Input doesn't contain an existing namespace - will use namespace from config")
        return _get_namespace_from_config()
    return existing_namespaces


def collect_from_ns(namespace, output_dir):
    "Collect the context of a specific namespace. Typically runs in parallel processes."
    logger.info("Started collecting from namespace '%s'", namespace)
    ns_output_dir = os.path.join(output_dir, namespace)
    make_dir(ns_output_dir)

    collect_connectivity_check(namespace, ns_output_dir)
    get_redis_enterprise_debug_info(namespace, ns_output_dir)
    collect_pod_rs_logs(namespace, ns_output_dir)
    collect_resources_list(namespace, ns_output_dir)
    collect_events(namespace, ns_output_dir)
    collect_api_resources(namespace, ns_output_dir)
    collect_api_resources_description(namespace, ns_output_dir)
    collect_pods_logs(namespace, ns_output_dir)


def run(namespace_input, output_dir):
    """
        Collect logs
    """
    start_time = time.time()
    namespaces = _get_namespaces_to_run_on(namespace_input)

    output_file_name = "redis_enterprise_k8s_debug_info_{}".format(TIME_FORMAT)
    if not output_dir:
        # if not specified, use cwd
        output_dir = os.getcwd()
    output_dir = os.path.join(output_dir, output_file_name)
    make_dir(output_dir)
    collect_cluster_info(output_dir)

    processes = []
    for namespace in namespaces:
        p = Process(target=collect_from_ns, args=[namespace, output_dir])
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    archive_files(output_dir, output_file_name)
    logger.info("Finished Redis Enterprise log collector")
    logger.info("--- Run time: %d minutes ---", round(((time.time() - start_time) / 60), 3))


def get_non_ready_rs_pod_names(namespace):
    """
        get names of rs pods that are not ready
    """
    pod_names = []
    rs_pods = get_pods(namespace, selector='redis.io/role=node')
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


def collect_pod_rs_logs(namespace, output_dir):
    """
        get logs from rs pods that are not ready
    """
    rs_pod_logs_dir = os.path.join(output_dir, "rs_pod_logs")
    rs_pod_names = get_pod_names(namespace=namespace, selector='redis.io/role=node')
    if not rs_pod_names:
        logger.warning("Namespace '%s' Could not get rs pods list - "
                       "skipping rs pods logs collection", namespace)
        return
    make_dir(rs_pod_logs_dir)
    # TODO restore usage of get_non_ready_rs_pod_names once RS bug is resolved (RED-51857) # pylint: disable=W0511
    for rs_pod_name in rs_pod_names:
        pod_log_dir = os.path.join(rs_pod_logs_dir, rs_pod_name)
        make_dir(pod_log_dir)
        cmd = "cd \"{}\" && kubectl -n {} cp {}:{} ./ -c {}".format(pod_log_dir,
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
        cmd = "cd \"{}\" && kubectl -n {} cp {}:{} ./ -c {}".format(pod_config_dir,
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


def debuginfo_attempt_on_pod(namespace, output_dir, pod_name, attempt):
    """
    Execute the rladmin command to get debug info on a specific pod
    Returns: true on success, false on failure
    """
    prog = "/opt/redislabs/bin/rladmin"
    cmd = "kubectl -n {} exec {} -c {} {} cluster debug_info path /tmp" \
        .format(namespace, pod_name, RLEC_CONTAINER_NAME, prog)
    return_code, out = run_shell_command(cmd)
    if "Downloading complete" not in out:
        logger.warning("Failed running rladmin command in pod: %s (attempt %d)",
                       out.rstrip(), attempt)
        return False

    # get the debug file name
    match = re.search(r'File (/tmp/(.*\.gz))', out)
    if match:
        debug_file_path = match.group(1)
        debug_file_name = match.group(2)
        logger.info("Namespace '%s': debug info created on pod %s in path %s",
                    namespace, pod_name, debug_file_path)
    else:
        logger.warning(
            "Failed to extract debug info name from output (attempt %d for pod %s) - (%s)",
            attempt, pod_name, out)
        return False

    # copy package from RS pod
    cmd = "cd \"{}\" && kubectl -n {} cp {}:{} ./{}".format(output_dir,
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


def get_redis_enterprise_debug_info(namespace, output_dir):
    """
        Connects to an RS cluster node,
        creates and copies debug info package from a pod, preferably one that passes readiness probe
    """
    rs_pods = get_pods(namespace, selector='redis.io/role=node')
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
        for attempt in range(3):
            if attempt > 0:
                time.sleep(1)
            if debuginfo_attempt_on_pod(namespace,
                                        output_dir,
                                        pod_name,
                                        attempt + 1):
                logger.info("Namespace '%s': Collected Redis Enterprise cluster debug package", namespace)
                return


def collect_resources_list(namespace, output_dir):
    """
        Prints the output of kubectl get all to a file
    """
    collect_helper(output_dir,
                   cmd="kubectl get all -o wide -n {}".format(namespace),
                   file_name="resources_list",
                   resource_name="resources list",
                   namespace=namespace)


def collect_cluster_info(output_dir):
    """
        Prints the output of kubectl cluster-info to a file
    """
    collect_helper(output_dir, cmd="kubectl cluster-info",
                   file_name="cluster_info", resource_name="cluster-info")


def collect_events(namespace, output_dir):
    """
        Prints the output of kubectl cluster-info to a file
    """
    # events need -n parameter in kubectl
    if not namespace:
        logger.warning("Cannot collect events without namespace - "
                       "skipping events collection")
        return
    cmd = "kubectl get events -n {} -o wide".format(namespace)
    collect_helper(output_dir, cmd=cmd,
                   file_name="events", resource_name="events", namespace=namespace)


def collect_api_resources(namespace, output_dir):
    """
        Creates file for each of the API resources
        with the output of kubectl get <resource> -o yaml
    """
    logger.info("Namespace '%s': Collecting API resources", namespace)
    resources_out = OrderedDict()
    for resource in API_RESOURCES:
        output = run_kubectl_get_yaml(namespace, resource)
        if output:
            resources_out[resource] = output
            logger.info("Namespace '%s':   + Collected %s", namespace, resource)
    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.yaml".format(entry)), "w+") as file_handle:
            file_handle.write(out)


def collect_api_resources_description(namespace, output_dir):
    """
        Creates file for each of the API resources
        with the output of kubectl describe <resource>
    """
    logger.info("Namespace '%s': Collecting API resources description", namespace)
    resources_out = OrderedDict()
    for resource in API_RESOURCES:
        output = run_kubectl_describe(namespace, resource)
        if output:
            resources_out[resource] = output
            logger.info("Namespace: '%s' + Collected %s", namespace, resource)

    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.txt".format(entry)), "w+") as file_handle:
            file_handle.write(out)


def collect_pods_logs(namespace, output_dir):
    """
        Collects all the pods logs from given namespace
    """
    logger.info("Namespace '%s': Collecting pods' logs:", namespace)
    logs_dir = os.path.join(output_dir, "pods")

    pods = get_pod_names(namespace)
    if not pods:
        logger.warning("Namespace '%s' Could not get pods list - "
                       "skipping pods logs collection", namespace)
        return

    make_dir(logs_dir)
    for pod in pods:
        containers = get_list_of_containers_from_pod(namespace, pod)
        init_containers = get_list_of_init_containers_from_pod(namespace, pod)
        containers.extend(init_containers)
        if containers is None:
            logger.warning("Namespace '%s' Could not get containers for pod: %s list - "
                           "skipping pods logs collection", namespace, pod)
            continue
        for container in containers:
            cmd = "kubectl logs -c {} -n  {} {}" \
                .format(container, namespace, pod)
            with open(os.path.join(logs_dir, "{}.log".format(f'{pod}-{container}')),
                      "w+") as file_handle:
                _, output = run_shell_command(cmd)
                file_handle.write(output)

            # operator and admission containers restart after changing the operator-environment-configmap
            # getting the logs of the containers before the restart can help us with debugging potential bugs
            get_logs_before_restart_cmd = "kubectl logs -c {} -n  {} {} -p" \
                .format(container, namespace, pod)
            with open(os.path.join(logs_dir, "{}.log".format(f'{pod}-{container}-instance-before-restart')),
                      "w+") as file_handle:
                err_code, output = run_shell_command(get_logs_before_restart_cmd)
                if err_code == 0:
                    file_handle.write(output)
                else:  # no previous container instance found; did not restart
                    os.unlink(file_handle.name)

            logger.info("Namespace '%s':  + %s-%s", namespace, pod, container)


def collect_connectivity_check(namespace, output_dir):
    """
        Collect connectivity checks to files (using certain ns).
    """
    # Verify with curl.
    if sys.platform != 'win32':
        collect_helper(output_dir,
                       cmd="APISERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}') \
                           && curl -k -v ${APISERVER}/api/",
                       file_name="connectivity_check_via_curl",
                       resource_name="connectivity check via curl")
    # Verify with kubectl.
    collect_helper(output_dir,
                   cmd="kubectl get all -v=6 -n {}".format(namespace),
                   file_name="connectivity_check_via_kubectl",
                   resource_name="connectivity check via kubectl",
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


def get_pods(namespace, selector=""):
    """
    Returns list of pods
    """
    if selector:
        selector = '--selector="{}"'.format(selector)
    cmd = 'kubectl get pod -n {} {} -o json '.format(namespace, selector)
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get pods: %s", out)
        return None
    return json.loads(out)['items']


def get_list_of_containers_from_pod(namespace, pod_name):
    """
        Returns list of containers from a given pod
    """
    cmd = f"kubectl get pod {pod_name} -o jsonpath='{{.spec.containers[*].name}}' -n {namespace}"
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get containers from pod: %s", out)
        return None
    return out.replace("'", "").split()


def get_list_of_init_containers_from_pod(namespace, pod_name):
    """
        Returns a list of init containers from a given pod.
    """
    cmd = f"kubectl get pod {pod_name} -o jsonpath='{{.spec.initContainers[*].name}}' -n {namespace}"
    return_code, out = run_shell_command(cmd)
    if return_code:
        logger.warning("Failed to get init containers from pod: %s", out)
        return None
    return out.replace("'", "").split()


def get_pod_names(namespace, selector=""):
    """
        Returns list of pod names
    """
    pods = get_pods(namespace, selector)
    if not pods:
        logger.info("Namespace '%s': Cannot find pods", namespace)
        return None
    return [pod['metadata']['name'] for pod in pods]


def get_namespace_from_config():
    """
        Returns the namespace from current context if one is set OW None
    """
    # find namespace from config file
    cmd = "kubectl config view -o json"
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


def run_kubectl_get_yaml(namespace, resource_type):
    """
        Runs kubectl get command with yaml format
    """
    cmd = "kubectl get -n {} {} -o yaml".format(namespace, resource_type)
    return_code, out = run_shell_command(cmd)
    if return_code == 0:
        return out
    logger.warning("Namespace '%s': Failed to get %s resource %s.", namespace, resource_type, out.rstrip())
    return None


def run_shell_command(args):
    """
        Run a shell command
    """
    # to allow timeouts to work in windows,
    # would need to find another mechanism that signal.alarm based
    if sys.platform == 'win32' or timeout == 0:
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
    if timeout != 0:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)
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


def run_kubectl_describe(namespace, resource_type):
    """
        Runs kubectl describe command
    """
    cmd = "kubectl describe -n {} {}".format(namespace, resource_type)
    return_code, out = run_shell_command(cmd)
    if return_code == 0:
        return out
    logger.warning("Namespace: '%s': Failed to describe %s resource: %s", namespace, resource_type, out)
    return None


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
    parser.add_argument('-t', '--timeout', action="store",
                        type=int, default=timeout,
                        help="time to wait for external commands to "
                             "finish execution "
                             "(default: 180s, specify 0 to not timeout) "
                             "(Linux only)")

    # pylint: disable=locally-disabled, invalid-name
    results = parser.parse_args()

    # pylint: disable=locally-disabled, invalid-name
    timeout = results.timeout
    if timeout < 0:
        logger.error("timeout can't be less than 0")
        sys.exit(1)

    logger.info("Started Redis Enterprise k8s log collector")
    run(results.namespace, results.output_dir)
