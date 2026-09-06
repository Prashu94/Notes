### Introducing Threads
1. Thread is the smallest unit of execution that can be scheduled by the operating system.
2. A process is a group of associated threads that execute in the shared environment.
3. Single Threaded: Contains exactly one thread
4. Multi-Threaded: Contains one or more threads.
5. JVM : creates 2 different types of platform threads:
	- System Thread: Created by JVM
	- User Defined thread: Created by the application developer.
6. Shared Memory: Referring to static variables as well as instance variables passed to a thread. For example: If one threaded updates the value of a static variable, this information is immediately available for other threads within the process to read.
7. Each time the virtual thread is ready to run , it waits for a carrier thread to be available. The virtual thread does not automatically get the same carrier thread. 
### Thread Concurrency
1. Property of executing multiple threads and processes at the same time is referred to as concurrency.
2. A thread scheduler determines which threads should be currently executing. For example: A Thread scheduler may employ a round-robin schedule in which each available thread receives an equal number of CPU cycles with which to execute, with threads visited in a circular order.
3. A context switch is the process of storing the thread's current state and later restoring the state of the thread to continue execution. 
4. Thread Priority is a numeric value associated with a thread that the scheduler considers when determining which threads should execute. The priority can be set from 1 (Thread.MIN_PRIORITY) to 10 (Thread.MAX_PRIORITY)
```
	var thread1 = new Thread(() -> System.out.println("super Important"));
	thread1.setPriority(Thread.MAX_PRIORITY);
	thread1.start();
	
	var thread2 = new Thread(() -> System.out.println("Less Important"));
	thread2.start();
	thread2.setPriority(2);
```

### Creating a Thread
1. One of the most common ways to define a task for a thread is by using the Runnable interface, which takes no arguments and returns no data.
```
	@FunctionalInterface public interface Runnable {
		void run();
	}
	
	Thread.ofPlatform().start(() -> System.out.println("Hello"));
	System.out.println("World");
```


```
Platform Type -  Factory
var builder = Thread.ofPlatform();
Thread thread = builder.start(runnable);

Virtual Type - Factory
var builder = Thread.ofVirtual();
Thread thread = builder.start(runnable);

Platform Type - Constructor
Thread thread = new Thread(runnable);
thread.start();

```
join() method tells the main() method not to end before the three threads have completed.
run() - synchronous, start() - asynchronous

2. Daemon Threads : One that will not prevent the JVM from exiting when the program finishes.
![[Pasted image 20260905130019.png]]

### Creating Threads with Concurrency API
1. Java includes java.util.concurrent package, which we refer to as concurrency API, to handle the work of managing threads for you.
2. The concurrency API includes the ExecutorService interface, which defines services that create and manage threads.
3. First obtain the instance fo ExecutorService interface, and then you send the service tasks to be processed. The framework includes numerous features , such as thread pooling and scheduling. 
4. The Concurrency API includes the Executors factory class that can be used to create instances of the ExecutorService object. 
```
	try(ExecutorService service = 
	Executors.newSingleThreadExecutor()) {
		System.out.println("begin");
		service.execute(printInventory);
		service.execute(printRecords);
		service.execute(printInventiory);
		System.out.println("end");
	}
```

### Submitting Tasks
1. execute() method is fire and forget, which takes the Runnable instance and completes the task aynchronously as the return type of the method is void.
2. submit() method is for synchronous operations and returns the Future instance that can be used to determine wherther the task is complete.
3. 