# Redis Enterprise Database API
This document describes the parameters for the Redis Enterprise Database custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [ActiveActiveInfo](#activeactiveinfo)
  * [AzureBlobStorage](#azureblobstorage)
  * [BackupInfo](#backupinfo)
  * [BackupSpec](#backupspec)
  * [BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold)
  * [DBUpgradeSpec](#dbupgradespec)
  * [DatabaseAuditingConfiguration](#databaseauditingconfiguration)
  * [DbAlertsSettings](#dbalertssettings)
  * [DbModule](#dbmodule)
  * [FtpStorage](#ftpstorage)
  * [GoogleStorage](#googlestorage)
  * [InternalEndpoint](#internalendpoint)
  * [MountPointStorage](#mountpointstorage)
  * [RedisEnterpriseConnection](#redisenterpriseconnection)
  * [RedisEnterpriseDatabase](#redisenterprisedatabase)
  * [RedisEnterpriseDatabaseList](#redisenterprisedatabaselist)
  * [RedisEnterpriseDatabaseSpec](#redisenterprisedatabasespec)
  * [RedisEnterpriseDatabaseStatus](#redisenterprisedatabasestatus)
  * [ReplicaSource](#replicasource)
  * [ReplicaSourceStatus](#replicasourcestatus)
  * [RolePermission](#rolepermission)
  * [S3Storage](#s3storage)
  * [SftpStorage](#sftpstorage)
  * [SwiftStorage](#swiftstorage)
* [Enums](#enums)
  * [DatabasePersistence](#databasepersistence)
  * [DatabaseStatus](#databasestatus)
  * [DatabaseType](#databasetype)
  * [ReplicaSourceType](#replicasourcetype)
  * [RolePermissionType](#rolepermissiontype)
## Objects

### ActiveActiveInfo
Connection/ association  for Active-Active database related resources.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The the corresponding Active-Active database name, Redis Enterprise Active Active Database custom resource name, this Resource is associated with. In case this resource is created manually at the active active database creation this field must be filled via the user, otherwise, the operator will assign this field automatically. Note: this feature is currently unsupported. | string |  | true |
| participatingClusterName | The corresponding participating cluster name, Redis Enterprise Remote Cluster custom resource name, in the Active-Active database, In case this resource is created manually at the active active database creation this field must be filled via the user, otherwise, the operator will assign this field automatically. Note: this feature is currently unsupported. | string |  | true |
[Back to Table of Contents](#table-of-contents)

### AzureBlobStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| absSecretName | The name of the secret that holds ABS credentials. The secret must contain the keys "AccountName" and "AccountKey", and these must hold the corresponding credentials | string |  | true |
| container | Azure Blob Storage container name. | string |  | true |
| subdir | Optional. Azure Blob Storage subdir under container. | string | empty | false |
[Back to Table of Contents](#table-of-contents)

### BackupInfo


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| backupFailureReason | Reason of last failed backup process | *string |  | false |
| backupHistory | Backup history retention policy (number of days, 0 is forever) | *int |  | false |
| backupInterval | Interval in seconds in which automatic backup will be initiated | *int |  | false |
| backupIntervalOffset | Offset (in seconds) from round backup interval when automatic backup will be initiated (should be less than backup_interval) | *int |  | false |
| backupProgressPercentage | Database scheduled periodic backup progress (percentage) | *int |  | false |
| backupStatus | Status of scheduled periodic backup process | *string |  | false |
| lastBackupTime | Time of last successful backup | *string |  | false |
[Back to Table of Contents](#table-of-contents)

### BackupSpec
The various backup storage options are validated to be mutually exclusive, although for technical reasons, the relevant error is not very clear and indicates a conflict in the specified storage type.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| interval | Backup Interval in seconds | int | 86400 | false |
| ftp |  | *[FtpStorage](#ftpstorage) |  | false |
| s3 |  | *[S3Storage](#s3storage) |  | false |
| abs |  | *[AzureBlobStorage](#azureblobstorage) |  | false |
| swift |  | *[SwiftStorage](#swiftstorage) |  | false |
| sftp |  | *[SftpStorage](#sftpstorage) |  | false |
| gcs |  | *[GoogleStorage](#googlestorage) |  | false |
| mount |  | *[MountPointStorage](#mountpointstorage) |  | false |
[Back to Table of Contents](#table-of-contents)

### BdbAlertSettingsWithThreshold
Threshold for database alert

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| enabled | Alert enabled or disabled | bool |  | true |
| threshold | Threshold for alert going on/off | string |  | true |
[Back to Table of Contents](#table-of-contents)

### DBUpgradeSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| upgradeModulesToLatest | DEPRECATED Upgrades the modules to the latest version that supports the DB version during a DB upgrade action, to upgrade the DB version view the 'redisVersion' field. Notes - All modules must be without specifying the version. in addition, This field is currently not supported for Active-Active databases. The default is true | *bool |  | true |
[Back to Table of Contents](#table-of-contents)

### DatabaseAuditingConfiguration
DatabaseAuditingConfiguration defines the configuration for auditing database connection and authentication events

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| dbConnsAuditing | Enables auditing of database connection and authentication events. When enabled, connection, authentication, and disconnection events are tracked and sent to the configured audit listener (configured at the cluster level). The cluster-level auditing configuration must be set before enabling this on a database. | *bool |  | false |
[Back to Table of Contents](#table-of-contents)

### DbAlertsSettings
DbAlertsSettings An API object that represents the database alerts configuration.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| bdb_backup_delayed | Periodic backup has been delayed for longer than specified threshold value [minutes] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_crdt_src_high_syncer_lag | Active-active source - sync lag is higher than specified threshold value [seconds] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_crdt_src_syncer_connection_error | Active-active source - sync has connection error while trying to connect replica source | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_crdt_src_syncer_general_error | Active-active source - sync encountered in general error | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_high_latency | Latency is higher than specified threshold value [micro-sec] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_high_throughput | Throughput is higher than specified threshold value [requests / sec.] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_long_running_action | An alert for state-machines that are running for too long | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_low_throughput | Throughput is lower than specified threshold value [requests / sec.] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_ram_dataset_overhead | Dataset RAM overhead of a shard has reached the threshold value [% of its RAM limit] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_ram_values | Percent of values kept in a shard's RAM is lower than [% of its key count] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_replica_src_high_syncer_lag | Replica-of source - sync lag is higher than specified threshold value [seconds] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_replica_src_syncer_connection_error | Replica-of source - sync has connection error while trying to connect replica source | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_shard_num_ram_values | Number of values kept in a shard's RAM is lower than [values] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_size | Dataset size has reached the threshold value [% of the memory limit] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
| bdb_proxy_cert_expiring_soon | Proxy certificate will expire in less than specified threshold value [days] | *[BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold) |  | false |
[Back to Table of Contents](#table-of-contents)

### DbModule
Redis Enterprise module (see https://redis.io/docs/latest/develop/reference/modules/)

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The name of the module, e.g. "search" or "ReJSON". The complete list of modules available in the cluster can be retrieved from the '.status.modules' field in the REC. | string |  | true |
| version | The semantic version of the module, e.g. '1.6.12'. Optional for REDB, but must be set for REAADB. Note that this field is deprecated, and will be removed in future releases. for bundled modules, the version is ignored, and the latest version is used (the only one supported for each redis version) | string |  | false |
| config | Module command line arguments e.g. VKEY_MAX_ENTITY_COUNT 30 | string |  | false |
[Back to Table of Contents](#table-of-contents)

### FtpStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| url | a URI of the "ftps://[USER[:PASSWORD]@]HOST[:PORT]/PATH[/]" format | string |  | true |
[Back to Table of Contents](#table-of-contents)

### GoogleStorage
GoogleStorage

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| gcsSecretName | The name of the secret that holds the Google Cloud Storage credentials. The secret must contain the keys "CLIENT_ID", "PRIVATE_KEY", "PRIVATE_KEY_ID", "CLIENT_EMAIL" and these must hold the corresponding credentials. The keys should correspond to the values in the key JSON. | string |  | true |
| bucketName | Google Storage bucket name. | string |  | true |
| subdir | Optional. Google Storage subdir under bucket. | string | empty | false |
[Back to Table of Contents](#table-of-contents)

### InternalEndpoint


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| host | Hostname assigned to the database | string |  | false |
| port | Database port name | int |  | false |
[Back to Table of Contents](#table-of-contents)

### MountPointStorage
MountPointStorage

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| path | Path to the local mount point. You must create the mount point on all nodes, and the redislabs:redislabs user must have read and write permissions on the local mount point. | string |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseConnection
Connection between a database, and Its Redis Enterprise Cluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The name of the Redis Enterprise Cluster where the database should be stored. | string |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseDatabase
RedisEnterpriseDatabase is the Schema for the redisenterprisedatabases API

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#objectmeta-v1-meta) |  | false |
| spec |  | [RedisEnterpriseDatabaseSpec](#redisenterprisedatabasespec) |  | false |
| status |  | [RedisEnterpriseDatabaseStatus](#redisenterprisedatabasestatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseDatabaseList
RedisEnterpriseDatabaseList contains a list of RedisEnterpriseDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ListMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#listmeta-v1-meta) |  | false |
| items |  | [][RedisEnterpriseDatabase](#redisenterprisedatabase) |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseDatabaseSpec
RedisEnterpriseDatabaseSpec defines the desired state of RedisEnterpriseDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| redisEnterpriseCluster | Connection to the Redis Enterprise Cluster. | *[RedisEnterpriseConnection](#redisenterpriseconnection) |  | false |
| memorySize | Memory size for the database using formats like 100MB or 0.1GB. Minimum value is 100MB. For Auto Tiering (formerly Redis on Flash), this value represents RAM+Flash memory and must be at least 1GB. | string | 100MB | false |
| rackAware | Enables rack awareness for improved availability. See https://redis.io/docs/latest/operate/rs/clusters/configure/rack-zone-awareness/ | *bool |  | false |
| shardCount | Number of database server-side shards. | uint16 | 1 | false |
| replication | Enables in-memory database replication for higher availability. Creates a replica shard for every master shard. Defaults to false. | *bool | false | false |
| persistence | Database persistence policy for on-disk storage. | *[DatabasePersistence](#databasepersistence) | disabled | false |
| databaseSecretName | Name of the secret containing the database password (Redis databases only). The secret is created automatically if it doesn't exist. The password is stored under the 'password' key in the secret. If creating the secret manually, create an opaque secret with the password under the 'password' key. To disable authentication, set the value of the 'password' key in the secret to an empty string. Note: For Active-Active databases, this secret is not created automatically. For memcached databases, use memcachedSaslSecretName instead. | string |  | false |
| evictionPolicy | Database eviction policy. See https://redis.io/docs/latest/operate/rs/databases/memory-performance/eviction-policy/ | string | volatile-lru | false |
| tlsMode | TLS mode for database connections. enabled: All client and replication connections must use TLS. disabled: No connections use TLS. replica_ssl: Only replication connections use TLS. | string | disabled | false |
| clientAuthenticationCertificates | Names of secrets containing TLS client certificates for authentication. | []string |  | false |
| replicaSources | Source databases to replicate from. | [][ReplicaSource](#replicasource) |  | false |
| alertSettings | Database alert configuration. | *[DbAlertsSettings](#dbalertssettings) |  | false |
| backup | Target for automatic database backups. | *[BackupSpec](#backupspec) |  | false |
| modulesList | List of modules associated with the database. Retrieve valid modules from the REC object status. Use the "name" and "versions" fields for module configuration. To specify explicit module versions, disable automatic module upgrades by setting '.upgradeSpec.upgradeModulesToLatest' to 'false' in the REC. Note: Specifying module versions is deprecated and will be removed in future releases. for Redis version 8 and above, bundled modules are enabled automatically, so there is no need to specify them | *[][DbModule](#dbmodule) |  | false |
| rolesPermissions | Redis Enterprise ACL and role bindings to apply to the database. | [][RolePermission](#rolepermission) |  | false |
| defaultUser | Allows connections with the default user. When disabled, the DatabaseSecret is not created or updated. | *bool | true | false |
| ossCluster | Enables OSS Cluster mode. Note: Not all client libraries support OSS cluster mode. | *bool | false | false |
| proxyPolicy | Proxy policy for the database. Supported policies: single, all-master-shards, all-nodes. Defaults to single when ossCluster is disabled, all-master-shards when enabled. | string |  | false |
| dataInternodeEncryption | Internode encryption (INE) setting that overrides the cluster-wide policy. false: INE is disabled for this database regardless of cluster policy. true: INE is enabled if supported by the database, otherwise creation fails. unspecified: INE is disabled if not supported by the database. Deleting this property after setting it has no effect. | *bool |  | false |
| databasePort | TCP port assigned to the database within the Redis Enterprise cluster. Must be unique across all databases in the Redis Enterprise cluster. Generated automatically if omitted. Cannot be changed after creation. | *int |  | false |
| databaseServicePort | A custom port to be exposed by the database services. Can be modified/added/removed after REDB creation. If set, it'll replace the default service port (namely, databasePort or defaultRedisPort). | *int |  | false |
| shardsPlacement | Shard placement strategy: "dense" or "sparse". dense: Shards reside on as few nodes as possible. sparse: Shards are distributed across as many nodes as possible. | string | dense | false |
| type | Database type: redis or memcached. | *[DatabaseType](#databasetype) | redis | false |
| isRof | Enables Auto Tiering (formerly Redis on Flash) for Redis databases only. Defaults to false. | *bool | false | false |
| rofRamSize | RAM portion size for Auto Tiering (formerly Redis on Flash) databases using formats like 100MB or 0.1GB. For v1 (Redis < 8.0): Required. Must be at least 10% of the combined memory size (RAM+Flash) specified in "memorySize". For v2 (Redis >= 8.0): Optional. Specifies the maximum RAM limit for the database. When omitted, RS uses default configuration. Can be used together with rofRamRatio to control both RAM growth strategy and maximum RAM limit. | string |  | false |
| rofRamRatio | RAM allocation ratio for Redis Flex (v2) databases as a percentage of total data size. Valid range: 0-100. When omitted, RS uses the default value of 50%. Controls how much RAM is allocated per unit of data (e.g., 30% means 3MB RAM per 10MB data). RAM grows proportionally with data until rofRamSize limit is reached (if specified). Only applicable when isRof=true and Redis version >= 8.0 (BigStore v2 - Redis Flex). | *int |  | false |
| memcachedSaslSecretName | Name of the secret containing credentials for memcached database authentication. Store credentials in an opaque secret with 'username' and 'password' keys. Note: Connections are not encrypted. | string |  | false |
| redisVersion | Redis OSS version for the database. Specify version as <major.minor> prefix or use channels: 'major': Upgrades to the most recent major Redis version. 'latest': Upgrades to the most recent Redis version. To use 'latest', set redisUpgradePolicy on the cluster first. Back up the database before upgrading. Only applies to Redis databases. Note: Version specification is not supported for Active-Active databases. | string |  | false |
| upgradeSpec | Database upgrade configuration. | *[DBUpgradeSpec](#dbupgradespec) |  | false |
| activeActive | Connection and association information for Active-Active databases. | *[ActiveActiveInfo](#activeactiveinfo) |  | false |
| resp3 | Enables RESP3 protocol support for the database. Deleting this property after setting it has no effect. See the Redis Enterprise documentation for more information. | *bool |  | false |
| shardingEnabled | Enables database sharding for Active-Active databases. Enabled by default for REAADBs. For regular REDBs, use the shardCount field instead: shardCount = 1 disables sharding, shardCount > 1 enables sharding. | *bool |  | false |
| auditing | Database auditing configuration. | *[DatabaseAuditingConfiguration](#databaseauditingconfiguration) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseDatabaseStatus
RedisEnterpriseDatabaseStatus defines the observed state of RedisEnterpriseDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| databaseUID | Database UID provided by redis enterprise | string |  | false |
| specStatus | Whether the desired specification is valid | [SpecStatusName](#specstatusname) |  | false |
| status | The status of the database | [DatabaseStatus](#databasestatus) |  | false |
| createdTime | Time when the database was created | string |  | false |
| lastUpdated | Time when the database was last updated | string |  | false |
| shardStatuses | Aggregated statuses of shards | map[string]uint16 |  | false |
| lastActionUid | UID of the last action done by operator on this database | string |  | false |
| lastActionStatus | Status of the last action done by operator on this database | string |  | false |
| version | Database compatibility version | string |  | false |
| replicaSourceStatuses | ReplicaSource statuses | [][ReplicaSourceStatus](#replicasourcestatus) |  | false |
| internalEndpoints | Endpoints listed internally by the Redis Enterprise Cluster. Can be used to correlate a ReplicaSourceStatus entry. | [][InternalEndpoint](#internalendpoint) |  | false |
| redisEnterpriseCluster | The Redis Enterprise Cluster Object this Resource is associated with | string |  | false |
| observedGeneration | The generation (built in update counter of K8s) of the REDB resource that was fully acted upon, meaning that all changes were handled and sent as an API call to the Redis Enterprise Cluster (REC). This field value should equal the current generation when the resource changes were handled. Note: the lastActionStatus field tracks actions handled asynchronously by the Redis Enterprise Cluster. | int64 |  | false |
| backupInfo | Information on the database's periodic backup | *[BackupInfo](#backupinfo) |  | false |
| activeActive | Connection/ association to the Active-Active database. | *[ActiveActiveInfo](#activeactiveinfo) |  | false |
| bigstoreVersion | BigStore version for Redis on Flash databases (1 for Auto Tiering, 2 for Redis Flex). Read-only field populated from RS. | *int |  | false |
[Back to Table of Contents](#table-of-contents)

### ReplicaSource


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| replicaSourceType | The type of resource from which the source database URI is derived. If set to 'SECRET', the source database URI is derived from the secret named in the ReplicaSourceName field. The secret must have a key named 'uri' that defines the URI of the source database in the form of 'redis://...'. The type of secret (kubernetes, vault, ...) is determined by the secret mechanism used by the underlying REC object. If set to 'REDB', the source database URI is derived from the RedisEnterpriseDatabase resource named in the ReplicaSourceName field. | [ReplicaSourceType](#replicasourcetype) |  | true |
| replicaSourceName | The name of the resource from which the source database URI is derived. The type of resource must match the type specified in the ReplicaSourceType field. | string |  | true |
| compression | GZIP compression level (0-6) to use for replication. | int |  | false |
| clientKeySecret | Secret that defines the client certificate and key used by the syncer in the target database cluster. The secret must have 2 keys in its map: "cert" which is the PEM encoded certificate, and "key" which is the PEM encoded private key. | *string |  | false |
| serverCertSecret | Secret that defines the server certificate used by the proxy in the source database cluster. The secret must have 1 key in its map: "cert" which is the PEM encoded certificate. | *string |  | false |
| tlsSniName | TLS SNI name to use for the replication link. | *string |  | false |
[Back to Table of Contents](#table-of-contents)

### ReplicaSourceStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| lag | Lag in millisec between source and destination (while synced). | int |  | false |
| lastError | Last error encountered when syncing from the source. | string |  | false |
| lastUpdate | Time when we last receive an update from the source. | string |  | false |
| rdbSize | The source’s RDB size to be transferred during the syncing phase. | int |  | false |
| rdbTransferred | Number of bytes transferred from the source’s RDB during the syncing phase. | int |  | false |
| status | Sync status of this source | string |  | false |
| endpointHost | The internal host name of the replica source database. Can be used as an identifier. See the internalEndpoints list on the REDB status. | string |  | true |
[Back to Table of Contents](#table-of-contents)

### RolePermission
Redis Enterprise Role and ACL Binding

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| type | Type of Redis Enterprise Database Role Permission. Currently, only "redis-enterprise" is supported, which uses roles and ACLs defined within Redis Enterprise directly. | [RolePermissionType](#rolepermissiontype) | redis-enterprise | true |
| role | Role Name of RolePermissionType (note: use exact name of the role from the Redis Enterprise role list, case sensitive) | string |  | true |
| acl | Acl Name of RolePermissionType (note: use exact name of the ACL from the Redis Enterprise ACL list, case sensitive) | string |  | true |
[Back to Table of Contents](#table-of-contents)

### S3Storage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| awsSecretName | The name of the secret that holds the AWS credentials. The secret must contain the keys "AWS_ACCESS_KEY_ID" and "AWS_SECRET_ACCESS_KEY", and these must hold the corresponding credentials. | string |  | true |
| bucketName | Amazon S3 bucket name. | string |  | true |
| subdir | Optional. Amazon S3 subdir under bucket. | string | empty | false |
[Back to Table of Contents](#table-of-contents)

### SftpStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| sftpSecretName | The name of the secret that holds SFTP credentials. The secret must contain the "Key" key, which is the SSH private key for connecting to the sftp server. | string |  | true |
| sftp_url | SFTP url | string |  | true |
[Back to Table of Contents](#table-of-contents)

### SwiftStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| swiftSecretName | The name of the secret that holds Swift credentials. The secret must contain the keys "Key" and "User", and these must hold the corresponding credentials: service access key and service user name (pattern for the latter does not allow special characters &,<,>,") | string |  | true |
| auth_url | Swift service authentication URL. | string |  | true |
| container | Swift object store container for storing the backup files. | string |  | true |
| prefix | Optional. Prefix (path) of backup files in the swift container. | string | empty | false |
[Back to Table of Contents](#table-of-contents)
## Enums

### DatabasePersistence
Database persistence policy. see https://redis.io/docs/latest/operate/rs/databases/configure/database-persistence/

| Value | Description |
| ----- | ----------- |
| "disabled" | Data is not persisted |
| "aofEverySecond" | Data is synced to disk every second |
| "aofAlways" | Data is synced to disk with every write. |
| "snapshotEvery1Hour" | A snapshot of the database is created every hour |
| "snapshotEvery6Hour" | A snapshot of the database is created every 6 hours. |
| "snapshotEvery12Hour" | A snapshot of the database is created every 12 hours. |
[Back to Table of Contents](#table-of-contents)

### DatabaseStatus
State of the Redis Enterprise Database

| Value | Description |
| ----- | ----------- |
| "pending" | Database is pending creation |
| "active" | Database is ready to be used |
| "active-change-pending" | Database is ready to be used, but a change is pending |
| "delete-pending" | Database will be deleted soon |
| "import-pending" | Database will be imported soon |
| "creation-failed" | Database creation has failed |
| "recovery" | Database creation has failed |
| "" | Database status unknown |
[Back to Table of Contents](#table-of-contents)

### DatabaseType

| Value | Description |
| ----- | ----------- |
| "redis" |  |
| "memcached" |  |
[Back to Table of Contents](#table-of-contents)

### ReplicaSourceType

| Value | Description |
| ----- | ----------- |
| "SECRET" | When ReplicaSourceType is set to 'SECRET', the source database URI is derived from the secret named in the ReplicaSourceName field. The secret must have a key named 'uri' that defines the URI of the source database in the form of 'redis://...'. The type of secret (kubernetes, vault, ...) is determined by the secret mechanism used by the underlying REC object. |
| "REDB" | When ReplicaSourceType is set to 'REDB', the source database URI is derived from the RedisEnterpriseDatabase resource named in the ReplicaSourceName field. |
[Back to Table of Contents](#table-of-contents)

### RolePermissionType

| Value | Description |
| ----- | ----------- |
| "redis-enterprise" | Use Roles and ACLs defined within Redis Enterprise directly |
[Back to Table of Contents](#table-of-contents)
