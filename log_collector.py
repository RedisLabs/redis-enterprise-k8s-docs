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

logger = logging.getLogger("log collector")

output_dir = ""
namespace = ""
timestr = time.strftime("%Y%m%d-%H%M%S")
dir_name = "redis_enterprise_k8s_debug_info_{}".format(timestr)

api_resources = [
    "RedisEnterpriseCluster",
    "StatefulSet",
    "Deployment",
    "Services",
    "ConfigMap",
    "Routes",
    "Ingress",
]


def run(configured_namespace, configured_output_path):
    global output_dir, namespace

    namespace = ""
    if configured_namespace:
        namespace = configured_namespace
    else:
        namespace = get_namespace_from_config()

    global timestr
    global dir_name

    if configured_output_path:
        output_dir = "{}{}{}".format(configured_output_path, "/" if configured_output_path[-1] != "/" else "", dir_name)
    else:
        output_dir = "{}/{}".format(os.path.dirname(os.path.abspath(__file__)), dir_name)

    rc, out = run_shell_command("mkdir -p {}".format(output_dir))
    if rc:
        logger.warning("Could not create output directory {} - exiting".format(out))
        sys.exit()

    get_redis_enterprise_debug_info()
    collect_cluster_info()
    collect_resources_list()
    collect_events()
    collect_api_resources()
    collect_pods_logs()
    archive_files()
    logger.info("Finished Redis Enterprise log collector")


def get_redis_enterprise_debug_info():
    """
        Connects to an RS cluster node, creates and copies debug info package from the pod
    """
    cmd = 'kubectl get pod {} --selector="redis.io/role=node" |tail -1 |cut -d " " -f1'.format(get_namespace_argument())
    rc, out = run_shell_command(cmd)
    if rc or out == "No resources found.\n":
        logger.warning(
            "Cannot find redis enterprise pod, Error: {} - Skipping collecting Redis Enterprise cluster debug info".format(
                out))
        return

    pod = out.strip("\n")

    cmd = "kubectl {} exec {} /opt/redislabs/bin/rladmin cluster debug_info path /tmp".format(
        get_namespace_argument(), pod)
    rc, out = run_shell_command(cmd)
    if "Downloading complete" not in out:
        logger.warning("Failed running rladmin command in pod: {}".format(out))
        return

    # get the debug file name
    match = re.search('File (.*\.gz)', out)
    if match:
        debug_file = match.group(1)
        logger.info("debug info created on pod {} in path {}".format(pod, debug_file))
    else:
        logger.warning(
            "Failed to extract debug info name from output - "
            "Skipping collecting Redis Enterprise cluster debug info".format(out))
        return

    # copy package from RS pod
    cmd = "kubectl {} cp {}:{} {}".format(get_namespace_argument(), pod, debug_file, output_dir)
    rc, out = run_shell_command(cmd)
    if rc:
        logger.warning(
            "Failed to debug info from pod to output directory".format(out))
        return

    logger.info("Collected Redis Enterprise cluster debug package")


def collect_resources_list():
    """
        Prints the output of kubectl get all to a file
    """
    collect_helper(cmd="kubectl get all", file_name="resources_list", resource_name="resources list")


def collect_cluster_info():
    """
        Prints the output of kubectl cluster-info to a file
    """
    collect_helper(cmd="kubectl cluster-info", file_name="cluster_info", resource_name="cluster-info")


def collect_events():
    """
        Prints the output of kubectl cluster-info to a file
    """
    global output_dir
    # events need -n parameter in kubectl
    if not namespace:
        logger.warning("Cannot collect events without namespace - skipping events collection")
        return
    cmd = "kubectl get events {}".format(get_namespace_argument())
    collect_helper(cmd=cmd, file_name="events", resource_name="events")


def collect_api_resources():
    """
        Creates file for each of the API resources with the output of kubectl get <resource> -o yaml
    """
    logger.info("Collecting API resources:")
    resources_out = OrderedDict()
    for resource in api_resources:
        output = run_kubectl_get(resource)
        if output:
            resources_out[resource] = run_kubectl_get(resource)
            logger.info("  + {}".format(resource))

    for entry, out in resources_out.iteritems():
        with open("{}/{}.yaml".format(output_dir, entry), "w+") as fp:
            fp.write(out)


def collect_pods_logs():
    """
        Collects all the pods logs from given namespace
    """
    global output_dir
    logger.info("Collecting pods' logs:")
    logs_dir = "{}/pods".format(output_dir)
    rc, out = run_shell_command("mkdir -p {}".format(logs_dir))
    if rc:
        logger.warning("Failed to create directory for pods' logs - Skipping. Output: {}".format(out))
        return

    pods = get_pods()
    if not pods:
        logger.warning("Could not get pods list - skipping pods logs collection")
        return

    for pod in pods:
        cmd = "kubectl logs {} {}".format(get_namespace_argument(), pod)
        with open("{}/{}.log".format(logs_dir, pod), "w+") as fp:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                # read one line a time - we do not want to read large files to memory
                line = p.stdout.readline()
                if line:
                    fp.write(line)
                else:
                    break
        logger.info("  + {}".format(pod))


def archive_files():
    global dir_name
    file_name = output_dir + ".tar.gz"

    with tarfile.open(file_name, "w|gz") as tar:
        tar.add(output_dir, arcname=dir_name)
    logger.info("Archived files into {}".format(file_name))

    rc, out = run_shell_command("rm -rf {}".format(output_dir))
    if rc:
        logger.warning("Failed to delete directory after archiving: {}".format(out))


def get_pods():
    """
        Returns list of pods names
    """
    cmd = "kubectl get pod {} --no-headers|cut -d \" \" -f1".format(get_namespace_argument())
    rc, out = run_shell_command(cmd)
    if rc == 0:
        return out.split("\n")[:-1]
    logger.warning("Failed to get pods: {}".format(out))


def get_namespace_argument():
    global namespace
    if namespace:
        return "-n {}".format(namespace)
    return ""


def get_namespace_from_config():
    """
        Returns the namespace from current context if one is set OW None
    """
    # find namespace from config file
    cmd = "kubectl config view -o yaml"
    rc, out = run_shell_command(cmd)
    if rc:
        return

    config = yaml.load(out)
    current_context = config.get('current-context')
    if not current_context:
        return

    for context in config.get('contexts', []):
        if context['name'] == current_context:
            if context['context'].get("namespace"):
                return context['context']["namespace"]
            break


def collect_helper(cmd, file_name, resource_name):
    """
        Runs command, write output to file_name, logs the resource_name
    """
    global output_dir
    rc, out = run_shell_command(cmd)
    if rc:
        logger.warning("Error when running {}: {}".format(cmd, out))
        return
    path = "{}/{}".format(output_dir, file_name)
    with open(path, "w+") as fp:
        fp.write(out)
    logger.info("Collected {}".format(resource_name))


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

    return 0, output


def run_kubectl_get(resource_type):
    """
        Runs kubectl get command
    """
    cmd = "kubectl get {} {} -o yaml".format(resource_type, get_namespace_argument())
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
