# Hibernate / JPA — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard — production failures with Testcontainers/Spring)

---

# Part A — Basic

## Exercise 1 — Entity mapping fundamentals

**Difficulty:** Basic

**Task:** Map a `Product` entity with table name `products`, non-null `sku`, and a `BigDecimal price` column `price_amount`. Persist one row with Spring Data JPA and verify the DDL/INSERT.

**Solution:**

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 64)
    private String sku;

    @Column(name = "price_amount", nullable = false, precision = 19, scale = 4)
    private BigDecimal price;

    protected Product() {}

    public Product(String sku, BigDecimal price) {
        this.sku = sku;
        this.price = price;
    }

    // getters/setters
}
```

```java
public interface ProductRepository extends JpaRepository<Product, Long> {}
```

```java
@SpringBootTest
@Transactional
class ProductMappingTest {
    @Autowired ProductRepository repo;

    @Test
    void persistsWithCustomColumnName() {
        var p = repo.save(new Product("SKU-1", new BigDecimal("19.99")));
        assertThat(p.getId()).isNotNull();
        assertThat(repo.findById(p.getId())).get()
                .extracting(Product::getSku, Product::getPrice)
                .containsExactly("SKU-1", new BigDecimal("19.99"));
    }
}
```

```yaml
spring.jpa.hibernate.ddl-auto: validate  # or create-drop for local lab
spring.jpa.show-sql: true
```

**Senior takeaway:** `@Column` defaults are not portable — always specify `nullable`, `length`, and money `precision/scale`. Hibernate 6 maps `BigDecimal` correctly; `double` for money is a production bug.

---

## Exercise 2 — Embeddable value object

**Difficulty:** Basic

**Task:** Model `Customer` with an embedded `Address` (street, city, zip). No separate `address` table — columns live on `customer`.

**Solution:**

```java
@Embeddable
public class Address {
    private String street;
    private String city;

    @Column(name = "zip_code", length = 16)
    private String zip;

    protected Address() {}
    public Address(String street, String city, String zip) {
        this.street = street;
        this.city = city;
        this.zip = zip;
    }
    // getters
}

@Entity
@Table(name = "customer")
public class Customer {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @Embedded
    private Address address;

    protected Customer() {}
    public Customer(String name, Address address) {
        this.name = name;
        this.address = address;
    }
    // getters/setters
}
```

```sql
-- Hibernate generates roughly:
-- customer(id, name, street, city, zip_code)
```

**Senior takeaway:** `@Embeddable` is for **has-a** without identity. Use `@OneToOne` with its own table only when Address has independent lifecycle or history.

---

## Exercise 3 — Bidirectional `@OneToMany` / `@ManyToOne`

**Difficulty:** Basic

**Task:** Map `Author` ↔ `Book`. Always set the owning side (`Book.author`) in a helper method so FK stays consistent.

**Solution:**

```java
@Entity
public class Author {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;

    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Book> books = new ArrayList<>();

    protected Author() {}
    public Author(String name) { this.name = name; }

    public void addBook(Book book) {
        books.add(book);
        book.setAuthor(this); // owning side
    }
}

@Entity
public class Book {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "author_id", nullable = false)
    private Author author;

    protected Book() {}
    public Book(String title) { this.title = title; }
    void setAuthor(Author author) { this.author = author; }
    // getters
}
```

```java
@Test
void bidirectionalHelperSetsFk() {
    var author = new Author("Murakami");
    author.addBook(new Book("Kafka on the Shore"));
    em.persist(author);
    em.flush();
    em.clear();

    var loaded = em.find(Author.class, author.getId());
    assertThat(loaded.getBooks()).hasSize(1);
    assertThat(loaded.getBooks().get(0).getAuthor().getId()).isEqualTo(author.getId());
}
```

**Senior takeaway:** `mappedBy` means **inverse** side — FK is on `Book`. Forgetting `book.setAuthor(this)` yields `author_id = null` at flush.

---

## Exercise 4 — Spring Data derived queries

**Difficulty:** Basic

**Task:** Add `findByAuthorNameIgnoreCaseAndTitleContaining` and `countByAuthorId`. Prove they generate expected SQL.

**Solution:**

```java
public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findByAuthor_NameIgnoreCaseAndTitleContaining(String authorName, String fragment);
    long countByAuthorId(Long authorId);
}
```

```java
@Test
void derivedQueryWorks() {
    var a = authorRepo.save(new Author("Orwell"));
    a.addBook(new Book("1984"));
    a.addBook(new Book("Animal Farm"));
    authorRepo.save(a);

    assertThat(bookRepo.findByAuthor_NameIgnoreCaseAndTitleContaining("orwell", "198"))
            .extracting(Book::getTitle)
            .containsExactly("1984");
    assertThat(bookRepo.countByAuthorId(a.getId())).isEqualTo(2);
}
```

**Senior takeaway:** Underscore in `Author_Name` traverses associations. Derived queries are fine for simple filters; complex joins belong in `@Query` or Specifications.

---

## Exercise 5 — JPQL parameter binding

**Difficulty:** Basic

**Task:** Write a JPQL query returning books published after a date with a minimum average rating (join `Review`).

**Solution:**

```java
@Entity
public class Review {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private int rating;
    @ManyToOne(fetch = FetchType.LAZY) private Book book;
    // ...
}

public interface BookRepository extends JpaRepository<Book, Long> {
    @Query("""
        select b from Book b
        where b.publishedAt > :since
          and (select avg(r.rating) from Review r where r.book = b) >= :minAvg
        """)
    List<Book> findWellRatedSince(
            @Param("since") LocalDate since,
            @Param("minAvg") double minAvg);
}
```

```java
@Test
void jpqlAggregateFilter() {
    // seed books + reviews ...
    var results = bookRepo.findWellRatedSince(LocalDate.of(2020, 1, 1), 4.0);
    assertThat(results).isNotEmpty();
}
```

**Senior takeaway:** Always use **named parameters** — never string-concatenate user input into JPQL. Correlated subqueries are readable but can be slow; consider a grouped query or denormalized `avg_rating` column at scale.

---

## Exercise 6 — `@Enumerated` mapping

**Difficulty:** Basic

**Task:** Map `OrderStatus` as `STRING`. Show why `ORDINAL` is dangerous.

**Solution:**

```java
public enum OrderStatus { PENDING, PAID, SHIPPED, CANCELLED }

@Entity
public class ShopOrder {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    private OrderStatus status = OrderStatus.PENDING;
    // ...
}
```

```java
// ORDINAL stores 0,1,2,3 — reordering enum constants corrupts existing rows
// @Enumerated(EnumType.ORDINAL)  // NEVER in production
```

**Senior takeaway:** `STRING` is the default senior choice. For unknown future values from other services, use `@JdbcTypeCode(SqlTypes.NAMED_ENUM)` (Postgres) or a converter.

---

## Exercise 7 — `LAZY` vs `EAGER` in one test

**Difficulty:** Basic

**Task:** Demonstrate that `EAGER` always loads `author` with `Book`, while `LAZY` loads it only when accessed inside a transaction.

**Solution:**

```java
@Entity
public class EagerBook {
    @Id Long id;
    String title;
    @ManyToOne(fetch = FetchType.EAGER)
    Author author;
}

@Entity
public class LazyBook {
    @Id Long id;
    String title;
    @ManyToOne(fetch = FetchType.LAZY)
    Author author;
}
```

```java
@Test
void lazyRequiresTransaction() {
    LazyBook book = em.find(LazyBook.class, 1L);
    // outside TX: book.getAuthor().getName() → LazyInitializationException

    TransactionTemplate tx = new TransactionTemplate(transactionManager);
    tx.executeWithoutResult(status -> {
        LazyBook b = em.find(LazyBook.class, 1L);
        assertThat(b.getAuthor().getName()).isNotBlank(); // extra SELECT
    });
}
```

Enable SQL logging and count statements: `EagerBook` find = 1 or 2 queries always; `LazyBook` find = 1 until touch.

**Senior takeaway:** Default `@ManyToOne` is `EAGER` in JPA spec — **override to `LAZY`** everywhere except tiny, always-needed associations.

---

## Exercise 8 — `persist` vs `merge` identity

**Difficulty:** Basic

**Task:** Show that `persist` returns void and uses the same instance; `merge` on a detached entity returns a **different** managed instance.

**Solution:**

```java
@Test
void persistVsMerge() {
    var book = new Book("Dune");
    em.persist(book);
    assertThat(em.contains(book)).isTrue();

    em.detach(book);
    book.setTitle("Dune Messiah");
    Book managed = em.merge(book);

    assertThat(managed).isNotSameAs(book);
    assertThat(em.contains(book)).isFalse();
    assertThat(em.contains(managed)).isTrue();
    assertThat(managed.getTitle()).isEqualTo("Dune Messiah");
}
```

**Senior takeaway:** Spring Data `save()` calls `merge` when `id != null`. Updates via detached entities from REST DTOs cause subtle bugs — load inside TX, mutate, rely on dirty checking.

---

## Exercise 9 — `@GeneratedValue` IDENTITY

**Difficulty:** Basic

**Task:** Persist 3 `Book` rows with `GenerationType.IDENTITY`. Observe INSERT-per-row and immediate ID assignment.

**Solution:**

```java
@Entity
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    // ...
}

@Test
void identityAssignsIdAfterInsert() {
    var b1 = repo.save(new Book("A"));
    assertThat(b1.getId()).isNotNull(); // ID available after save (flush)
    repo.saveAll(List.of(new Book("B"), new Book("C")));
}
```

```yaml
logging.level.org.hibernate.SQL: DEBUG
```

**Senior takeaway:** `IDENTITY` disables JDBC batching for inserts — acceptable for low volume; use `SEQUENCE` + `allocationSize` for bulk loads (Exercise 16).

---

## Exercise 10 — Read JPA config and SQL logging

**Difficulty:** Basic

**Task:** Configure Hibernate to format SQL, log bind parameters, and name the persistence unit. Run one test and read the output.

**Solution:**

```yaml
spring:
  jpa:
    open-in-view: false
    show-sql: false  # prefer logging below
    properties:
      hibernate:
        format_sql: true
        use_sql_comments: true
        jdbc:
          batch_size: 30
        order_inserts: true
        order_updates: true

logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.orm.jdbc.bind: TRACE
```

```java
@SpringBootApplication
public class BookstoreApp {
    public static void main(String[] args) {
        SpringApplication.run(BookstoreApp.class, args);
    }
}
```

**Senior takeaway:** `show-sql: true` bypasses logging frameworks and duplicates output in prod. Use `org.hibernate.SQL` + bind TRACE locally; ship structured metrics (query count/latency) in prod.

---

# Part B — Intermediate

## Exercise 11 — N+1 detection and `join fetch` fix

**Difficulty:** Intermediate

**Task:** Load all books and print author names. Count SQL statements before and after `join fetch`.

**Solution:**

```java
// BROKEN — N+1
List<Book> books = bookRepo.findAll();
books.forEach(b -> System.out.println(b.getAuthor().getName()));

// FIX
@Query("select distinct b from Book b join fetch b.author")
List<Book> findAllWithAuthor();
```

```java
@Test
void nPlusOneFixed() {
    // seed 10 books, 10 authors
    var proxy = new DataSourceProxyBeanPostProcessor(); // or datasource-proxy lib
    int before = proxy.getQueryCount();
    bookRepo.findAll().forEach(b -> b.getAuthor().getName());
    int nPlusOne = proxy.getQueryCount() - before; // expect 11

    proxy.reset();
    bookRepo.findAllWithAuthor().forEach(b -> b.getAuthor().getName());
    int fixed = proxy.getQueryCount() - before; // expect 1
    assertThat(fixed).isLessThan(nPlusOne);
}
```

**Senior takeaway:** N+1 is invisible in unit tests with 2 rows — use SQL counters or Hibernate statistics. `join fetch` is the scalpel; `@EntityGraph` (Exercise 12) is the Spring Data idiom.

---

## Exercise 12 — `@EntityGraph` on repository method

**Difficulty:** Intermediate

**Task:** Replace `join fetch` with `@EntityGraph(attributePaths = "author")` on `findAll`.

**Solution:**

```java
@EntityGraph(attributePaths = {"author"})
@Override
List<Book> findAll();

// or
@EntityGraph(attributePaths = {"author", "reviews"})
@Query("select b from Book b where b.id in :ids")
List<Book> findAllWithGraph(@Param("ids") List<Long> ids);
```

```java
@Test
void entityGraphLoadsAssociation() {
    var books = bookRepo.findAll();
    assertThat(books.get(0).getAuthor().getName()).isNotBlank(); // no extra SELECT
}
```

**Senior takeaway:** `@EntityGraph` generates a `left outer join` fetch plan — same SQL family as `join fetch`, but keeps queries declarative and works with `JpaSpecificationExecutor`.

---

## Exercise 13 — Pagination + `join fetch` (two-query pattern)

**Difficulty:** Intermediate

**Task:** Page authors with their books without `MultipleBagFetchException` or broken `LIMIT` semantics.

**Solution:**

```java
public interface AuthorRepository extends JpaRepository<Author, Long> {
    @Query("select a.id from Author a order by a.name")
    Page<Long> findIds(Pageable pageable);

    @Query("select distinct a from Author a join fetch a.books where a.id in :ids")
    List<Author> fetchWithBooks(@Param("ids") List<Long> ids);
}

@Service
public class AuthorPageService {
    public Page<Author> pageWithBooks(Pageable pageable) {
        Page<Long> ids = authorRepo.findIds(pageable);
        if (ids.isEmpty()) return Page.empty(pageable);
        List<Author> content = authorRepo.fetchWithBooks(ids.getContent());
        // preserve page order
        Map<Long, Author> byId = content.stream()
                .collect(Collectors.toMap(Author::getId, Function.identity()));
        List<Author> ordered = ids.getContent().stream().map(byId::get).toList();
        return new PageImpl<>(ordered, pageable, ids.getTotalElements());
    }
}
```

**Senior takeaway:** `join fetch` + `Pageable` makes Hibernate fetch **all** rows then slice in memory — silent OOM. Two-query pattern is the production default for paginated graphs.

---

## Exercise 14 — Optimistic locking with `@Version`

**Difficulty:** Intermediate

**Task:** Two transactions read the same `Account`, both add money, both save — one must throw `OptimisticLockingFailureException`.

**Solution:**

```java
@Entity
public class Account {
    @Id private String id;
    private long balanceCents;
    @Version private long version;
    // getters/setters
}

@Test
void optimisticLockConflict() {
    accountRepo.save(new Account("a1", 1000L));

    TransactionTemplate tx = new TransactionTemplate(transactionManager);

    tx.executeWithoutResult(s -> {
        var a = accountRepo.findById("a1").orElseThrow();
        a.setBalanceCents(a.getBalanceCents() + 100);
        accountRepo.save(a);
    }); // commits, version 0 → 1

    assertThatThrownBy(() -> tx.executeWithoutResult(s -> {
        var a = accountRepo.findById("a1").orElseThrow(); // still sees version 0 if stale
        a.setBalanceCents(a.getBalanceCents() + 100);
        accountRepo.save(a); // UPDATE ... WHERE version = 0 → 0 rows
    })).hasCauseInstanceOf(OptimisticLockingFailureException.class);
}
```

Expose `version` as ETag in REST for If-Match concurrency control.

**Senior takeaway:** `@Version` prevents lost updates without long DB locks. Retries must be **application-level** with backoff — not infinite loops on hot rows.

---

## Exercise 15 — Pessimistic write lock

**Difficulty:** Intermediate

**Task:** Serialize balance transfers on the same account using `LockModeType.PESSIMISTIC_WRITE`.

**Solution:**

```java
public interface AccountRepository extends JpaRepository<Account, String> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select a from Account a where a.id = :id")
    Optional<Account> findForUpdate(@Param("id") String id);
}

@Service
public class TransferService {
    @Transactional
    public void transfer(String from, String to, long cents) {
        Account src = accountRepo.findForUpdate(from).orElseThrow();
        Account dst = accountRepo.findForUpdate(to).orElseThrow();
        if (src.getBalanceCents() < cents) throw new IllegalStateException("insufficient");
        src.setBalanceCents(src.getBalanceCents() - cents);
        dst.setBalanceCents(dst.getBalanceCents() + cents);
    }
}
```

```sql
-- Hibernate emits: select ... from account where id = ? for update
```

**Senior takeaway:** Pessimistic locks trade throughput for correctness. Lock ordering (`from` then `to` by id) prevents deadlocks — see Exercise 26.

---

## Exercise 16 — `IDENTITY` vs `SEQUENCE` batch insert

**Difficulty:** Intermediate

**Task:** Persist 1000 `EventLog` rows. Compare `PreparedStatement` count with `IDENTITY` vs `SEQUENCE` and `hibernate.jdbc.batch_size=50`.

**Solution:**

```java
@Entity
@SequenceGenerator(name = "event_seq", sequenceName = "event_log_seq", allocationSize = 50)
public class EventLog {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "event_seq")
    private Long id;
    private String payload;
}

// IDENTITY variant: @GeneratedValue(strategy = GenerationType.IDENTITY)
```

```yaml
spring.jpa.properties.hibernate.jdbc.batch_size: 50
spring.jpa.properties.hibernate.order_inserts: true
spring.jpa.properties.hibernate.generate_statistics: true
```

```java
@Test
void batchInsertWithSequence() {
    var logs = IntStream.range(0, 1000)
            .mapToObj(i -> new EventLog("evt-" + i))
            .toList();
    long t0 = System.nanoTime();
    eventRepo.saveAll(logs);
    em.flush();
  long ms = (System.nanoTime() - t0) / 1_000_000;
    Statistics stats = sessionFactory.getStatistics();
    // SEQUENCE: ~20 batched INSERTs; IDENTITY: ~1000 individual INSERTs
}
```

**Senior takeaway:** `IDENTITY` forces row-by-row insert to read generated keys — the #1 silent perf regression after "it worked in dev." Use `SEQUENCE` (Postgres) or batch JDBC with `RETURNING` awareness.

---

## Exercise 17 — Bulk JPQL `UPDATE` vs persistence context

**Difficulty:** Intermediate

**Task:** Bulk-update book titles, then show stale in-memory entity until `clear()`.

**Solution:**

```java
@Test
void bulkUpdateBypassesPc() {
    bookRepo.save(new Book("Old Title"));
    Long id = bookRepo.findAll().get(0).getId();

    em.createQuery("update Book b set b.title = 'Bulk' where b.id = :id")
            .setParameter("id", id)
            .executeUpdate();

    Book inPc = em.find(Book.class, id);
    assertThat(inPc.getTitle()).isEqualTo("Old Title"); // stale

    em.clear();
    Book fresh = em.find(Book.class, id);
    assertThat(fresh.getTitle()).isEqualTo("Bulk");
}
```

```java
// Safer pattern: @Modifying(clearAutomatically = true, flushAutomatically = true)
@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update Book b set b.title = :title where b.id = :id")
int retitle(@Param("id") Long id, @Param("title") String title);
```

**Senior takeaway:** Bulk DML does not update the persistence context. Mixing bulk updates with managed entities in the same TX is a classic "UI shows old data" bug.

---

## Exercise 18 — Soft delete with `@SQLDelete` and `@Where`

**Difficulty:** Intermediate

**Task:** `delete(book)` sets `deleted = true`. JPQL hides it; native SQL does not.

**Solution:**

```java
@Entity
@SQLDelete(sql = "UPDATE book SET deleted = true WHERE id = ?")
@SQLRestriction("deleted = false") // Hibernate 6; was @Where
public class Book {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    @Column(nullable = false)
    private boolean deleted = false;
}

@Test
void softDeleteAndNativeLeak() {
    var book = bookRepo.save(new Book("Visible"));
    bookRepo.delete(book);

    assertThat(bookRepo.findById(book.getId())).isEmpty();

    Number nativeCount = (Number) em.createNativeQuery(
            "SELECT count(*) FROM book WHERE id = :id", Number.class)
            .setParameter("id", book.getId())
            .getSingleResult();
    assertThat(nativeCount.intValue()).isEqualTo(1); // row still there
}
```

**Senior takeaway:** Soft delete filters apply only to entity queries. Native SQL, reporting replicas, and caches need the same `deleted = false` predicate — or you leak "deleted" data.

---

## Exercise 19 — Disable OSIV and fix `LazyInitializationException`

**Difficulty:** Intermediate

**Task:** Turn off Open Session In View. Fix a controller that returns `Book` with `author.name` by loading a DTO inside `@Transactional` service.

**Solution:**

```yaml
spring.jpa.open-in-view: false
```

```java
// BROKEN after OSIV off
@GetMapping("/books/{id}")
BookDto get(@PathVariable Long id) {
    Book b = bookRepo.findById(id).orElseThrow();
    return new BookDto(b.getId(), b.getTitle(), b.getAuthor().getName()); // LIE
}

// FIXED
public record BookDto(Long id, String title, String authorName) {}

@Service
public class BookQueryService {
    @Transactional(readOnly = true)
    public BookDto get(Long id) {
        Book b = bookRepo.findById(id).orElseThrow();
        return new BookDto(b.getId(), b.getTitle(), b.getAuthor().getName());
    }
}

// BETTER — one query
@Query("select new com.example.BookDto(b.id, b.title, a.name) from Book b join b.author a where b.id = :id")
Optional<BookDto> findDto(@Param("id") Long id);
```

**Senior takeaway:** OSIV hides lazy-loading during JSON serialization — it holds a DB connection for the entire HTTP render. Disabling it forces explicit fetch boundaries (good) and cuts connection hold time (critical under load).

---

## Exercise 20 — Datasource-proxy SQL budget test

**Difficulty:** Intermediate

**Task:** Assert a service method runs ≤ 3 SQL statements using `datasource-proxy` or `ttddyy` wrapper.

**Solution:**

```java
@Bean
DataSource dataSource(DataSourceProperties props) {
    DataSource real = props.initializeDataSourceBuilder().build();
  return ProxyDataSourceBuilder.create(real)
            .name("proxy")
            .logQueryBySlf4j(INFO)
            .countQuery(new AtomicLong()::addAndGet) // hook for tests
            .build();
}

@SpringBootTest
class SqlBudgetTest {
    @Autowired BookService service;
    static AtomicLong queryCount = new AtomicLong();

    @BeforeEach void reset() { queryCount.set(0); }

    @Test
    void listDashboardUnderBudget() {
        service.listDashboard();
        assertThat(queryCount.get()).isLessThanOrEqualTo(3);
    }
}
```

**Senior takeaway:** Asserting SQL count is more valuable than 80% of integration tests. One service method → 50 queries means N+1 ships to prod.

---

# Part C — Hard (production failures)

## Exercise 21 — N+1 timeout under load (Testcontainers)

**Difficulty:** Hard

**Task:** Seed 500 books. A dashboard endpoint triggers N+1. Prove p95 latency exceeds 2s, then fix with `join fetch` and prove ≤ 3 queries and p95 < 200ms.

**Solution:**

```java
@Testcontainers
@SpringBootTest(webEnvironment = RANDOM_PORT)
class N1ProductionIncidentTest {
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry r) {
        r.add("spring.datasource.url", postgres::getJdbcUrl);
        r.add("spring.datasource.username", postgres::getUsername);
        r.add("spring.datasource.password", postgres::getPassword);
        r.add("spring.jpa.open-in-view", () -> "false");
    }

    @Autowired TestRestTemplate rest;
    @Autowired BookSeeder seeder;

    @Test
    void n1CausesSloBreachThenFixed() {
        seeder.insert(500);
        // broken endpoint uses findAll + lazy author
        long brokenP95 = hammer("/api/books/broken", 50);
        assertThat(brokenP95).isGreaterThan(2000);

        long fixedP95 = hammer("/api/books/fixed", 50);
        assertThat(fixedP95).isLessThan(200);
    }
}
```

```java
@Query("select distinct b from Book b join fetch b.author")
List<Book> findAllWithAuthor();
```

**Senior takeaway:** N+1 is a **capacity** incident, not a correctness bug. It passes CI with H2 and 5 rows. Load test + SQL count gates in CI catch it.

---

## Exercise 22 — Lost update without `@Version` (Testcontainers)

**Difficulty:** Hard

**Task:** Two concurrent threads increment `visits` on a `PageStat` row without `@Version`. Prove one increment is lost. Add `@Version` and retry logic — no lost updates.

**Solution:**

```java
@Entity
public class PageStat {
    @Id private String path;
    private long visits;
    // @Version private long version; — add in fix
}

@Test
void lostUpdateWithoutVersion() throws Exception {
    repo.save(new PageStat("/home", 0));
    var latch = new CountDownLatch(1);
    Runnable inc = () -> {
        latch.await();
        tx.executeWithoutResult(s -> {
            var p = repo.findById("/home").orElseThrow();
            p.setVisits(p.getVisits() + 1);
            repo.save(p);
        });
    };
    var t1 = Thread.startVirtualThread(inc);
    var t2 = Thread.startVirtualThread(inc);
    latch.countDown();
    t1.join(); t2.join();
    assertThat(repo.findById("/home").get().getVisits()).isEqualTo(1); // LOST UPDATE

    // Fix: @Version + retry
}
```

```java
@Retryable(retryFor = OptimisticLockingFailureException.class, maxAttempts = 5)
@Transactional
public void increment(String path) {
    var p = repo.findById(path).orElseThrow();
    p.setVisits(p.getVisits() + 1);
}
```

**Senior takeaway:** Read-modify-write without versioning relies on luck. At scale, lost updates corrupt analytics, inventory, and quotas — always ask "what if two pods do this at once?"

---

## Exercise 23 — 2nd level cache stale read after native UPDATE (Testcontainers)

**Difficulty:** Hard

**Task:** Enable 2nd-level cache on `Product`. Read through cache. Native SQL updates price. Show stale cached value until eviction.

**Solution:**

```yaml
spring.jpa.properties.hibernate.cache.use_second_level_cache: true
spring.jpa.properties.hibernate.cache.region.factory_class: org.hibernate.cache.jcache.JCacheRegionFactory
```

```java
@Entity
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Product { /* id, sku, price */ }

@Test
void secondLevelCacheStaleAfterNative() {
    var p = repo.save(new Product("SKU-1", new BigDecimal("10.00")));
    em.clear();

    Product cached = repo.findById(p.getId()).orElseThrow(); // hits cache on 2nd read
    em.createNativeQuery("UPDATE products SET price_amount = 99.99 WHERE id = :id")
            .setParameter("id", p.getId())
            .executeUpdate();

    em.clear();
    Product stale = repo.findById(p.getId()).orElseThrow();
    assertThat(stale.getPrice()).isNotEqualByComparingTo(new BigDecimal("99.99")); // STALE

    cacheManager.getCache("com.example.Product").evict(p.getId());
    Product fresh = repo.findById(p.getId()).orElseThrow();
    assertThat(fresh.getPrice()).isEqualByComparingTo(new BigDecimal("99.99"));
}
```

**Senior takeaway:** 2nd-level cache is fast until **anything** bypasses Hibernate — native queries, ETL, DBA hotfix. Pair caches with eviction strategy, TTL, or avoid caching frequently mutated entities.

---

## Exercise 24 — Flyway migration failure mid-deploy (Testcontainers)

**Difficulty:** Hard

**Task:** V1 creates table. V2 adds `NOT NULL` column without default on a non-empty table — migration fails. Prove app won't start. Fix with multi-step migration (nullable → backfill → NOT NULL).

**Solution:**

```sql
-- V1__init.sql
CREATE TABLE customer (id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL);

-- V2__broken.sql (fails on existing rows)
ALTER TABLE customer ADD COLUMN email TEXT NOT NULL;

-- V2__fixed_step1.sql
ALTER TABLE customer ADD COLUMN email TEXT;

-- V3__backfill.sql
UPDATE customer SET email = concat('unknown+', id, '@example.com') WHERE email IS NULL;

-- V4__enforce.sql
ALTER TABLE customer ALTER COLUMN email SET NOT NULL;
```

```java
@Test
void flywayFailedMigrationBlocksStartup() {
    // seed data via JDBC before V2
    assertThatThrownBy(() -> contextRunner.withPropertyValues(...).run(ctx -> {}))
            .hasRootCauseInstanceOf(FlywayException.class);
}
```

```yaml
spring.flyway.validate-on-migrate: true
spring.flyway.baseline-on-migrate: false
```

**Senior takeaway:** Failed Flyway on deploy locks the fleet. Expand-contract migrations (add nullable → backfill → constrain) are non-optional for zero-downtime. Never `NOT NULL` without default on live tables.

---

## Exercise 25 — Connection pool exhaustion from OSIV (Testcontainers + load)

**Difficulty:** Hard

**Task:** With `open-in-view: true` and a slow client (WireMock delay on response), 20 concurrent requests exhaust a pool of size 10. Disable OSIV + DTO fetch — pool stays healthy.

**Solution:**

```yaml
spring.datasource.hikari.maximum-pool-size: 10
spring.datasource.hikari.connection-timeout: 2000
spring.jpa.open-in-view: true  # incident config
```

```java
@Test
void osivExhaustsPool() {
    // Endpoint returns entity graph, client reads body slowly (1s delay)
    ExecutorService pool = Executors.newFixedThreadPool(20);
    List<Future<?>> futures = IntStream.range(0, 20)
            .mapToObj(i -> pool.submit(() -> rest.getForEntity("/books/slow-client", String.class)))
            .toList();

    assertThatThrownBy(() -> {
        futures.get(15).get(3, TimeUnit.SECONDS);
    }).hasCauseInstanceOf(ResourceAccessException.class); // pool timeout

    // Fix: open-in-view: false + @Transactional service + DTO
}
```

**Senior takeaway:** OSIV ties connection lifetime to **client read speed** — slow mobile clients and large JSON become pool exhaustion. This is the #1 reason senior teams disable OSIV.

---

## Exercise 26 — Deadlock: pessimistic lock ordering (Testcontainers)

**Difficulty:** Hard

**Task:** `transfer(a,b)` locks account `a` then `b`. Two concurrent transfers `a→b` and `b→a` deadlock. Fix by locking accounts in consistent `id` order.

**Solution:**

```java
// BROKEN
public void transfer(String from, String to, long cents) {
    lock(from);
    lock(to);
}

// FIXED
@Transactional
public void transfer(String fromId, String toId, long cents) {
    String first = fromId.compareTo(toId) < 0 ? fromId : toId;
    String second = fromId.compareTo(toId) < 0 ? toId : fromId;
    Account a = accountRepo.findForUpdate(first).orElseThrow();
    Account b = accountRepo.findForUpdate(second).orElseThrow();
    // debit/credit based on fromId/toId
}
```

```java
@Test
void concurrentOppositeTransfersNoDeadlock() throws Exception {
    // seed accounts; run a→b and b→a concurrently 50 times
    // without fix: Postgres logs deadlock detected
    // with fix: all complete
}
```

**Senior takeaway:** Deadlocks are normal with pessimistic locking — DB picks a victim. Consistent lock ordering + short transactions + retry on `40001` serialization/deadlock is production hygiene.

---

## Exercise 27 — Batch insert regression after IDENTITY migration (Testcontainers)

**Difficulty:** Hard

**Task:** App migrated from Oracle (`SEQUENCE`) to Postgres (`IDENTITY`). Bulk ingest job slows 10×. Prove JDBC batching stopped; fix with `SEQUENCE` generator.

**Solution:**

```java
@Test
void identityKillsBatching() {
    statistics.clear();
    ingestService.importRows(5000);
    long jdbcBatchCount = statistics.getEntityInsertCount(); // ~5000 individual

    // switch to SEQUENCE + allocationSize 50
    ingestService.importRows(5000);
    // ~100 batched statements in logs
}
```

```java
@SequenceGenerator(name = "ingest_seq", sequenceName = "ingest_seq", allocationSize = 50)
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "ingest_seq")
```

**Senior takeaway:** ORM migrations change performance characteristics silently. Benchmark insert throughput in staging with production row counts; watch Hibernate stats `session.metrics` in prod canaries.

---

## Exercise 28 — `merge()` wipes associations in production (Testcontainers)

**Difficulty:** Hard

**Task:** PUT endpoint maps JSON → detached `Author` with `id` but empty `books` list. `repository.save()` merges and orphan-removes all books. Reproduce and fix with load-update-DTO pattern.

**Solution:**

```java
// BROKEN controller
@PutMapping("/authors/{id}")
void update(@PathVariable Long id, @RequestBody Author payload) {
    payload.setId(id);
    authorRepo.save(payload); // merge: books = empty → orphanRemoval deletes all
}

// FIXED
@PutMapping("/authors/{id}")
AuthorDto update(@PathVariable Long id, @RequestBody AuthorUpdateDto dto) {
    return authorService.update(id, dto);
}

@Transactional
public AuthorDto update(Long id, AuthorUpdateDto dto) {
    Author author = authorRepo.findById(id).orElseThrow();
    author.setName(dto.name()); // copy scalar fields only
    return AuthorDto.from(author);
}
```

```java
@Test
void mergeWipesChildren() {
    var author = authorRepo.save(authorWithBooks(3));
    var detached = new Author();
    detached.setId(author.getId());
    detached.setName("Renamed");
    // detached.books is empty default
    authorRepo.save(detached);
    em.flush();
    assertThat(bookRepo.countByAuthorId(author.getId())).isZero(); // DATA LOSS
}
```

**Senior takeaway:** `merge` replaces managed state with detached graph — null/empty collections become deletes with `orphanRemoval=true`. Never expose entities on REST; DTO in, explicit field copy, associations via dedicated endpoints.

---

## Exercise 29 — `@SQLRestriction` soft delete filter

**Difficulty:** Basic

**Task:** Map `Customer` with `@SQLDelete` UPDATE flag and `@SQLRestriction("deleted = false")`. Persist, remove, assert `findAll` empty but row exists with `deleted=true` via native query.

**Solution:**

```java
@Entity
@SQLDelete(sql = "UPDATE customers SET deleted = true WHERE id = ?")
@SQLRestriction("deleted = false")
class Customer {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    String email;
    boolean deleted = false;
}

@Query(value = "SELECT COUNT(*) FROM customers WHERE deleted = true", nativeQuery = true)
long countSoftDeleted();
```

```java
@Test
void softDeleteHidesFromOrm() {
    var c = repo.save(new Customer("a@b.com"));
    repo.delete(c);
    assertThat(repo.findAll()).isEmpty();
    assertThat(repo.countSoftDeleted()).isEqualTo(1);
}
```

**Senior takeaway:** Add partial unique index on `email WHERE deleted=false` or re-registration breaks after soft delete.

---

## Exercise 30 — `@NaturalId` lookup

**Difficulty:** Basic

**Task:** Map `Product` with `@NaturalId(mutable = false) String sku`. Load via `EntityManager.unwrap(Session.class).byNaturalId(Product.class).using("sku", "X").load()`.

**Solution:**

```java
@Entity
class Product {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    @NaturalId(mutable = false)
    @Column(nullable = false, unique = true)
    String sku;
    BigDecimal price;
}

@Test
void loadByNaturalId(EntityManager em) {
    em.persist(new Product("SKU-9", new BigDecimal("1.00")));
    em.flush();
    em.clear();
    Session session = em.unwrap(Session.class);
    Product p = session.byNaturalId(Product.class).using("sku", "SKU-9").load();
    assertThat(p.getPrice()).isEqualByComparingTo("1.00");
}
```

**Senior takeaway:** Natural id cache helps read-heavy SKU resolution — evict region after bulk catalog import.

---

## Exercise 31 — `@BatchSize` vs N+1 measurement

**Difficulty:** Intermediate

**Task:** `Author` one-to-many `Book`; load 10 authors with lazy books. Compare SQL count with and without `@BatchSize(16)` using datasource-proxy or Hibernate statistics.

**Solution:**

```java
@Entity
class Author {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    @OneToMany(mappedBy = "author")
    @BatchSize(size = 16) // toggle for lab
    List<Book> books = new ArrayList<>();
}

@Test
void batchFetchReducesQueries() {
    // seed 10 authors x 3 books
    statistics.setStatisticsEnabled(true);
    statistics.clear();
    authorRepo.findAll().forEach(a -> a.getBooks().size());
    long queries = statistics.getPrepareStatementCount();
    assertThat(queries).isLessThan(15); // without @BatchSize expect ~11+
}
```

**Senior takeaway:** Hot list endpoints should use DTO projection — `@BatchSize` is safety net, not primary design.

---

## Exercise 32 — `@NamedEntityGraph` on repository

**Difficulty:** Intermediate

**Task:** Declare `@NamedEntityGraph(name = "Order.withLines", attributeNodes = @NamedAttributeNode("lines"))` on `Order`. Repository method with `@EntityGraph("Order.withLines")` loads order + lines in bounded queries.

**Solution:**

```java
@Entity
@NamedEntityGraph(
    name = "Order.withLines",
    attributeNodes = @NamedAttributeNode("lines"))
class Order {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    Long id;
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    List<OrderLine> lines;
}

interface OrderRepository extends JpaRepository<Order, Long> {
    @EntityGraph("Order.withLines")
    Optional<Order> findWithLinesById(Long id);
}
```

```java
@Test
void graphLoadsLines(@Autowired OrderRepository repo, EntityManager em) {
    // persist order + 2 lines
    var o = repo.findWithLinesById(orderId).orElseThrow();
    assertThat(o.getLines()).hasSize(2);
    em.clear();
    // access lines without LazyInitializationException
    assertThat(repo.findWithLinesById(orderId).orElseThrow().getLines()).hasSize(2);
}
```

**Senior takeaway:** Do not use `@EntityGraph` FETCH join with `Page` — duplicates rows; use LOAD type or separate count query.

---

## Exercise 33 — Soft delete + unique constraint production bug (Testcontainers)

**Difficulty:** Hard

**Task:** Reproduce duplicate email registration failure after soft delete on Postgres Testcontainers; fix with partial unique index or compound unique `(email, deleted)`.

**Solution:**

```sql
-- Flyway V2__partial_unique_email.sql (Postgres)
CREATE UNIQUE INDEX uk_customer_email_active ON customers (email) WHERE deleted = false;
```

```java
@Testcontainers
@SpringBootTest
class SoftDeleteUniqueIT {
    @Container @ServiceConnection
    static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16-alpine");

    @Test
    void reregisterAfterSoftDelete() {
        var c = repo.save(new Customer("u@x.com"));
        repo.delete(c); // soft
        assertThat(repo.save(new Customer("u@x.com")).getId()).isNotNull();
    }
}
```

Without partial index, second save throws `DataIntegrityViolationException`.

**Senior takeaway:** Soft delete changes constraint design — ORM annotations alone do not fix DB uniqueness; coordinate with Flyway and product policy on email reuse.

---

## Exercise 34 — Spring Data Specification admin search

**Difficulty:** Intermediate

**Task:** Build dynamic admin order search: optional `status`, `createdAfter`, `customerEmailContains` filters using `JpaSpecificationExecutor`. Always AND a mandatory `tenantId` spec. Return `Page<OrderSummaryProjection>` with allowlisted sort fields.

**Solution:**

```java
public interface OrderRepository extends JpaRepository<Order, Long>, JpaSpecificationExecutor<Order> {
    @Query("""
        SELECT o.id AS id, o.status AS status, o.total AS total
        FROM Order o WHERE o.id IN :ids
        """)
    List<OrderSummaryProjection> findSummariesByIds(@Param("ids") List<Long> ids);
}

public final class OrderSpecs {
    public static Specification<Order> hasTenant(UUID tenantId) {
        return (root, q, cb) -> cb.equal(root.get("tenantId"), tenantId);
    }
    public static Specification<Order> statusEq(Status s) {
        return (root, q, cb) -> cb.equal(root.get("status"), s);
    }
    public static Specification<Order> createdAfter(Instant after) {
        return (root, q, cb) -> cb.greaterThanOrEqualTo(root.get("createdAt"), after);
    }
    public static Specification<Order> customerEmailContains(String term) {
        return (root, q, cb) -> cb.like(cb.lower(root.join("customer").get("email")),
            "%" + term.toLowerCase() + "%");
    }
}

@Service
class OrderAdminService {
    Page<OrderSummaryProjection> search(UUID tenantId, SearchCriteria c, Pageable pageable) {
        var spec = Specification.where(OrderSpecs.hasTenant(tenantId));
        if (c.status() != null) spec = spec.and(OrderSpecs.statusEq(c.status()));
        if (c.createdAfter() != null) spec = spec.and(OrderSpecs.createdAfter(c.createdAfter()));
        if (c.email() != null && !c.email().isBlank())
            spec = spec.and(OrderSpecs.customerEmailContains(c.email()));
        return orderRepo.findAll(spec, pageable).map(o -> /* map or use projection query */);
    }
}
```

```java
@DataJpaTest
class OrderSpecsIT {
    @Test
    void tenantSpecIsolatesRows() {
        // seed tenant A + B orders; assert findAll(hasTenant(A)) size
    }
}
```

**Senior takeaway:** Specifications compose admin filters safely — always bolt on tenant spec server-side; never trust client to filter multi-tenant data.

---

## Exercise 35 — `@Modifying` bulk status update + persistence context

**Difficulty:** Intermediate

**Task:** Add repository method to expire open carts older than 24h. Verify `clearAutomatically` prevents stale reads in same transaction test. Assert returned row count.

**Solution:**

```java
public interface CartRepository extends JpaRepository<Cart, Long> {
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query("UPDATE Cart c SET c.status = com.app.CartStatus.EXPIRED WHERE c.status = OPEN AND c.updatedAt < :cutoff")
    int expireStale(@Param("cutoff") Instant cutoff);
}
```

```java
@DataJpaTest
class CartExpireIT {
    @Autowired CartRepository carts;
    @Autowired TestEntityManager em;

    @Test
    void expireUpdatesAndClearsContext() {
        var cart = carts.save(new Cart(/* OPEN, updated 2 days ago */));
        int updated = carts.expireStale(Instant.now().minus(24, ChronoUnit.HOURS));
        assertThat(updated).isEqualTo(1);
        assertThat(carts.findById(cart.getId())).get()
            .extracting(Cart::getStatus).isEqualTo(CartStatus.EXPIRED);
    }
}
```

**Senior takeaway:** Bulk JPQL bypasses entity listeners — pair `@Modifying` clear with L2 eviction on hot entities if second-level cache enabled.

---

## Exercise 36 — Feign client with timeouts and error decoder

**Difficulty:** Hard

**Task:** From a Spring Boot app using JPA repositories, call an external `pricing-service` via OpenFeign to enrich `Product` listings. Configure timeouts; map 404 to `PriceNotFoundException`. Keep Feign DTOs separate from JPA entities.

**Solution:**

```java
@FeignClient(name = "pricing", configuration = PricingFeignConfig.class)
public interface PricingClient {
    @GetMapping("/prices/{sku}")
    PriceDto getPrice(@PathVariable String sku);
}

@Service
class ProductCatalogService {
    ProductCardDto enrich(Product p) {
        var price = pricingClient.getPrice(p.getSku()); // DTO boundary — not Product entity
        return productMapper.toCard(p, price);
    }
}
```

```yaml
spring.cloud.openfeign.client.config.pricing:
  connectTimeout: 500
  readTimeout: 2000
```

**Senior takeaway:** JPA entities stay inside the persistence layer — Feign DTOs are anti-corruption at the integration boundary (eazybytes DTO pattern).

---

## Exercise 37 — Spring Cloud Config refresh + `@RefreshScope`

**Difficulty:** Intermediate

**Task:** Externalize `catalog.page-size` consumed by a JPA-backed paginated repository call. Use Config Server + `@RefreshScope` on `CatalogProperties`; refresh without restart and verify new page size in SQL `LIMIT`.

**Solution:**

```java
@Component
@RefreshScope
@ConfigurationProperties(prefix = "catalog")
class CatalogProperties {
    private int pageSize = 20;
    // getter/setter
}

@Service
class CatalogService {
    Page<Product> list(Pageable ignored) {
        return productRepo.findAll(PageRequest.of(0, props.getPageSize()));
    }
}
```

```bash
curl -X POST http://localhost:8080/actuator/refresh
# verify smaller page-size changes rows returned
```

**Senior takeaway:** Pagination defaults belong in config, not hardcoded `@PageableDefault` only — refresh changes read patterns without redeploy.

---

## Exercise 38 — Gateway route + JWT filter protecting JPA API

**Difficulty:** Hard

**Task:** Place Spring Cloud Gateway in front of a JPA-backed `products` service. Route `/api/catalog/**` with JWT validation; unauthorized callers never hit the repository layer.

**Solution:**

```yaml
spring.cloud.gateway.routes:
  - id: catalog
    uri: lb://CATALOG
    predicates:
      - Path=/api/catalog/**
    filters:
      - TokenRelay=
spring.security.oauth2.resourceserver.jwt.issuer-uri: ${KEYCLOAK_ISSUER}
```

```java
// catalog-service — resource server still validates JWT
@RestController
@RequestMapping("/products")
class ProductController {
    @GetMapping
    Page<ProductDto> list(@AuthenticationPrincipal Jwt jwt, Pageable pageable) {
        return catalogService.listForTenant(jwt.getClaim("tenant_id"), pageable);
    }
}
```

**Senior takeaway:** Gateway JWT filter is the first line; JPA queries still scope by tenant from token claims — defense in depth.

---

## Weekend drill

1. Disable OSIV in a sample app; fix every `LazyInitializationException` with DTOs or fetch joins.
2. Add `@Version` to a REST resource and wire `If-Match` / 412 responses.
3. Run `EXPLAIN ANALYZE` on the worst Hibernate-generated query from your SQL logs.
4. Add a CI step that fails if any integration test exceeds 10 SQL statements per HTTP call.
