# Redis Enterprise Database API
This document describes the parameters for the Redis Enterprise Database custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [AzureBlobStorage](#azureblobstorage)
  * [BackupInfo](#backupinfo)
  * [BackupSpec](#backupspec)
  * [BdbAlertSettingsWithThreshold](#bdbalertsettingswiththreshold)
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
  * [RepliceSourceType](#replicesourcetype)
  * [RolePermissionType](#rolepermissiontype)
## Objects

### AzureBlobStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| absSecretName | The name of the secret that holds ABS credentials. The secret must contain the keys \"AccountName\" and \"AccountKey\", and these must hold the corresponding credentials | string |  | true |
| container | Azure Blob Storage container name. | string |  | true |
| subdir | Optional. Azure Blob Storage subdir under container. | string | empty | false |
[Back to Table of Contents](#table-of-contents)

### BackupInfo


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| backupFailureReason | Reason of last failed backup process | string |  | false |
| backupHistory | Backup history retention policy (number of days, 0 is forever) | int |  | true |
| backupInterval | Interval in seconds in which automatic backup will be initiated | int |  | false |
| backupIntervalOffset | Offset (in seconds) from round backup interval when automatic backup will be initiated (should be less than backup_interval) | int |  | false |
| backupProgressPercentage | Database scheduled periodic backup progress (percentage) | int |  | false |
| backupStatus | Status of scheduled periodic backup process | string |  | false |
| lastBackupTime | Time of last successful backup | string |  | false |
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
| name | The module's name e.g \"ft\" for redissearch | string |  | true |
| version | Module's semantic version e.g \"1.6.12\" | string |  | true |
| config | Module command line arguments e.g. VKEY_MAX_ENTITY_COUNT 30 | string |  | false |
[Back to Table of Contents](#table-of-contents)

### FtpStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| url | a URI of the \"ftps://[USER[:PASSWORD]@]HOST[:PORT]/PATH[/]\" format | string |  | true |
[Back to Table of Contents](#table-of-contents)

### GoogleStorage
GoogleStorage

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| gcsSecretName | The name of the secret that holds the Google Cloud Storage credentials. The secret must contain the keys \"CLIENT_ID\", \"PRIVATE_KEY\", \"PRIVATE_KEY_ID\", \"CLIENT_EMAIL\" and these must hold the corresponding credentials. The keys should correspond to the values in the key JSON. | string |  | true |
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
| metadata |  | [metav1.ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#objectmeta-v1-meta) |  | false |
| spec |  | [RedisEnterpriseDatabaseSpec](#redisenterprisedatabasespec) |  | false |
| status |  | [RedisEnterpriseDatabaseStatus](#redisenterprisedatabasestatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseDatabaseList
RedisEnterpriseDatabaseList contains a list of RedisEnterpriseDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ListMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#listmeta-v1-meta) |  | false |
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
| replication | In-memory database replication. When enabled, database will have replica shard for every master - leading to higher availability. | *bool | false | false |
| persistence | Database on-disk persistence policy | *[DatabasePersistence](#databasepersistence) | disabled | false |
| databaseSecretName | The name of the secret that holds the password to the database. If secret does not exist, it will be created. To define the password, create an opaque secret and set the name in the spec. The password will be taken from the value of the 'password' key. Use an empty string as value to disable authentication for the database. | string |  | false |
| evictionPolicy | Database eviction policy. see more https://docs.redislabs.com/latest/rs/administering/database-operations/eviction-policy/ | string | volatile-lru | false |
| tlsMode | Require SSL authenticated and encrypted connections to the database. enabled - all incoming connections to the Database must use SSL. disabled - no incoming connection to the Database should use SSL. replica_ssl - databases that replicate from this one need to use SSL. | string | disabled | false |
| clientAuthenticationCertificates | The Secrets containing TLS Client Certificate to use for Authentication | []string |  | false |
| replicaSources | What databases to replicate from | [][ReplicaSource](#replicasource) |  | false |
| alertSettings | Settings for database alerts | *[DbAlertsSettings](#dbalertssettings) |  | false |
| backup | Target for automatic database backups. | *[BackupSpec](#backupspec) |  | false |
| modulesList | List of modules associated with database | *[][DbModule](#dbmodule) |  | false |
| rolesPermissions | List of Redis Enteprise ACL and Role bindings to apply | [][RolePermission](#rolepermission) |  | false |
| defaultUser | Is connecting with a default user allowed?  If disabled, the DatabaseSecret will not be created or updated | *bool | true | false |
| ossCluster | OSS Cluster mode option. Note that not all client libraries support OSS cluster mode. | *bool | false | false |
| proxyPolicy | The policy used for proxy binding to the endpoint. Supported proxy policies are: single/all-master-shards/all-nodes When left blank, the default value will be chosen according to the value of ossCluster - single if disabled, all-master-shards when enabled | string |  | false |
| dataInternodeEncryption | Internode encryption (INE) setting. An optional boolean setting, overriding a similar cluster-wide policy. If set to False, INE is guaranteed to be turned off for this DB (regardless of cluster-wide policy). If set to True, INE will be turned on, unless the capability is not supported by the DB ( in such a case we will get an error and database creation will fail). If left unspecified, will be disabled if internode encryption is not supported by the DB (regardless of cluster default). Deleting this property after explicitly setting its value shall have no effect. | *bool |  | false |
| databasePort | Database port number. TCP port on which the database is available. Will be generated automatically if omitted. can not be changed after creation | *int |  | false |
| shardsPlacement | Control the density of shards - should they reside on as few or as many nodes as possible. Available options are \"dense\" or \"sparse\". If left unset, defaults to \"dense\". | string |  | false |
| databaseType | The type of the database (RAM vs FLASH). Defaults to \"RAM\". | [DatabaseType](#databasetype) | RAM | false |
| rofRamSize | The size of the RAM portion of an RoF database. Similarly to \"memorySize\" use formats like 100MB, 0.1GB It must be at least 10% of combined memory size (RAM+Flash), as specified by \"memorySize\". | string |  | false |
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
[Back to Table of Contents](#table-of-contents)

### ReplicaSource


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| replicaSourceType | Determines what resource ReplicaSourceName refers to SECRET - Get URI from secret named in ReplicaSourceName.  The secret will have a key named 'uri' that defines the complete, redis:// URI.  The type of secret is determined by the secret mechanism used by the underlying REC object REDB - Determine URI from Kubernetes REDB resource named in ReplicaSourceName | [RepliceSourceType](#replicesourcetype) |  | true |
| replicaSourceName | Resource (SECRET/REDB) name of type ReplicaSourceType | string |  | true |
| compression | GZIP Compression level (0-9) to use for replication | int |  | false |
| clientKeySecret | Secret that defines what client key to use.  The secret needs 2 keys in its map, \"cert\" that is the PEM encoded certificate and \"key\" that is the PEM encoded private key | *string |  | false |
| serverCertSecret | Secret that defines the Server's certificate.  The secret needs 1 key in its map, \"cert\" that is the PEM encoded certificate | *string |  | false |
| tlsSniName | TLS SNI Name to use | *string |  | false |
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
| awsSecretName | The name of the secret that holds the AWS credentials. The secret must contain the keys \"AWS_ACCESS_KEY_ID\" and \"AWS_SECRET_ACCESS_KEY\", and these must hold the corresponding credentials. | string |  | true |
| bucketName | Amazon S3 bucket name. | string |  | true |
| subdir | Optional. Amazon S3 subdir under bucket. | string | empty | false |
[Back to Table of Contents](#table-of-contents)

### SftpStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| sftpSecretName | The name of the secret that holds SFTP credentials. The secret must contain the \"Key\" key, which is the SSH private key for connecting to the sftp server. | string |  | true |
| sftp_url | SFTP url | string |  | true |
[Back to Table of Contents](#table-of-contents)

### SwiftStorage


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| swiftSecretName | The name of the secret that holds Swift credentials. The secret must contain the keys \"Key\" and \"User\", and these must hold the corresponding credentials: service access key and service user name (pattern for the latter does not allow special characters &,<,>,\") | string |  | true |
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
| "RAM" |  |
| "FLASH" |  |
[Back to Table of Contents](#table-of-contents)

### RepliceSourceType

| Value | Description |
| ----- | ----------- |
| "SECRET" | Information on DB to Replicate from stored in a secret |
| "REDB" | Replicate from a DB created via the RedisEnterpriseDatabase Controller. Note - specify only names of REDBs created on the same namespace. To configure replicaof with a database configured on another namespace, use \"SECRET\". |
[Back to Table of Contents](#table-of-contents)

### RolePermissionType

| Value | Description |
| ----- | ----------- |
| "redis-enterprise" | Use Roles and ACLs defined within Redis Enterprise directly |
[Back to Table of Contents](#table-of-contents)
