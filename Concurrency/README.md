# Concurrency & Multi-threading

> Complete guide to concurrent programming concepts.

---

## Study Order

| Step | File | Topic |
|------|------|-------|
| 0 | [Concurrency_Learning_Path.md](Concurrency_Learning_Path.md) | Overview & roadmap |
| 1 | [Concurrency_01_Foundations.md](Concurrency_01_Foundations.md) | Basics, threads vs processes |
| 2 | [Concurrency_02_Thread_Management.md](Concurrency_02_Thread_Management.md) | Creating & managing threads |
| 3 | [Concurrency_03_Synchronization.md](Concurrency_03_Synchronization.md) | Locks, mutexes, semaphores |
| 4 | [Concurrency_04_Communication.md](Concurrency_04_Communication.md) | Thread communication |
| 5 | [Concurrency_05_Patterns.md](Concurrency_05_Patterns.md) | Producer-Consumer, etc. |
| 6 | [Concurrency_06_HighLevel.md](Concurrency_06_HighLevel.md) | Thread pools, executors |
| 7 | [Concurrency_07_Problems.md](Concurrency_07_Problems.md) | Deadlocks, race conditions |
| 8 | [Concurrency_08_Projects.md](Concurrency_08_Projects.md) | Practice projects |
| 9 | [Concurrency_Locks_Isolation_Complete_Guide.md](Concurrency_Locks_Isolation_Complete_Guide.md) | Deep dive on locks |

---

## Key Concepts Quick Reference

### Synchronization Primitives

| Primitive | Purpose | Use Case |
|-----------|---------|----------|
| Mutex | Mutual exclusion | Protect critical section |
| Semaphore | Control access count | Limit concurrent access |
| Condition Variable | Thread signaling | Wait/notify pattern |
| Read-Write Lock | Concurrent reads | Read-heavy workloads |

### Common Problems

| Problem | Cause | Solution |
|---------|-------|----------|
| Deadlock | Circular wait | Lock ordering, timeout |
| Race Condition | Unsynchronized access | Proper locking |
| Starvation | Unfair scheduling | Fair locks |
| Livelock | Active waiting loop | Backoff strategy |

### Patterns

| Pattern | Use Case |
|---------|----------|
| Producer-Consumer | Queue processing |
| Reader-Writer | Shared data access |
| Thread Pool | Task execution |
| Future/Promise | Async results |

---

*Back to [Main Index](../README.md)*
