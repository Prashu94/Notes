# Kubernetes CKA/CKAD Study Plan

## 📅 8-Week Comprehensive Study Plan

This structured study plan will help you prepare for both CKA and CKAD certifications systematically.

---

## 🎯 Study Approach

### Weekly Structure
- **Monday-Thursday**: Theory + Hands-on Labs (2-3 hours/day)
- **Friday**: Review + Practice Exercises (2-3 hours)
- **Saturday**: Mock Exam or Project (3-4 hours)
- **Sunday**: Rest or light review

### Learning Method
1. **Read**: Study module theory (30-45 min)
2. **Practice**: Run all examples (45-60 min)
3. **Exercise**: Complete module exercises (60-90 min)
4. **Review**: Document learnings and errors (15-30 min)

---

## 📚 Week 1: Kubernetes Fundamentals

### Goals
- Understand Kubernetes architecture
- Learn core concepts and objects
- Master kubectl basics

### Day 1: Architecture & Components
- [ ] Study Module 01: Kubernetes Architecture
- [ ] Set up local Kubernetes cluster (minikube/kind)
- [ ] Explore control plane components
- [ ] Practice: Inspect cluster components

**Exercises**:
```bash
- List all system pods
- Check component health
- Explore API resources
- Practice kubectl explain
```

### Day 2: Kubernetes Objects & API
- [ ] Understanding Pods
- [ ] Namespaces and resource organization
- [ ] Labels and selectors
- [ ] Practice: Create and manage pods

**Exercises**:
```bash
- Create pods imperatively
- Work with namespaces
- Practice label selectors
- Inspect pod specifications
```

### Day 3: Workloads - Deployments
- [ ] Study Module 03: Deployments
- [ ] ReplicaSets and replica management
- [ ] Deployment strategies
- [ ] Practice: Create and manage deployments

**Exercises**:
```bash
- Create deployments
- Scale applications
- Update container images
- Rollback deployments
```

### Day 4: Workloads - Other Controllers
- [ ] DaemonSets
- [ ] StatefulSets
- [ ] Jobs and CronJobs
- [ ] Practice: Different workload types

**Exercises**:
```bash
- Create DaemonSet
- Deploy StatefulSet application
- Schedule batch jobs
- Configure CronJobs
```

### Day 5: Week 1 Review
- [ ] Complete all Module 01 exercises
- [ ] Complete all Module 03 exercises
- [ ] Create personal cheat sheet
- [ ] Practice speed drills (create resources quickly)

### Weekend Project: Multi-Tier Application
Deploy a complete application stack:
- Frontend deployment (3 replicas)
- Backend deployment (2 replicas)
- Database StatefulSet (1 replica)
- Use appropriate labels
- Document your approach

**Time Target**: Complete in 45 minutes

---

## 🌐 Week 2: Services & Networking

### Goals
- Master Service types
- Understand Kubernetes networking
- Implement network policies
- Configure Ingress

### Day 1: Services
- [ ] Study Module 04: Services & Networking
- [ ] ClusterIP, NodePort, LoadBalancer
- [ ] Service discovery and DNS
- [ ] Practice: Expose applications

**Exercises**:
```bash
- Create different service types
- Test service connectivity
- Explore DNS resolution
- Debug service issues
```

### Day 2: Networking Fundamentals
- [ ] Pod networking model
- [ ] CNI plugins (Calico, Flannel, Weave)
- [ ] Network troubleshooting
- [ ] Practice: Network debugging

**Exercises**:
```bash
- Test pod-to-pod communication
- Verify DNS functionality
- Explore network interfaces
- Debug connectivity issues
```

### Day 3: Network Policies
- [ ] Network policy concepts
- [ ] Ingress and egress rules
- [ ] Policy selectors
- [ ] Practice: Implement policies

**Exercises**:
```bash
- Create deny-all policy
- Allow specific traffic
- Test policy enforcement
- Troubleshoot network policies
```

### Day 4: Ingress Controllers
- [ ] Ingress concepts
- [ ] Ingress rules and paths
- [ ] TLS/SSL termination
- [ ] Practice: Configure Ingress

**Exercises**:
```bash
- Install Ingress controller
- Create Ingress resources
- Configure host-based routing
- Configure path-based routing
```

### Day 5: Week 2 Review
- [ ] Complete all Module 04 exercises
- [ ] Practice service troubleshooting
- [ ] Test network policy scenarios
- [ ] Speed drill: Services and Ingress

### Weekend Project: Microservices Network
Deploy microservices architecture:
- 3 microservices (frontend, api, database)
- Services for each component
- Network policies restricting traffic
- Ingress for external access
- Document network flow

**Time Target**: Complete in 60 minutes

---

## 💾 Week 3: Storage & Configuration

### Goals
- Master persistent storage
- Understand volume types
- Configure applications with ConfigMaps
- Manage secrets securely

### Day 1: Volumes
- [ ] Study Module 05: Storage
- [ ] Volume types (emptyDir, hostPath, etc.)
- [ ] Persistent Volumes (PV)
- [ ] Persistent Volume Claims (PVC)
- [ ] Practice: Work with volumes

**Exercises**:
```bash
- Create various volume types
- Create PV and PVC
- Bind PVC to PV
- Use volumes in pods
```

### Day 2: Storage Classes
- [ ] Storage Classes
- [ ] Dynamic provisioning
- [ ] Volume expansion
- [ ] Practice: Dynamic storage

**Exercises**:
```bash
- Create StorageClass
- Use dynamic provisioning
- Expand volumes
- Test different access modes
```

### Day 3: ConfigMaps
- [ ] Study Module 06: Configuration
- [ ] ConfigMap creation methods
- [ ] Using ConfigMaps (env, volume)
- [ ] Practice: Application configuration

**Exercises**:
```bash
- Create ConfigMaps from literals
- Create from files
- Mount as environment variables
- Mount as volumes
```

### Day 4: Secrets
- [ ] Secret types
- [ ] Creating and using Secrets
- [ ] Security best practices
- [ ] Practice: Secret management

**Exercises**:
```bash
- Create generic secrets
- Create TLS secrets
- Use secrets in pods
- Update secrets safely
```

### Day 5: Week 3 Review
- [ ] Complete Module 05 exercises
- [ ] Complete Module 06 exercises
- [ ] Practice storage scenarios
- [ ] Speed drill: Storage and config

### Weekend Project: Stateful Application
Deploy WordPress with MySQL:
- MySQL StatefulSet with persistent storage
- WordPress Deployment
- Use ConfigMap for configuration
- Use Secret for passwords
- Expose via Service

**Time Target**: Complete in 60 minutes

---

## 🔐 Week 4: Security & RBAC

### Goals
- Understand Kubernetes security
- Master RBAC
- Configure security contexts
- Implement pod security

### Day 1: Authentication & Authorization
- [ ] Study Module 07: Security
- [ ] Authentication methods
- [ ] Authorization modes (RBAC, ABAC, etc.)
- [ ] Practice: User authentication

**Exercises**:
```bash
- Create user certificates
- Configure kubeconfig
- Test authentication
- Understand service accounts
```

### Day 2: RBAC Deep Dive
- [ ] Roles and ClusterRoles
- [ ] RoleBindings and ClusterRoleBindings
- [ ] ServiceAccounts
- [ ] Practice: RBAC configuration

**Exercises**:
```bash
- Create Roles and RoleBindings
- Create ClusterRoles
- Bind roles to ServiceAccounts
- Test permissions with kubectl auth can-i
```

### Day 3: Security Contexts
- [ ] Pod security contexts
- [ ] Container security contexts
- [ ] RunAsUser, RunAsGroup
- [ ] Practice: Security hardening

**Exercises**:
```bash
- Configure security contexts
- Run as non-root user
- Set filesystem group
- Test security constraints
```

### Day 4: Pod Security & Network Policies
- [ ] Pod Security Standards
- [ ] Pod Security Admission
- [ ] Network Policies (security aspect)
- [ ] Practice: Secure deployments

**Exercises**:
```bash
- Implement Pod Security Standards
- Create restrictive network policies
- Test security enforcement
- Audit security configurations
```

### Day 5: Week 4 Review
- [ ] Complete all Module 07 exercises
- [ ] Practice RBAC scenarios
- [ ] Security troubleshooting
- [ ] Speed drill: RBAC and security

### Weekend Project: Secure Multi-Tenant Application
Create secure environment:
- Multiple namespaces (tenants)
- ServiceAccount per tenant
- Roles with minimal permissions
- Network policies isolating tenants
- Resource quotas per namespace

**Time Target**: Complete in 75 minutes

---

## 🔧 Week 5: Cluster Operations (CKA Focus)

### Goals
- Install Kubernetes cluster
- Upgrade cluster safely
- Backup and restore etcd
- Manage certificates

### Day 1: Cluster Installation
- [ ] Study Module 02: Cluster Installation
- [ ] kubeadm installation
- [ ] Control plane setup
- [ ] Worker node joining
- [ ] Practice: Install cluster

**Exercises**:
```bash
- Install kubeadm, kubelet, kubectl
- Initialize control plane
- Install CNI plugin
- Join worker nodes
```

### Day 2: Cluster Upgrades
- [ ] Upgrade process
- [ ] Control plane upgrade
- [ ] Worker node upgrade
- [ ] Practice: Cluster upgrade

**Exercises**:
```bash
- Check available versions
- Upgrade control plane
- Upgrade worker nodes
- Verify upgrade success
```

### Day 3: etcd Management
- [ ] etcd architecture
- [ ] Backup procedures
- [ ] Restore procedures
- [ ] Practice: Backup/restore

**Exercises**:
```bash
- Create etcd snapshot
- Verify backup
- Restore from backup
- Automate backup script
```

### Day 4: Certificate Management
- [ ] Certificate locations
- [ ] Certificate expiry checking
- [ ] Certificate renewal
- [ ] Practice: Manage certificates

**Exercises**:
```bash
- Check certificate expiry
- Renew certificates
- Update kubeconfig
- Verify certificate chain
```

### Day 5: Week 5 Review
- [ ] Complete Module 02 exercises
- [ ] Practice upgrade scenarios
- [ ] Practice backup/restore
- [ ] Speed drill: Cluster operations

### Weekend Project: HA Cluster Setup
Set up high availability:
- 3 control plane nodes
- 2 worker nodes
- Load balancer for API server
- etcd backup automation
- Test failure scenarios

**Time Target**: Complete setup in 90 minutes

---

## 🔍 Week 6: Observability & Troubleshooting

### Goals
- Monitor cluster and applications
- Implement logging
- Configure probes
- Master troubleshooting

### Day 1: Monitoring
- [ ] Study Module 08: Observability
- [ ] Metrics Server
- [ ] Resource metrics
- [ ] kubectl top
- [ ] Practice: Monitor resources

**Exercises**:
```bash
- Install metrics server
- Check node metrics
- Check pod metrics
- Monitor resource usage
```

### Day 2: Logging
- [ ] Container logs
- [ ] Cluster-level logging
- [ ] Log aggregation
- [ ] Practice: Log management

**Exercises**:
```bash
- View container logs
- Stream logs
- Previous container logs
- Multi-container pod logs
```

### Day 3: Health Probes
- [ ] Liveness probes
- [ ] Readiness probes
- [ ] Startup probes
- [ ] Practice: Configure probes

**Exercises**:
```bash
- Configure HTTP probes
- Configure TCP probes
- Configure exec probes
- Test probe behavior
```

### Day 4: Troubleshooting
- [ ] Common issues
- [ ] Debugging techniques
- [ ] Events and logs
- [ ] Practice: Fix problems

**Exercises**:
```bash
- Debug image pull errors
- Fix CrashLoopBackOff
- Resolve scheduling issues
- Fix service connectivity
```

### Day 5: Week 6 Review
- [ ] Complete Module 08 exercises
- [ ] Practice troubleshooting scenarios
- [ ] Create troubleshooting checklist
- [ ] Speed drill: Debug and fix

### Weekend Project: Monitoring Stack
Deploy observability solution:
- Application with multiple components
- Configure health probes
- Set up centralized logging
- Monitor with metrics-server
- Create troubleshooting runbook

**Time Target**: Complete in 60 minutes

---

## 🚀 Week 7: Application Lifecycle (CKAD Focus)

### Goals
- Manage application updates
- Configure resource limits
- Implement autoscaling
- Multi-container patterns

### Day 1: Rolling Updates
- [ ] Study Module 10: Application Lifecycle
- [ ] Deployment strategies
- [ ] Rolling updates
- [ ] Rollback procedures
- [ ] Practice: Update applications

**Exercises**:
```bash
- Perform rolling update
- Monitor rollout status
- Pause/resume rollout
- Rollback deployment
```

### Day 2: Resource Management
- [ ] Resource requests and limits
- [ ] QoS classes
- [ ] LimitRanges
- [ ] ResourceQuotas
- [ ] Practice: Resource allocation

**Exercises**:
```bash
- Set resource requests/limits
- Create LimitRange
- Create ResourceQuota
- Test quota enforcement
```

### Day 3: Autoscaling
- [ ] Horizontal Pod Autoscaler (HPA)
- [ ] Vertical Pod Autoscaler (VPA)
- [ ] Cluster Autoscaler
- [ ] Practice: Configure autoscaling

**Exercises**:
```bash
- Create HPA
- Generate load
- Watch scaling behavior
- Configure custom metrics
```

### Day 4: Multi-Container Patterns
- [ ] Sidecar pattern
- [ ] Ambassador pattern
- [ ] Adapter pattern
- [ ] Practice: Multi-container pods

**Exercises**:
```bash
- Create sidecar logging container
- Implement ambassador pattern
- Create adapter for metrics
- Share volumes between containers
```

### Day 5: Week 7 Review
- [ ] Complete Module 10 exercises
- [ ] Practice update scenarios
- [ ] Test autoscaling
- [ ] Speed drill: Deployments

### Weekend: CKAD Mock Exam
- [ ] Complete CKAD Practice Exam 1
- [ ] Time yourself strictly (120 min)
- [ ] Review incorrect answers
- [ ] Identify weak areas

---

## 📝 Week 8: Practice & Exam Preparation

### Goals
- Complete mock exams
- Speed optimization
- Review all topics
- Final preparation

### Day 1: CKA Mock Exam 1
- [ ] Complete CKA Practice Exam 1 (Module 12)
- [ ] Time: 120 minutes strict
- [ ] Grade yourself
- [ ] Review all answers

### Day 2: Review Weak Areas
- [ ] Identify topics from mock exam
- [ ] Re-study specific modules
- [ ] Practice problem areas
- [ ] Create targeted exercises

### Day 3: CKA Mock Exam 2
- [ ] Complete CKA Practice Exam 2
- [ ] Time: 120 minutes strict
- [ ] Aim for >80% score
- [ ] Document mistakes

### Day 4: CKAD Mock Exam (if applicable)
- [ ] Complete CKAD Practice Exam 1
- [ ] Time: 120 minutes strict
- [ ] Focus on speed
- [ ] Review imperative commands

### Day 5: Speed Drills
- [ ] Practice common tasks under time pressure
- [ ] Set up aliases and shortcuts
- [ ] Practice kubectl explain
- [ ] Memorize frequent patterns

**Speed Drill Tasks** (2 minutes each):
```bash
1. Create deployment with 3 replicas
2. Expose deployment as NodePort
3. Scale deployment to 5
4. Create ConfigMap and use in pod
5. Create Secret and mount in pod
6. Create NetworkPolicy
7. Create ServiceAccount with Role
8. Create PV and PVC
9. Backup etcd
10. Drain and uncordon node
```

### Weekend: Final Review
- [ ] Review all modules quickly
- [ ] Practice exam tips
- [ ] Review kubectl cheat sheet
- [ ] Relax and prepare mentally
- [ ] Schedule exam for next week!

---

## 📊 Progress Tracking

### Weekly Checklist

#### Week 1: ☐ Fundamentals
- ☐ Architecture understood
- ☐ Pods mastered
- ☐ Deployments practiced
- ☐ Weekend project completed

#### Week 2: ☐ Networking
- ☐ Services mastered
- ☐ Network policies understood
- ☐ Ingress configured
- ☐ Weekend project completed

#### Week 3: ☐ Storage & Config
- ☐ Persistent storage understood
- ☐ ConfigMaps mastered
- ☐ Secrets practiced
- ☐ Weekend project completed

#### Week 4: ☐ Security
- ☐ RBAC mastered
- ☐ Security contexts understood
- ☐ Pod security practiced
- ☐ Weekend project completed

#### Week 5: ☐ Cluster Ops (CKA)
- ☐ Installation practiced
- ☐ Upgrades mastered
- ☐ etcd backup/restore comfortable
- ☐ Weekend project completed

#### Week 6: ☐ Observability
- ☐ Monitoring configured
- ☐ Logging understood
- ☐ Probes mastered
- ☐ Troubleshooting practiced

#### Week 7: ☐ App Lifecycle (CKAD)
- ☐ Updates and rollbacks mastered
- ☐ Resource management understood
- ☐ Autoscaling practiced
- ☐ Mock exam completed

#### Week 8: ☐ Exam Prep
- ☐ Mock exam 1 completed
- ☐ Mock exam 2 completed
- ☐ Speed drills practiced
- ☐ Ready for certification!

---

## 🎯 Success Metrics

### By End of Week 4
- ✓ Complete 50% of modules
- ✓ Comfortable with kubectl
- ✓ Can deploy applications
- ✓ Understand networking basics

### By End of Week 6
- ✓ Complete 80% of modules
- ✓ Comfortable with troubleshooting
- ✓ Can perform cluster operations
- ✓ Understand security concepts

### By End of Week 8
- ✓ Complete all modules
- ✓ Score >75% on mock exams
- ✓ Complete tasks in time
- ✓ Ready for certification!

---

## 💡 Study Tips

### Effective Learning
1. **Hands-on First**: Always practice, don't just read
2. **Make Mistakes**: Breaking things teaches best
3. **Document**: Keep notes of common errors
4. **Teach Others**: Explain concepts to solidify understanding
5. **Daily Practice**: Consistency beats intensity

### Time Management
1. Set timer for practice tasks
2. Track time spent on each question type
3. Know when to skip and move on
4. Practice under exam conditions

### Resources
- **Official Docs**: kubernetes.io/docs (allowed in exam)
- **kubectl explain**: Your best friend in exam
- **Practice Platforms**: killer.sh, KodeKloud
- **Community**: Join Kubernetes Slack, Reddit r/kubernetes

### Before Exam Day
- [ ] Good night sleep (7-8 hours)
- [ ] Light breakfast
- [ ] Test exam environment
- [ ] Review cheat sheet quickly
- [ ] Stay calm and confident

---

## 📞 Need Help?

### Stuck on Concepts?
- Re-read the module
- Watch YouTube tutorials
- Ask on Kubernetes Slack
- Practice more examples

### Technical Issues?
- Check cluster logs
- Verify configurations
- Use kubectl describe
- Check official documentation

### Exam Anxiety?
- Take breaks during study
- Practice mindfulness
- Mock exams build confidence
- Remember: You can retake!

---

## 🎓 Certification Next Steps

### After CKA
1. Practice real-world scenarios
2. Join Kubernetes community
3. Consider CKAD if not done
4. Explore CKS (Security Specialist)

### After CKAD
1. Deploy production applications
2. Learn GitOps (ArgoCD, Flux)
3. Consider CKA if not done
4. Explore Helm and operators

### After Both
1. **CKS** - Certified Kubernetes Security Specialist
2. Contribute to Kubernetes project
3. Mentor others
4. Build cloud-native applications

---

## ✅ Final Checklist Before Exam

**Technical Preparation**:
- [ ] Completed all 12 modules
- [ ] Solved all exercises
- [ ] Completed 3+ mock exams
- [ ] Scoring >70% consistently
- [ ] Can complete tasks quickly

**Exam Environment**:
- [ ] Tested PSI browser
- [ ] Stable internet connection
- [ ] Quiet environment arranged
- [ ] ID documents ready
- [ ] Desk cleared (only allowed items)

**Mental Preparation**:
- [ ] Well-rested
- [ ] Confident in abilities
- [ ] Familiar with exam format
- [ ] Reviewed cheat sheet
- [ ] Ready to succeed!

---

**Remember**: You don't need to know everything perfectly. You need to know enough to pass (66%) and know where to find information quickly during the exam.

**Good luck! You've got this!** 🚀🎉

