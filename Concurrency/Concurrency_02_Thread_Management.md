# Module 2: Basic Thread Management

Time to write code! We'll create threads, start them, and coordinate their execution.

---

## 1. Creating and Starting Threads

### Java - Two Ways to Create Threads

#### Method 1: Extend Thread class
```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Hello from " + Thread.currentThread().getName());
    }
}

// Usage
MyThread t = new MyThread();
t.start();  // Don't call run() directly!
```

#### Method 2: Implement Runnable (Preferred)
```java
class MyTask implements Runnable {
    @Override
    public void run() {
        System.out.println("Hello from " + Thread.currentThread().getName());
    }
}

// Usage
Thread t = new Thread(new MyTask());
t.start();
```

#### Method 3: Lambda (Most Common)
```java
Thread t = new Thread(() -> {
    System.out.println("Hello from " + Thread.currentThread().getName());
});
t.start();
```

> **Why Runnable over Thread?**
> - Java doesn't support multiple inheritance
> - Separates "what to run" from "how to run"
> - Can be used with ExecutorService

### Go - Goroutines

Goroutines are lightweight threads managed by Go runtime.

```go
package main

import (
    "fmt"
    "time"
)

func sayHello() {
    fmt.Println("Hello from goroutine")
}

func main() {
    // Start a goroutine - just add 'go' keyword!
    go sayHello()
    
    // Anonymous function
    go func() {
        fmt.Println("Hello from anonymous goroutine")
    }()
    
    // With parameters
    go func(msg string) {
        fmt.Println(msg)
    }("Hello with parameter")
    
    time.Sleep(time.Second) // Wait for goroutines (bad practice, we'll fix this)
}
```

### Comparison

| Aspect | Java Thread | Go Goroutine |
|--------|-------------|--------------|
| Memory | ~1MB stack | ~2KB stack (grows) |
| Creation | OS thread | User-space (cheap!) |
| Syntax | `new Thread().start()` | `go func()` |
| Scaling | Thousands | Millions |

---

## 2. Waiting for Completion

### Java - join()

```java
public class JoinExample {
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            System.out.println("Thread 1 starting");
            try { Thread.sleep(2000); } catch (InterruptedException e) {}
            System.out.println("Thread 1 done");
        });
        
        Thread t2 = new Thread(() -> {
            System.out.println("Thread 2 starting");
            try { Thread.sleep(1000); } catch (InterruptedException e) {}
            System.out.println("Thread 2 done");
        });
        
        t1.start();
        t2.start();
        
        System.out.println("Main: waiting for threads...");
        
        t1.join();  // Block until t1 finishes
        t2.join();  // Block until t2 finishes
        
        System.out.println("Main: all threads completed!");
    }
}
```

**Output:**
```
Thread 1 starting
Thread 2 starting
Main: waiting for threads...
Thread 2 done
Thread 1 done
Main: all threads completed!
```

### Go - sync.WaitGroup

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func main() {
    var wg sync.WaitGroup
    
    // Tell WaitGroup we're adding 2 goroutines
    wg.Add(2)
    
    go func() {
        defer wg.Done()  // Decrement counter when done
        fmt.Println("Goroutine 1 starting")
        time.Sleep(2 * time.Second)
        fmt.Println("Goroutine 1 done")
    }()
    
    go func() {
        defer wg.Done()
        fmt.Println("Goroutine 2 starting")
        time.Sleep(1 * time.Second)
        fmt.Println("Goroutine 2 done")
    }()
    
    fmt.Println("Main: waiting for goroutines...")
    wg.Wait()  // Block until counter is 0
    fmt.Println("Main: all goroutines completed!")
}
```

### WaitGroup Pattern
```
wg.Add(n)    → "I'm starting n tasks"
wg.Done()    → "One task finished" (usually with defer)
wg.Wait()    → "Block until all tasks done"
```

---

## 3. Thread Sleep and Yield

### Sleep - Pause Execution

**Java:**
```java
try {
    Thread.sleep(1000);  // Sleep for 1 second (1000 ms)
} catch (InterruptedException e) {
    // Thread was interrupted while sleeping
    Thread.currentThread().interrupt();  // Preserve interrupt status
}
```

**Go:**
```go
import "time"

time.Sleep(1 * time.Second)
time.Sleep(500 * time.Millisecond)
```

### Yield - Give Up CPU

Suggests to scheduler that current thread is willing to yield its CPU time.

**Java:**
```java
Thread.yield();  // Hint to scheduler (may be ignored)
```

**Go:**
```go
import "runtime"

runtime.Gosched()  // Yield to other goroutines
```

> **Note:** `yield()` is just a hint. The scheduler may ignore it. Don't rely on it for synchronization!

---

## 4. Daemon Threads

Daemon threads run in the background and don't prevent program exit.

### Java Daemon Threads

```java
public class DaemonExample {
    public static void main(String[] args) throws InterruptedException {
        Thread daemon = new Thread(() -> {
            while (true) {
                System.out.println("Daemon running...");
                try { Thread.sleep(500); } catch (InterruptedException e) {}
            }
        });
        
        daemon.setDaemon(true);  // Must set BEFORE start()
        daemon.start();
        
        Thread.sleep(2000);
        System.out.println("Main thread exiting...");
        // Program exits, daemon is killed automatically
    }
}
```

**Output:**
```
Daemon running...
Daemon running...
Daemon running...
Daemon running...
Main thread exiting...
```

### Use Cases for Daemon Threads
- Background logging
- Garbage collection
- Monitoring/heartbeat tasks
- Cache cleanup

### Go - No Direct Equivalent

In Go, when `main()` returns, all goroutines are terminated. Every goroutine is essentially "daemon-like".

```go
func main() {
    go func() {
        for {
            fmt.Println("Background task...")
            time.Sleep(500 * time.Millisecond)
        }
    }()
    
    time.Sleep(2 * time.Second)
    fmt.Println("Main exiting...")
    // All goroutines terminated when main exits
}
```

---

## 5. Passing Data to Threads

### Java - Via Constructor or Lambda Closure

```java
// Method 1: Constructor
class Task implements Runnable {
    private final String message;
    
    public Task(String message) {
        this.message = message;
    }
    
    @Override
    public void run() {
        System.out.println(message);
    }
}

new Thread(new Task("Hello")).start();

// Method 2: Lambda closure (must be effectively final)
String msg = "Hello";
new Thread(() -> System.out.println(msg)).start();
```

### Go - Via Function Parameters

```go
// Correct: Pass as parameter
for i := 0; i < 5; i++ {
    go func(n int) {
        fmt.Println(n)
    }(i)  // Pass i as argument
}

// WRONG: Closure captures variable (common bug!)
for i := 0; i < 5; i++ {
    go func() {
        fmt.Println(i)  // Will likely print "5" five times!
    }()
}
```

---

## 6. Getting Results from Threads

### Java - Using Callable and Future

```java
import java.util.concurrent.*;

public class FutureExample {
    public static void main(String[] args) throws Exception {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        
        // Callable returns a value (unlike Runnable)
        Callable<Integer> task = () -> {
            Thread.sleep(1000);
            return 42;
        };
        
        Future<Integer> future = executor.submit(task);
        
        System.out.println("Doing other work...");
        
        // get() blocks until result is available
        Integer result = future.get();
        System.out.println("Result: " + result);
        
        executor.shutdown();
    }
}
```

### Go - Using Channels

```go
package main

import "fmt"

func compute(ch chan int) {
    // Do work...
    ch <- 42  // Send result to channel
}

func main() {
    ch := make(chan int)
    
    go compute(ch)
    
    fmt.Println("Doing other work...")
    
    result := <-ch  // Receive blocks until value available
    fmt.Println("Result:", result)
}
```

---

## 7. Hands-On Exercise

### Exercise: Parallel Download Simulation

Simulate downloading 5 files concurrently.

**Java Solution:**
```java
import java.util.concurrent.CountDownLatch;

public class ParallelDownload {
    public static void main(String[] args) throws InterruptedException {
        String[] files = {"file1.zip", "file2.zip", "file3.zip", "file4.zip", "file5.zip"};
        CountDownLatch latch = new CountDownLatch(files.length);
        
        long start = System.currentTimeMillis();
        
        for (String file : files) {
            new Thread(() -> {
                try {
                    System.out.println("Downloading " + file + "...");
                    Thread.sleep((long) (Math.random() * 2000 + 1000));  // 1-3 seconds
                    System.out.println("✓ " + file + " complete");
                } catch (InterruptedException e) {
                } finally {
                    latch.countDown();
                }
            }).start();
        }
        
        latch.await();  // Wait for all downloads
        
        long duration = System.currentTimeMillis() - start;
        System.out.println("\nAll downloads complete in " + duration + "ms");
    }
}
```

**Go Solution:**
```go
package main

import (
    "fmt"
    "math/rand"
    "sync"
    "time"
)

func download(file string, wg *sync.WaitGroup) {
    defer wg.Done()
    
    fmt.Printf("Downloading %s...\n", file)
    time.Sleep(time.Duration(rand.Intn(2000)+1000) * time.Millisecond)
    fmt.Printf("✓ %s complete\n", file)
}

func main() {
    files := []string{"file1.zip", "file2.zip", "file3.zip", "file4.zip", "file5.zip"}
    var wg sync.WaitGroup
    
    start := time.Now()
    
    for _, file := range files {
        wg.Add(1)
        go download(file, &wg)
    }
    
    wg.Wait()
    
    fmt.Printf("\nAll downloads complete in %v\n", time.Since(start))
}
```

---

## 8. Key Takeaways

| Concept | Java | Go |
|---------|------|-----|
| Create thread | `new Thread(runnable).start()` | `go func()` |
| Wait for completion | `thread.join()` | `sync.WaitGroup` |
| Sleep | `Thread.sleep(ms)` | `time.Sleep(duration)` |
| Return values | `Callable` + `Future` | Channels |
| Background thread | `setDaemon(true)` | All goroutines (main exit kills all) |

---

## Practice Challenges

1. **Counter**: Create 10 threads that each increment a counter 1000 times. Print the final value. (It won't be 10000 - this demonstrates race conditions!)

2. **Parallel Sum**: Split an array into chunks, sum each chunk in a separate thread, combine results.

3. **Timeout**: Start a long-running task and cancel it if it takes more than 2 seconds.

---

## Next Module

→ [Module 3: Synchronization & Shared State](./Concurrency_03_Synchronization.md)

*We'll fix the race condition problem and learn about locks, mutexes, and atomic operations.*

---

*Created: January 29, 2026*
