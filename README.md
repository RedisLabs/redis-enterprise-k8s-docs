### Deploying Redis Enterprise K8s using an operator (custom controller)
#### Prerequisites:
* A minimum of 3 nodes which support the following requirements:  
    https://redislabs.com/redis-enterprise-documentation/administering/designing-production/hardware-requirements/
* A kubernetes version of 1.8 or higher
* For service broker - a k8s distribution that supports service catalog (see also: https://kubernetes.io/docs/concepts/extend-kubernetes/service-catalog/) 

#### Note: For REHL based images and/or deployments on OpenShift, please use redis-enterprise-cluster_rhel_.yaml and operator_rehl_.yaml 

#### Deployment:

Clone this repository, which contains the deployment files:
```
git clone git@github.com:RedisLabs/redis-enterprise-k8s-docs.git
```

Create a new namespace - for OpenShift see below 
```
kubectl create namespace demo
```

##### For OpenShift run:
```
oc new-project my-project
```

If you run OpenShift perform the following (you will need admin permissions for your cluster)
(provides the operator permissions for pods):

```
oc apply -f scc.yaml
```

You should receive the following response:
```
securitycontextconstraints.security.openshift.io "redis-enterprise-scc" configured*
```

Followed by:
```
oc adm policy add-scc-to-group redis-enterprise-scc system:serviceaccounts:my-project
```

###### Deployment cont.

If you're deploying a service broker also apply the sb_rbac.yaml file. First, edit sb_rbac.yaml namespace field to reflect the namespace you've created or switched to in the previous steps.

```
kubectl apply -f sb_rbac.yaml
```
You should receive the following response:
```
clusterrolebinding.rbac.authorization.k8s.io/redis-enterprise-operator configured
```


The next step applies rbac.yaml, creating a service account, role and role binding to allow resources access control (provides permissions to create and manage resources):
```
kubectl apply -f rbac.yaml
```

You should receive the following response:
```
clusterrolebinding.rbac.authorization.k8s.io/redis-enterprise-operator configured
```

The next step applies crd.yaml, creating a CustomResourceDefinition for redis enterprise cluster resource.
This creates another API resource to be handled by the k8s API server and managed by the operator we will deploy next.
```
kubectl apply -f crd.yaml
```

You should receive the following response:
```
customresourcedefinition.apiextensions.k8s.io/redisenterpriseclusters.app.redislabs.com configured
```

Create the operator deployment: a deployment responsible for managing the k8s deployment and lifecycle of a redis-enterprise-cluster.
Among many other responsibilities it creates a stateful set that runs the redis enterprise nodes (as pods).

Before applying - edit the tag according to the relevant operator version: ```image: redislabs/operator:tag```
```
kubectl apply -f operator.yaml
```

You should receive the following response:
```
deployment.apps/redis-enterprise-operator created
```

* Run ```kubectl get Deployment``` and verify redis-enterprise-operator deployment is running

A typical response may look like this:
```
|NAME                     |DESIRED | CURRENT  | UP-TO-DATE | AVAILABLE | AGE|
|-------------------------|-------------------------------------------------|
|redis-enterprise-operator|1	   | 1        |  1         | 1         | 2m |
```

Create A Redis Enterprise Cluster:
Choose the configuration relevant for you - you may find additional examples in the examples folder. Note that you will need to specify an image tag if you'd like to pull a RHEL image.

```kubectl apply -f redis-enterprise-cluster.yaml```

Run ```kubectl get rec``` and verify creation was successful. rec is a shortcut for RedisEnterpriseClusters.

