# Google Kubernetes Engine

ACE 3.2 and 4.2. PCA 1.3 and 2.3. GKE is managed Kubernetes. You still own manifests, requests and limits, and the choice of Autopilot or Standard.

Choose GKE when the team needs the Kubernetes API, StatefulSets, custom network policy, sidecars, or a platform that must look the same on Google Cloud and on-premises (GKE Enterprise). Choose Cloud Run when they only need to run a container.

## Modes and cluster scope

| Choice | You manage | You pay for | Exam default |
| --- | --- | --- | --- |
| Autopilot | Workloads. Google manages nodes. | Pod CPU, memory, and ephemeral storage requests | Recommended unless you need node access, DaemonSets that the mode rejects, or very large custom nodes |
| Standard | Node pools, OS upgrades (or auto-upgrade), node images | Nodes, whether pods fill them or not | GPUs in specific layouts, DaemonSets, SSH to nodes, custom kubelet |

| Scope | Control plane | Use |
| --- | --- | --- |
| Zonal | One zone | Labs. Not production HA |
| Regional | Replicas across zones | Production. Control plane survives a zone |

Private cluster: nodes have no public IP. The control plane is reached through private endpoint or an authorized network. Cloud NAT if pods must call the internet. This is the ACE “private cluster” bullet and the usual PCA security answer.

GKE Enterprise (formerly Anthos) adds fleet management, Config Sync, Policy Controller, and attached clusters (on-premises VMware, bare metal, and other clouds through GKE Multi-Cloud). Pick it when the stem says consistent policy across many clusters, including clusters that are not only in Google Cloud.

## Create and connect

```bash
# Autopilot regional private cluster
gcloud container clusters create-auto app \
  --region="$REGION" \
  --network=NETWORK \
  --subnetwork=SUBNET \
  --enable-private-nodes \
  --enable-master-global-access   # only if you truly need it

# Standard regional cluster with a node pool
gcloud container clusters create app-std \
  --region="$REGION" \
  --num-nodes=1 \
  --machine-type=e2-standard-4 \
  --release-channel=regular \
  --workload-pool="${PROJECT_ID}.svc.id.goog" \
  --enable-ip-alias \
  --enable-autoscaling --min-nodes=1 --max-nodes=5

gcloud container clusters list
gcloud container clusters describe app --region="$REGION"

gcloud container clusters get-credentials app --region="$REGION"
kubectl get nodes
kubectl get pods,svc,statefulset -A
```

Release channels (Rapid, Regular, Stable) control how fast Kubernetes versions arrive. Auto-upgrade of the control plane and nodes is the operational-excellence answer. Pinning forever is how you fail a supportability question.

## Workloads

```bash
kubectl create deployment web --image=REGION-docker.pkg.dev/PROJECT/REPO/web:1.2
kubectl expose deployment web --port=80 --target-port=8080 --type=ClusterIP
kubectl autoscale deployment web --min=2 --max=10 --cpu-percent=60
kubectl get hpa

# Vertical pod autoscaling is a cluster feature plus a recommender or updater.
gcloud container clusters update app --region="$REGION" --enable-vertical-pod-autoscaling
```

ACE 4.2 names Pods, Services, and StatefulSets.

- **Deployment** plus ReplicaSet: stateless replicas.
- **StatefulSet**: stable identity and a volume claim per pod. Databases you insist on running yourself.
- **DaemonSet**: one pod per node. Log collectors. Often Standard mode, because Autopilot restricts node-level pods.
- **Job / CronJob**: run to completion.
- **Service**: ClusterIP (in cluster), NodePort (rarely what you want), LoadBalancer (Google Cloud load balancer), headless (StatefulSet DNS).
- **Ingress** or **Gateway API**: HTTP routing. GKE Ingress creates an external or internal Application Load Balancer.
- **HPA**: scale pods on CPU, memory, or custom metrics.
- **VPA**: recommend or set requests. Do not fight HPA on the same metric.
- **Cluster autoscaler** (Standard) or Autopilot’s own capacity: add nodes when pods are pending.
- **Node auto-provisioning**: create node pools for pending pod shapes.

Node pools (Standard):

```bash
gcloud container node-pools create pool-b \
  --cluster=app-std --region="$REGION" \
  --machine-type=e2-standard-8 \
  --enable-autoscaling --min-nodes=0 --max-nodes=4 \
  --node-labels=workload=batch \
  --node-taints=workload=batch:NoSchedule

gcloud container node-pools update pool-b \
  --cluster=app-std --region="$REGION" \
  --enable-autoscaling --min-nodes=1 --max-nodes=6

gcloud container node-pools delete pool-b \
  --cluster=app-std --region="$REGION"
```

Spot pods (Autopilot) and Spot node pools (Standard) are the discount for fault-tolerant pods.

## Artifact Registry and Workload Identity

ACE 4.2: the cluster must pull images. Put images in Artifact Registry, not the retired Container Registry.

```bash
gcloud artifacts repositories create apps \
  --repository-format=docker --location="$REGION"

# On GKE, the node service account or the pod needs reader.
# Workload Identity is the right way for the pod to call Google APIs.
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[NAMESPACE/KSA_NAME]"

kubectl annotate serviceaccount KSA_NAME \
  --namespace NAMESPACE \
  iam.gke.io/gcp-service-account="$SA_EMAIL"
```

Grant `roles/artifactregistry.reader` to the node pool service account (Standard) so nodes can pull. Private clusters still pull if Private Google Access or Cloud NAT is in place. Private Google Access is the better answer for `*.pkg.dev`.

## Networking you get asked about

- **VPC-native / alias IP**: pod and service ranges are real VPC IPs. This is required for modern features. Routes-based clusters are legacy.
- **Dataplane V2**: eBPF, enforced NetworkPolicy. Turn it on for network policy stems.
- **NetworkPolicy**: east-west allow rules inside the cluster. It does not replace VPC firewalls for traffic that enters the VPC.
- **Multi-cluster Services / Multi-cluster Ingress**: one global ingress across clusters. PCA global serving.
- **Cloud Service Mesh**: managed Istio-style traffic, mTLS, retries. Pick it when the stem says service-to-service auth and traffic shifting inside the mesh. Do not add it for a single Cloud Run service.

## Security

- **Binary Authorization**: deploy only images that a attestor signed. Supply-chain answer, shared with Cloud Run.
- **Workload Identity**: no JSON keys on the node.
- **Shielded GKE nodes**, secure boot.
- **GKE Security Posture** and **Policy Controller** (gatekeeper constraints) for fleet rules: no privileged pods, required labels.
- **Secret Manager** add-on or CSI, not secrets baked into images.
- Control plane **authorized networks** and **private endpoint**.

```bash
gcloud container binauthz policy export > policy.yaml
# Edit, then import. Attestors are a longer setup; know the product name.
```

## Backup for GKE

Backup for GKE captures cluster config and volume data. It is the answer for “restore the namespace after a bad apply”, not for application-consistent database dumps. Databases still want their own backup (Cloud SQL backup, or a dump).

```bash
gcloud services enable gkebackup.googleapis.com
gcloud beta container backup-restore backup-plans create app-plan \
  --location="$REGION" \
  --cluster=projects/$PROJECT_ID/locations/$REGION/clusters/app \
  --all-namespaces \
  --include-volume-data
```

## Exercises

1. The platform team refuses to patch node OS images. Which mode?
2. Pods must call BigQuery as a specific service account with no key file. Which GKE feature?
3. You need `kubectl get nodes` to show a pool you can SSH, plus a DaemonSet log agent. Which mode?
4. Production control plane must survive a zone loss. Zonal or regional?
5. Security wants the same “no :latest images” rule on clusters in Google Cloud and on VMware. Which product family?

### Answers

1. Autopilot. Node lifecycle is Google’s.
2. Workload Identity, binding the Kubernetes service account to the Google service account that has a BigQuery role.
3. Standard. Autopilot hides nodes and blocks many DaemonSets.
4. Regional.
5. GKE Enterprise with Policy Controller (and Config Sync to ship the constraint). Binary Authorization if the rule is specifically image signatures.
