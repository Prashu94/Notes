# Traps that change the answer

## Availability

- 99.9% is not a license to design 99.999%.
- A read replica is not high availability. The standby (regional Cloud SQL, or Spanner) is.
- Multi-region storage is not the same as a multi-region relational database.
- Zonal GKE is not a production control plane.

## Identity

- Editor and Owner are the wrong least-privilege answer.
- A JSON key is the wrong credential answer.
- Scopes do not replace IAM. A narrow scope can still deny a call IAM would allow.
- Granting a role on the project is broader than granting it on the bucket or the service account.
- `allUsers` on a bucket is a public data incident, not a convenience.

## Network

- Peering is not transitive.
- Shared VPC and peering solve different problems.
- Private Service Connect is not private services access.
- Private Google Access is not Cloud NAT.
- Cloud Armor does not attach to a passthrough network load balancer.
- Premium tier is required for global anycast load balancers.
- You can expand a subnet. You cannot shrink it.
- The implied ingress rule is deny. The implied egress rule is allow.
- Health checks and IAP have specific source ranges. If you forget them, the feature “does nothing”.

## Data

- BigQuery is not the system of record for a checkout.
- Cloud Storage is not SMB or NFS.
- Local SSD is empty after stop.
- Archive class is slow to pay for, not slow to fetch. Access is milliseconds. Retrieval fees and minimum duration are the cost.
- A lifecycle rule does not by itself version objects. Versioning is separate.
- A budget does not stop spend.
- Bigtable hotspots come from a monotonic row-key prefix.
- Firestore mode is chosen at create time.
- Cloud SQL public IP with `0.0.0.0/0` is never the secure answer.

## Compute and delivery

- Autopilot will not satisfy a stem that needs SSH to nodes or arbitrary DaemonSets.
- Cloud Run has no guest OS to patch.
- App Engine flexible does not scale to zero.
- Spot is for work that can stop.
- Container Registry and Pub/Sub Lite are the wrong recommendations.
- `kubectl apply` from a laptop is not Cloud Deploy.
- Binary Authorization is what blocks an image. Scanning only reports.

## AI

- A prebuilt API beats a custom model when the task is invoices, OCR, or translation and nobody asked to train.
- RAG without a tenant filter leaks data.
- Model Armor is not a VPC firewall.
- Calling Gemini is not the same workload as training on AI Hypercomputer.
- A human-review step in a case study is a requirement. Do not auto-publish.

## Case studies

- Do not migrate a system the PDF says stays.
- Do not add a product the PDF’s cost track would not pay for.
- Do not use a retired company’s name in your reasoning on exam day.
- The PDF on the split screen beats your memory. Look at it.

## Names

- Cloud Run functions and Cloud Functions gen2 are the same family. Gen1 is legacy.
- Sensitive Data Protection is the DLP product. The API may still say `dlp`.
- GKE Enterprise is Anthos.
- Gemini Enterprise Agent Platform is the current name sitting on the Vertex AI platform.
- Looker Studio is Data Studio.
