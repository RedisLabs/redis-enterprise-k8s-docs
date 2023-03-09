# Redis Enterprise Active Active Database API
This document describes the parameters for the Redis Enterprise Active Active Database custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [ParticipatingCluster](#participatingcluster)
  * [ParticipatingClusterStatus](#participatingclusterstatus)
  * [RedisEnterpriseActiveActiveDatabase](#redisenterpriseactiveactivedatabase)
  * [RedisEnterpriseActiveActiveDatabaseList](#redisenterpriseactiveactivedatabaselist)
  * [RedisEnterpriseActiveActiveDatabaseSpec](#redisenterpriseactiveactivedatabasespec)
  * [RedisEnterpriseActiveActiveDatabaseStatus](#redisenterpriseactiveactivedatabasestatus)
  * [SecretStatus](#secretstatus)
* [Enums](#enums)
  * [ActiveActiveDatabaseSecretStatus](#activeactivedatabasesecretstatus)
  * [ActiveActiveDatabaseStatus](#activeactivedatabasestatus)
## Objects

### ParticipatingCluster
Instance/cluster specifications and configurations.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The name of the remote cluster CR to link. | string |  | true |
[Back to Table of Contents](#table-of-contents)

### ParticipatingClusterStatus
Status of participating cluster.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The name of the remote cluster CR that is linked. | string |  | true |
| id | The corresponding ID of the instance in the active-active database. | *int64 |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseActiveActiveDatabase
RedisEnterpriseActiveActiveDatabase is the schema for the redisenterpriseactiveactivedatabase API

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#objectmeta-v1-meta) |  | false |
| spec |  | [RedisEnterpriseActiveActiveDatabaseSpec](#redisenterpriseactiveactivedatabasespec) |  | false |
| status |  | [RedisEnterpriseActiveActiveDatabaseStatus](#redisenterpriseactiveactivedatabasestatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseActiveActiveDatabaseList
RedisEnterpriseActiveActiveDatabaseList contains a list of RedisEnterpriseActiveActiveDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ListMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#listmeta-v1-meta) |  | false |
| items |  | [][RedisEnterpriseActiveActiveDatabase](#redisenterpriseactiveactivedatabase) |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseActiveActiveDatabaseSpec
RedisEnterpriseActiveActiveDatabaseSpec defines the desired state of RedisEnterpriseActiveActiveDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| redisEnterpriseCluster | Connection to Redis Enterprise Cluster | *[RedisEnterpriseConnection](#redisenterpriseconnection) |  | false |
| participatingClusters | The list of instances/ clusters specifications and configurations. | []*[ParticipatingCluster](#participatingcluster) |  | true |
| globalConfigurations | The Active-Active database global configurations, contains the global properties for each of the participating clusters/ instances databases within the Active-Active database. | *[RedisEnterpriseDatabaseSpec](#redisenterprisedatabasespec) |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseActiveActiveDatabaseStatus
RedisEnterpriseActiveActiveDatabaseStatus defines the observed state of RedisEnterpriseActiveActiveDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| specStatus | Whether the desired specification is valid | [SpecStatusName](#specstatusname) |  | false |
| status | The status of the active active database. | [ActiveActiveDatabaseStatus](#activeactivedatabasestatus) |  | false |
| participatingClusters | The list of instances/ clusters statuses. | []*[ParticipatingClusterStatus](#participatingclusterstatus) |  | false |
| globalConfigurations | The active-active default global configurations linked REDB | string |  | false |
| linkedRedbs | The linked REDBs. | []string |  | false |
| guid | The active-active database corresponding GUID. | string |  | false |
| lastTaskUid | The last active-active database task UID. | string |  | false |
| redisEnterpriseCluster | The Redis Enterprise Cluster Object this Resource is associated with | string |  | false |
| secretsStatus | The status of the secrets | []*[SecretStatus](#secretstatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### SecretStatus
Status of secrets.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | The name of the secret. | string |  | true |
| status | The status of the secret. | [ActiveActiveDatabaseSecretStatus](#activeactivedatabasesecretstatus) |  | false |
[Back to Table of Contents](#table-of-contents)
## Enums

### ActiveActiveDatabaseSecretStatus

| Value | Description |
| ----- | ----------- |
| "Invalid" |  |
| "Valid" |  |
[Back to Table of Contents](#table-of-contents)

### ActiveActiveDatabaseStatus

| Value | Description |
| ----- | ----------- |
| "pending" | Active-active database is pending creation. |
| "active" | Active-active database is ready to be used. |
| "active-change-pending" | Database is ready to be used, but a change is pending. |
| "delete-pending" | Active-active database will be deleted soon. |
| "creation-failed" | Active-active database creation has failed. |
| "error" | Active-active database is in recovery. ActiveActiveDatabaseStatusRecovery ActiveActiveDatabaseStatus = "recovery" Active-active database status error. |
| "" | Active-active database status unknown. |
[Back to Table of Contents](#table-of-contents)
