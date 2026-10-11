# Lab 03 — Instance template and regional MIG

## Goal

Template, regional managed instance group, health check, snapshot of a disk.

This lab creates two e2-micro VMs. Delete them the same day.

## Steps

```bash
gcloud compute instance-templates create lab-tpl \
  --machine-type=e2-micro \
  --image-family=debian-12 --image-project=debian-cloud \
  --tags=lab-web

gcloud compute health-checks create http lab-hc --port=80

gcloud compute instance-groups managed create lab-mig \
  --region="$REGION" --template=lab-tpl --size=2 \
  --zones="${REGION}-a,${REGION}-b"

gcloud compute instance-groups managed set-autoscaling lab-mig \
  --region="$REGION" --min-num-replicas=2 --max-num-replicas=4 \
  --target-cpu-utilization=0.8

gcloud compute instance-groups managed list-instances lab-mig --region="$REGION"

# Snapshot the boot disk of one instance. The disk name often matches the instance.
INSTANCE=$(gcloud compute instance-groups managed list-instances lab-mig \
  --region="$REGION" --format="value(instance)" | head -1)
# INSTANCE is a URL. Take the last path segment as the name, then snapshot in its zone.
echo "$INSTANCE"
```

Create a snapshot once you know the disk name and zone from `gcloud compute instances list`:

```bash
gcloud compute disks snapshot DISK_NAME --zone=ZONE --snapshot-names=lab-snap
gcloud compute snapshots describe lab-snap
```

## Cleanup

```bash
gcloud compute instance-groups managed delete lab-mig --region="$REGION" --quiet
gcloud compute instance-templates delete lab-tpl --quiet
gcloud compute health-checks delete lab-hc --quiet
gcloud compute snapshots delete lab-snap --quiet
```
