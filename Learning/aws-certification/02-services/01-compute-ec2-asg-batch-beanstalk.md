# Compute: EC2, Auto Scaling, Batch, Beanstalk, App Runner

SAA 2.1, 3.2, 4.2. SAP 2.1, 2.5, 4.3. DVA uses EC2 and Beanstalk only when the app is hosted there. The developer exam does not ask you to design a placement group.

Official:

- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html
- https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-purchasing-options.html
- https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/Welcome.html
- https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html
- https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html

## Which compute

| Signal in the stem | Service |
| --- | --- |
| A guest OS, a commercial installer, a kernel module, a lift-and-shift server | EC2 |
| A container, no Kubernetes requirement, least ops | ECS on Fargate, or App Runner if the stem is a web service from source or an image |
| The team requires the Kubernetes API | EKS |
| A request under 15 minutes, scales to zero, no special OS | Lambda |
| A web app the team wants to push with `git` or a platform, and they will accept EB's opinion | Elastic Beanstalk |
| A queue of jobs, hours long, with dependencies, Spot-friendly | AWS Batch |
| Hadoop or Spark | EMR, not Batch |
| A simple VPS, tiny scope | Lightsail. Out of scope on SAA. In scope on SAP. Still loses an HA enterprise stem |
| Must run in the customer's building | Outposts |
| Must run at a 5G edge | Wavelength |
| HPC cluster with a scheduler | ParallelCluster. Recognize it. The usual exam answer is still a cluster placement group plus the instance family |

## Instance families

The generation number changes. The letter is the exam.

| Letter | Intent | Loses when |
| --- | --- | --- |
| T | Burstable. Credits. Cheap for idle dev | Steady high CPU. Credits exhaust and the instance crawls |
| M | General | A specialized bottleneck |
| C | Compute | The workload is memory bound |
| R, X, z | Memory | You are paying for RAM you do not use |
| I, D, H | Local NVMe or dense storage | The data must survive a stop. Instance store is ephemeral |
| G, P, Inf, Trn | GPU or accelerator | The stem is a CPU web app |
| Mac | macOS build fleets | Anything that is not macOS |
| `g` suffix, `a` suffix | Graviton (Arm) or AMD | The binary is x86-only and they cannot rebuild |
| `d` in the name | Local NVMe attached | You needed EBS durability |

Placement groups:

| Group | What it does |
| --- | --- |
| Cluster | Packs instances in one AZ for low latency. One rack failure takes the group |
| Spread | A handful of instances on distinct hardware. Critical singletons |
| Partition | Spreads partitions across racks. HDFS, Kafka, Cassandra |

Hibernation saves RAM to EBS and stops the instance. Supported types only. It is a cost tool for a workstation-like instance, not an HA tool.

## Purchasing

| Option | Commit | Interruption | Exam use |
| --- | --- | --- | --- |
| On-Demand | None | None from AWS for price | Unknown or short-lived |
| Compute Savings Plan | $/hour, 1 or 3 years | None | Steady EC2, Fargate, and Lambda together |
| EC2 Instance Savings Plan | Family and Region | None | Cheaper, less flexible |
| Standard RI | Instance attributes | None | Legacy, and still the name for RDS, ElastiCache, Redshift, OpenSearch, DynamoDB reserved capacity |
| Convertible RI | Can change family | None | When they say Reserved and also say they might change size |
| Spot | None | Yes, two-minute warning for many workloads | Fault-tolerant, checkpointed, queue workers |
| Dedicated Host | You pay for the host | None | Per-socket licenses, or a compliance rule that names a dedicated host |
| Dedicated Instance | Hardware not shared, host can change | None | Weaker than a host. Rarely the best answer |
| Capacity Reservation | AZ capacity held for you | None | On-Demand price plus the assurance the launch succeeds. Combine with a Savings Plan for the discount |

A mixed instances policy on an ASG: base On-Demand, the rest Spot, across sizes so a Spot pool drying up does not stall the scale-out. The only database is not Spot.

```bash
aws ec2 run-instances --image-id "$AMI" --instance-type m7i.large \
  --subnet-id "$SUBNET" --security-group-ids "$SG" \
  --iam-instance-profile Name=app-role \
  --metadata-options HttpTokens=required \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3,Encrypted=true}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=app}]'
aws ec2 create-launch-template --launch-template-name app --launch-template-data file://lt.json
```

## Auto Scaling

An ASG needs a launch template, subnets in more than one AZ, a minimum, a maximum, and a health check.

| Health check | Replaces the instance when |
| --- | --- |
| EC2 | The hypervisor says the instance is down. A dead process on a live OS stays in service |
| ELB | The load balancer health check fails. This is what you want for a web tier |

Scaling policies:

| Policy | Signal |
| --- | --- |
| Target tracking | Keep CPU, request count per target, or SQS backlog near a number. The default choice |
| Step | Different increments at different thresholds |
| Simple | One adjustment. Older |
| Scheduled | Known peaks. A Monday morning |
| Predictive | Machine learning on the group's history. Good when the pattern repeats and target tracking reacts too late |
| Warm pools | Pre-initialized instances so scale-out skips boot. You pay for the stopped pool |

Lifecycle hooks let you configure an instance before it takes traffic, or drain it before terminate. Systems Manager or a Lambda handles the hook.

```bash
aws autoscaling create-auto-scaling-group --auto-scaling-group-name app \
  --launch-template LaunchTemplateName=app,Version='$Latest' \
  --min-size 2 --max-size 10 --desired-capacity 2 \
  --vpc-zone-identifier "$PRIV_A,$PRIV_B" \
  --health-check-type ELB --health-check-grace-period 120 \
  --target-group-arns "$TG_ARN"
aws autoscaling put-scaling-policy --auto-scaling-group-name app \
  --policy-name cpu40 --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {"PredefinedMetricType": "ASGAverageCPUUtilization"},
    "TargetValue": 40.0
  }'
```

Termination policy and scale-in protection matter when the stem has a long job on one instance. Protect that instance, or move the job to Batch so the ASG is not your queue.

AWS Auto Scaling (the service, not EC2 Auto Scaling) builds plans across EC2, ECS, DynamoDB, and Aurora replicas. EC2 Auto Scaling is the group itself. The exam uses both names. Read which one the option describes.

## Load balancing, short version

The full table lives in `02-services/10-edge-route53-cloudfront-global-accelerator-waf-shield.md`. Compute questions still force the choice: ALB for HTTP, NLB for TCP and static IP and PrivateLink, Gateway Load Balancer for a firewall appliance.

Sticky sessions hide state on one instance. They are the compromise for an app you cannot change. They make scale-in drop users. Prefer DynamoDB or ElastiCache for the session.

## Elastic Beanstalk

Beanstalk owns the ASG, the load balancer, the platform updates, and the deployment policy. You bring the application.

| Deployment | Behavior |
| --- | --- |
| All at once | Downtime. Dev |
| Rolling | Batches. Mixed versions |
| Rolling with additional batch | Adds capacity first |
| Immutable | A second ASG. Cut over or fail. Safer |
| Traffic splitting | Canary via the load balancer |
| Blue/green | Two environments, then swap CNAMEs |

Worker environments pull from SQS. That is the Beanstalk answer for a background job when the team is already on Beanstalk. A new design uses Lambda or ECS.

`.ebextensions` and saved configurations are how you set packages, files, and option settings. The exam rarely asks for the file format. It asks when Beanstalk beats raw EC2: least operational overhead for a standard web app.

## App Runner

Source from a repo or an ECR image. App Runner builds, runs, scales, and puts HTTPS in front. No cluster to run. It loses when you need a VPC feature it does not expose, a Windows service, or a non-HTTP port. On SAA the safer "platform" answer is Beanstalk if App Runner is not in the options. On SAP, App Runner is in scope.

## Batch

A compute environment (EC2 or Fargate, On-Demand or Spot), a job queue, a job definition. Array jobs fan out. Dependencies order the steps. Use it when the work is a batch of minutes to hours and you do not want to write the scaler. Do not use it as the synchronous API tier.

## User data, AMIs, and patching

User data runs on first boot. It is not a configuration management system. Bake an AMI with EC2 Image Builder, launch from the AMI, and patch with Systems Manager Patch Manager on a maintenance window. Golden AMI plus an ASG instance refresh rolls the fleet.

Instance refresh and a new launch template version is the immutable path. SSH plus `yum update` on one box is the path the exam rejects.

## Exercises

1. A web tier is steady all day at 70% CPU and spikes for an hour. The base is On-Demand. The CFO wants the base cheaper without interruption risk, and the spike as cheap as possible. Which two purchasing options?
2. An ASG health check is EC2. Users see 502s from instances whose process has crashed. What do you change?
3. A Windows application cannot be load balanced. The vendor license is per socket. The RTO for an instance failure is 20 minutes. What do you run it on, and what is the HA story you will not promise?
4. Jobs arrive in bursts, take 45 minutes, can restart from a checkpoint, and must not require a cluster to administer. Lambda, EC2 ASG, or Batch?
5. Beanstalk rolling deploy left half the fleet on the old version and the new version fails its health check. Which Beanstalk policy would have kept the old fleet intact until the new one was healthy?

## Answers

1. A Compute Savings Plan or a Standard/Convertible RI for the base. Spot in a mixed ASG for the spike, with the application able to die.
2. ELB health checks on the ASG, and a target group health check that hits the process, not just TCP if HTTP can be checked.
3. A Dedicated Host sized for the license. You can still use Multi-AZ for the data and a second host for failover if the license allows two installs. You cannot promise horizontal scale-out of one licensed socket.
4. AWS Batch on Spot with retries. Lambda's 15-minute ceiling loses. An ASG you scale yourself is more operations than the stem wants.
5. Immutable, or blue/green with a swap after health. Rolling replaces the live fleet in place.

## Instance families and tenancy

| Family | You buy it for | The incident it causes |
| --- | --- | --- |
| M | Balanced web and app | None, until the metric says CPU or RAM is the actual limit |
| C | CPU | A memory-heavy JVM that then swaps |
| R | RAM, caches, in-memory databases | Paying for RAM the process does not use |
| T | Burstable dev and low-duty apps | Credit exhaustion. The box is "randomly slow" every afternoon. Move it to M or C |
| I, D | Local NVMe or dense disk | The data dies with the host if you treated instance store as the only copy |
| G, P, Inf, Trn | GPU and accelerators | A sandbox bill. An SCP belongs on the sandbox OU |
| Mac | macOS build fleets | Rare. Do not pick it for Linux |

The `g` suffix (`m7g`) is Graviton. It is a price-performance move when the software runs on ARM. A Standard Reserved Instance for `m5` does not discount `m7g`.

Tenancy is a separate axis. Shared hardware is the default. A dedicated instance means you do not share the host with another account, and it is rarely the answer. A Dedicated Host is a physical server you can see, for a per-socket or per-core license, or for a compliance rule that names a host. It is not the cheap option. It does not by itself give you horizontal scale.

Placement groups. Cluster packs instances in one AZ for the lowest latency between them. That contradicts a Multi-AZ web tier. Spread puts a handful of critical instances on distinct hardware. Partition spreads a large distributed system (Hadoop-style) across racks. The highly available web tier is an ASG across subnets, not a cluster placement group.

Hibernation writes RAM to EBS and stops the instance. The type must support it. It is a cost tool for a workstation-style box, not high availability. A stopped instance is down.

## Auto Scaling that actually matches the failure

A launch template is the source of truth: AMI, instance type, security groups, the instance profile, and IMDSv2 (`HttpTokens=required`). User data runs on first boot. It is a bad place for a secret and a bad place for the only copy of your configuration. Bake the AMI. Pass configuration through Systems Manager or a secret.

Minimum 2 and subnets in two AZs for a tier that claimed high availability. Health check type ELB, with a grace period long enough to boot, so a slow start is not terminated as unhealthy. An EC2 health check only notices the hypervisor. A dead process stays in the load balancer until the check hits the process.

Target tracking is the default policy: keep CPU or `ALBRequestCountPerTarget` near a number. Step scaling is for increments you want to control. Scheduled scaling is the Monday spike you can see on a calendar. A cooldown on a step policy stops you from launching a second wave before the first has registered. Target tracking has its own warmup and does not use that cooldown the same way.

Scale on the bottleneck. Queue workers scale on `ApproximateNumberOfMessagesVisible`. CPU of an idle poller stays low while the queue grows. Lifecycle hooks let you pause on launch or on terminate so a job can finish or a log can ship. Termination policies decide which instance dies. The default is oldest launch template, then closest to the next billing hour. AZ rebalance tries not to leave you in one AZ.

Mixed instances policies put On-Demand or a Savings Plan under the base and Spot on the burst. Capacity rebalance replaces a Spot instance when the interruption risk rises, before the two-minute notice. The application must still tolerate the notice. Spot as 100 percent of the only database is the outage.

Instance refresh starts a rolling replacement from a new template version. That is the immutable path. Minimum healthy percentage is how you avoid dropping below capacity during the refresh. SSH and a package update on one box is how the next scale-out launches the old bug.

## What runs the job

Beanstalk is a platform: you give it an application version and an environment, and it owns the ASG, the load balancer, and the platform updates. Immutable and blue/green keep the old fleet until the new one is healthy. Rolling and all-at-once touch the live fleet. Worker environments pull SQS. Use Beanstalk when the team wants a standard web app and the least cluster work. Leave it when you need a design the platform cannot express.

App Runner takes a source repo or an image and runs an HTTPS service. It loses when you need a Windows service, a non-HTTP port, or a VPC control it does not expose. On SAA, if App Runner is not in the options, Beanstalk or Fargate is the managed answer. On SAP, App Runner is in scope.

Batch is a compute environment, a job queue, and a job definition. Array jobs fan out. Job dependencies order steps. Spot in the compute environment is normal because a failed job retries. Use it for minutes-to-hours of work you do not want to scale yourself. Do not put a synchronous API on it. EMR remains the Spark and Hadoop answer. Batch is not a Spark cluster.

Lambda is the other compute in `02-lambda-and-serverless.md`. The cut is: under 15 minutes, no special OS, scale to zero. Anything that must stay warm, speak UDP, or hold a GPU is not Lambda.

## More exercises

6. A T3 fleet is slow every afternoon and idle every morning. Credits or a bigger T?
7. Cluster placement group or an ASG in two AZs for a low-latency trading mesh that also has a public website?
8. Spot interruption arrives. What does the instance get, and what must the job have already done?
9. User data installs the app and pulls a password from a public GitHub repo. Replace both habits.
10. An ASG minimum is 1, one subnet, EC2 health check. Name the three resilience defects.

## Answers

6. Credits. The baseline was exceeded and the balance hit zero. A bigger T postpones it. Move the afternoon load to M or C, or spread it.
7. The mesh can use a cluster placement group in one AZ and needs its own failure story. The website is an ASG in two AZs behind a load balancer. One placement group cannot be both.
8. A two-minute warning through the instance metadata and EventBridge. The job checkpoints and exits. If it cannot, it does not belong on Spot.
9. An AMI or a launch template that does not contain the secret, an instance role, and the password in Secrets Manager. User data that curls a public repo is both a supply-chain bug and a credential bug.
10. One instance is a single point of failure. One subnet is one AZ. An EC2 health check leaves a dead process in service. Minimum 2, two subnets, ELB health check.
