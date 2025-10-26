# Module 08: Observability & Debugging

## 📚 Overview

Observability and troubleshooting are critical skills for managing Kubernetes clusters.

**Exam Weight**: CKA (30% - Troubleshooting), CKAD (20% - Application Observability & Maintenance)

---

## Container Logging

### View Logs

```bash
# Current logs
kubectl logs pod-name

# Previous container (after crash)
kubectl logs pod-name --previous

# Specific container in multi-container pod
kubectl logs pod-name -c container-name

# Follow logs (stream)
kubectl logs -f pod-name

# Last N lines
kubectl logs pod-name --tail=100

# Since timestamp
kubectl logs pod-name --since=1h
kubectl logs pod-name --since-time=2023-10-01T10:00:00Z

# All pods with label
kubectl logs -l app=nginx

# Deployment logs
kubectl logs deployment/nginx
```

---

## Health Probes

Health probes monitor container health and availability.

### Liveness Probe

Determines if container is running. Kubelet kills and restarts if it fails.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-pod
spec:
  containers:
    - name: app
      image: nginx
      livenessProbe:
        httpGet:
          path: /healthz
          port: 8080
        initialDelaySeconds: 3
        periodSeconds: 10
        timeoutSeconds: 1
        successThreshold: 1
        failureThreshold: 3
```

### Readiness Probe

Determines if container is ready to serve traffic. Service removes pod from endpoints if it fails.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-pod
spec:
  containers:
    - name: app
      image: nginx
      readinessProbe:
        httpGet:
          path: /ready
          port: 8080
        initialDelaySeconds: 5
        periodSeconds: 5
```

### Startup Probe

For slow-starting containers. Other probes disabled until this succeeds.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: startup-pod
spec:
  containers:
    - name: app
      image: myapp
      startupProbe:
        httpGet:
          path: /startup
          port: 8080
        failureThreshold: 30
        periodSeconds: 10
```

### Probe Types

**HTTP GET**:
```yaml
httpGet:
  path: /health
  port: 8080
  httpHeaders:
    - name: Custom-Header
      value: Value
```

**TCP Socket**:
```yaml
tcpSocket:
  port: 3306
```

**Exec Command**:
```yaml
exec:
  command:
    - cat
    - /tmp/healthy
```

---

## Monitoring

### Resource Usage

```bash
# Node metrics
kubectl top nodes

# Pod metrics
kubectl top pods

# Pod metrics with containers
kubectl top pods --containers

# Specific namespace
kubectl top pods -n kube-system

# Sort by CPU
kubectl top pods --sort-by=cpu

# Sort by memory
kubectl top pods --sort-by=memory
```

### Metrics Server

**Install**:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Verify**:
```bash
kubectl get deployment metrics-server -n kube-system
kubectl top nodes
```

---

## Debugging Pods

### Describe Resources

```bash
# Pod details
kubectl describe pod pod-name

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Namespace events
kubectl get events -n default

# Watch events
kubectl get events --watch
```

### Common Pod Issues

**ImagePullBackOff**:
```bash
kubectl describe pod pod-name
# Check: Image name, imagePullSecrets, registry access
```

**CrashLoopBackOff**:
```bash
kubectl logs pod-name
kubectl logs pod-name --previous
# Check: Application errors, resource limits
```

**Pending**:
```bash
kubectl describe pod pod-name
# Check: Insufficient resources, node selectors, taints
```

### Execute Commands in Container

```bash
# Interactive shell
kubectl exec -it pod-name -- /bin/bash
kubectl exec -it pod-name -- /bin/sh

# Specific container
kubectl exec -it pod-name -c container-name -- /bin/bash

# Single command
kubectl exec pod-name -- ls -la /app
kubectl exec pod-name -- env
kubectl exec pod-name -- ps aux
```

### Debug with Ephemeral Containers

```bash
# Add debug container (K8s 1.23+)
kubectl debug pod-name -it --image=busybox

# Debug with different image
kubectl debug pod-name -it --image=ubuntu --target=container-name

# Create copy of pod for debugging
kubectl debug pod-name -it --copy-to=debug-pod --image=ubuntu
```

### Port Forwarding

```bash
# Forward local port to pod
kubectl port-forward pod-name 8080:80

# Forward to service
kubectl port-forward service/my-service 8080:80

# Forward to deployment
kubectl port-forward deployment/nginx 8080:80

# Listen on all interfaces
kubectl port-forward --address 0.0.0.0 pod-name 8080:80
```

---

## Debugging Services

### Service Issues

```bash
# Check service
kubectl get svc my-service
kubectl describe svc my-service

# Check endpoints
kubectl get endpoints my-service

# No endpoints? Check:
# 1. Selector matches pod labels
kubectl get pods --show-labels
# 2. Pods are running and ready
kubectl get pods
# 3. Target port is correct
kubectl describe svc my-service
```

### Test Service Connectivity

```bash
# Create test pod
kubectl run test --image=busybox --rm -it --restart=Never -- sh

# From test pod:
wget -O- http://service-name:port
nc -zv service-name port
nslookup service-name
```

---

## Debugging Nodes

### Node Status

```bash
# List nodes
kubectl get nodes
kubectl get nodes -o wide

# Node details
kubectl describe node node-name

# Node conditions
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

### Node Issues

**NotReady**:
```bash
# Check node
kubectl describe node node-name

# SSH to node and check:
systemctl status kubelet
journalctl -u kubelet -f

# Check disk pressure
df -h
```

**MemoryPressure / DiskPressure**:
```bash
# Free up resources
kubectl drain node-name --ignore-daemonsets
# Clean up on node
# Uncordon when ready
kubectl uncordon node-name
```

---

## Troubleshooting Workflow

### 1. Check Pod Status

```bash
kubectl get pods
# Status: Running, Pending, CrashLoopBackOff, Error, ImagePullBackOff
```

### 2. Describe Pod

```bash
kubectl describe pod pod-name
# Check: Events, Conditions, Container statuses
```

### 3. Check Logs

```bash
kubectl logs pod-name
kubectl logs pod-name --previous
```

### 4. Check Events

```bash
kubectl get events --sort-by='.lastTimestamp'
kubectl get events --field-selector involvedObject.name=pod-name
```

### 5. Execute Commands

```bash
kubectl exec -it pod-name -- /bin/sh
```

### 6. Check Resources

```bash
kubectl top nodes
kubectl top pods
```

### 7. Check Network

```bash
kubectl run test --image=busybox --rm -it -- wget -O- http://service:port
```

---

## Common Issues & Solutions

### Pod Won't Start

**Symptom**: Pending status

**Check**:
```bash
kubectl describe pod pod-name
```

**Causes**:
- Insufficient CPU/memory
- No nodes matching nodeSelector
- Taints without tolerations
- PVC not bound

### Pod Crashes Repeatedly

**Symptom**: CrashLoopBackOff

**Check**:
```bash
kubectl logs pod-name
kubectl logs pod-name --previous
kubectl describe pod pod-name
```

**Causes**:
- Application error
- Missing configuration
- Resource limits too low
- Failed liveness probe

### Can't Pull Image

**Symptom**: ImagePullBackOff, ErrImagePull

**Check**:
```bash
kubectl describe pod pod-name
```

**Causes**:
- Wrong image name
- Missing imagePullSecret
- Private registry auth
- Network issues

### Service Not Working

**Symptom**: Can't connect to service

**Check**:
```bash
kubectl get svc,endpoints
kubectl describe svc service-name
```

**Causes**:
- Selector doesn't match pods
- Target port incorrect
- Pods not ready
- Network policy blocking

---

## Exam Tips

**Quick Troubleshooting Commands**:
```bash
# Get pod status
kubectl get pods

# Describe for details
kubectl describe pod pod-name

# Check logs
kubectl logs pod-name
kubectl logs pod-name --previous

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Execute command
kubectl exec -it pod-name -- /bin/sh

# Check resources
kubectl top nodes
kubectl top pods

# Port forward for testing
kubectl port-forward pod-name 8080:80

# Check service endpoints
kubectl get endpoints service-name

# Test connectivity
kubectl run test --image=busybox --rm -it -- wget http://service:port
```

**Common Tasks**:
1. Debug pod that won't start
2. Check logs of crashed container
3. Test service connectivity
4. Verify endpoints are created
5. Check resource usage
6. Add health probes to pod
7. Debug node issues

**Health Probe Template**:
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Summary

**Logging**:
- `kubectl logs`: View container logs
- `--previous`: Logs from crashed container
- `-f`: Follow logs

**Health Probes**:
- **Liveness**: Restart unhealthy containers
- **Readiness**: Remove from service endpoints
- **Startup**: For slow-starting containers

**Monitoring**:
- `kubectl top`: Resource usage
- Metrics Server required

**Debugging**:
- `kubectl describe`: Detailed information
- `kubectl exec`: Run commands in container
- `kubectl port-forward`: Test connectivity
- `kubectl get events`: Check cluster events

**Troubleshooting Flow**:
1. Check status → 2. Describe → 3. Logs → 4. Events → 5. Exec → 6. Resources

**Next Module**: [Module 09: Cluster Maintenance →](../09-cluster-maintenance/README.md)
