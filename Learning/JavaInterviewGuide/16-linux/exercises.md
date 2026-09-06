# Linux — Practical Exercises

Do these on a VM, WSL, or container with a JDK. Production triage skills live in Part C.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) — 33 exercises total.

---

## Part A — Basic (10)

### Exercise A1 — Find a Java process with ps

**Task:** Start a Spring app; find its PID and full command line.

**Solution:**

```bash
java -jar order-service.jar &
ps aux | grep '[o]rder-service'
ps -p <pid> -o pid,user,%cpu,%mem,cmd
```

**Expected output:**

```
  4521 prashant  2.3  4.1 java -jar order-service.jar
    PID USER     %CPU %MEM CMD
   4521 prashant  2.3  4.1 java -jar order-service.jar
```

---

### Exercise A2 — top / load average

**Task:** Observe CPU and load while hitting the app.

**Solution:**

```bash
top -p <pid>
# press '1' for per-CPU
curl -s http://localhost:8080/actuator/health > /dev/null &
```

**Expected output (top header):**

```
load average: 0.52, 0.48, 0.45
%Cpu(s): 12.3 us,  2.1 sy,  0.0 ni, 85.0 id,  0.0 wa
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 4521 prashant  20   0  4.2g   512m   32m S  18.2   6.4   0:12.34 java
```

---

### Exercise A3 — Disk usage with df

**Task:** Check filesystem usage before deploy.

**Solution:**

```bash
df -h
df -h /var /tmp
df -i /var   # inode check
```

**Expected output:**

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        49G   22G   26G  46% /
/dev/sda1        49G   22G   26G  46% /var
```

---

### Exercise A4 — Find large directories with du

**Task:** Find what consumed `/var/log`.

**Solution:**

```bash
sudo du -xh /var/log --max-depth=1 | sort -h
sudo du -sh /var/log/*
```

**Expected output:**

```
4.0K    /var/log/private
128M    /var/log/journal
1.2G    /var/log/app
1.4G    /var/log
```

---

### Exercise A5 — Decode ls permissions

**Task:** Explain `drwxr-x---` and numeric mode.

**Solution:**

```bash
ls -la /opt/order-service
stat -c '%a %n' /opt/order-service/app.jar
```

**Expected output:**

```
drwxr-x---  5 deploy deploy 4096 Sep  5 14:00 order-service
640 /opt/order-service/app.jar
```

**Decode:** `drwxr-x---` = dir, owner rwx, group r-x, other --- (750). File `640` = owner rw, group r, other none — app user can read jar, others cannot.

---

### Exercise A6 — chmod and chown

**Task:** Fix script that fails with `Permission denied`.

**Solution:**

```bash
ls -l deploy.sh
# -rw-r--r-- deploy deploy
chmod u+x deploy.sh
chown deploy:deploy deploy.sh
./deploy.sh
```

**Expected output:**

```
-rwxr-xr-- 1 deploy deploy 512 Sep  5 14:00 deploy.sh
Starting order-service...
```

---

### Exercise A7 — Listening ports with ss

**Task:** Confirm app listens on 8080; find process.

**Solution:**

```bash
ss -lntp | grep 8080
ss -lntp 'sport = :8080'
```

**Expected output:**

```
LISTEN 0  100  *:8080  *:*  users:(("java",pid=4521,fd=68))
```

---

### Exercise A8 — curl health check

**Task:** Verbose curl to local actuator; read status and timing.

**Solution:**

```bash
curl -v http://localhost:8080/actuator/health
curl -o /dev/null -s -w 'http_code=%{http_code} time=%{time_total}s\n' \
  http://localhost:8080/actuator/health
```

**Expected output:**

```
< HTTP/1.1 200
{"status":"UP"}
http_code=200 time=0.023s
```

---

### Exercise A9 — journalctl for systemd service

**Task:** Tail logs for `order-service` unit; filter errors since boot.

**Solution:**

```bash
sudo journalctl -u order-service -f
sudo journalctl -u order-service -p err -b
sudo journalctl -u order-service --since "10 min ago" | tail -20
```

**Expected output:**

```
Sep 05 14:12:01 host order-service[4521]: Started OrderServiceApplication in 8.2 seconds
Sep 05 14:15:33 host order-service[4521]: ERROR c.e.p.PaymentClient - Connection refused
```

---

### Exercise A10 — Signals: graceful vs kill -9

**Task:** Stop Java with SIGTERM; observe shutdown hooks. Compare SIGKILL.

**Solution:**

```bash
kill -15 <pid>    # SIGTERM
# logs: "Commencing graceful shutdown"
sleep 5
kill -9 <pid>     # SIGKILL — no shutdown hook
```

**Expected output (SIGTERM):**

```
Tomcat started on port 8080
... Graceful shutdown complete
(process exits 0)
```

**Expected output (SIGKILL):** Process vanishes immediately; no shutdown log; possible incomplete transaction.

---

## Part B — Intermediate (10)

### Exercise B1 — Thread dump via SIGQUIT

**Task:** Capture thread dump from running Spring app.

**Solution:**

```bash
kill -3 <pid>
# dump goes to stdout / catalina.out / journal

jcmd <pid> Thread.print > /tmp/threaddump.txt
head -30 /tmp/threaddump.txt
```

**Expected output:**

```
"http-nio-8080-exec-1" #25 daemon prio=5 os_prio=0 cpu=12.34ms elapsed=1.23s tid=0x... nid=0x1a2 runnable
   java.lang.Thread.State: RUNNABLE
        at java.net.SocketInputStream.socketRead0(Native Method)
        at org.apache.coyote.http11.Http11Processor.service(...)
```

---

### Exercise B2 — Too many open files (ulimit)

**Task:** Reproduce EMFILE; compare ulimit vs fixing leak.

**Solution:**

```java
// LeakSockets.java
var list = new java.util.ArrayList<java.net.Socket>();
for (int i = 0; i < 10_000; i++) list.add(new java.net.Socket());
```

```bash
ulimit -n
java LeakSockets.java
ls /proc/<pid>/fd | wc -l
ulimit -n 65535
```

**Expected output:**

```
1024
Exception: Too many open files
1024
(after raise ulimit, runs longer — still wrong; fix is close sockets in finally)
```

---

### Exercise B3 — Disk full simulation

**Task:** Fill `/tmp`; watch app fail writing logs; recover.

**Solution:**

```bash
df -h /tmp
dd if=/dev/zero of=/tmp/fill bs=1M count=4000 status=progress   # careful on small disks
df -h /tmp
curl http://localhost:8080/api/orders   # may 500 if log append fails
rm /tmp/fill
```

**Expected output:**

```
/dev/sda1  49G  49G  0 100% /
java.io.IOException: No space left on device
```

**logrotate snippet:**

```
/var/log/app/*.log {
    daily
    rotate 7
    compress
    missingok
    copytruncate
}
```

---

### Exercise B4 — Port already bound

**Task:** Start two apps on 8080; diagnose.

**Solution:**

```bash
java -jar order-service.jar --server.port=8080 &
java -jar payment-service.jar --server.port=8080
ss -lntp | grep 8080
```

**Expected output (second start):**

```
Web server failed to start. Port 8080 was already in use.
LISTEN ... users:(("java",pid=4521,fd=68))
```

Fix: change port or stop first process.

---

### Exercise B5 — Connection refused vs timeout

**Task:** Distinguish nothing listening vs firewall drop.

**Solution:**

```bash
nc -vz 127.0.0.1 5432          # nothing listening
# nc: connect to 127.0.0.1 port 5432 (tcp) failed: Connection refused

sudo iptables -A INPUT -p tcp --dport 5432 -j DROP   # if permitted
nc -vz 127.0.0.1 5432
# nc: connect to 127.0.0.1 port 5432 (tcp) timed out
```

**Expected output in Spring:**

```
Connection refused → org.postgresql.util.PSQLException: Connection refused
Timeout          → java.net.SocketTimeoutException: connect timed out
```

Refused = wrong host/port or service down. Timeout = network/firewall/security group.

---

### Exercise B6 — Count 5xx in logs

**Task:** One-liner 5xx count from JSON access log.

**Solution:**

```bash
grep '"status":5' /var/log/app/access.log | wc -l

jq -r 'select(.status >= 500)' /var/log/app/access.log | wc -l

awk '$9 ~ /^5/ {c++} END {print c+0}' /var/log/nginx/access.log
```

**Expected output:**

```
47
```

---

### Exercise B7 — RSS vs heap (-Xmx)

**Task:** `-Xmx256m` + 200MB direct buffer; compare `ps RSS` vs heap.

**Solution:**

```bash
java -Xmx256m -jar heap-demo.jar &
ps -p <pid> -o rss=,vsz=,cmd
jcmd <pid> GC.heap_info
```

**Expected output:**

```
 524288 java -Xmx256m ...     # RSS ~512 MB in KB columns
 heap usage: 180M / 256M
```

RSS > heap because of metaspace, thread stacks, code cache, **direct buffers**, native libs.

---

### Exercise B8 — CPU steal (vmstat)

**Task:** Read `vmstat 1`; explain `st` column.

**Solution:**

```bash
vmstat 1 5
```

**Expected output:**

```
 procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 8123456 120000 2048000  0    0     5    12  450  890  8  2 88  1  3
```

**Interpretation:** `st=3` means hypervisor stole 3% CPU from this VM (noisy neighbor on shared host). High `st` + high API latency → request larger instance or dedicated host.

---

### Exercise B9 — TLS certificate expiry

**Task:** Check cert dates for a host.

**Solution:**

```bash
echo | openssl s_client -servername api.example.com -connect api.example.com:443 2>/dev/null \
  | openssl x509 -noout -dates -subject -issuer
```

**Expected output:**

```
notBefore=Jan 15 00:00:00 2026 GMT
notAfter=Apr 15 23:59:59 2026 GMT
subject=CN = api.example.com
issuer=C = US, O = Let's Encrypt, CN = R3
```

Alert if `notAfter` < 14 days away.

---

### Exercise B10 — Distroless pod debug

**Task:** Get thread dump from distroless Java container (no shell).

**Solution:**

```bash
# Option 1: ephemeral debug container (K8s 1.23+)
kubectl debug -it pod/order-svc-xxx --image=eclipse-temurin:21 --target=order-svc --share-processes -- \
  jcmd 1 Thread.print

# Option 2: actuator (if enabled + secured)
kubectl port-forward pod/order-svc-xxx 8080:8080
curl -u admin:$TOKEN http://localhost:8080/actuator/threaddump | head

# Option 3: debug sidecar sharing PID namespace
```

**Expected output:**

```
"main" #1 prio=5 os_prio=0 cpu=120ms elapsed=3600s tid=0x... nid=0x1 runnable
```

---

## Part C — Hard (8)

### Exercise C1 — Five-minute production triage playbook

**Task:** App "slow" — run this sequence in order; document findings.

**Solution:**

```bash
# 1. Is it up?
curl -sf http://localhost:8080/actuator/health || echo DOWN

# 2. Recent errors
sudo journalctl -u order-service --since "5 min ago" -p warning

# 3. CPU / memory
ps -p $(pgrep -f order-service) -o %cpu,%mem,rss,etime,cmd
top -b -n 1 -p $(pgrep -f order-service) | tail -2

# 4. Disk / FDs
df -h /var /tmp
ls /proc/$(pgrep -f order-service)/fd | wc -l
ulimit -n

# 5. Network / DB
ss -tan | awk '$1=="ESTAB"' | wc -l
nc -vz db.internal 5432

# 6. GC pauses (if GC log enabled)
grep "Pause Young" /var/log/app/gc.log | tail -5

# 7. Thread dump if CPU high
jcmd $(pgrep -f order-service) Thread.print | grep -c RUNNABLE
```

**Expected output (example RCA):**

```
health: UP
FD count: 987 / 1024  ← near limit
ESTAB connections: 412
→ leak of HTTP client connections; restart mitigates; fix pool config
```

---

### Exercise C2 — Inode exhaustion

**Task:** Disk has space but `No space left on device` on write.

**Solution:**

```bash
df -h /var
df -i /var
find /var/tmp -type f | wc -l
```

**Simulate (lab only):**

```bash
mkdir /tmp/inode-test && cd /tmp/inode-test
for i in $(seq 1 50000); do touch "f$i"; done
```

**Expected output:**

```
df -h: 40% used
df -i: 100% IUsed — IAvail 0
touch: cannot touch 'f50001': No space left on device
```

Fix: delete small files / move temp dir / raise inode count (new filesystem).

---

### Exercise C3 — strace slow syscall

**Task:** App hangs on startup; trace syscalls for 10 s.

**Solution:**

```bash
strace -f -p <pid> -e trace=network,file -tt -T 2>&1 | head -40
# or startup:
strace -f -o /tmp/strace.log java -jar order-service.jar
grep -E 'connect|open.*jdbc' /tmp/strace.log | tail -20
```

**Expected output:**

```
14:22:01.123 connect(5, {sa_family=AF_INET, sin_port=htons(5432), sin_addr=inet_addr("10.0.1.5")}, 16) = -1 ETIMEDOUT (Connection timed out) <30.001234>
```

→ DB unreachable; not JVM heap issue.

---

### Exercise C4 — tcpdump API latency

**Task:** Capture HTTP to upstream payment service; measure SYN→response.

**Solution:**

```bash
sudo tcpdump -i any -nn host 10.0.2.20 and port 443 -w /tmp/pay.pcap &
curl http://localhost:8080/api/orders/1/pay
sudo kill %1
tcpdump -nn -r /tmp/pay.pcap | head -20
```

**Expected output:**

```
14:30:01.100 IP 10.0.1.10.45678 > 10.0.2.20.443: Flags [S]
14:30:01.105 IP 10.0.2.20.443 > 10.0.1.10.45678: Flags [S.]
14:30:03.500 IP 10.0.2.20.443 > 10.0.1.10.45678: Flags [P.], seq 1:1420, ack 518
```

2.4 s until data — payment SSL handshake slow; aligns with trace span.

---

### Exercise C5 — Permission denied on prod log dir

**Task:** Service user cannot write `/var/log/app` after deploy.

**Solution:**

```bash
ls -laZ /var/log/app          # SELinux context if enabled
namei -l /var/log/app/app.log
sudo -u order-svc touch /var/log/app/test.log
```

**Expected output:**

```
drwxr-xr-x root root /var/log
drwxr-x--- root deploy /var/log/app
touch: cannot touch '/var/log/app/test.log': Permission denied
```

**Fix:**

```bash
sudo chown order-svc:order-svc /var/log/app
sudo chmod 750 /var/log/app
# SELinux: sudo chcon -t var_log_t /var/log/app
```

---

### Exercise C6 — OOM killer investigation

**Task:** Process killed overnight; confirm OOM in kernel log.

**Solution:**

```bash
dmesg -T | grep -i 'killed process'
journalctl -k | grep -i oom
grep -i oom /var/log/syslog
```

**Expected output:**

```
Sep  5 03:14:22 host kernel: Out of memory: Killed process 4521 (java) total-vm:8388608kB, anon-rss:6291456kB
Sep  5 03:14:22 host kernel: oom_reaper: reaped process 4521 (java)
```

**Mitigation:** Lower heap, raise cgroup memory limit in K8s, fix leak, add swap only as buffer (not solution).

---

### Exercise C7 — File descriptor leak over time

**Task:** Plot FD count every 30 s; identify leak.

**Solution:**

```bash
PID=$(pgrep -f order-service)
while true; do
  echo "$(date +%T) $(ls /proc/$PID/fd 2>/dev/null | wc -l)"
  sleep 30
done
```

**Expected output:**

```
14:00:00 180
14:00:30 245
14:01:00 310
14:01:30 375
```

Monotonic growth → leak (unclosed streams/sockets). Thread dump + heap dump for pool holding clients.

---

### Exercise C8 — Full incident RCA: slow API (synthetic)

**Task:** Given symptoms, produce written RCA with evidence commands.

**Scenario:** p99 latency 2 s (normal 200 ms) since 14:00; CPU normal; errors none.

**Solution:**

```bash
# Evidence collection
grep '"duration":' /var/log/app/access.log | jq -r 'select(.duration>1000) | .uri' | sort | uniq -c | sort -rn | head
#   412 /api/orders/{id}

ss -tan state established '( dport = :5432 )' | wc -l
# 48 connections — normal ~10

PGPASSWORD=... psql -h db.internal -c "SELECT pid, now()-query_start AS dur, state, query FROM pg_stat_activity WHERE state != 'idle' ORDER BY dur DESC LIMIT 5;"
```

**Expected output:**

```
  pid  |   dur    | state  |              query
-------+----------+--------+--------------------------------
 10234 | 00:00:08 | active | SELECT * FROM orders WHERE ...
```

**RCA document:**

```
Impact:     GET /api/orders/{id} p99 2s since 14:00 UTC
Cause:      Missing index on orders(customer_id) after migration; seq scan on 4M rows
Evidence:   pg_stat_activity 8s queries; EXPLAIN shows Seq Scan
Mitigation: CREATE INDEX CONCURRENTLY idx_orders_customer_id (deployed 14:45)
Prevention: Add migration review checklist; datasource-proxy slow query alert >500ms
```


### Exercise 29 — crictl on kind/minikube node

**Task:** List running pod sandboxes with crictl on a cluster node.

**Solution:**

```bash
docker exec -it kind-control-plane crictl ps
docker exec -it kind-control-plane crictl pods
docker exec -it kind-control-plane crictl logs $(docker exec kind-control-plane crictl ps -q | head -1)
```

**Expected output:** Container IDs matching `kubectl get pods -A` on node.

---

### Exercise 30 — PSI memory pressure readout

**Task:** Read memory pressure metrics on cgroup v2 host.

**Solution:**

```bash
cat /proc/pressure/memory
cat /sys/fs/cgroup/kubepods.slice/memory.current 2>/dev/null || true
systemd-cgtop --batch=1 | head -20
```

**Expected output:**

```
some avg10=0.00 avg60=0.00 avg300=0.00 total=...
full avg10=0.00 ...
```

---

### Exercise 31 — bpftrace connect latency sketch

**Task:** One-liner histogram of TCP connect latency to port 5432 (lab only).

**Solution:**

```bash
sudo bpftrace -e 'kprobe:tcp_connect { @start[tid] = nsecs; }
  kretprobe:tcp_connect /@start[tid]/ { @us = hist((nsecs - @start[tid]) / 1000); delete(@start[tid]); }'
# Ctrl-C after sample traffic: psql or nc test
```

**Expected output:** Histogram `@us` with latency buckets in microseconds.

---

### Exercise 32 — perf flame graph on Java

**Task:** Record 30s CPU profile of Spring PID; note symbol requirement.

**Solution:**

```bash
PID=$(pgrep -f order-service)
sudo perf record -g -p $PID -- sleep 30
sudo perf script | stackcollapse-perf.pl | flamegraph.pl > /tmp/app.svg
```

**Expected output:** SVG flame graph; if `[unknown]` dominates, attach async-profiler or enable frame pointers.

---

### Exercise 33 — auditd rule and ausearch drill

**Task:** Add audit watch on `/etc/hosts` write; trigger change; query log.

**Solution:**

```bash
sudo auditctl -w /etc/hosts -p wa -k hosts-change
echo "# test" | sudo tee -a /etc/hosts
sudo ausearch -k hosts-change -i
sudo auditctl -W /etc/hosts  # remove watch after lab
```

**Expected output:** ausearch shows syscall=openat path=/etc/hosts type=PATH with your user.


---

## Stats

| Section | Count |
|---------|------:|
| Part A — Basic | 12 |
| Part B — Intermediate | 12 |
| Part C — Hard | 9 |
| **Total** | **33** |
