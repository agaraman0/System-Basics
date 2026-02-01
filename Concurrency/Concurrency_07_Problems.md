# Module 7: Common Problems & Debugging

Understanding what goes wrong and how to fix it.

---

## 1. Deadlock

A deadlock occurs when two or more threads are blocked forever, each waiting for the other.

### The Classic Deadlock

```
Thread A                    Thread B
────────                    ────────
1. Lock(X)                  1. Lock(Y)
2. Wait for Y...            2. Wait for X...
   ↓ blocked forever           ↓ blocked forever
```

### Java Deadlock Example

```java
public class DeadlockExample {
    private final Object lockA = new Object();
    private final Object lockB = new Object();
    
    public void method1() {
        synchronized (lockA) {           // Thread 1 gets lockA
            System.out.println("Thread 1: holding lockA");
            sleep(100);  // Simulate work
            
            synchronized (lockB) {       // Thread 1 waits for lockB
                System.out.println("Thread 1: holding lockA and lockB");
            }
        }
    }
    
    public void method2() {
        synchronized (lockB) {           // Thread 2 gets lockB
            System.out.println("Thread 2: holding lockB");
            sleep(100);  // Simulate work
            
            synchronized (lockA) {       // Thread 2 waits for lockA - DEADLOCK!
                System.out.println("Thread 2: holding lockB and lockA");
            }
        }
    }
    
    public static void main(String[] args) {
        DeadlockExample obj = new DeadlockExample();
        
        new Thread(obj::method1, "Thread-1").start();
        new Thread(obj::method2, "Thread-2").start();
        // Program hangs forever!
    }
    
    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) {}
    }
}
```

### Go Deadlock Example

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func main() {
    var lockA, lockB sync.Mutex
    
    // Goroutine 1
    go func() {
        lockA.Lock()
        fmt.Println("Goroutine 1: holding lockA")
        time.Sleep(100 * time.Millisecond)
        
        lockB.Lock()  // Waits for lockB
        fmt.Println("Goroutine 1: holding both")
        lockB.Unlock()
        lockA.Unlock()
    }()
    
    // Goroutine 2
    go func() {
        lockB.Lock()
        fmt.Println("Goroutine 2: holding lockB")
        time.Sleep(100 * time.Millisecond)
        
        lockA.Lock()  // Waits for lockA - DEADLOCK!
        fmt.Println("Goroutine 2: holding both")
        lockA.Unlock()
        lockB.Unlock()
    }()
    
    time.Sleep(5 * time.Second)
    fmt.Println("This will never print")
}
```

### Four Conditions for Deadlock

All four must be true for deadlock to occur:

| Condition | Description | Example |
|-----------|-------------|---------|
| **Mutual Exclusion** | Resources can't be shared | Only one thread can hold a lock |
| **Hold and Wait** | Holding one resource, waiting for another | Has lockA, waiting for lockB |
| **No Preemption** | Can't forcibly take resources | Can't steal a lock from another thread |
| **Circular Wait** | A waits for B, B waits for A | Thread 1 → lockB → Thread 2 → lockA → Thread 1 |

### Preventing Deadlocks

#### 1. Lock Ordering (Break Circular Wait)

```java
// ALWAYS acquire locks in the same order
public void safeMethod1() {
    synchronized (lockA) {      // Always A first
        synchronized (lockB) {  // Then B
            // work
        }
    }
}

public void safeMethod2() {
    synchronized (lockA) {      // Always A first (same order!)
        synchronized (lockB) {
            // work
        }
    }
}
```

#### 2. Lock Timeout (Break Hold and Wait)

```java
public boolean tryTransfer(Account from, Account to, int amount) {
    while (true) {
        if (from.lock.tryLock(100, TimeUnit.MILLISECONDS)) {
            try {
                if (to.lock.tryLock(100, TimeUnit.MILLISECONDS)) {
                    try {
                        // Do transfer
                        return true;
                    } finally {
                        to.lock.unlock();
                    }
                }
            } finally {
                from.lock.unlock();
            }
        }
        // Back off and retry
        Thread.sleep(random.nextInt(100));
    }
}
```

#### 3. Single Lock (Eliminate Multiple Locks)

```java
// Instead of multiple fine-grained locks
private final Object globalLock = new Object();

public void transfer(Account from, Account to, int amount) {
    synchronized (globalLock) {
        from.withdraw(amount);
        to.deposit(amount);
    }
}
```

---

## 2. Livelock

Threads are not blocked but can't make progress because they keep responding to each other.

### Real-World Analogy

Two people in a hallway:
```
Person A: "After you" → steps right
Person B: "After you" → steps right
Person A: "After you" → steps left
Person B: "After you" → steps left
... forever dancing ...
```

### Java Livelock Example

```java
public class LivelockExample {
    static class Spoon {
        private Diner owner;
        
        public synchronized void use() {
            System.out.println(owner.name + " is eating");
        }
        
        public synchronized void setOwner(Diner d) { owner = d; }
        public synchronized Diner getOwner() { return owner; }
    }
    
    static class Diner {
        private String name;
        private boolean isHungry;
        
        public Diner(String name) {
            this.name = name;
            this.isHungry = true;
        }
        
        public void eatWith(Spoon spoon, Diner spouse) {
            while (isHungry) {
                if (spoon.getOwner() != this) {
                    try { Thread.sleep(1); } catch (InterruptedException e) {}
                    continue;
                }
                
                // Being polite causes livelock!
                if (spouse.isHungry) {
                    System.out.println(name + ": You eat first, " + spouse.name);
                    spoon.setOwner(spouse);
                    continue;  // Give spoon away, try again
                }
                
                spoon.use();
                isHungry = false;
                spoon.setOwner(spouse);
            }
        }
    }
    
    public static void main(String[] args) {
        Diner husband = new Diner("Husband");
        Diner wife = new Diner("Wife");
        Spoon spoon = new Spoon();
        spoon.setOwner(husband);
        
        new Thread(() -> husband.eatWith(spoon, wife)).start();
        new Thread(() -> wife.eatWith(spoon, husband)).start();
        // Both keep passing spoon, neither eats!
    }
}
```

### Fixing Livelock

Add randomness to break the symmetry:

```java
public void eatWith(Spoon spoon, Diner spouse) {
    while (isHungry) {
        if (spoon.getOwner() != this) {
            Thread.sleep(1);
            continue;
        }
        
        if (spouse.isHungry) {
            // Random chance to be selfish
            if (Math.random() < 0.5) {
                System.out.println(name + ": I'll eat first this time");
                spoon.use();
                isHungry = false;
                spoon.setOwner(spouse);
                return;
            }
            spoon.setOwner(spouse);
            continue;
        }
        
        spoon.use();
        isHungry = false;
        spoon.setOwner(spouse);
    }
}
```

---

## 3. Starvation

A thread can never get the resources it needs because other threads keep taking them.

### Causes of Starvation

| Cause | Example |
|-------|---------|
| Unfair locks | High-priority threads always win |
| Greedy threads | One thread holds lock for too long |
| Wrong priorities | Low-priority thread never scheduled |

### Example: Reader Starvation

```java
// If readers keep coming, writer never gets access
ReadWriteLock lock = new ReentrantReadWriteLock(false);  // Unfair

// Fix: Use fair lock
ReadWriteLock fairLock = new ReentrantReadWriteLock(true);  // Fair
```

### Fair vs Unfair Locks

```java
// Unfair (default) - faster but can cause starvation
ReentrantLock unfair = new ReentrantLock(false);

// Fair - FIFO ordering, prevents starvation
ReentrantLock fair = new ReentrantLock(true);
```

### Preventing Starvation

1. **Use fair locks** when necessary
2. **Limit lock hold time** - don't do I/O while holding locks
3. **Avoid priority inversion** - be careful with thread priorities
4. **Use timeouts** - don't wait forever

---

## 4. Race Condition Detection

### Go Race Detector

Go has a built-in race detector:

```bash
# Run with race detector
go run -race main.go

# Test with race detector
go test -race ./...

# Build with race detector (slower, for testing only)
go build -race -o myapp
```

Example output:
```
==================
WARNING: DATA RACE
Write at 0x00c0000180a8 by goroutine 7:
  main.increment()
      /app/main.go:12 +0x4a

Previous read at 0x00c0000180a8 by goroutine 6:
  main.increment()
      /app/main.go:12 +0x3e

Goroutine 7 (running) created at:
  main.main()
      /app/main.go:20 +0x7a
==================
```

### Java Thread Sanitizer (TSan)

Available in some JVMs (e.g., with special flags):

```bash
# With OpenJDK build that supports TSan
java -XX:+EnableThreadSanitizer MyApp
```

### Static Analysis Tools

**Java:**
- SpotBugs (FindBugs successor)
- IntelliJ IDEA inspections
- Error Prone

**Go:**
- `go vet`
- staticcheck
- golangci-lint

```bash
# Go static analysis
go vet ./...
staticcheck ./...
golangci-lint run
```

---

## 5. Thread Dumps (Java)

A thread dump shows what every thread is doing - essential for debugging deadlocks.

### Getting a Thread Dump

```bash
# Method 1: jstack
jstack <pid>

# Method 2: kill -3 (sends to stderr)
kill -3 <pid>

# Method 3: jcmd
jcmd <pid> Thread.print

# Method 4: In code
Thread.getAllStackTraces().forEach((thread, stack) -> {
    System.out.println(thread.getName() + " - " + thread.getState());
    for (StackTraceElement element : stack) {
        System.out.println("    " + element);
    }
});
```

### Reading a Thread Dump

```
"Thread-1" #12 prio=5 os_prio=0 tid=0x00007f... nid=0x5e03 
    waiting for monitor entry [0x00007f...]
   java.lang.Thread.State: BLOCKED (on object monitor)
        at DeadlockExample.method1(DeadlockExample.java:15)
        - waiting to lock <0x000000076b2a1e60> (a java.lang.Object)
        - locked <0x000000076b2a1e50> (a java.lang.Object)

"Thread-2" #13 prio=5 os_prio=0 tid=0x00007f... nid=0x5e04
    waiting for monitor entry [0x00007f...]
   java.lang.Thread.State: BLOCKED (on object monitor)
        at DeadlockExample.method2(DeadlockExample.java:25)
        - waiting to lock <0x000000076b2a1e50> (a java.lang.Object)
        - locked <0x000000076b2a1e60> (a java.lang.Object)

Found 1 deadlock.
```

### Key Thread States

| State | Meaning |
|-------|---------|
| RUNNABLE | Running or ready to run |
| BLOCKED | Waiting for monitor lock |
| WAITING | Waiting indefinitely (wait, join) |
| TIMED_WAITING | Waiting with timeout (sleep, wait(ms)) |
| TERMINATED | Finished execution |

---

## 6. Go Debugging Tools

### Goroutine Dump

```go
import (
    "os"
    "runtime/pprof"
)

// Dump all goroutines
pprof.Lookup("goroutine").WriteTo(os.Stdout, 1)

// Or use SIGQUIT
// kill -QUIT <pid>  → prints to stderr
```

### pprof Profiling

```go
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    // Start pprof server
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()
    
    // Your app...
}
```

```bash
# View in browser
open http://localhost:6060/debug/pprof/

# Goroutine profile
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Block profile (where goroutines block)
go tool pprof http://localhost:6060/debug/pprof/block

# Mutex profile (lock contention)
go tool pprof http://localhost:6060/debug/pprof/mutex
```

### Detecting Goroutine Leaks

```go
import "runtime"

func TestNoLeak(t *testing.T) {
    before := runtime.NumGoroutine()
    
    // Run your code
    doSomething()
    
    time.Sleep(100 * time.Millisecond)  // Let goroutines finish
    
    after := runtime.NumGoroutine()
    if after > before {
        t.Errorf("Goroutine leak: before=%d, after=%d", before, after)
    }
}
```

---

## 7. Common Debugging Patterns

### 1. Add Logging with Thread/Goroutine ID

**Java:**
```java
private static final Logger log = LoggerFactory.getLogger(MyClass.class);

public void process() {
    log.info("[{}] Starting process", Thread.currentThread().getName());
    // ...
}
```

**Go:**
```go
import "runtime"

func getGID() uint64 {
    b := make([]byte, 64)
    runtime.Stack(b, false)
    // Parse goroutine ID from stack trace
    // (Use only for debugging!)
}

log.Printf("[goroutine %d] Starting process", getGID())
```

### 2. Timeout Everything

```java
// Java
Future<Result> future = executor.submit(task);
try {
    Result result = future.get(5, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    log.error("Task timed out - possible deadlock?");
    future.cancel(true);
}
```

```go
// Go
select {
case result := <-resultCh:
    return result, nil
case <-time.After(5 * time.Second):
    return nil, errors.New("timeout - possible deadlock?")
}
```

### 3. Health Checks

```java
// Periodic check that threads are making progress
ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor();
monitor.scheduleAtFixedRate(() -> {
    if (taskQueue.size() > 1000) {
        log.warn("Queue backing up: {} tasks", taskQueue.size());
    }
    if (activeWorkers.get() == 0 && !taskQueue.isEmpty()) {
        log.error("Workers stalled! Queue has {} items", taskQueue.size());
        // Dump threads for debugging
    }
}, 1, 1, TimeUnit.SECONDS);
```

---

## 8. Debugging Checklist

When you suspect a concurrency bug:

```
□ Can you reproduce it reliably?
  - Add Thread.sleep() to widen race window
  - Run under load/stress test
  
□ Is it a deadlock?
  - Take thread dump
  - Look for BLOCKED threads waiting for each other
  
□ Is it a race condition?
  - Run with race detector (Go: -race)
  - Look for missing synchronization
  
□ Is it starvation?
  - Check thread priorities
  - Look for unfair locks
  - Check for threads holding locks too long
  
□ Is it a livelock?
  - Look for threads that are RUNNABLE but not progressing
  - Check for retry loops without backoff
```

---

## 9. Key Takeaways

| Problem | Symptom | Fix |
|---------|---------|-----|
| Deadlock | Threads BLOCKED forever | Lock ordering, timeouts |
| Livelock | Threads RUNNABLE, no progress | Add randomness/backoff |
| Starvation | One thread never runs | Fair locks, limit hold time |
| Race condition | Inconsistent results | Proper synchronization |

### Prevention Is Better Than Debugging

1. **Design for concurrency** from the start
2. **Minimize shared mutable state**
3. **Use high-level abstractions** (channels, executors)
4. **Test under load** with race detectors
5. **Add observability** (metrics, logging)

---

## Practice Challenges

1. **Deadlock Detector**: Write code that detects potential deadlocks at runtime

2. **Reproduce a Race**: Create a test that reliably reproduces a race condition

3. **Thread Dump Analyzer**: Parse a thread dump and identify deadlocks

---

## Next Module

→ [Module 8: Mini Projects](./Concurrency_08_Projects.md)

*Put it all together with hands-on projects*

---

*Created: January 29, 2026*
