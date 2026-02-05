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
| upgradeModulesToLatest | Upgrades the modules to the latest version that supportes the DB version during a DB upgrade action, to upgrade the DB version view the 'redisVersion' field. Notes - All modules must be without specifing the version. in addition, This field is currently not supported for Active-Active databases. | *bool |  | true |
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
[Back to Table of Contents](#table-of-contents)

### DbModule
Redis Enterprise Module: https://redislabs.com/redis-enterprise/modules/

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The module's name e.g "ft" for redissearch | string |  | true |
| version | Module's semantic version e.g "1.6.12" - optional only in REDB, must be set in REAADB | string |  | false |
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
| redisEnterpriseCluster | Connection to Redis Enterprise Cluster | *[RedisEnterpriseConnection](#redisenterpriseconnection) |  | false |
| memorySize | memory size of database. use formats like 100MB, 0.1GB. minimum value in 100MB. When redis on flash (RoF) is enabled, this value refers to RAM+Flash memory, and it must not be below 1GB. | string | 100MB | false |
| rackAware | Whether database should be rack aware. This improves availability - more information: https://docs.redislabs.com/latest/rs/concepts/high-availability/rack-zone-awareness/ | *bool |  | false |
| shardCount | Number of database server-side shards | uint16 | 1 | false |
| replication | In-memory database replication. When enabled, database will have replica shard for every master - leading to higher availability. Defaults to false. | *bool | false | false |
| persistence | Database on-disk persistence policy | *[DatabasePersistence](#databasepersistence) | disabled | false |
| databaseSecretName | The name of the secret that holds the password to the database (redis databases only). If secret does not exist, it will be created. To define the password, create an opaque secret and set the name in the spec. The password will be taken from the value of the 'password' key. Use an empty string as value within the secret to disable authentication for the database. Notes - For Active-Active databases this secret will not be automatically created, and also, memcached databases must not be set with a value, and a secret/password will not be automatically created for them. Use the memcachedSaslSecretName field to set authentication parameters for memcached databases. | string |  | false |
| evictionPolicy | Database eviction policy. see more https://docs.redislabs.com/latest/rs/administering/database-operations/eviction-policy/ | string | volatile-lru | false |
| tlsMode | Require SSL authenticated and encrypted connections to the database. enabled - all incoming connections to the Database must use SSL. disabled - no incoming connection to the Database should use SSL. replica_ssl - databases that replicate from this one need to use SSL. | string | disabled | false |
| clientAuthenticationCertificates | The Secrets containing TLS Client Certificate to use for Authentication | []string |  | false |
| replicaSources | What databases to replicate from | [][ReplicaSource](#replicasource) |  | false |
| alertSettings | Settings for database alerts | *[DbAlertsSettings](#dbalertssettings) |  | false |
| backup | Target for automatic database backups. | *[BackupSpec](#backupspec) |  | false |
| modulesList | List of modules associated with database. Note - For Active-Active databases this feature is currently in preview. For this feature to take effect for Active-Active databases, set a boolean environment variable with the name "ENABLE_ALPHA_FEATURES" to True. This variable can be set via the redis-enterprise-operator pod spec, or through the operator-environment-config Config Map. | *[][DbModule](#dbmodule) |  | false |
| rolesPermissions | List of Redis Enteprise ACL and Role bindings to apply | [][RolePermission](#rolepermission) |  | false |
| defaultUser | Is connecting with a default user allowed?  If disabled, the DatabaseSecret will not be created or updated | *bool | true | false |
| ossCluster | OSS Cluster mode option. Note that not all client libraries support OSS cluster mode. | *bool | false | false |
| proxyPolicy | The policy used for proxy binding to the endpoint. Supported proxy policies are: single/all-master-shards/all-nodes When left blank, the default value will be chosen according to the value of ossCluster - single if disabled, all-master-shards when enabled | string |  | false |
| dataInternodeEncryption | Internode encryption (INE) setting. An optional boolean setting, overriding a similar cluster-wide policy. If set to False, INE is guaranteed to be turned off for this DB (regardless of cluster-wide policy). If set to True, INE will be turned on, unless the capability is not supported by the DB ( in such a case we will get an error and database creation will fail). If left unspecified, will be disabled if internode encryption is not supported by the DB (regardless of cluster default). Deleting this property after explicitly setting its value shall have no effect. | *bool |  | false |
| databasePort | Database port number. TCP port on which the database is available. Will be generated automatically if omitted. can not be changed after creation | *int |  | false |
| shardsPlacement | Control the density of shards - should they reside on as few or as many nodes as possible. Available options are "dense" or "sparse". If left unset, defaults to "dense". | string |  | false |
| type | The type of the database. | *[DatabaseType](#databasetype) | redis | false |
| isRof | Whether it is an RoF database or not. Applicable only for databases of type "REDIS". Assumed to be false if left blank. | *bool |  | false |
| rofRamSize | The size of the RAM portion of an RoF database. Similarly to "memorySize" use formats like 100MB, 0.1GB It must be at least 10% of combined memory size (RAM+Flash), as specified by "memorySize". | string |  | false |
| memcachedSaslSecretName | Credentials used for binary authentication in memcached databases. The credentials should be saved as an opaque secret and the name of that secret should be configured using this field. For username, use 'username' as the key and the actual username as the value. For password, use 'password' as the key and the actual password as the value. Note that connections are not encrypted. | string |  | false |
| redisVersion | Redis OSS version. Version can be specified via <major.minor> prefix, or via channels - for existing databases - Upgrade Redis OSS version. For new databases - the version which the database will be created with. If set to 'major' - will always upgrade to the most recent major Redis version. If set to 'latest' - will always upgrade to the most recent Redis version. Depends on 'redisUpgradePolicy' - if you want to set the value to 'latest' for some databases, you must set redisUpgradePolicy on the cluster before. Possible values are 'major' or 'latest' When using upgrade - make sure to backup the database before. This value is used only for database type 'redis' | string |  | false |
| upgradeSpec | Specifications for DB upgrade. | *[DBUpgradeSpec](#dbupgradespec) |  | false |
| activeActive | Connection/ association to the Active-Active database. | *[ActiveActiveInfo](#activeactiveinfo) |  | false |
| resp3 | Whether this database supports RESP3 protocol. Note - Deleting this property after explicitly setting its value shall have no effect. Please view the corresponding field in RS doc for more info. | *bool |  | false |
| shardingEnabled | Toggles database sharding for REAADBs (Active Active databases) and enabled by default. This field is blocked for REDB (non-Active Active databases) and sharding is toggled via the shardCount field - when shardCount is 1 this is disabled otherwise enabled. | *bool |  | false |
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
| type | Type of Redis Enterprise Database Role Permission | [RolePermissionType](#rolepermissiontype) |  | true |
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
Database persistence policy. see https://docs.redislabs.com/latest/rs/concepts/data-access/persistence/

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
