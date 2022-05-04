# Deploying Redis on Flash on K8s using Redis Enterprise operator

## General information about Redis on Flash
If you are interested to learn more about Redis on Flash you may read the following docs:
* [Redis on Flash official documentation](https://docs.redis.com/latest/rs/concepts/memory-performance/redis-flash/)
* [Redis on Flash technology overview](https://redis.com/redis-enterprise/technology/redis-on-flash/)

## Prerequisites
To create RoF (Redis on Flash) databases using the
Redis Enterprise operator, the following prerequisites must be met:
* A K8s cluster with worker nodes that have locally attached NVMe SSDs. Deploying RoF
  on K8s cluster with network attached SSDs is unsupported.
  Refer to the official documentation for your platform for help
  with setting up worker nodes with locally attached NVMe SSDs.
* The locally attached NVMe SSDs must be formatted and mounted on the worker machines
  that will run the Redis Enterprise pods. Make sure that on every worker node, the locally attached
  SSD is mouted at the same path. This is critical for the next steps.
* The locally attached NVMe SSDs must be provisioned as persistent volumes, and assigned
  a unique storage class name.
* RoF is currently in preview. For this feature to take effect, 
  set a boolean environment variable with the name \"ENABLE_ALPHA_FEATURES\" to True. 
  This variable can be set via the redis-enterprise-operator pod spec, 
  or through the operator-environment-config Config Map.

### Formatting and mounting locally attached SSDs
Some cloud providers will automatically format and mount locally attached SSDs for you.
Others may leave this task to the user. It is up to the user to
ensure that locally attached SSDs are mounted. Otherwise, they can't be used by the
operator as flash storage.
There are several ways to mount the locally attached SSDs if your cloud provider doesn't do it automatically.
One way to mount local SSDs is by running a privileged pod on all worker nodes, having the root of
the host file system mounted at a special location (like `/host`) in one of its containers.
That container (that could be an init container), should run a couple of commands that will
format and mount the locally attached SSDs on the worker node. See the example in the next
section for more details.

### Provisioning locally attached SSDs as persistent volumes
In order for the operator to be able to take advantage of the locally attached SSDs,
they must be provisioned as local persistent volumes and assigned a unique storage class name.
One way to provision locally attached SSDs is by using the [local volume static provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/README.md).
The provisioner deploys a daemon set along with additional API objects that will aid with
the task of provisioning locally attached SSDs.
Here is an example of a daemon set with additional explanations:
```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: openshift-aws-provisioner
  namespace: default
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: provisioner
      app.kubernetes.io/instance: openshift-aws
  template:
    metadata:
      labels:
        app.kubernetes.io/name: provisioner
        app.kubernetes.io/instance: openshift-aws
    spec:
      serviceAccountName: local-ssd-provisioner
      nodeSelector:
        kubernetes.io/os: linux
        node.kubernetes.io/instance-type: i3.2xlarge
      initContainers:
        - name: nvme-mount-init-container
          image: registry.access.redhat.com/ubi8/ubi
          securityContext:
            privileged: true
          volumeMounts:
          - mountPath: /host
            name: host-slash
            mountPropagation: Bidirectional
          command: ["/bin/bash", "-c", "--"]
          args: ["chroot /host /bin/sh -c \"mkfs -t xfs /dev/nvme0n1 && mkdir -p /mnt/disks/ssd0 && mount /dev/nvme0n1 /mnt/disks/ssd0; echo SUCCESS!\""]
      containers:
        - name: provisioner
          image: k8s.gcr.io/sig-storage/local-volume-provisioner:v2.4.0
          securityContext:
            privileged: true
          env:
          - name: MY_NODE_NAME
            valueFrom:
              fieldRef:
                fieldPath: spec.nodeName
          - name: MY_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: JOB_CONTAINER_IMAGE
            value: k8s.gcr.io/sig-storage/local-volume-provisioner:v2.4.0
          ports:
          - name: metrics
            containerPort: 8080
          volumeMounts:
            - name: provisioner-config
              mountPath: /etc/provisioner/config
              readOnly: true
            - name: provisioner-dev
              mountPath: /dev
            - name: nvme-ssd
              mountPath: /mnt/disks
              mountPropagation: HostToContainer
      volumes:
        - name: provisioner-config
          configMap:
            name: openshift-aws-provisioner-config
        - name: provisioner-dev
          hostPath:
            path: /dev
        - name: nvme-ssd
          hostPath:
            path: /mnt/disks
        - name: host-slash
          hostPath:
            path: /
            type: ''
```
> Note: this is just an example of a static provisioner `DaemonSet` that we used for our testing/development purposes.
  You may need a different configuration, depending on k8s platform you are running on.
Some key points:
* Notice `host-slash` volume of type hostPath. It is mounted in the `nvme-mount-init-container`
  with bidirectional mount propagation. In general, `hostPath` volumes are considered unsafe.
  In case you are willing to avoid using `hostPath` volumes you will need a different way of provisioning
  local persistent volumes.
* The `nvme-mount-init-container` init container formats the locally attached SSD (`mkfs` command),
  and mounts it at `/mnt/disks/ssd0` (`mount` command). Those commands are executed after we
  change the root to `/host` which is the mount path of the root of the host machine file system.
  This is what ensures that the locally attached SSD is mounted in the file system of the host machine.

The local volume static provisioner also creates a storage class object. The name of the storage class is
an arbitrary string that could be chosen when the YAML files are [generated from a helm template](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner/blob/master/helm/README.md). This storage class name is used when a redis enterprise cluster with RoF support is created. Here is an example of such
storage class:
```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nvme-ssd
  labels:
    helm.sh/chart: provisioner-2.6.0-alpha.0
    app.kubernetes.io/name: provisioner
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/instance: openshift-aws
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

## Deploying Redis on Flash Databases on Kubernetes using Redis Enterprise operator

If all the above requirements are met, you can deploy a RoF database with the two steps below: 
using the operator:
* [Create a Redis Enterprise Cluster with RoF support.](#create-a-redis-enterprise-cluster-with-rof-support)
* [Create a Redis Enterprise Database using flash storage.](#create-a-redis-enterprise-database-using-flash-storage)

See explanation below for details.

### Create a Redis Enterprise Cluster with RoF support
To deploy a Redis Enterprise cluster using locally attached SSDs, set the following attributes in the `spec` section of the Redis Enterprise cluster custom resource:
locally attached SSDs (assuming the prerequisites above are met), several attributes
of the Redis Enterprise Cluster custom resource spec must be set:
* The desired flash storage driver. Currently the only supported value is `rocksdb`.
* The storage class name identifying the locally attached SSDs. This is the name of the storage class
  that was created by the local volume static provisioner.
* The minimal required flash disk size.

Here is an example of a Redis Enterprise Cluster custom resource providing those attributes:
```
apiVersion: app.redislabs.com/v1
kind: RedisEnterpriseCluster
metadata:
  name: "rec"
spec:
  # Add fields here
  nodes: 3
  redisOnFlashSpec:
    enabled: true
    flashStorageEngine: rocksdb
    storageClassName: local-scsi
    flashDiskSize: 100G
```
> Note that the `enabled` field must be set to true.

### Create a Redis Enterprise Database using flash storage
Unless specified otherwise, any new database will use RAM only.
In order to create a database taking advantage of locally attached SSDs,
you must set `isRof` to be `true`, and the size of the RAM portion must be set as well.
For example:
```
apiVersion: app.redislabs.com/v1alpha1
kind: RedisEnterpriseDatabase
metadata:
  name: rof-redb
spec:
  redisEnterpriseCluster:
    name: rec
  isRof: true
  memorySize: 2GB
  rofRamSize: 0.5GB
```
> Note that both `memorySize` and `rofRamSize` are specified. In case `isRof` is `true`, memorySize
refers to the combined memory size (RAM + Flash), while `rofRamSize` specifies the RAM capacity of the database.
Remember that `rofRamSize` must be at least 10% of combined (RAM + Flash) memory capacity.

