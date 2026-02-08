# Redis Enterprise Cluster API
This document describes the parameters for the Redis Enterprise Cluster custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [APIServiceSpec](#apiservicespec)
  * [ActiveActive](#activeactive)
  * [AuditingConfig](#auditingconfig)
  * [AuditingConfiguration](#auditingconfiguration)
  * [Backup](#backup)
  * [BundledDatabaseRedisVersions](#bundleddatabaseredisversions)
  * [BundledDatabaseVersions](#bundleddatabaseversions)
  * [CallHomeClient](#callhomeclient)
  * [CallHomeS3Target](#callhomes3target)
  * [ClusterCertificate](#clustercertificate)
  * [ClusterCertificatesStatus](#clustercertificatesstatus)
  * [CmServer](#cmserver)
  * [ContainerTimezoneSpec](#containertimezonespec)
  * [CrdbCoordinator](#crdbcoordinator)
  * [CrdbWorker](#crdbworker)
  * [HTTPModuleSource](#httpmodulesource)
  * [HTTPSModuleSource](#httpsmodulesource)
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
  * [ModuleSource](#modulesource)
  * [OcspConfiguration](#ocspconfiguration)
  * [OcspStatus](#ocspstatus)
  * [OssClusterLoadBalancerSettings](#ossclusterloadbalancersettings)
  * [OssClusterSettings](#ossclustersettings)
  * [PdnsServer](#pdnsserver)
  * [PersistenceStatus](#persistencestatus)
  * [PersistentConfigurationSpec](#persistentconfigurationspec)
  * [PropagateHost](#propagatehost)
  * [RSClusterCertificates](#rsclustercertificates)
  * [ReadOnlyRootFilesystemPolicy](#readonlyrootfilesystempolicy)
  * [RedisEnterpriseCluster](#redisenterprisecluster)
  * [RedisEnterpriseClusterList](#redisenterpriseclusterlist)
  * [RedisEnterpriseClusterSpec](#redisenterpriseclusterspec)
  * [RedisEnterpriseClusterStatus](#redisenterpriseclusterstatus)
  * [RedisEnterpriseServicesConfiguration](#redisenterpriseservicesconfiguration)
  * [RedisOnFlashSpec](#redisonflashspec)
  * [ResourceLimitsSettings](#resourcelimitssettings)
  * [S3Backup](#s3backup)
  * [SAMLIssuerSpec](#samlissuerspec)
  * [SAMLServiceProviderSpec](#samlserviceproviderspec)
  * [SAMLSpec](#samlspec)
  * [SSOSpec](#ssospec)
  * [Saslauthd](#saslauthd)
  * [SecurityContextSpec](#securitycontextspec)
  * [Services](#services)
  * [ServicesRiggerConfigurationSpec](#servicesriggerconfigurationspec)
  * [SlaveHA](#slaveha)
  * [StartingPolicy](#startingpolicy)
  * [StatsArchiver](#statsarchiver)
  * [UpgradeSpec](#upgradespec)
  * [UsageMeterSpec](#usagemeterspec)
  * [UserDefinedModule](#userdefinedmodule)
* [Enums](#enums)
  * [CertificatesUpdateStatus](#certificatesupdatestatus)
  * [ClusterState](#clusterstate)
  * [IngressMethod](#ingressmethod)
  * [LDAPProtocol](#ldapprotocol)
  * [LDAPSearchScope](#ldapsearchscope)
  * [OperatingMode](#operatingmode)
  * [OssClusterExternalAccessType](#ossclusterexternalaccesstype)
  * [PvcStatus](#pvcstatus)
  * [RedisOnFlashsStorageEngine](#redisonflashsstorageengine)
  * [ServicePortPolicy](#serviceportpolicy)
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

### AuditingConfig
AuditingConfig defines the audit listener connection parameters

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| auditProtocol | Protocol used to send audit notifications. Valid values: "TCP" or "local". For production systems, use "TCP". "local" is for development/testing only. | string |  | true |
| auditAddress | TCP/IP address or file path where audit notifications will be sent. For TCP protocol: IP address of the audit listener. For local protocol: file path for audit output (development/testing only). | string |  | true |
| auditPort | Port number where audit notifications will be sent (TCP protocol only). | *int |  | false |
| auditReconnectInterval | Interval in seconds between attempts to reconnect to the audit listener. | *int | 1 | false |
| auditReconnectMaxAttempts | Maximum number of attempts to reconnect to the audit listener. Set to 0 for infinite attempts. | *int | 0 | false |
[Back to Table of Contents](#table-of-contents)

### AuditingConfiguration
AuditingConfiguration defines the configuration for auditing database connection and authentication events

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| config | Configuration for the audit listener connection | *[AuditingConfig](#auditingconfig) |  | false |
| dbConnsAuditing | Cluster-wide default policy for database connection auditing. When set to true, connection auditing will be enabled by default for all new databases. Existing databases are not affected and can override this setting individually. | *bool |  | false |
[Back to Table of Contents](#table-of-contents)

### Backup


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| s3 | Configurations for backups to s3 and s3-compatible storage | *[S3Backup](#s3backup) |  | false |
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

### CallHomeClient


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| disabled | Whether to disable the call home client. Enabled by default. | *bool |  | false |
| imageSpec |  | *[ImageSpec](#imagespec) |  | false |
| resources | Compute resource requirements for Call Home Client pod | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 0.25 CPU and 256Mi memory | false |
| proxySecretName | if needed, add proxy details in secret. the name of the proxy secret in the secret, can send the following keys: proxy-url, proxy-username, proxy-password (the url includes the proxy port). | string |  | false |
| s3Target | S3-compatible storage target for call home data upload. When enabled, call home data will be uploaded to this S3 target only. Before using this feature, please coordinate with Redis. | *[CallHomeS3Target](#callhomes3target) |  | false |
| interval | Interval between call home reports (e.g., "1h", "30m"). Passed as --interval flag to the call home client binary. If not specified, the CALL_HOME_CLIENT_INTERVAL environment variable is used, or the default value of 24h. Changing defaults is not recommended. | string |  | false |
| cronExpression | Cron expression for scheduling the call home CronJob (e.g., "0 */6 * * *"). If not specified, the CALL_HOME_CLIENT_CRON_SCHEDULE environment variable is used, or the default value of "0 23 * * *" (23:00 UTC daily). Changing defaults is not recommended. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### CallHomeS3Target
CallHomeS3Target defines an S3-compatible custom target for call home data upload.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Whether S3 upload is enabled. When true, call home data will be uploaded to the specified S3 target only. | bool |  | false |
| url | Full S3 URL including bucket (e.g., "https://bucket.s3.region.amazonaws.com" or "s3://bucket/prefix"). | string |  | false |
| endpoint | S3-compatible endpoint URL. | string |  | false |
| bucket | S3 bucket name. Required when S3Target is enabled. | string |  | false |
| region | AWS region for the S3 bucket (e.g., "us-east-1"). | string |  | false |
| prefix | S3 object key prefix/subfolder for uploaded files (e.g., "reports/2025"). If specified, files will be uploaded to s3://bucket/prefix/filename. | string |  | false |
| credentialsSecretName | Name of the Kubernetes secret containing S3 credentials. The secret must contain keys "access-key" and "secret-key". Optional keys: "session-token" (for AWS STS), "ca-cert" (for custom CA). The credentials must have s3:PutObject permission on the target bucket. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### ClusterCertificate


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name |  | string |  | true |
| certificate |  | string |  | true |
| key |  | string |  | true |
[Back to Table of Contents](#table-of-contents)

### ClusterCertificatesStatus
ClusterCertificatesStatus Stores information about cluster certificates and their update process. In Active-Active databases, this is used to detect updates to the certificates, and trigger synchronization across the participating clusters.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| generation | Generation stores the version of the cluster's Proxy and Syncer certificate secrets. This generation counter is automatically incremented when proxy or syncer certificates are updated. In Active-Active databases (REAADB), the operator monitors this field to detect certificate changes and automatically triggers a CRDB force update (equivalent to 'crdb-cli crdb update --force'), which synchronizes the certificate changes to all participating clusters, eliminating the need for manual intervention to maintain sync. | *int64 |  | false |
| updateStatus | The status of the cluster's certificates update | [CertificatesUpdateStatus](#certificatesupdatestatus) |  | false |
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

### HTTPModuleSource
HTTPModuleSource defines an HTTP source for downloading a module

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| url | URL to download the module from (must use http:// scheme) | string |  | true |
| credentialsSecret | Name of the Kubernetes secret containing credentials for downloading the module, if needed. The secret must contain 'username' and 'password' keys. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### HTTPSModuleSource
HTTPSModuleSource defines an HTTPS source for downloading a module

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| url | URL to download the module from (must use https:// scheme) | string |  | true |
| credentialsSecret | Name of the Kubernetes secret containing credentials for downloading the module, if needed. The secret must contain 'username' and 'password' keys. | string |  | false |
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
| directoryTimeoutSeconds | The connection timeout to the LDAP server when authenticating a user, in seconds | *int |  | false |
[Back to Table of Contents](#table-of-contents)

### LicenseStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| licenseState | Is the license expired | string |  | true |
| activationDate | When the license was activated | string |  | true |
| expirationDate | When the license will\has expired | string |  | true |
| shardsLimit | Total number of shards (both RAM and flash) allowed under this license. | int32 |  | true |
| shardsUsage | Total number of shards (both RAM and flash) currently in use under this license. | string |  | true |
| features | Additional features enabled by this license | []string |  | true |
| owner | The license owner's name | string |  | true |
| flashShards | Number of flash shards currently in use under this license | int32 |  | true |
| flashShardsLimit | Number of flash shards allowed under this license | *int32 |  | true |
| ramShards | Number of RAM shards currently in use under this license | int32 |  | true |
| ramShardsLimit | Number of RAM shards allowed under this license | *int32 |  | true |
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

### ModuleSource
ModuleSource defines the source location for downloading a user-defined module. Exactly one of the source types (HTTP, HTTPS) must be specified.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| http | HTTP source configuration for downloading the module via HTTP | *[HTTPModuleSource](#httpmodulesource) |  | false |
| https | HTTPS source configuration for downloading the module via HTTPS | *[HTTPSModuleSource](#httpsmodulesource) |  | false |
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

### OssClusterLoadBalancerSettings
Configuration for LoadBalancer services created to assign public IPs for Redis Enterprise cluster nodes.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| serviceAnnotations | Additional annotations to set on LoadBalancer services created for Redis Enterprise cluster nodes. These annotations are merged with global service annotations from spec.services.servicesAnnotations. | map[string]string |  | false |
| externalTrafficPolicy | ExternalTrafficPolicy specifies the externalTrafficPolicy for LoadBalancer services created for Redis Enterprise cluster nodes. Choose "Local" to configure the LoadBalancer to only route traffic to the single worker node hosting the Redis Enterprise cluster node for that service. Choose "Cluster" to route traffic to any worker node, providing a more stable behavior during failovers, but with increased overhead due to additional hop. Defaults to "Local" when podCIDRs is configured, and "Cluster" otherwise. | *v1.ServiceExternalTrafficPolicy |  | false |
[Back to Table of Contents](#table-of-contents)

### OssClusterSettings
Cluster-level configuration for OSS cluster mode databases.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| externalAccessType | Specifies the mechanism for enabling external access to OSS cluster databases. When unset or set to "Disabled", external access is not allowed for any OSS cluster databases. When set to a specific mechanism (e.g., "LoadBalancer"), that mechanism is used to provide external access. Note: Individual databases must still enable external access via their ossClusterSettings.enableExternalAccess field. | *[OssClusterExternalAccessType](#ossclusterexternalaccesstype) |  | false |
| loadBalancer | Configuration for LoadBalancer services created to assign public IPs for Redis Enterprise cluster nodes. | *[OssClusterLoadBalancerSettings](#ossclusterloadbalancersettings) |  | false |
| podCIDRs | A list of Kubernetes pod CIDR ranges from which pod IPs are allocated. Supports both IPv4 (e.g., "10.30.0.0/16") and IPv6 addresses. This field should only be configured when OSS cluster databases need to be accessed from both internal and external clients. When configured, internal communication can reach pods directly using their pod IPs, bypassing the external access mechanism (e.g., load balancer services) for improved performance. IMPORTANT: For this feature to work correctly, the entire data path must preserve the client source IP address. This is required because the Redis server uses the client's source IP to construct the CLUSTER SHARDS/SLOTS response - returning pod IPs for internal clients (matching podCIDRs) or load balancer addresses for external clients. On cloud platforms, this typically requires configuring the load balancer to preserve source IPs. | []string |  | false |
[Back to Table of Contents](#table-of-contents)

### PdnsServer


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Deprecated: The PDNS Server is now disabled by the operator. This field will be ignored. | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### PersistenceStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| status | The current status of the PVCs | [PvcStatus](#pvcstatus) |  | false |
| succeeded | The number of PVCs that are provisioned with the expected size | string |  | false |
[Back to Table of Contents](#table-of-contents)

### PersistentConfigurationSpec
Persistent storage configuration for Redis Enterprise cluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Enables persistent volumes for Redis Enterprise pods. | *bool | True | true |
| storageClassName | Storage class for persistent volumes in Redis Enterprise pods. Leave empty to use the default storage class. | string |  | true |
| volumeSize | Size of the persistent volume for each Redis Enterprise pod. To enable resizing after cluster creation, see https://redis.io/docs/latest/operate/kubernetes/re-clusters/expand-pvc/. | resource.Quantity |  | true |
| enablePersistentVolumeResize | Enables persistent volume resizing. Disabled by default. To enable resizing after cluster creation, see https://redis.io/docs/latest/operate/kubernetes/re-clusters/expand-pvc/. | *bool |  | false |
[Back to Table of Contents](#table-of-contents)

### PropagateHost
Used to specify that the timezone is configured to match the host machine timezone.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
[Back to Table of Contents](#table-of-contents)

### RSClusterCertificates


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| apiCertificateSecretName | Secret name to use for cluster's API certificate. The secret must contain the following structure - A key 'name' with the value 'api'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. | string |  | false |
| cmCertificateSecretName | Secret name to use for cluster's CM (Cluster Manager) certificate. The secret must contain the following structure - A key 'name' with the value 'cm'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. | string |  | false |
| metricsExporterCertificateSecretName | Secret name to use for cluster's Metrics Exporter certificate. The secret must contain the following structure - A key 'name' with the value 'metrics_exporter'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. | string |  | false |
| proxyCertificateSecretName | Secret name to use for cluster's Proxy certificate. The secret must contain the following structure - A key 'name' with the value 'proxy'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. Note: For Active-Active databases (REAADB), certificate updates are automatically reconciled. When you update this secret, the operator detects the change and automatically executes a CRDB force update (equivalent to 'crdb-cli crdb update --force'), which synchronizes the certificate changes to all participating clusters, eliminating the need for manual intervention. | string |  | false |
| syncerCertificateSecretName | Secret name to use for cluster's Syncer certificate. The secret must contain the following structure - A key 'name' with the value 'syncer'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. Note: For Active-Active databases (REAADB), certificate updates are automatically reconciled. When you update this secret, the operator detects the change and automatically executes a CRDB force update (equivalent to 'crdb-cli crdb update --force'), which synchronizes the certificate changes to all participating clusters, eliminating the need for manual intervention. | string |  | false |
| ldapClientCertificateSecretName | Secret name to use for cluster's LDAP client certificate. The secret must contain the following structure - A key 'name' with the value 'ldap_client'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, LDAP client certificate authentication will be disabled. | string |  | false |
| dpInternodeEncryptionCertificateSecretName | Secret name to use for cluster's Data Plane Internode Encryption (DPINE) certificate. The secret must contain the following structure - A key 'name' with the value 'data_internode_encryption'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. | string |  | false |
| cpInternodeEncryptionCertificateSecretName | Secret name to use for cluster's Control Plane Internode Encryption (CPINE) certificate. The secret must contain the following structure - A key 'name' with the value 'ccs_internode_encryption'. - A key 'certificate' with the value of the certificate in PEM format. - A key 'key' with the value of the private key. If left blank, a cluster-provided certificate will be used. | string |  | false |
| ssoServiceCertificateSecretName | Secret name to use for the SSO Service Provider (SP) certificate. This certificate is used by the cluster to sign SAML requests and encrypt SAML responses. The secret must contain 'name' (set to "sso_service"), 'certificate', and 'key' fields (same format as other cluster certificates). This certificate must be configured as part of the SSO setup and before SSO can be enabled for the cluster. | string |  | false |
| ssoIssuerCertificateSecretName | Secret name to use for the SSO Identity Provider (IdP) certificate. This is the public certificate from your SAML Identity Provider used to verify SAML assertions. The secret must contain 'name' (set to "sso_issuer") and 'certificate' fields (no 'key' field needed for IdP cert). This certificate must be configured as part of the SSO setup and before SSO can be enabled for the cluster. Note: While IdP metadata XML may contain the certificate, Redis Enterprise Server does not use it from there, so the certificate must be provided separately via this secret. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### ReadOnlyRootFilesystemPolicy
Read-only root filesystem policy for Redis Enterprise pods

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Enables read-only root filesystem for Redis Enterprise containers. Default is false. | bool |  | true |
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
| serviceAccountName | Name of the service account to use for Redis Enterprise. | string | RedisEnterpriseCluster's name | false |
| createServiceAccount | Creates a service account for Redis Enterprise. | *bool | True | false |
| uiServiceType | Service type for exposing the Redis Enterprise UI (https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types). | *v1.ServiceType | ClusterIP | false |
| uiAnnotations | Additional annotations for the Redis Enterprise UI service. | map[string]string |  | false |
| servicesRiggerSpec | Specification for service rigger | *[ServicesRiggerConfigurationSpec](#servicesriggerconfigurationspec) |  | false |
| redisEnterpriseAdditionalPodSpecAttributes | ADVANCED USAGE USE AT YOUR OWN RISK - specify pod attributes that are required for the statefulset - Redis Enterprise pods. Pod attributes managed by the operator might override these settings. Also make sure the attributes are supported by the K8s version running on the cluster - the operator does not validate that. | *[v1.PodSpec](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#podspec-v1-core) |  | false |
| license | Redis Enterprise license key. Defaults to Trial Mode license (https://docs.redislabs.com/latest/rs/administering/cluster-operations/settings/license-keys/#trial-mode). | string | Empty string which is a Trial Mode license | false |
| licenseSecretName | Name or path of the Kubernetes secret or Vault secret containing the cluster license. When left blank, the license is read from the "license" field. Cannot specify non-empty values in both "license" and "licenseSecretName" fields. The license must be stored under the key "license". | string | Empty string | false |
| username | Username for the Redis Enterprise admin user. | string | demo@redis.com | false |
| nodeSelector | Node selector for scheduling Redis Enterprise pods on specific nodes. | *map[string]string |  | false |
| redisEnterpriseImageSpec | Container image specification for Redis Enterprise. | *[ImageSpec](#imagespec) | the default Redis Enterprise image for this version | false |
| redisEnterpriseServicesRiggerImageSpec | Container image specification for Services Rigger. | *[ImageSpec](#imagespec) | the default Services Rigger image for this version | false |
| bootstrapperImageSpec | Container image specification for Bootstrapper. | *[ImageSpec](#imagespec) | the default Bootstrapper image for this version | false |
| redisEnterpriseNodeResources | Resource requirements for Redis Enterprise containers. | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 2 CPUs and 4GB memory | false |
| bootstrapperResources | Resource requirements for bootstrapper containers. | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 0.1 CPUs and 128Mi memory | false |
| redisEnterpriseServicesRiggerResources | Resource requirements for Services Rigger pods. | *[v1.ResourceRequirements](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#resourcerequirements-v1-core) | 0.5 CPU and 0.5GB memory | false |
| pullSecrets | Image pull secrets for accessing private container registries. | [][v1.LocalObjectReference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#localobjectreference-v1-core) | empty | false |
| persistentSpec | Persistent storage configuration for Redis Enterprise cluster. | [PersistentConfigurationSpec](#persistentconfigurationspec) |  | false |
| sideContainersSpec | Additional sidecar containers to add to each Redis Enterprise pod. | []v1.Container | empty | false |
| extraLabels | Additional labels applied to resources created by the operator (Services, Secrets, StatefulSet, etc.). Note that PersistentVolumeClaims are only labeled with extra labels specified during cluster creation. Modifying this field after cluster creation does not affect existing PersistentVolumeClaims. | map[string]string | empty | false |
| podAntiAffinity | Custom anti-affinity rules for Redis Enterprise pods. If specified, this overrides the default anti-affinity rules which place Redis Enterprise pods on separate nodes. | *v1.PodAntiAffinity |  | false |
| antiAffinityAdditionalTopologyKeys | Additional topology keys for anti-affinity rules to support installation across different zones or vCenters. | []string |  | false |
| activeActive | Ingress connectivity configuration for Active-Active databases. This field is deprecated, use ingressOrRouteSpec instead; cannot be used simultaneously with ingressOrRouteSpec. | *[ActiveActive](#activeactive) |  | false |
| upgradeSpec | Redis Enterprise upgrade configuration. | *[UpgradeSpec](#upgradespec) |  | false |
| enforceIPv4 | Forces IPv4 networking by setting the ENFORCE_IPV4 environment variable. | *bool | False | false |
| clusterRecovery | Initiates cluster recovery when set to true. This field is automatically cleared after recovery completes. | *bool |  | false |
| rackAwarenessNodeLabel | Node label that specifies rack ID for creating a rack-aware cluster. Requires the label to exist on all nodes and the operator to have cluster role permissions to list nodes. | string |  | false |
| priorityClassName | Priority class name for pods managed by the operator. | string |  | false |
| hostAliases | Host aliases to add to Redis Enterprise pods. | []v1.HostAlias |  | false |
| volumes | Additional volumes for Redis Enterprise pods. | [][v1.Volume](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#volume-v1-core) |  | false |
| redisEnterpriseVolumeMounts | Additional volume mounts for Redis Enterprise containers. | [][v1.VolumeMount](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#volumemount-v1-core) |  | false |
| podAnnotations | Additional annotations applied to operator-managed pods. | map[string]string |  | false |
| redisEnterprisePodAnnotations | Annotations specifically for Redis Enterprise pods. | map[string]string |  | false |
| podTolerations | Tolerations for all managed pods. For more information, see https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/ | [][v1.Toleration](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#toleration-v1-core) | empty | false |
| slaveHA | High availability configuration for replica shards. | *[SlaveHA](#slaveha) |  | false |
| clusterCredentialSecretName | Name or path of the secret containing cluster credentials. Defaults to the cluster name if left blank. For Kubernetes secrets (default): Can be customized to any valid secret name, or left blank to use the cluster name. The secret can be pre-created with 'username' and 'password' fields, or otherwise it will be automatically created with a default username and auto-generated password. For Vault secrets: Can be customized with the path of the secret within Vault. The secret must be pre-created in Vault before REC creation. This field cannot be changed after cluster creation. | string |  | false |
| clusterCredentialSecretType | Type of secret for cluster credentials (vault or kubernetes). Defaults to kubernetes if left blank. | string |  | true |
| clusterCredentialSecretRole | Vault role for cluster credentials. Used only when ClusterCredentialSecretType is vault. Defaults to "redis-enterprise-rec" if blank. | string |  | true |
| vaultCASecret | Name of the Kubernetes secret containing Vault's CA certificate. Defaults to "vault-ca-cert". | string |  | false |
| redisEnterpriseServicesConfiguration | Configuration for optional Redis Enterprise services. Note: Disabling the CM Server service removes the cluster's UI Service from the Kubernetes cluster. The saslauthd entry is deprecated and will be removed. | *[RedisEnterpriseServicesConfiguration](#redisenterpriseservicesconfiguration) |  | false |
| dataInternodeEncryption | Cluster-wide internode encryption (INE) policy for new databases. Can be overridden for specific databases using the same setting in RedisEnterpriseDatabase. | *bool |  | false |
| redisUpgradePolicy | Redis upgrade policy for the cluster. Possible values: "major" or "latest". This policy determines which Redis version the cluster uses when upgrading databases. For more information, see https://redis.io/docs/latest/operate/rs/installing-upgrading/upgrading#redis-upgrade-policy | string |  | false |
| certificates | Custom certificates for the Redis Enterprise cluster. | *[RSClusterCertificates](#rsclustercertificates) |  | false |
| podStartingPolicy | Configuration for detecting and mitigating StatefulSet pods stuck in "ContainerCreating" state. | *[StartingPolicy](#startingpolicy) |  | false |
| redisEnterpriseTerminationGracePeriodSeconds | Termination grace period in seconds for Redis Enterprise pods. Pods should not be forcefully terminated as clean shutdown prevents data loss. The default value is intentionally large (1 year). For pure caching configurations where data loss is acceptable, a shorter value may be used. | *int64 | 31536000 | false |
| redisOnFlashSpec | Redis Flex (previously known as Redis on Flash) configuration. When provided, the cluster can create Redis Flex databases. | *[RedisOnFlashSpec](#redisonflashspec) |  | false |
| ocspConfiguration | An API object that represents the cluster's OCSP configuration. To enable OCSP, the cluster's proxy certificate should contain the OCSP responder URL. | *[OcspConfiguration](#ocspconfiguration) |  | false |
| encryptPkeys | Private key encryption Possible values: true/false | *bool |  | false |
| redisEnterpriseIPFamily | When the operator is running in a dual-stack environment (both IPv4 and IPv6 network interfaces are available), specifies the IP family of the network interface that will be used by the Redis Enterprise cluster, as well as services created by the operator (API, UI, Prometheus services). | v1.IPFamily |  | false |
| containerTimezone | Container timezone configuration. While the default timezone on all containers is UTC, this setting can be used to set the timezone on services rigger/bootstrapper/RS containers. Currently the only supported value is to propagate the host timezone to all containers. | *[ContainerTimezoneSpec](#containertimezonespec) |  | false |
| ingressOrRouteSpec | Access configurations for the Redis Enterprise cluster and databases. At most one of ingressOrRouteSpec or activeActive fields can be set at the same time. | *[IngressOrRouteSpec](#ingressorroutespec) |  | false |
| services | Customization options for operator-managed service resources created for Redis Enterprise clusters and databases | *[Services](#services) |  | false |
| ossClusterSettings | Cluster-level configuration for OSS cluster mode databases. | *[OssClusterSettings](#ossclustersettings) |  | false |
| ldap | Cluster-level LDAP configuration, such as server addresses, protocol, authentication and query settings. | *[LDAPSpec](#ldapspec) |  | false |
| sso | SSO authentication configuration for the Cluster Manager UI. For setup instructions, see https://redis.io/docs/latest/ | *[SSOSpec](#ssospec) |  | false |
| extraEnvVars | ADVANCED USAGE: use carefully. Add environment variables to RS StatefulSet's containers. | []v1.EnvVar |  | false |
| resp3Default | Whether databases will turn on RESP3 compatibility upon database upgrade. Note - Deleting this property after explicitly setting its value shall have no effect. Please view the corresponding field in RS doc for more info. | *bool |  | false |
| backup | Cluster-wide backup configurations | *[Backup](#backup) |  | false |
| securityContext | The security configuration that will be applied to RS pods. | *[SecurityContextSpec](#securitycontextspec) |  | false |
| usageMeter | The configuration of the usage meter. | *[UsageMeterSpec](#usagemeterspec) |  | false |
| userDefinedModules | List of user-defined modules to be downloaded and installed during cluster bootstrap The modules on the list will be downloaded on cluster creation, upgrade, scale-out and recovery and installed on all nodes. Alpha feature - use only if instructed. Note that changing this field for a running cluster will trigger a rolling update. | [][UserDefinedModule](#userdefinedmodule) |  | false |
| auditing | Cluster-level configuration for auditing database connection and authentication events. Includes both the audit listener connection parameters and the default policy for new databases. | *[AuditingConfiguration](#auditingconfiguration) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseClusterStatus
RedisEnterpriseClusterStatus defines the observed state of RedisEnterpriseCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| state | State of Redis Enterprise cluster | [ClusterState](#clusterstate) |  | true |
| specStatus | Validity of Redis Enterprise cluster specification | [SpecStatusName](#specstatusname) |  | true |
| modules | Modules Available in Cluster | [][Module](#module) |  | false |
| licenseStatus | State of the Cluster's License | *[LicenseStatus](#licensestatus) |  | false |
| bundledDatabaseVersions | Versions of open source databases bundled by Redis Enterprise Software - please note that in order to use a specific version it should be supported by the ‘upgradePolicy’ - ‘major’ or ‘latest’ according to the desired version (major/minor) | []*[BundledDatabaseVersions](#bundleddatabaseversions) |  | false |
| ocspStatus | An API object that represents the cluster's OCSP status | *[OcspStatus](#ocspstatus) |  | false |
| managedAPIs | Indicates cluster APIs that are being managed by the operator. This only applies to cluster APIs which are optionally-managed by the operator, such as cluster LDAP configuration. Most other APIs are automatically managed by the operator, and are not listed here. | *[ManagedAPIs](#managedapis) |  | false |
| ingressOrRouteMethodStatus | The ingressOrRouteSpec/ActiveActive spec method that exist | [IngressMethod](#ingressmethod) |  | false |
| redisEnterpriseIPFamily | The chosen IP family of the cluster if was specified in REC spec. | v1.IPFamily |  | false |
| persistenceStatus | The status of the Persistent Volume Claims that are used for Redis Enterprise cluster persistence. The status will correspond to the status of one or more of the PVCs (failed/resizing if one of them is in resize or failed to resize) | [PersistenceStatus](#persistencestatus) |  | false |
| certificatesStatus | Stores information about cluster certificates and their update process. In Active-Active databases, this is used to detect updates to the certificates, and trigger synchronization across the participating clusters. | *[ClusterCertificatesStatus](#clustercertificatesstatus) |  | false |
| clusterCredentialSecretName | The name of the secret containing cluster credentials that was set upon cluster creation. This field is used to prevent changes to ClusterCredentialSecretName after cluster creation. | string |  | false |
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

### ResourceLimitsSettings
Resource limits management settings for Redis Enterprise node containers.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| allowAutoAdjustment | Allows Redis Enterprise to automatically adjust resource limits (such as max open file descriptors) for its data plane processes. When enabled, the SYS_RESOURCE capability is added to Redis Enterprise pods and their allowPrivilegeEscalation field is set. Disabled by default. | *bool |  | false |
[Back to Table of Contents](#table-of-contents)

### S3Backup


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| url | Specifies the URL for S3 export and import | string |  | false |
| caCertificateSecretName | Secret name that holds the S3 CA certificate, which contains the TLS certificate mapped to the key in the secret 'cert' | string |  | false |
[Back to Table of Contents](#table-of-contents)

### SAMLIssuerSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| entityID | Identity Provider entity ID (issuer identifier). Example: "urn:sso:example:idp" or "https://idp.example.com". | string |  | true |
| loginURL | Identity Provider SSO login URL where SAML authentication requests are sent. Example: "https://idp.example.com/sso/saml". | string |  | true |
| logoutURL | Identity Provider single logout URL where SAML logout requests are sent. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### SAMLServiceProviderSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| baseAddress | Base address used to construct Service Provider (SP) URLs, such as the ACS URL and SLO URL. Format: [<scheme>://]<hostname>[:<port>] Examples:\n  - "https://redis-ui.example.com:9443" (recommended - explicit scheme)\n  - "redis-ui.example.com:9443" (defaults to https://)\n  - "http://redis-ui.example.com:9443" (NOT recommended for production)\n\nIf the scheme is not specified, the operator automatically prepends "https://". WARNING: Using "http://" is NOT recommended for production environments as it transmits sensitive SAML assertions in plaintext. Only use "http://" for testing/development purposes.\n\nIf set, this value is used to construct the SP URLs.\n\nIf unset, the base address is automatically determined from the REC Cluster Manager UI service: - If the UI service type is LoadBalancer (configured via spec.uiServiceType), the load balancer address is used. - Otherwise, the cluster-internal DNS name is used (e.g., rec-ui.svc.cluster.local). - The port defaults to 8443 if not specified.\n\nUsage guidelines: - For LoadBalancer services: Leave this field blank to use the default REC UI service, or set it explicitly to the LoadBalancer address for custom services. - For Ingress: Set this to the ingress hostname and port (typically 443), e.g., "https://redis-ui.example.com:443". | string |  | false |
[Back to Table of Contents](#table-of-contents)

### SAMLSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| idpMetadataSecretName | Name of a secret in the same namespace that contains the Identity Provider (IdP) metadata XML. The secret must contain a key named 'idp_metadata' with the IdP metadata XML content. The XML can be plain text or base64-encoded; the operator handles encoding as needed. Obtain this metadata from your SAML Identity Provider (for example, Okta or Azure AD). This is the recommended configuration method, as it's less error-prone. Either idpMetadataSecretName or issuer must be specified. If both are provided, idpMetadataSecretName takes precedence and issuer is ignored. | string |  | false |
| issuer | Manual Identity Provider (IdP) configuration. Use this when IdP metadata XML is unavailable. Either idpMetadataSecretName or issuer must be specified. If both are provided, idpMetadataSecretName takes precedence and issuer is ignored. | *[SAMLIssuerSpec](#samlissuerspec) |  | false |
| spMetadataSecretName | Name of a secret where the operator stores the Service Provider (SP) metadata XML. The operator creates this secret with a key named 'sp_metadata' that contains the base64-encoded SP metadata XML. Upload this metadata to your Identity Provider. If not specified, the Service Provider metadata isn't stored in a K8s secret, but can still be obtained directly from the cluster's UI and/or API. Note: This secret is only created when the cluster is configured to use Kubernetes secrets (spec.clusterCredentialSecretType is unset or set to "kubernetes"). When using Vault secrets, the operator does not create this secret. Users can obtain the SP metadata directly from the Redis Enterprise Server API endpoint: GET /v1/cluster/sso/saml/metadata/sp and store it in Vault themselves if needed. | string |  | false |
| serviceProvider | Service Provider (SP) configuration. | *[SAMLServiceProviderSpec](#samlserviceproviderspec) |  | false |
[Back to Table of Contents](#table-of-contents)

### SSOSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Enables SSO for Cluster Manager authentication. SSO requires the following configuration: - Service Provider certificate (spec.certificates.ssoServiceCertificateSecretName) - Identity Provider certificate (spec.certificates.ssoIssuerCertificateSecretName) - IdP metadata or manual issuer configuration (spec.sso.saml.idpMetadataSecretName or spec.sso.saml.issuer) - Base address for Service Provider URLs (auto-determined from UI service or set via spec.sso.saml.serviceProvider.baseAddress) | bool |  | true |
| enforceSSO | Enforces SSO-only authentication for the Cluster Manager. When true, local username/password authentication is disabled for non-admin users. When false (default), both SSO and local authentication are available. | bool |  | false |
| saml | SAML-based SSO configuration. Currently,SAML is the only supported SSO protocol. | *[SAMLSpec](#samlspec) |  | true |
[Back to Table of Contents](#table-of-contents)

### Saslauthd


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the saslauthd service | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### SecurityContextSpec
Security configuration for Redis Enterprise pods.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| readOnlyRootFilesystemPolicy | Policy for enabling read-only root filesystem for Redis Enterprise containers. Note that certain filesystem paths remain writable through mounted volumes to ensure proper functionality. | *[ReadOnlyRootFilesystemPolicy](#readonlyrootfilesystempolicy) |  | false |
| resourceLimits | Resource limits management settings for Redis Enterprise node containers. | *[ResourceLimitsSettings](#resourcelimitssettings) |  | false |
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
| databaseServicePortPolicy | DatabaseServicePortPolicy instructs how to determine the service ports for REDB services. Defaults to DatabasePortForward, if not specified otherwise. Note - Regardless whether this flag is set or not, if an REDB/REAADB is configured with databaseServicePort that would be the port exposed by the Service. Options:\n\tDatabasePortForward - The service port will be the same as the database port.\n\tRedisDefaultPort - The service port will be the default Redis port (6379). | [ServicePortPolicy](#serviceportpolicy) | DatabasePortForward | false |
[Back to Table of Contents](#table-of-contents)

### SlaveHA


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| slaveHAGracePeriod | Grace period in seconds between node failure and when the high availability mechanism starts relocating shards. Set to 0 to not affect cluster configuration. | *uint32 | 1800 | true |
[Back to Table of Contents](#table-of-contents)

### StartingPolicy


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Enables detection and mitigation of pod startup issues. | *bool | False | true |
| startingThresholdSeconds | Time in seconds to wait before taking action on a pod stuck during startup. Set to 0 to disable. | *uint32 | 540 | true |
[Back to Table of Contents](#table-of-contents)

### StatsArchiver


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| operatingMode | Whether to enable/disable the stats archiver service | [OperatingMode](#operatingmode) |  | true |
[Back to Table of Contents](#table-of-contents)

### UpgradeSpec
Redis Enterprise upgrade configuration

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| autoUpgradeRedisEnterprise | Enables automatic Redis Enterprise cluster upgrades when the operator is upgraded. | bool |  | true |
[Back to Table of Contents](#table-of-contents)

### UsageMeterSpec
UsageMeterSpec - the configuration of the usage meter.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| callHomeClient |  | *[CallHomeClient](#callhomeclient) |  | false |
[Back to Table of Contents](#table-of-contents)

### UserDefinedModule
UserDefinedModule represents a user-defined Redis module to be downloaded and installed during bootstrap

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | Name of the module | string |  | true |
| source | Source location for downloading the module | [ModuleSource](#modulesource) |  | true |
[Back to Table of Contents](#table-of-contents)
## Enums

### CertificatesUpdateStatus
CertificatesUpdateStatus stores the status of the cluster's certificates update

| Value | Description |
| ----- | ----------- |
| "InProgress" | CertificatesUpdateStatusInProgress indicates that the certificates update is in progress |
| "Completed" | CertificatesUpdateStatusCompleted indicates that the certificates update has been completed |
[Back to Table of Contents](#table-of-contents)

### ClusterState
State of the Redis Enterprise Cluster

| Value | Description |
| ----- | ----------- |
| "PendingCreation" | PendingCreation means cluster is not created yet |
| "BootstrappingFirstPod" | Bootstrapping first pod |
| "Initializing" | Initializing means the cluster was created and nodes are in the process of joining the cluster |
| "RecoveryReset" | RecoveryReset resets the cluster by deleting all pods |
| "RecoveringFirstPod" | RecoveringFirstPod means the cluster entered cluster recovery |
| "Running" | Running means the cluster's sub-resources have been created and are in running state |
| "Error" | Error means the there was an error when starting creating/updating the one or more of the cluster's resources |
| "Invalid" | Invalid means an invalid spec was applied |
| "InvalidUpgrade" | InvalidUpgrade means an upgrade is not possible at this time |
| "Upgrade" | Upgrade |
| "Deleting" | Deleting |
| "ClusterRecreating" | ClusterRecreating - similar to RecoveryReset - delete all pods before recreation of the cluster. |
| "RunningRollingUpdate" | RunningRollingUpdate similar to Running state and the STS is during rolling-update |
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

### OssClusterExternalAccessType
OssClusterExternalAccessType specifies the mechanism used to provide external access to OSS cluster databases.
This is a cluster-level control that determines whether external access is allowed and which mechanism to use.
Individual databases must still opt-in to external access via their ossClusterSettings.enableExternalAccess field.

| Value | Description |
| ----- | ----------- |
| "LoadBalancer" | OssClusterExternalAccessLoadBalancer uses LoadBalancer services per REC pod to provide external access |
| "Disabled" | OssClusterExternalAccessDisabled explicitly disables external access for OSS cluster databases |
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

### ServicePortPolicy

| Value | Description |
| ----- | ----------- |
| "DatabasePortForward" |  |
| "RedisDefaultPort" |  |
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
