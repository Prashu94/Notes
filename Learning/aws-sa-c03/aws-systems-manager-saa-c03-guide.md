# AWS Systems Manager (SSM) – SAA-C03 Exam Comprehensive Guide

AWS Systems Manager is a unified interface that helps you view operational data from multiple AWS services and automate operational tasks across your AWS resources at scale. For the SAA-C03 (Solutions Architect Associate) exam, you must understand the major Systems Manager capabilities, their use cases, integrations, security boundaries, and how they help implement operational excellence, cost optimization, reliability, performance efficiency, and security.

---
## 1. Core Value Proposition
Systems Manager provides: 
- Centralized operational tooling for hybrid and multi-account environments
- Secure, auditable, agent-based + agentless operations
- Automation at scale for patching, configuration, remediation
- Inventory, governance, and change control
- Parameter and secret configuration management
- Secure shell/session replacement (no inbound ports, no bastions)

Key identity concept: Least privilege via IAM roles (instance profile + user permissions). Many capabilities depend on the SSM Agent installed on managed nodes (EC2, on-premise servers, edge devices, some container/VM form factors) plus the `AmazonSSMManagedInstanceCore` policy attached to the instance role.

---
## 2. High-Level Architecture Components
| Component | Purpose | Exam Focus |
|-----------|---------|------------|
| SSM Agent | Runs on managed instances to execute commands, collect inventory, send/receive messages | Must be installed + instance needs IAM role |
| Parameter Store | Hierarchical, versioned, encrypted (KMS) configuration + plain text storage | Secure config, decouple secrets; Standard vs Advanced params |
| Session Manager | Secure shell/PowerShell/port forwarding without opening inbound ports or bastions | No SSH keys, logs to CloudWatch Logs & S3 |
| Automation | Define runbooks (YAML/JSON) to orchestrate actions (patch, AMI creation, remediation) | Managed vs custom runbooks, approval steps |
| Run Command | Execute ad hoc or scheduled commands across fleets | No SSH needed; rate limiting & concurrency controls |
| Patch Manager | Automate patch baseline application & maintenance windows | Baselines: Predefined vs custom; compliance reporting |
| State Manager | Enforce and maintain desired state (document association) | Drift correction |
| Inventory | Collect metadata (apps, network configs, files, registry, etc.) | Query via SSM + Athena |
| Incident Manager (integrated) | Respond to critical events | Not deep focus but know integration |
| OpsCenter / OpsItems | Centralize operational issues with contextual data | Ties into CloudWatch/Config/Alarm events |
| Change Manager | Standardize, approve, track operational changes | Change templates + approvals |
| Explorer | Aggregated operational dashboard across accounts/regions | Governance & multi-account mgmt |
| Maintenance Windows | Define scheduled windows to perform tasks | Used by Run Command, Automation, Patch |
| Distributor | Package distribution and agent updates | Controlled binary delivery |
| Hybrid Activations | Manage on-premise/other cloud servers | Activation code/id, becomes managed instance (mi-*) |

---
## 3. Managed Instances & Hybrid Activations
Managed Instance Requirements:
- SSM Agent installed (Amazon Linux 2 + current Windows AMIs include it by default)
- Instance profile with `AmazonSSMManagedInstanceCore` (includes SSM + EC2 messages + SSMMessages + KMS decrypt if needed)
- Outbound internet or VPC endpoints: `ssm`, `ec2messages`, `ssmmessages`, `logs`, `s3`, `kms` as needed
- Tags help target operations (Run Command/State Manager associations)

Hybrid Activations:
- Register on-premises servers with an Activation (Activation Code + ID)
- Each server appears with an `mi-` ID
- IAM role linked to activation defines permissions
- Use cases: central patching, inventory, remote management, parameterized configs

Exam Tip: No inbound connectivity required; operations are agent-initiated (poll model). This is a security differentiator vs SSH/RDP.

---
## 4. Parameter Store
Features:
- Hierarchical paths: `/app/env/component/key`
- Standard vs Advanced parameters (Advanced adds >4KB size, policies, higher throughput, costs)
- Data types: String, StringList, SecureString
- Versioning & history
- KMS encryption for SecureString (custom or AWS managed key)
- Parameter policies: Expiration, no-change alert, compliance (Advanced only)
- Integration: Lambda env retrieval, CloudFormation dynamic references (`{{resolve:ssm:/path}}` or `{{resolve:ssm-secure:/path:version}}`), ECS task definitions, CodeBuild, AppConfig, EC2 user data scripts

Performance Considerations:
- Standard throughput: 40 req/s (shared) | Advanced: higher (1000 req/s with caching)
- Caching via SSM Agent or SDK local caching libs reduces API costs + throttling

When to use Parameter Store vs Secrets Manager:
- Use Parameter Store for general configuration, less-rotated values; Secrets Manager for credential rotation workflows (RDS/Redshift/DocumentDB credentials) & secret rotation automation
- Exam scenario: If rotation required every 30 days automatically -> Secrets Manager

Security:
- Enforce encryption via IAM condition `ssm:Tier` or `ssm:ResourceTag`
- Restrict path hierarchy with IAM resource ARNs (e.g., `arn:aws:ssm:region:acct:parameter/myapp/prod/*`)

Common Exam Gotchas:
- `SecureString` values are decrypted only for authorized principals
- Use `kms:Decrypt` permissions on the key + SSM parameter permissions
- CloudFormation dynamic reference resolves at deploy time (stored in template history unencrypted? No – resolved server-side, not persisted in plaintext in stack template body)

---
## 5. Session Manager
Use Cases:
- Replace bastion hosts & SSH/RDP inbound rules
- IAM + MFA + CloudTrail auditing for shell access
- Port forwarding (e.g., access internal DB from dev laptop) without opening ports

Security & Compliance:
- No inbound ports; agent establishes secure channel
- Logging: Stream session logs & commands to S3 and/or CloudWatch Logs
- KMS encryption for logs and data in transit + encryption at rest
- Restrict access via IAM policies (`ssm:StartSession`, `ssm:DescribeSessions`)
- SCPs can restrict session usage across org

Advanced:
- Document-based session preferences (e.g., idle timeout)
- Port forwarding vs SSH key injection (Session Manager can integrate with SSH via proxy command)

Exam Distinctions:
- Need interactive shell with full audit trail -> Session Manager
- Need just remote command execution, no interactive terminal -> Run Command
- Avoid storing SSH keys, minimize attack surface -> Session Manager

---
## 6. Run Command
Run ad hoc or targeted commands across a fleet using SSM Documents.

Key Concepts:
- Command Documents: JSON/YAML (AWS- prefixed = AWS managed)
- Targeting: Instance IDs, tags, resource groups
- Concurrency & error thresholds (e.g., 50% concurrency, halt if >10% errors)
- Output Options: S3 bucket + CloudWatch Logs
- Rate control protects from widespread impact / surge on dependencies

Use Cases:
- Install packages, patch point issues, gather diagnostics, bootstrap
- Multi-account operations via AWS Organizations + Delegated Admin (Explorer/Run Command cross-account)

Exam Tip: For repeated desired state apply -> Use State Manager; for one-off command -> Run Command.

---
## 7. State Manager
Maintains and enforces desired state via Associations (document + targets + schedule).

Capabilities:
- Apply patches, join domain, configure CloudWatch Agent, baseline configs
- Re-apply if drift detected (periodic or event-based schedule like cron or rate expressions)
- Integrates with Maintenance Windows for controlled change periods

Exam Scenario: Guarantee antivirus definitions installed daily across all prod Windows instances -> State Manager association with schedule.

---
## 8. Patch Manager
Automates OS and software patching.

Key Elements:
- Patch Baseline: Approve/Reject patches by classification (Security/Critical/Important), severity, product, auto-approval delays
- Predefined Baselines: AWS provided (e.g., for Amazon Linux, Windows)
- Custom Baselines: Tailor to compliance requirements
- Patch Groups: Tag instances with `Patch Group=Prod` to map to baseline
- Maintenance Windows: Execute patch operations in approved window
- Compliance Reporting: View patch compliance state (COMPLIANT/NON_COMPLIANT)

Workflow:
1. Tag instances with Patch Group
2. Associate baseline (auto or explicit)
3. Schedule patching via Maintenance Window or Automation
4. Review compliance in Explorer / Compliance dashboard

Exam Distinctions:
- Need to patch only security patches within 3 days: Use auto-approval + delay + maintenance window
- Need compliance reports for auditors: Patch Manager + Compliance + AWS Config (advanced)

---
## 9. Maintenance Windows
Define recurring windows for safe operations.
- Register tasks: Run Command, Automation, Lambda, Step Functions
- Control: Max concurrency + error threshold
- Ensure operational tasks don’t run outside approved times (governance)

Exam Tip: Use with Patch Manager and State Manager to ensure changes happen during low-impact time.

---
## 10. Automation (Runbooks)
Automates multi-step operations and remediation.

Runbook Types:
- AWS managed (`AWS-CreateImage`, `AWS-RestartEC2Instance`)
- Community
- Custom (YAML/JSON with steps: `aws:runCommand`, `aws:invokeLambda`, `aws:createImage`, branching, approvals)

Features:
- Parameters & outputs (can feed into other workflows)
- Approval steps (`aws:approve`) with SNS notifications
- Rate control & concurrency
- Integration: EventBridge rule triggers automation on event (e.g., CloudWatch alarm -> restart)
- Automation execution role vs target instance role separation

Use Cases:
- Golden AMI pipeline (update, harden, test, create AMI, tag, distribute)
- Self-healing remediation (e.g., high memory -> restart service)
- Compliance enforcement (ensure specific agent installed)

Exam Scenario: Need standardized, auditable AMI creation -> SSM Automation Runbook `AWS-UpdateLinuxAmi` or custom chain.

---
## 11. Change Manager
Provides change request lifecycle (plan, approve, implement) integrated with Automation.
- Change Templates define required parameters, approvals
- Change Requests implemented via runbooks
- Supports standard vs emergency changes
- Audit trail preserved

Exam Tip: For controlled, auditable operational change with approvals, pick Change Manager (not just a runbook alone).

---
## 12. OpsCenter & OpsItems
Central place to view, investigate, and remediate operational issues.
- OpsItems include contextual data: related CloudWatch alarms, Config changes, logs, events
- Can attach automation runbooks for remediation
- Prioritize with severity; integrate with ChatOps or ticketing

Exam Angle: Provide unified operations dashboard for multiple accounts -> Systems Manager Explorer + OpsCenter.

---
## 13. Explorer
Aggregated operations + compliance view across accounts/regions.
- Supports AWS Organizations delegated admin
- Surfaces patch compliance, inventory coverage, OpsItems
- Tag-based filtering for business context

---
## 14. Inventory & Compliance
Inventory:
- Collect metadata: Installed applications, network configs, services, registry (Windows), files
- Query via `ListInventoryEntries` or integrate with Athena (store in S3)
- Use tags + resource data sync

Compliance:
- Central view of patch, association (State Manager), custom compliance items
- Extend with custom items via `PutComplianceItems`

Exam Scenario: Need to track all installed versions of Log4j across fleet -> Inventory + Athena queries.

---
## 15. Distributor
Package management for distributing & updating software packages.
- Store versioned installers
- Control access with IAM
- Deploy via State Manager association or Run Command

Exam Use Case: Roll out internal security agent across hybrid fleet -> Distributor + State Manager.

---
## 16. AppConfig (Related Service Integration)
Though not strictly part of SSM core exam domain, know difference:
- AppConfig used for feature flagging, progressive config rollout, validation
- Parameter Store or Secrets Manager is the backing store for config values
- Exam Distinction: If safe deployment of dynamic configuration with rollback needed -> AppConfig

---
## 17. Security, IAM, and Logging
IAM Roles:
- Instance profile: grants SSM agent permissions (SSM, EC2Messages, SSMMessages, Logs, S3, KMS)
- Session initiation: User/role must have `ssm:StartSession` + resource-level constraints
- Parameter Store access: path scoping & KMS key permissions

Network:
- Prefer VPC Endpoints for private access (Interface endpoints); reduces need for NAT/Internet
- Required endpoints: `com.amazonaws.region.ssm`, `ec2messages`, `ssmmessages`; plus `logs`, `s3`, `kms` depending on features

Encryption:
- KMS for SecureString and session data logs encryption
- S3 bucket encryption for logs/artifacts

Auditing:
- CloudTrail logs API interactions
- Session logs to CW Logs / S3; command history kept

Least Privilege Strategy:
- Separate automation execution role from resource target roles
- Use condition keys: `ssm:resourceTag/Environment`, `ssm:SessionDocumentAccessCheck`

---
## 18. Multi-Account & Governance
Patterns:
- Use AWS Organizations + Delegated Administrator for Systems Manager centralization
- Resource Data Sync to central S3 bucket for inventory & compliance aggregation
- Service Control Policies to restrict high-risk docs or session types
- Tagging standards for environment, cost center, compliance scope

Exam Scenario: Central ops team needs aggregated patch compliance for all prod accounts -> Resource Data Sync + Explorer.

---
## 19. Pricing Considerations (High-Level)
- Most core features (Run Command, Session Manager, Parameter Store Standard tier) are no additional cost
- Advanced Parameter Store incurs charges (higher throughput, larger size, policies)
- Automation: Standard vs Premium steps (Premium = charged; approvals, 3rd-party, some integrations). Associate exam should know concept, not exact price
- AppConfig, OpsCenter advanced usage, and some integrations may incur charges

Exam Tip: If asked how to avoid new costs for config storage -> Use Standard Parameters if under limits.

---
## 20. Comparing Similar Services (Exam Differentiators)
| Need | Choose |
|------|--------|
| Replace bastion host, record shell | Session Manager |
| Execute one-time fleet command | Run Command |
| Enforce recurring state (agent installed) | State Manager |
| Multi-step remediation with approvals | Automation Runbook + Approval Step |
| Patch OS monthly with compliance | Patch Manager + Maintenance Window |
| Store encrypted small config values | Parameter Store SecureString |
| Auto-rotate database secrets | Secrets Manager |
| Progressive config rollout & validation | AppConfig |
| Create golden AMI pipeline | SSM Automation |
| Centralize ops issues | OpsCenter |
| Governance & change approvals | Change Manager |

---
## 20.1. AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing AWS Systems Manager resources and operations.

### Prerequisites

```bash
# Install or update AWS CLI
# macOS/Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Default region, Output format (json)
```

### Parameter Store Operations

```bash
# Put a standard parameter (String)
aws ssm put-parameter \
  --name "/myapp/dev/api-endpoint" \
  --type "String" \
  --value "https://api.example.com" \
  --description "API endpoint for development environment"

# Put a secure string parameter (encrypted)
aws ssm put-parameter \
  --name "/myapp/prod/db-password" \
  --type "SecureString" \
  --value "SuperSecurePassword123!" \
  --description "Production database password" \
  --key-id "alias/aws/ssm"

# Put parameter with custom KMS key
aws ssm put-parameter \
  --name "/myapp/prod/api-key" \
  --type "SecureString" \
  --value "sk-1234567890abcdef" \
  --key-id "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012" \
  --tags Key=Environment,Value=Production Key=Team,Value=Backend

# Put StringList parameter
aws ssm put-parameter \
  --name "/myapp/allowed-ips" \
  --type "StringList" \
  --value "192.168.1.1,192.168.1.2,192.168.1.3" \
  --description "Allowed IP addresses"

# Update existing parameter (overwrite)
aws ssm put-parameter \
  --name "/myapp/prod/db-password" \
  --type "SecureString" \
  --value "NewSecurePassword456!" \
  --overwrite

# Get parameter value
aws ssm get-parameter \
  --name "/myapp/dev/api-endpoint"

# Get parameter with decryption (for SecureString)
aws ssm get-parameter \
  --name "/myapp/prod/db-password" \
  --with-decryption

# Get multiple parameters
aws ssm get-parameters \
  --names "/myapp/dev/api-endpoint" "/myapp/dev/db-host" "/myapp/dev/db-port"

# Get multiple parameters with decryption
aws ssm get-parameters \
  --names "/myapp/prod/db-password" "/myapp/prod/api-key" \
  --with-decryption

# Get parameters by path (hierarchical)
aws ssm get-parameters-by-path \
  --path "/myapp/prod" \
  --recursive

# Get parameters by path with decryption
aws ssm get-parameters-by-path \
  --path "/myapp/prod" \
  --recursive \
  --with-decryption

# Get parameter history
aws ssm get-parameter-history \
  --name "/myapp/prod/db-password"

# Delete parameter
aws ssm delete-parameter \
  --name "/myapp/dev/api-endpoint"

# Delete multiple parameters
aws ssm delete-parameters \
  --names "/myapp/dev/api-endpoint" "/myapp/dev/db-host"

# List all parameters
aws ssm describe-parameters

# List parameters with specific filters
aws ssm describe-parameters \
  --filters "Key=Name,Values=/myapp/prod"

# List parameters with tags
aws ssm describe-parameters \
  --parameter-filters "Key=tag:Environment,Values=Production"

# Add tags to parameter
aws ssm add-tags-to-resource \
  --resource-type "Parameter" \
  --resource-id "/myapp/prod/api-key" \
  --tags Key=CostCenter,Value=Engineering Key=Compliance,Value=Required

# List tags for parameter
aws ssm list-tags-for-resource \
  --resource-type "Parameter" \
  --resource-id "/myapp/prod/api-key"

# Remove tags from parameter
aws ssm remove-tags-from-resource \
  --resource-type "Parameter" \
  --resource-id "/myapp/prod/api-key" \
  --tag-keys CostCenter

# Label parameter version
aws ssm label-parameter-version \
  --name "/myapp/prod/db-password" \
  --parameter-version 3 \
  --labels "stable" "production"

# Get parameter by label
aws ssm get-parameter \
  --name "/myapp/prod/db-password:stable" \
  --with-decryption
```

### Session Manager Operations

```bash
# Start interactive session with instance
aws ssm start-session \
  --target i-0123456789abcdef0

# Start session with custom document
aws ssm start-session \
  --target i-0123456789abcdef0 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["3306"],"localPortNumber":["13306"]}'

# Start SSH session (port forwarding for SSH)
aws ssm start-session \
  --target i-0123456789abcdef0 \
  --document-name AWS-StartSSHSession

# List active sessions
aws ssm describe-sessions \
  --state Active

# List all sessions (active and history)
aws ssm describe-sessions \
  --state History

# Terminate session
aws ssm terminate-session \
  --session-id "john.doe-0123456789abcdef0"

# Get session details
aws ssm describe-sessions \
  --filters "key=SessionId,value=john.doe-0123456789abcdef0"

# Configure session preferences
aws ssm create-document \
  --name SessionManagerPreferences \
  --document-type Session \
  --content '{
    "schemaVersion": "1.0",
    "description": "Session Manager preferences",
    "sessionType": "Standard_Stream",
    "inputs": {
      "s3BucketName": "my-session-logs-bucket",
      "s3KeyPrefix": "session-logs/",
      "s3EncryptionEnabled": true,
      "cloudWatchLogGroupName": "/aws/ssm/session-logs",
      "cloudWatchEncryptionEnabled": true,
      "kmsKeyId": "alias/my-kms-key",
      "runAsEnabled": false,
      "idleSessionTimeout": "20"
    }
  }'
```

### Run Command Operations

```bash
# Run shell script on Linux instance
aws ssm send-command \
  --instance-ids "i-0123456789abcdef0" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["echo Hello World","uptime","df -h"]' \
  --comment "System diagnostics"

# Run PowerShell script on Windows instance
aws ssm send-command \
  --instance-ids "i-0123456789abcdef1" \
  --document-name "AWS-RunPowerShellScript" \
  --parameters 'commands=["Get-Service","Get-Process | Select -First 10"]'

# Run command on multiple instances by tag
aws ssm send-command \
  --targets "Key=tag:Environment,Values=Production" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo yum update -y","sudo systemctl restart httpd"]' \
  --comment "Update and restart web servers"

# Run command with output to S3
aws ssm send-command \
  --instance-ids "i-0123456789abcdef0" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["ps aux","netstat -tulpn"]' \
  --output-s3-bucket-name "my-ssm-output-bucket" \
  --output-s3-key-prefix "run-command-output/"

# Run command with CloudWatch output
aws ssm send-command \
  --instance-ids "i-0123456789abcdef0" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["tail -100 /var/log/messages"]' \
  --cloud-watch-output-config '{"CloudWatchLogGroupName":"/aws/ssm/run-command","CloudWatchOutputEnabled":true}'

# Run command with timeout and concurrency control
aws ssm send-command \
  --targets "Key=tag:Role,Values=WebServer" \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo service nginx restart"]' \
  --timeout-seconds 600 \
  --max-concurrency "5" \
  --max-errors "1"

# List command invocations
aws ssm list-commands

# Get command status
aws ssm list-command-invocations \
  --command-id "12345678-1234-1234-1234-123456789012"

# Get command output
aws ssm get-command-invocation \
  --command-id "12345678-1234-1234-1234-123456789012" \
  --instance-id "i-0123456789abcdef0"

# Cancel command
aws ssm cancel-command \
  --command-id "12345678-1234-1234-1234-123456789012"

# Install CloudWatch agent via Run Command
aws ssm send-command \
  --targets "Key=tag:MonitoringGroup,Values=WebServers" \
  --document-name "AWS-ConfigureAWSPackage" \
  --parameters '{"action":["Install"],"name":["AmazonCloudWatchAgent"]}'
```

### Patch Manager Operations

```bash
# Create custom patch baseline (Linux)
aws ssm create-patch-baseline \
  --name "CustomLinuxBaseline" \
  --operating-system "AMAZON_LINUX_2" \
  --approval-rules 'PatchRules=[{PatchFilterGroup={PatchFilters=[{Key=CLASSIFICATION,Values=[Security,Bugfix]},{Key=SEVERITY,Values=[Critical,Important]}]},ApprovalAfterDays=7}]' \
  --description "Custom baseline for Amazon Linux 2"

# Create patch baseline (Windows)
aws ssm create-patch-baseline \
  --name "CustomWindowsBaseline" \
  --operating-system "WINDOWS" \
  --approval-rules 'PatchRules=[{PatchFilterGroup={PatchFilters=[{Key=CLASSIFICATION,Values=[SecurityUpdates,CriticalUpdates]},{Key=MSRC_SEVERITY,Values=[Critical,Important]}]},ApprovalAfterDays=3}]' \
  --description "Custom Windows security baseline"

# Get default patch baseline
aws ssm get-default-patch-baseline

# Register patch baseline for patch group
aws ssm register-patch-baseline-for-patch-group \
  --baseline-id "pb-0123456789abcdef0" \
  --patch-group "Production-WebServers"

# Scan for available patches
aws ssm send-command \
  --targets "Key=tag:PatchGroup,Values=Production-WebServers" \
  --document-name "AWS-RunPatchBaseline" \
  --parameters '{"Operation":["Scan"]}'

# Install patches
aws ssm send-command \
  --targets "Key=tag:PatchGroup,Values=Production-WebServers" \
  --document-name "AWS-RunPatchBaseline" \
  --parameters '{"Operation":["Install"]}'

# Get patch compliance summary
aws ssm describe-instance-patch-states \
  --instance-ids i-0123456789abcdef0

# List patch baselines
aws ssm describe-patch-baselines

# Get patch baseline details
aws ssm get-patch-baseline \
  --baseline-id "pb-0123456789abcdef0"

# Update patch baseline
aws ssm update-patch-baseline \
  --baseline-id "pb-0123456789abcdef0" \
  --approval-rules 'PatchRules=[{PatchFilterGroup={PatchFilters=[{Key=CLASSIFICATION,Values=[Security]},{Key=SEVERITY,Values=[Critical]}]},ApprovalAfterDays=0}]'

# Deregister patch baseline
aws ssm deregister-patch-baseline-for-patch-group \
  --baseline-id "pb-0123456789abcdef0" \
  --patch-group "Production-WebServers"

# Delete patch baseline
aws ssm delete-patch-baseline \
  --baseline-id "pb-0123456789abcdef0"

# Get patch compliance for instance
aws ssm describe-instance-patches \
  --instance-id "i-0123456789abcdef0"

# Describe patch group state
aws ssm describe-patch-group-state \
  --patch-group "Production-WebServers"
```

### State Manager Operations

```bash
# Create State Manager association (run script periodically)
aws ssm create-association \
  --name "AWS-RunShellScript" \
  --targets "Key=tag:Environment,Values=Production" \
  --parameters '{"commands":["sudo yum update -y","sudo systemctl status httpd"]}' \
  --schedule-expression "cron(0 2 ? * SUN *)" \
  --association-name "WeeklySystemUpdate"

# Create association to install CloudWatch agent
aws ssm create-association \
  --name "AWS-ConfigureAWSPackage" \
  --targets "Key=instanceids,Values=*" \
  --parameters '{"action":["Install"],"name":["AmazonCloudWatchAgent"]}' \
  --schedule-expression "rate(30 days)" \
  --association-name "InstallCloudWatchAgent"

# Create association with output location
aws ssm create-association \
  --name "AWS-RunShellScript" \
  --targets "Key=tag:Role,Values=Database" \
  --parameters '{"commands":["df -h","free -m"]}' \
  --schedule-expression "rate(1 hour)" \
  --output-location '{"S3Location":{"OutputS3BucketName":"my-ssm-output","OutputS3KeyPrefix":"state-manager/"}}' \
  --association-name "HourlyDiskCheck"

# List associations
aws ssm list-associations

# Describe association
aws ssm describe-association \
  --association-id "12345678-1234-1234-1234-123456789012"

# Get association status
aws ssm describe-association-execution-targets \
  --association-id "12345678-1234-1234-1234-123456789012" \
  --execution-id "12345678-1234-1234-1234-123456789012"

# Update association
aws ssm update-association \
  --association-id "12345678-1234-1234-1234-123456789012" \
  --schedule-expression "cron(0 3 ? * SUN *)" \
  --parameters '{"commands":["sudo yum update -y"]}'

# Delete association
aws ssm delete-association \
  --association-id "12345678-1234-1234-1234-123456789012"
```

### Maintenance Windows Operations

```bash
# Create maintenance window
aws ssm create-maintenance-window \
  --name "ProductionPatchWindow" \
  --description "Monthly patching for production servers" \
  --schedule "cron(0 2 ? * SUN#1 *)" \
  --duration 4 \
  --cutoff 1 \
  --allow-unassociated-targets \
  --tags Key=Environment,Value=Production

# Register target with maintenance window
aws ssm register-target-with-maintenance-window \
  --window-id "mw-0123456789abcdef0" \
  --target-type "INSTANCE" \
  --targets "Key=tag:PatchGroup,Values=Production-WebServers" \
  --owner-information "Production Web Servers"

# Register task with maintenance window (Run Command)
aws ssm register-task-with-maintenance-window \
  --window-id "mw-0123456789abcdef0" \
  --target-id "12345678-1234-1234-1234-123456789012" \
  --task-arn "AWS-RunPatchBaseline" \
  --task-type "RUN_COMMAND" \
  --priority 1 \
  --max-concurrency "10" \
  --max-errors "5" \
  --task-invocation-parameters 'RunCommand={Parameters={Operation=[Install]}}'

# Register Lambda task with maintenance window
aws ssm register-task-with-maintenance-window \
  --window-id "mw-0123456789abcdef0" \
  --task-arn "arn:aws:lambda:us-east-1:123456789012:function:MyMaintenanceFunction" \
  --task-type "LAMBDA" \
  --priority 1 \
  --max-concurrency "1" \
  --max-errors "1"

# List maintenance windows
aws ssm describe-maintenance-windows

# Get maintenance window details
aws ssm get-maintenance-window \
  --window-id "mw-0123456789abcdef0"

# List maintenance window executions
aws ssm describe-maintenance-window-executions \
  --window-id "mw-0123456789abcdef0"

# Update maintenance window
aws ssm update-maintenance-window \
  --window-id "mw-0123456789abcdef0" \
  --schedule "cron(0 3 ? * SUN#1 *)" \
  --duration 6

# Delete maintenance window
aws ssm delete-maintenance-window \
  --window-id "mw-0123456789abcdef0"
```

### Inventory Operations

```bash
# Get inventory for instance
aws ssm get-inventory \
  --filters "Key=AWS:InstanceInformation.InstanceId,Values=i-0123456789abcdef0"

# List inventory entries
aws ssm list-inventory-entries \
  --instance-id "i-0123456789abcdef0" \
  --type-name "AWS:Application"

# Get inventory schema
aws ssm get-inventory-schema

# Put inventory (custom inventory)
aws ssm put-inventory \
  --instance-id "i-0123456789abcdef0" \
  --items '[{
    "TypeName": "Custom:MyApplication",
    "SchemaVersion": "1.0",
    "CaptureTime": "2026-02-08T10:00:00Z",
    "Content": [{
      "Name": "MyApp",
      "Version": "1.2.3",
      "Status": "Running"
    }]
  }]'

# Create resource data sync
aws ssm create-resource-data-sync \
  --sync-name "MyInventorySync" \
  --s3-destination "BucketName=my-inventory-bucket,Prefix=inventory/,SyncFormat=JsonSerDe,Region=us-east-1"

# List resource data syncs
aws ssm list-resource-data-sync

# Delete resource data sync
aws ssm delete-resource-data-sync \
  --sync-name "MyInventorySync"
```

### Documents Management

```bash
# List SSM documents
aws ssm list-documents

# List documents by owner
aws ssm list-documents \
  --filters "Key=Owner,Values=Self"

# Describe document
aws ssm describe-document \
  --name "AWS-RunShellScript"

# Get document content
aws ssm get-document \
  --name "AWS-RunShellScript"

# Create custom document
aws ssm create-document \
  --name "MyCustomRunbook" \
  --document-type "Command" \
  --content file://my-runbook.json \
  --tags Key=Purpose,Value=Automation

# Update document
aws ssm update-document \
  --name "MyCustomRunbook" \
  --content file://my-runbook-v2.json \
  --document-version '$LATEST'

# Delete document
aws ssm delete-document \
  --name "MyCustomRunbook"

# Share document with account
aws ssm modify-document-permission \
  --name "MyCustomRunbook" \
  --permission-type "Share" \
  --account-ids-to-add "123456789012"

# Make document public
aws ssm modify-document-permission \
  --name "MyCustomRunbook" \
  --permission-type "Share" \
  --account-ids-to-add "all"
```

### OpsCenter Operations

```bash
# Create OpsItem
aws ssm create-ops-item \
  --title "High CPU usage on production instances" \
  --description "CPU utilization exceeded 90% threshold" \
  --priority 2 \
  --source "CloudWatch" \
  --operational-data '{
    "CloudWatchAlarm": {
      "Value": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighCPU",
      "Type": "SearchableString"
    }
  }' \
  --notifications '[{
    "Arn": "arn:aws:sns:us-east-1:123456789012:ops-notifications"
  }]' \
  --tags Key=Environment,Value=Production

# List OpsItems
aws ssm describe-ops-items

# List OpsItems with filters
aws ssm describe-ops-items \
  --ops-item-filters "Key=Status,Values=Open,Operator=Equal"

# Get OpsItem details
aws ssm get-ops-item \
  --ops-item-id "oi-0123456789abcdef0"

# Update OpsItem status
aws ssm update-ops-item \
  --ops-item-id "oi-0123456789abcdef0" \
  --status "InProgress"

# Add related item to OpsItem
aws ssm create-ops-item-related-item \
  --ops-item-id "oi-0123456789abcdef0" \
  --association-type "RelatesTo" \
  --resource-type "AWS::SSM::Document" \
  --resource-uri "arn:aws:ssm:us-east-1:123456789012:document/MyRunbook"
```

### Compliance Operations

```bash
# Get compliance summary
aws ssm list-resource-compliance-summaries

# Get compliance summary by type
aws ssm list-compliance-summaries

# Get instance compliance
aws ssm list-compliance-items \
  --resource-ids "i-0123456789abcdef0" \
  --resource-types "ManagedInstance"

# Put custom compliance item
aws ssm put-compliance-items \
  --resource-id "i-0123456789abcdef0" \
  --resource-type "ManagedInstance" \
  --compliance-type "Custom:AntiVirus" \
  --execution-summary "ExecutionTime=2026-02-08T10:00:00Z,ExecutionId=12345" \
  --items '[{
    "Id": "av-scan-1",
    "Title": "Antivirus scan completed",
    "Severity": "INFORMATIONAL",
    "Status": "COMPLIANT"
  }]'

# Get compliance details for patch
aws ssm describe-instance-patches \
  --instance-id "i-0123456789abcdef0" \
  --filters "Key=State,Values=Missing"
```

### Managed Instances Operations

```bash
# List managed instances
aws ssm describe-instance-information

# List managed instances with filters
aws ssm describe-instance-information \
  --filters "Key=tag:Environment,Values=Production"

# Get instance details
aws ssm describe-instance-information \
  --instance-information-filter-list "key=InstanceIds,valueSet=i-0123456789abcdef0"

# Create hybrid activation (for on-premises)
aws ssm create-activation \
  --default-instance-name "OnPremServer" \
  --iam-role "SSMServiceRole" \
  --registration-limit 10 \
  --expiration-date "2026-12-31T23:59:59" \
  --tags Key=Location,Value=DataCenter1

# Delete activation
aws ssm delete-activation \
  --activation-id "12345678-1234-1234-1234-123456789012"

# Deregister managed instance
aws ssm deregister-managed-instance \
  --instance-id "mi-0123456789abcdef0"
```

### Automation Runbook Operations

```bash
# Start automation execution
aws ssm start-automation-execution \
  --document-name "AWS-RestartEC2Instance" \
  --parameters "InstanceId=i-0123456789abcdef0"

# Start automation with multiple parameters
aws ssm start-automation-execution \
  --document-name "AWS-CreateImage" \
  --parameters "InstanceId=i-0123456789abcdef0,NoReboot=true,ImageName=MyAMI-2026-02-08"

# List automation executions
aws ssm describe-automation-executions

# Get automation execution details
aws ssm get-automation-execution \
  --automation-execution-id "12345678-1234-1234-1234-123456789012"

# Stop automation execution
aws ssm stop-automation-execution \
  --automation-execution-id "12345678-1234-1234-1234-123456789012"

# Start automation with targets (multiple instances)
aws ssm start-automation-execution \
  --document-name "AWS-RestartEC2Instance" \
  --targets "Key=tag:RestartGroup,Values=WebServers" \
  --max-concurrency "5" \
  --max-errors "1"
```

### Service Settings Operations

```bash
# Get service setting
aws ssm get-service-setting \
  --setting-id "arn:aws:ssm:us-east-1:123456789012:servicesetting/ssm/parameter-store/high-throughput-enabled"

# Update service setting
aws ssm update-service-setting \
  --setting-id "arn:aws:ssm:us-east-1:123456789012:servicesetting/ssm/parameter-store/high-throughput-enabled" \
  --setting-value "true"

# Reset service setting
aws ssm reset-service-setting \
  --setting-id "arn:aws:ssm:us-east-1:123456789012:servicesetting/ssm/parameter-store/high-throughput-enabled"
```

---
## 21. Common Exam Scenarios & Solutions
1. Scenario: Need secure remote access to EC2 in private subnets without opening ports. Solution: Session Manager with proper IAM; optionally port forwarding.
2. Scenario: Standardize patching across 500 Linux instances with reports. Solution: Patch Manager + Patch Baseline + Patch Group tags + Maintenance Window + Explorer.
3. Scenario: Automatically remediate stopped critical service. Solution: CloudWatch Alarm -> EventBridge -> Automation Runbook (restart service) or Lambda.
4. Scenario: Enforce specific antivirus config daily. Solution: State Manager association.
5. Scenario: Provide centralized view of inventory and patch compliance across accounts. Solution: Resource Data Sync + Explorer.
6. Scenario: Securely store API keys, rarely rotated, accessible by Lambda. Solution: Parameter Store SecureString.
7. Scenario: Need approval before applying infrastructure change script. Solution: Automation Runbook with `aws:approve` step or Change Manager template.
8. Scenario: Roll out internal security agent to all hybrid nodes. Solution: Distributor + State Manager.
9. Scenario: Build hardened AMI monthly automatically. Solution: Automation runbook chain (patch, scan, test, create image, tag).
10. Scenario: Limit command execution to only instances tagged Environment=Prod. Solution: IAM policy with condition on `ssm:resourceTag/Environment`.

---
## 22. Hands-On Example Snippets
### 22.1 Creating a Secure String Parameter (CLI)
```
aws ssm put-parameter \
	--name /myapp/prod/db/password \
	--type SecureString \
	--value 'SuperSecret!' \
	--key-id alias/my-kms-key \
	--overwrite
```

### 22.2 Starting a Session
```
aws ssm start-session --target i-0123456789abcdef0
```

### 22.3 Run Command Across Tag Group
```
aws ssm send-command \
	--document-name AWS-RunShellScript \
	--targets Key=tag:Role,Values=WebServer \
	--parameters commands='yum install -y amazon-cloudwatch-agent' \
	--comment "Install CW Agent" \
	--region us-east-1
```

### 22.4 Sample Automation Execution (Start EC2 Instance)
```
aws ssm start-automation-execution \
	--document-name AWS-StartEC2Instance \
	--parameters InstanceId=i-0123456789abcdef0
```

### 22.5 Maintenance Window Creation
```
aws ssm create-maintenance-window \
	--name "MonthlyPatch" \
	--schedule "cron(0 5 ? * SUN#1 *)" \
	--duration 4 \
	--cutoff 1 \
	--allow-unassociated-targets
```

---
## 23. Design & Architecture Best Practices (Exam Lens)
- Prefer automation & immutable images vs manual patching (Automation + Patch Manager)
- Remove bastions -> Session Manager (improves security posture)
- Enforce tagging early to enable fleet targeting & governance
- Use Parameter Store for decoupling config from code, promote environment isolation
- Integrate CloudWatch + EventBridge + Automation for self-healing patterns
- Use Change Manager / Approval steps for production-impacting operations
- Private VPC endpoints for restricted networks to avoid public internet for management traffic
- Separate read vs write access to parameters for principle of least privilege

---
## 24. Troubleshooting & Operational Insights
Symptoms & Likely Causes:
- Instance not showing as managed: Missing IAM instance profile, SSM Agent not running, blocked outbound endpoints
- Session Manager fails: IAM permission missing, endpoint not reachable, KMS decrypt deny
- Parameter throttling: Exceeded Standard throughput -> use caching or upgrade parameter tier
- Patch compliance low: Incorrect Patch Group tag, baseline not associated, maintenance window not triggered

Diagnostics:
- Check SSM Agent logs (`/var/log/amazon/ssm/`)
- Use `aws ssm describe-instance-information`
- CloudWatch Logs for session or command output

---
## 25. Quick Recall Sheet (High-Yield Exam Points)
- Session Manager: No inbound ports, logs to S3/CW, IAM controlled
- Parameter Store: Hierarchical, SecureString with KMS, Standard vs Advanced
- Patch Manager: Baseline + Patch Group tag + Maintenance Window
- State Manager: Enforce recurring config (drift correction)
- Run Command: One-time fleet actions with rate + error controls
- Automation: Runbooks for multi-step remediation & AMI pipelines
- Change Manager: Approvals + governance on operational change
- OpsCenter/Explorer: Central aggregated operations view
- Distributor: Software package distribution
- Hybrid Activations: On-prem management with Activation Code/ID
- Resource Data Sync: Aggregate inventory/compliance to central S3

---
## 26. Practice Questions (Self-Test)
1. You need secure CLI shell access to private EC2 instances without opening any inbound ports and want all commands logged centrally. Which service? (Answer: Session Manager)
2. You must apply only critical security patches to production Linux within 48 hours and report compliance. Which combination? (Patch Manager + Custom Baseline + Maintenance Window + Explorer)
3. Store app config values (non-rotated) encrypted and pulled at deploy time via CloudFormation templates. Which service and feature? (Parameter Store SecureString + dynamic references)
4. Automate creation of a hardened AMI monthly with approvals. Which feature? (Automation runbook with approval step)
5. Enforce that a log shipping agent stays installed. Which feature? (State Manager association)
6. Collect metadata of installed software across hybrid fleet and query centrally. Which combination? (Inventory + Resource Data Sync + Athena)
7. Need to restrict parameter path access to only /prod/ for a deployment role. Which mechanism? (IAM policy resource scoping to parameter ARN path)
8. Need single place to see operational issues + related alarms. Which feature? (OpsCenter OpsItems)
9. Need to distribute an internal security agent to all nodes regularly. Which feature? (Distributor + State Manager)
10. Need to reduce risk of unauthorized ad hoc production changes; require approval before execution. Which capability? (Change Manager or Automation with approval)

---
## 27. Final Tips for Exam Day
- Map scenario verbs: "enforce" -> State Manager; "multi-step with approvals" -> Automation / Change Manager; "ad hoc run" -> Run Command; "secure access" -> Session Manager
- Always consider least privilege & no inbound security group exposures
- Pair patch operations with Maintenance Windows for governance
- Distinguish Parameter Store vs Secrets Manager vs AppConfig
- Remember Resource Data Sync purpose (central aggregation)
- Recognize when to use runbook vs Lambda (complex orchestrated vs single action)

---
## 28. References (For Further Study)
- AWS Systems Manager User Guide
- AWS SAA-C03 Exam Guide Objectives
- AWS Blogs: Operational Excellence with Systems Manager
- AWS Well-Architected Framework (Operations Pillar)

---
© 2025 – Study reference guide. Not an official AWS publication.

