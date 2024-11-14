# Redis Enterprise Remote Cluster API
This document describes the parameters for the Redis Enterprise Remote Cluster custom resource
> Note this document is auto-generated from code comments. To contribute a change please change the code comments.
## Table of Contents
* [Objects](#objects)
  * [RedisEnterpriseRemoteCluster](#redisenterpriseremotecluster)
  * [RedisEnterpriseRemoteClusterList](#redisenterpriseremoteclusterlist)
  * [RedisEnterpriseRemoteClusterSpec](#redisenterpriseremoteclusterspec)
  * [RedisEnterpriseRemoteClusterStatus](#redisenterpriseremoteclusterstatus)
* [Enums](#enums)
  * [RemoteClusterStatus](#remoteclusterstatus)
## Objects

### RedisEnterpriseRemoteCluster
RedisEntepriseRemoteCluster represents a remote participating cluster.

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ObjectMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#objectmeta-v1-meta) |  | false |
| spec |  | [RedisEnterpriseRemoteClusterSpec](#redisenterpriseremoteclusterspec) |  | false |
| status |  | [RedisEnterpriseRemoteClusterStatus](#redisenterpriseremoteclusterstatus) |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseRemoteClusterList
RedisEnterpriseRemoteClusterList contains a list of RedisEnterpriseRemoteCluster

| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| metadata |  | [metav1.ListMeta](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.24/#listmeta-v1-meta) |  | false |
| items |  | [][RedisEnterpriseRemoteCluster](#redisenterpriseremotecluster) |  | true |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseRemoteClusterSpec


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| recName | The name of the REC that the RERC is pointing at | string |  | true |
| recNamespace | The namespace of the REC that the RERC is pointing at | string |  | true |
| secretName | The name of the secret containing cluster credentials. Must be of the following format: "redis-enterprise-<RERC name>" | string |  | false |
| apiFqdnUrl | The URL of the cluster, will be used for the active-active database URL. | string |  | true |
| dbFqdnSuffix | The database URL suffix, will be used for the active-active database replication endpoint and replication endpoint SNI. | string |  | false |
[Back to Table of Contents](#table-of-contents)

### RedisEnterpriseRemoteClusterStatus


| Field | Description | Scheme | Default Value | Required |
| ----- | ----------- | ------ | -------- | -------- |
| local | Indicates whether this object represents a local or a remote cluster. | *bool |  | false |
| status | The status of the remote cluster. | [RemoteClusterStatus](#remoteclusterstatus) |  | false |
| specStatus | Whether the desired specification is valid. | [SpecStatusName](#specstatusname) |  | false |
| observedGeneration | observedGeneration is the most recent generation observed for this RERC. It corresponds to the RERC's generation, which is updated by the API Server. | int64 |  | false |
[Back to Table of Contents](#table-of-contents)
## Enums

### RemoteClusterStatus
TODO: Add a kubebuilder enum annotation here.

| Value | Description |
| ----- | ----------- |
| "Active" |  |
| "Error" |  |
[Back to Table of Contents](#table-of-contents)
