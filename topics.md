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
- [Operator Deployment Spec](#operator-deployment-spec)

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

### `WARNING`:
> PodSecurityPolicy is [deprecated](https://kubernetes.io/blog/2021/04/06/podsecuritypolicy-deprecation-past-present-and-future/) for Kubernetes v1.21+ and invalid for v1.25+.  
Users are advised to [migrate](https://kubernetes.io/docs/tasks/configure-pod-container/migrate-from-psp/) to [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) / [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) mechanism.

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

This content [has moved](https://docs.redis.com/latest/kubernetes/re-clusters/delete_custom_resources/) to the Redis Enterprise doc site, [docs.redis.com](https://docs.redis.com/latest/kubernetes/).

### REDB `redisVersion` field
The ‘redisVersion’ field is used for specifying Redis OSS version on REDB.
Possible values: `major` or `latest`.  
There are some important notes before using this field: 
* When using this field - it will always upgrade to the specified version (the database version will be upgraded to the most recent “major” or “latest” version respectively
) with some limitations:
    - The value must be compatible with `redisUpgradePolicy` on REC spec - if you use ‘latest’ for some REDBs - you must set `redisUpgradePolicy` in REC spec before.
    - If your database `auto_upgrade` field is set to `true`, it will automatically upgrade regardless the value in this field (`redisUpgradePolicy` on the REC).
> Note: With Redis operator versions older than 6.2.10, every REDB is created automatically with ‘auto_upgrade’ set to ‘true’.

> Any violation of these limitations may result in errors in the operator.

### Operator Deployment Spec  
* To increase the time before admission's liveness performing the first probe, you need to edit the deployment by running:
```
kubectl edit deployment redis-enterprise-operator
```
under the `spec` find the `admission` container - `livenessProbe` and edit the value of `initialDelaySeconds`:
```yaml
livenessProbe:
  ...
  ...
  initialDelaySeconds: <VALUE_YOU_CHOOSE>
  ...
```
Or you can run patch command -(here it sets its value to 20s, replace with the value you need)
> Note: Here the admission container's index is 1, replace with the admission container's index in your deployment.  
> You can run the command  
```kubectl get pod <REDIS_ENTERPRISE_OPERATOR_POD_NAME> -o jsonpath='{.spec.containers[*].name}' ```  
> and get the containers list
```
kubectl patch deployment redis-enterprise-operator  --type json   -p='[{"op": "replace", "path": "/spec/template/spec/containers/1/livenessProbe/initialDelaySeconds", "value":20}]'
```

## Handling password rotation using `/v1/users/password`
Currently, requests to `/v1/users/password` must be routed to the master node (this constraint may be dropped
in the future).
The default headless service created by the operator, however, has a pod selector corresponding with all cluster
nodes, master and non-masters alike. As a result, this service is not suitable for requests that must address
the master node directly, since they are not guaranteed to be routed to the pod running the master node.
In order to use `/v1/users/password` API endpoint, we recommend manually creating a headless
service similar to the default service created by the operator, with the addition of a master pod selector,
as in the following example:
```yaml
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: "2022-04-19T15:00:44Z"
  labels:
    app: redis-enterprise
    redis.io/cluster: <your cluster name>
  name: rec-master
spec:
  ...
  selector:
    app: redis-enterprise
    redis.io/cluster: rec
    redis.io/role: node
    redis.io/role-master: "1"
```

Sending `/v1/users/password` requests to the master node using this service should work fine.

## Host machine time zone propagation
You can propagate the host machine time zone by mounting `/etc/localtime` from the host
to all Redis Enterprise containers, using a hostPath volume.
Host time zone propagation is handled separately for operator deployment and the rest of the
Redis Enterprise pods (that include the services rigger).
To propagate host time zone to Redis Enterprise operator pod, you need to add a `hostPath` volume
manually before creating the deployment. Here is an example:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-enterprise-operator
spec:
  replicas: 1
  selector:
    matchLabels:
      name: redis-enterprise-operator
  template:
    metadata:
      labels:
        name: redis-enterprise-operator
    spec:
      serviceAccountName: redis-enterprise-operator
      volumes:
      - name: tz-volume
        hostPath:
          path: /etc/localtime
      containers:
        - name: redis-enterprise-operator
          ...
          volumeMounts:
          - mountPath: /etc/localtime
            name: tz-volume
        - name: admission
          ...
          volumeMounts:
          - mountPath: /etc/localtime
            name: tz-volume
```
Propagation of host time zone to all the rest of the pods is enabled by configuring the
`containerTimezone` property of the `RedisEnterpriseCluster`, as in the example below:
```
apiVersion: app.redislabs.com/v1
kind: RedisEnterpriseCluster
metadata:
  name: rec
spec:
  nodes: 3
  containerTimezone:
    propagateHost: {}
```
> Note that `propagateHost` is an empty struct, but must be included to enable host time zone propagation.

#### Possible restrictions on using `hostPath` volumes
Usage of `hostPath` volumes may be restricted by various mechanisms due to security considerations.
Depending on your setup, you may need to explicitly allow creation of pods with `hostPath` volumes by the operator.

For instance, OpenShift 4 users will need to modify the `redis-enterprise-scc` security context constraints (SCC) by
setting the value of `allowHostDirVolumePlugin` to `true` as in the following example:
```
apiVersion: security.openshift.io/v1
kind: SecurityContextConstraints
allowHostDirVolumePlugin: true
...
```
