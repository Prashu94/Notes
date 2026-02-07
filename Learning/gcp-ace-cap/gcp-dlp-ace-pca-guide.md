# Google Cloud Data Loss Prevention (DLP) - ACE & PCA Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [DLP Architecture](#dlp-architecture)
3. [InfoTypes and Detectors](#infotypes-and-detectors)
4. [Inspection Jobs](#inspection-jobs)
5. [De-identification](#de-identification)
6. [Templates and Job Triggers](#templates-and-job-triggers)
7. [Data Profiles](#data-profiles)
8. [Risk Analysis](#risk-analysis)
9. [Integration with Other Services](#integration-with-other-services)
10. [Security and IAM](#security-and-iam)
11. [Best Practices](#best-practices)
12. [ACE Exam Focus](#ace-exam-focus)
13. [PCA Exam Focus](#pca-exam-focus)

---

## Overview

### What is Cloud DLP?

Cloud Data Loss Prevention (DLP) is a fully managed service for discovering, classifying, and protecting sensitive data. It helps you understand and manage sensitive data across your organization.

**Key Capabilities:**
- **Inspection**: Find sensitive data in storage, databases, and data streams
- **Classification**: Categorize data by type (PII, PHI, financial)
- **De-identification**: Mask, tokenize, or encrypt sensitive data
- **Risk Analysis**: Assess re-identification risk of datasets
- **Data Profiling**: Automatic discovery and classification at scale

### DLP Use Cases

| Use Case | Description | Industry |
|----------|-------------|----------|
| **PII Discovery** | Find names, SSNs, emails | All |
| **PHI Protection** | Protect medical records | Healthcare |
| **PCI Compliance** | Detect credit card numbers | Finance/Retail |
| **Data Masking** | Anonymize data for analytics | All |
| **GDPR Compliance** | Right to be forgotten | All (EU) |
| **Data Migration** | Classify before cloud migration | All |

---

## DLP Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLOUD DLP ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      DLP API SERVICE                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │   │
│  │  │  Inspection │  │    De-ID    │  │    Risk     │             │   │
│  │  │   Engine    │  │   Engine    │  │  Analysis   │             │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│           ┌─────────────────────┼─────────────────────┐                │
│           │                     │                      │                │
│           ▼                     ▼                      ▼                │
│   ┌──────────────┐    ┌──────────────┐     ┌──────────────┐           │
│   │    Cloud     │    │   BigQuery   │     │   Datastore/ │           │
│   │   Storage    │    │              │     │   Firestore  │           │
│   └──────────────┘    └──────────────┘     └──────────────┘           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     OUTPUTS & ACTIONS                            │   │
│  │  • Findings (to BigQuery/Pub/Sub)                               │   │
│  │  • De-identified data                                            │   │
│  │  • Data profiles                                                 │   │
│  │  • Alerts/Notifications                                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Processing Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| **Content API** | Inspect/de-identify content inline | Real-time processing |
| **Storage Jobs** | Scan data at rest | Batch discovery |
| **Hybrid Jobs** | Scan data from any source | External data |
| **Data Profiles** | Automatic continuous scanning | Large-scale discovery |

---

## InfoTypes and Detectors

### Built-in InfoTypes

Cloud DLP provides 150+ built-in detectors:

#### Personal Identifiable Information (PII)
```
PERSON_NAME          # Names
EMAIL_ADDRESS        # Email addresses
PHONE_NUMBER         # Phone numbers
STREET_ADDRESS       # Physical addresses
DATE_OF_BIRTH        # Birthdates
```

#### Government IDs
```
US_SOCIAL_SECURITY_NUMBER    # US SSN
US_PASSPORT                  # US Passport
US_DRIVERS_LICENSE_NUMBER    # US Driver's License
UK_NATIONAL_INSURANCE_NUMBER # UK NI Number
```

#### Financial Information
```
CREDIT_CARD_NUMBER           # Credit/debit cards
IBAN_CODE                    # International bank accounts
US_BANK_ROUTING_MICR         # US bank routing
SWIFT_CODE                   # SWIFT codes
```

#### Healthcare
```
US_DEA_NUMBER               # DEA numbers
US_HEALTHCARE_NPI           # Healthcare provider IDs
ICD9_CODE                   # Medical diagnosis codes
ICD10_CODE                  # Medical diagnosis codes
```

### Custom InfoTypes

#### Dictionary-Based
```python
from google.cloud import dlp_v2

client = dlp_v2.DlpServiceClient()

# Custom dictionary InfoType
custom_info_type = {
    "info_type": {"name": "COMPANY_EMPLOYEE_ID"},
    "dictionary": {
        "word_list": {
            "words": ["EMP001", "EMP002", "EMP003"]
        }
    }
}

# Or from Cloud Storage
custom_info_type = {
    "info_type": {"name": "COMPANY_EMPLOYEE_ID"},
    "dictionary": {
        "cloud_storage_path": {
            "path": "gs://my-bucket/employee_ids.txt"
        }
    }
}
```

#### Regex-Based
```python
# Custom regex InfoType
custom_info_type = {
    "info_type": {"name": "EMPLOYEE_ID"},
    "regex": {
        "pattern": "EMP[0-9]{6}"  # EMP followed by 6 digits
    }
}

# With context
custom_info_type = {
    "info_type": {"name": "INTERNAL_PROJECT_CODE"},
    "regex": {
        "pattern": "PRJ-[A-Z]{3}-[0-9]{4}"
    },
    "detection_rules": [{
        "hotword_rule": {
            "hotword_regex": {"pattern": "project|code|id"},
            "proximity": {"window_before": 10},
            "likelihood_adjustment": {
                "fixed_likelihood": "VERY_LIKELY"
            }
        }
    }]
}
```

#### Stored InfoTypes
```bash
# Create stored InfoType (large dictionaries)
gcloud dlp stored-info-types create \
    --project=my-project \
    --display-name="Customer IDs" \
    --description="List of customer identifiers" \
    --dictionary-cloud-storage-path="gs://bucket/customer_ids.txt"
```

### Likelihood Levels

| Level | Meaning |
|-------|---------|
| `VERY_UNLIKELY` | Very low confidence |
| `UNLIKELY` | Low confidence |
| `POSSIBLE` | Medium confidence |
| `LIKELY` | High confidence |
| `VERY_LIKELY` | Very high confidence |

---

## Inspection Jobs

### Inline Content Inspection

```python
from google.cloud import dlp_v2

def inspect_string(project_id, content):
    """Inspect a string for sensitive data."""
    client = dlp_v2.DlpServiceClient()
    
    # Configure inspection
    inspect_config = {
        "info_types": [
            {"name": "EMAIL_ADDRESS"},
            {"name": "PHONE_NUMBER"},
            {"name": "CREDIT_CARD_NUMBER"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"}
        ],
        "min_likelihood": dlp_v2.Likelihood.POSSIBLE,
        "include_quote": True,  # Include matched text
        "limits": {
            "max_findings_per_request": 100
        }
    }
    
    # Create request
    item = {"value": content}
    response = client.inspect_content(
        request={
            "parent": f"projects/{project_id}",
            "inspect_config": inspect_config,
            "item": item
        }
    )
    
    # Process findings
    for finding in response.result.findings:
        print(f"Info type: {finding.info_type.name}")
        print(f"Likelihood: {finding.likelihood.name}")
        print(f"Quote: {finding.quote}")
        print(f"Location: {finding.location}")

# Example usage
content = """
Contact John Doe at john.doe@example.com or 555-123-4567.
His SSN is 123-45-6789 and credit card is 4532-1234-5678-9012.
"""
inspect_string("my-project", content)
```

### Storage Inspection Jobs

#### Inspect Cloud Storage
```python
def create_storage_inspection_job(project_id, bucket_name):
    """Create a DLP job to inspect Cloud Storage."""
    client = dlp_v2.DlpServiceClient()
    
    # Storage configuration
    storage_config = {
        "cloud_storage_options": {
            "file_set": {
                "url": f"gs://{bucket_name}/**"
            },
            "file_types": ["TEXT_FILE", "CSV", "JSON"],
            "files_limit_percent": 100
        }
    }
    
    # Inspection configuration
    inspect_config = {
        "info_types": [
            {"name": "EMAIL_ADDRESS"},
            {"name": "CREDIT_CARD_NUMBER"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"}
        ],
        "min_likelihood": dlp_v2.Likelihood.LIKELY
    }
    
    # Actions
    actions = [{
        "save_findings": {
            "output_config": {
                "table": {
                    "project_id": project_id,
                    "dataset_id": "dlp_findings",
                    "table_id": "storage_scan_results"
                }
            }
        }
    }]
    
    # Create job
    job = client.create_dlp_job(
        request={
            "parent": f"projects/{project_id}",
            "inspect_job": {
                "storage_config": storage_config,
                "inspect_config": inspect_config,
                "actions": actions
            }
        }
    )
    
    return job.name
```

#### Inspect BigQuery
```python
def create_bigquery_inspection_job(project_id, dataset_id, table_id):
    """Create a DLP job to inspect BigQuery table."""
    client = dlp_v2.DlpServiceClient()
    
    # BigQuery configuration
    storage_config = {
        "big_query_options": {
            "table_reference": {
                "project_id": project_id,
                "dataset_id": dataset_id,
                "table_id": table_id
            },
            "rows_limit": 10000,
            "sample_method": "RANDOM_START",
            "identifying_fields": [
                {"name": "customer_id"}
            ]
        }
    }
    
    inspect_config = {
        "info_types": [
            {"name": "EMAIL_ADDRESS"},
            {"name": "PHONE_NUMBER"},
            {"name": "CREDIT_CARD_NUMBER"}
        ],
        "min_likelihood": dlp_v2.Likelihood.LIKELY
    }
    
    actions = [{
        "save_findings": {
            "output_config": {
                "table": {
                    "project_id": project_id,
                    "dataset_id": "dlp_findings",
                    "table_id": f"{table_id}_findings"
                }
            }
        }
    }, {
        "pub_sub": {
            "topic": f"projects/{project_id}/topics/dlp-notifications"
        }
    }]
    
    job = client.create_dlp_job(
        request={
            "parent": f"projects/{project_id}",
            "inspect_job": {
                "storage_config": storage_config,
                "inspect_config": inspect_config,
                "actions": actions
            }
        }
    )
    
    return job.name
```

### gcloud Commands

```bash
# Create inspection job template
gcloud dlp job-triggers create \
    --project=my-project \
    --display-name="Weekly PII Scan" \
    --inspect-config-info-types="EMAIL_ADDRESS,PHONE_NUMBER,CREDIT_CARD_NUMBER" \
    --storage-cloud-storage-url="gs://my-bucket/**" \
    --trigger-schedule="0 0 * * 0"  # Weekly

# List jobs
gcloud dlp jobs list --project=my-project

# Get job details
gcloud dlp jobs describe JOB_ID --project=my-project

# Cancel job
gcloud dlp jobs cancel JOB_ID --project=my-project
```

---

## De-identification

### De-identification Techniques

| Technique | Description | Reversible |
|-----------|-------------|------------|
| **Masking** | Replace with * or other characters | No |
| **Redaction** | Remove completely | No |
| **Replacement** | Replace with placeholder | No |
| **Bucketing** | Group into ranges | No |
| **Crypto Hash** | One-way hash | No |
| **Date Shift** | Shift dates randomly | With key |
| **Format Preserving Encryption** | Encrypt keeping format | Yes |
| **Deterministic Encryption** | Same input = same output | Yes |
| **Tokenization** | Replace with token | Yes |

### Masking

```python
def deidentify_with_masking(project_id, content):
    """De-identify using masking."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "info_types": [{"name": "EMAIL_ADDRESS"}],
                "primitive_transformation": {
                    "character_mask_config": {
                        "masking_character": "*",
                        "number_to_mask": 0,  # Mask all
                        "characters_to_ignore": [{
                            "common_characters_to_ignore": "PUNCTUATION"
                        }]
                    }
                }
            }, {
                "info_types": [{"name": "CREDIT_CARD_NUMBER"}],
                "primitive_transformation": {
                    "character_mask_config": {
                        "masking_character": "#",
                        "number_to_mask": 12,  # Keep last 4
                        "reverse_order": True
                    }
                }
            }]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content}
        }
    )
    
    return response.item.value

# Input: "Email: john@example.com, Card: 4532-1234-5678-9012"
# Output: "Email: ****@*******.***, Card: ####-####-####-9012"
```

### Redaction

```python
def deidentify_with_redaction(project_id, content):
    """De-identify by removing sensitive data."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "info_types": [{"name": "US_SOCIAL_SECURITY_NUMBER"}],
                "primitive_transformation": {
                    "redact_config": {}  # Remove completely
                }
            }]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content}
        }
    )
    
    return response.item.value

# Input: "SSN: 123-45-6789"
# Output: "SSN: "
```

### Replacement

```python
def deidentify_with_replacement(project_id, content):
    """De-identify by replacing with placeholder."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "info_types": [{"name": "PERSON_NAME"}],
                "primitive_transformation": {
                    "replace_config": {
                        "new_value": {"string_value": "[REDACTED]"}
                    }
                }
            }, {
                "info_types": [{"name": "EMAIL_ADDRESS"}],
                "primitive_transformation": {
                    "replace_with_info_type_config": {}  # Replace with type name
                }
            }]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content}
        }
    )
    
    return response.item.value

# Input: "Contact John Doe at john@example.com"
# Output: "Contact [REDACTED] at [EMAIL_ADDRESS]"
```

### Crypto-Based De-identification

#### Format-Preserving Encryption (FPE)

```python
def deidentify_with_fpe(project_id, content, key_name):
    """De-identify using format-preserving encryption."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "info_types": [{"name": "CREDIT_CARD_NUMBER"}],
                "primitive_transformation": {
                    "crypto_replace_ffx_fpe_config": {
                        "crypto_key": {
                            "kms_wrapped": {
                                "wrapped_key": "BASE64_WRAPPED_KEY",
                                "crypto_key_name": key_name
                            }
                        },
                        "common_alphabet": "NUMERIC",
                        "surrogate_info_type": {
                            "name": "TOKEN_CC"
                        }
                    }
                }
            }]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content}
        }
    )
    
    return response.item.value

# Input: "Card: 4532-1234-5678-9012"
# Output: "Card: TOKEN_CC(10):8271936450"  # Reversible with key
```

#### Deterministic Encryption

```python
def deidentify_with_deterministic(project_id, content, key_name):
    """De-identify with deterministic encryption (same input = same output)."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "info_types": [{"name": "EMAIL_ADDRESS"}],
                "primitive_transformation": {
                    "crypto_deterministic_config": {
                        "crypto_key": {
                            "kms_wrapped": {
                                "wrapped_key": "BASE64_WRAPPED_KEY",
                                "crypto_key_name": key_name
                            }
                        },
                        "surrogate_info_type": {
                            "name": "TOKEN_EMAIL"
                        }
                    }
                }
            }]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content}
        }
    )
    
    return response.item.value
```

### Date Shifting

```python
def deidentify_with_date_shift(project_id, content):
    """Shift dates while preserving relative relationships."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "info_types": [{"name": "DATE_OF_BIRTH"}],
                "primitive_transformation": {
                    "date_shift_config": {
                        "upper_bound_days": 30,
                        "lower_bound_days": -30,
                        "context": {"name": "patient_id"},  # Same shift per patient
                        "crypto_key": {
                            "kms_wrapped": {
                                "wrapped_key": "BASE64_WRAPPED_KEY",
                                "crypto_key_name": "projects/p/locations/l/keyRings/r/cryptoKeys/k"
                            }
                        }
                    }
                }
            }]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": {"value": content}
        }
    )
    
    return response.item.value
```

### Bucketing

```python
def deidentify_with_bucketing(project_id, content):
    """Replace values with ranges/buckets."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "record_transformations": {
            "field_transformations": [{
                "fields": [{"name": "age"}],
                "primitive_transformation": {
                    "bucketing_config": {
                        "buckets": [
                            {
                                "min": {"integer_value": 0},
                                "max": {"integer_value": 17},
                                "replacement_value": {"string_value": "Minor"}
                            },
                            {
                                "min": {"integer_value": 18},
                                "max": {"integer_value": 30},
                                "replacement_value": {"string_value": "18-30"}
                            },
                            {
                                "min": {"integer_value": 31},
                                "max": {"integer_value": 50},
                                "replacement_value": {"string_value": "31-50"}
                            },
                            {
                                "min": {"integer_value": 51},
                                "max": {"integer_value": 100},
                                "replacement_value": {"string_value": "51+"}
                            }
                        ]
                    }
                }
            }]
        }
    }
    
    # For structured data
    table_data = {
        "table": {
            "headers": [{"name": "name"}, {"name": "age"}],
            "rows": [
                {"values": [{"string_value": "John"}, {"integer_value": 25}]},
                {"values": [{"string_value": "Jane"}, {"integer_value": 45}]}
            ]
        }
    }
    
    response = client.deidentify_content(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_config": deidentify_config,
            "item": table_data
        }
    )
    
    return response.item
```

---

## Templates and Job Triggers

### Inspection Templates

```python
def create_inspect_template(project_id):
    """Create a reusable inspection template."""
    client = dlp_v2.DlpServiceClient()
    
    inspect_config = {
        "info_types": [
            {"name": "EMAIL_ADDRESS"},
            {"name": "PHONE_NUMBER"},
            {"name": "CREDIT_CARD_NUMBER"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"}
        ],
        "min_likelihood": dlp_v2.Likelihood.LIKELY,
        "limits": {
            "max_findings_per_request": 100,
            "max_findings_per_item": 10
        },
        "include_quote": True
    }
    
    template = client.create_inspect_template(
        request={
            "parent": f"projects/{project_id}",
            "inspect_template": {
                "display_name": "PII Detection Template",
                "description": "Detects common PII types",
                "inspect_config": inspect_config
            }
        }
    )
    
    return template.name
```

### De-identification Templates

```python
def create_deidentify_template(project_id):
    """Create a reusable de-identification template."""
    client = dlp_v2.DlpServiceClient()
    
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "info_types": [{"name": "EMAIL_ADDRESS"}],
                    "primitive_transformation": {
                        "character_mask_config": {
                            "masking_character": "*",
                            "number_to_mask": 0
                        }
                    }
                },
                {
                    "info_types": [{"name": "CREDIT_CARD_NUMBER"}],
                    "primitive_transformation": {
                        "character_mask_config": {
                            "masking_character": "#",
                            "number_to_mask": 12,
                            "reverse_order": True
                        }
                    }
                },
                {
                    "info_types": [{"name": "US_SOCIAL_SECURITY_NUMBER"}],
                    "primitive_transformation": {
                        "redact_config": {}
                    }
                }
            ]
        }
    }
    
    template = client.create_deidentify_template(
        request={
            "parent": f"projects/{project_id}",
            "deidentify_template": {
                "display_name": "Standard PII Masking",
                "description": "Masks common PII types",
                "deidentify_config": deidentify_config
            }
        }
    )
    
    return template.name
```

### Job Triggers

```python
def create_job_trigger(project_id, bucket_name):
    """Create a scheduled inspection job."""
    client = dlp_v2.DlpServiceClient()
    
    job_trigger = client.create_job_trigger(
        request={
            "parent": f"projects/{project_id}",
            "job_trigger": {
                "display_name": "Weekly PII Scan",
                "description": "Scans storage bucket weekly for PII",
                "triggers": [{
                    "schedule": {
                        "recurrence_period_duration": {"seconds": 604800}  # Weekly
                    }
                }],
                "status": dlp_v2.JobTrigger.Status.HEALTHY,
                "inspect_job": {
                    "storage_config": {
                        "cloud_storage_options": {
                            "file_set": {"url": f"gs://{bucket_name}/**"}
                        }
                    },
                    "inspect_config": {
                        "info_types": [
                            {"name": "EMAIL_ADDRESS"},
                            {"name": "CREDIT_CARD_NUMBER"}
                        ],
                        "min_likelihood": dlp_v2.Likelihood.LIKELY
                    },
                    "actions": [{
                        "save_findings": {
                            "output_config": {
                                "table": {
                                    "project_id": project_id,
                                    "dataset_id": "dlp_results",
                                    "table_id": "findings"
                                }
                            }
                        }
                    }]
                }
            }
        }
    )
    
    return job_trigger.name
```

```bash
# gcloud commands for job triggers
gcloud dlp job-triggers list --project=my-project

gcloud dlp job-triggers describe TRIGGER_ID --project=my-project

gcloud dlp job-triggers delete TRIGGER_ID --project=my-project
```

---

## Data Profiles

### Overview

Data Profiles provide automatic, continuous discovery and classification of sensitive data across your organization.

### Configuration

```bash
# Enable data profiles at organization level
gcloud dlp discovery-configs create \
    --project=my-project \
    --location=global \
    --org-config='{
        "projectId": "my-project",
        "inspectTemplates": ["projects/my-project/inspectTemplates/pii-template"],
        "tableProfiles": {
            "dataProfileTypes": ["COLUMN_DATA_PROFILE", "TABLE_DATA_PROFILE"]
        }
    }'
```

### Scanning Targets

| Target | Description |
|--------|-------------|
| **BigQuery** | Tables and views |
| **Cloud Storage** | Files and objects |
| **Datastore** | Entities |

### Profile Levels

- **Project Profile**: Overall project statistics
- **Table/Bucket Profile**: Per-resource statistics
- **Column/Field Profile**: Per-column sensitivity

---

## Risk Analysis

### K-Anonymity

```python
def analyze_k_anonymity(project_id, dataset_id, table_id):
    """Analyze k-anonymity risk."""
    client = dlp_v2.DlpServiceClient()
    
    risk_job = client.create_dlp_job(
        request={
            "parent": f"projects/{project_id}",
            "risk_job": {
                "source_table": {
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "table_id": table_id
                },
                "privacy_metric": {
                    "k_anonymity_config": {
                        "quasi_ids": [
                            {"name": "zip_code"},
                            {"name": "age"},
                            {"name": "gender"}
                        ]
                    }
                },
                "actions": [{
                    "save_findings": {
                        "output_config": {
                            "table": {
                                "project_id": project_id,
                                "dataset_id": "dlp_results",
                                "table_id": "k_anonymity_results"
                            }
                        }
                    }
                }]
            }
        }
    )
    
    return risk_job.name
```

### L-Diversity

```python
def analyze_l_diversity(project_id, dataset_id, table_id):
    """Analyze l-diversity risk."""
    client = dlp_v2.DlpServiceClient()
    
    risk_job = client.create_dlp_job(
        request={
            "parent": f"projects/{project_id}",
            "risk_job": {
                "source_table": {
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "table_id": table_id
                },
                "privacy_metric": {
                    "l_diversity_config": {
                        "quasi_ids": [
                            {"name": "zip_code"},
                            {"name": "age"}
                        ],
                        "sensitive_attribute": {"name": "diagnosis"}
                    }
                }
            }
        }
    )
    
    return risk_job.name
```

### Risk Analysis Types

| Type | Description | Use Case |
|------|-------------|----------|
| **K-Anonymity** | Minimum group size for quasi-identifiers | Basic re-identification risk |
| **L-Diversity** | Sensitive value diversity within groups | Attribute disclosure risk |
| **K-Map** | Re-identification via external data | External attack risk |
| **Delta Presence** | Membership inference risk | Data set membership disclosure |

---

## Integration with Other Services

### BigQuery Integration

```python
# De-identify BigQuery table
def deidentify_bigquery_table(project_id, source_table, dest_table):
    client = dlp_v2.DlpServiceClient()
    
    job = client.create_dlp_job(
        request={
            "parent": f"projects/{project_id}",
            "inspect_job": {
                "storage_config": {
                    "big_query_options": {
                        "table_reference": source_table
                    }
                },
                "inspect_config": {
                    "info_types": [{"name": "EMAIL_ADDRESS"}]
                },
                "actions": [{
                    "deidentify": {
                        "transformation_config": {
                            "deidentify_template": "projects/p/deidentifyTemplates/t"
                        },
                        "transformation_details_storage_config": {
                            "table": dest_table
                        }
                    }
                }]
            }
        }
    )
    
    return job.name
```

### Dataflow Integration

```python
# DLP transform in Dataflow pipeline
import apache_beam as beam
from apache_beam.ml.gcp import dlp

def run_pipeline():
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | "Read" >> beam.io.ReadFromText("gs://input/*.csv")
            | "Inspect" >> dlp.InspectForDetails(
                project="my-project",
                inspect_config={
                    "info_types": [
                        {"name": "EMAIL_ADDRESS"},
                        {"name": "PHONE_NUMBER"}
                    ]
                }
            )
            | "Deidentify" >> dlp.DeidentifyText(
                project="my-project",
                deidentify_config={
                    "info_type_transformations": {
                        "transformations": [{
                            "primitive_transformation": {
                                "character_mask_config": {
                                    "masking_character": "*"
                                }
                            }
                        }]
                    }
                }
            )
            | "Write" >> beam.io.WriteToText("gs://output/deidentified")
        )
```

### Pub/Sub Integration

```python
# DLP inspection with Pub/Sub notification
def create_job_with_pubsub(project_id, bucket_name, topic_name):
    client = dlp_v2.DlpServiceClient()
    
    job = client.create_dlp_job(
        request={
            "parent": f"projects/{project_id}",
            "inspect_job": {
                "storage_config": {
                    "cloud_storage_options": {
                        "file_set": {"url": f"gs://{bucket_name}/**"}
                    }
                },
                "inspect_config": {
                    "info_types": [{"name": "CREDIT_CARD_NUMBER"}],
                    "min_likelihood": dlp_v2.Likelihood.LIKELY
                },
                "actions": [
                    {
                        "pub_sub": {
                            "topic": f"projects/{project_id}/topics/{topic_name}"
                        }
                    },
                    {
                        "publish_findings_to_cloud_data_catalog": {}
                    }
                ]
            }
        }
    )
    
    return job.name
```

---

## Security and IAM

### IAM Roles

| Role | Description |
|------|-------------|
| `roles/dlp.admin` | Full DLP access |
| `roles/dlp.user` | Run inspections, create templates |
| `roles/dlp.reader` | View configurations and results |
| `roles/dlp.jobsEditor` | Create and manage jobs |
| `roles/dlp.jobsReader` | View job results |
| `roles/dlp.storedInfoTypesEditor` | Manage stored InfoTypes |

### Service Account Configuration

```bash
# Create service account for DLP
gcloud iam service-accounts create dlp-service \
    --display-name="DLP Service Account"

# Grant DLP permissions
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:dlp-service@my-project.iam.gserviceaccount.com" \
    --role="roles/dlp.user"

# Grant access to source data
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:dlp-service@my-project.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

# Grant access to write results
gcloud projects add-iam-policy-binding my-project \
    --member="serviceAccount:dlp-service@my-project.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"
```

### VPC Service Controls

```yaml
# Include DLP in service perimeter
accessLevel:
  resources:
    - "//dlp.googleapis.com"
    - "//bigquery.googleapis.com"
    - "//storage.googleapis.com"
```

---

## Best Practices

### InfoType Selection

1. **Start broad, refine later**: Begin with common InfoTypes, add custom as needed
2. **Use likelihood thresholds**: Filter false positives with minimum likelihood
3. **Combine with context**: Use hotword rules to improve accuracy

### De-identification Strategy

| Data Use | Recommended Technique |
|----------|----------------------|
| Analytics (no re-identification needed) | Masking, Redaction |
| Testing (need realistic data) | FPE, Bucketing |
| Research (may need to re-link) | Tokenization with key |
| Compliance (audit trail) | Deterministic encryption |

### Performance Optimization

```python
# Batch processing for efficiency
def batch_inspect(project_id, content_items):
    """Inspect multiple items in one request."""
    client = dlp_v2.DlpServiceClient()
    
    items = [{"value": item} for item in content_items]
    
    response = client.inspect_content(
        request={
            "parent": f"projects/{project_id}",
            "inspect_config": {
                "info_types": [{"name": "EMAIL_ADDRESS"}],
                "min_likelihood": dlp_v2.Likelihood.LIKELY
            },
            "item": {"table": {"rows": [{"values": items}]}}
        }
    )
    
    return response.result.findings
```

### Cost Optimization

| Strategy | Implementation |
|----------|----------------|
| Use sampling | `rows_limit` or `files_limit_percent` |
| Limit InfoTypes | Only scan for needed types |
| Use templates | Reuse configurations |
| Schedule off-peak | Run jobs during low-usage periods |

---

## ACE Exam Focus

### Key Concepts for ACE

1. **InfoTypes**: Know common built-in types (EMAIL, SSN, CREDIT_CARD)
2. **Basic Inspection**: Inline content inspection
3. **Simple De-identification**: Masking and redaction
4. **Job Triggers**: Understand scheduled scanning
5. **IAM Roles**: Know basic DLP roles

### Sample ACE Questions

**Q1:** Your company needs to find all email addresses in a Cloud Storage bucket before migration. What should you use?
- **A:** Create a DLP inspection job with `EMAIL_ADDRESS` InfoType and Cloud Storage as the source.

**Q2:** How do you mask credit card numbers while keeping the last 4 digits visible?
- **A:** Use `character_mask_config` with `reverse_order: true` and `number_to_mask: 12`

**Q3:** Which DLP technique removes sensitive data completely?
- **A:** Redaction (`redact_config`)

### ACE gcloud Commands

```bash
# List InfoTypes
gcloud dlp info-types list

# Create inspection job
gcloud dlp jobs create \
    --project=my-project \
    --storage-cloud-storage-url="gs://bucket/**" \
    --info-types="EMAIL_ADDRESS,CREDIT_CARD_NUMBER"

# List jobs
gcloud dlp jobs list --project=my-project

# List templates
gcloud dlp templates list --project=my-project
```

---

## PCA Exam Focus

### Architecture Decision Framework

#### When to Use DLP

| Scenario | DLP Feature |
|----------|-------------|
| Data discovery | Inspection jobs, Data profiles |
| Compliance reporting | Scheduled scans, BigQuery output |
| Data anonymization | De-identification templates |
| Real-time protection | Content API integration |
| Risk assessment | K-anonymity, L-diversity analysis |

### Sample PCA Questions

**Q1:** Design a data governance architecture for a healthcare company that needs to:
- Discover PHI across 500+ BigQuery tables
- De-identify data for analytics
- Maintain audit trail for compliance

**A:**
- **Discovery**: Data Profiles at organization level
- **Classification**: Custom InfoTypes for healthcare codes + built-in PHI types
- **De-identification**: 
  - Deterministic encryption for linkable fields (patient_id)
  - Date shifting for dates (preserving relationships)
  - Bucketing for ages
- **Audit**: 
  - Save findings to BigQuery
  - Publish to Data Catalog
  - Cloud Audit Logs for all DLP operations

**Q2:** A financial services company needs to process customer data for ML while protecting PII. How should they design the pipeline?

**A:**
- **Ingestion**: Dataflow pipeline with DLP transform
- **De-identification**:
  - FPE for account numbers (maintain format for validation)
  - Tokenization for SSN (reversible with key in KMS)
  - Masking for names (non-reversible)
- **Storage**: De-identified data in BigQuery
- **Key Management**: Cloud KMS with separate keys per data type
- **Access Control**: Column-level security in BigQuery

**Q3:** How do you ensure de-identified data meets k=5 anonymity requirement?

**A:**
1. Run k-anonymity risk analysis with quasi-identifiers
2. Review results for groups with k < 5
3. Apply additional generalization:
   - Increase bucketing ranges for ages
   - Reduce location granularity (city → state)
4. Re-run analysis until k ≥ 5 achieved

### Multi-Cloud DLP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DLP ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│   │   Cloud     │     │  BigQuery   │     │  External   │  │
│   │   Storage   │     │             │     │   Sources   │  │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘  │
│          │                   │                   │          │
│          └───────────────────┼───────────────────┘          │
│                              │                               │
│                              ▼                               │
│                    ┌─────────────────┐                      │
│                    │   CLOUD DLP     │                      │
│                    │  • Inspection   │                      │
│                    │  • De-ID        │                      │
│                    │  • Risk Analysis│                      │
│                    └────────┬────────┘                      │
│                             │                                │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│   ┌──────────┐       ┌──────────┐       ┌──────────┐      │
│   │ BigQuery │       │ Data     │       │ Pub/Sub  │      │
│   │ Findings │       │ Catalog  │       │ Alerts   │      │
│   └──────────┘       └──────────┘       └──────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

### DLP Capabilities

| Capability | ACE Focus | PCA Focus |
|------------|-----------|-----------|
| Inspection | Basic InfoTypes | Custom types, templates |
| De-identification | Masking, redaction | FPE, tokenization, keys |
| Risk Analysis | Awareness | K-anonymity, L-diversity |
| Data Profiles | Awareness | Organization-wide design |
| Integration | Basic setup | Architecture patterns |

### Key Takeaways

| Topic | ACE | PCA |
|-------|-----|-----|
| InfoTypes | Built-in types | Custom + stored types |
| De-ID | Simple transforms | Crypto, keys, reversibility |
| Jobs | Single scans | Scheduled, templates |
| Risk | Awareness | Implementation |
| Integration | Basic | Multi-service architecture |
