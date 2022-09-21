<!-- omit in toc -->
# Deploying Redis Enterprise on Kubernetes

* [Quick start Guide](#quickstart-guide)
  * [Installation on OpenShift](#installation-on-openshift)
* [Configuration](#configuration)
  * [RedisEnterpriseCluster custom resource](#redisenterprisecluster-custom-resource)
  * [Private Repositories](#private-repositories)
  * [Pull Secrets](#pull-secrets)
  * [Advanced Configuration](#advanced-configuration)
* [Connect to Redis Enterprise Software web console](#How-to-connect-to-Redis-Enterprise-Software-web-console?)
* [Upgrade](#upgrade)
* [Supported K8S Distributions](#supported-k8s-distributions)

This page describes how to deploy Redis Enterprise on Kubernetes using the Redis Enterprise Operator. The Redis Enterprise Operator supports two Custom Resource Definitions (CRDs):
* Redis Enterprise Cluster (REC): an API to create Redis Enterprise clusters. Note that only one cluster is supported per operator deployment.
* Redis Enterprise Database (REDB): an API to create Redis databases running on the Redis Enterprise cluster.
Note that the Redis Enterprise Operator is namespaced.
High level architecture and overview of the solution can be found [HERE](https://docs.redislabs.com/latest/platforms/kubernetes/).

## Quick start guide

This content [has moved](https://docs.redis.com/latest/kubernetes/deployment/quick-start/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).

### Installation on OpenShift

This content [has moved](https://docs.redis.com/latest/kubernetes/deployment/openshift/openshift-cli/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).

### Installation on VMWare Tanzu

 This content [has moved](https://docs.redis.com/latest/kubernetes/deployment/tanzu/) to the [Redis Enterprise docs site](https://docs.redis.com/latest/kubernetes/).
 
## Configuration

### RedisEnterpriseCluster custom resource
The operator deploys a `RedisEnterpriseCluster` with default configurations values, but those can be customized in the `RedisEnterpriseCluster` spec as follow:

Some examples [have moved](https://docs.redis.com/latest/kubernetes/reference/cluster-options/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).


* Cluster username (Default is demo@redislabs.com)
  ```yaml
  username: "admin@acme.com"
  ```

* Extra Labels: Additional labels to tag the k8s resources created during deployment
  ```yaml
    extraLabels:
      example1: "some-value"
      example2: "some-value"
  ```

* UI service type: Load Balancer or cluster IP (default)
  ```yaml
  uiServiceType: LoadBalancer
  ```

* Database service type (optional): Service types for access to databases. Should be a comma separated list. The possible values are cluster_ip, headless, and load_balancer. Default value is `cluster_ip,headless`. For example, to create a load_balancer type database service, explicitly add the following declaration to the Redis Enterprise Cluster spec:
  ```yaml
  servicesRiggerSpec:
    databaseServiceType: load_balancer
  ```

* UI annotations: Add custom annotation to the UI service
  ```yaml
    uiAnnotations:
      uiAnnotation1: 'UI-annotation1'
      uiAnnotation2: 'UI-Annotation2'
  ```

* SideCar containers: images that will run along side the redis enterprise containers
  ```yaml
    sideContainersSpec:
      - name: sidecar
        image: dockerhub_repo/repo:tag
        imagePullPolicy: IfNotPresent
  ```

* IPV4 enforcement

  You might not have IPV6 support in your K8S cluster.
  In this case, you could enforce the use of IPV4, by adding the following attribute to the REC spec:
  ```yaml
    enforceIPv4: true
  ```
  Note: Setting 'enforceIPv4' to 'true' is a requirement for running REC on PKS.

  [requirements]: https://redislabs.com/redis-enterprise-documentation/administering/designing-production/hardware-requirements/
  [service-catalog]: https://kubernetes.io/docs/concepts/extend-kubernetes/service-catalog/

* Full detail can be found in [Redis Enterprise Cluster Custom Resource Specification](redis_enterprise_cluster_api.md).

### Private Repositories

This content [has moved](https://docs.redis.com/latest/kubernetes/deployment/container-images/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).

### Pull secrets

This content [has moved](https://docs.redis.com/latest/kubernetes/deployment/container-images/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).

### Advanced Configuration

- To configure priority class, node pool, eviction thresholds and other advanced configuration see [topics.md](topics.md) file.
- Full [Redis Enterprise cluster custom resource specification](redis_enterprise_cluster_api.md)
- Full [Redis Enterprise database custom resource specification](redis_enterprise_database_api.md)


## Connect to Redis Enterprise Software web console

This content [has moved](https://docs.redis.com/latest/kubernetes/re-clusters/connect-to-admin-console/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).


## Upgrade

This content [has moved](https://docs.redis.com/latest/kubernetes/re-clusters/upgrade-redis-cluster/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).

## Supported K8S Distributions

This content [has moved](https://docs.redis.com/latest/kubernetes/reference/supported_k8s_distributions/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).