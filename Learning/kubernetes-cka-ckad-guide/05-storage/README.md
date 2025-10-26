# Module 05: Storage

## 📚 Table of Contents

- [Overview](#overview)
- [Volumes](#volumes)
  - [Volume Types](#volume-types)
  - [EmptyDir](#emptydir)
  - [HostPath](#hostpath)
  - [ConfigMap and Secret Volumes](#configmap-and-secret-volumes)
- [Persistent Volumes (PV)](#persistent-volumes-pv)
- [Persistent Volume Claims (PVC)](#persistent-volume-claims-pvc)
- [Storage Classes](#storage-classes)
- [Dynamic Provisioning](#dynamic-provisioning)
- [Volume Modes](#volume-modes)
- [Access Modes](#access-modes)
- [Reclaim Policies](#reclaim-policies)
- [Volume Expansion](#volume-expansion)
- [StatefulSets with Storage](#statefulsets-with-storage)
- [Best Practices](#best-practices)
- [Exam Tips](#exam-tips)

---

## Overview

Kubernetes provides several storage abstractions to persist data beyond pod lifecycles.

**Exam Weight**:
- **CKA**: 10% - Storage
- **CKAD**: 10% - Application Deployment (includes storage)

**Key Concepts**:
- **Volumes**: Directory accessible to containers in a pod
- **Persistent Volumes (PV)**: Cluster-level storage resource
- **Persistent Volume Claims (PVC)**: Request for storage by users
- **Storage Classes**: Define different storage types with provisioners

**Storage Hierarchy**:
```
Pod → PVC → PV → Physical Storage
```

---

## Volumes

### What is a Volume?

A Volume is a directory accessible to all containers in a Pod. Unlike container filesystems, volumes persist across container restarts.

### Volume Types

| Type | Description | Use Case | Persistence |
|------|-------------|----------|-------------|
| **emptyDir** | Empty directory created when pod starts | Temporary scratch space | Pod lifetime |
| **hostPath** | Mount from host node filesystem | Testing, node monitoring | Beyond pod |
| **configMap** | Mount ConfigMap as files | Configuration files | N/A |
| **secret** | Mount Secret as files | Sensitive data | N/A |
| **persistentVolumeClaim** | Claim a Persistent Volume | Databases, file storage | Beyond pod |
| **nfs** | NFS network share | Shared storage | Beyond pod |
| **csi** | Container Storage Interface | Cloud storage | Beyond pod |

---

### EmptyDir

Created when a pod is assigned to a node. Deleted when pod is removed.

**Use Cases**:
- Scratch space
- Cache
- Sharing files between containers in same pod

**Example**: Basic emptyDir

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-pod
spec:
  containers:
    - name: writer
      image: busybox
      command: ["/bin/sh", "-c"]
      args:
        - while true; do
            date >> /data/log.txt;
            sleep 5;
          done
      volumeMounts:
        - name: shared-data
          mountPath: /data
    
    - name: reader
      image: busybox
      command: ["/bin/sh", "-c"]
      args:
        - tail -f /data/log.txt
      volumeMounts:
        - name: shared-data
          mountPath: /data
  
  volumes:
    - name: shared-data
      emptyDir: {}
```

**Example**: emptyDir with memory backing

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: memory-backed-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: cache
          mountPath: /cache
  
  volumes:
    - name: cache
      emptyDir:
        medium: Memory  # Backed by tmpfs (RAM)
        sizeLimit: 128Mi
```

**Test**:
```bash
kubectl exec emptydir-pod -c reader -- cat /data/log.txt
```

---

### HostPath

Mounts a file or directory from the host node's filesystem.

**⚠️ Warning**: Use with caution. Pods on different nodes see different data.

**Use Cases**:
- Accessing Docker socket
- Running cAdvisor
- Testing and development

**Types**:
- `DirectoryOrCreate`: Creates directory if it doesn't exist
- `Directory`: Directory must exist
- `FileOrCreate`: Creates file if doesn't exist
- `File`: File must exist
- `Socket`: Unix socket must exist

**Example**: HostPath volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostpath-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: host-data
          mountPath: /usr/share/nginx/html
  
  volumes:
    - name: host-data
      hostPath:
        path: /data/web  # Path on host
        type: DirectoryOrCreate
```

**Example**: Access Docker socket

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: docker-debug
spec:
  containers:
    - name: docker-cli
      image: docker:latest
      command: ["sleep", "3600"]
      volumeMounts:
        - name: docker-sock
          mountPath: /var/run/docker.sock
  
  volumes:
    - name: docker-sock
      hostPath:
        path: /var/run/docker.sock
        type: Socket
```

---

### ConfigMap and Secret Volumes

Mount configuration or sensitive data as files.

**Example**: ConfigMap as volume

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  config.json: |
    {
      "database": "postgres",
      "port": 5432
    }
  settings.ini: |
    [app]
    debug=false
    log_level=info
---
apiVersion: v1
kind: Pod
metadata:
  name: configmap-volume-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: config
          mountPath: /etc/config
          readOnly: true
  
  volumes:
    - name: config
      configMap:
        name: app-config
```

**Example**: Secret as volume

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  username: admin
  password: secretpassword
---
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: credentials
          mountPath: /etc/secrets
          readOnly: true
  
  volumes:
    - name: credentials
      secret:
        secretName: db-credentials
        defaultMode: 0400  # File permissions
```

**Example**: Mount specific keys

```yaml
volumes:
  - name: config
    configMap:
      name: app-config
      items:
        - key: config.json
          path: app/config.json  # Mount at /etc/config/app/config.json
        - key: settings.ini
          path: settings/app.ini
```

---

## Persistent Volumes (PV)

A PersistentVolume (PV) is a piece of storage in the cluster provisioned by an administrator or dynamically using Storage Classes.

**Lifecycle**: Independent of any pod using the PV

**Example**: NFS PersistentVolume

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 10Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs
  nfs:
    server: 192.168.1.100
    path: /exports/data
```

**Example**: HostPath PV (for testing)

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-storage
  hostPath:
    path: /mnt/data
    type: DirectoryOrCreate
```

**Check PV Status**:
```bash
kubectl get pv
kubectl describe pv nfs-pv
```

**PV Phases**:
- `Available`: Ready to be claimed
- `Bound`: Bound to a PVC
- `Released`: PVC deleted, but not yet reclaimed
- `Failed`: Automatic reclamation failed

---

## Persistent Volume Claims (PVC)

A PersistentVolumeClaim (PVC) is a request for storage by a user.

**Example**: Basic PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
```

**Example**: PVC with specific PV

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: specific-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs
  selector:
    matchLabels:
      environment: production
```

**Example**: Pod using PVC

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: persistent-storage
          mountPath: /usr/share/nginx/html
  
  volumes:
    - name: persistent-storage
      persistentVolumeClaim:
        claimName: my-pvc
```

**Check PVC Status**:
```bash
kubectl get pvc
kubectl describe pvc my-pvc
```

**PVC Phases**:
- `Pending`: No matching PV found
- `Bound`: Successfully bound to a PV
- `Lost`: PV lost

---

## Storage Classes

StorageClasses provide a way to describe different "classes" of storage.

**Benefits**:
- Dynamic provisioning
- Different performance tiers
- Cloud provider integration

**Example**: AWS EBS StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iopsPerGB: "10"
  fsType: ext4
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
```

**Example**: Local StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

**Example**: NFS StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs
provisioner: example.com/nfs
parameters:
  server: nfs-server.example.com
  path: /exports
  readOnly: "false"
```

**List StorageClasses**:
```bash
kubectl get storageclasses
kubectl get sc  # Short form
kubectl describe sc fast-ssd
```

**Set Default StorageClass**:
```yaml
metadata:
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
```

---

## Dynamic Provisioning

Dynamic provisioning automatically creates PVs when a PVC is created.

**How it works**:
1. User creates PVC referencing a StorageClass
2. StorageClass provisioner creates a PV
3. PVC is bound to the new PV

**Example**: PVC with dynamic provisioning

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd  # References StorageClass
```

**What happens**:
```bash
# 1. Create PVC
kubectl apply -f pvc.yaml

# 2. Check - PV is automatically created
kubectl get pv
kubectl get pvc

# 3. PVC is bound
NAME          STATUS   VOLUME                 CAPACITY   STORAGECLASS
dynamic-pvc   Bound    pvc-12345-abcde       10Gi       fast-ssd
```

---

## Volume Modes

Defines how the volume is consumed.

**Volume Modes**:
- `Filesystem`: Default. Mounted as a filesystem
- `Block`: Raw block device

**Example**: Block volume

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: block-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Block  # Block device
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd
---
apiVersion: v1
kind: Pod
metadata:
  name: block-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeDevices:  # Use volumeDevices for block
        - name: data
          devicePath: /dev/xvda
  
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: block-pvc
```

---

## Access Modes

Defines how volumes can be mounted.

| Access Mode | Description | Abbreviation | Use Case |
|-------------|-------------|--------------|----------|
| **ReadWriteOnce** | Single node read-write | RWO | Databases, block storage |
| **ReadOnlyMany** | Multiple nodes read-only | ROX | Static content, config |
| **ReadWriteMany** | Multiple nodes read-write | RWX | Shared file storage (NFS) |
| **ReadWriteOncePod** | Single pod read-write | RWOP | Exclusive pod access (1.22+) |

**Example**: Different access modes

```yaml
# RWO - Single node
spec:
  accessModes:
    - ReadWriteOnce

# ROX - Multiple nodes, read-only
spec:
  accessModes:
    - ReadOnlyMany

# RWX - Multiple nodes, read-write
spec:
  accessModes:
    - ReadWriteMany
```

**Compatibility**: Not all storage types support all modes

| Storage Type | RWO | ROX | RWX |
|--------------|-----|-----|-----|
| AWS EBS | ✅ | ❌ | ❌ |
| GCE PD | ✅ | ✅ | ❌ |
| NFS | ✅ | ✅ | ✅ |
| Azure Disk | ✅ | ❌ | ❌ |
| Azure File | ✅ | ✅ | ✅ |

---

## Reclaim Policies

Defines what happens to a PV when its PVC is deleted.

| Policy | Description | Use Case |
|--------|-------------|----------|
| **Retain** | Manual reclamation required | Production data |
| **Delete** | PV and backing storage deleted | Development |
| **Recycle** | Basic scrub (`rm -rf`) - deprecated | Legacy |

**Example**: PV with Retain policy

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: important-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain  # Keep data
  storageClassName: standard
  hostPath:
    path: /mnt/important-data
```

**Change Reclaim Policy**:
```bash
kubectl patch pv important-pv -p '{"spec":{"persistentVolumeReclaimPolicy":"Delete"}}'
```

---

## Volume Expansion

Expand PVC size without recreating it (requires StorageClass support).

**Enable in StorageClass**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expandable
provisioner: kubernetes.io/aws-ebs
allowVolumeExpansion: true  # Enable expansion
```

**Expand PVC**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: expandable-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi  # Original size
```

```bash
# Edit PVC to increase size
kubectl edit pvc expandable-pvc
# Change storage: 10Gi → storage: 20Gi

# Check status
kubectl get pvc expandable-pvc
# May require pod restart for filesystem expansion
```

**Note**: Some volume types require pod restart or specific CSI driver support.

---

## StatefulSets with Storage

StatefulSets use VolumeClaimTemplates for persistent storage per pod.

**Example**: StatefulSet with persistent storage

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
              name: mysql
          env:
            - name: MYSQL_ROOT_PASSWORD
              value: password
          volumeMounts:
            - name: data
              mountPath: /var/lib/mysql
  
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 10Gi
```

**How it works**:
```
mysql-0 → PVC: data-mysql-0 → PV: pvc-abc123
mysql-1 → PVC: data-mysql-1 → PV: pvc-def456
mysql-2 → PVC: data-mysql-2 → PV: pvc-ghi789
```

**Check StatefulSet PVCs**:
```bash
kubectl get pvc
# Shows: data-mysql-0, data-mysql-1, data-mysql-2

kubectl get pv
# Shows three bound PVs
```

---

## Best Practices

### 1. Use StorageClasses for Dynamic Provisioning

```yaml
# Define StorageClasses for different tiers
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
  annotations:
    storageclass.kubernetes.io/is-default-class: "false"
provisioner: kubernetes.io/aws-ebs
parameters:
  type: io2
  iopsPerGB: "50"
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
```

### 2. Use Appropriate Access Modes

```yaml
# Database - RWO
spec:
  accessModes:
    - ReadWriteOnce

# Shared content - RWX
spec:
  accessModes:
    - ReadWriteMany
```

### 3. Set Resource Limits

```yaml
spec:
  resources:
    requests:
      storage: 10Gi
    limits:
      storage: 50Gi
```

### 4. Use WaitForFirstConsumer for Node Affinity

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer  # Wait for pod scheduling
```

### 5. Label PVs for Organization

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: production-pv
  labels:
    environment: production
    tier: database
    cost-center: engineering
```

---

## Exam Tips

### Quick Commands

**Create PVC**:
```bash
# Imperative (limited options)
kubectl create -f pvc.yaml

# Check status
kubectl get pvc
kubectl describe pvc my-pvc

# Check bound PV
kubectl get pv
```

**Volume in Pod**:
```bash
# Check mounted volumes
kubectl describe pod my-pod | grep -A 10 Volumes

# Exec into pod and check mount
kubectl exec my-pod -- df -h /data
kubectl exec my-pod -- ls -la /data
```

**Troubleshooting**:
```bash
# PVC stuck in Pending
kubectl describe pvc my-pvc
# Check: No PV matching requirements, StorageClass not found

# Check PV details
kubectl get pv -o wide

# Check StorageClasses
kubectl get sc

# Check provisioner logs (if dynamic)
kubectl logs -n kube-system -l app=provisioner
```

### Common Tasks

**Task 1**: Create PV and PVC
```bash
# 1. Create PV
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /mnt/data
EOF

# 2. Create PVC
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
EOF

# 3. Verify binding
kubectl get pvc task-pvc
```

**Task 2**: Use PVC in Pod
```bash
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# Edit pod.yaml to add volume
# Then apply
kubectl apply -f pod.yaml

# Verify
kubectl exec nginx -- ls -la /data
```

**Task 3**: Expand PVC
```bash
# Edit PVC
kubectl edit pvc my-pvc
# Change storage size

# Check status
kubectl get pvc my-pvc -w
```

### Quick Reference

**PV Template**:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-name
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: standard
  hostPath:
    path: /mnt/data
```

**PVC Template**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-name
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

**Pod with PVC Template**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-name
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: storage
          mountPath: /data
  volumes:
    - name: storage
      persistentVolumeClaim:
        claimName: pvc-name
```

---

## Summary

**Storage Types**:
- **emptyDir**: Temporary, pod lifetime
- **hostPath**: Node filesystem, testing only
- **PV/PVC**: Persistent, production-ready

**Key Concepts**:
- **PV**: Cluster-level storage resource
- **PVC**: User request for storage
- **StorageClass**: Dynamic provisioning
- **Access Modes**: RWO, ROX, RWX, RWOP
- **Reclaim Policies**: Retain, Delete

**Commands**:
```bash
# PV and PVC
kubectl get pv
kubectl get pvc
kubectl describe pv <name>
kubectl describe pvc <name>

# StorageClass
kubectl get sc
kubectl describe sc <name>

# Check binding
kubectl get pv,pvc
```

**Next Module**: [Module 06: Configuration & Secrets →](../06-configuration-secrets/README.md)

---

**📝 Practice**: Complete the exercises in `exercises/exercises.md`!
