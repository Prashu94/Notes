# Lab 01 — Project, IAM, impersonation

## Goal

Enable an API, grant a group role if you have a group, create a service account, impersonate it, and confirm you did not create a key.

## Steps

```bash
gcloud services enable storage.googleapis.com iam.googleapis.com

gcloud iam service-accounts create lab-runner --display-name="Lab runner"
SA="lab-runner@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA}" \
  --role="roles/storage.objectViewer"

gcloud iam service-accounts add-iam-policy-binding "$SA" \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/iam.serviceAccountTokenCreator"

gcloud auth print-access-token --impersonate-service-account="$SA" >/dev/null
echo "impersonation worked"

gcloud iam service-accounts keys list --iam-account="$SA"
# Expect no user-managed keys.
```

If you have a group:

```bash
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="group:YOUR_GROUP" \
  --role="roles/viewer"
```

## Check

`gcloud projects get-iam-policy $PROJECT_ID` shows the binding. The key list is empty.

## Cleanup

```bash
gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA}" --role="roles/storage.objectViewer"
gcloud iam service-accounts delete "$SA"
```
