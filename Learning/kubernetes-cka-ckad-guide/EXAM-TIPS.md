# CKA & CKAD Exam Tips and Tricks

## 🎯 Before You Schedule

### Prerequisites Checklist
- [ ] Completed all modules (1-12)
- [ ] Scored >70% on at least 3 mock exams
- [ ] Comfortable with kubectl commands
- [ ] Can complete common tasks in <5 minutes
- [ ] Familiar with kubernetes.io documentation navigation

### What's Included with Your Exam
- **2 killer.sh practice sessions** (use wisely!)
- **One free retake** (within 12 months of first attempt)
- **Access to kubernetes.io docs during exam**

---

## 🖥️ Exam Environment

### What You Can Access
✅ kubernetes.io/docs
✅ kubernetes.io/blog
✅ github.com/kubernetes (for documentation)
✅ Calculator (system calculator only)
✅ Notepad (provided in exam interface)

### What You Cannot Access
❌ Personal notes
❌ Other websites
❌ ChatGPT or AI tools
❌ Communication apps
❌ Multiple monitors (can only use one)

### Technical Setup
```
Browser: PSI Secure Browser (Chrome-based)
Internet: Stable connection (10+ Mbps recommended)
Webcam: Required and working
Microphone: Required
Environment: Quiet room, no other people
Desk: Clear except for water in clear container
```

---

## ⏰ Time Management Strategy

### Exam Duration: 120 Minutes (2 Hours)

**Time Allocation** (for ~17-20 questions):
```
Per Question Average: 6-7 minutes
First Pass (complete easy ones): 60 minutes
Second Pass (harder questions): 45 minutes
Review and Verify: 15 minutes
```

### The Two-Pass Strategy

**Pass 1: Quick Wins (0-60 min)**
- Read ALL questions quickly first
- Mark difficulty mentally: Easy ⭐ / Medium ⭐⭐ / Hard ⭐⭐⭐
- Complete all ⭐ Easy questions (3-5 min each)
- Complete ⭐⭐ Medium questions if confident (7-10 min each)
- **Skip** ⭐⭐⭐ Hard questions for now
- Goal: Secure 50-60% score in first hour

**Pass 2: Challenges (60-105 min)**
- Return to skipped questions
- Attempt all ⭐⭐⭐ Hard questions
- If stuck after 10 min, move to next
- Don't obsess over single question
- Goal: Push score to 70%+

**Pass 3: Review (105-120 min)**
- Verify your solutions are running
- Check for typos in names
- Ensure you're in correct namespace/context
- Quick syntax check of YAML files
- Final attempts on incomplete questions

---

## 🚀 Speed Optimization

### Setup Phase (First 2 Minutes)

**1. Configure Shell**
```bash
# Set up aliases (exam provides these, but verify)
alias k=kubectl
alias kn='kubectl config set-context --current --namespace'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kd='kubectl describe'
alias kdel='kubectl delete'

# Enable bash completion
source <(kubectl completion bash)
complete -F __start_kubectl k

# Verify aliases work
k get nodes
```

**2. Configure Vim (if you use it)**
```bash
# Add to ~/.vimrc
cat >> ~/.vimrc << EOF
set number
set tabstop=2
set shiftwidth=2
set expandtab
syntax on
EOF
```

**3. Test Cluster Access**
```bash
# Verify you can access clusters
kubectl config get-contexts
kubectl config use-context <first-context>
kubectl get nodes
```

### Command Speed Tips

**Use Imperative Commands**
```bash
# ❌ SLOW: Write YAML from scratch
vim pod.yaml
# ... write entire pod spec ...

# ✅ FAST: Generate YAML
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
vim pod.yaml  # Just edit specific fields
kubectl apply -f pod.yaml
```

**Master --dry-run=client -o yaml**
```bash
# Pod
k run mypod --image=nginx --dry-run=client -o yaml > pod.yaml

# Deployment
k create deployment mydeploy --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Service
k expose deployment mydeploy --port=80 --type=NodePort --dry-run=client -o yaml > svc.yaml

# ConfigMap
k create configmap myconfig --from-literal=key=value --dry-run=client -o yaml > cm.yaml

# Secret
k create secret generic mysecret --from-literal=password=pass123 --dry-run=client -o yaml > secret.yaml

# Job
k create job myjob --image=busybox --dry-run=client -o yaml > job.yaml

# CronJob
k create cronjob mycron --image=busybox --schedule="*/5 * * * *" --dry-run=client -o yaml > cron.yaml
```

**Quick Edits**
```bash
# Edit existing resource
k edit pod mypod

# Replace resource (faster for major changes)
k replace --force -f pod.yaml

# Patch resource (for single field changes)
k patch deployment mydeploy -p '{"spec":{"replicas":5}}'
```

---

## 📋 Common Task Patterns

### Pattern 1: Create Pod Quickly
```bash
# Basic pod
k run nginx --image=nginx

# With environment variables
k run nginx --image=nginx --env="ENV=prod" --env="DEBUG=true"

# With labels
k run nginx --image=nginx --labels="app=web,tier=frontend"

# With command
k run busybox --image=busybox --command -- sleep 3600

# With restart policy
k run nginx --image=nginx --restart=Never  # Pod
k run nginx --image=nginx --restart=OnFailure  # Job
k run nginx --image=nginx --restart=Always  # Deployment
```

### Pattern 2: Create and Expose Deployment
```bash
# One-liner: Create and expose
k create deployment nginx --image=nginx --replicas=3 && \
k expose deployment nginx --port=80 --type=NodePort --name=nginx-service

# With specific NodePort
k create deployment nginx --image=nginx --replicas=3
k expose deployment nginx --port=80 --type=NodePort --dry-run=client -o yaml > svc.yaml
# Edit svc.yaml to add nodePort: 30080
k apply -f svc.yaml
```

### Pattern 3: ConfigMap/Secret in Pod
```bash
# Create ConfigMap
k create configmap app-config \
  --from-literal=DB_HOST=mysql \
  --from-literal=DB_PORT=3306

# Use in pod (as environment variables)
k run myapp --image=nginx --dry-run=client -o yaml > pod.yaml
```

Add to pod.yaml:
```yaml
spec:
  containers:
  - name: nginx
    image: nginx
    envFrom:
    - configMapRef:
        name: app-config
```

### Pattern 4: Resource with Limits
```bash
# Pod with resources
k run nginx --image=nginx \
  --requests='cpu=100m,memory=128Mi' \
  --limits='cpu=200m,memory=256Mi'
```

### Pattern 5: Multi-Container Pod
```bash
# Generate base
k run multi --image=nginx --dry-run=client -o yaml > pod.yaml

# Edit to add second container
vim pod.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi
spec:
  containers:
  - name: nginx
    image: nginx
  - name: busybox
    image: busybox
    command: ['sleep', '3600']
```

---

## 🔍 Troubleshooting Workflow

### When Pod Won't Start

**Step 1: Check Status**
```bash
k get pod <pod-name>
# Look at STATUS column: Pending, ImagePullBackOff, CrashLoopBackOff, etc.
```

**Step 2: Describe Pod**
```bash
k describe pod <pod-name>
# Look at:
# - Events section (most important!)
# - Conditions
# - Container states
```

**Step 3: Check Logs**
```bash
k logs <pod-name>
k logs <pod-name> --previous  # If container restarted
k logs <pod-name> -c <container>  # For multi-container
```

**Step 4: Common Issues and Fixes**

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Pending | Insufficient resources | Check node capacity, reduce requests |
| Pending | No nodes match | Check nodeSelector, taints, affinity |
| ImagePullBackOff | Wrong image name | Fix image name, check registry |
| CrashLoopBackOff | Application error | Check logs, fix application |
| Error | Command failed | Check command syntax in spec |
| CreateContainerConfigError | Bad ConfigMap/Secret reference | Verify ConfigMap/Secret exists |

### When Service Not Working

```bash
# 1. Check service exists
k get svc <service-name>

# 2. Check endpoints
k get endpoints <service-name>
# Should show pod IPs. If empty, selector is wrong!

# 3. Verify selector matches pods
k get svc <service-name> -o yaml | grep -A3 selector
k get pods --show-labels

# 4. Test connectivity from another pod
k run test --image=busybox -it --rm -- wget -O- http://<service-name>:<port>
```

---

## 📝 Context Switching

### CRITICAL: Always Verify Context!

```bash
# Every question specifies context and namespace
# Example: "Context: cluster1, Namespace: production"

# 1. Switch context
kubectl config use-context cluster1

# 2. Verify (important!)
kubectl config current-context

# 3. Set namespace (if specified)
kubectl config set-context --current --namespace=production

# 4. Verify namespace
kubectl config view --minify | grep namespace
```

### Context Switching Checklist
```
[ ] Read question completely
[ ] Note required context
[ ] Switch context: kubectl config use-context <name>
[ ] VERIFY context: kubectl config current-context
[ ] Set namespace if needed
[ ] Proceed with task
[ ] Verify solution before moving on
```

---

## 🎯 Exam-Specific Tips

### Reading Questions

**What to Look For**:
- Required context/cluster
- Namespace
- Resource names (be precise!)
- Labels and selectors
- Specific values (ports, replicas, etc.)
- Verification requirements

**Common Keywords**:
- "Create" → Use imperative or YAML
- "Expose" → Create Service
- "Scale" → kubectl scale or edit replicas
- "Update" → kubectl set image or edit
- "Fix" / "Troubleshoot" → Identify and resolve issue
- "Configure" → Usually edit YAML or use patch

### Scoring Strategy

**Questions are weighted differently!**
- Some worth 2%, others worth 13%
- Check weight before starting
- Prioritize high-value questions in Pass 2

**To Pass (66%)**:
- If questions are equal weight: 13-14 correct out of 20
- But weights vary, so aim for 15+ correct
- Don't waste 20 minutes on a 2% question!

### Common Mistakes to Avoid

❌ **Not switching context** → 0 points!
❌ **Wrong namespace** → Resource created but not found → 0 points!
❌ **Typos in resource names** → Won't match question requirements → 0 points!
❌ **Not verifying solution** → May think it works but doesn't → 0 points!
❌ **Spending 30 min on one question** → Miss easier questions → Fail!

✅ **Do This Instead**:
- Double-check context BEFORE starting
- Copy-paste names from question when possible
- Always verify: `kubectl get <resource> <name>`
- Timebox: If stuck >10 min, move on
- Test your solution actually works

---

## 📚 kubectl explain - Your Best Friend

### How to Use

```bash
# Get field documentation
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers

# Show all fields recursively
kubectl explain deployment.spec --recursive | less

# Search for specific field
kubectl explain pod.spec.containers --recursive | grep -i "liveness"
```

### Common Lookups During Exam

```bash
# Liveness/Readiness probes
kubectl explain pod.spec.containers.livenessProbe

# Resource requests/limits
kubectl explain pod.spec.containers.resources

# Volume mounts
kubectl explain pod.spec.containers.volumeMounts
kubectl explain pod.spec.volumes

# Security context
kubectl explain pod.spec.securityContext
kubectl explain pod.spec.containers.securityContext

# Node affinity
kubectl explain pod.spec.affinity.nodeAffinity

# Tolerations
kubectl explain pod.spec.tolerations

# Service spec
kubectl explain service.spec

# NetworkPolicy
kubectl explain networkpolicy.spec
```

---

## 🔗 Using Kubernetes Documentation

### Efficient Navigation

**Start Points**:
1. kubernetes.io/docs → Search box (top right)
2. kubernetes.io/docs/reference/ → kubectl, API reference
3. kubernetes.io/docs/concepts/ → Understand concepts
4. kubernetes.io/docs/tasks/ → How-to guides (best for exam!)

**Best Sections for Exam**:
```
Tasks → Most practical examples
├── Configure Pods and Containers
├── Manage Cluster Daemons
├── Manage Kubernetes Objects
└── Inject Data Into Applications

Reference
├── kubectl Cheat Sheet (★ BOOKMARK THIS)
└── API Reference
```

### Search Tips

**Good Searches**:
- "pod with configmap" → Clear examples
- "create secret" → Direct instructions
- "network policy examples" → Real YAML
- "kubectl cheat sheet" → Quick reference

**Less Useful**:
- Avoid architecture/theory pages during exam
- Skip "Getting Started" guides
- Don't read entire concepts pages

### Copy-Paste Strategy

1. Find example in docs
2. Copy YAML to clipboard
3. Paste in terminal
4. Modify for question requirements
5. Apply and verify

**Tip**: Use browser's find feature (Ctrl+F / Cmd+F) to locate specific fields in long doc pages!

---

## 💪 Mental Preparation

### The Night Before
- [ ] Get 7-8 hours sleep
- [ ] Light review of cheat sheet only
- [ ] Don't cram new topics
- [ ] Prepare exam space
- [ ] Test webcam and mic

### Exam Day Morning
- [ ] Eat a good breakfast
- [ ] Drink water (but not too much!)
- [ ] Light exercise or stretching
- [ ] Arrive 15 min early
- [ ] Use restroom before starting

### During Exam
- **Stay calm**: Deep breaths if stressed
- **Don't panic**: Everyone finds it challenging
- **Trust preparation**: You've practiced this
- **Keep moving**: Don't get stuck on one question
- **Focus**: One question at a time

### If You're Stuck
1. Skip question, move on
2. Come back with fresh perspective
3. Use documentation
4. Partial credit is better than zero
5. Make educated guess if running out of time

---

## 🎉 After the Exam

### Results
- Available within 24 hours (usually 12-15 hours)
- Sent via email to registered address
- Pass/Fail + score percentage
- No detailed breakdown of which questions were wrong

### If You Pass ✅
- Certificate issued immediately
- Valid for 3 years
- Can share badge on LinkedIn
- Keep practicing to maintain skills!

### If You Don't Pass ❌
- Don't be discouraged! Many people need 2 attempts
- You get ONE free retake
- Wait 24 hours before retaking
- Review weak areas identified during exam
- Complete more mock exams
- Try again when ready!

---

## 🎯 Final Checklist - Day Before Exam

### Knowledge Check
- [ ] Completed all 12 modules
- [ ] Solved 100+ exercises
- [ ] Completed 3+ mock exams scoring >70%
- [ ] Can create common resources in <5 min
- [ ] Comfortable with troubleshooting

### Technical Check
- [ ] PSI Secure Browser installed and tested
- [ ] Webcam working
- [ ] Microphone working
- [ ] Internet stable (>10 Mbps)
- [ ] System requirements met
- [ ] Test environment completed

### Environment Check
- [ ] Quiet room arranged
- [ ] No other people present
- [ ] Good lighting for webcam
- [ ] Desk cleared (only water allowed)
- [ ] Phone out of reach
- [ ] Do Not Disturb signs posted

### Mental Check
- [ ] Well-rested
- [ ] Confident in preparation
- [ ] Familiar with exam format
- [ ] Know time management strategy
- [ ] Ready to pass!

---

## 📖 Quick Reference - Print This!

```
IMPERATIVE COMMANDS CHEAT SHEET
================================

POD
k run <name> --image=<image>
k run <name> --image=<image> --dry-run=client -o yaml > pod.yaml

DEPLOYMENT
k create deployment <name> --image=<image> --replicas=3
k scale deployment <name> --replicas=5
k set image deployment/<name> <container>=<new-image>

SERVICE
k expose deployment <name> --port=80 --type=NodePort

CONFIGMAP
k create configmap <name> --from-literal=<key>=<value>

SECRET
k create secret generic <name> --from-literal=<key>=<value>

NAMESPACE
k create namespace <name>
k config set-context --current --namespace=<name>

RBAC
k create serviceaccount <name>
k create role <name> --verb=<verbs> --resource=<resources>
k create rolebinding <name> --role=<role> --serviceaccount=<ns>:<sa>

NODE OPERATIONS
k drain <node> --ignore-daemonsets --delete-emptydir-data
k cordon <node>
k uncordon <node>

ETCD BACKUP
ETCDCTL_API=3 etcdctl snapshot save <file> \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

DEBUGGING
k get pods
k describe pod <name>
k logs <name>
k exec -it <name> -- /bin/sh
k get events --sort-by='.lastTimestamp'

CONTEXT SWITCHING
k config use-context <context>
k config current-context
k config set-context --current --namespace=<ns>
```

---

## 🌟 You've Got This!

Remember:
- 66% is passing, not 100%
- Speed matters more than perfection
- kubectl explain and docs are your friends
- Practice builds confidence
- Thousands have passed before you

**Good luck on your certification journey!** 🚀

