# Lab 07 — Pub/Sub and a Cloud Run function

## Goal

Topic, gen2 function, publish, see the log.

## Steps

```bash
gcloud services enable cloudfunctions.googleapis.com run.googleapis.com \
  eventarc.googleapis.com pubsub.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com

gcloud pubsub topics create lab-orders
mkdir -p /tmp/lab-fn && cd /tmp/lab-fn
cat > main.py << 'EOF'
import functions_framework

@functions_framework.cloud_event
def handle(event):
    print("got", event.data)
EOF
cat > requirements.txt << 'EOF'
functions-framework==3.8.1
EOF

gcloud functions deploy lab-on-message --gen2 --runtime=python312 \
  --region="$REGION" --source=. --entry-point=handle \
  --trigger-topic=lab-orders

gcloud pubsub topics publish lab-orders --message='{"id":1}'
# Give it half a minute, then:
gcloud functions logs read lab-on-message --gen2 --region="$REGION" --limit=10
```

## Cleanup

```bash
gcloud functions delete lab-on-message --gen2 --region="$REGION" --quiet
gcloud pubsub topics delete lab-orders --quiet
```
