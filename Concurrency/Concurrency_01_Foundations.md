# Module 1: Concurrency Foundations

Understanding the core concepts before writing concurrent code.

---

## 1. Concurrency vs Parallelism

These terms are often confused but mean different things:

### Concurrency
> **Dealing with multiple things at once** (structure)

- Multiple tasks making progress, but not necessarily simultaneously
- Can happen on a single CPU core (time-slicing)
- About **structure** and **design**

```
Single Core - Concurrent (interleaved):
Task A: ████░░░░████░░░░████
Task B: ░░░░████░░░░████░░░░
        ─────────────────────▶ time
```

### Parallelism
> **Doing multiple things at once** (execution)

- Multiple tasks running simultaneously on multiple cores
- Requires multiple CPU cores
- About **execution** and **performance**

```
Multi Core - Parallel (simultaneous):
Core 1: ████████████████████
Core 2: ████████████████████
        ─────────────────────▶ time
```

### The Key Insight
> "Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once." — Rob Pike

| Aspect | Concurrency | Parallelism |
|--------|-------------|-------------|
| Definition | Structure | Execution |
| Cores needed | 1+ | 2+ |
| Goal | Responsiveness, organization | Speed, throughput |
| Example | Web server handling requests | Matrix multiplication |

### Real-World Analogy
- **Concurrent**: One barista handling multiple orders (starts coffee, takes next order while waiting)
- **Parallel**: Multiple baristas each making a coffee simultaneously

---

## 2. Threads vs Processes

### Process
- Independent execution unit with its **own memory space**
- Heavy to create and context-switch
- Processes are **isolated** from each other
- Communication requires IPC (Inter-Process Communication)

### Thread
- Lightweight execution unit **within a process**
- Shares memory with other threads in same process
- Faster to create and switch between
- Can directly share data (but needs synchronization!)

```
┌─────────────────────────────────────────┐
│              PROCESS                     │
│  ┌─────────────────────────────────────┐│
│  │         SHARED MEMORY               ││
│  │    (heap, global variables)         ││
│  └─────────────────────────────────────┘│
│                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Thread 1│ │ Thread 2│ │ Thread 3│   │
│  │ (stack) │ │ (stack) │ │ (stack) │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────┘
```

### Comparison

| Aspect | Process | Thread |
|--------|---------|--------|
| Memory | Separate | Shared |
| Creation cost | High | Low |
| Context switch | Slow (~1-10ms) | Fast (~1-100μs) |
| Communication | IPC (pipes, sockets) | Direct memory access |
| Crash isolation | Isolated | One crash can kill all |

### Java Example
```java
// Creating a thread
Thread thread = new Thread(() -> {
    System.out.println("Running in thread: " + Thread.currentThread().getName());
});
thread.start();
```

### Go Example
```go
// Creating a goroutine (lightweight thread)
go func() {
    fmt.Println("Running in goroutine")
}()
```

---

## 3. Why is Concurrency Hard?

Three main problems make concurrent programming challenging:

### Problem 1: Race Conditions

When multiple threads access shared data and at least one modifies it, the result depends on **timing**.

```java
// DANGER: Race condition!
class Counter {
    private int count = 0;
    
    public void increment() {
        count++;  // NOT atomic! (read → add → write)
    }
}
```

What `count++` actually does:
```
Thread A                    Thread B
────────                    ────────
1. Read count (0)
                            2. Read count (0)
3. Add 1 (= 1)
                            4. Add 1 (= 1)
5. Write count (1)
                            6. Write count (1)

Expected: 2
Actual: 1  ← BUG!
```

### Problem 2: Deadlock

Two or more threads waiting forever for each other to release resources.

```
Thread A                    Thread B
────────                    ────────
1. Lock resource X          1. Lock resource Y
2. Wait for Y...            2. Wait for X...
   (blocked forever)           (blocked forever)
```

**Four conditions for deadlock (all must be true):**
1. **Mutual exclusion** - Resources can't be shared
2. **Hold and wait** - Holding one resource, waiting for another
3. **No preemption** - Can't forcibly take resources
4. **Circular wait** - A waits for B, B waits for A

### Problem 3: Memory Visibility

Changes made by one thread may not be visible to other threads due to CPU caching.

```java
// Thread A
running = false;  // May stay in CPU cache

// Thread B
while (running) {  // May never see the update!
    doWork();
}
```

---

## 4. Thread Lifecycle

A thread goes through several states during its lifetime:

```
                    ┌──────────────┐
                    │     NEW      │
                    │  (created)   │
                    └──────┬───────┘
                           │ start()
                           ▼
    ┌───────────────────────────────────────────┐
    │               RUNNABLE                     │
    │  ┌─────────┐           ┌─────────┐        │
    │  │ READY   │◄─────────►│ RUNNING │        │
    │  │(waiting │ scheduled │(on CPU) │        │
    │  │ for CPU)│           │         │        │
    │  └─────────┘           └─────────┘        │
    └───────────────────────────────────────────┘
           │                        │
           │ wait()/               │ sleep()/
           │ join()                │ blocking I/O
           ▼                        ▼
    ┌─────────────┐         ┌─────────────┐
    │   WAITING   │         │   TIMED     │
    │ (indefinite)│         │  WAITING    │
    └─────────────┘         └─────────────┘
           │                        │
           │ notify()/             │ timeout/
           │ interrupt()           │ interrupt()
           └────────────┬──────────┘
                        │
                        ▼
                ┌──────────────┐
                │  TERMINATED  │
                │  (finished)  │
                └──────────────┘
```

### States Explained

| State | Description | How to enter |
|-------|-------------|--------------|
| NEW | Thread created but not started | `new Thread()` |
| RUNNABLE | Ready to run or currently running | `thread.start()` |
| BLOCKED | Waiting for a monitor lock | Entering `synchronized` block |
| WAITING | Waiting indefinitely | `wait()`, `join()` |
| TIMED_WAITING | Waiting for specified time | `sleep(ms)`, `wait(ms)` |
| TERMINATED | Finished execution | Run method completes |

### Java Example - Thread States
```java
Thread t = new Thread(() -> {
    try {
        Thread.sleep(1000);  // TIMED_WAITING
    } catch (InterruptedException e) {}
});

System.out.println(t.getState());  // NEW
t.start();
System.out.println(t.getState());  // RUNNABLE
Thread.sleep(100);
System.out.println(t.getState());  // TIMED_WAITING
t.join();
System.out.println(t.getState());  // TERMINATED
```

---

## 5. Key Takeaways

1. **Concurrency ≠ Parallelism**: Concurrency is structure, parallelism is execution
2. **Threads share memory**: This is both powerful and dangerous
3. **Three main problems**: Race conditions, deadlocks, visibility
4. **Understand the lifecycle**: Know what state your threads are in

---

## Practice Questions

1. Can you have concurrency without parallelism? (Yes - single core)
2. Can you have parallelism without concurrency? (Yes - SIMD operations)
3. Why might you choose processes over threads? (Isolation, stability)
4. What makes `count++` unsafe in concurrent code? (Not atomic)

---

## Next Module

→ [Module 2: Basic Thread Management](./Concurrency_02_Thread_Management.md)

*We'll create threads, start them, and learn to coordinate their execution.*

---

*Created: January 29, 2026*
