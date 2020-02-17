<!-- omit in toc -->
# Deploying Redis Enterprise K8s using an operator (custom controller)

- [Documentation](#documentation)
- [Quickstart Guide](#quickstart-guide)
  - [Prerequisites](#prerequisites)
- [Basic installation](#basic-installation)
  - [OpenShift](#openshift)

## Documentation

- [Quickstart Guide](#quickstart-guide)
- [Advanced Topics](docs/topics.md)
- [Resource Specification Reference](docs/operator.md)

## Quickstart Guide

### Prerequisites

- A minimum of 3 nodes which support the following requirements
- A kubernetes version of 1.8 or higher
- For service broker - a k8s distribution that supports service catalog (see also: service-catalog)
- Access to DockerHub, RedHat Container Catalog or a private repository that can serve the required images

## Basic installation

create a new namespace:

```bash
kubectl create namespace demo
```

To run a default installation with `kubectl` run the following:

```bash
kubectl apply -f bundle.yaml
```

or

```bash
kubectl apply -f role.yaml
kubectl apply -f role_binding.yaml
kubectl apply -f service_account.yaml
kubectl apply -f crds/app_v1_redisenterprisecluster_crd.yaml
kubectl apply -f operator.yaml
```

Run `kubectl get Deployment` and verify redis-enterprise-operator deployment is running.

A typical response may look like this:

```bash
|NAME                     |DESIRED | CURRENT  | UP-TO-DATE | AVAILABLE | AGE|
|-------------------------|-------------------------------------------------|
|redis-enterprise-operator|1	   | 1        |  1         | 1         | 2m |
```

Create A Redis Enterprise Cluster.  Choose the configuration relevant for you (see next section).  There are additional examples in the examples folder. Note that you need to specify an image tag if you'd like to pull a RHEL image.

```bash
kubectl apply -f crds/app_v1_redisenterprisecluster_cr.yaml
```

Run ```kubectl get rec``` and verify creation was successful. "rec" is a shortcut for RedisEnterpriseClusters.
In the deployment you should have the operator deployment, and in the rec you should have a single cluster.

### OpenShift

 To run OpenShift you will need to run a bit more stuff.
 > Notice: you will need to replace `<my-project>` with you project name

 Create a new project:

```bash
oc new-project my-project
```

perform the following commands (you need admin permissions for your cluster):

```bash
oc apply -f openshift/scc.yaml
```

You should receive the following response:
`securitycontextconstraints.security.openshift.io "redis-enterprise-scc" configured`

Provide the operator permissions for pods (substitute your project for "my-project"):

```bash
oc adm policy add-scc-to-group redis-enterprise-scc system:serviceaccounts:my-project
```

From here you can continue almost like in the basic installation

```bash
kubectl apply -f openshift.bundle.yaml
```

Apply the `RedisEnterpriseCluster` resource with RHEL7 based images

```bash
kubectl apply -f openshift/redis-enterprise-cluster_rhel.yaml
```
