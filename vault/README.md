# Integrating the Redis Enterprise Operator with Hashicorp Vault
## Overview
Hashicorp Vault can be used to store secrets as an alternative to K8s secrets. Hashicorp Vault can be configured as the source of secrets used by the Redis Enterprise K8s operator. For now, the following items are supported:
* Redis Enterprise Cluster Credentials
* REDB admission TLS cert
* REDB secrets:
    * Replica of
    * Backup credentials
    * TLS keys
    * default user secret

This document explains how to use Hashicorp Vault as a source for secrets.
> Note: when using Openshift it might be recommended to use oc instead of kubectl 
## Prerequisites
* Deploy a Hashicorp Vault instance and make sure there is network access to it from the Kubernetes cluster. The solution has been tested with Hashicorp Vault v1.6.2. The Hashicorp Vault instance must be using TLS.
* Configure the Hashicorp Vault Kubernetes authentication for the Kubernetes cluster the operator is being deployed. Refer to the Hashicorp Vault documentation for details.
* Deploy the Hashicorp Vault agent sidecar controller on the Kubernetes cluster (https://learn.hashicorp.com/tutorials/vault/kubernetes-sidecar)
* Note that Hashicorp offers a Vault Enterprise product. The Vault Enterprise product supports namespaces. Those namespaces should not be confused with Kubernetes namespaces. This document assumes that the Hashicorp Vault instance used is the Enterprise product and a Vault namespace is used. The namespace is referred to as the <VAULT_NAMESPACE> below.
* Redis Enterprise will use a kv-v2 secret engine. Make sure it is available on the Hashicorp Vault instance (or create one if needed) and take note of the path it is mounted on, since it will be used later.

## Deployment
### General considerations
Hashicorp Vault and the Redis Enterprise Operator can be deployed in multiple scenarios that might affect the details of the process below. The document assumes the following:
* Hashicorp Vault enterprise is used, and Vault namespaces are used. If that is not the case, it is recommended to remove the namespace parameters, environment variables and annotations from the relevant directions.
* Multiple Redis Enterprise Clusters are configured within the same K8s cluster, configured to authenticate to Hashicorp Vault.
* To ensure privacy and avoid duplication, the K8S_NAMESPACE is appended to multiple names of Hashicorp Vault configurations. That might need to be further adjusted in cases multiple K8s clusters are used with the same K8s namespaces.
### Deploying the operator
1. Deploy the operator by applying the Redis Labs Kubernetes Operator Bundle as explained [here](../README.md) - steps 1,2 (steps 1-4 on OpenShift). Once operator is running, proceed to the steps below. Avoid creating the Redis Enterprise Cluster custom resource.
2. Configure a Hashicorp Vault policy. The policy will be used to grant the operator access to the secrets.
   
    Run the following command within the Hashicorp Vault interface (use kubectl exec when Vault is deployed on Kubernetes, replace <K8S_NAMESPACE> with the namespace where the operator is deployed into):
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
3. Create a role to bind the Redis Enterprise operator service account to the policy configured in the previous step:
    ```
    vault  write -namespace=<VAULT_NAMESPACE> auth/<AUTH_PATH>/role/redis-enterprise-operator-<K8S_NAMESPACE> \
            bound_service_account_names="redis-enterprise-operator"  \
            bound_service_account_namespaces=<K8S_NAMESPACE> \
            policies=redisenterprise-<K8S_NAMESPACE>
    ```
   > Note - replace AUTH_PATH with the path kubernetes auth is enabled in Hashicorp Vault. The default is "kubernetes"
4. Create a K8s secret containing the Certificate Authority Certificate (CACert) used to create the Hashicorp Vault instance server certificate. Name the secret vault-ca-cert. Save the ca cert to a file before running the following command:
```
kubectl create secret generic vault-ca-cert \
        --namespace <K8S_NAMESPACE> \
        --from-file=vault.ca=<vault instance server CA certificate path>
```
5. Modify the operator deployment to enable Hashicorp Vault agent sidecar container:
    * Determine the Hashicorp Vault server Fully Qualified Domain Name (FQDN). If the Vault server is running with k8s, it would typically be <YOUR_VAULT_SERVICE_NAME>.<YOUR_VAULT_SERVICE_NAMESPACE>):
    * The path the kv-2 secret engine being used is enabled on should be set as the value of the "VAULT_SECRET_ROOT" environment variable. 
    * The value of the VAULT_SECRET_PREFIX should be unique to the Redis Enterprise Cluster. Here we use "redisenterprise-<K8s_NAMESPACE>". This value has to be consistent with Hashicorp Vault roles and policies.
    * The value of the VAULT_SERVER_FQDN environment variable should be set with the Fully Qualified Domain Name of the Hashicorp Vault server.
    * Save the following content to a file called operator-deployment-patch.yaml, replacing values as needed:
```
spec:
 template:
   metadata:
     annotations:
       vault.hashicorp.com/agent-init-first: "true"
       vault.hashicorp.com/agent-inject: "true"
       vault.hashicorp.com/agent-inject-token: "true"
       vault.hashicorp.com/ca-cert: "/vault/tls/vault.ca"
       vault.hashicorp.com/tls-secret: "vault-ca-cert"
       vault.hashicorp.com/role: "redis-enterprise-operator"
       vault.hashicorp.com/namespace: <VAULT_NAMESPACE>
   spec:
     volumes:
     - name: vault-ca-cert
       secret:
         defaultMode: 420
         secretName: vault-ca-cert
     containers:
     - name: redis-enterprise-operator
       env:
       - name: VAULT_SERVER_FQDN
         value: <Your FQDN>
       - name: VAULT_SERVICE_PORT_HTTPS
         value: "8200"
       - name: VAULT_SECRET_ROOT
         value: "secret"
       - name: VAULT_SECRET_PREFIX
         value: "redisenterprise-<K8S_NAMESPACE>"
       - name: VAULT_NAMESPACE
         value: <VAULT_NAMESPACE>
       volumeMounts:
       - mountPath: /vault/tls
         name: vault-ca-cert
         readOnly: true
   ```
   > Note - the server certificate of the Hashicorp Vault instance must be signed by the Certificate Authority used within the secret. 
   >  
   * Run the following command to update the operator deployment:
   ```
    kubectl patch deployment redis-enterprise-operator -n <operator namespace> --patch "$(cat operator-deployment-patch.yaml)"
   ```
   > Note - the change configures the sidecar injector to inject a token into the operator pod and configures the TLS settings required for secure communication with the Hashicorp Vault instance.  
5. Verify that the sidecar container was created within the operator deployment. The operator pod should have 2 containers running.
### Creating the REC
1. Choose a random password. Unlike the default deployment, the operator is not creating a default password for the Redis Enterprise Cluster credentials and those need to be chosen. It is recommended to use a tool to generate a random password at least 8 characters long.
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
      clusterCredentialSecretRole: redis-enterprise-rec-<K8S_NAMESPACE
      vaultCASecret: vault-ca-cert
      podAnnotations:
          vault.hashicorp.com/namespace: <VAULT_NAMESPACE>
          vault.hashicorp.com/auth-path: auth/<AUTH_PATH>
         
    ```
   > Note -  the "clusterCredentialSecretName" field as used to query the secret from Hashicorp Vault. See section below for explanation about secret name field values.
### Deploy REDB admission controller
It is not recommended to use the admission bundle here if you want to avoid creation of K8s secrets.
Instead, do a step by step installation.
1. Deploy the service - apply the following [yaml](../admission/service.yaml)
2. Generate a json file with key/cert pair to be used by admission:
    ```
    kubectl exec -it $(kubectl get pod -l name=redis-enterprise-operator -o jsonpath='{.items[0].metadata.name}') -- /usr/local/bin/generate-tls -infer > output.json
    ```
3. Apply the secret to vault - execute the following within the Hashicorp Vault CLI interface (you will need to copy the file from the previous step):
    ```
    vault kv put secret/redisenterprise/admission-tls @output.json
    ```
4. Apply the admission deployment [yaml](../admission/deployment.yaml) 
5. Modify the admission deployment to enable Hashicorp Vault agent sidecar container:
   * Save the following content to a file called admission-deployment-patch.yaml (set values as needed):
        ```
        spec:
          template:
            metadata:
              annotations:
                vault.hashicorp.com/agent-init-first: "true"
                vault.hashicorp.com/agent-inject: "true"
                vault.hashicorp.com/agent-inject-token: "true"
                vault.hashicorp.com/ca-cert: "/vault/tls/vault.ca"
                vault.hashicorp.com/tls-secret: "vault-ca-cert"
                vault.hashicorp.com/role: "redis-enterprise-operator"
                vault.hashicorp.com/namespace: <VAULT_NAMESPACE>
            spec:
              serviceAccountName: redis-enterprise-operator
              volumes:
              - name: vault-ca-cert
                secret:
                  defaultMode: 420
                  secretName: vault-ca-cert
              containers:
              - name: admin
                env:
                - name: VAULT_SERVER_FQDN
                  value: <Your FQDN>
                - name: VAULT_SERVICE_PORT_HTTPS
                  value: "8200"
                - name: CREDENTIAL_TYPE
                  value: "vault"
                - name: VAULT_SECRET_ROOT
                  value: "secret"
                - name: VAULT_SECRET_PREFIX
                  value: "redisenterprise-<K8S_NAMESPACE>"
                - name: VAULT_NAMESPACE
                  value: <VAULT_NAMESPACE>
                volumeMounts:
                - mountPath: /vault/tls
                  name: vault-ca-cert
                  readOnly: true
        ```
   * Patch the deployment
        ```
            kubectl patch deployment admission-deploy -n <operator namespace> --patch "$(cat admission-deployment-patch.yaml)"
        ```
6. Create the Kubernetes Validating Webhook
    **NOTE**: One must replace REPLACE_WITH_NAMESPACE in the following command with the namespace the REC was installed into.

    ```shell script
    # save cert
    CERT=`cat  output.json | jq -r ".cert"`
    sed 's/NAMESPACE_OF_SERVICE_ACCOUNT/REPLACE_WITH_NAMESPACE/g' ../admission/webhook.yaml | kubectl create -f -
    
    # create patch file
    cat > modified-webhook.yaml <<EOF
    webhooks:
    - admissionReviewVersions:
      clientConfig:
        caBundle: $CERT
      name: redb.admission.redislabs
      admissionReviewVersions: ["v1beta1"]
    EOF
    # patch webhook with caBundle
    kubectl patch ValidatingWebhookConfiguration redb-admission --patch "$(cat modified-webhook.yaml)"
    ```
7. Make sure admission works, see [here](../admission/README.md#verifying-installation) for steps description

### Creating REDB
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
> Note - when using the Redis Enterprise Vault plugin it it recommended to set defaultUser: false and associate users through ACL bindings to the REDB


