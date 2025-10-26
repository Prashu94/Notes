# 📚 Complete Module Index

Quick navigation to all modules and resources in this comprehensive Kubernetes CKA/CKAD guide.

---

## 🎯 Getting Started

- **[Main README](./README.md)** - Overview, certification info, module structure
- **[Getting Started Guide](./GETTING-STARTED.md)** - How to use this repository effectively
- **[8-Week Study Plan](./STUDY-PLAN.md)** - Structured learning path
- **[Exam Tips & Tricks](./EXAM-TIPS.md)** - Essential exam strategies
- **[kubectl Cheat Sheet](./kubectl-cheat-sheet.md)** - Quick command reference

---

## 📖 Core Modules

### Module 01: Kubernetes Architecture & Fundamentals
**Path**: `01-kubernetes-architecture/`
- ✅ **[Theory](./01-kubernetes-architecture/README.md)** - Complete
  - Control plane components
  - Worker node components
  - Kubernetes API
  - Object model
- 📁 **[Examples](./01-kubernetes-architecture/examples/)** - Practical demos
- 📝 **[Exercises](./01-kubernetes-architecture/exercises/exercises.md)** - 15 exercises
- ✅ **[Solutions](./01-kubernetes-architecture/exercises/solutions.md)** - Complete

**Focus**: Architecture, components, API
**CKA Weight**: 5% | **CKAD Weight**: 5%
**Study Time**: 6-8 hours

---

### Module 02: Cluster Installation & Configuration
**Path**: `02-cluster-installation/`
- ✅ **[Theory](./02-cluster-installation/README.md)** - Complete
  - kubeadm installation
  - Cluster upgrades
  - etcd backup/restore
  - Certificate management
  - High Availability setup
- 📁 **[Examples](./02-cluster-installation/examples/)** - Installation scripts
- 📝 **[Exercises](./02-cluster-installation/exercises/)** - Hands-on practice

**Focus**: Cluster operations and maintenance
**CKA Weight**: 25% | **CKAD Weight**: 5%
**Study Time**: 12-15 hours (CKA), 2-3 hours (CKAD)

---

### Module 03: Workloads & Scheduling
**Path**: `03-workloads-scheduling/`
- ✅ **[Theory](./03-workloads-scheduling/README.md)** - Complete
  - Pods and lifecycle
  - Deployments
  - StatefulSets
  - DaemonSets
  - Jobs and CronJobs
  - Scheduling mechanisms
  - Resource management
- 📁 **[Examples](./03-workloads-scheduling/examples/)** - YAML templates
- 📝 **[Exercises](./03-workloads-scheduling/exercises/)** - Practice scenarios

**Focus**: Application workloads and pod management
**CKA Weight**: 15% | **CKAD Weight**: 40%
**Study Time**: 10-12 hours

---

### Module 04: Services & Networking
**Path**: `04-services-networking/`
- 📖 **[Theory](./04-services-networking/README.md)** - Planned
  - Service types (ClusterIP, NodePort, LoadBalancer)
  - Ingress and Ingress Controllers
  - Network Policies
  - DNS and service discovery
  - CNI plugins
- 📁 **[Examples](./04-services-networking/examples/)** - Network configurations
- 📝 **[Exercises](./04-services-networking/exercises/)** - Networking labs

**Focus**: Service exposure and network security
**CKA Weight**: 20% | **CKAD Weight**: 20%
**Study Time**: 10-12 hours

---

### Module 05: Storage
**Path**: `05-storage/`
- 📖 **[Theory](./05-storage/README.md)** - Planned
  - Volume types
  - Persistent Volumes (PV)
  - Persistent Volume Claims (PVC)
  - Storage Classes
  - StatefulSet storage
- 📁 **[Examples](./05-storage/examples/)** - Storage configurations
- 📝 **[Exercises](./05-storage/exercises/)** - Storage scenarios

**Focus**: Data persistence and volume management
**CKA Weight**: 10% | **CKAD Weight**: 15%
**Study Time**: 8-10 hours

---

### Module 06: Configuration & Secrets
**Path**: `06-configuration-secrets/`
- 📖 **[Theory](./06-configuration-secrets/README.md)** - Planned
  - ConfigMaps
  - Secrets
  - Environment variables
  - Volume mounts
  - Security best practices
- 📁 **[Examples](./06-configuration-secrets/examples/)** - Config templates
- 📝 **[Exercises](./06-configuration-secrets/exercises/)** - Configuration tasks

**Focus**: Application configuration management
**CKA Weight**: 5% | **CKAD Weight**: 25%
**Study Time**: 6-8 hours

---

### Module 07: Security
**Path**: `07-security/`
- 📖 **[Theory](./07-security/README.md)** - Planned
  - RBAC (Roles, RoleBindings)
  - ServiceAccounts
  - Security Contexts
  - Pod Security Standards
  - Network Policies (security aspect)
- 📁 **[Examples](./07-security/examples/)** - Security policies
- 📝 **[Exercises](./07-security/exercises/)** - Security scenarios

**Focus**: Cluster and application security
**CKA Weight**: 12% | **CKAD Weight**: 15%
**Study Time**: 10-12 hours

---

### Module 08: Observability & Debugging
**Path**: `08-observability-debugging/`
- 📖 **[Theory](./08-observability-debugging/README.md)** - Planned
  - Logging strategies
  - Resource metrics
  - Health probes (liveness, readiness, startup)
  - Troubleshooting workflows
  - Debugging techniques
- 📁 **[Examples](./08-observability-debugging/examples/)** - Monitoring configs
- 📝 **[Exercises](./08-observability-debugging/exercises/)** - Debug scenarios

**Focus**: Application and cluster monitoring
**CKA Weight**: 30% | **CKAD Weight**: 15%
**Study Time**: 10-12 hours

---

### Module 09: Cluster Maintenance
**Path**: `09-cluster-maintenance/`
- 📖 **[Theory](./09-cluster-maintenance/README.md)** - Planned
  - Node maintenance (drain, cordon)
  - Backup strategies
  - Restore procedures
  - Cluster upgrades (detailed)
  - etcd operations
- 📁 **[Examples](./09-cluster-maintenance/examples/)** - Maintenance scripts
- 📝 **[Exercises](./09-cluster-maintenance/exercises/)** - Maintenance tasks

**Focus**: Operational maintenance procedures
**CKA Weight**: 15% | **CKAD Weight**: 5%
**Study Time**: 8-10 hours (CKA), 2-3 hours (CKAD)

---

### Module 10: Application Lifecycle Management
**Path**: `10-application-lifecycle/`
- 📖 **[Theory](./10-application-lifecycle/README.md)** - Planned
  - Rolling updates
  - Rollback procedures
  - Scaling strategies
  - Self-healing mechanisms
  - Helm basics
- 📁 **[Examples](./10-application-lifecycle/examples/)** - Update strategies
- 📝 **[Exercises](./10-application-lifecycle/exercises/)** - Lifecycle tasks

**Focus**: Managing application updates and scaling
**CKA Weight**: 8% | **CKAD Weight**: 20%
**Study Time**: 8-10 hours

---

### Module 11: Advanced Topics
**Path**: `11-advanced-topics/`
- 📖 **[Theory](./11-advanced-topics/README.md)** - Planned
  - Custom Resource Definitions (CRDs)
  - Operators pattern
  - Admission Controllers
  - Advanced scheduling
  - Service Mesh basics
- 📁 **[Examples](./11-advanced-topics/examples/)** - Advanced configs
- 📝 **[Exercises](./11-advanced-topics/exercises/)** - Advanced scenarios

**Focus**: Advanced Kubernetes concepts
**CKA Weight**: Optional | **CKAD Weight**: Optional
**Study Time**: 6-8 hours (optional enrichment)

---

### Module 12: Practice Exams & Mock Scenarios
**Path**: `12-practice-exams/`
- ✅ **[CKA Practice Exam 1](./12-practice-exams/README.md)** - Complete (20 questions)
- 📝 **[CKA Practice Exam 2](./12-practice-exams/cka-exam-2.md)** - Planned
- 📝 **[CKA Practice Exam 3](./12-practice-exams/cka-exam-3.md)** - Planned
- 📝 **[CKAD Practice Exam 1](./12-practice-exams/ckad-exam-1.md)** - Planned
- 📝 **[CKAD Practice Exam 2](./12-practice-exams/ckad-exam-2.md)** - Planned

**Focus**: Timed practice under exam conditions
**Study Time**: 10-15 hours (multiple attempts)

---

## 📊 Study Paths by Certification

### CKA (Certified Kubernetes Administrator)

**Essential Modules** (in order):
1. ✅ Module 01 - Architecture (100%)
2. ✅ Module 02 - Installation (100%)
3. ✅ Module 03 - Workloads (70%)
4. Module 04 - Networking (100%)
5. Module 05 - Storage (80%)
6. Module 07 - Security (100%)
7. Module 08 - Observability (100%)
8. Module 09 - Maintenance (100%)
9. ✅ Module 12 - Practice Exams

**Total Study Time**: 80-100 hours over 6-8 weeks

**Exam Weight Distribution**:
- 25% - Cluster Architecture, Installation & Configuration
- 15% - Workloads & Scheduling
- 20% - Services & Networking
- 10% - Storage
- 30% - Troubleshooting

---

### CKAD (Certified Kubernetes Application Developer)

**Essential Modules** (in order):
1. Module 01 - Architecture (60%)
2. ✅ Module 03 - Workloads (100%)
3. Module 04 - Networking (80%)
4. Module 05 - Storage (100%)
5. Module 06 - Configuration (100%)
6. Module 07 - Security (70%)
7. Module 08 - Observability (100%)
8. Module 10 - App Lifecycle (100%)
9. Module 12 - Practice Exams

**Total Study Time**: 60-80 hours over 4-6 weeks

**Exam Weight Distribution**:
- 20% - Application Design and Build
- 20% - Application Deployment
- 15% - Application Observability and Maintenance
- 25% - Application Environment, Configuration and Security
- 20% - Services & Networking

---

## 🗓️ Recommended Study Sequences

### Complete Beginner (No Kubernetes Experience)
```
Week 1: Module 01 (100%)
Week 2: Module 03 (100%)
Week 3: Module 04 (100%)
Week 4: Module 05, 06 (100%)
Week 5: Module 07, 08 (100%)
Week 6: Module 02, 09 (CKA) or Module 10 (CKAD)
Week 7: Module 10 or Review
Week 8: Module 12 - Practice Exams
```

### Intermediate (Some K8s Experience)
```
Week 1: Modules 01-03 (Review + Installation)
Week 2: Modules 04-05 (Networking, Storage)
Week 3: Modules 06-07 (Config, Security)
Week 4: Modules 08-09 (Observability, Maintenance)
Week 5-6: Module 12 (Multiple practice exams)
```

### Advanced (Experienced, Need Certification)
```
Week 1: Modules 01-05 (Quick review)
Week 2: Modules 06-10 (Deep dive on weak areas)
Week 3: Module 12 (Practice exams, speed drills)
```

---

## 📈 Progress Tracking

### Module Completion Status

- ✅ Complete with examples and exercises
- 📖 Theory available
- 📝 Planned/In progress

| Module | Status | Theory | Examples | Exercises | Solutions |
|--------|--------|--------|----------|-----------|-----------|
| 01 - Architecture | ✅ | ✅ | ✅ | ✅ | ✅ |
| 02 - Installation | ✅ | ✅ | 📝 | 📝 | 📝 |
| 03 - Workloads | ✅ | ✅ | 📝 | 📝 | 📝 |
| 04 - Networking | 📖 | 📝 | 📝 | 📝 | 📝 |
| 05 - Storage | 📖 | 📝 | 📝 | 📝 | 📝 |
| 06 - Configuration | 📖 | 📝 | 📝 | 📝 | 📝 |
| 07 - Security | 📖 | 📝 | 📝 | 📝 | 📝 |
| 08 - Observability | 📖 | 📝 | 📝 | 📝 | 📝 |
| 09 - Maintenance | 📖 | 📝 | 📝 | 📝 | 📝 |
| 10 - App Lifecycle | 📖 | 📝 | 📝 | 📝 | 📝 |
| 11 - Advanced | 📖 | 📝 | 📝 | 📝 | 📝 |
| 12 - Practice Exams | ✅ | ✅ | N/A | N/A | ✅ |

---

## 🔍 Quick Search

### By Topic

**Pods & Containers**:
- Module 01 (Basics)
- Module 03 (Workloads)
- Module 06 (Configuration)
- Module 08 (Debugging)

**Cluster Operations**:
- Module 01 (Architecture)
- Module 02 (Installation)
- Module 09 (Maintenance)

**Networking**:
- Module 04 (Services, Ingress)
- Module 07 (Network Policies)

**Storage**:
- Module 05 (Volumes, PV, PVC)

**Security**:
- Module 06 (Secrets)
- Module 07 (RBAC, Security Contexts)

**Troubleshooting**:
- Module 08 (Observability)
- Module 12 (Practice scenarios)

---

## 📝 Additional Resources

### Essential Files
- ✅ [README.md](./README.md) - Start here
- ✅ [GETTING-STARTED.md](./GETTING-STARTED.md) - Usage guide
- ✅ [STUDY-PLAN.md](./STUDY-PLAN.md) - 8-week plan
- ✅ [EXAM-TIPS.md](./EXAM-TIPS.md) - Exam strategies
- ✅ [kubectl-cheat-sheet.md](./kubectl-cheat-sheet.md) - Command reference

### External Resources
- [kubernetes.io/docs](https://kubernetes.io/docs/) - Official docs
- [killer.sh](https://killer.sh/) - Practice exams (with purchase)
- [kubernetes.io/docs/reference/kubectl/cheatsheet/](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) - Official cheat sheet

---

## 🎯 Next Steps

### New to This Guide?
1. Read [README.md](./README.md)
2. Review [GETTING-STARTED.md](./GETTING-STARTED.md)
3. Start [Module 01](./01-kubernetes-architecture/README.md)

### Ready to Study?
1. Choose your certification path (CKA/CKAD/Both)
2. Follow [STUDY-PLAN.md](./STUDY-PLAN.md)
3. Complete modules sequentially
4. Practice with Module 12 exams

### Almost Ready for Exam?
1. Review [EXAM-TIPS.md](./EXAM-TIPS.md)
2. Complete all practice exams in Module 12
3. Achieve >70% on mock exams
4. Book your certification!

---

## 📞 Support & Contribution

### Need Help?
- Review module theory and examples
- Check [kubectl-cheat-sheet.md](./kubectl-cheat-sheet.md)
- Search kubernetes.io documentation
- Ask on Kubernetes Slack or Reddit r/kubernetes

### Want to Contribute?
- Report errors via issues
- Suggest improvements
- Submit pull requests
- Share your success story!

---

## ✅ Certification Checklist

**Before Scheduling Exam**:
- [ ] Completed all relevant modules
- [ ] Solved 100+ exercises
- [ ] Completed 3+ mock exams
- [ ] Scoring >70% consistently
- [ ] Reviewed exam tips

**Technical Preparation**:
- [ ] Comfortable with kubectl
- [ ] Can create resources in <5 min
- [ ] Know troubleshooting workflows
- [ ] Practiced context switching

**Mental Preparation**:
- [ ] Well-rested
- [ ] Confident in abilities
- [ ] Familiar with exam format
- [ ] Ready to succeed!

---

**Last Updated**: October 2025
**Kubernetes Version**: 1.31+
**Repository Status**: Active Development

**Good luck with your Kubernetes certification journey!** 🚀
