# Redis Enterprise Operator Helm Chart

Official Helm chart for installing, configuring and upgrading **Redis Enterprise Operator for Kubernetes**.

[Redis Enterprise](https://redis.com/redis-enterprise-software/overview/) is a self-managed data platform that unlocks the full potential of Redis at enterprise scale - on premises or in the cloud.  
[Redis Enterprise Operator for Kubernetes](https://redis.com/redis-enterprise-software/redis-enterprise-on-kubernetes/) provides a simple, Kubernetes-native way for deploying and managing Redis Enterprise on Kubernetes.

## Prerequisites

- Kubernetes 1.23+  
  Supported Kubernetes versions can vary according to the Kubernetes distribution being used.  
  Please consult the [release notes](https://docs.redis.com/latest/kubernetes/release-notes/) for detailed supported distributions information per operator version.
- Helm 3.10+

## Installing the Chart

To install the chart:

```sh
helm install [RELEASE_NAME] [PATH_TO_CHART]
```

The `[PATH_TO_CHART]` may be a path to the chart root directory, or a chart archive on the local filesystem.  
  
To install the chart on **OpenShift**, set the `isOpenshift=true` value:

```sh
helm install [RELEASE_NAME] [PATH_TO_CHART] \
     --set isOpenshift=true
```

To create and select a namespace for the installation, specify the `--namespace` and `--create-namespace` flags:

```sh
helm install [RELEASE_NAME] [PATH_TO_CHART] \
     --namespace [NAMESPACE] \
     --create-namespace
```

For example, to install the chart with release name "my-redis-enterprise" from within the chart's root directory:

```sh
helm install my-redis-enterprise . \
     --namespace redis-enterprise \
     --create-namespace
```

Note: the chart installation includes several jobs that configure the CRDs and admission controller used by the operator.  
These jobs run synchronously during the execution of `helm install` command, and may take around 1 minute to complete.  
To view additional progress information during the `helm install` execution, use the `--debug` flag:

```sh
helm install [RELEASE_NAME] [PATH_TO_CHART] \
     --debug
```

See [Configuration](#configuration) section below for various configuration options.  
See [Creating a Redis Enterprise Cluster](#creating-a-redis-enterprise-cluster) section below for instructions for creating a Redis Enterprise Cluster.  
See [helm install](https://helm.sh/docs/helm/helm_install/) and [Using Helm](https://helm.sh/docs/intro/using_helm/#helm-install-installing-a-package) for more information and options when installing charts.

## Uninstalling the Chart

Before uninstalling the chart, delete any custom resources managed by the Redis Enterprise Operator:

```sh
kubectl delete redb <name>
kubectl delete rerc <name>
kubectl delete reaadb <name>
kubectl delete rec <name>
```

To uninstall a previously installed chart:

```sh
helm uninstall [RELEASE_NAME]
```

This removes all the Kubernetes resources associated with the chart and deletes the release.

See [helm uninstall](https://helm.sh/docs/helm/helm_uninstall/) for more information and options when uninstalling charts.

## Creating a Redis Enterprise Cluster

Once the chart is installed and the Redis Enterprise Operator is running, a Redis Enterprise Cluster can be created.  
As of now, the Redis Enterprise Cluster is created directly via custom resources, and not via Helm.

To create a Redis Enterprise Cluster:

1. Validate that the `redis-enterprise-operator` pod is in `RUNNING` state:

```sh
kubectl get pods -n [NAMESPACE]
```

2. Create a file for the `RedisEnterpriseCluster` custom resource:

```yaml
apiVersion: app.redislabs.com/v1
kind: RedisEnterpriseCluster
metadata:
  name: rec
spec:
  nodes: 3
```

3. Apply the custom resource:

```sh
kubectl apply -f rec.yaml -n [NAMESPACE]
```

See [Create a Redis Enterprise cluster](https://docs.redis.com/latest/kubernetes/deployment/quick-start/#create-a-redis-enterprise-cluster-rec) and [Redis Enterprise Cluster API](https://github.com/RedisLabs/redis-enterprise-k8s-docs/blob/master/redis_enterprise_cluster_api.md) for more information and options for creating a Redis Enterprise Cluster.

## Configuration

The chart supports several configuration options that allows to customize the behavior and capabilities of the Redis Enterprise Operator.  
For a list of configurable options and their descriptions, please refer to the `values.yaml` file at the root of the chart.

To install the chart with a customized values file:

```sh
helm install [RELEASE_NAME] [PATH_TO_CHART] \
     --values [PATH_TO_VALUES_FILE]
```

To install the chart with the default values files but with some specific values overriden:

```sh
helm install [RELEASE_NAME] [PATH_TO_CHART] \
     --set key1=value1 \
     --set key2=value2
```

See [Customizing the Chart Before Installing](https://helm.sh/docs/intro/using_helm/#customizing-the-chart-before-installing) for additional information on how to customize the chart installation.

## Known Limitations

This is a preliminary release of this Helm chart, and as of now some if its functionality is still limited:

- The chart only installs the Redis Enterprise Operator, but doesn't create a Redis Enterprise Cluster. See [Creating a Redis Enterprise Cluster](#creating-a-redis-enterprise-cluster) section for instructions on how to directly create a Redis Enterprise Cluster.
- Several configuration options for the operator are still unsupported, including multiple REDB namespaces, rack-aware, and vault integration. These options can be enabled by following the relevant instructions in the [product documentation](https://docs.redis.com/latest/kubernetes/).
- CRDs installed by the chart are not removed upon chart uninstallation. These could be manually removed when the chart is uninstalled and are no longer needed, using the following command:
  ```sh
  kubectl delete crds -l app=redis-enterprise
  ```
- Helm chart upgrades are not supported, nor migrations from a non-Helm deployment to a Helm deployment.
- Limited testing in advanced setups such as Active-Active configurations, airgapped deployments, IPv6/dual-stack environments.
- The chart is still unpublished in a "helm repo" or ArtifactHub, and thus can only be installed from a local source (chart directory/archive).
- While not really a limitation, please note that this chart also installs the [admission controller](https://docs.redis.com/latest/kubernetes/deployment/quick-start/#enable-the-admission-controller) by default, and there's no option to disable it (as opposed to the non-Helm deployment).