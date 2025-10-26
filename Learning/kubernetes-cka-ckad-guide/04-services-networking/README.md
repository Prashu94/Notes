# Module 04: Services & Networking

## 📚 Table of Contents

- [Overview](#overview)
- [Services](#services)
  - [Service Types](#service-types)
  - [ClusterIP Service](#clusterip-service)
  - [NodePort Service](#nodeport-service)
  - [LoadBalancer Service](#loadbalancer-service)
  - [ExternalName Service](#externalname-service)
  - [Headless Services](#headless-services)
- [Service Discovery](#service-discovery)
- [Endpoints and EndpointSlices](#endpoints-and-endpointslices)
- [Ingress](#ingress)
  - [Ingress Controllers](#ingress-controllers)
  - [Ingress Rules](#ingress-rules)
  - [TLS/SSL Termination](#tlsssl-termination)
- [Network Policies](#network-policies)
  - [Ingress Rules](#network-policy-ingress-rules)
  - [Egress Rules](#network-policy-egress-rules)
  - [Policy Selection](#policy-selection)
- [DNS in Kubernetes](#dns-in-kubernetes)
- [CNI (Container Network Interface)](#cni-container-network-interface)
- [Best Practices](#best-practices)
- [Exam Tips](#exam-tips)

---

## Overview

Services and networking are fundamental concepts in Kubernetes that enable:
- **Service Discovery**: Finding and connecting to applications
- **Load Balancing**: Distributing traffic across pods
- **Network Isolation**: Controlling traffic flow with policies
- **External Access**: Exposing applications outside the cluster

**Exam Weight**:
- **CKA**: 20% - Services & Networking
- **CKAD**: 20% - Services & Networking

**Key Concepts**:
- Services provide stable networking endpoints for pods
- Ingress manages external HTTP/HTTPS access
- Network Policies control pod-to-pod communication
- DNS enables service discovery within the cluster

---

## Services

### What is a Service?

A Service is an abstract way to expose an application running on a set of Pods as a network service. Services solve the problem of pod IP addresses being ephemeral.

**Key Characteristics**:
- Stable IP address (ClusterIP)
- Stable DNS name
- Load balancing across pod replicas
- Service discovery mechanism

### Service Types

Kubernetes supports four types of Services:

| Type | Description | Use Case | Accessibility |
|------|-------------|----------|---------------|
| **ClusterIP** | Internal cluster IP | Internal communication | Cluster-only |
| **NodePort** | Opens port on each node | Development/testing | External via node IP:port |
| **LoadBalancer** | Cloud load balancer | Production external access | External via LB IP |
| **ExternalName** | DNS CNAME record | External service mapping | DNS redirection |

---

### ClusterIP Service

The default service type. Creates an internal IP address accessible only within the cluster.

**Use Cases**:
- Internal microservice communication
- Database access from applications
- Internal APIs

**Example**: Basic ClusterIP Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: default
spec:
  type: ClusterIP  # Default, can be omitted
  selector:
    app: backend
    tier: api
  ports:
    - name: http
      protocol: TCP
      port: 80        # Service port
      targetPort: 8080  # Container port
    - name: https
      protocol: TCP
      port: 443
      targetPort: 8443
```

**How it works**:
```
Client Pod → Service ClusterIP:80 → kube-proxy → Backend Pod:8080
```

**Key Fields**:
- `selector`: Matches pods to include in service
- `port`: Port the service listens on
- `targetPort`: Port on the pod to forward traffic to

**Imperative Command**:
```bash
kubectl expose deployment backend --port=80 --target-port=8080 --name=backend-service
```

---

### NodePort Service

Exposes the service on each Node's IP at a static port (30000-32767).

**Use Cases**:
- Development and testing
- Small-scale deployments
- When LoadBalancer is not available

**Example**: NodePort Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-nodeport
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - name: http
      protocol: TCP
      port: 80          # Service port
      targetPort: 8080  # Container port
      nodePort: 30080   # Port on node (optional, auto-assigned if omitted)
```

**Access Methods**:
```bash
# From outside cluster
curl http://<node-ip>:30080

# From inside cluster
curl http://frontend-nodeport:80
```

**Traffic Flow**:
```
External Client → Node IP:30080 → ClusterIP:80 → Pod:8080
```

**Imperative Command**:
```bash
kubectl expose deployment frontend --type=NodePort --port=80 --target-port=8080
```

---

### LoadBalancer Service

Creates an external load balancer (in cloud environments) and assigns a public IP.

**Use Cases**:
- Production external access
- Cloud environments (AWS ELB, GCP Load Balancer, Azure Load Balancer)
- High-availability applications

**Example**: LoadBalancer Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-loadbalancer
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"  # AWS specific
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 8080
  # Optional: Restrict load balancer access
  loadBalancerSourceRanges:
    - 10.0.0.0/8
    - 192.168.0.0/16
```

**Traffic Flow**:
```
Internet → Cloud Load Balancer → NodePort → ClusterIP → Pod
```

**Check External IP**:
```bash
kubectl get svc web-loadbalancer
# Wait for EXTERNAL-IP to be assigned (may take 1-2 minutes)
```

---

### ExternalName Service

Maps a service to a DNS name (external service).

**Use Cases**:
- Accessing external databases
- Migrating services
- Service aliasing

**Example**: ExternalName Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
  namespace: production
spec:
  type: ExternalName
  externalName: database.example.com
```

**Usage**:
```bash
# Pods can connect to "external-database" which resolves to "database.example.com"
mysql -h external-database -u user -p
```

---

### Headless Services

A service without a ClusterIP (ClusterIP: None). Returns pod IPs directly instead of load balancing.

**Use Cases**:
- StatefulSets (direct pod access)
- Custom load balancing
- Service mesh implementations

**Example**: Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql-headless
spec:
  clusterIP: None  # Makes it headless
  selector:
    app: mysql
  ports:
    - name: mysql
      port: 3306
      targetPort: 3306
```

**DNS Resolution**:
```bash
# Returns all pod IPs (A records)
nslookup mysql-headless.default.svc.cluster.local

# StatefulSet pod DNS
mysql-0.mysql-headless.default.svc.cluster.local
mysql-1.mysql-headless.default.svc.cluster.local
```

---

## Service Discovery

Kubernetes provides two primary methods for service discovery:

### 1. Environment Variables

Kubernetes automatically creates environment variables for each service.

**Format**:
```bash
<SERVICE_NAME>_SERVICE_HOST=<cluster-ip>
<SERVICE_NAME>_SERVICE_PORT=<port>
```

**Example**:
```bash
# If service "backend" exists when pod starts
BACKEND_SERVICE_HOST=10.96.0.10
BACKEND_SERVICE_PORT=80
```

**Limitation**: Only services created **before** the pod will have environment variables.

### 2. DNS (Preferred)

CoreDNS provides DNS-based service discovery.

**DNS Format**:
```
<service-name>.<namespace>.svc.cluster.local
```

**Examples**:
```bash
# Same namespace
curl http://backend-service

# Different namespace
curl http://backend-service.production

# Fully qualified
curl http://backend-service.production.svc.cluster.local

# External services
curl http://external-database.default.svc.cluster.local
```

**DNS for Headless Services**:
```bash
# StatefulSet pod
<pod-name>.<service-name>.<namespace>.svc.cluster.local

# Example
mysql-0.mysql.default.svc.cluster.local
```

---

## Endpoints and EndpointSlices

### Endpoints

Endpoints track the IP addresses of pods backing a service.

**View Endpoints**:
```bash
kubectl get endpoints backend-service

# Detailed view
kubectl describe endpoints backend-service
```

**Manual Endpoint (Service without selector)**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-api
spec:
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-api  # Must match service name
subsets:
  - addresses:
      - ip: 192.168.1.100
      - ip: 192.168.1.101
    ports:
      - port: 80
```

### EndpointSlices

Modern replacement for Endpoints (more scalable).

**View EndpointSlices**:
```bash
kubectl get endpointslices
kubectl describe endpointslice backend-service-abc123
```

---

## Ingress

Ingress provides HTTP/HTTPS routing to services based on hostnames and paths.

**Benefits over LoadBalancer**:
- Single load balancer for multiple services
- Host-based and path-based routing
- TLS/SSL termination
- Cost-effective

### Ingress Architecture

```
Internet → Ingress Controller (NGINX/Traefik/etc.) → Services → Pods
```

### Ingress Controllers

Popular implementations:
- **NGINX Ingress Controller** (most common)
- **Traefik**
- **HAProxy**
- **AWS ALB Ingress Controller**
- **GCE Ingress Controller**

**Install NGINX Ingress Controller**:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### Basic Ingress Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simple-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
```

### Path-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: myapp.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
          - path: /web
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: default-service
                port:
                  number: 8080
```

**Path Types**:
- `Prefix`: Matches path prefix (e.g., `/api` matches `/api/users`)
- `Exact`: Exact match only
- `ImplementationSpecific`: Depends on ingress controller

### Host-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-based-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
    - host: www.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
    - host: admin.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: admin-service
                port:
                  number: 3000
```

### TLS/SSL Termination

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - secure.example.com
      secretName: tls-secret  # Secret containing cert and key
  rules:
    - host: secure.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: secure-service
                port:
                  number: 443
```

**Create TLS Secret**:
```bash
kubectl create secret tls tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/cert.key
```

### Ingress Annotations

Common NGINX annotations:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: annotated-ingress
  annotations:
    # Rewrite target URL
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    
    # SSL redirect
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    
    # Backend protocol
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    
    # Rate limiting
    nginx.ingress.kubernetes.io/limit-rps: "10"
    
    # Whitelist source IPs
    nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,192.168.0.0/16"
    
    # Custom timeout
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "30"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  ingressClassName: nginx
  rules:
    - host: app.example.com
      http:
        paths:
          - path: /api(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 8080
```

---

## Network Policies

Network Policies control traffic between pods (like firewalls).

**Important**: Requires a CNI plugin that supports Network Policies (Calico, Cilium, Weave Net).

### Default Behavior

- **Without Network Policies**: All pods can communicate with all pods
- **With Network Policies**: Traffic is denied unless explicitly allowed

### Network Policy Components

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: example-policy
  namespace: default
spec:
  podSelector:          # Which pods this policy applies to
    matchLabels:
      app: backend
  policyTypes:          # Types of policies
    - Ingress
    - Egress
  ingress:              # Incoming traffic rules
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
  egress:               # Outgoing traffic rules
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - protocol: TCP
          port: 5432
```

### Deny All Ingress Traffic

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}  # Empty selector = all pods in namespace
  policyTypes:
    - Ingress
  # No ingress rules = deny all
```

### Deny All Egress Traffic

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  # No egress rules = deny all
```

### Allow Specific Pods (Ingress)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend
      tier: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        # Allow from frontend pods
        - podSelector:
            matchLabels:
              app: frontend
        # Allow from monitoring namespace
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 8080
        - protocol: TCP
          port: 8443
```

### Allow Specific CIDR (Egress)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-external-api
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Egress
  egress:
    # Allow DNS
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
    # Allow external API
    - to:
        - ipBlock:
            cidr: 192.168.100.0/24
            except:
              - 192.168.100.50/32
      ports:
        - protocol: TCP
          port: 443
```

### Complex Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-app-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web
      tier: frontend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow from ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
    # Allow from monitoring
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 9090  # Metrics port
  egress:
    # Allow DNS
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
    # Allow backend API
    - to:
        - podSelector:
            matchLabels:
              app: api
              tier: backend
      ports:
        - protocol: TCP
          port: 8080
    # Allow database
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

### Network Policy Selectors

**podSelector**: Selects pods in the same namespace
```yaml
podSelector:
  matchLabels:
    app: backend
```

**namespaceSelector**: Selects all pods in matching namespaces
```yaml
namespaceSelector:
  matchLabels:
    environment: production
```

**Combined Selectors**: Both namespace AND pod must match
```yaml
- from:
    - namespaceSelector:
        matchLabels:
          environment: production
      podSelector:
        matchLabels:
          app: frontend
```

**ipBlock**: Match IP CIDR ranges
```yaml
- to:
    - ipBlock:
        cidr: 10.0.0.0/8
        except:
          - 10.0.1.0/24
```

---

## DNS in Kubernetes

Kubernetes uses CoreDNS for internal DNS resolution.

### DNS Records

**Service DNS Format**:
```
<service>.<namespace>.svc.<cluster-domain>
```

**Pod DNS Format**:
```
<pod-ip-with-dashes>.<namespace>.pod.<cluster-domain>
```

**Examples**:
```bash
# Service in same namespace
backend-service

# Service in different namespace
backend-service.production

# Fully qualified
backend-service.production.svc.cluster.local

# Pod (10.244.1.5)
10-244-1-5.default.pod.cluster.local
```

### DNS Configuration

**View CoreDNS ConfigMap**:
```bash
kubectl get configmap coredns -n kube-system -o yaml
```

**Custom DNS Policy in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: custom-dns-pod
spec:
  dnsPolicy: "None"  # None, Default, ClusterFirst, ClusterFirstWithHostNet
  dnsConfig:
    nameservers:
      - 8.8.8.8
      - 8.8.4.4
    searches:
      - default.svc.cluster.local
      - svc.cluster.local
      - cluster.local
    options:
      - name: ndots
        value: "2"
  containers:
    - name: app
      image: nginx
```

**DNS Policies**:
- `ClusterFirst`: Use cluster DNS (default)
- `Default`: Use node's DNS
- `ClusterFirstWithHostNet`: For pods with hostNetwork=true
- `None`: Custom DNS configuration

### Troubleshooting DNS

```bash
# Test DNS from pod
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Check CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# View CoreDNS logs
kubectl logs -n kube-system -l k8s-app=kube-dns

# Describe CoreDNS service
kubectl describe svc kube-dns -n kube-system
```

---

## CNI (Container Network Interface)

CNI plugins provide networking capabilities to Kubernetes pods.

### Popular CNI Plugins

| CNI Plugin | Features | Network Policy Support |
|------------|----------|----------------------|
| **Calico** | L3 networking, BGP, Network Policies | ✅ Yes |
| **Flannel** | Simple overlay network, VXLAN | ❌ No |
| **Cilium** | eBPF-based, L7 policies, observability | ✅ Yes |
| **Weave Net** | Overlay network, encryption | ✅ Yes |
| **Canal** | Flannel + Calico policies | ✅ Yes |

### Install CNI Plugin

**Calico**:
```bash
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

**Flannel**:
```bash
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

**Weave Net**:
```bash
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
```

### View CNI Configuration

```bash
# View CNI config on node
cat /etc/cni/net.d/10-calico.conflist

# Check CNI pods
kubectl get pods -n kube-system | grep -E 'calico|flannel|weave'
```

---

## Best Practices

### Service Best Practices

1. **Use ClusterIP for Internal Services**
   ```yaml
   # Internal microservices should use ClusterIP
   spec:
     type: ClusterIP
   ```

2. **Named Ports**
   ```yaml
   # Use named ports for clarity
   ports:
     - name: http
       port: 80
     - name: metrics
       port: 9090
   ```

3. **Session Affinity**
   ```yaml
   # For stateful applications
   spec:
     sessionAffinity: ClientIP
     sessionAffinityConfig:
       clientIP:
         timeoutSeconds: 10800
   ```

### Ingress Best Practices

1. **Use TLS for Production**
   ```yaml
   spec:
     tls:
       - hosts:
           - example.com
         secretName: tls-secret
   ```

2. **Rate Limiting**
   ```yaml
   annotations:
     nginx.ingress.kubernetes.io/limit-rps: "10"
     nginx.ingress.kubernetes.io/limit-connections: "5"
   ```

3. **Whitelist IPs**
   ```yaml
   annotations:
     nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8"
   ```

### Network Policy Best Practices

1. **Default Deny**
   ```yaml
   # Start with deny-all, then allow specific traffic
   spec:
     podSelector: {}
     policyTypes:
       - Ingress
       - Egress
   ```

2. **Explicit Allow DNS**
   ```yaml
   # Always allow DNS for egress policies
   egress:
     - to:
         - namespaceSelector:
             matchLabels:
               name: kube-system
       ports:
         - protocol: UDP
           port: 53
   ```

3. **Namespace Isolation**
   ```yaml
   # Label namespaces for policy selection
   metadata:
     labels:
       environment: production
       team: backend
   ```

---

## Exam Tips

### Time-Saving Commands

**Create Service Imperatively**:
```bash
# Expose deployment
kubectl expose deployment nginx --port=80 --target-port=8080 --name=nginx-service

# Create NodePort service
kubectl expose deployment nginx --type=NodePort --port=80 --name=nginx-nodeport

# Create service from YAML
kubectl create service clusterip my-service --tcp=80:8080
```

**Create Ingress Imperatively**:
```bash
# Create basic ingress
kubectl create ingress simple --rule="example.com/=web-service:80"

# With TLS
kubectl create ingress tls-ingress --rule="secure.com/=web:443,tls=my-cert"
```

**Test Connectivity**:
```bash
# Test service from another pod
kubectl run test --image=busybox --rm -it --restart=Never -- wget -O- http://service-name

# Test with curl
kubectl run curl --image=curlimages/curl --rm -it --restart=Never -- curl http://service-name

# DNS lookup
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup service-name
```

**Debug Network Policies**:
```bash
# Check if CNI supports Network Policies
kubectl get pods -n kube-system | grep -E 'calico|cilium|weave'

# Test connectivity before/after applying policy
kubectl exec pod1 -- wget -O- --timeout=2 http://pod2-service
```

### Common Tasks

**Task 1**: Expose deployment with ClusterIP
```bash
kubectl expose deployment nginx --port=80 --target-port=8080
```

**Task 2**: Create NodePort service
```bash
kubectl expose deployment app --type=NodePort --port=80 --target-port=3000 --name=app-nodeport
```

**Task 3**: Create ingress with host-based routing
```bash
kubectl create ingress multi-host \
  --rule="api.example.com/=api-svc:8080" \
  --rule="web.example.com/=web-svc:80"
```

**Task 4**: Deny all ingress to namespace
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

**Task 5**: Allow specific pods to communicate
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
```

### Quick Reference

**Service YAML Template**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: ClusterIP  # ClusterIP/NodePort/LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
```

**Ingress YAML Template**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
    - host: example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-service
                port:
                  number: 80
```

**Network Policy YAML Template**:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: my-policy
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: allowed-app
      ports:
        - port: 8080
```

---

## Summary

**Services** provide stable networking for dynamic pods:
- ClusterIP for internal communication
- NodePort for external access (development)
- LoadBalancer for production external access
- Ingress for HTTP/HTTPS routing

**Network Policies** control pod-to-pod communication:
- Require CNI plugin support
- Default deny + explicit allow is best practice
- Use labels for flexible policy application

**Key Commands**:
```bash
# Services
kubectl expose deployment <name> --port=80 --target-port=8080
kubectl get svc
kubectl describe svc <name>

# Ingress
kubectl create ingress <name> --rule="host/path=service:port"
kubectl get ingress
kubectl describe ingress <name>

# Network Policies
kubectl apply -f network-policy.yaml
kubectl get networkpolicies
kubectl describe networkpolicy <name>

# DNS testing
kubectl run -it --rm debug --image=busybox -- nslookup <service>
```

**Next Module**: [Module 05: Storage →](../05-storage/README.md)

---

**📝 Practice**: Complete the exercises in `exercises/exercises.md` to reinforce your learning!
