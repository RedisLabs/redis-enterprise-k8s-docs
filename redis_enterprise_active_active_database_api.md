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
  * [ReplicationStatus](#replicationstatus)
## Objects

### ParticipatingCluster
Specifies the configuration for a participating cluster in the Active-Active database.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | Name of the remote cluster custom resource to link. | string |  | true |
| externalReplicationPort | Port number for the replication endpoint. Use this field when you use LoadBalancers for synchronization between Active-Active replicas and need to specify the port number that the LoadBalancer listens on. | *int |  | false |
| namespace | Namespace where the REAADB object is deployed within the corresponding participating cluster. Ensure that the Redis Enterprise operator is configured to watch this namespace in the corresponding cluster and that the required RBAC configuration is properly set up. For more information about setting up multiple namespaces, see https://redis.io/docs/latest/operate/kubernetes/re-clusters/multi-namespace/. If you don't specify a namespace, the REAADB is deployed to the REC's namespace in the corresponding cluster. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### ParticipatingClusterStatus
The status of a participating cluster.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | Name of the linked remote cluster custom resource. | string |  | true |
| id | ID of the instance in the Active-Active database. | *int64 |  | false |
| replicationStatus | Replication status of the participating cluster. | [ReplicationStatus](#replicationstatus) |  | false |
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
| redisEnterpriseCluster | Connection to the Redis Enterprise Cluster. | *[RedisEnterpriseConnection](#redisenterpriseconnection) |  | false |
| participatingClusters | List of participating cluster specifications and configurations. | []*[ParticipatingCluster](#participatingcluster) |  | true |
| globalConfigurations | Global configurations for the Active-Active database. Contains the global properties for each participating cluster database within the Active-Active database. | *[RedisEnterpriseDatabaseSpec](#redisenterprisedatabasespec) |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseActiveActiveDatabaseStatus
RedisEnterpriseActiveActiveDatabaseStatus defines the observed state of RedisEnterpriseActiveActiveDatabase

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| specStatus | Indicates whether the desired specification is valid. | [SpecStatusName](#specstatusname) |  | false |
| status | Status of the Active-Active database. This status doesn't include the replication link (data path) status. To view the replication link status, see the ReplicationStatus field or status.replicationStatus on the custom resource. | [ActiveActiveDatabaseStatus](#activeactivedatabasestatus) |  | false |
| participatingClusters | List of participating cluster statuses. | []*[ParticipatingClusterStatus](#participatingclusterstatus) |  | false |
| globalConfigurations | Name of the REDB with the default global configurations for the Active-Active database. | string |  | false |
| linkedRedbs | List of linked REDBs. | []string |  | false |
| guid | GUID of the Active-Active database. | string |  | false |
| lastTaskUid | UID of the last Active-Active database task. | string |  | false |
| redisEnterpriseCluster | Name of the Redis Enterprise Cluster that this resource is associated with. | string |  | false |
| secretsStatus | Status of the secrets. | []*[SecretStatus](#secretstatus) |  | false |
| replicationStatus | Overall replication status. | [ReplicationStatus](#replicationstatus) |  | false |
| clusterCertificatesGeneration | Certificate generation number from the participating cluster's REC.Status.CertificatesStatus.Generation. The operator monitors this field to detect when proxy or syncer certificates are updated on the local participating cluster. When the operator detects a change, it automatically runs a CRDB force update (equivalent to 'crdb-cli crdb update --force'), which synchronizes the certificate changes to all participating clusters and prevents sync issues. This eliminates the manual step of running crdb-cli commands when you rotate certificates in Active-Active deployments on Kubernetes. | *int64 |  | false |
[Back to Table of Contents](#table-of-contents)

### SecretStatus
The status of a secret.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| name | Name of the secret. | string |  | true |
| status | Status of the secret. | [ActiveActiveDatabaseSecretStatus](#activeactivedatabasesecretstatus) |  | false |
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
| "pending" | The Active-Active database is pending creation. |
| "active" | The Active-Active database is ready to use. |
| "active-change-pending" | The database is ready to use, but a change is pending. |
| "delete-pending" | The Active-Active database is scheduled for deletion. |
| "creation-failed" | Active-Active database creation failed. |
| "error" | The Active-Active database is in recovery. ActiveActiveDatabaseStatusRecovery ActiveActiveDatabaseStatus = "recovery" The Active-Active database encountered an error. |
| "" | The Active-Active database status is unknown. |
[Back to Table of Contents](#table-of-contents)

### ReplicationStatus

| Value | Description |
| ----- | ----------- |
| "up" |  |
| "down" |  |
[Back to Table of Contents](#table-of-contents)
