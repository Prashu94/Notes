# Azure — Practical Exercises

Run these in a dev subscription or read the expected output for interview prep. No subscription? Do Part A on paper with `az` command syntax.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) — 33 exercises total.

---

## Part A — Basic (10)

### Exercise A1 — Create a resource group

**Task:** Create `rg-interview-dev` in `eastus` with tag `env=dev`.

**Solution:**

```bash
az group create \
  --name rg-interview-dev \
  --location eastus \
  --tags env=dev owner=you
```

**Expected output:**

```json
{
  "id": "/subscriptions/<sub-id>/resourceGroups/rg-interview-dev",
  "location": "eastus",
  "name": "rg-interview-dev",
  "properties": { "provisioningState": "Succeeded" },
  "tags": { "env": "dev", "owner": "you" }
}
```

---

### Exercise A2 — List resources in a resource group

**Task:** Show all resources in `rg-interview-dev`.

**Solution:**

```bash
az resource list --resource-group rg-interview-dev -o table
```

**Expected output:**

```
Name                 ResourceGroup       Type                               Location
-------------------  ------------------  ---------------------------------  ----------
kv-interview-dev     rg-interview-dev    Microsoft.KeyVault/vaults          eastus
```

(empty table if RG is new)

---

### Exercise A3 — Create a storage account

**Task:** Create `stinterviewdev001` (globally unique name) with Standard LRS.

**Solution:**

```bash
az storage account create \
  --name stinterviewdev001 \
  --resource-group rg-interview-dev \
  --location eastus \
  --sku Standard_LRS \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false
```

**Expected output:**

```json
{
  "primaryEndpoints": {
    "blob": "https://stinterviewdev001.blob.core.windows.net/"
  },
  "provisioningState": "Succeeded"
}
```

---

### Exercise A4 — Key Vault: create and set a secret

**Task:** Create vault `kv-interview-dev` and store secret `db-password`.

**Solution:**

```bash
az keyvault create \
  --name kv-interview-dev \
  --resource-group rg-interview-dev \
  --location eastus \
  --enable-rbac-authorization true

az keyvault secret set \
  --vault-name kv-interview-dev \
  --name db-password \
  --value 'P@ssw0rd!DevOnly'
```

**Expected output:**

```
{
  "attributes": { "enabled": true },
  "id": "https://kv-interview-dev.vault.azure.net/secrets/db-password/<version>",
  "name": "db-password",
  "value": "P@ssw0rd!DevOnly"
}
```

---

### Exercise A5 — Read a Key Vault secret

**Task:** Fetch `db-password` value (requires `Key Vault Secrets User` on your identity).

**Solution:**

```bash
az keyvault secret show \
  --vault-name kv-interview-dev \
  --name db-password \
  --query value -o tsv
```

**Expected output:**

```
P@ssw0rd!DevOnly
```

---

### Exercise A6 — Create a VNet and subnet

**Task:** VNet `10.10.0.0/16`, subnet `snet-aks` `10.10.1.0/24`.

**Solution:**

```bash
az network vnet create \
  --resource-group rg-interview-dev \
  --name vnet-interview \
  --address-prefix 10.10.0.0/16 \
  --subnet-name snet-aks \
  --subnet-prefix 10.10.1.0/24
```

**Expected output:**

```json
{
  "newVNet": {
    "addressSpace": { "addressPrefixes": ["10.10.0.0/16"] },
    "subnets": [{ "name": "snet-aks", "addressPrefix": "10.10.1.0/24" }]
  }
}
```

---

### Exercise A7 — NSG rule: allow HTTPS inbound

**Task:** Add inbound TCP 443 rule to NSG `nsg-aks`.

**Solution:**

```bash
az network nsg rule create \
  --resource-group rg-interview-dev \
  --nsg-name nsg-aks \
  --name AllowHttpsInbound \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 443 \
  --source-address-prefixes Internet \
  --destination-address-prefixes '*'
```

**Expected output:**

```json
{
  "access": "Allow",
  "destinationPortRange": "443",
  "name": "AllowHttpsInbound",
  "priority": 100,
  "protocol": "Tcp",
  "provisioningState": "Succeeded"
}
```

---

### Exercise A8 — AKS cluster (minimal dev)

**Task:** Create 1-node AKS cluster `aks-interview-dev` in existing subnet.

**Solution:**

```bash
az aks create \
  --resource-group rg-interview-dev \
  --name aks-interview-dev \
  --node-count 1 \
  --node-vm-size Standard_D2s_v3 \
  --vnet-subnet-id $(az network vnet subnet show \
    -g rg-interview-dev --vnet-name vnet-interview --name snet-aks -o tsv --query id) \
  --enable-managed-identity \
  --generate-ssh-keys
```

**Expected output (truncated):**

```json
{
  "fqdn": "aks-interview-dev-<hash>.hcp.eastus.azmk8s.io",
  "kubernetesVersion": "1.29.x",
  "provisioningState": "Succeeded"
}
```

---

### Exercise A9 — Get AKS credentials

**Task:** Merge kubeconfig for `aks-interview-dev`.

**Solution:**

```bash
az aks get-credentials \
  --resource-group rg-interview-dev \
  --name aks-interview-dev \
  --overwrite-existing

kubectl get nodes
```

**Expected output:**

```
NAME                                STATUS   ROLES   AGE   VERSION
aks-nodepool1-12345678-vmss000000   Ready    agent   5m    v1.29.x
```

---

### Exercise A10 — Account and subscription context

**Task:** Show current subscription; switch if needed.

**Solution:**

```bash
az account show -o table
az account list -o table
az account set --subscription "Visual Studio Enterprise"
az account show --query "{name:name, id:id, tenant:tenantId}" -o json
```

**Expected output:**

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "name": "Visual Studio Enterprise",
  "tenant": "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
}
```

---

## Part B — Intermediate (10)

### Exercise B1 — Reference architecture (whiteboard)

**Task:** Draw SPA → Front Door/APIM → AKS (Spring) → Azure SQL + Event Hubs → consumers. Mark Key Vault, managed identity, private endpoints.

**Solution (checklist):**

```
[Browser SPA]
    │ HTTPS
    ▼
[Azure Front Door / APIM] ── WAF, rate limit, JWT validate
    │
    ▼
[AKS Ingress] ── pods: order-service, payment-service
    │                    │
    │ MI (AcrPull)       │ MI (Key Vault Secrets User)
    ▼                    ▼
[ACR]              [Key Vault] ── secrets, certs
    │
    ▼
[Azure SQL / PostgreSQL] ◄── private endpoint in VNet
[Event Hubs] ──► [Functions / consumers]
```

**Expected output:** 5-minute verbal walkthrough covering auth, secrets, and no public DB endpoint.

---

### Exercise B2 — Managed identity + RBAC

**Task:** Assign system-assigned MI on AKS workload to Key Vault and ACR. Document role names.

**Solution:**

```bash
# User-assigned MI (preferred for multiple workloads)
az identity create -g rg-interview-dev -n id-order-svc

PRINCIPAL_ID=$(az identity show -g rg-interview-dev -n id-order-svc --query principalId -o tsv)
KV_ID=$(az keyvault show -g rg-interview-dev -n kv-interview-dev --query id -o tsv)
ACR_ID=$(az acr show -g rg-interview-dev -n acrinterviewdev --query id -o tsv)

az role assignment create --assignee "$PRINCIPAL_ID" --role "Key Vault Secrets User" --scope "$KV_ID"
az role assignment create --assignee "$PRINCIPAL_ID" --role "AcrPull" --scope "$ACR_ID"
```

**Expected output:**

```json
{
  "principalName": "<guid>",
  "roleDefinitionName": "Key Vault Secrets User",
  "scope": "/subscriptions/.../vaults/kv-interview-dev"
}
```

**Senior takeaway:** System-assigned MI dies with the resource; user-assigned survives pod churn and is easier to pre-provision RBAC.

---

### Exercise B3 — Azure Function: HTTP → queue → file

**Task:** HTTP trigger enqueues message; queue trigger writes a file. Show poison queue after 5 failures.

**Solution:**

```bash
func init InterviewQueue --worker-runtime java
cd InterviewQueue
func new --name HttpEnqueue --template "HTTP trigger"
func new --name QueueWriter --template "Azure Queue Storage trigger"
```

```java
// HttpEnqueue.java — POST body → queue
@FunctionName("HttpEnqueue")
public HttpResponseMessage run(
    @HttpTrigger(method = "post", authLevel = Function) HttpRequestMessage<String> req,
    @QueueOutput(name = "msg", queueName = "orders", connection = "AzureWebJobsStorage")
    OutputBinding<String> msg) {
  msg.setValue(req.getBody());
  return req.createResponseBuilder(HttpStatus.OK).body("enqueued").build();
}
```

```bash
# local.settings.json — UseDevelopmentStorage=true (Azurite)
func start
curl -X POST http://localhost:7071/api/HttpEnqueue -d '{"orderId":"1"}'
```

**Expected output:**

```
enqueued
```

Queue trigger logs: `Wrote order 1`. Throw in trigger → after 5 dequeues message lands in `orders-poison`.

---

### Exercise B4 — Passwordless Spring datasource (AKS)

**Task:** Sketch Spring + federated workload identity to Azure PostgreSQL.

**Solution:**

```yaml
# application.yml
spring:
  datasource:
    url: jdbc:postgresql://pg-interview.postgres.database.azure.com:5432/app?sslmode=require
    username: order-svc@pg-interview
    azure:
      passwordless-enabled: true
```

```bash
# Federated credential (OIDC from AKS SA)
az aks pod-identity add --resource-group rg-interview-dev --cluster-name aks-interview-dev \
  --namespace default --name order-svc-identity

# DB: CREATE USER "order-svc" WITH LOGIN; GRANT ... (Entra ID auth)
```

**Expected output:** Pod starts without `SPRING_DATASOURCE_PASSWORD`; connection succeeds via token from `DefaultAzureCredential`.

---

### Exercise B5 — KEDA ScaledObject on Kafka lag

**Task:** Scale consumer deployment 1–10 on lag. Explain why `minReplicaCount: 0` is risky.

**Solution:**

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-consumer-scaler
spec:
  scaleTargetRef:
    name: order-consumer
  minReplicaCount: 1
  maxReplicaCount: 10
  triggers:
    - type: azure-eventhub
      metadata:
        consumerGroup: order-cg
        unprocessedEventThreshold: "100"
        blobContainer: keda-checkpoint
        connectionFromEnv: EVENTHUB_CONNECTION
```

**Expected output:** `kubectl get hpa` shows `TARGETS` rising with lag; pods scale 1 → 4 when threshold exceeded.

**Senior takeaway:** `minReplicaCount: 0` saves cost but cold-start + `latest` offset can hide lag until traffic spikes — dangerous for SLA consumers.

---

### Exercise B6 — Application Insights correlation

**Task:** Enable Java agent; trace service A → B; find shared `operation_Id`.

**Solution:**

```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=..."
export JAVA_TOOL_OPTIONS="-javaagent:/opt/app/applicationinsights-agent.jar"

curl https://order-svc/actuator/health
curl https://order-svc/api/orders/1   # calls payment-svc internally
```

```kusto
requests
| where timestamp > ago(15m)
| where name contains "GET /api/orders"
| project operation_Id, cloud_RoleName, name, duration
| join kind=inner (
    dependencies
    | where timestamp > ago(15m)
    | project operation_Id, target, name, duration
) on operation_Id
```

**Expected output:**

```
operation_Id                          cloud_RoleName  name
------------------------------------  --------------  -----------------
a1b2c3d4-e5f6-7890-abcd-ef1234567890  order-service   GET /api/orders/1
a1b2c3d4-e5f6-7890-abcd-ef1234567890  payment-service HTTP GET payment-svc
```

---

### Exercise B7 — SAS direct blob upload

**Task:** Java returns time-limited SAS; browser PUTs file; never stream 2 GB through Spring.

**Solution:**

```java
// POST /uploads → { uploadUrl, blobUrl, expiresAt }
BlobSasPermission perm = new BlobSasPermission().setWritePermission(true);
OffsetDateTime expiry = OffsetDateTime.now().plusMinutes(15);
BlobServiceSasSignatureValues values = new BlobServiceSasSignatureValues(expiry, perm)
    .setStartTime(OffsetDateTime.now().minusMinutes(5));
String sas = blobClient.generateSas(values);
String uploadUrl = blobClient.getBlobUrl() + "?" + sas;
```

```typescript
// React
const { uploadUrl } = await fetch("/api/uploads", { method: "POST" }).then((r) => r.json());
await fetch(uploadUrl, { method: "PUT", body: file, headers: { "x-ms-blob-type": "BlockBlob" } });
```

**Expected output:**

```bash
az storage blob list --account-name stinterviewdev001 --container-name uploads -o table
```

```
Name          Blob Type    Length
------------  -----------  --------
invoice.pdf   BlockBlob    2097152
```

---

### Exercise B8 — Private endpoint for Key Vault

**Task:** Disable public access; access vault only via private endpoint in `snet-private`.

**Solution:**

```bash
az network private-endpoint create \
  --name pe-kv \
  --resource-group rg-interview-dev \
  --vnet-name vnet-interview \
  --subnet snet-private \
  --private-connection-resource-id $(az keyvault show -g rg-interview-dev -n kv-interview-dev -o tsv --query id) \
  --group-id vault \
  --connection-name kv-conn

az keyvault update -n kv-interview-dev --public-network-access Disabled
```

**Expected output:** `az keyvault secret list` from laptop **fails** (public blocked). Same command from jump box in VNet **succeeds**.

---

### Exercise B9 — ACR integrated with AKS

**Task:** Attach ACR; deploy image `acrinterviewdev.azurecr.io/order-service:1.0.0`.

**Solution:**

```bash
az acr create -g rg-interview-dev -n acrinterviewdev --sku Basic
az aks update -g rg-interview-dev -n aks-interview-dev -a acrinterviewdev

docker build -t acrinterviewdev.azurecr.io/order-service:1.0.0 .
az acr login -n acrinterviewdev
docker push acrinterviewdev.azurecr.io/order-service:1.0.0

kubectl create deployment order-svc --image=acrinterviewdev.azurecr.io/order-service:1.0.0
kubectl get pods
```

**Expected output:**

```
NAME                         READY   STATUS    RESTARTS   AGE
order-svc-7d4f8b9c6d-xxxxx   1/1     Running   0          30s
```

---

### Exercise B10 — Well-Architected review

**Task:** One risk + mitigation per pillar for your AKS + SQL design.

**Solution:**

| Pillar | Risk | Mitigation |
|--------|------|------------|
| Reliability | Single AZ AKS node pool | Multi-AZ node pool + PDB |
| Security | Secrets in env vars | Key Vault + CSI driver + MI |
| Cost | Over-provisioned D4s nodes | VPA/HPA + dev shutdown schedule |
| Operational excellence | No deployment rollback tested | Helm `--atomic` + runbook |
| Performance | Cross-region SQL latency | Read replicas / cache near compute |

**Expected output:** 5 bullets you can deliver in a system-design interview in under 3 minutes.

---

## Part C — Hard (8)

### Exercise C1 — Workload Identity Federation (OIDC)

**Task:** AKS service account `order-svc` gets tokens for Key Vault without pod identity addon secrets.

**Solution:**

```bash
export AKS_OIDC_ISSUER=$(az aks show -g rg-interview-dev -n aks-interview-dev --query "oidcIssuerProfile.issuerUrl" -o tsv)

az identity federated-credential create \
  --name order-svc-federated \
  --identity-name id-order-svc \
  --resource-group rg-interview-dev \
  --issuer "$AKS_OIDC_ISSUER" \
  --subject system:serviceaccount:default:order-svc \
  --audience api://AzureADTokenExchange
```

```yaml
# pod spec
serviceAccountName: order-svc
labels:
  azure.workload.identity/use: "true"
```

**Expected output:** Pod logs show `DefaultAzureCredential` acquired token; `az keyvault secret show` equivalent from app succeeds.

---

### Exercise C2 — Hub-spoke VNet peering

**Task:** Hub `10.0.0.0/16` with Azure Firewall; spoke `10.10.0.0/16` for AKS. Allow egress only via hub.

**Solution:**

```bash
az network vnet peering create -g rg-hub --vnet-name vnet-hub -n hub-to-spoke \
  --remote-vnet $(az network vnet show -g rg-interview-dev -n vnet-interview -o tsv --query id) \
  --allow-vnet-access --allow-forwarded-traffic

az network vnet peering create -g rg-interview-dev --vnet-name vnet-interview -n spoke-to-hub \
  --remote-vnet $(az network vnet show -g rg-hub -n vnet-hub -o tsv --query id) \
  --allow-vnet-access --allow-forwarded-traffic
```

**Expected output:** AKS pod `curl https://ifconfig.me` returns firewall egress IP, not random node IP. `az network vnet peering list` shows `Connected` both directions.

---

### Exercise C3 — Durable Functions saga (compensation)

**Task:** Orchestrator: ReserveStock → Charge → Ship. Compensate on failure. Explain no JDBC in orchestrator.

**Solution:**

```csharp
[FunctionName("OrderSaga")]
public static async Task RunOrchestrator(
    [OrchestrationTrigger] IDurableOrchestrationContext ctx)
{
    var orderId = ctx.GetInput<string>();
    string reservationId = null;
    try {
        reservationId = await ctx.CallActivityAsync<string>("ReserveStock", orderId);
        await ctx.CallActivityAsync("Charge", orderId);
        await ctx.CallActivityAsync("Ship", orderId);
    } catch {
        if (reservationId != null)
            await ctx.CallActivityAsync("ReleaseStock", reservationId);
        throw;
    }
}
```

**Expected output:** Charge fails → `ReleaseStock` activity runs → orchestration status `Failed` with compensation completed.

**Senior takeaway:** Orchestrator must be deterministic and replay-safe — no `DateTime.Now`, no direct DB I/O; only activity calls.

---

### Exercise C4 — Azure Front Door + custom domain + WAF

**Task:** Route `api.example.com` to AKS ingress; block SQLi via WAF managed rule.

**Solution:**

```bash
az afd profile create -g rg-interview-dev --profile-name afd-interview --sku Standard_AzureFrontDoor
az afd endpoint create -g rg-interview-dev --profile-name afd-interview --endpoint-name api --enabled-state Enabled
# origin group → AKS public IP / internal via Private Link
az afd waf-policy create -g rg-interview-dev --policy-name waf-interview --sku Standard_AzureFrontDoor
az afd security-policy create ... --waf-policy /subscriptions/.../wafPolicies/waf-interview
```

**Expected output:**

```bash
curl -I "https://api.example.com/actuator/health"
```

```
HTTP/2 200
x-azure-ref: ...
```

Malicious `?id=1' OR '1'='1` returns `403` from WAF.

---

### Exercise C5 — Cost estimate (back-of-envelope)

**Task:** AKS 3× D4s_v3, Azure SQL 4 vCore, App Insights 20 GB/day — rough monthly USD.

**Solution:**

```
AKS control plane:     ~$73/mo (standard tier)
3× D4s_v3 (Linux):     ~3 × $140  = $420/mo
Azure SQL 4 vCore GP:  ~$500/mo (varies by region/RI)
App Insights ingestion: 20 GB/day × 30 × $2.30/GB ≈ $1,380/mo (first 5 GB free helps)
Egress (estimate):     $50–200/mo

Total ballpark:        ~$2,400–2,800/mo dev/qa (no RI, eastus)
```

**Expected output:** Interview answer within ±30% with stated assumptions (region, RI, retention).

---

### Exercise C6 — DR: geo-redundant SQL + failover group

**Task:** Primary `eastus`, secondary `westus2`; manual failover drill.

**Solution:**

```bash
az postgres flexible-server create -g rg-interview-dev -n pg-interview-east -l eastus ...
az postgres flexible-server create -g rg-interview-dev -n pg-interview-west -l westus2 ...
az postgres flexible-server failover-group create -g rg-interview-dev -n fg-interview \
  --server-name pg-interview-east --partner-server pg-interview-west

az postgres flexible-server failover-group set-primary -g rg-interview-dev -n fg-interview \
  --server-name pg-interview-west
```

**Expected output:** Connection string host changes to west endpoint; RPO per Azure docs (typically minutes of log replay); app must reconnect via failover group listener FQDN.

---

### Exercise C7 — Incident RCA: Key Vault access denied

**Task:** Pods crash with `403 Forbidden` on secret fetch after deploy. Diagnose with CLI only.

**Solution:**

```bash
# 1. Confirm secret exists
az keyvault secret show --vault-name kv-interview-dev --name db-password

# 2. Check MI principal
kubectl get sa order-svc -o yaml
az identity show -g rg-interview-dev -n id-order-svc --query principalId -o tsv

# 3. List role assignments on vault
az role assignment list --scope $(az keyvault show -n kv-interview-dev -o tsv --query id) -o table

# 4. Network — private endpoint only?
az keyvault show -n kv-interview-dev --query publicNetworkAccess -o tsv

# 5. Pod identity / workload identity labels
kubectl describe pod -l app=order-svc | grep -A5 "Azure"
```

**Root cause example:** New deployment used wrong `serviceAccountName`; MI lost `Key Vault Secrets User`.

**Fix:**

```bash
az role assignment create --assignee <principal> --role "Key Vault Secrets User" --scope <kv-id>
kubectl rollout restart deployment order-svc
```

**Expected output:** Pods `Running`; logs no longer show `403`; `kubectl logs` shows successful datasource init.

---

### Exercise C8 — Landing zone: policy + diagnostic settings

**Task:** Enforce `allowed locations = eastus,westus2` and send Activity Log to Log Analytics.

**Solution:**

```bash
az policy assignment create \
  --name allowed-locations \
  --scope /subscriptions/<sub-id> \
  --policy-set-definition /providers/Microsoft.Authorization/policySetDefinitions/... \
  --params '{"listOfAllowedLocations":{"value":["eastus","westus2"]}}'

az monitor diagnostic-settings create \
  --name send-to-law \
  --resource /subscriptions/<sub-id> \
  --workspace $(az monitor log-analytics workspace show -g rg-interview-dev -n law-interview -o tsv --query id) \
  --logs '[{"category":"Administrative","enabled":true}]'
```

**Expected output:** `az group create -l northeurope` → `RequestDisallowedByPolicy`. Portal Activity Log appears in Log Analytics within 5 minutes.

---


### Exercise A29 — Container Apps vs AKS (choose the platform)

**Task:** For each scenario, pick **Azure Container Apps (ACA)** or **AKS** and justify in one sentence.

**Solution:**

| Scenario | Choice | Why |
|----------|--------|-----|
| 3 microservices, HTTP + Dapr, scale-to-zero dev | **ACA** | Built-in KEDA scaling, no control-plane ops, per-revision traffic split |
| 50 services, custom CNI, DaemonSets, GPU nodes | **AKS** | Full Kubernetes API — sidecars, operators, node pools |
| Batch job spikes from Service Bus queue | **ACA** | KEDA `azure-servicebus` scaler; pay per vCPU-second when idle |
| Team already runs Istio + Gatekeeper cluster-wide | **AKS** | Service mesh and admission policies are first-class on K8s |
| Spring Boot monolith + minimal ops team | **ACA** | Container + ingress + secrets; no etcd upgrades |

**Decision checklist (whiteboard):**

```
Need full K8s API (CRDs, DaemonSet, CNI choice)?  → AKS
Need scale-to-zero + Dapr + simple revisions?       → ACA
Hard multi-tenant cluster isolation + own SRE?        → AKS
Event-driven autoscale without managing nodes?        → ACA
```

**Expected output:** Interview answer names **one** platform per scenario with a concrete constraint (API surface, ops burden, or scaling model) — not "it depends" alone.

**Senior takeaway:** ACA is opinionated PaaS on Kubernetes internals you don't manage; AKS is Kubernetes you operate — cost of control plane + node pools buys flexibility.

---

### Exercise A30 — Azure Monitor workbook: failed deployments

**Task:** Create a workbook query listing failed `Microsoft.Resources/deployments` in the last 24 h with resource group and error code.

**Solution:**

```bash
# Prerequisites: Log Analytics workspace receiving Activity Log via diagnostic settings
WORKSPACE_ID=$(az monitor log-analytics workspace show   -g rg-interview-dev -n law-interview --query customerId -o tsv)
```

**Workbook KQL (paste in Azure Monitor → Workbooks → New):**

```kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where OperationNameValue == "MICROSOFT.RESOURCES/DEPLOYMENTS/WRITE"
| where ActivityStatusValue == "Failed"
| project TimeGenerated,
          ResourceGroup,
          Caller,
          StatusCode = tostring(parse_json(Properties).statusCode),
          Message = tostring(parse_json(Properties).statusMessage)
| order by TimeGenerated desc
```

**Pin as tile + parameterize resource group:**

```kusto
AzureActivity
| where TimeGenerated > ago(24h)
| where ResourceGroup in ({ResourceGroup})
| where ActivityStatusValue == "Failed"
| summarize Failures = count() by ResourceGroup, bin(TimeGenerated, 1h)
| render timechart
```

**Expected output:** Workbook table shows rows like:

```
2026-09-05T14:22Z  rg-interview-dev  sp-ci-pipeline  InvalidTemplateDeployment  ...
```

Timechart spikes align with failed pipeline runs.

**Senior takeaway:** Workbooks turn KQL into shareable operational dashboards — parameterize `ResourceGroup` and `Subscription` so platform and app teams reuse one template.

---

### Exercise B29 — Azure OpenAI + Managed Identity + Private Endpoint

**Task:** Deploy Azure OpenAI with public access disabled. Call `chat/completions` from an ACA/AKS workload using **user-assigned MI** over private endpoint — no API key in env vars.

**Solution:**

```bash
RG=rg-interview-dev
LOC=eastus
VNET=vnet-interview
SUBNET=snet-private-endpoints
PE=subnet-pe-openai

# 1. OpenAI account — disable public network
az cognitiveservices account create -g $RG -n oai-interview -l $LOC   --kind OpenAI --sku S0 --custom-domain oai-interview   --public-network-access Disabled

az cognitiveservices account deployment create -g $RG -n oai-interview   --deployment-name gpt-4o-mini --model-name gpt-4o-mini --model-version "2024-07-18"   --model-format OpenAI --sku-capacity 10 --sku-name Standard

# 2. Private endpoint + DNS zone group
az network private-endpoint create -g $RG -n pe-openai --vnet-name $VNET   --subnet $PE --private-connection-resource-id $(az cognitiveservices account show -g $RG -n oai-interview -o tsv --query id)   --group-id account --connection-name openai-pe

az network private-dns zone create -g $RG -n privatelink.openai.azure.com
az network private-endpoint dns-zone-group create -g $RG -n default   --endpoint-name pe-openai --private-dns-zone privatelink.openai.azure.com --zone-name openai

# 3. User-assigned MI + RBAC (Cognitive Services OpenAI User)
az identity create -g $RG -n id-order-svc
PRINCIPAL=$(az identity show -g $RG -n id-order-svc --query principalId -o tsv)
OAI_ID=$(az cognitiveservices account show -g $RG -n oai-interview -o tsv --query id)
az role assignment create --assignee $PRINCIPAL --role "Cognitive Services OpenAI User" --scope $OAI_ID
```

**App code (DefaultAzureCredential — no secrets):**

```java
// Spring on ACA with user-assigned MI client id in env AZURE_CLIENT_ID
OpenAIClient client = new OpenAIClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("https://oai-interview.openai.azure.com/")
    .buildClient();

ChatCompletions completions = client.getChatCompletions("gpt-4o-mini",
    new ChatCompletionsOptions(List.of(new ChatRequestUserMessage("Summarize order ORD-1"))));
```

**Verify from jump box in VNet:**

```bash
curl -H "Authorization: Bearer $(az account get-access-token --resource https://cognitiveservices.azure.com -o tsv --query accessToken)"   "https://oai-interview.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-06-01"   -H "Content-Type: application/json"   -d '{"messages":[{"role":"user","content":"ping"}]}'
```

**Expected output:** Public internet curl → timeout/refused. From VNet + MI token → `200` with `"content":"..."`. No `AZURE_OPENAI_KEY` in container env.

**Senior takeaway:** Private Link removes public exfil path; MI replaces long-lived keys — RBAC scope is the OpenAI **account**, not subscription-wide Contributor.

---

### Exercise B30 — Microsoft Defender for Cloud: secure score + CI gate

**Task:** Enable Defender plans on subscription, export recommendations to Log Analytics, fail CI when critical misconfigurations appear on `order-svc` resources.

**Solution:**

```bash
# Enable Defender for Containers + CSPM (Cloud Security Posture Management)
az security pricing create --name VirtualMachines --tier Standard
az security pricing create --name Containers --tier Standard
az security pricing create --name CloudPosture --tier Standard

# Continuous export to Log Analytics
az security automation create -g rg-interview-dev -n export-defender   --location eastus   --scopes /subscriptions/<sub-id>   --actions '[{"type":"Workspace","workspace":"/subscriptions/.../law-interview"}]'
```

**CI KQL gate (Azure DevOps / GitHub Actions runs `az monitor log-analytics query`):**

```kusto
SecurityRecommendation
| where TimeGenerated > ago(1d)
| where RecommendationName contains "order" or ResourceName contains "order-svc"
| where RecommendationSeverity == "High"
| where RecommendationState == "Unhealthy"
| project RecommendationName, ResourceId, Description
```

```bash
RESULT=$(az monitor log-analytics query --workspace $WORKSPACE_ID --analytics-query "$KQL" -o tsv)
if [ -n "$RESULT" ]; then
  echo "Defender: unhealthy high recommendations on order-svc"
  exit 1
fi
```

**Remediate example finding:**

```bash
# "Azure Kubernetes Service clusters should have Defender profile enabled"
az aks update -g rg-interview-dev -n aks-interview --enable-defender --enable-azure-monitor-metrics
```

**Expected output:** Portal Secure Score rises after enabling Defender profile. CI fails with printed recommendation names until remediated; passes when `Unhealthy` count = 0.

**Senior takeaway:** Defender recommendations are policy-as-signal — wire exports to CI so drift is caught before prod deploy, not during an audit.

---

### Exercise C29 — Backup + ASR disaster recovery drill

**Task:** Protect Azure SQL (or PostgreSQL Flexible) with geo-redundant backup; replicate an AKS-adjacent VM/workload to secondary region with **Azure Site Recovery (ASR)**; run a documented failover drill and measure RTO/RPO.

**Solution:**

```bash
# --- Backup: PostgreSQL Flexible Server geo-redundant ---
az postgres flexible-server create -g rg-interview-dev -n pg-interview-east -l eastus   --sku-name Standard_D2s_v3 --tier GeneralPurpose --storage-size 128   --backup-retention 35 --geo-redundant-backup Enabled

# Point-in-time restore drill (same region)
az postgres flexible-server restore -g rg-interview-dev -n pg-interview-pitr-test   --source-server pg-interview-east --restore-time "2026-09-05T10:00:00Z"
```

```bash
# --- ASR: replicate VM (jump box / stateless worker) eastus → westus2 ---
az vm create -g rg-interview-dev -n vm-order-worker -l eastus --image Ubuntu2204 --size Standard_B2s   --vnet-name vnet-interview-east --subnet snet-compute --public-ip-address ""

VAULT_ID=$(az recoveryservices vault create -g rg-interview-dev -n rsv-interview -l westus2   --query id -o tsv)

az backup vault backup-properties set --vault-id $VAULT_ID   --backup-storage-redundancy GeoRedundant

# Enable replication (simplified — portal Replicate or ASR REST)
az site-recovery replication-protected-item create   --resource-group rg-interview-dev --vault-name rsv-interview   --fabric-name eastus-fabric --protection-container eastus-container   --policy-name 24-hour-retention-policy   --provider-specific-inputs @asr-replication.json
```

**Failover drill runbook:**

```bash
# 1. Snapshot RPO baseline
az postgres flexible-server show -g rg-interview-dev -n pg-interview-east   --query "backup.earliestRestoreDate"

# 2. Test failover (ASR test failover — non-disruptive)
az rest --method post   --url "https://management.azure.com/subscriptions/<sub>/resourceGroups/rg-interview-dev/.../testFailover?api-version=2023-06-06"

# 3. Validate app connectivity to secondary endpoints
curl -sf https://api-west.example.com/actuator/health

# 4. Failback / cleanup test network
az rest --method post .../testFailoverCleanup
```

**RTO/RPO worksheet:**

```
RPO (backup):     geo-redundant PG backup → typically ≤ 1 h data loss (confirm SLA)
RPO (ASR):        replication frequency policy (15 min / 30 min)
RTO (ASR test):   DNS cutover + app config swap — measure wall-clock from decision to health 200
RTO (PITR):       new server provision + connection string update — often 30–90 min
```

**Expected output:** Test failover VM boots in westus2 isolated network; health check passes on secondary URL. Runbook documents actual RTO (e.g. 42 min) and RPO assumptions signed by team.

**Senior takeaway:** Backup answers "restore data to a point in time"; ASR answers "keep workload alive in another region" — run **test failovers** quarterly; production failover is irreversible without a rehearsed failback plan.

---

---

## Stats

| Section | Count |
|---------|------:|
| Part A — Basic | 12 |
| Part B — Intermediate | 12 |
| Part C — Hard | 9 |
| **Total** | **33** |

**No subscription?** Complete A1–A10 command syntax on paper; do B1, B10, C5, C7 as written drills — still high interview value.
