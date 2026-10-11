# Associate Cloud Engineer — exam blueprint

Source: the Associate Cloud Engineer certification exam guide, reviewed October 2026. Weights are Google’s approximations.

Role in one line: deploy and secure applications and infrastructure, monitor several projects, and keep solutions inside performance targets. AI tooling is in the role description. The scored work is still platform operations.

| Section | Weight | One-line job |
| --- | --- | --- |
| 1. Setting up a cloud solution environment | ~20% | Org, projects, IAM, APIs, quotas, billing, operations suite |
| 2. Planning and configuring a cloud solution | ~17.5% | Pick compute, storage, and network for a workload |
| 3. Deploying and implementing a cloud solution | ~25% | Actually create the resources. Heaviest section |
| 4. Ensuring successful operation | ~20% | Day-2: disks, clusters, traffic, backups, logs, alerts |
| 5. Configuring access and security | ~17.5% | IAM policies, custom roles, service accounts |

50–60 questions, 2 hours, 125 USD plus tax, valid 3 years. No case studies. Recommended experience is 6+ months hands-on.

## Section 1 — Setting up a cloud solution environment (~20%)

### 1.1 Projects and accounts

- Resource hierarchy: organization, folders, projects, resources. Inheritance flows down.
- Organization policies on that hierarchy.
- Grant IAM roles inside a project.
- Users and groups in Cloud Identity, manual and automated.
- Enable APIs in a project.
- Provision the operations suite (Cloud Logging, Cloud Monitoring).
- Quotas: read them and request increases.

### 1.2 Billing

- Create billing accounts.
- Link projects to a billing account.
- Budgets and alerts. A budget alert does not stop spend unless you build that yourself.
- Billing export (BigQuery, and the file export to Cloud Storage where the product offers it).

## Section 2 — Planning and configuring (~17.5%)

### 2.1 Compute

- Choose Compute Engine, GKE, Cloud Run, or Cloud Functions / Cloud Run functions for the workload.
- Spot VMs and custom machine types when they fit.

### 2.2 Data storage

- Product choice: Cloud SQL, BigQuery, Firestore, Spanner, Bigtable. AlloyDB shows up again in section 3 and 4, so treat it as in scope even though this bullet’s examples omit it.
- Disk and object class: zonal Persistent Disk, regional Persistent Disk, Cloud Storage Standard, Nearline, Coldline, Archive.

### 2.3 Network

- Load balancing choice.
- Where resources can live in a network (regions, zones, global vs regional resources).
- Network Service Tiers (Premium vs Standard).

## Section 3 — Deploying and implementing (~25%)

### 3.1 Compute Engine

- Launch an instance: disks, availability policy, SSH keys.
- Autoscaled managed instance group from an instance template.
- OS Login.
- VM Manager.

### 3.2 GKE

- Install and configure `kubectl`.
- Deploy a cluster: Autopilot, regional, private, GKE Enterprise.
- Deploy a containerized application.

### 3.3 Cloud Run and Cloud Functions

- Deploy an application.
- Receive Google Cloud events: Pub/Sub, Cloud Storage object notifications, Eventarc.
- Decide among Cloud Run (fully managed), Cloud Run for Anthos / GKE Enterprise, and Cloud Functions / Cloud Run functions.

### 3.4 Data

- Deploy Cloud SQL, Firestore, BigQuery, Spanner, Pub/Sub, Dataflow, Cloud Storage, AlloyDB.
- Load data: command-line upload, load from Cloud Storage, Storage Transfer Service.

### 3.5 Networking

- VPC with subnets: custom-mode VPC, Shared VPC.
- Ingress and egress firewall rules and policies: IP ranges, network tags, service accounts.
- Peer external networks: Cloud VPN, VPC Network Peering.

### 3.6 Infrastructure as code

- Cloud Foundation Toolkit, Config Connector, Terraform, Helm.

## Section 4 — Successful operation (~20%)

### 4.1 Compute Engine

- Connect remotely.
- Inventory running VMs (IDs and details).
- Snapshots: create from a VM, list, delete, schedule.
- Images: create from a VM or a snapshot, list, delete.

### 4.2 GKE

- Inventory: nodes, Pods, Services.
- Access Artifact Registry from GKE.
- Node pools: add, edit, remove.
- Kubernetes resources: Pods, Services, StatefulSets.
- Horizontal and vertical autoscaling.

### 4.3 Cloud Run

- Deploy a new version.
- Traffic splitting.
- Scaling parameters.

### 4.4 Storage and databases

- Secure objects in Cloud Storage.
- Object lifecycle policies.
- Query Cloud SQL, BigQuery, Spanner, Firestore, AlloyDB.
- Estimate storage cost.
- Backup and restore Cloud SQL and Firestore.
- Job status for Dataflow and BigQuery.

### 4.5 Networking

- Add a subnet.
- Expand a subnet’s IP range.
- Reserve static external or internal IPs.
- Cloud DNS and Cloud NAT.

### 4.6 Monitoring and logging

- Alerting policies on metrics.
- Custom metrics from apps or logs.
- Export logs (on-premises, BigQuery).
- Log buckets, log analytics, log routers.
- View and filter logs; open a log entry.
- Cloud diagnostics for an application issue.
- Google Cloud status.
- Ops Agent.
- Managed Service for Prometheus.
- Audit logs.

## Section 5 — Access and security (~17.5%)

### 5.1 IAM

- View and create IAM policies.
- Basic, predefined, and custom roles.

### 5.2 Service accounts

- Create service accounts.
- Minimum permissions in IAM policies.
- Attach a service account to a resource.
- IAM on the service account itself (who can use it).
- Impersonation.
- Short-lived credentials. User-managed JSON keys are the thing you avoid.

## How ACE questions are written

Most stems are “which command”, “which setting”, or “which product for this constraint”.

- If the stem names a click-path or a flag, it is section 3 or 4.
- If the stem asks you to choose among four products, it is section 2. Use the decision trees.
- If the stem is about who can do what, it is section 5. Least privilege wins. Basic roles (Owner, Editor, Viewer) are almost never the best answer.
- A budget does not stop charges. An organization policy can prevent an action. A firewall is stateful and applies to ingress or egress you specify. Implied deny is the default for ingress that no rule allows.

Study the service chapters, then do `03-ace/ace-hands-on-exercises.md` and `03-ace/ace-practice-exam.md`.
