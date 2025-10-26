# Module 02: Cluster Installation & Configuration

## 📋 Learning Objectives

By the end of this module, you will be able to:
- Install Kubernetes cluster using kubeadm
- Configure control plane and worker nodes
- Upgrade Kubernetes cluster
- Implement High Availability (HA) clusters
- Backup and restore etcd
- Manage certificates

## 🎯 CKA Exam Relevance

This module covers **25%** of the CKA exam:
- Cluster installation and configuration
- Managing cluster upgrades
- etcd backup and restore
- Certificate management

**CKAD**: Basic understanding required (5% coverage)

---

## 🏗️ Installation Methods

### 1. kubeadm (Exam Focus)
- Production-ready tool for bootstrapping clusters
- Used in CKA exam
- Supports upgrades and certificate management

### 2. Minikube (Learning)
- Single-node cluster for local development
- Good for CKAD practice

### 3. kind (Kubernetes in Docker)
- Multiple nodes in Docker containers
- Fast and lightweight

### 4. Managed Services (Production)
- EKS (AWS), GKE (Google), AKS (Azure)
- Not covered in exam

---

## 🚀 Installing Kubernetes with kubeadm

### Prerequisites

**System Requirements** (per node):
- 2 CPUs minimum
- 2GB RAM minimum
- Network connectivity between nodes
- Unique hostname, MAC address, product_uuid
- Required ports open

**Required Ports**:

**Control Plane**:
```
6443       - Kubernetes API server
2379-2380  - etcd server client API
10250      - Kubelet API
10259      - kube-scheduler
10257      - kube-controller-manager
```

**Worker Nodes**:
```
10250      - Kubelet API
30000-32767 - NodePort Services
```

### Step 1: Prepare All Nodes

```bash
# Disable swap (required by kubelet)
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Load required kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# Set required sysctl parameters
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system

# Verify modules loaded
lsmod | grep br_netfilter
lsmod | grep overlay

# Verify sysctl settings
sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward
```

### Step 2: Install Container Runtime (containerd)

```bash
# Install containerd
sudo apt-get update
sudo apt-get install -y containerd

# Configure containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# Set SystemdCgroup = true (required for kubeadm)
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

# Restart containerd
sudo systemctl restart containerd
sudo systemctl enable containerd

# Verify containerd is running
sudo systemctl status containerd
```

### Step 3: Install kubeadm, kubelet, kubectl

```bash
# Add Kubernetes apt repository
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

# Download Google Cloud public signing key
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg \
  https://packages.cloud.google.com/apt/doc/apt-key.gpg

# Add Kubernetes apt repository
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] \
  https://apt.kubernetes.io/ kubernetes-xenial main" | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list

# Install specific version (for production)
sudo apt-get update
sudo apt-get install -y kubelet=1.31.0-00 kubeadm=1.31.0-00 kubectl=1.31.0-00

# Hold packages to prevent auto-updates
sudo apt-mark hold kubelet kubeadm kubectl

# Verify installation
kubeadm version
kubelet --version
kubectl version --client
```

### Step 4: Initialize Control Plane

**On Master Node**:

```bash
# Initialize cluster
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --apiserver-advertise-address=<MASTER_IP> \
  --control-plane-endpoint=<MASTER_IP>:6443

# Output will include:
# 1. kubectl config setup instructions
# 2. Worker node join command

# Setup kubectl for regular user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Verify control plane components
kubectl get nodes
kubectl get pods -n kube-system

# Check cluster info
kubectl cluster-info
```

**kubeadm init options**:
```bash
--pod-network-cidr      # CIDR for pod network (depends on CNI)
--apiserver-advertise-address  # IP address API server advertises
--control-plane-endpoint      # HA: Load balancer endpoint
--kubernetes-version    # Specific K8s version
--upload-certs          # Upload certificates to cluster (HA)
--config               # Configuration file path
```

### Step 5: Install Network Plugin (CNI)

**Calico** (Exam common):
```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# Verify pods are running
kubectl get pods -n kube-system -l k8s-app=calico-node
```

**Flannel**:
```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# Verify
kubectl get pods -n kube-system -l app=flannel
```

**Weave Net**:
```bash
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml

# Verify
kubectl get pods -n kube-system -l name=weave-net
```

### Step 6: Join Worker Nodes

**On each Worker Node**:

```bash
# Use the join command from kubeadm init output
sudo kubeadm join <MASTER_IP>:6443 \
  --token <TOKEN> \
  --discovery-token-ca-cert-hash sha256:<HASH>
```

**If you lost the join command**:

```bash
# On master node, create new token
kubeadm token create --print-join-command

# Or manually construct
# Get token
kubeadm token list

# Get CA cert hash
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | \
  openssl rsa -pubin -outform der 2>/dev/null | \
  openssl dgst -sha256 -hex | sed 's/^.* //'
```

### Step 7: Verify Cluster

```bash
# Check all nodes
kubectl get nodes

# Verify all system pods
kubectl get pods -n kube-system

# Check component health
kubectl get componentstatuses

# Test pod creation
kubectl run nginx --image=nginx
kubectl get pods

# Cleanup test pod
kubectl delete pod nginx
```

---

## 🔧 Cluster Configuration

### kubeadm Configuration File

Instead of command-line flags, use a configuration file:

```yaml
# kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.31.0
controlPlaneEndpoint: "loadbalancer.example.com:6443"
networking:
  podSubnet: "10.244.0.0/16"
  serviceSubnet: "10.96.0.0/12"
apiServer:
  extraArgs:
    authorization-mode: "Node,RBAC"
    enable-admission-plugins: "NodeRestriction"
  certSANs:
  - "kubernetes.example.com"
  - "192.168.1.100"
etcd:
  local:
    dataDir: "/var/lib/etcd"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "192.168.1.100"
  bindPort: 6443
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
```

**Initialize with config file**:
```bash
sudo kubeadm init --config kubeadm-config.yaml
```

### Kubelet Configuration

Located at: `/var/lib/kubelet/config.yaml`

```yaml
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
authentication:
  anonymous:
    enabled: false
  webhook:
    enabled: true
authorization:
  mode: Webhook
cgroupDriver: systemd
clusterDNS:
- 10.96.0.10
clusterDomain: cluster.local
containerRuntimeEndpoint: unix:///var/run/containerd/containerd.sock
cpuManagerPolicy: none
evictionHard:
  imagefs.available: 15%
  memory.available: 100Mi
  nodefs.available: 10%
maxPods: 110
```

**Apply configuration changes**:
```bash
sudo systemctl restart kubelet
```

---

## ⬆️ Cluster Upgrade

**IMPORTANT**: Always upgrade one minor version at a time (1.30 → 1.31 → 1.32)

### Upgrade Planning

1. Read release notes
2. Test in staging environment
3. Backup etcd
4. Upgrade control plane nodes
5. Upgrade worker nodes
6. Verify cluster health

### Upgrade Procedure

**Step 1: Upgrade kubeadm on Control Plane**

```bash
# Find available versions
apt-cache madison kubeadm

# Upgrade kubeadm (replace x with desired version)
sudo apt-mark unhold kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm=1.31.1-00
sudo apt-mark hold kubeadm

# Verify version
kubeadm version
```

**Step 2: Plan and Apply Upgrade**

```bash
# Check upgrade plan
sudo kubeadm upgrade plan

# Apply upgrade (on first control plane node)
sudo kubeadm upgrade apply v1.31.1

# For additional control plane nodes
sudo kubeadm upgrade node
```

**Step 3: Drain Control Plane Node**

```bash
# Mark node unschedulable and evict pods
kubectl drain <control-plane-node> --ignore-daemonsets
```

**Step 4: Upgrade kubelet and kubectl**

```bash
# Upgrade packages
sudo apt-mark unhold kubelet kubectl
sudo apt-get update
sudo apt-get install -y kubelet=1.31.1-00 kubectl=1.31.1-00
sudo apt-mark hold kubelet kubectl

# Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

**Step 5: Uncordon Node**

```bash
kubectl uncordon <control-plane-node>

# Verify node version
kubectl get nodes
```

**Step 6: Upgrade Worker Nodes**

For each worker node:

```bash
# On control plane: Drain the node
kubectl drain <worker-node> --ignore-daemonsets --delete-emptydir-data

# On worker node: Upgrade kubeadm
sudo apt-mark unhold kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm=1.31.1-00
sudo apt-mark hold kubeadm

# Upgrade node
sudo kubeadm upgrade node

# Upgrade kubelet and kubectl
sudo apt-mark unhold kubelet kubectl
sudo apt-get update
sudo apt-get install -y kubelet=1.31.1-00 kubectl=1.31.1-00
sudo apt-mark hold kubelet kubectl

# Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# On control plane: Uncordon the node
kubectl uncordon <worker-node>
```

**Step 7: Verify Upgrade**

```bash
# Check all nodes updated
kubectl get nodes

# Verify pods are running
kubectl get pods --all-namespaces

# Check component versions
kubectl version
kubeadm version
kubelet --version
```

---

## 💾 etcd Backup and Restore

### Backup etcd

```bash
# Set etcd environment variables
ETCDCTL_API=3

# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db --write-out=table

# Copy backup to safe location
cp /tmp/etcd-backup.db /backup/etcd-backup-$(date +%Y%m%d-%H%M%S).db
```

### Automated Backup Script

```bash
#!/bin/bash
# etcd-backup.sh

BACKUP_DIR="/backup/etcd"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/etcd-backup-$TIMESTAMP.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
ETCDCTL_API=3 etcdctl snapshot save $BACKUP_FILE \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    ETCDCTL_API=3 etcdctl snapshot status $BACKUP_FILE --write-out=table
    
    # Delete backups older than 7 days
    find $BACKUP_DIR -name "etcd-backup-*.db" -mtime +7 -delete
else
    echo "Backup failed!"
    exit 1
fi
```

### Restore etcd

```bash
# Stop API server and etcd
sudo mv /etc/kubernetes/manifests/kube-apiserver.yaml /tmp/
sudo mv /etc/kubernetes/manifests/etcd.yaml /tmp/

# Restore from backup
ETCDCTL_API=3 etcdctl snapshot restore /tmp/etcd-backup.db \
  --data-dir=/var/lib/etcd-restore \
  --initial-cluster=master=https://192.168.1.100:2380 \
  --initial-advertise-peer-urls=https://192.168.1.100:2380 \
  --name=master

# Update etcd manifest to use restored data
sudo vi /tmp/etcd.yaml
# Change: --data-dir=/var/lib/etcd to --data-dir=/var/lib/etcd-restore

# Restore manifests
sudo mv /tmp/etcd.yaml /etc/kubernetes/manifests/
sudo mv /tmp/kube-apiserver.yaml /etc/kubernetes/manifests/

# Wait for etcd and API server to start
kubectl get pods -n kube-system -w
```

---

## 🔐 Certificate Management

### Certificate Locations

```
/etc/kubernetes/pki/
├── ca.crt                      # Cluster CA certificate
├── ca.key                      # Cluster CA key
├── apiserver.crt               # API server certificate
├── apiserver.key               # API server key
├── apiserver-kubelet-client.crt
├── apiserver-kubelet-client.key
├── front-proxy-ca.crt
├── front-proxy-ca.key
├── front-proxy-client.crt
├── front-proxy-client.key
├── sa.key                      # Service account key
├── sa.pub                      # Service account public key
└── etcd/
    ├── ca.crt                  # etcd CA certificate
    ├── ca.key                  # etcd CA key
    ├── server.crt              # etcd server certificate
    ├── server.key              # etcd server key
    ├── peer.crt               # etcd peer certificate
    └── peer.key               # etcd peer key
```

### Check Certificate Expiry

```bash
# Check all certificates
sudo kubeadm certs check-expiration

# Example output:
# CERTIFICATE                EXPIRES                  RESIDUAL TIME
# admin.conf                 Jan 01, 2025 12:00 UTC   364d
# apiserver                  Jan 01, 2025 12:00 UTC   364d
# apiserver-etcd-client      Jan 01, 2025 12:00 UTC   364d
```

### Renew Certificates

```bash
# Renew all certificates
sudo kubeadm certs renew all

# Renew specific certificate
sudo kubeadm certs renew apiserver

# Verify renewal
sudo kubeadm certs check-expiration

# Restart control plane components
sudo kubectl -n kube-system delete pod -l component=kube-apiserver
sudo kubectl -n kube-system delete pod -l component=kube-controller-manager
sudo kubectl -n kube-system delete pod -l component=kube-scheduler
```

### Manual Certificate Renewal

```bash
# Generate new certificates with custom duration
sudo kubeadm init phase certs apiserver --config /path/to/kubeadm-config.yaml

# Update kubeconfig
sudo kubeadm init phase kubeconfig all
```

---

## 🏗️ High Availability (HA) Cluster

### HA Architecture

```
         Load Balancer (HAProxy/nginx)
         192.168.1.100:6443
                 │
    ┌────────────┼────────────┐
    │            │            │
Master-1     Master-2     Master-3
   │            │            │
   └────────────┴────────────┘
              etcd cluster
```

### Setup HA Cluster

**Step 1: Setup Load Balancer**

```bash
# HAProxy configuration
# /etc/haproxy/haproxy.cfg

frontend kubernetes-frontend
    bind 192.168.1.100:6443
    mode tcp
    option tcplog
    default_backend kubernetes-backend

backend kubernetes-backend
    mode tcp
    option tcp-check
    balance roundrobin
    server master1 192.168.1.101:6443 check fall 3 rise 2
    server master2 192.168.1.102:6443 check fall 3 rise 2
    server master3 192.168.1.103:6443 check fall 3 rise 2
```

**Step 2: Initialize First Control Plane**

```bash
# On master-1
sudo kubeadm init \
  --control-plane-endpoint="192.168.1.100:6443" \
  --upload-certs \
  --pod-network-cidr=10.244.0.0/16

# Save the output:
# - Worker node join command
# - Control plane join command with --certificate-key
```

**Step 3: Join Additional Control Planes**

```bash
# On master-2 and master-3
sudo kubeadm join 192.168.1.100:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane \
  --certificate-key <certificate-key>
```

---

## 🎯 Exam Tips

### CKA Specific

1. **Know kubeadm commands**:
   - `kubeadm init`
   - `kubeadm join`
   - `kubeadm upgrade plan/apply`
   - `kubeadm token create`
   - `kubeadm certs check-expiration`

2. **Practice etcd backup/restore**: This is a common exam question

3. **Remember certificate locations**: `/etc/kubernetes/pki/`

4. **Know drain/cordon/uncordon**: Essential for node maintenance

5. **Understand upgrade order**: Control plane → Workers

### Time-Saving Commands

```bash
# Generate join command
kubeadm token create --print-join-command

# Quick etcd backup
ETCDCTL_API=3 etcdctl snapshot save /tmp/backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Check upgrade versions
apt-cache madison kubeadm | head -5

# Drain node quickly
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data --force
```

---

## 📚 Key Commands Reference

```bash
# Installation
kubeadm init --pod-network-cidr=10.244.0.0/16
kubeadm join <endpoint> --token <token> --discovery-token-ca-cert-hash sha256:<hash>
kubeadm token create --print-join-command

# Upgrade
kubeadm upgrade plan
kubeadm upgrade apply v1.31.1
kubeadm upgrade node

# etcd
etcdctl snapshot save <file>
etcdctl snapshot restore <file>
etcdctl snapshot status <file>

# Certificates
kubeadm certs check-expiration
kubeadm certs renew all

# Node management
kubectl drain <node> --ignore-daemonsets
kubectl cordon <node>
kubectl uncordon <node>

# Cluster info
kubectl cluster-info
kubectl get nodes
kubectl version
kubeadm version
```

---

**Next Module**: [03 - Workloads & Scheduling](../03-workloads-scheduling/README.md)
