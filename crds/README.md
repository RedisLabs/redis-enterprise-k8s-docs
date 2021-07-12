## CRD's Schema<br/>


Purpose:
The schema is meant to ease the use of CRDs by restricting the fields to defined types and providing relevant description.


### Work Flow - How add a new field:
* Not all steps are always required

#### 1. Update Tags:
In the files 
+ `pkg/apis/app/v1alpha1/redisenterprisedatabase_types.go`<br/>
+ `pkg/apis/app/v1alpha1/redisenterprisecluster_types.go`<br/>
add tags on top of variables to mark allowed types (Enum)<br/>
(see: https://book.kubebuilder.io/reference/markers/crd-validation.html).<br/>
They will be used by the operator sdk when creating the scheme.<br/>
**Default values** do not appear in the schema since the operator has its own default mechanism.


#### 2 .Create the schema:
1) Install operator-sdk version 0.17.2.<br/> 
See: https://sdk.operatorframework.io/docs/installation/install-operator-sdk/#install-from-github-release
2) Run `operator-sdk generate crds`

#### 3. Update the schema:
- Edit the current schema in all of the relevant CRD yamls with the new section that was generated<br/>
- Note that fields which are k8s objects might be very long - e.g. `SideContainersSpec`
in this case -<br/>it appears in the schema but with no description in the fields since it extends the schema and is not unique for Redis Enterprise. 

