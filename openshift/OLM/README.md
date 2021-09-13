# Installing Redis Enterprise Operator on Openshift's OLM
### Overview
One way to install Redis Enterprise Operator is using Openshift's marketplace for operators - OLM.<br>
This document is a step-by-step guide for how to do that.<br>
For users who wish to use Redis Enterprise Operator with Hashicorp Vault this document also contains reference for required steps.

1. [ Installation ](#Installation)
2. [ Deploying Multi-Namespaced REDB ](#multi_ns_redb)
3. [ Troubleshooting ](#Troubleshooting)

### Installation:
<a name="Installation"></a>

1. Create a project for the Redis Enterprise Operator and apply the SCC (Security Context Constraint):<br>
   follow steps [1-3](../../README.md#installation-on-openshift).
2. When running with Vault follow these steps: 
   1. Verify the [prerequisites](../../vault/README.md#prerequisites).
   1. Configure Vault policy for the operator: [step 1-2](../../vault/README.md#deploying-the-operator:).
   2. Configure the operator's configmap: [step 3](../../vault/README.md#deploying-the-operator:).
   3. Create a Vault CA certificate secret: [step 5](../../vault/README.md#deploying-the-operator).
3. Install the Redis Enterprise Operator:<br>
   In your project, under the left menu bar select "Operators" -> "OperatorHub" -> select "Redis Enterprise Operator" and click on "Install Operator":
   
   ![Alt text](images/install_operator.png?raw=true "Title")<br>
   
   Click "Install":<br>
   ![Alt text](images/install_operator2.png?raw=true "Title")<br>
   Next configure the Operator Installation:
   - Channels:
     - For the latest version use "production" Update Channel. When using the production channel, each new operator version will be used for upgrades.
     - When using a version specific channel, if a newer minor version is released for that version, it will be used for upgrades. 
   - "Approval strategy" can be Manual or Automatic as explained here: https://docs.openshift.com/container-platform/4.7/operators/admin/olm-upgrading-operators.html
   - "Installed Namespace" - choose your project name.<br>
   Click "Install" and wait for the Operator to complete installation, this can around 1 minute.
  ![Alt text](images/install_operator3.png?raw=true "Title")
4. Create a Redis Enterprise Cluster (REC) instance:<br>
   1. When Using Vault:<br>
      Follow steps [1-3](../../vault/README.md#creating-the-redis-enterprise-cluster) to configure the REC credentials and policy for the REC service account.
   2. Create an REC.<br>
      - Click "Create instance" under RedisEnterpriseCluster:
      ![Alt text](images/create_rec.png?raw=true "Title")
       You can then configure it using "Form View" or "YAML view".<br>
      - If you do not need special configuration just click "Create" to use the default values<br>
      - Follow the REC status: it should start with *BootstrappingFirstPod* then proceed to *Initializing* and eventually *Running*<br>
        ![Alt text](images/create_rec2.png?raw=true "Title")
      
      The relevant K8S resources would now be created - you can view them from "Resources" or navigate the menu to watch specific resources.

5. Create a Redis Enterprise Database (REDB) instance:<br>
   - Note you must first have an REC in order to create a database
   - Note that an admission controller for REDB objects is automatically deployed when installing the operator
   1. When Running Vault:
      Create a secret for the REDB follow [step 1](../../vault/README.md#creating-an-redb).
   2. Create an REDB instance.  You can then configure it using "Form View" or "YAML view" then click "Create".<br>
      ![Alt text](images/redb.png?raw=true "Title")
      Verify it's status is "Active":<br>
      ![Alt text](images/redb2.png?raw=true "Title")

### Running With Multi-Namespaced REDB
<a name="multi_ns_redb"></a>
The Redis Enterprise Operator provides a method for a single deployed operator/cluster combination to listen for REDB objects in multiple specified individual namespaces.<br>
To support this feature, after installing the REC, follow instructions as detailed [here](../../multi-namespace-redb/README.md#multi-namespaced-redb) starting with step 2.


### Troubleshooting
<a name="Troubleshooting"></a>
1. Operator installation fails.<br>
   In case the reason is not clear you can examine your operator installation by running:<br>
   `kubectl get pod -n openshift-marketplace`<br>
   you should be able to find the relevant pod for Redis Enterprise Operator - you can then run<br>
   `kubectl describe pod <POD NAME> -n openshift-marketplace` or <br>
   `kubectl logs pod <POD NAME> -n openshift-marketplace`<br> to investigate further.
2. The Operator pod is not starting.
   Connect to the Operator pod's containers and view logs.<br>
   One possible reason is Vault was not configured to use the correct service account, In this case the logs should indicate it.
3. After creating an REC the Stateful set does not start.<br>
   It is likely you did not apply the SCC as needed. Repeat step 1 and delete the first STS pod that is trying to start.
   

   
   




