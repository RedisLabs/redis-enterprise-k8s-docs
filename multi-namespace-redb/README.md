# Multi-Namespaced REDB

The Redis Enterprise Operator provides a method for a single deployed operator/cluster combination to listen for REDB objects in multiple specified individual namespaces.

In order to do this, there are a few changes from a traditional operator and RedisEnterpriseCluster deployment

## Deployment steps
### 1. Redis Enterprise Cluster Deployment
Deploy a Redis Enterprise Cluster, see [README](../README.md)
### 2. Adjusting role/role_bindings in watched namespaces

Both the operator's and the RedisEnterpriseCluster custom resource's (same name as the REC, unless manually overridden) service accounts have to be given access via a namespaced role and role_binding in each individual namespace that the operator is expected to watch. Apply those documents within the watched namespaces:

```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: redb-role
rules:
  - apiGroups:
      - app.redislabs.com
    resources:
      - "*"
    verbs:
      - "*"
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["*"]
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create"]
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "watch", "list", "update", "patch", "create", "delete"]

---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: redb-role
subjects:
- kind: ServiceAccount
  name: redis-enterprise-operator
  namespace: NAMESPACE_OF_SERVICE_ACCOUNT
- kind: ServiceAccount
  name: NAME_OF_REC_SERVICE_ACCOUNT  # service account of the REC, usually the same as the name of the custom resource
  namespace: NAMESPACE_OF_SERVICE_ACCOUNT
roleRef:
  kind: Role
  name: redb-role
  apiGroup: rbac.authorization.k8s.io

```

### 3. Updating the operator deployment

The operator has to be deployed with a comma seperated list of namespaces it will watch for REDB objects.

Specifically, a new environment variable is added to the operator's container (edit the redis-enterprise-deployment deployment within the operator namespace):

```yaml
env:
...
- name: REDB_NAMESPACES
value: "comma,delimited,list,of,namespaces,to,watch"
...
``` 
### 4. Updating the admission control deployment
Admission control for REDB is recommended. If that is used, repeat step 3 to update the admission-deploy deployment (same environment variable).

After these steps have been done, users within the specified namespaces that have permission to create REDB objects will be able to create them.  The database will be created within the centrally managed redis enterprise cluster and services corresponding to the databases will be visible within the namespace.

## Additional areas for consideration
* When deploying multiple Redis Enterprise Operators within the same K8s cluster, do not configure more than one of the operators to watch the same namespace.
* Only configure the operator to watch a namespace once the namespace is created and configured with the role/role_binding as explained above. If configured to watch a namespace without setting those permissions or a namespace that is not created yet, the operator will fail and not perform normal operations.
* The Redis Enterprise Operator creates a service named after the REDB within the REDB namespace. The service is of type "External Name". This service can only be accessed from within the K8s cluster. Configuring Load Balancer/Node Port services automatically is not supported at this time. The service type configuration within the Redis Enterprise Cluster custom resource will be ignored. The External Name service will point to another ClusterIP service created within the operator namespace, exposing the actual Redis endpoint.
