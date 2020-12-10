# Redis Enterprise Cluster API
This document describes the parameters for the Redis Enterprise Cluster custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [ActiveActive](#activeactive)
  * [ImageSpec](#imagespec)
  * [Module](#module)
  * [PersistentConfigurationSpec](#persistentconfigurationspec)
  * [RedisEnterpriseCluster](#redisenterprisecluster)
  * [RedisEnterpriseClusterList](#redisenterpriseclusterlist)
  * [RedisEnterpriseClusterSpec](#redisenterpriseclusterspec)
  * [RedisEnterpriseClusterStatus](#redisenterpriseclusterstatus)
  * [ServicesRiggerConfigurationSpec](#servicesriggerconfigurationspec)
  * [SlaveHA](#slaveha)
  * [UpgradeSpec](#upgradespec)
* [Enums](#enums)
  * [ActiveActiveMethod](#activeactivemethod)
  * [ClusterEventReason](#clustereventreason)
  * [ClusterState](#clusterstate)
  * [SpecStatusName](#specstatusname)
## Objects

### ActiveActive


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| method | Used to distinguish between different platforms implementation | [ActiveActiveMethod](#activeactivemethod) |  | true |
| apiIngressUrl | RS API URL | string |  | true |
| dbIngressSuffix | DB ENDPOINT SUFFIX - will be used to set the db host ingress <db name><db ingress suffix>. Creates a host name so it should be unique if more than one db is created on the cluster with the same name | string |  | true |
| ingressAnnotations | Used for ingress controllers such as ha-proxy or nginx in GKE | map[string]string |  | false |
[Back to Table of Contents](#table-of-contents)

### ImageSpec
Image specification

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| repository | Repository | string |  | true |
| versionTag |  | string |  | true |
| imagePullPolicy |  | v1.PullPolicy |  | true |
[Back to Table of Contents](#table-of-contents)

### Module


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name |  | string |  | true |
| displayName |  | string |  | true |
| versions |  | []string |  | true |
[Back to Table of Contents](#table-of-contents)

### PersistentConfigurationSpec
Specification for Redis Enterprise Cluster persistence

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Whether to add persistent volume to Redis Enterprise pods | *bool | True | true |
| storageClassName | Storage class for persistent volume in Redis Enterprise pods Leave empty to use the default | string |  | true |
| volumeSize |  | resource.Quantity |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseCluster
RedisEnterpriseCluster is the Schema for the redisenterpriseclusters API

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#objectmeta-v1-meta) |  | false |
| spec |  | [RedisEnterpriseClusterSpec](#redisenterpriseclusterspec) |  | false |
| status |  | [RedisEnterpriseClusterStatus](#redisenterpriseclusterstatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseClusterList
RedisEnterpriseClusterList contains a list of RedisEnterpriseCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ListMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#listmeta-v1-meta) |  | false |
| items |  | [][RedisEnterpriseCluster](#redisenterprisecluster) |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseClusterSpec
RedisEnterpriseClusterSpec defines the desired state of RedisEnterpriseCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| nodes | Number of Redis Enterprise nodes (pods) | int32 | 3 | true |
| serviceAccountName | Name of the service account to use | string | RedisEnterpriseCluster's name | false |
| createServiceAccount | Whether to create service account | *bool | True | false |
| uiServiceType | Type of service used to expose Redis Enterprise UI (https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) | *v1.ServiceType | ClusterIP | false |
| uiAnnotations | Annotations for Redis Enterprise UI service | map[string]string |  | false |
| servicesRiggerSpec | Specification for service rigger | *[ServicesRiggerConfigurationSpec](#servicesriggerconfigurationspec) |  | false |
| license | Redis Enterprise License | string | Empty string which is a [Trial Mode licesne](https://docs.redislabs.com/latest/rs/administering/cluster-operations/settings/license-keys/#trial-mode) | false |
| username | Username for the admin user of Redis Enterprise | string | demo@redislabs.com | false |
| nodeSelector | Selector for nodes that could fit Redis Enterprise pod | *map[string]string |  | false |
| redisEnterpriseImageSpec | Specification for Redis Enterprise container image | *[ImageSpec](#imagespec) | the default Redis Enterprise image for this version | false |
| redisEnterpriseServicesRiggerImageSpec | Specification for Services Rigger container image | *[ImageSpec](#imagespec) | the default Services Rigger image for this version | false |
| bootstrapperImageSpec | Specification for Bootstrapper container image | *[ImageSpec](#imagespec) | the default Bootstrapper image for this version | false |
| redisEnterpriseNodeResources | Compute resource requirements for Redis Enterprise containers | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#resourcerequirements-v1-core) | 2 CPUs and 4GB memory | false |
| bootstrapperResources | Compute resource requirements for bootstrapper containers | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#resourcerequirements-v1-core) | 0.1 CPUs and 128Mi memory | false |
| redisEnterpriseServicesRiggerResources | Compute resource requirements for Services Rigger pod | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#resourcerequirements-v1-core) | 0.5 CPU and 0.5GB memory | false |
| pullSecrets | PullSecrets is an optional list of references to secrets in the same namespace to use for pulling any of the images. If specified, these secrets will be passed to individual puller implementations for them to use. More info: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/ | [][v1.LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#localobjectreference-v1-core) | empty | false |
| persistentSpec | Specification for Redis Enterprise Cluster persistence | [PersistentConfigurationSpec](#persistentconfigurationspec) |  | false |
| sideContainersSpec | Specification for a side container that will be added to each Redis Enterprise pod | []v1.Container | empty | false |
| extraLabels | Labels that the user defines for their convenience | map[string]string | empty | false |
| podAntiAffinity | Override for the default anti-affinity rules of the Redis Enterprise pods | *v1.PodAntiAffinity |  | false |
| antiAffinityAdditionalTopologyKeys | Additional antiAffinity terms in order to support installation on different zones/vcenters | []string |  | false |
| activeActive | Specification for ActiveActive setup | *[ActiveActive](#activeactive) |  | false |
| upgradeSpec | Specification for upgrades of Redis Enterprise | *[UpgradeSpec](#upgradespec) |  | false |
| podSecurityPolicyName | Name of pod security policy to use on pods See https://kubernetes.io/docs/concepts/policy/pod-security-policy/ | string | empty | false |
| enforceIPv4 | Sets ENFORCE_IPV4 environment variable | *bool | False | false |
| clusterRecovery | ClusterRecovery initiates cluster recovery when set to true. Note that this field is cleared automatically after the cluster is recovered | *bool |  | false |
| rackAwarenessNodeLabel | Node label that specifies rack ID - if specified, will create rack aware cluster. Rack awareness requires node label must exist on all nodes. Additionally, operator needs a special cluster role with permission to list nodes. | string |  | false |
| priorityClassName | Adds the priority class to pods managed by the operator | string |  | false |
| volumes | additional volumes | [][v1.Volume](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#volume-v1-core) |  | false |
| redisEnterpriseVolumeMounts | additional volume mounts within the redis enterprise containers | [][v1.VolumeMount](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#volumemount-v1-core) |  | false |
| podAnnotations | pod annotations | map[string]string |  | false |
| podTolerations | Tolerations that are added to all managed pods. for more information: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/ | [][v1.Toleration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#toleration-v1-core) | empty | false |
| slaveHA | Slave high availability mechanism configuration. | *[SlaveHA](#slaveha) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseClusterStatus
RedisEnterpriseClusterStatus defines the observed state of RedisEnterpriseCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| state | State of Redis Enterprise Cluster | [ClusterState](#clusterstate) |  | true |
| specStatus | Validity of Redis Enterprise Cluster specification | [SpecStatusName](#specstatusname) |  | true |
| modules | Modules Available in Cluster | [][Module](#module) |  | false |
[Back to Table of Contents](#table-of-contents)

### ServicesRiggerConfigurationSpec
Specification for service rigger

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| databaseServiceType | Service types for access to databases. should be a comma separated list. The possible values are cluster_ip, headless and load_balancer. | string | cluster_ip,headless | true |
| serviceNaming |  | string |  | true |
| extraEnvVars |  | []v1.EnvVar |  | false |
[Back to Table of Contents](#table-of-contents)

### SlaveHA


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| slaveHAGracePeriod | Time in seconds between when a node fails, and when slave high availability mechanism starts relocating shards. If set to 0, will not affect cluster configuration. | *uint32 | 1800 | true |
[Back to Table of Contents](#table-of-contents)

### UpgradeSpec
Specification for upgrades of Redis Enterprise

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| autoUpgradeRedisEnterprise | Whether to upgrade Redis Enterprise automatically when operator is upgraded | bool |  | true |
[Back to Table of Contents](#table-of-contents)
## Enums

### ActiveActiveMethod
Method of ingress from another cluster in Active-Active configuration

| Value | Description |
| ----- | ----------- |
| "openShiftRoute" | Routes are only usable in OpenShift |
| "ingress" | See https://kubernetes.io/docs/concepts/services-networking/ingress/ |
[Back to Table of Contents](#table-of-contents)

### ClusterEventReason
Reason for cluster event

| Value | Description |
| ----- | ----------- |
| "InvalidConfiguration" | Invalid Configuration |
| "StatusChange" | Status Change |
[Back to Table of Contents](#table-of-contents)

### ClusterState
State of the Redis Enterprise Cluster

| Value | Description |
| ----- | ----------- |
| "PendingCreation" | ClusterPendingCreate means cluster is not created yet |
| "BootstrappingFirstPod" | Bootstrapping first pod |
| "Initializing" | ClusterInitializing means the cluster was created and nodes are in the process of joining the cluster |
| "RecoveryReset" | ClusterRecoveryReset resets the cluster by deleting all pods |
| "RecoveringFirstPod" | ClusterRecoveringFirstPod means the cluster entered cluster recovery |
| "Running" | ClusterRunning means the cluster's sub-resources have been created and are in running state |
| "Error" | ClusterError means the there was an error when starting creating/updating the one or more of the cluster's resources |
| "Invalid" | ClusterConfigurationInvalid means an invalid spec was applied |
| "InvalidUpgrade" | ClusterInvalidUpgrade means an upgrade is not possible at this time |
| "Upgrade" | ClusterUpgrade |
[Back to Table of Contents](#table-of-contents)

### SpecStatusName
Whether the REC specification is valid (custom resource)

| Value | Description |
| ----- | ----------- |
| "Invalid" | Specification status invalid |
| "Valid" | Specification status valid |
[Back to Table of Contents](#table-of-contents)
