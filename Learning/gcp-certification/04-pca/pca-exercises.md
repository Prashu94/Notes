# PCA exercises

Scenario practice. Write the design in six lines (compute, data, network, security, operations, what you rejected) before you read the sample.

## 1. Bank batch

A bank runs a nightly risk batch that can restart from the last checkpoint. It is a container. It must not run on shared Kubernetes with the public website. Data stays in the EU. About 40 TB of input sits in Cloud Storage and the output is a BigQuery table. Staff of two.

Sample: Cloud Run jobs or Batch in an EU region, private, service account with bucket read and BigQuery write, VPC-SC if the rest of the estate uses it, Cloud Scheduler or Workflows to start it, Spot or the job’s retry for cost. Reject a multi-tenant GKE cluster with the website, and reject a always-on GPU VM.

## 2. Global ledger

A payments ledger must take writes in the US and Europe with strong consistency. Availability target in the stem is 99.999%. The schema can change. The team has three years.

Sample: Spanner multi-region. Application on GKE or Cloud Run in both regions behind a global external Application Load Balancer. CMEK, private endpoint, audit logs. Reject Cloud SQL with a cross-region read replica (replicas are not strongly consistent writers).

## 3. Factory files

Windows apps must keep using SMB. The factory has a 10 Gbps circuit they can bring to a colocation. Identity is Active Directory.

Sample: NetApp Volumes for SMB, Dedicated Interconnect, Managed Microsoft AD or AD federation, DNS forwarding. Reject Cloud Storage signed URLs, because the apps will not change this year. Reject HA VPN as the only path if they already have the circuit and the bandwidth.

## 4. Model canary

A fraud model is in production. The next version should take 5% of calls and roll back if precision drops. Prompts are not the interface. Calls are JSON features. Features include account numbers.

Sample: Agent Platform endpoint traffic split, Model Monitoring or a custom metric on precision, Sensitive Data Protection or tokenization before training, IAM on the endpoint, private endpoint. Reject shipping the model inside the web container with no split.

## 5. Missed pages

The on-call inbox has 400 unread alert emails. CPU alerts fire all day. Two real outages were a full disk and a bad release. The business wants fewer pages and safer releases.

Sample: Delete CPU-only paging. SLO burn alerts to a real channel. Disk-usage alert. Cloud Deploy canary. Error budget policy. This is operational excellence, not a new database.

## 6. Partner API

A partner calls one inventory API. They must not reach the rest of the VPC. You must not learn their internal subnets. Calls need a quota and an API key.

Sample: Private Service Connect for the private path, or a public Apigee endpoint if they are on the internet. Apigee for the key and quota. Reject VPC peering, which shares route tables and is not an API product.

## 7. Science cluster that is really VMware

The admin team will only operate vCenter. The CFO asked for “Kubernetes everywhere” in a slide. The applications are OVA images.

Sample: VMware Engine now. A later wave for anything they choose to containerize. Reject a forced GKE migration in the same change window as the data center exit.

## 8. Lake that became a swamp

Analysts copy CSVs to their laptops. Nobody knows which table is official. The warehouse is BigQuery.

Sample: Dataplex or an authorized-view layer, a curated dataset, IAM that removes raw export, Analytics Hub for sharing, column-level security. Reject another warehouse.

## 9. Sustainability slide

The board wants lower carbon. The latency budget for the checkout database is 5 ms inside `europe-west1`. A teammate proposes moving it to a distant lower-carbon region.

Sample: Keep the database where the latency budget is met. Improve utilization (right-size, autoscaling, scale to zero on the web tier). Use Carbon Footprint to measure. Sustainability does not beat a written latency requirement.

## 10. Supply chain

A regulator asked how you know production images were not tampered with. Builds currently run on a developer laptop.

Sample: Cloud Build from git, Artifact Registry, vulnerability scanning, Binary Authorization with an attestor, Cloud Deploy. Reject a PDF policy with no technical control.
