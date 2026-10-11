# Lab 05 — Cloud Run traffic split

## Goal

Deploy two revisions of a tiny service and send 10% of traffic to the new one. Then invoke it.

Cloud Shell has Python and the gcloud run integration.

## Steps

```bash
gcloud services enable run.googleapis.com
mkdir -p /tmp/lab-run && cd /tmp/lab-run
cat > main.py << 'EOF'
import os
from flask import Flask
app = Flask(__name__)

@app.get("/")
def root():
    return os.environ.get("VERSION", "unknown")
EOF
cat > requirements.txt << 'EOF'
flask==3.0.3
gunicorn==22.0.0
EOF
cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD exec gunicorn --bind :$PORT --workers 1 main:app
EOF

gcloud run deploy lab-web --source=. --region="$REGION" \
  --allow-unauthenticated --set-env-vars=VERSION=one

gcloud run deploy lab-web --source=. --region="$REGION" \
  --set-env-vars=VERSION=two --no-traffic

REV=$(gcloud run revisions list --service=lab-web --region="$REGION" \
  --format="value(metadata.name)" --sort-by="~metadata.creationTimestamp" | head -1)
PREV=$(gcloud run revisions list --service=lab-web --region="$REGION" \
  --format="value(metadata.name)" --sort-by="~metadata.creationTimestamp" | sed -n '2p')

gcloud run services update-traffic lab-web --region="$REGION" \
  --to-revisions="${REV}=10,${PREV}=90"

URL=$(gcloud run services describe lab-web --region="$REGION" --format='value(status.url)')
for i in 1 2 3 4 5 6 7 8 9 10; do curl -s "$URL"; echo; done
```

You should see mostly `one` and an occasional `two`.

## Cleanup

```bash
gcloud run services delete lab-web --region="$REGION" --quiet
```
