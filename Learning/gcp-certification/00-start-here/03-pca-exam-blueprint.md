# Professional Cloud Architect — exam blueprint

Source: *Professional Cloud Architect Certification exam guide*, English PDF, reviewed October 2026. Weights are Google’s approximations.

Role: design, develop, and manage solutions that are robust, secure, scalable, efficient, cost-effective, highly available, and flexible, and that serve a business objective. You are expected to know migration, deployment, orchestration, open source, and hybrid or multicloud design.

The Well-Architected Framework is required knowledge. Six pillars run through every section:

1. Operational excellence
2. Security
3. Reliability
4. Performance optimization
5. Cost optimization
6. Sustainability

| Section | Weight |
| --- | --- |
| 1. Designing and planning a cloud solution architecture | ~25% |
| 2. Managing and provisioning a cloud solution infrastructure | ~17.5% |
| 3. Designing for security and compliance | ~17.5% |
| 4. Analyzing and optimizing technical and business processes | ~15% |
| 5. Managing implementation | ~12.5% |
| 6. Ensuring solution and operations excellence | ~12.5% |

2 hours, 50–60 questions, 200 USD plus tax, English and Japanese, valid 2 years. No prerequisite. Recommended experience: 3+ years in industry including 1+ year designing and managing solutions on Google Cloud.

Each standard exam uses **2 of these 4 case studies**. Case-study questions are **20–30%** of the exam. The PDF stays on a split screen. Read the official PDFs on the exam guide page. Do not study retired companies (Mountkirk Games, TerramEarth, Helicopter Racing League, Dress4Win). They are not on the current guide.

Current case studies:

- Altostrat Media
- Cymbal Retail
- EHR Healthcare
- KnightMotives Automotive

Several of them use generative AI. Walkthroughs are in `04-pca/case-studies.md`.

## Section 1 — Design and plan (~25%)

### 1.1 Business requirements

- Business use cases and product strategy
- Functional and non-functional requirements
- Business continuity plan
- Cost optimization
- Supporting the application design
- Integration patterns with external systems
- Movement of data
- Design decision trade-offs
- Workload disposition: build, buy, modify, or deprecate
- Success measures: KPI, ROI, metrics
- Security and compliance
- Observability

### 1.2 Technical requirements

- Well-Architected Framework
- High availability and failover
- Flexibility of cloud resources
- Scalability for growth
- Performance and latency
- Gemini Cloud Assist
- Backup and recovery

### 1.3 Network, storage, and compute

- On-premises and multicloud integration
- AI and ML: Gemini LLMs, Agent Builder, Model Garden, Gemini models, AI Hypercomputer
- Cloud-native networking: VPC, peering, firewalls, load balancers, routing, container networking, Shared VPC, Private Service Connect
- Data processing choice
- Storage type: object, file, databases
- Map compute to GKE, Cloud Run, Cloud Run functions
- Compute resources: spot VMs, custom machine types, specialized workloads

### 1.4 Migration plan

- Integrate with existing systems
- Assess and migrate systems and data, including **Google Cloud Migration Center**
- Migration methodology, workload testing, network planning, dependency planning
- Software license implications and financial impact

### 1.5 Future improvements

- Cloud and technology improvements
- Evolution of business needs
- Cloud-first design

## Section 2 — Manage and provision (~17.5%)

### 2.1 Network topologies

- Hybrid networking to on-premises
- Multicloud, including Google Cloud to Google Cloud
- Intrusion protection, access control, firewalls
- VPC design and load balancing: cloud, internet, and cloud-adjacent services

### 2.2 Storage systems

- Data storage allocation
- Data processing and compute provisioning
- Security and access management
- Data transfer and latency
- Retention and lifecycle
- Data growth
- Data protection: backup and recovery

### 2.3 Compute systems

- Provisioning
- Spot versus standard
- Network for Compute Engine, GKE, serverless, and **Google Cloud VMware Engine**
- Orchestration, configuration, patch management
- Container orchestration
- Serverless computing

### 2.4 Gemini Enterprise Agent Platform — end-to-end ML

- Agent Platform Pipelines for the ML lifecycle
- Data integration for Agent Platform
- AI Hypercomputer: Cloud Run functions and Agent Platform for ML and AI; GPUs and TPUs for training and serving; consumption models; large-scale training

### 2.5 Prebuilt solutions and APIs

- Differentiate Google AI APIs: Search, Conversation, Vision, Image, Video, Audio
- Gemini Enterprise features: AI Agents and NotebookLM
- Models from Model Garden

## Section 3 — Security and compliance (~17.5%)

### 3.1 Security

- IAM
- Resource hierarchy
- Data security: keys, encryption, secrets
- Separation of duties
- Auditing, VPC Service Controls, context-aware access, organization policy, hierarchical firewall policy
- Customer-managed encryption keys with Cloud KMS
- Secure remote access: Identity-Aware Proxy, service account impersonation, Chrome Enterprise Premium, Workload Identity Federation
- Software supply chain
- Securing AI: Model Armor, Sensitive Data Protection, secure model deployment

### 3.2 Compliance

- Legislation: health-record privacy, children’s privacy, data privacy, ownership, data sovereignty
- Commercial: cardholder data, PII
- Industry certifications such as SOC 2
- Audits, including logs

## Section 4 — Technical and business processes (~15%)

### 4.1 Technical processes

- SDLC
- CI/CD
- Troubleshooting and root-cause analysis
- Testing and validation of software and infrastructure
- Service catalog and provisioning
- Disaster recovery

### 4.2 Business processes

- Stakeholder management
- Change management
- Team skills readiness
- Decision-making
- Customer success
- Cost and resource optimization, CapEx versus OpEx
- Business continuity

## Section 5 — Implementation (~12.5%)

### 5.1 Advise delivery teams

- Application and infrastructure deployment
- API management, including Apigee
- Test frameworks: load, unit, integration
- Data and system migration tooling
- Gemini Cloud Assist

### 5.2 Use Google Cloud programmatically

- Cloud Shell Editor, Cloud Code, Cloud Shell Terminal
- `gcloud`, `gsutil`, `bq`
- Emulators: Bigtable, Spanner, Pub/Sub, Firestore
- Infrastructure as code and Terraform
- Google API access patterns
- Google API client libraries

## Section 6 — Operations excellence (~12.5%)

- 6.1 Operational excellence pillar of the Well-Architected Framework
- 6.2 Observability: monitoring and logging, profiling and benchmarking, alerting
- 6.3 Deployment and release management
- 6.4 Support of deployed solutions
- 6.5 Quality control
- 6.6 Reliability in production: chaos engineering, penetration testing, load testing

## How PCA questions are written

The stem gives a constraint. The correct option is the smallest design that meets that constraint. Extra availability, extra regions, and extra products are wrong when the case study did not ask for them.

Read in this order:

1. Availability target (99.9% is regional HA, not automatic multi-region Spanner).
2. Data model (object, file, relational, document, wide-column, warehouse).
3. Consistency and where writes happen.
4. Compliance and data residency.
5. Team skills (Kubernetes or not, VMware or not, rewrite budget or not).
6. Cost and sustainability only after the requirement is met.

Match the answer to a pillar. If two options both “work”, the one that satisfies the stated pillar and the stated number wins.
