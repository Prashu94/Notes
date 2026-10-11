# Containers: ECR, ECS, EKS, Fargate

SAA 2.1 and 3.2. SAP 4.3 and 4.4. SAP-C03 adds Service Connect, VPC Lattice, image security, and multi-tenant container designs. DVA-C02 lists ECR, ECS, and EKS. DVA-C03 makes building images and deploying to Fargate scored.

Official:

- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
- https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html

## The choice

| They say | You pick |
| --- | --- |
| "We have Docker, we do not want servers, we do not want Kubernetes" | ECS on Fargate |
| "We already run Kubernetes" or "we need the Kubernetes API" | EKS. Fargate profiles or managed node groups |
| "We must control the host, DaemonSets, and GPUs" | ECS on EC2 or EKS managed node groups. Fargate does not give you the host |
| "A web service from an image, almost no cluster talk" | App Runner |
| "Run this on premises with the same API" | ECS Anywhere or EKS Anywhere |
| "OpenShift" | ROSA. Recognize it. Do not pick it for a team that has no OpenShift requirement |

App Mesh is in maintenance. A new design uses ECS Service Connect or VPC Lattice. Do not answer App Mesh for a green-field mesh.

## ECR

Private registry, image scanning, lifecycle policies, replication, pull-through cache of public images.

```bash
aws ecr create-repository --repository-name orders --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=KMS
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin \
  "$ACCOUNT.dkr.ecr.us-east-1.amazonaws.com"
docker build -t orders:1 .
docker tag orders:1 "$ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/orders:1"
docker push "$ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/orders:1"
```

Basic scanning is Clair-style on push. Enhanced scanning uses Amazon Inspector and continuous CVE updates. The SAP-C03 and DVA-C03 image-security stem wants scanning on push, a pipeline that fails the build on critical CVEs, and an immutable tag. `latest` in production loses.

A repository policy lets another account pull. The task execution role needs `ecr:GetAuthorizationToken` and `ecr:BatchGetImage`. The task role is different: it is what the container's SDK uses to call S3 or DynamoDB. People swap them and the pull fails or the app fails.

## ECS

A cluster, a task definition, a service, and optionally a capacity provider.

| Field | Meaning |
| --- | --- |
| Task definition | Image, CPU, memory, ports, env, log driver, execution role, task role |
| Service | Desired count, deployment, load balancer, network, autoscaling |
| `awsvpc` | The task gets an ENI and a security group. Required for Fargate |
| Capacity provider | FARGATE, FARGATE_SPOT, or an EC2 ASG. A strategy mixes them |
| Deployment circuit breaker | Rolls the service back when new tasks will not stabilize |

```bash
aws ecs create-cluster --cluster-name orders --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
aws ecs register-task-definition --cli-input-json file://task.json
aws ecs create-service --cluster orders --service-name api \
  --task-definition orders --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIV_A,$PRIV_B],securityGroups=[$SG],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$TG,containerName=api,containerPort=8080"
```

`assignPublicIp=ENABLED` is for a public subnet with no NAT. Private subnets use DISABLED plus a NAT or endpoints. The exam likes private plus endpoints.

Service Connect gives ECS tasks a name in a namespace and a proxy for retries and traffic stats, without you running a mesh. Use it for service-to-service inside ECS. Use VPC Lattice when the clients include Lambda, EKS, and other accounts.

ECS Service Auto Scaling uses target tracking on CPU, memory, or ALB requests. Scale on the signal that actually saturates.

Logs: `awslogs` driver to CloudWatch Logs, or FireLens to Kinesis or OpenSearch. Container Insights adds CPU, memory, and network metrics. SAP-C03 calls container monitoring out. Turn Insights on. Add an alarm on running task count versus desired.

## EKS

The control plane is AWS-managed. You still own node groups, the VPC CNI, IAM, and add-ons.

| Feature | Why it is the answer |
| --- | --- |
| Managed node group | EC2 workers, AMI updates drained for you |
| Fargate profile | Pods that match a namespace run on Fargate. No nodes |
| IRSA | A service account assumes an IAM role via OIDC. No node role shared by every pod |
| Pod Identity | A newer way to map a service account to a role. Same least-privilege outcome |
| Private API endpoint | The Kubernetes API is not on the internet. Operators come from the VPC or a private CI |
| Security groups for pods | The pod has its own SG when the stem refuses "all pods share the node SG" |

A node role that can read every secret in the account is the anti-pattern IRSA replaces. DVA questions about "the pod's SDK credentials" want IRSA or Pod Identity, not keys in the image.

EKS Auto Mode and EKS managed capabilities keep moving. If the stem says "least operational overhead Kubernetes," prefer the managed node or Auto Mode option over a self-built cluster on raw EC2.

## Image and supply chain

| Control | Where |
| --- | --- |
| Scan on push | ECR |
| Fail the pipeline | CodeBuild sees Inspector findings and exits non-zero |
| Sign images | AWS Signer |
| Admit only signed images | An admission controller or a pipeline gate |
| Least privilege at runtime | Task role or IRSA, read-only root filesystem where the app allows it |
| Multi-tenant | One cluster is fine with namespaces, separate roles, and network policy. Separate clusters when the stem says a hard regulatory boundary |

## Exercises

1. A task pulls from ECR and then the app cannot read DynamoDB. The execution role has DynamoDB permissions and the task role has ECR permissions. What is swapped?
2. Fargate tasks in private subnets cannot pull the image. There is no NAT. Name two ways to fix the pull.
3. Two ECS services must call each other by name with retries. A third caller is a Lambda in another account. Service Connect, App Mesh, or VPC Lattice?
4. EKS pods on a node share one instance role and can read a finance bucket they should not see. Which feature gives the finance pod its own role?
5. Production deploys `orders:latest`. A bad push is immediately live. What tag practice and what ECS setting limit the blast?

## Answers

1. The execution role pulls the image and writes logs. The task role is the app's AWS credentials. Put ECR on the execution role and DynamoDB on the task role.
2. A NAT gateway so the task can reach the ECR public endpoint, or interface endpoints for ECR (`api` and `dkr`) plus S3 (the image layers live in S3) with private DNS. Endpoints are the answer when the stem forbids the internet.
3. VPC Lattice, because the caller is outside ECS and in another account. Service Connect is the right narrower answer when every caller is an ECS service in the mesh. App Mesh is the legacy option.
4. IRSA or EKS Pod Identity, with a role only the finance service account can assume.
5. Immutable tags (`orders:1.4.2` or the image digest) and a deployment circuit breaker so tasks that fail health checks roll the service back. A lifecycle policy can expire untagged images. It does not make `latest` safe.

## ECS, the objects

A task definition is the blueprint: image, CPU, memory, the execution role, the task role, logging, and the port. A task is a running copy. A service keeps a desired count of tasks and registers them with a load balancer. `awsvpc` network mode gives each task its own ENI and security group. That is Fargate's mode, and it is the mode you want on EC2 as well when you can.

The execution role is used by the ECS agent: pull from ECR, write logs, read secrets that are injected as environment variables. The task role is the application's credentials. Swapping them is exercise 1 and it is the most common container IAM item.

Fargate is capacity you do not patch. You set CPU and memory from the allowed pairs. It loses when you need a GPU, a custom kernel module, or a daemon on the host. EC2 launch type is for those, and you then patch the instances or use Bottlerocket and a capacity provider. Capacity providers plus a strategy are how a service mixes Fargate and Fargate Spot, or On-Demand and Spot instances. The base is the on-demand count. The weight is the Spot share.

Service autoscaling uses Application Auto Scaling on CPU, memory, or ALB request count, or a custom metric such as queue depth. The service's deployment configuration has a minimum healthy percent and a maximum percent. Minimum 100 and maximum 200 means you launch the new tasks before you stop the old ones. That requires spare capacity. A circuit breaker rolls the deployment back when new tasks fail to become healthy, instead of looping forever.

Load balancers: an ALB for HTTP, an NLB for TCP or for PrivateLink. Health checks must hit the application. A target group looking at TCP will keep a process that returns 500.

ECS Exec is the "shell into the task" path that replaces SSH on the host. It is IAM and audit, not a bastion. Service Connect gives ECS services names and retries inside the cluster. VPC Lattice is the answer when the caller is Lambda in another account or anything that is not another ECS service. App Mesh is in maintenance. Do not start a new mesh on it.

## EKS

Managed node groups or Fargate profiles. You still operate Kubernetes add-ons, upgrades, and network policy if you chose EC2 nodes. IRSA maps a Kubernetes service account to an IAM role through OIDC. EKS Pod Identity is the newer mapping. Either way, the node role is not the application role. A node role that can read the finance bucket is the bug in exercise 4: every pod on the node can use it.

Cluster Autoscaler or Karpenter adds nodes. Horizontal Pod Autoscaler adds pods. They solve different shortages. A pending pod because of CPU is a node problem. A service that is slow with spare node CPU is a replica problem.

## ECR

Images live in ECR. Scan on push. A critical finding fails the pipeline. Immutable tags or digests. Lifecycle policies expire untagged images so you do not pay for every build forever. Replication across Regions is how the standby Region can pull without depending on the primary Region during a failure. Interface endpoints for `ecr.api` and `ecr.dkr`, plus an S3 gateway endpoint, are how a private task pulls with no NAT. The layers are in S3. An ECR endpoint alone is not enough.

## More exercises

6. Minimum healthy percent is 100 and the deploy sits pending. The cluster has no spare CPU. What is the setting buying you, and what do you add?
7. Fargate Spot is the entire service. A Spot interruption stops every task. What should the base have been?
8. A Kubernetes team wants no nodes to patch and still wants the Kubernetes API. Which compute?
9. The image pull fails with `CannotPullContainer` and the task role has `ecr:GetAuthorizationToken`. Which role is wrong?
10. Two accounts must pull the same image during a Regional failover. Replication or a public repository?

## Answers

6. It refuses to stop old tasks until new ones are healthy, so you need room to run both. Add capacity, or temporarily lower the minimum if the stem accepts a dip. A circuit breaker does not create CPU.
7. A non-Spot base large enough to serve, with Spot as the weight above it. All-Spot is acceptable only when a full interruption is an acceptable outage.
8. EKS on Fargate. ECS on Fargate drops the Kubernetes API. Self-managed nodes are what they asked to stop patching.
9. The execution role. `GetAuthorizationToken` and the layer download belong there. The task role is not consulted for the pull.
10. ECR replication into the standby Region, and the standby execution role allowed to pull there. A public repository fails the security sentence. Pulling across Regions during the outage assumes the primary Region's ECR is up.
