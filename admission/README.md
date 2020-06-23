## REDB Admission Controller Setup

In order to enable the REDB admission controller one has to deploy multiple Kubernetes resource.

One can either install them via the provided yaml bundle, or individually.

##### Bundle Installation

1. one installs them via a bundle after editing it to use the correct namespace.

**NOTE**: One must replace REPLACE_WITH_NAMESPACE in the following command with the proper namespace

```shell script
sed 's/NAMESPACE_OF_SERVICE_ACCOUNT/REPLACE_WITH_NAMESPACE/g' admission.bundle.yaml | kubectl create -f -
```

If this is the first time one is deploying the admission controller, one has to approve the CSR and setup the webhook to enable resource validation.  If one has already set these up, and one is just updating the admission controller, one skips steps 2 and 3 as they are already configured correctly   

2. and waits for the CSR to ready and approves it

wait for it to be ready to be approved

```shell script
kubectl get csr admission-tls
```

and approve it once it's pending approval

```shell script
kubectl certificate approve admission-tls
```
or on openshift
```shell script
oc adm certificate approve admission-tls
```

3. and modifies the webhook to use the certificate generated

```shell script
# save cert
CERT=`kubectl get csr admission-tls -o jsonpath='{.status.certificate}'`
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

##### Individual Installation

1. ClusterRole that allows creation and watching of CertificateSigningRequest resources

```shell script
kubectl apply -f cluster_role.yaml
```

2. namespaced Role that allows creation and reading of Secrets

```shell script
kubectl apply -f role.yaml
```

3. ServiceAccount for admission controller to run as

```shell script
kubectl apply -f service_account.yaml
```

4. Binding ClusterRole and namespaced Role to the service account

**NOTE**: one must change the namespace for the ClusterRoleBinding to the namespace you are loading these resources into 

```shell script
sed 's/NAMESPACE_OF_SERVICE_ACCOUNT/REPLACE_WITH_NAMESPACE/g' cluster_role_binding.yaml | kubectl apply -f -
kubectl apply -f role_binding.yaml
```

5. Kubernetes Service that is used to access the Admission Control HTTP Server

```shell script
kubectl apply -f service.yaml
```

6. TLS Key generator and Signing Requester + Admission Controller HTTP Server

```shell script
kubectl apply -f deployment.yaml
```

**Note**: Same as above with the bundle installation, the first time deploying the admission controller, one has to approve the CertificateSigningRequest and deploy the admisison webhook resource.

1. approve CSR

```shell script
kubectl certificate approve admission-tls
```
or on openshift

```shell script
oc adm certificate approve admission-tls
```

2. and modifies the webhook to use the certificate generated

```shell script
# replace REPLACE_WITH_NAMESPACE with the correct namespace
sed 's/NAMESPACE_OF_SERVICE_ACCOUNT/REPLACE_WITH_NAMESPACE/g' webhook.yaml | kubectl apply -f -

# save cert
CERT=`kubectl get csr admission-tls -o jsonpath='{.status.certificate}'`

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

##### Verifying Installation

In order to verify that the all the components of the webhook are installed correctly, we will try to apply an invalid resource that should force the admission controller to reject it.  If it applies succesfully, it means the admission controller has not been hooked up correctly.

```shell script
$ kubectl apply -f - << EOF
apiVersion: app.redislabs.com/v1alpha1
kind: RedisEnterpriseDatabase
metadata:
  name: test-database-custom-resource
EOF
```

This must fail with an error output by the admissio nwebhook redb.admisison.redislabs that is being denied becuase it can't get the login crendentials for the Redis Enterprise Cluster as none was specified.

```shell script
Error from server: error when creating "STDIN": admission webhook "redb.admission.redislabs" denied the request: createRECClient: GetLoginInfo: resource name may not be empty
```