# Lab 02 — VPC, firewall, NAT, address

## Goal

Custom-mode VPC, a subnet with Private Google Access, an IAP SSH firewall, Cloud NAT, and a reserved address. No default-network habits.

## Steps

```bash
gcloud services enable compute.googleapis.com

gcloud compute networks create lab-vpc --subnet-mode=custom --bgp-routing-mode=regional

gcloud compute networks subnets create lab-app \
  --network=lab-vpc --region="$REGION" --range=10.50.0.0/24 \
  --enable-private-ip-google-access

gcloud compute firewall-rules create lab-iap-ssh \
  --network=lab-vpc --direction=INGRESS --action=ALLOW \
  --rules=tcp:22 --source-ranges=35.235.240.0/20 \
  --target-tags=lab

gcloud compute routers create lab-rtr --network=lab-vpc --region="$REGION"
gcloud compute routers nats create lab-nat \
  --router=lab-rtr --region="$REGION" \
  --auto-allocate-nat-external-ips --nat-all-subnet-ip-ranges

gcloud compute addresses create lab-ip --region="$REGION"

gcloud compute instances create lab-vm \
  --zone="$ZONE" --machine-type=e2-micro \
  --network=lab-vpc --subnet=lab-app --no-address \
  --tags=lab \
  --image-family=debian-12 --image-project=debian-cloud \
  --metadata=enable-oslogin=TRUE
```

Your user needs `roles/iap.tunnelResourceAccessor` and OS Login. Then:

```bash
gcloud compute ssh lab-vm --zone="$ZONE" --tunnel-through-iap
```

Inside the VM, `curl -I https://storage.googleapis.com` should work because of Private Google Access. `apt-get update` should work because of Cloud NAT. There is no public IP (`--no-address`).

## Cleanup

```bash
gcloud compute instances delete lab-vm --zone="$ZONE" --quiet
gcloud compute addresses delete lab-ip --region="$REGION" --quiet
gcloud compute routers nats delete lab-nat --router=lab-rtr --region="$REGION" --quiet
gcloud compute routers delete lab-rtr --region="$REGION" --quiet
gcloud compute firewall-rules delete lab-iap-ssh --quiet
gcloud compute networks subnets delete lab-app --region="$REGION" --quiet
gcloud compute networks delete lab-vpc --quiet
```
