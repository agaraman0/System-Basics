# Concurrency in Low-Level Design Interviews

> A comprehensive guide to the three categories of concurrency problems: Correctness, Coordination, and Scarcity. Master these patterns and you'll handle any concurrency challenge in interviews.

---

## Table of Contents

1. [Overview: The Three Categories](#1-overview-the-three-categories)
2. [Category 1: Correctness](#2-category-1-correctness)
3. [Category 2: Coordination](#3-category-2-coordination)
4. [Category 3: Scarcity](#4-category-3-scarcity)
5. [Mental Checklist for Interviews](#5-mental-checklist-for-interviews)
6. [Common Interview Problems](#6-common-interview-problems)
7. [Quick Reference](#7-quick-reference)

---

# 1. Overview: The Three Categories

When concurrency comes up in low-level design interviews, problems fall into **three main categories**:

```
┌─────────────────────────────────────────────────────────────────┐
│              THREE CATEGORIES OF CONCURRENCY                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. CORRECTNESS                                                  │
│     └── Shared state gets corrupted by concurrent access        │
│     └── Tools: Locks, Atomic Variables                          │
│                                                                  │
│  2. COORDINATION                                                 │
│     └── Work flows from one thread to another                   │
│     └── Tools: Blocking Queues, Bounded Queues                  │
│                                                                  │
│  3. SCARCITY                                                     │
│     └── Limited resources need to be shared                     │
│     └── Tools: Semaphores, Connection Pools                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Once you recognize which category a problem falls into, the solution becomes straightforward.

---

# 2. Category 1: Correctness

## 2.1 The Problem

Correctness issues happen when **shared state gets corrupted** because two threads access it at the same time.

### Example: Ticket Booking Service

```java
// Java - This code has a BUG!
public class BookingService {
    private Map<String, Seat> seats = new HashMap<>();
    
    public boolean bookSeat(String seatId, String userId) {
        Seat seat = seats.get(seatId);
        
        if (seat.isAvailable()) {      // CHECK
            seat.book(userId);          // ACT
            return true;
        }
        return false;
    }
}
```

```python
# Python - This code has a BUG!
class BookingService:
    def __init__(self):
        self.seats = {}
    
    def book_seat(self, seat_id: str, user_id: str) -> bool:
        seat = self.seats[seat_id]
        
        if seat.is_available():        # CHECK
            seat.book(user_id)          # ACT
            return True
        return False
```

### What Goes Wrong

```
Thread A (Alice)              Thread B (Bob)
─────────────────             ─────────────────
Check: Is seat 7A available?
→ Yes!
                              Check: Is seat 7A available?
                              → Yes! (Alice hasn't booked yet)

Book seat 7A for Alice
                              Book seat 7A for Bob
                              → Overwrites Alice's booking!

Result: Bob has the seat, Alice thinks she has it too!
        Alice shows up at the concert and finds Bob in her seat.
```

## 2.2 Pattern 1: Check-Then-Act

The **check-then-act** pattern is the most common correctness bug:

```
1. CHECK a condition
2. ACT based on that condition

Problem: Between CHECK and ACT, another thread can interfere!
```

### Where It Appears

| System | Check | Act |
|--------|-------|-----|
| **Ticket Booking** | Is seat available? | Book the seat |
| **Parking Lot** | Is spot empty? | Assign car to spot |
| **Rate Limiter** | Is user under limit? | Allow request |
| **Inventory** | Is stock available? | Process order |

### The Fix: Make It Atomic with Locks

The check and action must happen together as **one atomic operation**.

```java
// Java - FIXED with synchronized block
public class BookingService {
    private Map<String, Seat> seats = new HashMap<>();
    private final Object lock = new Object();
    
    public boolean bookSeat(String seatId, String userId) {
        synchronized (lock) {           // ACQUIRE LOCK
            Seat seat = seats.get(seatId);
            
            if (seat.isAvailable()) {   // CHECK
                seat.book(userId);       // ACT
                return true;
            }
            return false;
        }                               // RELEASE LOCK
    }
}
```

```python
# Python - FIXED with lock
import threading

class BookingService:
    def __init__(self):
        self.seats = {}
        self.lock = threading.Lock()
    
    def book_seat(self, seat_id: str, user_id: str) -> bool:
        with self.lock:                 # ACQUIRE LOCK
            seat = self.seats[seat_id]
            
            if seat.is_available():     # CHECK
                seat.book(user_id)       # ACT
                return True
            return False
                                        # RELEASE LOCK (automatic)
```

### How It Works Now

```
Thread A (Alice)              Thread B (Bob)
─────────────────             ─────────────────
Acquire lock ✓

Check: Is seat 7A available?
→ Yes!
                              Try to acquire lock
                              → BLOCKED! (Alice has it)
                              → Waiting...

Book seat 7A for Alice
Set status = "booked"

Release lock ✓
                              Acquire lock ✓
                              Check: Is seat 7A available?
                              → No! (Alice already booked)
                              Release lock ✓

Result: Alice has the seat, Bob correctly sees it's taken.
```

## 2.3 Pattern 2: Read-Modify-Write

The **read-modify-write** pattern is the second most common correctness bug:

```
1. READ a value
2. MODIFY it (compute new value)
3. WRITE it back

Problem: Looks like one operation, but it's actually THREE!
```

### Example: Counter Increment

```java
// This looks like ONE operation...
count++;

// But it's actually THREE:
// 1. Read current value of count
// 2. Add 1 to it
// 3. Write the new value back
```

### What Goes Wrong

```
Thread A                      Thread B
────────                      ────────
Read count: 5
                              Read count: 5
Compute: 5 + 1 = 6
                              Compute: 5 + 1 = 6
Write count = 6
                              Write count = 6

Result: count = 6
Expected: count = 7
We LOST an increment!
```

### Where It Appears

| System | Read | Modify | Write |
|--------|------|--------|-------|
| **Hit Counter** | Get current count | Add 1 | Store new count |
| **Bank Account** | Get balance | Add/subtract | Store new balance |
| **Inventory** | Get quantity | Subtract ordered | Store new quantity |
| **Metrics** | Get current metric | Aggregate | Store updated metric |

### The Fix: Atomic Variables

For simple counters, use **atomic variables** that handle read-modify-write at the hardware level.

```java
// Java - Using AtomicInteger
import java.util.concurrent.atomic.AtomicInteger;

public class Counter {
    private AtomicInteger count = new AtomicInteger(0);
    
    public int increment() {
        return count.incrementAndGet();  // Atomic at CPU level!
    }
    
    public int get() {
        return count.get();
    }
}
```

Modern CPUs have special instructions like **Compare-And-Swap (CAS)** that do read-modify-write in a single CPU cycle, guaranteeing no other thread can see the value mid-update.

### Python: No Built-in Atomics

Unfortunately, Python doesn't have built-in atomic variables. Use a lock instead:

```python
# Python - Using Lock (no atomic integers available)
import threading

class Counter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()
    
    def increment(self) -> int:
        with self.lock:
            self.count += 1
            return self.count
    
    def get(self) -> int:
        return self.count
```

## 2.4 When to Use Lock vs Atomic

| Scenario | Use |
|----------|-----|
| Single variable/counter | Atomic Variable (if available) |
| Flags, simple statistics | Atomic Variable |
| Multiple related variables | Lock |
| Complex operations | Lock |
| Transferring between accounts | Lock (must update both atomically) |

```java
// Atomic is NOT enough here - need a lock!
public void transfer(Account from, Account to, int amount) {
    // WRONG: Two separate atomic operations aren't atomic together!
    from.balance.addAndGet(-amount);
    to.balance.addAndGet(amount);
    // If crash between these lines, money disappears!
    
    // CORRECT: Use a lock
    synchronized (lock) {
        from.balance -= amount;
        to.balance += amount;
    }
}
```

## 2.5 Lock Primitives by Language

| Language | Lock Primitive | Example |
|----------|---------------|---------|
| **Java** | `synchronized` block | `synchronized (lock) { ... }` |
| **Java** | `ReentrantLock` | `lock.lock(); try { ... } finally { lock.unlock(); }` |
| **Python** | `threading.Lock` | `with lock: ...` |
| **Go** | `sync.Mutex` | `mu.Lock(); defer mu.Unlock()` |
| **Rust** | `std::sync::Mutex` | `let guard = mutex.lock().unwrap();` |
| **C++** | `std::mutex` | `std::lock_guard<std::mutex> guard(mtx);` |

---

# 3. Category 2: Coordination

## 3.1 The Problem

Coordination problems occur when **work flows from one thread to another**.

### Example: Welcome Email on Signup

```
User signs up → Send welcome email (takes 500ms)

Problem: Don't want signup request blocked for 500ms!
Solution: Hand off email sending to a background thread.
```

```
┌───────────────────┐         ┌───────────────────┐
│   API Threads     │         │  Worker Threads   │
│   (Producers)     │         │   (Consumers)     │
│                   │         │                   │
│  User signs up    │         │  Send email       │
│       │           │         │       ▲           │
│       ▼           │         │       │           │
│   Put task ───────┼────►────┼─── Take task      │
│       │           │  QUEUE  │       │           │
│   Return OK       │         │  Process email    │
│                   │         │                   │
└───────────────────┘         └───────────────────┘
```

### Two Problems Arise

1. **How does the worker know when new work arrives?**
2. **What happens if work arrives faster than workers can process?**

## 3.2 Problem 1: Waiting for Work

### Naive Approach: Busy Polling (BAD!)

```java
// Java - BAD: Burns CPU doing nothing!
public void worker() {
    while (true) {
        if (!queue.isEmpty()) {
            Task task = queue.poll();
            process(task);
        }
        // Spinning constantly, wasting CPU!
    }
}
```

```python
# Python - BAD: Burns CPU doing nothing!
def worker():
    while True:
        if not queue.empty():
            task = queue.get_nowait()
            process(task)
        # Spinning constantly, wasting CPU!
```

### Slightly Better: Sleep and Poll (Still Bad)

```java
// Java - Better but still has problems
public void worker() {
    while (true) {
        Task task = queue.poll();
        if (task != null) {
            process(task);
        } else {
            Thread.sleep(100);  // Sleep 100ms
        }
    }
}
```

**Problems:**
- Still wasting CPU cycles
- Introduces latency (up to 100ms delay before processing)

### The Solution: Blocking Queue

A **blocking queue** makes the worker sleep when empty and wake up instantly when work arrives.

```java
// Java - CORRECT: Using BlockingQueue
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class EmailService {
    private BlockingQueue<EmailTask> queue = new LinkedBlockingQueue<>();
    
    // Producer: API thread
    public void onUserSignup(User user) {
        queue.put(new EmailTask(user.getEmail()));  // Add to queue
        // Return immediately - don't wait for email to send
    }
    
    // Consumer: Worker thread
    public void worker() {
        while (true) {
            try {
                EmailTask task = queue.take();  // BLOCKS if empty!
                sendEmail(task);                 // Wakes up when task arrives
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
}
```

```python
# Python - CORRECT: Using Queue (blocking by default)
import queue
import threading

class EmailService:
    def __init__(self):
        self.queue = queue.Queue()  # Blocking queue by default
    
    # Producer: API thread
    def on_user_signup(self, user):
        self.queue.put(EmailTask(user.email))  # Add to queue
        # Return immediately
    
    # Consumer: Worker thread
    def worker(self):
        while True:
            task = self.queue.get()  # BLOCKS if empty!
            self.send_email(task)     # Wakes up when task arrives
            self.queue.task_done()
```

### How Blocking Queue Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    BLOCKING QUEUE BEHAVIOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Worker calls take() on EMPTY queue:                            │
│  → Thread goes to SLEEP (no CPU usage)                          │
│  → OS scheduler runs other threads                              │
│                                                                  │
│  Producer calls put():                                           │
│  → Item added to queue                                          │
│  → Sleeping worker WAKES UP instantly                           │
│  → Worker processes the task                                    │
│                                                                  │
│  No CPU waste! No latency! Perfect efficiency!                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 3.3 Problem 2: Too Much Work (Back Pressure)

### The Problem: Unbounded Queue

```
Marketing email goes out → 50,000 users click at once
→ 50,000 background tasks created
→ Queue grows and grows
→ Memory exhausted
→ Process CRASHES!
```

### The Solution: Bounded Blocking Queue

Set a **maximum size**. When full, producers block until there's room.

```java
// Java - Bounded BlockingQueue
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

public class EmailService {
    // Maximum 1000 items in queue
    private BlockingQueue<EmailTask> queue = new ArrayBlockingQueue<>(1000);
    
    public void onUserSignup(User user) {
        queue.put(new EmailTask(user.getEmail()));  // BLOCKS if queue full!
        // This creates BACK PRESSURE - system naturally slows down
    }
    
    public void worker() {
        while (true) {
            EmailTask task = queue.take();  // BLOCKS if queue empty
            sendEmail(task);
        }
    }
}
```

```python
# Python - Bounded Queue
import queue

class EmailService:
    def __init__(self):
        self.queue = queue.Queue(maxsize=1000)  # Maximum 1000 items
    
    def on_user_signup(self, user):
        self.queue.put(EmailTask(user.email))  # BLOCKS if queue full!
        # Back pressure naturally applied
    
    def worker(self):
        while True:
            task = self.queue.get()  # BLOCKS if queue empty
            self.send_email(task)
            self.queue.task_done()
```

### Back Pressure Explained

```
┌─────────────────────────────────────────────────────────────────┐
│                      BACK PRESSURE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Without back pressure (unbounded queue):                        │
│                                                                  │
│  [Producer] ──► [Queue grows infinitely] ──► [Consumer]         │
│                        │                                         │
│                        ▼                                         │
│                  OUT OF MEMORY!                                  │
│                                                                  │
│  With back pressure (bounded queue):                             │
│                                                                  │
│  [Producer] ──► [Queue at max size] ──► [Consumer]              │
│       │              │                                           │
│       │              ▼                                           │
│       └─── BLOCKED (waits for space) ───┘                       │
│                                                                  │
│  System naturally slows down when overwhelmed!                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Always Bound Your Queues!

**Rule**: There's almost no reason to ever use an unbounded queue. Always set a maximum size.

## 3.4 Coordination Summary

| Problem | Solution |
|---------|----------|
| Worker needs to wait for work | Blocking Queue (`take()` blocks when empty) |
| Work arrives faster than processing | Bounded Queue (`put()` blocks when full) |

### Where Coordination Appears

- Task schedulers
- Background job processors
- Message queues
- Producer-consumer systems
- Thread pools

---

# 4. Category 3: Scarcity

## 4.1 The Problem

Scarcity problems occur when you need to **limit concurrent access to finite resources**.

### Example: External API Rate Limit

```
External API allows only 10 concurrent requests.
You have 50 threads that might call it simultaneously.
Need: "Only 10 of you can be here at any time!"
```

## 4.2 Solution 1: Semaphores

A **semaphore** is a bucket of permits:

```
┌─────────────────────────────────────────────────────────────────┐
│                      SEMAPHORE CONCEPT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    ┌─────────────┐                               │
│                    │   BUCKET    │                               │
│                    │  ┌───────┐  │                               │
│                    │  │ 🎫🎫🎫 │  │  ← 5 permits available        │
│                    │  │ 🎫🎫   │  │                               │
│                    │  └───────┘  │                               │
│                    └─────────────┘                               │
│                                                                  │
│  Before operation: ACQUIRE permit (take from bucket)            │
│  After operation:  RELEASE permit (put back in bucket)          │
│  No permits left:  WAIT until someone releases                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

```java
// Java - Using Semaphore
import java.util.concurrent.Semaphore;

public class DownloadService {
    // Only 5 concurrent downloads allowed
    private Semaphore semaphore = new Semaphore(5);
    
    public void download(String url) {
        try {
            semaphore.acquire();        // Get permit (blocks if none available)
            doDownload(url);            // Do the work
        } finally {
            semaphore.release();        // ALWAYS release, even if exception!
        }
    }
}
```

```python
# Python - Using Semaphore
import threading

class DownloadService:
    def __init__(self):
        self.semaphore = threading.Semaphore(5)  # Only 5 concurrent
    
    def download(self, url: str):
        try:
            self.semaphore.acquire()    # Get permit
            self.do_download(url)       # Do the work
        finally:
            self.semaphore.release()    # ALWAYS release!
```

### Critical: Always Release in Finally!

**What happens if we don't use `finally`?**

```java
// WRONG - permit leaked on exception!
public void download(String url) {
    semaphore.acquire();
    doDownload(url);        // If this throws exception...
    semaphore.release();    // ...this never runs!
}
```

```
Exception thrown 5 times:
→ 5 permits permanently lost
→ Bucket is empty forever
→ All threads blocked
→ System halted!
```

**Always use try-finally:**

```java
// CORRECT - permit always returned
public void download(String url) {
    try {
        semaphore.acquire();
        doDownload(url);        // Even if this throws...
    } finally {
        semaphore.release();    // ...permit is released!
    }
}
```

## 4.3 Solution 2: Resource Pools (Connection Pool)

Sometimes you're not just counting - you're managing **actual objects with state**.

### Example: Database Connection Pool

```
Each database connection:
- Holds open TCP socket
- Consumes memory
- Tracks transaction state

Creating new connection for every query is expensive!
Solution: Create pool of connections, reuse them.
```

### Implementation Using Blocking Queue

```java
// Java - Connection Pool with BlockingQueue
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ArrayBlockingQueue;

public class ConnectionPool {
    private BlockingQueue<Connection> pool;
    
    public ConnectionPool(int size) {
        pool = new ArrayBlockingQueue<>(size);
        
        // Pre-create connections
        for (int i = 0; i < size; i++) {
            pool.put(createConnection());
        }
    }
    
    public ResultSet runQuery(String sql) {
        Connection conn = null;
        try {
            conn = pool.take();         // Get connection (blocks if none)
            return conn.execute(sql);   // Use it
        } finally {
            if (conn != null) {
                pool.put(conn);         // Return to pool (ALWAYS!)
            }
        }
    }
}
```

```python
# Python - Connection Pool with Queue
import queue

class ConnectionPool:
    def __init__(self, size: int):
        self.pool = queue.Queue(maxsize=size)
        
        # Pre-create connections
        for _ in range(size):
            self.pool.put(self.create_connection())
    
    def run_query(self, sql: str):
        conn = None
        try:
            conn = self.pool.get()      # Get connection (blocks if none)
            return conn.execute(sql)    # Use it
        finally:
            if conn is not None:
                self.pool.put(conn)     # Return to pool (ALWAYS!)
```

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONNECTION POOL                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Initial state: Pool has 10 connections                         │
│                                                                  │
│  Thread A: take() → gets connection 1                           │
│  Thread B: take() → gets connection 2                           │
│  ...                                                             │
│  Thread J: take() → gets connection 10                          │
│                                                                  │
│  Thread K: take() → BLOCKS (pool empty)                         │
│                      │                                           │
│                      │ waiting...                                │
│                      │                                           │
│  Thread A: put() → returns connection 1 to pool                 │
│                      │                                           │
│                      ▼                                           │
│  Thread K: → wakes up, gets connection 1                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4.4 Scarcity Summary

| Resource Type | Solution |
|---------------|----------|
| Counting (rate limits, concurrent operations) | Semaphore |
| Objects with state (connections, file handles) | Blocking Queue as Pool |

### The Pattern is the Same

```
1. ACQUIRE something scarce
2. USE it
3. RELEASE it (always, even on failure!)
```

---

# 5. Mental Checklist for Interviews

When concurrency comes up in your interview, ask yourself these questions:

```
┌─────────────────────────────────────────────────────────────────┐
│               CONCURRENCY INTERVIEW CHECKLIST                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Is there SHARED STATE that multiple threads access?         │
│     │                                                            │
│     └─► CORRECTNESS problem                                      │
│         • Look for: check-then-act, read-modify-write           │
│         • Solution: Lock or Atomic Variable                      │
│                                                                  │
│  2. Is WORK FLOWING from one thread to another?                 │
│     │                                                            │
│     └─► COORDINATION problem                                     │
│         • What happens when no work? → Blocking Queue           │
│         • What happens when too much work? → Bounded Queue      │
│         • Solution: Bounded Blocking Queue                       │
│                                                                  │
│  3. Is there a FIXED LIMIT on some resource?                    │
│     │                                                            │
│     └─► SCARCITY problem                                         │
│         • Counting permits → Semaphore                          │
│         • Reusable objects → Connection Pool (Blocking Queue)   │
│         • ALWAYS release in finally block!                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

# 6. Common Interview Problems

## 6.1 Ticket Booking System

**Problem**: Multiple users booking same seat
**Category**: Correctness (check-then-act)
**Solution**: Lock around check and book

```java
public boolean bookSeat(String seatId, String userId) {
    synchronized (lock) {
        if (seats.get(seatId).isAvailable()) {
            seats.get(seatId).book(userId);
            return true;
        }
        return false;
    }
}
```

## 6.2 Parking Lot System

**Problem**: Multiple entrances assigning same spot
**Category**: Correctness (check-then-act)
**Solution**: Lock around spot assignment

```java
public ParkingSpot assignSpot(Car car) {
    synchronized (lock) {
        ParkingSpot spot = findAvailableSpot();
        if (spot != null) {
            spot.assignCar(car);
        }
        return spot;
    }
}
```

## 6.3 Rate Limiter

**Problem**: Checking and incrementing request count
**Category**: Correctness (check-then-act + read-modify-write)
**Solution**: Lock or Atomic with check

```java
public boolean allowRequest(String userId) {
    synchronized (lock) {
        int count = requestCounts.getOrDefault(userId, 0);
        if (count < MAX_REQUESTS) {
            requestCounts.put(userId, count + 1);
            return true;
        }
        return false;
    }
}
```

## 6.4 Task Scheduler / Job Queue

**Problem**: Distributing work to workers
**Category**: Coordination
**Solution**: Bounded Blocking Queue

```java
private BlockingQueue<Task> queue = new ArrayBlockingQueue<>(1000);

public void submitTask(Task task) {
    queue.put(task);  // Blocks if full
}

public void worker() {
    while (true) {
        Task task = queue.take();  // Blocks if empty
        process(task);
    }
}
```

## 6.5 Web Crawler

**Problem**: Limiting concurrent HTTP requests
**Category**: Scarcity
**Solution**: Semaphore

```java
private Semaphore semaphore = new Semaphore(10);  // Max 10 concurrent

public void crawl(String url) {
    try {
        semaphore.acquire();
        fetchPage(url);
    } finally {
        semaphore.release();
    }
}
```

## 6.6 Database Connection Pool

**Problem**: Reusing expensive connections
**Category**: Scarcity
**Solution**: Blocking Queue as pool

```java
private BlockingQueue<Connection> pool;

public Result query(String sql) {
    Connection conn = pool.take();
    try {
        return conn.execute(sql);
    } finally {
        pool.put(conn);
    }
}
```

---

# 7. Quick Reference

## 7.1 Summary Table

| Category | Pattern | Solution | Key Point |
|----------|---------|----------|-----------|
| **Correctness** | Check-then-act | Lock | Make check+act atomic |
| **Correctness** | Read-modify-write | Atomic / Lock | Single CPU operation |
| **Coordination** | Producer-consumer | Blocking Queue | `take()` blocks when empty |
| **Coordination** | Back pressure | Bounded Queue | `put()` blocks when full |
| **Scarcity** | Rate limiting | Semaphore | Bucket of permits |
| **Scarcity** | Object reuse | Pool (BlockingQueue) | Take, use, return |

## 7.2 Code Patterns

### Pattern 1: Lock for Correctness

```java
// Java
synchronized (lock) {
    // atomic operations here
}

// Python
with lock:
    # atomic operations here
```

### Pattern 2: Blocking Queue for Coordination

```java
// Java
BlockingQueue<Task> queue = new ArrayBlockingQueue<>(1000);
queue.put(task);     // Producer (blocks if full)
queue.take();        // Consumer (blocks if empty)

// Python
queue = Queue(maxsize=1000)
queue.put(task)      # Producer
queue.get()          # Consumer
```

### Pattern 3: Semaphore for Scarcity

```java
// Java
Semaphore sem = new Semaphore(10);
try {
    sem.acquire();
    // use resource
} finally {
    sem.release();
}

// Python
sem = Semaphore(10)
try:
    sem.acquire()
    # use resource
finally:
    sem.release()
```

### Pattern 4: Pool for Object Reuse

```java
// Java
BlockingQueue<Resource> pool = new ArrayBlockingQueue<>(10);
Resource r = pool.take();
try {
    // use resource
} finally {
    pool.put(r);
}

// Python
pool = Queue(maxsize=10)
r = pool.get()
try:
    # use resource
finally:
    pool.put(r)
```

## 7.3 Golden Rules

1. **Always protect shared mutable state** with locks or atomics
2. **Always bound your queues** to prevent memory exhaustion
3. **Always release resources in finally** to prevent leaks
4. **Recognize the pattern first**, then apply the standard solution

---

## References

- Hello Interview: Low-Level Design Concurrency Guide
- Java Concurrency in Practice - Brian Goetz
- Python threading documentation

---

*Last updated: January 2025*
