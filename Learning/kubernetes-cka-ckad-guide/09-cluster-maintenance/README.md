# Module 09: Cluster Maintenance

## 📚 Overview

Learn cluster maintenance tasks including node management, upgrades, backups, and disaster recovery.

**Exam Weight**: CKA (12% - Cluster Architecture, Installation & Configuration)

---

## Node Maintenance

### Drain Node

Safely evict pods from a node before maintenance.

```bash
# Drain node (evicts pods)
kubectl drain node-name

# Ignore DaemonSets
kubectl drain node-name --ignore-daemonsets

# Force deletion of pods not managed by controllers
kubectl drain node-name --force

# Delete emptyDir volumes
kubectl drain node-name --delete-emptydir-data

# Set grace period
kubectl drain node-name --grace-period=60

# Combined (common exam scenario)
kubectl drain node-name --ignore-daemonsets --force --delete-emptydir-data
```

**What happens**:
1. Node marked unschedulable (cordoned)
2. Pods gracefully terminated
3. Pods rescheduled on other nodes
4. Node ready for maintenance

### Cordon Node

Mark node as unschedulable without evicting existing pods.

```bash
# Cordon node (no new pods)
kubectl cordon node-name

# Check status
kubectl get nodes
# Shows: SchedulingDisabled
```

**Use case**: Prevent new pods while existing pods continue running.

### Uncordon Node

Make node schedulable again.

```bash
# Uncordon node
kubectl uncordon node-name

# Verify
kubectl get nodes
```

**Workflow**:
```bash
# 1. Cordon
kubectl cordon node-name

# 2. Perform maintenance

# 3. Uncordon
kubectl uncordon node-name
```

---

## Cluster Upgrades

### Upgrade Strategy

Kubernetes supports version skew:
- Control plane components can be one minor version apart
- Kubelets can be two minor versions behind API server
- Kubectl within one minor version

**Example**: If API server is 1.28, kubelet can be 1.26-1.28

### Check Versions

```bash
# Cluster version
kubectl version --short

# Component versions
kubectl get nodes -o wide

# Available versions
kubeadm upgrade plan
```

### Upgrade Control Plane

**For first control plane node**:

```bash
# 1. Drain node
kubectl drain control-plane-node --ignore-daemonsets

# 2. Upgrade kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm=1.28.x-00

# 3. Verify kubeadm version
kubeadm version

# 4. Check upgrade plan
sudo kubeadm upgrade plan

# 5. Upgrade cluster
sudo kubeadm upgrade apply v1.28.x

# 6. Upgrade kubelet and kubectl
sudo apt-get install -y kubelet=1.28.x-00 kubectl=1.28.x-00

# 7. Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# 8. Uncordon node
kubectl uncordon control-plane-node
```

**For additional control plane nodes**:

```bash
# 1. Drain
kubectl drain control-plane-node-2 --ignore-daemonsets

# 2. Upgrade kubeadm
sudo apt-get install -y kubeadm=1.28.x-00

# 3. Upgrade node
sudo kubeadm upgrade node

# 4. Upgrade kubelet and kubectl
sudo apt-get install -y kubelet=1.28.x-00 kubectl=1.28.x-00

# 5. Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# 6. Uncordon
kubectl uncordon control-plane-node-2
```

### Upgrade Worker Nodes

```bash
# From control plane, drain worker
kubectl drain worker-node-1 --ignore-daemonsets --force

# On worker node:

# 1. Upgrade kubeadm
sudo apt-get install -y kubeadm=1.28.x-00

# 2. Upgrade node configuration
sudo kubeadm upgrade node

# 3. Upgrade kubelet and kubectl
sudo apt-get install -y kubelet=1.28.x-00 kubectl=1.28.x-00

# 4. Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# From control plane, uncordon
kubectl uncordon worker-node-1
```

### Upgrade Best Practices

1. **One minor version at a time**: 1.26 → 1.27 → 1.28
2. **Backup etcd first**
3. **Upgrade control plane before workers**
4. **Test in non-production first**
5. **Check release notes**
6. **Monitor during upgrade**

---

## etcd Backup & Restore

### Backup etcd

```bash
# Set etcdctl API version
export ETCDCTL_API=3

# Backup etcd
sudo ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
sudo ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot.db --write-out=table
```

**Output**:
```
+----------+----------+------------+------------+
|   HASH   | REVISION | TOTAL KEYS | TOTAL SIZE |
+----------+----------+------------+------------+
| 12345678 |    45678 |       1234 |     2.1 MB |
+----------+----------+------------+------------+
```

### Restore etcd

```bash
# Stop API server (on control plane)
sudo systemctl stop kube-apiserver

# Restore etcd
sudo ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-snapshot.db \
  --data-dir=/var/lib/etcd-restore \
  --initial-cluster=control-plane=https://127.0.0.1:2380 \
  --initial-advertise-peer-urls=https://127.0.0.1:2380

# Update etcd manifest to use new data directory
sudo vi /etc/kubernetes/manifests/etcd.yaml
# Change: --data-dir=/var/lib/etcd-restore

# etcd and API server will restart automatically
# Wait for cluster to be ready
kubectl get nodes
```

### Find etcd Certificates

```bash
# From etcd pod spec
kubectl describe pod etcd-control-plane -n kube-system

# Common locations:
--cacert=/etc/kubernetes/pki/etcd/ca.crt
--cert=/etc/kubernetes/pki/etcd/server.crt
--key=/etc/kubernetes/pki/etcd/server.key
--endpoints=https://127.0.0.1:2379
```

---

## Certificate Management

### View Certificates

```bash
# API server certificates
sudo openssl x509 -in /etc/kubernetes/pki/apiserver.crt -text -noout

# Check expiration
sudo kubeadm certs check-expiration
```

### Renew Certificates

```bash
# Renew all certificates
sudo kubeadm certs renew all

# Renew specific certificate
sudo kubeadm certs renew apiserver

# Restart control plane components
sudo systemctl restart kubelet
```

---

## OS Upgrades

When performing OS upgrades on nodes:

```bash
# 1. Drain node
kubectl drain node-name --ignore-daemonsets --force

# 2. SSH to node and perform OS upgrade
ssh node-name
sudo apt-get update && sudo apt-get upgrade -y
sudo reboot

# 3. Wait for node to come back online

# 4. Uncordon node
kubectl uncordon node-name

# 5. Verify
kubectl get nodes
```

---

## Cluster Backup Strategy

### What to Backup

1. **etcd** (most important)
   - All cluster state
   - All Kubernetes objects

2. **Certificate files**
   - `/etc/kubernetes/pki/`

3. **Kubeconfig files**
   - `/etc/kubernetes/admin.conf`

4. **Application manifests** (if not in source control)

### Backup Script Example

```bash
#!/bin/bash

BACKUP_DIR="/backup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save "$BACKUP_DIR/etcd-snapshot.db" \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Backup certificates
cp -r /etc/kubernetes/pki "$BACKUP_DIR/"

# Backup kubeconfig
cp /etc/kubernetes/admin.conf "$BACKUP_DIR/"

# Export all resources (optional)
kubectl get all --all-namespaces -o yaml > "$BACKUP_DIR/all-resources.yaml"

echo "Backup completed: $BACKUP_DIR"
```

---

## Monitoring Node Health

### Node Conditions

```bash
# Check node conditions
kubectl describe node node-name | grep Conditions: -A 10
```

**Conditions**:
- **Ready**: Node is healthy
- **MemoryPressure**: Node running out of memory
- **DiskPressure**: Node running out of disk
- **PIDPressure**: Too many processes
- **NetworkUnavailable**: Network not configured

### Taints

Automatically added when node has issues:

```bash
# View taints
kubectl describe node node-name | grep Taints

# Common taints:
# node.kubernetes.io/not-ready:NoExecute
# node.kubernetes.io/unreachable:NoExecute
# node.kubernetes.io/memory-pressure:NoSchedule
# node.kubernetes.io/disk-pressure:NoSchedule
```

---

## Exam Tips

**Quick Commands**:
```bash
# Node management
kubectl drain node-name --ignore-daemonsets --force
kubectl cordon node-name
kubectl uncordon node-name

# Cluster upgrade
kubeadm upgrade plan
sudo kubeadm upgrade apply v1.28.0
sudo apt-get install -y kubelet=1.28.0-00 kubectl=1.28.0-00
sudo systemctl daemon-reload && sudo systemctl restart kubelet

# etcd backup
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# etcd restore
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd.db --data-dir=/var/lib/etcd-restore

# Check versions
kubectl version --short
kubeadm version
kubelet --version

# Check certificates
sudo kubeadm certs check-expiration
```

**Common Tasks**:
1. Drain node for maintenance
2. Upgrade cluster components
3. Backup etcd
4. Restore etcd from backup
5. Cordon/uncordon nodes
6. Check certificate expiration

**Upgrade Order**:
1. Control plane node 1 (with `kubeadm upgrade apply`)
2. Additional control plane nodes (with `kubeadm upgrade node`)
3. Worker nodes

---

## Summary

**Node Maintenance**:
- `kubectl drain`: Evict pods + cordon
- `kubectl cordon`: Mark unschedulable
- `kubectl uncordon`: Make schedulable

**Cluster Upgrades**:
- Upgrade one minor version at a time
- Control plane before workers
- Backup etcd first
- Use `kubeadm upgrade`

**etcd Backup**:
- `etcdctl snapshot save`: Create backup
- `etcdctl snapshot restore`: Restore backup
- Always backup before major changes

**Certificates**:
- Check expiration: `kubeadm certs check-expiration`
- Renew: `kubeadm certs renew all`

**Next Module**: [Module 10: Application Lifecycle →](../10-application-lifecycle/README.md)
