# GKE deep dive

Read `02-gke.md` first. This file is private clusters, identity, upgrades, autoscaling, and the fleet controls PCA uses.

## Private cluster, piece by piece

A private cluster has three independent switches. Questions combine them.

| Switch | Effect |
| --- | --- |
| Private nodes | Node IPs are internal only. No public IP on the node. |
| Private control-plane endpoint | `kubectl` does not use a public control-plane IP. You reach it from the VPC or from an authorized network path. |
| Control-plane authorized networks | Even a public endpoint accepts `kubectl` only from listed CIDRs. |
| Private Google Access on the subnet | Nodes pull images and call Google APIs without Cloud NAT. |
| Cloud NAT | Nodes reach the public internet (OS packages, third-party APIs). |

Image pull of `pkg.dev` needs Private Google Access or NAT. Private Google Access is the better answer for Google APIs. NAT is the answer for the public internet. You often need both.

```bash
gcloud container clusters create app \
  --region="$REGION" \
  --network=prod --subnetwork=app \
  --cluster-secondary-range-name=pods \
  --services-secondary-range-name=services \
  --enable-private-nodes \
  --enable-private-endpoint \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-master-authorized-networks \
  --master-authorized-networks=10.0.0.0/8 \
  --enable-ip-alias \
  --workload-pool="${PROJECT_ID}.svc.id.goog" \
  --release-channel=regular \
  --enable-dataplane-v2

gcloud container clusters create-auto app-auto \
  --region="$REGION" \
  --network=prod --subnetwork=app \
  --enable-private-nodes
```

`master-ipv4-cidr` is a /28 that must not overlap the VPC. It is the control plane’s range, peered into your VPC. Pod secondary ranges must be large. A /24 for pods runs out immediately. Plan /16 or larger for pods on a real cluster, and a separate range for services.

VPC-native (alias IP, `--enable-ip-alias`) is required for modern features. Routes-based clusters are legacy.

## Upgrades

Release channels:

| Channel | What you accept |
| --- | --- |
| Rapid | Newest Kubernetes. Non-prod or a platform team that wants features early. |
| Regular | Default production. |
| Stable | Slowest. Regulated or change-averse. |

You still get upgrades. A channel is not a pin forever. Maintenance exclusions can freeze a window (Black Friday). A cluster that is many versions behind loses support and some CVE fixes.

Standard node pools upgrade with a surge: max surge creates extra nodes, max unavailable caps how many can be down. Set surge so PodDisruptionBudgets can be honored.

```bash
gcloud container clusters update app --region="$REGION" \
  --maintenance-window-start=2026-10-12T08:00:00Z \
  --maintenance-window-end=2026-10-12T14:00:00Z \
  --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=TU,WE"

gcloud container node-pools update pool-1 \
  --cluster=app --region="$REGION" \
  --max-surge-upgrade=1 --max-unavailable-upgrade=0 \
  --enable-autoscaling --min-nodes=1 --max-nodes=5
```

Autopilot upgrades nodes for you. That is the point of the mode.

## Autoscaling, three layers

| Layer | Scales | Mode |
| --- | --- | --- |
| Horizontal Pod Autoscaler | Pod replicas | CPU, memory, or custom / external metrics |
| Vertical Pod Autoscaler | Requests on a pod | Off, Initial (set once), Recreate, Auto |
| Cluster autoscaler or Autopilot | Nodes or capacity | Pending pods that do not fit |

Do not run HPA and VPA Auto on the same CPU metric. They fight. VPA Initial plus HPA is a common pair: VPA recommends requests, HPA scales replicas.

Node auto-provisioning (Standard) creates node pools when a pending pod needs a shape you did not define (GPU, large memory). Autopilot does this without a node pool you manage.

```bash
kubectl autoscale deployment web --cpu-percent=60 --min=2 --max=20
gcloud container clusters update app --region="$REGION" \
  --enable-vertical-pod-autoscaling \
  --enable-autoscaling --min-nodes=1 --max-nodes=8
```

A PodDisruptionBudget (`minAvailable`) is what keeps a voluntary upgrade from taking the whole service down. It does not stop a zone failure.

## Workload Identity

The pod’s Kubernetes service account is allowed to impersonate a Google service account. No JSON key on the node.

```bash
gcloud iam service-accounts create gke-web --project="$PROJECT_ID"
SA="gke-web@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA}" --role="roles/bigquery.dataViewer"

gcloud iam service-accounts add-iam-policy-binding "$SA" \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[apps/web]"

kubectl create namespace apps
kubectl create serviceaccount web --namespace apps
kubectl annotate serviceaccount web --namespace apps \
  iam.gke.io/gcp-service-account="$SA"
```

The pod spec must use that Kubernetes service account. The cluster must have been created with `--workload-pool=PROJECT_ID.svc.id.goog`. The node service account still needs `roles/artifactregistry.reader` to pull images, unless you use a separate image-pull identity. Those are two different identities: pull versus call BigQuery.

## Services, Ingress, Gateway

| Object | Creates | Stem |
| --- | --- | --- |
| ClusterIP | Nothing outside the cluster | East-west only |
| NodePort | A port on every node | Rarely the right public answer |
| LoadBalancer Service | A passthrough or external network load balancer | TCP, client IP, not HTTP routing |
| Ingress | An external or internal Application Load Balancer | Host and path routing |
| Gateway API | The newer load-balancer API on GKE | Same job as Ingress, current API |
| Multi Cluster Ingress | One global LB across clusters | Global active-active HTTP |
| Internal LB annotation | Internal passthrough or internal ALB | Callers are in the VPC |

Container-native load balancing uses network endpoint groups of pod IPs, not node ports. Health checks hit pods directly. This is the default you want.

Cloud Armor and Cloud CDN attach to the Application Load Balancer that Ingress or Gateway created, not to a ClusterIP.

## Policy and supply chain

**NetworkPolicy** is enforced when Dataplane V2 is on (Cilium) or when the older Calico provider is enabled. A NetworkPolicy object does nothing if the cluster cannot enforce it. Default is allow all east-west until you write a default-deny.

**Pod Security** standards (restricted, baseline) and **Policy Controller** (Gatekeeper constraints from GKE Enterprise) reject privileged pods. Policy Controller is fleet-wide. A PodSecurity admission config is one cluster.

**Binary Authorization** blocks deploy of images that lack an attestor signature. Dry-run mode logs violations without blocking. Enforcement mode blocks. The exam answer for “only signed images” is enforcement, not scanning alone.

```bash
gcloud container binauthz policy export > /tmp/binauthz.yaml
# Set defaultAdmissionRule.evaluationMode to REQUIRE_ATTESTATION
# and name the attestors. Then:
gcloud container binauthz policy import /tmp/binauthz.yaml
```

**Secret Manager** or the Secret Store CSI driver mounts secrets. Kubernetes Secrets are base64, etcd-encrypted if you turn on application-layer encryption, and still a worse store than Secret Manager for rotation.

## GKE Enterprise fleet

A fleet groups clusters: GKE, on-premises (VMware or bare metal software), and clusters on other clouds (GKE Multi-Cloud).

| Feature | Job |
| --- | --- |
| Config Sync | Git is the source of manifests. Drift is reverted. |
| Policy Controller | Constraints across the fleet |
| Config Controller | Google Cloud resources as Kubernetes objects, fleet-level |
| Cloud Service Mesh | mTLS, traffic splitting, retries between services |
| Multi Cluster Ingress | One external hostname, many clusters |
| Connect gateway | `kubectl` to attached clusters through Google’s API |

Pick the fleet when the stem says “same policy on the cluster in the plant and the cluster in `us-central1`”. A single Autopilot cluster does not need Config Sync to be valid. Do not add Anthos-era products to a one-cluster story.

## Backup for GKE

Backs up Kubernetes resources and, if you ask, persistent volume data. Restore can target another cluster in another region. It is the “I applied the wrong namespace” and “I lost the cluster” answer. It is not a substitute for database-native backups of Cloud SQL running outside the cluster. A pod that runs MySQL on a PVC should still dump or use a volume snapshot you have restored once.

```bash
gcloud services enable gkebackup.googleapis.com
gcloud beta container backup-restore backup-plans create app-plan \
  --location="$REGION" \
  --cluster="projects/${PROJECT_ID}/locations/${REGION}/clusters/app" \
  --all-namespaces \
  --include-volume-data \
  --cron-schedule="0 3 * * *" \
  --backup-retain-days=14
```

## Spot and cost

Standard: a node pool with Spot VMs. Autopilot: Spot pods. Both can disappear. Use them for batch Jobs, not for the only replica of a payment API. A PodDisruptionBudget does not stop a Spot preemption. Handle it in the app or with a retrying Job.

## Exercises

1. Nodes have no public IP. `docker pull` from Artifact Registry fails. `apt-get` is not the failing command. What is missing on the subnet?
2. The pod should query BigQuery. A key file is forbidden. List the three configuration objects.
3. Two teams want the same “no privileged pods” rule on six clusters, two of them on VMware. Which product?
4. HPA scales to 30 pods and they stay Pending. Autopilot is off. What scales next?
5. You need HTTP path routing, Cloud Armor, and pod-level health checks. Service type LoadBalancer or Ingress?

### Answers

1. Private Google Access. NAT would also work for registry traffic but is the broader tool. The stem said apt is fine to ignore, so the Google API path is the one that is broken.
2. A Kubernetes service account, a Google service account with a BigQuery role, and `roles/iam.workloadIdentityUser` binding the KS account to the Google account, plus the annotation. Workload pool must be on.
3. GKE Enterprise Policy Controller, with the VMware clusters attached to the fleet.
4. Cluster autoscaler, or node auto-provisioning if the pending pods need a new machine shape. Also check quota.
5. Ingress or Gateway API, which builds an Application Load Balancer and NEGs. A LoadBalancer Service is the wrong layer for paths and Armor.
