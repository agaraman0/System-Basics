# Module 6: High-Level Concurrency

Moving beyond primitives to production-ready abstractions.

---

## 1. Java: ExecutorService Deep Dive

`ExecutorService` is the standard way to manage thread pools in Java.

### Types of Executors

```java
import java.util.concurrent.*;

// Fixed pool: exact number of threads
ExecutorService fixed = Executors.newFixedThreadPool(4);

// Cached pool: grows/shrinks dynamically
ExecutorService cached = Executors.newCachedThreadPool();

// Single thread: sequential execution, survives failures
ExecutorService single = Executors.newSingleThreadExecutor();

// Scheduled: delayed and periodic execution
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(2);

// Work-stealing (Java 8+): uses all available cores
ExecutorService workStealing = Executors.newWorkStealingPool();

// Virtual threads (Java 21+): millions of lightweight threads
ExecutorService virtual = Executors.newVirtualThreadPerTaskExecutor();
```

### Choosing the Right Executor

| Type | Use Case | Thread Count |
|------|----------|--------------|
| Fixed | CPU-bound tasks | `Runtime.getRuntime().availableProcessors()` |
| Cached | Many short I/O tasks | 0 to Integer.MAX_VALUE |
| Single | Sequential execution | 1 |
| Scheduled | Timers, periodic tasks | N (configurable) |
| Work-Stealing | Fork/join parallelism | Available processors |
| Virtual | Massive I/O concurrency | Unlimited (lightweight) |

### Custom ThreadPoolExecutor

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    4,                              // corePoolSize
    8,                              // maximumPoolSize
    60L, TimeUnit.SECONDS,          // keepAliveTime
    new ArrayBlockingQueue<>(100),  // workQueue
    new CustomThreadFactory(),       // threadFactory
    new ThreadPoolExecutor.CallerRunsPolicy()  // rejectionPolicy
);

// Monitor the pool
System.out.println("Pool size: " + executor.getPoolSize());
System.out.println("Active: " + executor.getActiveCount());
System.out.println("Queue size: " + executor.getQueue().size());
System.out.println("Completed: " + executor.getCompletedTaskCount());
```

### Thread Factory

```java
class CustomThreadFactory implements ThreadFactory {
    private final AtomicInteger counter = new AtomicInteger(0);
    private final String prefix;
    
    public CustomThreadFactory(String prefix) {
        this.prefix = prefix;
    }
    
    @Override
    public Thread newThread(Runnable r) {
        Thread t = new Thread(r, prefix + "-" + counter.incrementAndGet());
        t.setDaemon(false);
        t.setPriority(Thread.NORM_PRIORITY);
        return t;
    }
}

// Usage
ExecutorService exec = Executors.newFixedThreadPool(4, 
    new CustomThreadFactory("worker"));
```

### Rejection Policies

What happens when the queue is full and max threads reached?

```java
// 1. AbortPolicy (default) - throws RejectedExecutionException
new ThreadPoolExecutor.AbortPolicy()

// 2. CallerRunsPolicy - caller thread executes the task (backpressure!)
new ThreadPoolExecutor.CallerRunsPolicy()

// 3. DiscardPolicy - silently drops the task
new ThreadPoolExecutor.DiscardPolicy()

// 4. DiscardOldestPolicy - drops oldest queued task, retries
new ThreadPoolExecutor.DiscardOldestPolicy()

// 5. Custom policy
RejectedExecutionHandler custom = (r, executor) -> {
    log.warn("Task rejected: " + r.toString());
    // Maybe write to dead letter queue
};
```

---

## 2. Java: CompletableFuture Advanced

### Chaining Operations

```java
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> fetchUser(userId))       // Async task
    .thenApply(user -> user.getEmail())         // Transform (sync)
    .thenApplyAsync(email -> sendEmail(email))  // Transform (async)
    .thenAccept(result -> log(result))          // Consume (no return)
    .exceptionally(ex -> {                      // Handle errors
        log.error("Failed", ex);
        return "fallback";
    });
```

### Combining Multiple Futures

```java
// Wait for both, combine results
CompletableFuture<String> userFuture = fetchUserAsync(id);
CompletableFuture<List<Order>> ordersFuture = fetchOrdersAsync(id);

CompletableFuture<UserWithOrders> combined = userFuture
    .thenCombine(ordersFuture, (user, orders) -> 
        new UserWithOrders(user, orders));

// Wait for first to complete
CompletableFuture<Object> fastest = CompletableFuture
    .anyOf(server1.fetch(), server2.fetch(), server3.fetch());

// Wait for all to complete
CompletableFuture<Void> allDone = CompletableFuture
    .allOf(task1, task2, task3);

// Collect all results
List<CompletableFuture<String>> futures = urls.stream()
    .map(url -> fetchAsync(url))
    .toList();

CompletableFuture<List<String>> allResults = CompletableFuture
    .allOf(futures.toArray(new CompletableFuture[0]))
    .thenApply(v -> futures.stream()
        .map(CompletableFuture::join)
        .toList());
```

### Timeout Handling

```java
// Java 9+
CompletableFuture<String> future = fetchAsync()
    .orTimeout(5, TimeUnit.SECONDS)              // Throws on timeout
    .completeOnTimeout("default", 5, TimeUnit.SECONDS);  // Default on timeout

// Java 8 compatible
CompletableFuture<String> withTimeout = fetchAsync()
    .applyToEither(
        failAfter(Duration.ofSeconds(5)),
        Function.identity()
    );

static <T> CompletableFuture<T> failAfter(Duration duration) {
    CompletableFuture<T> future = new CompletableFuture<>();
    Executors.newScheduledThreadPool(1).schedule(
        () -> future.completeExceptionally(new TimeoutException()),
        duration.toMillis(), TimeUnit.MILLISECONDS
    );
    return future;
}
```

### Error Handling Patterns

```java
CompletableFuture<String> future = fetchAsync()
    // Handle specific exceptions
    .exceptionally(ex -> {
        if (ex.getCause() instanceof NotFoundException) {
            return "not-found";
        }
        throw new CompletionException(ex);
    })
    // Handle with recovery async
    .exceptionallyAsync(ex -> fetchFromBackup())
    // Handle both success and failure
    .handle((result, ex) -> {
        if (ex != null) {
            log.error("Failed", ex);
            return "fallback";
        }
        return result;
    })
    // Always run (like finally)
    .whenComplete((result, ex) -> {
        cleanup();  // Runs regardless of success/failure
    });
```

---

## 3. Go: Context for Cancellation

`context.Context` is Go's standard way to handle cancellation, deadlines, and request-scoped values.

### Context Types

```go
import "context"

// Background: root context, never cancelled
ctx := context.Background()

// TODO: placeholder when unsure which context to use
ctx := context.TODO()

// WithCancel: manually cancellable
ctx, cancel := context.WithCancel(context.Background())
defer cancel()  // Always call cancel to release resources

// WithTimeout: auto-cancels after duration
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// WithDeadline: auto-cancels at specific time
deadline := time.Now().Add(5 * time.Second)
ctx, cancel := context.WithDeadline(context.Background(), deadline)
defer cancel()

// WithValue: attach request-scoped data (use sparingly!)
ctx := context.WithValue(parentCtx, "requestID", "abc123")
```

### Using Context for Cancellation

```go
package main

import (
    "context"
    "fmt"
    "time"
)

func worker(ctx context.Context, id int) error {
    for {
        select {
        case <-ctx.Done():
            // Context was cancelled
            fmt.Printf("Worker %d: cancelled (%v)\n", id, ctx.Err())
            return ctx.Err()
        default:
            // Do work
            fmt.Printf("Worker %d: working...\n", id)
            time.Sleep(500 * time.Millisecond)
        }
    }
}

func main() {
    // Create cancellable context
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()
    
    // Start workers
    go worker(ctx, 1)
    go worker(ctx, 2)
    
    // Wait for timeout
    <-ctx.Done()
    fmt.Println("Main: context done, reason:", ctx.Err())
    
    time.Sleep(100 * time.Millisecond)  // Let workers print
}
```

### Context in HTTP Handlers

```go
func handleRequest(w http.ResponseWriter, r *http.Request) {
    // Request context - cancelled when client disconnects
    ctx := r.Context()
    
    // Add timeout
    ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
    defer cancel()
    
    // Pass context to downstream calls
    result, err := fetchData(ctx)
    if err != nil {
        if err == context.Canceled {
            // Client disconnected
            return
        }
        if err == context.DeadlineExceeded {
            http.Error(w, "Request timeout", http.StatusGatewayTimeout)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    json.NewEncoder(w).Encode(result)
}

func fetchData(ctx context.Context) (Data, error) {
    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    resp, err := http.DefaultClient.Do(req)
    // ...
}
```

### Context Best Practices

```go
// 1. Always pass context as first parameter
func DoSomething(ctx context.Context, arg string) error

// 2. Never store context in structs
type Bad struct {
    ctx context.Context  // ❌ Don't do this
}

// 3. Always call cancel (use defer)
ctx, cancel := context.WithTimeout(ctx, time.Second)
defer cancel()  // ✅ Prevents resource leak

// 4. Check ctx.Done() in loops
for {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case item := <-items:
        process(item)
    }
}

// 5. Don't use context.WithValue for required data
// Use it for optional, request-scoped values like trace IDs
```

---

## 4. Graceful Shutdown

Properly stopping concurrent systems without losing work.

### Java Graceful Shutdown

```java
public class GracefulShutdown {
    private final ExecutorService executor;
    private final BlockingQueue<Task> queue;
    private volatile boolean running = true;
    
    public void shutdown() {
        running = false;
        
        // Stop accepting new tasks
        executor.shutdown();
        
        try {
            // Wait for existing tasks to complete
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) {
                // Force shutdown after timeout
                List<Runnable> dropped = executor.shutdownNow();
                log.warn("Dropped {} tasks", dropped.size());
                
                // Wait again
                if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                    log.error("Executor did not terminate");
                }
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    // Register shutdown hook
    public static void main(String[] args) {
        GracefulShutdown app = new GracefulShutdown();
        
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down...");
            app.shutdown();
            System.out.println("Shutdown complete");
        }));
        
        app.run();
    }
}
```

### Go Graceful Shutdown

```go
package main

import (
    "context"
    "fmt"
    "os"
    "os/signal"
    "sync"
    "syscall"
    "time"
)

type Server struct {
    workers sync.WaitGroup
}

func (s *Server) StartWorker(ctx context.Context, id int) {
    s.workers.Add(1)
    go func() {
        defer s.workers.Done()
        for {
            select {
            case <-ctx.Done():
                fmt.Printf("Worker %d: shutting down\n", id)
                return
            default:
                fmt.Printf("Worker %d: working\n", id)
                time.Sleep(500 * time.Millisecond)
            }
        }
    }()
}

func (s *Server) Wait() {
    s.workers.Wait()
}

func main() {
    // Create cancellable context
    ctx, cancel := context.WithCancel(context.Background())
    
    // Start server
    server := &Server{}
    for i := 1; i <= 3; i++ {
        server.StartWorker(ctx, i)
    }
    
    // Listen for shutdown signals
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
    
    // Wait for signal
    sig := <-sigChan
    fmt.Printf("\nReceived signal: %v\n", sig)
    
    // Cancel context to stop workers
    cancel()
    
    // Wait for workers with timeout
    done := make(chan struct{})
    go func() {
        server.Wait()
        close(done)
    }()
    
    select {
    case <-done:
        fmt.Println("Graceful shutdown complete")
    case <-time.After(5 * time.Second):
        fmt.Println("Shutdown timed out")
    }
}
```

### HTTP Server Graceful Shutdown (Go)

```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"
)

func main() {
    server := &http.Server{
        Addr:    ":8080",
        Handler: http.HandlerFunc(handler),
    }
    
    // Start server in background
    go func() {
        log.Println("Server starting on :8080")
        if err := server.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()
    
    // Wait for shutdown signal
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    
    log.Println("Shutting down server...")
    
    // Give in-flight requests 30 seconds to complete
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    
    if err := server.Shutdown(ctx); err != nil {
        log.Fatal("Server forced to shutdown:", err)
    }
    
    log.Println("Server stopped")
}

func handler(w http.ResponseWriter, r *http.Request) {
    time.Sleep(5 * time.Second)  // Simulate work
    w.Write([]byte("Hello!"))
}
```

---

## 5. Java Virtual Threads (Java 21+)

Virtual threads are lightweight threads that make blocking I/O cheap.

```java
// Create virtual thread
Thread vt = Thread.ofVirtual().start(() -> {
    // Can block without wasting OS thread
    var result = httpClient.send(request, BodyHandlers.ofString());
});

// Virtual thread executor - one virtual thread per task
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    // Submit millions of tasks!
    for (int i = 0; i < 100_000; i++) {
        executor.submit(() -> {
            Thread.sleep(1000);  // Blocks but doesn't waste thread
            return fetchData();
        });
    }
}

// Structured concurrency (preview)
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<User> user = scope.fork(() -> fetchUser(id));
    Future<List<Order>> orders = scope.fork(() -> fetchOrders(id));
    
    scope.join();           // Wait for both
    scope.throwIfFailed();  // Propagate errors
    
    return new UserWithOrders(user.resultNow(), orders.resultNow());
}
```

### When to Use Virtual Threads

| Use Virtual Threads | Use Platform Threads |
|---------------------|----------------------|
| I/O-bound work | CPU-bound work |
| Many concurrent tasks | Few long-running tasks |
| Blocking operations | Non-blocking reactive code |
| Simple thread-per-request | Custom scheduling needed |

---

## 6. Comparison Table

| Feature | Java | Go |
|---------|------|-----|
| Thread pool | `ExecutorService` | Worker goroutines |
| Async results | `CompletableFuture` | Channels |
| Cancellation | `Future.cancel()` | `context.Context` |
| Timeout | `orTimeout()` | `context.WithTimeout()` |
| Shutdown signal | `Runtime.addShutdownHook()` | `signal.Notify()` |
| Lightweight threads | Virtual Threads (21+) | Goroutines |

---

## 7. Key Takeaways

1. **Use the right executor** for your workload (fixed vs cached vs work-stealing)
2. **CompletableFuture chains** keep async code readable
3. **Context is essential** in Go for cancellation and timeouts
4. **Always handle graceful shutdown** - don't lose work!
5. **Virtual threads** (Java 21+) simplify concurrent I/O code

---

## Practice Challenges

1. **Rate-Limited Client**: HTTP client that limits to N requests/second
2. **Circuit Breaker**: Stop calling failing service, retry after cooldown
3. **Scatter-Gather**: Query 3 replicas, use first response, cancel others

---

## Next Module

→ [Module 7: Common Problems & Debugging](./Concurrency_07_Problems.md)

*Deadlocks, livelocks, starvation - how to detect and fix them*

---

*Created: January 29, 2026*
