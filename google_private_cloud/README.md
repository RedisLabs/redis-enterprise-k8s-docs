<!-- omit in toc -->
# Deploying Redis Enterprise on Google Private Cloud

This page describes how to deploy Redis Enterprise on Google Private Cloud Kubernetes solution using the Redis Enterprise Operator.

### Prerequisites

- A Kubernetes cluster version of 1.20 or higher, with a minimum of 3 worker nodes.
- A Kubernetes client (kubectl) with a matching version.
- Access to DockerHub, Harbor or a private repository that can serve the required images.  



The following are the images and tags for this release:

| Component | k8s |
| --- | --- |
| Redis Enterprise | `redislabs/redis:6.2.10-100` |
| Operator | `redislabs/operator:6.2.10-31` |
| Services Rigger | `redislabs/k8s-controller:6.2.10-31` |


### Installation
The "Basic" installation deploys the operator (from the current release) from DockerHub and default settings.
This is the fastest way to get up and running with a new Redis Enterprise on Kubernetes.

1. We will need to clone the yamls from [github](https://github.com/RedisLabs/redis-enterprise-k8s-docs/releases) to your local directory.

2. Create a new namespace:
    > Note:
    For the purpose of this doc, we'll use the name "demo" for our cluster's namespace.

    ```bash
    kubectl create namespace demo
    ```

    Switch context to the newly created namespace:

    ```bash
    kubectl config set-context --current --namespace=demo
    ```
*** 
For deploying the bundle and the Redis Enterprise Cluster custom resource we will use the [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/).
3. Customize the operator deployment - 

    Before deploying the bundle.yaml we will need to customize it .
    edit the `bundle\kustomize_bundle.yaml` file :
    > Note:
    Replace the [User Private repo] with your private images repository location.
   
4. Deploy the operator bundle
    
    with `kubectl`, the following command will deploy a bundle of all the yaml declarations required for the operator:

    ```bash
    kubectl apply -k bundle
    ```

    Run `kubectl get deployment` and verify redis-enterprise-operator deployment is running.

    A typical response may look like this:

    ```bash
    NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
    redis-enterprise-operator          1/1     1            1           2m
    ```

5. Customize the Redis Enterprise Cluster custom resource - 

    Before deploying the rec.yaml we will need to customize it .
    edit the `rec\kustomize_rec.yaml` file :
    > Note:
    Replace the [User Private repo] with your private images repository location.
    
    The kustomize_rec.yaml configure the Redis Enterprise Cluster custom resource with the default configuration, 
    which is suitable for development type deployments and works in typical scenarios. 
    The full list of attributes supported through the Redis Enterprise Cluster (REC) API can be found [HERE](redis_enterprise_cluster_api.md). 


6. Redis Enterprise Cluster custom resource - `RedisEnterpriseCluster`

   Create a `RedisEnterpriseCluster`(REC) using the kustomize capability, 

    ```bash
    kubectl apply -k rec
    ```

    > Note:
    The Operator can only manage one Redis Enterprise Cluster custom resource in a namespace. To deploy another Enterprise Clusters in the same Kubernetes cluster, deploy an Operator in an additional namespace for each additional Enterprise Cluster required. Note that each Enterprise Cluster can effectively host hundreds of Redis Database instances. Deploying multiple clusters is typically used for scenarios where complete operational isolation is required at the cluster level.
  
7. Run ```kubectl get rec``` and verify creation was successful. `rec` is a shortcut for RedisEnterpriseCluster. The cluster takes around 5-10 minutes to come up.
    A typical response may look like this:
    ```
    NAME  AGE
    rec   5m
    ```
    > Note: Once the cluster is up, the cluster GUI and API could be used to configure databases. It is recommended to use the K8s REDB API that is configured through the following steps. To configure the cluster using the cluster GUI/API, use the ui service created by the operator and the default credentials as set in a secret. The secret name is the same as the cluster name within the namespace.


*** For advanced configuration and more info you can visit our formal documentation [here](https://github.com/RedisLabs/redis-enterprise-k8s-docs/blob/master/README.md).