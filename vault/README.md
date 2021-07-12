# Integrating the Redis Enterprise Operator with Hashicorp Vault
## Overview
Hashicorp Vault can be used to store secrets as an alternative to K8s secrets.<br>
Hashicorp Vault can be configured as the source of secrets used by the Redis Enterprise K8s operator. For now, <br>
the following items are supported:
* Redis Enterprise Cluster Credentials
* REDB admission TLS cert
* REDB secrets:
    * Replica of
    * Backup credentials
    * TLS keys
    * default user secret

This document explains how to use Hashicorp Vault as a source for secrets.

1. [ Prerequisites ](#prerequisites)
2. [ Deployment ](#deployment)
3. [ Deploying the operator ](#deployment_operator)
4. [ Creating the REC ](#deployment_rec)
5. [ Creating an REDB ](#deployment_redb)

> Note: when using Openshift it might be recommended to use oc instead of kubectl 
<a name="prerequisites"></a>
## Prerequisites
* Deploy a Hashicorp Vault instance and make sure there is network access to it from the Kubernetes cluster. The solution has been tested with Hashicorp Vault v1.6.2. The Hashicorp Vault instance must be using TLS.
* Configure the Hashicorp Vault Kubernetes authentication for the Kubernetes cluster the operator is being deployed. Refer to the Hashicorp Vault documentation for details.
* Deploy the Hashicorp Vault agent sidecar controller on the Kubernetes cluster (https://learn.hashicorp.com/tutorials/vault/kubernetes-sidecar)
* Note that Hashicorp offers a Vault Enterprise product. The Vault Enterprise product supports namespaces. Those namespaces should not be confused with Kubernetes namespaces. This document assumes that the Hashicorp Vault instance used is the Enterprise product, and a Vault namespace is used. The namespace is referred to as the <VAULT_NAMESPACE> below.
* Redis Enterprise will use a kv-v2 secret engine. Make sure it is available on the Hashicorp Vault instance (or create one if needed) and take note of the path it is mounted on, since it will be used later.

<a name="deployment"></a>
## Deployment
### General considerations
Hashicorp Vault and the Redis Enterprise Operator can be deployed in multiple scenarios that might affect the details of the process below. The document assumes the following:
* Hashicorp Vault enterprise is used, and Vault namespaces are used. If that is not the case, it is recommended to remove the namespace parameters, environment variables from the relevant directions.
* Multiple Redis Enterprise Clusters are configured within the same K8s cluster, configured to authenticate to Hashicorp Vault.
* To ensure privacy and avoid duplication, the K8S_NAMESPACE is appended to multiple names of Hashicorp Vault configurations. That might need to be further adjusted in cases multiple K8s clusters are used with the same K8s namespaces.
* The minimum TTL of the Vault token under the policy assigned to redis enterprise should be one hour. (see also https://learn.hashicorp.com/tutorials/vault/token-management#configure-the-token-ttl) 

<a name="deployment_operator"></a>
### Deploying the operator
1. Configure a Hashicorp Vault policy. The policy will be used to grant the operator access to the secrets.
   
   Run the following command within the Hashicorp Vault interface (use kubectl exec when Vault is deployed on Kubernetes, replace `<K8S_NAMESPACE>` with the namespace where the operator is deployed into):
    ```
    vault policy write -namespace=<VAULT_NAMESPACE> redisenterprise-<K8S_NAMESPACE> - <<EOF
    path "secret/data/redisenterprise-<K8S_NAMESPACE>/*" {
      capabilities = ["create", "read", "update", "delete", "list"]
    }
    path "secret/metadata/redisenterprise-<K8S_NAMESPACE>/*" {
      capabilities = ["list"]
    }
    EOF
    ```
2. Create a role to bind the Redis Enterprise operator service account to the policy configured in the previous step:
    ```
    vault write -namespace=<VAULT_NAMESPACE> auth/<AUTH_PATH>/role/redis-enterprise-operator-<K8S_NAMESPACE> \
            bound_service_account_names="redis-enterprise-operator"  \
            bound_service_account_namespaces=<K8S_NAMESPACE> \
            policies=redisenterprise-<K8S_NAMESPACE>
    ```
   > Note - replace `<AUTH_PATH>` with the path kubernetes auth is enabled in Hashicorp Vault. The default is "kubernetes"
3. Create the operator's configuration in configmap called with the relevant Vault configuration:<br>
   edit and save this content in a file called `operator-environment-config.yaml`<br>
   run `kubectl apply -f operator-environment-config.yaml`<br>
   see notes on the parameters below.
   ```
   apiVersion: v1
   kind: ConfigMap
   metadata:
      name: operator-environment-config
   data:
      CREDENTIAL_TYPE: "vault"
      VAULT_SERVER_FQDN: <Your FQDN>
      VAULT_SERVICE_PORT_HTTPS: "8200"
      VAULT_SECRET_ROOT: "secret"
      VAULT_SECRET_PREFIX: "redisenterprise-<K8S_NAMESPACE>"   
      VAULT_AUTH_PATH: <VAULT_AUTH_PATH>
      VAULT_NAMESPACE: <VAULT_NAMESPACE>
      VAULT_ROLE: "redis-enterprise-operator-<K8S_NAMESPACE>"
   ```
   * `VAULT_SERVER_FQDN`: Hashicorp Vault server Fully Qualified Domain Name (FQDN). If the Vault server is running with k8s,<br>
  it would typically be `<YOUR_VAULT_SERVICE_NAME>.<YOUR_VAULT_SERVICE_NAMESPACE>)`:
   * `VAULT_SECRET_ROOT`: the path the kv-2 secret engine being used is enabled on.
   * `VAULT_SECRET_PREFIX`: should be unique to the Redis Enterprise Cluster. Here we use `redisenterprise-<K8s_NAMESPACE>`.<br>
     This value has to be consistent with Hashicorp Vault roles and policies.
   * `VAULT_SERVER_FQDN`: the Fully Qualified Domain Name of the Hashicorp Vault server.
   * `VAULT_AUTH_PATH`: the path kubernetes auth is enabled in Hashicorp Vault,  defaults to `kubernetes` - use no leading/trailing slashes.<br>
   * `VAULT_NAMESPACE`: should be used when deploying with Hashicorp Vault enterprise.<br>
   * `VAULT_ROLE`: the Vault role you configured in the previous step, defaults to `redis-enterprise-opertaor`.<br>
   
4. Deploy the operator by applying the Redis Labs Kubernetes Operator Bundle as explained [here](../README.md) - steps 1,2 (steps 1-4 on OpenShift).<br>
   Once operator is running, proceed to the steps below. Avoid creating the Redis Enterprise Cluster custom resource.
5. Save the admission controller secret to Vault:
    1. Generate a json file with key/cert pair to be used by admission:
        ```
        kubectl exec -it $(kubectl get pod -l name=redis-enterprise-operator -o jsonpath='{.items[0].metadata.name}') -- /usr/local/bin/generate-tls -infer > output.json
        ```
    2. Apply the secret to vault - execute the following within the Hashicorp Vault CLI interface (you will need to copy the file from the previous step):
        ```
        vault kv put <VAULT_SECRET_ROOT>/redisenterprise-<K8S_NAMESPACE>/admission-tls @output.json
        ```
       > Note - the output.json file is needed for additional steps below (deployment of admission controller)   

6. Create a K8s secret containing the Certificate Authority Certificate (CACert) used to create the Hashicorp Vault instance server certificate.<br>
   Name the secret `vault-ca-cert` and the key `vault.ca` . Save the CA cert to a file before running the following command:
   ```
   kubectl create secret generic vault-ca-cert \
           --namespace <K8S_NAMESPACE> \
           --from-file=vault.ca=<vault instance server CA certificate path>
   ```
   > Note - the server certificate of the Hashicorp Vault instance must be signed by the Certificate Authority used within the secret. <br>

<a name="deployment_rec"></a>
### Creating the Redis Enterprise Cluster
1. Choose a random password. Unlike the default deployment, the operator is not creating a default password for the Redis Enterprise Cluster credentials, and those need to be chosen. It is recommended to use a tool to generate a random password at least 8 characters long.
2. Save the password as a secret within the Hashicorp Vault instance, replace values as needed. Execute the following command within the Hashicorp Vault CLI interface:
    ```
    vault kv put -namespace=<VAULT_NAMESPACE> <VAULT_SECRET_ROOT>/redisenterprise-<K8S_NAMESPACE>/<REC_NAME> username=<YOUR_USERNAME> password=<YOUR_PASSWORD>
    ```
   > Note - The username field in the REC spec will be ignored when using vault. The username from the vault secret will be used instead.
   > Note - this example matches configuring the operator with environment variable values: VAULT_SECRET_ROOT=secret, VAULT_SECRET_PREFIX=redisenterprise-<K8s_NAMESPACE> as mentioned above
3. Create a role in vault for the REC service account:
    ```
    vault  write -namespace=<VAULT_NAMESPACE> auth/<AUTH_PATH>/role/redis-enterprise-rec-<K8S_NAMESPACE> \
           bound_service_account_names=<REC_NAME>  \
           bound_service_account_namespaces=<K8S_NAMESPACE> \
           policies=redisenterprise-<K8S_NAMESPACE>

    ```
4. Apply the Redis Enterprise Cluster yaml. Example (make sure the clusterCredentialSecretName is consistent with Hashicorp Vault configuration above):
    ```
    apiVersion: app.redislabs.com/v1
    kind: RedisEnterpriseCluster
    metadata:
      name: rec
    spec:
      # Add fields here
      nodes: 3
      clusterCredentialSecretName: rec 
      clusterCredentialSecretType: vault
      clusterCredentialSecretRole: redis-enterprise-rec-<K8S_NAMESPACE>
      vaultCASecret: vault-ca-cert
      podAnnotations:
          vault.hashicorp.com/auth-path: auth/<AUTH_PATH>
    ```
   > Note -  the "clusterCredentialSecretName" field as used to query the secret from Hashicorp Vault. See section below for explanation about secret name field values.
### Deploy REDB admission controller (for OLM this is not needed)
It is not recommended to use the admission bundle here if you want to avoid creation of K8s secrets.
Instead, do a step by step installation.   
1. Create the Kubernetes Validating Webhook (for OLM this is not needed)
    **NOTE**: One must replace REPLACE_WITH_NAMESPACE in the following command with the namespace the REC was installed into.

    ```shell script
    # save cert
    CERT=`cat  output.json | jq -r ".cert"`
    sed 's/NAMESPACE_OF_SERVICE_ACCOUNT/REPLACE_WITH_NAMESPACE/g' ../admission/webhook.yaml | kubectl create -f -
    
    # create patch file
    cat > modified-webhook.yaml <<EOF
    webhooks:
    - name: redb.admission.redislabs
      clientConfig:
        caBundle: $CERT
      admissionReviewVersions: ["v1beta1"]
    EOF
    # patch webhook with caBundle
    kubectl patch ValidatingWebhookConfiguration redb-admission --patch "$(cat modified-webhook.yaml)"
    ```
   > Note - use the output.json that was created in the steps above
2. Make sure admission works, see [here](../admission/README.md#verifying-installation) for steps description

<a name="deployment_redb"></a>
### Creating an REDB
An REDB has several secrets associate with it:
1. The password for the REDB
2. [Replica Source](../redis_enterprise_database_api.md#replicasource) (optional)
3. [Backup Credentials](../redis_enterprise_database_api.md#backupspec) (optional)
4. [Client Auth](../redis_enterprise_database_api.md#redisenterprisedatabasespec) (optional)
 
Steps to create an REDB:
1. Create a password in Vault in this path (change according to the specific configuration, see above) `redisenterprise-<K8S_NAMESPACE>/redb-<REDB_NAME>`: <br>
   e.g. ```vault kv put secret/redisenterprise-<K8S_NAMESPACE>/redb-mydb password=somepassword```
2. Create the REDB custom resource.  
   Follow the step 6 [here](../README.md). 
   The REC spec indicted you are running with Vault and no further configuration is required. 
3. The other REDB secrets (2 to 4) should be created in this path `redisenterprise-<K8S_NAMESPACE>/`. The secrets should comply with the 
   REDB [secrets schema](https://github.com/RedisLabs/redis-enterprise-operator/blob/master/deploy/redis_enterprise_database_api.md).
> Note - when using the Redis Enterprise Vault plugin it recommended to set defaultUser: false and associate users through ACL bindings to the REDB
