<!-- omit in toc -->
# Deploying Redis Enterprise K8s using an operator (custom controller)

* [Documentation](#documentation)
* [Quickstart Guide](#quickstart-guide)
* [Prerequisites](#prerequisites)
* [Basic installation](#basic-installation)
* [OpenShift](#openshift)
* [Configuration Options](#configuration)
* [Private Repositories](#private-repositories)
* [Pull Secrets](#pull-secrets)
* [IPV4 enforcement](#ipv4-enforcement)

>Note: Please see the release notes for what's new in the latest release.

## Additional Documentation

- [Advanced Topics](docs/topics.md)
- [Resource Specification Reference](docs/operator.md)

## Quickstart Guide

### Prerequisites

- A minimum of 3 nodes which support the following requirements
- A Kubernetes cluster (server) version of 1.8 or higher
- A Kubernetes client (kubectl) with a matching version. For OpenShift, an OpenShift client (oc).
- For service broker - a k8s distribution that supports service catalog (see also: service-catalog)
- Access to DockerHub, RedHat Container Catalog or a private repository that can serve the required images

For Service Broker, please see examples/with_service_broker_rhel.yaml. RedHat certified images are available on: https://access.redhat.com/containers/#/product/71f6d1bb3408bd0d

The following are the images and tags for this release:

Redis Enterprise    -   `redislabs/redis:5.4.10-22` or `redislabs/redis:5.4.6-22b.rhel7-openshift`

Operator            -   `redislabs/operator:5.4.10-8` or `redislabs/operator:5.4.6-8.rhel7`

Services Rigger     -   `redislabs/k8s-controller:5.4.10-8` or `redislabs/k8s-controller:5.4.10-8b.rhel7`

Service Broker      -   `redislabs/service-broker:78_4b9b17f` or `redislabs/service-broker:78_4b9b17f.rhel7`

## Basic installation
The "Basic" installations deploys the operator from the current release with the default Ubuntu/Alpine base OS images from DockerHub and default settings.
This is the fastest way to get up and running with a new cluster in most environments.
Other Kubernetes distributions setup process as well as other custom configurations are referenced in this repository.

1. Create a new namespace:

```bash
kubectl create namespace demo
```

Switch context to the newly created namespace:

```bash
kubectl config set-context --current --namespace=demo
```

2. To deploy the default installation with `kubectl`, the following command will deploy a bundle of all the yaml declarations required for the operator:

```bash
kubectl apply -f bundle.yaml
```

Alternatively, to run each of the declarations of the bundle individually, run the following commands *instead* of the bundle:

```bash
kubectl apply -f role.yaml
kubectl apply -f role_binding.yaml
kubectl apply -f service_account.yaml
kubectl apply -f crds/app_v1_redisenterprisecluster_crd.yaml
kubectl apply -f operator.yaml
```
> Note: The rbac.yaml file used in previous releases has been broken down into three distinct files:
role.yaml, role_binding.yaml and service_account.yaml.
The crd.yaml file was renamed to redisenterprisecluster_crd.yaml, with the API version prepended to the filename.

3. Run `kubectl get deployment` and verify redis-enterprise-operator deployment is running.

A typical response may look like this:

```bash
|NAME                     |DESIRED | CURRENT  | UP-TO-DATE | AVAILABLE | AGE|
|-------------------------|-------------------------------------------------|
|redis-enterprise-operator|1	   | 1        |  1         | 1         | 2m |
```

4. Create A Redis Enterprise Cluster using the default configuration, which is suitable for development type deployments and works in typical scenarios. For more advanced deployment options you may choose the configuration relevant for you - see the index at the top for documentation references that cover many scenarios and the examples in the example folder.

```bash
kubectl apply -f crds/app_v1_redisenterprisecluster_cr.yaml
```

> Note: The redis-enterprise-cluster.yaml file was renamed to redisenterprisecluster_cr.yaml, with the API version prepended to the filename.

5. Run ```kubectl get rec``` and verify creation was successful. "rec" is a shortcut for RedisEnterpriseCluster.
A typical response may look like this:
```bash
|NAME               |AGE
|redis-enterprise   |5m
```

### OpenShift

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

```bash
kubectl apply -f openshift.bundle.yaml
```

Apply the `RedisEnterpriseCluster` resource with RHEL7 based images

```bash
kubectl apply -f openshift/redis-enterprise-cluster_rhel.yaml
```

#### Configuration:
The operator deploys with default configurations values, but those can be customized:

Redis Image
```yaml
  redisEnterpriseImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       redislabs/redis
    versionTag:       5.4.10-22
```

Persistence
```yaml
  persistentSpec:
    enabled: true
    volumeSize: "10Gi" # if you don't provide default is 5 times RAM size
    storageClassName: "standard" #on AWS common storage class is gp2
```

Redis Enterprise Nodes (pods)
```yaml
  redisEnterpriseNodeResources:
    limits:
      cpu: "4000m"
      memory: 4Gi
    requests:
      cpu: "4000m"
      memory: 4Gi
```

User Name to be used for accessing the cluster. Default is demo@redislabs.com
```yaml
username: "admin@acme.com"
```

UI service type: Load Balancer or cluster IP (default)
```yaml
uiServiceType: LoadBalancer
```

Extra Labels: additional labels to tag the k8s resources created during deployment
```yaml
  extraLabels:
    example1: "some-value"
    example2: "some-value"
```

UI annotations - add custom annotation to the UI service
```yaml
  uiAnnotations:
    uiAnnotation1: 'UI-annotation1'
    uiAnnotation2: 'UI-Annotation2'
```


SideCar containers- images that will run along side the redis enterprise containers
```yaml
  sideContainersSpec:
    - name: sidecar
      image: dockerhub_repo/repo:tag
      imagePullPolicy: IfNotPresent
```

Service Broker (only for supported clusters)
```yaml
  serviceBrokerSpec:
    enabled: true
    persistentSpec:
      storageClassName: "gp2" #adjust according to infrastructure
```

CRDB (Active Active):
*Currently supported for OpenShift*

```yaml
activeActive: # edit values according to your cluster
  apiIngressUrl:  my-cluster1-api.myopenshiftcluster1.com
  dbIngressSuffix: -dbsuffix1.myopenshiftcluster1.com
  method: openShiftRoute
```

With Service Broker support (add this in addition to serviceBrokerSpec section):
```yaml
activeActive: # edit values according to your cluster
  apiIngressUrl:  my-cluster1-api.myopenshiftcluster1.com
  dbIngressSuffix: -dbsuffix1.myopenshiftcluster1.com
  method: openShiftRoute
    peerClusters:
      - apiIngressUrl: my-cluster2-api.myopenshiftcluster2.com
        authSecret: cluster2_secret
        dbIngressSuffix: -dbsuffix2.myopenshiftcluster2.com
        fqdn: <cluster2_name>.<cluster2_namespace>.svc.cluster.local
      - apiIngressUrl: my-cluster3-api.myopenshiftcluster3.com
        authSecret: cluster3_secret
        dbIngressSuffix: -dbsuffix3.myopenshiftcluster3.com
        fqdn: <cluster3_name>.<cluster3_namespace>.svc.cluster.local
```

#### Private Repositories

Whenever images are not pulled from DockerHub, the following configuration options must be specified:

In *RedisEnterpriseClusterSpec* (redis_enterprise_cluster.yaml):
- *redisEnterpriseImageSpec*
- *redisEnterpriseServicesRiggerImageSpec*
- *serviceBrokerSpec - imageSpec* (if deploying the Service Broker)
- *bootstrapperImageSpec*

Image specifications in *RedisEnterpriseClusterSpec* follow the same schema:

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| repository | Repository | string |  | true |
| versionTag |  | string |  | true |
| imagePullPolicy |  | v1.PullPolicy |  | true |

For example:
```yaml
  redisEnterpriseImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       harbor.corp.local/redisenterprise/redis
    versionTag:       5.4.10-22
```

```yaml
  redisEnterpriseServicesRiggerImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       harbor.corp.local/redisenterprise/k8s-controller
    versionTag:       5.4.10-8
```

```yaml
  bootstrapperImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       harbor.corp.local/redisenterprise/operator
    versionTag:       5.4.10-8
```

In Operator Deployment spec (operator.yaml):
- containers - image

For example:
```yaml
spec:
  template:
    spec:
      containers:
        - name: redis-enterprise-operator
          image: harbor.corp.local/redisenterprise/operator:5.4.10-8
```

Image specification follow the [K8s Container schema](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#container-v1-core).

#### Pull secrets

Private repositories which require login can be accessed by creating a pull secret and declaring it in both the *RedisEnterpriseClusterSpec* and in the Operator Deployment spec.

[Create a pull secret](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-secret-by-providing-credentials-on-the-command-line) by running:

```shell
kubectl create secret docker-registry regcred --docker-server=<your-registry-server> --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email>
```
where:

-   `<your-registry-server>`  is your Private Docker Registry FQDN. ([https://index.docker.io/v1/](https://index.docker.io/v1/)  for DockerHub)
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

#### IPV4 enforcement
You might not have IPV6 support in your K8S cluster.
In this case, you could enforce the use of IPV4, by adding the following attribute to the REC spec:
```yaml
  enforceIPv4: true
```
Note: Setting 'enforceIPv4' to 'true' is a requirement for running REC on PKS.

[requirements]: https://redislabs.com/redis-enterprise-documentation/administering/designing-production/hardware-requirements/
[service-catalog]: https://kubernetes.io/docs/concepts/extend-kubernetes/service-catalog/
