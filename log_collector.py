#!/usr/bin/env python

# Redis Enterprise Cluster log collector script.
# Creates a directory with output of kubectl for several API objects and for pods logs
# unless pass a -n parameter will run on current namespace. Run with -h to see options

import argparse
import yaml
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

logger = logging.getLogger("log collector")

TIME_FORMAT = time.strftime("%Y%m%d-%H%M%S")

api_resources = [
    "RedisEnterpriseCluster",
    "StatefulSet",
    "Deployment",
    "Services",
    "ConfigMap",
    "Routes",
    "Ingress",
]


def make_dir(directory):
    if not os.path.exists(directory):
        # noinspection PyBroadException
        try:
            os.mkdir(directory)
        except:
            logger.exception("Could not create directory %s - exiting", directory)
            sys.exit()


def run(namespace, output_dir):
    if not namespace:
        namespace = get_namespace_from_config()

    if not output_dir:
        output_dir_name = "redis_enterprise_k8s_debug_info_{}".format(TIME_FORMAT)
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_dir_name)

    make_dir(output_dir)

    get_redis_enterprise_debug_info(namespace, output_dir)
    collect_cluster_info(output_dir)
    collect_resources_list(output_dir)
    collect_events(namespace, output_dir)
    collect_api_resources(namespace, output_dir)
    collect_pods_logs(namespace, output_dir)
    archive_files(output_dir, output_dir_name)
    logger.info("Finished Redis Enterprise log collector")


def get_redis_enterprise_debug_info(namespace, output_dir):
    """
        Connects to an RS cluster node, creates and copies debug info package from the pod
    """
    pod_names = get_pod_names(namespace, selector='redis.io/role=node')
    if not pod_names:
        logger.warning("Cannot find redis enterprise pod")
        return

    pod_name = pod_names[0]

    cmd = "kubectl -n {} exec {} /opt/redislabs/bin/rladmin cluster debug_info path /tmp".format(namespace, pod_name)
    rc, out = run_shell_command(cmd)
    if "Downloading complete" not in out:
        logger.warning("Failed running rladmin command in pod: {}".format(out))
        return

    # get the debug file name
    match = re.search(r'File (/tmp/(.*\.gz))', out)
    if match:
        debug_file_path = match.group(1)
        debug_file_name = match.group(2)
        logger.info("debug info created on pod {} in path {}".format(pod_name, debug_file_path))
    else:
        logger.warning(
            "Failed to extract debug info name from output - "
            "Skipping collecting Redis Enterprise cluster debug info".format(out))
        return

    # copy package from RS pod
    output_path = os.path.join(output_dir, debug_file_name)
    cmd = "kubectl -n {} cp {}:{} {}".format(namespace, pod_name, debug_file_path, output_path)
    rc, out = run_shell_command(cmd)
    if rc:
        logger.warning(
            "Failed to debug info from pod to output directory".format(out))
        return

    logger.info("Collected Redis Enterprise cluster debug package")


def collect_resources_list(output_dir):
    """
        Prints the output of kubectl get all to a file
    """
    collect_helper(output_dir, cmd="kubectl get all", file_name="resources_list", resource_name="resources list")


def collect_cluster_info(output_dir):
    """
        Prints the output of kubectl cluster-info to a file
    """
    collect_helper(output_dir, cmd="kubectl cluster-info", file_name="cluster_info", resource_name="cluster-info")


def collect_events(namespace, output_dir):
    """
        Prints the output of kubectl cluster-info to a file
    """
    # events need -n parameter in kubectl
    if not namespace:
        logger.warning("Cannot collect events without namespace - skipping events collection")
        return
    cmd = "kubectl get events -n {}".format(namespace)
    collect_helper(output_dir, cmd=cmd, file_name="events", resource_name="events")


def collect_api_resources(namespace, output_dir):
    """
        Creates file for each of the API resources with the output of kubectl get <resource> -o yaml
    """
    logger.info("Collecting API resources:")
    resources_out = OrderedDict()
    for resource in api_resources:
        output = run_kubectl_get(namespace, resource)
        if output:
            resources_out[resource] = run_kubectl_get(namespace, resource)
            logger.info("  + {}".format(resource))

    for entry, out in resources_out.items():
        with open(os.path.join(output_dir, "{}.yaml".format(entry)), "w+") as fp:
            fp.write(out)


def collect_pods_logs(namespace, output_dir):
    """
        Collects all the pods logs from given namespace
    """
    logger.info("Collecting pods' logs:")
    logs_dir = os.path.join(output_dir, "pods")
    make_dir(logs_dir)

    pods = get_pod_names(namespace)
    if not pods:
        logger.warning("Could not get pods list - skipping pods logs collection")
        return

    for pod in pods:
        cmd = "kubectl logs -n {} {} --all-containers=true".format(namespace, pod)
        with open(os.path.join(logs_dir, "{}.log".format(pod)), "w+") as fp:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                # read one line a time - we do not want to read large files to memory
                line = native_string(p.stdout.readline())
                if line:
                    fp.write(line)
                else:
                    break
        logger.info("  + {}".format(pod))


def archive_files(output_dir, output_dir_name):
    file_name = output_dir + ".tar.gz"

    with tarfile.open(file_name, "w|gz") as tar:
        tar.add(output_dir, arcname=output_dir_name)
    logger.info("Archived files into {}".format(file_name))

    try:
        shutil.rmtree(output_dir)
    except OSError as e:
        logger.warning("Failed to delete directory after archiving: %s", e)


def get_pod_names(namespace, selector=""):
    """
        Returns list of pods names
    """
    if selector:
        selector = '--selector="{}"'.format(selector)
    cmd = 'kubectl get pod -n {} {} -o json '.format(namespace, selector)
    rc, out = run_shell_command(cmd)
    if rc:
        logger.warning("Failed to get pod names: {}".format(out))
        return
    pods_json = json.loads(out)

    return [pod['metadata']['name'] for pod in pods_json['items']]


def get_namespace_from_config():
    """
        Returns the namespace from current context if one is set OW None
    """
    # find namespace from config file
    cmd = "kubectl config view -o yaml"
    rc, out = run_shell_command(cmd)
    if rc:
        return

    config = yaml.safe_load(out)
    current_context = config.get('current-context')
    if not current_context:
        return

    for context in config.get('contexts', []):
        if context['name'] == current_context:
            if context['context'].get("namespace"):
                return context['context']["namespace"]
            break


def collect_helper(output_dir, cmd, file_name, resource_name):
    """
        Runs command, write output to file_name, logs the resource_name
    """
    rc, out = run_shell_command(cmd)
    if rc:
        logger.warning("Error when running {}: {}".format(cmd, out))
        return
    path = os.path.join(output_dir, file_name)
    with open(path, "w+") as fp:
        fp.write(out)
    logger.info("Collected {}".format(resource_name))


def native_string(x):
    return x if isinstance(x, str) else x.decode('utf-8', 'replace')


def run_shell_command(cmd):
    """
        Returns a tuple of the shell exit code, output
    """
    try:
        output = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        logger.warning("Failed in shell command: {}, output: {}".format(cmd, ex.output))
        return ex.returncode, ex.output

    return 0, native_string(output)


def run_kubectl_get(namespace, resource_type):
    """
        Runs kubectl get command
    """
    cmd = "kubectl get -n {} {} -o yaml".format(namespace, resource_type)
    rc, out = run_shell_command(cmd)
    if rc == 0:
        return out
    logger.warning("Failed to get {} resource: {}".format(resource_type, out))


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description='Redis Enterprise K8s log collector')
    parser.add_argument('-n', '--namespace', action="store", type=str)
    parser.add_argument('-o', '--output_dir', action="store", type=str)
    results = parser.parse_args()
    logger.info("Started Redis Enterprise k8s log collector")
    run(results.namespace, results.output_dir)
