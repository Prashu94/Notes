# Lab 04 — Autopilot and a Deployment

## Goal

Regional Autopilot cluster, credentials, a Deployment, a ClusterIP Service. Delete the cluster when you finish. This is the costly lab.

## Steps

```bash
gcloud services enable container.googleapis.com artifactregistry.googleapis.com
gcloud container clusters create-auto lab-gke --region="$REGION"
gcloud container clusters get-credentials lab-gke --region="$REGION"

kubectl create deployment hello --image=us-docker.pkg.dev/google-samples/containers/gke/hello-app:1.0
kubectl expose deployment hello --port=80 --target-port=8080
kubectl get pods,svc
kubectl scale deployment hello --replicas=2
kubectl autoscale deployment hello --min=2 --max=4 --cpu-percent=70
kubectl get hpa
```

## Cleanup

```bash
gcloud container clusters delete lab-gke --region="$REGION" --quiet
```
