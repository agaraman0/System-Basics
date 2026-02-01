# Complete Reference: All Types of Locks in Computing

> A comprehensive guide to every type of lock used in software systems - from low-level hardware locks to distributed coordination mechanisms.

---

## Table of Contents

1. [Lock Fundamentals](#1-lock-fundamentals)
2. [Application-Level Locks](#2-application-level-locks)
3. [Database Locks](#3-database-locks)
4. [Distributed Locks](#4-distributed-locks)
5. [Hardware & OS Locks](#5-hardware--os-locks)
6. [Lock-Free & Wait-Free Alternatives](#6-lock-free--wait-free-alternatives)
7. [Lock Problems & Solutions](#7-lock-problems--solutions)
8. [Choosing the Right Lock](#8-choosing-the-right-lock)

---

# 1. Lock Fundamentals

## 1.1 What is a Lock?

A **lock** (also called mutex, monitor, or synchronization primitive) is a mechanism that enforces mutual exclusion - ensuring only one thread/process can access a shared resource at a time.

```
WITHOUT LOCK:                    WITH LOCK:
─────────────                    ──────────
Thread A: read x (10)            Thread A: acquire lock
Thread B: read x (10)                      read x (10)
Thread A: write x = 11                     write x = 11
Thread B: write x = 11                     release lock
Result: x = 11 (WRONG!)          Thread B: acquire lock
Expected: x = 12                           read x (11)
                                           write x = 12
                                           release lock
                                 Result: x = 12 (CORRECT!)
```

## 1.2 Lock Properties

| Property | Description |
|----------|-------------|
| **Mutual Exclusion** | Only one holder at a time |
| **Progress** | If no one holds lock, someone can acquire it |
| **Bounded Waiting** | No starvation - everyone eventually gets the lock |
| **Deadlock Freedom** | System doesn't get stuck |

## 1.3 Lock Classification

```
┌─────────────────────────────────────────────────────────────────┐
│                      LOCK TAXONOMY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  BY STRATEGY          BY SCOPE            BY BEHAVIOR           │
│  ───────────          ─────────           ───────────           │
│  • Pessimistic        • Process-local     • Blocking            │
│  • Optimistic         • Thread-local      • Non-blocking        │
│                       • Inter-process     • Spin                 │
│                       • Distributed       • Hybrid               │
│                                                                  │
│  BY MODE              BY GRANULARITY      BY FAIRNESS           │
│  ───────              ──────────────      ───────────           │
│  • Exclusive (X)      • Fine-grained      • Fair (FIFO)         │
│  • Shared (S)         • Coarse-grained    • Unfair              │
│  • Intent (IX/IS)     • Hierarchical      • Reader-preferred    │
│  • Update (U)                             • Writer-preferred    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# 2. Application-Level Locks

## 2.1 Mutex (Mutual Exclusion Lock)

The most basic lock - binary state (locked/unlocked), single owner.

### Characteristics
- **Binary**: Either locked or unlocked
- **Owned**: Only the thread that acquired can release
- **Blocking**: Waiters sleep until lock available

### Implementation

```python
import threading

# Basic mutex
mutex = threading.Lock()

counter = 0

def increment():
    global counter
    mutex.acquire()      # Block until acquired
    try:
        counter += 1     # Critical section
    finally:
        mutex.release()  # Always release

# Context manager (preferred)
def increment_safe():
    global counter
    with mutex:          # Auto acquire/release
        counter += 1
```

```java
// Java
import java.util.concurrent.locks.ReentrantLock;

ReentrantLock mutex = new ReentrantLock();

public void increment() {
    mutex.lock();
    try {
        counter++;
    } finally {
        mutex.unlock();
    }
}
```

```go
// Go
import "sync"

var mutex sync.Mutex
var counter int

func increment() {
    mutex.Lock()
    defer mutex.Unlock()
    counter++
}
```

```c
// C with pthreads
#include <pthread.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
int counter = 0;

void* increment(void* arg) {
    pthread_mutex_lock(&mutex);
    counter++;
    pthread_mutex_unlock(&mutex);
    return NULL;
}
```

### When to Use
- Protecting shared mutable state
- Simple critical sections
- When you need ownership semantics

---

## 2.2 Reentrant Lock (Recursive Mutex)

A mutex that can be acquired multiple times by the **same thread**.

### Problem Reentrant Locks Solve

```python
# DEADLOCK with regular mutex!
mutex = threading.Lock()

def outer():
    with mutex:
        print("outer")
        inner()         # Tries to acquire same lock = DEADLOCK

def inner():
    with mutex:         # Already held by this thread!
        print("inner")
```

### Solution: Reentrant Lock

```python
import threading

rlock = threading.RLock()  # Reentrant lock

def outer():
    with rlock:
        print("outer")
        inner()           # Same thread can reacquire

def inner():
    with rlock:           # Succeeds! Same thread already holds it
        print("inner")

# Output:
# outer
# inner
```

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    REENTRANT LOCK STATE                          │
├─────────────────────────────────────────────────────────────────┤
│  owner: Thread-1                                                 │
│  count: 2          (acquired twice by same thread)               │
│                                                                  │
│  Thread-1: acquire() → count=1                                   │
│  Thread-1: acquire() → count=2  (allowed, same owner)            │
│  Thread-1: release() → count=1                                   │
│  Thread-1: release() → count=0, owner=None (truly released)      │
└─────────────────────────────────────────────────────────────────┘
```

```java
// Java ReentrantLock
import java.util.concurrent.locks.ReentrantLock;

ReentrantLock lock = new ReentrantLock();

public void outer() {
    lock.lock();
    try {
        System.out.println("outer, hold count: " + lock.getHoldCount()); // 1
        inner();
    } finally {
        lock.unlock();
    }
}

public void inner() {
    lock.lock();
    try {
        System.out.println("inner, hold count: " + lock.getHoldCount()); // 2
    } finally {
        lock.unlock();
    }
}
```

### When to Use
- Recursive algorithms that need synchronization
- When calling other synchronized methods from synchronized code
- Simplifying lock management in complex call hierarchies

---

## 2.3 Read-Write Lock (RWLock / Shared-Exclusive Lock)

Allows **multiple concurrent readers** OR **single exclusive writer**.

### Motivation

```
Regular Mutex:               RWLock:
Reader 1: [====]             Reader 1: [====]
Reader 2:       [====]       Reader 2: [====]  ← Concurrent!
Reader 3:             [====] Reader 3: [====]  ← Concurrent!

3 readers take 3x time       3 readers finish together
```

### Compatibility Matrix

```
         ┌─────────────────────────────────┐
         │      Lock Currently Held        │
         ├─────────┬───────────┬───────────┤
         │  None   │  Read(S)  │  Write(X) │
┌────────┼─────────┼───────────┼───────────┤
│Request │         │           │           │
│ Read   │    ✓    │     ✓     │     ✗     │
│ Write  │    ✓    │     ✗     │     ✗     │
└────────┴─────────┴───────────┴───────────┘
```

### Implementation

```python
import threading

class ReadWriteLock:
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0
        self._writers_waiting = 0
        self._writer_active = False
    
    def acquire_read(self):
        """Acquire read lock - multiple readers allowed"""
        with self._read_ready:
            # Wait if writer is active or writers are waiting (writer preference)
            while self._writer_active or self._writers_waiting > 0:
                self._read_ready.wait()
            self._readers += 1
    
    def release_read(self):
        """Release read lock"""
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()  # Wake waiting writers
    
    def acquire_write(self):
        """Acquire write lock - exclusive access"""
        with self._read_ready:
            self._writers_waiting += 1
            # Wait until no readers and no active writer
            while self._readers > 0 or self._writer_active:
                self._read_ready.wait()
            self._writers_waiting -= 1
            self._writer_active = True
    
    def release_write(self):
        """Release write lock"""
        with self._read_ready:
            self._writer_active = False
            self._read_ready.notify_all()  # Wake all waiters


# Usage
rwlock = ReadWriteLock()
cache = {}

def read_cache(key):
    rwlock.acquire_read()
    try:
        return cache.get(key)
    finally:
        rwlock.release_read()

def write_cache(key, value):
    rwlock.acquire_write()
    try:
        cache[key] = value
    finally:
        rwlock.release_write()
```

```java
// Java ReadWriteLock
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

ReadWriteLock rwLock = new ReentrantReadWriteLock();
Map<String, String> cache = new HashMap<>();

public String read(String key) {
    rwLock.readLock().lock();
    try {
        return cache.get(key);
    } finally {
        rwLock.readLock().unlock();
    }
}

public void write(String key, String value) {
    rwLock.writeLock().lock();
    try {
        cache.put(key, value);
    } finally {
        rwLock.writeLock().unlock();
    }
}
```

```go
// Go RWMutex
import "sync"

var rwMutex sync.RWMutex
var cache = make(map[string]string)

func read(key string) string {
    rwMutex.RLock()         // Read lock
    defer rwMutex.RUnlock()
    return cache[key]
}

func write(key, value string) {
    rwMutex.Lock()          // Write lock
    defer rwMutex.Unlock()
    cache[key] = value
}
```

### Fairness Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| **Reader-preferred** | Readers never wait for readers | Read-heavy, starvation risk for writers |
| **Writer-preferred** | New readers wait if writer waiting | Write-heavy, starvation risk for readers |
| **Fair** | FIFO ordering | Balanced workload |

### When to Use
- Read-heavy workloads (caches, config, lookup tables)
- When reads significantly outnumber writes
- When read operations are expensive

---

## 2.4 Semaphore

A lock with a **counter** - allows N concurrent accesses.

### Types

| Type | Initial Count | Use Case |
|------|---------------|----------|
| **Binary Semaphore** | 1 | Same as mutex |
| **Counting Semaphore** | N | Resource pools |
| **Bounded Semaphore** | N (can't exceed) | Strict resource limiting |

### Implementation

```python
import threading

# Counting semaphore - allow 5 concurrent DB connections
connection_semaphore = threading.Semaphore(5)

def query_database(sql):
    connection_semaphore.acquire()  # Blocks if 5 already acquired
    try:
        conn = get_connection()
        return conn.execute(sql)
    finally:
        connection_semaphore.release()

# Bounded semaphore - error if release more than acquired
bounded = threading.BoundedSemaphore(5)
# bounded.release() without acquire → raises ValueError
```

```java
// Java Semaphore
import java.util.concurrent.Semaphore;

Semaphore connectionPool = new Semaphore(5);

public Result queryDatabase(String sql) throws InterruptedException {
    connectionPool.acquire();  // or tryAcquire() for non-blocking
    try {
        Connection conn = getConnection();
        return conn.execute(sql);
    } finally {
        connectionPool.release();
    }
}

// Try with timeout
if (connectionPool.tryAcquire(5, TimeUnit.SECONDS)) {
    try {
        // use resource
    } finally {
        connectionPool.release();
    }
} else {
    // timeout - resource not available
}
```

### Semaphore vs Mutex

| Aspect | Mutex | Semaphore |
|--------|-------|-----------|
| Count | Binary (0 or 1) | Any N |
| Ownership | Thread that locked must unlock | Any thread can release |
| Use case | Mutual exclusion | Resource counting |
| Recursion | May support (reentrant) | Not applicable |

### Producer-Consumer with Semaphore

```python
import threading
import queue

class BoundedBuffer:
    def __init__(self, capacity):
        self.buffer = queue.Queue(maxsize=capacity)
        self.empty_slots = threading.Semaphore(capacity)  # Available slots
        self.filled_slots = threading.Semaphore(0)        # Items ready
        self.mutex = threading.Lock()                      # Buffer access
    
    def produce(self, item):
        self.empty_slots.acquire()    # Wait for empty slot
        with self.mutex:
            self.buffer.put(item)
        self.filled_slots.release()   # Signal item available
    
    def consume(self):
        self.filled_slots.acquire()   # Wait for item
        with self.mutex:
            item = self.buffer.get()
        self.empty_slots.release()    # Signal slot freed
        return item
```

---

## 2.5 Spin Lock

A lock where waiters **busy-wait** (spin) instead of sleeping.

### How It Works

```c
// Spin lock in C
typedef struct {
    volatile int locked;
} spinlock_t;

void spin_lock(spinlock_t *lock) {
    while (__sync_lock_test_and_set(&lock->locked, 1)) {
        // Spin! Keep trying
        while (lock->locked) {
            __builtin_ia32_pause();  // CPU hint: we're spinning
        }
    }
}

void spin_unlock(spinlock_t *lock) {
    __sync_lock_release(&lock->locked);
}
```

### Spin Lock vs Blocking Lock

```
BLOCKING LOCK:                    SPIN LOCK:
Thread acquires lock              Thread acquires lock
  │                                 │
Other thread waits:               Other thread waits:
  → Context switch (expensive)      → Busy loop (CPU cycles)
  → Sleep                           → Keep checking
  → Wake up (expensive)             → Immediate acquisition
  │                                 │
Good for: long critical sections  Good for: very short critical sections
```

### When to Use Spin Locks

| Use Spin Lock | Use Blocking Lock |
|---------------|-------------------|
| Critical section < 1μs | Critical section > 1μs |
| Multi-core guaranteed | Single core possible |
| Kernel/driver code | Application code |
| Low contention | High contention |
| Can't sleep (interrupt context) | Can sleep |

### Adaptive Spin Lock

Modern approach: spin for a bit, then block.

```java
// Java's synchronized uses adaptive spinning
// Pseudocode:
void adaptiveLock() {
    int spins = 0;
    while (!tryAcquire()) {
        if (spins++ < MAX_SPINS) {
            Thread.onSpinWait();  // Spin
        } else {
            park();              // Block (sleep)
            spins = 0;
        }
    }
}
```

---

## 2.6 Condition Variable

Not a lock itself, but used **with** a lock for thread signaling.

### The Problem

```python
# BAD: Busy waiting
while not condition_met():
    pass  # Wastes CPU!

# GOOD: Wait on condition
with lock:
    while not condition_met():
        condition.wait()  # Sleep until signaled
```

### Implementation

```python
import threading

class BoundedQueue:
    def __init__(self, capacity):
        self.queue = []
        self.capacity = capacity
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
    
    def put(self, item):
        with self.not_full:
            while len(self.queue) >= self.capacity:
                self.not_full.wait()      # Wait until not full
            self.queue.append(item)
            self.not_empty.notify()       # Signal item available
    
    def get(self):
        with self.not_empty:
            while len(self.queue) == 0:
                self.not_empty.wait()     # Wait until not empty
            item = self.queue.pop(0)
            self.not_full.notify()        # Signal space available
            return item
```

```java
// Java Condition
import java.util.concurrent.locks.*;

class BoundedQueue<T> {
    private final Queue<T> queue = new LinkedList<>();
    private final int capacity;
    private final Lock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();
    
    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() >= capacity) {
                notFull.await();          // Release lock and wait
            }
            queue.add(item);
            notEmpty.signal();            // Wake one waiter
        } finally {
            lock.unlock();
        }
    }
    
    public T get() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();
            }
            T item = queue.remove();
            notFull.signal();
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

### Important: Always Use While Loop!

```python
# WRONG: if statement
with lock:
    if not condition_met():
        condition.wait()
    # BUG: condition may not be true here (spurious wakeup!)

# CORRECT: while loop
with lock:
    while not condition_met():
        condition.wait()
    # Guaranteed: condition is true here
```

---

## 2.7 Barrier (Synchronization Barrier)

Makes threads wait until **all** threads reach a point.

```
Thread 1: ════════════╗
Thread 2: ════════╗   ║
Thread 3: ══════════╗ ║    All continue
Thread 4: ════╗     ║ ║         ↓
              ║     ║ ║    ════════════
              ╚═════╩═╩═══►  BARRIER
```

### Implementation

```python
import threading

barrier = threading.Barrier(4)  # Wait for 4 threads

def worker(id):
    print(f"Worker {id}: doing phase 1")
    # ... work ...
    
    barrier.wait()  # Wait for all 4 threads
    
    print(f"Worker {id}: doing phase 2")
    # ... work ...

threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()
```

```java
// Java CyclicBarrier
import java.util.concurrent.CyclicBarrier;

CyclicBarrier barrier = new CyclicBarrier(4, () -> {
    System.out.println("All threads reached barrier!");
});

public void worker(int id) throws Exception {
    System.out.println("Worker " + id + ": phase 1");
    barrier.await();  // Wait for all
    System.out.println("Worker " + id + ": phase 2");
}
```

### Use Cases
- Parallel algorithms with phases
- Testing concurrent code
- Matrix computations, simulations

---

## 2.8 Latch (CountDownLatch)

One-time barrier: threads wait until count reaches zero.

```python
import threading

class CountDownLatch:
    def __init__(self, count):
        self.count = count
        self.lock = threading.Condition()
    
    def count_down(self):
        with self.lock:
            self.count -= 1
            if self.count <= 0:
                self.lock.notify_all()
    
    def await(self):
        with self.lock:
            while self.count > 0:
                self.lock.wait()


# Usage: Wait for 3 services to be ready
startup_latch = CountDownLatch(3)

def service_init(name):
    print(f"{name} starting...")
    time.sleep(random.random())
    print(f"{name} ready!")
    startup_latch.count_down()

def main_app():
    startup_latch.await()  # Wait for all services
    print("All services ready, starting main app!")
```

```java
// Java CountDownLatch
import java.util.concurrent.CountDownLatch;

CountDownLatch latch = new CountDownLatch(3);

// Worker threads
new Thread(() -> {
    doWork();
    latch.countDown();
}).start();

// Main thread waits
latch.await();  // Blocks until count = 0
System.out.println("All workers done!");
```

---

## 2.9 StampedLock (Java)

Optimistic read lock with upgrade capability.

```java
import java.util.concurrent.locks.StampedLock;

StampedLock lock = new StampedLock();
double x, y;

// Optimistic read (no lock, just a stamp)
public double distanceFromOrigin() {
    long stamp = lock.tryOptimisticRead();  // No actual lock!
    double currentX = x, currentY = y;
    
    if (!lock.validate(stamp)) {  // Check if write occurred
        // Fallback to regular read lock
        stamp = lock.readLock();
        try {
            currentX = x;
            currentY = y;
        } finally {
            lock.unlockRead(stamp);
        }
    }
    return Math.sqrt(currentX * currentX + currentY * currentY);
}

// Write lock
public void move(double deltaX, double deltaY) {
    long stamp = lock.writeLock();
    try {
        x += deltaX;
        y += deltaY;
    } finally {
        lock.unlockWrite(stamp);
    }
}

// Upgrade read to write
public void moveIfAt(double expectedX, double expectedY, double newX, double newY) {
    long stamp = lock.readLock();
    try {
        while (x == expectedX && y == expectedY) {
            long writeStamp = lock.tryConvertToWriteLock(stamp);
            if (writeStamp != 0L) {
                stamp = writeStamp;
                x = newX;
                y = newY;
                break;
            } else {
                lock.unlockRead(stamp);
                stamp = lock.writeLock();
            }
        }
    } finally {
        lock.unlock(stamp);
    }
}
```

---

# 3. Database Locks

## 3.1 Row-Level Locks

### Shared Lock (S-Lock / Read Lock)

```sql
-- PostgreSQL
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- MySQL
SELECT * FROM accounts WHERE id = 1 FOR SHARE;          -- MySQL 8.0+
SELECT * FROM accounts WHERE id = 1 LOCK IN SHARE MODE; -- Older
```

**Properties:**
- Multiple transactions can hold S-lock on same row
- Blocks X-locks (writes)
- Released based on isolation level

### Exclusive Lock (X-Lock / Write Lock)

```sql
-- All databases
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- Implicit on write operations
UPDATE accounts SET balance = 100 WHERE id = 1;
DELETE FROM accounts WHERE id = 1;
```

**Properties:**
- Only one transaction can hold X-lock
- Blocks both S-locks and X-locks
- Held until transaction commits

### Lock Variants (PostgreSQL)

```sql
-- FOR UPDATE: Strongest, blocks all
SELECT * FROM t WHERE id = 1 FOR UPDATE;

-- FOR NO KEY UPDATE: Allows foreign key checks
SELECT * FROM t WHERE id = 1 FOR NO KEY UPDATE;

-- FOR SHARE: Multiple readers
SELECT * FROM t WHERE id = 1 FOR SHARE;

-- FOR KEY SHARE: Weakest, only prevents key changes
SELECT * FROM t WHERE id = 1 FOR KEY SHARE;
```

### Non-Blocking Options

```sql
-- NOWAIT: Error immediately if locked
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;

-- SKIP LOCKED: Skip locked rows (great for job queues)
SELECT * FROM jobs 
WHERE status = 'pending' 
ORDER BY created_at 
LIMIT 10 
FOR UPDATE SKIP LOCKED;
```

---

## 3.2 Table-Level Locks

### PostgreSQL Table Lock Modes

```sql
-- From weakest to strongest:
LOCK TABLE t IN ACCESS SHARE MODE;           -- SELECT
LOCK TABLE t IN ROW SHARE MODE;              -- SELECT FOR UPDATE/SHARE
LOCK TABLE t IN ROW EXCLUSIVE MODE;          -- UPDATE, DELETE, INSERT
LOCK TABLE t IN SHARE UPDATE EXCLUSIVE MODE; -- VACUUM, some ALTER
LOCK TABLE t IN SHARE MODE;                  -- CREATE INDEX (non-concurrent)
LOCK TABLE t IN SHARE ROW EXCLUSIVE MODE;    -- CREATE TRIGGER, some ALTER
LOCK TABLE t IN EXCLUSIVE MODE;              -- Blocks everything except SELECT
LOCK TABLE t IN ACCESS EXCLUSIVE MODE;       -- Blocks everything (DDL, TRUNCATE)
```

### MySQL Table Locks

```sql
-- Explicit table locks
LOCK TABLES 
    orders WRITE,      -- Exclusive
    products READ;     -- Shared

-- Do work...

UNLOCK TABLES;
```

### Compatibility Matrix (PostgreSQL)

```
                  │ AS │ RS │ RE │ SUE │ S │ SRE │ E │ AE │
──────────────────┼────┼────┼────┼─────┼───┼─────┼───┼────┤
ACCESS SHARE      │ ✓  │ ✓  │ ✓  │  ✓  │ ✓ │  ✓  │ ✓ │ ✗  │
ROW SHARE         │ ✓  │ ✓  │ ✓  │  ✓  │ ✓ │  ✓  │ ✗ │ ✗  │
ROW EXCLUSIVE     │ ✓  │ ✓  │ ✓  │  ✓  │ ✗ │  ✗  │ ✗ │ ✗  │
SHARE UPDATE EXCL │ ✓  │ ✓  │ ✓  │  ✗  │ ✗ │  ✗  │ ✗ │ ✗  │
SHARE             │ ✓  │ ✓  │ ✗  │  ✗  │ ✓ │  ✗  │ ✗ │ ✗  │
SHARE ROW EXCL    │ ✓  │ ✓  │ ✗  │  ✗  │ ✗ │  ✗  │ ✗ │ ✗  │
EXCLUSIVE         │ ✓  │ ✗  │ ✗  │  ✗  │ ✗ │  ✗  │ ✗ │ ✗  │
ACCESS EXCLUSIVE  │ ✗  │ ✗  │ ✗  │  ✗  │ ✗ │  ✗  │ ✗ │ ✗  │
```

---

## 3.3 Gap Locks (MySQL/InnoDB)

Locks the "gap" between index records to prevent phantom reads.

```sql
-- Existing rows: id = 10, 20, 30

SELECT * FROM t WHERE id BETWEEN 15 AND 25 FOR UPDATE;

-- Locks:
-- 1. Row lock on id = 20
-- 2. Gap lock on (10, 20)  ← Prevents INSERT of id = 15
-- 3. Gap lock on (20, 30)  ← Prevents INSERT of id = 25
```

```
Index:  ──10────────20────────30──
             │      │      │
Gap locks:   └(gap)─┴(gap)─┘
```

### Next-Key Lock

Combination of row lock + gap lock (InnoDB default at REPEATABLE READ).

```sql
-- Next-key lock on id = 20 includes:
-- 1. Record lock on id = 20
-- 2. Gap lock on (10, 20]
```

---

## 3.4 Intent Locks

Signal intention to lock at a finer granularity.

```
┌───────────────────────────────────────┐
│              DATABASE                  │
│  ┌─────────────────────────────────┐  │
│  │         TABLE (IX)              │  │  ← Intent Exclusive on table
│  │  ┌───────────────────────────┐  │  │
│  │  │       PAGE (IX)           │  │  │  ← Intent Exclusive on page
│  │  │  ┌─────────────────────┐  │  │  │
│  │  │  │     ROW (X)         │  │  │  │  ← Actual Exclusive on row
│  │  │  └─────────────────────┘  │  │  │
│  │  └───────────────────────────┘  │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
```

| Lock | Meaning |
|------|---------|
| **IS** (Intent Shared) | Will acquire S-lock on descendant |
| **IX** (Intent Exclusive) | Will acquire X-lock on descendant |
| **SIX** (Shared + Intent Exclusive) | S-lock on this, X-lock on descendant |

### Why Intent Locks?

Without intent locks, to take a table X-lock, you'd need to check every row.
With intent locks, just check the table's intent lock!

---

## 3.5 Advisory Locks

Application-controlled locks using arbitrary keys.

### PostgreSQL Advisory Locks

```sql
-- Session-level locks (held until released or session ends)
SELECT pg_advisory_lock(12345);           -- Blocking
SELECT pg_try_advisory_lock(12345);       -- Non-blocking, returns bool
SELECT pg_advisory_unlock(12345);         -- Release

-- Transaction-level (auto-released on commit/rollback)
SELECT pg_advisory_xact_lock(12345);

-- Two-argument form (namespace, key)
SELECT pg_advisory_lock(1, 123);  -- Class 1, object 123
```

### Use Case: Distributed Job Processing

```python
def process_job(job_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Try to get exclusive lock on this job
        cursor.execute("SELECT pg_try_advisory_lock(%s)", (job_id,))
        acquired = cursor.fetchone()[0]
        
        if not acquired:
            return "Job being processed by another worker"
        
        try:
            # Process job (we have exclusive access)
            do_work(job_id)
            return "Job completed"
        finally:
            cursor.execute("SELECT pg_advisory_unlock(%s)", (job_id,))
```

### MySQL GET_LOCK

```sql
-- Acquire named lock (blocking with timeout)
SELECT GET_LOCK('my_lock', 10);  -- 10 second timeout

-- Check if locked
SELECT IS_FREE_LOCK('my_lock');

-- Release
SELECT RELEASE_LOCK('my_lock');

-- Release all locks for session
SELECT RELEASE_ALL_LOCKS();
```

---

## 3.6 Predicate Locks

Lock all rows matching a condition, including future rows.

```sql
-- Conceptually (not explicit SQL):
-- Lock all rows where status = 'pending'
LOCK PREDICATE (status = 'pending');

-- Any INSERT with status = 'pending' would be blocked
```

Used internally by SERIALIZABLE isolation to prevent phantoms.

---

## 3.7 Optimistic Locking (Version-Based)

Not a real lock - conflict detection at write time.

```sql
-- Add version column
ALTER TABLE products ADD COLUMN version INT DEFAULT 0;

-- Read
SELECT id, name, price, version FROM products WHERE id = 1;
-- Returns: id=1, name='Widget', price=10.00, version=5

-- Update with version check
UPDATE products 
SET price = 12.00, version = version + 1
WHERE id = 1 AND version = 5;

-- If rows_affected = 0, someone else modified it → retry
```

### Implementation

```python
def update_product_optimistic(product_id, new_price, max_retries=3):
    for attempt in range(max_retries):
        with db.connection() as conn:
            # Read current version
            row = conn.execute(
                "SELECT price, version FROM products WHERE id = %s",
                (product_id,)
            ).fetchone()
            
            if not row:
                raise NotFoundError()
            
            current_price, version = row
            
            # Try to update
            result = conn.execute("""
                UPDATE products 
                SET price = %s, version = version + 1
                WHERE id = %s AND version = %s
            """, (new_price, product_id, version))
            
            if result.rowcount > 0:
                conn.commit()
                return True  # Success!
            
            # Version mismatch - retry
            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
    
    raise ConcurrentModificationError("Max retries exceeded")
```

---

# 4. Distributed Locks

## 4.1 Redis SETNX Lock

Simple single-node lock using SET with NX (Not eXists).

```python
import redis
import uuid
import time

class RedisLock:
    def __init__(self, redis_client, name, ttl_seconds=30):
        self.redis = redis_client
        self.name = f"lock:{name}"
        self.ttl = ttl_seconds
        self.token = str(uuid.uuid4())  # Unique owner identifier
    
    def acquire(self, blocking=True, timeout=None):
        """Acquire the lock"""
        start = time.time()
        
        while True:
            # SET with NX (only if not exists) and EX (expiry)
            acquired = self.redis.set(
                self.name,
                self.token,
                nx=True,
                ex=self.ttl
            )
            
            if acquired:
                return True
            
            if not blocking:
                return False
            
            if timeout and (time.time() - start) >= timeout:
                return False
            
            time.sleep(0.1)  # Brief sleep before retry
    
    def release(self):
        """Release the lock (only if we own it)"""
        # Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        return self.redis.eval(lua_script, 1, self.name, self.token)
    
    def extend(self, additional_seconds):
        """Extend lock TTL (if we still own it)"""
        lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("PEXPIRE", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        return self.redis.eval(
            lua_script, 1, 
            self.name, self.token, 
            int(additional_seconds * 1000)
        )
    
    def __enter__(self):
        if not self.acquire():
            raise LockError("Could not acquire lock")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# Usage
redis_client = redis.Redis()

with RedisLock(redis_client, "order:123") as lock:
    # Critical section
    process_order(123)
```

### Why Lua Script for Release?

```python
# BAD: Race condition!
if redis.get("lock:x") == my_token:
    # Another process could acquire lock here!
    redis.delete("lock:x")  # Deletes wrong owner's lock!

# GOOD: Atomic check-and-delete with Lua
lua_script = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
end
return 0
"""
```

---

## 4.2 Redlock Algorithm

Distributed lock across multiple independent Redis nodes.

### Algorithm

```
1. Get current time in milliseconds
2. Try to acquire lock on all N nodes sequentially
3. Calculate elapsed time
4. Lock acquired if:
   - Acquired on majority (N/2 + 1) nodes
   - Total elapsed time < lock TTL
5. If failed, release lock on all nodes
```

```python
import redis
import time
import uuid

class Redlock:
    def __init__(self, redis_connections, lock_name, ttl_ms=30000):
        self.servers = redis_connections  # List of Redis clients
        self.lock_name = f"lock:{lock_name}"
        self.ttl_ms = ttl_ms
        self.token = str(uuid.uuid4())
        self.quorum = len(self.servers) // 2 + 1
        self.clock_drift_factor = 0.01
    
    def acquire(self):
        start_time = time.time() * 1000
        
        # Try to acquire on all servers
        acquired_count = 0
        for server in self.servers:
            try:
                if self._acquire_single(server):
                    acquired_count += 1
            except redis.RedisError:
                pass  # Server unavailable
        
        # Calculate validity
        elapsed = time.time() * 1000 - start_time
        drift = self.ttl_ms * self.clock_drift_factor + 2
        validity_time = self.ttl_ms - elapsed - drift
        
        # Check if we got quorum with enough validity time
        if acquired_count >= self.quorum and validity_time > 0:
            return True
        else:
            # Failed - release all
            self._release_all()
            return False
    
    def _acquire_single(self, server):
        return server.set(
            self.lock_name,
            self.token,
            nx=True,
            px=self.ttl_ms
        )
    
    def _release_all(self):
        for server in self.servers:
            try:
                self._release_single(server)
            except redis.RedisError:
                pass
    
    def _release_single(self, server):
        lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        end
        return 0
        """
        server.eval(lua_script, 1, self.lock_name, self.token)


# Usage with 5 independent Redis servers
servers = [
    redis.Redis(host='redis1'),
    redis.Redis(host='redis2'),
    redis.Redis(host='redis3'),
    redis.Redis(host='redis4'),
    redis.Redis(host='redis5'),
]

lock = Redlock(servers, "my-resource")
if lock.acquire():
    try:
        do_work()
    finally:
        lock._release_all()
```

---

## 4.3 ZooKeeper Lock

Uses ephemeral sequential nodes for strong consistency.

### How It Works

```
/locks/my-resource/
  ├── lock-0000000001  ← Client A (smallest = holds lock)
  ├── lock-0000000002  ← Client B (watches 001)
  └── lock-0000000003  ← Client C (watches 002)

When Client A releases (or dies):
  - Node 001 deleted automatically (ephemeral)
  - Client B gets watch notification
  - Client B checks if it's now smallest → acquires lock
```

### Implementation (Python with Kazoo)

```python
from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock

# Connect to ZooKeeper
zk = KazooClient(hosts='127.0.0.1:2181')
zk.start()

# Create lock
lock = Lock(zk, "/locks/my-resource")

# Blocking acquire
with lock:
    # Critical section
    do_work()

# Non-blocking
if lock.acquire(blocking=False):
    try:
        do_work()
    finally:
        lock.release()
else:
    print("Could not acquire lock")

# With timeout
if lock.acquire(timeout=5):
    try:
        do_work()
    finally:
        lock.release()
```

### Manual Implementation

```python
from kazoo.client import KazooClient
import threading

class ZooKeeperLock:
    def __init__(self, zk_client, path):
        self.zk = zk_client
        self.path = path
        self.node = None
        self.event = threading.Event()
    
    def acquire(self):
        # Ensure parent path exists
        self.zk.ensure_path(self.path)
        
        # Create ephemeral sequential node
        self.node = self.zk.create(
            f"{self.path}/lock-",
            ephemeral=True,
            sequence=True
        )
        
        while True:
            # Get all children (lock requests)
            children = sorted(self.zk.get_children(self.path))
            
            # Check if we're first (have the lock)
            my_name = self.node.split('/')[-1]
            my_index = children.index(my_name)
            
            if my_index == 0:
                return True  # We have the lock!
            
            # Watch the node before us
            predecessor = f"{self.path}/{children[my_index - 1]}"
            self.event.clear()
            
            if self.zk.exists(predecessor, watch=self._watch):
                self.event.wait()  # Wait for predecessor to be deleted
    
    def _watch(self, event):
        self.event.set()  # Wake up acquisition loop
    
    def release(self):
        if self.node:
            self.zk.delete(self.node)
            self.node = None
```

---

## 4.4 etcd Lock

Similar to ZooKeeper, uses leases for TTL.

```python
import etcd3

# Connect
client = etcd3.client(host='localhost', port=2379)

# Using built-in lock
lock = client.lock('my-resource', ttl=30)

with lock:
    # Critical section
    do_work()

# Manual approach with lease
lease = client.lease(ttl=30)
success, _ = client.transaction(
    compare=[client.transactions.create('/locks/my-resource') == 0],
    success=[client.transactions.put('/locks/my-resource', 'locked', lease=lease)],
    failure=[]
)

if success:
    try:
        do_work()
    finally:
        client.delete('/locks/my-resource')
```

---

## 4.5 Database-Based Distributed Lock

Using PostgreSQL advisory locks or a dedicated lock table.

### Using Advisory Locks

```python
def distributed_lock(resource_id):
    """Distributed lock using PostgreSQL advisory lock"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Hash resource ID to int64 for advisory lock
        lock_id = hash(resource_id) & 0x7FFFFFFFFFFFFFFF
        
        # Try to acquire (non-blocking)
        cursor.execute("SELECT pg_try_advisory_lock(%s)", (lock_id,))
        acquired = cursor.fetchone()[0]
        
        return acquired, conn, lock_id
    except:
        conn.close()
        raise

def release_lock(conn, lock_id):
    cursor = conn.cursor()
    cursor.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
    conn.close()
```

### Using Lock Table

```sql
CREATE TABLE distributed_locks (
    resource_id VARCHAR(255) PRIMARY KEY,
    owner_id VARCHAR(255) NOT NULL,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Acquire lock
INSERT INTO distributed_locks (resource_id, owner_id, expires_at)
VALUES ('order:123', 'worker-1', NOW() + INTERVAL '30 seconds')
ON CONFLICT (resource_id) DO UPDATE
SET owner_id = EXCLUDED.owner_id,
    acquired_at = EXCLUDED.acquired_at,
    expires_at = EXCLUDED.expires_at
WHERE distributed_locks.expires_at < NOW();  -- Only if expired

-- Release lock
DELETE FROM distributed_locks 
WHERE resource_id = 'order:123' AND owner_id = 'worker-1';

-- Cleanup expired locks (run periodically)
DELETE FROM distributed_locks WHERE expires_at < NOW();
```

---

## 4.6 Comparison of Distributed Locks

| System | Consistency | Availability | Latency | Best For |
|--------|-------------|--------------|---------|----------|
| **Redis SETNX** | Weak | High | <1ms | Simple cases, single node |
| **Redlock** | Medium | Medium | ~10ms | Multi-node Redis |
| **ZooKeeper** | Strong (CP) | Medium | ~10ms | Leader election, consensus |
| **etcd** | Strong (CP) | Medium | ~10ms | Kubernetes, distributed config |
| **PostgreSQL** | Strong | High | ~1ms | Existing Postgres infrastructure |
| **Consul** | Strong (CP) | Medium | ~10ms | Service mesh |

---

# 5. Hardware & OS Locks

## 5.1 Atomic Operations (CPU)

Hardware-supported atomic instructions.

### Test-And-Set (TAS)

```c
// Atomically: old = *ptr; *ptr = 1; return old;
int test_and_set(int *ptr) {
    return __sync_lock_test_and_set(ptr, 1);
}

// Spin lock using TAS
void spin_lock(int *lock) {
    while (test_and_set(lock) == 1) {
        // Spin
    }
}
```

### Compare-And-Swap (CAS)

```c
// Atomically: if (*ptr == expected) { *ptr = new; return true; } return false;
bool compare_and_swap(int *ptr, int expected, int new_value) {
    return __sync_bool_compare_and_swap(ptr, expected, new_value);
}

// Lock-free counter
void increment(int *counter) {
    int old_value, new_value;
    do {
        old_value = *counter;
        new_value = old_value + 1;
    } while (!compare_and_swap(counter, old_value, new_value));
}
```

### Fetch-And-Add

```c
// Atomically: old = *ptr; *ptr += value; return old;
int fetch_and_add(int *ptr, int value) {
    return __sync_fetch_and_add(ptr, value);
}

// Ticket lock
typedef struct {
    int ticket;
    int turn;
} ticket_lock_t;

void ticket_lock(ticket_lock_t *lock) {
    int my_ticket = fetch_and_add(&lock->ticket, 1);
    while (lock->turn != my_ticket) {
        // Wait for my turn
    }
}

void ticket_unlock(ticket_lock_t *lock) {
    fetch_and_add(&lock->turn, 1);
}
```

## 5.2 Memory Barriers / Fences

Prevent CPU reordering of memory operations.

```c
// Full barrier - no reordering across this point
__sync_synchronize();

// Store barrier - all stores before complete before stores after
__asm__ __volatile__("sfence" ::: "memory");

// Load barrier - all loads before complete before loads after
__asm__ __volatile__("lfence" ::: "memory");
```

## 5.3 Futex (Linux)

Fast userspace mutex - only syscall when contention.

```c
#include <linux/futex.h>
#include <sys/syscall.h>

// Simplified futex-based lock
typedef struct {
    int val;  // 0 = unlocked, 1 = locked no waiters, 2 = locked with waiters
} futex_lock_t;

void futex_lock(futex_lock_t *lock) {
    int c;
    if ((c = __sync_val_compare_and_swap(&lock->val, 0, 1)) != 0) {
        // Contention - need to wait
        do {
            if (c == 2 || __sync_val_compare_and_swap(&lock->val, 1, 2) != 0) {
                // Wait in kernel
                syscall(SYS_futex, &lock->val, FUTEX_WAIT, 2, NULL, NULL, 0);
            }
        } while ((c = __sync_val_compare_and_swap(&lock->val, 0, 2)) != 0);
    }
}

void futex_unlock(futex_lock_t *lock) {
    if (__sync_fetch_and_sub(&lock->val, 1) != 1) {
        lock->val = 0;
        syscall(SYS_futex, &lock->val, FUTEX_WAKE, 1, NULL, NULL, 0);
    }
}
```

---

# 6. Lock-Free & Wait-Free Alternatives

## 6.1 Lock-Free Data Structures

Operations may retry but always make progress system-wide.

### Lock-Free Stack

```python
import threading
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Node:
    value: Any
    next: Optional['Node'] = None

class LockFreeStack:
    def __init__(self):
        self._head = None
        self._lock = threading.Lock()  # For Python (no real CAS)
    
    def push(self, value):
        new_node = Node(value)
        while True:
            old_head = self._head
            new_node.next = old_head
            # CAS: if head unchanged, update it
            if self._cas_head(old_head, new_node):
                return
    
    def pop(self) -> Optional[Any]:
        while True:
            old_head = self._head
            if old_head is None:
                return None
            new_head = old_head.next
            if self._cas_head(old_head, new_head):
                return old_head.value
    
    def _cas_head(self, expected, new):
        # In real implementation, use atomic CAS
        with self._lock:
            if self._head is expected:
                self._head = new
                return True
            return False
```

```java
// Java with AtomicReference
import java.util.concurrent.atomic.AtomicReference;

public class LockFreeStack<T> {
    private final AtomicReference<Node<T>> head = new AtomicReference<>();
    
    private static class Node<T> {
        final T value;
        Node<T> next;
        
        Node(T value) { this.value = value; }
    }
    
    public void push(T value) {
        Node<T> newNode = new Node<>(value);
        Node<T> oldHead;
        do {
            oldHead = head.get();
            newNode.next = oldHead;
        } while (!head.compareAndSet(oldHead, newNode));
    }
    
    public T pop() {
        Node<T> oldHead;
        Node<T> newHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null;
            newHead = oldHead.next;
        } while (!head.compareAndSet(oldHead, newHead));
        return oldHead.value;
    }
}
```

## 6.2 Wait-Free Structures

Every operation completes in bounded steps.

```java
// Wait-free counter using AtomicLong
import java.util.concurrent.atomic.AtomicLong;

public class WaitFreeCounter {
    private final AtomicLong value = new AtomicLong(0);
    
    public void increment() {
        value.incrementAndGet();  // Single atomic operation
    }
    
    public long get() {
        return value.get();
    }
}
```

## 6.3 MVCC (Multi-Version Concurrency Control)

Readers see consistent snapshots without locks.

```python
class MVCCStore:
    def __init__(self):
        self.versions = {}  # key -> [(version, value), ...]
        self.current_version = 0
        self.lock = threading.Lock()
    
    def write(self, key, value):
        with self.lock:
            self.current_version += 1
            if key not in self.versions:
                self.versions[key] = []
            self.versions[key].append((self.current_version, value))
    
    def read(self, key, snapshot_version=None):
        """Read value at specific snapshot (no lock needed!)"""
        if snapshot_version is None:
            snapshot_version = self.current_version
        
        versions = self.versions.get(key, [])
        
        # Find latest version <= snapshot
        for version, value in reversed(versions):
            if version <= snapshot_version:
                return value
        return None
    
    def begin_transaction(self):
        """Start transaction with current snapshot"""
        return self.current_version
```

---

# 7. Lock Problems & Solutions

## 7.1 Deadlock

Two or more processes waiting for each other indefinitely.

```
Process A              Process B
──────────────         ──────────────
Lock resource X        Lock resource Y
     │                      │
     ▼                      ▼
Wait for Y ◄───────────► Wait for X
     │                      │
   BLOCKED               BLOCKED
     │                      │
     └──────DEADLOCK────────┘
```

### Deadlock Conditions (All Required)

1. **Mutual Exclusion**: Resources can't be shared
2. **Hold and Wait**: Process holds resource while waiting for another
3. **No Preemption**: Resources can't be forcibly taken
4. **Circular Wait**: Circular chain of processes waiting

### Solutions

**1. Lock Ordering (Prevent Circular Wait)**

```python
# BAD: Inconsistent ordering
def transfer_bad(from_acc, to_acc, amount):
    with lock(from_acc):      # Thread 1: lock A
        with lock(to_acc):    # Thread 1: wants B, Thread 2: has B, wants A
            # DEADLOCK!

# GOOD: Consistent ordering
def transfer_good(from_acc, to_acc, amount):
    first, second = sorted([from_acc, to_acc], key=lambda x: x.id)
    with lock(first):
        with lock(second):
            # Safe!
```

**2. Lock Timeout**

```python
def acquire_with_timeout(lock, timeout):
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError("Could not acquire lock")
    return acquired

# Usage
try:
    with timeout_lock(lock_a, 5):
        with timeout_lock(lock_b, 5):
            do_work()
except TimeoutError:
    # Handle timeout, retry later
    pass
```

**3. Try-Lock with Backoff**

```python
import random
import time

def try_acquire_both(lock_a, lock_b, max_retries=10):
    for attempt in range(max_retries):
        if lock_a.acquire(blocking=False):
            if lock_b.acquire(blocking=False):
                return True  # Got both!
            else:
                lock_a.release()  # Release and retry
        
        # Random backoff to break symmetry
        time.sleep(random.uniform(0.001, 0.01 * (2 ** attempt)))
    
    return False
```

**4. Deadlock Detection**

```python
class DeadlockDetector:
    def __init__(self):
        self.lock_graph = {}  # thread -> set of threads it's waiting for
    
    def waiting_for(self, waiter, holder):
        """Record that waiter is waiting for holder's lock"""
        if waiter not in self.lock_graph:
            self.lock_graph[waiter] = set()
        self.lock_graph[waiter].add(holder)
        
        if self._has_cycle():
            raise DeadlockError(f"Deadlock detected: {waiter} → {holder}")
    
    def _has_cycle(self):
        """Detect cycle using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.lock_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True  # Cycle!
            
            rec_stack.remove(node)
            return False
        
        for node in self.lock_graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False
```

## 7.2 Livelock

Processes keep changing state in response to each other but make no progress.

```
Person A              Person B
────────────          ────────────
Move left             Move right
     │                     │
     ▼                     ▼
See B, move right     See A, move left
     │                     │
     ▼                     ▼
See B, move left      See A, move right
     │                     │
     └───── FOREVER ───────┘
```

### Solution: Add Randomness

```python
import random
import time

def polite_lock_acquire(lock, other_lock):
    while True:
        if lock.acquire(blocking=False):
            if other_lock.acquire(blocking=False):
                return True
            lock.release()
        
        # Random delay breaks symmetry
        time.sleep(random.uniform(0.001, 0.1))
```

## 7.3 Starvation

A process never gets the resource due to unfair scheduling.

```
High Priority: [====][====][====][====]
High Priority: [====][====][====][====]
Low Priority:  waiting... waiting... waiting... (STARVED)
```

### Solution: Fair Locks

```python
import threading
import collections

class FairLock:
    """FIFO lock - first waiter gets lock first"""
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = collections.deque()
        self._owner = None
    
    def acquire(self):
        event = threading.Event()
        
        with self._lock:
            if self._owner is None and not self._queue:
                self._owner = threading.current_thread()
                return
            self._queue.append(event)
        
        event.wait()  # Wait for our turn
    
    def release(self):
        with self._lock:
            self._owner = None
            if self._queue:
                next_waiter = self._queue.popleft()
                self._owner = next_waiter
                next_waiter.set()  # Wake next in line
```

## 7.4 Priority Inversion

High-priority task blocked by low-priority task holding a lock.

```
High Priority:   [blocked waiting for lock...]
Medium Priority: [====running====][====running====]
Low Priority:    [holding lock............][release]
                       │                      │
                       └── Medium preempts ───┘
                          Low, prolonging wait
```

### Solution: Priority Inheritance

When high-priority task waits, temporarily boost low-priority task.

```python
class PriorityInheritanceLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._owner = None
        self._original_priority = None
    
    def acquire(self, thread_priority):
        while True:
            with self._lock:
                if self._owner is None:
                    self._owner = threading.current_thread()
                    self._original_priority = thread_priority
                    return
                
                # Boost owner's priority if waiter has higher priority
                if thread_priority > self._original_priority:
                    self._boost_priority(self._owner, thread_priority)
            
            time.sleep(0.001)  # Yield
    
    def release(self):
        with self._lock:
            self._restore_priority(self._owner, self._original_priority)
            self._owner = None
```

## 7.5 Lock Convoy

Multiple threads repeatedly contend for same lock in sequence.

```
Thread 1: [lock][work][unlock][lock][work][unlock]...
Thread 2: [wait...][lock][work][unlock][wait...][lock]...
Thread 3: [wait......][wait...][lock][work][unlock]...

All threads synchronized on same "heartbeat"
```

### Solution: Reduce Lock Granularity or Duration

```python
# BAD: Lock held during I/O
def process_bad(items):
    with lock:
        for item in items:
            result = slow_network_call(item)  # I/O under lock!
            save(result)

# GOOD: Minimize lock scope
def process_good(items):
    results = [slow_network_call(item) for item in items]  # I/O without lock
    with lock:
        for result in results:
            save(result)  # Only protect shared state
```

---

# 8. Choosing the Right Lock

## 8.1 Decision Flowchart

```
START
  │
  ▼
Is it single-threaded?
  │
  ├─Yes→ No lock needed!
  │
  ▼
Is it distributed (multiple machines)?
  │
  ├─Yes→ Need strong consistency?
  │         │
  │         ├─Yes→ ZooKeeper/etcd
  │         └─No→ Redis Lock
  │
  ▼
Is it read-heavy (>90% reads)?
  │
  ├─Yes→ RWLock or MVCC
  │
  ▼
Critical section < 1μs?
  │
  ├─Yes→ SpinLock (multi-core only)
  │
  ▼
Need recursive locking?
  │
  ├─Yes→ ReentrantLock
  │
  ▼
Need to limit concurrent access?
  │
  ├─Yes→ Semaphore
  │
  ▼
Basic Mutex
```

## 8.2 Quick Reference Table

| Scenario | Lock Type | Why |
|----------|-----------|-----|
| Simple critical section | Mutex | Basic, sufficient |
| Recursive calls | ReentrantLock | Same thread can reacquire |
| 90%+ reads | RWLock | Concurrent readers |
| Resource pool (N items) | Semaphore | Allow N concurrent |
| Very short critical section | SpinLock | Avoid context switch |
| Cross-service coordination | Redis/ZooKeeper | Distributed |
| Database rows | SELECT FOR UPDATE | DB handles it |
| Low contention updates | Optimistic lock | No blocking |
| Thread coordination | Condition Variable | Wait/notify |
| Phase synchronization | Barrier | Wait for all |

## 8.3 Performance Characteristics

| Lock Type | Uncontended Cost | Contended Cost | Memory |
|-----------|------------------|----------------|--------|
| Mutex | ~25ns | High (sleep/wake) | Low |
| SpinLock | ~10ns | High (CPU burn) | Lowest |
| RWLock | ~50ns | Medium | Medium |
| Semaphore | ~30ns | High | Low |
| Redis Lock | ~1ms | Low (distributed) | External |
| DB Lock | ~1ms | Medium | External |

## 8.4 Anti-Patterns to Avoid

```python
# 1. Lock held during I/O
with lock:
    data = network_call()  # DON'T!

# 2. Nested locks without ordering
with lock_a:
    with lock_b:  # Potential deadlock
        pass

# 3. Forgetting to release
lock.acquire()
process()  # If this throws, lock never released!
# FIX: Use try/finally or context manager

# 4. Busy waiting instead of condition variable
while not ready:
    pass  # Burns CPU!
# FIX: Use condition.wait()

# 5. Global lock for everything
global_lock = Lock()
def everything():
    with global_lock:  # Serializes all operations!
        pass
# FIX: Fine-grained locks
```

---

## Summary

| Category | Locks |
|----------|-------|
| **Application** | Mutex, ReentrantLock, RWLock, Semaphore, SpinLock, Condition, Barrier, Latch |
| **Database** | Row (S/X), Table, Gap, Intent, Advisory, Predicate, Optimistic |
| **Distributed** | Redis SETNX, Redlock, ZooKeeper, etcd, Consul, DB-based |
| **Hardware** | TAS, CAS, Fetch-And-Add, Memory Barriers, Futex |
| **Lock-Free** | CAS loops, Lock-free structures, MVCC |

---

*Last updated: January 2025*
