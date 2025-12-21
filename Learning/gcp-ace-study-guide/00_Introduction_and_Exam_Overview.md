# Google Cloud Associate Cloud Engineer Exam Guide

## 00. Introduction and Exam Overview

### Exam Details

| Aspect | Details |
|--------|---------|
| **Certification** | Associate Cloud Engineer |
| **Duration** | 2 hours |
| **Format** | 50-60 multiple choice / multiple select |
| **Prerequisites** | None (6+ months hands-on recommended) |
| **Validity** | 2 years |
| **Cost** | $125 USD |
| **Languages** | English, Japanese, Spanish, Portuguese, French, German, Indonesian |
| **Delivery** | Test center or online proctored |

### Exam Domain Weightage

| Domain | Weight | Topics |
|--------|--------|--------|
| **Setting up a cloud solution environment** | ~20% | Resource hierarchy, billing, IAM, CLI |
| **Planning and configuring a cloud solution** | ~20% | Compute, storage, network planning |
| **Deploying and implementing** | ~25% | GCE, GKE, App Engine, Cloud Run, data solutions |
| **Ensuring successful operation** | ~20% | Monitoring, logging, ops |
| **Configuring access and security** | ~15% | IAM, service accounts, audit logs |

### Study Guide Structure

| File | Domain | Key Topics |
|------|--------|------------|
| [01_Setting_Up_Environment.md](./01_Setting_Up_Environment.md) | Environment Setup | Hierarchy, billing, gcloud CLI |
| [02_Compute_Services.md](./02_Compute_Services.md) | Compute | GCE, GKE, App Engine, Cloud Run |
| [03_Storage_and_Database_Services.md](./03_Storage_and_Database_Services.md) | Storage/DB | GCS, Cloud SQL, Spanner, Firestore, BigQuery |
| [04_Networking.md](./04_Networking.md) | Networking | VPC, firewalls, load balancing, VPN |
| [05_IAM_and_Security.md](./05_IAM_and_Security.md) | Security | IAM, service accounts, encryption |
| [06_Deploying_and_Implementing.md](./06_Deploying_and_Implementing.md) | Deployment | Terraform, Cloud Build, CI/CD |
| [07_Operations_and_Monitoring.md](./07_Operations_and_Monitoring.md) | Operations | Monitoring, logging, SLI/SLO |

### Key Exam Tips

1. **Know `gcloud` Commands**: The exam heavily tests practical CLI knowledge
2. **Understand IAM Hierarchy**: Permissions flow from Org → Folder → Project → Resource
3. **Service Selection**: Know when to choose GCE vs GKE vs App Engine vs Cloud Run
4. **Database Selection**: Understand use cases for each database service
5. **Networking Concepts**: VPC peering, Shared VPC, firewall rules are heavily tested
6. **Cost Optimization**: Know pricing models (SUD, CUD, Spot VMs)
7. **High Availability**: Understand regional vs zonal resources

### Hands-on Practice Resources

| Resource | Purpose |
|----------|---------|
| **Cloud Skills Boost** | Free labs and quests |
| **Google Cloud Free Tier** | 90-day $300 credit + always-free tier |
| **Official Practice Exam** | Available after scheduling |
| **GCP Architecture Center** | Reference architectures |

### Essential gcloud Commands to Memorize

```bash
# Authentication
gcloud auth login
gcloud auth application-default login

# Configuration
gcloud config set project PROJECT_ID
gcloud config set compute/zone ZONE
gcloud config configurations list

# Compute
gcloud compute instances create/list/describe/delete
gcloud compute ssh INSTANCE_NAME

# GKE
gcloud container clusters create/get-credentials
kubectl get pods/deployments/services

# Storage
gcloud storage buckets create/list
gcloud storage cp SOURCE DESTINATION

# IAM
gcloud projects get-iam-policy PROJECT
gcloud projects add-iam-policy-binding PROJECT --member --role

# Logging/Monitoring
gcloud logging read FILTER
gcloud monitoring dashboards list
```

---
**Next**: [01. Setting Up a Cloud Solution Environment](./01_Setting_Up_Environment.md)
