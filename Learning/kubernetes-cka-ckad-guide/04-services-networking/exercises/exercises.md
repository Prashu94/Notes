# Module 04: Services & Networking - Exercises

## Instructions

These exercises are designed to test your understanding of Kubernetes Services, Ingress, and Network Policies. Each exercise includes:
- **Objective**: What you need to accomplish
- **Requirements**: Specific criteria to meet
- **Hints**: Guidance if you get stuck

Work through these exercises in order. Solutions are provided in `solutions.md`.

---

## Exercise 1: Create ClusterIP Service

**Objective**: Create a deployment and expose it with a ClusterIP service.

**Requirements**:
1. Create a deployment named `webapp` with 3 replicas using the `nginx:alpine` image
2. The deployment should have the label `app=webapp` and `tier=frontend`
3. Create a ClusterIP service named `webapp-service` that:
   - Exposes port 80
   - Forwards traffic to container port 80
   - Uses the correct selector to target the deployment
4. Test the service from within the cluster

**Hints**:
- Use `kubectl expose` or create a YAML manifest
- Test with `kubectl run` to create a temporary pod

---

## Exercise 2: NodePort Service for External Access

**Objective**: Expose an application using a NodePort service.

**Requirements**:
1. Create a deployment named `external-app` with 2 replicas using `hashicorp/http-echo` image
   - Container should run with args: `["-text=Hello from NodePort"]`
   - Container port: 5678
2. Create a NodePort service that:
   - Exposes port 8080
   - Forwards to container port 5678
   - Uses NodePort 30100
   - Name: `external-app-nodeport`
3. Access the application from outside the cluster using a node IP

**Hints**:
- Use `kubectl get nodes -o wide` to find node IPs
- Test with `curl http://<node-ip>:30100`

---

## Exercise 3: Multi-Port Service

**Objective**: Create a service that exposes multiple ports.

**Requirements**:
1. Create a deployment named `api-gateway` with the `nginx` image
2. Create a service that exposes three ports:
   - Port 80 → targetPort 80 (HTTP)
   - Port 443 → targetPort 443 (HTTPS)
   - Port 9090 → targetPort 9090 (Metrics)
3. All ports should have meaningful names
4. Verify endpoints are created correctly

**Hints**:
- Use named ports in the service definition
- Check endpoints with `kubectl get endpoints`

---

## Exercise 4: Headless Service for StatefulSet

**Objective**: Create a headless service for direct pod access.

**Requirements**:
1. Create a headless service named `mysql-headless`:
   - ClusterIP: None
   - Port: 3306
   - Selector: `app=mysql`
2. Create a simple StatefulSet named `mysql` with 3 replicas
   - Use image: `mysql:8.0`
   - Environment variable: `MYSQL_ROOT_PASSWORD=secret`
   - Use the headless service
3. Verify you can resolve individual pod DNS names

**Hints**:
- Headless services have `clusterIP: None`
- StatefulSet pods get DNS: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`
- Test DNS with: `kubectl run -it --rm debug --image=busybox -- nslookup mysql-0.mysql-headless`

---

## Exercise 5: Service with Session Affinity

**Objective**: Create a service with session affinity for stateful applications.

**Requirements**:
1. Create a deployment named `stateful-app` with 3 replicas using `nginx` image
2. Create a service that:
   - Enables session affinity based on ClientIP
   - Sets timeout to 3600 seconds
   - Exposes port 80
3. Test that requests from the same client go to the same pod

**Hints**:
- Use `sessionAffinity: ClientIP`
- Check which pod handles requests by examining logs

---

## Exercise 6: Basic Ingress Setup

**Objective**: Create an Ingress resource for host-based routing.

**Requirements**:
1. Create two deployments:
   - `web-app` using `nginx` image
   - `api-app` using `nginx` image
2. Create ClusterIP services for both deployments
3. Create an Ingress that routes:
   - `www.example.local` → `web-app` service
   - `api.example.local` → `api-app` service
4. Name the Ingress `host-based-ingress`

**Hints**:
- You may need to install an Ingress controller (NGINX)
- Test with: `curl -H "Host: www.example.local" http://<ingress-ip>`

---

## Exercise 7: Path-Based Ingress Routing

**Objective**: Create an Ingress with path-based routing.

**Requirements**:
1. Create three deployments:
   - `frontend` (nginx)
   - `api-backend` (nginx)
   - `admin-panel` (nginx)
2. Create services for all deployments
3. Create an Ingress named `path-routing` that routes:
   - `/` → `frontend` service
   - `/api` → `api-backend` service
   - `/admin` → `admin-panel` service
4. All routes should use the same host: `app.example.local`

**Hints**:
- Use `pathType: Prefix`
- Order matters - more specific paths should come first

---

## Exercise 8: Ingress with TLS

**Objective**: Create an Ingress with TLS termination.

**Requirements**:
1. Create a self-signed certificate and key:
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout tls.key -out tls.crt -subj "/CN=secure.example.local"
   ```
2. Create a TLS secret named `tls-secret` with the certificate
3. Create a deployment and service named `secure-app`
4. Create an Ingress that:
   - Uses TLS for host `secure.example.local`
   - Routes to `secure-app` service
   - Redirects HTTP to HTTPS

**Hints**:
- Create secret: `kubectl create secret tls tls-secret --cert=tls.crt --key=tls.key`
- Add annotation for SSL redirect (NGINX): `nginx.ingress.kubernetes.io/ssl-redirect: "true"`

---

## Exercise 9: Deny All Network Policy

**Objective**: Implement a default deny policy for a namespace.

**Requirements**:
1. Create a namespace named `secure-ns`
2. Create a NetworkPolicy that denies all ingress traffic to all pods in the namespace
3. Create a test deployment in the namespace
4. Verify that no traffic can reach the pods

**Hints**:
- Empty `podSelector: {}` applies to all pods
- Empty ingress rules list means deny all
- Test from another pod in different namespace

---

## Exercise 10: Allow Specific Pod Communication

**Objective**: Create a NetworkPolicy that allows traffic only from specific pods.

**Requirements**:
1. Create a namespace `app-ns`
2. Create two deployments:
   - `frontend` with label `tier=frontend`
   - `backend` with label `tier=backend`
3. Create a NetworkPolicy that:
   - Applies to `backend` pods
   - Allows ingress from `frontend` pods only on port 8080
   - Denies all other ingress traffic
4. Test connectivity from frontend (should work) and from other pods (should fail)

**Hints**:
- Use `podSelector` to target backend pods
- Use `from.podSelector` to allow frontend pods
- Test with `kubectl exec` and `wget` or `curl`

---

## Exercise 11: Namespace Isolation with Network Policy

**Objective**: Isolate traffic between namespaces using NetworkPolicy.

**Requirements**:
1. Create two namespaces:
   - `production` with label `env=production`
   - `development` with label `env=development`
2. Create a deployment in each namespace named `app`
3. Create NetworkPolicies that:
   - Allow pods in `production` to communicate only with other `production` pods
   - Allow pods in `development` to communicate only with other `development` pods
4. Verify cross-namespace communication is blocked

**Hints**:
- Use `namespaceSelector` with labels
- Label namespaces with `kubectl label namespace`

---

## Exercise 12: Allow DNS and External API

**Objective**: Create an egress policy that allows DNS and external API access.

**Requirements**:
1. Create a namespace `restricted`
2. Create a deployment named `external-client` with `curlimages/curl` image
3. Create a NetworkPolicy that:
   - Applies to all pods in the namespace
   - Allows egress to:
     - DNS (kube-dns) on port 53 UDP
     - External IP range 8.8.8.8/32 on port 443
   - Denies all other egress
4. Test DNS resolution and HTTPS access to 8.8.8.8

**Hints**:
- CoreDNS is in `kube-system` namespace
- Use `namespaceSelector` for DNS
- Use `ipBlock` for external IPs

---

## Exercise 13: Combined Ingress and Egress Policy

**Objective**: Create a comprehensive policy with both ingress and egress rules.

**Requirements**:
1. Create namespace `three-tier`
2. Create three deployments:
   - `web` (tier=web)
   - `api` (tier=api)
   - `database` (tier=database)
3. Create NetworkPolicies that enforce:
   - `web` can receive from Ingress controller only
   - `web` can send to `api` on port 8080
   - `api` can receive from `web` only
   - `api` can send to `database` on port 5432
   - `database` can receive from `api` only
   - All pods can access DNS
4. Test the complete traffic flow

**Hints**:
- Create separate policies for each tier
- Always allow DNS in egress rules
- Test each connection path

---

## Exercise 14: Service Discovery with DNS

**Objective**: Understand and test Kubernetes DNS resolution.

**Requirements**:
1. Create three namespaces: `ns1`, `ns2`, `ns3`
2. In each namespace, create:
   - Deployment named `app`
   - Service named `app-service`
3. From a pod in `ns1`, test DNS resolution:
   - Short name: `app-service`
   - Namespace-qualified: `app-service.ns2`
   - Fully qualified: `app-service.ns3.svc.cluster.local`
4. Document all DNS formats that work

**Hints**:
- Use `nslookup` or `dig` from a debug pod
- Try different DNS name formats

---

## Exercise 15: Troubleshoot Broken Service

**Objective**: Debug and fix a non-functional service.

**Requirements**:
You've been given a broken setup. Fix the issues:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: broken-app
    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: broken-service
spec:
  type: ClusterIP
  selector:
    app: myapp-service
  ports:
  - port: 80
    targetPort: 8080
```

Tasks:
1. Apply the YAML and identify why the service doesn't work
2. Fix all issues
3. Verify the service is functional

**Hints**:
- Check endpoints: `kubectl get endpoints broken-service`
- Verify selectors match pod labels
- Verify target port matches container port
- Use `kubectl describe` to investigate

---

## Bonus Exercise 16: Rate Limiting with Ingress

**Objective**: Implement rate limiting on an Ingress.

**Requirements**:
1. Create a deployment `rate-limited-app` with nginx
2. Create a service for the deployment
3. Create an Ingress with annotations that:
   - Limit requests to 10 per second
   - Limit concurrent connections to 5
   - Return 429 status when limit is exceeded
4. Test the rate limiting with load testing tool

**Hints**:
- Use NGINX Ingress Controller annotations
- Test with `ab` (Apache Bench) or `hey`

---

## Bonus Exercise 17: Custom Endpoints Service

**Objective**: Create a service that points to external endpoints.

**Requirements**:
1. Create a service named `external-db` without a selector
2. Manually create an Endpoints object that points to:
   - 192.168.1.100:5432
   - 192.168.1.101:5432
3. Verify the service resolves to the external IPs
4. Create a pod that connects to the service

**Hints**:
- Service and Endpoints must have the same name
- Use `kubectl get endpoints` to verify

---

## Bonus Exercise 18: Ingress with Multiple TLS Certificates

**Objective**: Create an Ingress with different TLS certificates for different hosts.

**Requirements**:
1. Create two self-signed certificates:
   - cert1 for `app1.example.local`
   - cert2 for `app2.example.local`
2. Create two TLS secrets
3. Create two deployments and services
4. Create a single Ingress that:
   - Routes to both services based on host
   - Uses the appropriate TLS certificate for each host

**Hints**:
- Multiple `tls` entries in Ingress spec
- Each TLS entry specifies hosts and secret

---

## Testing Checklist

After completing all exercises, verify:

- [ ] Created ClusterIP, NodePort, and LoadBalancer services
- [ ] Exposed multi-port services
- [ ] Created and tested headless services
- [ ] Implemented session affinity
- [ ] Created host-based and path-based Ingress routes
- [ ] Configured TLS termination on Ingress
- [ ] Implemented default deny NetworkPolicy
- [ ] Created pod-to-pod allow policies
- [ ] Configured namespace isolation
- [ ] Created egress policies for DNS and external access
- [ ] Combined ingress and egress policies
- [ ] Tested Kubernetes DNS resolution
- [ ] Debugged and fixed service issues
- [ ] Implemented Ingress rate limiting
- [ ] Created services with custom endpoints
- [ ] Configured multiple TLS certificates

---

**Time Estimate**: 4-6 hours for all exercises

**Next**: Review solutions in [solutions.md](./solutions.md) after attempting the exercises.
