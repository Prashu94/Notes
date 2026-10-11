# Compute Engine deep dive

Read `01-compute-engine.md` first. This file is the mechanism that file shortened: lifecycle, disks, groups, access, and the flags exam questions hide in the stem.

## Instance lifecycle

| State | CPU billed? | Memory? | Persistent disk? | Ephemeral external IP? | Local SSD |
| --- | --- | --- | --- | --- | --- |
| Running | Yes | Yes | Yes | Held | Present |
| Suspending / Suspended | No | State written to disk | Yes | Released unless static | Lost |
| Stopping / Terminated (stopped) | No | No | Yes, you still pay for the disk | Released unless static | Lost |
| Deleted | No | No | Only if you kept the disk (`--keep-disk`) | Released | Gone |

`stop` is not `delete`. A stopped VM still costs disk. `suspend` preserves memory so resume is faster. `reset` is a hard reboot and keeps the same disks and, if it is static, the same IP.

Host maintenance:

- **Migrate** (default when the disk is Persistent Disk or Hyperdisk): Google live-migrates the VM. Brief pause. Local SSD and most GPUs cannot live-migrate. They need **Terminate**.
- On host error, the VM can auto-restart if automatic restart is on.

```bash
gcloud compute instances stop web-1 --zone="$ZONE"
gcloud compute instances start web-1 --zone="$ZONE"
gcloud compute instances suspend web-1 --zone="$ZONE"
gcloud compute instances resume web-1 --zone="$ZONE"
gcloud compute instances reset web-1 --zone="$ZONE"

gcloud compute instances create gpu-1 --zone="$ZONE" \
  --machine-type=g2-standard-4 \
  --maintenance-policy=TERMINATE \
  --restart-on-failure \
  --accelerator=type=nvidia-l4,count=1
```

A stem that says “keep the same data across stop” is a persistent disk. A stem that says “fastest scratch, loss on stop is fine” is Local SSD. A stem that says “GPU workload” must accept terminate-on-maintenance.

## Machine families

You do not memorize every SKU. You match the adjective.

| Family | Adjective in the stem | Notes |
| --- | --- | --- |
| E2 | Cheap, general, dev, web | Shared-core `e2-micro` and `e2-small` burstable. Not a production database. |
| N2, N2D, N4, C4, N4A | Balanced production | N2D is AMD. Default “normal VM” when no adjective is stronger. |
| C2, C3, H3 | High CPU, games, media encode, HPC CPU | More cores per memory. |
| M3, M4, X4 | SAP HANA, in-memory, very large RAM | Certified shapes matter more than the family name for SAP. |
| A2, A3, G2 | GPU training or inference on a VM | Needs a zone that has the GPU. Often TERMINATE maintenance. |
| T2A, T2D | Arm, or cheaper AMD | The image must match the architecture. |
| Tau (T2D) | Scale-out cost | Not for the single huge database. |

Custom machines exist inside a family. Memory per vCPU has a min and max. Extended memory goes past the max and costs more. Use custom when a predefined type wastes CPU or RAM. Use predefined when the waste is small. The exam will not ask you to compute the exact GB multiple. It will ask custom versus a bigger predefined type versus Spot.

```bash
gcloud compute instances create custom-1 --zone="$ZONE" \
  --custom-cpu=6 --custom-memory=22GB
gcloud compute instances create custom-ext --zone="$ZONE" \
  --custom-cpu=2 --custom-memory=32GB --custom-extensions
```

Shared-core (`e2-micro`) is the free-tier-shaped answer for a lab. It is the wrong answer for a latency SLO.

## Disks in detail

| Type | What you provision | Survives stop | Zone failure | Exam cue |
| --- | --- | --- | --- | --- |
| pd-standard | Size. Throughput grows with size. | Yes | No | Cheap boot, sequential |
| pd-balanced | Size. Default for most new disks. | Yes | No | Normal production |
| pd-ssd | Size. IOPS grows with size. | Yes | No | Database on a VM |
| pd-extreme | Size plus provisioned IOPS | Yes | No | You set IOPS separately |
| hyperdisk-balanced | Size, IOPS, and throughput separately | Yes | No | Current default for high control |
| hyperdisk-extreme | Very high IOPS | Yes | No | Highest IOPS |
| hyperdisk-throughput | Streaming, large sequential | Yes | No | Analytics scratch that must persist |
| hyperdisk-ml | Inference checkpoints, many readers | Yes | No | ML |
| Regional PD (balanced or SSD) | Size. Sync copy in two zones. | Yes | Yes, the other zone | VM HA when you cannot use Cloud SQL |
| Local SSD | Fixed 375 GB slices, SCSI or NVMe | No | No | Scratch only |

Regional persistent disk is not a backup. Both replicas are in one region. A region loss takes both. Snapshots are the cross-region copy.

You cannot shrink a disk in place. You can grow it. The guest filesystem still needs to be expanded after the disk grows.

```bash
gcloud compute disks create data \
  --zone="$ZONE" --size=200GB --type=pd-balanced

gcloud compute disks create data-ha \
  --region="$REGION" --size=200GB --type=pd-balanced \
  --replica-zones="${REGION}-a,${REGION}-b"

gcloud compute instances attach-disk web-1 --zone="$ZONE" --disk=data

gcloud compute disks resize data --zone="$ZONE" --size=400GB

# Local SSD count is on the instance, not a separate durable disk
gcloud compute instances create scratch \
  --zone="$ZONE" --machine-type=n2-standard-4 \
  --local-ssd=interface=NVME \
  --maintenance-policy=TERMINATE
```

Boot disk type is chosen at create time. Changing it later means snapshot, new disk, new instance.

## Snapshots, images, machine images

Three different objects. Questions mix them up on purpose.

| Object | Contains | Use |
| --- | --- | --- |
| Snapshot | Incremental blocks of one disk | Backup, copy a disk to another region |
| Custom image | A bootable disk template | Instance templates, many identical VMs |
| Machine image | Several disks plus instance config | Clone a whole VM, including extra disks |

Snapshots are global resources stored in a location you choose (regional or multi-regional). Incremental means you pay for changed blocks after the first. Application consistency needs a guest flush (`--guest-flush`) or a database-native dump. A crash-consistent snapshot of a busy database is not a substitute for Cloud SQL PITR.

Instant snapshots are local and fast, for a short rollback. They are not a regional disaster copy.

```bash
gcloud compute disks snapshot data --zone="$ZONE" \
  --snapshot-names=data-1 --storage-location="$REGION" --guest-flush

gcloud compute disks create data-copy --source-snapshot=data-1 --zone="${REGION}-b"

gcloud compute images create web-golden \
  --source-disk=web-1 --source-disk-zone="$ZONE" \
  --family=web --storage-location="$REGION"

gcloud compute machine-images create web-mi \
  --source-instance=web-1 --source-instance-zone="$ZONE"

gcloud compute resource-policies create snapshot-schedule nightly \
  --region="$REGION" --max-retention-days=14 \
  --on-source-disk-delete=keep-auto-snapshots \
  --daily-schedule --start-time=03:00

gcloud compute disks add-resource-policies data \
  --zone="$ZONE" --resource-policies=nightly
```

Image families (`--image-family=debian-12 --image-project=debian-cloud`) always pick the newest image in that family. Pin an image name only when you need a freeze.

## Identity, SSH, metadata

Three ways onto a Linux VM:

| Method | When it is the answer |
| --- | --- |
| OS Login | IAM decides who can SSH. `roles/compute.osLogin` or `roles/compute.osAdminLogin`. 2-step verification can be required. ACE names this. |
| IAP TCP forwarding | No public IP. Firewall allows `35.235.240.0/20` to port 22. Plus `roles/iap.tunnelResourceAccessor`. |
| Metadata SSH keys | Legacy. Project-wide or instance keys. Weaker. Not the least-privilege answer. |
| Serial console | Break-glass when the network is dead. Off until you enable it. |

```bash
gcloud compute instances add-metadata web-1 --zone="$ZONE" \
  --metadata enable-oslogin=TRUE

gcloud compute ssh web-1 --zone="$ZONE" --tunnel-through-iap
gcloud compute instances get-serial-port-output web-1 --zone="$ZONE"
```

The metadata server is how the guest gets a token for the attached service account, without a key file:

```text
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
Header: Metadata-Flavor: Google
```

Startup scripts run as root on boot. Shutdown scripts run on stop or delete, with a short time budget. Do not put secrets in metadata. Metadata is readable by anyone who can read the instance. Put secrets in Secret Manager and let the attached service account read them.

```bash
gcloud compute instances add-metadata web-1 --zone="$ZONE" \
  --metadata-from-file startup-script=startup.sh
```

Scopes are a second gate on the metadata token. `cloud-platform` plus a tight IAM role is the current pattern. A scope of `devstorage.read_only` blocks a write even if IAM allows it. If a stem says “IAM allows it but the VM gets 403”, check the scope.

## Managed instance groups in detail

A template is immutable. Changing a template does not change running VMs. You create a new template and start an update.

Update types:

- **Proactive**: replace VMs now, within max surge and max unavailable.
- **Opportunistic**: replace only when a VM is recreated for another reason.
- **Canary**: two template versions with a target size or percent.

```bash
gcloud compute instance-groups managed rolling-action start-update web-mig \
  --region="$REGION" \
  --version=template=web-tpl-v2,name=canary,target-size=1 \
  --version=template=web-tpl-v1 \
  --max-surge=1 --max-unavailable=0 \
  --type=proactive
```

`--max-unavailable=0` keeps capacity. Surge creates extra VMs first. That needs quota.

Autohealing: a health check plus an initial delay long enough for the app to boot. Too short, and the group kills VMs that are still starting. That looks like an outage loop.

Autoscaler signals:

| Signal | Stem |
| --- | --- |
| CPU utilization | General web |
| Load-balancing utilization | Scale on requests the LB sends, not on a noisy neighbor CPU |
| Cloud Monitoring metric | Queue depth, custom app metric |
| Schedule | Known peak, scale before it |

```bash
gcloud compute instance-groups managed set-autoscaling web-mig \
  --region="$REGION" \
  --min-num-replicas=2 --max-num-replicas=10 \
  --target-cpu-utilization=0.6 \
  --scale-in-control=max-scaled-in-replicas=1,time-window=600
```

Scale-in control stops the group deleting half the fleet in one minute. Use it when sessions or connection draining matter.

Stateful MIG: a disk or IP sticks to a particular instance name. Use it only when a replica owns data. A database on a stateful MIG is usually worse than Cloud SQL.

Instance schedules start and stop VMs on a clock (dev fleets at night). That is cost, not HA. A schedule does not replace an autoscaler for traffic.

```bash
gcloud compute resource-policies create instance-schedule nights-off \
  --region="$REGION" \
  --vm-start-schedule="0 8 * * 1-5" \
  --vm-stop-schedule="0 20 * * 1-5" \
  --timezone="America/Los_Angeles"
gcloud compute instances add-resource-policies web-1 \
  --zone="$ZONE" --resource-policies=nights-off
```

## Reservations, CUDs, Spot

| Mechanism | What it guarantees | Discount? |
| --- | --- | --- |
| Spot | Nothing. Can be preempted. You get a short notice. | Deep discount |
| Reservation | Capacity in a zone for a machine shape | No, not by itself |
| Committed use discount | A spend or a resource commit for 1 or 3 years | Yes |
| Sustained use | Automatic as monthly usage grows, on families that still have it | Yes, you do not configure it |

A launch that must not fail for lack of stock needs a reservation. A steady production fleet needs a CUD. A restartable batch needs Spot. One answer does not do all three jobs.

```bash
gcloud compute reservations create launch-day \
  --zone="$ZONE" --vm-count=10 --machine-type=n2-standard-8

gcloud compute instances create batch \
  --zone="$ZONE" --machine-type=e2-standard-4 \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --max-run-duration=6h --instance-termination-action=DELETE
```

`--instance-termination-action` is either STOP or DELETE when Google preempts. STOP keeps the disk. The VM may still be deleted if you set a max run duration with DELETE. Read the flags you combine.

Placement policy `compact` puts VMs close for low latency (HPC). `spread` does the opposite. Compact is not HA. It is the opposite of HA.

## Multi-NIC and alias IP

A VM can have a `nic0` on one VPC and more NICs on other VPCs. Each NIC is in a subnet in the same zone’s region. Use this for appliances (firewall VM, load balancer VM) that must touch two networks. Routes and policy routing inside the guest are your problem. Most apps should have one NIC.

Alias IP ranges on a VM are extra internal addresses. GKE uses them for pods. You rarely assign them by hand.

## Exercises

1. A VM is stopped. Finance still sees disk charges. Why, and what deletes the charge?
2. You need a byte-for-byte copy of a 2 TB data disk in another region tonight, and you will create a VM from it tomorrow. Snapshot or machine image?
3. The MIG kills new VMs three minutes after boot. The app listens on port 80 after four minutes. What setting?
4. IAM allows `storage.objects.create` and the VM gets 403 from the metadata token. Name the second gate.
5. A GPU training VM was set to MIGRATE on host maintenance. What happens?

### Answers

1. Stop releases CPU, not the persistent disk. Delete the disk, or snapshot it and then delete it.
2. Snapshot, then create a disk from that snapshot in the other region. A machine image is for a whole VM configuration, and it is a heavier object than one data disk.
3. Increase the autohealing initial delay past four minutes, or fix the health check path so it is not failing during startup.
4. The instance access scope. `devstorage.read_only` blocks writes.
5. GPUs generally cannot live-migrate. The create or the maintenance event fails the migrate policy. Set TERMINATE and design the job to restart.
