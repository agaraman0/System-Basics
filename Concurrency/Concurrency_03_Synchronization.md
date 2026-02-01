# Module 3: Synchronization & Shared State

The heart of concurrent programming - protecting shared data from race conditions.

---

## 1. The Problem: Race Conditions Revisited

Let's prove the problem exists with real code:

### Java - Broken Counter
```java
public class BrokenCounter {
    private static int count = 0;
    
    public static void main(String[] args) throws InterruptedException {
        Thread[] threads = new Thread[10];
        
        for (int i = 0; i < 10; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 10000; j++) {
                    count++;  // NOT thread-safe!
                }
            });
            threads[i].start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        System.out.println("Expected: 100000");
        System.out.println("Actual:   " + count);  // Will be less!
    }
}
```

**Output (varies each run):**
```
Expected: 100000
Actual:   87534
```

### Go - Broken Counter
```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    var count int
    var wg sync.WaitGroup
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := 0; j < 10000; j++ {
                count++  // NOT thread-safe!
            }
        }()
    }
    
    wg.Wait()
    fmt.Println("Expected: 100000")
    fmt.Println("Actual:  ", count)  // Will be less!
}
```

### Why Does This Happen?

`count++` is NOT atomic. It's actually three operations:

```
1. READ  count from memory → register
2. ADD   1 to register
3. WRITE register → count in memory
```

Two threads can interleave:
```
Thread A                    Thread B
────────                    ────────
READ count (0)              
                            READ count (0)
ADD 1 (=1)                  
                            ADD 1 (=1)
WRITE count (1)             
                            WRITE count (1)  ← Overwrites!

Result: count = 1 (should be 2)
```

---

## 2. Critical Sections

A **critical section** is code that accesses shared resources and must not be executed by more than one thread at a time.

```
┌─────────────────────────────────────────────┐
│                                             │
│   Thread A        Thread B        Thread C  │
│      │               │               │      │
│      ▼               ▼               ▼      │
│   ┌──────────────────────────────────────┐  │
│   │         CRITICAL SECTION             │  │
│   │    (only ONE thread at a time)       │  │
│   │                                      │  │
│   │    count++                           │  │
│   │    balance = balance - amount        │  │
│   │    list.add(item)                    │  │
│   └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

**Goal:** Ensure **mutual exclusion** - only one thread executes the critical section at a time.

---

## 3. Mutex (Mutual Exclusion Lock)

A **mutex** is a lock that ensures only one thread can hold it at a time.

### Java - synchronized keyword

#### Method-level synchronization
```java
public class SafeCounter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;  // Only one thread can execute this at a time
    }
    
    public synchronized int getCount() {
        return count;
    }
}
```

#### Block-level synchronization
```java
public class SafeCounter {
    private int count = 0;
    private final Object lock = new Object();
    
    public void increment() {
        synchronized (lock) {  // Acquire lock
            count++;
        }  // Release lock automatically
    }
}
```

### Java - ReentrantLock (More Control)

```java
import java.util.concurrent.locks.ReentrantLock;

public class SafeCounter {
    private int count = 0;
    private final ReentrantLock lock = new ReentrantLock();
    
    public void increment() {
        lock.lock();  // Acquire lock
        try {
            count++;
        } finally {
            lock.unlock();  // ALWAYS unlock in finally!
        }
    }
    
    // Try to acquire lock without blocking
    public boolean tryIncrement() {
        if (lock.tryLock()) {
            try {
                count++;
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;  // Couldn't get lock
    }
}
```

### Go - sync.Mutex

```go
package main

import (
    "fmt"
    "sync"
)

type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()         // Acquire lock
    defer c.mu.Unlock() // Release when function returns
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

func main() {
    counter := SafeCounter{}
    var wg sync.WaitGroup
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := 0; j < 10000; j++ {
                counter.Increment()
            }
        }()
    }
    
    wg.Wait()
    fmt.Println("Expected: 100000")
    fmt.Println("Actual:  ", counter.Value())  // Now correct!
}
```

### synchronized vs ReentrantLock

| Feature | synchronized | ReentrantLock |
|---------|-------------|---------------|
| Simplicity | Simple | More verbose |
| Try lock | No | Yes (`tryLock()`) |
| Timeout | No | Yes (`tryLock(time)`) |
| Fairness | No | Optional |
| Interruptible | No | Yes (`lockInterruptibly()`) |
| Multiple conditions | No | Yes |

**Rule of thumb:** Use `synchronized` unless you need advanced features.

---

## 4. Read-Write Locks

When you have many readers and few writers, a regular mutex is inefficient. **Read-Write locks** allow:
- Multiple readers simultaneously (reads don't conflict)
- Only one writer (exclusive access)

### Java - ReadWriteLock

```java
import java.util.concurrent.locks.*;

public class Cache {
    private final Map<String, Object> cache = new HashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    private final Lock readLock = lock.readLock();
    private final Lock writeLock = lock.writeLock();
    
    public Object get(String key) {
        readLock.lock();  // Multiple readers OK
        try {
            return cache.get(key);
        } finally {
            readLock.unlock();
        }
    }
    
    public void put(String key, Object value) {
        writeLock.lock();  // Exclusive access
        try {
            cache.put(key, value);
        } finally {
            writeLock.unlock();
        }
    }
}
```

### Go - sync.RWMutex

```go
type Cache struct {
    mu    sync.RWMutex
    items map[string]interface{}
}

func (c *Cache) Get(key string) interface{} {
    c.mu.RLock()         // Read lock - multiple allowed
    defer c.mu.RUnlock()
    return c.items[key]
}

func (c *Cache) Set(key string, value interface{}) {
    c.mu.Lock()          // Write lock - exclusive
    defer c.mu.Unlock()
    c.items[key] = value
}
```

---

## 5. Atomic Operations

For simple operations (increment, compare-and-swap), atomics are faster than locks.

### Java - Atomic Classes

```java
import java.util.concurrent.atomic.*;

public class AtomicExample {
    private AtomicInteger count = new AtomicInteger(0);
    private AtomicLong total = new AtomicLong(0);
    private AtomicBoolean flag = new AtomicBoolean(false);
    private AtomicReference<String> ref = new AtomicReference<>("initial");
    
    public void increment() {
        count.incrementAndGet();    // Atomic increment, returns new value
        count.getAndIncrement();    // Atomic increment, returns old value
        count.addAndGet(5);         // Add 5 atomically
    }
    
    // Compare-and-swap (CAS)
    public void casExample() {
        // Only set to 10 if current value is 5
        boolean success = count.compareAndSet(5, 10);
    }
}
```

### Go - sync/atomic

```go
import "sync/atomic"

var count int64

func increment() {
    atomic.AddInt64(&count, 1)     // Atomic increment
}

func getValue() int64 {
    return atomic.LoadInt64(&count)  // Atomic read
}

func setValue(n int64) {
    atomic.StoreInt64(&count, n)     // Atomic write
}

// Compare-and-swap
func casExample() {
    // Only swap if current value equals 5
    swapped := atomic.CompareAndSwapInt64(&count, 5, 10)
}
```

### When to Use Atomics vs Locks

| Use Atomics | Use Locks |
|-------------|-----------|
| Single variable operations | Multiple variables |
| Simple increment/decrement | Complex logic in critical section |
| Performance critical counters | Need to hold lock across operations |
| Flag checking | Conditional updates with logic |

---

## 6. Volatile (Java Specific)

The `volatile` keyword ensures:
1. **Visibility** - Changes are immediately visible to other threads
2. **Ordering** - Prevents instruction reordering

```java
public class VolatileExample {
    private volatile boolean running = true;  // Visible across threads
    
    public void stop() {
        running = false;  // Guaranteed to be seen by other threads
    }
    
    public void run() {
        while (running) {  // Will see the update!
            doWork();
        }
    }
}
```

**Without volatile:**
```java
private boolean running = true;  // May be cached in CPU register

// Thread B may NEVER see this change!
while (running) { ... }  // Could loop forever
```

### volatile vs synchronized

| Feature | volatile | synchronized |
|---------|----------|--------------|
| Atomicity | No (only for read/write) | Yes |
| Visibility | Yes | Yes |
| Use case | Flags, state checks | Complex operations |
| Performance | Faster | Slower |

**Note:** Go doesn't have `volatile`. Use `sync/atomic` or channels instead.

---

## 7. Common Synchronization Patterns

### Double-Checked Locking (Singleton)

```java
public class Singleton {
    private static volatile Singleton instance;  // volatile is crucial!
    
    public static Singleton getInstance() {
        if (instance == null) {                    // First check (no lock)
            synchronized (Singleton.class) {
                if (instance == null) {            // Second check (with lock)
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

### Go - sync.Once (Better!)

```go
var (
    instance *Singleton
    once     sync.Once
)

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{}
    })
    return instance
}
```

---

## 8. Fixed Counter Example

### Java - Thread-Safe Counter

```java
import java.util.concurrent.atomic.AtomicInteger;

public class FixedCounter {
    private static AtomicInteger count = new AtomicInteger(0);
    
    public static void main(String[] args) throws InterruptedException {
        Thread[] threads = new Thread[10];
        
        for (int i = 0; i < 10; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 10000; j++) {
                    count.incrementAndGet();  // Atomic!
                }
            });
            threads[i].start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        System.out.println("Expected: 100000");
        System.out.println("Actual:   " + count.get());  // Always 100000!
    }
}
```

### Go - Thread-Safe Counter

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
)

func main() {
    var count int64
    var wg sync.WaitGroup
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := 0; j < 10000; j++ {
                atomic.AddInt64(&count, 1)  // Atomic!
            }
        }()
    }
    
    wg.Wait()
    fmt.Println("Expected: 100000")
    fmt.Println("Actual:  ", count)  // Always 100000!
}
```

---

## 9. Key Takeaways

| Concept | Java | Go |
|---------|------|-----|
| Basic lock | `synchronized` | `sync.Mutex` |
| Explicit lock | `ReentrantLock` | `sync.Mutex` |
| Read-write lock | `ReadWriteLock` | `sync.RWMutex` |
| Atomics | `AtomicInteger`, etc. | `sync/atomic` |
| Visibility | `volatile` | atomics or channels |
| Singleton | Double-checked locking | `sync.Once` |

### Rules to Remember

1. **Identify shared mutable state** - What variables are accessed by multiple threads?
2. **Protect all access** - Both reads AND writes need protection
3. **Keep critical sections small** - Hold locks for minimum time
4. **Prefer atomics for simple cases** - Faster than locks
5. **Always unlock** - Use `try-finally` (Java) or `defer` (Go)

---

## Practice Challenges

1. **Bank Account**: Implement thread-safe deposit/withdraw with overdraft protection

2. **Thread-Safe Stack**: Implement push/pop with proper synchronization

3. **Hit Counter**: Count website hits per second with atomic operations

---

## Next Module

→ [Module 4: Communication Between Threads](./Concurrency_04_Communication.md)

*Learn wait/notify, channels, and condition variables for thread coordination.*

---

*Created: January 29, 2026*
