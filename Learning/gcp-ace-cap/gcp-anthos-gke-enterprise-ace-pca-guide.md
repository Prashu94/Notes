# Google Cloud Anthos & GKE Enterprise - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Anthos Architecture](#anthos-architecture)
3. [GKE Enterprise](#gke-enterprise)
4. [Anthos on AWS/Azure](#anthos-on-awsazure)
5. [Anthos on VMware](#anthos-on-vmware)
6. [Anthos on Bare Metal](#anthos-on-bare-metal)
7. [Anthos Service Mesh](#anthos-service-mesh)
8. [Anthos Config Management](#anthos-config-management)
9. [Multi-Cluster Management](#multi-cluster-management)
10. [Connect Gateway](#connect-gateway)
11. [Security & Policy](#security--policy)
12. [Observability](#observability)
13. [Migration to Anthos](#migration-to-anthos)
14. [Cost Management](#cost-management)
15. [ACE Exam Focus](#ace-exam-focus)
16. [PCA Exam Focus](#pca-exam-focus)

---

## Overview

### What is Anthos?

Anthos is Google Cloud's application modernization platform that enables you to build, deploy, and manage applications across hybrid and multi-cloud environments. It provides a consistent platform for running applications on Google Cloud, on-premises data centers, and other cloud providers.

**Key Value Propositions:**
- **Consistency**: Same APIs and tools across all environments
- **Flexibility**: Run workloads where it makes sense (cloud, on-prem, edge)
- **Modernization**: Path from VMs to containers to serverless
- **Governance**: Centralized policy and configuration management
- **Security**: Zero-trust security model with service mesh

### Anthos vs GKE

| Feature | GKE (Standard) | GKE Enterprise (Anthos) |
|---------|----------------|-------------------------|
| **Scope** | Google Cloud only | Multi-cloud, hybrid |
| **Management** | Single cluster | Fleet of clusters |
| **Service Mesh** | Manual (Istio) | Managed (ASM) |
| **Config Management** | Manual | Anthos Config Management |
| **Security** | Basic | Advanced (Binary Auth, Policy Controller) |
| **Support** | Standard | Enterprise SLA |

### Anthos Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ANTHOS PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    CONTROL PLANE (Google Cloud)                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │   Fleet     │  │   Connect   │  │   Config    │             │   │
│  │  │   Mgmt      │  │   Gateway   │  │   Sync      │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                       DATA PLANE (Clusters)                       │   │
│  │                                                                    │   │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐     │   │
│  │  │   GKE    │   │  Anthos  │   │  Anthos  │   │  Anthos  │     │   │
│  │  │  (GCP)   │   │   AWS    │   │  VMware  │   │  Bare    │     │   │
│  │  │          │   │          │   │          │   │  Metal   │     │   │
│  │  └──────────┘   └──────────┘   └──────────┘   └──────────┘     │   │
│  │                                                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         SERVICES                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │   Service   │  │   Config    │  │   Policy    │             │   │
│  │  │   Mesh      │  │   Mgmt      │  │  Controller │             │   │
│  │  │   (ASM)     │  │   (ACM)     │  │             │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Anthos Architecture

### Fleet Management

A **Fleet** is a logical grouping of Kubernetes clusters that enables multi-cluster management. All Anthos clusters are registered to a fleet.

**Key Concepts:**
- **Fleet Host Project**: Google Cloud project that hosts the fleet
- **Membership**: Registration of a cluster to the fleet
- **Workload Identity Federation**: Identity management across clusters

```bash
# Register a GKE cluster to a fleet
gcloud container fleet memberships register my-gke-cluster \
    --gke-cluster=us-central1/my-gke-cluster \
    --enable-workload-identity

# List fleet memberships
gcloud container fleet memberships list

# Describe membership
gcloud container fleet memberships describe my-gke-cluster
```

### Hub and Spoke Model

```
┌─────────────────────────────────────────────────────────────┐
│                     FLEET HUB (GCP)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - Fleet management                                  │   │
│  │  - Config Sync                                      │   │
│  │  - Policy Controller                                │   │
│  │  - Connect Gateway                                  │   │
│  │  - Observability                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
      ┌──────────┐   ┌──────────┐   ┌──────────┐
      │   GKE    │   │  On-Prem │   │   AWS    │
      │ Cluster  │   │ Cluster  │   │ Cluster  │
      └──────────┘   └──────────┘   └──────────┘
```

### Anthos Identity

**Workload Identity Federation for GKE:**
- Kubernetes service accounts map to Google Cloud service accounts
- No service account keys required
- Works across all Anthos clusters

```bash
# Enable Workload Identity on GKE cluster
gcloud container clusters update my-cluster \
    --workload-pool=my-project.svc.id.goog \
    --zone=us-central1-a

# Configure Kubernetes service account
kubectl annotate serviceaccount my-ksa \
    iam.gke.io/gcp-service-account=my-gsa@my-project.iam.gserviceaccount.com

# Bind Kubernetes SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding my-gsa@my-project.iam.gserviceaccount.com \
    --role=roles/iam.workloadIdentityUser \
    --member="serviceAccount:my-project.svc.id.goog[default/my-ksa]"
```

---

## GKE Enterprise

### What is GKE Enterprise?

GKE Enterprise is the commercial name for Anthos capabilities on GKE clusters. It provides enterprise-grade features for running Kubernetes at scale.

**GKE Enterprise Features:**

| Feature | Description |
|---------|-------------|
| **Multi-cluster Management** | Manage multiple clusters as a fleet |
| **Anthos Service Mesh** | Managed Istio service mesh |
| **Anthos Config Management** | GitOps-based configuration |
| **Policy Controller** | OPA Gatekeeper for policy enforcement |
| **Binary Authorization** | Container image verification |
| **Advanced Security** | Workload Identity, security posture |

### Enabling GKE Enterprise

```bash
# Enable GKE Enterprise API
gcloud services enable anthos.googleapis.com
gcloud services enable gkehub.googleapis.com
gcloud services enable anthosconfigmanagement.googleapis.com
gcloud services enable mesh.googleapis.com

# Create GKE Enterprise cluster
gcloud container clusters create enterprise-cluster \
    --zone=us-central1-a \
    --workload-pool=my-project.svc.id.goog \
    --enable-mesh \
    --fleet-project=my-project
```

### GKE Enterprise Pricing

| Component | Pricing Model |
|-----------|--------------|
| **GKE Cluster** | Per vCPU/hour |
| **GKE Enterprise** | Per vCPU/hour (additional) |
| **Anthos Service Mesh** | Included with GKE Enterprise |
| **Config Management** | Included with GKE Enterprise |

---

## Anthos on AWS/Azure

### Anthos on AWS

Run Kubernetes clusters on AWS infrastructure, managed through Google Cloud.

**Architecture:**
- Control plane runs on AWS EC2 instances
- Node pools use AWS Auto Scaling groups
- Integrates with AWS VPC, EBS, IAM

```bash
# Prerequisites
# 1. AWS IAM roles and policies configured
# 2. VPC with appropriate subnets
# 3. SSH key pair created

# Create Anthos cluster on AWS
gcloud container aws clusters create my-aws-cluster \
    --aws-region=us-west-2 \
    --cluster-version=1.27 \
    --fleet-project=my-gcp-project \
    --vpc-id=vpc-0123456789abcdef0 \
    --pod-address-cidr-blocks=10.2.0.0/16 \
    --service-address-cidr-blocks=10.1.0.0/16 \
    --subnet-ids=subnet-0123456789abcdef0 \
    --iam-instance-profile=anthos-instance-profile \
    --database-encryption-kms-key-arn=arn:aws:kms:us-west-2:123456789012:key/key-id \
    --config-encryption-kms-key-arn=arn:aws:kms:us-west-2:123456789012:key/key-id \
    --role-arn=arn:aws:iam::123456789012:role/anthos-api-role \
    --admin-users=admin@example.com

# Create node pool
gcloud container aws node-pools create my-node-pool \
    --cluster=my-aws-cluster \
    --aws-region=us-west-2 \
    --node-version=1.27 \
    --min-nodes=1 \
    --max-nodes=5 \
    --max-pods-per-node=110 \
    --instance-type=t3.medium \
    --root-volume-size=50 \
    --root-volume-type=gp3 \
    --iam-instance-profile=anthos-node-profile \
    --ssh-ec2-key-pair=my-key-pair \
    --subnet-id=subnet-0123456789abcdef0
```

### Anthos on Azure

```bash
# Create Anthos cluster on Azure
gcloud container azure clusters create my-azure-cluster \
    --azure-region=eastus2 \
    --cluster-version=1.27 \
    --fleet-project=my-gcp-project \
    --resource-group-id=/subscriptions/SUB_ID/resourceGroups/my-rg \
    --vnet-id=/subscriptions/SUB_ID/resourceGroups/my-rg/providers/Microsoft.Network/virtualNetworks/my-vnet \
    --pod-address-cidr-blocks=10.2.0.0/16 \
    --service-address-cidr-blocks=10.1.0.0/16 \
    --ssh-public-key="$(cat ~/.ssh/id_rsa.pub)" \
    --admin-users=admin@example.com \
    --client=my-azure-client \
    --tenant=my-azure-tenant
```

### Multi-Cloud Use Cases

| Use Case | Description | Benefits |
|----------|-------------|----------|
| **Data Residency** | Run workloads in specific regions | Compliance |
| **Disaster Recovery** | Multi-cloud backup | Resilience |
| **Cost Optimization** | Use cheapest provider | Cost savings |
| **Vendor Independence** | Avoid lock-in | Flexibility |
| **M&A Integration** | Unified platform after acquisition | Consistency |

---

## Anthos on VMware

### Overview

Anthos on VMware (formerly GKE On-Prem) enables running Kubernetes clusters on VMware vSphere infrastructure.

**Components:**
- **Admin Cluster**: Manages user clusters
- **User Cluster**: Runs application workloads
- **Admin Workstation**: Used for cluster creation

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ON-PREMISES DATA CENTER                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  vSphere Infrastructure               │  │
│  │                                                       │  │
│  │  ┌─────────────┐         ┌─────────────┐            │  │
│  │  │   Admin     │         │    User     │            │  │
│  │  │   Cluster   │ ──────► │   Cluster   │            │  │
│  │  │             │ manages │             │            │  │
│  │  └─────────────┘         └─────────────┘            │  │
│  │         │                       │                    │  │
│  │         │                       │                    │  │
│  │  ┌──────▼──────┐         ┌─────▼─────┐             │  │
│  │  │   Admin     │         │   App     │             │  │
│  │  │ Workstation │         │ Workloads │             │  │
│  │  └─────────────┘         └───────────┘             │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             │ Connect Gateway
                             │
                             ▼
                    ┌─────────────────┐
                    │   Google Cloud  │
                    │   Console       │
                    └─────────────────┘
```

### Prerequisites

**vSphere Requirements:**
- vSphere 6.7 Update 3 or later
- vCenter Server
- NSX-T or standard vSphere networking
- F5 BIG-IP or Seesaw load balancer

**Hardware Requirements:**
- Admin cluster: 4 vCPU, 16 GB RAM minimum
- User cluster nodes: 4 vCPU, 8 GB RAM minimum

### Installation

```bash
# Download and configure admin workstation
# 1. Create admin workstation VM from OVA
# 2. SSH into admin workstation

# Generate SSH key
ssh-keygen -t rsa -f ~/.ssh/vsphere_key -N ""

# Create cluster configuration
cat > admin-cluster.yaml << EOF
apiVersion: v1
kind: AdminCluster
gkeOnPremVersion: 1.14.0
bundlePath: /var/lib/gke/bundles/gke-onprem-vsphere-1.14.0.tgz
vCenter:
  address: vcenter.example.com
  credentials:
    username: administrator@vsphere.local
    password: "password"
  datacenter: Datacenter
  datastore: datastore1
  cluster: Cluster
  resourcePool: resource-pool
  network: VM Network
loadBalancer:
  vips:
    controlPlaneVIP: 10.0.0.100
  kind: Seesaw
  seesaw:
    ipBlockFilePath: seesaw-ipblock.yaml
network:
  hostConfig:
    dnsServers:
    - 8.8.8.8
  ipBlockFilePath: admin-ipblock.yaml
adminMaster:
  cpus: 4
  memoryMB: 16384
  replicas: 3
EOF

# Create admin cluster
gkectl create admin --config admin-cluster.yaml

# Create user cluster
gkectl create cluster --config user-cluster.yaml --kubeconfig admin-kubeconfig
```

---

## Anthos on Bare Metal

### Overview

Anthos on Bare Metal enables running Kubernetes directly on physical servers or virtual machines without a hypervisor layer.

**Supported Environments:**
- Physical servers (bare metal)
- Virtual machines (KVM, VirtualBox, etc.)
- Edge locations
- Retail/manufacturing environments

### Deployment Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Standalone** | Single cluster, admin + user combined | Edge, small deployments |
| **Multi-cluster** | Admin cluster manages user clusters | Large deployments |
| **Hybrid** | Mix of admin and user on same nodes | Resource-constrained |

### Installation

```bash
# Prerequisites
# 1. Linux machines with container runtime
# 2. Network connectivity between nodes
# 3. Load balancer (F5, MetalLB, or manual)

# Create cluster configuration
cat > bmctl-config.yaml << EOF
apiVersion: baremetal.cluster.gke.io/v1
kind: Cluster
metadata:
  name: my-bare-metal-cluster
  namespace: cluster-my-bare-metal-cluster
spec:
  type: standalone
  profile: default
  anthosBareMetalVersion: 1.14.0
  gkeConnect:
    projectID: my-project
  controlPlane:
    nodePoolSpec:
      nodes:
      - address: 10.200.0.3
  loadBalancer:
    mode: bundled
    vips:
      controlPlaneVIP: 10.200.0.50
      ingressVIP: 10.200.0.51
    addressPools:
    - name: pool1
      addresses:
      - 10.200.0.51-10.200.0.70
  clusterNetwork:
    pods:
      cidrBlocks:
      - 192.168.0.0/16
    services:
      cidrBlocks:
      - 10.96.0.0/20
  nodeAccess:
    loginUser: root
EOF

# Create cluster
bmctl create cluster -c my-bare-metal-cluster
```

---

## Anthos Service Mesh

### Overview

Anthos Service Mesh (ASM) is a managed service mesh based on Istio that provides traffic management, security, and observability for microservices.

**Key Features:**
- **Traffic Management**: Load balancing, canary deployments, traffic splitting
- **Security**: mTLS, authorization policies
- **Observability**: Distributed tracing, metrics, logging
- **Managed Control Plane**: Google manages the Istio control plane

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ANTHOS SERVICE MESH                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              MANAGED CONTROL PLANE                   │   │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐            │   │
│  │   │  Istiod │  │ Config  │  │ Telemetry│            │   │
│  │   │         │  │  Sync   │  │         │            │   │
│  │   └─────────┘  └─────────┘  └─────────┘            │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    DATA PLANE                        │   │
│  │                                                      │   │
│  │  ┌────────────────┐    ┌────────────────┐          │   │
│  │  │    Pod A       │    │    Pod B       │          │   │
│  │  │ ┌────────────┐ │    │ ┌────────────┐ │          │   │
│  │  │ │   App      │ │    │ │   App      │ │          │   │
│  │  │ └────────────┘ │    │ └────────────┘ │          │   │
│  │  │ ┌────────────┐ │    │ ┌────────────┐ │          │   │
│  │  │ │   Envoy    │◄┼────┼►│   Envoy    │ │          │   │
│  │  │ │   Proxy    │ │mTLS│ │   Proxy    │ │          │   │
│  │  │ └────────────┘ │    │ └────────────┘ │          │   │
│  │  └────────────────┘    └────────────────┘          │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Installing ASM

```bash
# Download asmcli
curl https://storage.googleapis.com/csm-artifacts/asm/asmcli_1.17 > asmcli
chmod +x asmcli

# Install managed ASM (recommended)
./asmcli install \
  --project_id my-project \
  --cluster_name my-cluster \
  --cluster_location us-central1 \
  --fleet_id my-project \
  --output_dir ./asm-output \
  --enable_all \
  --managed

# Enable sidecar injection
kubectl label namespace default istio-injection=enabled --overwrite
```

### Traffic Management

#### Virtual Services

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-vs
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 90
    - destination:
        host: reviews
        subset: v2
      weight: 10
```

#### Destination Rules

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-dr
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
    loadBalancer:
      simple: ROUND_ROBIN
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### Security Policies

#### Peer Authentication (mTLS)

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # Enforce mTLS for all services
```

#### Authorization Policy

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: frontend-policy
  namespace: default
spec:
  selector:
    matchLabels:
      app: frontend
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/backend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

---

## Anthos Config Management

### Overview

Anthos Config Management (ACM) enables GitOps-style configuration management across your fleet of clusters.

**Components:**
- **Config Sync**: Syncs configuration from Git to clusters
- **Policy Controller**: Enforces policies using OPA Gatekeeper
- **Hierarchy Controller**: Namespace management

### Config Sync

#### Setup

```bash
# Enable Config Management
gcloud beta container fleet config-management enable

# Apply configuration
cat > config-management.yaml << EOF
apiVersion: configmanagement.gke.io/v1
kind: ConfigManagement
metadata:
  name: config-management
spec:
  sourceFormat: unstructured
  git:
    syncRepo: https://github.com/my-org/my-config-repo
    syncBranch: main
    secretType: ssh
    policyDir: config
EOF

kubectl apply -f config-management.yaml
```

#### Repository Structure

```
config-repo/
├── cluster/                    # Cluster-scoped resources
│   ├── namespaces.yaml
│   └── rbac.yaml
├── namespaces/                 # Namespace-scoped resources
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── backend/
│       ├── deployment.yaml
│       └── service.yaml
└── policies/                   # Policy Controller constraints
    ├── require-labels.yaml
    └── restrict-repos.yaml
```

### Policy Controller

Policy Controller uses OPA (Open Policy Agent) Gatekeeper to enforce policies.

#### Constraint Template

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

#### Constraint

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Namespace"]
  parameters:
    labels:
    - "team"
    - "environment"
```

---

## Connect Gateway

### Overview

Connect Gateway provides secure access to registered clusters from Google Cloud, enabling kubectl access without direct network connectivity.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                           │                                  │
│                           │ kubectl                          │
│                           ▼                                  │
│                  ┌─────────────────┐                        │
│                  │  Connect        │                        │
│                  │  Gateway        │                        │
│                  │  (GCP)          │                        │
│                  └────────┬────────┘                        │
│                           │                                  │
│     ┌─────────────────────┼─────────────────────┐          │
│     │                     │                      │          │
│     ▼                     ▼                      ▼          │
│ ┌────────┐          ┌────────┐            ┌────────┐       │
│ │ GKE    │          │ On-Prem │            │ AWS    │       │
│ │ Cluster│          │ Cluster │            │ Cluster│       │
│ └────────┘          └────────┘            └────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Configuration

```bash
# Generate kubeconfig for Connect Gateway
gcloud container fleet memberships get-credentials my-cluster

# Use kubectl with Connect Gateway
kubectl get pods --context=connectgateway_my-project_global_my-cluster

# Configure RBAC for gateway access
cat > gateway-rbac.yaml << EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: gateway-cluster-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: User
  name: user@example.com
EOF
kubectl apply -f gateway-rbac.yaml
```

---

## Security & Policy

### Binary Authorization

Enforce container image signing and verification before deployment.

```bash
# Enable Binary Authorization
gcloud services enable binaryauthorization.googleapis.com

# Create attestor
gcloud container binauthz attestors create my-attestor \
    --attestation-authority-note=projects/my-project/notes/my-note \
    --attestation-authority-note-project=my-project

# Create policy
cat > policy.yaml << EOF
globalPolicyEvaluationMode: ENABLE
defaultAdmissionRule:
  evaluationMode: REQUIRE_ATTESTATION
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
  requireAttestationsBy:
  - projects/my-project/attestors/my-attestor
admissionWhitelistPatterns:
- namePattern: gcr.io/google-containers/*
- namePattern: gcr.io/gke-release/*
EOF

gcloud container binauthz policy import policy.yaml
```

### Security Posture

```bash
# Enable security posture management
gcloud container clusters update my-cluster \
    --security-posture=standard \
    --workload-vulnerability-scanning=standard \
    --zone=us-central1-a

# View security findings
gcloud container security findings list --cluster=my-cluster
```

---

## Observability

### Cloud Operations Integration

ASM automatically integrates with Cloud Operations (formerly Stackdriver):

- **Cloud Logging**: Service mesh logs
- **Cloud Monitoring**: Service metrics and SLOs
- **Cloud Trace**: Distributed tracing

### Service Dashboard

```bash
# View service mesh metrics
gcloud monitoring dashboards list --filter="displayName:Service Mesh"

# Create SLO
cat > slo.yaml << EOF
displayName: "Availability SLO"
serviceLevelIndicator:
  requestBased:
    goodTotalRatio:
      goodServiceFilter: |
        metric.type="istio.io/service/server/request_count"
        resource.type="k8s_container"
        metric.labels.response_code="200"
      totalServiceFilter: |
        metric.type="istio.io/service/server/request_count"
        resource.type="k8s_container"
goal: 0.99
rollingPeriod: 86400s
EOF
```

---

## Migration to Anthos

### Migrate for Anthos

Migrate for Anthos (now Migrate to Containers) helps migrate VMs to containers running on GKE.

**Migration Process:**

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Source     │───►│  Migration   │───►│  Container   │
│   VM         │    │  Processing  │    │  on GKE      │
│              │    │              │    │              │
│  • VMware    │    │ • Extract    │    │ • Dockerfile │
│  • AWS       │    │ • Modernize  │    │ • Deployment │
│  • Azure     │    │ • Optimize   │    │ • Service    │
│  • GCE       │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Migration Steps

```bash
# Install Migrate for Anthos
migctl setup install --gke-cluster=my-cluster

# Create migration source (VMware)
migctl source create vmware my-vmware-source \
    --dc=Datacenter \
    --manager=vcenter.example.com \
    --username=admin \
    --password-file=password.txt

# Start migration
migctl migration create my-migration \
    --source=my-vmware-source \
    --vm-id=vm-123 \
    --intent=Image

# Generate artifacts
migctl migration get-artifacts my-migration

# Deploy to GKE
kubectl apply -f deployment_spec.yaml
```

---

## Cost Management

### Pricing Components

| Component | Pricing |
|-----------|---------|
| **GKE Enterprise** | Per vCPU/hour on cluster nodes |
| **Anthos on VMware** | Per vCPU/hour |
| **Anthos on Bare Metal** | Per vCPU/hour |
| **Anthos on AWS/Azure** | Per vCPU/hour + cloud provider costs |
| **ASM** | Included with GKE Enterprise |
| **ACM** | Included with GKE Enterprise |

### Cost Optimization

```bash
# Use committed use discounts
# 1-year or 3-year commitments for predictable workloads

# Right-size clusters
# Review resource utilization regularly

# Use GKE Autopilot for variable workloads
# Pay only for pod resources, not node capacity
```

---

## ACE Exam Focus

### Key Concepts for ACE

1. **Fleet Basics**: Understand fleet membership and registration
2. **Connect Gateway**: Know how to access clusters via Connect Gateway
3. **Workload Identity**: Configure service account mapping
4. **Basic ASM**: Understand sidecar injection and mTLS
5. **gcloud commands**: Cluster registration and basic operations

### Sample ACE Questions

**Q1:** How do you register an existing GKE cluster to a fleet?
- **A:** `gcloud container fleet memberships register <name> --gke-cluster=<location>/<cluster-name>`

**Q2:** What is required for Connect Gateway to work?
- **A:** 
  1. Cluster registered to fleet
  2. Connect agent deployed on cluster
  3. IAM permissions for users

**Q3:** How do you enable sidecar injection for a namespace in ASM?
- **A:** `kubectl label namespace <namespace> istio-injection=enabled`

### ACE gcloud Commands

```bash
# Fleet operations
gcloud container fleet memberships list
gcloud container fleet memberships register my-cluster --gke-cluster=us-central1/my-cluster
gcloud container fleet memberships describe my-cluster

# Connect Gateway
gcloud container fleet memberships get-credentials my-cluster

# Config Management
gcloud beta container fleet config-management status
```

---

## PCA Exam Focus

### Architecture Decision Framework

#### When to Use Anthos

| Scenario | Recommendation |
|----------|----------------|
| Pure cloud-native, GCP only | GKE Standard |
| Multi-cluster on GCP | GKE Enterprise |
| Hybrid (GCP + On-prem) | Anthos on VMware/Bare Metal |
| Multi-cloud requirements | Anthos on AWS/Azure |
| Edge computing | Anthos on Bare Metal |

#### Service Mesh Decisions

| Requirement | Solution |
|-------------|----------|
| Basic service communication | Kubernetes Services |
| mTLS between services | ASM |
| Traffic splitting/canary | ASM VirtualService |
| Advanced authorization | ASM AuthorizationPolicy |
| Multi-cluster service mesh | ASM with fleet |

### Sample PCA Questions

**Q1:** A company has workloads on GCP, AWS, and on-premises VMware. They need a consistent platform for managing all clusters with centralized policy enforcement. What architecture should they use?

**A:** 
- Fleet hub project on GCP
- GKE Enterprise for GCP workloads
- Anthos on AWS for AWS workloads
- Anthos on VMware for on-premises
- Anthos Config Management for GitOps
- Policy Controller for policy enforcement

**Q2:** A retail company needs to run Kubernetes at 1000 store locations with limited connectivity. What Anthos deployment model should they use?

**A:**
- Anthos on Bare Metal in standalone mode
- Edge profile for resource-constrained hardware
- Connect Gateway for remote management
- Config Sync for configuration distribution

**Q3:** Design a migration strategy for moving 50 legacy VMs to containers on GKE.

**A:**
1. **Assessment**: Analyze VM workloads with Migrate for Anthos
2. **Pilot**: Migrate 2-3 representative VMs first
3. **Containerize**: Use Migrate for Anthos to extract and containerize
4. **Modernize**: Refactor where beneficial
5. **Deploy**: Deploy to GKE with proper networking and security
6. **Validate**: Run parallel with VMs, then cutover

---

## Summary

### Anthos Decision Tree

```
                        Need Kubernetes?
                              │
                              ▼
                     ┌────────┴────────┐
                     │                  │
                     ▼                  ▼
                Single Cloud      Multi-Cloud/Hybrid
                     │                  │
                     ▼                  ▼
              ┌──────┴──────┐    ┌─────┴─────┐
              │              │    │           │
              ▼              ▼    ▼           ▼
           GKE           GKE    Anthos    Anthos
         Standard     Autopilot on AWS   on VMware
                                 │
                                 ▼
                              Anthos
                            Bare Metal
```

### Key Takeaways

| Topic | ACE Focus | PCA Focus |
|-------|-----------|-----------|
| Fleet | Registration | Multi-cluster strategy |
| Connect | Basic access | Security architecture |
| ASM | Sidecar injection | Traffic management, security |
| ACM | Basic sync | GitOps patterns, policy |
| Migration | Awareness | Full migration planning |
| Pricing | Awareness | Cost optimization |
