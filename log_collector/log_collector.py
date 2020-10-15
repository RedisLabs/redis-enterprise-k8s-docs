#!/usr/bin/env python

""" Redis Enterprise Cluster log collector script.
Creates a directory with output of kubectl for
several API objects and for pods logs unless pass a -n
parameter will run on current namespace. Run with -h to see options
"""

import argparse
import logging
import os
import re
import subprocess
import sys
import tarfile
import time
from collections import OrderedDict
import shutil
import json
import signal

RLEC_CONTAINER_NAME = "redis-enterprise-node"

RS_LOG_FOLDER_PATH = "/var/opt/redislabs/log"
# pylint: disable=locally-disabled, invalid-name
logger = logging.getLogger("log collector")

TIME_FORMAT = time.strftime("%Y%m%d-%H%M%S")

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


def run(namespace, output_dir):
    """
        Collect logs
    """
    if not namespace:
        namespace = get_namespace_from_config()
        if not namespace:
            namespace = "default"

    output_file_name = "redis_enterprise_k8s_debug_info_{}".format(TIME_FORMAT)

    if not output_dir:
        # if not specified, use cwd
        output_dir = os.getcwd()

    output_dir = os.path.join(output_dir, output_file_name)
    make_dir(output_dir)

    get_redis_enterprise_debug_info(namespace, output_dir)
    collect_pod_rs_logs(namespace, output_dir)
    collect_cluster_info(output_dir)
    collect_resources_list(namespace, output_dir)
    collect_events(namespace, output_dir)
    collect_api_resources(namespace, output_dir)
    collect_api_resources_description(namespace, output_dir)
    collect_pods_logs(namespace, output_dir)

    archive_files(output_dir, output_file_name)

    logger.info("Finished Redis Enterprise log collector")


def get_non_ready_rs_pod_names(namespace):
    """
        get names of rs pods that are not ready
    """
    pod_names = []
    rs_pods = get_pods(namespace, selector='redis.io/role=node')
    if not rs_pods:
        logger.warning("Cannot find redis enterprise pods")
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
    make_dir(rs_pod_logs_dir)
    non_ready_rs_pod_names = get_non_ready_rs_pod_names(namespace)
    if not non_ready_rs_pod_names:
        return
    for rs_pod_name in non_ready_rs_pod_names:
        pod_log_dir = os.path.join(rs_pod_logs_dir, rs_pod_name)
        make_dir(pod_log_dir)
        cmd = "kubectl -n {} cp {}:{} {} -c {}".format(namespace,
                                                       rs_pod_name,
                                                       RS_LOG_FOLDER_PATH,
                                                       pod_log_dir,
                                                       RLEC_CONTAINER_NAME)
        return_code, out = run_shell_command(cmd)
        if return_code:
            logger.warning("Failed to copy rs logs from pod "
                           "to output directory, output:%s", out)

        else:
            logger.info("Collected rs logs from pod marked as not ready, pod name: %s", rs_pod_name)

        pod_config_dir = os.path.join(pod_log_dir, "config")
        make_dir(pod_config_dir)
        cmd = "kubectl -n {} cp {}:{} {} -c {}".format(namespace,
                                                       rs_pod_name,
                                                       "/opt/redislabs/config",
                                                       pod_config_dir,
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
        logger.info("debug info created on pod %s in path %s",
                    pod_name, debug_file_path)
    else:
        logger.warning(
            "Failed to extract debug info name from output (attempt %d for pod %s) - (%s)",
            attempt, pod_name, out)
        return False

    # copy package from RS pod
    output_path = os.path.join(output_dir, debug_file_name)
    cmd = "kubectl -n {} cp {}:{} {}".format(namespace,
                                             pod_name,
                                             debug_file_path,
                                             output_path)
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
        logger.warning("Cannot find redis enterprise pod")
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
                logger.info("Collected Redis Enterprise cluster debug package")
                return


def collect_resources_list(namespace, output_dir):
    """
        Prints the output of kubectl get all to a file
    """
    collect_helper(output_dir,
                   cmd="kubectl get all -o wide -n {}".format(namespace),
                   file_name="resources_list",
                   resource_name="resources list")


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
                   file_name="events", resource_name="events")


def collect_api_resources(namespace, output_dir):
    """
        Creates file for each of the API resources
        with the output of kubectl get <resource> -o yaml
    """
    logger.info("Collecting API resources:")
    resources_out = OrderedDict()
    for resource in API_RESOURCES:
        output = run_kubectl_get_yaml(namespace, resource)
        if output:
            resources_out[resource] = output
            logger.info("  + %s", resource)

    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.yaml".format(entry)), "w+") as file_handle:
            file_handle.write(out)


def collect_api_resources_description(namespace, output_dir):
    """
        Creates file for each of the API resources
        with the output of kubectl describe <resource>
    """
    logger.info("Collecting API resources description:")
    resources_out = OrderedDict()
    for resource in API_RESOURCES:
        output = run_kubectl_describe(namespace, resource)
        if output:
            resources_out[resource] = output
            logger.info("  + %s", resource)

    for entry, out in resources_out.items():
        with open(os.path.join(output_dir,
                               "{}.txt".format(entry)), "w+") as file_handle:
            file_handle.write(out)


def collect_pods_logs(namespace, output_dir):
    """
        Collects all the pods logs from given namespace
    """
    logger.info("Collecting pods' logs:")
    logs_dir = os.path.join(output_dir, "pods")
    make_dir(logs_dir)

    pods = get_pod_names(namespace)
    if not pods:
        logger.warning("Could not get pods list - "
                       "skipping pods logs collection")
        return

    for pod in pods:
        cmd = "kubectl logs --all-containers=true -n  {} {}"\
            .format(namespace, pod)
        with open(os.path.join(logs_dir, "{}.log".format(pod)),
                  "w+") as file_handle:
            _, output = run_shell_command(cmd)
            file_handle.write(output)

        logger.info("  + %s", pod)


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


def get_pod_names(namespace, selector=""):
    """
        Returns list of pod names
    """
    return [pod['metadata']['name'] for pod in get_pods(namespace, selector)]


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


def collect_helper(output_dir, cmd, file_name, resource_name):
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
    logger.info("Collected %s", resource_name)


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
    logger.warning("Failed to get %s resource: %s",
                   resource_type, out.rstrip())
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
        piped_process = subprocess.Popen('ps --no-headers -o pid '
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

    piped_process = subprocess.Popen(args,
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
    logger.warning("Failed to describe %s resource: %s", resource_type, out)
    return None


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    # pylint: disable=locally-disabled, invalid-name
    parser = argparse.ArgumentParser(description='Redis Enterprise'
                                                 ' K8s log collector')

    parser.add_argument('-n', '--namespace', action="store", type=str)
    parser.add_argument('-o', '--output_dir', action="store", type=str)
    parser.add_argument('-t', '--timeout', action="store",
                        type=int, default=180,
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
