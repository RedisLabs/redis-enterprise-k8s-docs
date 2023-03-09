# Management of the Redis Enterprise Cluster credentials
## Background
When the operator creates a Redis Enterprise Cluster (REC) it generates random credentials that are used by the operator to perform operations on the Redis Enterprise Cluster using the cluster APIs.
The credentials are saved in a K8s secret (or Vault, see [README](vault/README.md)). When a K8s secret is used, the secret name default to the name of the Redis Enterprise Cluster.
## Using the Redis Enterprise Cluster Credentials
The credentials can be used to access the Redis Enterprise Cluster UI or API. Make sure connectivity is configured to the cluster pods using an appropriate service (or by a solution such as kubectl port forwarding). To inspect the random username and password created by the operator, use kubectl:
``` 
$ kubectl get secret rec -o jsonpath='{.data}'
map[password:MVUyTjd1Mm0= username:ZGVtb0ByZWRpc2xhYnMuY29t]
$ echo MVUyTjd1Mm0= | base64 --decode
```
> Note - other utilities to view secrets are available

## Changing the Redis Enterprise Cluster Credentials
### Replacing the password
Please follow the following steps:
1. Take note of the current password, see above
2. Exec into a Redis Enterprise Cluster node pod using the following command:
    ```
    kubectl exec -it <Redis Enterprise Cluster resource name>-0 bash
    ```
3. Within the pod console, run a command to add the new password as supported for the existing user, replace with the existing credentials and the new password:
    ```
    REC_USER="`cat /opt/redislabs/credentials/username`"; REC_PASSWORD="`cat /opt/redislabs/credentials/password`";curl -k --request POST --url https://localhost:9443/v1/users/password -u "$REC_USER:$REC_PASSWORD" --header 'Content-Type: application/json' --data "{\"username\":\"$REC_USER\",\"old_password\":\"$REC_PASSWORD\", \"new_password\":\"<NEW PASSWORD>\"}"
    ```
4. Update the cluster credential secret: using the commands ran outside of the Redis Enterprise Cluster node pod:
    > Note: For Vault users, see the instruction described [below](./cluster_credentials.md#creds_with_vault) and proceed to the next step.

    a. Save the existing username to a text file (replace <current username> with actual).
    ```
    echo -n "<current username>" > username
    ```
    b. Save the new password to a text file (replace <new password> with actual).
    ```
    echo -n "<new password>" > password
    ```
    c. Update the secret:
    ```
    kubectl create secret generic <cluster secret name> --from-file=./username --from-file=./password --dry-run -o yaml | kubectl apply -f -
    ```
5. Wait 5 minutes to make sure all components have read the new password from the updated secret
6. in case this cluster is participating in Active-Active database via REAADB follow the instructions [here](active_active_database_readme.md) under `Update existing participating cluster (RERC) secret`.
7. Exec into a Redis Enterprise Cluster node pod (see above) and run the following command to remove the previous password so only the new one applies. Important: replace OLD PASSWORD with the one being replaced, see step 1 above.
    ```
    REC_USER="`cat /opt/redislabs/credentials/username`"; REC_PASSWORD="`cat /opt/redislabs/credentials/password`";curl -k --request DELETE --url https://localhost:9443/v1/users/password -u "$REC_USER:$REC_PASSWORD" --header 'Content-Type: application/json' --data "{\"username\":\"$REC_USER\",\"old_password\":\"<OLD PASSWORD\"}"
    ```
    > Note: the username to be used with the K8s secret is the email displayed on the Redis Enterprise UI

    > Note: this procedure is only supported for version 6.0.20-5 or above
### Replacing the password and the username
Please follow the following steps:
1. Log into the Redis Enterprise Cluster UI using the credentials as explained above.
2. Add another admin user, choose a password
3. Set the new username with the Redis Enterprise Cluster spec (username field)
4. Update the cluster credential secret:
    > Note: For Vault users, see the instruction described [below](#creds_with_vault) and proceed to the next step.
    
    a. Save the new username to a text file (replace <new username> with actual).
    ```
    echo -n "<new username>" > username
    ```
    b. Save the new password to a text file (replace <new password> with actual).
    ```
    echo -n "<new password>" > password
    ```
    c. Update the secret:
    ```
    kubectl create secret generic <cluster secret name> --from-file=./username --from-file=./password --dry-run -o yaml | kubectl apply -f -
    ```
    > Note: the username to be used with the K8s secret is the email displayed on the Redis Enterprise UI
5. Wait 5 minutes to make sure all components have read the new password from the updated secret
6. in case this cluster is participating in Active-Active database via REAADB follow the instructions [here](active_active_database_readme.md) under `Update existing participating cluster (RERC) secret`.
7. Delete the previous admin user using the Redis Enterprise Cluster UI
   > Note: this procedure is only supported for version 6.0.20-5 or above
   > Note: the operator might log errors in the time period between updating the username in the REC spec and the secret update

<a name="creds_with_vault"></a>
### Updating the credentials secret in Vault
For users who store secrets in Vault, update the Vault secret containing the Redis Enterprise Cluster's credentials with the following key-value pairs: username:<desired_username>, password:<desired_password>.
For more information about Vault integration with the Redis Enterprise Cluster see [README](vault/README.md#deployment_rec).
