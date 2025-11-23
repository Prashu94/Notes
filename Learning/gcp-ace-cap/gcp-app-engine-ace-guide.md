# Google App Engine - Associate Cloud Engineer (ACE) Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [App Engine Environments](#app-engine-environments)
4. [Deployment & Configuration](#deployment--configuration)
5. [Managing Services & Versions](#managing-services--versions)
6. [Scaling & Performance](#scaling--performance)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security & IAM](#security--iam)
9. [ACE Exam Tips](#ace-exam-tips)

---

## Overview

Google App Engine is a fully managed Platform as a Service (PaaS) that allows you to build and deploy applications without managing the underlying infrastructure. For the ACE exam, you need to know how to deploy, manage versions, and configure scaling.

**Key Features:**
- **Serverless:** No server management.
- **Auto-scaling:** Scales from zero to millions of requests.
- **Support:** Multiple languages (Go, Java, Node.js, PHP, Python, Ruby).

---

## Core Concepts

### Application Hierarchy
- **Project:** Contains one App Engine Application.
- **Service:** Microservices (e.g., `default`, `frontend`, `backend`).
- **Version:** Immutable code deployment (e.g., `v1`, `v2`).
- **Instance:** The container running the code.

### Services
- **Default Service:** Every app has a `default` service.
- **Addressing:** `https://[SERVICE_ID]-dot-[PROJECT_ID].appspot.com`.

---

## App Engine Environments

You must understand the differences to choose the right environment for a given scenario.

### Standard Environment
Ideal for applications that need rapid scaling and low cost.
- **Startup:** Seconds.
- **Pricing:** Pay for instance hours; scales to 0 (free).
- **Access:** Sandbox environment; no local file system write access (except `/tmp`).
- **Network:** No background processes (limited); outbound requests via specific services.
- **Languages:** Specific versions of Python, Java, Node.js, Go, PHP, Ruby.

### Flexible Environment
Ideal for applications running in Docker containers or requiring specific system libraries.
- **Startup:** Minutes.
- **Pricing:** Pay for vCPU/RAM; minimum 1 instance always running.
- **Access:** Docker container; access to background processes and local disk.
- **Network:** Computes Engine based; supports VPC networking.
- **Languages:** Any (via Dockerfile).

**Comparison Table:**

| Feature | Standard | Flexible |
|---------|----------|----------|
| **Startup** | Seconds | Minutes |
| **Scale to Zero** | Yes | No |
| **SSH Access** | No | Yes |
| **Custom Runtime** | No (Limited) | Yes (Docker) |
| **Background Processes** | No | Yes |

---

## Deployment & Configuration

### The `app.yaml` Configuration
The blueprint for your service.

**Standard Example:**
```yaml
runtime: python39
service: default
handlers:
  - url: /.*
    script: auto
```

**Flexible Example:**
```yaml
runtime: custom
env: flex
manual_scaling:
  instances: 1
```

### Deploying with `gcloud`

**Basic Deployment:**
```bash
gcloud app deploy
```
*Deploys `app.yaml` to the current project.*

**Deploy Specific Service/Config:**
```bash
gcloud app deploy service1.yaml service2.yaml dispatch.yaml
```

**Deploy without Traffic Promotion:**
```bash
gcloud app deploy --no-promote
```
*Deploys new version but keeps traffic on the old version.*

**Deploy to Specific Version ID:**
```bash
gcloud app deploy --version=v1
```

---

## Managing Services & Versions

App Engine follows a hierarchy: **Application -> Service -> Version -> Instance**.

### Traffic Splitting
Crucial for A/B testing and canary deployments.

**Split traffic between versions:**
```bash
gcloud app services set-traffic default --splits v1=0.5,v2=0.5
```
*Routes 50% of traffic to v1 and 50% to v2.*

**Migrate all traffic:**
```bash
gcloud app services set-traffic default --splits v2=1.0
```

**Routing Methods:**
- **IP Address:** Default. Sticky by IP.
- **Cookie:** Sticky by user session.
- **Random:** Random distribution.

### Managing Versions
- **List versions:** `gcloud app versions list`
- **Delete a version:** `gcloud app versions delete [VERSION_ID]`
- **Start/Stop versions:** `gcloud app versions start [VERSION_ID]` / `stop`

---

## Scaling & Performance

### Automatic Scaling (Standard)
Scales based on request rate, response latency, and CPU.
Default for Standard environment.
```yaml
automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 0
  max_instances: 100
  max_concurrent_requests: 50
```

### Basic Scaling (Standard)
Creates instances when requests are received, shuts them down when idle.
```yaml
basic_scaling:
  max_instances: 10
  idle_timeout: 10m
```

### Manual Scaling (Standard & Flex)
Fixed number of instances.
```yaml
manual_scaling:
  instances: 5
```

---

## Monitoring & Logging

### Viewing Logs
- **Console:** Cloud Logging.
- **CLI:**
  ```bash
  gcloud app logs read
  gcloud app logs tail
  ```

### Debugging
- **Standard:** You cannot SSH into instances. Use Cloud Logging and Cloud Trace.
- **Flexible:** You can SSH into instances for debugging.
  ```bash
  gcloud app instances ssh [INSTANCE_ID] --service=[SERVICE_ID]
  ```

---

## Security & IAM

### IAM Roles
- **App Engine Admin:** Full control.
- **App Engine Deployer:** Can deploy versions.
- **App Engine Service Admin:** Can set traffic splits.

### Firewall Rules
Control access to your app.
```bash
gcloud app firewall-rules create 100 --action=ALLOW --source-range=192.0.2.1/32
```

---

## ACE Exam Tips

1.  **Deployment Commands:** Memorize `gcloud app deploy`. Know that it deploys `app.yaml` by default.
2.  **Traffic Splitting:** You use `gcloud app services set-traffic` to move traffic, not `gcloud app deploy` (unless you use `--promote`, which is default).
3.  **Standard vs Flex:**
    -   "Docker" -> **Flexible**
    -   "Custom Binary" -> **Flexible**
    -   "Scale to Zero" -> **Standard**
    -   "Immediate Scaling" -> **Standard**
4.  **Config Files:** `cron.yaml` is for scheduled tasks. `dispatch.yaml` is for routing rules.
5.  **Versions:** You can have multiple versions running, but only one receives traffic by default unless split.
