# Redis Enterprise Cluster API
This document describes the parameters for the Redis Enterprise Cluster custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [ActiveActive](#activeactive)
  * [BundledDatabaseVersions](#bundleddatabaseversions)
  * [ClusterCertificate](#clustercertificate)
  * [CmServer](#cmserver)
  * [CrdbCoordinator](#crdbcoordinator)
  * [CrdbWorker](#crdbworker)
  * [ImageSpec](#imagespec)
  * [LicenseStatus](#licensestatus)
  * [MdnsServer](#mdnsserver)
  * [Module](#module)
  * [OcspConfiguration](#ocspconfiguration)
  * [OcspStatus](#ocspstatus)
  * [PdnsServer](#pdnsserver)
  * [PersistentConfigurationSpec](#persistentconfigurationspec)
  * [RSClusterCertificates](#rsclustercertificates)
  * [RedisEnterpriseCluster](#redisenterprisecluster)
  * [RedisEnterpriseClusterList](#redisenterpriseclusterlist)
  * [RedisEnterpriseClusterSpec](#redisenterpriseclusterspec)
  * [RedisEnterpriseClusterStatus](#redisenterpriseclusterstatus)
  * [RedisEnterpriseServicesConfiguration](#redisenterpriseservicesconfiguration)
  * [RedisOnFlashSpec](#redisonflashspec)
  * [Saslauthd](#saslauthd)
  * [ServicesRiggerConfigurationSpec](#servicesriggerconfigurationspec)
  * [SlaveHA](#slaveha)
  * [StartingPolicy](#startingpolicy)
  * [StatsArchiver](#statsarchiver)
  * [UpgradeSpec](#upgradespec)
* [Enums](#enums)
  * [ActiveActiveMethod](#activeactivemethod)
  * [ClusterEventReason](#clustereventreason)
  * [ClusterState](#clusterstate)
  * [OperatingMode](#operatingmode)
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

### BundledDatabaseVersions


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| dbType |  | string |  | true |
| version |  | string |  | true |
[Back to Table of Contents](#table-of-contents)

### ClusterCertificate


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name |  | string |  | true |
| certificate |  | string |  | true |
| key |  | string |  | true |
[Back to Table of Contents](#table-of-contents)

### CmServer


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the CM server | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### CrdbCoordinator


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the crdb coordinator process | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### CrdbWorker


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the crdb worker processes | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### ImageSpec
Image specification

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| repository | Repository | string |  | true |
| versionTag |  | string |  | true |
| imagePullPolicy |  | v1.PullPolicy |  | true |
[Back to Table of Contents](#table-of-contents)

### LicenseStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| licenseState | Is the license expired | string |  | true |
| activationDate | When the license was activated | string |  | true |
| expirationDate | When the license will\has expired | string |  | true |
| shardsLimit | Number of redis shards allowed under this license | int32 |  | true |
[Back to Table of Contents](#table-of-contents)

### MdnsServer


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the Multicast DNS server | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### Module


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name |  | string |  | true |
| displayName |  | string |  | true |
| versions |  | []string |  | true |
[Back to Table of Contents](#table-of-contents)

### OcspConfiguration
An API object that represents the cluster's OCSP configuration

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| ocspFunctionality | Whether to enable/disable OCSP mechanism for the cluster. | *bool |  | false |
| queryFrequency | Determines the interval (in seconds) in which the control plane will poll the OCSP responder for a new status for the server certificate. Minimum value is 60. Maximum value is 86400. | *int |  | false |
| responseTimeout | Determines the time interval (in seconds) for which the request waits for a response from the OCSP responder. Minimum value is 1. Maximum value is 60. | *int |  | false |
| recoveryFrequency | Determines the interval (in seconds) in which the control plane will poll the OCSP responder for a new status for the server certificate when the current staple is invalid. Minimum value is 60. Maximum value is 86400. | *int |  | false |
| recoveryMaxTries | Determines the maximum number for the OCSP recovery attempts. After max number of tries passed, the control plane will revert back to the regular frequency. Minimum value is 1. Maximum value is 100. | *int |  | false |
[Back to Table of Contents](#table-of-contents)

### OcspStatus
An API object that represents the cluster's OCSP status

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| responderUrl | The OCSP responder url from which this status came from. | string |  | false |
| certStatus | Indicates the proxy certificate status - GOOD/REVOKED/UNKNOWN. | string |  | false |
| producedAt | The time at which the OCSP responder signed this response. | string |  | false |
| thisUpdate | The most recent time at which the status being indicated is known by the responder to have been correct. | string |  | false |
| nextUpdate | The time at or before which newer information will be available about the status of the certificate (if available) | string |  | false |
| revocationTime | The time at which the certificate was revoked or placed on hold. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### PdnsServer


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the pdns server | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### PersistentConfigurationSpec
Specification for Redis Enterprise Cluster persistence

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Whether to add persistent volume to Redis Enterprise pods | *bool | True | true |
| storageClassName | Storage class for persistent volume in Redis Enterprise pods Leave empty to use the default | string |  | true |
| volumeSize |  | resource.Quantity |  | true |
[Back to Table of Contents](#table-of-contents)

### RSClusterCertificates


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| apiCertificateSecretName | Secret Name/Path to use for Cluster's API Certificate. If left blank, will use certificate provided by the cluster. | string |  | false |
| cmCertificateSecretName | Secret Name/Path to use for Cluster's CM Certificate. If left blank, will use certificate provided by the cluster. | string |  | false |
| metricsExporterCertificateSecretName | Secret Name/Path to use for Cluster's Metrics Exporter Certificate. If left blank, will use certificate provided by the cluster. | string |  | false |
| proxyCertificateSecretName | Secret Name/Path to use for Cluster's Proxy Certificate. If left blank, will use certificate provided by the cluster. | string |  | false |
| syncerCertificateSecretName | Secret Name/Path to use for Cluster's Syncer Certificate. If left blank, will use certificate provided by the cluster. | string |  | false |
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
| redisEnterpriseAdditionalPodSpecAttributes | ADVANCED USAGE USE AT YOUR OWN RISK - specify pod attributes that are required for the statefulset - Redis Enterprise pods. Pod attributes managed by the operator might override these settings. Also make sure the attributes are supported by the K8s version running on the cluster - the operator does not validate that. | *[v1.PodSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#podspec-v1-core) |  | false |
| license | Redis Enterprise License | string | Empty string which is a [Trial Mode licesne](https://docs.redislabs.com/latest/rs/administering/cluster-operations/settings/license-keys/#trial-mode) | false |
| licenseSecretName | K8s secret or Vault Secret Name/Path to use for Cluster License. When left blank, the license is read from the \"license\" field. Note that you can't specify non-empty values in both \"license\" and \"licenseSecretName\", only one of these fields can be used to pass the license string. The license needs to be stored under the key \"license\". | string | Empty string | false |
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
| extraLabels | Labels that the user defines for their convenience. Note that Persistent Volume Claims would only be labeled with the extra labels specified during the cluster's creation (modifying this field when the cluster is running won't affect the Persistent Volume | map[string]string | empty | false |
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
| clusterCredentialSecretName | Secret Name/Path to use for Cluster Credentials.  If left blank, will use cluster name | string |  | false |
| clusterCredentialSecretType | Type of Secret to use for ClusterCredential: vault, kubernetes,... If left blank, will default to kubernetes secrets | string |  | true |
| clusterCredentialSecretRole | Used only if ClusterCredentialSecretType is vault, to define vault role to be used.  If blank, defaults to \"redis-enterprise-rec\" | string |  | true |
| vaultCASecret | K8s secret name containing Vault's CA cert - defaults to \"vault-ca-cert\" | string |  | false |
| redisEnterpriseServicesConfiguration | RS Cluster optional services settings. Note that when disabling the CM Server service, the cluster's UI Service will be removed from the k8s cluster | *[RedisEnterpriseServicesConfiguration](#redisenterpriseservicesconfiguration) |  | false |
| dataInternodeEncryption | Internode encryption (INE) cluster wide policy. An optional boolean setting. Specifies if INE should be on/off for new created REDBs. May be overridden for specific REDB via similar setting, please view the similar setting for REDB for more info. | *bool |  | false |
| redisUpgradePolicy | Redis upgrade policy to be set on the Redis Enterprise Cluster. Possible values: major/latest This value is used by the cluster to choose the Redis version of the database when an upgrade is performed. The Redis Enterprise Cluster includes multiple versions of OSS Redis that can be used for databases. | string |  | false |
| certificates | RS Cluster Certificates. Used to modify the certificates used by the cluster. See the \"RSClusterCertificates\" struct described above to see the supported certificates. | *[RSClusterCertificates](#rsclustercertificates) |  | false |
| podStartingPolicy | Mitigation setting for STS pods stuck in \"ContainerCreating\" | *[StartingPolicy](#startingpolicy) |  | false |
| redisEnterpriseTerminationGracePeriodSeconds | The TerminationGracePeriodSeconds value for the (STS created) REC pods. Note that pods should not be taken down intentionally by force. Because clean pod shutdown is essential to prevent data loss, the default value is intentionally large (1 year). When data loss is acceptable (such as pure caching configurations), a value of a few minutes may be acceptable. | *int64 | 31536000 | false |
| redisOnFlashSpec | Stores configurations specific to redis on flash. If provided, the cluster will be capable of creating redis on flash databases. | *[RedisOnFlashSpec](#redisonflashspec) |  | false |
| ocspConfiguration | An API object that represents the cluster's OCSP configuration. To enable OCSP, the cluster's proxy certificate should contain the OCSP responder URL. Note: This is an ALPHA Feature. For this feature to take effect, set a boolean environment variable with the name \"ENABLE_ALPHA_FEATURES\" to True. This variable can be set via the redis-enterprise-operator pod spec, or through the operator-environment-config Config Map. | *[OcspConfiguration](#ocspconfiguration) |  | false |
| encryptPkeys | Private key encryption - in order to enable, first need to mount ${ephemeralconfdir}/secrets/pem/passphrase and add the passphrase and then set fields value to 'true' Possible values: true/false Note: This is an ALPHA Feature. For this feature to take effect, set a boolean environment variable with the name \"ENABLE_ALPHA_FEATURES\" to True. This variable can be set via the redis-enterprise-operator pod spec, or through the operator-environment-config Config Map. | *bool |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseClusterStatus
RedisEnterpriseClusterStatus defines the observed state of RedisEnterpriseCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| state | State of Redis Enterprise Cluster | [ClusterState](#clusterstate) |  | true |
| specStatus | Validity of Redis Enterprise Cluster specification | [SpecStatusName](#specstatusname) |  | true |
| modules | Modules Available in Cluster | [][Module](#module) |  | false |
| licenseStatus | State of the Cluster's License | *[LicenseStatus](#licensestatus) |  | false |
| bundledDatabaseVersions | Versions of open source databases bundled by Redis Enterprise Software - please note that in order to use a specific version it should be supported by the ‘upgradePolicy’ - ‘major’ or ‘latest’ according to the desired version (major/minor) | []*[BundledDatabaseVersions](#bundleddatabaseversions) |  | false |
| ocspStatus | An API object that represents the cluster's OCSP status | *[OcspStatus](#ocspstatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseServicesConfiguration


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| mdnsServer |  | *[MdnsServer](#mdnsserver) |  | false |
| cmServer |  | *[CmServer](#cmserver) |  | false |
| statsArchiver |  | *[StatsArchiver](#statsarchiver) |  | false |
| saslauthd |  | *[Saslauthd](#saslauthd) |  | false |
| pdnsServer |  | *[PdnsServer](#pdnsserver) |  | false |
| crdbCoordinator |  | *[CrdbCoordinator](#crdbcoordinator) |  | false |
| crdbWorker |  | *[CrdbWorker](#crdbworker) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisOnFlashSpec
RedisOnFlashSpec contains all the parameters needed to configure in order to enable creation of redis on flash databases.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Indicates whether RoF is turned on or not. | bool |  | true |
| flashStorageEngine | The type of DB engine used on flash. Currently the only supported value is \"rocksdb\", but this will change in the figure. | string |  | true |
| storageClassName | Used to identify the storage class name of the corresponding volume claim template. | string |  | true |
| flashDiskSize | Required flash disk size. | resource.Quantity |  | false |
[Back to Table of Contents](#table-of-contents)

### Saslauthd


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the saslauthd service | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### ServicesRiggerConfigurationSpec
Specification for service rigger

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| databaseServiceType | Service types for access to databases. should be a comma separated list. The possible values are cluster_ip, headless and load_balancer. | string | cluster_ip,headless | true |
| serviceNaming |  | string |  | true |
| extraEnvVars |  | []v1.EnvVar |  | false |
| servicesRiggerAdditionalPodSpecAttributes | ADVANCED USAGE USE AT YOUR OWN RISK - specify pod attributes that are required for the rigger deployment pod. Pod attributes managed by the operator might override these settings (Containers, serviceAccountName, podTolerations, ImagePullSecrets, nodeSelector, PriorityClassName, PodSecurityContext). Also make sure the attributes are supported by the K8s version running on the cluster - the operator does not validate that. | *[v1.PodSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#podspec-v1-core) |  | false |
[Back to Table of Contents](#table-of-contents)

### SlaveHA


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| slaveHAGracePeriod | Time in seconds between when a node fails, and when slave high availability mechanism starts relocating shards. If set to 0, will not affect cluster configuration. | *uint32 | 1800 | true |
[Back to Table of Contents](#table-of-contents)

### StartingPolicy


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Whether to detect and attempt to mitigate pod startup issues | *bool | False | true |
| startingThresholdSeconds | Time in seconds to wait for a pod to be stuck while starting up before action is taken. If set to 0, will be treated as if disabled. | *uint32 | 540 | true |
[Back to Table of Contents](#table-of-contents)

### StatsArchiver


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the stats archiver service | [OperatingMode](#operatingmode) |  | true |
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
| "Deleting" | ClusterDeleting |
| "ClusterRecreating" | ClusterRecreating - similar to ClusterRecoveryReset - delete all pods before recreation of the cluster. |
[Back to Table of Contents](#table-of-contents)

### OperatingMode

| Value | Description |
| ----- | ----------- |
| "enabled" |  |
| "disabled" |  |
[Back to Table of Contents](#table-of-contents)

### SpecStatusName
Whether the REC specification is valid (custom resource)

| Value | Description |
| ----- | ----------- |
| "Invalid" | Specification status invalid |
| "Valid" | Specification status valid |
[Back to Table of Contents](#table-of-contents)
