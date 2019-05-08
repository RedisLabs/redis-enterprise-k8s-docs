# Overview

Redis-Enterprise is 

[Learn more](https://www.redislabs.com/).


## Design

![Architecture diagram](resources/image)

### Solution Information

Redis-Enterprise cluster is deployed within a Kubernetes `StatefulSet`.

The deployment creates two services:

- client-facing one, designed to be used for client connections to the Redis-Enterprise
  cluster with port forwarding or using a LoadBalancer,
- and service discovery - a headless service for connections between
  the Redis-Enterprise nodes.

Redis-Enterprise K8s application has the following ports configured:


# Installation

## Quick install with Google Cloud Marketplace

Get up and running with a few clicks! Install this Redis-Enterprise app to a
Google Kubernetes Engine cluster using Google Cloud Marketplace.

## Command line instructions

### Prerequisites

#### Set up command-line tools

You'll need the following tools in your development environment:

- [gcloud](https://cloud.google.com/sdk/gcloud/)
- [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/)
- [docker](https://docs.docker.com/install/)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Configure `gcloud` as a Docker credential helper:

```shell
gcloud auth configure-docker
```

#### Create a Google Kubernetes Engine cluster

Create a new cluster from the command line.

```shell
export CLUSTER=redis-cluster
export ZONE=us-west1-a

gcloud container clusters create "$CLUSTER" --zone "$ZONE"
```

Configure `kubectl` to connect to the new cluster.

```shell
gcloud container clusters get-credentials "$CLUSTER" --zone "$ZONE"
```

#### Clone this repo

Clone this repo and the associated tools repo.

```shell
git clone --recursive https://github.com/GoogleCloudPlatform/redis-enterprise-k8s-docs.git
```

#### Install the Application resource definition

An Application resource is a collection of individual Kubernetes components,
such as Services, Deployments, and so on, that you can manage as a group.

To set up your cluster to understand Application resources, run the following command:

```shell
kubectl apply -f "https://raw.githubusercontent.com/GoogleCloudPlatform/marketplace-k8s-app-tools/master/crd/app-crd.yaml"
```

You need to run this command once.

The Application resource is defined by the
[Kubernetes SIG-apps](https://github.com/kubernetes/community/tree/master/sig-apps)
community. The source code can be found on
[github.com/kubernetes-sigs/application](https://github.com/kubernetes-sigs/application).

### Install the Application

Navigate to the `marketplace` directory:

```shell
cd gcp-marketplace
```

#### Configure the app with environment variables

Choose an instance name and
[namespace](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
for the app. In most cases, you can use the `default` namespace.

```shell
export APP_INSTANCE_NAME=redis-1
export NAMESPACE=default
```

Set the number of replicas:

```shell
export REPLICAS=3
```


Set the username for the app:

```shell
export REDIS_ADMIN=admin@acme.com
```


Set the CPU and Memory for nodes:

```shell
export NODE_CPU=1000
export NODE_MEM=1000
```


Configure the container images:

```shell
export IMAGE_REDIS=redislabs/operator:498_f987b08
export IMAGE_UBBAGENT=us.gcr.io/proven-reality-226706/ubbagent
```

#### Create namespace in your Kubernetes cluster

If you use a different namespace than the `default`, run the command below to create a new namespace:

```shell
kubectl create namespace "$NAMESPACE"
```

#### Prerequisites for using Role-Based Access Control

If you want to use [role-based access control](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
for the app, you must grant your user the ability to create roles in
Kubernetes by running the following command:

```shell
kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole cluster-admin \
  --user $(gcloud config get-value account)
```

You need to run this command **once** for the cluster.
For steps to enable role-based access control in Google Kubernetes Engine, see
the [Kubernetes Engine documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/role-based-access-control).

#### Expand the manifest template

Use `envsubst` to expand the template. We recommend that you save the
expanded manifest file for future updates to the application.

1. Expand `RBAC` YAML file. You must configure RBAC related stuff .

    ```shell
    # Define name of service account
    export SERVICE_ACCOUNT=redis-enterprise-operator
    # Expand rbac.yaml.template
    envsubst '$APP_INSTANCE_NAME $NAMESPACE $SERVICE_ACCOUNT' < scripts/rbac.yaml.template > "${APP_INSTANCE_NAME}_rbac.yaml"
    ```

1. Expand `Application`/`crd`/`operator`/`ConfigMap` YAML files.

    ```shell
     awk 'FNR==1 {print "---"}{print}' manifest/* \
     | envsubst '$APP_INSTANCE_NAME $NAMESPACE $IMAGE_REDIS $REPLICAS $REDIS_ADMIN $SERVICE_ACCOUNT $NODE_CPU $NODE_MEM' \
     > "${APP_INSTANCE_NAME}_manifest.yaml"
    ```

#### Apply the manifest to your Kubernetes cluster

Use `kubectl` to apply the manifest to your Kubernetes cluster:

```shell
# rbac.yaml
kubectl apply -f "${APP_INSTANCE_NAME}_rbac.yaml" --namespace "${NAMESPACE}"
# manifest.yaml
kubectl apply -f "${APP_INSTANCE_NAME}_manifest.yaml" --namespace "${NAMESPACE}"
```

#### View the app in the Google Cloud Platform Console

To get the Console URL for your app, run the following command:

```shell
echo "https://console.cloud.google.com/kubernetes/application/${ZONE}/${CLUSTER}/${NAMESPACE}/${APP_INSTANCE_NAME}"
```

To view your app, open the URL in your browser.

#### Get the status of the cluster

By default, the application does not have an external IP address. To get the
status of the cluster, use `kubectl port-forward` to access the dashboard on the master
node:

```
kubectl port-forward  redis-enterprise-cluster-0 8443

```

#### Getting the Admin Password

See instructions here: https://docs.redislabs.com/latest/rs/faqs/

####  Access the Redis-Enterprise service externally

```
kubectl get services -n $NAMESPACE
```

> **NOTE:** It might take some time for the external IP to be provisioned.


# Uninstall the Application

## Using the Google Cloud Platform Console

1. In the GCP Console, open [Kubernetes Applications](https://console.cloud.google.com/kubernetes/application).

1. From the list of applications, click **Redis-Enterprise**.

1. On the Application Details page, click **Delete**.

## Using the command line

### Prepare the environment

Set your installation name and Kubernetes namespace:

```shell
export APP_INSTANCE_NAME=redis-enterprise-1
export NAMESPACE=default
```

### Delete the resources

> **NOTE:** We recommend to use a kubectl version that is the same as the version of your cluster. Using the same versions of kubectl and the cluster helps avoid unforeseen issues.

To delete the resources, use the expanded manifest file used for the
installation.

Run `kubectl` on the expanded manifest file:

```shell
# manifest.yaml
kubectl delete -f "${APP_INSTANCE_NAME}_manifest.yaml" --namespace "${NAMESPACE}"
# rbac.yaml
kubectl delete -f "${APP_INSTANCE_NAME}_rbac.yaml" --namespace "${NAMESPACE}"
```

Otherwise, delete the resources using types and a label:

```shell
kubectl delete statefulset,secret,service,configmap,serviceaccount,role,rolebinding,application \
  --namespace $NAMESPACE \
  --selector app.kubernetes.io/name=$APP_INSTANCE_NAME
```

### Delete the persistent volumes of your installation

By design, removal of StatefulSets in Kubernetes does not remove
PersistentVolumeClaims that were attached to their Pods. This prevents your
installations from accidentally deleting stateful data.

To remove the PersistentVolumeClaims with their attached persistent disks, run
the following `kubectl` commands:

```shell
for pv in $(kubectl get pvc --namespace $NAMESPACE \
  --selector app.kubernetes.io/name=$APP_INSTANCE_NAME \
  --output jsonpath='{.items[*].spec.volumeName}');
do
  kubectl delete pv/$pv --namespace $NAMESPACE
done

kubectl delete persistentvolumeclaims \
  --namespace $NAMESPACE \
  --selector app.kubernetes.io/name=$APP_INSTANCE_NAME
```

### Delete the GKE cluster

```
gcloud container clusters delete "$CLUSTER" --zone "$ZONE"
```

