<!-- omit in toc -->
# Advanced Configuration

- [Guaranteed Quality of Service](#guaranteed-quality-of-service)
- [Priority Class](#priority-class)
- [Node Pool](#node-pool)
- [K8s Out of Resource Handling recommendations](#k8s-out-of-resource-handling-recommendations)
  - [Monitoring](#monitoring)
  - [Eviction Thresholds](#eviction-thresholds)
- [Pod Security Policy (PSP)](#pod-security-policy-psp)
- [Side Cars](#side-cars)
- [Resource Limits and Quotas](#resource-limits-and-quotas)
- [Custom Resource Deletion](#custom-resource-deletion)

## Guaranteed Quality of Service

To make sure that all pods created by operator receive enough CPU and memory, we make sure k8s [quality of service is guaranteed](https://kubernetes.io/docs/tasks/configure-pod-container/quality-service-pod).
This means that for all containers in operator managed pods:

- Every Container must have a memory limit and a memory request, and they must be the same.
- Every Container must have a CPU limit and a CPU request, and they must be the same.

This is always the case with default settings, but if the user changes the resources of services rigger, redis enterprise, or bootstrapper, they should take care to keep quality of service.
If the user defines a side container, that runs alongside redis enterprise, they should also take care to keep the above mentioned settings.

## Priority Class

We recommend that users set a high [priority class](https://kubernetes.io/docs/concepts/configuration/pod-priority-preemption) for pods managed by operator.
This can be set by creating a dedicated PriorityClass resource, or using an existing one:

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: redis-enterprise-priority
value: 1000000000
globalDefault: false
description: "This priority class should be used for Redis Enterprise pods only."
```

And specifying the priorityClassName in REC spec.

## Node Pool

Kubernetes is a multi-tenant environment, so we want to protect Redis Enterprise from competing with [noisy neighbours](https://en.wikipedia.org/wiki/Cloud_computing_issues#Performance_interference_and_noisy_neighbors) for resources.  
Therefore for production environments, it's a good idea to run Redis Enterprise Cluster on a dedicated Node Pool.
How to set up a node pool depends very much on how you run k8s, but it's fair to assume each pool of nodes has a label.
For example, in GKE, the nodes node pool name is found in the nodes label `cloud.google.com/gke-nodepool`.

```bash
> kubectl get nodes -o jsonpath='{range .items[*]}node name: {.metadata.name}{"\t"}node pool: {.metadata.labels.cloud\.google\.com/gke-nodepool}{"\n"}{end}'
node name: gke-pool1-55d1ac88-213c 	node pool: pool1
node name: gke-pool1-55d1ac88-vrpp 	node pool: pool1
node name: gke-pool1-7253cc19-42g0 	node pool: pool1
node name: gke-pool2-f36f7402-6w9b 	node pool: pool2
node name: gke-pool2-f36f7402-qffp 	node pool: pool2
```

To run only on nodes with a specific label (pool name label in this case), we specify `nodeSelector` in REC spec.

```yaml
apiVersion: app.redislabs.com/v1
kind: RedisEnterpriseCluster
metadata:
  name: example-redisenterprisecluster
spec:
  nodes: 3
  nodeSelector:
    cloud.google.com/gke-nodepool: pool1
```

## K8s Out of Resource Handling recommendations

We highly recommend reading [k8s documentation of out of resource administration](https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource).

### Monitoring

We recommend monitoring node conditions, and specifically `MemoryPressure` and `DiskPressure`.
These conditions are true if an [eviction threshold](https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/#eviction-thresholds)
 has been met - meaning pod eviction is immanent.

```bash
> kubectl get nodes -o jsonpath='{range .items[*]}name:{.metadata.name}{"\t"}MemoryPressure:{.status.conditions[?(@.type == "MemoryPressure")].status}{"\t"}DiskPressure:{.status.conditions[?(@.type == "DiskPressure")].status}{"\n"}{end}'
name:gke-55d1ac88-213c	MemoryPressure:False	DiskPressure:False
name:gke-55d1ac88-vrpp	MemoryPressure:False	DiskPressure:False
name:gke-7253cc19-42g0	MemoryPressure:False	DiskPressure:False
```

### Eviction Thresholds

We recommend setting high a [soft eviction threshold](https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/#soft-eviction-thresholds),
relative to the [hard eviction threshold](https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource/#hard-eviction-thresholds).
The high soft threshold mean the node condition will change earlier, alerting the administrator.
We also recommend setting `eviction-max-pod-grace-period` high enough to allow RS pods to migrate redis databases itself, before being force killed.

The `eviction-soft-grace-period` should be set high enough for the administrator (or a k8s auto-scaling mechanism) to scale k8s up or out.

In general, eviction thresholds are managed by [kubelet arguments](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet).
For OpenShift, eviction thresholds can be managed via [config file](https://docs.openshift.com/container-platform/3.11/admin_guide/out_of_resource_handling.html#out-of-resource-create-config).
On GKE, these thresholds are [managed](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-architecture#node_allocatable).

## Pod Security Policy (PSP)

You can optionally use pod security policy.

```bash
kubectl apply -f advanced/psp.yaml
```

If you use this option, you should add the policy name to REC configuration, in redis-enterprise-cluster.yaml.

```yaml
podSecurityPolicyName: "redis-enterprise-psp"
```


## Side Cars

SideCar containers- images that will run along side the redis enterprise containers

```yaml
  sideContainersSpec:
    - name: sidecar
      image: dockerhub_repo/repo:tag
      imagePullPolicy: IfNotPresent
```

## Resource Limits and Quotas

All the pods created by the operator are set with a resources section to their spec, so it is possible to apply a ResourceQuota on the namespace of the Redis Enterprise Cluster. The operator itself is set with resources limits and requests.
The recommended settings are set in the operator.yaml file and the bundles. The operator was tested and proved to be working in minimal workloads with the following settings in operator.yaml:


```yaml
  resources:
    limits:
      cpu: 0.5
      memory: 256Mi
    requests:
      cpu: 0.5
      memory: 256Mi
```

When creating ResourceQuota, be careful when applying quotas on ConfigMaps. When testing the operator the limit was found to be met even when one ConfigMap was used, perhaps due to enforcement logic of some sort. The following ResourceQuota worked on internal testing, but might need tweaking according to the deployment scenario:
```yaml
  hard:
    secrets: "40"
    persistentvolumeclaims: "20"
    replicationcontrollers: "40"
    pods: "40"
    requests.storage: "120400Mi"
    services: "20"
    requests.memory: "43344Mi"
    limits.memory: "57792Mi"
    limits.cpu: "64"
    requests.cpu: "48"
```

## Custom Resource Deletion
### REDB Deletion
The Redis Enterprise Database (REDB) object has a finalizer, to make sure the database is deleted before the REDB custom resource is removed from k8s.  
The finalizer name is `finalizer.redisenterprisedatabases.app.redislabs.com`.  
When a user requests the deletion of REDB (for example by running `kubectl delete redb <name>`), the following happens:
1. K8s API adds `DeletionTimestamp` to the REDB resource.
2. The Operator notices the `DeletionTimestamp`, and sends delete request to the RS API.
3. When RS API approves the delete request, the operator removes the REDB finalizer.
4. K8s cleans up the REDB resource, now that it has no finalizers.

If for some reason the user ends up with an REDB resource that can't be deleted, because the finalizer can't be removed, they can remove the finalizer manually by editing the REDB resource.
For example, if the REDB name is `redis-enterprise-database`, here is a command to remove its finalizer manually:
```shell script
kubectl patch redb redis-enterprise-database --type=json -p '[{"op":"remove","path":"/metadata/finalizers","value":"finalizer.redisenterprisedatabases.app.redislabs.com"}]'
```
note: In this case the database may still exist in the Redis Enterprise cluster, and should be deleted via RS GUI, or API.

### REC Deletion
The Redis Enterprise Cluster (REC) object has a finalizer, to make sure all REDBs on that cluster are deleted before the REC custom resource is removed from k8s.  
The finalizer name is `redbfinalizer.redisenterpriseclusters.app.redislabs.com`.  
When a user requests the deletion of an REC (for example by running `kubectl delete rec <name>`), the following happens:
1. K8s API adds `DeletionTimestamp` to the REC resource.
2. The Operator notices the `DeletionTimestamp`, and checks if this REC has REDBs attached to it.
3. If there are such REDBs, the operator will not delete the REC, and will log the error: `Cannot delete REC, as REDBs that were stored in the cluster still exist.`
4. When there are no more REDBs attached to that REC, the operator will remove the finalizer from the REC resource.
5. K8s cleans up the REC resource, including deployments and stateful sets, now that it has no finalizers.

If for some reason the user ends up with an REC resource that can't be deleted, because the finalizer can't be removed, they can remove the finalizer manually by editing the REC resource.
For example, if the REC name is `redis-enterprise`, here is a command to remove its finalizer manually:
```shell script
kubectl patch rec redis-enterprise --type=json -p '[{"op":"remove","path":"/metadata/finalizers","value":"redbfinalizer.redisenterpriseclusters.app.redislabs.com"}]'
```
note: In this case the REDB resources that were attached to the REC may still exist. see [REDB Deletion](#redb-deletion) for details on how to delete these REDBs.
