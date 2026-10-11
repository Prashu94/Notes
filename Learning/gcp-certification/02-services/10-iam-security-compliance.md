# Security, keys, compliance, and supply chain

ACE section 5 is IAM and service accounts, already in the foundations chapter. This chapter is the rest of the security catalog, which PCA section 3 scores directly.

## Encryption

| Situation | What you say |
| --- | --- |
| Default | Google-managed encryption at rest. Already on for Google Cloud storage products. |
| You want to control key rotation, disable a key, or separate key admins from data admins | CMEK with Cloud KMS |
| You need FIPS HSM-backed keys | Cloud HSM (a KMS protection level) |
| You supply raw key material per request and Google does not store it | CSEK. Rare. Operationally painful. |
| Data in use, memory encrypted | Confidential Computing (Confidential VM, Confidential GKE nodes) |
| You must destroy data by destroying the key | CMEK, and you accept that this is a blunt instrument |

```bash
gcloud kms keyrings create app --location="$REGION"
gcloud kms keys create data \
  --keyring=app --location="$REGION" \
  --purpose=encryption --rotation-period=90d \
  --next-rotation-time=2026-12-01T00:00:00Z

# Let the Cloud Storage service agent use the key. The agent email is per project.
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
gcloud kms keys add-iam-policy-binding data \
  --keyring=app --location="$REGION" \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gs-project-accounts.iam.gserviceaccount.com" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

gcloud storage buckets update gs://$PROJECT_ID-lake \
  --default-encryption-key=projects/$PROJECT_ID/locations/$REGION/keyRings/app/cryptoKeys/data
```

Separation of duties: `roles/cloudkms.admin` does not need to be combined with the encrypter role. Key admins manage keys. Workload service accounts encrypt and decrypt.

**Secret Manager** stores passwords, API tokens, and certificates. It is not a KMS key. KMS encrypts. Secret Manager holds the secret value and versions it.

```bash
printf '%s' 's3cr3t' | gcloud secrets create db-password --data-file=-
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets versions access latest --secret=db-password
```

Cloud Run and GKE can mount secrets. Do not put them in the image or in git.

## Network and access controls PCA names

| Control | Job |
| --- | --- |
| IAM | Who can call which API |
| Resource hierarchy | Where that IAM and policy attach |
| Organization policy | What configurations are legal |
| VPC Service Controls | API perimeter so data cannot be copied to an outside project |
| Access Context Manager | Conditions (IP, device, identity) used by VPC-SC and IAP. Context-aware access. |
| Hierarchical firewall policy | Network deny the project cannot override |
| IAP | Identity on HTTPS or on TCP (SSH/RDP) without a public IP or a VPN |
| Chrome Enterprise Premium | Beyondcorp-style zero trust for users and devices. The exam lists it next to IAP. |
| Workload Identity Federation | External identities (AWS, Azure, GitHub) become short-lived Google credentials. No JSON keys. |
| Service account impersonation | A principal mints short-lived tokens for a service account |
| Certificate Authority Service | Private CA |
| Certificate Manager | TLS certs for load balancers |

IAP for SSH:

```bash
gcloud compute firewall-rules create allow-iap-ssh \
  --network=prod --direction=INGRESS --action=ALLOW \
  --rules=tcp:22 --source-ranges=35.235.240.0/20

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="group:sre@example.com" --role="roles/iap.tunnelResourceAccessor"

gcloud compute ssh web-1 --zone="$ZONE" --tunnel-through-iap
```

VPC Service Controls: create a perimeter, add projects, restrict services such as `storage.googleapis.com` and `bigquery.googleapis.com`. Ingress and egress rules allow the few paths you need (Cloud Build, a specific function). A perimeter breach shows up in audit logs. IAM can still be correct and the call fails because of the perimeter. That is intentional.

## Detect and respond

| Product | Job |
| --- | --- |
| Security Command Center | Posture, misconfigurations, vulnerability findings, threat detection. Standard and Premium tiers. Premium adds more detectors and compliance views. |
| Google Security Operations (Chronicle) | Security analytics and hunting at scale. SCC can export toward it. |
| Advisory Notifications | Tell security contacts about important risks |
| Web Security Scanner | Scan App Engine, GKE, and Compute Engine web apps for common bugs |
| Sensitive Data Protection | Find and de-identify PII (the product formerly called DLP) |
| Model Armor | Inspect prompts and responses for the AI threats the exam names (prompt injection, and related abuse). PCA “securing AI”. |
| reCAPTCHA / Fraud Defense | Bot and fraud. Recognition. |
| Binary Authorization | Only signed images deploy to GKE or Cloud Run |
| Artifact Analysis / vulnerability scanning | Scan images in Artifact Registry |
| Assured Open Source Software | Known-good open-source builds. Supply chain. |

```bash
# Sensitive Data Protection inspect template is API-heavy.
# The recognition task: inspect content or a BigQuery table or a Cloud Storage bucket,
# then de-identify with masking or tokenization before the data reaches a model or a broad analyst group.
gcloud services enable dlp.googleapis.com
```

The API is still often `dlp.googleapis.com` even though the product name is Sensitive Data Protection. Exam answers use the product name. Commands may use `dlp`.

Securing AI, as the exam lists it:

- Do not train on regulated data that has not been through Sensitive Data Protection or an approved dataset.
- Deploy models with IAM, VPC-SC, CMEK, and a private endpoint where the product supports it.
- Put Model Armor on the prompt path for user-facing agents.
- Log prompts in a controlled dataset, not in an open log bucket, if they can contain PII.

## Compliance

| Requirement in the stem | What you actually do |
| --- | --- |
| Health data, BAA | Use services covered by the BAA, CMEK where required, VPC-SC, audit logs, Access Transparency for Google support access |
| Cardholder data | Reduce scope. Tokenize with a vault or Sensitive Data Protection. Segment the network. Do not log PANs. |
| Data residency / sovereignty | Organization policy on resource locations, regional services, Assured Workloads for controlled environments (EU, and other regimes the product supports) |
| Children’s privacy | Data minimization, consent, short retention. Product choice does not replace that. |
| SOC 2 | Access Transparency, audit log export, SCC compliance reports, change management. The certification is about your controls plus Google’s reports. |
| Who at Google accessed this | Access Transparency logs, Access Approval if you want to approve support access |
| Asset list for an audit | Cloud Asset Inventory |

```bash
gcloud asset search-all-resources --scope=projects/$PROJECT_ID --query="name:web-1"
gcloud asset export --content-type=resource \
  --project="$PROJECT_ID" \
  --output-path=gs://$PROJECT_ID-lake/asset/resources.json
```

Assured Workloads creates a folder with the right org policies and personnel controls for a regime. It is the PCA answer when the stem says a regulated folder, not a normal project with a wiki.

## Supply chain

1. Source in a real git host (GitHub, GitLab, Secure Source Manager, or Cloud Source Repositories).
2. Cloud Build builds it. Store the provenance.
3. Artifact Registry holds the image. On-demand scanning or Artifact Analysis finds CVEs.
4. Binary Authorization requires an attestor before GKE or Cloud Run deploys.
5. Deploy with Cloud Deploy, not a laptop `kubectl apply` to production.

```bash
gcloud artifacts repositories create apps \
  --repository-format=docker --location="$REGION"
gcloud artifacts docker images scan ${REGION}-docker.pkg.dev/$PROJECT_ID/apps/web:1
gcloud artifacts docker images list-vulnerabilities \
  ${REGION}-docker.pkg.dev/$PROJECT_ID/apps/web:1
```

## Exercises

1. Disks are already encrypted. The security team wants to disable a key and revoke data. Which product?
2. GitHub Actions must deploy without a JSON key. Which mechanism?
3. Analysts in another project must not `bq extract` a table to their personal bucket. IAM already limits them, and the stem still worries about a stolen credential. What perimeter?
4. A public chatbot must reject prompt-injection attempts and must not echo national ID numbers. Which two products?
5. Only images signed by the release team may reach production GKE. Which product?

### Answers

1. Cloud KMS CMEK. Google-managed encryption does not give them a key to disable.
2. Workload Identity Federation.
3. VPC Service Controls around the projects and `bigquery.googleapis.com`.
4. Model Armor on the prompt and response path, and Sensitive Data Protection to detect and mask identifiers.
5. Binary Authorization with an attestor. Artifact Analysis finds CVEs but does not by itself block an unsigned deploy.
