# CI/CD, infrastructure as code, and release

ACE 3.6. PCA 4.1, 5.1, 5.2, 6.3.

## The path a change takes

```
git push
  → Cloud Build (test, build image, scan)
  → Artifact Registry
  → Binary Authorization attestor
  → Cloud Deploy (dev, then stage, then prod, with a strategy)
  → Cloud Run or GKE or a GCE MIG rolling update
```

Terraform is parallel to that, for infrastructure. Do not bake infrastructure changes into a container build. Do not bake application releases into a Terraform apply of the image tag if Cloud Deploy already owns the rollout. One owner per change type.

## Cloud Build

A trigger on a repository runs `cloudbuild.yaml`. Builds run as a service account. Give that account the minimum roles (`artifactregistry.writer`, `logging.logWriter`) and impersonation rights if it must deploy. Private pools when the build must sit on your VPC (private Git, private package mirrors).

```bash
gcloud builds submit --tag ${REGION}-docker.pkg.dev/$PROJECT_ID/apps/web:1 .

# cloudbuild.yaml
# steps:
# - name: 'gcr.io/cloud-builders/docker'
#   args: ['build', '-t', '$_IMAGE', '.']
# images: ['$_IMAGE']

gcloud builds triggers create github \
  --name=web \
  --repo-owner=ORG --repo-name=web \
  --branch-pattern='^main$' \
  --build-config=cloudbuild.yaml \
  --service-account=projects/$PROJECT_ID/serviceAccounts/$SA_EMAIL

gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

Cloud Source Repositories is Google’s hosted git. Many teams use GitHub or GitLab and connect those. **Secure Source Manager** is the hardened option. **Developer Connect** links external repos. The exam accepts “a repository plus a trigger”. It does not require Cloud Source Repositories specifically unless the stem says it.

## Artifact Registry

Docker, Maven, npm, Python, Apt, and other formats. Regional or multi-regional repositories. Cleanup policies delete old images. This replaced Container Registry. If a stem says `gcr.io`, the modern answer is still “move it to Artifact Registry”.

```bash
gcloud artifacts repositories create apps \
  --repository-format=docker --location="$REGION" \
  --description=apps

gcloud artifacts docker images list ${REGION}-docker.pkg.dev/$PROJECT_ID/apps
gcloud auth configure-docker ${REGION}-docker.pkg.dev
docker push ${REGION}-docker.pkg.dev/$PROJECT_ID/apps/web:1
```

## Cloud Deploy

A **delivery pipeline** has stages (dev, prod). A **target** is a GKE cluster or a Cloud Run service. A **release** is a set of rendered manifests. Strategies: standard (rolling), canary, and verify jobs. Rollback promotes the previous release again.

```bash
gcloud deploy apply --file=clouddeploy.yaml --region="$REGION"
gcloud deploy releases create rel-1 \
  --delivery-pipeline=web --region="$REGION" \
  --images=web=${REGION}-docker.pkg.dev/$PROJECT_ID/apps/web:1
gcloud deploy rollouts list --delivery-pipeline=web --release=rel-1 --region="$REGION"
gcloud deploy releases promote --release=rel-1 --delivery-pipeline=web \
  --region="$REGION" --to-target=prod
```

This is the PCA “deployment and release management” answer for Kubernetes and Cloud Run. A laptop is not a release process. App Engine traffic splitting is the legacy equivalent for App Engine apps.

## Terraform and friends

```bash
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

- Remote state in Cloud Storage, versioning on, least privilege on the bucket.
- Separate state per environment. Do not one-apply dev and prod.
- **Infrastructure Manager** runs Terraform with a Google Cloud API, locks, and a service account. Use it when the stem wants Terraform without a self-hosted runner.
- **Config Connector** is for teams that want Google Cloud resources declared next to Kubernetes manifests.
- **Helm** renders Kubernetes charts. It is not a Google Cloud provisioner.
- **Cloud Foundation Toolkit** modules are a starting point for folders, projects, VPCs, and IAM. They are not mandatory.
- **Deployment Manager** is legacy. Do not choose it for a new design.
- Policy as code: organization policies, Policy Controller, and `terraform plan` in the pipeline. A service catalog (Service Catalog, or a Terraform module registry) is how you let teams provision an approved pattern. PCA 4.1 names service catalog and provisioning.

## Testing the exam names

| Test | What it proves |
| --- | --- |
| Unit | A function, no cloud |
| Integration | The service plus emulators or a sandbox project |
| Load | Latency and saturation against an SLO. PCA 6.6. |
| Infrastructure | `terraform plan` reviewed, plus an apply in a scratch project |
| Penetration | Authorized attack to find holes. Not something you run against production without a scope. |
| Chaos | Kill a zone or a dependency on purpose. Match the failure mode you claim to survive. |

Load testing tools are not prescribed. The answer is “run a load test and read Cloud Monitoring and Cloud Profiler”, not a vendor name, unless the stem names one.

## GitOps

Config Sync (GKE Enterprise) pulls manifests from git and rejects drift. That is the answer when many clusters must match git. Cloud Deploy pushes a release. Both are valid. The stem’s “pull from git” versus “promote a pipeline” wording tells you which.

## Exercises

1. Name the registry you push to, and the product that blocks an unsigned image.
2. Dev must auto-deploy and prod must require approval. Which product models stages?
3. A build must reach a private Git server on the VPC. Which Cloud Build feature?
4. Two people run `terraform apply` from laptops against one state file. What do you change?

### Answers

1. Artifact Registry, and Binary Authorization.
2. Cloud Deploy, with an approval on the prod stage.
3. A private pool peered to the VPC.
4. Remote state in Cloud Storage with locking, and a pipeline that applies. Stop applying from laptops.
