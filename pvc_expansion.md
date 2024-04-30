# PVCs Expansion

Persistent Volume Claims are used for Redis Enterprise Cluster persistence.  
The PVCs are created by the operator and are used by the REC pods.  
The PVCs are created with a specific size and can be resized if the underlying storage class supports it.

## How to expand REC PVCs?

Some important points before using this new feature:
1. **Pay attention! the process involves deletion and recreation of the statefulset.**
2. Do Not change any other filed, related to the statefulset, in the spec while the resizing is still in progress.
3. To be able to expand a PVC - the storage class must support it (the underlying volume driver must support resize).
4. Set the `allowVolumeExpansion` field to true in the StorageClass object(s).
5. Currently, we only support PVC that supports online expansion.
6. Shrink (reduce the size) of the PVCs is not allowed.
7. Backup your databases before the change.

- In order to expand the PVCs that are used by the REC for persistent please follow the steps:
  - To use this feature enable the persistent resize flag under the REC spec:  
    - Set a boolean "enablePersistentVolumeResize" to True.
    - Set the value of the `volumeSize` under the `persistentSpec` to the requested size.
      ```bash
        spec:
          persistentSpec:
            enabled: true
            storageClassName: ""
            volumeSize: <NEW_SIZE>
            enablePersistentVolumeResize: true
      ```
      - Once you apply the change, the PVCs will be resized and once all the PVCs are resized - the statefulset will be deleted and recreated.  
      You can see the status of the process in the REC status:
      The status of the Persistent Volume Claims that are used for Redis Enterprise Cluster persistence.  The status will correspond
      to the status of one or more of the PVCs (failed/resizing if one of
      them is in resize or failed to resize)  
      In the middle of the process the status will be:
          ```bash
        status:
        ......
            persistenceStatus:
            status: Resizing
            succeeded: 2/3
        ```  
        In the end of the process, you will see the new size and the status will be 'Provisioned':
        ```bash
        status:
        ......
            persistenceStatus:
            status: Provisioned
            succeeded: 3/3
        ```

 - In addition, if any error occur during the process - you can watch the events and logs in the operator or the PVCs/StorageClasses logs to detect the issue.
 - For additional help, refer to the official Kubernetes documentation on [expanding-persistent-volumes-claims](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#expanding-persistent-volumes-claims),[recovering-from-failure-when-expanding-volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#recovering-from-failure-when-expanding-volumes) (**It is a manual process described on K8s documentation, and the results are on your responsibility**) 


