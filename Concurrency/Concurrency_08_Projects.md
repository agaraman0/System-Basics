# Module 8: Mini Projects

Put everything together with hands-on implementations.

---

## Project 1: Concurrent Web Scraper

Fetch multiple URLs concurrently with rate limiting and timeout.

### Java Implementation

```java
import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;

public class ConcurrentScraper {
    private final HttpClient client;
    private final ExecutorService executor;
    private final Semaphore rateLimiter;  // Control concurrency
    
    public ConcurrentScraper(int maxConcurrent) {
        this.client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
        this.executor = Executors.newFixedThreadPool(maxConcurrent);
        this.rateLimiter = new Semaphore(maxConcurrent);
    }
    
    public CompletableFuture<String> fetch(String url) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                rateLimiter.acquire();
                try {
                    HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(url))
                        .timeout(Duration.ofSeconds(30))
                        .GET()
                        .build();
                    
                    HttpResponse<String> response = client.send(
                        request, HttpResponse.BodyHandlers.ofString());
                    
                    System.out.printf("✓ Fetched %s (%d bytes)%n", 
                        url, response.body().length());
                    return response.body();
                    
                } finally {
                    rateLimiter.release();
                }
            } catch (Exception e) {
                System.err.printf("✗ Failed %s: %s%n", url, e.getMessage());
                throw new CompletionException(e);
            }
        }, executor);
    }
    
    public Map<String, String> scrapeAll(List<String> urls) {
        Map<String, CompletableFuture<String>> futures = new HashMap<>();
        
        // Start all fetches
        for (String url : urls) {
            futures.put(url, fetch(url));
        }
        
        // Collect results
        Map<String, String> results = new ConcurrentHashMap<>();
        for (var entry : futures.entrySet()) {
            try {
                results.put(entry.getKey(), entry.getValue().get(60, TimeUnit.SECONDS));
            } catch (Exception e) {
                results.put(entry.getKey(), "ERROR: " + e.getMessage());
            }
        }
        
        return results;
    }
    
    public void shutdown() {
        executor.shutdown();
        try {
            executor.awaitTermination(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
    }
    
    public static void main(String[] args) {
        List<String> urls = List.of(
            "https://httpbin.org/delay/1",
            "https://httpbin.org/delay/2",
            "https://httpbin.org/get",
            "https://httpbin.org/headers",
            "https://httpbin.org/ip"
        );
        
        ConcurrentScraper scraper = new ConcurrentScraper(3);
        
        long start = System.currentTimeMillis();
        Map<String, String> results = scraper.scrapeAll(urls);
        long elapsed = System.currentTimeMillis() - start;
        
        System.out.printf("%nScraped %d URLs in %dms%n", results.size(), elapsed);
        scraper.shutdown();
    }
}
```

### Go Implementation

```go
package main

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "sync"
    "time"
)

type Scraper struct {
    client      *http.Client
    semaphore   chan struct{}
    maxRetries  int
}

func NewScraper(maxConcurrent int) *Scraper {
    return &Scraper{
        client: &http.Client{
            Timeout: 30 * time.Second,
        },
        semaphore:  make(chan struct{}, maxConcurrent),
        maxRetries: 3,
    }
}

type Result struct {
    URL   string
    Body  string
    Error error
}

func (s *Scraper) Fetch(ctx context.Context, url string) Result {
    // Acquire semaphore
    s.semaphore <- struct{}{}
    defer func() { <-s.semaphore }()
    
    var lastErr error
    for attempt := 0; attempt < s.maxRetries; attempt++ {
        if attempt > 0 {
            time.Sleep(time.Duration(attempt) * time.Second)  // Backoff
        }
        
        req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
        if err != nil {
            return Result{URL: url, Error: err}
        }
        
        resp, err := s.client.Do(req)
        if err != nil {
            lastErr = err
            continue
        }
        defer resp.Body.Close()
        
        body, err := io.ReadAll(resp.Body)
        if err != nil {
            lastErr = err
            continue
        }
        
        fmt.Printf("✓ Fetched %s (%d bytes)\n", url, len(body))
        return Result{URL: url, Body: string(body)}
    }
    
    fmt.Printf("✗ Failed %s: %v\n", url, lastErr)
    return Result{URL: url, Error: lastErr}
}

func (s *Scraper) ScrapeAll(ctx context.Context, urls []string) []Result {
    results := make([]Result, len(urls))
    var wg sync.WaitGroup
    
    for i, url := range urls {
        wg.Add(1)
        go func(idx int, u string) {
            defer wg.Done()
            results[idx] = s.Fetch(ctx, u)
        }(i, url)
    }
    
    wg.Wait()
    return results
}

func main() {
    urls := []string{
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/get",
        "https://httpbin.org/headers",
        "https://httpbin.org/ip",
    }
    
    scraper := NewScraper(3)
    
    ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
    defer cancel()
    
    start := time.Now()
    results := scraper.ScrapeAll(ctx, urls)
    elapsed := time.Since(start)
    
    successCount := 0
    for _, r := range results {
        if r.Error == nil {
            successCount++
        }
    }
    
    fmt.Printf("\nScraped %d/%d URLs in %v\n", successCount, len(urls), elapsed)
}
```

---

## Project 2: Producer-Consumer Pipeline

Multi-stage pipeline: Read → Process → Write

### Go Implementation (Pipeline Pattern)

```go
package main

import (
    "context"
    "fmt"
    "math/rand"
    "sync"
    "time"
)

// Stage 1: Generate data
func generate(ctx context.Context, count int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for i := 0; i < count; i++ {
            select {
            case <-ctx.Done():
                return
            case out <- i:
                fmt.Printf("[Generate] Produced: %d\n", i)
                time.Sleep(50 * time.Millisecond)
            }
        }
    }()
    return out
}

// Stage 2: Process data (fan-out to multiple workers)
func process(ctx context.Context, in <-chan int, numWorkers int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    
    worker := func(id int) {
        defer wg.Done()
        for n := range in {
            select {
            case <-ctx.Done():
                return
            default:
                // Simulate processing
                time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
                result := n * n
                fmt.Printf("[Worker %d] %d -> %d\n", id, n, result)
                out <- result
            }
        }
    }
    
    wg.Add(numWorkers)
    for i := 0; i < numWorkers; i++ {
        go worker(i)
    }
    
    go func() {
        wg.Wait()
        close(out)
    }()
    
    return out
}

// Stage 3: Aggregate results
func aggregate(ctx context.Context, in <-chan int) int {
    sum := 0
    for n := range in {
        select {
        case <-ctx.Done():
            return sum
        default:
            sum += n
            fmt.Printf("[Aggregate] Sum so far: %d\n", sum)
        }
    }
    return sum
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    
    // Build pipeline
    generated := generate(ctx, 10)
    processed := process(ctx, generated, 3)
    result := aggregate(ctx, processed)
    
    fmt.Printf("\n=== Final sum of squares: %d ===\n", result)
}
```

### Java Implementation

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Pipeline {
    private final BlockingQueue<Integer> stage1To2 = new ArrayBlockingQueue<>(10);
    private final BlockingQueue<Integer> stage2To3 = new ArrayBlockingQueue<>(10);
    private volatile boolean running = true;
    
    // Stage 1: Generate
    class Generator implements Runnable {
        @Override
        public void run() {
            try {
                for (int i = 0; i < 20 && running; i++) {
                    stage1To2.put(i);
                    System.out.printf("[Generate] Produced: %d%n", i);
                    Thread.sleep(50);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    // Stage 2: Process
    class Processor implements Runnable {
        private final int id;
        
        Processor(int id) { this.id = id; }
        
        @Override
        public void run() {
            try {
                while (running || !stage1To2.isEmpty()) {
                    Integer n = stage1To2.poll(100, TimeUnit.MILLISECONDS);
                    if (n != null) {
                        Thread.sleep((long) (Math.random() * 100));
                        int result = n * n;
                        System.out.printf("[Worker %d] %d -> %d%n", id, n, result);
                        stage2To3.put(result);
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    // Stage 3: Aggregate
    class Aggregator implements Runnable {
        private final AtomicInteger sum = new AtomicInteger(0);
        
        @Override
        public void run() {
            try {
                while (running || !stage2To3.isEmpty()) {
                    Integer n = stage2To3.poll(100, TimeUnit.MILLISECONDS);
                    if (n != null) {
                        int newSum = sum.addAndGet(n);
                        System.out.printf("[Aggregate] Sum so far: %d%n", newSum);
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        int getSum() { return sum.get(); }
    }
    
    public void run() throws InterruptedException {
        Aggregator aggregator = new Aggregator();
        
        ExecutorService executor = Executors.newFixedThreadPool(5);
        executor.submit(new Generator());
        executor.submit(new Processor(0));
        executor.submit(new Processor(1));
        executor.submit(new Processor(2));
        executor.submit(aggregator);
        
        Thread.sleep(5000);
        running = false;
        
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);
        
        System.out.printf("%n=== Final sum of squares: %d ===%n", aggregator.getSum());
    }
    
    public static void main(String[] args) throws InterruptedException {
        new Pipeline().run();
    }
}
```

---

## Project 3: Rate Limiter

Limit operations to N per second using token bucket algorithm.

### Go Implementation

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

type RateLimiter struct {
    tokens     chan struct{}
    refillRate time.Duration
    capacity   int
    stop       chan struct{}
}

func NewRateLimiter(rps int) *RateLimiter {
    rl := &RateLimiter{
        tokens:     make(chan struct{}, rps),
        refillRate: time.Second / time.Duration(rps),
        capacity:   rps,
        stop:       make(chan struct{}),
    }
    
    // Fill initial tokens
    for i := 0; i < rps; i++ {
        rl.tokens <- struct{}{}
    }
    
    // Start refill goroutine
    go rl.refill()
    
    return rl
}

func (rl *RateLimiter) refill() {
    ticker := time.NewTicker(rl.refillRate)
    defer ticker.Stop()
    
    for {
        select {
        case <-rl.stop:
            return
        case <-ticker.C:
            select {
            case rl.tokens <- struct{}{}:
                // Token added
            default:
                // Bucket full, discard
            }
        }
    }
}

func (rl *RateLimiter) Wait(ctx context.Context) error {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-rl.tokens:
        return nil
    }
}

func (rl *RateLimiter) TryAcquire() bool {
    select {
    case <-rl.tokens:
        return true
    default:
        return false
    }
}

func (rl *RateLimiter) Stop() {
    close(rl.stop)
}

func main() {
    limiter := NewRateLimiter(5)  // 5 requests per second
    defer limiter.Stop()
    
    var wg sync.WaitGroup
    ctx := context.Background()
    
    start := time.Now()
    
    // Try to make 20 requests
    for i := 0; i < 20; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            
            if err := limiter.Wait(ctx); err != nil {
                fmt.Printf("Request %d: cancelled\n", id)
                return
            }
            
            elapsed := time.Since(start)
            fmt.Printf("Request %d: executed at %v\n", id, elapsed.Round(time.Millisecond))
        }(i)
    }
    
    wg.Wait()
    fmt.Printf("\nCompleted 20 requests in %v\n", time.Since(start))
}
```

### Java Implementation

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimiter {
    private final Semaphore tokens;
    private final ScheduledExecutorService refiller;
    private final int capacity;
    
    public RateLimiter(int requestsPerSecond) {
        this.capacity = requestsPerSecond;
        this.tokens = new Semaphore(requestsPerSecond);
        this.refiller = Executors.newSingleThreadScheduledExecutor();
        
        // Refill tokens periodically
        long refillPeriodMs = 1000 / requestsPerSecond;
        refiller.scheduleAtFixedRate(() -> {
            if (tokens.availablePermits() < capacity) {
                tokens.release();
            }
        }, refillPeriodMs, refillPeriodMs, TimeUnit.MILLISECONDS);
    }
    
    public void acquire() throws InterruptedException {
        tokens.acquire();
    }
    
    public boolean tryAcquire() {
        return tokens.tryAcquire();
    }
    
    public boolean tryAcquire(long timeout, TimeUnit unit) throws InterruptedException {
        return tokens.tryAcquire(timeout, unit);
    }
    
    public void shutdown() {
        refiller.shutdown();
    }
    
    public static void main(String[] args) throws InterruptedException {
        RateLimiter limiter = new RateLimiter(5);  // 5 RPS
        ExecutorService executor = Executors.newFixedThreadPool(10);
        AtomicInteger counter = new AtomicInteger(0);
        
        long start = System.currentTimeMillis();
        
        // Submit 20 requests
        for (int i = 0; i < 20; i++) {
            final int id = i;
            executor.submit(() -> {
                try {
                    limiter.acquire();
                    long elapsed = System.currentTimeMillis() - start;
                    System.out.printf("Request %d: executed at %dms%n", id, elapsed);
                    counter.incrementAndGet();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }
        
        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);
        
        System.out.printf("%nCompleted %d requests in %dms%n", 
            counter.get(), System.currentTimeMillis() - start);
        limiter.shutdown();
    }
}
```

---

## Project 4: Thread-Safe LRU Cache

Concurrent cache with least-recently-used eviction.

### Java Implementation

```java
import java.util.*;
import java.util.concurrent.locks.*;

public class ConcurrentLRUCache<K, V> {
    private final int capacity;
    private final Map<K, Node<K, V>> map;
    private final DoublyLinkedList<K, V> list;
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    public ConcurrentLRUCache(int capacity) {
        this.capacity = capacity;
        this.map = new HashMap<>();
        this.list = new DoublyLinkedList<>();
    }
    
    public V get(K key) {
        lock.writeLock().lock();  // Need write lock to update access order
        try {
            Node<K, V> node = map.get(key);
            if (node == null) {
                return null;
            }
            // Move to front (most recently used)
            list.moveToFront(node);
            return node.value;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void put(K key, V value) {
        lock.writeLock().lock();
        try {
            Node<K, V> existing = map.get(key);
            if (existing != null) {
                existing.value = value;
                list.moveToFront(existing);
                return;
            }
            
            // Evict if at capacity
            if (map.size() >= capacity) {
                Node<K, V> lru = list.removeLast();
                if (lru != null) {
                    map.remove(lru.key);
                    System.out.println("Evicted: " + lru.key);
                }
            }
            
            // Add new node
            Node<K, V> node = new Node<>(key, value);
            list.addFirst(node);
            map.put(key, node);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public int size() {
        lock.readLock().lock();
        try {
            return map.size();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    // Node for doubly linked list
    private static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev, next;
        
        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }
    
    // Doubly linked list
    private static class DoublyLinkedList<K, V> {
        private Node<K, V> head, tail;
        
        void addFirst(Node<K, V> node) {
            node.next = head;
            node.prev = null;
            if (head != null) head.prev = node;
            head = node;
            if (tail == null) tail = node;
        }
        
        void moveToFront(Node<K, V> node) {
            if (node == head) return;
            remove(node);
            addFirst(node);
        }
        
        void remove(Node<K, V> node) {
            if (node.prev != null) node.prev.next = node.next;
            else head = node.next;
            if (node.next != null) node.next.prev = node.prev;
            else tail = node.prev;
        }
        
        Node<K, V> removeLast() {
            if (tail == null) return null;
            Node<K, V> node = tail;
            remove(node);
            return node;
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        ConcurrentLRUCache<String, Integer> cache = new ConcurrentLRUCache<>(3);
        
        // Concurrent access
        Thread[] threads = new Thread[5];
        for (int i = 0; i < 5; i++) {
            final int id = i;
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 10; j++) {
                    String key = "key" + (id * 10 + j) % 5;
                    cache.put(key, id * 10 + j);
                    Integer val = cache.get(key);
                    System.out.printf("Thread %d: put/get %s = %d%n", id, key, val);
                }
            });
            threads[i].start();
        }
        
        for (Thread t : threads) t.join();
        System.out.println("Final cache size: " + cache.size());
    }
}
```

### Go Implementation

```go
package main

import (
    "container/list"
    "fmt"
    "sync"
)

type LRUCache struct {
    capacity int
    cache    map[string]*list.Element
    list     *list.List
    mu       sync.RWMutex
}

type entry struct {
    key   string
    value interface{}
}

func NewLRUCache(capacity int) *LRUCache {
    return &LRUCache{
        capacity: capacity,
        cache:    make(map[string]*list.Element),
        list:     list.New(),
    }
}

func (c *LRUCache) Get(key string) (interface{}, bool) {
    c.mu.Lock()
    defer c.mu.Unlock()
    
    if elem, ok := c.cache[key]; ok {
        c.list.MoveToFront(elem)
        return elem.Value.(*entry).value, true
    }
    return nil, false
}

func (c *LRUCache) Put(key string, value interface{}) {
    c.mu.Lock()
    defer c.mu.Unlock()
    
    if elem, ok := c.cache[key]; ok {
        c.list.MoveToFront(elem)
        elem.Value.(*entry).value = value
        return
    }
    
    // Evict if at capacity
    if c.list.Len() >= c.capacity {
        oldest := c.list.Back()
        if oldest != nil {
            c.list.Remove(oldest)
            delete(c.cache, oldest.Value.(*entry).key)
            fmt.Printf("Evicted: %s\n", oldest.Value.(*entry).key)
        }
    }
    
    // Add new entry
    elem := c.list.PushFront(&entry{key: key, value: value})
    c.cache[key] = elem
}

func (c *LRUCache) Size() int {
    c.mu.RLock()
    defer c.mu.RUnlock()
    return c.list.Len()
}

func main() {
    cache := NewLRUCache(3)
    
    var wg sync.WaitGroup
    
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for j := 0; j < 10; j++ {
                key := fmt.Sprintf("key%d", (id*10+j)%5)
                cache.Put(key, id*10+j)
                if val, ok := cache.Get(key); ok {
                    fmt.Printf("Goroutine %d: put/get %s = %v\n", id, key, val)
                }
            }
        }(i)
    }
    
    wg.Wait()
    fmt.Printf("Final cache size: %d\n", cache.Size())
}
```

---

## Project 5: Worker Pool with Job Queue

Robust worker pool with graceful shutdown.

### Go Implementation

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

type Job struct {
    ID      int
    Payload string
}

type Result struct {
    JobID  int
    Output string
    Error  error
}

type WorkerPool struct {
    numWorkers int
    jobs       chan Job
    results    chan Result
    wg         sync.WaitGroup
}

func NewWorkerPool(numWorkers, jobQueueSize int) *WorkerPool {
    return &WorkerPool{
        numWorkers: numWorkers,
        jobs:       make(chan Job, jobQueueSize),
        results:    make(chan Result, jobQueueSize),
    }
}

func (p *WorkerPool) Start(ctx context.Context) {
    for i := 0; i < p.numWorkers; i++ {
        p.wg.Add(1)
        go p.worker(ctx, i)
    }
}

func (p *WorkerPool) worker(ctx context.Context, id int) {
    defer p.wg.Done()
    
    for {
        select {
        case <-ctx.Done():
            fmt.Printf("Worker %d: shutting down\n", id)
            return
        case job, ok := <-p.jobs:
            if !ok {
                fmt.Printf("Worker %d: job channel closed\n", id)
                return
            }
            
            // Process job
            fmt.Printf("Worker %d: processing job %d\n", id, job.ID)
            time.Sleep(100 * time.Millisecond)  // Simulate work
            
            p.results <- Result{
                JobID:  job.ID,
                Output: fmt.Sprintf("Processed: %s", job.Payload),
            }
        }
    }
}

func (p *WorkerPool) Submit(job Job) {
    p.jobs <- job
}

func (p *WorkerPool) Results() <-chan Result {
    return p.results
}

func (p *WorkerPool) Shutdown() {
    close(p.jobs)
    p.wg.Wait()
    close(p.results)
}

func main() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()
    
    pool := NewWorkerPool(3, 10)
    pool.Start(ctx)
    
    // Submit jobs
    go func() {
        for i := 0; i < 10; i++ {
            pool.Submit(Job{
                ID:      i,
                Payload: fmt.Sprintf("data-%d", i),
            })
        }
    }()
    
    // Collect results
    go func() {
        for result := range pool.Results() {
            fmt.Printf("Result: Job %d -> %s\n", result.JobID, result.Output)
        }
    }()
    
    // Let it run
    time.Sleep(2 * time.Second)
    
    // Graceful shutdown
    fmt.Println("\nInitiating shutdown...")
    pool.Shutdown()
    fmt.Println("Shutdown complete")
}
```

### Java Implementation

```java
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class WorkerPool {
    private final ExecutorService executor;
    private final BlockingQueue<Job> jobQueue;
    private final BlockingQueue<Result> resultQueue;
    private final AtomicBoolean running = new AtomicBoolean(true);
    
    record Job(int id, String payload) {}
    record Result(int jobId, String output, Exception error) {}
    
    public WorkerPool(int numWorkers, int queueSize) {
        this.jobQueue = new ArrayBlockingQueue<>(queueSize);
        this.resultQueue = new ArrayBlockingQueue<>(queueSize);
        this.executor = Executors.newFixedThreadPool(numWorkers);
        
        // Start workers
        for (int i = 0; i < numWorkers; i++) {
            final int workerId = i;
            executor.submit(() -> worker(workerId));
        }
    }
    
    private void worker(int id) {
        while (running.get() || !jobQueue.isEmpty()) {
            try {
                Job job = jobQueue.poll(100, TimeUnit.MILLISECONDS);
                if (job != null) {
                    System.out.printf("Worker %d: processing job %d%n", id, job.id());
                    Thread.sleep(100);  // Simulate work
                    
                    resultQueue.put(new Result(
                        job.id(),
                        "Processed: " + job.payload(),
                        null
                    ));
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        System.out.printf("Worker %d: shutting down%n", id);
    }
    
    public void submit(Job job) throws InterruptedException {
        jobQueue.put(job);
    }
    
    public Result takeResult() throws InterruptedException {
        return resultQueue.take();
    }
    
    public Result pollResult(long timeout, TimeUnit unit) throws InterruptedException {
        return resultQueue.poll(timeout, unit);
    }
    
    public void shutdown() {
        running.set(false);
        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
    }
    
    public static void main(String[] args) throws Exception {
        WorkerPool pool = new WorkerPool(3, 10);
        
        // Submit jobs
        for (int i = 0; i < 10; i++) {
            pool.submit(new Job(i, "data-" + i));
        }
        
        // Collect results
        for (int i = 0; i < 10; i++) {
            Result result = pool.pollResult(5, TimeUnit.SECONDS);
            if (result != null) {
                System.out.printf("Result: Job %d -> %s%n", result.jobId(), result.output());
            }
        }
        
        System.out.println("\nInitiating shutdown...");
        pool.shutdown();
        System.out.println("Shutdown complete");
    }
}
```

---

## Summary: What You've Built

| Project | Concepts Used |
|---------|---------------|
| **Web Scraper** | Futures, semaphores, rate limiting, timeouts |
| **Pipeline** | Channels, fan-out, producer-consumer |
| **Rate Limiter** | Token bucket, semaphores, scheduled tasks |
| **LRU Cache** | Read-write locks, thread-safe data structures |
| **Worker Pool** | Thread pools, blocking queues, graceful shutdown |

---

## Challenge Extensions

1. **Add metrics** to worker pool (jobs/second, queue depth, latency)
2. **Circuit breaker** for web scraper (stop calling failing URLs)
3. **Sharded cache** for higher concurrency (partition by key hash)
4. **Priority queue** for worker pool (high-priority jobs first)
5. **Distributed rate limiter** using Redis

---

## Congratulations! 🎉

You've completed the entire Concurrency & Multi-threading curriculum!

### Your Learning Path

```
✅ Module 1: Foundations - Concurrency vs parallelism, threads vs processes
✅ Module 2: Thread Management - Creating, starting, joining threads
✅ Module 3: Synchronization - Locks, mutexes, atomics
✅ Module 4: Communication - wait/notify, channels, BlockingQueue
✅ Module 5: Patterns - Producer-consumer, thread pools, futures
✅ Module 6: High-Level - ExecutorService, CompletableFuture, context
✅ Module 7: Problems - Deadlocks, livelocks, debugging
✅ Module 8: Projects - Real implementations
```

### Next Steps

1. **Practice** - Implement these patterns in your own projects
2. **Read source code** - Study Java ConcurrentHashMap, Go runtime
3. **Benchmark** - Measure performance of your concurrent code
4. **Explore advanced topics** - Lock-free data structures, actors, STM

---

*Created: January 29, 2026*
