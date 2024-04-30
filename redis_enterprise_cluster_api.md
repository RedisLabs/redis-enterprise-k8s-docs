# Redis Enterprise Cluster API
This document describes the parameters for the Redis Enterprise Cluster custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [APIServiceSpec](#apiservicespec)
  * [ActiveActive](#activeactive)
  * [BundledDatabaseRedisVersions](#bundleddatabaseredisversions)
  * [BundledDatabaseVersions](#bundleddatabaseversions)
  * [ClusterCertificate](#clustercertificate)
  * [CmServer](#cmserver)
  * [ContainerTimezoneSpec](#containertimezonespec)
  * [CrdbCoordinator](#crdbcoordinator)
  * [CrdbWorker](#crdbworker)
  * [ImageSpec](#imagespec)
  * [IngressOrRouteSpec](#ingressorroutespec)
  * [LDAPAuthenticationQuery](#ldapauthenticationquery)
  * [LDAPAuthorizationQuery](#ldapauthorizationquery)
  * [LDAPQuery](#ldapquery)
  * [LDAPServer](#ldapserver)
  * [LDAPSpec](#ldapspec)
  * [LicenseStatus](#licensestatus)
  * [ManagedAPIs](#managedapis)
  * [MdnsServer](#mdnsserver)
  * [Module](#module)
  * [OcspConfiguration](#ocspconfiguration)
  * [OcspStatus](#ocspstatus)
  * [PdnsServer](#pdnsserver)
  * [PersistenceStatus](#persistencestatus)
  * [PersistentConfigurationSpec](#persistentconfigurationspec)
  * [PropagateHost](#propagatehost)
  * [RSClusterCertificates](#rsclustercertificates)
  * [RedisEnterpriseCluster](#redisenterprisecluster)
  * [RedisEnterpriseClusterList](#redisenterpriseclusterlist)
  * [RedisEnterpriseClusterSpec](#redisenterpriseclusterspec)
  * [RedisEnterpriseClusterStatus](#redisenterpriseclusterstatus)
  * [RedisEnterpriseServicesConfiguration](#redisenterpriseservicesconfiguration)
  * [RedisOnFlashSpec](#redisonflashspec)
  * [Saslauthd](#saslauthd)
  * [Services](#services)
  * [ServicesRiggerConfigurationSpec](#servicesriggerconfigurationspec)
  * [SlaveHA](#slaveha)
  * [StartingPolicy](#startingpolicy)
  * [StatsArchiver](#statsarchiver)
  * [UpgradeSpec](#upgradespec)
* [Enums](#enums)
  * [ClusterState](#clusterstate)
  * [IngressMethod](#ingressmethod)
  * [LDAPProtocol](#ldapprotocol)
  * [LDAPSearchScope](#ldapsearchscope)
  * [OperatingMode](#operatingmode)
  * [PvcStatus](#pvcstatus)
  * [RedisOnFlashsStorageEngine](#redisonflashsstorageengine)
  * [ServiceType](#servicetype)
  * [SpecStatusName](#specstatusname)
## Objects

### APIServiceSpec
Customization options for the REC API service.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| type | Type of service to create for the REC API service. Defaults to ClusterIP service, if not specified otherwise. | *[ServiceType](#servicetype) | ClusterIP | false |
[Back to Table of Contents](#table-of-contents)

### ActiveActive


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| method | Used to distinguish between different platforms implementation | [IngressMethod](#ingressmethod) |  | true |
| apiIngressUrl | RS API URL | string |  | true |
| dbIngressSuffix | DB ENDPOINT SUFFIX - will be used to set the db host ingress <db name><db ingress suffix>. Creates a host name so it should be unique if more than one db is created on the cluster with the same name | string |  | true |
| ingressAnnotations | Used for ingress controllers such as ha-proxy or nginx in GKE | map[string]string |  | false |
[Back to Table of Contents](#table-of-contents)

### BundledDatabaseRedisVersions


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| version |  | string |  | true |
| major |  | bool |  | true |
[Back to Table of Contents](#table-of-contents)

### BundledDatabaseVersions


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| dbType |  | string |  | true |
| version |  | string |  | true |
| major |  | bool |  | false |
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

### ContainerTimezoneSpec
Used to set the timezone across all redis enterprise containers - You can either propagate the hosts timezone to RS pods or set it manually via timezoneName.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| propagateHost | Identifies that container timezone should be in sync with the host, this option mounts a hostPath volume onto RS pods that could be restricted in some systems. | *[PropagateHost](#propagatehost) |  | false |
| timezoneName | POSIX-style timezone name as a string to be passed as EnvVar to RE pods, e.g. "Europe/London". | string |  | false |
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
| repository | The repository (name) of the container image to be deployed. | string |  | true |
| versionTag | The tag of the container image to be deployed. | string |  | true |
| digestHash | The digest hash of the container image to pull. When specified, the container image is pulled according to the digest hash instead of the image tag. The versionTag field must also be specified with the image tag matching this digest hash. Note: This field is only supported for OLM deployments. | string |  | false |
| imagePullPolicy | The image pull policy to be applied to the container image. One of Always, Never, IfNotPresent. | v1.PullPolicy |  | true |
[Back to Table of Contents](#table-of-contents)

### IngressOrRouteSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| method | Used to distinguish between different platforms implementation. | [IngressMethod](#ingressmethod) |  | true |
| apiFqdnUrl | RS API URL | string |  | true |
| dbFqdnSuffix | DB ENDPOINT SUFFIX - will be used to set the db host ingress <db name><db fqdn suffix>. Creates a host name so it should be unique if more than one db is created on the cluster with the same name | string |  | true |
| ingressAnnotations | Additional annotations to set on ingress resources created by the operator | map[string]string |  | false |
[Back to Table of Contents](#table-of-contents)

### LDAPAuthenticationQuery
Configuration of LDAP authentication queries

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| template | Configuration for a template query. Mutually exclusive with the 'query' field. The substring '%u' will be replaced with the username, e.g., 'cn=%u,ou=dev,dc=example,dc=com'. | *string |  | false |
| query | Configuration for a search query. Mutually exclusive with the 'template' field. The substring '%u' in the query filter will be replaced with the username. | *[LDAPQuery](#ldapquery) |  | false |
[Back to Table of Contents](#table-of-contents)

### LDAPAuthorizationQuery
Configuration of LDAP authorization queries

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| attribute | Configuration for an attribute query. Mutually exclusive with the 'query' field. Holds the name of an attribute of the LDAP user entity that contains a list of the groups that the user belongs to. e.g., 'memberOf'. | *string |  | false |
| query | Configuration for a search query. Mutually exclusive with the 'attribute' field. The substring '%D' in the query filter will be replaced with the user's Distinguished Name. | *[LDAPQuery](#ldapquery) |  | false |
[Back to Table of Contents](#table-of-contents)

### LDAPQuery
Configuration for an LDAP search query.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| base | The Distinguished Name of the entry at which to start the search, e.g., 'ou=dev,dc=example,dc=com'. | string |  | true |
| filter | An RFC-4515 string representation of the filter to apply in the search. For an authentication query, the substring '%u' will be replaced with the username, e.g., '(cn=%u)'. For an authorization query, the substring '%D' will be replaced with the user's Distinguished Name, e.g., '(members=%D)'. | string |  | true |
| scope | The search scope for an LDAP query. One of: BaseObject, SingleLevel, WholeSubtree | [LDAPSearchScope](#ldapsearchscope) |  | true |
[Back to Table of Contents](#table-of-contents)

### LDAPServer
Address of an LDAP server.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| host | Host name of the LDAP server | string |  | true |
| port | Port number of the LDAP server. If unspecified, defaults to 389 for LDAP and STARTTLS protocols, and 636 for LDAPS protocol. | *uint32 |  | false |
[Back to Table of Contents](#table-of-contents)

### LDAPSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| protocol | Specifies the LDAP protocol to use. One of: LDAP, LDAPS, STARTTLS. | [LDAPProtocol](#ldapprotocol) |  | true |
| servers | One or more LDAP servers. If multiple servers are specified, they must all share an identical organization tree structure. | [][LDAPServer](#ldapserver) |  | true |
| bindCredentialsSecretName | Name of a secret within the same namespace, holding the credentials used to communicate with the LDAP server for authentication queries. The secret must have a key named 'dn' with the Distinguished Name of the user to execute the query, and 'password' with its password. If left blank, credentials-based authentication is disabled. | *string |  | false |
| caCertificateSecretName | Name of a secret within the same namespace, holding a PEM-encoded CA certificate for validating the TLS connection to the LDAP server. The secret must have a key named 'cert' with the certificate data. This field is applicable only when the protocol is LDAPS or STARTTLS. | *string |  | false |
| enabledForControlPlane | Whether to enable LDAP for control plane access. Disabled by default. | bool |  | false |
| enabledForDataPlane | Whether to enable LDAP for data plane access. Disabled by default. | bool |  | false |
| cacheTTLSeconds | The maximum TTL of cached entries. | *int |  | false |
| authenticationQuery | Configuration of authentication queries, mapping between the username, provided to the cluster for authentication, and the LDAP Distinguished Name. | [LDAPAuthenticationQuery](#ldapauthenticationquery) |  | true |
| authorizationQuery | Configuration of authorization queries, mapping between a user's Distinguished Name and its group memberships. | [LDAPAuthorizationQuery](#ldapauthorizationquery) |  | true |
[Back to Table of Contents](#table-of-contents)

### LicenseStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| licenseState | Is the license expired | string |  | true |
| activationDate | When the license was activated | string |  | true |
| expirationDate | When the license will\has expired | string |  | true |
| shardsLimit | Number of redis shards allowed under this license | int32 |  | true |
[Back to Table of Contents](#table-of-contents)

### ManagedAPIs
Indicates cluster APIs that are being managed by the operator. This only applies to cluster APIs which are optionally-managed by the operator, such as cluster LDAP configuration. Most other APIs are automatically managed by the operator, and are not listed here.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| ldap | Indicate whether cluster LDAP configuration is managed by the operator. When this is enabled, the operator will reconcile the cluster LDAP configuration according to the '.spec.ldap' field in the RedisEnterpriseCluster resource. | *bool |  | false |
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

### PersistenceStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| status | The current status of the PVCs | [PvcStatus](#pvcstatus) |  | false |
| succeeded | The number of PVCs that are provisioned with the expected size | string |  | false |
[Back to Table of Contents](#table-of-contents)

### PersistentConfigurationSpec
Specification for Redis Enterprise Cluster persistence

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Whether to add persistent volume to Redis Enterprise pods | *bool | True | true |
| storageClassName | Storage class for persistent volume in Redis Enterprise pods. Leave empty to use the default. If using the default this way, make sure the Kubernetes Cluster has a default Storage Class configured. This can be done by running a `kubectl get storageclass` and see if one of the Storage Classes' names contains a `(default)` mark. | string |  | true |
| volumeSize | To enable resizing after creating the cluster - please follow the instructions in the pvc_expansion readme | resource.Quantity |  | true |
| enablePersistentVolumeResize | Whether to enable PersistentVolumes resize. Disabled by default. Read the instruction in pvc_expansion readme carefully before using this feature. | *bool |  | false |
[Back to Table of Contents](#table-of-contents)

### PropagateHost
Used to specify that the timezone is configured to match the host machine timezone.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
[Back to Table of Contents](#table-of-contents)

### RSClusterCertificates


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| apiCertificateSecretName | Secret name to use for cluster's API certificate. If left blank, a cluster-provided certificate will be used. | string |  | false |
| cmCertificateSecretName | Secret name to use for cluster's CM (Cluster Manager) certificate. If left blank, a cluster-provided certificate will be used. | string |  | false |
| metricsExporterCertificateSecretName | Secret name to use for cluster's Metrics Exporter certificate. If left blank, a cluster-provided certificate will be used. | string |  | false |
| proxyCertificateSecretName | Secret name to use for cluster's Proxy certificate. If left blank, a cluster-provided certificate will be used. | string |  | false |
| syncerCertificateSecretName | Secret name to use for cluster's Syncer certificate. If left blank, a cluster-provided certificate will be used. | string |  | false |
| ldapClientCertificateSecretName | Secret name to use for cluster's LDAP client certificate. If left blank, LDAP client certificate authentication will be disabled. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseCluster
RedisEnterpriseCluster is the Schema for the redisenterpriseclusters API

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#objectmeta-v1-meta) |  | false |
| spec |  | [RedisEnterpriseClusterSpec](#redisenterpriseclusterspec) |  | false |
| status |  | [RedisEnterpriseClusterStatus](#redisenterpriseclusterstatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseClusterList
RedisEnterpriseClusterList contains a list of RedisEnterpriseCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ListMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#listmeta-v1-meta) |  | false |
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
| redisEnterpriseAdditionalPodSpecAttributes | ADVANCED USAGE USE AT YOUR OWN RISK - specify pod attributes that are required for the statefulset - Redis Enterprise pods. Pod attributes managed by the operator might override these settings. Also make sure the attributes are supported by the K8s version running on the cluster - the operator does not validate that. | *[v1.PodSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#podspec-v1-core) |  | false |
| license | Redis Enterprise License | string | Empty string which is a [Trial Mode licesne](https://docs.redislabs.com/latest/rs/administering/cluster-operations/settings/license-keys/#trial-mode) | false |
| licenseSecretName | K8s secret or Vault Secret Name/Path to use for Cluster License. When left blank, the license is read from the "license" field. Note that you can't specify non-empty values in both "license" and "licenseSecretName", only one of these fields can be used to pass the license string. The license needs to be stored under the key "license". | string | Empty string | false |
| username | Username for the admin user of Redis Enterprise | string | demo@redis.com | false |
| nodeSelector | Selector for nodes that could fit Redis Enterprise pod | *map[string]string |  | false |
| redisEnterpriseImageSpec | Specification for Redis Enterprise container image | *[ImageSpec](#imagespec) | the default Redis Enterprise image for this version | false |
| redisEnterpriseServicesRiggerImageSpec | Specification for Services Rigger container image | *[ImageSpec](#imagespec) | the default Services Rigger image for this version | false |
| bootstrapperImageSpec | Specification for Bootstrapper container image | *[ImageSpec](#imagespec) | the default Bootstrapper image for this version | false |
| redisEnterpriseNodeResources | Compute resource requirements for Redis Enterprise containers | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 2 CPUs and 4GB memory | false |
| bootstrapperResources | Compute resource requirements for bootstrapper containers | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 0.1 CPUs and 128Mi memory | false |
| redisEnterpriseServicesRiggerResources | Compute resource requirements for Services Rigger pod | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 0.5 CPU and 0.5GB memory | false |
| pullSecrets | PullSecrets is an optional list of references to secrets in the same namespace to use for pulling any of the images. If specified, these secrets will be passed to individual puller implementations for them to use. More info: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/ | [][v1.LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#localobjectreference-v1-core) | empty | false |
| persistentSpec | Specification for Redis Enterprise Cluster persistence | [PersistentConfigurationSpec](#persistentconfigurationspec) |  | false |
| sideContainersSpec | Specification for a side container that will be added to each Redis Enterprise pod | []v1.Container | empty | false |
| extraLabels | Labels that the user defines for their convenience. Note that Persistent Volume Claims would only be labeled with the extra labels specified during the cluster's creation (modifying this field when the cluster is running won't affect the Persistent Volume | map[string]string | empty | false |
| podAntiAffinity | Override for the default anti-affinity rules of the Redis Enterprise pods | *v1.PodAntiAffinity |  | false |
| antiAffinityAdditionalTopologyKeys | Additional antiAffinity terms in order to support installation on different zones/vcenters | []string |  | false |
| activeActive | Specification for ActiveActive setup. At most one of ingressOrRouteSpec or activeActive fields can be set at the same time. | *[ActiveActive](#activeactive) |  | false |
| upgradeSpec | Specification for upgrades of Redis Enterprise | *[UpgradeSpec](#upgradespec) |  | false |
| podSecurityPolicyName | DEPRECATED PodSecurityPolicy support is removed in Kubernetes v1.25 and the use of this field is invalid for use when running on Kubernetes v1.25+. Future versions of the RedisEnterpriseCluster API will remove support for this field altogether. For migration instructions, see https://kubernetes.io/docs/tasks/configure-pod-container/migrate-from-psp/\n\nName of pod security policy to use on pods | string | empty | false |
| enforceIPv4 | Sets ENFORCE_IPV4 environment variable | *bool | False | false |
| clusterRecovery | ClusterRecovery initiates cluster recovery when set to true. Note that this field is cleared automatically after the cluster is recovered | *bool |  | false |
| rackAwarenessNodeLabel | Node label that specifies rack ID - if specified, will create rack aware cluster. Rack awareness requires node label must exist on all nodes. Additionally, operator needs a special cluster role with permission to list nodes. | string |  | false |
| priorityClassName | Adds the priority class to pods managed by the operator | string |  | false |
| hostAliases | Adds hostAliases entries to the Redis Enterprise pods | []v1.HostAlias |  | false |
| volumes | additional volumes | [][v1.Volume](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#volume-v1-core) |  | false |
| redisEnterpriseVolumeMounts | additional volume mounts within the redis enterprise containers | [][v1.VolumeMount](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#volumemount-v1-core) |  | false |
| podAnnotations | annotations for the service rigger and redis enterprise pods | map[string]string |  | false |
| redisEnterprisePodAnnotations | annotations for redis enterprise pod | map[string]string |  | false |
| podTolerations | Tolerations that are added to all managed pods. for more information: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/ | [][v1.Toleration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#toleration-v1-core) | empty | false |
| slaveHA | Slave high availability mechanism configuration. | *[SlaveHA](#slaveha) |  | false |
| clusterCredentialSecretName | Secret Name/Path to use for Cluster Credentials. To be used only if ClusterCredentialSecretType is vault. If left blank, will use cluster name. | string |  | false |
| clusterCredentialSecretType | Type of Secret to use for ClusterCredential: vault, kubernetes,... If left blank, will default to kubernetes secrets | string |  | true |
| clusterCredentialSecretRole | Used only if ClusterCredentialSecretType is vault, to define vault role to be used.  If blank, defaults to "redis-enterprise-rec" | string |  | true |
| vaultCASecret | K8s secret name containing Vault's CA cert - defaults to "vault-ca-cert" | string |  | false |
| redisEnterpriseServicesConfiguration | RS Cluster optional services settings. Notes: When disabling the CM Server service, the cluster's UI Service will be removed from the k8s cluster. Also the saslauthd entry is deprecated and will be removed (the service was already removed from the cluster and is always disabled). | *[RedisEnterpriseServicesConfiguration](#redisenterpriseservicesconfiguration) |  | false |
| dataInternodeEncryption | Internode encryption (INE) cluster wide policy. An optional boolean setting. Specifies if INE should be on/off for new created REDBs. May be overridden for specific REDB via similar setting, please view the similar setting for REDB for more info. | *bool |  | false |
| redisUpgradePolicy | Redis upgrade policy to be set on the Redis Enterprise Cluster. Possible values: major/latest This value is used by the cluster to choose the Redis version of the database when an upgrade is performed. The Redis Enterprise Cluster includes multiple versions of OSS Redis that can be used for databases. | string |  | false |
| certificates | RS Cluster Certificates. Used to modify the certificates used by the cluster. See the "RSClusterCertificates" struct described above to see the supported certificates. | *[RSClusterCertificates](#rsclustercertificates) |  | false |
| podStartingPolicy | Mitigation setting for STS pods stuck in "ContainerCreating" | *[StartingPolicy](#startingpolicy) |  | false |
| redisEnterpriseTerminationGracePeriodSeconds | The TerminationGracePeriodSeconds value for the (STS created) REC pods. Note that pods should not be taken down intentionally by force. Because clean pod shutdown is essential to prevent data loss, the default value is intentionally large (1 year). When data loss is acceptable (such as pure caching configurations), a value of a few minutes may be acceptable. | *int64 | 31536000 | false |
| redisOnFlashSpec | Stores configurations specific to redis on flash. If provided, the cluster will be capable of creating redis on flash databases. | *[RedisOnFlashSpec](#redisonflashspec) |  | false |
| ocspConfiguration | An API object that represents the cluster's OCSP configuration. To enable OCSP, the cluster's proxy certificate should contain the OCSP responder URL. | *[OcspConfiguration](#ocspconfiguration) |  | false |
| encryptPkeys | Private key encryption Possible values: true/false | *bool |  | false |
| redisEnterpriseIPFamily | When the operator is running in a dual-stack environment (both IPv4 and IPv6 network interfaces are available), specifies the IP family of the network interface that will be used by the Redis Enterprise Cluster, as well as services created by the operator (API, UI, Prometheus services). | v1.IPFamily |  | false |
| containerTimezone | Container timezone configuration. While the default timezone on all containers is UTC, this setting can be used to set the timezone on services rigger/bootstrapper/RS containers. Currently the only supported value is to propagate the host timezone to all containers. | *[ContainerTimezoneSpec](#containertimezonespec) |  | false |
| ingressOrRouteSpec | Access configurations for the Redis Enterprise Cluster and Databases. At most one of ingressOrRouteSpec or activeActive fields can be set at the same time. | *[IngressOrRouteSpec](#ingressorroutespec) |  | false |
| services | Customization options for operator-managed service resources created for Redis Enterprise clusters and databases | *[Services](#services) |  | false |
| ldap | Cluster-level LDAP configuration, such as server addresses, protocol, authentication and query settings. | *[LDAPSpec](#ldapspec) |  | false |
| extraEnvVars | ADVANCED USAGE: use carefully. Add environment variables to RS StatefulSet's containers. | []v1.EnvVar |  | false |
| resp3Default | Whether databases will turn on RESP3 compatibility upon database upgrade. Note - Deleting this property after explicitly setting its value shall have no effect. Please view the corresponding field in RS doc for more info. | *bool |  | false |
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
| managedAPIs | Indicates cluster APIs that are being managed by the operator. This only applies to cluster APIs which are optionally-managed by the operator, such as cluster LDAP configuration. Most other APIs are automatically managed by the operator, and are not listed here. | *[ManagedAPIs](#managedapis) |  | false |
| ingressOrRouteMethodStatus | The ingressOrRouteSpec/ActiveActive spec method that exist | [IngressMethod](#ingressmethod) |  | false |
| redisEnterpriseIPFamily | The chosen IP family of the cluster if was specified in REC spec. | v1.IPFamily |  | false |
| persistenceStatus | The status of the Persistent Volume Claims that are used for Redis Enterprise Cluster persistence. The status will correspond to the status of one or more of the PVCs (failed/resizing if one of them is in resize or failed to resize) | [PersistenceStatus](#persistencestatus) |  | false |
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
| flashStorageEngine | The type of DB engine used on flash. This field is DEPRECATED, if you wish to change the driver from RocksDB to Speedb use bigStoreDriver | [RedisOnFlashsStorageEngine](#redisonflashsstorageengine) |  | false |
| storageClassName | Used to identify the storage class name of the corresponding volume claim template. | string |  | true |
| flashDiskSize | Required flash disk size. | resource.Quantity |  | false |
| bigStoreDriver | Used to change the bigstore_driver when REC is up and running. | [RedisOnFlashsStorageEngine](#redisonflashsstorageengine) |  | false |
[Back to Table of Contents](#table-of-contents)

### Saslauthd


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the saslauthd service | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### Services
Customization options for operator-managed service resources created for Redis Enterprise clusters and databases

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| servicesAnnotations | Global additional annotations to set on service resources created by the operator. The specified annotations will not override annotations that already exist and didn't originate from the operator. | map[string]string |  | false |
| apiService | Customization options for the REC API service. | *[APIServiceSpec](#apiservicespec) |  | false |
[Back to Table of Contents](#table-of-contents)

### ServicesRiggerConfigurationSpec
Specification for service rigger

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| databaseServiceType | Service types for access to databases. should be a comma separated list. The possible values are cluster_ip, headless and load_balancer. | string | cluster_ip,headless | true |
| serviceNaming | Used to determine how to name the services created automatically when a database is created. When bdb_name is used, the database name will be also used for the service name. When redis-port is used, the service will be named redis-<port> | string | bdb_name | true |
| extraEnvVars |  | []v1.EnvVar |  | false |
| servicesRiggerAdditionalPodSpecAttributes | ADVANCED USAGE USE AT YOUR OWN RISK - specify pod attributes that are required for the rigger deployment pod. Pod attributes managed by the operator might override these settings (Containers, serviceAccountName, podTolerations, ImagePullSecrets, nodeSelector, PriorityClassName, PodSecurityContext). Also make sure the attributes are supported by the K8s version running on the cluster - the operator does not validate that. | *[v1.PodSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#podspec-v1-core) |  | false |
| podAnnotations | annotations for the service rigger pod | map[string]string |  | false |
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

### IngressMethod
Used to distinguish between different platforms implementation

| Value | Description |
| ----- | ----------- |
| "openShiftRoute" | Routes are only usable in OpenShift |
| "ingress" | See https://kubernetes.io/docs/concepts/services-networking/ingress/ |
| "istio" | Ingress implemented via Istio |
[Back to Table of Contents](#table-of-contents)

### LDAPProtocol
The transport protocol used for LDAP.

| Value | Description |
| ----- | ----------- |
| "LDAP" | Plain unencrypted LDAP protocol |
| "LDAPS" | LDAP over SSL |
| "STARTTLS" | LDAP over TLS |
[Back to Table of Contents](#table-of-contents)

### LDAPSearchScope
The search scope for an LDAP query.

| Value | Description |
| ----- | ----------- |
| "BaseObject" | Specifies that search should only be performed against the entry specified as the search base DN. |
| "SingleLevel" | Specifies that search should only be performed against entries that are immediate subordinates of the entry specified as the search base DN. |
| "WholeSubtree" | Specifies that the search should be performed against the search base and all entries below. |
[Back to Table of Contents](#table-of-contents)

### OperatingMode

| Value | Description |
| ----- | ----------- |
| "enabled" |  |
| "disabled" |  |
[Back to Table of Contents](#table-of-contents)

### PvcStatus

| Value | Description |
| ----- | ----------- |
| "Provisioned" |  |
| "Provisioning" |  |
| "Resizing" |  |
| "ResizeFailed" |  |
[Back to Table of Contents](#table-of-contents)

### RedisOnFlashsStorageEngine

| Value | Description |
| ----- | ----------- |
| "rocksdb" |  |
| "speedb" |  |
[Back to Table of Contents](#table-of-contents)

### ServiceType
ServiceType determines how the service is exposed in the cluster.

| Value | Description |
| ----- | ----------- |
| "ClusterIP" | ClusterIP service provides access via a cluster-internal IP address. |
| "NodePort" | NodePort service provides access via a dedicated port exposed on every cluster node. |
| "LoadBalancer" | LoadBalancer service provides access via an external load balancer provided by the cloud provider platform. |
[Back to Table of Contents](#table-of-contents)

### SpecStatusName
Whether the REC specification is valid (custom resource)

| Value | Description |
| ----- | ----------- |
| "Invalid" | Specification status invalid |
| "Valid" | Specification status valid |
[Back to Table of Contents](#table-of-contents)
