# Module 5: Concurrency Patterns

Battle-tested patterns that solve common concurrent programming problems.

---

## 1. Producer-Consumer Pattern

The most fundamental concurrency pattern. One or more producers create work, one or more consumers process it.

```
┌──────────┐     ┌─────────────┐     ┌──────────┐
│ Producer │────►│   Buffer    │────►│ Consumer │
│          │     │  (Queue)    │     │          │
└──────────┘     └─────────────┘     └──────────┘
     │                 ▲                   │
     │    Blocks if    │    Blocks if      │
     └────  full  ─────┴────  empty  ──────┘
```

### When to Use
- Decoupling work generation from work processing
- Rate differences between producer and consumer
- Load balancing across multiple consumers
- Buffering bursts of work

### Java Implementation

```java
import java.util.concurrent.*;

public class ProducerConsumerPattern {
    public static void main(String[] args) {
        // Bounded queue provides backpressure
        BlockingQueue<Task> queue = new ArrayBlockingQueue<>(100);
        
        // Multiple producers
        for (int i = 0; i < 2; i++) {
            int producerId = i;
            new Thread(() -> {
                try {
                    while (true) {
                        Task task = generateTask(producerId);
                        queue.put(task);  // Blocks if full
                        System.out.printf("Producer %d: queued %s%n", producerId, task);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Producer-" + i).start();
        }
        
        // Multiple consumers
        for (int i = 0; i < 4; i++) {
            int consumerId = i;
            new Thread(() -> {
                try {
                    while (true) {
                        Task task = queue.take();  // Blocks if empty
                        processTask(task);
                        System.out.printf("Consumer %d: processed %s%n", consumerId, task);
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Consumer-" + i).start();
        }
    }
    
    static Task generateTask(int producerId) throws InterruptedException {
        Thread.sleep(100);  // Simulate work
        return new Task("Task from P" + producerId);
    }
    
    static void processTask(Task task) throws InterruptedException {
        Thread.sleep(200);  // Simulate processing
    }
    
    record Task(String name) {}
}
```

### Go Implementation

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Task struct {
    Name string
}

func producer(id int, tasks chan<- Task, wg *sync.WaitGroup) {
    defer wg.Done()
    for i := 0; i < 5; i++ {
        task := Task{Name: fmt.Sprintf("Task-%d-%d", id, i)}
        tasks <- task  // Blocks if channel full
        fmt.Printf("Producer %d: queued %s\n", id, task.Name)
        time.Sleep(100 * time.Millisecond)
    }
}

func consumer(id int, tasks <-chan Task, wg *sync.WaitGroup) {
    defer wg.Done()
    for task := range tasks {  // Exits when channel closed
        fmt.Printf("Consumer %d: processing %s\n", id, task.Name)
        time.Sleep(200 * time.Millisecond)
    }
}

func main() {
    tasks := make(chan Task, 10)  // Buffered channel
    
    var producerWg, consumerWg sync.WaitGroup
    
    // Start 2 producers
    for i := 0; i < 2; i++ {
        producerWg.Add(1)
        go producer(i, tasks, &producerWg)
    }
    
    // Start 4 consumers
    for i := 0; i < 4; i++ {
        consumerWg.Add(1)
        go consumer(i, tasks, &consumerWg)
    }
    
    // Wait for producers, then close channel
    producerWg.Wait()
    close(tasks)
    
    // Wait for consumers to finish
    consumerWg.Wait()
    fmt.Println("All done!")
}
```

---

## 2. Reader-Writer Pattern

Multiple readers can access simultaneously, but writers need exclusive access.

```
Readers (concurrent):     Writer (exclusive):
┌────────┐                ┌────────┐
│Reader 1│──┐             │ Writer │
├────────┤  │             └───┬────┘
│Reader 2│──┼──► [DATA]       │
├────────┤  │         ◄───────┘
│Reader 3│──┘         (exclusive lock)
└────────┘
(shared lock)
```

### When to Use
- Read-heavy workloads (caches, configs)
- Reads significantly outnumber writes
- Reads don't modify state

### Java Implementation

```java
import java.util.concurrent.locks.*;
import java.util.*;

public class ThreadSafeCache<K, V> {
    private final Map<K, V> cache = new HashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    private final Lock readLock = lock.readLock();
    private final Lock writeLock = lock.writeLock();
    
    public V get(K key) {
        readLock.lock();
        try {
            return cache.get(key);
        } finally {
            readLock.unlock();
        }
    }
    
    public void put(K key, V value) {
        writeLock.lock();
        try {
            cache.put(key, value);
        } finally {
            writeLock.unlock();
        }
    }
    
    public V computeIfAbsent(K key, java.util.function.Function<K, V> compute) {
        // First try read lock
        readLock.lock();
        try {
            V value = cache.get(key);
            if (value != null) return value;
        } finally {
            readLock.unlock();
        }
        
        // Need write lock to compute and store
        writeLock.lock();
        try {
            // Double-check after acquiring write lock
            V value = cache.get(key);
            if (value != null) return value;
            
            value = compute.apply(key);
            cache.put(key, value);
            return value;
        } finally {
            writeLock.unlock();
        }
    }
}
```

### Go Implementation

```go
package main

import (
    "sync"
)

type Cache struct {
    mu    sync.RWMutex
    items map[string]interface{}
}

func NewCache() *Cache {
    return &Cache{items: make(map[string]interface{})}
}

func (c *Cache) Get(key string) (interface{}, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    val, ok := c.items[key]
    return val, ok
}

func (c *Cache) Set(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.items[key] = value
}

func (c *Cache) GetOrCompute(key string, compute func() interface{}) interface{} {
    // Try read first
    c.mu.RLock()
    if val, ok := c.items[key]; ok {
        c.mu.RUnlock()
        return val
    }
    c.mu.RUnlock()
    
    // Need write lock
    c.mu.Lock()
    defer c.mu.Unlock()
    
    // Double-check
    if val, ok := c.items[key]; ok {
        return val
    }
    
    val := compute()
    c.items[key] = val
    return val
}
```

---

## 3. Thread Pool Pattern

Reuse a fixed set of threads to execute many tasks.

```
┌────────┐
│ Task 1 │──┐
├────────┤  │     ┌─────────┐     ┌──────────┐
│ Task 2 │──┼────►│  Queue  │────►│ Worker 1 │
├────────┤  │     └─────────┘     ├──────────┤
│ Task 3 │──┤           │         │ Worker 2 │
├────────┤  │           │         ├──────────┤
│  ...   │──┘           └────────►│ Worker 3 │
└────────┘                        └──────────┘
                               (fixed pool size)
```

### When to Use
- Many short-lived tasks
- Control resource usage (limit concurrent operations)
- Avoid thread creation overhead
- HTTP servers, database connection pools

### Java - ExecutorService

```java
import java.util.concurrent.*;

public class ThreadPoolExample {
    public static void main(String[] args) throws Exception {
        // Fixed pool: exactly N threads
        ExecutorService fixed = Executors.newFixedThreadPool(4);
        
        // Cached pool: creates threads as needed, reuses idle ones
        ExecutorService cached = Executors.newCachedThreadPool();
        
        // Single thread: sequential execution
        ExecutorService single = Executors.newSingleThreadExecutor();
        
        // Scheduled: delayed and periodic tasks
        ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(2);
        
        // Submit tasks
        Future<String> future = fixed.submit(() -> {
            Thread.sleep(1000);
            return "Result";
        });
        
        // Fire and forget
        fixed.execute(() -> System.out.println("Running in pool"));
        
        // Wait for result
        String result = future.get();  // Blocks
        System.out.println(result);
        
        // Shutdown
        fixed.shutdown();  // No new tasks, finish existing
        fixed.awaitTermination(10, TimeUnit.SECONDS);
        
        // Or force shutdown
        // fixed.shutdownNow();  // Interrupt running tasks
    }
}
```

### Java - Custom ThreadPoolExecutor

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,                      // Core pool size
    8,                      // Maximum pool size
    60, TimeUnit.SECONDS,   // Keep-alive time for idle threads
    new ArrayBlockingQueue<>(100),  // Work queue
    new ThreadPoolExecutor.CallerRunsPolicy()  // Rejection policy
);

// Rejection policies:
// AbortPolicy: throws RejectedExecutionException (default)
// CallerRunsPolicy: caller thread runs the task (backpressure)
// DiscardPolicy: silently discard
// DiscardOldestPolicy: discard oldest, retry
```

### Go - Worker Pool

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Job struct {
    ID   int
    Data string
}

type Result struct {
    JobID  int
    Output string
}

func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
    defer wg.Done()
    for job := range jobs {
        fmt.Printf("Worker %d processing job %d\n", id, job.ID)
        time.Sleep(100 * time.Millisecond)  // Simulate work
        results <- Result{JobID: job.ID, Output: "Processed: " + job.Data}
    }
}

func main() {
    numWorkers := 3
    numJobs := 10
    
    jobs := make(chan Job, numJobs)
    results := make(chan Result, numJobs)
    
    // Start worker pool
    var wg sync.WaitGroup
    for i := 1; i <= numWorkers; i++ {
        wg.Add(1)
        go worker(i, jobs, results, &wg)
    }
    
    // Send jobs
    for i := 1; i <= numJobs; i++ {
        jobs <- Job{ID: i, Data: fmt.Sprintf("data-%d", i)}
    }
    close(jobs)
    
    // Wait for workers and close results
    go func() {
        wg.Wait()
        close(results)
    }()
    
    // Collect results
    for result := range results {
        fmt.Printf("Result: Job %d -> %s\n", result.JobID, result.Output)
    }
}
```

---

## 4. Future/Promise Pattern

Represent a value that will be available in the future.

```
┌────────┐     ┌────────────┐     ┌────────────┐
│ Submit │────►│  Future    │────►│   Result   │
│  Task  │     │ (pending)  │     │ (complete) │
└────────┘     └────────────┘     └────────────┘
                    │
            get() blocks until ready
```

### When to Use
- Async operations with results
- Parallel computation with aggregation
- Non-blocking I/O

### Java - CompletableFuture

```java
import java.util.concurrent.*;

public class FuturePattern {
    public static void main(String[] args) throws Exception {
        // Basic future
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            sleep(1000);
            return "Hello";
        });
        
        // Chain transformations (non-blocking)
        CompletableFuture<String> transformed = future
            .thenApply(s -> s + " World")          // Transform result
            .thenApply(String::toUpperCase);       // Transform again
        
        // Combine futures
        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> "Hello");
        CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> "World");
        
        CompletableFuture<String> combined = future1
            .thenCombine(future2, (a, b) -> a + " " + b);
        
        // Wait for all
        CompletableFuture<Void> all = CompletableFuture.allOf(future1, future2);
        
        // Wait for any
        CompletableFuture<Object> any = CompletableFuture.anyOf(future1, future2);
        
        // Error handling
        CompletableFuture<String> withFallback = future
            .exceptionally(ex -> "Fallback value");
        
        // Async callback (non-blocking)
        future.thenAccept(result -> System.out.println("Got: " + result));
        
        // Blocking get
        String result = transformed.get();  // or get(timeout, unit)
        System.out.println(result);
    }
    
    static void sleep(long ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) {}
    }
}
```

### Go - Channels as Futures

```go
package main

import (
    "fmt"
    "time"
)

// Future represents an async result
type Future[T any] struct {
    result chan T
    err    chan error
}

func NewFuture[T any](fn func() (T, error)) *Future[T] {
    f := &Future[T]{
        result: make(chan T, 1),
        err:    make(chan error, 1),
    }
    
    go func() {
        result, err := fn()
        if err != nil {
            f.err <- err
        } else {
            f.result <- result
        }
    }()
    
    return f
}

func (f *Future[T]) Get() (T, error) {
    select {
    case result := <-f.result:
        return result, nil
    case err := <-f.err:
        var zero T
        return zero, err
    }
}

func (f *Future[T]) GetWithTimeout(timeout time.Duration) (T, error) {
    select {
    case result := <-f.result:
        return result, nil
    case err := <-f.err:
        var zero T
        return zero, err
    case <-time.After(timeout):
        var zero T
        return zero, fmt.Errorf("timeout")
    }
}

func main() {
    // Create async computation
    future := NewFuture(func() (string, error) {
        time.Sleep(1 * time.Second)
        return "Hello, Future!", nil
    })
    
    fmt.Println("Computing...")
    
    // Get result (blocks)
    result, err := future.Get()
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Result:", result)
    }
}
```

---

## 5. Fan-Out/Fan-In Pattern

Distribute work across multiple workers (fan-out), collect results (fan-in).

```
                 Fan-Out                    Fan-In
              ┌──────────┐              ┌───────────┐
              │ Worker 1 │──────┐       │           │
┌─────────┐   ├──────────┤      ├──────►│  Merger   │──► Result
│  Input  │──►│ Worker 2 │──────┤       │           │
└─────────┘   ├──────────┤      │       └───────────┘
              │ Worker 3 │──────┘
              └──────────┘
```

### When to Use
- CPU-bound parallel processing
- Batch processing with aggregation
- Map-reduce style operations

### Go Implementation

```go
package main

import (
    "fmt"
    "sync"
)

// Fan-out: one input to multiple workers
func fanOut(input <-chan int, numWorkers int) []<-chan int {
    outputs := make([]<-chan int, numWorkers)
    
    for i := 0; i < numWorkers; i++ {
        outputs[i] = worker(input)
    }
    
    return outputs
}

func worker(input <-chan int) <-chan int {
    output := make(chan int)
    go func() {
        defer close(output)
        for n := range input {
            output <- n * n  // Process: square the number
        }
    }()
    return output
}

// Fan-in: merge multiple inputs into one
func fanIn(inputs ...<-chan int) <-chan int {
    output := make(chan int)
    var wg sync.WaitGroup
    
    // Start a goroutine for each input channel
    for _, ch := range inputs {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for n := range c {
                output <- n
            }
        }(ch)
    }
    
    // Close output when all inputs are done
    go func() {
        wg.Wait()
        close(output)
    }()
    
    return output
}

func main() {
    // Create input
    input := make(chan int)
    go func() {
        defer close(input)
        for i := 1; i <= 10; i++ {
            input <- i
        }
    }()
    
    // Fan-out to 3 workers
    workers := fanOut(input, 3)
    
    // Fan-in results
    results := fanIn(workers...)
    
    // Collect
    sum := 0
    for result := range results {
        fmt.Printf("Got: %d\n", result)
        sum += result
    }
    fmt.Printf("Sum of squares: %d\n", sum)
}
```

### Java Implementation

```java
import java.util.concurrent.*;
import java.util.stream.*;
import java.util.*;

public class FanOutFanIn {
    public static void main(String[] args) throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(4);
        List<Integer> inputs = IntStream.rangeClosed(1, 10).boxed().toList();
        
        // Fan-out: submit all tasks
        List<Future<Integer>> futures = inputs.stream()
            .map(n -> executor.submit(() -> {
                Thread.sleep(100);  // Simulate work
                return n * n;
            }))
            .toList();
        
        // Fan-in: collect results
        int sum = 0;
        for (Future<Integer> future : futures) {
            int result = future.get();
            System.out.println("Got: " + result);
            sum += result;
        }
        
        System.out.println("Sum of squares: " + sum);
        executor.shutdown();
    }
    
    // With CompletableFuture (cleaner)
    public static void withCompletableFuture() {
        List<Integer> inputs = IntStream.rangeClosed(1, 10).boxed().toList();
        
        List<CompletableFuture<Integer>> futures = inputs.stream()
            .map(n -> CompletableFuture.supplyAsync(() -> n * n))
            .toList();
        
        // Wait for all and sum
        int sum = futures.stream()
            .map(CompletableFuture::join)
            .mapToInt(Integer::intValue)
            .sum();
        
        System.out.println("Sum: " + sum);
    }
}
```

---

## 6. Pattern Comparison

| Pattern | Problem Solved | Java | Go |
|---------|---------------|------|-----|
| Producer-Consumer | Decouple work generation/processing | `BlockingQueue` | Channels |
| Reader-Writer | Many readers, few writers | `ReadWriteLock` | `sync.RWMutex` |
| Thread Pool | Reuse threads, control resources | `ExecutorService` | Worker goroutines |
| Future/Promise | Async results | `CompletableFuture` | Channels |
| Fan-Out/Fan-In | Parallel processing | `ExecutorService` | Multiple channels |

---

## 7. Key Takeaways

1. **Producer-Consumer** decouples producers from consumers - use bounded queues!
2. **Reader-Writer** optimizes for read-heavy workloads
3. **Thread Pools** control resources and avoid creation overhead
4. **Futures** make async code manageable
5. **Fan-Out/Fan-In** parallelizes work and aggregates results

---

## Practice Challenges

1. **Pipeline**: Chain multiple producers/consumers (A → B → C)
2. **Rate Limiter**: Allow only N operations per second
3. **Parallel Map**: Implement `parallelMap(list, fn)` using fan-out/fan-in

---

## Next Module

→ [Module 6: High-Level Concurrency](./Concurrency_06_HighLevel.md)

*ExecutorService, CompletableFuture, Go context, and cancellation patterns*

---

*Created: January 29, 2026*
