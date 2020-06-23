<!-- omit in toc -->
# Deploying Redis Enterprise on Kubernetes

* [Quickstart Guide](#quickstart-guide)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
  * [Installation on OpenShift](#installation-on-openshift)
* [Configuration](#configuration)
  * [RedisEnterpriseCluster custom resource](#redisenterprisecluster-custom-resource)
  * [Private Repositories](#private-repositories)
  * [Pull Secrets](#pull-secrets)
  * [Advanced Configuration](#advanced-configuration)
* [Upgrade](#upgrade)

This page describe how to deploy Redis Enterprise on Kubernetes using the Redis Enterprise Operator. High level architecture and overview of the solution can be found [HERE](https://docs.redislabs.com/latest/platforms/kubernetes/).

## Quickstart Guide

### Prerequisites

- A Kubernetes cluster version of 1.11 or higher, with a minimum of 3 worker nodes.
- A Kubernetes client (kubectl) with a matching version. For OpenShift, an OpenShift client (oc).
- Access to DockerHub, RedHat Container Catalog or a private repository that can serve the required images.


The following are the images and tags for this release:
| Component | k8s | Openshift |
| --- | --- | --- |
| Redis Enterprise | `redislabs/redis:6.0.6-35` | `redislabs/redis:6.0.6-35.rhel7-openshift` |
| Operator | `redislabs/operator:6.0.6-5` | `redislabs/operator:6.0.6-5.rhel7` |
| Services Rigger | `redislabs/k8s-controller:6.0.6-5` | `redislabs/k8s-controller:6.0.6-5.rhel7` |
> * RedHat certified images are available on [Redhat Catalog](https://access.redhat.com/containers/#/product/71f6d1bb3408bd0d) </br>


### Installation
The "Basic" installation deploys the operator (from the current release) with the default Ubuntu/Alpine base OS images from DockerHub and default settings.
This is the fastest way to get up and running with a new Redis Enterprise on Kubernetes.

1. Create a new namespace:

    ```bash
    kubectl create namespace demo
    ```

    Switch context to the newly created namespace:

    ```bash
    kubectl config set-context --current --namespace=demo
    ```

2. Deploy the operator bundle

   To deploy the default installation with `kubectl`, the following command will deploy a bundle of all the yaml declarations required for the operator:

    ```bash
    kubectl apply -f bundle.yaml
    ```

    Alternatively, to run each of the declarations of the bundle individually, run the following commands *instead* of the bundle:

    ```bash
    kubectl apply -f role.yaml
    kubectl apply -f role_binding.yaml
    kubectl apply -f service_account.yaml
    kubectl apply -f crds/app_v1_redisenterprisecluster_crd.yaml
    kubectl apply -f crds/app_v1alpha1_redisenterprisedatabase_crd.yaml
    kubectl apply -f operator.yaml
    ```
    > Note: The rbac.yaml file used in previous releases has been broken down into three distinct files:
    `role.yaml`, `role_binding.yaml` and `service_account.yaml`.
    The `crd.yaml` file was renamed to `redisenterprisecluster_crd.yaml`, with the API version prepended to the filename.
    Apply the `crds/app_v1alpha1_redisenterprisedatabase_crd.yaml` if managing database instances through Kubernetes API and commands is desired.

3. Run `kubectl get deployment` and verify redis-enterprise-operator deployment is running.

    A typical response may look like this:

    ```bash
    NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
    redis-enterprise-operator          1/1     1            1           2m
    ```

4. Redis Enterprise Cluster custom resource - `RedisEnterpriseCluster`

   Create a `RedisEnterpriseCluster`(REC) using the default configuration, which is suitable for development type deployments and works in typical scenarios. For more advanced deployment options you may choose the configuration relevant for you - see the index at the top for documentation references that cover many scenarios and the examples in the example folder.

    ```bash
    kubectl apply -f crds/app_v1_redisenterprisecluster_cr.yaml
    ```

    > Note: The redis-enterprise-cluster.yaml file was renamed to redisenterprisecluster_cr.yaml, with the API version prepended to the filename.

5. Run ```kubectl get rec``` and verify creation was successful. `rec` is a shortcut for RedisEnterpriseCluster.
    A typical response may look like this:
    ```
    NAME               AGE
    redis-enterprise   5m
    ```

6. Redis Enterprise Database custom resource - `RedisEnterpriseDatabase` 

   Create a `RedisEnterpriseDatabase` (REDB) by using Custom Resource.
   The Redis Enterprise Operator can be instructed to manage databases on the Redis Enterprise Cluster using the REDB custom resource.
    Example:
    ```yaml
    cat << EOF > /tmp/redis-enterprise-database.yml
    apiVersion: app.redislabs.com/v1alpha1
    kind: RedisEnterpriseDatabase
    metadata:
      name: redis-enterprise-database
    spec:
      redisEnterpriseCluster:
        name: redis-enterprise
      memorySize: 100MB
    EOF
    kubectl apply -f /tmp/redis-enterprise-database.yml
    ```
    Replace the name of the cluster with the one used on the current namespace.
    All REDB configuration options are documented [here](redis_enterprise_database_api.md).


   > Optional: REDB admission controller
   >
   > When using the REDB Custom Resource Definition (Redis Enterprise Database) it is recommended to set up admission control to improve input validation and catch configuration errors before they reach the cluster. The procedure is documented [here](admission/README.md)



### Installation on OpenShift

The "OpenShift" installations deploys the operator from the current release with the RHEL image from DockerHub and default OpenShift settings.
This is the fastest way to get up and running with a new cluster on OpenShift 3.x.
For OpenShift 4.x, you may choose to use OLM deployment from within your OpenShift cluster or follow the steps below.
Other custom configurations are referenced in this repository.
> Note: you will need to replace `<my-project>` with your project name

1. Create a new project:

    ```bash
    oc new-project my-project
    ```

2. Perform the following commands (you need cluster admin permissions for your Kubernetes cluster):

    ```bash
    oc apply -f openshift/scc.yaml
    ```

    You should receive the following response:
    `securitycontextconstraints.security.openshift.io "redis-enterprise-scc" configured`

3. Provide the operator permissions for pods (substitute your project for "my-project"):

    ```bash
    oc adm policy add-scc-to-group redis-enterprise-scc system:serviceaccounts:my-project
    ```

4. Deploy the OpenShift operator bundle:
    > NOTE: Update the `storageClassName` setting in `openshift.bundle.yaml` (by default its set to `gp2`).

    ```bash
    oc apply -f openshift.bundle.yaml
    ``` 

5. Redis Enterprise Cluster custom resource - `RedisEnterpriseCluster`

    Apply the `RedisEnterpriseCluster` resource with RHEL7 based images:

    ```bash
    kubectl apply -f openshift/redis-enterprise-cluster_rhel.yaml
    ```

6. Redis Enterprise Database custom resource - `RedisEnterpriseDatabase`

   Create a `RedisEnterpriseDatabase` (REDB) by using Custom Resource.
   The Redis Enterprise Operator can be instructed to manage databases on the Redis Enterprise Cluster using the REDB custom resource.
    Example:
    ```yaml
    cat << EOF > /tmp/redis-enterprise-database.yml
    apiVersion: app.redislabs.com/v1alpha1
    kind: RedisEnterpriseDatabase
    metadata:
      name: redis-enterprise-database
    spec:
      redisEnterpriseCluster:
        name: redis-enterprise
      memorySize: 100MB
    EOF
    kubectl apply -f /tmp/redis-enterprise-database.yml
    ```
    Replace the name of the cluster with the one used on the current namespace.
    All REDB configuration options are documented [here](redis_enterprise_database_api.md).


   > Optional: REDB admission controller
   >
   > When using the REDB Custom Resource Definition (Redis Enterprise Database) it is recommended to set up the admission controller to improve input validation and catch configuration errors before they reach the cluster. The procedure is documented [here](admission/README.md).



## Configuration

### RedisEnterpriseCluster custom resource
The operator deploys a `RedisEnterpriseCluster` with default configurations values, but those can be customized in the `RedisEnterpriseCluster` spec as follow:

* Redis Enterprise Image
  ```yaml
    redisEnterpriseImageSpec:
      imagePullPolicy:  IfNotPresent
      repository:       redislabs/redis
      versionTag:       6.0.6-35
  ```

* Persistence
  ```yaml
    persistentSpec:
      enabled: true
      volumeSize: "10Gi" # if you don't provide default is 5 times RAM size
      storageClassName: "standard" #on AWS common storage class is gp2
  ```

* Redis Enterprise Nodes(pods) resources
  ```yaml
    redisEnterpriseNodeResources:
      limits:
        cpu: "4000m"
        memory: 4Gi
      requests:
        cpu: "4000m"
        memory: 4Gi
  ```

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

* CRDB (Active Active):
  >  Currently supported for OpenShift*
  ```yaml
  activeActive: # edit values according to your cluster
    apiIngressUrl:  my-cluster1-api.myopenshiftcluster1.com
    dbIngressSuffix: -dbsuffix1.myopenshiftcluster1.com
    method: openShiftRoute
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

Whenever images are not pulled from DockerHub, the following configuration must be specified:

In *RedisEnterpriseClusterSpec* (redis_enterprise_cluster.yaml):
- *redisEnterpriseImageSpec*
- *redisEnterpriseServicesRiggerImageSpec*
- *bootstrapperImageSpec*

Image specifications in *RedisEnterpriseClusterSpec* follow the same schema:
>see [ImageSpec](redis_enterprise_cluster_api.md#imagespec) for full reference

For example:
```yaml
  redisEnterpriseImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       harbor.corp.local/redisenterprise/redis
    versionTag:       6.0.6-35
```

```yaml
  redisEnterpriseServicesRiggerImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       harbor.corp.local/redisenterprise/k8s-controller
    versionTag:       6.0.6-5
```

```yaml
  bootstrapperImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       harbor.corp.local/redisenterprise/operator
    versionTag:       6.0.6-5
```

In Operator Deployment spec (operator.yaml):

For example:
```yaml
spec:
  template:
    spec:
      containers:
        - name: redis-enterprise-operator
          image: harbor.corp.local/redisenterprise/operator:6.0.6-5
```

Image specification follow the [K8s Container schema](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#container-v1-core).

### Pull secrets

Private repositories which require login can be accessed by creating a pull secret and declaring it in both the *RedisEnterpriseClusterSpec* and in the Operator Deployment spec.

[Create a pull secret](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-secret-by-providing-credentials-on-the-command-line) by running:

```shell
kubectl create secret docker-registry regcred --docker-server=<your-registry-server> --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email>
```
where:

-   `<your-registry-server>`  is your Private repository FQDN. ([https://index.docker.io/v1/](https://index.docker.io/v1/)  for DockerHub)
-   `<your-name>`  is your Docker username.
-   `<your-pword>`  is your Docker password.
-   `<your-email>`  is your Docker email.

This creates a pull secret names `regcred`

To use in the *RedisEnterpriseClusterSpec*:
```yaml
spec:
  pullSecrets:
    -name: regcred
```  

To use in the Operator Deployment:
```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      -name: regcred
```

### Advanced Configuration
- To configure Priority Class, Node Pool, Eviction Thresholds and other advances configuration see [topics.md](topics.md) file.
- Full [Redis Enterprise Cluster Custom Resource Specification](redis_enterprise_cluster_api.md)
- Full [Redis Enterprise Database Custom Resource Specification](redis_enterprise_database_api.md)

</br> </br>
## Upgrade
The Operator automates and simplifies the upgrade process.  
The Redis Enterprise Cluster Software, and the Redis Enterprise Operator for Kubernetes versions are tightly coupled and should be upgraded together.  
It is recommended to use the bundle.yaml to upgrade, as it loads all the relevant CRD documents for this version. If the updated CRDs are not loaded, the operator might fail.
There are two ways to upgrade - either set 'autoUpgradeRedisEnterprise' within the Redis Enterprise Cluster Spec to instruct the operator to automatically upgrade to the compatible version, or specify the correct Redis Enterprise image manually using the versionTag attribute. The Redis Enterprise Version compatible with this release is 6.0.6-35

```yaml
  autoUpgradeRedisEnterprise: true
```

Alternatively:
```yaml
  RedisEnterpriseImageSpec:
    versionTag: redislabs/redis:6.0.6-35
```
