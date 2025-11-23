# Google Compute Engine - ACE Practice Questions

## Question 1
You need to create a Linux VM instance running Ubuntu 22.04 LTS in the us-central1-a zone with 4 vCPUs and 16 GB RAM. The instance should allow HTTP traffic. Which gcloud command should you use?

**A)** 
```bash
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=n2-standard-4 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server
```

**B)** 
```bash
gcloud compute instances create my-vm \
  --region=us-central1 \
  --machine-type=n2-standard-4 \
  --boot-disk-image=ubuntu-2204-lts
```

**C)** 
```bash
gcloud instances create my-vm \
  --zone=us-central1-a \
  --cpu=4 \
  --memory=16GB
```

**D)** 
```bash
gcloud compute create instance my-vm \
  --zone=us-central1-a \
  --type=standard-4
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Uses the correct command structure: `gcloud compute instances create`
  - Specifies zone (instances are zonal resources)
  - `n2-standard-4` provides exactly 4 vCPUs and 16 GB RAM
  - Correctly specifies image family and project
  - Uses `--tags=http-server` to identify the instance for firewall rules
  
- Option B is incorrect because:
  - Instances are zonal resources, not regional (must use `--zone`, not `--region`)
  - `--boot-disk-image` is not the correct parameter

- Option C is incorrect because:
  - Wrong command: should be `gcloud compute instances create`, not `gcloud instances create`
  - Custom machine types use `--custom-cpu` and `--custom-memory`, not `--cpu` and `--memory`

- Option D is incorrect because:
  - Wrong command structure: should be `instances create`, not `create instance`
  - `--type` is not a valid parameter

---

## Question 2
Your company has a web application running on a Compute Engine instance. You need to ensure the application data persists even if the instance is deleted. Currently, all data is stored on the boot disk. What should you do?

**A)** Change the boot disk type from pd-balanced to pd-ssd for better durability

**B)** Attach a new persistent disk to the instance, move the application data to it, and configure the disk to not auto-delete with the instance

**C)** Enable local SSD for better performance and data persistence

**D)** Take regular snapshots of the boot disk every hour

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Additional persistent disks can be configured to survive instance deletion
  - By default, boot disks are deleted with the instance, but additional disks are not
  - The `--auto-delete` flag can be set to `no` when attaching to ensure data persistence
  - This is the standard approach for separating application data from the OS

Commands:
```bash
# Create disk
gcloud compute disks create data-disk \
  --size=100GB \
  --zone=us-central1-a

# Attach disk (with auto-delete disabled)
gcloud compute instances attach-disk INSTANCE_NAME \
  --disk=data-disk \
  --zone=us-central1-a
```

- Option A is incorrect because:
  - Changing disk type doesn't affect whether data persists after instance deletion
  - Boot disks are deleted by default when instance is deleted regardless of type

- Option C is incorrect because:
  - Local SSDs are ephemeral and data is LOST when the instance stops or is deleted
  - They are the opposite of persistent storage

- Option D is incorrect because:
  - While snapshots are good for backups, they don't automatically restore data
  - This adds operational overhead and doesn't directly solve the persistence requirement

---

## Question 3
You need to create a managed instance group that automatically scales between 2 and 10 instances based on CPU utilization (target 60%). The instances should be created from a template named "web-template". Which command should you use?

**A)** 
```bash
gcloud compute instance-groups managed create web-mig \
  --base-instance-name=web \
  --template=web-template \
  --size=2 \
  --zone=us-central1-a && \
gcloud compute instance-groups managed set-autoscaling web-mig \
  --max-num-replicas=10 \
  --min-num-replicas=2 \
  --target-cpu-utilization=0.6 \
  --zone=us-central1-a
```

**B)** 
```bash
gcloud compute instance-groups create web-mig \
  --template=web-template \
  --autoscale-min=2 \
  --autoscale-max=10 \
  --cpu-target=60
```

**C)** 
```bash
gcloud compute instance-groups managed create web-mig \
  --template=web-template \
  --autoscaling=true \
  --replicas=2-10 \
  --cpu=60%
```

**D)** 
```bash
gcloud compute instances create-autoscaling-group web-mig \
  --template=web-template \
  --min=2 \
  --max=10
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - First creates the managed instance group with initial size
  - Then configures autoscaling with a separate command
  - `--target-cpu-utilization=0.6` sets the 60% CPU target (as a decimal)
  - All parameters are correctly specified

- Option B is incorrect because:
  - `instance-groups create` creates unmanaged groups (not managed groups)
  - Unmanaged groups don't support autoscaling or templates
  - Parameter names are incorrect

- Option C is incorrect because:
  - `--autoscaling`, `--replicas`, and `--cpu` are not valid parameters
  - Autoscaling must be set with a separate command

- Option D is incorrect because:
  - `create-autoscaling-group` is not a valid gcloud command
  - Correct syntax is `instance-groups managed create`

---

## Question 4
You have a Compute Engine instance in the STOPPED state. You need to change its machine type from n2-standard-2 to n2-standard-4. What is the correct procedure?

**A)** Delete the instance and create a new one with the desired machine type

**B)** Use the command: `gcloud compute instances set-machine-type INSTANCE_NAME --machine-type=n2-standard-4 --zone=ZONE`

**C)** Take a snapshot, create a new instance from the snapshot with the new machine type

**D)** You cannot change the machine type of an existing instance

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Machine type can be changed when instance is in STOPPED state
  - The `set-machine-type` command is specifically designed for this purpose
  - Instance must be stopped first (cannot change while running)

Complete procedure:
```bash
# Stop the instance
gcloud compute instances stop my-instance --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type my-instance \
  --machine-type=n2-standard-4 \
  --zone=us-central1-a

# Start the instance
gcloud compute instances start my-instance --zone=us-central1-a
```

- Option A is incorrect because:
  - Deleting and recreating is unnecessary and results in data loss
  - The instance can be modified in place

- Option C is incorrect because:
  - This is overly complex and creates unnecessary copies
  - Direct modification is supported

- Option D is incorrect because:
  - Machine type CAN be changed for stopped instances
  - This is a common operation

---

## Question 5
Your application requires very high IOPS for temporary data processing. The data doesn't need to persist after the job completes. Which storage option should you use?

**A)** Standard Persistent Disk (pd-standard)

**B)** SSD Persistent Disk (pd-ssd)

**C)** Local SSD

**D)** Extreme Persistent Disk (pd-extreme)

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Local SSDs provide the highest IOPS and lowest latency
  - They are physically attached to the server hosting the VM
  - Data doesn't need to persist (ephemeral storage is acceptable)
  - Most cost-effective for temporary high-performance storage
  - Performance: Up to 680,000 read IOPS and 360,000 write IOPS per device

Creating instance with Local SSD:
```bash
gcloud compute instances create high-perf-vm \
  --local-ssd=interface=NVME \
  --zone=us-central1-a
```

- Option A is incorrect because:
  - Standard persistent disk uses HDD, which has much lower IOPS
  - Not suitable for high IOPS requirements

- Option B is incorrect because:
  - While SSD persistent disks offer good performance, they're slower than Local SSD
  - More expensive for temporary storage
  - Unnecessary persistence feature

- Option D is incorrect because:
  - While extreme persistent disk offers very high IOPS, it's more expensive than Local SSD
  - Provides unnecessary persistence
  - Local SSD is better for temporary, high-performance workloads

**Important Note:** Local SSD data is LOST when the instance stops, is deleted, or fails!

---

## Question 6
You need to allow SSH access to specific Compute Engine instances for members of your development team. The team members should authenticate using their corporate Google Workspace accounts. What should you do?

**A)** Create a shared SSH key file and distribute it to all team members

**B)** Enable OS Login on the instances and grant the `roles/compute.osLogin` role to the team's Google Group

**C)** Add each team member's public SSH key to the instance metadata

**D)** Create a service account and share its private key with the team

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - OS Login links SSH access to IAM permissions
  - Users authenticate with their Google Workspace accounts
  - No need to manage individual SSH keys
  - Provides centralized access control and audit logging
  - Follows security best practices

Implementation:
```bash
# Enable OS Login on instance
gcloud compute instances add-metadata INSTANCE_NAME \
  --metadata=enable-oslogin=TRUE \
  --zone=ZONE

# Grant SSH access to group
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=group:developers@example.com \
  --role=roles/compute.osLogin

# Optional: For sudo access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=group:developers@example.com \
  --role=roles/compute.osAdminLogin
```

- Option A is incorrect because:
  - Sharing SSH keys is a security risk
  - No way to revoke access for individual users
  - Violates principle of individual accountability
  - Keys can be compromised

- Option C is incorrect because:
  - Requires manual management of SSH keys
  - Difficult to scale as team grows
  - No centralized audit trail
  - Hard to revoke access quickly

- Option D is incorrect because:
  - Service accounts are for applications, not users
  - Sharing private keys violates security best practices
  - No individual user audit trail

---

## Question 7
You are running a batch processing job on preemptible VMs. The job takes 30 hours to complete, but preemptible VMs can run for a maximum of 24 hours. What should you do to ensure the job completes?

**A)** Use standard VMs instead of preemptible VMs

**B)** Design the application to checkpoint its progress and resume from the last checkpoint when preempted

**C)** Request an exception from Google to extend the 24-hour limit

**D)** Use Spot VMs instead, which don't have a 24-hour limit

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Preemptible VMs have a hard 24-hour limit
  - Application must be designed to handle preemption
  - Checkpointing allows job to resume from last saved state
  - This is the recommended pattern for long-running batch jobs
  - Cost savings of preemptible VMs (60-80% cheaper) justify the added complexity

Best Practice Implementation:
1. Save progress to persistent storage (Cloud Storage, Cloud SQL)
2. On startup, check for existing checkpoint
3. Resume from checkpoint if found, otherwise start fresh
4. Use shutdown scripts to save state when preempted:
```bash
gcloud compute instances create batch-vm \
  --preemptible \
  --metadata=shutdown-script='#!/bin/bash
    # Save current state
    python save_checkpoint.py'
```

- Option A is incorrect because:
  - While this works, it eliminates 60-80% cost savings
  - Defeats the purpose of using preemptible VMs
  - Not the recommended solution for batch workloads

- Option C is incorrect because:
  - The 24-hour limit is fixed and cannot be extended
  - No exception process exists

- Option D is incorrect because:
  - While Spot VMs don't have a 24-hour limit, they can still be preempted at any time
  - You still need checkpointing logic
  - Spot VMs have similar pricing to preemptible VMs

**Note:** The question is designed to test knowledge of preemptible VM limitations and proper handling of preemption.

---

## Question 8
You need to create a custom machine type with 6 vCPUs and 30 GB of RAM in the us-east1-b zone using the N2 machine series. Which command should you use?

**A)** 
```bash
gcloud compute instances create custom-vm \
  --machine-type=n2-custom-6-30720 \
  --zone=us-east1-b
```

**B)** 
```bash
gcloud compute instances create custom-vm \
  --custom-cpu=6 \
  --custom-memory=30GB \
  --zone=us-east1-b
```

**C)** 
```bash
gcloud compute instances create custom-vm \
  --machine-type=custom \
  --cpus=6 \
  --ram=30GB \
  --series=n2 \
  --zone=us-east1-b
```

**D)** 
```bash
gcloud compute instances create custom-vm \
  --custom-vm-type=n2 \
  --custom-cpu=6 \
  --custom-memory=30720 \
  --zone=us-east1-b
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Custom machine type naming convention: `{series}-custom-{vCPUs}-{memory-MB}`
  - N2 series specified
  - 6 vCPUs specified
  - 30 GB = 30,720 MB (memory must be in MB)
  - Correct syntax: `n2-custom-6-30720`

Alternative (also correct):
```bash
gcloud compute instances create custom-vm \
  --custom-cpu=6 \
  --custom-memory=30GB \
  --custom-vm-type=n2 \
  --zone=us-east1-b
```

- Option B is incorrect because:
  - Missing `--custom-vm-type=n2` to specify the machine series
  - Would default to N1 series

- Option C is incorrect because:
  - `--machine-type=custom`, `--cpus`, `--ram`, and `--series` are not valid parameters
  - Incorrect command structure

- Option D is incorrect because:
  - `--custom-memory` should be `30GB` or `30720` (not `30720` without unit when using this flag)
  - While `--custom-vm-type=n2` is correct, memory format is wrong

**Important:** Custom machine types are available for N1, N2, N2D, and E2 series only.

---

## Question 9
You need to regularly back up a persistent disk attached to a production instance. The backups should be retained for 30 days. What is the most efficient approach?

**A)** Create manual snapshots daily using `gcloud compute disks snapshot`

**B)** Create a snapshot schedule and attach it to the disk

**C)** Copy the disk data to Cloud Storage every day

**D)** Create a new persistent disk from the source disk daily

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Snapshot schedules automate the backup process
  - Can define retention policies (auto-delete after 30 days)
  - Snapshots are incremental (cost-effective)
  - No manual intervention required
  - Most efficient and recommended approach

Implementation:
```bash
# Create snapshot schedule
gcloud compute resource-policies create snapshot-schedule daily-backup \
  --region=us-central1 \
  --max-retention-days=30 \
  --on-source-disk-delete=keep-auto-snapshots \
  --daily-schedule \
  --start-time=02:00

# Attach schedule to disk
gcloud compute disks add-resource-policies my-disk \
  --resource-policies=daily-backup \
  --zone=us-central1-a
```

- Option A is incorrect because:
  - Requires manual intervention or scripting
  - No automatic retention management
  - Would need to manually delete old snapshots
  - More prone to errors

- Option C is incorrect because:
  - Copying entire disk to Cloud Storage is inefficient
  - Takes longer and uses more storage
  - Snapshots are specifically designed for this use case
  - More expensive

- Option D is incorrect because:
  - Creating full disk copies is extremely inefficient
  - No incremental backups
  - Much more expensive than snapshots
  - Higher storage costs

**Key Advantage:** Snapshots are incremental - only changed blocks are stored after the first snapshot.

---

## Question 10
Your instance needs to communicate with Cloud Storage, but you don't want it to have a public IP address. What should you do?

**A)** Enable Private Google Access on the subnet

**B)** Create a Cloud NAT gateway

**C)** Use a proxy server with a public IP

**D)** Assign a static external IP address to the instance

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Private Google Access allows instances without external IPs to access Google APIs and services
  - Cloud Storage is accessed via Google APIs
  - No public IP needed on the instance
  - Traffic stays within Google's network
  - This is the recommended and most secure approach

Implementation:
```bash
# Enable Private Google Access on subnet
gcloud compute networks subnets update SUBNET_NAME \
  --region=REGION \
  --enable-private-ip-google-access

# Create instance without external IP
gcloud compute instances create private-vm \
  --subnet=SUBNET_NAME \
  --no-address \
  --zone=ZONE
```

- Option B is incorrect because:
  - Cloud NAT is used for accessing the internet, not Google APIs
  - Unnecessary for accessing Cloud Storage
  - More complex and expensive
  - Would work but is not the optimal solution

- Option C is incorrect because:
  - Adds unnecessary complexity
  - Proxy server would need to be managed
  - Not the intended solution for this use case

- Option D is incorrect because:
  - This directly contradicts the requirement (no public IP)
  - Less secure
  - Incurs additional costs

**Important:** Private Google Access must be enabled at the subnet level and works only for Google APIs, not for general internet access.

---

## Question 11
You want to view the CPU and memory utilization metrics for a specific Compute Engine instance over the last 7 days. What is the simplest way to do this?

**A)** SSH into the instance and run `top` command

**B)** View the instance in Cloud Console and check the Monitoring tab

**C)** Install the Cloud Monitoring agent and create custom dashboards

**D)** Use `gcloud compute instances describe` command

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Cloud Console provides built-in monitoring graphs
  - Shows CPU, disk, and network metrics by default
  - No additional configuration needed
  - Can select different time ranges (including last 7 days)
  - Most straightforward approach

Access via Console:
1. Navigate to Compute Engine > VM instances
2. Click on the instance name
3. Go to the "Monitoring" tab
4. Select time range (7 days)

Alternative using gcloud (for metrics):
```bash
gcloud monitoring time-series list \
  --filter='resource.type="gce_instance" AND resource.labels.instance_id="INSTANCE_ID"' \
  --format="table(metric.type, points[].value)"
```

- Option A is incorrect because:
  - `top` only shows current metrics, not historical
  - Cannot show 7 days of history
  - Requires SSH access
  - Not persistent

- Option C is incorrect because:
  - Cloud Monitoring agent is useful but not required for basic metrics
  - CPU and network metrics are available by default
  - Memory metrics DO require the agent, but the question asks for the "simplest" way
  - Creating custom dashboards is more work than needed

- Option D is incorrect because:
  - `describe` shows instance configuration, not performance metrics
  - Doesn't provide CPU/memory utilization data

**Note:** For memory utilization, the Cloud Monitoring agent needs to be installed. However, CPU and network metrics are automatically collected.

---

## Question 12
You need to allow a Compute Engine instance to access BigQuery datasets. What is the recommended way to grant this access?

**A)** Create a service account, grant it BigQuery permissions, and attach it to the instance

**B)** Download a service account key and store it on the instance

**C)** Use your personal credentials and configure them on the instance

**D)** Grant BigQuery permissions to the default Compute Engine service account

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - Service accounts are the recommended identity for VMs
  - Follows principle of least privilege (create dedicated SA for specific purpose)
  - IAM permissions control access to BigQuery
  - No key management needed (uses instance metadata service)
  - Easy to audit and manage

Implementation:
```bash
# Create service account
gcloud iam service-accounts create bq-reader \
  --display-name="BigQuery Reader"

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:bq-reader@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/bigquery.dataViewer

# Create instance with service account
gcloud compute instances create my-vm \
  --service-account=bq-reader@PROJECT_ID.iam.gserviceaccount.com \
  --scopes=cloud-platform \
  --zone=ZONE
```

- Option B is incorrect because:
  - Downloading service account keys is a security risk
  - Keys can be compromised if stored on disk
  - Google recommends avoiding service account keys when possible
  - Key rotation and management overhead

- Option C is incorrect because:
  - Personal credentials should never be used for application/VM authentication
  - Violates security best practices
  - No way to revoke access without changing personal credentials
  - Creates audit trail issues

- Option D is incorrect because:
  - While this works, it's not following least privilege
  - Default service account may be used by multiple instances
  - Better to create dedicated service accounts for specific purposes
  - Harder to audit specific permissions

**Best Practice:** Always create dedicated service accounts with minimum required permissions for each workload.

---

## Question 13
Your instance is failing to start. When you check the serial port output, you see errors related to the startup script. How can you temporarily disable the startup script to troubleshoot?

**A)** Delete the startup script from the instance metadata

**B)** Add `--metadata=startup-script-disabled=true` to the instance

**C)** Stop the instance, remove the metadata key `startup-script`, then start it

**D)** Startup scripts cannot be disabled; you must delete and recreate the instance

**Correct Answer:** C

**Explanation:**
- Option C is correct because:
  - Startup scripts are stored in instance metadata
  - Removing the metadata key prevents script execution
  - Instance must be stopped to modify certain metadata
  - Can re-add the script after troubleshooting

Implementation:
```bash
# Stop the instance
gcloud compute instances stop my-instance --zone=ZONE

# Remove startup script
gcloud compute instances remove-metadata my-instance \
  --keys=startup-script \
  --zone=ZONE

# Start the instance (no startup script will run)
gcloud compute instances start my-instance --zone=ZONE

# After troubleshooting, re-add the script
gcloud compute instances add-metadata my-instance \
  --metadata-from-file=startup-script=script.sh \
  --zone=ZONE
```

- Option A is incorrect because:
  - While this is the right approach, the answer doesn't specify stopping the instance first
  - Some metadata can be modified while running, but startup script changes are safer when stopped

- Option B is incorrect because:
  - `startup-script-disabled` is not a recognized metadata key
  - This would not actually disable the script

- Option D is incorrect because:
  - Startup scripts CAN be disabled by removing the metadata
  - No need to recreate the instance

**Tip:** Use `gcloud compute instances get-serial-port-output` to view startup script errors:
```bash
gcloud compute instances get-serial-port-output my-instance --zone=ZONE
```

---

## Question 14
You need to ensure that all Compute Engine instances in your project use only specific machine types (n2-standard-2, n2-standard-4, n2-standard-8). How can you enforce this policy?

**A)** Create a custom IAM role that only allows creating these machine types

**B)** Use Organization Policy constraints to restrict allowed machine types

**C)** Create a Cloud Function that monitors and deletes non-compliant instances

**D)** Document the policy in a wiki and train all users

**Correct Answer:** B

**Explanation:**
- Option B is correct because:
  - Organization Policies provide centralized constraint enforcement
  - Can whitelist specific machine types
  - Prevents non-compliant instances from being created
  - Applies to all projects in the organization or folder
  - Cannot be bypassed by users

Implementation (using gcloud):
```yaml
# Create policy.yaml
name: projects/PROJECT_ID/policies/compute.vmExternalIpAccess
spec:
  rules:
    - allowAll: false
    - condition:
        expression: "resource.machineType.endsWith('/n2-standard-2') || resource.machineType.endsWith('/n2-standard-4') || resource.machineType.endsWith('/n2-standard-8')"
      allowAll: true
```

Or using the constraint for machine types:
```yaml
constraint: constraints/compute.restrictMachineTypes
listPolicy:
  allowedValues:
    - "n2-standard-2"
    - "n2-standard-4"
    - "n2-standard-8"
```

Apply:
```bash
gcloud resource-manager org-policies set-policy policy.yaml --project=PROJECT_ID
```

- Option A is incorrect because:
  - IAM roles control what actions can be performed, not what values parameters can have
  - No IAM permission exists to restrict machine types
  - IAM works at the API operation level, not parameter level

- Option C is incorrect because:
  - Reactive approach (deletes after creation)
  - Doesn't prevent creation of non-compliant instances
  - Can cause disruptions
  - More complex to implement and maintain

- Option D is incorrect because:
  - No technical enforcement
  - Relies on user compliance
  - Error-prone
  - Not scalable

**Organization Policy Constraints** are the proper way to enforce allowed/denied values for GCP resources.

---

## Question 15
You have a managed instance group with 10 instances. You need to perform a rolling update to change the instance template. The update should never have more than 3 instances unavailable at a time. Which command should you use?

**A)** 
```bash
gcloud compute instance-groups managed rolling-action start-update web-mig \
  --version=template=new-template \
  --max-unavailable=3 \
  --zone=ZONE
```

**B)** 
```bash
gcloud compute instance-groups managed update web-mig \
  --template=new-template \
  --max-down=3 \
  --zone=ZONE
```

**C)** 
```bash
gcloud compute instance-groups managed set-instance-template web-mig \
  --template=new-template \
  --rolling-update \
  --unavailable=3
```

**D)** 
```bash
gcloud compute instance-groups managed rolling-action replace web-mig \
  --template=new-template \
  --max-surge=0 \
  --max-unavailable=30% \
  --zone=ZONE
```

**Correct Answer:** A

**Explanation:**
- Option A is correct because:
  - `rolling-action start-update` is the correct command for rolling updates
  - `--version=template=new-template` specifies the new template
  - `--max-unavailable=3` ensures max 3 instances down at a time
  - Gradually replaces old instances with new ones

Complete example with additional options:
```bash
gcloud compute instance-groups managed rolling-action start-update web-mig \
  --version=template=new-template \
  --max-unavailable=3 \
  --max-surge=0 \
  --zone=us-central1-a
```

- Option B is incorrect because:
  - `instance-groups managed update` is not the correct command
  - `--max-down` is not a valid parameter

- Option C is incorrect because:
  - `set-instance-template` changes the template but doesn't trigger a rolling update
  - Existing instances keep running with old template
  - New instances will use new template
  - `--rolling-update` and `--unavailable` are not valid parameters

- Option D is incorrect because:
  - `rolling-action replace` is not a valid subcommand
  - However, the parameter structure is close to correct
  - `--max-unavailable=30%` would be 3 instances (30% of 10), so this could work if the command were correct

**Key Parameters:**
- `--max-unavailable`: Maximum instances down during update
- `--max-surge`: Maximum new instances created above target size
- Can use absolute numbers or percentages

