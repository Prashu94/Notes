# AI and ML deep dive

Read `13-ai-ml-and-gemini.md` first. This file is how the PCA objectives in sections 2.4 and 2.5 turn into a design you can defend, including the renewal exam’s generative-AI weight.

Names: the exam guide says Gemini Enterprise Agent Platform. Consoles and APIs still say Vertex AI and `aiplatform.googleapis.com`. Use the exam name in an answer, and the API name in a command.

## Prebuilt API versus a Gemini model versus a model you train

| The task | First choice | Train your own only if |
| --- | --- | --- |
| Invoice, form, ID document | Document AI processor | The processor misses fields you cannot customize |
| Label a photo, OCR, safe search | Vision API | You need a private taxonomy Vision does not have |
| Transcribe a call | Speech-to-Text | Heavy domain vocabulary, and even then try adaptation first |
| Translate | Translation API | |
| Short sentiment or entities | Natural Language API | The labels are your own |
| Shot breaks and labels on a file | Video Intelligence | |
| Talk to a user with intents and handoff | Conversational Agents | |
| Search your corpus | Agent Search / Vertex AI Search | |
| Answer in prose over your corpus | Gemini plus retrieval | |
| Recommend products | Retail search or a recommendations model | |
| Score a tabular fraud row every millisecond | A deployed custom or AutoML model, or BigQuery ML | |
| Generate or summarize with no private corpus | A Gemini model, grounded on Google Search if the facts must be current | |

Document AI and a Gemini prompt both “read an invoice”. Document AI is the structured extractor. Gemini is the reasoner you add if the stem asks for a judgment or a letter. Using only Gemini and hoping the JSON is stable is the weaker design when a processor exists.

## Calling a model

Enable the API, pick a region where the model is offered, and call with Application Default Credentials. Do not put an API key in a mobile app for a private enterprise model. Mobile clients call your backend. The backend calls Gemini.

```bash
gcloud services enable aiplatform.googleapis.com
```

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="PROJECT_ID", location="us-central1")
model = GenerativeModel("gemini-2.5-flash")
response = model.generate_content(
    "Summarize the attached policy in five bullets.",
    generation_config={"temperature": 0.2, "max_output_tokens": 512},
)
print(response.text)
```

The model ID changes. On exam day use the family the stem names. Temperature near 0 for extraction. Higher only when the stem wants variation. Max output tokens cap cost and runaway answers.

Function calling is how the model requests a tool (`get_order`, `search_catalog`) instead of inventing a result. You execute the tool, return the JSON, and the model writes the final sentence. The tool runs in your service account’s IAM. The model does not get a bypass.

Grounding with Google Search attaches public-web sources. Use it when the answer must cite the web. Do not use it as a substitute for your private catalog. Private facts use retrieval.

## RAG that does not leak

1. Documents land in a bucket, one prefix or one index per tenant if the tenants are hostile to each other.
2. A pipeline (Cloud Run, Dataflow, or an Agent Platform pipeline) chunks them.
3. An embedding model writes vectors.
4. The vector store is Vector Search, BigQuery with a vector index, or AlloyDB. Store tenant id, document id, and an ACL beside the vector.
5. The query path embeds the question, filters by tenant and by the caller’s allowed document ids, then sends only those chunks to Gemini.
6. The response returns citations (document id, chunk).
7. Model Armor inspects the prompt and the response.
8. Sensitive Data Protection redacts identifiers before anything is logged or embedded, if the corpus is not supposed to contain them.
9. Prompts that you keep go to a locked dataset, not the default log bucket.

The filter in step 5 is the control that stops the case-study failure mode where customer A sees customer B’s contract. A shared index with no filter is a bug, not a simplification.

Vector Search is the managed nearest-neighbor index when you are serving many queries and the vectors are not already in BigQuery. BigQuery vector search is the answer when the embeddings already live next to the warehouse facts and the callers are SQL. AlloyDB is the answer when the operational Postgres app needs the vectors in the same transaction boundary.

## Agents

Agent Builder and Gemini Enterprise agents are the managed place to assemble instructions, tools, and data stores. Conversational Agents (Dialogflow CX) is the dialogue manager with flows, pages, and human handoff. NotebookLM, named on the exam guide, is the grounded notebook over sources a person supplies.

Use an agent when the stem says a user talks to a system that must call your APIs. Use a single `generate_content` call when the stem is one summarization in a pipeline. An agent platform for a nightly one-shot summary is extra moving parts.

Human in the loop, when the case study requires it, is a queue of drafts and a person who approves before publish. The model does not write to the production catalog directly. Cloud Tasks or Pub/Sub plus a Cloud Run review UI is enough machinery.

## Training and MLOps (section 2.4)

Agent Platform Pipelines are Kubeflow pipelines: data extract from BigQuery or Cloud Storage, train, evaluate against a threshold, deploy only if the metric holds, register the version.

| Piece | Role |
| --- | --- |
| Managed dataset | Tabular, text, image, video, with a schema |
| Custom job | Your container, your code |
| AutoML | The platform picks the model for tabular or vision when you have labeled rows and no modeling team |
| Hyperparameter tuning | Many trials. Use Spot or a cheaper machine for trials. |
| Experiments | Compare runs |
| Model Registry | Versions and aliases (`prod`, `candidate`) |
| Endpoint | Deployed model, traffic split, autoscaling |
| Model Monitoring | Skew and drift against training stats, alert to Monitoring |
| Feature Store | The same feature definition offline and online |
| AI Hypercomputer | The large job: GPU or TPU topology, reservations, high-bandwidth networking |
| Cloud Run functions | A thin trigger or a small inference wrapper, which the exam guide names next to Hypercomputer |

```bash
gcloud ai endpoints create --region="$REGION" --display-name=fraud
gcloud ai endpoints deploy-model ENDPOINT_ID \
  --region="$REGION" \
  --model=MODEL_ID \
  --display-name=v2 \
  --traffic-split=0=95,v2=5 \
  --machine-type=n1-standard-4 \
  --min-replica-count=1 --max-replica-count=3
```

Traffic split on the endpoint is the canary. A separate Cloud Run service that you forget to route is not a canary the platform can roll back.

Consumption models: on-demand prediction for spiky low volume, a min replica count when latency cannot wait for scale from zero, reservations and committed use for a training run that must have the GPUs, Spot or flex for interruptible trials. Match the spend to how interruptible the job is. The same way you treat VMs.

BigQuery ML is the path when the team will not leave SQL. The model can be exported or used from SQL. It is the wrong path for a multimodal Gemini app.

## Security checklist for an AI system

| Risk | Control |
| --- | --- |
| Prompt injection | Model Armor, tight tool allow-lists, system instructions that are not your only control |
| Training data has PII or PHI | Sensitive Data Protection, approved datasets, CMEK, do not send regulated text to an endpoint outside the perimeter |
| Model or logs leak other tenants | IAM on the endpoint, retrieval filter, separate indexes or hard tenant filters |
| Someone copies the dataset to a personal project | VPC Service Controls on `aiplatform.googleapis.com` and `storage.googleapis.com` |
| Key control | CMEK on the bucket, the index, and the endpoint where the product supports it |
| Public client calls the model directly | No. Your backend holds the identity. |
| Untrusted container serves the model | Binary Authorization if it runs on GKE or Cloud Run |
| You cannot explain a denial | Log the decision and the citation. Explainable AI or logged features when a person is denied credit or a similar regulated decision. |

Gemini Cloud Assist in the console is an operator aid. It is not an approval. A design it suggests still goes through Terraform review. The exam lists it under technical requirements and under advising teams. Know what it is for: explain an error, draft a diagram, point at a document. Know what it is not: a control plane.

## Cost

Token cost dominates chat. Cache and retrieve instead of stuffing the whole manual into the prompt. Pick the smaller Gemini model for classification. Batch prediction is cheaper than online for a nightly score of a million rows. A GPU endpoint with `min-replica-count` of 2 costs money all night. Scale it to the traffic, or use a model API that is not a dedicated GPU if the latency budget allows.

## Exercises

1. The business wants invoice fields in a database. Nobody asked for a custom model. What do you deploy?
2. A 5% canary of a fraud model must roll back if precision drops. Where is the split configured?
3. Two tenants share one vector index. What must the query include besides the embedding?
4. A developer wants the mobile app to call Gemini with an API key in the binary. What do you require instead?
5. The case study says a person approves catalog text before it is published. Where does the model write?

### Answers

1. A Document AI processor, then a load into BigQuery or Cloud SQL. Gemini only if they also want a narrative.
2. On the Agent Platform endpoint traffic split, with Model Monitoring or a custom metric. Not a DNS weight.
3. A tenant filter, and an ACL filter for the caller. The nearest neighbor without that filter is the bug.
4. The app calls your backend. The backend uses a service account. Model Armor sits on that path.
5. To a draft store or a review queue. Production is updated only after approval.
