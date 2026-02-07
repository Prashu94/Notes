# Google Cloud Vertex AI - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Vertex AI Platform Components](#vertex-ai-platform-components)
3. [AutoML](#automl)
4. [Custom Training](#custom-training)
5. [Pre-trained APIs](#pre-trained-apis)
6. [Model Deployment & Serving](#model-deployment--serving)
7. [MLOps with Vertex AI](#mlops-with-vertex-ai)
8. [Vertex AI Pipelines](#vertex-ai-pipelines)
9. [Feature Store](#feature-store)
10. [Model Registry & Experimentation](#model-registry--experimentation)
11. [Generative AI on Vertex AI](#generative-ai-on-vertex-ai)
12. [Security & IAM](#security--iam)
13. [Cost Optimization](#cost-optimization)
14. [ACE Exam Focus](#ace-exam-focus)
15. [PCA Exam Focus](#pca-exam-focus)

---

## Overview

### What is Vertex AI?

Vertex AI is Google Cloud's unified machine learning platform that brings together all Google Cloud services for building ML under one unified API, client library, and user interface. It combines AutoML and custom training into a single platform.

**Key Value Propositions:**
- **Unified Platform**: Single interface for data scientists and ML engineers
- **End-to-End MLOps**: From data preparation to model monitoring
- **Pre-trained APIs**: Ready-to-use AI capabilities (Vision, Speech, NLP)
- **AutoML**: Train high-quality models with minimal ML expertise
- **Custom Training**: Full flexibility with TensorFlow, PyTorch, Scikit-learn, XGBoost
- **Generative AI**: Access to foundation models (PaLM, Gemini, Imagen)

### Vertex AI vs Legacy AI Platform

| Feature | AI Platform (Legacy) | Vertex AI |
|---------|---------------------|-----------|
| **Status** | Deprecated | Current |
| **AutoML** | Separate products | Integrated |
| **Pipelines** | Kubeflow on GKE | Managed service |
| **Feature Store** | Not available | Built-in |
| **Experiments** | Limited | Full tracking |
| **Model Registry** | Basic | Comprehensive |

---

## Vertex AI Platform Components

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           VERTEX AI PLATFORM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│  │   DATA PREP     │   │    TRAINING     │   │   DEPLOYMENT    │       │
│  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤       │
│  │ • Datasets      │   │ • AutoML        │   │ • Endpoints     │       │
│  │ • Feature Store │   │ • Custom        │   │ • Batch         │       │
│  │ • Labeling      │   │ • Hyperparameter│   │ • Online        │       │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘       │
│                                                                          │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│  │    MLOPS        │   │   MONITORING    │   │  GENERATIVE AI  │       │
│  ├─────────────────┤   ├─────────────────┤   ├─────────────────┤       │
│  │ • Pipelines     │   │ • Model Monitor │   │ • PaLM API      │       │
│  │ • Experiments   │   │ • Prediction    │   │ • Gemini        │       │
│  │ • Model Registry│   │ • Drift         │   │ • Imagen        │       │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Services

| Component | Purpose | ACE Relevance | PCA Relevance |
|-----------|---------|---------------|---------------|
| **AutoML** | No-code ML training | Basic awareness | When to use |
| **Custom Training** | Full control ML | Basic awareness | Architecture decisions |
| **Predictions** | Model serving | Deployment | Scaling, cost |
| **Pipelines** | MLOps workflows | Awareness | Full understanding |
| **Feature Store** | Feature management | Awareness | Design patterns |
| **Model Registry** | Version control | Awareness | Governance |
| **Experiments** | Track training runs | Awareness | MLOps patterns |

---

## AutoML

### What is AutoML?

AutoML (Automated Machine Learning) allows you to train high-quality custom models with minimal ML expertise. Google's AutoML handles:
- Feature engineering
- Architecture search (Neural Architecture Search)
- Hyperparameter tuning
- Model selection

### AutoML Model Types

#### 1. AutoML Image

**Classification:**
- Single-label: One class per image
- Multi-label: Multiple classes per image

**Object Detection:**
- Identify and locate objects with bounding boxes

**Image Segmentation:**
- Pixel-level classification

```bash
# Create image dataset
gcloud ai datasets create \
    --display-name="product-images" \
    --metadata-schema-uri="gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml" \
    --region=us-central1

# Import data from GCS
gcloud ai datasets import \
    --dataset=DATASET_ID \
    --import-schema-uri="gs://google-cloud-aiplatform/schema/dataset/ioformat/image_classification_single_label_io_format_1.0.0.yaml" \
    --data-uri="gs://my-bucket/images/data.csv" \
    --region=us-central1
```

#### 2. AutoML Tabular

**Classification:**
- Binary or multi-class prediction
- Example: Fraud detection, churn prediction

**Regression:**
- Predict numeric values
- Example: Price prediction, demand forecasting

**Forecasting:**
- Time-series predictions
- Example: Sales forecasting, resource planning

```bash
# Create tabular dataset
gcloud ai datasets create \
    --display-name="sales-data" \
    --metadata-schema-uri="gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml" \
    --region=us-central1

# Train AutoML model
gcloud ai models upload \
    --display-name="sales-prediction" \
    --artifact-uri="gs://my-bucket/model/" \
    --container-image-uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest" \
    --region=us-central1
```

#### 3. AutoML Text

**Classification:**
- Single-label or multi-label
- Example: Sentiment analysis, topic classification

**Entity Extraction:**
- Identify entities in text
- Example: Extract names, dates, locations

**Sentiment Analysis:**
- Determine sentiment polarity

#### 4. AutoML Video

**Classification:**
- Categorize video content

**Object Tracking:**
- Track objects across video frames

**Action Recognition:**
- Identify actions in video

### AutoML Training Configuration

```python
from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project="my-project", location="us-central1")

# Create and train AutoML model
dataset = aiplatform.TabularDataset.create(
    display_name="customer-churn",
    gcs_source="gs://my-bucket/data/churn.csv"
)

# Train classification model
job = aiplatform.AutoMLTabularTrainingJob(
    display_name="churn-prediction",
    optimization_prediction_type="classification",
    column_specs={
        "customer_id": "categorical",
        "monthly_charges": "numeric",
        "tenure_months": "numeric",
        "churn": "categorical"  # target
    }
)

model = job.run(
    dataset=dataset,
    target_column="churn",
    training_fraction_split=0.8,
    validation_fraction_split=0.1,
    test_fraction_split=0.1,
    budget_milli_node_hours=1000  # 1 node-hour
)
```

### When to Use AutoML

| Scenario | AutoML | Custom Training |
|----------|--------|-----------------|
| Limited ML expertise | ✅ | ❌ |
| Quick prototyping | ✅ | ❌ |
| Standard tasks (classification, detection) | ✅ | Either |
| Need state-of-art performance | ❌ | ✅ |
| Custom architectures | ❌ | ✅ |
| Full control over training | ❌ | ✅ |
| Complex preprocessing | ❌ | ✅ |

---

## Custom Training

### Overview

Custom training gives you full control over the training process using your own code with any ML framework.

### Supported Frameworks

- **TensorFlow** (1.x and 2.x)
- **PyTorch**
- **Scikit-learn**
- **XGBoost**
- **Custom containers** (any framework)

### Training Options

#### 1. Pre-built Containers

Google provides optimized containers for popular frameworks:

```bash
# TensorFlow 2.x
us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12:latest
us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-12:latest

# PyTorch
us-docker.pkg.dev/vertex-ai/training/pytorch-cpu.1-13:latest
us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13:latest

# Scikit-learn
us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest

# XGBoost
us-docker.pkg.dev/vertex-ai/training/xgboost-cpu.1-6:latest
```

#### 2. Custom Containers

Use your own Docker container for custom environments:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY trainer/ ./trainer/

ENTRYPOINT ["python", "-m", "trainer.task"]
```

```bash
# Build and push container
docker build -t gcr.io/my-project/custom-trainer:v1 .
docker push gcr.io/my-project/custom-trainer:v1
```

### Training Job Configuration

```python
from google.cloud import aiplatform

# Custom training job
job = aiplatform.CustomTrainingJob(
    display_name="custom-model-training",
    script_path="trainer/task.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12:latest",
    requirements=["pandas", "numpy"],
    model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest"
)

# Run training
model = job.run(
    replica_count=1,
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    args=["--epochs=10", "--batch-size=32"]
)
```

### Distributed Training

```python
# Distributed training configuration
from google.cloud import aiplatform

job = aiplatform.CustomJob(
    display_name="distributed-training",
    worker_pool_specs=[
        {
            "machine_spec": {
                "machine_type": "n1-standard-8",
                "accelerator_type": "NVIDIA_TESLA_V100",
                "accelerator_count": 2
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": "gcr.io/my-project/trainer:v1",
                "command": ["python", "train.py"],
                "args": ["--distributed=true"]
            }
        },
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
            },
            "replica_count": 4,
            "container_spec": {
                "image_uri": "gcr.io/my-project/trainer:v1",
                "command": ["python", "train.py"],
                "args": ["--worker=true"]
            }
        }
    ]
)
```

### Hyperparameter Tuning

```python
from google.cloud import aiplatform
from google.cloud.aiplatform import hyperparameter_tuning as hpt

# Define hyperparameter spec
parameter_spec = {
    "learning_rate": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
    "batch_size": hpt.DiscreteParameterSpec(values=[16, 32, 64, 128], scale="linear"),
    "num_layers": hpt.IntegerParameterSpec(min=1, max=5, scale="linear")
}

# Create hyperparameter tuning job
hp_job = aiplatform.HyperparameterTuningJob(
    display_name="hp-tuning-job",
    custom_job=custom_job,
    metric_spec={"accuracy": "maximize"},
    parameter_spec=parameter_spec,
    max_trial_count=20,
    parallel_trial_count=4
)

hp_job.run()
```

---

## Pre-trained APIs

### Overview

Pre-trained APIs provide ready-to-use AI capabilities without training. Ideal for common tasks.

### Vision API

**Capabilities:**
- Label Detection
- Face Detection
- OCR (Text Detection)
- Logo Detection
- Landmark Detection
- Safe Search Detection
- Object Localization

```python
from google.cloud import vision

client = vision.ImageAnnotatorClient()

# Analyze image from GCS
image = vision.Image()
image.source.image_uri = "gs://my-bucket/image.jpg"

# Label detection
response = client.label_detection(image=image)
for label in response.label_annotations:
    print(f"{label.description}: {label.score:.2f}")

# OCR
response = client.text_detection(image=image)
print(response.full_text_annotation.text)

# Safe search
response = client.safe_search_detection(image=image)
safe = response.safe_search_annotation
print(f"Adult: {safe.adult}, Violence: {safe.violence}")
```

```bash
# gcloud command
gcloud ml vision detect-labels gs://my-bucket/image.jpg
gcloud ml vision detect-text gs://my-bucket/document.png
```

### Natural Language API

**Capabilities:**
- Sentiment Analysis
- Entity Recognition
- Entity Sentiment
- Syntax Analysis
- Content Classification

```python
from google.cloud import language_v1

client = language_v1.LanguageServiceClient()

document = language_v1.Document(
    content="Google Cloud is amazing! I love using Vertex AI.",
    type_=language_v1.Document.Type.PLAIN_TEXT
)

# Sentiment analysis
sentiment = client.analyze_sentiment(document=document)
print(f"Score: {sentiment.document_sentiment.score}")
print(f"Magnitude: {sentiment.document_sentiment.magnitude}")

# Entity recognition
entities = client.analyze_entities(document=document)
for entity in entities.entities:
    print(f"{entity.name}: {entity.type_.name}")
```

### Speech-to-Text API

**Capabilities:**
- Real-time transcription
- Batch transcription
- Multi-language support
- Punctuation
- Speaker diarization

```python
from google.cloud import speech

client = speech.SpeechClient()

# Transcribe audio file
audio = speech.RecognitionAudio(uri="gs://my-bucket/audio.wav")
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code="en-US",
    enable_automatic_punctuation=True,
    enable_speaker_diarization=True,
    diarization_speaker_count=2
)

response = client.recognize(config=config, audio=audio)
for result in response.results:
    print(result.alternatives[0].transcript)
```

### Text-to-Speech API

```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()

input_text = texttospeech.SynthesisInput(text="Hello, welcome to Vertex AI!")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-F",
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=input_text, voice=voice, audio_config=audio_config
)

with open("output.mp3", "wb") as out:
    out.write(response.audio_content)
```

### Translation API

```python
from google.cloud import translate_v2 as translate

client = translate.Client()

# Detect language
result = client.detect_language("Bonjour le monde")
print(f"Detected: {result['language']} ({result['confidence']})")

# Translate text
translation = client.translate(
    "Hello, how are you?",
    target_language="es"
)
print(f"Translation: {translation['translatedText']}")
```

### Video Intelligence API

```python
from google.cloud import videointelligence

client = videointelligence.VideoIntelligenceServiceClient()

# Analyze video
features = [
    videointelligence.Feature.LABEL_DETECTION,
    videointelligence.Feature.SHOT_CHANGE_DETECTION,
    videointelligence.Feature.OBJECT_TRACKING
]

operation = client.annotate_video(
    request={
        "input_uri": "gs://my-bucket/video.mp4",
        "features": features
    }
)

result = operation.result(timeout=300)
for annotation in result.annotation_results[0].segment_label_annotations:
    print(f"Label: {annotation.entity.description}")
```

---

## Model Deployment & Serving

### Deployment Options

#### 1. Online Prediction (Endpoints)

Real-time predictions with low latency:

```python
from google.cloud import aiplatform

# Deploy model to endpoint
endpoint = model.deploy(
    deployed_model_display_name="my-model-v1",
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=10,
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    traffic_percentage=100
)

# Make prediction
instances = [{"feature1": 1.0, "feature2": "value"}]
predictions = endpoint.predict(instances=instances)
print(predictions)
```

```bash
# Deploy using gcloud
gcloud ai endpoints create \
    --display-name="production-endpoint" \
    --region=us-central1

gcloud ai endpoints deploy-model ENDPOINT_ID \
    --model=MODEL_ID \
    --display-name="deployed-model-v1" \
    --machine-type="n1-standard-4" \
    --min-replica-count=1 \
    --max-replica-count=5 \
    --traffic-split=0=100 \
    --region=us-central1
```

#### 2. Batch Prediction

Process large amounts of data offline:

```python
# Create batch prediction job
batch_prediction_job = model.batch_predict(
    job_display_name="batch-prediction-job",
    gcs_source="gs://my-bucket/input/data.jsonl",
    gcs_destination_prefix="gs://my-bucket/output/",
    machine_type="n1-standard-4",
    starting_replica_count=2,
    max_replica_count=10
)

# Wait for completion
batch_prediction_job.wait()
print(f"Output: {batch_prediction_job.output_info}")
```

### Traffic Splitting

Deploy multiple model versions with traffic splitting:

```python
# Deploy new version with traffic split
endpoint.deploy(
    model=new_model,
    deployed_model_display_name="my-model-v2",
    traffic_split={
        "0": 90,  # 90% to existing model
        "new-model-id": 10  # 10% to new model
    }
)
```

### Autoscaling Configuration

```python
# Deploy with autoscaling
endpoint = model.deploy(
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=10,
    autoscaling_target_cpu_utilization=60,  # Scale when CPU > 60%
    autoscaling_target_accelerator_duty_cycle=60  # For GPUs
)
```

---

## MLOps with Vertex AI

### MLOps Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MLOps LIFECYCLE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │  DATA    │───►│  TRAIN   │───►│  DEPLOY  │───►│ MONITOR  │        │
│   │ PREPARE  │    │  MODEL   │    │  MODEL   │    │  MODEL   │        │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘        │
│        │                                               │                │
│        └───────────────────────────────────────────────┘                │
│                          FEEDBACK LOOP                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Model Monitoring

```python
from google.cloud import aiplatform

# Create model monitoring job
model_monitoring_job = aiplatform.ModelDeploymentMonitoringJob.create(
    display_name="model-monitoring",
    endpoint=endpoint,
    logging_sampling_strategy={
        "random_sample_config": {"sample_rate": 0.8}
    },
    model_deployment_monitoring_objective_configs=[
        {
            "deployed_model_id": deployed_model_id,
            "objective_config": {
                "training_dataset": {
                    "gcs_source": {"uris": ["gs://bucket/training_data.csv"]},
                    "data_format": "csv",
                    "target_field": "target"
                },
                "training_prediction_skew_detection_config": {
                    "skew_thresholds": {"feature1": {"value": 0.1}}
                },
                "prediction_drift_detection_config": {
                    "drift_thresholds": {"feature1": {"value": 0.1}}
                }
            }
        }
    ],
    model_monitoring_alert_config={
        "email_alert_config": {
            "user_emails": ["ml-team@company.com"]
        }
    }
)
```

### Monitoring Types

| Type | Description | When to Alert |
|------|-------------|---------------|
| **Training-Serving Skew** | Difference between training data and serving data | Features drift significantly from training |
| **Prediction Drift** | Change in predictions over time | Model behavior changes |
| **Feature Attribution Drift** | Change in feature importance | Different features driving predictions |

---

## Vertex AI Pipelines

### Overview

Vertex AI Pipelines orchestrates ML workflows as directed acyclic graphs (DAGs). Based on Kubeflow Pipelines.

### Creating a Pipeline

```python
from kfp import dsl
from kfp.v2 import compiler
from google.cloud import aiplatform

# Define pipeline components
@dsl.component(base_image="python:3.9")
def preprocess_data(input_path: str, output_path: str):
    import pandas as pd
    df = pd.read_csv(input_path)
    # Preprocessing logic
    df.to_csv(output_path, index=False)

@dsl.component(base_image="gcr.io/my-project/trainer:v1")
def train_model(data_path: str, model_path: str):
    # Training logic
    pass

@dsl.component
def deploy_model(model_path: str, endpoint_name: str):
    # Deployment logic
    pass

# Define pipeline
@dsl.pipeline(name="ml-pipeline", description="End-to-end ML pipeline")
def ml_pipeline(input_data: str, output_bucket: str):
    preprocess_task = preprocess_data(
        input_path=input_data,
        output_path=f"{output_bucket}/preprocessed/data.csv"
    )
    
    train_task = train_model(
        data_path=preprocess_task.outputs["output_path"],
        model_path=f"{output_bucket}/model/"
    )
    
    deploy_task = deploy_model(
        model_path=train_task.outputs["model_path"],
        endpoint_name="production"
    )

# Compile pipeline
compiler.Compiler().compile(
    pipeline_func=ml_pipeline,
    package_path="pipeline.json"
)

# Run pipeline
aiplatform.init(project="my-project", location="us-central1")

job = aiplatform.PipelineJob(
    display_name="training-pipeline",
    template_path="pipeline.json",
    parameter_values={
        "input_data": "gs://my-bucket/raw/data.csv",
        "output_bucket": "gs://my-bucket"
    }
)
job.run()
```

### Pre-built Components

Google provides pre-built pipeline components:

```python
from google_cloud_pipeline_components import aiplatform as gcc_aip

# Use pre-built AutoML component
@dsl.pipeline(name="automl-pipeline")
def automl_pipeline():
    dataset_create = gcc_aip.TabularDatasetCreateOp(
        project="my-project",
        display_name="my-dataset",
        gcs_source="gs://my-bucket/data.csv"
    )
    
    training_job = gcc_aip.AutoMLTabularTrainingJobRunOp(
        project="my-project",
        display_name="automl-training",
        dataset=dataset_create.outputs["dataset"],
        target_column="target",
        optimization_prediction_type="classification"
    )
    
    deploy = gcc_aip.ModelDeployOp(
        project="my-project",
        model=training_job.outputs["model"],
        endpoint="projects/my-project/locations/us-central1/endpoints/123"
    )
```

---

## Feature Store

### Overview

Vertex AI Feature Store is a centralized repository to store, serve, and manage ML features. Ensures consistency between training and serving.

### Key Concepts

- **Feature Store**: Top-level container
- **Entity Type**: Category of entities (e.g., users, products)
- **Entity**: Single instance (e.g., user_123)
- **Feature**: Individual attribute (e.g., age, purchase_count)

### Creating Feature Store

```python
from google.cloud import aiplatform

# Create feature store
feature_store = aiplatform.Featurestore.create(
    featurestore_id="my_feature_store",
    online_store_fixed_node_count=1
)

# Create entity type
users_entity = feature_store.create_entity_type(
    entity_type_id="users",
    description="User entity type"
)

# Create features
users_entity.create_feature(
    feature_id="age",
    value_type="INT64",
    description="User age"
)

users_entity.create_feature(
    feature_id="purchase_count",
    value_type="INT64",
    description="Total purchases"
)

users_entity.create_feature(
    feature_id="average_order_value",
    value_type="DOUBLE",
    description="Average order value"
)
```

### Ingesting Features

```python
# Batch ingestion from BigQuery
users_entity.ingest_from_bq(
    feature_ids=["age", "purchase_count", "average_order_value"],
    feature_time="feature_timestamp",
    bq_source_uri="bq://my-project.my_dataset.user_features",
    entity_id_field="user_id"
)

# Batch ingestion from GCS
users_entity.ingest_from_gcs(
    feature_ids=["age", "purchase_count"],
    feature_time="feature_timestamp",
    gcs_source_uris=["gs://my-bucket/features/users.avro"],
    gcs_source_type="avro",
    entity_id_field="user_id"
)
```

### Serving Features

```python
# Online serving (low latency)
entity_views = feature_store.read(
    entity_type_id="users",
    entity_ids=["user_123", "user_456"],
    feature_ids=["age", "purchase_count"]
)

# Batch serving for training
training_data = feature_store.batch_serve_to_bq(
    bq_destination_output_uri="bq://my-project.my_dataset.training_data",
    serving_feature_ids={
        "users": ["age", "purchase_count", "average_order_value"]
    },
    read_instances_uri="gs://my-bucket/training_instances.csv"
)
```

### Feature Store Benefits

| Benefit | Description |
|---------|-------------|
| **Training-Serving Consistency** | Same features for training and inference |
| **Feature Reuse** | Share features across ML projects |
| **Point-in-Time Lookups** | Avoid data leakage with historical values |
| **Low Latency Serving** | Online serving for real-time predictions |
| **Monitoring** | Track feature freshness and health |

---

## Model Registry & Experimentation

### Experiments Tracking

```python
from google.cloud import aiplatform

# Initialize experiment
aiplatform.init(experiment="my-experiment")

# Start a run
with aiplatform.start_run("run-001") as run:
    # Log parameters
    run.log_params({
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 10
    })
    
    # Training loop
    for epoch in range(10):
        # ... training code ...
        
        # Log metrics
        run.log_metrics({
            "accuracy": 0.95,
            "loss": 0.05
        })
    
    # Log artifacts
    run.log_model(model, artifact_id="trained-model")
```

### Model Registry

```python
from google.cloud import aiplatform

# Register model
model = aiplatform.Model.upload(
    display_name="my-model",
    artifact_uri="gs://my-bucket/model/",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-12:latest",
    labels={"version": "1.0", "team": "ml-team"}
)

# List model versions
models = aiplatform.Model.list(filter="display_name=my-model")

# Get specific model version
model = aiplatform.Model(model_name="projects/my-project/locations/us-central1/models/123")

# Model aliases
model.update(version_aliases=["production", "stable"])
```

---

## Generative AI on Vertex AI

### Foundation Models

#### PaLM API / Gemini

```python
import vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.generative_models import GenerativeModel

# Initialize
vertexai.init(project="my-project", location="us-central1")

# Text generation with Gemini
model = GenerativeModel("gemini-1.0-pro")
response = model.generate_content("Explain machine learning in simple terms")
print(response.text)

# Chat
chat = model.start_chat()
response = chat.send_message("What is Vertex AI?")
print(response.text)
response = chat.send_message("How does it compare to SageMaker?")
print(response.text)
```

#### Embeddings

```python
from vertexai.language_models import TextEmbeddingModel

model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
embeddings = model.get_embeddings(["Hello world", "Vertex AI is great"])
for embedding in embeddings:
    print(f"Vector dimension: {len(embedding.values)}")
```

#### Code Generation

```python
from vertexai.language_models import CodeGenerationModel

model = CodeGenerationModel.from_pretrained("code-bison@001")
response = model.predict(
    prefix="Write a Python function to calculate fibonacci numbers:"
)
print(response.text)
```

### Model Tuning

```python
from vertexai.language_models import TextGenerationModel

# Supervised tuning
model = TextGenerationModel.from_pretrained("text-bison@001")
tuning_job = model.tune_model(
    training_data="gs://my-bucket/tuning_data.jsonl",
    tuned_model_display_name="my-tuned-model",
    epochs=4,
    learning_rate_multiplier=1.0
)
```

### Imagen (Image Generation)

```python
from vertexai.vision_models import ImageGenerationModel

model = ImageGenerationModel.from_pretrained("imagen-2.0")
images = model.generate_images(
    prompt="A serene mountain landscape at sunset",
    number_of_images=4
)
for i, image in enumerate(images):
    image.save(f"generated_{i}.png")
```

---

## Security & IAM

### IAM Roles

| Role | Description | Use Case |
|------|-------------|----------|
| `roles/aiplatform.user` | Use Vertex AI services | Data scientists |
| `roles/aiplatform.admin` | Full access to Vertex AI | ML platform admins |
| `roles/aiplatform.featurestoreUser` | Use Feature Store | Feature consumers |
| `roles/aiplatform.modelUser` | Make predictions | Applications |
| `roles/aiplatform.pipelinesUser` | Run pipelines | CI/CD systems |

### Service Account Configuration

```bash
# Create service account for ML workloads
gcloud iam service-accounts create vertex-ai-sa \
    --display-name="Vertex AI Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:vertex-ai-sa@my-project.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:vertex-ai-sa@my-project.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### VPC Service Controls

```yaml
# Vertex AI in VPC Service Controls perimeter
resources:
  - aiplatform.googleapis.com
  - storage.googleapis.com
  - bigquery.googleapis.com
```

### CMEK (Customer-Managed Encryption Keys)

```python
# Create endpoint with CMEK
endpoint = aiplatform.Endpoint.create(
    display_name="secure-endpoint",
    encryption_spec_key_name="projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key"
)
```

---

## Cost Optimization

### Training Cost Optimization

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **Spot VMs** | Up to 91% | Use preemptible instances for training |
| **Right-sizing** | 20-40% | Choose appropriate machine types |
| **Distributed training** | Faster completion | Use multi-worker training |
| **Early stopping** | Variable | Stop training when metrics plateau |

```python
# Use spot VMs for training
custom_job = aiplatform.CustomJob(
    display_name="spot-training",
    worker_pool_specs=[{
        "machine_spec": {
            "machine_type": "n1-standard-8",
            "accelerator_type": "NVIDIA_TESLA_T4",
            "accelerator_count": 1
        },
        "replica_count": 1,
        "disk_spec": {
            "boot_disk_type": "pd-ssd",
            "boot_disk_size_gb": 100
        },
        "container_spec": {
            "image_uri": "gcr.io/my-project/trainer:v1"
        }
    }],
    scheduling={"restart_job_on_worker_restart": True}  # Spot VM support
)
```

### Prediction Cost Optimization

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| **Autoscaling** | Variable | May have cold start latency |
| **Batch predictions** | 50-80% | Higher latency, no real-time |
| **Model optimization** | 20-40% | Requires model changes |
| **Regional endpoints** | Lower egress | Single region only |

---

## ACE Exam Focus

### Key Concepts for ACE

1. **Pre-trained APIs**: Know when to use Vision, Speech, NLP APIs
2. **Basic AutoML**: Understand data requirements and training process
3. **Deployment basics**: Deploy models to endpoints
4. **IAM**: Vertex AI roles and service accounts
5. **gcloud commands**: Basic model and endpoint management

### Sample ACE Questions

**Q1:** Your team needs to extract text from scanned documents. What should you use?
- **A:** Vision API with TEXT_DETECTION or DOCUMENT_TEXT_DETECTION

**Q2:** You need to deploy a custom TensorFlow model for real-time predictions. What steps are required?
- **A:** 
  1. Upload model to Vertex AI Model Registry
  2. Create an endpoint
  3. Deploy model to endpoint with appropriate machine type

**Q3:** Which IAM role should a data scientist have to train models but not deploy them?
- **A:** `roles/aiplatform.user` (can train, cannot manage endpoints)

### ACE gcloud Commands

```bash
# List models
gcloud ai models list --region=us-central1

# Create endpoint
gcloud ai endpoints create --display-name="my-endpoint" --region=us-central1

# Deploy model
gcloud ai endpoints deploy-model ENDPOINT_ID \
    --model=MODEL_ID \
    --display-name="deployed-model" \
    --machine-type="n1-standard-4" \
    --region=us-central1

# Make prediction
gcloud ai endpoints predict ENDPOINT_ID \
    --region=us-central1 \
    --json-request=request.json
```

---

## PCA Exam Focus

### Architecture Decision Framework

#### When to Use AutoML vs Custom Training

| Scenario | Recommendation |
|----------|----------------|
| Limited ML expertise, standard task | AutoML |
| Need quick baseline model | AutoML |
| Complex custom architecture | Custom Training |
| State-of-the-art performance required | Custom Training |
| Specific framework requirement (PyTorch) | Custom Training |

#### When to Use Pre-trained APIs vs AutoML

| Scenario | Recommendation |
|----------|----------------|
| Generic task (OCR, sentiment) | Pre-trained API |
| Domain-specific vocabulary | AutoML Text |
| Custom categories | AutoML |
| Compliance requires model ownership | AutoML or Custom |

### MLOps Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ML ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│   │   Source    │────►│   Build     │────►│   Test      │              │
│   │   (Git)     │     │   (Cloud    │     │   (Vertex   │              │
│   │             │     │    Build)   │     │   Pipeline) │              │
│   └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                  │                       │
│                                                  ▼                       │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│   │  Monitor    │◄────│   Serve     │◄────│   Deploy    │              │
│   │  (Vertex    │     │  (Endpoint) │     │  (Model     │              │
│   │  Monitoring)│     │             │     │   Registry) │              │
│   └─────────────┘     └─────────────┘     └─────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sample PCA Questions

**Q1:** A financial company needs a fraud detection system that processes 10,000 transactions/second with <100ms latency. The model needs to be updated daily with new fraud patterns. Design the solution.

**A:** 
- **Training**: Custom training with TensorFlow on Vertex AI (daily retraining)
- **Feature Store**: Store user behavior features for training-serving consistency
- **Serving**: Vertex AI endpoint with autoscaling, GPU-accelerated
- **Pipeline**: Vertex AI Pipelines for automated daily retraining
- **Monitoring**: Model monitoring for prediction drift

**Q2:** A retail company wants to build a product recommendation system. They have 100M users and 10M products. What architecture should they use?

**A:**
- **Embeddings**: Custom training to create user/product embeddings
- **Similarity**: Store embeddings in Vector Search (Matching Engine)
- **Real-time**: Cache top recommendations in Memorystore
- **Batch**: Nightly batch predictions for less active users

**Q3:** A healthcare company needs to classify medical images with 99.9% accuracy. They have 50,000 labeled images. What approach should they take?

**A:**
- **Start with AutoML**: Establish baseline with AutoML Vision
- **Custom Training**: If AutoML insufficient, use transfer learning from medical imaging models
- **Validation**: Extensive test dataset, cross-validation
- **Monitoring**: Continuous monitoring for model degradation

---

## Summary Comparison

| Feature | ACE Focus | PCA Focus |
|---------|-----------|-----------|
| Pre-trained APIs | How to use | When to choose |
| AutoML | Basic training | Architecture decisions |
| Custom Training | Awareness | Full implementation |
| Pipelines | Awareness | Design and implementation |
| Feature Store | Awareness | Integration patterns |
| Model Monitoring | Basic | Full implementation |
| Cost Optimization | Basic | Detailed strategies |
| Security | IAM basics | VPC-SC, CMEK, compliance |
