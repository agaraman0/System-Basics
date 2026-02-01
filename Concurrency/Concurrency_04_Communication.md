# Module 4: Communication Between Threads

Threads don't just need protection - they need to **communicate** and **coordinate**.

---

## 1. The Coordination Problem

Imagine a producer-consumer scenario:

```
Producer: "I made something!"
Consumer: "I need something to process!"

Without coordination:
- Consumer spins wastefully checking for data (busy waiting)
- Or consumer might miss data entirely
```

**We need threads to WAIT for conditions and SIGNAL when conditions change.**

---

## 2. Java: wait() and notify()

Every Java object has a built-in **monitor** with wait/notify capability.

### Basic Pattern

```java
synchronized (lock) {
    while (!condition) {
        lock.wait();      // Release lock, sleep until notified
    }
    // Condition is true, proceed
}

// Another thread:
synchronized (lock) {
    condition = true;
    lock.notify();        // Wake up ONE waiting thread
    // or
    lock.notifyAll();     // Wake up ALL waiting threads
}
```

### Producer-Consumer with wait/notify

```java
import java.util.LinkedList;
import java.util.Queue;

public class ProducerConsumer {
    private final Queue<Integer> buffer = new LinkedList<>();
    private final int capacity = 5;
    
    public synchronized void produce(int item) throws InterruptedException {
        // Wait while buffer is full
        while (buffer.size() == capacity) {
            System.out.println("Buffer full, producer waiting...");
            wait();
        }
        
        buffer.add(item);
        System.out.println("Produced: " + item + " | Buffer size: " + buffer.size());
        
        notifyAll();  // Wake up consumers
    }
    
    public synchronized int consume() throws InterruptedException {
        // Wait while buffer is empty
        while (buffer.isEmpty()) {
            System.out.println("Buffer empty, consumer waiting...");
            wait();
        }
        
        int item = buffer.poll();
        System.out.println("Consumed: " + item + " | Buffer size: " + buffer.size());
        
        notifyAll();  // Wake up producers
        return item;
    }
    
    public static void main(String[] args) {
        ProducerConsumer pc = new ProducerConsumer();
        
        // Producer thread
        Thread producer = new Thread(() -> {
            for (int i = 0; i < 10; i++) {
                try {
                    pc.produce(i);
                    Thread.sleep(100);
                } catch (InterruptedException e) {}
            }
        });
        
        // Consumer thread
        Thread consumer = new Thread(() -> {
            for (int i = 0; i < 10; i++) {
                try {
                    pc.consume();
                    Thread.sleep(200);  // Slower consumer
                } catch (InterruptedException e) {}
            }
        });
        
        producer.start();
        consumer.start();
    }
}
```

### Critical Rules for wait/notify

| Rule | Reason |
|------|--------|
| Always call in `synchronized` block | Must hold lock to wait/notify |
| Always use `while` loop, not `if` | Spurious wakeups can occur |
| Prefer `notifyAll()` over `notify()` | `notify()` can cause missed signals |
| Check condition AFTER waking up | Another thread might have changed it |

### Common Mistake: if vs while

```java
// WRONG - Can break due to spurious wakeup
synchronized (lock) {
    if (buffer.isEmpty()) {  // ❌ if
        wait();
    }
    process(buffer.poll());  // Might be null!
}

// CORRECT - Always re-check condition
synchronized (lock) {
    while (buffer.isEmpty()) {  // ✅ while
        wait();
    }
    process(buffer.poll());  // Guaranteed not null
}
```

---

## 3. Java: Condition Variables

`Condition` provides more flexibility than wait/notify - multiple conditions per lock.

```java
import java.util.concurrent.locks.*;

public class BoundedBuffer<T> {
    private final Object[] items;
    private int count, putIndex, takeIndex;
    
    private final Lock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();   // For producers
    private final Condition notEmpty = lock.newCondition();  // For consumers
    
    public BoundedBuffer(int capacity) {
        items = new Object[capacity];
    }
    
    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (count == items.length) {
                notFull.await();  // Wait until not full
            }
            items[putIndex] = item;
            putIndex = (putIndex + 1) % items.length;
            count++;
            notEmpty.signal();  // Signal consumers
        } finally {
            lock.unlock();
        }
    }
    
    @SuppressWarnings("unchecked")
    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (count == 0) {
                notEmpty.await();  // Wait until not empty
            }
            T item = (T) items[takeIndex];
            takeIndex = (takeIndex + 1) % items.length;
            count--;
            notFull.signal();  // Signal producers
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

### wait/notify vs Condition

| Feature | wait/notify | Condition |
|---------|-------------|-----------|
| Multiple conditions | No (one per object) | Yes |
| Selective signaling | No | Yes (`signal` specific condition) |
| Interruptible wait | No | Yes (`awaitUninterruptibly`) |
| Timed wait | `wait(ms)` | `await(time, unit)` |

---

## 4. Go: Channels

Go takes a different approach: **"Don't communicate by sharing memory; share memory by communicating."**

Channels are typed conduits for passing data between goroutines.

### Channel Basics

```go
// Create channels
ch := make(chan int)      // Unbuffered channel
ch := make(chan int, 10)  // Buffered channel (capacity 10)

// Send (blocks if full/no receiver)
ch <- 42

// Receive (blocks if empty/no sender)
value := <-ch

// Close channel (signals no more values)
close(ch)
```

### Unbuffered vs Buffered Channels

```
UNBUFFERED (synchronous):
┌──────────┐         ┌──────────┐
│ Sender   │────────►│ Receiver │
│ (blocks) │         │ (blocks) │
└──────────┘         └──────────┘
Both must be ready - handoff

BUFFERED (asynchronous):
┌──────────┐    ┌─────────┐    ┌──────────┐
│ Sender   │───►│ Buffer  │───►│ Receiver │
└──────────┘    │ [_][_]  │    └──────────┘
                └─────────┘
Sender blocks only when full
Receiver blocks only when empty
```

### Producer-Consumer with Channels

```go
package main

import (
    "fmt"
    "time"
)

func producer(ch chan<- int) {  // Send-only channel
    for i := 0; i < 10; i++ {
        fmt.Printf("Producing: %d\n", i)
        ch <- i
        time.Sleep(100 * time.Millisecond)
    }
    close(ch)  // Signal no more items
}

func consumer(ch <-chan int) {  // Receive-only channel
    for item := range ch {  // Loop until channel closed
        fmt.Printf("Consumed: %d\n", item)
        time.Sleep(200 * time.Millisecond)
    }
    fmt.Println("Consumer done")
}

func main() {
    ch := make(chan int, 5)  // Buffered channel
    
    go producer(ch)
    consumer(ch)  // Run in main goroutine
}
```

### Channel Direction (Type Safety)

```go
chan T     // Bidirectional
chan<- T   // Send-only
<-chan T   // Receive-only

func worker(jobs <-chan int, results chan<- int) {
    for job := range jobs {
        results <- job * 2
    }
}
```

---

## 5. Go: Select Statement

`select` lets you wait on multiple channel operations - like `switch` for channels.

```go
select {
case msg := <-ch1:
    fmt.Println("Received from ch1:", msg)
case ch2 <- value:
    fmt.Println("Sent to ch2")
case <-time.After(1 * time.Second):
    fmt.Println("Timeout!")
default:
    fmt.Println("No channel ready")  // Non-blocking
}
```

### Example: Timeout Pattern

```go
func fetchWithTimeout(url string) (string, error) {
    resultCh := make(chan string)
    errCh := make(chan error)
    
    go func() {
        result, err := fetch(url)
        if err != nil {
            errCh <- err
            return
        }
        resultCh <- result
    }()
    
    select {
    case result := <-resultCh:
        return result, nil
    case err := <-errCh:
        return "", err
    case <-time.After(5 * time.Second):
        return "", fmt.Errorf("timeout fetching %s", url)
    }
}
```

### Example: Non-blocking Operations

```go
// Non-blocking receive
select {
case msg := <-ch:
    fmt.Println("Received:", msg)
default:
    fmt.Println("No message available")
}

// Non-blocking send
select {
case ch <- msg:
    fmt.Println("Sent message")
default:
    fmt.Println("Channel full, dropping message")
}
```

---

## 6. Go: sync.Cond (Condition Variable)

Go also has condition variables for complex waiting patterns.

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Queue struct {
    items []int
    cond  *sync.Cond
    cap   int
}

func NewQueue(capacity int) *Queue {
    return &Queue{
        items: make([]int, 0),
        cond:  sync.NewCond(&sync.Mutex{}),
        cap:   capacity,
    }
}

func (q *Queue) Put(item int) {
    q.cond.L.Lock()
    defer q.cond.L.Unlock()
    
    for len(q.items) == q.cap {
        q.cond.Wait()  // Wait until not full
    }
    
    q.items = append(q.items, item)
    fmt.Printf("Put: %d | Size: %d\n", item, len(q.items))
    q.cond.Broadcast()  // Wake all waiters
}

func (q *Queue) Take() int {
    q.cond.L.Lock()
    defer q.cond.L.Unlock()
    
    for len(q.items) == 0 {
        q.cond.Wait()  // Wait until not empty
    }
    
    item := q.items[0]
    q.items = q.items[1:]
    fmt.Printf("Take: %d | Size: %d\n", item, len(q.items))
    q.cond.Broadcast()
    return item
}

func main() {
    q := NewQueue(3)
    
    // Producer
    go func() {
        for i := 0; i < 10; i++ {
            q.Put(i)
            time.Sleep(100 * time.Millisecond)
        }
    }()
    
    // Consumer
    for i := 0; i < 10; i++ {
        q.Take()
        time.Sleep(200 * time.Millisecond)
    }
}
```

> **Note:** In Go, channels are usually preferred over sync.Cond. Use sync.Cond only when channels don't fit your use case.

---

## 7. Java: BlockingQueue

`BlockingQueue` is the Java standard library solution - no manual wait/notify needed!

### BlockingQueue Interface

```java
// Core blocking operations
void put(E e)          // Blocks if full
E take()               // Blocks if empty

// Non-blocking operations  
boolean offer(E e)     // Returns false if full
E poll()               // Returns null if empty

// Timed operations
boolean offer(E e, long timeout, TimeUnit unit)
E poll(long timeout, TimeUnit unit)
```

### Common Implementations

| Implementation | Bound | Ordering | Notes |
|----------------|-------|----------|-------|
| `ArrayBlockingQueue` | Bounded | FIFO | Fixed size array |
| `LinkedBlockingQueue` | Optional | FIFO | Higher throughput |
| `PriorityBlockingQueue` | Unbounded | Priority | Sorted order |
| `SynchronousQueue` | 0 | Direct handoff | No storage |
| `DelayQueue` | Unbounded | Delay time | Elements expire |

### Producer-Consumer with BlockingQueue

```java
import java.util.concurrent.*;

public class BlockingQueueExample {
    public static void main(String[] args) {
        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(5);
        
        // Producer
        Thread producer = new Thread(() -> {
            try {
                for (int i = 0; i < 10; i++) {
                    System.out.println("Producing: " + i);
                    queue.put(i);  // Blocks if full
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {}
        });
        
        // Consumer
        Thread consumer = new Thread(() -> {
            try {
                for (int i = 0; i < 10; i++) {
                    Integer item = queue.take();  // Blocks if empty
                    System.out.println("Consumed: " + item);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {}
        });
        
        producer.start();
        consumer.start();
    }
}
```

### Bounded vs Unbounded BlockingQueue

```java
// BOUNDED - Blocks producer when full (backpressure)
BlockingQueue<Task> bounded = new ArrayBlockingQueue<>(100);

// UNBOUNDED - Never blocks producer (can cause OOM!)
BlockingQueue<Task> unbounded = new LinkedBlockingQueue<>();

// Recommendation: Always use bounded queues in production!
```

---

## 8. Comparison: Java vs Go Communication

| Concept | Java | Go |
|---------|------|-----|
| Basic signaling | `wait()`/`notify()` | Channels |
| Condition variables | `Condition` | `sync.Cond` |
| Blocking queue | `BlockingQueue` | Buffered channel |
| Select/multiplex | Not built-in | `select` |
| Philosophy | Shared memory | Message passing |

### When to Use What

**Java:**
- `BlockingQueue` for most producer-consumer patterns
- `wait()/notify()` for simple signaling
- `Condition` for multiple wait conditions

**Go:**
- Channels for almost everything
- `select` for multiplexing
- `sync.Cond` rarely (channels are better)

---

## 9. Key Takeaways

1. **Don't busy-wait** - Use proper wait mechanisms
2. **Always use `while` loops** with wait/notify (spurious wakeups)
3. **Channels are Go's strength** - Prefer them over shared memory
4. **BlockingQueue is your friend** - Don't reinvent it in Java
5. **Bounded queues provide backpressure** - Essential for production

---

## Practice Challenges

1. **Ping-Pong**: Two threads alternating printing "ping" and "pong"

2. **Multiple Consumers**: One producer, three consumers sharing work

3. **Request-Response**: Simulate async request with response channel

---

## Next Module

→ [Module 5: Concurrency Patterns](./Concurrency_05_Patterns.md)

*Classic patterns: Producer-Consumer, Reader-Writer, Thread Pool, Future/Promise*

---

*Created: January 29, 2026*
