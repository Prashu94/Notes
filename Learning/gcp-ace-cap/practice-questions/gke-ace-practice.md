# Google Kubernetes Engine (GKE) - ACE Practice Questions

## Question 1
You need to create a GKE cluster with 3 nodes in the us-central1-a zone. Which command should you use?

**A)** 
```bash
gcloud container clusters create my-cluster \
  --zone=us-central1-a \
  --num-nodes=3
```

**B)** 
```bash
gcloud compute clusters create my-cluster \
  --zone=us-central1-a \
  --nodes=3
```

**C)** 
```bash
kubectl create cluster my-cluster \
  --zone=us-central1-a \
  --num-nodes=3
```

**D)** 
```bash
gcloud kubernetes clusters create my-cluster \
  --region=us-central1 \
  --nodes=3
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `gcloud container clusters create` is the correct command for GKE
  - `--zone=us-central1-a` specifies the zone (zonal cluster)
  - `--num-nodes=3` creates 3 nodes per zone (3 total for zonal)
  - Correct syntax and parameters

Create cluster examples:
```bash
# Basic zonal cluster
gcloud container clusters create my-cluster \
  --zone=us-central1-a \
  --num-nodes=3

# With specific machine type
gcloud container clusters create my-cluster \
  --zone=us-central1-a \
  --machine-type=n1-standard-2 \
  --num-nodes=3

# Regional cluster (high availability)
gcloud container clusters create my-cluster \
  --region=us-central1 \
  --num-nodes=3
# Creates 3 nodes per zone × 3 zones = 9 total nodes
```

- Option B is incorrect because:
  - Wrong command: should be `gcloud container`, not `gcloud compute`
  - `compute` is for Compute Engine, not GKE
  - `--nodes` is not the correct parameter name

- Option C is incorrect because:
  - `kubectl` is for managing Kubernetes resources, not creating clusters
  - Cannot create GKE clusters with kubectl
  - Must use `gcloud container clusters create`

- Option D is incorrect because:
  - Wrong command: should be `gcloud container`, not `gcloud kubernetes`
  - `--nodes` is not the correct parameter name (should be `--num-nodes`)

**Get cluster credentials:**
```bash
gcloud container clusters get-credentials my-cluster --zone=us-central1-a
```

---

## Question 2
Your application running in GKE needs to access Cloud Storage buckets. What is the recommended way to grant this access?

**A)** Create a service account key and mount it as a Kubernetes secret

**B)** Use Workload Identity to bind Kubernetes service accounts to GCP service accounts

**C)** Grant the default Compute Engine service account storage permissions

**D)** Use node service account with storage permissions

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Workload Identity is Google's recommended way for GKE pods to access GCP services
  - No service account keys required
  - Fine-grained access control per Kubernetes service account/namespace
  - Follows security best practices
  - Integrates with IAM

Setup Workload Identity:
```bash
# 1. Enable Workload Identity on cluster (new cluster)
gcloud container clusters create my-cluster \
  --workload-pool=PROJECT_ID.svc.id.goog \
  --zone=us-central1-a

# Or update existing cluster
gcloud container clusters update my-cluster \
  --workload-pool=PROJECT_ID.svc.id.goog \
  --zone=us-central1-a

# 2. Create GCP service account
gcloud iam service-accounts create gke-storage-sa \
  --display-name="GKE Storage Access"

# 3. Grant Cloud Storage permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:gke-storage-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# 4. Create Kubernetes service account
kubectl create serviceaccount k8s-sa \
  --namespace=default

# 5. Bind K8s SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  gke-storage-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member=serviceAccount:PROJECT_ID.svc.id.goog[default/k8s-sa]

# 6. Annotate Kubernetes service account
kubectl annotate serviceaccount k8s-sa \
  iam.gke.io/gcp-service-account=gke-storage-sa@PROJECT_ID.iam.gserviceaccount.com \
  --namespace=default

# 7. Use in Pod
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  serviceAccountName: k8s-sa
  containers:
  - name: app
    image: gcr.io/my-project/my-app
```

- Option A is incorrect because:
  - Service account keys are a security risk
  - Keys can be compromised
  - Google recommends avoiding key files
  - Workload Identity is the proper solution

- Option C is incorrect because:
  - Default Compute Engine SA has broad permissions
  - Violates principle of least privilege
  - All pods would have same permissions
  - Hard to audit specific access

- Option D is incorrect because:
  - Node service account applies to all pods on the node
  - Too broad, not per-application
  - Violates least privilege

**Workload Identity Benefits:**
- No service account keys
- Fine-grained permissions
- Integrates with IAM
- Audit trail
- Automatic credential rotation

---

## Question 3
You need to scale your GKE deployment to handle increased traffic. The deployment should automatically scale based on CPU usage. What should you create?

**A)** Horizontal Pod Autoscaler (HPA)

**B)** Vertical Pod Autoscaler (VPA)

**C)** Cluster Autoscaler

**D)** Manual scaling with `kubectl scale`

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - HPA automatically scales the number of pods based on metrics
  - CPU utilization is a common autoscaling metric
  - Integrated with Kubernetes metrics server
  - Adjusts replica count dynamically

Create HPA:
```bash
# Create deployment first
kubectl create deployment web-app \
  --image=gcr.io/my-project/web-app \
  --replicas=2

# Create HPA (scale 2-10 pods based on 70% CPU)
kubectl autoscale deployment web-app \
  --cpu-percent=70 \
  --min=2 \
  --max=10

# Or using YAML
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

# Apply HPA
kubectl apply -f hpa.yaml

# Check HPA status
kubectl get hpa
```

How HPA works:
1. Metrics server collects CPU/memory usage
2. HPA controller checks metrics every 15 seconds
3. If average CPU > target, adds pods
4. If average CPU < target, removes pods
5. Respects min/max replica bounds

- Option B is incorrect because:
  - VPA adjusts pod resource requests/limits (CPU/memory)
  - Doesn't change number of pods
  - Different use case (right-sizing resources)

- Option C is incorrect because:
  - Cluster Autoscaler adds/removes nodes, not pods
  - Works with HPA (complementary)
  - Scales infrastructure, not application

- Option D is incorrect because:
  - Manual scaling doesn't automatically respond to load
  - Requires human intervention
  - Not suitable for dynamic traffic

**Autoscaling Comparison:**
- **HPA**: Scale number of pods (horizontal)
- **VPA**: Scale pod resources (vertical)
- **Cluster Autoscaler**: Scale number of nodes

Combined example:
```bash
# HPA scales pods based on CPU
kubectl autoscale deployment web-app --cpu-percent=70 --min=2 --max=10

# Cluster Autoscaler automatically adds nodes when needed
gcloud container clusters update my-cluster \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5 \
  --zone=us-central1-a
```

---

## Question 4
You need to deploy an application to GKE that requires access to a secrets stored in Secret Manager. What is the recommended approach?

**A)** Create Kubernetes secrets and sync from Secret Manager manually

**B)** Use the Secret Manager CSI driver

**C)** Mount Secret Manager secrets as environment variables

**D)** Hardcode secrets in the Docker image

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Secret Manager CSI driver mounts secrets directly into pods
  - Secrets stay in Secret Manager (centralized)
  - Automatic rotation support
  - No manual syncing needed
  - Secure and auditable

Setup Secret Manager CSI Driver:
```bash
# 1. Enable Secret Manager CSI driver on cluster
gcloud container clusters update my-cluster \
  --update-addons=GcpSecretManagerCsiDriver=ENABLED \
  --zone=us-central1-a

# 2. Create secret in Secret Manager
echo -n "my-secret-value" | gcloud secrets create db-password --data-file=-

# 3. Grant access to GCP service account (via Workload Identity)
gcloud secrets add-iam-policy-binding db-password \
  --member=serviceAccount:gke-app-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

# 4. Create pod with secret mounted
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  serviceAccountName: k8s-sa  # Mapped to gke-app-sa via Workload Identity
  containers:
  - name: app
    image: gcr.io/my-project/app
    volumeMounts:
    - name: secrets
      mountPath: "/secrets"
      readOnly: true
  volumes:
  - name: secrets
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "app-secrets"
---
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: app-secrets
spec:
  provider: gcp
  parameters:
    secrets: |
      - resourceName: "projects/PROJECT_ID/secrets/db-password/versions/latest"
        path: "db-password.txt"

# Apply
kubectl apply -f pod.yaml

# Secret will be available at /secrets/db-password.txt in the pod
```

- Option A is incorrect because:
  - Manual syncing is error-prone
  - Operational overhead
  - Secrets can become stale
  - Built-in CSI driver eliminates this need

- Option C is incorrect because:
  - Environment variables are less secure (visible in `kubectl describe`)
  - No automatic rotation
  - CSI driver is the recommended approach

- Option D is incorrect because:
  - Major security violation
  - Secrets exposed in image layers
  - Cannot rotate without rebuilding image
  - Fails security audits

**Secret Manager Benefits:**
- Centralized secret management
- Automatic rotation
- Audit logging
- Versioning
- Access control via IAM

---

## Question 5
Your GKE cluster needs to pull private images from Container Registry. What should you configure?

**A)** Create a Kubernetes imagePullSecrets with Container Registry credentials

**B)** Use the default GKE service account which already has access

**C)** Grant the GKE node service account the Storage Object Viewer role

**D)** Make the Container Registry public

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - GKE nodes pull images using their service account
  - Container Registry uses Cloud Storage for image storage
  - `roles/storage.objectViewer` allows reading images
  - Default configuration, but sometimes needs explicit grant

Grant access:
```bash
# Get the node service account
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format="value(projectNumber)")
NODE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Storage Object Viewer role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:${NODE_SA} \
  --role=roles/storage.objectViewer

# Or grant at bucket level (Container Registry bucket)
gsutil iam ch serviceAccount:${NODE_SA}:objectViewer gs://artifacts.PROJECT_ID.appspot.com
```

Pull private image in pod:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app
    image: gcr.io/my-project/private-image:v1
  # No imagePullSecrets needed with proper IAM permissions!
```

- Option A is incorrect because:
  - Not necessary when using GCP service accounts
  - More complex setup
  - imagePullSecrets are for non-GCP registries
  - IAM-based access is simpler

- Option B is partially correct:
  - Default service account USUALLY has access
  - But may need explicit grant in some cases
  - Option C is more explicit and guaranteed

- Option D is incorrect because:
  - Making registry public exposes images to everyone
  - Security risk
  - Not appropriate for private images

**Alternative: Dedicated Service Account**
```bash
# Create dedicated service account for pulling images
gcloud iam service-accounts create gcr-puller

# Grant access to Container Registry
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:gcr-puller@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer

# Use custom service account for node pool
gcloud container node-pools create custom-pool \
  --cluster=my-cluster \
  --service-account=gcr-puller@PROJECT_ID.iam.gserviceaccount.com \
  --zone=us-central1-a
```

---

## Question 6
You need to expose a GKE deployment to the internet with a global load balancer. What type of Kubernetes service should you create?

**A)** ClusterIP

**B)** NodePort

**C)** LoadBalancer (with `cloud.google.com/load-balancer-type: "External"` annotation)

**D)** Ingress

**Correct Answer:** D

**Explanation:**
- Option D is correct because:
  - Ingress creates HTTP(S) Load Balancer (global)
  - Layer 7 load balancing with advanced features
  - SSL termination, URL-based routing
  - Global anycast IP
  - CDN integration possible

Create Ingress:
```yaml
# 1. Create deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: gcr.io/my-project/web-app
        ports:
        - containerPort: 8080
---
# 2. Create NodePort or ClusterIP service
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort  # Or ClusterIP
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
---
# 3. Create Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80

# Apply all
kubectl apply -f ingress.yaml

# Get Ingress IP (takes a few minutes to provision)
kubectl get ingress web-ingress
```

Advanced Ingress (SSL, multiple paths):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: advanced-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
    networking.gke.io/managed-certificates: "web-cert"
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
---
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: web-cert
spec:
  domains:
    - example.com
```

- Option A is incorrect because:
  - ClusterIP is internal only
  - Not accessible from internet
  - Used for pod-to-pod communication

- Option B is incorrect because:
  - NodePort exposes service on each node's IP
  - Not a global load balancer  
  - No advanced routing features
  - Manual DNS management needed

- Option C is incorrect because:
  - LoadBalancer service creates Network Load Balancer (L4), not global HTTP(S) LB
  - Regional, not global
  - No URL-based routing
  - Ingress is better for HTTP(S) traffic

**Service Types:**
- **ClusterIP**: Internal only (default)
- **NodePort**: Accessible via node IPs (testing)
- **LoadBalancer**: Network Load Balancer (L4, regional)
- **Ingress**: HTTP(S) Load Balancer (L7, global)

---

## Question 7
You need to perform a rolling update of your deployment to a new image version without downtime. What command should you use?

**A)** 
```bash
kubectl set image deployment/web-app web=gcr.io/my-project/web-app:v2
```

**B)** 
```bash
kubectl delete deployment web-app && kubectl create deployment web-app --image=gcr.io/my-project/web-app:v2
```

**C)** 
```bash
kubectl scale deployment web-app --replicas=0 && kubectl scale deployment web-app --replicas=3
```

**D)** 
```bash
kubectl replace deployment web-app --image=gcr.io/my-project/web-app:v2
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `kubectl set image` updates the deployment with a new image
  - Performs rolling update automatically
  - Zero downtime (maintains availability)
  - Creates new pods before terminating old ones
  - Follows Kubernetes deployment strategy

Rolling update workflow:
```bash
# Update image
kubectl set image deployment/web-app \
  web=gcr.io/my-project/web-app:v2

# Update multiple containers
kubectl set image deployment/web-app \
  web=gcr.io/my-project/web-app:v2 \
  sidecar=gcr.io/my-project/sidecar:v2

# Monitor rollout status
kubectl rollout status deployment/web-app

# View rollout history
kubectl rollout history deployment/web-app

# Rollback if needed
kubectl rollout undo deployment/web-app

# Rollback to specific revision
kubectl rollout undo deployment/web-app --to-revision=2
```

Deployment with rollout strategy:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max 2 extra pods during update
      maxUnavailable: 1  # Max 1 pod can be unavailable
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: gcr.io/my-project/web-app:v1
```

- Option B is incorrect because:
  - Deleting deployment causes downtime
  - All pods terminate before new ones start
  - Not a rolling update
  - Service disruption

- Option C is incorrect because:
  - Scaling to 0 causes complete outage
  - Not a rolling update
  - Major service disruption

- Option D is incorrect because:
  - `kubectl replace` is not for image updates
  - Requires full manifest
  - Not the standard rolling update approach

**Rolling Update vs Recreate:**
```yaml
# Rolling Update (default, zero downtime)
spec:
  strategy:
    type: RollingUpdate

# Recreate (all old pods deleted first, brief downtime)
spec:
  strategy:
    type: Recreate
```

---

## Question 8
Your GKE cluster is running out of capacity. Pods are pending because there aren't enough nodes. What should you enable to automatically add nodes when needed?

**A)** Horizontal Pod Autoscaler

**B)** Vertical Pod Autoscaler

**C)** Cluster Autoscaler

**D)** Node Auto-provisioning

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Cluster Autoscaler automatically adds/removes nodes based on pod demand
  - Detects pending pods (unable to schedule)
  - Adds nodes to handle the load
  - Removes underutilized nodes to save costs
  - Works with HPA

Enable Cluster Autoscaler:
```bash
# Enable on existing cluster
gcloud container clusters update my-cluster \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --zone=us-central1-a

# Enable on specific node pool
gcloud container node-pools update default-pool \
  --cluster=my-cluster \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --zone=us-central1-a

# Create cluster with autoscaling
gcloud container clusters create my-cluster \
  --zone=us-central1-a \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --num-nodes=3
```

How it works:
1. Pod cannot be scheduled (pending state)
2. Cluster Autoscaler detects pending pods
3. Calculates required nodes
4. Adds nodes to the cluster
5. Pod gets scheduled on new node

Scale-down behavior:
- Removes nodes when utilization < 50% for 10+ minutes
- Never scales below min-nodes
- Respects PodDisruptionBudgets

- Option A is incorrect because:
  - HPA scales pods, not nodes
  - Doesn't add cluster capacity
  - Complements Cluster Autoscaler

- Option B is incorrect because:
  - VPA adjusts pod resources, doesn't add nodes
  - Different use case

- Option D is incorrect because:
  - Node Auto-provisioning is a GKE feature but more advanced
  - Automatically creates node pools with optimal machine types
  - Cluster Autoscaler is the standard answer for scaling existing pools

**Complete Autoscaling Setup:**
```bash
# 1. Enable Cluster Autoscaler (nodes)
gcloud container clusters update my-cluster \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10

# 2. Create HPA (pods)
kubectl autoscale deployment web-app \
  --cpu-percent=70 \
  --min=2 \
  --max=50

# Now:
# - Traffic increases → HPA adds pods
# - Not enough nodes → Cluster Autoscaler adds nodes
# - Traffic decreases → HPA reduces pods
# - Nodes underutilized → Cluster Autoscaler removes nodes
```

---

## Question 9
You need to run a batch job in GKE that processes data and then exits. Which Kubernetes resource should you use?

**A)** Deployment

**B)** StatefulSet

**C)** Job

**D)** DaemonSet

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Jobs run pods to completion and then stop
  - Designed for batch processing
  - Track successful completions
  - Retries on failure
  - Pod terminates when done

Create Job:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processor
spec:
  completions: 1      # Run 1 successful pod
  parallelism: 1      # 1 pod at a time
  backoffLimit: 3     # Retry up to 3 times on failure
  template:
    spec:
      containers:
      - name: processor
        image: gcr.io/my-project/data-processor
        command: ["python", "process.py"]
      restartPolicy: Never  # Don't restart on completion

# Apply
kubectl apply -f job.yaml

# Monitor job
kubectl get jobs
kubectl describe job data-processor

# View logs
kubectl logs job/data-processor

# Delete job after completion
kubectl delete job data-processor
```

Parallel job processing:
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-processor
spec:
  completions: 10     # Process 10 items total
  parallelism: 3      # 3 pods running at a time
  template:
    spec:
      containers:
      - name: worker
        image: gcr.io/my-project/worker
      restartPolicy: Never
```

CronJob for scheduled batch jobs:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"  # Run at 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: reporter
            image: gcr.io/my-project/report-generator
          restartPolicy: OnFailure
```

- Option A is incorrect because:
  - Deployments are for long-running services
  - Pods restart continuously
  - Not designed for batch jobs
  - Pods never terminate

- Option B is incorrect because:
  - StatefulSets are for stateful applications (databases)
  - Pods are long-running
  - Not for batch processing

- Option D is incorrect because:
  - DaemonSets run one pod per node
  - Continuous running
  - Not for batch jobs

**Job vs CronJob:**
- **Job**: Run once (or fixed number of times)
- **CronJob**: Run on schedule (recurring)

---

## Question 10
You need to ensure that at least 2 pods of a deployment are always available during voluntary disruptions (updates, pod evictions). What should you create?

**A)** HorizontalPodAutoscaler

**B)** PodDisruptionBudget

**C)** ResourceQuota

**D)** NetworkPolicy

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - PodDisruptionBudget (PDB) limits disruptions during voluntary operations
  - Ensures minimum availability during updates
  - Prevents too many pods from being unavailable
  - Works with kubectl drain, cluster autoscaler, rolling updates

Create PodDisruptionBudget:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
spec:
  minAvailable: 2     # At least 2 pods must be available
  selector:
    matchLabels:
      app: web-app

# Or use maxUnavailable
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
spec:
  maxUnavailable: 1   # At most 1 pod can be unavailable
  selector:
    matchLabels:
      app: web-app

# Apply
kubectl apply -f pdb.yaml

# View PDB status
kubectl get pdb
kubectl describe pdb web-app-pdb
```

How PDB works:
1. Deployment has 5 pods with PDB minAvailable: 2
2. During rolling update or node drain:
   - Controller ensures >= 2 pods remain running
   - Only terminates pods if constraint can be met
3. Prevents too many simultaneous disruptions

Example: Node drain with PDB
```bash
# Drain node (respects PDB)
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# Process:
# - Checks PDB constraints
# - Evicts pods gradually
# - Ensures minAvailable is respected
# - May take time if PDB is restrictive
```

- Option A is incorrect because:
  - HPA scales pods based on metrics
  - Doesn't control disruption tolerance
  - Different purpose

- Option C is incorrect because:
  - ResourceQuota limits resource usage per namespace
  - Doesn't control pod availability
  - Different use case

- Option D is incorrect because:
  - NetworkPolicy controls network traffic
  - Doesn't relate to pod availability
  - Different purpose

**Best Practices:**
```yaml
# For critical services, use percentage
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: critical-app-pdb
spec:
  minAvailable: 75%   # 75% of pods must be available
  selector:
    matchLabels:
      app: critical-app
      tier: production
```

**PDB with Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: nginx
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-app-pdb
spec:
  minAvailable: 3     # 3 out of 5 must be available
  selector:
    matchLabels:
      app: web-app
```
