# Labs

Run these in a project you can delete. Set a budget alert first. Delete every resource at the end of the lab. Commands assume:

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export ZONE="us-central1-a"
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"
gcloud config set compute/zone "$ZONE"
```

| Lab | You practice | Delete when done |
| --- | --- | --- |
| [01](lab-01-project-iam-billing.md) | Project, API, IAM, service account impersonation | Bindings and the service account |
| [02](lab-02-vpc-nat-firewall.md) | Custom VPC, subnet, firewall, NAT, static IP | Network and addresses |
| [03](lab-03-compute-mig.md) | Template, regional MIG, snapshot | MIG, template, snapshots, disks |
| [04](lab-04-gke-autopilot.md) | Autopilot, Deployment, Artifact Registry pull | Cluster and repository |
| [05](lab-05-cloud-run.md) | Deploy, traffic split, private invoke | Service |
| [06](lab-06-storage-bigquery.md) | Bucket lifecycle, load, partitioned table | Bucket and dataset |
| [07](lab-07-pubsub-function.md) | Topic, gen2 function, message | Topic, function |
| [08](lab-08-logging-sink.md) | Log read, sink, metric | Sink and metric |
| [09](lab-09-cloudsql-private.md) | Private services access and a private Cloud SQL instance. **Costs money. Skip if you are watching spend.** | Instance and the peering range |
| [10](lab-10-terraform.md) | One bucket via Terraform | Bucket and state |

Labs 04 and 09 are the expensive ones. Autopilot bills for the pods you run. Cloud SQL bills until you delete the instance, not until you stop it.
