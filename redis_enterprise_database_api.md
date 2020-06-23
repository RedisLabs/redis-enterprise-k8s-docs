# Redis Enterprise Database API
This document describes the parameters for the Redis Enterprise Database custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [RedisEnterpriseConnection](#redisenterpriseconnection)
  * [RedisEnterpriseDatabase](#redisenterprisedatabase)
  * [RedisEnterpriseDatabaseList](#redisenterprisedatabaselist)
  * [RedisEnterpriseDatabaseSpec](#redisenterprisedatabasespec)
  * [RedisEnterpriseDatabaseStatus](#redisenterprisedatabasestatus)
* [Enums](#enums)
  * [DatabasePersistence](#databasepersistence)
  * [DatabaseStatus](#databasestatus)
## Objects

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
| redisEnterpriseCluster | Connection to Redis Enterprise Cluster | [RedisEnterpriseConnection](#redisenterpriseconnection) |  | true |
| memorySize | memory size of database. use formats like 100MB, 0.1GB. minimum value in 100MB. | string | 100MB | false |
| rackAware | Whether database should be rack aware. This improves availability - more information: https://docs.redislabs.com/latest/rs/concepts/high-availability/rack-zone-awareness/ | *bool |  | false |
| shardCount | Number of database server-side shards | uint16 | 1 | false |
| replication | In-memory database replication. When enabled, database will have replica shard for every master - leading to higher availability. | *bool | false | false |
| persistence | Database on-disk persistence policy | *[DatabasePersistence](#databasepersistence) | disabled | false |
| databaseSecretName | The name of the K8s secret that holds the password to the database. | string |  | false |
| evictionPolicy | Database eviction policy. see more https://docs.redislabs.com/latest/rs/administering/database-operations/eviction-policy/ | string | volatile-lru | false |
| tlsMode | Require SSL authenticated and encrypted connections to the database. enabled - all incoming connections to the Database must use SSL. disabled - no incoming connection to the Database should use SSL. replica_ssl - databases that replicate from this one need to use SSL. | string | disabled | false |
| enforceClientAuthentication | Require authentication of client certificates for SSL connections to the database. | *bool | true | false |
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
[Back to Table of Contents](#table-of-contents)
## Enums

### DatabasePersistence
Database persistence policy. see https://docs.redislabs.com/latest/rs/concepts/data-access/persistence/

| Value | Description |
| ----- | ----------- |
| DatabasePersistenceDisabled | Data is not persisted |
| DatabasePersistenceAofEverySecond | Data is synced to disk every second |
| DatabasePersistenceAofAlways | Data is synced to disk with every write. |
| DatabasePersistenceSnapshotEveryHour | A snapshot of the database is created every hour |
| DatabasePersistenceSnapshotEvery6Hour | A snapshot of the database is created every 6 hours. |
| DatabasePersistenceSnapshotEvery12Hour | A snapshot of the database is created every 12 hours. |
[Back to Table of Contents](#table-of-contents)

### DatabaseStatus
State of the Redis Enterprise Database

| Value | Description |
| ----- | ----------- |
| DatabaseStatusPending | Database is pending creation |
| DatabaseStatusActive | Database is ready to be used |
| DatabaseStatusActiveChangePending | Database is ready to be used, but a change is pending |
| DatabaseStatusDeletePending | Database will be deleted soon |
| DatabaseStatusImportPending | Database will be imported soon |
| DatabaseStatusCreationFailed | Database creation has failed |
| DatabaseStatusRecovery | Database creation has failed |
| DatabaseStatusUnknown | Database status unknown |
[Back to Table of Contents](#table-of-contents)
