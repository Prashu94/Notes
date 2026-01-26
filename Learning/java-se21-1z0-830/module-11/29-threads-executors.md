# Module 11: Concurrency - Threads and Executors

## Table of Contents
1. [Introduction to Concurrency](#introduction-to-concurrency)
2. [Platform Threads vs Virtual Threads (Java 21)](#platform-threads-vs-virtual-threads-java-21)
3. [Creating Threads](#creating-threads)
4. [Thread Lifecycle](#thread-lifecycle)
5. [Runnable vs Callable](#runnable-vs-callable)
6. [ExecutorService Framework](#executorservice-framework)
7. [Thread Pools](#thread-pools)
8. [Future and CompletableFuture](#future-and-completablefuture)
9. [Best Practices](#best-practices)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to Concurrency

**Concurrency** allows multiple tasks to execute simultaneously, improving application performance and responsiveness.

### Key Concepts

```java
// Sequential execution
void processSequential() {
    task1();  // Completes before task2
    task2();  // Completes before task3
    task3();
    // Total time: time(task1) + time(task2) + time(task3)
}

// Concurrent execution
void processConcurrent() throws InterruptedException {
    Thread t1 = new Thread(() -> task1());
    Thread t2 = new Thread(() -> task2());
    Thread t3 = new Thread(() -> task3());
    
    t1.start();
    t2.start();
    t3.start();
    
    t1.join();  // Wait for all to complete
    t2.join();
    t3.join();
    // Total time: max(time(task1), time(task2), time(task3))
}
```

### Thread vs Process

| Aspect | Process | Thread |
|--------|---------|--------|
| Memory | Separate address space | Shares process memory |
| Creation | Expensive | Lightweight |
| Communication | IPC (slow) | Shared memory (fast) |
| Isolation | High | Low |
| Context Switch | Slow | Fast |

---

## Platform Threads vs Virtual Threads (Java 21)

### Platform Threads (Traditional)

**Platform threads** are 1:1 mapped to OS threads. They are **expensive** to create and maintain.

```java
// Creating platform thread
Thread platformThread = new Thread(() -> {
    System.out.println("Platform thread: " + Thread.currentThread());
});
platformThread.start();

// Platform threads are limited by OS
// Typical limit: 1000-5000 threads
```

### Virtual Threads (Java 21 - Project Loom)

**Virtual threads** are lightweight threads managed by the JVM. They are **cheap** to create and can scale to millions.

```java
// Creating virtual thread (Java 21)
Thread virtualThread = Thread.startVirtualThread(() -> {
    System.out.println("Virtual thread: " + Thread.currentThread());
});

// Or using Thread.ofVirtual()
Thread vThread = Thread.ofVirtual()
    .name("my-virtual-thread")
    .start(() -> {
        System.out.println("Virtual: " + Thread.currentThread().getName());
    });

// Virtual threads allow massive concurrency
// Can create millions of virtual threads
for (int i = 0; i < 1_000_000; i++) {
    Thread.startVirtualThread(() -> {
        // Some task
    });
}
```

### Platform vs Virtual Comparison

```java
// Platform threads - limited scalability
void platformThreadExample() throws InterruptedException {
    long start = System.currentTimeMillis();
    
    List<Thread> threads = new ArrayList<>();
    for (int i = 0; i < 10_000; i++) {
        Thread t = new Thread(() -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        threads.add(t);
        t.start();
    }
    
    for (Thread t : threads) {
        t.join();
    }
    
    System.out.println("Time: " + (System.currentTimeMillis() - start));
    // May fail with OutOfMemoryError or take very long
}

// Virtual threads - massive scalability
void virtualThreadExample() throws InterruptedException {
    long start = System.currentTimeMillis();
    
    List<Thread> threads = new ArrayList<>();
    for (int i = 0; i < 10_000; i++) {
        Thread t = Thread.startVirtualThread(() -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        threads.add(t);
    }
    
    for (Thread t : threads) {
        t.join();
    }
    
    System.out.println("Time: " + (System.currentTimeMillis() - start));
    // Completes in ~1 second
}
```

### When to Use Virtual Threads

```java
// ✅ GOOD: I/O-bound tasks
Thread.startVirtualThread(() -> {
    try {
        URL url = new URL("https://example.com");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        // Read response
    } catch (Exception e) {
        e.printStackTrace();
    }
});

// ✅ GOOD: Blocking operations
Thread.startVirtualThread(() -> {
    try (Socket socket = new Socket("localhost", 8080)) {
        // Network I/O
    } catch (Exception e) {
        e.printStackTrace();
    }
});

// ❌ BAD: CPU-intensive tasks (use platform threads or parallel streams)
Thread.ofPlatform().start(() -> {
    // Heavy computation
    for (int i = 0; i < 1_000_000_000; i++) {
        // CPU work
    }
});
```

---

## Creating Threads

### Method 1: Extending Thread Class

```java
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread running: " + Thread.currentThread().getName());
        for (int i = 0; i < 5; i++) {
            System.out.println(i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// Usage
MyThread thread = new MyThread();
thread.setName("Worker-1");
thread.start();  // Starts execution in new thread
```

### Method 2: Implementing Runnable

```java
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable running: " + Thread.currentThread().getName());
    }
}

// Usage
Thread thread = new Thread(new MyRunnable());
thread.start();

// Anonymous class
Thread thread2 = new Thread(new Runnable() {
    @Override
    public void run() {
        System.out.println("Anonymous runnable");
    }
});
thread2.start();

// Lambda expression (preferred)
Thread thread3 = new Thread(() -> {
    System.out.println("Lambda runnable");
});
thread3.start();
```

### Common Thread Methods

```java
Thread thread = new Thread(() -> {
    System.out.println("Running...");
});

// Start thread
thread.start();

// Get thread name
String name = thread.getName();
thread.setName("Worker-Thread");

// Get/set priority (1-10, default 5)
int priority = thread.getPriority();
thread.setPriority(Thread.MAX_PRIORITY);  // 10

// Check if alive
boolean isAlive = thread.isAlive();

// Wait for thread to complete
thread.join();

// Sleep current thread
Thread.sleep(1000);  // 1 second

// Get current thread
Thread current = Thread.currentThread();
```

---

## Thread Lifecycle

A thread goes through several states during its lifecycle.

### Thread States

```java
public enum State {
    NEW,           // Created but not started
    RUNNABLE,      // Running or ready to run
    BLOCKED,       // Waiting for monitor lock
    WAITING,       // Waiting indefinitely
    TIMED_WAITING, // Waiting for specified time
    TERMINATED     // Execution completed
}

// Checking thread state
Thread thread = new Thread(() -> {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
});

System.out.println(thread.getState());  // NEW

thread.start();
System.out.println(thread.getState());  // RUNNABLE

Thread.sleep(100);
System.out.println(thread.getState());  // TIMED_WAITING (sleeping)

thread.join();
System.out.println(thread.getState());  // TERMINATED
```

### State Transitions

```java
class ThreadStateDemo {
    public static void main(String[] args) throws InterruptedException {
        Object lock = new Object();
        
        // Thread will be in WAITING state
        Thread waitingThread = new Thread(() -> {
            synchronized (lock) {
                try {
                    lock.wait();  // WAITING state
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });
        
        // Thread will be in TIMED_WAITING state
        Thread timedWaitingThread = new Thread(() -> {
            try {
                Thread.sleep(5000);  // TIMED_WAITING state
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        
        // Thread will be in BLOCKED state
        Thread blockedThread = new Thread(() -> {
            synchronized (lock) {
                System.out.println("In synchronized block");
            }
        });
        
        System.out.println("Before start: " + waitingThread.getState());  // NEW
        
        waitingThread.start();
        timedWaitingThread.start();
        
        Thread.sleep(100);  // Give threads time to enter states
        
        System.out.println("Waiting: " + waitingThread.getState());        // WAITING
        System.out.println("Timed: " + timedWaitingThread.getState());     // TIMED_WAITING
        
        synchronized (lock) {
            blockedThread.start();
            Thread.sleep(100);
            System.out.println("Blocked: " + blockedThread.getState());    // BLOCKED
        }
        
        synchronized (lock) {
            lock.notify();  // Wake up waitingThread
        }
        
        waitingThread.join();
        timedWaitingThread.join();
        blockedThread.join();
        
        System.out.println("After join: " + waitingThread.getState());     // TERMINATED
    }
}
```

---

## Runnable vs Callable

### Runnable Interface

**No return value**, cannot throw checked exceptions.

```java
@FunctionalInterface
public interface Runnable {
    void run();
}

// Usage
Runnable task = () -> {
    System.out.println("Task running");
    // Cannot return value
    // Cannot throw checked exceptions
};

new Thread(task).start();
```

### Callable Interface

**Returns a value**, can throw checked exceptions.

```java
@FunctionalInterface
public interface Callable<V> {
    V call() throws Exception;
}

// Usage
Callable<Integer> task = () -> {
    System.out.println("Callable task");
    Thread.sleep(1000);
    return 42;  // Returns value
};

// Callable requires ExecutorService
ExecutorService executor = Executors.newSingleThreadExecutor();
Future<Integer> future = executor.submit(task);
Integer result = future.get();  // Blocks until result available
System.out.println("Result: " + result);  // 42

executor.shutdown();
```

### Comparison

```java
// Runnable - no return value
Runnable runnable = () -> {
    System.out.println("Runnable");
    // void - no return
};

// Callable - returns value
Callable<String> callable = () -> {
    System.out.println("Callable");
    return "Result";  // Returns value
};

// Callable can throw checked exceptions
Callable<String> callableWithException = () -> {
    if (new Random().nextBoolean()) {
        throw new IOException("Error");  // OK - checked exception
    }
    return "Success";
};

// Runnable cannot throw checked exceptions
Runnable runnableWithException = () -> {
    try {
        throw new IOException("Error");  // Must catch
    } catch (IOException e) {
        e.printStackTrace();
    }
};
```

---

## ExecutorService Framework

**ExecutorService** manages thread pools and task execution.

### Creating ExecutorService

```java
// Single thread executor
ExecutorService single = Executors.newSingleThreadExecutor();

// Fixed thread pool (n threads)
ExecutorService fixed = Executors.newFixedThreadPool(5);

// Cached thread pool (creates threads as needed)
ExecutorService cached = Executors.newCachedThreadPool();

// Scheduled thread pool (for delayed/periodic tasks)
ScheduledExecutorService scheduled = Executors.newScheduledThreadPool(3);

// Virtual thread executor (Java 21)
ExecutorService virtual = Executors.newVirtualThreadPerTaskExecutor();
```

### Submitting Tasks

```java
ExecutorService executor = Executors.newFixedThreadPool(3);

// Submit Runnable (no return value)
executor.submit(() -> {
    System.out.println("Task 1");
});

// Submit Callable (returns Future)
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(1000);
    return 42;
});

// Execute Runnable (fire and forget)
executor.execute(() -> {
    System.out.println("Task 2");
});

// Get result
try {
    Integer result = future.get();  // Blocks
    System.out.println("Result: " + result);
} catch (InterruptedException | ExecutionException e) {
    e.printStackTrace();
}

// Shutdown executor
executor.shutdown();
```

### Shutdown Methods

```java
ExecutorService executor = Executors.newFixedThreadPool(3);

// Submit tasks
executor.submit(() -> {
    try {
        Thread.sleep(5000);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
});

// shutdown() - graceful shutdown
// Stops accepting new tasks, waits for running tasks to complete
executor.shutdown();

// isShutdown() - check if shutdown initiated
System.out.println("Is shutdown: " + executor.isShutdown());  // true

// awaitTermination() - wait for shutdown to complete
try {
    boolean terminated = executor.awaitTermination(10, TimeUnit.SECONDS);
    System.out.println("Terminated: " + terminated);
} catch (InterruptedException e) {
    e.printStackTrace();
}

// shutdownNow() - forceful shutdown
// Stops accepting new tasks, attempts to stop running tasks
List<Runnable> notExecuted = executor.shutdownNow();
System.out.println("Not executed: " + notExecuted.size());

// isTerminated() - check if all tasks completed
System.out.println("Is terminated: " + executor.isTerminated());
```

---

## Thread Pools

### Fixed Thread Pool

Fixed number of threads. Tasks wait in queue if all threads busy.

```java
ExecutorService executor = Executors.newFixedThreadPool(3);

// Submit 10 tasks to 3 threads
for (int i = 0; i < 10; i++) {
    final int taskId = i;
    executor.submit(() -> {
        System.out.println("Task " + taskId + " by " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    });
}

executor.shutdown();
```

### Cached Thread Pool

Creates new threads as needed. Reuses idle threads. Good for many short tasks.

```java
ExecutorService executor = Executors.newCachedThreadPool();

// Efficiently handles varying load
for (int i = 0; i < 100; i++) {
    executor.submit(() -> {
        System.out.println(Thread.currentThread().getName());
    });
}

executor.shutdown();
```

### Single Thread Executor

Single worker thread. Tasks execute sequentially.

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

// Tasks execute one at a time in order
executor.submit(() -> System.out.println("Task 1"));
executor.submit(() -> System.out.println("Task 2"));
executor.submit(() -> System.out.println("Task 3"));
// Output: Task 1, Task 2, Task 3 (in order)

executor.shutdown();
```

### Scheduled Thread Pool

Schedules tasks with delay or periodic execution.

```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

// Execute after delay
scheduler.schedule(() -> {
    System.out.println("Executed after 3 seconds");
}, 3, TimeUnit.SECONDS);

// Execute periodically (fixed rate)
scheduler.scheduleAtFixedRate(() -> {
    System.out.println("Executing every 2 seconds");
}, 0, 2, TimeUnit.SECONDS);  // initialDelay=0, period=2

// Execute periodically (fixed delay)
scheduler.scheduleWithFixedDelay(() -> {
    System.out.println("Executing with 2 second delay");
}, 0, 2, TimeUnit.SECONDS);  // delay between completion and next start

// Cancel after 10 seconds
scheduler.schedule(() -> {
    scheduler.shutdown();
}, 10, TimeUnit.SECONDS);
```

---

## Future and CompletableFuture

### Future Interface

Represents result of asynchronous computation.

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

Future<Integer> future = executor.submit(() -> {
    Thread.sleep(2000);
    return 42;
});

// Check if done
System.out.println("Is done: " + future.isDone());  // false

// Get result (blocks until available)
try {
    Integer result = future.get();  // Blocks for 2 seconds
    System.out.println("Result: " + result);  // 42
} catch (InterruptedException | ExecutionException e) {
    e.printStackTrace();
}

// Get with timeout
try {
    Integer result = future.get(1, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    System.out.println("Timeout!");
}

// Cancel task
future.cancel(true);  // mayInterruptIfRunning

executor.shutdown();
```

### CompletableFuture (Java 8+)

More powerful asynchronous programming API.

```java
// Create CompletableFuture
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        e.printStackTrace();
    }
    return "Hello";
});

// Chain operations
future.thenApply(s -> s + " World")
      .thenApply(String::toUpperCase)
      .thenAccept(System.out::println);  // HELLO WORLD

// Combine futures
CompletableFuture<Integer> future1 = CompletableFuture.supplyAsync(() -> 10);
CompletableFuture<Integer> future2 = CompletableFuture.supplyAsync(() -> 20);

CompletableFuture<Integer> combined = future1.thenCombine(future2, (a, b) -> a + b);
System.out.println(combined.get());  // 30

// Handle exceptions
CompletableFuture<String> futureWithError = CompletableFuture.supplyAsync(() -> {
    if (true) throw new RuntimeException("Error!");
    return "Success";
}).exceptionally(ex -> {
    System.out.println("Handled: " + ex.getMessage());
    return "Default";
});

System.out.println(futureWithError.get());  // Default

// Run async without return value
CompletableFuture<Void> async = CompletableFuture.runAsync(() -> {
    System.out.println("Async task");
});
async.join();  // Wait for completion
```

---

## Best Practices

### 1. Always Shutdown Executors

```java
ExecutorService executor = Executors.newFixedThreadPool(5);
try {
    // Submit tasks
    executor.submit(() -> {
        // Task code
    });
} finally {
    executor.shutdown();
}
```

### 2. Use Virtual Threads for I/O-Bound Tasks

```java
// ✅ GOOD: Virtual threads for I/O
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
try {
    for (int i = 0; i < 1_000_000; i++) {
        executor.submit(() -> {
            // I/O operation
        });
    }
} finally {
    executor.shutdown();
}
```

### 3. Handle InterruptedException Properly

```java
// ✅ GOOD
public void run() {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();  // Restore interrupt status
        // Clean up
    }
}

// ❌ BAD - swallows interrupt
public void run() {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        // Do nothing
    }
}
```

### 4. Prefer ExecutorService over Manual Threads

```java
// ❌ BAD
for (int i = 0; i < 100; i++) {
    new Thread(() -> {
        // Task
    }).start();
}

// ✅ GOOD
ExecutorService executor = Executors.newFixedThreadPool(10);
for (int i = 0; i < 100; i++) {
    executor.submit(() -> {
        // Task
    });
}
executor.shutdown();
```

---

## Summary and Exam Tips

### Key Concepts

- **Platform threads**: 1:1 mapped to OS threads, expensive
- **Virtual threads**: JVM-managed, lightweight, millions possible
- **Runnable**: No return value, no checked exceptions
- **Callable**: Returns value, can throw checked exceptions
- **ExecutorService**: Manages thread pools
- **Future**: Result of async computation

### Exam Tips

- Virtual threads are **Java 21** feature (Project Loom)
- `thread.start()` creates new thread; `thread.run()` executes in current thread
- `Thread.sleep()` throws `InterruptedException`
- `executor.shutdown()` waits for tasks; `shutdownNow()` stops immediately
- `future.get()` blocks until result available
- `future.get(timeout)` throws `TimeoutException` if not ready
- Fixed pool has fixed threads; cached pool creates as needed
- Single thread executor executes tasks **sequentially**
- Scheduled executor supports delayed and periodic tasks

---

**Next:** [Practice Questions - Threads and Executors](29-practice-questions.md)
