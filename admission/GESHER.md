# Admission Conrol with Gesher Installation for Redis Enterprise Operator

## Gesher Background

Gesher is an operator that enables Kubernetes administrator to delegate the ability to setup webhook validating admisison controllers to users for running within their own namespace.

Gesher is configured by two custom resources.
 
1) A cluster-scoped **NamespacedValidatingType** that defines what Kubernetes resources and operations Gesher is allowed to Proxy
2) A namespace-scoped **NamespacedValidatingRule** that is a namespaced equivalent to Kubernetes **ValidatingWebhookConfiguration** but only effects resources within its same namespace.

### Choosing Traditional Cluster or Gesher's Delegated installation methods.

Redis Labs provides two methods for integrating admission control into one's system, what we refer to as *cluster* and *delegated* configurations.

*Cluster* configuration integrates admission via the standard Kubernetes **ValidatingWebhookConfiguration** resource.  This is a cluster-scoped kubernetes resource that can only be configured by a cluster administrator.

*Delegated* configuration integrates admission via the open source [Gesher admission proxy operator](https://github.com/redislabs/gesher).  Gesher enables an administrator to setup an operator that delegates the ability to setup admission control on namespaced objects to users with the appropriate RBAC permissions within the same namespace as the object.  Instead of requiring a cluster-scoped resource that can impact all resources on a machine, Gesher's namespaced-scoped custom resources only impact resources within the same namespace.  This avoids the needs for administrator intervention for every namespaced operator that will be deployed.  

We recommend using *Cluster* configuration when the cluster administrator is the one installing and managing the operator, as well as in clusters where one only expects a single operator to be used.  

*Delegated* configuration is meant for cases where the cluster administrator expects multiple namespaced operators to be used without their direct knowledge or intervention.

If the cluster administrator involvement will always be required, using Gesher just adds complexity without any significant gain.     

## Installing Gesher

## Gesher Bundle Installation

Install the Gesher bundle into its own namespace:

This must be done by the Kubernetes cluster administrator.

**NOTE**: One must replace REPLACE_WITH_GESHER_NAMESPACE in the following command with the proper namespace
**NOTE**: If one is using openshift, one should replace `gesher.bundle.yaml` with `gesher.openshift.bundle.yaml` 

```shell script
sed 's/NAMESPACE_OF_SERVICE_ACCOUNT/REPLACE_WITH_GESHER_NAMESPACE/g' gesher.bundle.yaml | kubectl create -f -
```

This will deploy the admission proxy, and via an included **NamespacedValidatingType** custom resource, allow forwarding of REDB admission requests.  However, until a **NamespacedValidatingRule** is installed into a namespace, admission is not setup.

## Individual Yaml Installation

1. Create, and switch to, a dedicated namespace for the Gesher Admission proxy

    If installing using Cluster Admission Controller method, skip this, and other steps related to Gesher, to step 11.

    ```shell script
    kubectl create namespace gesher
    kubectl config set-context --current --namespace=gesher
    ```

2. ServiceAccount for the Gesher Admission proxy to run as

    ```shell script
    kubectl apply -f gesher/service_account.yaml
    ```

3. namespaced Role that allows the Gesher Admission proxy to function as an operator in its namespace.

    ```shell script
    kubectl apply -f gesher/role.yaml
    ```

4. Cluster Role that allows controlling the Kubernetes cluster's Admission webhook configuration, and the CRDs of the Gesher operator

    ```shell script
    kubectl apply -f gesher/cluster_role.yaml
    ```

5. Binding namespaced Role, and the Cluster Role to the service account of the Gesher Admission proxy

    NOTE: One must replace REPLACE_WITH_NAMESPACE in the following command with the namespace Gesher is being installed to, from above.

    ```shell script
    kubectl apply -f gesher/role_binding.yaml
    kubectl apply -f gesher/cluster_role_binding.yaml
    ```

6. Kubernetes Service that is used to access the Gesher Admission Control HTTP proxy

    ```shell script
    kubectl apply -f gesher/service.yaml
    ```

8. Deployment for the Gesher operator

**Note:** if one is using openshift, one should replace `operator.yaml` with `operator.openshift.yaml`

    ```shell script
    kubectl apply -f gesher/operator.yaml
    ```

9. NamespacedValidatingType and NamespacedValidatingRule CRDs

    **NamespacedValidatingTypes** and **NamespacedValidatingRules** are Custom Resource Definition that allow creating resources of the corresponding type.

    **NamespacedValidatingTypes** resources allow the Kubernetes cluster administrator to specify which resources _can_ be proxied by the Gesher Admission Controller proxy. Having a resource of this type is required - but not sufficient - to forward Admission requests to a namespaced Admission Controller.
    A resource of this type will be created in the next step, to allow Admission Control of Redis Enterprise Database resources.

    **NamespacedValidatingRules** functions as the 'implementation' to **NamespacedValidatingTypes** 'interface'. A resource of this type represents a namespaced Admission Controller, and will usually be created in the same namespace as the Admission Controller, and possibly, the operator for the CRDs being admission controlled.
    A resource of this type, that will register the Admission Controller for Redis Enterprise Database resources, will be created in the last step.

    ```shell script
    kubectl apply -f gesher/crds/app.redislabs.com_namespacedvalidatingtype_crd.yaml
    kubectl apply -f gesher/crds/app.redislabs.com_namespacedvalidatingrule_crd.yaml
    ```

10. **NamespacedValidatingType** Custom Resource

    This is the Custom resource, mentioned in the previous step, that allows forwarding of Admission Control requests for Redis Enterprise Database resources.

    ```shell script
    kubectl apply -f gesher/type.yaml
    ```
    
## Verifying Gesher installation

One can verify that gesher is running correctly by verifying that the **ValidatingWebhookConfiguration** it creates to point at itself has been created and has the appropriate data corresponding to the **NamespacedValidatingType** that was loaded

```shell script
$ kubectl get ValidatingWebhookConfiguration
NAME                   CREATED AT
proxy.webhook.gesher   2020-10-05T16:18:21Z
```

and

```shell script
$ kubectl get -o yaml ValidatingWebhookConfiguration proxy.webhook.gesher
apiVersion: admissionregistration.k8s.io/v1beta1
kind: ValidatingWebhookConfiguration
metadata:
  name: proxy.webhook.gesher
  <snipped>
webhooks:
- admissionReviewVersions:
  - v1beta1
  clientConfig:
    caBundle: <snipped>
    service:
      name: gesher
      namespace: automation-1
      path: /proxy
      port: 443
  failurePolicy: Fail
  matchPolicy: Exact
  name: proxy.webhook.gesher
  namespaceSelector: {}
  objectSelector: {}
  rules:
  - apiGroups:
    - app.redislabs.com
    apiVersions:
    - v1alpha1
    operations:
    - '*'
    resources:
    - redisenterprisedatabases
    scope: Namespaced
  sideEffects: Unknown
  timeoutSeconds: 30
```

## Installing Admission Controller

Installing the admission controller with gesher is similiar to the traditional installation.  It is a 2 step process

1. Installing the admission controller via a single bundle or individual yaml files
2. Hooking up the admission webhook via gesher

## Admission Control via Bundle Installation

1. Install the Admission Controller via a bundle into the same namespace the REC was installed into.

```shell script
kubectl create -f admission.bundle.yaml
```

## Individual Yaml Installation

1. namespaced Role that allows creation and reading of Secrets

    ```shell script
    kubectl apply -f role.yaml
    ```

2. ServiceAccount for admission controller to run as

    ```shell script
    kubectl apply -f service_account.yaml
    ```

3. Binding namespaced Role to the service account

    ```shell script
    kubectl apply -f role_binding.yaml
    ```

4. Kubernetes Service that is used to access the Admission Control HTTP Server

    ```shell script
    kubectl apply -f service.yaml
    ```

5. TLS Key generator + Admission Controller HTTP Server

    ```shell script
    kubectl apply -f deployment.yaml
    ```
   
## Hooking up the Admission controller with Gesher

**NOTE**: This only has to be done the first time setting up the admission controller, it can be skipped on update

1. Wait for the secret to be created

    ```shell script
    kubectl get secret admission-tls
    NAME            TYPE     DATA   AGE
    admission-tls   Opaque   2      2m43s
    ```

2. Enable the gesher rule using the generated certificate

      ```shell script
      # save cert
      CERT=`kubectl get secret admission-tls -o jsonpath='{.data.cert}'`
      sed -e "s#CERTIFICATE_PLACEHOLDER#${CERT}#g" gesher/rule.yaml | kubectl create -f -
      ```
 
## Verifying Installation

In order to verify that the all the components of the Admission Controller are installed correctly, we will try to apply an invalid resource that should force the admission controller to reject it.  If it applies succesfully, it means the admission controller has not been hooked up correctly.

```shell script
$ kubectl apply -f - << EOF
apiVersion: app.redislabs.com/v1alpha1
kind: RedisEnterpriseDatabase
metadata:
  name: test-database-custom-resource
EOF
```

This must fail with an error output by the admission webhook redb.admisison.redislabs that is being denied because it can't get the login credentials for the Redis Enterprise Cluster as none were specified.

```shell script
Error from server: error when creating "STDIN": admission webhook "proxy.webhook.gesher" denied the request: proxied webhook webhook denied the request: failed get RedisEnterpriseCluster client: custom resource (RedisEnterpriseCluster) not found: resource name may not be empty
```