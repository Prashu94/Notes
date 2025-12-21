# Chapter 08: AI, Machine Learning, and Data Analytics

AI is no longer a niche topic. For the PCA exam, you must understand how to integrate AI/ML into enterprise architectures, especially with the 2025 focus on Generative AI.

> **Key Insight**: "The renewal exam focuses on generative AI solutions, with 90-100% of questions being case study-based around GenAI implementations."
>
> — [Google Cloud PCA Certification](https://cloud.google.com/learn/certification/cloud-architect)

## 🧠 Vertex AI: The Unified Platform

Vertex AI is Google Cloud's unified machine learning platform, bringing together all ML capabilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vertex AI Platform                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MODEL DEVELOPMENT                           │    │
│  │  • AutoML (no-code)    • Custom Training               │    │
│  │  • Notebooks           • Feature Store                  │    │
│  │  • Experiments         • TensorBoard                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              MODEL DEPLOYMENT                            │    │
│  │  • Endpoints (Online)  • Batch Predictions             │    │
│  │  • Model Registry      • Model Monitoring              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              GENERATIVE AI                               │    │
│  │  • Model Garden        • Gemini Models                  │    │
│  │  • Vertex AI Studio    • Agent Builder                  │    │
│  │  • Grounding           • RAG                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Vertex AI Components

| Component | Description | Use Case |
| :--- | :--- | :--- |
| **AutoML** | No-code ML model training | Quick prototypes, limited ML expertise |
| **Custom Training** | Full control with custom code | Complex models, specific requirements |
| **Vertex AI Workbench** | Managed Jupyter notebooks | Data exploration, model development |
| **Feature Store** | Centralized feature management | Feature reuse, consistency |
| **Model Registry** | Version and manage models | Model governance, deployment |
| **Endpoints** | Deploy models for predictions | Real-time inference |
| **Pipelines** | MLOps automation | Training workflows, CI/CD for ML |

### AutoML vs Custom Training

| Aspect | AutoML | Custom Training |
| :--- | :--- | :--- |
| **Ease of Use** | No code required | Requires ML expertise |
| **Customization** | Limited | Full control |
| **Data Requirements** | Structured data, images, text | Any data format |
| **Training Time** | Hours | Varies (hours to days) |
| **Cost** | Pay per training hour | Pay for compute resources |
| **Best For** | Quick PoC, simple problems | Complex, custom requirements |

**Example: Deploy AutoML Model**
```bash
# Create AutoML training job
gcloud ai custom-jobs create \
    --region=us-central1 \
    --display-name="tabular-classification-job" \
    --config=automl-config.yaml

# automl-config.yaml
# workerPoolSpecs:
#   machineSpec:
#     machineType: n1-standard-8
#   replicaCount: 1
#   containerSpec:
#     imageUri: gcr.io/cloud-aiplatform/training/automl-tabular:latest
#     args:
#       - --training_data=gs://my-bucket/data/train.csv
#       - --target_column=label

# Deploy model to endpoint
gcloud ai endpoints deploy-model ENDPOINT_ID \
    --region=us-central1 \
    --model=MODEL_ID \
    --display-name="production-model" \
    --machine-type=n1-standard-4 \
    --min-replica-count=1 \
    --max-replica-count=5
```

## 🚀 Generative AI & Gemini

### Model Garden

Access to foundation models including Google's Gemini and third-party models.

| Model | Type | Use Case |
| :--- | :--- | :--- |
| **Gemini 1.5 Pro** | Multimodal | Long context, reasoning, multimodal tasks |
| **Gemini 1.5 Flash** | Multimodal | Fast, cost-effective tasks |
| **PaLM 2** | Text | Text generation, chat, code |
| **Codey** | Code | Code generation, completion |
| **Imagen** | Image | Image generation |
| **Chirp** | Speech | Speech-to-text |

### Using Gemini API

**Example: Python SDK**
```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialize Vertex AI
vertexai.init(project="my-project", location="us-central1")

# Load Gemini model
model = GenerativeModel("gemini-1.5-pro")

# Text generation
response = model.generate_content("Explain quantum computing in simple terms")
print(response.text)

# Multimodal: Image + Text
image = Part.from_uri(
    uri="gs://my-bucket/image.jpg",
    mime_type="image/jpeg"
)
response = model.generate_content(
    [image, "Describe this image and identify any text in it"]
)
print(response.text)

# Chat conversation
chat = model.start_chat()
response = chat.send_message("Hello! Can you help me with Python?")
print(response.text)
response = chat.send_message("How do I read a CSV file?")
print(response.text)
```

### Grounding

Connect LLMs to your data to reduce hallucinations and provide accurate responses.

**Grounding Options**:
| Type | Description | Use Case |
| :--- | :--- | :--- |
| **Google Search** | Ground with web search | Public information queries |
| **Vertex AI Search** | Ground with enterprise data | Internal knowledge base |
| **Custom Retrieval** | RAG with your data | Specific domain knowledge |

**Example: Grounding with Vertex AI Search**
```python
from vertexai.generative_models import GenerativeModel, Tool
from vertexai.preview.generative_models import grounding

# Create a grounded model
model = GenerativeModel("gemini-1.5-pro")

# Ground with Vertex AI Search datastore
tool = Tool.from_retrieval(
    retrieval=grounding.Retrieval(
        source=grounding.VertexAISearch(datastore="projects/my-project/locations/global/collections/default_collection/dataStores/my-datastore")
    )
)

response = model.generate_content(
    "What are our company's policies on remote work?",
    tools=[tool]
)
print(response.text)
```

### RAG (Retrieval-Augmented Generation)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Architecture                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INDEXING PHASE                                               │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ [Documents] → [Chunking] → [Embedding] → [Vector DB]  │     │
│  │                              Model         (Vertex AI │     │
│  │                                            Vector     │     │
│  │                                            Search)    │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  2. RETRIEVAL PHASE                                              │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ [User Query] → [Embedding] → [Vector Search] → [Top K] │     │
│  │                 Model        Similarity         Results│     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
│  3. GENERATION PHASE                                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ [Query + Context] → [LLM (Gemini)] → [Grounded Answer] │     │
│  │                                                         │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Example: RAG with Vertex AI Vector Search**
```python
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

# Generate embeddings
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")

def get_embedding(text):
    embeddings = embedding_model.get_embeddings([text])
    return embeddings[0].values

# Index creation (one-time setup)
index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name="document-index",
    description="RAG document embeddings",
    dimensions=768,  # Depends on embedding model
    approximate_neighbors_count=150,
    leaf_node_embedding_count=500,
    leaf_nodes_to_search_percent=7,
)

# Create endpoint
index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name="document-search-endpoint",
    public_endpoint_enabled=True,
)

# Deploy index
index_endpoint.deploy_index(
    index=index,
    deployed_index_id="deployed-doc-index",
)

# Query (retrieval)
def retrieve_context(query, top_k=5):
    query_embedding = get_embedding(query)
    response = index_endpoint.find_neighbors(
        deployed_index_id="deployed-doc-index",
        queries=[query_embedding],
        num_neighbors=top_k,
    )
    return response
```

### Vertex AI Agent Builder

Build conversational AI agents with enterprise data.

**Components**:
- **Search Apps**: Enterprise search over your data
- **Chat Apps**: Conversational interfaces with grounding
- **Recommendations**: Personalized recommendations

```bash
# Create a search app with gcloud
gcloud discovery engines create my-search-app \
    --location=global \
    --display-name="Enterprise Knowledge Search" \
    --industry-vertical=GENERIC \
    --solution-type=SOLUTION_TYPE_SEARCH

# Create a data store
gcloud discovery data-stores create my-data-store \
    --location=global \
    --display-name="Company Documents" \
    --industry-vertical=GENERIC \
    --solution-type=SOLUTION_TYPE_SEARCH \
    --content-config=CONTENT_REQUIRED
```

## 📊 Data Analytics Pipeline

### Modern Data Stack on Google Cloud

```
┌─────────────────────────────────────────────────────────────────┐
│                  Data Analytics Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INGEST                                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Streaming:                    Batch:                    │    │
│  │ • Pub/Sub                     • Storage Transfer        │    │
│  │ • Datastream (CDC)            • BigQuery Transfer       │    │
│  │ • Kafka → Pub/Sub             • Dataproc                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  PROCESS                                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Streaming:                    Batch:                    │    │
│  │ • Dataflow (Apache Beam)      • Dataflow               │    │
│  │ • Pub/Sub → BigQuery         • Dataproc (Spark)        │    │
│  │                               • BigQuery SQL            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  STORE                                                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Data Warehouse:               Data Lake:                │    │
│  │ • BigQuery                    • Cloud Storage           │    │
│  │                               • BigLake                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ANALYZE & VISUALIZE                                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • Looker / Looker Studio      • Vertex AI              │    │
│  │ • BigQuery ML                 • Connected Sheets        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Dataflow (Apache Beam)

Unified batch and streaming data processing.

**Example: Streaming Pipeline**
```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Define pipeline options
options = PipelineOptions([
    '--project=my-project',
    '--region=us-central1',
    '--runner=DataflowRunner',
    '--temp_location=gs://my-bucket/temp',
    '--streaming'
])

# Define pipeline
with beam.Pipeline(options=options) as p:
    (p
     | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
         subscription='projects/my-project/subscriptions/my-sub')
     | 'Parse JSON' >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
     | 'Window' >> beam.WindowInto(beam.window.FixedWindows(60))
     | 'Aggregate' >> beam.CombinePerKey(sum)
     | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
         'my-project:dataset.table',
         schema='field1:STRING,field2:INTEGER',
         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
    )
```

### BigQuery ML

Train ML models directly in BigQuery using SQL.

**Supported Models**:
| Model Type | Use Case |
| :--- | :--- |
| LINEAR_REG | Regression/Forecasting |
| LOGISTIC_REG | Binary/Multi-class classification |
| KMEANS | Clustering |
| ARIMA_PLUS | Time series forecasting |
| BOOSTED_TREE_CLASSIFIER/REGRESSOR | Complex classification/regression |
| DNN_CLASSIFIER/REGRESSOR | Deep learning |
| IMPORTED TENSORFLOW | Custom TF models |

**Example: BigQuery ML**
```sql
-- Create a classification model
CREATE OR REPLACE MODEL `myproject.mydataset.customer_churn_model`
OPTIONS(
  model_type='LOGISTIC_REG',
  input_label_cols=['churned'],
  data_split_method='AUTO_SPLIT'
) AS
SELECT
  customer_id,
  tenure,
  monthly_charges,
  total_charges,
  contract_type,
  payment_method,
  churned
FROM `myproject.mydataset.customer_data`
WHERE churned IS NOT NULL;

-- Evaluate the model
SELECT *
FROM ML.EVALUATE(MODEL `myproject.mydataset.customer_churn_model`);

-- Make predictions
SELECT
  customer_id,
  predicted_churned,
  predicted_churned_probs
FROM ML.PREDICT(
  MODEL `myproject.mydataset.customer_churn_model`,
  (SELECT * FROM `myproject.mydataset.new_customers`)
);

-- Feature importance
SELECT *
FROM ML.FEATURE_IMPORTANCE(MODEL `myproject.mydataset.customer_churn_model`);
```

## 🏗️ AI Architectural Patterns

### Pattern 1: Real-time ML Inference

```
┌─────────────────────────────────────────────────────────────────┐
│                Real-time ML Inference Pattern                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Client] → [Cloud Run/GKE] → [Vertex AI Endpoint]             │
│                    │                    │                        │
│                    ↓                    ↓                        │
│            [Feature Store]     [Model Monitoring]               │
│            (Real-time features) (Drift detection)               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Pattern 2: Batch ML Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Batch ML Pipeline                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Cloud Scheduler] → [Vertex AI Pipeline]                       │
│                            │                                     │
│                            ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Extract    → 2. Transform → 3. Train → 4. Evaluate   │   │
│  │    (BigQuery)    (Dataflow)    (Custom)   (Metrics)     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                     │
│                            ↓                                     │
│  [Model Registry] → [Conditional Deploy] → [Endpoint]          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Pattern 3: GenAI Application

```
┌─────────────────────────────────────────────────────────────────┐
│                 GenAI Application Pattern                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [User Interface] → [Cloud Run (API)]                           │
│                           │                                      │
│                           ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  Orchestration Layer                       │  │
│  │  • Input validation    • Prompt engineering               │  │
│  │  • Context management  • Response formatting               │  │
│  └───────────────────────────────────────────────────────────┘  │
│           │                           │                          │
│           ↓                           ↓                          │
│  [Vector Search]              [Gemini API]                      │
│  (RAG Retrieval)              (Generation)                      │
│           │                           │                          │
│           └───────────────────────────┘                          │
│                           │                                      │
│                           ↓                                      │
│  [Cloud Logging] + [Cloud Monitoring] (Observability)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🎮 Compute for AI

### GPU vs TPU Selection

| Aspect | GPU (NVIDIA) | TPU (Google) |
| :--- | :--- | :--- |
| **Best For** | Broad ML workloads | TensorFlow/JAX, large models |
| **Programming** | CUDA, most frameworks | TensorFlow, JAX, PyTorch/XLA |
| **Model Types** | Any | Dense models, transformers |
| **Pricing** | Per-hour | Per-hour (often cheaper for large scale) |
| **Availability** | Spot/On-demand | On-demand, reserved |

### GPU Types

| GPU | Memory | Use Case |
| :--- | :--- | :--- |
| **T4** | 16 GB | Inference, small training |
| **L4** | 24 GB | Inference, efficient training |
| **A100** | 40/80 GB | Large model training |
| **H100** | 80 GB | Largest models, GenAI |

**Example: GKE with GPU**
```yaml
# GKE node pool with GPUs
apiVersion: container.google.com/v1
kind: NodePool
metadata:
  name: gpu-pool
spec:
  cluster: my-cluster
  config:
    machineType: a2-highgpu-1g
    accelerators:
      - acceleratorCount: 1
        acceleratorType: nvidia-tesla-a100
    diskSizeGb: 100
  management:
    autoRepair: true
    autoUpgrade: true
  autoscaling:
    enabled: true
    minNodeCount: 0
    maxNodeCount: 10
```

## 🔐 AI Governance

### Model Cards and Responsible AI

**Key Considerations**:
- **Fairness**: Test for bias across demographic groups
- **Explainability**: Use Vertex Explainable AI for model interpretability
- **Privacy**: Apply differential privacy, anonymization
- **Safety**: Content filtering, output validation

**Example: Explainable AI**
```python
from google.cloud import aiplatform

# Enable explanations on model deployment
model.deploy(
    endpoint=endpoint,
    deployed_model_display_name="explained-model",
    machine_type="n1-standard-4",
    explanation_metadata=aiplatform.explain.ExplanationMetadata(
        inputs={
            "feature1": aiplatform.explain.ExplanationMetadata.InputMetadata(
                input_tensor_name="feature1"
            ),
        },
        outputs={
            "prediction": aiplatform.explain.ExplanationMetadata.OutputMetadata(
                output_tensor_name="prediction"
            )
        }
    ),
    explanation_parameters=aiplatform.explain.ExplanationParameters(
        sampled_shapley_attribution=aiplatform.explain.SampledShapleyAttribution(
            path_count=10
        )
    )
)
```

---

📚 **Documentation Links**:
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview)
- [BigQuery ML Documentation](https://cloud.google.com/bigquery/docs/bqml-introduction)
- [Dataflow Documentation](https://cloud.google.com/dataflow/docs)
- [Responsible AI Practices](https://cloud.google.com/responsible-ai)
- [Model Garden](https://cloud.google.com/vertex-ai/docs/generative-ai/model-garden/explore-models)

---
*End of PCA Study Guide*

## 🎯 Final Exam Tips

1. **Master the Well-Architected Framework** - It's the foundation for every answer
2. **Know the Case Studies** - 20-30% of questions are case study-based
3. **Prefer Managed Services** - Google Cloud usually favors managed over self-managed
4. **Understand Trade-offs** - Many questions ask for the "best" solution among correct options
5. **Focus on GenAI for Renewal** - The renewal exam is heavily GenAI focused

**Good luck with your certification! 🚀**
