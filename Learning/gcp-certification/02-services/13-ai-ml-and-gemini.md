# AI, ML, and Gemini

PCA sections 1.3, 2.4, 2.5, and the “securing AI” bullet in 3.1. ACE is lighter: know that these products exist and which one a simple stem wants. The PCA renewal exam is mostly generative AI. This chapter matters for both the standard architect exam and renewal.

Product names moved. The exam guide says **Gemini Enterprise Agent Platform**. Older docs and many consoles still say **Vertex AI**. Treat them as the same platform unless a question contrasts two SKUs. **Gemini Enterprise** (agents, NotebookLM) is the end-user and agent product the exam lists separately from the training platform.

## What to use

| Job | Product |
| --- | --- |
| Call a Gemini model with text, image, audio, or video | Agent Platform / Vertex AI generative API, a Gemini model |
| Browse and deploy a foundation model | Model Garden |
| Chatbot with tools and grounding | Agent Builder, or Gemini Enterprise agents |
| Ground answers in your documents | RAG: embeddings in Vector Search, BigQuery vector search, or AlloyDB, plus a Gemini model. Vertex AI Search / Agent Search for the managed search product. |
| Train a custom model, track experiments | Managed training, Experiments, Model Registry |
| Orchestrate data prep, train, evaluate, deploy | Agent Platform Pipelines (Kubeflow Pipelines on the platform) |
| Online or batch prediction | Endpoint (inference) |
| Features reused by many models | Feature Store |
| Drift and skew after launch | Model Monitoring |
| Large training run, GPUs or TPUs, high-bandwidth fabric | AI Hypercomputer |
| One-shot vision, speech, translation, without training | Prebuilt APIs (Vision, Speech-to-Text, Text-to-Speech, Translation, Natural Language, Video Intelligence, Document AI) |
| Contact-center or website conversation | Conversational Agents (Dialogflow CX). Dialogflow ES is the older product. |
| SQL users train a model | BigQuery ML |
| Notebook for an analyst | Colab Enterprise or Agent Platform Workbench |
| Research notes over your corpus | NotebookLM, as named in the exam guide |
| Prompt and response filtering | Model Armor |
| PII in training data or prompts | Sensitive Data Protection |

## Gemini models

You do not memorize a model version that will be stale. You know how to choose:

- A **faster, cheaper** Gemini model for high-volume classification and routing.
- A **stronger** Gemini model for hard reasoning, long documents, and multimodal analysis.
- Context windows are large. That does not mean you paste your whole lake into the prompt. Retrieval is cheaper and more controllable.
- **Grounding with Google Search** when the answer must reflect the public web and you can show sources.
- **Function calling** when the model must call your API rather than invent a result.
- **System instructions** set role and policy. They are not a security boundary. Model Armor and IAM are.

Enterprise controls the exam cares about: CMEK, VPC Service Controls, private endpoints, data residency where the model is offered, and not using customer prompts to train Google’s foundation models under the enterprise terms. Read the current data-governance page before you promise a customer that. The exam tests the idea: enterprise generative AI has a governance story, not only a prompt.

```bash
# Enable the platform API. The service name is still often aiplatform.
gcloud services enable aiplatform.googleapis.com

# List publisher models you can call (names change)
gcloud ai models list --region="$REGION" 2>/dev/null | head

# A prediction call is usually the client library, not a one-line gcloud.
# Python shape, using Application Default Credentials:
#   import vertexai
#   from vertexai.generative_models import GenerativeModel
#   vertexai.init(project=PROJECT_ID, location=REGION)
#   model = GenerativeModel("gemini-2.5-flash")
#   print(model.generate_content("Summarize this paragraph: ...").text)
```

Use the model ID the Model Garden page shows on exam day. Do not hard-code a 2024 model ID into a design you will defend in 2026.

## Pipelines, training, serving

Agent Platform Pipelines (PCA 2.4) are the MLOps answer: a graph that prepares data, trains, evaluates against a threshold, and deploys only if the metric holds. Run them on a schedule or on new data in Cloud Storage or BigQuery.

```bash
gcloud ai pipelines list --region="$REGION"
# Compiling and submitting a pipeline is a Python SDK action
# (KFP compiler, aiplatform.PipelineJob.submit).
```

Training:

- Managed dataset and a training job for tabular or custom containers.
- Custom jobs and hyperparameter tuning.
- GPUs and TPUs attached to the job. AI Hypercomputer when the job is large enough to care about topology and a reservation.
- Spot or flex consumption for interruptible experiments. Reserved or committed capacity for the training run that cannot stop.

Serving:

- An **endpoint** with one or more deployed models, traffic split for canaries.
- Autoscaling replicas.
- Private endpoint on your VPC when the model is sensitive.
- Cloud Run functions or Cloud Run in front of a model only when you need a thin application wrapper. The exam explicitly allows AI Hypercomputer, Cloud Run functions, and Agent Platform together. Do not force every inference through GKE.

Model Registry holds versions. Model Monitoring compares prediction skew and drift to training stats and alerts. Feature Store stops each team from rebuilding the same feature badly.

## Prebuilt APIs (PCA 2.5)

Differentiate them. The exam says Search, Conversation, Vision, Image, Video, and Audio.

| API | Input | Do not use it for |
| --- | --- | --- |
| Vision / Image | Labels, OCR, safe search, logos | A custom defect model. That is a trained model in Model Garden or your own training. |
| Video Intelligence | Shot detection, labels on video | Live broadcast packaging. That is Transcoder API or Live Stream API. |
| Speech-to-Text | Audio to text | A full contact center. Add Conversational Agents. |
| Text-to-Speech | Text to audio | |
| Translation | Language to language | |
| Natural Language | Entities and sentiment on text | Long RAG answers. That is Gemini. |
| Document AI | Forms, invoices, OCR with structure | A data warehouse. |
| Conversational Agents | Intent, dialogue, handoff to a human | Bulk classification of stored text. |
| Vertex AI Search / Agent Search | Search and recommendations over your data | The system of record. |
| Discovery-style retail search | Product discovery in commerce case studies | |

```bash
gcloud services enable vision.googleapis.com language.googleapis.com \
  speech.googleapis.com texttospeech.googleapis.com translate.googleapis.com \
  documentai.googleapis.com dialogflow.googleapis.com
```

Calls are REST or client libraries with ADC. There is often no long-lived `gcloud` “run OCR” command. Know which API, which IAM role (`roles/documentai.apiUser` and similar), and that the file should sit in Cloud Storage for large inputs.

## RAG pattern you can defend

1. Documents land in Cloud Storage.
2. A pipeline chunks them and writes embeddings (a Gemini embedding model, or a model from Model Garden).
3. Vectors live in Vector Search, BigQuery, or AlloyDB, next to the metadata you must filter on (tenant, region, product line).
4. The request embeds the question, retrieves top-k with an authorization filter, and sends those chunks to Gemini.
5. The answer cites the chunk ids. A human reviews when the case study says human-in-the-loop (Cymbal’s catalog is the example of that constraint).
6. Model Armor and Sensitive Data Protection sit on the path. IAM and VPC-SC sit under it.

Skipping the authorization filter is how one tenant sees another tenant’s documents. That is a security question, not an ML question.

## Gemini for operators

**Gemini Cloud Assist** (PCA 1.2 and 5.1) helps in the console: explain an error, suggest a design, read a product page in context. It does not replace IAM. A suggestion is not a change request. **Gemini Code Assist** helps in the IDE. **Gemini in BigQuery** writes SQL. The architect uses these tools and still reviews the plan.

## Workbenches

| Product | Who |
| --- | --- |
| Colab Enterprise | Notebooks with IAM, a runtime in your project |
| Workbench (Agent Platform) | Managed notebook VM for data scientists |
| Cloud Workstations | Locked-down developer desktop, not specifically a training cluster |
| Deep Learning VM images and containers | You assemble the CUDA image yourself on Compute Engine or GKE |

## Exercises

1. The team has no training data and needs to extract invoice fields. Which API?
2. You must canary 5% of predictions to a new model version and roll back. Where does traffic split live?
3. A contact center on the website, with human handoff. Which product?
4. Training a large model needs a GPU fabric and a reservation. Which platform name does the exam use?
5. User prompts may contain card numbers, and the bot must not follow “ignore your instructions”. Which two controls?

### Answers

1. Document AI. Not a custom Gemini fine-tune as the first step.
2. An Agent Platform / Vertex AI endpoint, traffic split between deployed models.
3. Conversational Agents (Dialogflow CX), often with Agent Search if it must answer from a catalog.
4. AI Hypercomputer.
5. Sensitive Data Protection (inspect and redact) and Model Armor.
