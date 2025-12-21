# Chapter 01: Case Studies Analysis

A significant portion (20-30%) of the PCA exam questions are linked to specific, publicly available case studies. Understanding these scenarios is key to passing.

> Case study questions assess your ability to apply your knowledge to a realistic business situation. You can view the case studies on a split screen during the exam.
>
> — [Google Cloud Certification](https://cloud.google.com/learn/certification/cloud-architect)

## 📚 Official Case Studies (2025)

### 1. EHR Healthcare

**Company Profile**: A leading provider of electronic health record (EHR) software for the medical industry.

#### Business Context
| Aspect | Details |
| :--- | :--- |
| **Business Goal** | Modernizing legacy healthcare systems to a SaaS model |
| **Current State** | On-premises data centers with legacy infrastructure |
| **Target State** | Cloud-native, HIPAA-compliant healthcare platform |

#### Key Challenges
- **Compliance**: HIPAA requirements for protected health information (PHI)
- **Scalability**: Need to handle variable workloads across different healthcare providers
- **Data Residency**: Healthcare data must remain in specific geographic regions
- **Integration**: Must integrate with existing hospital systems via HL7/FHIR standards

#### Keywords to Watch
`"On-premise to cloud"`, `"Strict compliance"`, `"Disaster recovery"`, `"PHI"`, `"HIPAA"`, `"Data residency"`

#### Typical Solutions Pattern
```
┌─────────────────────────────────────────────────────────────────┐
│                     EHR Healthcare Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│  [Cloud Armor] → [Global LB] → [Cloud Run/GKE]                 │
│                                        ↓                         │
│                              [Cloud SQL with CMEK]              │
│                                        ↓                         │
│  [VPC Service Controls] ← [Cloud DLP] ← [Cloud Healthcare API]  │
│                                        ↓                         │
│                         [Cloud KMS with HSM]                    │
└─────────────────────────────────────────────────────────────────┘
```

**Example gcloud Commands**:
```bash
# Create a VPC Service Controls perimeter for healthcare data
gcloud access-context-manager perimeters create healthcare-perimeter \
    --title="Healthcare Data Perimeter" \
    --resources=projects/12345 \
    --restricted-services=bigquery.googleapis.com,storage.googleapis.com \
    --access-levels=accessPolicies/123456789/accessLevels/trusted_access

# Enable Cloud Healthcare API
gcloud services enable healthcare.googleapis.com

# Create a HIPAA-aligned dataset
gcloud healthcare datasets create ehr-dataset \
    --location=us-central1
```

---

### 2. Cymbal Retail

**Company Profile**: A large retail company transitioning from traditional brick-and-mortar to an omni-channel experience.

#### Business Context
| Aspect | Details |
| :--- | :--- |
| **Business Goal** | Transitioning from monolith to microservices and improving global customer experience |
| **Current State** | Monolithic application with regional databases |
| **Target State** | Globally distributed microservices with real-time analytics |

#### Key Challenges
- **Global Scalability**: Support customers across multiple continents with low latency
- **Database Scaling**: Move from regional MySQL to globally distributed database
- **Real-time Analytics**: Provide real-time inventory and customer insights
- **AI/ML Integration**: Personalized recommendations and demand forecasting

#### Keywords to Watch
`"Microservices"`, `"Omni-channel"`, `"Cloud Spanner"`, `"Vertex AI"`, `"Global load balancing"`, `"Real-time"`

#### Typical Solutions Pattern
```
┌─────────────────────────────────────────────────────────────────┐
│                    Cymbal Retail Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│  [Global HTTP(S) LB + Cloud CDN]                               │
│              ↓                                                   │
│  [Cloud Run Services]  ←→  [Pub/Sub]  →  [Dataflow]           │
│              ↓                                   ↓               │
│  [Cloud Spanner (Multi-region)]      [BigQuery + Looker]       │
│              ↓                                   ↓               │
│  [Memorystore (Redis)]               [Vertex AI Predictions]   │
└─────────────────────────────────────────────────────────────────┘
```

**Example Terraform Configuration**:
```hcl
# Cloud Spanner instance for global retail data
resource "google_spanner_instance" "retail_db" {
  name         = "cymbal-retail-spanner"
  config       = "nam-eur-asia1"  # Multi-region config
  display_name = "Cymbal Retail Global Database"
  
  autoscaling_config {
    autoscaling_limits {
      min_processing_units = 1000
      max_processing_units = 10000
    }
    autoscaling_targets {
      high_priority_cpu_utilization_percent = 65
    }
  }
}

# Global Load Balancer for retail services
resource "google_compute_global_address" "retail_ip" {
  name = "cymbal-retail-ip"
}
```

---

### 3. Helicopter Racing League (HRL)

**Company Profile**: An emerging sports entertainment company hosting helicopter racing events with real-time streaming.

#### Business Context
| Aspect | Details |
| :--- | :--- |
| **Business Goal** | Modernizing data analytics pipeline and enhancing viewer experience |
| **Current State** | Legacy infrastructure unable to handle real-time data processing |
| **Target State** | Real-time telemetry processing with predictive analytics |

#### Key Challenges
- **Real-time Processing**: Ingest and process telemetry data from racing helicopters
- **Low Latency**: Deliver live statistics to viewers in real-time
- **Machine Learning**: Predict race outcomes and enhance viewer engagement
- **Edge Computing**: Process data closer to racing venues

#### Keywords to Watch
`"Real-time streaming"`, `"IoT"`, `"Pub/Sub"`, `"Dataflow"`, `"BigQuery ML"`, `"Edge computing"`, `"Low latency"`

#### Typical Solutions Pattern
```
┌─────────────────────────────────────────────────────────────────┐
│                       HRL Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│  [IoT Devices] → [Pub/Sub] → [Dataflow (Streaming)]            │
│                                        ↓                         │
│                              [BigQuery Streaming]               │
│                                        ↓                         │
│                     [BigQuery ML / Vertex AI Predictions]       │
│                                        ↓                         │
│                        [Looker Real-time Dashboards]            │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4. Mountkirk Games

**Company Profile**: A global online gaming company requiring massive scale infrastructure.

#### Business Context
| Aspect | Details |
| :--- | :--- |
| **Business Goal** | Support massive scale online gaming with unpredictable traffic spikes |
| **Current State** | Self-managed game servers with scaling challenges |
| **Target State** | Managed, auto-scaling gaming infrastructure |

#### Key Challenges
- **Unpredictable Scale**: Handle viral game launches and unexpected player surges
- **Low Latency**: Sub-100ms latency for real-time multiplayer gaming
- **Global Distribution**: Serve players across all continents
- **Stateful Workloads**: Manage game state across distributed servers

#### Keywords to Watch
`"Global Load Balancing"`, `"Cloud Pub/Sub"`, `"Cloud Spanner"`, `"GKE"`, `"Agones"`, `"Low latency"`, `"Auto-scaling"`

#### Typical Solutions Pattern
```
┌─────────────────────────────────────────────────────────────────┐
│                   Mountkirk Games Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│  [Global TCP/UDP LB] → [GKE + Agones (Game Servers)]           │
│              ↓                        ↓                         │
│  [Memorystore (Redis)]    [Cloud Spanner (Game State)]        │
│              ↓                        ↓                         │
│  [Pub/Sub (Events)]  →  [Dataflow]  →  [BigQuery Analytics]   │
└─────────────────────────────────────────────────────────────────┘
```

**Example: GKE with Agones for Game Servers**:
```yaml
# Agones Fleet configuration for game servers
apiVersion: agones.dev/v1
kind: Fleet
metadata:
  name: mountkirk-game-servers
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
  template:
    spec:
      ports:
      - name: default
        portPolicy: Dynamic
        containerPort: 7654
      template:
        spec:
          containers:
          - name: game-server
            image: gcr.io/mountkirk-games/game-server:v1.2
            resources:
              requests:
                memory: "128Mi"
                cpu: "500m"
```

---

## 🛠️ How to Analyze a Case Study

### Step 1: Identify Business vs. Technical Requirements

| Business Requirement | Potential Technical Solution |
| :--- | :--- |
| "Reduce operational overhead" | Move to Serverless (Cloud Run, Cloud Functions) |
| "Global availability" | Use Cloud Spanner, Global Load Balancers |
| "Real-time insights" | Pub/Sub + Dataflow + BigQuery Streaming |
| "Protect sensitive user data" | DLP API, VPC Service Controls, Cloud KMS |
| "Cost-effective scaling" | Autoscaling, Spot VMs, Committed Use Discounts |
| "Minimize downtime during migration" | Database Migration Service, Transfer Appliance |
| "Support multiple teams" | Shared VPC, Resource Hierarchy, IAM |

### Step 2: Map to Well-Architected Framework Pillars

| Pillar | Key Questions to Ask |
| :--- | :--- |
| **Operational Excellence** | How will they deploy, operate, and monitor? |
| **Security** | What data protection and compliance needs exist? |
| **Reliability** | What are the availability and DR requirements? |
| **Cost Optimization** | How can they maximize ROI? |
| **Performance** | What are the latency and throughput requirements? |

### Step 3: Consider Trade-offs

| Trade-off | Example |
| :--- | :--- |
| **Consistency vs. Availability** | Spanner (Strong consistency) vs. Firestore (Eventual consistency) |
| **Cost vs. Performance** | Standard vs. Spot VMs |
| **Flexibility vs. Simplicity** | GKE Standard vs. Cloud Run |
| **Control vs. Management** | Self-managed vs. Managed services |

## 💡 Pro Tips for Case Study Questions

1. **Ignore Distractors**: Case studies are long; focus on the *specific problem* described in the question stem.

2. **Read the Question First**: Before diving into the case study, understand what the question is asking.

3. **The "Best" Choice**: Sometimes two options seem correct. Choose the one that best fits:
   - The **business goal** (e.g., if "cost-effective" is mentioned, prefer cheaper options)
   - The **Well-Architected Framework** principles
   - **Managed services** over self-managed (Google's preference)

4. **Look for Keywords**: Specific terms often point to specific services:
   - "Globally distributed SQL" → Cloud Spanner
   - "Event-driven" → Pub/Sub + Cloud Functions
   - "Real-time analytics" → BigQuery Streaming + Dataflow
   - "Container orchestration" → GKE
   - "Serverless containers" → Cloud Run
   - "HIPAA/PCI-DSS" → VPC Service Controls + Cloud KMS

5. **Consider the Migration Path**: Questions often ask about migration strategies—consider DMS, Transfer Service, and phased approaches.

---

📚 **Documentation Links**:
- [Cloud Architecture Center](https://cloud.google.com/architecture)
- [Solution Designs](https://cloud.google.com/architecture#designs)
- [Migration Guides](https://cloud.google.com/architecture#migrations)

---
[Next Chapter: Solution Architecture Design](02_Designing_and_Planning_Solution_Architecture.md)
