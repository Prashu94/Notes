# PCA practice exam

Fifteen original scenario questions. There is no official passing score. Aim to explain the wrong options, not only to guess the letter. About 30 minutes.

## Questions

**1.** A case study prints 99.9% for customer-facing systems in one country and says a legacy partner interface must stay in a colocation. Which design fits?

A. Multi-region Spanner and a cutover of the partner interface next week.
B. Regional GKE or Cloud Run, Cloud SQL HA, and HA VPN or Interconnect to the partner that stays.
C. One zonal VM and a nightly snapshot.
D. BigQuery as the system of record for the transactions.

**2.** You must choose a network path for a service another company will call. Neither side should learn the other’s subnets. Which technology?

A. VPC Network Peering.
B. Shared VPC.
C. Private Service Connect.
D. A public IP on the database.

**3.** The security review asks for customer-managed keys on a bucket and a way to store the database password for Cloud Run. Which pair?

A. Cloud KMS CMEK, and Secret Manager.
B. Secret Manager for both the key and the disk encryption.
C. A JSON file in the image.
D. Default encryption only, because CMEK disables Google encryption.

**4.** A container platform team wants node patches, DaemonSets, and SSH. A different team wants no node management. Which GKE modes match?

A. Both should use Autopilot.
B. Standard for the first team, Autopilot for the second.
C. App Engine flexible for both.
D. Cloud Run for the DaemonSet team.

**5.** Analysts run `SELECT *` on a 20 TB table and filter `event_date` in the application. The bill is mostly BigQuery. What do you change first?

A. Move the table to Cloud SQL.
B. Partition by `event_date`, cluster on the next filter, and select only needed columns.
C. Turn on Cloud CDN in front of BigQuery.
D. Export to CSV every hour.

**6.** A chatbot answers from customer documents. One customer saw another customer’s contract in an answer. What failed?

A. The Gemini model was too small.
B. Retrieval had no authorization filter on tenant.
C. Cloud CDN cached the HTML.
D. The VPC was custom mode.

**7.** GitHub Actions deploys with a key file. The PCA security objective wants that pattern gone. What replaces it?

A. Workload Identity Federation to a service account.
B. A longer-lived key, rotated yearly.
C. `roles/owner` on the GitHub bot user.
D. Embedding the key in Secret Manager and printing it in logs.

**8.** Which release design matches operational excellence for a GKE checkout service?

A. `kubectl apply` from a laptop on Friday.
B. Cloud Deploy canary, metrics checked, automatic or one-click rollback.
C. A zonal cluster and a spreadsheet.
D. Editing the running container with `kubectl exec`.

**9.** A Windows file share must remain SMB. Which store?

A. Cloud Storage.
B. Firestore.
C. NetApp Volumes.
D. Bigtable.

**10.** Large model training was specified, with GPUs and a need to reserve capacity. Which exam term fits the platform?

A. Cloud Scheduler.
B. AI Hypercomputer.
C. Looker Studio.
D. Cloud DNS.

**11.** You need API keys, a developer portal, and quotas for partners. Which product does the exam guide name for API management?

A. Apigee.
B. Cloud Tasks.
C. VPC firewall rules.
D. Filestore.

**12.** An architecture diagram shows Cloud SQL with a public IP and authorized networks `0.0.0.0/0`, “temporary”. The data is health records. What do you require before go-live?

A. Leave it, if IAM is correct.
B. Private IP, no authorized network of the world, VPC-SC or equivalent perimeter, audit logs.
C. A larger machine type.
D. Cloud CDN.

**13.** Two regions must both accept ledger writes with strong consistency. Which database configuration?

A. Cloud SQL primary plus a cross-region read replica.
B. Firestore with a cache.
C. Spanner in a multi-region configuration.
D. BigQuery streaming inserts.

**14.** The board asks which pillar a “delete idle VMs and prefer autoscaling” decision serves, after reliability is already met.

A. Only security.
B. Cost optimization, and often sustainability through higher utilization.
C. It has no pillar. It is only finance.
D. Operational excellence only, because cost is not in the framework.

**15.** A migration plan for 200 VMs with unknown dependencies should start with which named product?

A. A manual spreadsheet only.
B. Google Cloud Migration Center discovery, then waves, with Migrate to Virtual Machines for the rehost wave.
C. Spanner migration for every VM.
D. Transfer Appliance for the RAM of each VM.

## Answer key

| # | Answer | Why |
| --- | --- | --- |
| 1 | B | Match the printed availability and do not move what must stay. |
| 2 | C | Peering exchanges routes. Shared VPC is for one organization. |
| 3 | A | KMS holds keys. Secret Manager holds the password. |
| 4 | B | Mode follows the operational requirement. |
| 5 | B | Prune bytes scanned. CDN does not sit in front of query jobs. |
| 6 | B | RAG without a tenant filter is a data leak. |
| 7 | A | Short-lived federation. Keys are the anti-pattern. |
| 8 | B | Section 6 wants a release process and a rollback. |
| 9 | C | SMB is a file protocol. Objects are not SMB. |
| 10 | B | The exam guide’s term for large GPU/TPU training. |
| 11 | A | Section 5.1 names Apigee. |
| 12 | B | Public databases fail a health-data design. |
| 13 | C | Read replicas do not take strongly consistent writes. |
| 14 | B | Cost is a pillar. Sustainability follows if utilization improves. Reliability was already met, so this is not an availability change. |
| 15 | B | Section 1.4 names Migration Center. |
