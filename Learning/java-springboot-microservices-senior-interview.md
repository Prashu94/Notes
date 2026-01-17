# Senior Java Developer Interview Questions (10+ Years Experience)
## Java, Spring Boot & Microservices

---

# Part 1: Advanced Java Concepts

## 1. Explain the Java Memory Model and how volatile keyword works at CPU level.

**Answer:**

The Java Memory Model (JMM) defines how threads interact through memory and what behaviors are allowed in concurrent execution.

**Memory Architecture:**
```
┌─────────────────────────────────────────────────────┐
│                    Main Memory                       │
│              (Shared Variables)                      │
└─────────────────────────────────────────────────────┘
         ↑↓                              ↑↓
┌─────────────────────┐        ┌─────────────────────┐
│   Thread 1          │        │   Thread 2          │
│  ┌───────────────┐  │        │  ┌───────────────┐  │
│  │ CPU Cache L1  │  │        │  │ CPU Cache L1  │  │
│  │ CPU Cache L2  │  │        │  │ CPU Cache L2  │  │
│  │ Registers     │  │        │  │ Registers     │  │
│  └───────────────┘  │        │  └───────────────┘  │
└─────────────────────┘        └─────────────────────┘
```

**Problems without volatile:**
1. **Visibility Problem**: Changes made by one thread may not be visible to others
2. **Reordering Problem**: Compiler/CPU may reorder instructions for optimization

**How volatile works:**

```java
class SharedData {
    private volatile boolean flag = false;
    private int data = 0;
    
    // Writer thread
    public void write() {
        data = 42;           // 1
        flag = true;         // 2 - volatile write (memory barrier)
    }
    
    // Reader thread
    public void read() {
        if (flag) {          // 3 - volatile read (memory barrier)
            System.out.println(data);  // 4 - guaranteed to see 42
        }
    }
}
```

**CPU Level Operations:**

1. **Store Buffer Flush**: On volatile write, CPU flushes store buffer to cache
2. **Cache Invalidation**: Other CPUs invalidate their cached copy
3. **Memory Barriers**: 
   - **LoadLoad**: Prevents reordering of reads before volatile read
   - **StoreStore**: Prevents reordering of writes before volatile write
   - **LoadStore**: Prevents reordering of read before volatile write
   - **StoreLoad**: Full memory fence

**Happens-Before Guarantee:**
```java
// Everything before volatile write happens-before volatile read
Thread 1: x = 1; volatileVar = true;  // x=1 happens-before
Thread 2: if(volatileVar) { y = x; }   // y will see x=1
```

**When to use volatile vs synchronized:**

| Scenario | volatile | synchronized |
|----------|----------|--------------|
| Simple flag | ✓ | ✗ |
| Counter increment | ✗ | ✓ |
| Read-heavy, single writer | ✓ | ✗ |
| Compound operations | ✗ | ✓ |

---

## 2. Explain how ConcurrentHashMap achieves thread-safety and its internal implementation changes from Java 7 to Java 8+.

**Answer:**

**Java 7 Implementation (Segment-based locking):**

```java
// Conceptual structure
class ConcurrentHashMap<K,V> {
    final Segment<K,V>[] segments;  // Default 16 segments
    
    static class Segment<K,V> extends ReentrantLock {
        volatile HashEntry<K,V>[] table;
        int count;
    }
    
    static class HashEntry<K,V> {
        final K key;
        final int hash;
        volatile V value;
        final HashEntry<K,V> next;
    }
}
```

**Java 7 Characteristics:**
- 16 segments by default (concurrency level)
- Each segment is independently lockable
- Maximum 16 concurrent writes
- Lock striping technique

**Java 8+ Implementation (Node-based with CAS):**

```java
// Conceptual structure
class ConcurrentHashMap<K,V> {
    volatile Node<K,V>[] table;
    
    static class Node<K,V> {
        final int hash;
        final K key;
        volatile V val;
        volatile Node<K,V> next;
    }
    
    // TreeNode for bins with more than 8 entries
    static class TreeNode<K,V> extends Node<K,V> {
        TreeNode<K,V> parent, left, right;
    }
}
```

**Java 8 Operations:**

**Put Operation:**
```java
final V putVal(K key, V value, boolean onlyIfAbsent) {
    int hash = spread(key.hashCode());
    
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();  // CAS initialization
            
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            // Empty bucket - use CAS (no locking!)
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value)))
                break;
        }
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);  // Help with resizing
            
        else {
            // Bucket not empty - lock only this bucket
            synchronized (f) {
                // Add to linked list or tree
            }
        }
    }
}
```

**Get Operation (Lock-free):**
```java
public V get(Object key) {
    Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
    int h = spread(key.hashCode());
    
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (e = tabAt(tab, (n - 1) & h)) != null) {
        
        // volatile read - no locking needed
        if ((eh = e.hash) == h) {
            if ((ek = e.key) == key || (ek != null && key.equals(ek)))
                return e.val;
        }
        // Search in tree or linked list
    }
    return null;
}
```

**Key Improvements in Java 8:**

| Feature | Java 7 | Java 8+ |
|---------|--------|---------|
| **Locking** | Segment lock | Per-bucket lock |
| **Empty bucket insert** | Segment lock | CAS (lock-free) |
| **Read operations** | Nearly lock-free | Completely lock-free |
| **Collision handling** | Linked list | Linked list → Red-Black tree |
| **Tree threshold** | N/A | 8 nodes |
| **Concurrency** | Fixed (16) | Dynamic (n buckets) |

**Atomic Operations in Java 8:**

```java
// Atomic compute operations
map.compute(key, (k, v) -> v == null ? 1 : v + 1);
map.computeIfAbsent(key, k -> expensiveComputation(k));
map.computeIfPresent(key, (k, v) -> v + 1);
map.merge(key, 1, Integer::sum);

// These are atomic and thread-safe
```

---

## 3. What is the difference between strong, soft, weak, and phantom references? When would you use each?

**Answer:**

**Reference Types Hierarchy:**

```java
// Strong Reference (default)
Object obj = new Object();

// Soft Reference
SoftReference<Object> softRef = new SoftReference<>(new Object());

// Weak Reference
WeakReference<Object> weakRef = new WeakReference<>(new Object());

// Phantom Reference
ReferenceQueue<Object> queue = new ReferenceQueue<>();
PhantomReference<Object> phantomRef = new PhantomReference<>(new Object(), queue);
```

**Comparison:**

| Type | GC Behavior | Use Case | Memory Pressure |
|------|-------------|----------|-----------------|
| **Strong** | Never collected while reachable | Normal objects | N/A |
| **Soft** | Collected before OOM | Caching | Low priority cleanup |
| **Weak** | Collected at next GC | Canonical mappings | High priority cleanup |
| **Phantom** | Already finalized | Pre-mortem cleanup | Resource cleanup |

**1. Strong Reference:**
```java
// Object won't be GC'd while strong reference exists
Object obj = new Object();
obj = null;  // Now eligible for GC
```

**2. Soft Reference (Memory-sensitive cache):**
```java
class ImageCache {
    private Map<String, SoftReference<Image>> cache = new HashMap<>();
    
    public Image getImage(String path) {
        SoftReference<Image> ref = cache.get(path);
        Image image = (ref != null) ? ref.get() : null;
        
        if (image == null) {
            image = loadImage(path);
            cache.put(path, new SoftReference<>(image));
        }
        return image;
    }
}

// JVM will clear soft references before throwing OutOfMemoryError
// Good for caches - keeps data as long as memory permits
```

**3. Weak Reference (Canonical mappings):**
```java
// WeakHashMap example - keys are weak references
WeakHashMap<Key, Value> cache = new WeakHashMap<>();

Key key = new Key("data");
cache.put(key, new Value("cached"));

key = null;  // Key has no strong reference
System.gc();
// Entry is removed from WeakHashMap automatically

// Use case: Listeners that shouldn't prevent GC
class EventManager {
    private List<WeakReference<EventListener>> listeners = new ArrayList<>();
    
    public void addListener(EventListener listener) {
        listeners.add(new WeakReference<>(listener));
    }
    
    public void fireEvent(Event event) {
        Iterator<WeakReference<EventListener>> it = listeners.iterator();
        while (it.hasNext()) {
            EventListener listener = it.next().get();
            if (listener == null) {
                it.remove();  // Clean up dead references
            } else {
                listener.onEvent(event);
            }
        }
    }
}
```

**4. Phantom Reference (Resource cleanup):**
```java
class ResourceCleaner {
    private ReferenceQueue<LargeResource> queue = new ReferenceQueue<>();
    private Map<PhantomReference<LargeResource>, NativeHandle> resources = new HashMap<>();
    
    public LargeResource create() {
        LargeResource resource = new LargeResource();
        NativeHandle handle = resource.getNativeHandle();
        
        PhantomReference<LargeResource> ref = 
            new PhantomReference<>(resource, queue);
        resources.put(ref, handle);
        
        return resource;
    }
    
    // Cleanup thread
    public void cleanupLoop() {
        while (true) {
            PhantomReference<LargeResource> ref = 
                (PhantomReference<LargeResource>) queue.remove();  // Blocks
            
            NativeHandle handle = resources.remove(ref);
            handle.close();  // Clean up native resource
            ref.clear();
        }
    }
}

// Phantom references:
// - get() always returns null
// - Enqueued AFTER object is finalized but BEFORE memory reclaimed
// - Better than finalize() for cleanup
```

**Java 9+ Cleaner API (Preferred over Phantom References):**
```java
class Resource implements AutoCloseable {
    private static final Cleaner cleaner = Cleaner.create();
    private final Cleaner.Cleanable cleanable;
    private final NativeHandle handle;
    
    public Resource() {
        this.handle = allocateNative();
        this.cleanable = cleaner.register(this, new CleanupAction(handle));
    }
    
    @Override
    public void close() {
        cleanable.clean();
    }
    
    private static class CleanupAction implements Runnable {
        private final NativeHandle handle;
        
        CleanupAction(NativeHandle handle) {
            this.handle = handle;
        }
        
        @Override
        public void run() {
            handle.release();
        }
    }
}
```

---

## 4. Explain the Fork/Join framework and how work-stealing algorithm works.

**Answer:**

The Fork/Join framework is designed for parallel execution of divide-and-conquer algorithms.

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│                  ForkJoinPool                        │
│  ┌─────────────────────────────────────────────┐    │
│  │  Worker Thread 1  │  Worker Thread 2  │ ... │    │
│  │  ┌─────────────┐  │  ┌─────────────┐  │     │    │
│  │  │ Deque       │  │  │ Deque       │  │     │    │
│  │  │ ┌─────────┐ │  │  │ ┌─────────┐ │  │     │    │
│  │  │ │ Task 1  │ │  │  │ │ Task 4  │ │  │     │    │
│  │  │ │ Task 2  │ │  │  │ │ Task 5  │ │  │     │    │
│  │  │ │ Task 3  │ │  │  │ └─────────┘ │  │     │    │
│  │  │ └─────────┘ │  │  └─────────────┘  │     │    │
│  │  └─────────────┘  └───────────────────┘     │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
              ↓ Work Stealing ↓
    Thread 2 steals from Thread 1's deque (from tail)
```

**Work-Stealing Algorithm:**

1. Each worker thread has its own double-ended queue (deque)
2. Worker pushes/pops tasks from HEAD of its own deque (LIFO)
3. When idle, worker STEALS from TAIL of another worker's deque (FIFO)
4. Stealing from tail reduces contention with the owner

**Example Implementation:**

```java
// RecursiveTask returns a result
class SumTask extends RecursiveTask<Long> {
    private static final int THRESHOLD = 10000;
    private final long[] array;
    private final int start, end;
    
    public SumTask(long[] array, int start, int end) {
        this.array = array;
        this.start = start;
        this.end = end;
    }
    
    @Override
    protected Long compute() {
        int length = end - start;
        
        // Base case - compute directly
        if (length <= THRESHOLD) {
            long sum = 0;
            for (int i = start; i < end; i++) {
                sum += array[i];
            }
            return sum;
        }
        
        // Recursive case - split and fork
        int mid = start + length / 2;
        
        SumTask leftTask = new SumTask(array, start, mid);
        SumTask rightTask = new SumTask(array, mid, end);
        
        // Fork left task (runs asynchronously)
        leftTask.fork();
        
        // Compute right task in current thread
        long rightResult = rightTask.compute();
        
        // Join left task (wait for result)
        long leftResult = leftTask.join();
        
        return leftResult + rightResult;
    }
}

// Usage
ForkJoinPool pool = ForkJoinPool.commonPool();
long[] array = new long[10000000];
Arrays.fill(array, 1);

SumTask task = new SumTask(array, 0, array.length);
long sum = pool.invoke(task);
System.out.println("Sum: " + sum);  // 10000000
```

**RecursiveAction (no return value):**
```java
class ParallelSort extends RecursiveAction {
    private static final int THRESHOLD = 10000;
    private final int[] array;
    private final int start, end;
    
    @Override
    protected void compute() {
        if (end - start <= THRESHOLD) {
            Arrays.sort(array, start, end);
        } else {
            int mid = start + (end - start) / 2;
            invokeAll(
                new ParallelSort(array, start, mid),
                new ParallelSort(array, mid, end)
            );
            merge(array, start, mid, end);
        }
    }
}
```

**Best Practices:**

```java
// DO: Fork-Compute-Join pattern
leftTask.fork();
rightResult = rightTask.compute();  // Use current thread
leftResult = leftTask.join();

// DON'T: Fork both (wastes current thread)
leftTask.fork();
rightTask.fork();
leftResult = leftTask.join();
rightResult = rightTask.join();

// DO: Use invokeAll for multiple tasks
invokeAll(task1, task2, task3);

// DO: Choose appropriate threshold
// Too small = overhead of task creation
// Too large = poor parallelism
```

**CompletableFuture with ForkJoinPool:**
```java
CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
    // Runs in ForkJoinPool.commonPool() by default
    return "Result";
});

// Chain operations
future.thenApply(s -> s.toUpperCase())
      .thenAccept(System.out::println);
```

---

## 5. What are the different ways to create immutable objects in Java? Explain with thread-safety considerations.

**Answer:**

**1. Traditional Approach:**

```java
public final class ImmutablePerson {
    private final String name;
    private final int age;
    private final List<String> hobbies;
    private final Address address;  // Mutable object
    
    public ImmutablePerson(String name, int age, List<String> hobbies, Address address) {
        this.name = name;
        this.age = age;
        // Defensive copy for mutable collections
        this.hobbies = new ArrayList<>(hobbies);
        // Deep copy for mutable objects
        this.address = new Address(address);
    }
    
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
    
    // Return defensive copy
    public List<String> getHobbies() {
        return new ArrayList<>(hobbies);
    }
    
    // Return copy of mutable object
    public Address getAddress() {
        return new Address(address);
    }
}
```

**2. Java 16+ Records:**

```java
public record Person(String name, int age, List<String> hobbies) {
    // Compact constructor for validation and defensive copying
    public Person {
        Objects.requireNonNull(name, "Name cannot be null");
        if (age < 0) throw new IllegalArgumentException("Age cannot be negative");
        hobbies = List.copyOf(hobbies);  // Immutable copy
    }
    
    // Override getter if needed
    @Override
    public List<String> hobbies() {
        return hobbies;  // Already immutable from constructor
    }
}

// Usage
Person person = new Person("John", 30, List.of("Reading", "Gaming"));
```

**3. Builder Pattern for Immutable Objects:**

```java
public final class ImmutableConfig {
    private final String host;
    private final int port;
    private final int timeout;
    private final boolean ssl;
    private final Map<String, String> properties;
    
    private ImmutableConfig(Builder builder) {
        this.host = builder.host;
        this.port = builder.port;
        this.timeout = builder.timeout;
        this.ssl = builder.ssl;
        this.properties = Map.copyOf(builder.properties);
    }
    
    // Only getters, no setters
    public String getHost() { return host; }
    public int getPort() { return port; }
    public int getTimeout() { return timeout; }
    public boolean isSsl() { return ssl; }
    public Map<String, String> getProperties() { return properties; }
    
    // Create modified copy
    public ImmutableConfig withPort(int newPort) {
        return new Builder(this).port(newPort).build();
    }
    
    public static class Builder {
        private String host = "localhost";
        private int port = 8080;
        private int timeout = 30000;
        private boolean ssl = false;
        private Map<String, String> properties = new HashMap<>();
        
        public Builder() {}
        
        // Copy constructor
        public Builder(ImmutableConfig config) {
            this.host = config.host;
            this.port = config.port;
            this.timeout = config.timeout;
            this.ssl = config.ssl;
            this.properties = new HashMap<>(config.properties);
        }
        
        public Builder host(String host) {
            this.host = host;
            return this;
        }
        
        public Builder port(int port) {
            this.port = port;
            return this;
        }
        
        public Builder timeout(int timeout) {
            this.timeout = timeout;
            return this;
        }
        
        public Builder ssl(boolean ssl) {
            this.ssl = ssl;
            return this;
        }
        
        public Builder property(String key, String value) {
            this.properties.put(key, value);
            return this;
        }
        
        public ImmutableConfig build() {
            validate();
            return new ImmutableConfig(this);
        }
        
        private void validate() {
            if (host == null || host.isEmpty()) {
                throw new IllegalStateException("Host is required");
            }
            if (port <= 0 || port > 65535) {
                throw new IllegalStateException("Invalid port");
            }
        }
    }
}

// Usage
ImmutableConfig config = new ImmutableConfig.Builder()
    .host("api.example.com")
    .port(443)
    .ssl(true)
    .property("apiKey", "secret")
    .build();

// Create modified copy
ImmutableConfig newConfig = config.withPort(8443);
```

**4. Using Lombok:**

```java
@Value  // Makes class immutable
@Builder(toBuilder = true)  // Allows creating modified copies
public class ImmutableUser {
    String username;
    String email;
    @Singular List<String> roles;
}

// Usage
ImmutableUser user = ImmutableUser.builder()
    .username("john")
    .email("john@example.com")
    .role("USER")
    .role("ADMIN")
    .build();

// Create modified copy
ImmutableUser modified = user.toBuilder()
    .email("john.doe@example.com")
    .build();
```

**Thread-Safety Guarantees:**

```java
// Immutable objects are inherently thread-safe
public final class ThreadSafeCounter {
    private final int count;
    
    public ThreadSafeCounter(int count) {
        this.count = count;
    }
    
    public ThreadSafeCounter increment() {
        return new ThreadSafeCounter(count + 1);  // Return new instance
    }
    
    public int getCount() {
        return count;
    }
}

// Safe publication
class Publisher {
    // volatile ensures visibility
    private volatile ThreadSafeCounter counter = new ThreadSafeCounter(0);
    
    public void increment() {
        // Even though this isn't atomic, the counter object itself is immutable
        counter = counter.increment();
    }
    
    public int getCount() {
        return counter.getCount();
    }
}
```

**Immutable Collections (Java 9+):**

```java
// Factory methods return immutable collections
List<String> list = List.of("a", "b", "c");
Set<String> set = Set.of("a", "b", "c");
Map<String, Integer> map = Map.of("a", 1, "b", 2);

// Immutable copies
List<String> immutableCopy = List.copyOf(mutableList);
Map<K, V> immutableMap = Map.copyOf(mutableMap);
```

---

# Part 2: Spring Boot Advanced Concepts

## 6. Explain Spring Boot auto-configuration mechanism. How does @Conditional work?

**Answer:**

**Auto-Configuration Flow:**

```
Application Startup
        ↓
spring.factories loaded
(META-INF/spring.factories)
        ↓
@EnableAutoConfiguration processes
Auto-configuration classes
        ↓
@Conditional annotations evaluated
        ↓
Beans created if conditions match
```

**How Spring Boot Finds Auto-Configurations:**

```properties
# META-INF/spring.factories (Spring Boot 2.x)
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  com.example.MyAutoConfiguration,\
  com.example.AnotherAutoConfiguration

# META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports (Spring Boot 3.x)
com.example.MyAutoConfiguration
com.example.AnotherAutoConfiguration
```

**Creating Custom Auto-Configuration:**

```java
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
@ConditionalOnProperty(prefix = "custom.datasource", name = "enabled", havingValue = "true")
@EnableConfigurationProperties(CustomDataSourceProperties.class)
public class CustomDataSourceAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public DataSource customDataSource(CustomDataSourceProperties properties) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(properties.getUrl());
        config.setUsername(properties.getUsername());
        config.setPassword(properties.getPassword());
        config.setMaximumPoolSize(properties.getMaxPoolSize());
        return new HikariDataSource(config);
    }
    
    @Bean
    @ConditionalOnBean(DataSource.class)
    @ConditionalOnMissingBean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}

@ConfigurationProperties(prefix = "custom.datasource")
@Validated
public class CustomDataSourceProperties {
    @NotBlank
    private String url;
    private String username;
    private String password;
    private int maxPoolSize = 10;
    
    // Getters and setters
}
```

**@Conditional Annotations:**

```java
// 1. @ConditionalOnClass - Bean/Class exists in classpath
@ConditionalOnClass(name = "com.mongodb.client.MongoClient")
public MongoTemplate mongoTemplate() { }

// 2. @ConditionalOnMissingClass - Class NOT in classpath
@ConditionalOnMissingClass("com.mongodb.client.MongoClient")
public void fallbackConfig() { }

// 3. @ConditionalOnBean - Bean exists in context
@ConditionalOnBean(DataSource.class)
public JdbcTemplate jdbcTemplate(DataSource ds) { }

// 4. @ConditionalOnMissingBean - Bean NOT in context
@ConditionalOnMissingBean(DataSource.class)
public DataSource defaultDataSource() { }

// 5. @ConditionalOnProperty - Property has specific value
@ConditionalOnProperty(
    prefix = "feature",
    name = "enabled",
    havingValue = "true",
    matchIfMissing = false
)
public FeatureService featureService() { }

// 6. @ConditionalOnResource - Resource exists
@ConditionalOnResource(resources = "classpath:custom-config.xml")
public void loadCustomConfig() { }

// 7. @ConditionalOnWebApplication - Web application
@ConditionalOnWebApplication(type = Type.SERVLET)
public WebConfig webConfig() { }

// 8. @ConditionalOnExpression - SpEL expression
@ConditionalOnExpression("${feature.enabled:false} and ${feature.version} > 2")
public void advancedFeature() { }

// 9. Custom Condition
@Conditional(OnProductionEnvironmentCondition.class)
public void productionOnlyBean() { }
```

**Custom Condition Implementation:**

```java
public class OnProductionEnvironmentCondition implements Condition {
    
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        Environment env = context.getEnvironment();
        String[] activeProfiles = env.getActiveProfiles();
        
        return Arrays.asList(activeProfiles).contains("prod") ||
               Arrays.asList(activeProfiles).contains("production");
    }
}

// Usage
@Configuration
@Conditional(OnProductionEnvironmentCondition.class)
public class ProductionConfig {
    // Only loaded in production
}
```

**Auto-Configuration Order:**

```java
@AutoConfiguration
@AutoConfigureBefore(DataSourceAutoConfiguration.class)
@AutoConfigureAfter(JpaRepositoriesAutoConfiguration.class)
@AutoConfigureOrder(Ordered.HIGHEST_PRECEDENCE)
public class MyAutoConfiguration {
    // Runs before DataSourceAutoConfiguration
    // Runs after JpaRepositoriesAutoConfiguration
}
```

**Debugging Auto-Configuration:**

```yaml
# application.yml
debug: true  # Prints auto-configuration report

logging:
  level:
    org.springframework.boot.autoconfigure: DEBUG
```

```bash
# Output shows:
# Positive matches (what was configured)
# Negative matches (what was not configured and why)
# Exclusions
# Unconditional classes
```

---

## 7. How does Spring handle transactions? Explain propagation levels and isolation levels.

**Answer:**

**Transaction Management Architecture:**

```
@Transactional Method Call
        ↓
Spring AOP Proxy intercepts
        ↓
TransactionInterceptor invoked
        ↓
PlatformTransactionManager
   (DataSourceTransactionManager,
    JpaTransactionManager, etc.)
        ↓
Begin/Commit/Rollback Transaction
```

**@Transactional Proxy Behavior:**

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private PaymentService paymentService;
    
    @Transactional
    public void createOrder(Order order) {
        orderRepository.save(order);
        paymentService.processPayment(order);  // Separate transaction?
    }
    
    // IMPORTANT: Self-invocation bypasses proxy!
    public void publicMethod() {
        internalMethod();  // @Transactional won't work!
    }
    
    @Transactional
    public void internalMethod() {
        // Transaction not started when called from publicMethod()
    }
}
```

**Propagation Levels:**

```java
public enum Propagation {
    REQUIRED,       // Default - Join existing or create new
    REQUIRES_NEW,   // Always create new, suspend existing
    SUPPORTS,       // Join if exists, else non-transactional
    NOT_SUPPORTED,  // Always non-transactional, suspend if exists
    MANDATORY,      // Must have existing, else exception
    NEVER,          // Must not have existing, else exception
    NESTED          // Nested transaction with savepoint
}
```

**Propagation Examples:**

```java
@Service
public class TransactionExamples {
    
    // REQUIRED (Default)
    @Transactional(propagation = Propagation.REQUIRED)
    public void required() {
        // Joins existing transaction or creates new one
        // If outer transaction rolls back, this rolls back too
    }
    
    // REQUIRES_NEW
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void requiresNew() {
        // Always creates new transaction
        // Outer transaction is suspended
        // Can commit/rollback independently
    }
    
    // NESTED
    @Transactional(propagation = Propagation.NESTED)
    public void nested() {
        // Creates savepoint within existing transaction
        // Can rollback to savepoint without affecting outer
        // If outer rolls back, nested rolls back too
    }
}

// Real-world example
@Service
public class OrderService {
    
    @Autowired
    private AuditService auditService;
    
    @Transactional
    public void processOrder(Order order) {
        saveOrder(order);
        
        try {
            // Audit logging shouldn't fail the order
            auditService.logOrderCreation(order);
        } catch (Exception e) {
            // Log and continue
        }
    }
}

@Service
public class AuditService {
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOrderCreation(Order order) {
        // Runs in separate transaction
        // If this fails, order still processes
        // If order fails, this still commits
    }
}
```

**Isolation Levels:**

```java
public enum Isolation {
    DEFAULT,           // Use database default
    READ_UNCOMMITTED,  // Dirty reads possible
    READ_COMMITTED,    // Prevents dirty reads
    REPEATABLE_READ,   // Prevents non-repeatable reads
    SERIALIZABLE       // Full isolation, lowest concurrency
}
```

**Isolation Problems:**

| Problem | Description | Prevented By |
|---------|-------------|--------------|
| **Dirty Read** | Read uncommitted data from another transaction | READ_COMMITTED |
| **Non-Repeatable Read** | Same query returns different results | REPEATABLE_READ |
| **Phantom Read** | New rows appear in repeated query | SERIALIZABLE |

```java
@Service
public class BankService {
    
    // Prevent dirty reads for financial data
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public BigDecimal getBalance(Long accountId) {
        return accountRepository.findById(accountId)
            .map(Account::getBalance)
            .orElse(BigDecimal.ZERO);
    }
    
    // Prevent non-repeatable reads for transfers
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = accountRepository.findById(fromId).orElseThrow();
        Account to = accountRepository.findById(toId).orElseThrow();
        
        // Balance won't change during this transaction
        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));
        
        accountRepository.save(from);
        accountRepository.save(to);
    }
    
    // Full isolation for reports
    @Transactional(isolation = Isolation.SERIALIZABLE, readOnly = true)
    public Report generateMonthlyReport() {
        // No phantom reads - consistent snapshot
        return reportGenerator.generate();
    }
}
```

**Rollback Configuration:**

```java
@Transactional(
    rollbackFor = {CustomException.class, IOException.class},
    noRollbackFor = {EntityNotFoundException.class}
)
public void processWithCustomRollback() {
    // Rolls back for CustomException and IOException
    // Does NOT rollback for EntityNotFoundException
}

// Default behavior:
// - RuntimeException and Error: Rollback
// - Checked Exception: No rollback (commit)
```

**Read-Only Transactions:**

```java
@Transactional(readOnly = true)
public List<Order> getOrders() {
    // Optimization hints for:
    // - JPA/Hibernate: No dirty checking
    // - JDBC: Connection set to read-only mode
    // - Some databases: Route to read replicas
    return orderRepository.findAll();
}
```

**Transaction Timeout:**

```java
@Transactional(timeout = 30)  // 30 seconds
public void longRunningProcess() {
    // TransactionTimedOutException if exceeds timeout
}
```

---

## 8. Explain Spring Security architecture. How does the filter chain work?

**Answer:**

**Security Filter Chain Architecture:**

```
HTTP Request
     ↓
┌─────────────────────────────────────────────────────────┐
│              DelegatingFilterProxy                       │
│         (Bridges Servlet Filter → Spring Bean)          │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│              FilterChainProxy                            │
│  (Spring Security's entry point)                        │
└─────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────┐
│           SecurityFilterChain                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │ SecurityContextPersistenceFilter                │    │
│  │ CorsFilter                                      │    │
│  │ CsrfFilter                                      │    │
│  │ LogoutFilter                                    │    │
│  │ UsernamePasswordAuthenticationFilter           │    │
│  │ BasicAuthenticationFilter                      │    │
│  │ BearerTokenAuthenticationFilter (OAuth2)       │    │
│  │ RequestCacheAwareFilter                        │    │
│  │ SecurityContextHolderAwareRequestFilter       │    │
│  │ AnonymousAuthenticationFilter                  │    │
│  │ SessionManagementFilter                        │    │
│  │ ExceptionTranslationFilter                     │    │
│  │ FilterSecurityInterceptor / AuthorizationFilter│    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
     ↓
Controller / Resource
```

**Modern Spring Security 6.x Configuration:**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)
public class SecurityConfig {
    
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
                .ignoringRequestMatchers("/api/webhook/**")
            )
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**", "/actuator/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/**").authenticated()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter()))
            )
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint(customAuthEntryPoint())
                .accessDeniedHandler(customAccessDeniedHandler())
            )
            .addFilterBefore(customFilter(), UsernamePasswordAuthenticationFilter.class)
            .build();
    }
    
    @Bean
    public JwtAuthenticationConverter jwtAuthConverter() {
        JwtGrantedAuthoritiesConverter grantedAuthoritiesConverter = 
            new JwtGrantedAuthoritiesConverter();
        grantedAuthoritiesConverter.setAuthoritiesClaimName("roles");
        grantedAuthoritiesConverter.setAuthorityPrefix("ROLE_");
        
        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(grantedAuthoritiesConverter);
        return converter;
    }
    
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
    
    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }
}
```

**Custom Authentication Filter:**

```java
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;
    
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {
        
        String authHeader = request.getHeader("Authorization");
        
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }
        
        String token = authHeader.substring(7);
        String username = jwtService.extractUsername(token);
        
        if (username != null && 
            SecurityContextHolder.getContext().getAuthentication() == null) {
            
            UserDetails userDetails = userDetailsService.loadUserByUsername(username);
            
            if (jwtService.isTokenValid(token, userDetails)) {
                UsernamePasswordAuthenticationToken authToken = 
                    new UsernamePasswordAuthenticationToken(
                        userDetails,
                        null,
                        userDetails.getAuthorities()
                    );
                authToken.setDetails(
                    new WebAuthenticationDetailsSource().buildDetails(request)
                );
                
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }
        
        filterChain.doFilter(request, response);
    }
}
```

**Method Security:**

```java
@Service
public class OrderService {
    
    @PreAuthorize("hasRole('ADMIN') or #order.userId == authentication.principal.id")
    public void updateOrder(Order order) {
        // Only ADMIN or owner can update
    }
    
    @PostAuthorize("returnObject.userId == authentication.principal.id")
    public Order getOrder(Long id) {
        // Check after method execution
        return orderRepository.findById(id).orElseThrow();
    }
    
    @PreFilter("filterObject.status == 'PENDING'")
    public void processOrders(List<Order> orders) {
        // Only process PENDING orders
    }
    
    @PostFilter("filterObject.visibility == 'PUBLIC' or " +
                "filterObject.userId == authentication.principal.id")
    public List<Order> getUserOrders() {
        // Filter results after retrieval
        return orderRepository.findAll();
    }
}
```

**Custom UserDetailsService:**

```java
@Service
public class CustomUserDetailsService implements UserDetailsService {
    
    private final UserRepository userRepository;
    
    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));
        
        return org.springframework.security.core.userdetails.User
            .withUsername(user.getUsername())
            .password(user.getPassword())
            .authorities(getAuthorities(user))
            .accountExpired(!user.isActive())
            .accountLocked(user.isLocked())
            .credentialsExpired(false)
            .disabled(!user.isEnabled())
            .build();
    }
    
    private Collection<? extends GrantedAuthority> getAuthorities(User user) {
        return user.getRoles().stream()
            .flatMap(role -> role.getPermissions().stream())
            .map(permission -> new SimpleGrantedAuthority(permission.getName()))
            .collect(Collectors.toSet());
    }
}
```

---

## 9. How do you handle distributed transactions in microservices? Explain SAGA pattern.

**Answer:**

**Distributed Transaction Challenges:**
- No single transaction manager
- Network partitions
- Service failures
- Eventual consistency

**SAGA Pattern:**

A saga is a sequence of local transactions where each transaction updates data within a single service.

**Two SAGA Coordination Approaches:**

**1. Choreography (Event-driven):**

```
┌─────────┐   OrderCreated    ┌─────────┐   PaymentCompleted   ┌─────────┐
│  Order  │ ───────────────→  │ Payment │ ────────────────────→ │  Stock  │
│ Service │                   │ Service │                       │ Service │
└─────────┘                   └─────────┘                       └─────────┘
     ↑                             ↑                                 │
     │        OrderFailed          │        PaymentFailed            │
     └─────────────────────────────┴─────────────────────────────────┘
                         Compensating Events
```

**2. Orchestration (Central coordinator):**

```
                    ┌──────────────────┐
                    │ SAGA Orchestrator │
                    │   (Order Saga)    │
                    └──────────────────┘
                     ↓       ↓       ↓
              ┌──────┴───┐ ┌─┴─────┐ ┌┴───────┐
              │  Order   │ │Payment│ │ Stock  │
              │ Service  │ │Service│ │Service │
              └──────────┘ └───────┘ └────────┘
```

**Choreography Implementation:**

```java
// Order Service
@Service
public class OrderService {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Transactional
    public Order createOrder(CreateOrderRequest request) {
        Order order = new Order();
        order.setStatus(OrderStatus.PENDING);
        order.setItems(request.getItems());
        order.setTotalAmount(calculateTotal(request.getItems()));
        
        order = orderRepository.save(order);
        
        // Publish event
        OrderCreatedEvent event = new OrderCreatedEvent(
            order.getId(),
            order.getCustomerId(),
            order.getTotalAmount()
        );
        kafkaTemplate.send("order-events", event);
        
        return order;
    }
    
    @KafkaListener(topics = "payment-events")
    public void handlePaymentEvent(PaymentEvent event) {
        if (event instanceof PaymentCompletedEvent) {
            updateOrderStatus(event.getOrderId(), OrderStatus.PAID);
        } else if (event instanceof PaymentFailedEvent) {
            // Compensating action
            cancelOrder(event.getOrderId());
        }
    }
    
    @KafkaListener(topics = "stock-events")
    public void handleStockEvent(StockEvent event) {
        if (event instanceof StockReservedEvent) {
            updateOrderStatus(event.getOrderId(), OrderStatus.CONFIRMED);
        } else if (event instanceof StockFailedEvent) {
            // Compensating action - refund payment
            kafkaTemplate.send("payment-commands", 
                new RefundCommand(event.getOrderId()));
            cancelOrder(event.getOrderId());
        }
    }
}

// Payment Service
@Service
public class PaymentService {
    
    @KafkaListener(topics = "order-events")
    public void handleOrderCreated(OrderCreatedEvent event) {
        try {
            processPayment(event);
            kafkaTemplate.send("payment-events", 
                new PaymentCompletedEvent(event.getOrderId()));
        } catch (PaymentException e) {
            kafkaTemplate.send("payment-events", 
                new PaymentFailedEvent(event.getOrderId(), e.getMessage()));
        }
    }
    
    @KafkaListener(topics = "payment-commands")
    public void handleRefundCommand(RefundCommand command) {
        refundPayment(command.getOrderId());
    }
}
```

**Orchestration Implementation:**

```java
// SAGA Orchestrator
@Service
public class OrderSagaOrchestrator {
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private PaymentServiceClient paymentClient;
    
    @Autowired
    private StockServiceClient stockClient;
    
    @Autowired
    private SagaStateRepository sagaRepository;
    
    @Transactional
    public Order executeOrderSaga(CreateOrderRequest request) {
        SagaState saga = new SagaState();
        saga.setStatus(SagaStatus.STARTED);
        sagaRepository.save(saga);
        
        try {
            // Step 1: Create Order
            Order order = orderService.createOrder(request);
            saga.setOrderId(order.getId());
            saga.setCurrentStep(SagaStep.ORDER_CREATED);
            sagaRepository.save(saga);
            
            // Step 2: Process Payment
            PaymentResult payment = paymentClient.processPayment(
                new PaymentRequest(order.getId(), order.getTotalAmount())
            );
            saga.setPaymentId(payment.getId());
            saga.setCurrentStep(SagaStep.PAYMENT_COMPLETED);
            sagaRepository.save(saga);
            
            // Step 3: Reserve Stock
            StockResult stock = stockClient.reserveStock(
                new StockRequest(order.getId(), order.getItems())
            );
            saga.setCurrentStep(SagaStep.STOCK_RESERVED);
            saga.setStatus(SagaStatus.COMPLETED);
            sagaRepository.save(saga);
            
            orderService.updateStatus(order.getId(), OrderStatus.CONFIRMED);
            return order;
            
        } catch (PaymentException e) {
            compensate(saga, SagaStep.PAYMENT_FAILED);
            throw new SagaFailedException("Payment failed", e);
            
        } catch (StockException e) {
            compensate(saga, SagaStep.STOCK_FAILED);
            throw new SagaFailedException("Stock reservation failed", e);
        }
    }
    
    private void compensate(SagaState saga, SagaStep failedStep) {
        saga.setStatus(SagaStatus.COMPENSATING);
        sagaRepository.save(saga);
        
        List<SagaStep> stepsToCompensate = getCompletedSteps(saga, failedStep);
        
        for (SagaStep step : stepsToCompensate) {
            try {
                executeCompensation(saga, step);
            } catch (Exception e) {
                // Log and continue with other compensations
                log.error("Compensation failed for step: {}", step, e);
            }
        }
        
        saga.setStatus(SagaStatus.COMPENSATED);
        sagaRepository.save(saga);
    }
    
    private void executeCompensation(SagaState saga, SagaStep step) {
        switch (step) {
            case ORDER_CREATED:
                orderService.cancelOrder(saga.getOrderId());
                break;
            case PAYMENT_COMPLETED:
                paymentClient.refundPayment(saga.getPaymentId());
                break;
            case STOCK_RESERVED:
                stockClient.releaseStock(saga.getOrderId());
                break;
        }
    }
}
```

**State Machine Based SAGA (Spring State Machine):**

```java
@Configuration
@EnableStateMachineFactory
public class OrderSagaStateMachineConfig 
        extends StateMachineConfigurerAdapter<SagaState, SagaEvent> {
    
    @Override
    public void configure(StateMachineStateConfigurer<SagaState, SagaEvent> states) 
            throws Exception {
        states
            .withStates()
            .initial(SagaState.STARTED)
            .state(SagaState.ORDER_CREATED)
            .state(SagaState.PAYMENT_PENDING)
            .state(SagaState.PAYMENT_COMPLETED)
            .state(SagaState.STOCK_PENDING)
            .state(SagaState.COMPLETED)
            .state(SagaState.COMPENSATING)
            .end(SagaState.FAILED)
            .end(SagaState.COMPENSATED);
    }
    
    @Override
    public void configure(StateMachineTransitionConfigurer<SagaState, SagaEvent> transitions) 
            throws Exception {
        transitions
            .withExternal()
                .source(SagaState.STARTED).target(SagaState.ORDER_CREATED)
                .event(SagaEvent.ORDER_CREATE_SUCCESS)
                .action(orderCreatedAction())
            .and()
            .withExternal()
                .source(SagaState.ORDER_CREATED).target(SagaState.PAYMENT_PENDING)
                .event(SagaEvent.INITIATE_PAYMENT)
                .action(initiatePaymentAction())
            .and()
            .withExternal()
                .source(SagaState.PAYMENT_PENDING).target(SagaState.PAYMENT_COMPLETED)
                .event(SagaEvent.PAYMENT_SUCCESS)
            .and()
            .withExternal()
                .source(SagaState.PAYMENT_PENDING).target(SagaState.COMPENSATING)
                .event(SagaEvent.PAYMENT_FAILED)
                .action(compensateAction());
    }
}
```

**Comparison:**

| Aspect | Choreography | Orchestration |
|--------|--------------|---------------|
| **Coupling** | Loosely coupled | More coupled to orchestrator |
| **Complexity** | Harder to understand flow | Clear, centralized flow |
| **Single Point of Failure** | No | Orchestrator can be SPOF |
| **Debugging** | Harder | Easier |
| **Adding Steps** | Complex (update multiple services) | Simple (update orchestrator) |

---

## 10. How do you implement resilience patterns in microservices? Explain Circuit Breaker, Retry, and Bulkhead.

**Answer:**

**Resilience4j Implementation (Recommended for Spring Boot 3.x):**

**1. Circuit Breaker Pattern:**

```java
// Configuration
@Configuration
public class CircuitBreakerConfig {
    
    @Bean
    public CircuitBreakerRegistry circuitBreakerRegistry() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)                    // 50% failure rate
            .slowCallRateThreshold(50)                   // 50% slow calls
            .slowCallDurationThreshold(Duration.ofSeconds(2))
            .waitDurationInOpenState(Duration.ofSeconds(30))  // Time before half-open
            .permittedNumberOfCallsInHalfOpenState(3)   // Test calls in half-open
            .slidingWindowType(SlidingWindowType.COUNT_BASED)
            .slidingWindowSize(10)                       // Last 10 calls
            .minimumNumberOfCalls(5)                     // Min calls before evaluating
            .recordExceptions(IOException.class, TimeoutException.class)
            .ignoreExceptions(BusinessException.class)
            .build();
        
        return CircuitBreakerRegistry.of(config);
    }
}

// Service Implementation
@Service
public class PaymentService {
    
    private final CircuitBreaker circuitBreaker;
    private final PaymentGatewayClient paymentClient;
    
    public PaymentService(CircuitBreakerRegistry registry, 
                          PaymentGatewayClient paymentClient) {
        this.circuitBreaker = registry.circuitBreaker("paymentService");
        this.paymentClient = paymentClient;
        
        // Register event listeners
        circuitBreaker.getEventPublisher()
            .onStateTransition(event -> 
                log.info("Circuit breaker state: {} -> {}", 
                    event.getStateTransition().getFromState(),
                    event.getStateTransition().getToState()))
            .onFailureRateExceeded(event -> 
                log.warn("Failure rate exceeded: {}", event.getFailureRate()));
    }
    
    public PaymentResult processPayment(PaymentRequest request) {
        return circuitBreaker.executeSupplier(() -> 
            paymentClient.process(request)
        );
    }
    
    // With fallback
    public PaymentResult processPaymentWithFallback(PaymentRequest request) {
        return Try.ofSupplier(
            CircuitBreaker.decorateSupplier(circuitBreaker, 
                () -> paymentClient.process(request)))
            .recover(throwable -> handleFallback(request, throwable))
            .get();
    }
    
    private PaymentResult handleFallback(PaymentRequest request, Throwable t) {
        if (t instanceof CallNotPermittedException) {
            log.warn("Circuit breaker is open, using fallback");
            return PaymentResult.pending(request.getId(), "Service temporarily unavailable");
        }
        throw new PaymentException("Payment failed", t);
    }
}
```

**2. Retry Pattern:**

```java
@Configuration
public class RetryConfig {
    
    @Bean
    public RetryRegistry retryRegistry() {
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(3)
            .waitDuration(Duration.ofMillis(500))
            .exponentialBackoffMultiplier(2)           // 500ms, 1000ms, 2000ms
            .retryOnResult(response -> response == null)
            .retryExceptions(IOException.class, TimeoutException.class)
            .ignoreExceptions(BusinessException.class)
            .failAfterMaxAttempts(true)
            .build();
        
        return RetryRegistry.of(config);
    }
}

@Service
public class ExternalApiService {
    
    private final Retry retry;
    private final ExternalApiClient apiClient;
    
    public ExternalApiService(RetryRegistry registry, ExternalApiClient apiClient) {
        this.retry = registry.retry("externalApi");
        this.apiClient = apiClient;
        
        retry.getEventPublisher()
            .onRetry(event -> log.info("Retry attempt #{} for {}", 
                event.getNumberOfRetryAttempts(), event.getName()))
            .onSuccess(event -> log.info("Call succeeded after {} attempts", 
                event.getNumberOfRetryAttempts()));
    }
    
    public ApiResponse callExternalApi(ApiRequest request) {
        return retry.executeSupplier(() -> apiClient.call(request));
    }
    
    // Combine with Circuit Breaker
    public ApiResponse callWithResilience(ApiRequest request) {
        Supplier<ApiResponse> supplier = () -> apiClient.call(request);
        
        // Retry wraps Circuit Breaker
        // Retry → Circuit Breaker → Actual Call
        Supplier<ApiResponse> decoratedSupplier = 
            Decorators.ofSupplier(supplier)
                .withCircuitBreaker(circuitBreaker)
                .withRetry(retry)
                .decorate();
        
        return Try.ofSupplier(decoratedSupplier)
            .recover(this::fallback)
            .get();
    }
}
```

**3. Bulkhead Pattern (Isolation):**

```java
@Configuration
public class BulkheadConfig {
    
    // Semaphore Bulkhead (limits concurrent calls)
    @Bean
    public BulkheadRegistry bulkheadRegistry() {
        BulkheadConfig config = BulkheadConfig.custom()
            .maxConcurrentCalls(10)          // Max 10 concurrent calls
            .maxWaitDuration(Duration.ofMillis(500))  // Wait time for slot
            .build();
        
        return BulkheadRegistry.of(config);
    }
    
    // Thread Pool Bulkhead (dedicated thread pool)
    @Bean
    public ThreadPoolBulkheadRegistry threadPoolBulkheadRegistry() {
        ThreadPoolBulkheadConfig config = ThreadPoolBulkheadConfig.custom()
            .maxThreadPoolSize(10)
            .coreThreadPoolSize(5)
            .queueCapacity(20)
            .keepAliveDuration(Duration.ofSeconds(20))
            .build();
        
        return ThreadPoolBulkheadRegistry.of(config);
    }
}

@Service
public class OrderProcessingService {
    
    private final Bulkhead bulkhead;
    private final ThreadPoolBulkhead threadPoolBulkhead;
    
    public OrderProcessingService(BulkheadRegistry registry,
                                   ThreadPoolBulkheadRegistry tpRegistry) {
        this.bulkhead = registry.bulkhead("orderProcessing");
        this.threadPoolBulkhead = tpRegistry.bulkhead("orderProcessingAsync");
    }
    
    // Semaphore bulkhead - same thread
    public Order processOrder(OrderRequest request) {
        return bulkhead.executeSupplier(() -> doProcessOrder(request));
    }
    
    // Thread pool bulkhead - separate thread pool
    public CompletableFuture<Order> processOrderAsync(OrderRequest request) {
        return threadPoolBulkhead.executeSupplier(() -> doProcessOrder(request));
    }
}
```

**4. Rate Limiter:**

```java
@Configuration
public class RateLimiterConfig {
    
    @Bean
    public RateLimiterRegistry rateLimiterRegistry() {
        RateLimiterConfig config = RateLimiterConfig.custom()
            .limitForPeriod(100)                    // 100 requests
            .limitRefreshPeriod(Duration.ofSeconds(1))  // per second
            .timeoutDuration(Duration.ofMillis(500))    // Wait time for permit
            .build();
        
        return RateLimiterRegistry.of(config);
    }
}

@Service
public class ApiService {
    
    private final RateLimiter rateLimiter;
    
    public ApiResponse callApi(ApiRequest request) {
        return rateLimiter.executeSupplier(() -> externalApi.call(request));
    }
}
```

**5. Time Limiter:**

```java
@Configuration
public class TimeLimiterConfig {
    
    @Bean
    public TimeLimiterRegistry timeLimiterRegistry() {
        TimeLimiterConfig config = TimeLimiterConfig.custom()
            .timeoutDuration(Duration.ofSeconds(5))
            .cancelRunningFuture(true)
            .build();
        
        return TimeLimiterRegistry.of(config);
    }
}

@Service
public class SlowService {
    
    private final TimeLimiter timeLimiter;
    
    public CompletableFuture<Result> callSlowService() {
        Supplier<CompletableFuture<Result>> supplier = 
            () -> CompletableFuture.supplyAsync(this::slowOperation);
        
        return timeLimiter.executeFutureSupplier(supplier);
    }
}
```

**Spring Boot Annotations (Simplified):**

```java
@Service
public class ResilientService {
    
    @CircuitBreaker(name = "backendA", fallbackMethod = "fallback")
    @Retry(name = "backendA")
    @Bulkhead(name = "backendA")
    @RateLimiter(name = "backendA")
    @TimeLimiter(name = "backendA")
    public CompletableFuture<String> doSomething() {
        return CompletableFuture.supplyAsync(() -> 
            backendService.doSomething());
    }
    
    public CompletableFuture<String> fallback(Throwable t) {
        return CompletableFuture.completedFuture("Fallback response");
    }
}
```

**application.yml Configuration:**

```yaml
resilience4j:
  circuitbreaker:
    instances:
      backendA:
        registerHealthIndicator: true
        slidingWindowSize: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 10000
        permittedNumberOfCallsInHalfOpenState: 3
        
  retry:
    instances:
      backendA:
        maxAttempts: 3
        waitDuration: 500ms
        exponentialBackoffMultiplier: 2
        
  bulkhead:
    instances:
      backendA:
        maxConcurrentCalls: 10
        maxWaitDuration: 500ms
        
  ratelimiter:
    instances:
      backendA:
        limitForPeriod: 100
        limitRefreshPeriod: 1s
        timeoutDuration: 500ms
        
  timelimiter:
    instances:
      backendA:
        timeoutDuration: 5s
        cancelRunningFuture: true
```

---

## 11. How do you implement API versioning and backward compatibility in microservices?

**Answer:**

**API Versioning Strategies:**

**1. URL Path Versioning:**

```java
@RestController
@RequestMapping("/api/v1/users")
public class UserControllerV1 {
    
    @GetMapping("/{id}")
    public UserDTOV1 getUser(@PathVariable Long id) {
        return userService.getUserV1(id);
    }
}

@RestController
@RequestMapping("/api/v2/users")
public class UserControllerV2 {
    
    @GetMapping("/{id}")
    public UserDTOV2 getUser(@PathVariable Long id) {
        return userService.getUserV2(id);
    }
}
```

**2. Header Versioning:**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping(value = "/{id}", headers = "X-API-Version=1")
    public UserDTOV1 getUserV1(@PathVariable Long id) {
        return userService.getUserV1(id);
    }
    
    @GetMapping(value = "/{id}", headers = "X-API-Version=2")
    public UserDTOV2 getUserV2(@PathVariable Long id) {
        return userService.getUserV2(id);
    }
}
```

**3. Content Negotiation (Accept Header):**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping(value = "/{id}", produces = "application/vnd.company.v1+json")
    public UserDTOV1 getUserV1(@PathVariable Long id) {
        return userService.getUserV1(id);
    }
    
    @GetMapping(value = "/{id}", produces = "application/vnd.company.v2+json")
    public UserDTOV2 getUserV2(@PathVariable Long id) {
        return userService.getUserV2(id);
    }
}
```

**4. Query Parameter Versioning:**

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping(value = "/{id}", params = "version=1")
    public UserDTOV1 getUserV1(@PathVariable Long id) {
        return userService.getUserV1(id);
    }
    
    @GetMapping(value = "/{id}", params = "version=2")
    public UserDTOV2 getUserV2(@PathVariable Long id) {
        return userService.getUserV2(id);
    }
}
```

**Custom Version Resolver:**

```java
@Configuration
public class WebMvcConfig implements WebMvcConfigurer {
    
    @Override
    public void addArgumentResolvers(List<HandlerMethodArgumentResolver> resolvers) {
        resolvers.add(new ApiVersionArgumentResolver());
    }
}

public class ApiVersionArgumentResolver implements HandlerMethodArgumentResolver {
    
    @Override
    public boolean supportsParameter(MethodParameter parameter) {
        return parameter.hasParameterAnnotation(ApiVersion.class);
    }
    
    @Override
    public Object resolveArgument(MethodParameter parameter,
                                  ModelAndViewContainer mavContainer,
                                  NativeWebRequest webRequest,
                                  WebDataBinderFactory binderFactory) {
        
        String versionHeader = webRequest.getHeader("X-API-Version");
        String versionParam = webRequest.getParameter("version");
        
        String version = versionHeader != null ? versionHeader : 
                        versionParam != null ? versionParam : "1";
        
        return Integer.parseInt(version);
    }
}

// Usage
@GetMapping("/{id}")
public UserDTO getUser(@PathVariable Long id, @ApiVersion int version) {
    return switch (version) {
        case 1 -> userService.getUserV1(id);
        case 2 -> userService.getUserV2(id);
        default -> throw new UnsupportedVersionException(version);
    };
}
```

**DTO Evolution for Backward Compatibility:**

```java
// V1 DTO
public class UserDTOV1 {
    private Long id;
    private String name;
    private String email;
}

// V2 DTO - Extended with new fields
public class UserDTOV2 {
    private Long id;
    private String firstName;    // Split from name
    private String lastName;     // Split from name
    private String email;
    private String phone;        // New field
    
    @JsonProperty("name")        // Backward compatible
    public String getFullName() {
        return firstName + " " + lastName;
    }
}

// Adapter/Mapper
@Component
public class UserDTOMapper {
    
    public UserDTOV1 toV1(User user) {
        return new UserDTOV1(
            user.getId(),
            user.getFirstName() + " " + user.getLastName(),
            user.getEmail()
        );
    }
    
    public UserDTOV2 toV2(User user) {
        return new UserDTOV2(
            user.getId(),
            user.getFirstName(),
            user.getLastName(),
            user.getEmail(),
            user.getPhone()
        );
    }
}
```

**API Gateway Versioning:**

```yaml
# Spring Cloud Gateway
spring:
  cloud:
    gateway:
      routes:
        - id: user-service-v1
          uri: lb://user-service-v1
          predicates:
            - Path=/api/v1/users/**
            - Header=X-API-Version, 1
          
        - id: user-service-v2
          uri: lb://user-service-v2
          predicates:
            - Path=/api/v2/users/**
            - Header=X-API-Version, 2
          
        - id: user-service-default
          uri: lb://user-service-v2
          predicates:
            - Path=/api/users/**
          filters:
            - AddRequestHeader=X-API-Version, 2
```

**Deprecation Strategy:**

```java
@RestController
@RequestMapping("/api/v1/users")
@Deprecated(since = "2.0", forRemoval = true)
public class UserControllerV1 {
    
    @GetMapping("/{id}")
    public ResponseEntity<UserDTOV1> getUser(@PathVariable Long id) {
        return ResponseEntity.ok()
            .header("X-API-Deprecated", "true")
            .header("X-API-Sunset", "2025-12-31")
            .header("X-API-Upgrade-To", "/api/v2/users")
            .body(userService.getUserV1(id));
    }
}
```

**OpenAPI Documentation:**

```java
@OpenAPIDefinition(
    info = @Info(
        title = "User Service API",
        version = "2.0.0",
        description = "User management API"
    ),
    servers = {
        @Server(url = "/api/v1", description = "Version 1 (Deprecated)"),
        @Server(url = "/api/v2", description = "Version 2 (Current)")
    }
)
@Configuration
public class OpenApiConfig {
    
    @Bean
    public GroupedOpenApi v1Api() {
        return GroupedOpenApi.builder()
            .group("v1")
            .pathsToMatch("/api/v1/**")
            .build();
    }
    
    @Bean
    public GroupedOpenApi v2Api() {
        return GroupedOpenApi.builder()
            .group("v2")
            .pathsToMatch("/api/v2/**")
            .build();
    }
}
```

---

## 12. How do you handle distributed caching in microservices? Explain cache invalidation strategies.

**Answer:**

**Distributed Caching Architecture:**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Service A  │     │  Service B  │     │  Service C  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────┴──────┐
                    │ Redis Cluster│
                    │ (Distributed │
                    │   Cache)     │
                    └─────────────┘
```

**Redis Cache Configuration:**

```java
@Configuration
@EnableCaching
public class RedisCacheConfig {
    
    @Bean
    public RedisConnectionFactory redisConnectionFactory() {
        RedisClusterConfiguration clusterConfig = new RedisClusterConfiguration(
            List.of("redis-node1:6379", "redis-node2:6379", "redis-node3:6379")
        );
        clusterConfig.setMaxRedirects(3);
        
        LettuceClientConfiguration clientConfig = LettuceClientConfiguration.builder()
            .commandTimeout(Duration.ofSeconds(2))
            .readFrom(ReadFrom.REPLICA_PREFERRED)
            .build();
        
        return new LettuceConnectionFactory(clusterConfig, clientConfig);
    }
    
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(30))
            .serializeKeysWith(SerializationPair.fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(SerializationPair.fromSerializer(new GenericJackson2JsonRedisSerializer()))
            .disableCachingNullValues();
        
        Map<String, RedisCacheConfiguration> cacheConfigs = Map.of(
            "users", defaultConfig.entryTtl(Duration.ofHours(1)),
            "products", defaultConfig.entryTtl(Duration.ofMinutes(15)),
            "sessions", defaultConfig.entryTtl(Duration.ofMinutes(30))
        );
        
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(cacheConfigs)
            .transactionAware()
            .build();
    }
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(new GenericJackson2JsonRedisSerializer());
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(new GenericJackson2JsonRedisSerializer());
        return template;
    }
}
```

**Service with Caching:**

```java
@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final CacheManager cacheManager;
    private final RedisTemplate<String, Object> redisTemplate;
    
    @Cacheable(value = "users", key = "#id", unless = "#result == null")
    public User getUser(Long id) {
        return userRepository.findById(id).orElse(null);
    }
    
    @CachePut(value = "users", key = "#user.id")
    public User updateUser(User user) {
        return userRepository.save(user);
    }
    
    @CacheEvict(value = "users", key = "#id")
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
    
    @CacheEvict(value = "users", allEntries = true)
    public void clearAllUsers() {
        // Clear entire cache
    }
    
    @Caching(evict = {
        @CacheEvict(value = "users", key = "#user.id"),
        @CacheEvict(value = "usersByEmail", key = "#user.email")
    })
    public void deleteUserCompletely(User user) {
        userRepository.delete(user);
    }
}
```

**Cache Invalidation Strategies:**

**1. Time-To-Live (TTL):**

```java
@Cacheable(value = "products", key = "#id")
public Product getProduct(Long id) {
    return productRepository.findById(id).orElse(null);
}

// TTL configured in cache manager
// Stale data possible within TTL window
```

**2. Event-Driven Invalidation:**

```java
@Service
public class ProductService {
    
    @Autowired
    private KafkaTemplate<String, CacheInvalidationEvent> kafkaTemplate;
    
    @CachePut(value = "products", key = "#product.id")
    @Transactional
    public Product updateProduct(Product product) {
        Product saved = productRepository.save(product);
        
        // Publish invalidation event for other services
        CacheInvalidationEvent event = new CacheInvalidationEvent(
            "products",
            product.getId().toString(),
            CacheOperation.UPDATE
        );
        kafkaTemplate.send("cache-invalidation", event);
        
        return saved;
    }
}

@Component
public class CacheInvalidationListener {
    
    @Autowired
    private CacheManager cacheManager;
    
    @KafkaListener(topics = "cache-invalidation")
    public void handleCacheInvalidation(CacheInvalidationEvent event) {
        Cache cache = cacheManager.getCache(event.getCacheName());
        if (cache != null) {
            switch (event.getOperation()) {
                case UPDATE:
                case DELETE:
                    cache.evict(event.getKey());
                    break;
                case CLEAR:
                    cache.clear();
                    break;
            }
        }
    }
}
```

**3. Write-Through Cache:**

```java
@Service
public class WriteThruCacheService {
    
    @Autowired
    private RedisTemplate<String, Product> redisTemplate;
    
    @Autowired
    private ProductRepository productRepository;
    
    public Product saveProduct(Product product) {
        // Write to database first
        Product saved = productRepository.save(product);
        
        // Then update cache
        String key = "product:" + saved.getId();
        redisTemplate.opsForValue().set(key, saved, Duration.ofHours(1));
        
        return saved;
    }
    
    public Product getProduct(Long id) {
        String key = "product:" + id;
        Product cached = redisTemplate.opsForValue().get(key);
        
        if (cached != null) {
            return cached;
        }
        
        Product product = productRepository.findById(id).orElse(null);
        if (product != null) {
            redisTemplate.opsForValue().set(key, product, Duration.ofHours(1));
        }
        
        return product;
    }
}
```

**4. Write-Behind (Write-Back) Cache:**

```java
@Service
public class WriteBehindCacheService {
    
    @Autowired
    private RedisTemplate<String, Product> redisTemplate;
    
    @Autowired
    private BlockingQueue<Product> writeQueue;
    
    // Async writer running in background
    @Scheduled(fixedDelay = 1000)
    public void flushToDatabase() {
        List<Product> batch = new ArrayList<>();
        writeQueue.drainTo(batch, 100);  // Batch up to 100 items
        
        if (!batch.isEmpty()) {
            productRepository.saveAll(batch);
        }
    }
    
    public void saveProduct(Product product) {
        // Write to cache immediately
        String key = "product:" + product.getId();
        redisTemplate.opsForValue().set(key, product);
        
        // Queue for async database write
        writeQueue.offer(product);
    }
}
```

**5. Cache Versioning:**

```java
@Service
public class VersionedCacheService {
    
    private static final String VERSION_KEY = "cache:version:products";
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    public Product getProduct(Long id) {
        Long version = (Long) redisTemplate.opsForValue().get(VERSION_KEY);
        if (version == null) version = 1L;
        
        String key = "product:" + version + ":" + id;
        return (Product) redisTemplate.opsForValue().get(key);
    }
    
    public void invalidateAll() {
        // Increment version - all old keys become invalid
        redisTemplate.opsForValue().increment(VERSION_KEY);
    }
}
```

**6. Two-Level Caching (Local + Distributed):**

```java
@Configuration
public class TwoLevelCacheConfig {
    
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory redisFactory) {
        // L1: Caffeine (Local, Fast)
        CaffeineCacheManager localCacheManager = new CaffeineCacheManager();
        localCacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(Duration.ofMinutes(5)));
        
        // L2: Redis (Distributed)
        RedisCacheManager redisCacheManager = RedisCacheManager.builder(redisFactory)
            .cacheDefaults(RedisCacheConfiguration.defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(30)))
            .build();
        
        return new TwoLevelCacheManager(localCacheManager, redisCacheManager);
    }
}

public class TwoLevelCacheManager implements CacheManager {
    
    private final CacheManager localCacheManager;
    private final CacheManager distributedCacheManager;
    
    @Override
    public Cache getCache(String name) {
        Cache localCache = localCacheManager.getCache(name);
        Cache distributedCache = distributedCacheManager.getCache(name);
        return new TwoLevelCache(localCache, distributedCache);
    }
}

public class TwoLevelCache implements Cache {
    
    private final Cache localCache;
    private final Cache distributedCache;
    
    @Override
    public ValueWrapper get(Object key) {
        // Check L1 first
        ValueWrapper local = localCache.get(key);
        if (local != null) {
            return local;
        }
        
        // Check L2
        ValueWrapper distributed = distributedCache.get(key);
        if (distributed != null) {
            // Populate L1
            localCache.put(key, distributed.get());
            return distributed;
        }
        
        return null;
    }
    
    @Override
    public void put(Object key, Object value) {
        localCache.put(key, value);
        distributedCache.put(key, value);
    }
    
    @Override
    public void evict(Object key) {
        localCache.evict(key);
        distributedCache.evict(key);
        // Also publish invalidation event for other instances
    }
}
```

---

## 13. How do you implement observability (logging, metrics, tracing) in microservices?

**Answer:**

**Three Pillars of Observability:**

```
┌─────────────────────────────────────────────────────────┐
│                    Observability                        │
├─────────────────┬─────────────────┬────────────────────┤
│     Logging     │     Metrics     │     Tracing        │
│   (What)        │   (How Much)    │   (Where)          │
├─────────────────┼─────────────────┼────────────────────┤
│ ELK/Loki        │ Prometheus      │ Jaeger/Zipkin      │
│ Application logs│ Counters/Gauges │ Distributed traces │
│ Error tracking  │ Histograms      │ Span correlation   │
└─────────────────┴─────────────────┴────────────────────┘
```

**1. Structured Logging:**

```java
// Dependencies: spring-boot-starter-logging, logstash-logback-encoder

// logback-spring.xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <include resource="org/springframework/boot/logging/logback/defaults.xml"/>
    
    <springProfile name="!local">
        <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
            <encoder class="net.logstash.logback.encoder.LogstashEncoder">
                <includeMdcKeyName>traceId</includeMdcKeyName>
                <includeMdcKeyName>spanId</includeMdcKeyName>
                <includeMdcKeyName>userId</includeMdcKeyName>
                <customFields>{"service":"order-service","version":"1.0.0"}</customFields>
            </encoder>
        </appender>
        
        <root level="INFO">
            <appender-ref ref="JSON"/>
        </root>
    </springProfile>
</configuration>
```

```java
@Slf4j
@Service
public class OrderService {
    
    public Order createOrder(OrderRequest request) {
        // Add context to MDC
        MDC.put("userId", request.getUserId().toString());
        MDC.put("orderId", UUID.randomUUID().toString());
        
        try {
            log.info("Creating order", 
                StructuredArguments.kv("items", request.getItems().size()),
                StructuredArguments.kv("total", request.getTotal()));
            
            Order order = processOrder(request);
            
            log.info("Order created successfully",
                StructuredArguments.kv("orderId", order.getId()),
                StructuredArguments.kv("status", order.getStatus()));
            
            return order;
            
        } catch (Exception e) {
            log.error("Failed to create order",
                StructuredArguments.kv("error", e.getMessage()),
                e);
            throw e;
            
        } finally {
            MDC.clear();
        }
    }
}
```

**2. Metrics with Micrometer:**

```java
@Configuration
public class MetricsConfig {
    
    @Bean
    public MeterRegistryCustomizer<MeterRegistry> metricsCommonTags() {
        return registry -> registry.config()
            .commonTags("application", "order-service")
            .commonTags("environment", System.getenv("ENV"));
    }
}

@Service
public class OrderService {
    
    private final Counter orderCounter;
    private final Timer orderTimer;
    private final DistributionSummary orderValue;
    private final AtomicInteger activeOrders;
    
    public OrderService(MeterRegistry registry) {
        this.orderCounter = Counter.builder("orders.created")
            .description("Number of orders created")
            .tags("type", "online")
            .register(registry);
        
        this.orderTimer = Timer.builder("orders.processing.time")
            .description("Time to process orders")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);
        
        this.orderValue = DistributionSummary.builder("orders.value")
            .description("Order values")
            .baseUnit("dollars")
            .publishPercentileHistogram()
            .register(registry);
        
        this.activeOrders = registry.gauge("orders.active", new AtomicInteger(0));
    }
    
    public Order createOrder(OrderRequest request) {
        activeOrders.incrementAndGet();
        
        try {
            return orderTimer.record(() -> {
                Order order = processOrder(request);
                
                orderCounter.increment();
                orderValue.record(order.getTotal().doubleValue());
                
                return order;
            });
        } finally {
            activeOrders.decrementAndGet();
        }
    }
}
```

**Custom Business Metrics:**

```java
@Component
public class BusinessMetrics {
    
    private final MeterRegistry registry;
    
    @EventListener
    public void onOrderCompleted(OrderCompletedEvent event) {
        registry.counter("business.orders.completed",
            "paymentMethod", event.getPaymentMethod(),
            "region", event.getRegion()
        ).increment();
        
        registry.summary("business.orders.items",
            "category", event.getCategory()
        ).record(event.getItemCount());
    }
    
    @EventListener
    public void onPaymentFailed(PaymentFailedEvent event) {
        registry.counter("business.payments.failed",
            "reason", event.getFailureReason(),
            "gateway", event.getGateway()
        ).increment();
    }
}
```

**3. Distributed Tracing with Micrometer Tracing:**

```yaml
# application.yml
management:
  tracing:
    sampling:
      probability: 1.0  # 100% in dev, reduce in prod
  zipkin:
    tracing:
      endpoint: http://zipkin:9411/api/v2/spans
```

```java
@Configuration
public class TracingConfig {
    
    @Bean
    public ObservationHandler<Observation.Context> observationTextPublisher() {
        return new ObservationTextPublisher();
    }
}

@Service
public class OrderService {
    
    private final ObservationRegistry observationRegistry;
    private final PaymentClient paymentClient;
    private final InventoryClient inventoryClient;
    
    public Order createOrder(OrderRequest request) {
        // Create observation (span)
        return Observation.createNotStarted("order.create", observationRegistry)
            .lowCardinalityKeyValue("order.type", request.getType())
            .observe(() -> {
                // Child observations automatically linked
                Payment payment = paymentClient.processPayment(request);
                Inventory inventory = inventoryClient.reserve(request);
                
                return buildOrder(request, payment, inventory);
            });
    }
}

// RestClient propagates trace context automatically
@Configuration
public class RestClientConfig {
    
    @Bean
    public RestClient restClient(RestClient.Builder builder, ObservationRegistry registry) {
        return builder
            .baseUrl("http://payment-service")
            .observationRegistry(registry)
            .build();
    }
}

// WebClient for reactive
@Bean
public WebClient webClient(WebClient.Builder builder, ObservationRegistry registry) {
    return builder
        .baseUrl("http://inventory-service")
        .observationRegistry(registry)
        .build();
}
```

**4. Custom Spans:**

```java
@Service
public class ComplexService {
    
    @Autowired
    private Tracer tracer;
    
    public void complexOperation() {
        Span parentSpan = tracer.currentSpan();
        
        // Create child span for database operation
        Span dbSpan = tracer.nextSpan(parentSpan)
            .name("database-query")
            .tag("db.type", "postgresql")
            .tag("db.operation", "select")
            .start();
        
        try (Tracer.SpanInScope ws = tracer.withSpan(dbSpan)) {
            // Database operation
            executeQuery();
        } catch (Exception e) {
            dbSpan.error(e);
            throw e;
        } finally {
            dbSpan.end();
        }
        
        // Create child span for external API call
        Span apiSpan = tracer.nextSpan(parentSpan)
            .name("external-api-call")
            .tag("http.method", "POST")
            .tag("http.url", "https://api.external.com")
            .start();
        
        try (Tracer.SpanInScope ws = tracer.withSpan(apiSpan)) {
            callExternalApi();
        } finally {
            apiSpan.end();
        }
    }
}
```

**5. Health Checks and Readiness:**

```java
@Component
public class DatabaseHealthIndicator implements HealthIndicator {
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(1)) {
                return Health.up()
                    .withDetail("database", "PostgreSQL")
                    .withDetail("connection", "valid")
                    .build();
            }
        } catch (SQLException e) {
            return Health.down()
                .withException(e)
                .build();
        }
        return Health.down().build();
    }
}

@Component
public class ExternalServiceHealthIndicator implements HealthIndicator {
    
    @Autowired
    private RestClient restClient;
    
    @Override
    public Health health() {
        try {
            ResponseEntity<Void> response = restClient.get()
                .uri("/health")
                .retrieve()
                .toBodilessEntity();
            
            if (response.getStatusCode().is2xxSuccessful()) {
                return Health.up().build();
            }
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
        return Health.down().build();
    }
}
```

**Prometheus Endpoints:**

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, prometheus, metrics
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true
  metrics:
    export:
      prometheus:
        enabled: true
    distribution:
      percentiles-histogram:
        http.server.requests: true
```

---

## 14. How do you design for high availability and disaster recovery in microservices?

**Answer:**

**High Availability Architecture:**

```
                        ┌─────────────────┐
                        │   Global Load   │
                        │    Balancer     │
                        └────────┬────────┘
               ┌─────────────────┼─────────────────┐
               ↓                 ↓                 ↓
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │ Region 1 │      │ Region 2 │      │ Region 3 │
        │ (Active) │      │ (Active) │      │(Standby) │
        └────┬─────┘      └────┬─────┘      └────┬─────┘
             │                 │                 │
    ┌────────┴────────┐       ...               ...
    │                 │
┌───┴───┐         ┌───┴───┐
│  AZ-1 │         │  AZ-2 │
├───────┤         ├───────┤
│ K8s   │         │ K8s   │
│Cluster│←───────→│Cluster│
└───┬───┘         └───┬───┘
    │                 │
    └────────┬────────┘
             │
      ┌──────┴──────┐
      │   Database  │
      │   Cluster   │
      │  (Primary + │
      │  Replicas)  │
      └─────────────┘
```

**Kubernetes Deployment for HA:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      # Anti-affinity - spread across nodes/zones
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: order-service
                topologyKey: topology.kubernetes.io/zone
      
      # Topology spread constraints
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: order-service
      
      containers:
        - name: order-service
          image: order-service:1.0.0
          ports:
            - containerPort: 8080
          
          # Resource limits
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          
          # Health probes
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
          
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
          
          # Graceful shutdown
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
          
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "kubernetes,prod"
            
      # Graceful termination period
      terminationGracePeriodSeconds: 60
---
# Pod Disruption Budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: order-service
---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**Database High Availability:**

```java
// Multi-datasource configuration for read replicas
@Configuration
public class DataSourceConfig {
    
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @ConfigurationProperties("spring.datasource.replica")
    public DataSource replicaDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    public DataSource routingDataSource(
            @Qualifier("primaryDataSource") DataSource primary,
            @Qualifier("replicaDataSource") DataSource replica) {
        
        Map<Object, Object> dataSources = Map.of(
            DataSourceType.PRIMARY, primary,
            DataSourceType.REPLICA, replica
        );
        
        RoutingDataSource routing = new RoutingDataSource();
        routing.setTargetDataSources(dataSources);
        routing.setDefaultTargetDataSource(primary);
        return routing;
    }
}

public class RoutingDataSource extends AbstractRoutingDataSource {
    
    @Override
    protected Object determineCurrentLookupKey() {
        return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
            ? DataSourceType.REPLICA
            : DataSourceType.PRIMARY;
    }
}

@Service
public class OrderService {
    
    @Transactional(readOnly = true)  // Routes to replica
    public List<Order> getOrders() {
        return orderRepository.findAll();
    }
    
    @Transactional  // Routes to primary
    public Order createOrder(Order order) {
        return orderRepository.save(order);
    }
}
```

**Graceful Shutdown:**

```java
@Component
public class GracefulShutdown implements TomcatConnectorCustomizer, ApplicationListener<ContextClosedEvent> {
    
    private static final Logger log = LoggerFactory.getLogger(GracefulShutdown.class);
    private volatile Connector connector;
    
    @Override
    public void customize(Connector connector) {
        this.connector = connector;
    }
    
    @Override
    public void onApplicationEvent(ContextClosedEvent event) {
        log.info("Initiating graceful shutdown...");
        
        // Stop accepting new requests
        this.connector.pause();
        
        // Get thread pool
        Executor executor = this.connector.getProtocolHandler().getExecutor();
        
        if (executor instanceof ThreadPoolExecutor) {
            ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) executor;
            threadPoolExecutor.shutdown();
            
            try {
                // Wait for existing requests to complete
                if (!threadPoolExecutor.awaitTermination(30, TimeUnit.SECONDS)) {
                    log.warn("Forcing shutdown after timeout");
                    threadPoolExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        log.info("Graceful shutdown complete");
    }
}
```

**Disaster Recovery - Data Backup:**

```java
@Service
public class BackupService {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Autowired
    private S3Client s3Client;
    
    @Scheduled(cron = "0 0 2 * * *")  // Daily at 2 AM
    public void performDailyBackup() {
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME);
        String backupFile = "backup-" + timestamp + ".sql";
        
        try {
            // Create backup
            ProcessBuilder pb = new ProcessBuilder(
                "pg_dump",
                "-h", "primary-db.example.com",
                "-U", "backup_user",
                "-d", "orders",
                "-f", "/tmp/" + backupFile
            );
            pb.environment().put("PGPASSWORD", getDbPassword());
            Process process = pb.start();
            process.waitFor();
            
            // Upload to S3
            s3Client.putObject(
                PutObjectRequest.builder()
                    .bucket("dr-backups")
                    .key("databases/orders/" + backupFile)
                    .storageClass(StorageClass.STANDARD_IA)
                    .build(),
                RequestBody.fromFile(Paths.get("/tmp/" + backupFile))
            );
            
            // Enable cross-region replication in S3 for DR
            log.info("Backup completed: {}", backupFile);
            
        } catch (Exception e) {
            log.error("Backup failed", e);
            alertService.sendAlert("Database backup failed: " + e.getMessage());
        }
    }
}
```

**Multi-Region Failover:**

```java
@Configuration
public class MultiRegionConfig {
    
    @Bean
    public Route53Client route53Client() {
        return Route53Client.builder()
            .region(Region.AWS_GLOBAL)
            .build();
    }
    
    @Service
    public class FailoverService {
        
        @Autowired
        private Route53Client route53;
        
        public void failoverToRegion(String targetRegion) {
            // Update DNS to point to DR region
            ChangeBatch changeBatch = ChangeBatch.builder()
                .changes(Change.builder()
                    .action(ChangeAction.UPSERT)
                    .resourceRecordSet(ResourceRecordSet.builder()
                        .name("api.example.com")
                        .type(RRType.A)
                        .setIdentifier(targetRegion)
                        .region(ResourceRecordSetRegion.fromValue(targetRegion))
                        .aliasTarget(AliasTarget.builder()
                            .dnsName(getDRLoadBalancer(targetRegion))
                            .hostedZoneId(getHostedZoneId(targetRegion))
                            .build())
                        .build())
                    .build())
                .build();
            
            route53.changeResourceRecordSets(ChangeResourceRecordSetsRequest.builder()
                .hostedZoneId("ZONE_ID")
                .changeBatch(changeBatch)
                .build());
            
            log.info("Failover to {} complete", targetRegion);
        }
    }
}
```

---

## 15. What are your strategies for performance optimization in Spring Boot applications?

**Answer:**

**1. JVM Tuning:**

```bash
# G1GC for balanced performance (default in Java 11+)
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     -XX:G1HeapRegionSize=16m \
     -Xms2g -Xmx2g \
     -XX:+UseStringDeduplication \
     -XX:+ParallelRefProcEnabled \
     -jar app.jar

# ZGC for ultra-low latency (Java 15+)
java -XX:+UseZGC \
     -XX:+ZGenerational \
     -Xms4g -Xmx4g \
     -jar app.jar

# Virtual Threads (Java 21+)
java --enable-preview \
     -Djdk.virtualThreadScheduler.parallelism=256 \
     -jar app.jar
```

**2. Connection Pool Optimization:**

```yaml
# HikariCP configuration
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 300000
      connection-timeout: 20000
      max-lifetime: 1200000
      leak-detection-threshold: 60000
      
      # Performance tuning
      pool-name: OrderServicePool
      auto-commit: true
      connection-test-query: SELECT 1
      
      # Advanced settings
      data-source-properties:
        cachePrepStmts: true
        prepStmtCacheSize: 250
        prepStmtCacheSqlLimit: 2048
        useServerPrepStmts: true
        rewriteBatchedStatements: true
```

**3. JPA/Hibernate Optimization:**

```java
// Batch processing
@Configuration
public class JpaConfig {
    
    @Bean
    public HibernatePropertiesCustomizer hibernateCustomizer() {
        return properties -> {
            properties.put("hibernate.jdbc.batch_size", 50);
            properties.put("hibernate.order_inserts", true);
            properties.put("hibernate.order_updates", true);
            properties.put("hibernate.batch_versioned_data", true);
            properties.put("hibernate.jdbc.fetch_size", 100);
            
            // Second-level cache
            properties.put("hibernate.cache.use_second_level_cache", true);
            properties.put("hibernate.cache.region.factory_class", 
                "org.hibernate.cache.jcache.JCacheRegionFactory");
            properties.put("hibernate.cache.use_query_cache", true);
        };
    }
}

@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product {
    @Id
    private Long id;
    
    private String name;
    
    @Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private List<ProductImage> images;
}

// Avoid N+1 queries
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    // Fetch join to avoid N+1
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.status = :status")
    List<Order> findByStatusWithItems(@Param("status") OrderStatus status);
    
    // Entity graph
    @EntityGraph(attributePaths = {"items", "customer"})
    Optional<Order> findById(Long id);
    
    // Projection for read-only
    @Query("SELECT new com.example.dto.OrderSummary(o.id, o.total, o.status) FROM Order o")
    List<OrderSummary> findAllSummaries();
}

// Batch insert
@Service
public class BulkInsertService {
    
    @Autowired
    private EntityManager em;
    
    @Transactional
    public void bulkInsert(List<Product> products) {
        int batchSize = 50;
        
        for (int i = 0; i < products.size(); i++) {
            em.persist(products.get(i));
            
            if (i % batchSize == 0 && i > 0) {
                em.flush();
                em.clear();
            }
        }
    }
}
```

**4. Async Processing:**

```java
@Configuration
@EnableAsync
public class AsyncConfig {
    
    @Bean("taskExecutor")
    public Executor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(10);
        executor.setMaxPoolSize(50);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("Async-");
        executor.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
        executor.initialize();
        return executor;
    }
    
    // Virtual threads executor (Java 21+)
    @Bean("virtualExecutor")
    public Executor virtualThreadExecutor() {
        return Executors.newVirtualThreadPerTaskExecutor();
    }
}

@Service
public class NotificationService {
    
    @Async("virtualExecutor")
    public CompletableFuture<Void> sendNotifications(List<User> users, String message) {
        List<CompletableFuture<Void>> futures = users.stream()
            .map(user -> CompletableFuture.runAsync(() -> sendEmail(user, message)))
            .toList();
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
    }
}
```

**5. Response Compression:**

```yaml
server:
  compression:
    enabled: true
    mime-types: application/json,application/xml,text/html,text/plain
    min-response-size: 1024
```

**6. HTTP Client Optimization:**

```java
@Configuration
public class RestClientConfig {
    
    @Bean
    public RestClient restClient() {
        // Connection pool
        PoolingHttpClientConnectionManager connectionManager = 
            PoolingHttpClientConnectionManagerBuilder.create()
                .setMaxConnTotal(200)
                .setMaxConnPerRoute(50)
                .setDefaultSocketConfig(SocketConfig.custom()
                    .setSoTimeout(Timeout.ofSeconds(30))
                    .build())
                .build();
        
        CloseableHttpClient httpClient = HttpClients.custom()
            .setConnectionManager(connectionManager)
            .setDefaultRequestConfig(RequestConfig.custom()
                .setConnectionRequestTimeout(Timeout.ofSeconds(5))
                .setResponseTimeout(Timeout.ofSeconds(30))
                .build())
            .evictExpiredConnections()
            .evictIdleConnections(TimeValue.ofMinutes(5))
            .build();
        
        return RestClient.builder()
            .requestFactory(new HttpComponentsClientHttpRequestFactory(httpClient))
            .build();
    }
}
```

**7. Caching Strategy:**

```java
@Service
public class ProductService {
    
    @Autowired
    private ProductRepository repository;
    
    @Autowired
    private CacheManager cacheManager;
    
    // Simple cache
    @Cacheable(value = "products", key = "#id")
    public Product getProduct(Long id) {
        return repository.findById(id).orElse(null);
    }
    
    // Conditional caching
    @Cacheable(value = "products", key = "#category", 
               condition = "#category.length() > 3",
               unless = "#result == null || #result.isEmpty()")
    public List<Product> getByCategory(String category) {
        return repository.findByCategory(category);
    }
    
    // Cache warming on startup
    @PostConstruct
    public void warmCache() {
        List<Product> popular = repository.findTopPopular(100);
        Cache cache = cacheManager.getCache("products");
        popular.forEach(p -> cache.put(p.getId(), p));
    }
}
```

**8. Database Query Optimization:**

```java
// Use native queries for complex operations
@Query(value = """
    SELECT p.*, COUNT(o.id) as order_count
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.id AND o.created_at > :since
    WHERE p.category = :category
    GROUP BY p.id
    ORDER BY order_count DESC
    LIMIT :limit
    """, nativeQuery = true)
List<Object[]> findPopularProducts(
    @Param("category") String category,
    @Param("since") LocalDateTime since,
    @Param("limit") int limit);

// Use streaming for large results
@QueryHints(@QueryHint(name = HINT_FETCH_SIZE, value = "100"))
@Query("SELECT o FROM Order o WHERE o.status = :status")
Stream<Order> streamByStatus(@Param("status") OrderStatus status);

@Transactional(readOnly = true)
public void processLargeDataset() {
    try (Stream<Order> orders = orderRepository.streamByStatus(OrderStatus.PENDING)) {
        orders.forEach(this::processOrder);
    }
}
```

**9. Monitoring and Profiling:**

```java
@Aspect
@Component
public class PerformanceAspect {
    
    private final MeterRegistry registry;
    
    @Around("@annotation(Timed)")
    public Object measureTime(ProceedingJoinPoint joinPoint) throws Throwable {
        String methodName = joinPoint.getSignature().toShortString();
        Timer.Sample sample = Timer.start(registry);
        
        try {
            return joinPoint.proceed();
        } finally {
            sample.stop(Timer.builder("method.execution")
                .tag("method", methodName)
                .register(registry));
        }
    }
}
```

This comprehensive guide covers all critical topics for a 10+ years experienced Java developer interview, including advanced Java concepts, Spring Boot internals, and microservices architecture patterns.
