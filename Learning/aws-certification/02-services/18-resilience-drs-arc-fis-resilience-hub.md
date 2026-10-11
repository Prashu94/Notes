# Resilience: DRS, ARC, FIS, Resilience Hub

SAP tasks 1.3 and 2.2. SAP-C03 makes these four named tools. SAA knows the DR patterns and Backup. FIS is listed out of scope on the SAA guide. It is in play for Professional improvement and for SAP-C03.

Official:

- https://docs.aws.amazon.com/drs/latest/userguide/what-is-drs.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/what-is-route53-recovery.html
- https://docs.aws.amazon.com/fis/latest/userguide/what-is.html
- https://docs.aws.amazon.com/resilience-hub/latest/userguide/what-is.html

Patterns and RTO math: `04-sap/06-disaster-recovery-design.md`.

## Which tool

| Sentence | Tool |
| --- | --- |
| Lift-and-shift servers, continuous block replication, fail over into AWS | Elastic Disaster Recovery |
| We need a drill that is not a real failover | DRS drill, or a Backup restore test |
| The health check stays green and the site is broken | ARC routing controls. You flip traffic. DNS health will not save you |
| Is the recovery Region actually ready, or only drawn on a slide | ARC readiness check, and Resilience Hub's assessment |
| Score this application against a 15-minute RTO and a 1-minute RPO | Resilience Hub. It recommends tests and alarms. It does not move traffic |
| Inject an AZ failure on purpose | Fault Injection Service. Stop instances, pause an API, fill a disk, throttle |
| The alarm should run a known fix | Systems Manager Automation |

DRS replaces the old CloudEndure Disaster Recovery name. MGN is the migration cousin. Use DRS when the ongoing job is DR. Use MGN when the job is a one-time move. The replication idea is similar. The product you name is the one the stem's verb matches.

## FIS safety

Run experiments in a non-production account or with targets you can afford. An experiment has a role, an action, a target, and a stop condition. The stop condition is a CloudWatch alarm. Without it you are just breaking production. SAP-C03 wants the experiment. It does not want an unbounded blast.

```bash
aws resiliencehub list-apps
aws fis list-experiment-templates
aws drs describe-source-servers
aws route53-recovery-control-config list-clusters
```

ARC has a control plane in five Regions so you can still flip a control when one Region is the thing that is sick. That is the point. A Route 53 record you host only in the failing Region is a weaker story.

## Exercise

Health checks pass. Users cannot pay. The runbook says "log into the healthy Region and edit a weighted record," and last time the record's TTL was a day. The company also cannot prove the standby will boot. Name three changes.

## Answer

ARC routing controls so a human or an alarm flips traffic without waiting for a health check that is lying. A low TTL only helps the DNS path you are leaving behind. An ARC readiness check or a DRS drill or a Resilience Hub test so the standby is known to boot. Resilience Hub to keep the RTO policy honest after the architecture changes.

## How the four tools differ

| Tool | It does | It does not |
| --- | --- | --- |
| Elastic Disaster Recovery | Continuous block replication of servers into a staging area. You drill or fail over by launching recovery instances | Replace a database's native replication. Use DMS or Aurora Global when the RPO is the transaction log. DRS is the server product |
| Application Recovery Controller | Routing controls that flip traffic even when health checks are green, plus readiness checks and safety rules | Host the application. It decides where traffic goes |
| Resilience Hub | Assesses an application against an RTO and RPO policy and recommends alarms, SOPs, and tests | Fail over. A recommendation you did not run is not a drill |
| Fault Injection Service | Runs an experiment: stop instances, pause an API, fill a disk, throttle. A stop condition is a CloudWatch alarm | Run in production with no stop condition. That is an outage you caused on purpose |

SAA cares about the four DR patterns and about Backup. FIS is listed out of scope on the SAA guide. SAP and SAP-C03 use all four tools by name. MGN is the migration cousin of DRS. Same replication idea, different verb. DRS is "be ready to fail over." MGN is "cut over and leave."

## DRS

Source servers run an agent. Replication is continuous into a staging subnet. A drill launches recovery instances without redirecting production. A failover redirects. You still need a way to point users: Route 53, a load balancer, or ARC. Replication lag is the RPO you actually have, not the RPO you wrote down. A source that cannot keep up is an RPO breach. Point-in-time recovery from the replicated history covers "we replicated the ransomware too." Practice that before you need it.

## ARC

A cluster is the control plane, spread so one Region cannot take the controls down with it. A control panel holds routing controls. A safety rule stops you from turning every Region off at once. Readiness checks look at capacity, quotas, and configuration in the standby and fail the review when the standby cannot actually take the load. That is the "we drew a second Region" detector.

Use ARC when the failure is gray: health checks pass, users cannot pay, DNS TTL is long, and a human editing a weighted record is the current runbook. The routing control is the switch. A low TTL is still worth setting on any DNS you keep. It is not a substitute for the control when the RTO is seconds.

## Resilience Hub and FIS

You describe the application and the policy (RTO, RPO). Hub tells you the application does not meet it and which alarms and tests would help. You schedule the tests. Hub does not move traffic.

FIS experiments belong in a non-production account or on targets you can lose. The role can perform the action and nothing else. The stop condition fires when an alarm breaches, and the experiment halts. Actions include stopping instances in one AZ, injecting API faults, and stressing CPU. The SAP-C03 sentence is "prove the recovery." The sentence they do not want is an unbounded blast.

A backup restore test, a DRS drill, a FIS AZ failure, and an ARC failover drill answer different questions. Restore tests answer "is the backup real." DRS drills answer "will the server boot." FIS answers "does the Multi-AZ design actually tolerate an AZ." ARC drills answer "can we shift traffic." One tool's green check does not answer the others.

## More exercises

2. The database is Aurora. The servers are a fleet of VMs. Which component uses DRS, and which does not?
3. Readiness checks fail because the standby Region's Lambda concurrency quota is 10 and production uses 500. What do you fix before the next drill?
4. An experiment stops instances in one AZ and has no alarm. Why is that incomplete even in a test account?
5. Hub says the RTO is not met. The team adds a second Region and does not re-run the assessment. Are they done?
6. SAA stem: "test that we can recover," and FIS is one of the options next to a backup restore test. The guide lists FIS out of scope. Which do you pick when both would "work"?

## Answers

2. DRS for the VMs. Aurora uses Aurora replicas or Global Database, not a block-level agent on the database host. Putting DRS on a database that already has a better replication tool gives you a crash-consistent disk and a worse RPO story.
3. The quota. Request the increase and scale a test that consumes it. A readiness check is doing its job. Ignoring it means the failover fails on a service limit.
4. Nothing stops it if it spreads further than you meant, and you learned nothing about the alarm you claim will save you. Add a stop condition on the symptom you care about, such as error rate or healthy-host count.
5. No. The assessment is stale. Re-run it. Then drill. A diagram of a second Region is what Hub was already complaining about.
6. The backup restore test, or a Multi-AZ failover test described without FIS. SAA wants the recovery evidence. It does not require the FIS product. On SAP, FIS is a normal answer when the stem is an injected AZ failure with a stop condition.
