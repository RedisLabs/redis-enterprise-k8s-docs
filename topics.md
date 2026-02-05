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

This content has moved to [docs.redis.com](https://docs.redis.com/latest); see [Manage pod stability](https://docs.redis.com/latest/kubernetes/recommendations/pod-stability/).

## Priority Class

This content has moved to [docs.redis.com](https://docs.redis.com/latest); see [Manage pod stability](https://docs.redis.com/latest/kubernetes/recommendations/pod-stability/).

## Node Pool

This content has moved to [docs.redis.com](https://docs.redis.com); see [Control node selection](https://docs.redis.com/latest/kubernetes/recommendations/node-selection/).

## K8s Out of Resource Handling recommendations

We highly recommend reading [k8s documentation of out of resource administration](https://kubernetes.io/docs/tasks/administer-cluster/out-of-resource).

### Monitoring

This content has moved to [docs.redis.com](https://docs.redis.com); see [Manage node resources](https://docs.redis.com/latest/kubernetes/recommendations/node-resources/).

### Eviction Thresholds

This content has moved to [docs.redis.com](https://docs.redis.com); see [Manage node resources](https://docs.redis.com/latest/kubernetes/recommendations/node-resources/).
 
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

This content has moved to [docs.redis.com](https://docs.redis.com); see [Manage node resources](https://docs.redis.com/latest/kubernetes/recommendations/node-resources/).

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
  labels:
    app: redis-enterprise
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
