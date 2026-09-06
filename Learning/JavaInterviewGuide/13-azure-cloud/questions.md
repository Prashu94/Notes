# Azure Cloud & Azure Functions — 55 Senior Interview Questions

**Bar:** JDs mention Azure Functions, Azure services, AKS-adjacent deploy (Helm). Speak services, identity, networking, cost, not "the cloud".

---

### 1. Azure vs AWS vocabulary map.

**Short answer:** Azure and AWS use different names for the same patterns: subscriptions vs accounts, resource groups vs tags-only grouping, Entra ID vs IAM, App Service vs Elastic Beanstalk/ECS Fargate-lite, AKS vs EKS, Functions vs Lambda, Service Bus vs SQS/SNS, Event Hubs vs Kinesis, Key Vault vs Secrets Manager, APIM vs API Gateway, Front Door vs CloudFront, Azure Monitor vs CloudWatch/X-Ray. Java teams must translate runbooks, Terraform modules, and security models—not just service names. Build a one-page cheat sheet mapping identity, compute, messaging, data, networking, and observability. When migrating a Spring Boot service, trace each AWS dependency: RDS→Azure SQL/Postgres Flexible, ElastiCache→Azure Cache for Redis, S3→Blob Storage, ALB→App Gateway or Front Door, IAM roles→managed identities. Update CI/CD secrets, SDK endpoints, and cost tags.

#### What it is
Azure and AWS use different names for the same patterns: subscriptions vs accounts, resource groups vs tags-only grouping, Entra ID vs IAM, App Service vs Elastic Beanstalk/ECS Fargate-lite, AKS vs EKS, Functions vs Lambda, Service Bus vs SQS/SNS, Event Hubs vs Kinesis, Key Vault vs Secrets Manager, APIM vs API Gateway, Front Door vs CloudFront, Azure Monitor vs CloudWatch/X-Ray. Java teams must translate runbooks, Terraform modules, and security models—not just service names. 

#### How it works (internals)
Build a one-page cheat sheet mapping identity, compute, messaging, data, networking, and observability. When migrating a Spring Boot service, trace each AWS dependency: RDS→Azure SQL/Postgres Flexible, ElastiCache→Azure Cache for Redis, S3→Blob Storage, ALB→App Gateway or Front Door, IAM roles→managed identities. Update CI/CD secrets, SDK endpoints, and cost tags. Run a pilot service end-to-end before bulk porting Terraform.

#### When to use / when NOT to use
Onboarding Java engineers from AWS-heavy shops, writing multi-cloud RFPs, or planning lift-and-shift vs refactor. Essential before estimating migration timelines or interviewing candidates who list AWS but need Azure fluency. 

#### Production example
Maintain a living vocabulary doc linked from runbooks. Standardize naming: rg-{env}-{app}, mi-{app}-{env}. Use Azure Resource Graph to inventory resources and validate tag parity with former AWS cost allocation tags. Train teams on Entra ID vs IAM mental model early—it blocks more migrations than compute differences.

#### Common mistakes
- Assuming AWS IAM role patterns map 1:1 to Azure RBAC without scoped assignments.
- Treating a subscription like an AWS account without understanding management group hierarchy.
- Using AWS region naming habits and picking wrong Azure paired regions for DR.
- Ignoring that Azure private endpoints replace many VPC endpoint patterns differently.

#### Interview follow-ups (with model answers)

**Q:** How do you explain subscription vs AWS account to a Java lead?
**A:** An Azure subscription is a billing and policy boundary—like an AWS account—but identity lives in the Entra ID tenant spanning subscriptions. Multiple subscriptions often sit under one tenant with management groups enforcing guardrails. Java apps rarely care about subscription IDs except for SDK default credential chains and deployment pipelines. Tell leads: put each environment or business unit in its own subscription or resource group stack, assign RBAC at scope, and use tags for cost—not as security boundaries. Service principals and managed identities authenticate against the tenant, then RBAC grants access per subscription or resource group.

**Q:** What is the hardest AWS-to-Azure shift for Spring teams?
**A:** Identity and secret management trip most Spring teams. On AWS, instance profiles and IAM roles feel ambient; on Azure you choose between managed identity, service principal, and federated credentials explicitly, and Key Vault references behave differently in App Service versus AKS. Second is messaging: SQS plus SNS maps awkwardly to Service Bus topics/subscriptions or Event Hubs, and Spring Cloud Stream bindings must be rewritten. Third is observability: Micrometer exports to Azure Monitor via Application Insights agents with different sampling and connection string models than X-Ray. Budget time for pipeline and local dev credential stories, not just code changes.

#### Scenario probe
**Situation:** Your team runs 40 Spring microservices on EKS with IRSA; leadership wants Azure in 12 months.

**Model answer:** I'd start with a bounded context pilot on AKS with workload identity, map each AWS service in that slice, and produce the vocabulary/runbook doc from real findings. Parallel track: landing zone, Entra app registrations, ACR, and GitHub Actions with OIDC federated credentials. Defer big-bang parity; prove observability, secret rotation, and deploy path first. Estimate remaining services using pilot ratios, not spreadsheet guesses.

#### Code / config (when useful)
```text
AWS Lambda          → Azure Functions
AWS API Gateway     → API Management (APIM) / Functions HTTP trigger
AWS EKS             → AKS
AWS Secrets Manager → Key Vault
AWS CloudFormation  → ARM / Bicep / Terraform
```

---

### 2. Subscription, resource group, tags.

**Short answer:** A subscription is the primary billing and RBAC boundary. Resource groups are lifecycle containers—all resources in a group share location metadata but can span regions. Tags are key-value metadata for cost, ownership, and automation; they do not enforce isolation. Management groups nest subscriptions for policy inheritance. Java deployments typically land in rg-{env}-{domain} with mandatory tags like env, costCenter, owner, dataClassification.

#### What it is
A subscription is the primary billing and RBAC boundary. Resource groups are lifecycle containers—all resources in a group share location metadata but can span regions. Tags are key-value metadata for cost, ownership, and automation; they do not enforce isolation. Management groups nest subscriptions for policy inheritance. Java deployments typically land in rg-{env}-{domain} with mandatory tags like env, costCenter, owner, dataClassification.

#### How it works (internals)
Define a tagging standard and enforce via Azure Policy. Use separate subscriptions per environment or per cost center depending on enterprise size. Place each deployable system (App Service plan + apps + Key Vault + storage) in one resource group for blast-radius deletion. Automate group creation in Terraform or Bicep modules. Query with Resource Graph in CI to fail builds missing tags.

#### When to use / when NOT to use
Day one of any Azure landing zone, cost chargeback discussions, and cleanup of orphaned resources after PoCs. Interviewers probe whether candidates think in lifecycle and cost, not just 'create a VM'. 

#### Production example
Use deny policies for untagged creates in production subscriptions. Lock production resource groups with CanNotDelete locks. Align resource group boundaries to team ownership and IaC repo boundaries—one state file per group or per stack. Review tag compliance monthly in Cost Management exports feeding FinOps dashboards.

#### Common mistakes
- One giant resource group for everything, making safe deletes impossible.
- Using tags as security boundaries instead of RBAC and network isolation.
- Inconsistent tag casing breaking Cost Management filters and automation.
- Mixing dev and prod resources in one subscription without policy guardrails.

#### Interview follow-ups (with model answers)

**Q:** Subscription per environment or per application?
**A:** Enterprise Java estates usually use subscription per environment (dev, test, prod) or per business unit within prod, not per microservice. Per-app subscriptions explode RBAC and policy management overhead unless you are at hyperscale with strong automation. Resource groups provide finer lifecycle grouping inside a subscription. Production subscriptions get stricter policies, peering rules, and backup requirements. Dev subscriptions allow cheaper SKUs and open outbound. For regulated workloads, separate prod subscription simplifies audit scope and prevents dev principals from ever having prod write access at subscription scope.

**Q:** How do tags integrate with Java CI/CD?
**A:** Pipeline sets tags at deploy time via Terraform, Bicep, or Azure CLI—never rely on manual portal tagging. Pass git sha, build id, and service version as tags for traceability during incidents. Azure Policy can append default tags or deny noncompliant creates. Cost Management filters by tag for showback; pairing env and costCenter tags lets finance split Spring fleet spend. Resource Graph queries in GitHub Actions can assert all compute running a release carry the expected version tag before smoke tests proceed.

#### Scenario probe
**Situation:** Finance cannot allocate Azure spend to product lines after a year of unfettered PoCs.

**Model answer:** Immediate: Resource Graph inventory, mandatory tag policy with deny on create, retroactive tag scripts where safe. Structural: management group hierarchy, subscription strategy doc, locks on prod. Long term: FinOps dashboard from Cost Management exports; tie tag compliance to CI gates so new Java services cannot deploy without owner and costCenter.

#### Code / config (when useful)
```bicep
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-orders-api-prod'
  location: 'westeurope'
  tags: {
    Environment: 'prod'
    App: 'orders-api'
    Owner: 'payments-team'
  }
}
```

---

### 3. Entra ID: tenant, app registration, service principal, managed identity.

**Short answer:** The Entra ID tenant is the identity plane for humans and workloads. App registration defines an application object (client ID, redirect URIs, API permissions). A service principal is the tenant-local instance used for authentication and RBAC assignment. Managed identity is an automatically managed service principal tied to an Azure resource—system-assigned (lifecycle-bound) or user-assigned (shared across resources). Java apps use DefaultAzureCredential to chain MI, env vars, and local dev tools.

#### What it is
The Entra ID tenant is the identity plane for humans and workloads. App registration defines an application object (client ID, redirect URIs, API permissions). A service principal is the tenant-local instance used for authentication and RBAC assignment. Managed identity is an automatically managed service principal tied to an Azure resource—system-assigned (lifecycle-bound) or user-assigned (shared across resources). Java apps use DefaultAzureCredential to chain MI, env vars, and local dev tools.

#### How it works (internals)
Register apps for third-party OAuth or CI/CD federated credentials. Prefer managed identity over client secrets for App Service, Functions, AKS workload identity, and Container Apps. Grant RBAC (e.g., Key Vault Secrets User) to the MI at appropriate scope. Locally, use Azure CLI or IntelliJ Azure plugin for developer login; never commit secrets. For Spring, use azure-identity with @ConfigurationProperties for optional client overrides in tests.

#### When to use / when NOT to use
Every production deployment accessing Key Vault, Storage, SQL with Entra auth, or calling Microsoft Graph. Core interview topic for passwordless Java on Azure. 

#### Production example
User-assigned MI per app for clearer RBAC and rotation story. Federated credentials for GitHub Actions/Azure DevOps OIDC—no long-lived secrets in pipelines. Audit service principal credentials quarterly; disable secret-based SPs where MI exists. Document which identity each microservice uses in a service catalog.

#### Common mistakes
- Client secrets in application.properties checked into git.
- Granting Contributor instead of least-privilege data plane roles.
- Using system-assigned MI everywhere then failing to recreate RBAC on redeploy.
- Confusing app registration object ID with service principal object ID in RBAC.

#### Interview follow-ups (with model answers)

**Q:** When choose service principal over managed identity?
**A:** Use service principals with federated workload identity federation when the caller is outside Azure—GitHub Actions, on-prem Jenkins, or multi-cloud—or when you need one identity shared across non-Azure and Azure resources with stable object ID. Managed identity wins for runtime inside Azure compute because Azure rotates credentials and no secret storage is required. Hybrid Spring apps on VMs without MI extension still need SP or certificate auth. For local dev, developers authenticate as themselves via Azure CLI; apps should not embed SP secrets locally—use Azurite mocks or dev Key Vault with personal access.

**Q:** How does DefaultAzureCredential work in Spring Boot?
**A:** The azure-identity library tries credentials in order: environment variables, managed identity, shared token cache, IntelliJ/Azure CLI, Azure PowerShell. In App Service and AKS with workload identity, MI succeeds in production without code changes. Locally, developers run az login and the chain picks AzureCliCredential. Configure AZURE_CLIENT_ID for user-assigned MI. Spring Cloud Azure auto-configures credential beans for Key Vault, Service Bus, and Storage. Tests use @MockBean or Testcontainers with connection strings isolated from production identity paths. Automate federated credential creation in Terraform modules so GitHub environments receive least-privilege deploy rights without copying client secrets into CI variable groups.

#### Scenario probe
**Situation:** A Java API stores Key Vault client secret in App Service settings; audit flagged critical finding.

**Model answer:** Enable system or user-assigned MI on App Service, grant Key Vault Secrets User on vault scope, switch to Key Vault references or Spring Cloud Azure Key Vault integration with DefaultAzureCredential, remove secret setting, validate deploy slot swap still resolves references, update runbook for identity-first onboarding.

#### Code / config (when useful)
```java
TokenCredential credential = new DefaultAzureCredentialBuilder().build();
SecretClient secretClient = new SecretClientBuilder()
    .vaultUrl("https://myvault.vault.azure.net/")
    .credential(credential)
    .buildClient();
```

---

### 4. RBAC vs Key Vault access policy vs Azure RBAC on KV.

**Short answer:** Azure RBAC assigns ARM/control-plane and many data-plane roles at management scope (Owner, Contributor, Key Vault Secrets User). Legacy Key Vault access policies grant vault-specific permissions to keys/secrets/certificates bypassing Azure RBAC. Key Vault supports Azure RBAC for data plane (recommended): same role model as rest of Azure. Java apps need data-plane read on secrets; operators need control-plane for vault management—not blanket Contributor. Enable 'Azure role-based access control' on new vaults.

#### What it is
Azure RBAC assigns ARM/control-plane and many data-plane roles at management scope (Owner, Contributor, Key Vault Secrets User). Legacy Key Vault access policies grant vault-specific permissions to keys/secrets/certificates bypassing Azure RBAC. Key Vault supports Azure RBAC for data plane (recommended): same role model as rest of Azure. Java apps need data-plane read on secrets; operators need control-plane for vault management—not blanket Contributor.

#### How it works (internals)
Enable 'Azure role-based access control' on new vaults. Assign Key Vault Secrets User to app managed identity at vault or individual secret scope. Use RBAC assignment via Terraform azurerm_role_assignment. For break-glass, separate admin roles from runtime. Audit with Defender for Cloud and activity logs. Migrate legacy policy vaults with dual mode during transition.

#### When to use / when NOT to use
Designing secret access for Spring fleets, compliance reviews, and troubleshooting 'access denied' despite Contributor role—Contributor does not grant secret read on RBAC-enabled vaults. 

#### Production example
One vault per environment or per domain with network ACLs and private endpoint. Purge protection and soft delete enabled. Pipeline identity gets Secrets Officer only in lower envs; prod pipeline uses limited User role on specific secrets. Document deny assignments if used.

#### Common mistakes
- Granting Contributor expecting Key Vault secret access.
- Mixing access policies and Azure RBAC causing confusing effective permissions.
- Using vault access policy model on new vaults against current Microsoft guidance.
- Forgetting RBAC propagation delay after MI creation in automated deploys.

#### Interview follow-ups (with model answers)

**Q:** Why did my Java app get 403 from Key Vault after deploy?
**A:** Common causes: RBAC not assigned to the correct service principal object ID (user-assigned MI uses its own SP), assignment at wrong scope (resource group vs vault), vault firewall blocking App Service outbound IPs without VNet integration, or using access-policy vault while assigning Azure RBAC roles only. Contributor on subscription does not include secrets get permission on RBAC vaults. Verify with az role assignment list and Key Vault diagnostic logs. Allow five to ten minutes for RBAC propagation; retry logic in app startup should backoff. Confirm DefaultAzureCredential picks MI in App Service via AZURE_CLIENT_ID if user-assigned.

**Q:** Access policy vaults still in enterprise—migration approach?
**A:** Inventory vaults and callers—Java apps, Functions, pipelines. Enable Azure RBAC on vault alongside policies during coexistence window per Microsoft docs, map policy permissions to least-privilege roles (Secrets User, Crypto User), assign roles to each MI and pipeline SP, integration test all services, remove policy entries, switch vault to RBAC-only mode. Automate detection of legacy vaults via Azure Policy. Prioritize vaults with the most Java consumers and strictest audit requirements first; avoid big-bang cutover without slot-based validation. During migration from access policies, run parallel integration tests from every Java consumer before removing legacy policy entries, preventing a weekend outage when one batch job still used policy auth.

#### Scenario probe
**Situation:** Platform team gave microservices Contributor on production subscription for 'simplicity'.

**Model answer:** Revoke broad Contributor; assign per-service MI with Key Vault Secrets User, Storage Blob Data Contributor, and specific SQL Entra roles. Use Azure Policy deny on Contributor assignments to app identities. Provide break-glass PIM-eligible Owner for humans. Measure reduced blast radius in incident tabletop—any compromised pod should not mutate unrelated resources.

#### Code / config (when useful)
```bash
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee-object-id <mi-object-id> \
  --scope /subscriptions/.../providers/Microsoft.KeyVault/vaults/kv-orders-prod
```

---

### 5. App Service vs AKS vs Container Apps vs Functions.

**Short answer:** App Service: PaaS for JAR/WAR deploy, slots, easy ops, limited K8s control. AKS: full Kubernetes for complex microservices, service mesh, custom operators—highest ops burden. Container Apps: K8s-backed serverless containers, scale-to-zero, KEDA, simpler than AKS. Functions: event-driven snippets; Java cold starts and programming model limit enterprise use. Spring Boot teams usually pick App Service for modest services, AKS/ACA for container-native fleets, Functions for integration glue.

#### What it is
App Service: PaaS for JAR/WAR deploy, slots, easy ops, limited K8s control. AKS: full Kubernetes for complex microservices, service mesh, custom operators—highest ops burden. Container Apps: K8s-backed serverless containers, scale-to-zero, KEDA, simpler than AKS. Functions: event-driven snippets; Java cold starts and programming model limit enterprise use. Spring Boot teams usually pick App Service for modest services, AKS/ACA for container-native fleets, Functions for integration glue.

#### How it works (internals)
Decision matrix: team K8s skill, scaling pattern, networking (VNet integration), startup time, deployment frequency, and observability needs. Prototype latency and cost on candidate platform. For Spring, measure memory footprint on App Service P1v3 vs ACA vs AKS node pool sizing. Use Azure pricing calculator with autoscale profiles.

#### When to use / when NOT to use
Architecture reviews for new Java microservices, replatforming from on-prem Tomcat, or consolidating Functions sprawl into Container Apps. 

#### Production example
Standardize on two allowed platforms per org tier—e.g., App Service for internal CRUD APIs, AKS for high-scale event-driven systems. Container Apps for event-driven containers without cluster ops. Avoid Functions for heavy Spring context unless isolated triggers with Premium plan. 

#### Common mistakes
- Running full Spring Boot on Consumption Functions with unacceptable cold starts.
- Choosing AKS for three simple REST services without platform team capacity.
- Ignoring VNet requirements until late—App Service integration differs from ACA.
- Assuming Container Apps eliminates all Kubernetes knowledge for ingress and secrets.

#### Interview follow-ups (with model answers)

**Q:** When is App Service enough for Spring Boot?
**A:** App Service fits stateless HTTP APIs and moderate background jobs with built-in deployment slots, autoscale, Easy Auth, and Key Vault references when you do not need pod-level scheduling, sidecars, or custom CNI. Spring Boot 3 apps with 512MB–2GB heap run well on P1v3+ with always-on enabled. Choose AKS or ACA when you need gRPC service mesh, multi-container pods, GPU, strict network policies, or unified platform with non-Java workloads. App Service Java SE stack simplifies ops but hides less of the JVM tuning than containers—you still configure JAVA_OPTS and Application Insights agent.

**Q:** Container Apps vs AKS for a 15-service Spring fleet?
**A:** If you lack dedicated platform SREs and services are independently deployable HTTP/event consumers, Container Apps reduces control-plane toil—managed env, KEDA scaling, internal ingress. AKS wins when you need cluster-wide policies, custom CRDs, service mesh, Windows nodes, or multi-tenant cluster sharing with strict isolation. Cost: ACA can be cheaper at low baseline with scale-to-zero; AKS has cluster overhead but better at steady high throughput. Hybrid pattern: ACA for edge adapters, AKS for core domain services is common during migration. Revisit the matrix when traffic doubles or compliance adds private-link requirements, since App Service integrations differ materially from Container Apps networking as estates mature.

#### Scenario probe
**Situation:** Product wants serverless; team proposes rewriting Spring monolith as 200 Azure Functions.

**Model answer:** Push back with TCO and cold-start data: keep domain API on App Service or ACA, use Functions for discrete triggers (blob, timer, queue fan-out). Present decision matrix to leadership; pilot one bounded module on ACA with KEDA before committing to Functions-for-everything.

#### Code / config (when useful)
```text
Spring REST API (steady traffic)     → App Service Premium + VNet
Multi-service platform + Helm        → AKS
Scale-to-zero microservices          → Container Apps + KEDA
Queue/timer/blob glue                → Functions Premium
```

---

### 6. Azure Functions: hosting plans.

**Short answer:** Consumption: pay-per-execution, cold starts, 10-minute max timeout on default, no VNet on classic model. Premium (Elastic Premium): pre-warmed instances, VNet integration, longer runs, better for Java. Dedicated (App Service plan): runs on your ASP, predictable cost, always-on. Flex Consumption: newer model with improved scaling. Container Apps can host functions-style workloads with different ops model.

#### What it is
Consumption: pay-per-execution, cold starts, 10-minute max timeout on default, no VNet on classic model. Premium (Elastic Premium): pre-warmed instances, VNet integration, longer runs, better for Java. Dedicated (App Service plan): runs on your ASP, predictable cost, always-on. Flex Consumption: newer model with improved scaling. Container Apps can host functions-style workloads with different ops model. Java on Consumption is rarely acceptable for user-facing latency.

#### How it works (internals)
Profile cold start with Application Insights dependencies. Choose Premium EP1+ with minimum instances > 0 for Java. Set FUNCTIONS_WORKER_RUNTIME=java and align extension bundle. Configure host.json for timeout and concurrency. Use Application Insights sampling. For Spring-like workloads, prefer App Service or ACA instead.

#### When to use / when NOT to use
Designing event processors, evaluating serverless cost vs always-on, or explaining why Java team rejected Consumption for APIs. 

#### Production example
Premium plan with pre-warmed instances in prod; Consumption only for async batch with SLA tolerance. Monitor execution units and memory—Java heap settings via JAVA_OPTS on Premium/Dedicated. Set max concurrent calls per instance to avoid OOM. 

#### Common mistakes
- Consumption plan for synchronous HTTP APIs with Spring dependencies.
- Undersizing Premium EP1 for fat JAR deployments causing GC thrash.
- Ignoring VNet requirement until integration with private SQL fails.
- Not setting minimum instances on Premium—defeats warm pool benefit.

#### Interview follow-ups (with model answers)

**Q:** How do you size Premium plan for Java Functions?
**A:** Measure packaged artifact size, startup time, and steady-state heap under load test. EP1 (single core, 3.5GB) suits light handlers; heavier Spring-adjacent libraries need EP2+. Set minimum instance count to cover baseline RPS and eliminate cold start for warm path. Watch Application Insights 'cold start' metric and GC pauses. Concurrency host.json settings multiply memory pressure—lower maxConcurrentRequestsPerInstance if each invocation loads large object graphs. Cost trade-off: always-warm EP1 often beats Consumption plus angry users when p99 latency matters for business workflows. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Dedicated plan vs Premium for internal batch jobs?
**A:** Dedicated (existing App Service plan) makes sense when you already pay for unused capacity on a shared ASP running web apps—Functions become another site on same plan with no cold start if always-on. Premium adds elastic scale-out for spiky queues and native VNet integration without sharing web app noisy neighbors. For nightly Java batch with predictable duration and fixed throughput, Dedicated on B-series ASP can be cheapest. For Event Hub-driven bursty ETL, Premium elastic scale wins. Document choice in ADR with cost snapshot from Azure Monitor metrics over two weeks.

#### Scenario probe
**Situation:** Java Function on Consumption hits 30s cold starts; product owner escalates.

**Model answer:** Move HTTP trigger to Premium with min instances=1 or refactor to Container Apps/Java microservice. Short term: enable run from package, trim dependencies, use Graal native only if team has capacity. Show p95 latency before/after in App Insights to stakeholders.

#### Code / config (when useful)
```json
{
  "version": "2.0",
  "functionTimeout": "00:30:00",
  "extensions": { "http": { "routePrefix": "api" } }
}
```

---

### 7. Functions triggers and bindings.

**Short answer:** Triggers start execution: HTTP, Timer, Queue/Service Bus, Event Hub, Blob, Cosmos DB change feed, Event Grid. Bindings declare input/output data connections declaratively in function.json or annotations (@QueueTrigger, @CosmosDBOutput). Bindings reduce boilerplate but Java annotation support lags C#. Extension bundles version must match trigger types. Durable Functions adds orchestration triggers.

#### What it is
Triggers start execution: HTTP, Timer, Queue/Service Bus, Event Hub, Blob, Cosmos DB change feed, Event Grid. Bindings declare input/output data connections declaratively in function.json or annotations (@QueueTrigger, @CosmosDBOutput). Bindings reduce boilerplate but Java annotation support lags C#. Extension bundles version must match trigger types. Durable Functions adds orchestration triggers.

#### How it works (internals)
Define trigger in annotations or function.json; configure connection strings or identity-based connections in local.settings.json and application settings. Use identity connections (AzureWebJobsStorage via MI) where supported. Test locally with Azurite and Service Bus emulator. Version-lock extension bundle in host.json for reproducible deploys.

#### When to use / when NOT to use
Building integration adapters, IoT ingest, file processing pipelines—not primary choice for complex Spring domain logic. 

#### Production example
Prefer identity over connection strings; store settings in Key Vault references. Idempotent handlers with poison queue handling. Set retry policies in host.json and Service Bus lock duration appropriately. Monitor dead-letter queues and binding failures in App Insights.

#### Common mistakes
- Long synchronous work in Service Bus trigger without maxAutoLockRenewal.
- Binding to production storage account from dev laptop via shared keys.
- Mixing incompatible extension bundle versions after portal edits.
- Omitting output bindings and opening SDK clients manually anyway.

#### Interview follow-ups (with model answers)

**Q:** How do bindings compare to Spring Cloud Stream?
**A:** Bindings are declarative wiring at the Functions runtime level—good for single-purpose handlers with minimal DI. Spring Cloud Stream offers richer programming model, testability, and binder abstraction across Kafka, Service Bus, and Rabbit in one Spring Boot app. For enterprise Java teams already standardized on Spring, a Boot service on ACA or AKS with Stream often beats splitting logic across dozens of Function classes. Functions bindings win for small Azure-native glue where ops wants zero container management and handler fits in one class with few dependencies.

**Q:** Identity-based connections for Service Bus trigger?
**A:** Configure ServiceBusConnection__fullyQualifiedNamespace and assign Azure Service Bus Data Receiver role to function MI. Remove shared access keys from settings. In local dev, use Azurite equivalent patterns or developer credential via connection string in local.settings only. In host.json set retry and prefetch tuned for Java handler duration. Validate lock renewal if processing exceeds default lock—call renew via Service Bus SDK inside function or reduce batch size. Pipeline should fail if legacy connection string keys detected in prod slot settings. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Blob-triggered virus scan Function times out on large files.

**Model answer:** Increase function timeout on Premium, chunk processing via streaming, or move to Container Apps job with longer deadline. Use Event Grid blob created event to queue work item instead of heavy sync in trigger. Add DLQ and size threshold guard in metadata check.

#### Code / config (when useful)
```java
@FunctionName("ProcessOrder")
public void run(
    @ServiceBusQueueTrigger(name = "msg", queueName = "orders", connection = "ServiceBusConnection") String message,
    @CosmosDBOutput(name = "output", databaseName = "orders", containerName = "events", connection = "CosmosConnection")
    OutputBinding<OrderEvent> output) { }
```

---

### 8. Durable Functions.

**Short answer:** Extension implementing saga/orchestrator pattern: orchestrator functions coordinate activity functions with durable task hub backed by Azure Storage or Netherite. Supports timers, human approval, fan-out/fan-in, compensation. Java support exists but ecosystem and samples skew .NET. Useful for order workflows, document pipelines, and retry-heavy multi-step integrations without maintaining own state store. Add durable-task extension to host.json; define orchestrator with callActivity patterns; activities perform I/O.

#### What it is
Extension implementing saga/orchestrator pattern: orchestrator functions coordinate activity functions with durable task hub backed by Azure Storage or Netherite. Supports timers, human approval, fan-out/fan-in, compensation. Java support exists but ecosystem and samples skew .NET. Useful for order workflows, document pipelines, and retry-heavy multi-step integrations without maintaining own state store.

#### How it works (internals)
Add durable-task extension to host.json; define orchestrator with callActivity patterns; activities perform I/O. Configure task hub storage with MI. Use deterministic orchestrator code—no random or direct I/O in orchestrator. Version orchestrations for breaking changes. Monitor in Durable Functions monitoring blades and App Insights.

#### When to use / when NOT to use
Multi-step business processes with hours/days duration and built-in replay semantics—evaluate against Temporal or Spring Batch on ACA if team lacks .NET-oriented durable ops experience. 

#### Production example
Separate storage account for task hub from application data. Set appropriate concurrency throttles. Implement idempotent activities. Alert on orchestration failures and stuck instances. Consider Temporal/AKS if Java team needs first-class workflow DSL and ops maturity.

#### Common mistakes
- Non-deterministic code in orchestrator breaking replay.
- Sharing task hub storage with high-churn blob data causing throttling.
- Using Durable for simple queue processing better handled by Service Bus.
- Underestimating Java sample gap vs .NET for complex patterns.

#### Interview follow-ups (with model answers)

**Q:** Durable Functions vs Temporal for Java orchestration?
**A:** Temporal offers stronger Java SDK, explicit workflow code, and growing enterprise adoption for sagas spanning microservices. Durable Functions keeps orchestration inside Azure Functions billing and storage primitives—lower infra if already Functions-heavy but weaker Java ergonomics and debugging. Choose Durable when workflows are Azure-centric, step count modest, and ops team prefers Functions monitoring. Choose Temporal on AKS when workflows cross many services, need versioning discipline, and Java developers want unit-testable workflow logic without replay quirks. Hybrid: Durable orchestrator calling Spring APIs as activities.

**Q:** What storage backend for production task hub?
**A:** Default Azure Storage task hub works for most loads; watch transaction throttling on busy orchestrations. Netherite on Event Hubs targets higher throughput with different scaling characteristics—evaluate if orchestration fan-out creates storage bottlenecks. Use dedicated storage account with lifecycle management, MI access, and private endpoint if compliance requires. Backup task hub metadata understanding replay implications. Load test fan-out pattern representative of production peak before go-live; storage limits manifest as orchestration timeouts hard to diagnose without proper dashboards. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Order fulfillment needs 3-day workflow with human approval steps.

**Model answer:** Prototype Durable with external event (approval webhook) pattern; parallel estimate Temporal if Java team owns long-term maintenance. ADR comparing ops cost, test strategy, and vendor lock-in. Start with one non-critical workflow, instrument each activity with correlation IDs into App Insights.

#### Code / config (when useful)
```java
@FunctionName("OrderOrchestrator")
public String orderOrchestrator(@DurableOrchestrationTrigger(name = "ctx") TaskOrchestrationContext ctx) {
    String orderId = ctx.getInput(String.class);
    ctx.callActivity("ValidateOrder", orderId).await();
    ctx.callActivity("ChargePayment", orderId).await();
    return "DONE";
}
```

---

### 9. Why Java Functions can disappoint.

**Short answer:** Cold starts loading JVM and Spring-like libraries are slow on Consumption. Annotation/bindings maturity lags .NET/Node. Threading and concurrency model differs; debugging locally vs cloud inconsistent. Package size limits and deployment slot quirks. Graal native helps but adds build complexity.

#### What it is
Cold starts loading JVM and Spring-like libraries are slow on Consumption. Annotation/bindings maturity lags .NET/Node. Threading and concurrency model differs; debugging locally vs cloud inconsistent. Package size limits and deployment slot quirks. Graal native helps but adds build complexity. Microsoft samples and enterprise references skew non-Java. Teams expect Lambda+Java parity and hit latency and DX gaps.

#### How it works (internals)
Set expectations early with measured cold/warm timings. Minimize dependencies; avoid pulling full Spring context. Use Premium/EP with min instances. Consider isolate integration in Functions, core domain on App Service/ACA. Evaluate Quarkus/Micronaut native for specific handlers only with ROI proof.

#### When to use / when NOT to use
Architecture gate reviews before committing Java to Functions; post-mortems on failed serverless Java initiatives. 

#### Production example
If Java Functions remain, strict lint on dependency count, enforced Premium tier, automated perf gates in CI comparing startup time regression. Prefer non-Java for tiny functions; Java for shared library reuse only when justified. 

#### Common mistakes
- Porting Spring Boot app wholesale into a Function entrypoint.
- Ignoring Application Insights cold start telemetry in sprint reviews.
- Choosing Consumption because dev laptop tests felt fast after first warm.
- No fallback architecture when p99 SLA missed after launch.

#### Interview follow-ups (with model answers)

**Q:** Can GraalVM native fix Java Functions?
**A:** Native images cut cold start dramatically for small handlers but increase build time, restrict reflection used by many Java libraries, and complicate troubleshooting. Azure Functions Java native support evolves—verify current runtime compatibility before committing. Suitable for stable, narrow handlers without heavy dynamic class loading. Not a drop-in for typical Spring Boot fat JAR. Pilot one handler, measure build pipeline minutes and production memory footprint; native often shifts cost from latency to CI and developer iteration speed. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** What workloads still make sense for Java Functions?
**A:** Small Service Bus or Event Hub consumers doing transformation with minimal deps, timer-trigger housekeeping calling ARM or Graph APIs, and glue where JVM needed for shared crypto or parsing library already owned by Java team. Avoid HTTP-facing user APIs and long-lived connections. If handler needs Spring DI, JDBC pool, and 50 beans, move to Container Apps. Good rule: startup under five seconds warm, under one second ideally, artifact under 50MB, no full Spring context—otherwise reconsider platform. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** CTO mandates Functions-first; Java team threatens to quit.

**Model answer:** Facilitate data-driven workshop: demo cold starts, show ACA/App Service deploy parity with existing Spring CI, propose tiered policy—Functions for integration, containers for domain. Align on measurable SLOs; let platform team own reference architectures not slogans.

#### Code / config (when useful)
```xml
<dependency>
  <groupId>com.microsoft.azure.functions</groupId>
  <artifactId>azure-functions-java-library</artifactId>
</dependency>
```

---

### 10. API Management (APIM).

**Short answer:** Fully managed API gateway: import OpenAPI from App Service/AKS backends, apply policies (rate limit, JWT validate, rewrite, cache), developer portal, versioning, products/subscriptions. Tiers: Developer, Basic, Standard, Premium (VNet injection). Replaces or complements in-cluster ingress for external API consumers. Integrates with Entra ID, Application Insights, and Key Vault for named values. Deploy APIM, import APIs via Terraform azurerm_api_management_api, configure backend pointing to internal load balancer or App Service.

#### What it is
Fully managed API gateway: import OpenAPI from App Service/AKS backends, apply policies (rate limit, JWT validate, rewrite, cache), developer portal, versioning, products/subscriptions. Tiers: Developer, Basic, Standard, Premium (VNet injection). Replaces or complements in-cluster ingress for external API consumers. Integrates with Entra ID, Application Insights, and Key Vault for named values.

#### How it works (internals)
Deploy APIM, import APIs via Terraform azurerm_api_management_api, configure backend pointing to internal load balancer or App Service. Policies in XML or policy fragments for reuse. Enable Application Insights diagnostics. Use internal VNet mode for private backends. Cache GET responses where safe. Mutual TLS for B2B partners on Premium.

#### When to use / when NOT to use
External partner APIs, centralized auth/rate limits across many Spring services, legacy SOAP/REST mediation, or hiding internal cluster topology. 

#### Production example
Separate APIM per environment; store secrets in Key Vault named values. CI/CD policy promotion with diff review. Monitor backend latency vs gateway overhead. Disaster: secondary region Premium with Traffic Manager or Front Door origin failover.

#### Common mistakes
- APIM Basic without VNet exposing internal backends publicly.
- Copy-paste policies breaking JWT audience for multi-tenant apps.
- Caching authenticated responses without Vary headers.
- Skipping backend circuit breaker configuration during peak events.

#### Interview follow-ups (with model answers)

**Q:** APIM vs Spring Cloud Gateway in AKS?
**A:** Spring Cloud Gateway inside cluster gives developers code-first filters, service discovery integration, and no per-call APIM cost—good for internal east-west traffic. APIM excels at external API products, billing subscriptions, developer portal, and centralized policy without redeploying Java services. Common pattern: SCG for internal mesh edge, APIM for north-south partner traffic. Premium APIM VNet inject reaches private AKS ingress IP. Avoid running duplicate rate limiting at both layers without coordination—pick authoritative enforcement point. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** How validate JWT from Entra in APIM?
**A:** Use validate-jwt policy with openid-config URL of tenant, set required aud and iss claims matching Spring resource server configuration. Map roles claim to APIM products if needed. For multiple audiences, policy fragments per API. Test with expired and wrong-tenant tokens in CI contract tests hitting APIM dev tier. Align clock skew and signing key rotation with Spring Security OAuth2 resource server settings so gateway and service reject consistently—mismatch causes confusing 401 only at one hop. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Partners hit rate limits unevenly; three Spring services expose duplicate public URLs.

**Model answer:** Consolidate behind APIM with product-based subscriptions, unified OpenAPI, backend pools weighted by deployment. Move DNS to APIM custom domain; deprecate direct App Service URLs via firewall. Add App Insights correlation from APIM to backend via trace headers.

#### Code / config (when useful)
```xml
<inbound>
  <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
    <openid-config url="https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration" />
    <audiences><audience>api://orders-api</audience></audiences>
  </validate-jwt>
  <rate-limit calls="100" renewal-period="60" />
</inbound>
```

---

### 11. Application Gateway vs Front Door vs Load Balancer vs Traffic Manager.

**Short answer:** Azure Load Balancer: L4 TCP/UDP, regional, for AKS/API internal distribution. Application Gateway: L7 HTTP(S), WAF, path-based routing, regional, often AKS ingress. Azure Front Door: global L7 CDN/WAF, anycast edge, best for multi-region public HTTP. Traffic Manager: DNS-based global routing (priority, weighted, performance)—not a proxy. Java Spring apps typically: LB for internal gRPC/TCP, App Gateway or NGINX ingress for regional HTTP, Front Door for global users.

#### What it is
Azure Load Balancer: L4 TCP/UDP, regional, for AKS/API internal distribution. Application Gateway: L7 HTTP(S), WAF, path-based routing, regional, often AKS ingress. Azure Front Door: global L7 CDN/WAF, anycast edge, best for multi-region public HTTP. Traffic Manager: DNS-based global routing (priority, weighted, performance)—not a proxy. Java Spring apps typically: LB for internal gRPC/TCP, App Gateway or NGINX ingress for regional HTTP, Front Door for global users.

#### How it works (internals)
Map traffic patterns: single region vs global, TLS termination point, WAF requirements. AKS: install AGIC or NGINX plus optional Front Door origin to ingress IP. Health probes must hit Spring Actuator /health. Configure connection draining on deploys. Use Private Link origins with Front Door Premium where needed.

#### When to use / when NOT to use
Designing public API entry, multi-region failover, or replacing on-prem F5. Common interview trap: picking Traffic Manager expecting HTTP features. 

#### Production example
Front Door Standard/Premium with WAF managed rules for public SaaS; App Gateway WAF v2 for single-region with VNet integration. Document probe paths and timeout alignment with Spring startup during rolling updates. Separate staging Front Door endpoint or routing rules. 

#### Common mistakes
- Traffic Manager alone without health-aware origins at HTTP layer.
- App Gateway probe hitting wrong Actuator path causing flapping during deploy.
- Double TLS termination breaking client cert auth to Spring.
- Front Door caching dynamic authenticated API responses.

#### Interview follow-ups (with model answers)

**Q:** Front Door vs App Gateway for single-region Spring API?
**A:** Single region with users mostly local: App Gateway WAF v2 or in-cluster ingress is simpler and cheaper—direct VNet integration to AKS. Front Door adds value with global edge, DDoS at scale, and unified WAF across regions. If you plan multi-region within a year, Front Door early avoids re-DNS later. For internal-only APIs, neither—use internal LB plus private DNS. Cost-sensitive internal microservices often use NGINX ingress with cert-manager only. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** How configure health probes for Spring Boot on AKS?
**A:** Expose management port or separate management.server.port for /actuator/health/liveness and /readiness with K8s probes mirroring App Gateway settings. Probes should validate datasource and critical dependencies on readiness only—liveness stays lightweight. Set App Gateway probe interval and unhealthy threshold above pod startup time to survive slow JVM boots. During deploy, use preStop sleep and graceful shutdown in Spring so in-flight requests drain before pod kill. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Global Java SaaS needs WAF and failover; architect proposes Traffic Manager only.

**Model answer:** Clarify TM is DNS routing only—pair with Front Door or regional App Gateways as origins, health probes, and WAF at HTTP layer. Draw path: user→Front Door→origin pool per region→AKS ingress→Spring pods. Estimate cost and latency vs active-active requirements.

#### Code / config (when useful)
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
spec:
  rules:
    - host: api.contoso.com
      http:
        paths:
          - path: /orders
            pathType: Prefix
            backend:
              service:
                name: orders-api
                port:
                  number: 8080
```

---

### 12. AKS: node pools, CNI, ingress.

**Short answer:** Node pools: VM scale sets backing Kubernetes nodes; system pool vs user pool separation. Azure CNI assigns VNet IPs to pods (advanced networking) vs kubenet NAT overlay. Ingress: NGINX, AGIC (Application Gateway), or service mesh gateways expose Spring services. Cluster autoscaler and pod disruption budgets affect Java rolling deploys. Taints/tolerations isolate batch vs API pools.

#### What it is
Node pools: VM scale sets backing Kubernetes nodes; system pool vs user pool separation. Azure CNI assigns VNet IPs to pods (advanced networking) vs kubenet NAT overlay. Ingress: NGINX, AGIC (Application Gateway), or service mesh gateways expose Spring services. Cluster autoscaler and pod disruption budgets affect Java rolling deploys. Taints/tolerations isolate batch vs API pools.

#### How it works (internals)
Design IP plan for Azure CNI—pods consume subnet IPs. Create user node pool for Java apps with appropriate VM SKU (memory for heap). Install ingress controller via Helm; annotate services. Use cert-manager for TLS. Configure CPU/memory requests from JVM container awareness (-XX:MaxRAMPercentage). Enable workload identity for Key Vault and SQL.

#### When to use / when NOT to use
Production Kubernetes design interviews, troubleshooting pod scheduling failures, or planning private cluster connectivity. 

#### Production example
Dedicated user pool per environment tier; system pool untainted minimal. Monitor IP exhaustion on CNI subnets. Pod anti-affinity for critical APIs. Horizontal Pod Autoscaler on CPU/custom metrics from Micrometer. Regular node image upgrades via surge pools.

#### Common mistakes
- Undersized subnet for Azure CNI causing pod schedule failures at scale.
- Running Java without heap limits aligned to container memory requests.
- Single node pool mixing system and heavy Java workloads.
- Ingress controller without PodDisruptionBudget during node drain.

#### Interview follow-ups (with model answers)

**Q:** Azure CNI vs kubenet for Spring microservices?
**A:** Azure CNI gives pods real VNet IPs—required for many private endpoint scenarios, network policies with precise IP rules, and on-prem routing via ExpressRoute. kubenet conserves IPs with overlay but complicates some peering and observability of pod IPs. Enterprise Java estates on private SQL and Key Vault via private link usually choose Azure CNI with careful subnet sizing—/23 may be too small for 200-pod fleet. Plan IPAM with platform team before cluster create; expanding CNI subnets is painful. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** AGIC vs NGINX ingress for Java APIs?
**A:** Application Gateway Ingress Controller integrates Azure WAF and native App Gateway features—good when security mandates WAF outside cluster and ops prefers Azure-native tooling. NGINX ingress is flexible, widely known by Java teams, works with cert-manager and external-dns patterns. Service mesh (Istio) adds mTLS east-west at complexity cost. Pick AGIC when WAF compliance is non-negotiable and L7 routing stays moderate; NGINX when team wants portable Kubernetes skills and rich annotations. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** New pods fail with 'no IP addresses available' during Black Friday scale-up.

**Model answer:** Emergency: add node pool in new subnet or switch scaling to larger nodes fewer pods; long term: expand VNet subnet, review max pods per node settings, implement IP monitoring alert. Post-incident: capacity model linking HPA max replicas to IP math.

#### Code / config (when useful)
```bash
az aks create --name aks-orders-prod --node-count 3 \
  --network-plugin azure --network-policy azure --enable-managed-identity
```

---

### 13. Workload identity vs pod identity (legacy).

**Short answer:** Workload identity federates Kubernetes service account (KSA) to Entra ID user-assigned managed identity via OIDC issuer on AKS—Microsoft recommended. Legacy aad-pod-identity (NMI) intercepted metadata traffic—being retired. Java apps use DefaultAzureCredential or Spring Cloud Azure with workload identity enabled on cluster and labeled namespaces. Eliminates secrets for Key Vault, Storage, Service Bus. Enable OIDC issuer and workload identity on AKS.

#### What it is
Workload identity federates Kubernetes service account (KSA) to Entra ID user-assigned managed identity via OIDC issuer on AKS—Microsoft recommended. Legacy aad-pod-identity (NMI) intercepted metadata traffic—being retired. Java apps use DefaultAzureCredential or Spring Cloud Azure with workload identity enabled on cluster and labeled namespaces. Eliminates secrets for Key Vault, Storage, Service Bus.

#### How it works (internals)
Enable OIDC issuer and workload identity on AKS. Create user-assigned MI, federated credential trusting KSA subject. Annotate KSA with azure.workload.identity/client-id; label pod template. Assign RBAC roles to MI. Verify with az identity federated-credential and pod logs.

#### When to use / when NOT to use
Any new AKS Java deployment accessing Azure data plane; migration off pod identity or mounted secrets. 

#### Production example
One MI per microservice or per domain—not one super-MI for cluster. Automate KSA+MI binding in Helm chart values per env. Deny pods without workload identity label in prod via Azure Policy for Kubernetes. Audit role assignments quarterly.

#### Common mistakes
- Using deprecated pod identity on new clusters.
- Wrong federated credential subject mismatching namespace/service account.
- Granting subscription-wide roles to shared MI.
- Forgetting to restart pods after RBAC assignment propagation.

#### Interview follow-ups (with model answers)

**Q:** How configure Spring Boot for workload identity?
**A:** Enable Spring Cloud Azure with credential managed-identity-enabled and set AZURE_CLIENT_ID to user-assigned MI client id. Ensure pod service account matches federated credential. DefaultAzureCredential picks workload identity token file injected by AKS. Remove Key Vault connection strings from application.yml—use property source from Key Vault with MI auth. Local dev uses Azure CLI credential chain. Integration tests in CI may use service principal with federated GitHub OIDC separate from runtime MI. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Migration steps from pod identity to workload identity?
**A:** Inventory NMI annotations and identities per deployment. Enable workload identity on cluster alongside NMI during transition. For each Java service create federated credential, update Helm charts with service account labels, deploy to staging, validate Key Vault and SQL access, cut over prod with rolling update, remove NMI DaemonSet when all workloads migrated. Microsoft provides migration guide timelines—plan before NMI end-of-life blocks AKS upgrades. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Java pod logs show ManagedIdentityCredential authentication failed after AKS upgrade.

**Model answer:** Verify OIDC issuer URL in federated credential matches cluster, KSA annotation client-id correct, RBAC on MI present, and Spring using DefaultAzureCredential not stale client secret env var. Compare working staging pod YAML to prod; check namespace label azure.workload.identity/use.

#### Code / config (when useful)
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orders-api
  namespace: orders
  annotations:
    azure.workload.identity/client-id: "<user-assigned-mi-client-id>"
```

---

### 14. Azure SQL vs Postgres Flexible vs Cosmos vs Redis.

**Short answer:** Azure SQL: managed SQL Server, strong enterprise JDBC/Spring Data JPA fit, Entra auth, geo-replication. PostgreSQL Flexible Server: open-source, Spring support, lower cost for many workloads. Cosmos DB: global multi-model, partition key design critical, SDK differs from JDBC except PostgreSQL API limited. Azure Cache for Redis: session cache, rate counters, pub/sub—not primary database. Java teams default relational unless scale/geo/schema flexibility demands Cosmos.

#### What it is
Azure SQL: managed SQL Server, strong enterprise JDBC/Spring Data JPA fit, Entra auth, geo-replication. PostgreSQL Flexible Server: open-source, Spring support, lower cost for many workloads. Cosmos DB: global multi-model, partition key design critical, SDK differs from JDBC except PostgreSQL API limited. Azure Cache for Redis: session cache, rate counters, pub/sub—not primary database. Java teams default relational unless scale/geo/schema flexibility demands Cosmos.

#### How it works (internals)
Model access patterns first. Use Azure SQL or Postgres with Flyway/Liquibase in Spring Boot. Cosmos when global low-latency reads, elastic scale, or document model dominate—use Spring Data Cosmos SDK. Redis via Spring Cache abstraction with Lettuce driver; configure SSL and Entra where supported. Private endpoints for all prod data planes.

#### When to use / when NOT to use
Data layer architecture interviews, migration from self-hosted Oracle/SQL Server, or fixing wrong store choice (Cosmos as relational replacement). 

#### Production example
HA tiers: SQL Business Critical, Postgres zone redundant. Connection pooling via HikariCP sized to DB limits. Read replicas for reporting. Redis Premium with persistence for critical cache; cluster mode for large heap session stores.

#### Common mistakes
- Cosmos chosen without partition key strategy causing hot partitions.
- Redis as sole persistence without durability plan.
- Opening DB firewall to 0.0.0.0 instead of private link.
- Oversized Hikari pool exhausting SQL connection limits across pods.

#### Interview follow-ups (with model answers)

**Q:** Azure SQL vs Postgres Flexible for new Spring Boot service?
**A:** Choose Azure SQL when team knows T-SQL, needs SQL Server features, Windows-integrated tooling, or existing geo-dr patterns on SQL. Postgres Flexible suits open-source preference, JSON-heavy schemas with pg extensions, and often lower cost at moderate scale. Both support Entra authentication from Spring with JDBC URL parameters and token-based auth plugins. Evaluate licensing, DBA skills, and migration tools from current database. For typical CRUD microservice either works—standardize org-wide to reduce ops sprawl. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** When Cosmos DB for Java instead of relational?
**A:** Use Cosmos when you need turnkey multi-region writes with SLA, document model with flexible schema, or massive horizontal scale beyond single relational instance economics. Avoid when queries need ad hoc joins across entities or team only knows JPA. Spring Data Cosmos maps entities but partition key design is architectural commitment—wrong key causes RU throttling and refactor pain. Prefer relational plus read replicas until metrics prove need; interviewers want hearing partition key and consistency level trade-offs explicitly. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Team picked Cosmos for inventory service with complex joins and reporting.

**Model answer:** Recommend Azure SQL or Postgres with proper indexing; reserve Cosmos for high-volume telemetry or catalog slices with known partition keys. If already deployed, assess RU costs and query patterns—may need denormalization or sync to analytics SQL.

#### Code / config (when useful)
```properties
spring.datasource.url=jdbc:sqlserver://orders-sql.database.windows.net:1433;database=orders;encrypt=true;Authentication=Active Directory Managed Identity;
spring.data.redis.host=orders-cache.redis.cache.windows.net
spring.data.redis.ssl=true
```

---

### 15. Cosmos consistency levels.

**Short answer:** Five levels: Strong, Bounded Staleness, Session, Consistent Prefix, Eventual—default Session. Strong: linearizable reads cost double RU in single region; multi-region strong has constraints. Session: reads own writes for same session token—common default. Eventual: lowest latency/cost, stale reads possible. Java SDK handles session tokens automatically in same client instance.

#### What it is
Five levels: Strong, Bounded Staleness, Session, Consistent Prefix, Eventual—default Session. Strong: linearizable reads cost double RU in single region; multi-region strong has constraints. Session: reads own writes for same session token—common default. Eventual: lowest latency/cost, stale reads possible. Java SDK handles session tokens automatically in same client instance. Spring apps must design idempotency if using Eventual for read-your-writes sensitive flows.

#### How it works (internals)
Choose Session for most user-facing APIs; Strong for financial invariants in single region; Eventual for analytics aggregates. Set consistency at account or per-request in SDK. Load test RU consumption per level. Document consistency expectations in API contracts for downstream consumers.

#### When to use / when NOT to use
Cosmos architecture reviews, debugging 'lost update' reports, or multi-region active-active design. 

#### Production example
Monitor normalized RU and 429 throttling. Tune consistency per container if mixed workloads. Use change feed for projection to SQL for reporting instead of strong consistency everywhere. 

#### Common mistakes
- Strong globally without understanding latency and cost impact.
- Assuming JDBC-like transactional guarantees across documents.
- Ignoring session token loss when load balancer rotates stateless app instances incorrectly.
- No idempotency keys on writes under Eventual read paths.

#### Interview follow-ups (with model answers)

**Q:** Session consistency for Spring REST API—gotchas?
**A:** Session consistency guarantees a client sees its own writes when using same Cosmos client session token—typically same app instance or properly propagated token. Stateless Spring pods behind round-robin without sticky sessions may read pre-write state from another replica briefly unless you use Strong for that read or store session token in response and client resubmits. Prefer designing operations idempotent and UI tolerant of brief staleness, or route follow-up reads to same partition with appropriate patterns. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** How explain consistency to product owners?
**A:** Use bank balance vs social like count analogy: Strong is immediately accurate but slower and expensive; Eventual is fast but count might lag seconds; Session means 'you see your own post instantly but others might not yet.' Map product SLAs to levels per operation type—checkout totals Strong or Bounded Staleness; recommendation feed Eventual. Quantify cost difference with RU benchmarks from load tests so decisions are economic not abstract. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Users report placing order succeeds but order list empty for 30 seconds.

**Model answer:** Check consistency level on reads vs writes, SDK client instance affinity, and caching layer staleness. Fix: Session or Strong on order list query, cache invalidation on write, or return order id from POST for client-side optimistic UI.

#### Code / config (when useful)
```java
container.readItem(orderId, new PartitionKey(customerId),
    new CosmosItemRequestOptions().setConsistencyLevel(ConsistencyLevel.SESSION), Order.class);
```

---

### 16. Blob storage: tiers, SAS, private endpoint.

**Short answer:** Storage accounts hold blobs in Hot, Cool, Cold, Archive tiers by access frequency and minimum retention. Block blobs for Spring file uploads; append for logs. Shared Access Signature (SAS) grants time-limited delegated access without account keys. User delegation SAS uses Entra credentials. Private endpoints keep traffic on VNet; disable public access in prod.

#### What it is
Storage accounts hold blobs in Hot, Cool, Cold, Archive tiers by access frequency and minimum retention. Block blobs for Spring file uploads; append for logs. Shared Access Signature (SAS) grants time-limited delegated access without account keys. User delegation SAS uses Entra credentials. Private endpoints keep traffic on VNet; disable public access in prod. Java uses azure-storage-blob SDK or Spring Resource handlers.

#### How it works (internals)
Create storage account with hierarchical namespace if ADLS Gen2 needed. Generate user delegation SAS from service MI for download links. Configure lifecycle management rules tiering old blobs. Mount via private endpoint and private DNS zone. Spring: use @Value blob endpoints with DefaultAzureCredential for server-side; never embed account keys.

#### When to use / when NOT to use
Document storage, export archives, static asset hosting behind CDN, or secure file exchange with partners via short-lived SAS. 

#### Production example
Soft delete and versioning enabled. Immutable storage for compliance if required. Monitor egress costs with Front Door/CDN. Rotate any remaining account keys out; prefer RBAC Storage Blob Data Contributor on MI.

#### Common mistakes
- Long-lived account SAS with write permission leaked in logs.
- Archive tier for blobs needed without rehydration delay planning.
- Public container for 'temporary' uploads becoming data breach.
- Missing MD5/etag checks on concurrent Java uploads.

#### Interview follow-ups (with model answers)

**Q:** User delegation SAS vs account key SAS?
**A:** User delegation SAS is signed with Entra identity tied to storage account—Microsoft recommends over account keys. Java service generates SAS at runtime using BlobServiceClient.getUserDelegationKey after MI auth—no stored key. Account key SAS is simpler but key rotation revokes all links. Set tight expiry, HTTPS only, and minimum permissions (read vs write). Audit SAS generation in App Insights logs with correlation to requesting user for forensics. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Spring Boot large file upload to blob—pattern?
**A:** For large files avoid proxying through App Service memory—use direct upload SAS from client to blob or staged blocks API. Spring endpoint validates auth then returns short-lived write SAS and blob path. Server-side multipart for moderate sizes with streaming InputStream to BlobOutputStream. Configure timeout and retry policies in azure-sdk. Virus scan via Event Grid trigger on blob created moving to clean container. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Partner download links expire unpredictably; security audit finds account keys in Spring config.

**Model answer:** Migrate to MI plus user delegation SAS with documented TTL; remove keys from config using Key Vault references. Add lifecycle policy for Cool tier after 30 days. Enable private endpoint and disable public blob access.

#### Code / config (when useful)
```java
BlobServiceClient client = new BlobServiceClientBuilder()
    .endpoint("https://orders.blob.core.windows.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();
```

---

### 17. Networking: VNET, subnet, NSG, private endpoint, service endpoint.

**Short answer:** Virtual Network isolates Azure resources with private RFC1918 space. Subnets segment workloads; some subnets reserved (GatewaySubnet, AzureBastionSubnet). NSGs are stateful L3/L4 firewalls on subnet or NIC. Private endpoints map PaaS services into VNet as private IPs via Private Link. Java apps on AKS/App Service integrate VNet for private SQL, Key Vault, Storage without public exposure.

#### What it is
Virtual Network isolates Azure resources with private RFC1918 space. Subnets segment workloads; some subnets reserved (GatewaySubnet, AzureBastionSubnet). NSGs are stateful L3/L4 firewalls on subnet or NIC. Private endpoints map PaaS services into VNet as private IPs via Private Link. Java apps on AKS/App Service integrate VNet for private SQL, Key Vault, Storage without public exposure.

#### How it works (internals)
Hub-spoke or landing zone topology: hub with firewall, spokes per env. Delegate subnets for AKS (Azure CNI), App Service integration, private endpoints. NSG rules least privilege—allow only required ports to Spring Actuator from ingress subnet. Private DNS zones link endpoint FQDNs. Test with Network Watcher.

#### When to use / when NOT to use
Any production Java workload touching PaaS data; compliance requiring no public database endpoints; hybrid connectivity design. 

#### Production example
Centralized private DNS linked to all spokes. Azure Firewall or NVA for egress filtering. Document required outbound FQDNs for Spring dependencies (Maven repos, identity endpoints). NSG flow logs to Log Analytics.

#### Common mistakes
- Private endpoint without private DNS causing wrong public IP resolution.
- Overly permissive NSG allowing entire VNet on all ports.
- Subnet too small for AKS plus private endpoints combined.
- Forgetting Microsoft service tags in NSG for App Insights egress.

#### Interview follow-ups (with model answers)

**Q:** App Service VNet integration vs private endpoint to App Service?
**A:** Regional VNet integration lets outbound calls from App Service use spoke subnets to reach private endpoints on SQL/Storage—inbound still public unless ILB ASE or private endpoint for inbound App Service (preview/features vary). Private endpoint on PaaS targets the service; integration routes app outbound. For Spring API calling private SQL both matter: integrate app outbound path and SQL private endpoint with DNS. Internal-only APIs often move to AKS/ACA with internal load balancer instead. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** NSG design for AKS Spring cluster?
**A:** Allow ingress controller subnet to pod subnet on service ports; restrict east-west between namespaces via network policies (Calico/Azure NP) finer than NSG alone. NSG blocks unexpected lateral movement at subnet boundary. Log denied flows during deploy windows to catch misconfigured probes. Do not rely on NSG alone for microsegmentation—combine with Kubernetes NetworkPolicy for service-level rules matching zero-trust goals. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Spring app on App Service cannot reach private SQL after VNet integration enabled.

**Model answer:** Verify DNS resolves privatelink.database.windows.net, route all outbound enabled, SQL private endpoint in integrated subnet or peered spoke, NSG allows 1433, Entra auth still configured. Use tcpping/dns tools from Kudu console.

#### Code / config (when useful)
```bicep
resource pe 'Microsoft.Network/privateEndpoints@2023-05-01' = {
  name: 'pe-sql-orders'
  properties: {
    subnet: { id: subnetPe.id }
    privateLinkServiceConnections: [{
      name: 'sql-connection'
      properties: {
        privateLinkServiceId: sqlServer.id
        groupIds: ['sqlServer']
      }
    }]
  }
}
```

---

### 18. Hybrid: ExpressRoute vs VPN.

**Short answer:** ExpressRoute: private dedicated or partner circuit to Azure backbone, predictable latency, higher cost, no internet transit for Azure traffic. VPN Gateway: IPsec over internet, cheaper, good for dev/smaller bandwidth. Both connect on-prem to VNet for Java apps migrating gradually—on-prem ERP calling Azure APIs or reverse. ExpressRoute Gateway and VPN can coexist (ExpressRoute preferred path). Assess bandwidth, RTO, compliance, and cost.

#### What it is
ExpressRoute: private dedicated or partner circuit to Azure backbone, predictable latency, higher cost, no internet transit for Azure traffic. VPN Gateway: IPsec over internet, cheaper, good for dev/smaller bandwidth. Both connect on-prem to VNet for Java apps migrating gradually—on-prem ERP calling Azure APIs or reverse. ExpressRoute Gateway and VPN can coexist (ExpressRoute preferred path).

#### How it works (internals)
Assess bandwidth, RTO, compliance, and cost. ExpressRoute with redundant circuits for prod; VPN backup. Advertise on-prem routes via BGP. Design hub VNet with gateway subnet. Spring apps unaware if DNS and routing correct—test JDBC latency to Azure SQL over ER.

#### When to use / when NOT to use
Enterprise hybrid interviews, latency-sensitive mainframe-to-microservice bridges, or avoiding public internet for regulated data. 

#### Production example
Monitor circuit availability and BGP sessions. Separate prod/nonprod circuits or VLAN isolation. Document failover to VPN. Limit blast radius with route filters and firewall policies on hub.

#### Common mistakes
- Single non-redundant ExpressRoute for tier-1 Java order path.
- DNS split-brain resolving Azure names to public IP from on-prem.
- Underestimating provisioning lead time for ExpressRoute.
- No bandwidth monitoring until month-end invoice shock.

#### Interview follow-ups (with model answers)

**Q:** Java team on-prem calling Azure Spring APIs—network checklist?
**A:** Confirm on-prem DNS resolves internal APIM or App Service private DNS, firewall allows outbound to Azure private prefixes via ER/VPN, TLS trust for corporate CA if mTLS, and latency acceptable for synchronous chains. Test Entra token acquisition from on-prem AD federated to Entra. Spring clients need correct OAuth issuer URLs reachable—not blocked by proxy. Instrument end-to-end traces across on-prem hop with correlation IDs. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** When VPN enough instead of ExpressRoute?
**A:** VPN suits dev/test hybrid, backup path, small offices, or bandwidth under ~500Mbps sustained with tolerant latency jitter. Production Java workloads with steady high-volume DB replication or real-time integration usually justify ExpressRoute. Cost model: ER fixed port fee plus provider circuit; VPN only gateway hourly and egress. Start VPN for PoC; move ER before go-live if SLA demands sub-10ms stable latency to Azure SQL. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** On-prem batch job timeouts doubled after moving database to Azure SQL.

**Model answer:** Measure network path—likely hairpin via public internet instead of ER. Fix routing/DNS to private endpoint over ER, tune Hikari timeouts, consider moving batch runner into Azure VM/AKS same VNet as SQL.

#### Code / config (when useful)
```bash
az network vnet-gateway create --name vgw-orders --gateway-type Vpn \
  --vpn-type RouteBased --sku VpnGw2AZ
```

---

### 19. Event Hubs vs Kafka vs Service Bus vs Event Grid.

**Short answer:** Event Hubs: high-throughput event streaming, Kafka protocol surface, partitions, retention days—telemetry and stream ingest. Service Bus: enterprise messaging, queues/topics, sessions, transactions, lower throughput—workflow commands. Event Grid: push routing of discrete events (blob created, subscription lifecycle)—reactive automation. Managed Kafka on Event Hubs vs self-hosted on AKS vs Confluent Cloud choice for Spring Kafka teams. Map semantics: fire-and-forget events→Event Grid; ordered workflow→Service Bus; stream analytics→Event Hubs/Kafka.

#### What it is
Event Hubs: high-throughput event streaming, Kafka protocol surface, partitions, retention days—telemetry and stream ingest. Service Bus: enterprise messaging, queues/topics, sessions, transactions, lower throughput—workflow commands. Event Grid: push routing of discrete events (blob created, subscription lifecycle)—reactive automation. Managed Kafka on Event Hubs vs self-hosted on AKS vs Confluent Cloud choice for Spring Kafka teams.

#### How it works (internals)
Map semantics: fire-and-forget events→Event Grid; ordered workflow→Service Bus; stream analytics→Event Hubs/Kafka. Spring: spring-kafka with Event Hubs connection string or OAuth; Spring Cloud Stream Service Bus binder. Idempotent consumers with checkpointing. Choose partition key for ordering.

#### When to use / when NOT to use
Event-driven architecture interviews, replacing RabbitMQ/Kafka on-prem, or debugging duplicate message handling. 

#### Production example
Capture to ADLS for replay on Event Hubs. Service Bus premium for latency and isolation. Dead-letter monitoring and alerts. Schema registry (Avro/JSON Schema) for Kafka compatibility on Event Hubs.

#### Common mistakes
- Event Hubs for competing-consumer task queue needing DLQ semantics.
- Service Bus for millions/sec telemetry ingest cost explosion.
- Event Grid for bulk data transfer instead of blob/storage events only.
- No idempotency in Spring @KafkaListener on at-least-once delivery.

#### Interview follow-ups (with model answers)

**Q:** Service Bus vs Event Hubs for order events in Spring?
**A:** Order commands needing guaranteed processing, sessions for order-id ordering, and dead-letter investigation fit Service Bus topics/subscriptions with Spring Cloud Azure Service Bus. High-volume clickstream analytics fit Event Hubs with Kafka consumer groups. Hybrid: Service Bus for transactional outbox from SQL, Event Hubs for fan-out analytics—common in CQRS Java systems. Compare cost at peak TPS before deciding single bus for everything. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Event Grid role in microservices?
**A:** Event Grid notifies when something happened—blob uploaded, resource changed, custom topic business signal—and pushes to Function, Logic App, or webhook endpoint. Not a durable log consumers replay from indefinitely. Spring services publish custom events to Grid topics for decoupled subscribers without polling. Pair Grid with Service Bus when subscriber needs queue durability. Grid excels at Azure resource automation and fan-out with filtering on event type. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Team uses Event Hubs as task queue; messages lost on consumer crash.

**Model answer:** Migrate task workload to Service Bus queue with peek-lock, DLQ, and visibility timeout aligned to processing time. Keep Event Hubs for analytics stream. Implement idempotent Spring listener with checkpoint store.

#### Code / config (when useful)
```properties
spring.kafka.bootstrap-servers=${EVENTHUBS_NAMESPACE}.servicebus.windows.net:9093
spring.kafka.properties.sasl.mechanism=PLAIN
spring.kafka.properties.security.protocol=SASL_SSL
```

---

### 20. Service Bus sessions.

**Short answer:** Sessions group messages sharing SessionId processed exclusively by one consumer at a time—FIFO per session key. Required for order-line sequencing, per-tenant serialization, or stateful conversation. Java Spring listener sets sessionHandler or uses ServiceBusSessionReceiverClient. Max delivery count moves poison messages to DLQ. Premium tier for lower latency and more concurrent sessions.

#### What it is
Sessions group messages sharing SessionId processed exclusively by one consumer at a time—FIFO per session key. Required for order-line sequencing, per-tenant serialization, or stateful conversation. Java Spring listener sets sessionHandler or uses ServiceBusSessionReceiverClient. Max delivery count moves poison messages to DLQ. Premium tier for lower latency and more concurrent sessions.

#### How it works (internals)
Set sessionId on send (orderId, customerId). Enable sessions on queue/subscription. Configure max concurrent sessions per consumer instance in Spring. Handle SessionLockLostException with renewal. Scale out partitions via many session keys—not single session for all traffic.

#### When to use / when NOT to use
Interview scenarios needing ordering without Kafka partition rigidity; fixing race conditions in multi-instance Spring consumers. 

#### Production example
Monitor DLQ depth per session failures. Alert on session lock renew failures. Balance concurrent sessions with JVM thread pools. Document hot session keys causing single-consumer bottleneck.

#### Common mistakes
- One global session id serializing entire platform.
- Long processing without lock renewal losing message.
- Sessions on subscription without enabling on creation—must recreate entity.
- Assuming sessions provide global ordering across all messages.

#### Interview follow-ups (with model answers)

**Q:** Sessions vs Kafka partition key for Java ordering?
**A:** Kafka partition key pins all messages with same key to one partition consumed by one consumer in group—similar to session stickiness. Service Bus sessions add exclusive lock semantics and DLQ per message with peek-lock visibility—more enterprise messaging features. Kafka scales ordering partitions horizontally; Service Bus sessions compete for session locks across consumers—hot key problem similar. Choose Service Bus when already on Azure messaging with transactions; Kafka/Event Hubs when stream retention and replay dominate. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Spring configuration for session-enabled subscription?
**A:** Use ServiceBusProcessorClient with maxConcurrentSessions tuned to pod CPU. Message handler completes or abandons message; failures increment delivery count toward DLQ. Enable auto lock renewal for handlers exceeding default lock duration. Integration tests with Testcontainers or emulator validate session stickiness with parallel sends sharing sessionId processed sequentially. Observability: log sessionId and sequenceNumber in structured logs for traceability during incident replay. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Payment messages for same account processed out of order across three Spring pods.

**Model answer:** Enable Service Bus sessions with sessionId=accountId, tune concurrent sessions, add idempotency store keyed by paymentId. Verify no duplicate listeners on same subscription without session awareness.

#### Code / config (when useful)
```java
@ServiceBusSessionReceiverClientBuilder()
    .queueName("order-saga")
    .disableAutoComplete()
    .maxConcurrentSessions(16)
    .buildClient();
```

---

### 21. Azure Monitor, App Insights, Log Analytics.

**Short answer:** Azure Monitor is umbrella platform: metrics, alerts, dashboards. Log Analytics workspace stores KQL-queryable logs from resources, containers, App Insights. Application Insights is APM for Java via agent or OpenTelemetry—requests, dependencies, exceptions, live metrics. Diagnostic settings route platform logs to workspace. Java Spring integrates Micrometer → App Insights or OTel exporter.

#### What it is
Azure Monitor is umbrella platform: metrics, alerts, dashboards. Log Analytics workspace stores KQL-queryable logs from resources, containers, App Insights. Application Insights is APM for Java via agent or OpenTelemetry—requests, dependencies, exceptions, live metrics. Diagnostic settings route platform logs to workspace. Java Spring integrates Micrometer → App Insights or OTel exporter.

#### How it works (internals)
Create Log Analytics workspace per env or shared with RBAC separation. Enable App Insights on App Service/AKS via instrumentation key or connection string (prefer workspace-based). Configure diagnostic settings on SQL, Service Bus, Key Vault. Build KQL alerts for error rate, dependency failures. Use distributed tracing with W3C trace context across APIM→Spring→SQL.

#### When to use / when NOT to use
Observability design, incident response setup, or explaining difference between logs, metrics, traces to Java teams. 

#### Production example
Sampling tuned—100% on errors, reduced on health checks. Retention and cost caps on workspace ingestion. Action groups to PagerDuty/Teams. Workbooks for SRE dashboards. Separate dev/prod workspaces or tables with access control.

#### Common mistakes
- Logging PII to App Insights without scrubbing.
- Multiple disconnected App Insights resources per microservice without unified workspace query.
- Alert fatigue from thresholds on non-actionable CPU spikes during deploy.
- Missing dependency tracking on JDBC—only see HTTP layer.

#### Interview follow-ups (with model answers)

**Q:** App Insights agent vs OpenTelemetry for Spring Boot 3?
**A:** Microsoft supports OpenTelemetry Java agent exporting to Azure Monitor Application Insights—preferred long-term over legacy Java agent. Spring Boot 3 with Micrometer Observation registry integrates cleanly. Configure OTel exporter endpoint and connection string via environment. Agent auto-instruments JDBC, Kafka, HTTP clients. Custom spans via @WithSpan or Observation API. Validate parity of dependency names in portal before decommissioning old agent in production canary. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** KQL query pattern for Java exception spike?
**A:** In workspace: AppExceptions | where timestamp > ago(1h) | summarize count() by problemId, outerMessage | order by count_ desc. Join with requests table on operation_Id for failing endpoints. Filter cloud_RoleName to specific Spring service. Use anomaly detection alert rules on exception count baseline. Correlate with deployments table if release correlation enabled—often new build introduces NullPointer in specific controller. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Production outage but logs scattered across App Insights and AKS container logs.

**Model answer:** Consolidate AKS container logs to Log Analytics via Container Insights; enable App Insights Kubernetes attach with single workspace. Standardize trace correlation headers. Run joint KQL workbook across tables; document query runbook for on-call.

#### Code / config (when useful)
```properties
spring.application.name=orders-api
azure.application-insights.connection-string=${APPLICATIONINSIGHTS_CONNECTION_STRING}
management.endpoints.web.exposure.include=health,metrics,prometheus
```

---

### 22. Java on Azure observability.

**Short answer:** Combine Micrometer metrics, structured logging (JSON), distributed tracing, and JVM telemetry. Spring Boot Actuator exposes health and prometheus if enabled. Azure Monitor OpenTelemetry distro, Application Insights, and Container Insights for AKS. JFR/async profiler for deep dives. Correlate MDC traceId with App Insights operation_Id.

#### What it is
Combine Micrometer metrics, structured logging (JSON), distributed tracing, and JVM telemetry. Spring Boot Actuator exposes health and prometheus if enabled. Azure Monitor OpenTelemetry distro, Application Insights, and Container Insights for AKS. JFR/async profiler for deep dives. Correlate MDC traceId with App Insights operation_Id.

#### How it works (internals)
Add spring-boot-starter-actuator, micrometer-registry-azure-monitor or OTel. Configure logging pattern with traceId/spanId. Enable JDBC and Kafka instrumentation. Set cloud_RoleName per service. Use live metrics during deploy validation. Export custom business metrics (orders.failed) as Micrometer counters.

#### When to use / when NOT to use
Senior Java interview on running Spring fleet in prod; comparing to Datadog/New Relic on Azure. 

#### Production example
SLO dashboards on availability and latency percentiles. Alert on saturation (pool exhaustion, GC pause). Log ingestion budget with sampling policies. Runbooks link KQL queries to common failure modes.

#### Common mistakes
- Actuator endpoints publicly exposed without auth.
- Sync logging blocking threads under load—use async appenders carefully.
- No custom metrics—only infrastructure CPU visible during business incidents.
- Ignoring Log Analytics ingestion cost of DEBUG in prod.

#### Interview follow-ups (with model answers)

**Q:** How tie Spring logs to distributed trace in App Insights?
**A:** Enable W3C trace context propagation; MDC populated by Micrometer tracing carries traceId logged in JSON layout. App Insights maps operation_Id linking request telemetry to traces and exceptions. Ensure Feign/WebClient/RestTemplate propagate headers. APIM and Front Door forward traceparent if configured. In KQL: union traces and AppTraces on operation_Id. Without propagation, each hop appears disconnected complicating root cause during cross-service Java calls. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** JVM metrics worth alerting on Azure?
**A:** Alert on sustained high GC pause time, heap usage after full GC near max, thread pool queue depth for Tomcat, and Hikari pool pending connections—signals before OOMKill on AKS. Container memory working set vs limit catches -XX:MaxRAMPercentage misconfig. Use JMX metrics via JMX exporter or OTel JMX instrumentation. Avoid alerting every minor GC spike; use dynamic thresholds or multi-window detection. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Microservices blame each other during latency incident; no shared trace.

**Model answer:** Mandate trace context on internal APIs via Spring Cloud Sleuth/ Micrometer tracing; enable App Insights cloud role map; workshop on reading end-to-end transaction view. Add integration test asserting trace header propagation.

#### Code / config (when useful)
```java
@Autowired TelemetryClient telemetryClient;

public void placeOrder(Order o) {
    telemetryClient.trackEvent("OrderPlaced");
    telemetryClient.trackMetric("order.value", o.getTotal());
}
```

---

### 23. Key Vault references in App Service.

**Short answer:** App Service application settings can reference @Microsoft.KeyVault(SecretUri=...) resolved at runtime using managed identity—secrets never stored in config plane visibly. Supports slot sticky settings. Works with Spring if exposed as environment variables consumed by Spring Cloud Azure or standard ${} placeholders after resolution. Grant App Service MI Key Vault Secrets User. Add reference syntax in Configuration blade or ARM/Bicep.

#### What it is
App Service application settings can reference @Microsoft.KeyVault(SecretUri=...) resolved at runtime using managed identity—secrets never stored in config plane visibly. Supports slot sticky settings. Works with Spring if exposed as environment variables consumed by Spring Cloud Azure or standard ${} placeholders after resolution.

#### How it works (internals)
Grant App Service MI Key Vault Secrets User. Add reference syntax in Configuration blade or ARM/Bicep. Use versionless secret URI for auto-rotation pickup on restart. Validate in staging slot before swap. For Spring, map env vars to @ConfigurationProperties.

#### When to use / when NOT to use
Replacing plaintext JDBC passwords in App Service Java deployments; compliance requiring secret separation from code repo. 

#### Production example
Combine with Key Vault soft delete and purge protection. Audit secret access logs. Automate secret rotation with dual-write period updating vault then restarting app or using refresh where supported. 

#### Common mistakes
- Missing MI permission causing reference resolve failure at startup.
- Version pinned secret preventing rotation without redeploy config change.
- Mixing Key Vault reference syntax error causing literal string in env.
- Using references for non-secret config better in App Configuration.

#### Interview follow-ups (with model answers)

**Q:** Key Vault reference vs Spring Cloud Azure Key Vault starter?
**A:** References resolve before Spring starts—good for simple env injection like datasource password. Spring Cloud Azure loads properties directly from Key Vault at runtime with refresh events—richer for @RefreshScope beans. References simpler for ops-managed settings; starter better for many secrets and dynamic refresh without full restart if configured. Pick one pattern per service to avoid duplicate secret fetch paths and confused ownership. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Deployment slot swap with Key Vault references?
**A:** Ensure slot settings marked sticky where environment-specific vault URIs differ per slot. Both slots' MIs need vault access. Swap does not re-resolve references until worker restart—plan warm-up after swap. Test staging slot against staging vault secrets to prevent prod secret leakage during validation. Document slot-specific Key Vault naming convention rg-vault-env-app. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** App Service Spring app fails startup after enabling Key Vault references.

**Model answer:** Check MI RBAC, reference URI syntax, network firewall on vault blocking App Service outbound, and enable temporary logging of resolution errors. Verify VNet integration if vault private-only.

#### Code / config (when useful)
```text
SPRING_DATASOURCE_PASSWORD=@Microsoft.KeyVault(SecretUri=https://kv-orders.vault.azure.net/secrets/db-password/)
```

---

### 24. Secrets in Functions.

**Short answer:** Functions store app settings and connection strings in Function App configuration—should use Key Vault references with MI like App Service. local.settings.json for dev only—not deployed. Identity-based bindings preferred over AzureWebJobsStorage keys. Premium/VNet functions need vault private endpoint reachability. Enable system/user MI on Function App.

#### What it is
Functions store app settings and connection strings in Function App configuration—should use Key Vault references with MI like App Service. local.settings.json for dev only—not deployed. Identity-based bindings preferred over AzureWebJobsStorage keys. Premium/VNet functions need vault private endpoint reachability.

#### How it works (internals)
Enable system/user MI on Function App. Key Vault references in application settings. For Service Bus/Event Hub use __fullyQualifiedNamespace with RBAC roles. Spring-like heavy configs better moved to Container Apps; Functions keep minimal secrets.

#### When to use / when NOT to use
Securing Java function integrations; audit finding connection strings in portal settings. 

#### Production example
Scan settings for disallowed key patterns in CI policy. Rotate by updating vault secret versionless reference pickup on restart. Separate vault per env. Never commit local.settings.json.

#### Common mistakes
- Deploying local.settings.json via CI artifact.
- Shared storage keys across dev and prod function apps.
- Key Vault firewall blocking Functions without VNet integration on Premium.
- Storing large JSON configs as secrets instead of App Configuration.

#### Interview follow-ups (with model answers)

**Q:** Functions Key Vault reference cold start impact?
**A:** First resolution after scale-out fetches secret from Key Vault adding latency to cold start—cache behavior internal to platform. Mitigate with Premium min instances, versionless URIs to avoid config churn, and minimal secret count. Heavy secret fan-out at startup motivates moving Java workload off Functions to App Service where Spring Cloud Azure batches property source load more predictably. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Managed identity for AzureWebJobsStorage?
**A:** Use identity-based connection format storing account name not key; assign Storage Blob Data Owner/Contributor to function MI on storage account used by runtime. Reduces key leakage risk for Durable Functions task hub and runtime storage. Validate host.json extensions still bind correctly after migration from connection string—test scale-out and Durable orchestration replay in staging. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Security scan flags Service Bus connection string in Function app settings.

**Model answer:** Switch to ServiceBusConnection__fullyQualifiedNamespace identity binding, assign Data Owner/Receiver roles to MI, remove key from settings, redeploy slots, verify triggers fire from test message.

#### Code / config (when useful)
```json
{
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "ServiceBusConnection__fullyQualifiedNamespace": "sb-namespace.servicebus.windows.net"
  }
}
```

---

### 25. Deployment slots (App Service).

**Short answer:** Slots are live apps with own hostname sharing App Service plan—production slot swaps with staging after validation. Configuration can be slot-specific (sticky). Swap warms workers and swaps VIP with optional preview. Java SE or Tomcat stacks support slot swap; test JVM heap and datasource pool behavior post-swap. Create staging slot, deploy JAR via pipeline, warm with smoke tests against slot URL, swap with preview if needed.

#### What it is
Slots are live apps with own hostname sharing App Service plan—production slot swaps with staging after validation. Configuration can be slot-specific (sticky). Swap warms workers and swaps VIP with optional preview. Java SE or Tomcat stacks support slot swap; test JVM heap and datasource pool behavior post-swap.

#### How it works (internals)
Create staging slot, deploy JAR via pipeline, warm with smoke tests against slot URL, swap with preview if needed. Mark connection strings sticky per env. Use Application Insights release annotations. Auto-swap optional for dev. Roll back by swapping back.

#### When to use / when NOT to use
Blue/green for Spring APIs on App Service; interview on safe production deploy without Kubernetes. 

#### Production example
Always validate Actuator health on staging before swap. Database migration compatibility backward one version. APIM backend pool update if not sharing same backend hostname. Monitor errors immediately post-swap with alert window.

#### Common mistakes
- Non-sticky prod DB connection on staging slot corrupting prod data during test.
- Swap during active long-running jobs without graceful shutdown.
- Forgetting to sync Key Vault references permissions for staging MI.
- Assuming swap fixes incompatible schema migration.

#### Interview follow-ups (with model answers)

**Q:** Slots vs AKS rolling update for Spring team?
**A:** Slots give instant traffic flip with pre-warmed instance—simple mental model for teams without K8s. AKS rolling updates offer finer pod-level control, readiness probes, and canary via service mesh or Flagger. App Service slots limited to app tier features; no pod anti-affinity. Choose slots when on App Service PaaS path; AKS when already containerized with Helm pipelines. Cost: slots share plan capacity—ensure plan sized for both slots during warm-up. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Database migration strategy with slot swap?
**A:** Expand-contract pattern: deploy backward-compatible schema first, swap app reading new columns optional, then second release enforces. Never deploy staging slot code against prod DB schema ahead of migration unless migration ran first. Flyway in pipeline against shared DB requires careful ordering—run migration before swap with feature flags off until swap completes. Rollback plan: swap back only works if schema still compatible with previous app version. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Slot swap caused 502s; staging looked fine isolated.

**Model answer:** Investigate warmup failures—production hostnames, ARR affinity, startup probe timeout too low for JVM, or slot config not sticky for required settings. Increase warmup action, enable health check path, swap with preview to validate production URL before full flip.

#### Code / config (when useful)
```bash
az webapp deployment slot swap --resource-group rg-orders --name orders-api \
  --slot staging --target-slot production
```

---

### 26. CI/CD: GitHub Actions / Azure DevOps to Azure.

**Short answer:** GitHub Actions: workflow YAML, OIDC federated credentials to Azure without secrets, deploy to App Service/AKS/ACA via azure/login and deploy actions. Azure DevOps: pipelines YAML, Azure Repos, classic release gates, tighter enterprise AD integration. Both build Maven/Gradle, run tests, containerize to ACR, deploy with Helm/Terraform. Java teams often GitHub + Actions or ADO if enterprise already standardized. Configure federated credential on app registration for repo/environment.

#### What it is
GitHub Actions: workflow YAML, OIDC federated credentials to Azure without secrets, deploy to App Service/AKS/ACA via azure/login and deploy actions. Azure DevOps: pipelines YAML, Azure Repos, classic release gates, tighter enterprise AD integration. Both build Maven/Gradle, run tests, containerize to ACR, deploy with Helm/Terraform. Java teams often GitHub + Actions or ADO if enterprise already standardized.

#### How it works (internals)
Configure federated credential on app registration for repo/environment. Pipeline stages: build, test, SAST, container push, deploy infra, deploy app, smoke. Use environments with approval gates for prod. Cache Maven deps. Sign images with notation/cosign if policy requires.

#### When to use / when NOT to use
DevOps maturity interviews; designing secure pipeline without long-lived Azure SP secrets. 

#### Production example
Separate service connections/OIDC per subscription. Immutable artifact promotion—not rebuild on prod deploy. Secret scanning and dependency check plugins. Deployment health gates querying App Insights failures.

#### Common mistakes
- Long-lived AZURE_CREDENTIALS JSON in GitHub secrets.
- Deploying main branch directly to prod without environment protection.
- Skipping integration tests against Testcontainers Azure emulators.
- Terraform apply and app deploy same job without plan review.

#### Interview follow-ups (with model answers)

**Q:** OIDC federated credentials setup for GitHub to Azure?
**A:** Create app registration federated credential trusting GitHub issuer with subject org/repo:ref:refs/heads/main or environment. Grant least RBAC to deployment SP—Contributor scoped to target RG or use Azure Deployment Environments. Workflow uses azure/login@v2 with client-id, tenant-id, subscription-id. No client secret stored. Rotate by updating federated trust if repo renamed. Audit sign-in logs for unexpected subjects attempting token exchange. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Maven pipeline best practices on Azure?
**A:** Use temurin JDK matrix matching prod version, mvn -B verify with failsafe integration tests, publish test reports, build container with Jib or Dockerfile multi-stage. Tag images with git sha and semver. Push to ACR with az acr login or OIDC. Deploy Helm with --set image.tag. Cache ~/.m2 in Actions cache or ADO Cache@2. Run OWASP dependency check gate on CVSS threshold before prod stage approval. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Pipeline service principal has Owner on production subscription.

**Model answer:** Scope OIDC identity to resource group deploy roles, use separate infra SP with plan-only on PR and apply on merge, enable Azure Policy deny on broad assignments, migrate secrets to federated creds.

#### Code / config (when useful)
```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: azure/login@v2
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

---

### 27. Terraform on Azure (preview of topic 15).

**Short answer:** HashiCorp Terraform with azurerm provider provisions RG, App Service, AKS, SQL, Key Vault, networking. State in Azure Storage backend with locking. Modules encapsulate Spring service stacks. Import existing resources cautiously. Drift detection in CI.

#### What it is
HashiCorp Terraform with azurerm provider provisions RG, App Service, AKS, SQL, Key Vault, networking. State in Azure Storage backend with locking. Modules encapsulate Spring service stacks. Import existing resources cautiously. Drift detection in CI. Bicep is Azure-native alternative but Terraform wins multi-cloud skill transfer.

#### How it works (internals)
Structure repos: env folders or workspaces, reusable modules, tfvars per env. Plan on PR, apply on merge with approval. Use data sources for existing hub VNet. Output connection info to pipeline—not secrets.azurerm_key_vault_secret for bootstrap only with care.

#### When to use / when NOT to use
Platform engineering interviews; IaC governance; avoiding click-ops for Java landing zones. 

#### Production example
Remote state with RBAC and soft delete. Policy-as-code via Terraform azurerm provider plus Azure Policy. Version pin provider. Separate state per blast radius. Run terraform plan nightly detecting portal drift.

#### Common mistakes
- Secrets in tfvars committed to git.
- Single massive state file causing lock contention.
- Destroying Key Vault with purge protection blocking recreate same name.
- Missing depends_on causing race on RBAC before MI access.

#### Interview follow-ups (with model answers)

**Q:** Terraform module design for Spring Boot App Service?
**A:** Module inputs: app name, sku, env tags, MI enable, app insights connection, Key Vault id. Resources: app service plan, linux web app java 17, MI, role assignments Secrets User, diagnostic settings, slot optional. Outputs: hostname, principal id for pipeline. Keep app settings minimal—reference Key Vault. Consumer module per microservice instantiates with tfvars. Test module with terratest or kitchen-terraform in CI. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Handling Terraform and application deploy ordering?
**A:** Infra pipeline provisions platform—AKS, SQL, vault, MI RBAC—before app pipeline deploys JAR/Helm. App pipeline reads Terraform outputs from secure variable group or Azure Deployment Environments. Database migrations run in app pipeline after infra confirms SQL exists. Avoid Terraform provisioning application secrets that rotate frequently—apps pull from vault at runtime. Clear contract: Terraform owns platform, CI owns app artifact. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Terraform apply fails mid-run leaving Java app without Key Vault RBAC.

**Model answer:** Use targeted apply for role_assignment resource, add explicit depends_on MI creation, enable retry in pipeline, import existing assignment if partial create. Post-mortem: smaller modules and plan review gates.

#### Code / config (when useful)
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstate"
    container_name       = "tfstate"
    key                  = "orders-prod.tfstate"
  }
}
```

---

### 28. Cost controls.

**Short answer:** Tools: Cost Management budgets/alerts, tags for chargeback, Azure Advisor rightsizing, reservations/savings plans for predictable compute, spot node pools for batch, auto-shutdown dev RGs. Java-specific: JVM heap drives App Service SKU and AKS memory requests—oversizing multiplies cost. Monitor Log Analytics ingestion charges. Tag mandatory; monthly FinOps review. Right-size App Service plans from CPU/memory metrics.

#### What it is
Tools: Cost Management budgets/alerts, tags for chargeback, Azure Advisor rightsizing, reservations/savings plans for predictable compute, spot node pools for batch, auto-shutdown dev RGs. Java-specific: JVM heap drives App Service SKU and AKS memory requests—oversizing multiplies cost. Monitor Log Analytics ingestion charges.

#### How it works (internals)
Tag mandatory; monthly FinOps review. Right-size App Service plans from CPU/memory metrics. AKS cluster autoscaler with min=0 on dev ACA. Reserved instances for prod SQL and stable AKS nodes. Budget alerts at 80/100%. Export cost to Power BI. Kill orphaned resources via Resource Graph automation.

#### When to use / when NOT to use
Executive pressure on cloud bill; interview on operating Spring fleet economically. 

#### Production example
Budget per subscription with action groups. Deny expensive SKUs in dev via Policy. Use Cool blob tier and lifecycle rules. Review Advisor weekly. Savings plan for compute after baseline stable quarter.

#### Common mistakes
- Production SQL tier overprovisioned 'just in case' without metrics review.
- Verbose logging doubling Log Analytics bill.
- Always-on Premium Functions min instances for unused integrations.
- No dev subscription shutdown policy leaving AKS running nights.

#### Interview follow-ups (with model answers)

**Q:** Right-size Spring Boot on App Service from metrics?
**A:** Review Application Insights performance counters: CPU percentage sustained vs spikes, memory private bytes vs plan limit, response time under load. If CPU <40% and memory headroom >50% consistently, try lower SKU in staging load test before downgrade. Watch GC and thread pool saturation during peak—not just average. Scale out (instance count) cheaper than scale up SKU when HTTP bound; scale up when heap needs larger single instance memory. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Reserved capacity worth it for Java AKS fleet?
**A:** After 6–12 months stable node pool size, compute savings plan or reserved VM instances reduce cost 30–50% for always-on prod pools. Not for dev bursty clusters or autoscaler min-max wide range. Combine with spot pools for non-critical batch Java jobs tolerating eviction. Measure actual node-hours monthly before 1-year commit; hybrid benefit if existing licenses apply to Azure SQL or Windows nodes. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Azure bill doubled after microservices migration; finance demands 30% cut.

**Model answer:** Quick wins: Advisor recommendations, Log Analytics sampling, dev env schedules, SQL tier review, consolidate underutilized App Service plans. Medium: reservations for stable prod, ACA scale-to-zero for idle services. Present tag-based showback so product owners share accountability.

#### Code / config (when useful)
```bash
az consumption budget create --amount 5000 --time-grain Monthly \
  --budget-name orders-prod-monthly --category Cost
```

---

### 29. Autoscale.

**Short answer:** App Service autoscale on CPU, memory, HTTP queue, custom App Insights metrics. AKS Horizontal Pod Autoscaler on CPU/memory/custom metrics from Azure Monitor adapter. VMSS rules for self-hosted. Scale-out/in cooldowns prevent flapping. Java GC pauses can trigger false CPU spikes—use multiple signals.

#### What it is
App Service autoscale on CPU, memory, HTTP queue, custom App Insights metrics. AKS Horizontal Pod Autoscaler on CPU/memory/custom metrics from Azure Monitor adapter. VMSS rules for self-hosted. Scale-out/in cooldowns prevent flapping. Java GC pauses can trigger false CPU spikes—use multiple signals.

#### How it works (internals)
Define min/max instances aligned with SLA and cost. Custom metric autoscale on queue depth for Service Bus driven workers. AKS: set requests/limits so HPA meaningful. Test scale events in load test. Schedule scale profiles for known business hours.

#### When to use / when NOT to use
Handling traffic variability; preventing overnight over-provision; interview on HPA vs App Service scale. 

#### Production example
Max cap prevents runaway cost. Alert when at max sustained. Pre-warm before known events via scheduled scale. Document JVM warmup time in cooldown—avoid scale-in during active requests.

#### Common mistakes
- Autoscale on average CPU hiding peak latency.
- HPA without resource requests—unschedulable pods.
- Scale-in killing long Spring batch jobs without graceful shutdown.
- Identical min max defeating autoscale purpose.

#### Interview follow-ups (with model answers)

**Q:** Custom autoscale on Service Bus queue depth?
**A:** Export queue message count metric to Azure Monitor, create autoscale rule on ACA or Function Premium plan scaling on active messages or custom metric from Micrometer. Spring consumer apps on AKS: KEDA ScaledObject on Service Bus trigger scales deployments from zero. Set cooldown longer than average message processing time to avoid thrashing. Load test burst enqueue verifying scale-out latency meets SLA before Black Friday. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** App Service vs AKS autoscale differences?
**A:** App Service scales whole instances behind load balancer—simple HTTP metrics, limited granularity. AKS HPA scales pod replicas—finer per service, needs proper metrics adapter and pod scheduling headroom on nodes; may also need cluster autoscaler to add nodes. Multi-service cluster requires per-deployment HPA—not one cluster metric. Java teams on AKS must coordinate JVM heap per pod with node capacity when scaling out dozens of replicas. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Autoscale adds instances but p99 latency still high during peaks.

**Model answer:** Bottleneck likely downstream SQL connection pool or database RU—not compute. Profile dependencies in App Insights, scale connection pool cautiously, add read replica, tune autoscale on custom dependency latency metric not CPU alone.

#### Code / config (when useful)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

### 30. KEDA.

**Short answer:** Kubernetes Event-driven Autoscaling scales workloads from zero based on external metrics—Service Bus queue length, Event Hubs, Kafka, CPU, cron. Built into Azure Container Apps; add-on on AKS. Ideal for Java consumers processing backlog without idle pods costing money. Install KEDA on AKS via Helm. Define ScaledObject targeting Deployment with trigger auth using workload identity.

#### What it is
Kubernetes Event-driven Autoscaling scales workloads from zero based on external metrics—Service Bus queue length, Event Hubs, Kafka, CPU, cron. Built into Azure Container Apps; add-on on AKS. Ideal for Java consumers processing backlog without idle pods costing money.

#### How it works (internals)
Install KEDA on AKS via Helm. Define ScaledObject targeting Deployment with trigger auth using workload identity. Set minReplicaCount 0 for dev, 1+ for prod if cold start unacceptable. Configure polling interval and cooldown. ACA uses KEDA natively in scale rules.

#### When to use / when NOT to use
Queue worker Spring apps; replacing timer-based always-on polling; cost optimization interviews. 

#### Production example
Authenticate scalers with pod identity to Service Bus. Monitor scaler errors in KEDA logs. Set max replicas cap. Test scale-from-zero latency including JVM startup—may need minReplicas=1 for Java.

#### Common mistakes
- Scale to zero Java with 60s cold start breaking SLA.
- Missing trigger authentication causing scaler fail silent.
- Max replicas unlimited flooding downstream SQL.
- Cron scaler overlapping with queue scaler conflicts.

#### Interview follow-ups (with model answers)

**Q:** KEDA Service Bus scaler for Spring listener deployment?
**A:** ScaledObject references Azure Service Bus trigger with queueName, namespace, messageCount threshold per replica. Spring @ServiceBusListener deployment scales when unprocessed messages exceed threshold. Use workload identity in TriggerAuthentication. Tune messageCount—too aggressive over-scales empty consumers; too conservative lag grows. Combine with HPA fallback on CPU for mixed HTTP+listener pods only if architecture combines both—prefer separate deployments. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** KEDA on Container Apps vs AKS?
**A:** ACA abstracts KEDA rules in scale configuration—lower ops, integrated with env logs. AKS KEDA offers more triggers and customization for platform teams. Java Spring on ACA benefits faster time-to-value; AKS when need custom scalers or multi-tenant cluster. Both suffer Java cold start on scale-from-zero—measure before choosing zero min for production payment processors. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Night batch queue idle but six Java consumer pods running costing $4k/month.

**Model answer:** Deploy KEDA ScaledObject minReplicaCount=0 or 1 off-peak, cron scaler for business hours min=3, verify MI auth to Service Bus metrics, load test scale-out time acceptable for batch SLA.

#### Code / config (when useful)
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
spec:
  scaleTargetRef:
    name: order-processor
  minReplicaCount: 0
  maxReplicaCount: 20
  triggers:
    - type: azure-servicebus
      metadata:
        queueName: orders
        messageCount: "100"
```

---

### 31. Azure Policy and governance.

**Short answer:** Azure Policy assigns compliance rules at management group/subscription/RG—deny, audit, deployIfNotExists, modify. Examples: allowed locations, required tags, deny public IP on SQL, enforce TLS, require private endpoints. Initiative bundles policies. Java teams interact via denied deploys in CI and remediations on existing resources. Define policy initiatives in landing zone repo.

#### What it is
Azure Policy assigns compliance rules at management group/subscription/RG—deny, audit, deployIfNotExists, modify. Examples: allowed locations, required tags, deny public IP on SQL, enforce TLS, require private endpoints. Initiative bundles policies. Java teams interact via denied deploys in CI and remediations on existing resources.

#### How it works (internals)
Define policy initiatives in landing zone repo. Assign at MG scope descending to prod. Use deny in prod, audit in dev first. Remediation tasks for DINE policies. Exemptions with expiry for PoCs. Integrate policy compliance in pipeline pre-flight using what-if.

#### When to use / when NOT to use
Governance interviews; explaining why Terraform apply failed with PolicyViolation; FinOps and security alignment. 

#### Production example
Regular compliance dashboard to leadership. Break-glass exemption process. Policy version control in Git synced via Terraform azurerm_policy_set_definition. Combine with Defender for Cloud recommendations.

#### Common mistakes
- Deny policies without dev staging causing blocked legitimate experiments.
- No exemption workflow—teams circumvent with shadow subscriptions.
- Policies conflicting with required Spring features (e.g., deny all outbound).
- Ignoring audit-only policies never remediated.

#### Interview follow-ups (with model answers)

**Q:** Example policies for Spring microservices on AKS?
**A:** Require Kubernetes pods to run as non-root, limit allowed container registries to ACR only, enforce azure-policy addon labels, deny Service type LoadBalancer in prod forcing ingress controller, require workload identity label on namespaces hosting Java apps, audit missing network policies. Azure Policy for Kubernetes uses Gatekeeper constraints—test in dev cluster before prod deny breaks deploy pipeline. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Policy vs RBAC—who wins on deploy failure?
**A:** Azure Policy deny evaluates at resource creation regardless of RBAC permission—Contributor can be blocked from creating public SQL. RBAC controls who can attempt action; Policy controls what action allowed. Both must align for successful Terraform apply. Pipeline SP needs Contributor plus compliance with policies. Troubleshoot PolicyViolation error details in activity log; adjust template or request time-bound exemption with justification ticket. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Java team Terraform blocked: policy denies App Service without private endpoint.

**Model answer:** Add private endpoint module and DNS zone to Terraform, or request exemption for dev subscription only. Long term: update golden path template so Spring App Service module includes PE by default.

#### Code / config (when useful)
```json
{
  "mode": "Indexed",
  "policyRule": {
    "if": { "field": "type", "equals": "Microsoft.Storage/storageAccounts" },
    "then": { "effect": "deny" }
  }
}
```

---

### 32. Landing zone.

**Short answer:** Enterprise-scale architecture: management groups, platform subscriptions (identity, connectivity, management), application landing zones for workloads. Implements hub-spoke networking, centralized logging, policy, CI/CD identity, and optional ACR/APIM shared services. Microsoft Cloud Adoption Framework and Terraform/Bicep accelerator modules. Java apps deploy into spoke subscriptions with prewired private DNS and monitoring. Deploy platform landing zone first via CAF accelerator.

#### What it is
Enterprise-scale architecture: management groups, platform subscriptions (identity, connectivity, management), application landing zones for workloads. Implements hub-spoke networking, centralized logging, policy, CI/CD identity, and optional ACR/APIM shared services. Microsoft Cloud Adoption Framework and Terraform/Bicep accelerator modules. Java apps deploy into spoke subscriptions with prewired private DNS and monitoring.

#### How it works (internals)
Deploy platform landing zone first via CAF accelerator. Onboard app team with subscription vending, RBAC groups, network peering, pipeline SP/OIDC. Map Java service catalog to standard templates (App Service module, AKS baseline). Iterate policy and network before mass microservice migration.

#### When to use / when NOT to use
Enterprise Azure transformation interviews; distinguishing platform team vs app team responsibilities. 

#### Production example
Subscription vending automated with tags and policies attached. Regular landing zone version upgrades from Microsoft baseline. Document app onboarding checklist: MI, vault, App Insights, RG naming. 

#### Common mistakes
- App teams build own VNet without peering to hub—shadow IT.
- Skipping identity subscription consolidation—fragmented Entra apps.
- Landing zone too heavy blocking PoC velocity without sandbox MG.
- No app onboarding template—each Spring service reinvents Key Vault pattern.

#### Interview follow-ups (with model answers)

**Q:** Platform vs application team split for Spring on Azure?
**A:** Platform owns landing zone, AKS baseline, shared APIM, ACR, policy, central logging, and pipeline templates. Application teams own Spring code, service-specific config, database schema, and SLOs—deploy via golden path Helm/App Service module. Clear ticket interface for new subnet or RBAC role assignment. Platform publishes versioned 'Java on Azure' reference architecture quarterly; apps consume not fork. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Sandbox vs prod landing zone differences?
**A:** Sandbox MG: audit policies not deny, public endpoints allowed with spend caps, short-lived subscriptions, relaxed logging retention. Prod MG: deny public PaaS, mandatory PE, backup policies, PIM for admin. Java developers experiment in sandbox subscription; promotion requires compliance scan and move to prod spoke template—not copy-paste Terraform from sandbox missing PE modules. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Fifteen Java teams each created own Key Vault and VNet; ops unmaintainable.

**Model answer:** Establish landing zone and migration wave plan: consolidate to shared platform services, standard module library, subscription vending for new apps only via template. Freeze new shadow infra via policy deny.

#### Code / config (when useful)
```text
Management Group: corp
  ├── Platform (Connectivity, Identity, Management)
  └── Landing Zones (Orders, Billing, HR apps)
```

---

### 33. Azure Front Door + WAF.

**Short answer:** Front Door Standard/Premium: global HTTP load balancing, SSL offload, path routing, caching, WAF OWASP rules, bot protection, private link origins to AKS/App Service/APIM. Replaces regional App Gateway for edge when users worldwide. WAF custom rules block SQLi, rate limit IPs, geo filter. Create Front Door profile, origin groups pointing to regional ingress public IPs or private link. Configure managed rule sets, custom rules for /actuator block.

#### What it is
Front Door Standard/Premium: global HTTP load balancing, SSL offload, path routing, caching, WAF OWASP rules, bot protection, private link origins to AKS/App Service/APIM. Replaces regional App Gateway for edge when users worldwide. WAF custom rules block SQLi, rate limit IPs, geo filter.

#### How it works (internals)
Create Front Door profile, origin groups pointing to regional ingress public IPs or private link. Configure managed rule sets, custom rules for /actuator block. Enable access logs to Log Analytics. TLS certs from Key Vault or managed cert. Route /api/* to Spring backends with health probes.

#### When to use / when NOT to use
Public SaaS Java API security interviews; replacing CloudFront+WAF mental model. 

#### Production example
Separate WAF policy per env. Tune false positives on JSON payloads. DDoS Network Protection on VNet origins. Monitor blocked requests; alert spike anomalies. Use rate limit rules per APIM subscription key header.

#### Common mistakes
- Blocking legitimate JSON with aggressive SQLi rule without exclusion.
- Caching POST/authenticated API responses.
- Origin exposed publicly bypassing Front Door during DNS cutover.
- Health probe path requiring auth causing all origins unhealthy.

#### Interview follow-ups (with model answers)

**Q:** Front Door WAF with Spring Boot Actuator exposure?
**A:** Block /actuator/** at WAF custom rule except internal IP ranges if needed for ops. Spring should expose management on separate port or disable sensitive endpoints in prod via management.endpoints.web.exposure.exclude. Never rely on security through obscurity only—network restrict management. Front Door logs show scan attempts blocked—feed to SOC. Align with APIM path routing so actuator never published on public product API. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Private Link origin to internal AKS ingress?
**A:** Front Door Premium supports private link to internal load balancer fronting ingress controller—traffic never traverses public internet to origin. Configure private link approval on ILB. DNS still uses Front Door hostname for clients. Spring apps see X-Forwarded-* headers from Front Door—configure server.forward-headers-strategy for correct redirects and logging client IP. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** WAF blocks mobile app JSON login after rule set upgrade.

**Model answer:** Identify offending managed rule via WAF logs, create exclusion for specific JSON field or switch detection to prevention mode gradually in staging. Regression test mobile contract against WAF in CI.

#### Code / config (when useful)
```json
{
  "properties": {
    "policySettings": { "mode": "Prevention" },
    "managedRules": {
      "managedRuleSets": [{ "ruleSetType": "Microsoft_DefaultRuleSet", "ruleSetVersion": "2.1" }]
    }
  }
}
```

---

### 34. Private AKS API server.

**Short answer:** Private cluster sets API server to private endpoint in VNet—public FQDN disabled or restricted. kubectl and CI agents reach API via bastion, VPN, ExpressRoute, or runner VNet peering. Azure manages control plane; you secure access path. Required for many regulated Java on AKS estates. Create AKS with private cluster enabled, authorized IP ranges if hybrid.

#### What it is
Private cluster sets API server to private endpoint in VNet—public FQDN disabled or restricted. kubectl and CI agents reach API via bastion, VPN, ExpressRoute, or runner VNet peering. Azure manages control plane; you secure access path. Required for many regulated Java on AKS estates.

#### How it works (internals)
Create AKS with private cluster enabled, authorized IP ranges if hybrid. Deploy self-hosted GitHub runner or Azure DevOps agent in peered VNet. DNS private zone for regional AKS API FQDN. Document break-glass access via Azure Bastion jump host.

#### When to use / when NOT to use
Security architecture interviews; troubleshooting pipeline cannot reach API server. 

#### Production example
Separate dev private cluster with VPN for developers vs prod CI-only access. Monitor unauthorized API access attempts. Keep kubeconfig off laptops—use Azure RBAC AKS integration with az aks get-credentials. 

#### Common mistakes
- Private cluster without CI runner in VNet breaking all deploys.
- Developers sharing single kubeconfig with cluster-admin.
- Forgetting DNS zone link causing kubectl timeout.
- Public cluster accidentally recreated by Terraform default change.

#### Interview follow-ups (with model answers)

**Q:** GitHub Actions deploy to private AKS?
**A:** Run self-hosted runner VMSS in spoke VNet peered to AKS subnet with NSG allowing API server access. Workflow uses az aks get-credentials on runner. OIDC to Azure for az login without secrets. Alternative: Azure DevOps Microsoft-hosted agents cannot reach private API—must use self-hosted or deploy via Arc/Flux from within cluster pulling from ACR. Push images from cloud-hosted build job; deploy job self-hosted only. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Developer local kubectl to private cluster?
**A:** Require VPN or ExpressRoute to corporate VNet peered to AKS, or use Azure Bastion plus jump box with kubectl. Azure RBAC controls who gets clusterUser role. Avoid exposing API publicly with authorized IPs unless policy allows temporary debug. Spring developers rarely need kubectl if platform provides namespace-limited access and logs via App Insights. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Pipeline worked on public AKS; private cluster migration broke Helm deploy.

**Model answer:** Move deploy job to VNet runner, configure private DNS, verify SP/runner MI has AKS RBAC, test az aks command invoke as fallback. Document network diagram for ops.

#### Code / config (when useful)
```bash
az aks create --enable-private-cluster --network-plugin azure \
  --apiserver-authorized-ip-ranges ""  # empty when fully private
```

---

### 35. Ingress TLS.

**Short answer:** TLS typically terminates at ingress controller (NGINX/AGIC) or Front Door/APIM before Spring Tomcat. cert-manager automates Let's Encrypt or Key Vault cert issuance to K8s secrets. Spring may terminate TLS at pod level (less common) or run HTTP behind ingress. mTLS via service mesh for east-west. Install cert-manager, ClusterIssuer for Let's Encrypt DNS-01 or HTTP-01.

#### What it is
TLS typically terminates at ingress controller (NGINX/AGIC) or Front Door/APIM before Spring Tomcat. cert-manager automates Let's Encrypt or Key Vault cert issuance to K8s secrets. Spring may terminate TLS at pod level (less common) or run HTTP behind ingress. mTLS via service mesh for east-west.

#### How it works (internals)
Install cert-manager, ClusterIssuer for Let's Encrypt DNS-01 or HTTP-01. Annotate ingress with cert-manager.io/cluster-issuer. Use TLS 1.2+, strong ciphers. Renew before expiry with cert-manager auto. For corporate certs, sync from Key Vault via akv2k8s or CSI driver.

#### When to use / when NOT to use
HTTPS setup interviews; cert expiry incidents; mutual TLS B2B designs. 

#### Production example
Monitor cert expiry alerts redundant to cert-manager. HSTS at ingress. Optional pod TLS for compliance—performance cost. Document cipher compliance for PCI.

#### Common mistakes
- Cert-manager failed challenges leaving expired ingress cert.
- Spring redirect loop misconfigured forward headers behind TLS-terminating ingress.
- Wildcard cert shared across envs breaking blast radius rules.
- HTTP backend between ingress and pod on untrusted network without mTLS.

#### Interview follow-ups (with model answers)

**Q:** cert-manager with Azure DNS for Let's Encrypt?
**A:** Configure ClusterIssuer using DNS-01 challenge with Azure DNS zone service principal or workload identity to create TXT records. Works behind private origins unlike HTTP-01. Grant identity DNS Zone Contributor on zone. Spring ingress hostname in Certificate resource matches public DNS. Test renewal 30 days before expiry in staging cluster mirroring prod issuer config. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** TLS at ingress vs Spring Boot embedded Tomcat?
**A:** Terminate at ingress—simpler cert lifecycle, one cert per hostname, Spring runs HTTP on port 8080 inside cluster. Embedded Tomcat TLS per pod multiplies cert management and CPU—use only if regulatory requirement for encryption in pod network. Configure server.use-forward-headers and trust proxy headers when ingress terminates TLS so Spring generates correct https links. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Production API cert expired Saturday; customers down.

**Model answer:** Emergency manual cert apply to ingress secret, fix cert-manager issuer/challenge root cause Monday, add Prometheus alert on cert expiry <14 days, run quarterly DR drill for cert rotation.

#### Code / config (when useful)
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
spec:
  secretName: api-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - api.contoso.com
```

---

### 36. Azure SQL: AD auth, firewall, HA.

**Short answer:** Azure SQL Database supports Entra ID (formerly AAD) authentication for JDBC without SQL logins—token via azure-identity. Firewall allows IP or VNet rules; private endpoint preferred. HA: locally redundant backup default; zone redundant and Business Critical for higher SLA with readable secondary. Geo-replication for DR read-only or failover groups for automated DR. Spring: use com.microsoft.sqlserver.jdbc.SQLServerDataSource with ActiveDirectoryDefaultAuthentication or Spring Cloud Azure SQL starter.

#### What it is
Azure SQL Database supports Entra ID (formerly AAD) authentication for JDBC without SQL logins—token via azure-identity. Firewall allows IP or VNet rules; private endpoint preferred. HA: locally redundant backup default; zone redundant and Business Critical for higher SLA with readable secondary. Geo-replication for DR read-only or failover groups for automated DR.

#### How it works (internals)
Spring: use com.microsoft.sqlserver.jdbc.SQLServerDataSource with ActiveDirectoryDefaultAuthentication or Spring Cloud Azure SQL starter. Disable SQL auth in prod. Private endpoint plus private DNS. Configure failover group secondary in paired region; connection string points to listener.

#### When to use / when NOT to use
Database security and DR interviews for Java monoliths/microservices using JPA. 

#### Production example
Failover group with grace period automation policy. Test failover quarterly. Connection retry in HikariCP for transient faults. Monitor DTU/vCore saturation and deadlocks via SQL insights.

#### Common mistakes
- SQL login password in Spring config instead of Entra MI.
- Firewall open to Azure services without private endpoint misunderstanding shared pool risk.
- Failover group untested—wrong JDBC URL after failover.
- Pool size × pod count exceeding SQL max connections.

#### Interview follow-ups (with model answers)

**Q:** Spring Boot passwordless JDBC to Azure SQL?
**A:** Enable Entra admin on SQL server, assign MI db_datareader/db_datawriter or custom role, JDBC URL with authentication=ActiveDirectoryDefaultAuthentication and user MI object id as username for service principal style. Spring Cloud Azure simplifies datasource autoconfig. Local dev uses Azure CLI token via ActiveDirectoryDefaultAuthentication chain. Token refresh handled by driver—watch token expiry on very long-lived connections; pool validation query helps. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Failover group vs geo-replication for Java DR?
**A:** Failover group provides automatic listener endpoint redirect on planned/unplanned failover—Spring JDBC URL uses failover group listener FQDN. Geo-replication manual secondary promotion requires connection string change in app or DNS update. Failover groups suit RPO/RTO SLAs with automation; geo-replication cheaper read-only reporting secondary. Application must reconnect on failover—enable HikariCP connection test and Spring retry for transient SQL exceptions. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Failover test left Java app pointing at old primary DNS cache.

**Model answer:** Use failover group listener in JDBC URL, reduce DNS TTL, restart pods to flush pools, add resilience4j retry on SQL transient errors, document runbook with expected brief outage window.

#### Code / config (when useful)
```properties
spring.datasource.url=jdbc:sqlserver://orders-sql.database.windows.net:1433;database=orders;encrypt=true;hostNameInCertificate=*.database.windows.net;loginTimeout=30;Authentication=Active Directory Managed Identity;
```

---

### 37. Retry and throttling.

**Short answer:** Azure services return 429 throttling, 503 transient, timeouts—SDKs include built-in retry policies (exponential backoff). Spring: resilience4j retry/circuit breaker/rate limiter wrapping service calls. Cosmos RU throttling, Storage server busy, Service Bus lock renewal, SQL transient fault handling. Idempotency required for retries on non-read operations. Configure azure-sdk retry options globally or per client.

#### What it is
Azure services return 429 throttling, 503 transient, timeouts—SDKs include built-in retry policies (exponential backoff). Spring: resilience4j retry/circuit breaker/rate limiter wrapping service calls. Cosmos RU throttling, Storage server busy, Service Bus lock renewal, SQL transient fault handling. Idempotency required for retries on non-read operations.

#### How it works (internals)
Configure azure-sdk retry options globally or per client. Use @Retryable or resilience4j annotations on repository layers. Respect Retry-After headers. Circuit break when dependency unhealthy to protect fleet. Bulkhead thread pools for isolation.

#### When to use / when NOT to use
Resilience interviews; production incidents of retry storms; Cosmos 429 tuning. 

#### Production example
Metrics on retry counts and CB state in Micrometer. Jittered backoff avoiding synchronized retry spikes. DLQ after max attempts on messaging. Load test throttling behavior.

#### Common mistakes
- Infinite retry on non-transient 400 errors.
- Retry without idempotency causing duplicate orders.
- Aggressive retry amplifying outage (thundering herd).
- Ignoring Cosmos 429 total RU suggestion in response.

#### Interview follow-ups (with model answers)

**Q:** Resilience4j with Spring Cloud Azure Service Bus?
**A:** Wrap message handler business logic with @CircuitBreaker and @Retry naming instances per dependency. On failure abandon message for Service Bus retry/DLQ rather than infinite in-process retry burning lock time. Separate retry policy for Azure Storage upload vs SQL update. Export CB events to App Insights custom metrics. Tune waitDuration in open state based on downstream Azure status health API during regional incidents. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Cosmos 429 handling in Java SDK?
**A:** SDK retries with backoff based on x-ms-retry-after-ms header automatically—still tune max RU or partition layout. Application layer reduce parallel bulk operations. Use bulk executor with throttling awareness. Log 429 rate in Micrometer; sustained 429 means architecture change not more retries. Spring Data Cosmos inherits SDK behavior—monitor RequestCharge per operation in diagnostics. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Outage recovery caused retry storm collapsing Azure SQL.

**Model answer:** Implement circuit breakers and exponential backoff with jitter, cap max attempts, shed load at API gateway, staged pod restart instead of simultaneous reconnect. Post-incident: pool limits and SQL retry policy review.

#### Code / config (when useful)
```java
@Retry(name = "paymentGateway")
@CircuitBreaker(name = "paymentGateway")
public PaymentResult charge(Order order) { ... }
```

---

### 38. Event Hub vs Kafka for Spring.

**Short answer:** Event Hubs provides Kafka endpoint compatible with spring-kafka clients—no self-managed ZooKeeper/KRaft. Limits: partition count, retention, some admin API differences. Self-hosted Kafka on AKS offers full Kafka feature set and version control. Confluent Cloud on Azure another option. Spring Kafka config largely identical with bootstrap servers and OAuth bearer for Event Hubs.

#### What it is
Event Hubs provides Kafka endpoint compatible with spring-kafka clients—no self-managed ZooKeeper/KRaft. Limits: partition count, retention, some admin API differences. Self-hosted Kafka on AKS offers full Kafka feature set and version control. Confluent Cloud on Azure another option. Spring Kafka config largely identical with bootstrap servers and OAuth bearer for Event Hubs.

#### How it works (internals)
Use spring-kafka with bootstrap servers pointing to *.servicebus.windows.net:9093 and security.protocol=SASL_SSL with connection string or OAuth. Test consumer groups, exactly-once if needed with idempotent producer. Compare lag monitoring in Azure portal vs Kafka UI. 

#### When to use / when NOT to use
Choosing messaging for Spring Cloud Stream; migrating on-prem Kafka to Azure. 

#### Production example
Event Hubs Capture to ADLS for replay. Schema registry integration. Monitor consumer lag alerts. Dedicated cluster Event Hubs for high partition needs.

#### Common mistakes
- Assuming 100% Kafka admin API parity on Event Hubs.
- OAuth misconfiguration causing auth failures in prod only.
- Single partition bottleneck for ordered Java consumer.
- No capture/replay strategy for bug reprocessing.

#### Interview follow-ups (with model answers)

**Q:** Spring Kafka OAuth to Event Hubs?
**A:** Configure sasl.mechanism=OAUTHBEARER with callback handler using DefaultAzureCredential or custom token provider fetching Entra token for https://eventhubs.azure.net/. Assign Azure Event Hubs Data Receiver/Sender roles to MI. Remove connection strings from prod. Local dev may use connection string in profile. Verify spring-kafka version supports OAuth bearer required properties documented in Microsoft learn guide. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** When self-host Kafka on AKS instead?
**A:** Choose self-host when need latest Kafka version features, Kafka Connect ecosystem plugins not supported on Event Hubs, very high partition counts, or existing ops team with strong Kafka SRE skills. Event Hubs wins reduced ops, integrated Azure monitoring, and billing alignment for teams wanting Kafka protocol without cluster babysitting. TCO includes AKS node cost and Strimzi operator maintenance for self-host. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Spring Kafka works in dev with connection string; prod OAuth fails intermittently.

**Model answer:** Align token refresh in producer/consumer config, verify RBAC on MI, check clock skew, enable kafka client debug logging temporarily, use dedicated credential bean with refresh buffer before expiry.

#### Code / config (when useful)
```properties
spring.kafka.bootstrap-servers=${EVENTHUBS}.servicebus.windows.net:9093
spring.kafka.properties.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="${EVENTHUBS_CONNECTION_STRING}";
```

---

### 39. Function + VNET.

**Short answer:** Premium and Dedicated plans support regional VNet integration routing outbound through subnet to reach private endpoints on SQL, Storage, Service Bus. Required when Functions call private Java backends or databases without public endpoints. Consumption plan VNet support limited/evolving—check current SKU matrix. Delegate subnet to Microsoft.Web/serverFarms, enable VNet integration on Function App, route all outbound optional, configure private DNS zones linked to VNet. Java function uses same JDBC/ SDK endpoints as App Service private pattern.

#### What it is
Premium and Dedicated plans support regional VNet integration routing outbound through subnet to reach private endpoints on SQL, Storage, Service Bus. Required when Functions call private Java backends or databases without public endpoints. Consumption plan VNet support limited/evolving—check current SKU matrix.

#### How it works (internals)
Delegate subnet to Microsoft.Web/serverFarms, enable VNet integration on Function App, route all outbound optional, configure private DNS zones linked to VNet. Java function uses same JDBC/ SDK endpoints as App Service private pattern. 

#### When to use / when NOT to use
Functions accessing private SQL; security review blocking public PaaS endpoints. 

#### Production example
Subnet sizing for scale-out workers. NSG rules allowing required ports. Test cold start with VNet—may increase latency. Prefer ACA for heavy private networking Java workloads.

#### Common mistakes
- Consumption plan chosen then private SQL required mid-project.
- Missing private DNS on Function integrated VNet.
- Subnet too small /27 for scale-out instances.
- Confusing VNet integration outbound with private inbound to function.

#### Interview follow-ups (with model answers)

**Q:** Functions VNet vs Container Apps private env?
**A:** Container Apps environment injects fully into VNet with internal ingress and private endpoints natively—better fit for Java microservice calling multiple private backends continuously. Functions VNet suits short outbound calls from event triggers. ACA simplifies Spring Boot long-running HTTP with private APIM; Functions for small handlers. Compare cost at sustained always-on private workload—ACA often wins. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** DNS resolution for Key Vault private endpoint from Function?
**A:** Link privatelink.vaultcore.azure.net private DNS zone to integration VNet, ensure function app route all outbound enabled so SDK resolves private IP not public. DefaultAzureCredential uses vault URI hostname—DNS must be correct. Test with Kudu console nslookup from function worker after scale event. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Java Function cannot reach private SQL after security mandated private endpoints.

**Model answer:** Upgrade to Premium EP plan, configure VNet integration subnet and DNS, validate NSG and SQL private endpoint in same peered VNet, or migrate handler to ACA in private environment.

#### Code / config (when useful)
```bash
az functionapp vnet-integration add --name fn-orders --resource-group rg-orders \
  --vnet vnet-orders --subnet snet-functions
```

---

### 40. Cold start mitigation.

**Short answer:** Cold start: JVM bootstrap, class loading, Spring context init on Functions Consumption, ACA scale-from-zero, App Service after idle. Mitigations: Premium/min instances, always-on, smaller artifacts, AOT/native (limited), warm-up pings, provisioned concurrency patterns, avoid serverless for latency-sensitive Spring. Measure with App Insights cold start metric. Trim dependencies, lazy-init Spring beans cautiously, use App Service always-on or ACA minReplicas=1. Pre-warm staging slot before swap.

#### What it is
Cold start: JVM bootstrap, class loading, Spring context init on Functions Consumption, ACA scale-from-zero, App Service after idle. Mitigations: Premium/min instances, always-on, smaller artifacts, AOT/native (limited), warm-up pings, provisioned concurrency patterns, avoid serverless for latency-sensitive Spring. 

#### How it works (internals)
Measure with App Insights cold start metric. Trim dependencies, lazy-init Spring beans cautiously, use App Service always-on or ACA minReplicas=1. Pre-warm staging slot before swap. Synthetic traffic keep-alive only if policy allows.

#### When to use / when NOT to use
SLA discussions for 'serverless Java'; post-mortem on p99 latency spikes. 

#### Production example
Explicit platform choice documenting cold start SLO. Load test after deploy. Alert on activation count spikes. Consider Graal native only with measured CI cost-benefit.

#### Common mistakes
- Spring Boot fat JAR on Consumption without min instances.
- Lazy-init hiding startup errors until first request.
- Keep-alive hack violating architecture review without monitoring cost.
- Ignoring ACA Java startup probe killing pods mid-init.

#### Interview follow-ups (with model answers)

**Q:** App Service always-on for Java?
**A:** Always-on prevents idle unload of worker process—critical for Java on Windows/Linux App Service to avoid first-request cold JVM. Some low tiers restrict always-on. Combine with deployment slot warm-up and Application Insights availability tests hitting /actuator/health every minute from multiple regions—not as substitute for proper capacity but reduces idle sleep surprises. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** Container Apps min replicas trade-off?
**A:** minReplicas=1 eliminates scale-to-zero cold start but pays baseline container cost 24/7. Set min=0 for dev/test cost savings accepting 30–90s Java startup. Production APIs usually min>=1 with KEDA max for burst. Tune startupProbe failureThreshold × periodSeconds to exceed worst-case Spring boot time before Kubernetes kills pod during scale-out. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Marketing demo failed due to 45s first request on ACA scale-from-zero.

**Model answer:** Set minReplicas=1 before demo, run synthetic warm-up in pipeline pre-demo, long-term move latency-critical API to fixed minimum or App Service always-on tier; document SLO excludes cold start if scale-to-zero retained.

#### Code / config (when useful)
```json
{
  "minimumElasticInstanceCount": 2
}
```

---

### 41. Configuration: App Configuration service.

**Short answer:** Managed key-value and feature flag store with refresh, labels (env), Key Vault references, and push/pull SDK. Spring Cloud Azure App Configuration starter loads properties with @RefreshScope support. Replaces scattering config across App Service settings and property files. Geo-replicated for resilience. Create App Configuration store, connect via connection string (dev) or MI (prod).

#### What it is
Managed key-value and feature flag store with refresh, labels (env), Key Vault references, and push/pull SDK. Spring Cloud Azure App Configuration starter loads properties with @RefreshScope support. Replaces scattering config across App Service settings and property files. Geo-replicated for resilience.

#### How it works (internals)
Create App Configuration store, connect via connection string (dev) or MI (prod). Add spring-cloud-starter-azure-appconfiguration-config. Use labels for dev/prod. Enable feature flag management in portal or pipeline. Watch refresh polling interval impact.

#### When to use / when NOT to use
Dynamic config without redeploy; feature toggle governance; interview vs Spring Cloud Config Server self-hosted. 

#### Production example
MI with App Configuration Data Reader. Private endpoint for prod store. Audit changes via activity log. Separate stores per env or strict label discipline.

#### Common mistakes
- Refresh polling too aggressive increasing RU-like request costs.
- Same label keys across env causing prod dev cross-read misconfig.
- Storing secrets in plain config instead of Key Vault references.
- No cache fallback if App Configuration unreachable.

#### Interview follow-ups (with model answers)

**Q:** App Configuration vs Spring Cloud Config Server?
**A:** Spring Cloud Config Server self-hosted on AKS needs ops, HA, and git backend maintenance—flexible for git-native workflows. Azure App Configuration is managed, integrates feature flags natively, Key Vault references, and Azure RBAC—less ops for Java teams already on Azure. Hybrid: Config Server for complex git branching, App Configuration for runtime flags and Azure-native apps. Migration path: export properties to App Configuration keys gradually. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Key Vault reference in App Configuration?
**A:** Store Key Vault secret URI as reference type in App Configuration; App Configuration service resolves when client requests key—client never sees secret value in config store plaintext. Spring Cloud Azure resolves at property source load. Assign both App Configuration Data Reader and Key Vault Secrets User to app MI. Rotation updates vault secret; app refresh picks up on next poll or manual refresh endpoint. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Ops wants toggle payment provider without redeploying Spring Boot.

**Model answer:** Implement feature flag in App Configuration, @RefreshScope bean selecting provider, expose actuator refresh secured or automatic poll; pipeline updates flag with approval gate; validate fallback provider in code if config missing.

#### Code / config (when useful)
```properties
spring.cloud.azure.appconfiguration.stores[0].endpoint=https://appconfig-orders.azconfig.io
spring.cloud.azure.appconfiguration.stores[0].label=prod
```

---

### 42. Feature flags.

**Short answer:** Built-in feature management: enable/disable, gradual rollout (percentage, targeting), time window filters. Spring integration via FeatureManager API and @ConditionalOnFeature annotations patterns. Supports safe deployment—dark launch, canary by user segment, kill switch. Define flags in App Configuration with Feature flag checkbox. Use spring-cloud-azure-feature-management starter.

#### What it is
Built-in feature management: enable/disable, gradual rollout (percentage, targeting), time window filters. Spring integration via FeatureManager API and @ConditionalOnFeature annotations patterns. Supports safe deployment—dark launch, canary by user segment, kill switch.

#### How it works (internals)
Define flags in App Configuration with Feature flag checkbox. Use spring-cloud-azure-feature-management starter. Targeting filter uses user id from Spring Security context. Monitor evaluation events optionally. Combine with APIM or Front Door routing for coarse canary if needed.

#### When to use / when NOT to use
Progressive delivery interviews; reducing big-bang release risk for Java monoliths. 

#### Production example
Naming convention flag-* per service. Document flag lifecycle—remove stale flags. Test both paths in CI. Avoid flag combinatorial explosion untested.

#### Common mistakes
- Long-lived flags doubling code paths unmaintained.
- Percentage rollout without sticky user assignment causing flip-flop UX.
- Feature flag check only in UI not server enforcement.
- No default off behavior when App Configuration down.

#### Interview follow-ups (with model answers)

**Q:** Targeting filter for beta customers in Spring?
**A:** Configure Targeting filter in App Configuration with groups and default rollout percentage. Spring passes FeatureTargetingContext with userId from authenticated principal name. Beta group users always true; others percentage bucket. Ensure consistent user id hashing for sticky experience across sessions. Log flag evaluation at debug in staging only—avoid PII in logs. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** Feature flags vs deployment slots?
**A:** Slots swap entire binary—good for holistic release. Flags toggle behavior within same deployment—granular user segments and instant kill switch without redeploy. Combine: deploy new code dark with flag off, enable gradually, remove flag after stable. Slots poor for per-user canary; flags poor for incompatible schema changes requiring new code binary separation. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Flag enabled 50% rollout caused inconsistent pricing for same customer.

**Model answer:** Fix targeting to use stable customerId hash not sessionId, add server-side price validation, test targeting filter unit tests, reduce rollout to 5% until verified.

#### Code / config (when useful)
```java
@FeatureGate(feature = "beta-pricing")
public PricingResponse getBetaPricing() { ... }
```

---

### 43. Backup and DR.

**Short answer:** Azure Backup: VM, SQL, files, AKS via extensions. Azure Site Recovery: replicate VMs/ workloads to secondary region for failover. App Service backup backs up app content and config. Database geo-redundancy and failover groups primary for stateful Spring apps. RPO/RTO drive design—not all microservices need same tier.

#### What it is
Azure Backup: VM, SQL, files, AKS via extensions. Azure Site Recovery: replicate VMs/ workloads to secondary region for failover. App Service backup backs up app content and config. Database geo-redundancy and failover groups primary for stateful Spring apps. RPO/RTO drive design—not all microservices need same tier.

#### How it works (internals)
Classify services by tier. SQL failover groups, Blob GRS, ACR geo-replication. Document runbooks for regional failure. Test failover quarterly. Stateless Spring pods redeploy from ACR to secondary AKS via GitOps. Backup Key Vault soft delete aware recovery.

#### When to use / when NOT to use
DR architecture interviews; compliance BCP requirements; distinguishing backup from replication. 

#### Production example
ASR recovery plans with ordered startup—SQL before app. Monitor replication health. Immutable backups for ransomware. Align DNS/TM/Front Door failover with data promotion steps.

#### Common mistakes
- Backing up VMs but not testing SQL point-in-time restore.
- Assuming multi-region AKS without data replication plan.
- DR runbook untested for years.
- Forgot to include App Configuration and Key Vault in DR scope.

#### Interview follow-ups (with model answers)

**Q:** AKS Java app DR without StatefulSets?
**A:** Stateless Spring services: replicate container images to secondary region ACR, deploy manifest via Flux/Argo to standby cluster, front with Front Door origin failover or Traffic Manager. Stateful data in Azure SQL/Cosmos with geo replication—not in pod disks. Redeploy faster than ASR entire cluster if infrastructure as code mature. RTO dominated by DNS cutover and connection pool warm-up not pod schedule time. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Azure Backup for Azure SQL vs native PITR?
**A:** Azure SQL built-in automated backup provides point-in-time restore within retention—primary mechanism. Azure Backup vault policy adds long-term retention (LTR) and centralized management across mixed workloads. Java teams rely on SQL PITR for oops deletes; LTR for compliance years retention. Document restore procedure including Flyway migration alignment after restore to older timestamp. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Regional Azure outage; team has no tested failover plan for Spring API.

**Model answer:** Execute documented Front Door origin shift to secondary region if standby exists; if not, honest post-incident to build warm standby, SQL failover group, and quarterly game days. Communicate RTO realistically to business.

#### Code / config (when useful)
```bash
az sql failover-group create --name fog-orders --partner-server orders-sql-secondary \
  --resource-group rg-orders --server orders-sql-primary
```

---

### 44. Multi-region active-active.

**Short answer:** Traffic distributed across regions via Front Door with equal origins, data layer hardest—Cosmos multi-region writes, SQL failover group read-only secondaries, or conflict-prone async replication. Spring services stateless per region; sticky sessions or JWT without server session. Event Hubs Kafka geo-disaster recovery optional. Design data conflict strategy first. Deploy identical Helm releases per region.

#### What it is
Traffic distributed across regions via Front Door with equal origins, data layer hardest—Cosmos multi-region writes, SQL failover group read-only secondaries, or conflict-prone async replication. Spring services stateless per region; sticky sessions or JWT without server session. Event Hubs Kafka geo-disaster recovery optional.

#### How it works (internals)
Design data conflict strategy first. Deploy identical Helm releases per region. Use Front Door latency or weighted routing. Centralized observability cross-region workspace. Idempotent APIs mandatory. Consider CQRS with regional read models.

#### When to use / when NOT to use
Global SaaS scale interviews; distinguishing active-active from active-passive DR. 

#### Production example
Chaos test regional isolation. Monitor replication lag. Cost doubles baseline compute—finance alignment. Data residency compliance per region.

#### Common mistakes
- Active-active HTTP without split-brain safe database.
- Session affinity breaking on regional failure.
- Clock skew breaking distributed idempotency.
- Duplicate Event Hub processing without deduplication store.

#### Interview follow-ups (with model answers)

**Q:** Azure SQL in active-active Java read path?
**A:** True active-active writes to SQL in two regions require failover group with single writable primary— not dual write. Pattern: read-only replicas in secondary for read scaling via JDBC read-only routing or separate datasource bean. Writes go primary region only; async replication for reads. For dual-write needs consider Cosmos or application-level conflict resolution—not SQL active-active writes. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Front Door routing for active-active origins?
**A:** Configure multiple origin groups per region with equal weight or performance routing. Health probes remove unhealthy region automatically. Spring apps must tolerate regional drain—return 503 gracefully triggering probe failure. Use geo-specific App Configuration labels for regional feature differences. Test origin disable simulating outage; verify no cross-region session dependency breaks login. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** CEO wants active-active in EU and US; app uses single-region SQL with sessions.

**Model answer:** Propose phased: Front Door global entry, stateless JWT auth, SQL geo-replica for read scaling first, evaluate Cosmos for write-heavy global entities later. Refactor server session to Redis Premium active geo-replication if sessions required.

#### Code / config (when useful)
```properties
# Route tenants to home region — application-level sharding
orders.region.routing.enabled=true
```

---

### 45. Container registry (ACR).

**Short answer:** Managed Docker registry: Basic/Standard/Premium, geo-replication on Premium, content trust, private endpoint, ACR tasks build. AKS and ACA pull images via MI AcrPull role. Java pipelines push with Jib or docker build multi-stage with temurin base. Create ACR Premium for prod geo-rep. Attach to AKS with attach-acr or workload identity pull.

#### What it is
Managed Docker registry: Basic/Standard/Premium, geo-replication on Premium, content trust, private endpoint, ACR tasks build. AKS and ACA pull images via MI AcrPull role. Java pipelines push with Jib or docker build multi-stage with temurin base.

#### How it works (internals)
Create ACR Premium for prod geo-rep. Attach to AKS with attach-acr or workload identity pull. Scan images with Defender for Containers. Tag immutability policies. Use az acr build or GitHub Actions push.

#### When to use / when NOT to use
Container Java deploy interviews; securing supply chain; image pull failures on AKS. 

#### Production example
Separate ACR per env or repo namespace isolation. Retention policy for untagged manifests. Sign images if policy requires. No admin user enabled—MI only.

#### Common mistakes
- Admin user enabled on ACR with leaked password.
- Latest tag in Helm prod values causing uncontrolled deploys.
- Missing AcrPull on kubelet identity or workload.
- Huge fat layers from copying entire target/ without multi-stage.

#### Interview follow-ups (with model answers)

**Q:** Jib vs Dockerfile for Spring Boot to ACR?
**A:** Google Jib builds optimized layers without Docker daemon—great in CI agents, separates dependencies from classes for faster push/pull. Dockerfile multi-stage offers full control for custom OS packages and debugging tools. Both push to ACR via az acr login or OIDC. Jib default temurin base; pin base image digest for supply chain. Use ACR tasks cache for faster repeated builds. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Geo-replicate ACR for multi-region AKS?
**A:** Premium ACR replicates metadata and layers to secondary regions—regional pulls faster and resilient if primary region registry unavailable during outage. Configure regional webhooks carefully. Helm values use same login server with regional pull automatic. Monitor replication lag and storage cost growth from frequent builds pushing large Java layers—optimize Jib layering. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** AKS ImagePullBackOff after enabling private ACR only.

**Model answer:** Assign AcrPull to kubelet identity or attach ACR, configure private endpoint DNS on node VNet, verify agent pool can resolve and reach PE, test pull from debug pod.

#### Code / config (when useful)
```yaml
# Helm values
image:
  repository: acrcontoso.azurecr.io/orders-api
  tag: "sha-abc123"
```

---

### 46. Azure DevOps vs GitHub.

**Short answer:** Azure DevOps: integrated boards, repos, pipelines, test plans, artifacts—strong Microsoft enterprise ADO + Entra alignment. GitHub: dominant OSS workflow, Actions, Copilot, marketplace—Microsoft owns both but cultures differ. Java teams choose based on existing ALM, compliance, and developer preference. Evaluate: existing repos, pipeline investment, need for integrated test plans, OIDC to Azure from either. ADO YAML pipelines parallel to GitHub Actions.

#### What it is
Azure DevOps: integrated boards, repos, pipelines, test plans, artifacts—strong Microsoft enterprise ADO + Entra alignment. GitHub: dominant OSS workflow, Actions, Copilot, marketplace—Microsoft owns both but cultures differ. Java teams choose based on existing ALM, compliance, and developer preference.

#### How it works (internals)
Evaluate: existing repos, pipeline investment, need for integrated test plans, OIDC to Azure from either. ADO YAML pipelines parallel to GitHub Actions. GitHub Enterprise with EMU for compliance. Migrate with mirroring and parallel CI cutover per team.

#### When to use / when NOT to use
Tooling strategy interviews; no religious wars—practical trade-offs for Spring org. 

#### Production example
Single golden CI template per org regardless of host. Policy scanning in both. Environment approvals for prod. Unified artifact promotion to ACR.

#### Common mistakes
- Split org half GitHub half ADO without integration causing duplicate CI cost.
- Choosing ADO only for Azure deploy when all devs on GitHub friction.
- Ignoring GitHub Advanced Security licensing for Java dependency review.
- No shared template library—each team writes Maven pipeline from scratch.

#### Interview follow-ups (with model answers)

**Q:** When Azure DevOps over GitHub for Java enterprise?
**A:** Choose ADO when organization already standardized on Azure Boards traceability requirements, formal test plans linked to releases, and Entra-integrated permissions model preferred over GitHub teams. Heavy regulated industries with existing ADO investment. GitHub wins developer experience, open source alignment, and Actions marketplace richness for Spring Boot actions. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** Can GitHub Actions replace ADO pipelines fully for Azure deploy?
**A:** Yes for most Java build-test-deploy to App Service/AKS with OIDC, environments, and branch protections mirroring ADO gates. Gaps historically in enterprise reporting and test plan integration narrowing. Many enterprises use GitHub for code/CI and Azure Monitor for quality gates. ADO still common for work item driven release management workflows tied to CAB process. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Acquisition brings GitHub; parent company mandates Azure DevOps.

**Model answer:** Pilot unified template exporting to both temporarily, plan migration waves by repo complexity, train on ADO YAML parity, preserve Git history mirror, sunset dual CI after six months to reduce toil.

#### Code / config (when useful)
```yaml
# GitHub Actions environment
jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
```

---

### 47. Spring on Azure libraries.

**Short answer:** Spring Cloud Azure (Microsoft): starters for Key Vault, App Configuration, Service Bus, Event Hubs, Storage, Cosmos, SQL Entra auth, passwordless connections. Builds on azure-sdk and azure-identity with Spring Boot autoconfig. Preferred over raw SDK wiring in Spring apps. Add BOM com.azure.spring:spring-cloud-azure-dependencies aligned to Spring Boot version. Enable features via spring.cloud.azure.* properties.

#### What it is
Spring Cloud Azure (Microsoft): starters for Key Vault, App Configuration, Service Bus, Event Hubs, Storage, Cosmos, SQL Entra auth, passwordless connections. Builds on azure-sdk and azure-identity with Spring Boot autoconfig. Preferred over raw SDK wiring in Spring apps.

#### How it works (internals)
Add BOM com.azure.spring:spring-cloud-azure-dependencies aligned to Spring Boot version. Enable features via spring.cloud.azure.* properties. Use managed identity defaults. Reference official samples and migration guide from spring-cloud-azure repo.

#### When to use / when NOT to use
Java implementation interviews; evaluating build vs buy for Azure integrations. 

#### Production example
Pin BOM version per platform release train. Test upgrades in staging with contract tests against emulators. Monitor deprecated property renames across major versions. 

#### Common mistakes
- Mixing Spring Cloud Azure major version incompatible with Boot 3.
- Raw SDK beans duplicating autoconfig causing double clients.
- Disabling MI and reverting to connection strings under deadline pressure.
- Not reading release notes on breaking property namespace changes.

#### Interview follow-ups (with model answers)

**Q:** Spring Cloud Azure vs raw azure-sdk-java?
**A:** Spring Cloud Azure provides Boot starters, property binding, resource autoconfig, and lifecycle aligned with @ConfigurationProperties—faster consistent setup for Spring teams. Raw SDK when non-Spring app, need fine-grained client tuning, or feature not yet wrapped in starter. Senior architects standardize Spring Cloud Azure for microservices; allow SDK escape hatch for advanced Cosmos tuning documented in ADR. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Upgrade Spring Boot 2 to 3 with Spring Cloud Azure?
**A:** Follow compatibility matrix: Spring Cloud Azure 5.x for Boot 3/Jakarta EE. Replace javax imports, update Spring Security OAuth2 resource server config, migrate property keys per migration guide, retest Key Vault and Service Bus listeners in staging. Run integration tests with Testcontainers. Upgrade azure-identity transitively—verify DefaultAzureCredential chain still works on AKS workload identity post upgrade. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Team hand-rolled Key Vault SDK; inconsistent across twelve Spring services.

**Model answer:** Publish internal starter wrapping Spring Cloud Azure conventions, migrate one service pilot, lint check banning direct SecretClient in app code, platform owns version bumps quarterly.

#### Code / config (when useful)
```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.azure.spring</groupId>
      <artifactId>spring-cloud-azure-dependencies</artifactId>
      <version>5.14.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

---

### 48. Passwordless SQL from Spring.

**Short answer:** Eliminate SQL username/password; JDBC obtains Entra token via managed identity or developer credentials. Azure AD authentication plugin for SQL Server driver integrates with azure-identity. Spring Cloud Azure SQL autoconfigures datasource with ActiveDirectoryDefaultAuthentication. Set server admin to Entra group, grant MI database roles, configure spring.datasource.azure.passwordless.enabled=true or equivalent starter properties. JDBC URL without password field.

#### What it is
Eliminate SQL username/password; JDBC obtains Entra token via managed identity or developer credentials. Azure AD authentication plugin for SQL Server driver integrates with azure-identity. Spring Cloud Azure SQL autoconfigures datasource with ActiveDirectoryDefaultAuthentication.

#### How it works (internals)
Set server admin to Entra group, grant MI database roles, configure spring.datasource.azure.passwordless.enabled=true or equivalent starter properties. JDBC URL without password field. Local dev uses Azure CLI login. 

#### When to use / when NOT to use
Security mandate interviews; rotating SQL passwords pain elimination. 

#### Production example
Audit no SQL auth logins in prod. Monitor token acquisition failures in logs. Use failover group listener URL. Separate MI per service least privilege on DB.

#### Common mistakes
- Wrong username format—must be MI client id or Entra user depending on auth mode.
- MI lacks database user created via CREATE USER FROM EXTERNAL PROVIDER.
- Mixing password and Entra auth in same pool config.
- Firewall blocking Azure services when only private endpoint intended but misconfigured.

#### Interview follow-ups (with model answers)

**Q:** CREATE USER for managed identity in Azure SQL?
**A:** Connect as Entra admin, run CREATE USER [mi-name] FROM EXTERNAL PROVIDER; then ALTER ROLE db_datareader ADD MEMBER [mi-name]; use display name or object id per Microsoft doc for MI. Repeat per database not just server. Automate in Flyway callback or pipeline step after deploy. Failure symptom: login failed for user '<token-identified principal>'. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** Flyway with Entra auth in CI pipeline?
**A:** Pipeline SP or federated identity runs Flyway with JDBC Entra auth using service principal secret short-lived or OIDC token—not human user. Grant migration SP ddl_admin during migrate job only. Spring app MI separate read/write roles without ddl. Local developers run Flyway with Azure CLI credential. Store no passwords in flyway.conf—use env vars populated by pipeline OIDC. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Production Spring app Login failed for user after MI rotation redeploy.

**Model answer:** Verify CREATE USER used correct MI object id, RBAC not confused with database user, user-assigned MI client id in JDBC username, redeploy fixed AZURE_CLIENT_ID env; add startup health check validating DB connectivity before receiving traffic.

#### Code / config (when useful)
```properties
spring.datasource.url=jdbc:sqlserver://orders-sql.database.windows.net:1433;database=orders;encrypt=true;Authentication=Active Directory Default;
spring.datasource.driver-class-name=com.microsoft.sqlserver.jdbc.SQLServerDriver
```

---

### 49. Well-Architected Framework.

**Short answer:** Five pillars: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency. Azure-specific review assessments in Advisor. Maps to Java choices: HA SQL, MI passwordless, autoscale, observability, policy governance. Interviewers expect tying design decisions to pillars not buzzwords. Run Well-Architected Review workload in portal per major system.

#### What it is
Five pillars: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency. Azure-specific review assessments in Advisor. Maps to Java choices: HA SQL, MI passwordless, autoscale, observability, policy governance. Interviewers expect tying design decisions to pillars not buzzwords.

#### How it works (internals)
Run Well-Architected Review workload in portal per major system. Document trade-offs in ADRs referencing pillars. Use Advisor recommendations and reliability checklist for AKS/App Service. Iterate each release.

#### When to use / when NOT to use
Senior architect panel interviews; design review presentations; post-incident improvement plans. 

#### Production example
Quarterly WAF review with action items in backlog. Link SLOs to reliability pillar. Cost pillar in FinOps cadence. Security pillar aligned with Defender secure score.

#### Common mistakes
- Checkbox WAF review without remediations funded.
- Optimizing cost pillar breaking reliability SLO silently.
- Ignoring operational excellence—no runbooks or game days.
- Performance efficiency only JVM tuning ignoring database RU.

#### Interview follow-ups (with model answers)

**Q:** Example reliability decision for Spring on AKS?
**A:** Deploy pod anti-affinity and PDB minAvailable 1 during node upgrades, multi-zone node pools, HPA with max bound, readiness probes hitting database dependency, circuit breakers on external calls, and SQL failover group tested quarterly. Each maps reliability pillar goals: maintain SLA during platform events and dependency failures without manual heroics. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** Cost vs reliability trade-off articulation?
**A:** State explicitly: dev uses scale-to-zero ACA sacrificing cold start (cost win) while prod maintains minReplicas=3 across zones (reliability win). Use WAF review to record accepted risk and dollar savings. Avoid false economy—single non-zone SQL in prod saves money but fails reliability pillar; document business acceptance of downtime risk or upgrade tier. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Design review asks how your last Java Azure project met WAF pillars.

**Model answer:** Walk one concrete example per pillar: MI and private endpoints (security), HPA and failover group (reliability), reservations and log sampling (cost), GitOps and runbooks (ops excellence), load test right-sizing (performance)—honest gaps and planned improvements.

#### Code / config (when useful)
```text
Review checklist: MI ✓ | Private endpoints ✓ | DR tested ✓ | Budget alerts ✓ | p95 SLO ✓
```

---

### 50. Senior Azure design (typical JD).

**Short answer:** JD themes: design microservices on App Service/AKS/ACA, Entra ID and RBAC, Terraform/Bicep IaC, CI/CD, Azure SQL/Cosmos/Redis, messaging (Service Bus/Event Hubs), APIM/Front Door, observability, Well-Architected, cost governance, mentor teams, incident leadership, hybrid connectivity, security compliance, Spring Boot expertise, sometimes Azure certifications (AZ-305, AZ-204). Prepare stories: migration, incident, cost save, landing zone, passwordless, DR test. Whiteboard multi-tier Spring reference architecture. Demonstrate trade-off communication to business. Show hands-on kubectl/Terraform snippets plus leadership.

#### What it is
JD themes: design microservices on App Service/AKS/ACA, Entra ID and RBAC, Terraform/Bicep IaC, CI/CD, Azure SQL/Cosmos/Redis, messaging (Service Bus/Event Hubs), APIM/Front Door, observability, Well-Architected, cost governance, mentor teams, incident leadership, hybrid connectivity, security compliance, Spring Boot expertise, sometimes Azure certifications (AZ-305, AZ-204). 

#### How it works (internals)
Prepare stories: migration, incident, cost save, landing zone, passwordless, DR test. Whiteboard multi-tier Spring reference architecture. Demonstrate trade-off communication to business. Show hands-on kubectl/Terraform snippets plus leadership.

#### When to use / when NOT to use
Candidate preparing for staff/principal interviews; hiring manager calibration. 

#### Production example
Senior owns outcomes not tickets—SLOs, guardrails, golden paths, and escalation during outages. Balance build vs buy and platform vs product delivery. 

#### Common mistakes
- Cert memorization without production war stories.
- Only App Service experience claiming AKS expert.
- Cannot estimate cost or DR RTO verbally.
- Dismissing Java Functions without explaining why to stakeholders.

#### Interview follow-ups (with model answers)

**Q:** Whiteboard prompt: design order platform on Azure?
**A:** Start with requirements: TPS, RPO, regions, compliance. Draw Front Door/APIM, AKS Spring services, Service Bus for async, SQL with failover group, Redis cache, Key Vault MI, App Insights, private endpoints, GitHub OIDC pipeline, Terraform modules. Call out ADRs for Cosmos vs SQL, ACA vs AKS for workers, and WAF pillar mapping. Discuss phased delivery MVP on App Service before AKS scale need. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** How demonstrate leadership in Azure architect interview?
**A:** Share example aligning three teams on golden path module, resolving security vs velocity conflict with policy sandbox, leading post-mortem after regional outage with tracked remediations, mentoring Java devs on observability standards. Quantify business impact: reduced deploy time, incident MTTR, cost savings. Show collaboration with FinOps, security, and product—not lone hero architect. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Interview panel: 'You have 30 minutes, design our Java migration to Azure.'

**Model answer:** Clarify constraints first, propose landing zone plus pilot slice, data and identity early, incremental cutover with rollback, observability day one, cost and DR assumptions stated, team topology platform vs app—structured narrative beats jumping to AKS.

#### Code / config (when useful)
```text
[User] → [Front Door+WAF] → [React SWA]
              ↓
         [APIM] → [AKS/Ingress] → [Spring Boot] → [Azure SQL private]
              ↓                        ↓
         [Entra ID]              [Service Bus] → [Workers/KEDA]
                                       ↓
                              [Functions - blob glue]
         [Terraform] [Key Vault MI] [App Insights] [ACR+Helm CI/CD]
```

---

### 51. Azure Container Apps vs AKS decision matrix

**Short answer:** ACA: serverless containers, KEDA built-in, internal/external ingress, simpler ops, no control plane management, limits on advanced K8s features. AKS: full Kubernetes, service mesh, custom CRDs, Windows nodes, fine-grained network policy, higher SRE burden. Java Spring: ACA for event-driven and moderate HTTP; AKS for complex platform needs and large multi-team clusters. Score criteria: team K8s maturity, need for sidecars/mesh, peak scale, VNet complexity, compliance, cost at baseline vs burst. POC both with same Spring container on ACA env and AKS Helm chart.

#### What it is
ACA: serverless containers, KEDA built-in, internal/external ingress, simpler ops, no control plane management, limits on advanced K8s features. AKS: full Kubernetes, service mesh, custom CRDs, Windows nodes, fine-grained network policy, higher SRE burden. Java Spring: ACA for event-driven and moderate HTTP; AKS for complex platform needs and large multi-team clusters.

#### How it works (internals)
Score criteria: team K8s maturity, need for sidecars/mesh, peak scale, VNet complexity, compliance, cost at baseline vs burst. POC both with same Spring container on ACA env and AKS Helm chart. Measure ops toil hours/month. 

#### When to use / when NOT to use
2024+ architecture decisions avoiding default AKS; interview comparing PaaS containers vs K8s. 

#### Production example
Document org standard: greenfield microservice default ACA unless AKS trigger list hit (mesh, GPU, custom operator). Shared AKS platform for services exceeding ACA limits. 

#### Common mistakes
- AKS because 'everyone uses Kubernetes' with three services.
- ACA for service needing DaemonSet or unsupported API.
- Ignoring ACA max replicas and CPU/memory limits per revision.
- Running ACA and AKS without shared ACR/observability standards.

#### Interview follow-ups (with model answers)

**Q:** Concrete triggers to choose AKS over ACA for Spring?
**A:** Choose AKS when need Istio/Linkerd mTLS east-west, custom admission controllers, pod security policies at cluster scale, GPU workloads, multi-tenant cluster chargeback, or operators (Kafka Strimzi, Spark). ACA when HTTP and queue-driven Spring services, scale-to-zero dev envs, small platform team, and fast MVP. Hybrid common during migration: new services ACA, legacy on AKS until consolidated. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Operational cost comparison?
**A:** AKS cost includes control plane (free tier limited), nodes, SRE time for upgrades, ingress, monitoring agents. ACA bills per vCPU/memory consumption and requests—often lower ops headcount cost. Hidden ACA cost: egress, Log Analytics, and always-on min replicas for Java cold start avoidance. Model three-year TCO including engineer salary for platform team—AKS breaks even only at scale needing K8s features. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** CTO wants no Kubernetes; architects propose AKS for five Spring Boot APIs.

**Model answer:** Recommend Azure Container Apps with internal ingress and KEDA for queue workers, shared managed environment, MI to SQL; reserve AKS evaluation trigger doc if mesh required in 18 months.

---

### 52. Azure OpenAI + managed identity + private endpoint architecture

**Short answer:** Azure OpenAI Service hosts GPT models in your tenant with private networking, content filtering, and RBAC. Java apps call via REST or azure-ai-openai SDK using Entra token from MI—not API keys in prod. Private endpoint keeps traffic off public internet; DNS privatelink.openai.azure.com. Often fronted by APIM for rate limit and logging. Deploy AOAI resource, private endpoint in spoke, disable public network access.

#### What it is
Azure OpenAI Service hosts GPT models in your tenant with private networking, content filtering, and RBAC. Java apps call via REST or azure-ai-openai SDK using Entra token from MI—not API keys in prod. Private endpoint keeps traffic off public internet; DNS privatelink.openai.azure.com. Often fronted by APIM for rate limit and logging.

#### How it works (internals)
Deploy AOAI resource, private endpoint in spoke, disable public network access. Assign Cognitive Services User to app MI. Spring service uses DefaultAzureCredential with endpoint https://{resource}.openai.azure.com. APIM policy validates JWT and quotas. Log prompts carefully—PII redaction.

#### When to use / when NOT to use
GenAI integration interviews; enterprise security review blocking public OpenAI API. 

#### Production example
Separate deployments per env and model version pinning. Monitor token usage cost alerts. Responsible AI content filter enabled. DR: secondary region deployment if available for model.

#### Common mistakes
- API key in Spring application.properties committed to git.
- Public AOAI endpoint with only obscurity protection.
- Logging full prompts with customer PII to App Insights.
- No timeout and circuit breaker on model latency spikes.

#### Interview follow-ups (with model answers)

**Q:** Spring Boot calling Azure OpenAI with MI?
**A:** Add azure-ai-openai dependency, configure OpenAIClient with AzureKeyCredential replaced by TokenCredential from DefaultAzureCredential, set endpoint and deployment name. No api-key header in prod. Handle 429 with exponential backoff respecting Retry-After. Wrap calls in resilience4j circuit breaker when model regional capacity throttled. Unit test with mock client; integration test against dev AOAI with small token budget. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** APIM in front of Azure OpenAI—why?
**A:** APIM centralizes auth for multiple Java consumers, applies rate limit and quota per product subscription, strips internal headers, logs metadata without passing raw prompts if policy configured, and enables caching not recommended for chat but useful for embedding batch. Private APIM VNet reaches AOAI private endpoint. Spring microservices use APIM subscription key or OAuth at gateway while backend AOAI uses MI—defense in depth. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

#### Scenario probe
**Situation:** Legal blocks external OpenAI; product wants RAG in Spring app.

**Model answer:** Architecture: private AOAI plus Azure AI Search with PE, MI throughout, APIM governance, redacted logging, content filter on, document data residency in tenant; pilot non-PII use case first with WAF review on prompt injection.

---

### 53. Microsoft Defender for Cloud and workload protection

**Short answer:** Cloud security posture management (CSPM) and workload protection: Defender for App Service, Containers, SQL, Key Vault, Resource Manager recommendations. Vulnerability scanning ACR images, runtime threat detection AKS, adaptive application controls. Secure score tracks remediation. Integrates with Log Analytics alerts. Enable Defender plans per subscription relevant to Java stack.

#### What it is
Cloud security posture management (CSPM) and workload protection: Defender for App Service, Containers, SQL, Key Vault, Resource Manager recommendations. Vulnerability scanning ACR images, runtime threat detection AKS, adaptive application controls. Secure score tracks remediation. Integrates with Log Analytics alerts.

#### How it works (internals)
Enable Defender plans per subscription relevant to Java stack. Remediate High findings: public endpoints, missing MI, weak TLS. Wire alerts to SOC. Use regulatory compliance dashboard (PCI, ISO). CI gate fail on critical ACR scan CVEs.

#### When to use / when NOT to use
Security architect interviews; turning on Defender without drowning in alerts. 

#### Production example
Prioritize production subscription plans. Exemption process for false positives with expiry. Weekly triage rotation. Link recommendations to Terraform module fixes golden path.

#### Common mistakes
- Enabling all Defender tiers globally without budget approval.
- Ignoring recommendations until audit deadline.
- No ownership mapping recommendation to Java team vs platform.
- Disabling container runtime protection for 'performance' without risk acceptance.

#### Interview follow-ups (with model answers)

**Q:** Defender for Containers on AKS Spring fleet?
**A:** Deploys DaemonSet agents profiling container behavior, maps to MITRE tactics, alerts on suspicious exec and crypto mining. Requires Log Analytics workspace. Tune exclusions for legitimate Java agents (App Insights, JMX). Pair with admission policies blocking privileged containers. Use ACR vulnerability assessment in CI before deploy—shift left complements runtime Defender. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies.

**Q:** From Defender alert to Java team action?
**A:** Example: 'Container running as root' on Spring deployment—platform opens ticket to Helm chart securityContext runAsNonRoot. SQL alert ' excessive failed logins'—app team checks JDBC misconfig or attack—rotate not applicable with Entra MI. Define RACI: platform remediates infra misconfig, app team fixes code dependency CVE from ACR scan. SOC handles active incident containment. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Defender flags 400 critical findings after Java migration sprint.

**Model answer:** Triage by exploitability and exposure—public SQL first, then container root, then informational. Fix golden path Terraform, batch remediate with sprint capacity, defer low risk with documented exemption; report secure score trend weekly.

---

### 54. Azure Backup + Site Recovery for Java workloads

**Short answer:** Backup: policy-driven snapshots—Azure VM, SQL LTR, AKS namespace via extensions, file shares. Site Recovery: orchestrated failover of VMs and replication policies to secondary region with recovery plans and test failover. Java Spring stateless tiers redeploy; stateful tiers need Backup plus DB geo features coordinated. Map RPO/RTO per tier in BCP document. Enable ASR for critical VMs running legacy Java monoliths.

#### What it is
Backup: policy-driven snapshots—Azure VM, SQL LTR, AKS namespace via extensions, file shares. Site Recovery: orchestrated failover of VMs and replication policies to secondary region with recovery plans and test failover. Java Spring stateless tiers redeploy; stateful tiers need Backup plus DB geo features coordinated.

#### How it works (internals)
Map RPO/RTO per tier in BCP document. Enable ASR for critical VMs running legacy Java monoliths. Azure Backup vault with immutability. Recovery plan steps: SQL failover then app tier DNS update. Automate post-failover Spring health validation script.

#### When to use / when NOT to use
BCM interviews complementing question 43; regulated industries requiring tested DR evidence. 

#### Production example
Test failover annually minimum with signed report. Monitor replication health alerts. Separate backup vault RBAC from app team. Include App Configuration export in backup scope.

#### Common mistakes
- Backup enabled but restore never practiced—wrong RTO discovered live.
- ASR failover plan missing JDBC connection string update automation.
- Backing up AKS nodes instead of manifests and persistent data separately.
- No communication plan during DR test affecting customers.

#### Interview follow-ups (with model answers)

**Q:** ASR for Java app on Azure VM vs re-deploy to AKS?
**A:** ASR suits lift-and-shift Tomcat on VM with minimal refactor—replicates OS and app disk. Cloud-native Spring on AKS better DR strategy often GitOps redeploy to standby cluster plus database geo-replication—not ASR of nodes. ASR test failover validates VM path without production impact using isolated network. Choose based on migration stage: VM interim, container target state. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Backup vault immutability for ransomware?
**A:** Enable immutability on Backup vault preventing malicious admin delete before retention expires. Complement soft delete on Key Vault and Blob. Java app cannot replace offline backup strategy—protect vault RBAC with PIM. Document restore drill including scanning backup for compromise before restore to clean VNet. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** Auditor requires proof of restorable Java billing service within 4 hours RTO.

**Model answer:** Demonstrate last quarter test failover report: SQL PITR restore to isolated env, Helm redeploy Spring API, Front Door origin switch runbook timed under 4h, gaps logged with remediation dates.

---

### 55. Azure Monitor workbooks and alert rules for Spring on AKS

**Short answer:** Workbooks: interactive KQL dashboards combining Container Insights, App Insights, Prometheus metrics—pod CPU, JVM heap, HTTP failures, Service Bus lag. Alert rules: metric, log, activity log—action groups to Teams/PagerDuty. Spring-specific: Micrometer metrics via azure-monitor-metrics-export or OTel, kube-state-metrics, ingress 5xx rates. Enable Container Insights and App Insights on AKS. Import or build workbook template parameterized by cluster/namespace.

#### What it is
Workbooks: interactive KQL dashboards combining Container Insights, App Insights, Prometheus metrics—pod CPU, JVM heap, HTTP failures, Service Bus lag. Alert rules: metric, log, activity log—action groups to Teams/PagerDuty. Spring-specific: Micrometer metrics via azure-monitor-metrics-export or OTel, kube-state-metrics, ingress 5xx rates.

#### How it works (internals)
Enable Container Insights and App Insights on AKS. Import or build workbook template parameterized by cluster/namespace. Create alert rules: pod restart burst, readiness failures, latency p95 > SLO, exception rate, HPA at max. Link runbook URLs in action groups.

#### When to use / when NOT to use
SRE observability interviews for Java Kubernetes; reducing alert fatigue while catching real outages. 

#### Production example
Separate alert severity tiers. Dynamic thresholds where possible. Weekly workbook review in ops cadence. Version control workbook JSON in Git.

#### Common mistakes
- Alert on every pod restart ignoring CronJob expected restarts.
- Workbook without parameters hardcoded prod resource IDs.
- No runbook link—on-call pages with no context.
- Duplicate alerts App Insights plus Container Insights same condition.

#### Interview follow-ups (with model answers)

**Q:** Sample KQL alert for Spring 5xx spike on AKS?
**A:** AppRequests | where CloudRoleName == 'order-service' and Success == false and ResultCode startswith '5' | summarize count() by bin(timestamp, 5m) | where count_ > threshold. Or ContainerLog join with ingress nginx logs. Alert rule frequency 5m, severity Sev2, action group on-call. Include dimension cloud_RoleInstance to pinpoint pod. Tune threshold from seven-day baseline using anomaly detection alert type. Validate changes in staging with realistic load, capture before-and-after metrics in Application Insights, and document rollback steps before promoting the same pattern to production Java fleets.

**Q:** Workbook design for Java on-call engineer?
**A:** Single pane: cluster health tile, top failing requests, dependency map SQL/Service Bus latency, pod memory vs limit, recent deployments annotation, HPA current vs max replicas, DLQ depth. Parameter dropdown namespace. Link to live metrics and kubectl cheat sheet runbook. Saves fifteen minutes triage scrolling disparate blades during incident. Align platform engineering, security, and product owners on ownership boundaries, because ambiguous runbooks slow incidents when Spring services span App Service, AKS, and shared PaaS dependencies. Review quarterly as Azure SKUs, SDK defaults, and organizational policies evolve, since interview-ready architecture must reflect what teams operate today—not only what passed a design review last year.

#### Scenario probe
**Situation:** On-call flooded with CPU alerts during harmless HPA scale-out.

**Model answer:** Replace static CPU alerts with composite: high CPU AND rising 5xx OR queue lag; add alert processing rule suppression during known deploy window; document in workbook annotation layer; review weekly false positive rate.

---

## Scenario-based interview drills

### S1. AKS pod cannot reach Key Vault after enabling firewall

**Situation:** Spring Boot on AKS uses workload identity to read secrets from Azure Key Vault. Platform team enabled Key Vault firewall "Allow trusted Microsoft services" only and restricted to selected networks. New pods CrashLoop with `403 Forbidden` on startup; same container image worked yesterday on App Service.

**What they're testing:** Key Vault network ACLs, private endpoints, workload identity vs network path, and AKS egress patterns.

**How to structure your answer:**
- Separate identity (RBAC) from network (firewall/PE)
- Trace pod egress: public vs private endpoint DNS
- Fix PE in spoke VNet, private DNS zone, NSG rules
- Validate with `kubectl exec` curl and Managed Identity debug

**Model answer:** 403 after firewall change is network, not RBAC—Contributor or Secrets User on MI is useless if traffic never reaches data plane. App Service had trusted service bypass; AKS pods using public Key Vault endpoint are blocked. Options: (1) Private endpoint for Key Vault in AKS spoke, link `privatelink.vaultcore.azure.net` DNS zone to VNet, ensure Spring uses `https://{vault}.vault.azure.net` resolving to private IP; (2) Alternatively allow AKS egress public IP on vault firewall—fragile with node pool scaling. I'd verify workload identity: federated credential `system:serviceaccount:prod:order-sa`, MI has Key Vault Secrets User, pod labels `azure.workload.identity/client-id`. Debug: `kubectl run curl` pod with same SA, `az login` as pod identity, fetch secret. Check NSG allows PE subnet on 443. Spring `DefaultAzureCredential` should pick workload identity via `AZURE_CLIENT_ID`. Rollout: deploy PE, update DNS, test staging namespace, then enforce firewall deny public. Document that Java apps fail fast at startup—init containers fetching secrets need same network path. Prevention: infrastructure CI tests secret fetch from canary pod post-Terraform apply.

**Common weak answers:** Assign Contributor to fix 403; disable firewall "temporarily" in prod; use client secret in ConfigMap; conflate App Service and AKS networking.

**Follow-up probes (with answers):**

**Q:** Trusted Microsoft services bypass enough for AKS?
**A:** Not for standard pod egress to public endpoint—AKS isn't App Service. Use private endpoint or explicit IP allow rules for outbound NAT/firewall IP.

---

### S2. Azure Functions Java handler times out on Service Bus batch

**Situation:** Event-driven pricing updates use Azure Functions (Consumption plan, Java 17) triggered by Service Bus queue messages. During peak, functions exceed 5-minute default timeout; messages return to queue; duplicate processing causes incorrect prices until manual fix.

**What they're testing:** Functions limits, hosting plan choice, idempotent consumers, batching, and when Functions fit Java/Spring workloads.

**How to structure your answer:**
- Consumption timeout and cold start constraints
- Move heavy logic to Container Apps/AKS or Premium plan
- Idempotency key on price version
- Service Bus lock duration vs function duration

**Model answer:** Consumption plan suits short handlers; Spring-heavy classpath or JDBC aggregation over thousands of SKUs exceeds 5 minutes and fights cold starts. Immediate: Premium plan with pre-warmed instances, increase timeout to 30m, reduce batch size in trigger `@ServiceBusQueueTrigger` cardinality. Architectural: Functions as thin adapter dequeue → call AKS Spring service via internal REST or move consumer to Spring `@ServiceBusListener` on ACA with KEDA scale—better JVM tuning and connection pooling. Service Bus lock must exceed max processing time or message becomes visible for duplicate delivery—set lock duration 5m with renewal pattern or process smaller batches. Idempotency: `priceVersion` + `sku` unique constraint; handler checks before write. Monitor Application Insights for `Function.Timeout` and `ServiceBusMessageLockLost`. Cost narrative: Premium EP1 always-on vs duplicate price incident business cost. Senior pushback: don't force Functions because slide deck says serverless—Java domain logic belongs in Spring container with mature observability.

**Common weak answers:** Infinite retry on timeout; scale out Consumption without fixing duration; ignore duplicate messages; run full Spring Boot context in Consumption without memory profiling.

**Follow-up probes (with answers):**

**Q:** When Functions still right for Java team?
**A:** Small event transforms, timer housekeeping, blob-triggered fan-out starting ACA jobs—keep execution < 2 min, minimal dependencies, Premium if HTTP latency-sensitive.

---

### S3. Unexpected Azure bill from orphaned PaaS resources

**Situation:** After 18-month Java migration program, finance flags 40% higher Azure spend than projected. Investigation shows 23 unused App Service plans (no apps), 8 unattached managed disks from deleted AKS node pools, and premium Service Bus namespaces from PoCs still running.

**What they're testing:** Cost governance, resource lifecycle, tagging, FinOps practices, and platform accountability.

**How to structure your answer:**
- Inventory with Resource Graph / Cost Management
- Identify orphans and rightsizing targets
- Policy prevent recurrence
- Chargeback tags and automation

**Model answer:** I'd run Azure Resource Graph: App Service plans without sites, disks `managedBy` empty, old `rg-poc-*` groups. Export Cost Management by resource group and tag `owner`—PoCs without `costCenter` stand out. Quick wins: delete unattached disks, downscale idle SQL dev tiers, remove duplicate Service Bus namespaces consolidated to shared standard tier. Medium: move low-traffic Spring APIs from over-provisioned P1v3 to P0v3 or ACA with scale-to-zero dev. Long-term: Azure Policy deny resource create without mandatory tags; auto-shutdown dev clusters Friday; budget alerts at 80/100% with action groups to engineering managers. AKS: cluster autoscaler plus periodic review of unused PVCs and public IPs per LoadBalancer service. Implement `rg-poc` TTL automation via automation account. Communicate to leadership: migration velocity left debt; assign FinOps sprint with Java team leads owning their RGs. Java-specific: right-size JVM heap vs SKU—many teams over-provision CPU after lift-and-shift. Document savings baseline for quarterly review.

**Common weak answers:** Blame Azure pricing; accept spend without inventory; delete production disks without snapshot check; tags as optional nice-to-have.

**Follow-up probes (with answers):**

**Q:** How prevent orphaned disks after AKS node pool delete?
**A:** Terraform lifecycle policies, Azure Policy audit unattached disks > 7 days, Event Grid alert on disk detach, runbook requiring disk delete or snapshot in same change ticket.

---

### S4. GitHub Actions OIDC deploy fails RBAC to ACR

**Situation:** Java CI pipeline migrated from long-lived service principal secret to federated OIDC credentials for `az acr login` and `az aks get-credentials`. Builds fail with `AADSTS700213` or `Authorization failed` pushing image to `acrcorpprod.azurecr.io`.

**What they're testing:** Federated workload identity, Entra app registration, RBAC scope, subject/audience claims, and secure pipeline design.

**How to structure your answer:**
- Map GitHub `sub` claim to federated credential
- Role AcrPush at registry scope
- Separate identities per environment
- No secrets in GitHub variables for Azure auth

**Model answer:** Federated credential on app registration must match exact GitHub subject: `repo:org/order-service:ref:refs/heads/main` for prod, environment `production` for stricter `repo:org/order-service:environment:production`. Common failure: credential allows wrong branch or org rename not updated. Assign AcrPush to app SP on ACR resource id, not subscription Contributor. In workflow: `permissions: id-token: write`, `azure/login@v2` with `client-id`, `tenant-id`, `subscription-id`. After login, `az acr login -n acrcorpprod`. AKS deploy needs separate Azure Kubernetes Service RBAC Cluster Admin or narrower custom role via kubelogin—prefer deployment pipeline SP with `Azure Kubernetes Service RBAC Writer` on namespace. Audit: no `AZURE_CLIENT_SECRET` in GitHub. Rotate by deleting federated cred and recreating—no secret rotation ceremony. Test with workflow_dispatch dry-run. Document per-repo vs shared platform identity trade-off. Senior security: least privilege per microservice pipeline if blast radius warrants split.

**Common weak answers:** Revert to client secret; grant Owner at subscription; one federated cred for all repos; skip `id-token: write`.

**Follow-up probes (with answers):**

**Q:** OIDC vs managed identity in GitHub runner on Azure VM?
**A:** Self-hosted runner on Azure VM can use MI via `azure/login` with user-assigned MI—no federated cred. GitHub-hosted must use OIDC; choose based on runner trust boundary.

---

### S5. Private Link to Azure SQL breaks JDBC after VNet integration

**Situation:** Spring Boot on AKS moved from public Azure SQL endpoint to private endpoint in hub-spoke topology. Intermittent `The TCP/IP connection to the host has failed` errors; works from bastion VM, fails from some pods.

**What they're testing:** Private DNS zones, JDBC connection string, AKS subnet delegation, NSG/UDR, and SQL connectivity patterns.

**How to structure your answer:**
- DNS resolution from pod: `nslookup` sql FQDN
- Private DNS zone link to AKS spoke VNet
- JDBC must use private FQDN not public
- Subnet routing via firewall/NVA

**Model answer:** Private endpoint registers `dbname.database.windows.net` in `privatelink.database.windows.net` zone—only VNets linked resolve correctly. Pods on node pools without linked VNet or custom DNS forwarder get public IP or NXDOMAIN intermittently depending on CoreDNS config. Fix: link private DNS zone to AKS spoke; set `privateDnsZone` on endpoint; verify `az network private-endpoint-dns list` shows record. JDBC url `jdbc:sqlserver://dbname.database.windows.net:1433` should resolve to `10.x` private IP from pod `nslookup`. Check UDR sending SQL traffic through firewall requiring rule; NSG on PE subnet allow 1433 from AKS node subnet. Enable `redirect` vs `proxy` connection policy awareness—some drivers need `;encrypt=true;hostNameInCertificate=*.database.windows.net`. Spring Hikari: reduce pool size during network blips; set connection timeout and validation query. Test with BusyBox pod on each node pool—if only one pool fails, its subnet missing DNS link. Disable public network access on SQL only after validation. Runbook: SQL PE change requires coordinated Java deploy + DNS verification.

**Common weak answers:** Re-enable public SQL access; hardcode private IP in JDBC; ignore split node pool DNS config; disable encrypt.

**Follow-up probes (with answers):**

**Q:** App Service VNet integration vs AKS difference for SQL PE?
**A:** App Service integrates via regional VNet injection with DNS settings on plan; AKS relies on cluster DNS and node VNet DNS links—don't assume identical setup from App Service runbook.

---

### S6. Entra ID token validation fails after tenant migration

**Situation:** Java Spring Resource Server validates JWT from Entra ID. Company acquired subsidiary; users migrated to new tenant. Mobile React app updated issuer URL; backend `application.yml` still points to old tenant `issuer-uri`. APIs return 401 for migrated users only.

**What they're testing:** Entra multi-tenant vs single-tenant, Spring Security OAuth2 resource server config, issuer/audience validation, and migration coordination.

**How to structure your answer:**
- Compare failing JWT `iss` and `aud` claims
- Update `spring.security.oauth2.resourceserver.jwt.issuer-uri`
- Multi-issuer or B2B guest considerations
- Coordinate app registration API permissions

**Model answer:** Spring Security fetches OIDC metadata from `issuer-uri` to validate signature and issuer claim. Migrated users carry tokens from new tenant `https://login.microsoftonline.com/{newTid}/v2.0` while backend trusts old tid metadata—signature validation fails or issuer mismatch. Fix: update issuer-uri to new tenant, redeploy all API instances; verify `aud` matches app registration Application ID URI for API. If both tenants must work during transition, use `JwtIssuerAuthenticationManagerResolver` with multiple issuers—rare, time-boxed. Check React SPA: MSAL `authority` must match; otherwise users present valid tokens for wrong audience. App registration in new tenant needs exposed API scope; enterprise apps re-consent. Cache: JWK set rotation automatic if issuer correct. Test with token from migrated user decoded at jwt.ms. Communication: fullstack cutover window, not backend-only silent change. Document Entra cross-tenant migration runbook for Java teams.

**Common weak answers:** Disable issuer validation; accept any JWT; update frontend only; use symmetric secret for Entra tokens.

**Follow-up probes (with answers):**

**Q:** How validate audience in Spring for multi-audience tokens?
**A:** `JwtValidators.createDefaultWithIssuer` plus custom `OAuth2TokenValidator` checking `aud` contains your API app id—Entra v2 tokens may list multiple audiences.

---

### S7. APIM rate limit surfaces 429 storm to Spring services

**Situation:** Azure API Management fronts 12 Spring Boot microservices. Product launched partner integration; legitimate traffic spike triggers APIM rate-limit policy (1000 req/min per subscription). Partners retry aggressively; Spring services see cascading thread pool exhaustion from slow clients.

**What they're testing:** APIM policies, retry-after semantics, backend protection, and Java resilience patterns.

**How to structure your answer:**
- APIM 429 with Retry-After header
- Partner retry guidance (exponential backoff)
- Spring resilience4j bulkhead/rate limit at service
- Scale and cache hot read endpoints

**Model answer:** APIM rate limit is by design—fix policy tiers: separate subscription for partner with higher quota, or quota-by-key on JWT claim `partnerId`. Ensure 429 responses include `Retry-After` and Problem Details body so clients backoff—document in partner OpenAPI. Spring must not retry 429 synchronously on server side for same request—that amplifies load. Add resilience4j RateLimiter on expensive endpoints; cache GET catalog with Redis. APIM `forward-request` timeout aligned with Spring `server.tomcat.threads`—thread pool queue visible via Micrometer. Scale AKS HPA on request rate metric from APIM logs. Long-term: async pattern for bulk operations (accept 202, poll status) instead of synchronous burst. Monitor APIM `BackendDuration` vs `TotalDuration` to locate bottleneck. Senior: distinguish DDoS from partner misconfiguration; use diagnostic logs `lastError` reason `QuotaExceeded`.

**Common weak answers:** Disable rate limiting globally; infinite Tomcat threads; blame Spring without checking APIM metrics; tell partner "don't retry" without SDK guidance.

**Follow-up probes (with answers):**

**Q:** JWT validate at APIM or Spring or both?
**A:** Defense in depth: APIM validate-jwt for coarse reject; Spring Resource Server authoritative for authorization claims—never trust APIM-added headers without re-validation unless mTLS internal trust explicitly designed.

---

### S8. AKS node pool upgrade drains Spring pods mid-transaction

**Situation:** Platform runs weekly AKS node image upgrades with surge nodes. During drain, long-running Spring batch pods processing payment files receive SIGTERM; Kubernetes grace period 30s but batch needs 4 minutes. Files reprocessed twice after restart.

**What they're testing:** PodDisruptionBudgets, terminationGracePeriodSeconds, preStop hooks, idempotent batch design, and platform/app coordination.

**How to structure your answer:**
- SIGTERM → Spring graceful shutdown
- Extend grace period vs Job vs CronJob
- PDB maxUnavailable during business hours
- Idempotent file processing with checkpoint

**Model answer:** Kubernetes sends SIGTERM on drain; Spring Boot 3 `server.shutdown=graceful` stops accepting new work and waits for in-flight requests—must align `terminationGracePeriodSeconds` (e.g., 300) with longest batch step. For 4-minute files, 30s grace guarantees kill mid-processing. Fix app: checkpoint after each file line or file complete in DB; on restart skip processed ids. Fix platform: PDB `minAvailable: 1` on batch deployment during business hours blocks drain—schedule upgrades nights; use separate node pool for batch with `critical-addons` taint or dedicated pool upgrade window. Consider Kubernetes Job per file instead of long Deployment. `preStop` sleep hook only buys time if shutdown hook implemented. Azure AKS maintenance window configuration. Metrics: duplicate payment detection alert. Senior conversation with platform: application SLO drives grace period, not default 30s.

**Common weak answers:** `kill -9` ignore; disable upgrades; no idempotency because "we use transactions"; run batch only on single pod without PDB.

**Follow-up probes (with answers):**

**Q:** Spring `server.shutdown=graceful` enough?
**A:** Only for HTTP requests—it doesn't wait arbitrary `@Scheduled` work unless custom `SmartLifecycle` stops scheduler and awaits completion; batch needs explicit cooperative shutdown.

---

### S9. Azure Front Door routes to unhealthy Spring origin after deploy

**Situation:** Java API deployed to AKS behind Application Gateway Ingress Controller. Azure Front Door health probe path `/actuator/health` flaps unhealthy after deploy; users in EU get 502 while US origin healthy. New pods pass readiness but probe targets wrong host header.

**What they're testing:** Front Door probes, AGIC ingress, health groups, multi-origin failover, and Spring actuator exposure.

**How to structure your answer:**
- FD probe config: path, host, interval
- Match ingress host and TLS SNI
- Readiness vs liveness for routing
- Staged deploy origin priority

**Model answer:** Front Door origin group health probe must use hostname matching ingress rule—if probe sends `api.example.com` but AGIC rule expects different host, 404 fails probe. Spring actuator on management port 8081 vs main 8080—probe must hit port serving `/actuator/health` with `show-details=never` for anonymous FD. During deploy, old pods terminate before new pass readiness—brief flap normal; tune `minOriginHealthPercent` and deploy maxUnavailable. EU 502 while US healthy suggests regional origin weight or priority misconfiguration—verify FD profile routes EU users to EU AKS origin with correct backend host. AGIC health probe annotations `health-probe-path` align with FD. TLS: FD to origin HTTPS with valid cert on ingress. Don't expose sensitive actuator endpoints publicly—separate health group IP restrict if needed. Test: `curl -H "Host: api.example.com" https://origin-ip/actuator/health`. Post-deploy smoke from FD diagnostic logs. Coordinate Helm chart Service port names with probe config.

**Common weak answers:** Set FD probe to `/` returning 401 as unhealthy without fixing; disable health probes; single global origin ignoring latency; use liveness endpoint showing DOWN during intentional maintenance.

**Follow-up probes (with answers):**

**Q:** Readiness failing but liveness passing—should FD route traffic?
**A:** No—readiness removed from Service endpoints; FD/backend pool should mirror Service ready endpoints only. Fix readiness, not bypass with liveness.

---

### S10. Hybrid Java app loses Entra token refresh on-premises

**Situation:** Spring Boot app runs on-premises Windows VMs calling Azure SQL and Blob via Entra service principal with client secret rotating quarterly. After secret rotation in Entra, app still uses old secret until manual service restart—downtime window violates SLA.

**What they're testing:** Credential rotation, managed identity limitations on-prem, Azure Arc, Key Vault secret refs, and Java credential chain.

**How to structure your answer:**
- Client secret rotation without restart
- Key Vault as secret source with refresh
- Azure Arc enabled servers MI path
- Spring Cloud Azure credential refresh

**Model answer:** Hardcoded secret in `application.properties` requires restart—unacceptable. Move secret to on-prem Key Vault or HashiCorp Vault synced from Entra; Spring `DefaultAzureCredential` or `ClientSecretCredential` bean loading from vault with scheduled refresh or file watch. Better long-term: Azure Arc-enabled servers grant system-assigned MI to VM, eliminate SP secret—Java uses same DefaultAzureCredential as cloud. Short-term rotation runbook: update Key Vault secret version, app polls `SecretClient.getSecret` on failure with exponential backoff or `@Scheduled` refresh—bean reconstructs credential without full JVM restart if abstraction wraps token provider. For hybrid SQL Entra auth, token acquisition caches ~60 minutes—handle `AuthenticationException` triggering re-acquire. Monitor Entra sign-in logs for `7000222` invalid client secret. Automate rotation with Entra secret max age 90 days + alert at 14 days. Senior architects push Arc/MI over perpetual secrets; Java code identical cloud and hybrid via credential chain.

**Common weak answers:** Never rotate secrets; extend secret expiry to 10 years; embed new secret in jar; restart production at 3am without automation.

**Follow-up probes (with answers):**

**Q:** Arc MI vs service principal on VM?
**A:** Arc projects hybrid identity into Entra—passwordless, RBAC like cloud MI. SP still valid when Arc adoption blocked but requires secret lifecycle automation.

---
