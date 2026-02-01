# Concurrency & Multi-threading Learning Path

A comprehensive guide to learning concurrent programming with **Java** and **Go**.

---

## Learning Roadmap

### Module 1: Foundations
- [x] What is Concurrency vs Parallelism?
- [x] Threads vs Processes
- [x] Why is concurrency hard? (Race conditions, deadlocks)
- [x] Thread lifecycle

### Module 2: Basic Thread Management
- [x] Creating and starting threads (Java: Thread/Runnable, Go: goroutines)
- [x] Waiting for threads to complete (join)
- [x] Thread sleep and yield
- [x] Daemon threads

### Module 3: Synchronization & Shared State
- [x] Critical sections
- [x] Mutex / Locks (Java: synchronized, ReentrantLock | Go: sync.Mutex)
- [x] Read-Write Locks
- [x] Atomic operations
- [x] Volatile keyword (Java)

### Module 4: Communication Between Threads
- [x] wait/notify (Java)
- [x] Channels (Go)
- [x] Condition variables
- [x] BlockingQueue (Java)

### Module 5: Concurrency Patterns
- [x] Producer-Consumer
- [x] Reader-Writer
- [x] Thread Pool
- [x] Future/Promise
- [x] Fan-out/Fan-in

### Module 6: High-Level Concurrency
- [x] ExecutorService (Java)
- [x] CompletableFuture (Java)
- [x] Worker pools (Go)
- [x] Context and cancellation (Go)
- [x] Select statement (Go)

### Module 7: Common Problems & Debugging
- [x] Deadlocks - detection and prevention
- [x] Livelocks
- [x] Starvation
- [x] Race condition debugging
- [x] Thread dumps and profiling

### Module 8: Mini Projects
- [x] Concurrent web scraper
- [x] Producer-consumer pipeline
- [x] Rate limiter
- [x] Concurrent cache (LRU)
- [x] Worker pool implementation

---

## Progress Tracker

| Module | Status | Notes File |
|--------|--------|------------|
| Module 1: Foundations | ✅ Complete | `Concurrency_01_Foundations.md` |
| Module 2: Thread Management | ✅ Complete | `Concurrency_02_Thread_Management.md` |
| Module 3: Synchronization | ✅ Complete | `Concurrency_03_Synchronization.md` |
| Module 4: Communication | ✅ Complete | `Concurrency_04_Communication.md` |
| Module 5: Patterns | ✅ Complete | `Concurrency_05_Patterns.md` |
| Module 6: High-Level | ✅ Complete | `Concurrency_06_HighLevel.md` |
| Module 7: Problems | ✅ Complete | `Concurrency_07_Problems.md` |
| Module 8: Projects | ✅ Complete | `Concurrency_08_Projects.md` |

---

## Quick Reference

### Java Concurrency Cheatsheet
```java
// Create thread
Thread t = new Thread(() -> doWork());
t.start();
t.join();  // wait for completion

// Synchronization
synchronized(lock) { /* critical section */ }

// Executor
ExecutorService exec = Executors.newFixedThreadPool(4);
Future<Result> f = exec.submit(() -> compute());

// BlockingQueue
BlockingQueue<Task> q = new ArrayBlockingQueue<>(100);
q.put(task);    // blocks if full
q.take();       // blocks if empty
```

### Go Concurrency Cheatsheet
```go
// Create goroutine
go doWork()

// Channels
ch := make(chan int)    // unbuffered
ch := make(chan int, 5) // buffered

go func() { ch <- value }()  // send
result := <-ch               // receive

// Select (multiplexing)
select {
case v := <-ch1:
    handle(v)
case ch2 <- x:
    // sent
default:
    // non-blocking
}

// Mutex
var mu sync.Mutex
mu.Lock()
// critical section
mu.Unlock()
```

---

*Last updated: January 29, 2026*
