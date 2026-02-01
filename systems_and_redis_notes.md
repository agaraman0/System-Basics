# Systems Fundamentals & Redis Internals — Complete Conversation Notes

> This document is a consolidated, structured rewrite of a continuous discussion
> covering CPU cores, processes, threads, concurrency, parallelism, performance,
> and Redis internals, limitations, and capacity metrics.

---

## Q1. On a multicore processor, is it necessary that a process can be executed on just one core?

### Answer

No.

A **process is not limited to a single core**. What matters is **how many threads** the process has.

### Key Concepts
- The OS schedules **threads**, not processes.
- A **single-threaded process**:
  - Can run on only **one core at a time**
  - May migrate between cores over time
- A **multi-threaded process**:
  - Can execute **simultaneously on multiple cores**

### Rule
> A process can run on multiple cores **only if it has multiple runnable threads**.

---

## Q2. If there are multiple processes, each with multiple threads, and multiple cores — how do we structure these?

### Answer

You structure systems around **threads-to-core balance**, not processes.

### OS Reality
- Threads are scheduled onto cores
- Too many runnable threads cause:
  - Context switching
  - Cache thrashing
  - Lock contention

### Golden Rule
> **Runnable threads ≈ number of CPU cores (or a small multiple)**

---

### Common Models

#### 1. Process-per-core (CPU-bound)
- One process per core
- One thread per process
- Used for heavy computation

#### 2. Few processes with thread pools (most servers)
- 1–4 processes
- Threads ≈ cores
- Balanced CPU + I/O workloads

#### 3. Event-driven / async model
- Few threads
- Millions of logical tasks
- Best for I/O-heavy systems

---

## Q3. Parallelism vs Concurrency?

### Answer

They are related but **not the same**.

### Definitions
- **Concurrency**: Multiple tasks in progress (interleaving)
- **Parallelism**: Multiple tasks executing simultaneously

### Key Relationships
- Concurrency does **not** require multiple cores
- Parallelism **requires** multiple cores
- Parallelism always implies concurrency

### Mental Model
> Concurrency is about **structure**  
> Parallelism is about **hardware**

---

## Q4. How to achieve maximum performance from any machine?

### Answer

Performance comes from **balance**, not brute force.

### One-Sentence Rule
> **Maximum performance = keep every critical resource busy, but never contended.**

### Resources
- CPU
- Memory
- Cache
- Disk
- Network
- Locks

---

### Core Principles

#### CPU
- Threads ≈ cores
- Avoid oversubscription
- Avoid blocking

#### Memory
- Cache locality matters more than bandwidth
- Reduce allocations
- Avoid pointer chasing

#### Concurrency Model
- Pick **one** model
- Don’t mix threads + async poorly

#### Locks
- Reduce shared mutable state
- Shard data
- Prefer immutability

---

### Scaling Rule
> Scale **up** until contention appears, then scale **out**.

---

## Q5. Why does Redis use a single thread?

### Answer

Redis is single-threaded **by design**, to achieve:
- Ultra-low latency
- Deterministic behavior
- Zero locking overhead

### Redis Goals
- Microsecond-level commands
- Shared in-memory data structures
- Atomic operations by default

### Key Insight
> Locking costs more than Redis commands themselves.

---

### Benefits of Single Thread
- No locks
- No race conditions
- Perfect cache locality
- Predictable latency

### How Redis Handles Many Clients
- Event loop
- Non-blocking I/O (`epoll`, `kqueue`)
- Concurrency without parallelism

---

## Q6. What does “Redis is single-threaded” actually mean?

### Answer

It does **not** mean Redis uses only one OS thread.

### Precise Meaning
> **Exactly one thread executes all commands that mutate or read Redis data structures.**

### Redis Process Model
- One OS process
- Multiple helper threads:
  - I/O
  - Persistence
  - Replication
- **One command-execution thread**

---

### Important Clarification
- Commands are:
  - Serialized
  - Non-interleaved
  - Atomic

---

## Q7. How does this compare with other key-value databases?

### Comparison

#### Redis
- Single-threaded execution
- No locks
- Extremely low latency
- Scales via sharding

#### Memcached
- Multi-threaded
- Lock-based
- Higher throughput
- Simpler data model

#### RocksDB
- Embedded
- Multi-threaded
- Disk-backed
- Higher latency

#### Distributed KV stores (Cassandra, Dynamo-style)
- Many processes
- Sharded data
- Eventual consistency
- High throughput, higher latency

---

## Q8. Given Redis uses shared memory and is fully in-memory, what are its limitations and failure modes?

### Answer

Redis’s strengths **define its limitations**.

---

### 1. Memory Is a Hard Limit
- All data must fit in RAM
- No automatic paging
- OOM leads to:
  - Write failures
  - Evictions
  - Process termination

---

### 2. Single-Core CPU Bottleneck
- One core executes all commands
- CPU-heavy commands block everything

Dangerous commands:
- `KEYS`
- Large `LRANGE`
- `SMEMBERS`
- Large Lua scripts

---

### 3. Fork + Copy-on-Write Risks
- Persistence uses `fork()`
- Writes during snapshot duplicate memory pages
- Memory usage can double
- Common cause of Redis crashes

---

### 4. Asynchronous Persistence
- RDB snapshots → data loss window
- AOF (`everysec`) → ≤1 second data loss
- Writes acknowledged before disk flush

---

### 5. No Multi-Core Writes
- One Redis instance ≈ one CPU core
- Scaling requires sharding
- Hot shards are common failure points

---

### 6. Cluster & Replication Edge Cases
- Async replication
- Stale reads
- Lost writes during failover
- Limited cross-key atomicity

---

### 7. Large Objects Are Anti-Patterns
- Huge JSON blobs
- Logs
- Analytics data

Problems:
- Blocking execution
- Fragmentation
- Serialization cost

---

## Q9. What are Redis performance numbers, metrics, thresholds, and capacity limits?

### Throughput (Single Instance)
- GET/SET: **100k–500k ops/sec**
- Pipelined ops: **1–2M ops/sec**
- Complex/Lua: **10k–50k ops/sec**

---

### Latency (Healthy)
| Metric | Target |
|-----|-----|
| p50 | < 0.5 ms |
| p95 | < 1 ms |
| p99 | < 2–3 ms |
| p99.9 | < 5–10 ms |

Red flag:
- p99 > 5 ms (sustained)

---

### CPU Thresholds
- Healthy: ≤ 70% of one core
- Warning: 80%
- Critical: 100%

---

### Memory Thresholds
- used_memory ≤ 70–75% RAM
- Fragmentation ratio ≤ 1.5
- Fragmentation > 2.0 = danger
- Evictions > 0 (non-cache use) = bug

---

### Replication
- Replica lag < 100 ms (healthy)
- >1 sec = stale reads
- >5 sec = unsafe failover

---

### Persistence
- Fork time > 100–200 ms = risk
- Memory needed during snapshot ≈ dataset size

---

## Q10. Final Summary Mental Models

- OS schedules **threads**, not processes
- Concurrency ≠ parallelism
- Redis is single-threaded **at the data layer**
- Redis trades durability & parallelism for latency
- One bad Redis command can block everyone
- Redis scales horizontally, never vertically

> **Redis is fast until it suddenly isn’t — and when it breaks, it breaks hard.**

---

## End of Notes
