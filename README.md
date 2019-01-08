### Deploying Redis Enterprise K8s using an operator (custom controller)
### Table of Contents


* [Prerequisites](#prerequisites)
* [Deployment](#deployment)
* [Configuration Options](#configuration)



#### Prerequisites:
* A minimum of 3 nodes which support the following [requirements][] 
* A kubernetes version of 1.8 or higher
* For service broker - a k8s distribution that supports service catalog (see also: [service-catalog][])
> Note: For REHL based images and/or deployments on OpenShift, please use redis-enterprise-cluster_rhel.yaml and operator_rhel.yaml.  
For Service Broker, please see examples/with_service_broker_rhel.yaml. RedHat certified images are available on: https://access.redhat.com/containers/#/product/71f6d1bb3408bd0d  


#### Deployment:
Clone (or download) this repository, which contains the deployment files:
```
git clone https://github.com/RedisLabs/redis-enterprise-k8s-docs.git
```

1) Create a namespace / project:
    > For OpenShift deployment create a new project:
    ```
    oc new-project my-project
    ```
    
    > For non-OpenShift deployment - create a new namespace:
    ```
    kubectl create namespace demo
    ```



2) If you run OpenShift perform the following (you need admin permissions for your cluster)
(this provides the operator permissions for pods):
    ```
    oc apply -f scc.yaml
    ```
    > You should receive the following response:
    ```
    securitycontextconstraints.security.openshift.io "redis-enterprise-scc" configured*
    ```
    Followed by (change "my-project"):
    ```
    oc adm policy add-scc-to-group redis-enterprise-scc system:serviceaccounts:my-project
    ```
    If you're deploying a service broker also apply the sb_rbac.yaml file. First, edit sb_rbac.yaml namespace field to reflect the namespace you've created or switched to in the previous steps.
    ```
    kubectl apply -f sb_rbac.yaml
    ```
    > You should receive the following response:
    ```
    clusterrolebinding.rbac.authorization.k8s.io/redis-enterprise-operator configured
    ```

3) The next step applies rbac.yaml, creating a service account, role, and role-binding to allow resources access control (provides permissions to create and manage resources):
    ```
    kubectl apply -f rbac.yaml
    ```
    
    > You should receive the following response:
    ```
    clusterrolebinding.rbac.authorization.k8s.io/redis-enterprise-operator configured
    ```

4) The next step applies crd.yaml, creating a CustomResourceDefinition for redis enterprise cluster resource.
This creates another API resource to be handled by the k8s API server and managed by the operator we will deploy next.
    ```
    kubectl apply -f crd.yaml
    ```
    
    > You should receive the following response:
    ```
    customresourcedefinition.apiextensions.k8s.io/redisenterpriseclusters.app.redislabs.com configured
    ```

5) Create the operator deployment: a deployment responsible for managing the k8s deployment and lifecycle of a redis-enterprise-cluster.
    Among many other responsibilities, it creates a stateful set that runs the redis enterprise nodes (as pods).
    
    Before applying - edit the tag according to the relevant operator version: ```image: redislabs/operator:tag```
    ```
    kubectl apply -f operator.yaml
    ```
    
    > You should receive the following response:
    ```
    deployment.apps/redis-enterprise-operator created
    ```

6) Run ```kubectl get Deployment``` and verify redis-enterprise-operator deployment is running

    A typical response may look like this:
    ```
    |NAME                     |DESIRED | CURRENT  | UP-TO-DATE | AVAILABLE | AGE|
    |-------------------------|-------------------------------------------------|
    |redis-enterprise-operator|1	   | 1        |  1         | 1         | 2m |
    ```

7)  Create A Redis Enterprise Cluster:
    Choose the configuration relevant for you (see next section) - you may find additional examples in the examples folder. Note that you need to specify an image tag if you'd like to pull a RHEL image.

    ```kubectl apply -f redis-enterprise-cluster.yaml```

8) Run ```kubectl get rec``` and verify creation was successful. rec is a shortcut for RedisEnterpriseClusters.


#### Configuration:
The operator deploys with default configurations values, but those can be customized:

Redis Image
```yaml
  redisEnterpriseImageSpec:
    imagePullPolicy:  IfNotPresent
    repository:       redislabs/redis
    versionTag:       5.2.2-14
```

Persistence 
```yaml
  persistentSpec:
    enabled: true
    volumeSize: "10Gi" # if you don't provide default is 5 times RAM size
    storageClassName: "standard" #on AWS common storage class is gp2
```

Redis Enterprise Nodes (podes)
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

Service Broker (only for supported clusters)
```yaml 
  serviceBrokerSpec:
    enabled: true
    persistentSpec:
      storageClassName: "gp2" #adjust according to infrastructure 
```

SideCar containers- images that will run along side the redis enterprise containers
```yaml
  sideContainersSpec:
    - name: sidecar
      image: dockerhub_repo/repo:tag
      imagePullPolicy: IfNotPresent
```

[requirements]: https://redislabs.com/redis-enterprise-documentation/administering/designing-production/hardware-requirements/
[service-catalog]: https://kubernetes.io/docs/concepts/extend-kubernetes/service-catalog/
