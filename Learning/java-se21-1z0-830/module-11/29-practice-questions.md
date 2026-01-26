# Module 11: Practice Questions - Threads and Executors

## Questions (20)

---

### Question 1
```java
Thread thread = new Thread(() -> System.out.println("Running"));
thread.run();
```
What happens?

**A)** Creates new thread and prints "Running"  
**B)** Prints "Running" in current thread  
**C)** Compilation error  
**D)** RuntimeException

**Answer: B)**

**Explanation:** `run()` executes in the **current thread**, not a new thread. Use `start()` to create a new thread.

```java
thread.start(); // Correct - creates new thread
```

---

### Question 2
```java
Runnable task = () -> {
    return 42;
};
```
What happens?

**A)** Compiles successfully  
**B)** Compilation error - void method cannot return value  
**C)** RuntimeException  
**D)** Returns 42

**Answer: B)**

**Explanation:** `Runnable.run()` has **void** return type. Cannot return value. Use `Callable` for return values.

```java
// Correct
Callable<Integer> task = () -> 42;
```

---

### Question 3
```java
ExecutorService executor = Executors.newFixedThreadPool(2);
executor.submit(() -> System.out.println("Task 1"));
executor.submit(() -> System.out.println("Task 2"));
executor.submit(() -> System.out.println("Task 3"));
```
How many threads are created?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** Depends on execution

**Answer: B)**

**Explanation:** `newFixedThreadPool(2)` creates exactly **2 threads**. All 3 tasks are executed by these 2 threads.

---

### Question 4
```java
ExecutorService executor = Executors.newSingleThreadExecutor();
executor.submit(() -> System.out.println("A"));
executor.submit(() -> System.out.println("B"));
executor.submit(() -> System.out.println("C"));
executor.shutdown();
```
What is guaranteed about the output?

**A)** Always prints A, B, C  
**B)** Always prints C, B, A  
**C)** Order is unpredictable  
**D)** May not print anything

**Answer: A)**

**Explanation:** Single thread executor executes tasks **sequentially** in submission order. Output: A, B, C

---

### Question 5
```java
Callable<Integer> task = () -> {
    Thread.sleep(1000);
    return 42;
};
ExecutorService executor = Executors.newSingleThreadExecutor();
Future<Integer> future = executor.submit(task);
executor.shutdown();
System.out.println(future.get());
```
What happens?

**A)** Prints 42 immediately  
**B)** Prints 42 after ~1 second  
**C)** Compilation error  
**D)** RejectedExecutionException

**Answer: B)**

**Explanation:** `future.get()` **blocks** until result is available. Task sleeps 1 second, then returns 42.

---

### Question 6
```java
Thread thread = new Thread(() -> {
    System.out.println("Running");
});
System.out.println(thread.getState());
```
What is printed?

**A)** RUNNABLE  
**B)** NEW  
**C)** TERMINATED  
**D)** WAITING

**Answer: B)**

**Explanation:** Thread is created but not started. State is **NEW**.

---

### Question 7
```java
ExecutorService executor = Executors.newCachedThreadPool();
for (int i = 0; i < 100; i++) {
    executor.submit(() -> {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {}
    });
}
executor.shutdown();
```
How many threads might be created?

**A)** 1  
**B)** 10  
**C)** Up to 100  
**D)** Exactly 100

**Answer: C)**

**Explanation:** Cached thread pool creates threads as needed. Since all tasks sleep, **up to 100** threads might be created.

---

### Question 8
```java
Thread thread = Thread.startVirtualThread(() -> {
    System.out.println("Virtual");
});
```
This code requires which Java version?

**A)** Java 8  
**B)** Java 11  
**C)** Java 17  
**D)** Java 21

**Answer: D)**

**Explanation:** Virtual threads (Project Loom) were introduced in **Java 21**.

---

### Question 9
```java
ExecutorService executor = Executors.newFixedThreadPool(3);
executor.shutdown();
executor.submit(() -> System.out.println("Task"));
```
What happens?

**A)** Prints "Task"  
**B)** RejectedExecutionException  
**C)** Compilation error  
**D)** Blocks indefinitely

**Answer: B)**

**Explanation:** After `shutdown()`, new tasks are **rejected** with `RejectedExecutionException`.

---

### Question 10
```java
Callable<String> task = () -> {
    if (true) throw new IOException("Error");
    return "Success";
};
```
Does this compile?

**A)** Yes  
**B)** No - must catch IOException  
**C)** No - Callable cannot throw exceptions  
**D)** No - syntax error

**Answer: A)**

**Explanation:** `Callable.call()` is declared as `V call() throws Exception`. Can throw **checked exceptions**.

---

### Question 11
```java
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(5000);
    return 42;
});
Integer result = future.get(1, TimeUnit.SECONDS);
```
What happens?

**A)** Returns 42 after 5 seconds  
**B)** Returns 42 after 1 second  
**C)** TimeoutException after 1 second  
**D)** Compilation error

**Answer: C)**

**Explanation:** `get(timeout)` throws **TimeoutException** if result not available within timeout (1 second < 5 seconds).

---

### Question 12
```java
Thread thread = new Thread(() -> {
    System.out.println(Thread.currentThread().getName());
});
thread.setName("Worker");
thread.start();
```
What is printed?

**A)** main  
**B)** Worker  
**C)** Thread-0  
**D)** null

**Answer: B)**

**Explanation:** Thread name is set to "Worker" before starting. Prints **Worker**.

---

### Question 13
```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
scheduler.schedule(() -> System.out.println("Task"), 3, TimeUnit.SECONDS);
scheduler.shutdown();
```
What happens?

**A)** Task executes after 3 seconds  
**B)** Task never executes  
**C)** Task executes immediately  
**D)** RejectedExecutionException

**Answer: A)**

**Explanation:** `shutdown()` waits for scheduled tasks to complete. Task executes after 3 seconds.

---

### Question 14
```java
ExecutorService executor = Executors.newFixedThreadPool(5);
executor.shutdownNow();
```
What does `shutdownNow()` do?

**A)** Waits for tasks to complete  
**B)** Immediately stops all tasks  
**C)** Attempts to stop running tasks  
**D)** Blocks until all tasks finish

**Answer: C)**

**Explanation:** `shutdownNow()` **attempts** to stop running tasks (interrupts them) and returns list of tasks that never started.

---

### Question 15
```java
Thread thread = new Thread(() -> {
    try {
        Thread.sleep(1000);
    } catch (InterruptedException e) {
        System.out.println("Interrupted");
    }
});
thread.start();
thread.interrupt();
```
What is printed?

**A)** Nothing  
**B)** Interrupted  
**C)** InterruptedException  
**D)** Depends on timing

**Answer: B) or D)**

**Most likely B)**, but **D)** is technically correct. If interrupt happens while sleeping, "Interrupted" is printed. Timing dependent.

**Answer: B)**

---

### Question 16
```java
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> "Hello");
future.thenApply(s -> s + " World");
System.out.println(future.get());
```
What is printed?

**A)** Hello World  
**B)** Hello  
**C)** World  
**D)** Compilation error

**Answer: B)**

**Explanation:** `thenApply()` returns **new CompletableFuture**. Original `future` still contains "Hello".

```java
// Correct
CompletableFuture<String> result = future.thenApply(s -> s + " World");
System.out.println(result.get()); // Hello World
```

---

### Question 17
```java
ExecutorService executor = Executors.newSingleThreadExecutor();
Future<?> future = executor.submit(() -> {
    while (true) {
        // Infinite loop
    }
});
future.cancel(true);
```
What happens?

**A)** Task stops immediately  
**B)** Task is interrupted  
**C)** Task continues running  
**D)** Compilation error

**Answer: B)**

**Explanation:** `cancel(true)` **interrupts** the thread. Task must check interrupt status to stop.

```java
// Task should handle interruption
while (!Thread.currentThread().isInterrupted()) {
    // Work
}
```

---

### Question 18
```java
Thread thread = new Thread(() -> {
    System.out.println("Running");
});
thread.start();
thread.start();
```
What happens?

**A)** Prints "Running" twice  
**B)** IllegalThreadStateException  
**C)** Compilation error  
**D)** Prints "Running" once

**Answer: B)**

**Explanation:** Cannot call `start()` twice on same thread. Throws **IllegalThreadStateException**.

---

### Question 19
```java
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
for (int i = 0; i < 1_000_000; i++) {
    executor.submit(() -> {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {}
    });
}
executor.shutdown();
executor.awaitTermination(10, TimeUnit.SECONDS);
```
What is true about virtual threads?

**A)** Limited to ~10,000 threads  
**B)** Can create millions of threads  
**C)** Same as platform threads  
**D)** Not available in Java 21

**Answer: B)**

**Explanation:** Virtual threads are **lightweight** and can scale to **millions**. This code creates 1 million virtual threads.

---

### Question 20
```java
Future<Integer> future = executor.submit(() -> {
    return 42;
});
System.out.println(future.isDone());
Thread.sleep(100);
System.out.println(future.isDone());
```
What is the most likely output?

**A)** false, false  
**B)** true, true  
**C)** false, true  
**D)** true, false

**Answer: C)**

**Explanation:** Initially task may not be done (**false**). After 100ms sleep, task likely completed (**true**).

---

## Score Interpretation

- **18-20 correct**: Excellent! You master threads and executors.
- **15-17 correct**: Good grasp. Review ExecutorService shutdown and Future.
- **12-14 correct**: Fair understanding. Study thread lifecycle and virtual threads.
- **Below 12**: Need more practice. Review all concurrency basics.

---

**Previous:** [Theory - Threads and Executors](29-threads-executors.md)  
**Next:** [Theory - Thread Safety](30-thread-safety.md)
