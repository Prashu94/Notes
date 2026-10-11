# Compute Engine

ACE 2.1, 3.1, 4.1. PCA 1.3 and 2.3. This is the virtual-machine path: you own the guest OS, the image, patching (unless VM Manager does it), and the machine shape.

Choose Compute Engine when the workload needs a guest OS, a kernel module, a commercial installer that is not a container, a GPU attached to a VM, or a lift-and-shift of a server. If the team only has a container and no Kubernetes requirement, prefer Cloud Run. If they need the Kubernetes API, prefer GKE.

## Machine families

| Family | Shape | Stem language |
| --- | --- | --- |
| E2 | Cheap general purpose, shared or standard | Default cost-sensitive web and app |
| N2, N2D, N4 | Balanced general purpose | Production general compute |
| C2, C3, H3 | High CPU per memory | Game servers, HPC CPU, media |
| M1–M4, X4 | Very large memory | SAP HANA, in-memory databases |
| A2, A3, G2 | GPU | Training and inference when the app is a VM |
| T2A, T2D | Arm or AMD | Cost or Arm images |
| f1-micro, e2-micro | Shared core, tiny | Dev only. Not HA. |

Custom machine types: pick vCPU and memory when a predefined type wastes one dimension.

Spot versus standard: Spot is the volatility option (PCA 2.3). The VM can be preempted. Handle shutdown notices. Do not put the only database on Spot. Standard is the default for serving traffic.

Sole-tenant nodes: you own the physical server for licensing or compliance. Recognize the term. It is not the default isolation answer. Confidential VMs and Shielded VM are the security answers for a normal project.

## Disks

| Disk | Survives VM stop? | Survives VM delete? | Performance | Exam use |
| --- | --- | --- | --- | --- |
| Hyperdisk | Yes if you keep the disk | Yes until you delete the disk | Current high-performance block. Provision IOPS and throughput separately on Hyperdisk. | New performance-sensitive block |
| Persistent Disk balanced / SSD / standard | Yes | Yes | Network-attached, durable | Default |
| Regional Persistent Disk | Yes | Yes | Synchronous copy in two zones | HA for a VM pair that cannot use a regional managed database |
| Local SSD | No. Lost on stop or host maintenance that recreates the VM | No | Scratch, extremely fast | Caches, shuffle, temporary |
| RAM disk in the guest | No | No | Fastest, smallest | Not a Google Cloud product |

Hyperdisk is the current block product for new high-IOPS designs. Persistent Disk is still everywhere on the exams and in existing fleets. Local SSD is never a system of record.

Images are boot disks’ templates (public OS images or custom). Snapshots are incremental backups of Persistent Disks and are global resources you can restore in another region. Machine images capture multiple disks plus configuration for a full VM clone.

## Create, connect, inventory

```bash
# Boot from a public image, attach the workload service account, no wide scopes story:
gcloud compute instances create web-1 \
  --zone="$ZONE" \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-balanced \
  --service-account="$SA_EMAIL" \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --tags=web \
  --metadata=enable-oslogin=TRUE

# Availability policy: migrate on host maintenance is the default for PD.
# Terminate is required for some GPUs and for Local SSD in many cases.
gcloud compute instances create gpu-box \
  --zone="$ZONE" \
  --machine-type=g2-standard-4 \
  --maintenance-policy=TERMINATE \
  --accelerator=type=nvidia-l4,count=1 \
  --image-family=common-cu129-ubuntu-2204-nvidia \
  --image-project=deeplearning-platform-release

# Inventory (ACE 4.1)
gcloud compute instances list
gcloud compute instances describe web-1 --zone="$ZONE"
gcloud compute instances os-inventory describe web-1 --zone="$ZONE"

# SSH. OS Login uses IAM. IAP TCP forwarding avoids a public IP.
gcloud compute ssh web-1 --zone="$ZONE" --tunnel-through-iap

# Serial console is the break-glass when SSH is dead. Turn it on deliberately.
gcloud compute instances add-metadata web-1 --zone="$ZONE" \
  --metadata serial-port-enable=TRUE
```

Startup scripts and guest metadata configure first boot. For anything you will repeat, use an instance template, not a one-off startup script typed in the console.

## Instance templates and managed instance groups

ACE 3.1: an autoscaled MIG is created from a template.

```bash
gcloud compute instance-templates create web-tpl \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --tags=web \
  --service-account="$SA_EMAIL" \
  --scopes=cloud-platform \
  --metadata=enable-oslogin=TRUE

# Regional MIG: VMs in more than one zone. This is the HA pattern.
gcloud compute instance-groups managed create web-mig \
  --region="$REGION" \
  --template=web-tpl \
  --size=2 \
  --zones="${REGION}-a,${REGION}-b"

gcloud compute instance-groups managed set-autoscaling web-mig \
  --region="$REGION" \
  --min-num-replicas=2 \
  --max-num-replicas=10 \
  --target-cpu-utilization=0.6 \
  --cool-down-period=90

# Autohealing needs a health check
gcloud compute health-checks create http web-hc --port=80 --request-path=/healthz
gcloud compute instance-groups managed update web-mig \
  --region="$REGION" \
  --health-check=web-hc \
  --initial-delay=120

# Rolling replace
gcloud compute instance-groups managed rolling-action start-update web-mig \
  --region="$REGION" \
  --version=template=web-tpl
```

Unmanaged instance groups are a list of dissimilar VMs. They do not autoscale. The exam almost never wants them.

Stateful MIGs keep disks with a specific instance. Use them only when a replica owns data. Prefer a database.

## Images and snapshots

```bash
# Snapshot a disk. The disk can belong to a running VM.
gcloud compute disks snapshot web-1 --zone="$ZONE" --snapshot-names=web-1-snap

gcloud compute snapshots list
gcloud compute snapshots delete web-1-snap

# Schedule
gcloud compute resource-policies create snapshot-schedule nightly \
  --region="$REGION" \
  --max-retention-days=14 \
  --daily-schedule \
  --start-time=03:00
gcloud compute disks add-resource-policies web-1 \
  --zone="$ZONE" \
  --resource-policies=nightly

# Image from a disk or from a snapshot
gcloud compute images create web-image \
  --source-snapshot=web-1-snap \
  --source-snapshot-project="$PROJECT_ID"
gcloud compute images list --project="$PROJECT_ID"
gcloud compute images delete web-image
```

Snapshots are incremental and can be used in another region. Images are what instance templates boot. Do not confuse them.

## VM Manager (ACE 3.1)

VM Manager is OS inventory, patch, and configuration (OS Config). It needs the Ops Agent or OS Config agent, and the OS Config API.

```bash
gcloud services enable osconfig.googleapis.com
gcloud compute project-info add-metadata \
  --metadata enable-osconfig=TRUE,enable-guest-attributes=TRUE

gcloud compute os-config patch-jobs execute \
  --instance-filter-all \
  --rollout-mode=zone-by-zone \
  --display-name="monthly"
```

Patch jobs are the answer when the stem says “keep apt or Windows update consistent across the fleet” and the VMs must stay VMs. It is not the answer for containers. GKE node auto-upgrade and Cloud Run’s managed runtime replace this idea.

## Shielded VM, Confidential VM, sole tenant

- **Shielded VM**: secure boot, vTPM, integrity monitoring. Turn it on for production images that support it.
- **Confidential VM**: memory encryption with AMD SEV or Intel TDX so the host cannot read guest RAM. PCA security stems about data in use.
- **Sole tenant**: dedicated hardware, often for bring-your-own-license.

```bash
gcloud compute instances create shielded-1 \
  --zone="$ZONE" \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring
```

## Other compute products you must recognize

| Product | When it is the answer |
| --- | --- |
| Batch | Managed batch and HPC jobs (containers or scripts) with scheduling, Spot, and no cluster to run. Not Dataflow. Dataflow is for Beam pipelines. |
| Cloud GPUs | Accelerator attached to GCE, GKE, or Cloud Run. Not a separate “GPU service” you deploy by name. |
| AI Hypercomputer | The platform story for large training: VMs or GKE with GPUs or TPUs, high-bandwidth networking. PCA 1.3 and 2.4. |
| Cloud TPU | Tensor processing for training and some inference. Accessed as TPU VMs or via Agent Platform. |
| Capacity Planner / reservations | Hold stock for a launch. |
| Cluster Director / Cluster Toolkit | Slurm-style HPC clusters. Recognition. |
| VMware Engine | See the migration chapter. vSphere stays vSphere. |
| Bare Metal Solution / SAP on Google Cloud | Certified large HANA or Oracle shapes that are not a normal VM. |
| Workload Manager | Validation of SAP and similar workloads against best practices. |

```bash
# Batch job skeleton. The JSON spec is the real interface.
gcloud batch jobs submit render-1 \
  --location="$REGION" \
  --config=job.json
gcloud batch jobs describe render-1 --location="$REGION"
gcloud batch jobs delete render-1 --location="$REGION"
```

`job.json` specifies a task spec (container or script), how many tasks run in parallel, and machine type or Spot. Use Batch when the stem is “thousands of independent jobs, no Kubernetes team”. Use Dataflow when the stem is a data pipeline with windows and Beam.

## Exercises

1. Two zones, stateless web, health checks, scale on CPU. List the resources in order.
2. A video encode box needs fast scratch and can be deleted any time. Which disk, which provisioning model?
3. You must patch Debian fleets monthly and report OS inventory. Which product, which agent?
4. The only copy of an upload folder was on Local SSD and the VM stopped. What is the recovery?
5. A license requires a dedicated physical server. Which Compute Engine feature?

### Answers

1. Instance template, health check, regional managed instance group, autoscaler, firewall for the health checker and the load balancer. Then a load balancer if users are outside the VPC.
2. Local SSD, Spot. Durable outputs go to Cloud Storage before the VM exits.
3. VM Manager (OS Config) with the OS Config agent enabled. Ops Agent is for metrics and logs, and is often installed alongside.
4. There is no recovery. Local SSD is ephemeral. The design was wrong for a system of record.
5. Sole-tenant nodes.
