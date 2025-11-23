# GCP Associate Cloud Engineer Practice Test 02

## Exam Instructions

- **Total Questions**: 50
- **Time Limit**: 2 hours (120 minutes)
- **Passing Score**: 70% (35 correct answers)
- **Focus**: Compute Engine, Cloud Storage, and Networking

---

## Questions

### Question 1
You need to create a Compute Engine instance that automatically restarts if it crashes. Which setting should you configure?

**A)** Enable high availability mode
**B)** Set automatic restart to "On"
**C)** Use a managed instance group
**D)** Enable preemptible mode

**Answer**: B

---

### Question 2
Your application stores log files in Cloud Storage that must be deleted after 90 days. What should you configure?

**A)** Manual deletion script
**B)** Lifecycle management rule with Delete action after 90 days
**C)** Cloud Scheduler to delete old files
**D)** Retention policy for 90 days

**Answer**: B

---

### Question 3
You need to allow instances in a private subnet to download updates from the internet. What should you create?

**A)** External IP addresses for all instances
**B)** Cloud NAT gateway
**C)** VPN connection
**D)** Shared VPC

**Answer**: B

---

### Question 4
Your Cloud SQL instance needs to be accessible only from specific Compute Engine instances. What is the most secure approach?

**A)** Use public IP with authorized networks listing all instance IPs
**B)** Use private IP and ensure instances are in the same VPC
**C)** Create VPN tunnel
**D)** Use Cloud SQL Proxy on all instances

**Answer**: B

---

### Question 5
You need to create a snapshot of a persistent disk attached to a running instance. Is this possible?

**A)** No, instance must be stopped first
**B)** Yes, you can create snapshots of disks from running instances
**C)** Only for boot disks
**D)** Only for SSD disks

**Answer**: B

---

### Question 6
Your website requires 99.95% availability. Which Cloud Storage location type should you choose?

**A)** Single region
**B)** Dual-region
**C)** Multi-region
**D)** Zone

**Answer**: C

---

### Question 7
You need to copy a disk from us-central1-a to europe-west1-b. What is the correct procedure?

**A)** Create snapshot in us-central1-a, create disk from snapshot in europe-west1-b
**B)** Use gcloud compute disks copy
**C)** Attach disk to instance in target zone
**D)** Export disk to Cloud Storage, then import

**Answer**: A

---

### Question 8
Your application needs to process files immediately when they are uploaded to Cloud Storage. What trigger should you use?

**A)** Cloud Storage Change Notification via Pub/Sub
**B)** Cloud Scheduler polling
**C)** Manual processing
**D)** Cron job checking bucket

**Answer**: A

---

### Question 9
You need to block all egress traffic from a Compute Engine instance except to Google APIs. What firewall rules should you create?

**A)** Single deny all egress rule
**B)** Allow Google API ranges, then deny all with lower priority
**C)** Block specific IP ranges only
**D)** No egress rules needed

**Answer**: B

---

### Question 10
Your company requires all VM instances to use custom images with pre-installed security software. What should you do?

**A)** Create custom image with software installed, use for all instances
**B)** Use startup scripts
**C)** Install manually on each instance
**D)** Use metadata to configure

**Answer**: A

---

### Question 11
You need to increase the boot disk size of a running Compute Engine instance from 20GB to 50GB. What should you do?

**A)** Stop instance, modify disk size, restart instance
**B)** Create new disk and migrate data
**C)** You can increase disk size while instance is running
**D)** Delete instance and recreate with larger disk

**Answer**: C

---

### Question 12
Your Cloud Storage bucket contains sensitive data. You need to ensure objects are encrypted with your own encryption keys. What should you use?

**A)** Default encryption is sufficient
**B)** Customer-Managed Encryption Keys (CMEK)
**C)** Application-level encryption only
**D)** Bucket ACLs

**Answer**: B

---

### Question 13
You need to ensure traffic between two subnets in the same VPC is allowed. What firewall configuration is required?

**A)** Create allow rule for traffic between subnets
**B)** No configuration needed - implied allow rule exists
**C)** Enable VPC peering
**D)** Create ingress and egress rules

**Answer**: B

---

### Question 14
Your managed instance group needs to perform health checks on HTTP port 8080. What should you configure?

**A)** Firewall rule allowing 8080 from load balancer IP ranges
**B)** Security group allowing 8080
**C)** Network tag on instances
**D)** IAM policy for health checks

**Answer**: A

---

### Question 15
You need to reserve a static external IP address for a Compute Engine instance. Which command should you use?

**A)** gcloud compute addresses create my-ip --region=us-central1
**B)** gcloud compute ips reserve my-ip
**C)** gcloud networking reserve-ip my-ip
**D)** gcloud compute instances reserve-ip

**Answer**: A

---

### Question 16
Your application stores objects in Cloud Storage Standard class. Objects older than 30 days are rarely accessed. How can you optimize costs?

**A)** Delete old objects
**B)** Create lifecycle rule transitioning to Nearline after 30 days
**C)** Manually move objects monthly
**D)** Use Archive storage class initially

**Answer**: B

---

### Question 17
You need to create a regional managed instance group that spans 3 zones. How many instances will be created if you set size=6?

**A)** 6 instances per zone (18 total)
**B)** 6 instances total distributed across 3 zones
**C)** 2 instances per zone (6 total)
**D)** Configuration not possible

**Answer**: B

---

### Question 18
Your Compute Engine instance needs to access Cloud Storage buckets without using an external IP. What should you enable?

**A)** Cloud NAT
**B)** Private Google Access on the subnet
**C)** VPN tunnel
**D)** Proxy server

**Answer**: B

---

### Question 19
You need to share files temporarily with external users who don't have Google accounts. What should you use?

**A)** Make Cloud Storage bucket public
**B)** Signed URLs with expiration time
**C)** Grant allUsers:objectViewer IAM role
**D)** Create temporary Google accounts

**Answer**: B

---

### Question 20
Your instance needs more CPU and memory. It's currently using n1-standard-4. What is the fastest way to upgrade?

**A)** Create new instance with larger type, migrate data
**B)** Stop instance, change to n1-standard-8, start instance
**C)** Use live migration
**D)** Add additional instances

**Answer**: B

---

### Question 21
You need to create a VPC with private subnets only (no external IPs). How can instances access the internet for updates?

**A)** Assign temporary external IPs
**B)** Configure Cloud NAT gateway
**C)** Use VPN
**D)** Cannot access internet without external IPs

**Answer**: B

---

### Question 22
Your Cloud Storage bucket receives millions of objects daily. You need to minimize retrieval costs for data older than 90 days. What storage class should you use?

**A)** Nearline (accessed monthly)
**B)** Coldline (accessed quarterly)
**C)** Archive (accessed yearly)
**D)** Keep in Standard

**Answer**: B

---

### Question 23
You need to detect and remove unused persistent disks to reduce costs. What command should you use?

**A)** gcloud compute disks list --filter="users:null"
**B)** gcloud compute disks delete --unused
**C)** gcloud compute disks cleanup
**D)** gsutil cleanup disks

**Answer**: A

---

### Question 24
Your application requires a persistent disk with highest IOPS. Which disk type should you choose?

**A)** pd-standard (HDD)
**B)** pd-balanced (SSD)
**C)** pd-ssd
**D)** pd-extreme

**Answer**: D

---

### Question 25
You need to copy 500GB of data from on-premises to Cloud Storage. What method is most efficient for one-time transfer?

**A)** gsutil with parallel uploads
**B)** Cloud Console upload
**C)** Transfer Appliance
**D)** FTP transfer

**Answer**: A

---

### Question 26
Your VM needs to run a startup script that installs software on first boot. Where should you specify this?

**A)** Instance metadata with key "startup-script"
**B)** SSH and run manually
**C)** Instance template only
**D)** VPC configuration

**Answer**: A

---

### Question 27
You need to ensure a Cloud Storage bucket can only be accessed from within your VPC. What should you configure?

**A)** VPC Service Controls perimeter
**B)** Firewall rules
**C)** IAM conditions with IP restrictions
**D)** Private bucket setting

**Answer**: A

---

### Question 28
Your managed instance group is experiencing high CPU. Autoscaling is enabled with min=2, max=10, target CPU=60%. What will happen?

**A)** Nothing, autoscaling doesn't work on CPU
**B)** New instances will be added automatically up to max=10
**C)** Instances will be deleted
**D)** Alert will be sent but no auto-action

**Answer**: B

---

### Question 29
You need to create a new subnet in an existing custom VPC. Which command should you use?

**A)** gcloud compute networks create subnet
**B)** gcloud compute networks subnets create my-subnet --network=vpc --region=us-central1 --range=10.1.0.0/24
**C)** gcloud compute subnets add
**D)** gcloud vpc create-subnet

**Answer**: B

---

### Question 30
Your application uploads objects to Cloud Storage every minute. You need to minimize costs. Which storage class should you use initially?

**A)** Archive
**B)** Coldline
**C)** Nearline
**D)** Standard

**Answer**: D

---

### Question 31
You need to prevent accidental deletion of a critical Compute Engine persistent disk. What should you configure?

**A)** Snapshot the disk regularly
**B)** Set deletion protection flag on the disk
**C)** Create backup disk
**D)** IAM policy preventing deletion

**Answer**: B

---

### Question 32
Your Cloud Storage bucket needs to log all access for security auditing. What should you enable?

**A)** Cloud Audit Logs - Data Access logs
**B)** Cloud Monitoring metrics
**C)** Bucket lifecycle policy
**D)** Access Control Lists

**Answer**: A

---

### Question 33
You need to connect two VPCs in different projects for private communication. What should you configure?

**A)** Shared VPC
**B)** VPC Peering
**C)** Cloud VPN
**D)** External load balancer

**Answer**: B

---

### Question 34
Your instance group needs to serve HTTP traffic. Which type of load balancer should you create?

**A)** Network Load Balancer
**B)** Internal TCP/UDP Load Balancer
**C)** HTTP(S) Load Balancer
**D)** SSL Proxy Load Balancer

**Answer**: C

---

### Question 35
You need to make a Cloud Storage object publicly readable. Which command should you use?

**A)** gsutil acl ch -u AllUsers:R gs://bucket/object
**B)** gsutil iam ch allUsers:objectViewer gs://bucket
**C)** gsutil setacl public gs://bucket/object
**D)** Both A and B are correct depending on bucket access type

**Answer**: D

---

### Question 36
Your Compute Engine instance is experiencing network issues. Where can you view network-related logs?

**A)** Cloud Logging with resource.type="gce_instance"
**B)** VPC Flow Logs
**C)** Serial port output
**D)** All of the above

**Answer**: D

---

### Question 37
You need to ensure Cloud Storage objects are immutable for regulatory compliance. What should you use?

**A)** Versioning
**B)** Retention policy and lock
**C)** Lifecycle management
**D)** IAM deny policies

**Answer**: B

---

### Question 38
Your application needs a Compute Engine instance with 12 vCPUs and 64 GB RAM. No predefined type matches. What should you do?

**A)** Use closest predefined type
**B)** Create custom machine type
**C)** Use multiple smaller instances
**D)** Request quota increase

**Answer**: B

---

### Question 39
You need to view real-time CPU utilization of a Compute Engine instance. Where should you look?

**A)** Cloud Monitoring dashboard
**B)** SSH into instance and run top
**C)** gcloud compute instances describe
**D)** Serial port output

**Answer**: A

---

### Question 40
Your static website in Cloud Storage serves global users. How can you reduce latency?

**A)** Use multi-region bucket
**B)** Enable Cloud CDN
**C)** Create buckets in each region
**D)** Use faster storage class

**Answer**: B

---

### Question 41
You need to allow SSH access to instances with tag "ssh-enabled" from anywhere. What firewall rule should you create?

**A)** Allow TCP:22, source 0.0.0.0/0, target tag "ssh-enabled"
**B)** Allow SSH, source any, target all instances
**C)** Allow TCP:22 from VPC only
**D)** No rule needed, SSH is allowed by default

**Answer**: A

---

### Question 42
Your Cloud Storage bucket has versioning enabled. An important file was deleted. How can you recover it?

**A)** File is permanently deleted
**B)** List all versions with gsutil ls -a, restore the deleted version
**C)** Contact Google Support
**D)** Restore from backup only

**Answer**: B

---

### Question 43
You need to create 100 identical Compute Engine instances. What is the most efficient approach?

**A)** Create instances one by one using console
**B)** Create instance template, use managed instance group
**C)** Write script with 100 gcloud commands
**D)** Clone one instance 100 times

**Answer**: B

---

### Question 44
Your application requires a disk that survives instance deletion. What type should you use?

**A)** Boot disk with auto-delete enabled
**B)** Additional persistent disk with auto-delete disabled
**C)** Local SSD
**D)** Ephemeral disk

**Answer**: B

---

### Question 45
You need to monitor network egress from a specific subnet for security purposes. What should you enable?

**A)** Cloud Monitoring alerts
**B)** VPC Flow Logs
**C)** Firewall Rules Logging
**D)** Packet Mirroring

**Answer**: B

---

### Question 46
Your Cloud Storage bucket contains PII data. You need to automatically delete objects when they haven't been accessed for 180 days. What should you configure?

**A)** Lifecycle rule with Delete action based on age
**B)** Lifecycle rule with Delete action based on last access time (not available)
**C)** Manual review and deletion
**D)** Retention policy

**Answer**: A

---

### Question 47
You need to increase network throughput for a Compute Engine instance. What machine type should you consider?

**A)** Shared-core instance
**B)** Higher vCPU count (network scales with vCPUs)
**C)** Preemptible instance
**D)** Storage-optimized instance

**Answer**: B

---

### Question 48
Your application stores encryption keys in a Cloud Storage object. What is the security risk?

**A)** No risk if bucket is private
**B)** High risk - keys should never be stored in Cloud Storage
**C)** Acceptable if using CMEK
**D)** Secure if versioning is enabled

**Answer**: B

---

### Question 49
You need to copy objects from one Cloud Storage bucket to another in a different project. What permission do you need?

**A)** Storage Admin on source bucket only
**B)** Storage Object Viewer on source, Storage Object Creator on destination
**C)** Project Owner on both projects
**D)** Storage Admin on both buckets

**Answer**: B

---

### Question 50
Your Compute Engine instance needs 1TB of temporary scratch space that will be lost on stop. What should you use?

**A)** Persistent disk
**B)** Local SSD
**C)** Cloud Storage
**D)** Network-attached storage

**Answer**: B

---

## Answer Key

| Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer |
|----|--------|----|----|----|----|----|----|----|----|
| 1  | B | 11 | C | 21 | B | 31 | B | 41 | A |
| 2  | B | 12 | B | 22 | B | 32 | A | 42 | B |
| 3  | B | 13 | B | 23 | A | 33 | B | 43 | B |
| 4  | B | 14 | A | 24 | D | 34 | C | 44 | B |
| 5  | B | 15 | A | 25 | A | 35 | D | 45 | B |
| 6  | C | 16 | B | 26 | A | 36 | D | 46 | A |
| 7  | A | 17 | B | 27 | A | 37 | B | 47 | B |
| 8  | A | 18 | B | 28 | B | 38 | B | 48 | B |
| 9  | B | 19 | B | 29 | B | 39 | A | 49 | B |
| 10 | A | 20 | B | 30 | D | 40 | B | 50 | B |

**Score: ___/50**

---

## Topic Distribution

- **Compute Engine**: 18 questions
- **Cloud Storage**: 16 questions
- **VPC Networking**: 12 questions
- **IAM & Security**: 4 questions

**Test completed on**: __________
**Time taken**: __________ minutes
**Topics to review**: _________________________
