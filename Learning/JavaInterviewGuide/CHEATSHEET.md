# Answer cheat sheet (print this)

Use the **CORF** shape every time:

**C**ontext → **O**ptions → **R**isks/trade-offs → **F**ailure & how you verify

## Tables to memorize

### Transaction propagation
REQUIRED | REQUIRES_NEW | NESTED | SUPPORTS | NOT_SUPPORTED | MANDATORY | NEVER

Rollback default: **unchecked only**. Catch = commit. `rollbackFor`. Self-invocation skips proxy. OSIV off.

### Kafka
Order **per partition**. Group: one consumer per partition. At-least-once default. EOS ≠ Oracle. Outbox + inbox. Rebalance → duplicates. Stable `group.id`. Poison: DLT vs stall.

### Isolation (know Oracle RC)
RU / RC / RR / Serializable. Lost update: version or `FOR UPDATE`. `NOT IN` + NULL. Unindexed FKs.

### JVM
G1 default. Metaspace leaks = classloaders. Direct buffers off-heap. Virtual threads ≠ unbounded DB.

### REST
POST + Idempotency-Key. PUT idempotent. 409 vs 412. Problem Details. Cursor pagination. BOLA.

### K8s/Helm
Liveness ≠ DB. Startup probe for JVM. `Xmx` < limit. Graceful: preStop + `server.shutdown`. Helm 3-way merge. No secrets in values.

### Terraform
State + lock. `for_each` not `count`. `-/+` means replace. Plan file in CI. TF for cloud, Helm for apps.

### Linux war room
`ss -lntp` · `ps` · `df` · `free` · `dmesg` · `curl -v` · `jcmd Thread.print` · `kubectl describe` · `kill -3`

### EDA
`AFTER_COMMIT` listener is **not** safe. Dual-write. Outbox. Inbox. Fat vs thin. Honest UI pending.

### AI
Junior PR standard. No secrets. No auto-merge. You own authz/tx/money.
