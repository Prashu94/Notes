# Kubernetes CKA & CKAD Certification Guide

## 📚 Comprehensive Guide for Certified Kubernetes Administrator (CKA) and Certified Kubernetes Application Developer (CKAD)

This repository contains a complete guide to help you prepare for both CKA and CKAD certifications with detailed theory, practical examples, and exam-level exercises.

## 🎯 Certification Overview

### CKA (Certified Kubernetes Administrator)
- **Focus**: Cluster administration, troubleshooting, and management
- **Duration**: 2 hours
- **Passing Score**: 66%
- **Format**: Performance-based exam in a command-line environment

### CKAD (Certified Kubernetes Application Developer)
- **Focus**: Application deployment, configuration, and debugging
- **Duration**: 2 hours
- **Passing Score**: 66%
- **Format**: Performance-based exam in a command-line environment

## 📖 Module Structure

### Core Modules

1. **[Module 01: Kubernetes Architecture & Fundamentals](./01-kubernetes-architecture/README.md)**
   - Kubernetes components and architecture
   - Control plane and worker nodes
   - Kubernetes objects and API

2. **[Module 02: Cluster Installation & Configuration](./02-cluster-installation/README.md)**
   - kubeadm cluster setup
   - Cluster upgrade procedures
   - High availability clusters

3. **[Module 03: Workloads & Scheduling](./03-workloads-scheduling/README.md)**
   - Pods, ReplicaSets, Deployments
   - DaemonSets, StatefulSets, Jobs, CronJobs
   - Pod scheduling and resource management

4. **[Module 04: Services & Networking](./04-services-networking/README.md)**
   - Services (ClusterIP, NodePort, LoadBalancer)
   - Ingress and Ingress Controllers
   - Network Policies
   - DNS and Service Discovery

5. **[Module 05: Storage](./05-storage/README.md)**
   - Volumes and Persistent Volumes
   - Persistent Volume Claims
   - Storage Classes
   - StatefulSet storage

6. **[Module 06: Configuration & Secrets](./06-configuration-secrets/README.md)**
   - ConfigMaps
   - Secrets
   - Environment variables
   - Volume mounts

7. **[Module 07: Security](./07-security/README.md)**
   - RBAC (Role-Based Access Control)
   - Service Accounts
   - Security Contexts
   - Pod Security Standards
   - Network Policies

8. **[Module 08: Observability & Debugging](./08-observability-debugging/README.md)**
   - Logging and monitoring
   - Resource metrics
   - Liveness and readiness probes
   - Troubleshooting techniques

9. **[Module 09: Cluster Maintenance](./09-cluster-maintenance/README.md)**
   - Node maintenance
   - Backup and restore
   - Cluster upgrades
   - etcd management

10. **[Module 10: Application Lifecycle Management](./10-application-lifecycle/README.md)**
    - Rolling updates and rollbacks
    - Application scaling
    - Self-healing applications
    - Helm basics

11. **[Module 11: Advanced Topics](./11-advanced-topics/README.md)**
    - Custom Resource Definitions (CRDs)
    - Operators
    - Admission Controllers
    - Advanced scheduling

12. **[Module 12: Practice Scenarios & Mock Exams](./12-practice-exams/README.md)**
    - CKA practice questions
    - CKAD practice questions
    - Mock exam scenarios
    - Time-bound challenges

## 🚀 Getting Started

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install minikube (for local practice)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube

# Install kind (Kubernetes in Docker)
brew install kind

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
```

### Setting Up Practice Environment
```bash
# Start minikube cluster
minikube start --cpus=4 --memory=8192

# Verify cluster
kubectl cluster-info
kubectl get nodes

# Enable useful addons
minikube addons enable metrics-server
minikube addons enable ingress
```

## 💡 Study Tips

### For CKA
1. **Focus on cluster operations**: Learn kubeadm, etcd backup/restore, upgrades
2. **Master troubleshooting**: Practice debugging failed pods, services, and nodes
3. **Understand networking**: Deep dive into CNI, network policies, and DNS
4. **Practice RBAC**: Create roles, role bindings, and service accounts

### For CKAD
1. **Speed matters**: Practice creating resources quickly using imperative commands
2. **Know the basics well**: Pods, deployments, services, configmaps, secrets
3. **Debug applications**: Learn to read logs, describe resources, and fix issues
4. **Resource limits**: Understand requests, limits, and quality of service

## 📝 Exam Tips

### Time Management
- **CKA**: ~17-20 questions in 2 hours (~6-7 min per question)
- **CKAD**: ~15-20 questions in 2 hours (~6-8 min per question)
- Skip difficult questions and return later
- Use imperative commands to save time

### Essential Commands & Shortcuts
```bash
# Set aliases (exam provides these)
alias k=kubectl
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kd='kubectl describe'
alias kl='kubectl logs'

# Set default namespace
kubectl config set-context --current --namespace=<namespace>

# Verify resource creation
kubectl get <resource> <name> -o yaml

# Use dry-run for YAML generation
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
```

### Allowed Resources During Exam
- kubernetes.io/docs
- github.com/kubernetes
- kubernetes.io/blog

### Exam Environment
- Ubuntu terminal with kubectl pre-installed
- Multiple clusters (you'll switch between them)
- Copy-paste works from documentation
- No autocomplete for kubectl (practice without it!)

## 🎓 CKA vs CKAD Domains

### CKA Exam Domains (100%)
- **25%** - Cluster Architecture, Installation & Configuration
- **15%** - Workloads & Scheduling
- **20%** - Services & Networking
- **10%** - Storage
- **30%** - Troubleshooting

### CKAD Exam Domains (100%)
- **20%** - Application Design and Build
- **20%** - Application Deployment
- **15%** - Application Observability and Maintenance
- **25%** - Application Environment, Configuration and Security
- **20%** - Services & Networking

## 📚 Recommended Resources

### Official Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes API Reference](https://kubernetes.io/docs/reference/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### Practice Platforms
- [Killer.sh](https://killer.sh/) - Official CKA/CKAD practice exams
- [KodeKloud](https://kodekloud.com/) - Interactive labs
- [Play with Kubernetes](https://labs.play-with-k8s.com/)

### Books
- "Kubernetes Up & Running" by Kelsey Hightower
- "Kubernetes in Action" by Marko Lukša
- "The Kubernetes Book" by Nigel Poulton

## 🔥 Quick Start Practice

```bash
# Navigate to any module
cd 01-kubernetes-architecture

# Each module contains:
# - README.md: Theory and concepts
# - examples/: Practical YAML examples
# - exercises/: Practice problems
# - solutions/: Exercise solutions
```

## 📊 Progress Tracking

Track your preparation progress:
- [ ] Complete all 11 core modules
- [ ] Solve all module exercises
- [ ] Complete 3 full mock exams
- [ ] Practice speed drills (create resources under 2 minutes)
- [ ] Review troubleshooting scenarios
- [ ] Master kubectl commands and shortcuts

## 🤝 Contributing

Feel free to contribute improvements, additional examples, or corrections via pull requests.

## 📄 License

This guide is created for educational purposes. Kubernetes is a trademark of the Linux Foundation.

## ⭐ Good Luck!

Remember: **Practice, Practice, Practice!** The exam is hands-on, so theoretical knowledge alone won't be enough. Set up a cluster and work through every example and exercise.

---

*Last Updated: October 2025*
*Aligned with CKA/CKAD Exam Version 1.31*
