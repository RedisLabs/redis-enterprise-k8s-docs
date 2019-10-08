### Deploying Redis Enterprise K8s using an operator (custom controller)
### Table of Contents


* [Prerequisites](#prerequisites)
* [Deployment](#deployment)
* [Configuration Options](#configuration)
* [IPV4 enforcement](#ipv4-enforcement)



#### Prerequisites:
* A minimum of 3 nodes which support the following [requirements][]
* A kubernetes version of 1.8 or higher
* For service broker - a k8s distribution that supports service catalog (see also: [service-catalog][])
* Access to DockerHub, RedHat Container Catalog or a private repository that can serve the required images
> Note: For RHEL based images and/or deployments on OpenShift, please use redis-enterprise-cluster_rhel.yaml and operator_rhel.yaml.
For Service Broker, please see examples/with_service_broker_rhel.yaml. RedHat certified images are available on: https://access.redhat.com/containers/#/product/71f6d1bb3408bd0d

The following are the images and tags for this release:

Redis Enterprise    -   `redislabs/redis:5.4.6-18` or `redislabs/redis:5.4.6-18.rhel7-openshift`

Operator            -   `redislabs/operator:5.4.6-1183` or `redislabs/operator:5.4.6-1183.rhel7`

Services Rigger     -   `redislabs/k8s-controller:5.4.6-1183` or `redislabs/k8s-controller:5.4.6-1183.rhel7`

Service Broker      -   `redislabs/service-broker:78_4b9b17f` or `redislabs/service-broker:78_4b9b17f.rhel7`



#### Deployment:
Clone (or download) this repository, which contains the deployment files:
```
git clone https://github.com/RedisLabs/redis-enterprise-k8s-docs.git
```

1) Create a namespace / project.

    For non-OpenShift deployments, create a new namespace:

    ```
    kubectl create namespace demo
    ```

    For OpenShift deployments, create a new project (you can substitute `oc` for `kubectl` in the rest of these instructions):

    ```
    oc new-project my-project
    ```

    > For either deployment, switch context to operate within the newly created namespace:
    ```
    kubectl config set-context --current --namespace=demo
    ```

2) If you are not running OpenShift, skip to the next step.  For OpenShift, perform the following commands (you need admin permissions for your cluster):

    ```
    oc apply -f scc.yaml
    ```
      > You should receive the following response:

    `securitycontextconstraints.security.openshift.io "redis-enterprise-scc" configured`

    Provide the operator permissions for pods (substitute your project for "my-project"):
    ```
    oc adm policy add-scc-to-group redis-enterprise-scc system:serviceaccounts:my-project
    ```

    If you're deploying a service broker, also apply the sb_rbac.yaml file:
    ```
    oc apply -f sb_rbac.yaml
    ```

    > You should receive the following response:

    `clusterrole "redis-enterprise-operator-sb" configured`

    Bind the Cluster Service Broker role to the operator service account (in the current namespace):

     ```
    oc adm policy add-cluster-role-to-user redis-enterprise-operator-sb --serviceaccount redis-enterprise-operator --rolebinding-name=redis-enterprise-operator-sb
     ```
    > You should receive the following response:

    `cluster role "redis-enterprise-operator-sb" added: "redis-enterprise-operator"`

3) You can optionally use pod security policy.
    ```
    kubectl apply -f psp.yaml
    ```
    If you use this option, you should add the policy name to REC configuration, in redis-enterprise-cluster.yaml.
    ```
    podSecurityPolicyName: "redis-enterprise-psp"
    ```


4) The next step applies rbac.yaml, creating a service account, role, and role-binding to allow resources access control (provides permissions to create and manage resources):

    ```
    kubectl apply -f rbac.yaml
    ```

    > You should receive the following response:

    `clusterrolebinding.rbac.authorization.k8s.io/redis-enterprise-operator configured`

5) The next step applies crd.yaml, creating a CustomResourceDefinition for redis enterprise cluster resource.
This creates another API resource to be handled by the k8s API server and managed by the operator we will deploy next.
    ```
    kubectl apply -f crd.yaml
    ```

    > You should receive the following response:

    `customresourcedefinition.apiextensions.k8s.io/redisenterpriseclusters.app.redislabs.com configured`

6) Create the operator deployment: a deployment responsible for managing the k8s deployment and lifecycle of a redis-enterprise-cluster.
    Among many other responsibilities, it creates a stateful set that runs the redis enterprise nodes (as pods).

    Before applying, edit the tag according to the relevant operator version: `image: redislabs/operator:tag`
    ```
    kubectl apply -f operator.yaml
    ```

    > You should receive the following response:

    `deployment.apps/redis-enterprise-operator created`

7) Run `kubectl get Deployment` and verify redis-enterprise-operator deployment is running.

    A typical response may look like this:
    ```
    |NAME                     |DESIRED | CURRENT  | UP-TO-DATE | AVAILABLE | AGE|
    |-------------------------|-------------------------------------------------|
    |redis-enterprise-operator|1	   | 1        |  1         | 1         | 2m |
    ```

8)  Create A Redis Enterprise Cluster.  Choose the configuration relevant for you (see next section).  There are additional examples in the examples folder. Note that you need to specify an image tag if you'd like to pull a RHEL image.

    ```
    kubectl apply -f redis-enterprise-cluster.yaml
    ```

9) Run ```kubectl get rec``` and verify creation was successful. "rec" is a shortcut for RedisEnterpriseClusters.


#### Configuration:
The operator deploys with default configurations values, but those can be customized:

Redis Image
```yaml
  redisEnterpriseImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       redislabs/redis
    versionTag:       5.4.6-18
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
*Currently supported for OpenShift

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

#### IPV4 enforcement
You might not have IPV6 support in your K8S cluster.
In this case, you could enforce the use of IPV4, by adding the following attribute to the REC spec:
```yaml
  enforceIPv4: true
```
Note: Setting 'enforceIPv4' to 'true' is a requirement for running REC on PKS.

[requirements]: https://redislabs.com/redis-enterprise-documentation/administering/designing-production/hardware-requirements/
[service-catalog]: https://kubernetes.io/docs/concepts/extend-kubernetes/service-catalog/
