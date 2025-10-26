# Module 07: Security

## 📚 Overview

Security is critical in Kubernetes. This module covers authentication, authorization (RBAC), security contexts, and Pod Security Standards.

**Exam Weight**: CKA (12%), CKAD (15%)

---

## Authentication & Authorization

### Authentication Methods
- Client certificates
- Bearer tokens
- Service Account tokens
- OpenID Connect (OIDC)

### Authorization Modes
- **RBAC** (Role-Based Access Control) - Most common
- Node Authorization
- Webhook
- ABAC (Attribute-Based Access Control)

---

## Service Accounts

Service Accounts provide identity for pods.

**Create Service Account**:
```bash
kubectl create serviceaccount my-sa
```

**YAML**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-sa
  namespace: default
```

**Use in Pod**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sa-pod
spec:
  serviceAccountName: my-sa
  containers:
    - name: app
      image: nginx
```

**Default Service Account**: Every namespace has a `default` ServiceAccount automatically assigned to pods.

---

## RBAC (Role-Based Access Control)

### Core Components

1. **Role** / **ClusterRole**: Define permissions
2. **RoleBinding** / **ClusterRoleBinding**: Grant permissions to users/groups/service accounts

### Role vs ClusterRole

| Resource | Scope | Use Case |
|----------|-------|----------|
| **Role** | Namespace | Namespace-specific permissions |
| **ClusterRole** | Cluster-wide | Cluster resources, cross-namespace |

### Create Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods/log"]
    verbs: ["get"]
```

**Verbs**: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`

### Create RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
  - kind: ServiceAccount
    name: my-sa
    namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### ClusterRole Example

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-admin-pods
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["*"]  # All verbs
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list"]
```

### ClusterRoleBinding Example

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
  - kind: User
    name: jane
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin-pods
  apiGroup: rbac.authorization.k8s.io
```

### Imperative Commands

```bash
# Create Role
kubectl create role pod-reader --verb=get,list --resource=pods

# Create RoleBinding
kubectl create rolebinding read-pods --role=pod-reader --serviceaccount=default:my-sa

# Create ClusterRole
kubectl create clusterrole node-reader --verb=get,list --resource=nodes

# Create ClusterRoleBinding
kubectl create clusterrolebinding node-reader-binding --clusterrole=node-reader --serviceaccount=default:my-sa
```

### Check Permissions

```bash
# Check if user can perform action
kubectl auth can-i create pods --as=jane

# Check for service account
kubectl auth can-i list pods --as=system:serviceaccount:default:my-sa

# List all permissions
kubectl auth can-i --list --as=jane
```

---

## Security Contexts

Security contexts define privilege and access control settings for pods/containers.

### Pod-Level Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-pod
spec:
  securityContext:
    runAsUser: 1000      # UID
    runAsGroup: 3000     # GID
    fsGroup: 2000        # Volume ownership
    runAsNonRoot: true   # Enforce non-root
  containers:
    - name: app
      image: nginx
```

### Container-Level Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: container-security-pod
spec:
  containers:
    - name: app
      image: nginx
      securityContext:
        runAsUser: 2000
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE
```

### Common Security Context Options

| Field | Description |
|-------|-------------|
| `runAsUser` | User ID to run container |
| `runAsGroup` | Group ID |
| `runAsNonRoot` | Require non-root user |
| `readOnlyRootFilesystem` | Make root filesystem read-only |
| `allowPrivilegeEscalation` | Allow privilege escalation |
| `privileged` | Run as privileged container |
| `capabilities` | Add/drop Linux capabilities |
| `seLinuxOptions` | SELinux options |
| `fsGroup` | Group ownership for volumes |

### Best Practice Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: nginx
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        capabilities:
          drop:
            - ALL
```

---

## Pod Security Standards (PSS)

Replaced PodSecurityPolicy (deprecated in 1.21, removed in 1.25).

### Three Levels

1. **Privileged**: Unrestricted (default)
2. **Baseline**: Minimally restrictive, prevents known privilege escalations
3. **Restricted**: Heavily restricted, hardened

### Enable PSS on Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Modes**:
- `enforce`: Reject violating pods
- `audit`: Log violations (allowed)
- `warn`: Show warnings (allowed)

### Baseline Example

```bash
kubectl label namespace default pod-security.kubernetes.io/enforce=baseline
```

Allows:
- Non-root containers
- Specific capabilities
- No hostPath volumes

### Restricted Example

```bash
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted
```

Requires:
- Run as non-root
- Drop all capabilities
- No privilege escalation
- Read-only root filesystem

---

## Network Security

See [Module 04: Network Policies](../04-services-networking/README.md#network-policies)

---

## Image Security

### Use Private Registry

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-image-pod
spec:
  imagePullSecrets:
    - name: regcred
  containers:
    - name: app
      image: private-registry.com/app:1.0
```

### Image Pull Policy

```yaml
spec:
  containers:
    - name: app
      image: nginx:1.21
      imagePullPolicy: Always  # Always, IfNotPresent, Never
```

### Scan Images

```bash
# Use tools like Trivy
trivy image nginx:latest
```

---

## Secrets Management

### Encrypt Secrets at Rest

**Encryption Configuration** (`/etc/kubernetes/enc/encryption-config.yaml`):
```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64-encoded-32-byte-key>
      - identity: {}
```

**Enable in API Server**:
```bash
--encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml
```

### External Secrets Managers

- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- GCP Secret Manager

---

## Admission Controllers

Admission controllers intercept API requests before persistence.

**Common Controllers**:
- **NamespaceLifecycle**: Prevents actions in terminating namespaces
- **LimitRanger**: Enforces resource limits
- **ServiceAccount**: Automatically creates service accounts
- **PodSecurityPolicy** (deprecated): Enforced pod security policies
- **ValidatingAdmissionWebhook**: Custom validation
- **MutatingAdmissionWebhook**: Custom mutation

**Check Enabled Controllers**:
```bash
kubectl exec -n kube-system kube-apiserver-<node> -- kube-apiserver -h | grep enable-admission-plugins
```

---

## Best Practices

1. **Use RBAC with Least Privilege**
   - Grant minimum required permissions
   - Use namespaces for isolation

2. **Enable Pod Security Standards**
   - Use `restricted` for production
   - Use `baseline` for development

3. **Run as Non-Root**
   ```yaml
   securityContext:
     runAsNonRoot: true
     runAsUser: 1000
   ```

4. **Drop Capabilities**
   ```yaml
   securityContext:
     capabilities:
       drop: ["ALL"]
   ```

5. **Read-Only Root Filesystem**
   ```yaml
   securityContext:
     readOnlyRootFilesystem: true
   ```

6. **Enable Audit Logging**
   - Track API access
   - Monitor security events

7. **Use Network Policies**
   - Default deny
   - Explicit allow

8. **Scan Images**
   - Use trusted registries
   - Regular vulnerability scans

---

## Exam Tips

**Quick Commands**:
```bash
# ServiceAccount
kubectl create serviceaccount my-sa
kubectl get sa

# RBAC
kubectl create role pod-reader --verb=get,list --resource=pods
kubectl create rolebinding read-pods --role=pod-reader --serviceaccount=default:my-sa
kubectl auth can-i get pods --as=system:serviceaccount:default:my-sa

# ClusterRole
kubectl create clusterrole node-admin --verb=* --resource=nodes
kubectl create clusterrolebinding node-admin-binding --clusterrole=node-admin --user=jane

# Check permissions
kubectl auth can-i create deployments
kubectl auth can-i delete pods --as=jane
kubectl auth can-i --list
```

**Common Tasks**:
1. Create ServiceAccount and use in pod
2. Create Role with specific permissions
3. Create RoleBinding to grant permissions
4. Add security context to pod/container
5. Enable Pod Security Standard on namespace
6. Check if user can perform action

**Security Context Template**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
```

---

## Summary

- **ServiceAccounts**: Identity for pods
- **RBAC**: Role-based access control
  - Role/ClusterRole: Define permissions
  - RoleBinding/ClusterRoleBinding: Grant permissions
- **Security Contexts**: Pod/container privilege settings
- **Pod Security Standards**: Namespace-level policy enforcement
- **Best Practices**: Least privilege, non-root, drop capabilities, read-only filesystem

**Next Module**: [Module 08: Observability & Debugging →](../08-observability-debugging/README.md)
