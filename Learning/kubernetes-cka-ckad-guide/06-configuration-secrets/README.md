# Module 06: Configuration & Secrets

## 📚 Overview

Learn how to manage application configuration and sensitive data in Kubernetes using ConfigMaps and Secrets.

**Exam Weight**: CKA (10%), CKAD (25% - Application Design & Build)

---

## ConfigMaps

ConfigMaps store non-confidential configuration data in key-value pairs.

### Create ConfigMap

**From Literal Values**:
```bash
kubectl create configmap app-config \
  --from-literal=app.environment=production \
  --from-literal=app.log_level=info
```

**From File**:
```bash
# Create config file
echo "database=postgres" > app.properties
echo "port=5432" >> app.properties

kubectl create configmap file-config --from-file=app.properties
```

**From Directory**:
```bash
kubectl create configmap dir-config --from-file=./config-dir/
```

**From YAML**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.environment: "production"
  app.log_level: "info"
  database.conf: |
    host=db.example.com
    port=5432
    name=myapp
```

### Use ConfigMap in Pods

**As Environment Variables**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-env-pod
spec:
  containers:
    - name: app
      image: nginx
      env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: app.environment
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: app.log_level
```

**All Keys as Environment Variables**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-envfrom-pod
spec:
  containers:
    - name: app
      image: nginx
      envFrom:
        - configMapRef:
            name: app-config
```

**As Volume**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-volume-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: config
          mountPath: /etc/config
          readOnly: true
  volumes:
    - name: config
      configMap:
        name: app-config
```

**Specific Keys as Files**:
```yaml
volumes:
  - name: config
    configMap:
      name: app-config
      items:
        - key: database.conf
          path: db.conf
```

### Update ConfigMap

```bash
kubectl edit configmap app-config

# Or apply new version
kubectl apply -f configmap.yaml
```

**Note**: Pods must be restarted to pick up changes (unless using mounted volumes with automatic updates).

---

## Secrets

Secrets store sensitive data like passwords, tokens, and keys.

### Secret Types

| Type | Description |
|------|-------------|
| `Opaque` | Arbitrary user-defined data (default) |
| `kubernetes.io/service-account-token` | Service account token |
| `kubernetes.io/dockerconfigjson` | Docker registry credentials |
| `kubernetes.io/tls` | TLS certificate and key |
| `kubernetes.io/basic-auth` | Basic authentication credentials |
| `kubernetes.io/ssh-auth` | SSH authentication credentials |

### Create Secret

**From Literal**:
```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=s3cr3t
```

**From File**:
```bash
echo -n 'admin' > username.txt
echo -n 's3cr3t' > password.txt

kubectl create secret generic db-secret \
  --from-file=username=username.txt \
  --from-file=password=password.txt
```

**Docker Registry Secret**:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=user@example.com
```

**TLS Secret**:
```bash
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

**From YAML**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=       # base64 encoded "admin"
  password: czNjcjN0       # base64 encoded "s3cr3t"
```

**With stringData (no encoding needed)**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  username: admin
  password: s3cr3t
```

### Use Secret in Pods

**As Environment Variables**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-pod
spec:
  containers:
    - name: app
      image: nginx
      env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
```

**All Keys as Environment Variables**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-envfrom-pod
spec:
  containers:
    - name: app
      image: nginx
      envFrom:
        - secretRef:
            name: db-secret
```

**As Volume**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-volume-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
        - name: secret
          mountPath: /etc/secrets
          readOnly: true
  volumes:
    - name: secret
      secret:
        secretName: db-secret
        defaultMode: 0400
```

**Use Docker Registry Secret**:
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
      image: myregistry.com/myapp:latest
```

---

## Best Practices

1. **Use Secrets for Sensitive Data**
```yaml
# ConfigMap for non-sensitive
kind: ConfigMap
data:
  api_url: https://api.example.com

# Secret for sensitive
kind: Secret
stringData:
  api_key: super-secret-key
```

2. **Mount as Volumes for Automatic Updates**
```yaml
# Mounted ConfigMaps/Secrets update automatically (may take time)
volumeMounts:
  - name: config
    mountPath: /etc/config
```

3. **Use RBAC to Protect Secrets**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "list"]
```

4. **Enable Encryption at Rest**
```bash
# Enable in API server
--encryption-provider-config=/path/to/encryption-config.yaml
```

---

## Exam Tips

**Quick Commands**:
```bash
# ConfigMap
kubectl create configmap my-config --from-literal=key=value
kubectl get configmap
kubectl describe configmap my-config
kubectl edit configmap my-config

# Secret
kubectl create secret generic my-secret --from-literal=key=value
kubectl get secrets
kubectl describe secret my-secret
kubectl get secret my-secret -o yaml

# Decode secret
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 --decode

# Use in pod
kubectl run pod --image=nginx --dry-run=client -o yaml > pod.yaml
# Edit to add configMap/secret reference
```

**Common Tasks**:
1. Create ConfigMap from file: `kubectl create configmap config --from-file=app.conf`
2. Create Secret from literals: `kubectl create secret generic sec --from-literal=pass=123`
3. Mount ConfigMap as volume in pod
4. Use Secret as environment variable
5. Create Docker registry secret for private images

---

## Summary

- **ConfigMaps**: Non-sensitive configuration
- **Secrets**: Sensitive data (base64 encoded, not encrypted by default)
- **Usage**: Environment variables, mounted volumes, or imagePullSecrets
- **Updates**: Mounted volumes update automatically; env vars require pod restart

**Next Module**: [Module 07: Security →](../07-security/README.md)
