# Terraform — Practical Exercises

Run in a dev Azure subscription or read expected `plan` output for interview prep. Never `apply` untested changes to prod.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) — 33 exercises total.

---

## Part A — Basic (10)

### Exercise A1 — Init, plan, apply (local state)

**Task:** Create resource group `rg-interview-dev` with provider `azurerm`.

**Solution:**

```hcl
# main.tf
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-interview-dev"
  location = "eastus"
  tags = {
    env = "dev"
  }
}
```

```bash
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

**Expected output:**

```
azurerm_resource_group.rg: Creating...
azurerm_resource_group.rg: Creation complete after 2s [id=/subscriptions/.../resourceGroups/rg-interview-dev]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

---

### Exercise A2 — Variables and outputs

**Task:** Parameterize `location` and `env`; output RG id.

**Solution:**

```hcl
# variables.tf
variable "location" {
  type    = string
  default = "eastus"
}

variable "env" {
  type = string
}

# main.tf
resource "azurerm_resource_group" "rg" {
  name     = "rg-interview-${var.env}"
  location = var.location
  tags     = { env = var.env }
}

# outputs.tf
output "resource_group_id" {
  value = azurerm_resource_group.rg.id
}
```

```bash
terraform apply -var="env=dev" -auto-approve
terraform output resource_group_id
```

**Expected output:**

```
"/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/rg-interview-dev"
```

---

### Exercise A3 — terraform.tfvars

**Task:** Store defaults in `terraform.tfvars`; apply without `-var` flags.

**Solution:**

```hcl
# terraform.tfvars
env      = "qa"
location = "eastus"
```

```bash
terraform plan
```

**Expected output:**

```
# azurerm_resource_group.rg must be replaced
-/+ resource "azurerm_resource_group" "rg" {
      ~ name = "rg-interview-dev" -> "rg-interview-qa"
```

(or update in place if only tags change — depends on prior state)

---

### Exercise A4 — fmt and validate

**Task:** Fix formatting; validate configuration.

**Solution:**

```bash
terraform fmt -recursive
terraform validate
```

**Expected output:**

```
main.tf
Success! The configuration is valid.
```

---

### Exercise A5 — Locals and consistent tags

**Task:** DRY tags via `locals`.

**Solution:**

```hcl
locals {
  common_tags = {
    env     = var.env
    managed = "terraform"
    owner   = "interview-prep"
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-interview-${var.env}"
  location = var.location
  tags     = local.common_tags
}
```

```bash
terraform apply -auto-approve
az group show -n rg-interview-qa --query tags -o json
```

**Expected output:**

```json
{
  "env": "qa",
  "managed": "terraform",
  "owner": "interview-prep"
}
```

---

### Exercise A6 — Data source (existing RG)

**Task:** Read an existing RG created outside Terraform; reference its location.

**Solution:**

```hcl
data "azurerm_resource_group" "existing" {
  name = "rg-interview-qa"
}

resource "azurerm_storage_account" "sa" {
  name                     = "stinterviewqa001"
  resource_group_name      = data.azurerm_resource_group.existing.name
  location                 = data.azurerm_resource_group.existing.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

```bash
terraform plan
```

**Expected output:**

```
# data.azurerm_resource_group.existing will be read
# azurerm_storage_account.sa will be created
Plan: 1 to add, 0 to change, 0 to destroy.
```

---

### Exercise A7 — terraform show

**Task:** Inspect applied state for resource attributes.

**Solution:**

```bash
terraform show -json | jq '.values.root_module.resources[] | select(.address=="azurerm_resource_group.rg") | .values.location'
terraform state show azurerm_resource_group.rg
```

**Expected output:**

```
"eastus"
```

```
# azurerm_resource_group.rg:
resource "azurerm_resource_group" "rg" {
    id       = "/subscriptions/.../resourceGroups/rg-interview-qa"
    location = "eastus"
    name     = "rg-interview-qa"
    tags     = { ... }
}
```

---

### Exercise A8 — Targeted destroy

**Task:** Destroy only the storage account, keep RG.

**Solution:**

```bash
terraform destroy -target=azurerm_storage_account.sa
terraform state list
```

**Expected output:**

```
azurerm_storage_account.sa: Destroying...
Destroy complete! Resources: 1 destroyed.

azurerm_resource_group.rg
```

---

### Exercise A9 — Provider version constraint

**Task:** Pin `azurerm` to `~> 3.110`; run `terraform init -upgrade`.

**Solution:**

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }
}
```

```bash
terraform init -upgrade
```

**Expected output:**

```
- Using previously-installed hashicorp/azurerm v3.116.0
Terraform has been successfully initialized!
```

---

### Exercise A10 — Plan file workflow

**Task:** Save plan to file; apply exact plan in CI simulation.

**Solution:**

```bash
terraform plan -out=tfplan-$(date +%Y%m%d)
terraform show tfplan-20260905 | head -20
terraform apply tfplan-20260905
```

**Expected output:**

```
Saved the plan to: tfplan-20260905
...
Apply complete! Resources: 0 added, 1 changed, 0 destroyed.
```

---

## Part B — Intermediate (10)

### Exercise B1 — Remote state (azurerm backend)

**Task:** Migrate local state to Azure Storage backend.

**Solution:**

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstate001"
    container_name       = "tfstate"
    key                  = "interview/dev.terraform.tfstate"
  }
}
```

```bash
az group create -n rg-tfstate -l eastus
az storage account create -g rg-tfstate -n sttfstate001 --sku Standard_LRS
az storage container create --account-name sttfstate001 -n tfstate
terraform init -migrate-state
```

**Expected output:**

```
Do you want to copy existing state to the new backend? yes
Successfully configured the backend "azurerm"!
```

---

### Exercise B2 — count vs for_each footgun

**Task:** Create 3 NSG rules with `count`; remove middle; observe recreate. Rewrite with `for_each`.

**Solution:**

```hcl
# BAD — count index shift
variable "rules" {
  default = ["ssh", "https", "http"]
}
resource "azurerm_network_security_rule" "bad" {
  count = length(var.rules)
  name  = "allow-${var.rules[count.index]}"
  # ...
}

# GOOD — for_each map
variable "rules_map" {
  default = {
    ssh   = 22
    https = 443
    http  = 80
  }
}
resource "azurerm_network_security_rule" "good" {
  for_each = var.rules_map
  name     = "allow-${each.key}"
  destination_port_range = tostring(each.value)
}
```

Remove `https` from list vs map:

```bash
terraform plan
```

**Expected output (count):**

```
# azurerm_network_security_rule.bad[1] must be replaced
# azurerm_network_security_rule.bad[2] must be replaced
-/+ resource ... http becomes index 1, ssh unchanged
```

**Expected output (for_each):**

```
# azurerm_network_security_rule.good["https"] will be destroyed
Plan: 0 to add, 0 to change, 1 to destroy.
```

Only `https` rule removed — no accidental rename.

---

### Exercise B3 — Read a plan: ForceNew and data loss risk

**Task:** Rename storage account; explain `-/+` and write one-line risk.

**Solution:**

```hcl
resource "azurerm_storage_account" "sa" {
  name = "stinterviewnew001" # was stinterviewqa001
  # ...
}
```

```bash
terraform plan
```

**Expected output:**

```
# azurerm_storage_account.sa must be replaced
-/+ resource "azurerm_storage_account" "sa" {
      ~ name = "stinterviewqa001" -> "stinterviewnew001" # forces replacement
}
```

**One-line risk:** `ForceNew` destroys the old storage account and all blobs unless migrated — **data loss** if backups absent.

---

### Exercise B4 — Module with version pin

**Task:** Consume VNet module from git tag `v1.4.0`; plan upgrade to `v2.0.0`.

**Solution:**

```hcl
module "net" {
  source = "git::https://github.com/example/tf-modules.git//vnet?ref=v1.4.0"

  name                = "vnet-interview"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  address_space       = ["10.10.0.0/16"]
}
```

```bash
# bump ref=v2.0.0 after reading CHANGELOG (subnet naming breaking change)
terraform init -upgrade
terraform plan
```

**Expected output:**

```
module.net.azurerm_subnet.app: Refreshing state...
~ resource changes per v2 CHANGELOG
Plan: 1 to add, 2 to change, 1 to destroy.
```

---

### Exercise B5 — Import existing resource

**Task:** RG exists in portal; import into Terraform; plan until empty.

**Solution:**

```bash
az group create -n rg-imported -l eastus --tags env=imported
```

```hcl
resource "azurerm_resource_group" "imported" {
  name     = "rg-imported"
  location = "eastus"
  tags = {
    env = "imported"
  }
}
```

```bash
terraform import azurerm_resource_group.imported /subscriptions/<sub-id>/resourceGroups/rg-imported
terraform plan
```

**Expected output:**

```
Import successful!
...
No changes. Your infrastructure matches the configuration.
```

---

### Exercise B6 — CI skeleton (plan artifact + gated apply)

**Task:** GitHub Actions: OIDC login, `plan -out`, upload artifact, apply with approval.

**Solution:**

```yaml
# .github/workflows/terraform.yml
name: terraform
on:
  pull_request:
    paths: ["infra/**"]
  push:
    branches: [main]
    paths: ["infra/**"]

permissions:
  id-token: write
  contents: read

jobs:
  plan:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init
      - run: terraform plan -out=tfplan -no-color | tee plan.txt
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: infra/tfplan

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main'
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: hashicorp/setup-terraform@v3
      - uses: actions/download-artifact@v4
        with:
          name: tfplan
          path: infra
      - working-directory: infra
        run: |
          terraform init
          terraform apply -auto-approve tfplan
```

**Expected output:** PR shows plan in logs; merge to `main` waits for environment approval; apply uses exact saved plan.

---

### Exercise B7 — Checkov failure and fix

**Task:** Storage account with public blob access fails CI; fix security settings.

**Solution:**

```hcl
# BAD — fails CKV_AZURE_35
resource "azurerm_storage_account" "bad" {
  name                     = "stpublicbad001"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_nested_items_to_be_public = true
}
```

```bash
checkov -d .
```

**Expected output:**

```
FAILED checks: CKV_AZURE_35: "Ensure default action on Storage Account is Deny"
```

**Fix:**

```hcl
resource "azurerm_storage_account" "good" {
  name                            = "stsecured001"
  resource_group_name             = azurerm_resource_group.rg.name
  location                        = azurerm_resource_group.rg.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false
}
```

```bash
checkov -d .
```

```
Passed checks: 12, Failed checks: 0
```

---

### Exercise B8 — moved block (rename without destroy)

**Task:** Rename resource address `azurerm_resource_group.rg` → `azurerm_resource_group.app`.

**Solution:**

```hcl
moved {
  from = azurerm_resource_group.rg
  to   = azurerm_resource_group.app
}

resource "azurerm_resource_group" "app" {
  name     = "rg-interview-qa"
  location = "eastus"
  tags     = local.common_tags
}
```

```bash
terraform plan
```

**Expected output:**

```
azurerm_resource_group.app: Refreshing state... [id=...] (was azurerm_resource_group.rg)

No changes. Your infrastructure matches the configuration.
```

No destroy/create — state address updated only.

---

### Exercise B9 — Remote state data source (stack composition)

**Task:** App stack reads VNet id from core stack output — no magic CIDR strings in 4 repos.

**Solution:**

```hcl
# core stack outputs.tf
output "vnet_id" {
  value = azurerm_virtual_network.main.id
}

# app stack data.tf
data "terraform_remote_state" "core" {
  backend = "azurerm"
  config = {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstate001"
    container_name       = "tfstate"
    key                  = "core/prod.terraform.tfstate"
  }
}

resource "azurerm_subnet" "aks" {
  name                 = "snet-aks"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = split("/", data.terraform_remote_state.core.outputs.vnet_id)[8]
  address_prefixes     = ["10.10.1.0/24"]
}
```

```bash
terraform plan
```

**Expected output:** Subnet attaches to correct VNet id from remote state; changing core CIDR updates downstream on next plan.

---

### Exercise B10 — Blast radius memo

**Task:** Split stacks `00-identity`, `10-network`, `20-data`, `30-aks`. Why is bad apply on `20-data` worse than `30-aks`?

**Solution:**

```
Stack layout:
  00-identity  — Entra apps, federated creds, RBAC assignments
  10-network   — VNet, subnets, firewall, private DNS
  20-data      — SQL, storage, Key Vault secrets, backups
  30-aks       — cluster, node pools, ingress controllers
```

**Memo:** A mistaken `terraform apply` on `20-data` can **drop databases**, purge storage, or rotate secrets that invalidate all running pods — recovery requires point-in-time restore and coordinated app downtime. A bad `30-aks` apply might recreate node pools or misconfigure ingress — painful but workloads often survive if data plane is intact; Kubernetes redeploy heals faster than restoring SQL.

**Expected output:** One paragraph you can recite in a staff-level interview.

---

## Part C — Hard (8)

### Exercise C1 — Module composition (network + AKS)

**Task:** Root module calls `./modules/network` and `./modules/aks`; pass subnet id.

**Solution:**

```hcl
# modules/network/main.tf
variable "name" {}
variable "rg_name" {}
variable "location" {}
output "aks_subnet_id" { value = azurerm_subnet.aks.id }

# root main.tf
module "network" {
  source   = "./modules/network"
  name     = "vnet-interview"
  rg_name  = azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
}

module "aks" {
  source     = "./modules/aks"
  name       = "aks-interview"
  rg_name    = azurerm_resource_group.rg.name
  subnet_id  = module.network.aks_subnet_id
}
```

```bash
terraform plan
```

**Expected output:**

```
module.network.azurerm_subnet.aks: Creating...
module.aks.azurerm_kubernetes_cluster.main: Creating...
Plan: 8 to add, 0 to change, 0 to destroy.
```

---

### Exercise C2 — Workspaces vs directory-per-env

**Task:** Compare `terraform workspace` vs `env/dev`, `env/prod` folders; pick one for team of 8.

**Solution:**

```bash
# Workspace approach
terraform workspace new dev
terraform workspace new prod
terraform workspace select dev
terraform apply -var-file=dev.tfvars
```

**Tradeoff table:**

| Approach | Pros | Cons |
|----------|------|------|
| Workspaces | Single code path | Easy to apply wrong workspace; shared backend key mistakes |
| Dir per env | Clear blast radius, separate state keys | Duplication unless modules heavy |

**Recommendation for team of 8:** Directory per env (`infra/envs/dev`, `infra/envs/prod`) + separate state keys + CODEOWNERS on prod.

**Expected output:** Written decision with rollback story.

---

### Exercise C3 — lifecycle prevent_destroy

**Task:** Protect production SQL server from accidental destroy.

**Solution:**

```hcl
resource "azurerm_postgresql_flexible_server" "db" {
  name                = "pg-interview-prod"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku_name            = "GP_Standard_D4s_v3"
  storage_mb          = 32768
  version             = "16"

  lifecycle {
    prevent_destroy = true
  }
}
```

```bash
terraform destroy
```

**Expected output:**

```
Error: Instance cannot be destroyed
azurerm_postgresql_flexible_server.db has lifecycle.prevent_destroy set
```

---

### Exercise C4 — Dynamic block for NSG rules

**Task:** Generate ingress rules from a map variable.

**Solution:**

```hcl
variable "ingress_rules" {
  type = map(object({
    priority = number
    port     = number
    source   = string
  }))
  default = {
    https = { priority = 100, port = 443, source = "Internet" }
    ssh   = { priority = 200, port = 22,  source = "10.0.0.0/8" }
  }
}

resource "azurerm_network_security_group" "nsg" {
  name                = "nsg-aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  dynamic "security_rule" {
    for_each = var.ingress_rules
    content {
      name                       = "allow-${security_rule.key}"
      priority                   = security_rule.value.priority
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = tostring(security_rule.value.port)
      source_address_prefix      = security_rule.value.source
      destination_address_prefix = "*"
    }
  }
}
```

```bash
terraform plan -var='ingress_rules={https={priority=100,port=443,source=Internet}}'
```

**Expected output:** Only `allow-https` rule in plan; `ssh` rule destroyed.

---

### Exercise C5 — terraform apply -replace

**Task:** Force new node pool without tainting address in code.

**Solution:**

```bash
terraform apply -replace=azurerm_kubernetes_cluster_node_pool.user
```

**Expected output:**

```
azurerm_kubernetes_cluster_node_pool.user: Destroying...
azurerm_kubernetes_cluster_node_pool.user: Creating...
Apply complete! Resources: 1 added, 0 changed, 1 destroyed.
```

Pods reschedule to new nodes; state address unchanged.

---

### Exercise C6 — Bulk import script

**Task:** Import 3 subnets created manually.

**Solution:**

```bash
#!/usr/bin/env bash
set -euo pipefail
SUB="/subscriptions/<sub-id>"
RG="rg-interview-qa"
VNET="vnet-interview"

for name in snet-aks snet-apps snet-data; do
  terraform import "azurerm_subnet.${name//-/_}" \
    "${SUB}/resourceGroups/${RG}/providers/Microsoft.Network/virtualNetworks/${VNET}/subnets/${name}"
done
terraform plan
```

**Expected output:**

```
azurerm_subnet.snet_aks: Importing...
Import successful!
...
No changes. Your infrastructure matches the configuration.
```

---

### Exercise C7 — IAM role assignment module

**Task:** Reusable module assigns `AcrPull` to AKS kubelet identity.

**Solution:**

```hcl
# modules/role_assignment/main.tf
variable "principal_id" { type = string }
variable "role" { type = string }
variable "scope" { type = string }

resource "azurerm_role_assignment" "this" {
  principal_id         = var.principal_id
  role_definition_name = var.role
  scope                = var.scope
}

# root
module "aks_acr_pull" {
  source       = "./modules/role_assignment"
  principal_id = module.aks.kubelet_identity_object_id
  role         = "AcrPull"
  scope        = azurerm_container_registry.acr.id
}
```

```bash
terraform apply -auto-approve
az role assignment list --assignee <kubelet-id> --scope <acr-id> -o table
```

**Expected output:**

```
Principal                             Role     Scope
------------------------------------  -------  -----------------
<kubelet-object-id>                   AcrPull  .../registries/acrinterviewdev
```

---

### Exercise C8 — Drift detection workflow

**Task:** Portal change causes drift; detect and reconcile.

**Solution:**

```bash
# Someone adds tag in portal:
az group update -n rg-interview-qa --set tags.drill=manual

terraform plan
```

**Expected output:**

```
~ resource "azurerm_resource_group" "app" {
    ~ tags = {
        - "drill" = "manual" -> null
      }
}
Plan: 0 to add, 1 to change, 0 to destroy.
```

```bash
terraform apply -auto-approve   # revert drift
# OR update .tf to include tag if intentional
```

**Scheduled drift (Actions cron):**

```yaml
- run: terraform plan -detailed-exitcode -no-color
  continue-on-error: true
  id: plan
# exit code 2 = changes detected → alert Slack
```

**Expected output:** CI fails with "drift detected" when portal edits bypass Terraform.


### Exercise 29 — OpenTofu init parity check

**Task:** Run `tofu init` and `terraform init` (1.5) on same module; compare lock files.

**Solution:**

```bash
tofu init
terraform init
diff .terraform.lock.hcl || true
tofu plan -out=tofu.plan
terraform plan -out=tf.plan
```

**Expected output:** Plans substantially identical; document any provider source namespace differences in README.

---

### Exercise 30 — import block draft

**Task:** Write an `import` block for existing RG `rg-interview-import`.

**Solution:**

```hcl
import {
  to = azurerm_resource_group.rg
  id = "/subscriptions/SUB/resourceGroups/rg-interview-import"
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-interview-import"
  location = "eastus"
}
```

```bash
terraform plan   # shows Import action
```

**Expected output:** Plan imports 1 resource, 0 unexpected changes if config matches.

---

### Exercise 31 — terraform test mock module

**Task:** Add `.tftest.hcl` asserting module output `environment` equals input.

**Solution:**

```hcl
# tests/tags.tftest.hcl
run "env_tag" {
  command = plan
  module { source = "./modules/tags" }
  variables { env = "qa" }
  assert {
    condition     = output.env_tag == "qa"
    error_message = "env tag mismatch"
  }
}
```

```bash
terraform test
```

**Expected output:** `Success! 1 passed, 0 failed.`

---

### Exercise 32 — check block for public access

**Task:** Add postcondition failing if storage allows public network access.

**Solution:**

```hcl
resource "azurerm_storage_account" "sa" {
  name                     = "stinterviewchk001"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  public_network_access_enabled = false

  lifecycle {
    postcondition {
      condition     = self.public_network_access_enabled == false
      error_message = "Storage must not allow public network access"
    }
  }
}
```

**Expected output:** Apply succeeds when false; flipping to true fails at apply.

---

### Exercise 33 — OpenTofu vs TF pipeline decision memo

**Task:** Write one-page memo comparing license, CI image, and provider pins for org standard.

**Solution:**

```markdown
## Decision: OpenTofu 1.8 for new repos
- License: MPL-2.0 vs BSL 1.6+ — legal approved MPL for internal use
- CI: ghcr.io/opentofu/opentofu:1.8; pin providers identically
- Legacy: Terraform 1.5 frozen until Q3 migration window
- Risk: TFC-only features not used; Blob backend unchanged
- Pilot: network stack plan diff zero before mandate
```

**Expected output:** Reviewable memo with rollback plan and pilot criteria.


---

## Stats

| Section | Count |
|---------|------:|
| Part A — Basic | 12 |
| Part B — Intermediate | 12 |
| Part C — Hard | 9 |
| **Total** | **33** |
