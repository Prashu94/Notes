# ACE practice exam

Twenty original questions in the style of the Associate Cloud Engineer exam. One or more answers are correct only when the question says so. Write your choice, then read the key at the bottom. Time yourself at about 40 minutes.

## Questions

**1.** You need to stop developers creating Compute Engine instances with public IP addresses. Several of them have `roles/editor` on the project. What should you do?

A. Remove Editor and grant Viewer.
B. Set the organization policy constraint that denies external IPs on VMs, at the folder.
C. Create a VPC firewall rule that denies ingress from `0.0.0.0/0`.
D. Delete the default route to the internet gateway.

**2.** An application on a private VM must download OS packages from the internet and must read from Cloud Storage without a public IP on the VM. Which two features do you need?

A. Private Google Access and Cloud NAT.
B. A public IP and a firewall allow.
C. VPC peering and Shared VPC.
D. Cloud CDN and Cloud Armor.

**3.** You must run a stateless container that scales to zero and does not need Kubernetes. Which product?

A. App Engine flexible environment.
B. Compute Engine unmanaged instance group.
C. Cloud Run.
D. GKE Standard with one node.

**4.** Which command reserves a regional external address?

A. `gcloud compute addresses create web-ip --global`
B. `gcloud compute addresses create web-ip --region=us-central1`
C. `gcloud dns record-sets create web-ip --type=A`
D. `gcloud compute networks subnets expand-ip-range`

**5.** A managed instance group should replace VMs that fail an HTTP health check. What is required?

A. An unmanaged instance group and a snapshot schedule.
B. A health check attached to the managed instance group, and a firewall rule that allows the health check ranges.
C. Cloud Armor on the VPC.
D. OS Login.

**6.** You need the Kubernetes objects running in a regional Autopilot cluster. Which pair of commands?

A. `gcloud container clusters get-credentials` and `kubectl get pods`
B. `gcloud compute instances list` and `gcloud sql instances list`
C. `kubectl` only, with no credentials command, from a new laptop
D. `gcloud run services list`

**7.** Objects older than 90 days should move to Coldline, then delete at 365 days. Where do you configure that?

A. A BigQuery scheduled query.
B. A Cloud Storage lifecycle configuration on the bucket.
C. A snapshot schedule.
D. Nearline as the bucket default class only.

**8.** Which IAM binding follows least privilege for a person who must only view objects in one bucket?

A. `roles/editor` on the project.
B. `roles/storage.objectViewer` on that bucket, granted to a group.
C. `roles/owner` on the organization.
D. A user-managed service account key emailed to the person.

**9.** Cloud Run must reach a Memorystore instance that has only a private IP. What do you add?

A. An authorized network of `0.0.0.0/0` on Memorystore.
B. Direct VPC egress or a Serverless VPC Access connector into the VPC.
C. A public IP on Memorystore.
D. VPC Network Peering to the internet.

**10.** You want a record, in BigQuery, of who changed IAM, kept for years. What do you configure?

A. A log sink of audit logs to BigQuery, and retention on that dataset.
B. Turn on Admin Activity logs. They are off by default.
C. Cloud Trace.
D. A billing budget.

**11.** A GKE deployment must pull a private image. Where should the image live, and what identity needs access?

A. Container Registry, with a JSON key in the pod spec.
B. Artifact Registry, with the node service account or Workload Identity granted `roles/artifactregistry.reader`.
C. Cloud Source Repositories.
D. A public bucket with `allUsers`.

**12.** Which database is the best fit for a regional MySQL 8 application the team will not rewrite, with a standby in another zone?

A. Bigtable.
B. BigQuery.
C. Cloud SQL for MySQL with regional availability.
D. Firestore in Datastore mode.

**13.** You must upload 50 TB from an Amazon S3 bucket every night with retries. Which service?

A. `gcloud compute scp` in a loop.
B. Storage Transfer Service.
C. A snapshot of a Persistent Disk.
D. Cloud CDN.

**14.** How do you send 10% of Cloud Run traffic to a new revision?

A. `gcloud run services update-traffic` with revision percents.
B. Edit `/etc/nginx` on the Cloud Run host.
C. A VPC route with weight 10.
D. Two projects and a DNS weighted round robin only.

**15.** A subnet `10.1.0.0/24` is exhausted. What can you do?

A. Shrink it to `/28` to free space.
B. Expand the prefix length to a smaller number, such as `/23`, if the new range does not overlap.
C. Change the VPC from custom to auto mode to grow it.
D. Enable Cloud NAT, which adds addresses inside the subnet.

**16.** Which product runs a container to completion and then exits, without an HTTP service?

A. Cloud Run jobs.
B. Cloud CDN.
C. A global external Application Load Balancer.
D. Cloud DNS.

**17.** You need guest memory metrics from a Compute Engine VM. What do you install?

A. Nothing. The hypervisor always exports memory percent.
B. The Ops Agent.
C. Binary Authorization.
D. Filestore.

**18.** A service account used by Cloud Build should deploy Cloud Run, and the security policy forbids downloaded keys. What should humans and GitHub use?

A. A JSON key in Secret Manager that every developer downloads.
B. Impersonation or Workload Identity Federation onto that service account.
C. The Owner basic role on the default compute service account.
D. `allUsers` as `roles/run.invoker` and hope.

**19.** Which load balancer preserves the client source IP for UDP?

A. Global external Application Load Balancer.
B. External passthrough Network Load Balancer.
C. Cloud Armor.
D. Identity-Aware Proxy.

**20.** A Dataflow streaming job failed. Where do you confirm status?

A. `gcloud dataflow jobs list` and `gcloud dataflow jobs show`, then the job logs.
B. Cloud DNS.
C. The billing account list.
D. `gcloud sql backups list`.

## Answer key

| # | Answer | Why |
| --- | --- | --- |
| 1 | B | Editors can still create VMs. An organization policy stops the configuration. A firewall does not stop creation of a public IP. |
| 2 | A | Private Google Access covers Google APIs. Cloud NAT covers public internet apt mirrors. |
| 3 | C | Scale to zero, container, no cluster. |
| 4 | B | Global addresses are for global load balancers. VMs take regional addresses. |
| 5 | B | Autohealing is a health check on the MIG. Health check probes must be allowed. |
| 6 | A | `get-credentials` writes the kubeconfig. Then `kubectl`. |
| 7 | B | Lifecycle rules. A default class does not move existing objects by itself. |
| 8 | B | Predefined role, resource-level, group principal. |
| 9 | B | Serverless egress into the VPC. Do not publish Memorystore. |
| 10 | A | Admin Activity is already on. A sink copies it to BigQuery for the retention and SQL you want. |
| 11 | B | Artifact Registry plus a Google identity. No keys in the manifest. |
| 12 | C | Engine match, regional HA. BigQuery is not OLTP. |
| 13 | B | Scheduled, retried, checksummed transfer. |
| 14 | A | Traffic splitting is a Cloud Run feature. There is no VM to SSH to. |
| 15 | B | Subnets only grow. NAT does not enlarge the subnet. |
| 16 | A | Jobs run to completion. Services listen for HTTP. |
| 17 | B | Guest memory needs the agent. |
| 18 | B | Short-lived credentials. |
| 19 | B | Passthrough preserves source IP and supports UDP. Application load balancers terminate HTTP. |
| 20 | A | Job status is a Dataflow command, then logs. |
