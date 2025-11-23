# Google Cloud Load Balancing & Autoscaling Guide for ACE Certification

This guide covers the operational tasks for setting up Load Balancers and Autoscaling, a key requirement for the **Associate Cloud Engineer (ACE)** exam.

## 1. Managed Instance Groups (MIGs)

Load balancers distribute traffic to backends, typically Managed Instance Groups.

### 1.1 Creating an Instance Template
Defines the VM configuration (machine type, image, startup script).

```bash
gcloud compute instance-templates create my-web-template \
    --machine-type=e2-micro \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --tags=http-server \
    --metadata=startup-script='#! /bin/bash
apt-get update
apt-get install -y apache2
echo "Hello from $(hostname)" > /var/www/html/index.html'
```

### 1.2 Creating a Managed Instance Group
Uses the template to create a group of identical VMs.

```bash
gcloud compute instance-groups managed create my-web-mig \
    --template=my-web-template \
    --size=2 \
    --zone=us-central1-a
```

### 1.3 Configuring Autoscaling
Automatically adds/removes VMs based on load (CPU, LB utilization).

```bash
gcloud compute instance-groups managed set-autoscaling my-web-mig \
    --zone=us-central1-a \
    --max-num-replicas=10 \
    --min-num-replicas=2 \
    --target-cpu-utilization=0.60
```

## 2. HTTP(S) Load Balancing (Layer 7)

Used for web applications (HTTP/HTTPS). Global scope.

### 2.1 Components
1.  **Health Check**: Checks if backends are alive.
2.  **Backend Service**: Groups MIGs and defines distribution mode.
3.  **URL Map**: Routes requests based on Host/Path.
4.  **Target Proxy**: Terminates connections (HTTP or HTTPS).
5.  **Forwarding Rule**: The frontend IP and port.

### 2.2 Setup Steps

**1. Create Health Check:**
```bash
gcloud compute health-checks create http my-http-health-check \
    --port=80
```

**2. Create Backend Service:**
```bash
gcloud compute backend-services create my-web-backend \
    --protocol=HTTP \
    --health-checks=my-http-health-check \
    --global
```

**3. Add MIG to Backend Service:**
```bash
gcloud compute backend-services add-backend my-web-backend \
    --instance-group=my-web-mig \
    --instance-group-zone=us-central1-a \
    --global
```

**4. Create URL Map:**
```bash
gcloud compute url-maps create my-web-map \
    --default-service=my-web-backend
```

**5. Create Target HTTP Proxy:**
```bash
gcloud compute target-http-proxies create my-http-proxy \
    --url-map=my-web-map
```

**6. Create Global Forwarding Rule:**
```bash
gcloud compute forwarding-rules create my-http-rule \
    --target-http-proxy=my-http-proxy \
    --ports=80 \
    --global
```

## 3. Network Load Balancing (Layer 4)

Used for non-HTTP traffic (TCP/UDP) or when you need to preserve Client IP.

### 3.1 External Passthrough Network Load Balancer
*   **Regional**.
*   **Preserves Client IP**.
*   **Protocols**: TCP, UDP, ESP, ICMP.

**Setup Steps:**

**1. Create Health Check (TCP):**
```bash
gcloud compute health-checks create tcp my-tcp-health-check \
    --port=80
```

**2. Create Backend Service (Regional):**
```bash
gcloud compute backend-services create my-tcp-backend \
    --protocol=TCP \
    --region=us-central1 \
    --health-checks=my-tcp-health-check
```

**3. Add MIG to Backend Service:**
```bash
gcloud compute backend-services add-backend my-tcp-backend \
    --instance-group=my-web-mig \
    --instance-group-zone=us-central1-a \
    --region=us-central1
```

**4. Create Forwarding Rule:**
```bash
gcloud compute forwarding-rules create my-tcp-rule \
    --region=us-central1 \
    --ports=80 \
    --backend-service=my-tcp-backend
```

## 4. Internal Load Balancing

Distributes traffic from clients *inside* the VPC.

*   **Internal HTTP(S)**: Layer 7, Regional (Envoy-based).
*   **Internal TCP/UDP**: Layer 4, Regional (Andromeda-based).

**Key Difference in Command:**
Add `--load-balancing-scheme=INTERNAL` (for L4) or `--load-balancing-scheme=INTERNAL_MANAGED` (for L7) when creating the forwarding rule/backend service.

## 5. Cloud Armor (Security)

Protects External HTTP(S) Load Balancers from DDoS and web attacks.

**Create Security Policy:**
```bash
gcloud compute security-policies create my-security-policy \
    --description="Block bad IPs"
```

**Add Rule to Block IP:**
```bash
gcloud compute security-policies rules create 1000 \
    --security-policy=my-security-policy \
    --action=deny-403 \
    --src-ip-ranges=1.2.3.4/32
```

**Attach to Backend Service:**
```bash
gcloud compute backend-services update my-web-backend \
    --security-policy=my-security-policy \
    --global
```
