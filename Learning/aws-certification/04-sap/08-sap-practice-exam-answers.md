# SAP practice exam answers

One point each. 20 of 25 is 80% on this drill.

| # | Answer | Why |
| --- | --- | --- |
| 1 | B | Transit Gateway is the transitive hub. Peering does not transit and becomes a mesh. Lattice is application networking, not the data-center hub. The internet is not a private WAN |
| 2 | A | Overlapping CIDRs cannot be peered. Private NAT lets you connect them while you plan a renumber. There is no transitive peering feature that fixes an overlap |
| 3 | B | An SCP is the ceiling an administrator cannot remove. A managed policy can be detached. An alarm does not prevent the API call. Encryption does not stop `StopLogging` |
| 4 | B | Aurora Global meets a seconds-level RPO and a 15-minute RTO if the app tier can be scaled quickly. Multi-AZ does not survive a Region. Nightly snapshots miss the RPO. DynamoDB drops SQL, which they did not have to drop |
| 5 | B | The numbers are backup-and-restore numbers. Active-active and a full Global Database fleet spend money the RTO does not require. Global Accelerator is not a database |
| 6 | A | External id is the confused-deputy control |
| 7 | A | CloudFront caches. Global Accelerator does not. The write API does not need to be on the CDN |
| 8 | B | The gateway endpoint removes the S3 NAT charge. The NAT per AZ keeps package downloads alive when an AZ dies. Deleting every NAT breaks the mirrors |
| 9 | B | Change the Beanstalk policy. EKS is a new platform they did not ask for. SSH and removing the load balancer make the outage worse |
| 10 | B | MGN moves servers. Snow moves the bulk. DataSync can take the last changes. DMS CDC keeps the database cutover short. A refactor first misses the date |
| 11 | B | Delegated admin and a central route to tickets. Per-account heroics do not scale |
| 12 | A | The recovery Region needs its own quotas and its own machine images. The database being healthy does not launch compute |
| 13 | A | Tags do nothing in billing until the allocation tag is activated. The CUR is the line-item record |
| 14 | B | Multi-AZ or Aurora for the AZ. Proxy for Lambda connection storms. DynamoDB contradicts SQL |
| 15 | A | Control Tower is the managed landing zone. A spreadsheet will drift. Lightsail is not an organization |
| 16 | B | Guardrail, scoped data, human approval, redacted logs. A shared admin and a public prompt log fail the security task |
| 17 | A | ML-DSA is the signature algorithm named with ML-KEM. SSE-S3 is not post-quantum signatures |
| 18 | B | Clean Rooms is the cross-organization analytics collaboration that does not hand over the raw data |
| 19 | B | Lattice reaches across accounts and includes Lambda. A new App Mesh is the legacy mesh. Opening the security group is not a service mesh |
| 20 | B | The key is hot. Extra table capacity does not fix one popular partition. DynamoDB is already Multi-AZ |
| 21 | B | A vault lock in another account survives the application admin. Same-account snapshots with a polite tag do not |
| 22 | A | Routing controls flip traffic when the health check is a liar. A higher TTL makes the incident longer |
| 23 | B | FSx for Windows is SMB and AD. EFS is NFS. Instance store is not a share. Neptune is a graph |
| 24 | B | Assume a role. Keys in git, in an AMI, or in a plaintext parameter are the failures |
| 25 | A | Compute Savings Plans cover EC2, Fargate, and Lambda and survive family changes. A Standard RI does not. Spot is wrong for the database. Dedicated Hosts are not how Lambda is discounted |
