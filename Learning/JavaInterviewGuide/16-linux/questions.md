# Linux — 55 Senior Interview Questions (war-room commands)

**Bar:** You can diagnose a Spring/Kafka box or container. Not RHCE, but not "I only use the IDE".

---

### 1. `ps`, `top`, `htop`, `pidstat` — what's eating the node?

**Short answer:** Start with `top` or `htop` for live CPU and memory, then drill into the JVM with `ps` and `pidstat -p <pid>`. On a Kafka broker or Spring pod host, identify which process dominates CPU, whether threads are runaway, and whether I/O wait is high—not just that Java is high. Pair node view with cgroup limits on Kubernetes workers before restarting workloads.

#### What it is
Process inspection tools answer who is consuming what on a Linux node. `ps` snapshots processes; `top`/`htop` refresh interactively; `pidstat` reports per-PID CPU, memory, and I/O over intervals.

#### How it works (internals)
`top` reads `/proc` and sorts by CPU. `%wa` high means disk or network blocking threads. `pidstat 1` samples every second. `top -H` shows per-thread CPU inside the JVM.

#### When to use / when NOT to use
Use `top`/`htop` for orientation; use `pidstat` for time-series proof. Do not restart JVM based on `top` alone—confirm with `jstack`/`jcmd`.

#### Production example
Kafka consumer lag: `top` shows java at 380% CPU; `pidstat` confirms user CPU not I/O wait; `jstack` finds tight poll loop.

#### Common mistakes
- Ignoring `%wa`
- No cgroup check in containers
- Single `ps` snapshot

#### Interview follow-ups (with model answers)

**Q:** How do you find the Spring Boot PID inside a container?
**A:** Inside the pod, `ps -p 1 -o pid,cmd` often shows the JVM as PID 1. On the worker, `crictl ps` maps container to host PID for `pidstat -p`. Confirm command line matches your service jar before attaching tools.

**Q:** What does high `%wa` mean for a Kafka broker?
**A:** I/O wait means threads blocked on disk or network—not computing. Check data disk `%util` and `await` with `iostat -xz 1`, retention, and replication lag before increasing heap.

**Q:** When would you use `pidstat -d` versus `iotop`?
**A:** `pidstat -d` attributes disk I/O per PID over an interval—good for postmortems. `iotop` is live and interactive but needs root. I pick based on whether I need history or live triage.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate ps`, `top`, `htop`, `pidstat on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

#### Code / config (when useful)
```bash
ps aux --sort=-%cpu | head -15
pidstat -p $(pgrep -f 'kafka.Kafka') 1 10
```

---
### 2. Load average

**Short answer:** Load average is runnable plus uninterruptible tasks averaged over 1, 5, and 15 minutes—not CPU percent. On an 8-core box, load 8.0 means full utilization; load 16 means queuing or D-state I/O threads. Always divide by `nproc` before comparing across hosts.

#### What it is
Load average is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Load average, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Load average provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Load average on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Load average?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Load average?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Load average on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 3. `vmstat`, `iostat`, `mpstat`

**Short answer:** `vmstat` shows memory, swap, and run queues; `iostat` disk latency and utilization; `mpstat` per-core CPU. Use together when `top` shows pain but not the subsystem—especially Kafka disks and Spring I/O wait. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
vmstat`, `iostat`, `mpstat is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For vmstat`, `iostat`, `mpstat, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, vmstat`, `iostat`, `mpstat provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for vmstat`, `iostat`, `mpstat on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting vmstat`, `iostat`, `mpstat?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with vmstat`, `iostat`, `mpstat?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate vmstat`, `iostat`, `mpstat on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 4. Memory: `free -h`, `RSS` vs heap

**Short answer:** `free -h` is kernel RAM; JVM heap is only part of RSS. Metaspace, threads, direct buffers, and native code push container usage above `-Xmx`. OOM kills use cgroup limits, not heap settings.

#### What it is
Memory: `free -h`, `RSS` vs heap is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Memory: `free -h`, `RSS` vs heap, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Memory: `free -h`, `RSS` vs heap provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Memory: `free -h`, `RSS` vs heap on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Memory: `free -h`, `RSS` vs heap?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Memory: `free -h`, `RSS` vs heap?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Memory: `free -h`, `RSS` vs heap on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 5. `/proc/<pid>/status`, `smaps`

**Short answer:** `/proc` exposes VmRSS, thread count, and per-mapping RSS via `smaps`—essential when `jmap` is unavailable in distroless debug scenarios. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
/proc/<pid>/status`, `smaps is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For /proc/<pid>/status`, `smaps, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, /proc/<pid>/status`, `smaps provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for /proc/<pid>/status`, `smaps on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting /proc/<pid>/status`, `smaps?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with /proc/<pid>/status`, `smaps?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate /proc/<pid>/status`, `smaps on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 6. Open files: `lsof -p`, `ulimit -n`

**Short answer:** Every socket and file counts toward `ulimit -n`. Kafka and high-connection Spring apps hit FD limits before CPU. `lsof -p` finds leaks.

#### What it is
Open files: `lsof -p`, `ulimit -n is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Open files: `lsof -p`, `ulimit -n, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Open files: `lsof -p`, `ulimit -n provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Open files: `lsof -p`, `ulimit -n on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Open files: `lsof -p`, `ulimit -n?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Open files: `lsof -p`, `ulimit -n?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Open files: `lsof -p`, `ulimit -n on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 7. Network: `ss -lntp`, `netstat` legacy

**Short answer:** `ss` is fast modern socket listing; use `-lntp` for listening ports and established DB/Kafka connections. Prefer `ss` over deprecated `netstat`. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Network: `ss -lntp`, `netstat` legacy is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Network: `ss -lntp`, `netstat` legacy, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Network: `ss -lntp`, `netstat` legacy provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Network: `ss -lntp`, `netstat` legacy on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Network: `ss -lntp`, `netstat` legacy?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Network: `ss -lntp`, `netstat` legacy?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Network: `ss -lntp`, `netstat` legacy on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 8. `tcpdump` / `wireshark`

**Short answer:** Packet capture proves DNS, TLS, or reset issues when logs are vague. Filter by host/port; mind capture size on busy brokers. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
tcpdump` / `wireshark is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For tcpdump` / `wireshark, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, tcpdump` / `wireshark provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for tcpdump` / `wireshark on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting tcpdump` / `wireshark?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with tcpdump` / `wireshark?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate tcpdump` / `wireshark on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 9. DNS: `dig`, `nslookup`, `getent hosts`

**Short answer:** DNS failures look like app timeouts. `dig` gives TTL and authority; compare pod vs node resolver config. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
DNS: `dig`, `nslookup`, `getent hosts is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For DNS: `dig`, `nslookup`, `getent hosts, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, DNS: `dig`, `nslookup`, `getent hosts provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for DNS: `dig`, `nslookup`, `getent hosts on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting DNS: `dig`, `nslookup`, `getent hosts?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with DNS: `dig`, `nslookup`, `getent hosts?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate DNS: `dig`, `nslookup`, `getent hosts on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 10. `curl` for Spring

**Short answer:** `curl -v` tests HTTP/TLS, headers, and actuator endpoints from inside the cluster network—first step after `ss` confirms listen. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
curl` for Spring is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For curl` for Spring, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, curl` for Spring provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for curl` for Spring on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting curl` for Spring?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with curl` for Spring?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate curl` for Spring on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 11. `jq` on JSON logs

**Short answer:** Structured logs need `jq` filters for traceId, status, duration—faster than grep alone for Spring Cloud JSON. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
jq` on JSON logs is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For jq` on JSON logs, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, jq` on JSON logs provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for jq` on JSON logs on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting jq` on JSON logs?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with jq` on JSON logs?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate jq` on JSON logs on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 12. Disk: `df -h`, `du -sh *`, inode `df -i`

**Short answer:** Full disks and inode exhaustion stop Kafka and logs before CPU does. `du` finds offenders; `df -i` catches small-file storms. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Disk: `df -h`, `du -sh *`, inode `df -i is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Disk: `df -h`, `du -sh *`, inode `df -i, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Disk: `df -h`, `du -sh *`, inode `df -i provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Disk: `df -h`, `du -sh *`, inode `df -i on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Disk: `df -h`, `du -sh *`, inode `df -i?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Disk: `df -h`, `du -sh *`, inode `df -i?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Disk: `df -h`, `du -sh *`, inode `df -i on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 13. `journalctl` vs files

**Short answer:** systemd journal centralizes service logs; files under `/var/log` still matter for apps. Use `-u kafka -f` for follow. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
journalctl` vs files is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For journalctl` vs files, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, journalctl` vs files provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for journalctl` vs files on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting journalctl` vs files?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with journalctl` vs files?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate journalctl` vs files on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 14. systemd: `systemctl status`, `restart`, `enable`

**Short answer:** systemd owns service lifecycle on VMs; in K8s you still see systemd on the node for kubelet/containerd. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
systemd: `systemctl status`, `restart`, `enable is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For systemd: `systemctl status`, `restart`, `enable, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, systemd: `systemctl status`, `restart`, `enable provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for systemd: `systemctl status`, `restart`, `enable on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting systemd: `systemctl status`, `restart`, `enable?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with systemd: `systemctl status`, `restart`, `enable?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate systemd: `systemctl status`, `restart`, `enable on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 15. Signals: `kill`, `kill -3`, `kill -9`

**Short answer:** SIGQUIT (`kill -3`) triggers JVM thread dump; SIGKILL is last resort—no cleanup. Understand graceful shutdown vs `-9`. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Signals: `kill`, `kill -3`, `kill -9 is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Signals: `kill`, `kill -3`, `kill -9, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Signals: `kill`, `kill -3`, `kill -9 provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Signals: `kill`, `kill -3`, `kill -9 on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Signals: `kill`, `kill -3`, `kill -9?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Signals: `kill`, `kill -3`, `kill -9?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Signals: `kill`, `kill -3`, `kill -9 on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 16. `jcmd`, `jstack`, `jmap` on Linux

**Short answer:** JDK CLI tools attach to live JVM for threads, heap histogram, GC—run from same user/cgroup as process. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
jcmd`, `jstack`, `jmap` on Linux is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For jcmd`, `jstack`, `jmap` on Linux, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, jcmd`, `jstack`, `jmap` on Linux provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for jcmd`, `jstack`, `jmap` on Linux on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting jcmd`, `jstack`, `jmap` on Linux?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with jcmd`, `jstack`, `jmap` on Linux?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate jcmd`, `jstack`, `jmap` on Linux on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 17. `/var/log` and logrotate

**Short answer:** Logrotate prevents disk fill; misconfig causes silent truncation—check `logrotate.d` during disk incidents. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
/var/log` and logrotate is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For /var/log` and logrotate, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, /var/log` and logrotate provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for /var/log` and logrotate on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting /var/log` and logrotate?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with /var/log` and logrotate?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate /var/log` and logrotate on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 18. Permissions: `ls -l`, `chmod`, `chown`, `umask`

**Short answer:** Permission denied on data dirs or certs causes mysterious broker/app failures—verify owner and mode. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Permissions: `ls -l`, `chmod`, `chown`, `umask is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Permissions: `ls -l`, `chmod`, `chown`, `umask, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Permissions: `ls -l`, `chmod`, `chown`, `umask provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Permissions: `ls -l`, `chmod`, `chown`, `umask on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Permissions: `ls -l`, `chmod`, `chown`, `umask?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Permissions: `ls -l`, `chmod`, `chown`, `umask?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Permissions: `ls -l`, `chmod`, `chown`, `umask on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 19. `find`, `grep`, `rg`, `awk`, `sed`

**Short answer:** Log archaeology and config search at scale; `rg` ripgrep is faster than grep on large dirs. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
find`, `grep`, `rg`, `awk`, `sed is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For find`, `grep`, `rg`, `awk`, `sed, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, find`, `grep`, `rg`, `awk`, `sed provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for find`, `grep`, `rg`, `awk`, `sed on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting find`, `grep`, `rg`, `awk`, `sed?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with find`, `grep`, `rg`, `awk`, `sed?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate find`, `grep`, `rg`, `awk`, `sed on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 20. Pipes and `xargs`

**Short answer:** Compose one-liners: top PIDs, largest dirs, error counts—xargs avoids subshell footguns with `find`. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Pipes and `xargs is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Pipes and `xargs, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Pipes and `xargs provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Pipes and `xargs on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Pipes and `xargs?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Pipes and `xargs?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Pipes and `xargs on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 21. `strace -p`

**Short answer:** Syscall trace shows ECONNREFUSED, missing files, slow DNS—heavy overhead; short bursts only in prod. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
strace -p is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For strace -p, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, strace -p provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for strace -p on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting strace -p?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with strace -p?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate strace -p on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 22. `lscpu`, `nproc`, cgroup limits

**Short answer:** Know core count for load interpretation; cgroup CPU quota causes throttling invisible to `top` inside pod. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
lscpu`, `nproc`, cgroup limits is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For lscpu`, `nproc`, cgroup limits, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, lscpu`, `nproc`, cgroup limits provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for lscpu`, `nproc`, cgroup limits on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting lscpu`, `nproc`, cgroup limits?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with lscpu`, `nproc`, cgroup limits?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate lscpu`, `nproc`, cgroup limits on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 23. cgroups v2 memory

**Short answer:** v2 unified hierarchy: `memory.current`, `memory.max`, PSI pressure—explains OOMKilled with free RAM on node.

#### What it is
cgroups v2 memory is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For cgroups v2 memory, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, cgroups v2 memory provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for cgroups v2 memory on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting cgroups v2 memory?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with cgroups v2 memory?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate cgroups v2 memory on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 24. Time: `timedatectl`, NTP

**Short answer:** TLS and Kerberos fail with clock skew—`timedatectl` and chrony status are quick checks. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Time: `timedatectl`, NTP is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Time: `timedatectl`, NTP, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Time: `timedatectl`, NTP provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Time: `timedatectl`, NTP on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Time: `timedatectl`, NTP?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Time: `timedatectl`, NTP?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Time: `timedatectl`, NTP on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 25. `ulimit -a`

**Short answer:** Shows fd, process, core limits for the shell/service—compare to `/etc/security/limits.conf`. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
ulimit -a is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For ulimit -a, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, ulimit -a provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for ulimit -a on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting ulimit -a?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with ulimit -a?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate ulimit -a on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 26. `iptables` / `nft` / NSG

**Short answer:** Host firewall plus cloud NSG/SG—trace path when `ss` shows listen but `curl` fails cross-subnet. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
iptables` / `nft` / NSG is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For iptables` / `nft` / NSG, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, iptables` / `nft` / NSG provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for iptables` / `nft` / NSG on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting iptables` / `nft` / NSG?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with iptables` / `nft` / NSG?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate iptables` / `nft` / NSG on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 27. `ping` vs `curl` vs `nc -vz`

**Short answer:** ping tests ICMP (often blocked); `nc -vz` tests TCP port; `curl` tests app protocol—use the right probe. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
ping` vs `curl` vs `nc -vz is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For ping` vs `curl` vs `nc -vz, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, ping` vs `curl` vs `nc -vz provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for ping` vs `curl` vs `nc -vz on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting ping` vs `curl` vs `nc -vz?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with ping` vs `curl` vs `nc -vz?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate ping` vs `curl` vs `nc -vz on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 28. `/etc/hosts`, `resolv.conf`

**Short answer:** Pod and node resolver config—CoreDNS `ndots` and search domains cause intermittent Spring URL failures. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
/etc/hosts`, `resolv.conf is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For /etc/hosts`, `resolv.conf, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, /etc/hosts`, `resolv.conf provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for /etc/hosts`, `resolv.conf on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting /etc/hosts`, `resolv.conf?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with /etc/hosts`, `resolv.conf?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate /etc/hosts`, `resolv.conf on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 29. `env` and secrets in `ps`

**Short answer:** Secrets in environment visible in `/proc`—never pass prod passwords via env on shared hosts. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
env` and secrets in `ps is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For env` and secrets in `ps, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, env` and secrets in `ps provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for env` and secrets in `ps on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting env` and secrets in `ps?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with env` and secrets in `ps?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate env` and secrets in `ps on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 30. `tar`, `gzip`, `zstd`

**Short answer:** Archive heap dumps and log bundles for support—`zstd` faster than gzip for large artifacts. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
tar`, `gzip`, `zstd is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For tar`, `gzip`, `zstd, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, tar`, `gzip`, `zstd provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for tar`, `gzip`, `zstd on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting tar`, `gzip`, `zstd?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with tar`, `gzip`, `zstd?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate tar`, `gzip`, `zstd on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 31. `sha256sum` verify artifacts

**Short answer:** Verify downloaded JDK, agent JAR, or image tarball before install—supply-chain hygiene. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
sha256sum` verify artifacts is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For sha256sum` verify artifacts, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, sha256sum` verify artifacts provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for sha256sum` verify artifacts on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting sha256sum` verify artifacts?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with sha256sum` verify artifacts?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate sha256sum` verify artifacts on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 32. `id`, `sudo`, `su`

**Short answer:** Know effective user for file access and kubectl exec—sudo audit trails matter for compliance. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
id`, `sudo`, `su is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For id`, `sudo`, `su, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, id`, `sudo`, `su provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for id`, `sudo`, `su on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting id`, `sudo`, `su?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with id`, `sudo`, `su?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate id`, `sudo`, `su on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 33. Cron vs systemd timers

**Short answer:** Scheduled jobs on VMs; prefer timers for logging and dependency ordering. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Cron vs systemd timers is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Cron vs systemd timers, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Cron vs systemd timers provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Cron vs systemd timers on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Cron vs systemd timers?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Cron vs systemd timers?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Cron vs systemd timers on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 34. `rsync`, `scp`

**Short answer:** Move large log bundles or thread dump archives off restricted hosts—use compression and checksum. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
rsync`, `scp is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For rsync`, `scp, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, rsync`, `scp provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for rsync`, `scp on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting rsync`, `scp?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with rsync`, `scp?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate rsync`, `scp on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 35. `watch`

**Short answer:** Repeat command every 2s for demos and live incidents—`watch -n1 ss -s` for socket summary. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
watch is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For watch, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, watch provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for watch on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting watch?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with watch?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate watch on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 36. Exit codes

**Short answer:** Exit 137 often OOMKilled; 143 SIGTERM—map shell pipeline failures in CI and container exits. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Exit codes is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Exit codes, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Exit codes provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Exit codes on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Exit codes?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Exit codes?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Exit codes on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 37. `head`, `tail -f`, `less +F`

**Short answer:** Follow live logs; `less +F` pauses without losing stream—essential for Kafka server.log. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
head`, `tail -f`, `less +F is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For head`, `tail -f`, `less +F, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, head`, `tail -f`, `less +F provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for head`, `tail -f`, `less +F on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting head`, `tail -f`, `less +F?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with head`, `tail -f`, `less +F?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate head`, `tail -f`, `less +F on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 38. `sort | uniq -c | sort -nr`

**Short answer:** Top N error messages or slow endpoints from access logs—first step in log storms. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
sort | uniq -c | sort -nr is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For sort | uniq -c | sort -nr, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, sort | uniq -c | sort -nr provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for sort | uniq -c | sort -nr on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting sort | uniq -c | sort -nr?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with sort | uniq -c | sort -nr?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate sort | uniq -c | sort -nr on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 39. `date`, epoch

**Short answer:** Correlate JVM GC log timestamps with kernel and broker logs using epoch ms. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
date`, epoch is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For date`, epoch, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, date`, epoch provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for date`, epoch on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting date`, epoch?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with date`, epoch?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate date`, epoch on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 40. Kernel: `uname -a`, `sysctl`

**Short answer:** Kernel version and tunables (`vm.swappiness`, `tcp_tw_reuse`) for broker tuning disputes. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Kernel: `uname -a`, `sysctl is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Kernel: `uname -a`, `sysctl, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Kernel: `uname -a`, `sysctl provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Kernel: `uname -a`, `sysctl on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Kernel: `uname -a`, `sysctl?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Kernel: `uname -a`, `sysctl?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Kernel: `uname -a`, `sysctl on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 41. Hugepages / THP

**Short answer:** Kafka and some JVMs benefit from hugepages; THP can cause latency jitter—know `never` vs `madvise`. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Hugepages / THP is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Hugepages / THP, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Hugepages / THP provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Hugepages / THP on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Hugepages / THP?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Hugepages / THP?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Hugepages / THP on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 42. `dmesg` hardware/OOM

**Short answer:** Kernel OOM killer messages and hardware errors appear here—check after unexplained pod restarts. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
dmesg` hardware/OOM is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For dmesg` hardware/OOM, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, dmesg` hardware/OOM provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for dmesg` hardware/OOM on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting dmesg` hardware/OOM?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with dmesg` hardware/OOM?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate dmesg` hardware/OOM on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 43. Container: `docker exec` vs `kubectl exec`

**Short answer:** `kubectl exec` goes through API; debug distroless with ephemeral debug containers. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Container: `docker exec` vs `kubectl exec is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Container: `docker exec` vs `kubectl exec, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Container: `docker exec` vs `kubectl exec provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Container: `docker exec` vs `kubectl exec on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Container: `docker exec` vs `kubectl exec?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Container: `docker exec` vs `kubectl exec?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Container: `docker exec` vs `kubectl exec on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 44. Distroless / no `curl` in prod image

**Short answer:** Use `kubectl debug` netshoot or node-level curl when image has no shell tools. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Distroless / no `curl` in prod image is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Distroless / no `curl` in prod image, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Distroless / no `curl` in prod image provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Distroless / no `curl` in prod image on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Distroless / no `curl` in prod image?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Distroless / no `curl` in prod image?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Distroless / no `curl` in prod image on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 45. `openssl s_client -connect host:443`

**Short answer:** TLS handshake, cert chain, SNI from CLI—faster than guessing ingress misconfig. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
openssl s_client -connect host:443 is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For openssl s_client -connect host:443, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, openssl s_client -connect host:443 provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for openssl s_client -connect host:443 on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting openssl s_client -connect host:443?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with openssl s_client -connect host:443?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate openssl s_client -connect host:443 on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 46. `keytool` vs openssl

**Short answer:** JVM truststores use keytool; openssl for PEM chain inspection—both needed in hybrid TLS. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
keytool` vs openssl is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For keytool` vs openssl, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, keytool` vs openssl provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for keytool` vs openssl on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting keytool` vs openssl?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with keytool` vs openssl?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate keytool` vs openssl on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 47. Performance: `perf`, `async-profiler`

**Short answer:** CPU profiling when thread dumps show idle but CPU is high—native GC or hot methods. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Performance: `perf`, `async-profiler is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Performance: `perf`, `async-profiler, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Performance: `perf`, `async-profiler provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Performance: `perf`, `async-profiler on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Performance: `perf`, `async-profiler?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Performance: `perf`, `async-profiler?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Performance: `perf`, `async-profiler on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 48. `iotop`

**Short answer:** Live per-process disk I/O when `iostat` shows saturation—who is writing. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
iotop is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For iotop, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, iotop provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for iotop on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting iotop?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with iotop?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate iotop on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 49. One-minute incident checklist

**Short answer:** ss, df, free, top, dmesg tail, recent deploy—structured first minute on call. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
One-minute incident checklist is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For One-minute incident checklist, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, One-minute incident checklist provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for One-minute incident checklist on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting One-minute incident checklist?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with One-minute incident checklist?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate One-minute incident checklist on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 50. Senior: you type, you don't guess

**Short answer:** Reproduce from shell on the box without IDE—methodology and narration beat random changes. Capture output with UTC timestamps; correlate with JVM and cgroup limits on AKS before restart.

#### What it is
Senior: you type, you don't guess is standard war-room tooling on Linux hosts running Spring Boot, Kafka brokers, or Kubernetes workers. It answers kernel- or process-level questions that APM may miss during incidents. Interviewers expect you to name the command, interpret output, and know container/cgroup caveats on AKS.

#### How it works (internals)
Tools read `/proc`, `/sys`, or netlink sockets depending on subsystem. For Senior: you type, you don't guess, sample over 30–60 seconds before concluding; one snapshot misleads under GC spikes or burst I/O. Correlate with JVM tools (`jcmd`, `jstack`) when the suspect process is Java.

#### When to use / when NOT to use
Use early in triage when symptoms are node-wide, I/O bound, or network related. Skip when logs already show a clear application bug and OS metrics are healthy. On Kubernetes, pair node tools with `kubectl describe pod` and cgroup files under `/sys/fs/cgroup`.

#### Production example
During a production incident on `order-service` or a Kafka broker, Senior: you type, you don't guess provided the deciding evidence: whether CPU was real work vs I/O wait, which disk was saturated, or which PID held thousands of sockets. We fixed root cause (retention, FD leak, cgroup limit)—not just restarted the JVM.

#### Common mistakes
- Restarting Java before capturing 60s of samples
- Ignoring `%wa`, load average, or cgroup throttling
- Using host tools without mapping container PID to worker PID

#### Interview follow-ups (with model answers)

**Q:** When do you reach for Senior: you type, you don't guess on a Kafka broker or Spring node?
**A:** I use it when symptoms are node-wide or the JVM story does not add up. I capture baseline output with UTC timestamps, compare to a healthy peer, and correlate with consumer lag, DB pool metrics, or disk `await` before restarting Java. Restart-only fixes hide retention, FD leaks, and cgroup limit issues that return on the next peak.

**Q:** What do juniors misread when interpreting Senior: you type, you don't guess?
**A:** They confuse load with CPU percent, ignore `%wa` and D-state threads, or trust a single snapshot. I normalize by core count (`load / nproc`), pair with `iostat -xz` and `pidstat`, and check whether all pods on the node are sick versus one bad deployment. In containers I read cgroup `memory.max` and CPU throttling before blaming heap.

**Q:** How does Kubernetes change troubleshooting with Senior: you type, you don't guess?
**A:** Pod PID namespaces and cgroup limits mean host-level tools need the worker context. I `kubectl exec` for in-pod view, `kubectl describe` for OOM/throttle events, and `crictl` on the worker when kubelet is unhealthy. Node problems masquerade as microservice regressions—prove scope before rolling a new image.

#### Scenario probe

**Situation:** During an interview, `order-service` on AKS has rising p99 latency and you must demonstrate Senior: you type, you don't guess on a worker.

**Model answer:** I narrate hypothesis → command → evidence. I determine whether the issue is node-wide or pod-specific, capture metrics with timestamps, correlate with Kafka lag or JDBC pool exhaustion, and propose a fix with rollback (drain node, adjust limits, fix config)—not restart-first.

---
### 51. `crictl` and container runtime debugging on the node.

**Short answer:** On Kubernetes workers, containers run via containerd/CRI-O—not Docker CLI. `crictl` inspects pods, logs, and exec at the runtime layer when kubelet is sick but the node is up.

#### What it is
crictl talks CRI socket on the node (`/run/containerd/containerd.sock`). Essential when `kubectl logs` fails due to kubelet issues.

#### How it works (internals)
`crictl ps`, `pods`, `inspectp`, `logs`, `exec` mirror docker commands. Requires root on worker.

#### When to use / when NOT to use
Use on worker during kubelet/containerd incidents. Not for daily app debugging—prefer kubectl.

#### Production example
Pod stuck Terminating; crictl shows sandbox still running; manual stop after confirming orphan.

#### Common mistakes
- Using docker on containerd-only node
- crictl rm without confirming kubelet state

#### Interview follow-ups (with model answers)

**Q:** crictl vs kubectl logs?
**A:** kubectl goes API→kubelet→CRI; crictl direct when API/kubelet broken.

**Q:** Find CRI socket?
**A:** `crictl info` or `/run/containerd/containerd.sock` on AKS Ubuntu nodes.

#### Scenario probe

Node NotReady but SSH works; kubectl logs timeout.

SSH worker, `crictl ps` vs `kubectl get pods` on node—identify stuck sandboxes. Check containerd logs journalctl. Drain node after fixing if workloads reschedule safely.

---
### 52. eBPF / `bpftrace` basics for latency triage.

**Short answer:** eBPF programs attach kernel hooks safely without kernel modules. bpftrace one-liners measure syscall latency, TCP retransmits, JVM GC pauses at OS boundary—when strace too heavy.

#### What it is
Kernel verifier ensures bounded eBPF programs. bpftrace uses high-level scripts.

#### How it works (internals)
Example: trace connect latency to SQL port; count retransmits during Kafka lag incident.

#### When to use / when NOT to use
Use when node-level latency unexplained and app profilers clean. Learning curve—pair with platform team.

#### Production example
Payment API p99 up; bpftrace shows DNS latency spikes on getaddrinfo before JDBC connect.

#### Common mistakes
- Running bpftrace in prod without approval
- Attaching unsafe BPF from random GitHub scripts

#### Interview follow-ups (with model answers)

**Q:** vs strace?
**A:** eBPF lower overhead; strace per-syscall detail on one PID.

**Q:** AKS?
**A:** Often need privileged daemonset or node debug pod; check policy.

#### Scenario probe

Latency only on one AZ; strace too slow on prod traffic.

bpftrace histogram of TCP connect to DB IP by AZ; correlate with DNS or NSG change in that AZ.

---
### 53. `perf record` / flame graphs for Java on Linux.

**Short answer:** perf samples CPU stacks on Linux; async-profiler or perf-map-agent renders Java method names in flame graphs. Finds hot methods without JFR when only shell access.

#### What it is
perf uses HW counters; Java needs `-XX:+PreserveFramePointer` or profiler JAR for symbol map.

#### How it works (internals)
`perf record -g -p $PID -- sleep 60; perf script | stackcollapse | flamegraph.pl`

#### When to use / when NOT to use
Use when CPU high but jstack shows all waiting—actually hot code path or GC native.

#### Production example
Order service 400% CPU; flame graph shows Jackson deserialization dominating—fix DTO not heap.

#### Common mistakes
- perf without symbols shows only `[unknown]`
- Recording too long fills disk

#### Interview follow-ups (with model answers)

**Q:** async-profiler vs perf?
**A:** async-profiler easier for Java; perf built-in on most kernels.

**Q:** Containers?
**A:** Need perf privileges or debug profile; AKS node pool settings.

#### Scenario probe

Production pod CPU throttled at cgroup limit but JVM thread dump idle.

perf on host PID shows GC threads or compilation consuming quota—raise limit or fix allocation.

---
### 54. `systemd-cgtop` and cgroup v2 memory pressure.

**Short answer:** cgroup v2 unified hierarchy exposes memory.current, memory.pressure. systemd-cgtop shows slice consumption—critical for K8s v2 nodes and Java RSS vs limit.

#### What it is
Pressure stall information (PSI) signals memory contention before OOM.

#### How it works (internals)
`systemd-cgtop` on node; compare kubepods.slice to container limits.

#### When to use / when NOT to use
Use when pods OOMKilled but `free` shows RAM available—cgroup limit not node limit.

#### Production example
Spring pod OOMKilled at 512Mi while node has 32Gi free—cgtop shows kubepods pressure at limit.

#### Common mistakes
- Tuning node only looking at free -h
- Ignoring memory.high throttling

#### Interview follow-ups (with model answers)

**Q:** v1 vs v2?
**A:** AKS 1.29+ often v2; paths under /sys/fs/cgroup unified.

**Q:** PSI?
**A:** /proc/pressure/memory for stall metrics alerting.

#### Scenario probe

Intermittent latency without OOM; PSI memory some avg10 rising.

Identify sibling pod in same cgroup tree consuming burst; adjust limits or isolate noisy neighbor.

---
### 55. `auditd` and compliance logging.

**Short answer:** auditd records syscalls for compliance—who changed `/etc/sudoers`, loaded kernel module, accessed sensitive file. SOC2/PCI often require immutable audit trail.

#### What it is
Rules in `/etc/audit/rules.d`; logs to `/var/log/audit/audit.log`; ausearch/aureport query.

#### How it works (internals)
Watch `-w /etc/shadow -p wa -k identity`; forward to SIEM.

#### When to use / when NOT to use
Enable on bastions and nodes with break-glass access. Balance volume—don't audit every read.

#### Production example
Audit proves contractor account ran chmod on Kafka data dir during incident—feeds RCA.

#### Common mistakes
- Audit rules without log rotation
- Missing ship to SIEM until disk full

#### Interview follow-ups (with model answers)

**Q:** vs journald?
**A:** auditd syscall-level; journald service narrative—complementary.

**Q:** Containers?
**A:** Audit on host captures privileged container escapes if rules cover paths.

#### Scenario probe

Compliance asks prove no unauthorized prod SSH file edits last quarter.

ausearch -k prod-sshd-config -ts last-quarter; correlate with change tickets.

---

## Scenario-based interview drills

### S1. Kafka broker disk full on worker

**Situation:** Brokers crash-loop; df shows 100% on /var/lib/kafka.

**What they're testing:** df, du, retention, iostat

**How to structure your answer:** Disk → cause → fix retention → verify under-replicated

**Model answer:** I'd SSH worker, df -h and df -i, du top dirs, check log segments vs retention.hours. iostat await. Fix retention or expand disk before restart to avoid corrupt log.

**Common weak answers:** Restart broker first without freeing space

**Follow-up probes (with answers):**

**Q:** Follow-up on Kafka broker disk full on worker?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S2. Spring pod DNS intermittent

**Situation:** Only some pods fail curl to internal service.

**What they're testing:** CoreDNS, ndots, resolv.conf

**How to structure your answer:** Compare failing vs working pod resolv; check CoreDNS logs

**Model answer:** kubectl exec diff resolv.conf; dig from pod; CoreDNS metrics; check recent NetworkPolicy.

**Common weak answers:** Blame app without DNS test

**Follow-up probes (with answers):**

**Q:** Follow-up on Spring pod DNS intermittent?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S3. JVM high CPU thread dump clean

**Situation:** top shows 300% CPU; jstack all threads waiting.

**What they're testing:** perf, GC, wrong PID

**How to structure your answer:** Confirm PID namespace, perf record, GC logs

**Model answer:** Verify PID 1 in container; jcmd GC.heap; perf; check for JIT compilation loop.

**Common weak answers:** kill -9 immediately

**Follow-up probes (with answers):**

**Q:** Follow-up on JVM high CPU thread dump clean?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S4. Load average high CPU low

**Situation:** Load 32 on 8 core; CPU 20%.

**What they're testing:** D-state, iowait

**How to structure your answer:** vmstat iostat mpstat

**Model answer:** iostat -x, ps D state, dmesg, Kafka journal dir.

**Common weak answers:** Scale pods horizontally

**Follow-up probes (with answers):**

**Q:** Follow-up on Load average high CPU low?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S5. Connection refused but process up

**Situation:** curl connection refused port 8080.

**What they're testing:** ss bind address, wrong port

**How to structure your answer:** ss -lntp, actuator port

**Model answer:** ss -lntp grep java; check SPRING profile port; kubectl describe.

**Common weak answers:** Assume firewall first

**Follow-up probes (with answers):**

**Q:** Follow-up on Connection refused but process up?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S6. OOMKilled without heap dump

**Situation:** Pod restart loop OOMKilled.

**What they're testing:** cgroup limit vs Xmx

**How to structure your answer:** memory.max, RSS, NMT

**Model answer:** kubectl describe OOM; cgroup memory.current; jcmd NMT if brief window.

**Common weak answers:** Only raise Xmx

**Follow-up probes (with answers):**

**Q:** Follow-up on OOMKilled without heap dump?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S7. TLS handshake failures

**Situation:** openssl s_client fails mid-rollout.

**What they're testing:** cert chain, SNI, clock

**How to structure your answer:** openssl s_client, keytool

**Model answer:** Compare cert dates; check ingress secret; timedatectl.

**Common weak answers:** Disable TLS

**Follow-up probes (with answers):**

**Q:** Follow-up on TLS handshake failures?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S8. sudoers break-glass abuse

**Situation:** Audit alert on sudo chmod.

**What they're testing:** auditd, access review

**How to structure your answer:** ausearch, ticket correlation

**Model answer:** ausearch -k; correlate CMDB; rotate creds if unauthorized.

**Common weak answers:** Ignore audit lag

**Follow-up probes (with answers):**

**Q:** Follow-up on sudoers break-glass abuse?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S9. strace shows ECONNRESET to DB

**Situation:** App logs vague timeout.

**What they're testing:** strace vs app, network path

**How to structure your answer:** strace connect write, ss, nc

**Model answer:** strace -e trace=network; nc -vz; check NSG/SG.

**Common weak answers:** Increase timeout only

**Follow-up probes (with answers):**

**Q:** Follow-up on strace shows ECONNRESET to DB?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
### S10. Senior live troubleshoot interview

**Situation:** Broken pod: health 503, no obvious log.

**What they're testing:** Methodology not speed

**How to structure your answer:** Hypothesis, test, narrate

**Model answer:** State symptom; check listen port and logs; describe events; curl health; thread dump if needed.

**Common weak answers:** Random config changes without narrative

**Follow-up probes (with answers):**

**Q:** Follow-up on Senior live troubleshoot interview?
**A:** Name exact commands, sample output, rollback, and when to escalate to platform.

---
