# ReactJS + TypeScript — 58 Senior Interview Questions

**Bar:** 8–15 year fullstack JDs expect you to read/write React+TS, not be a pixel-perfect designer. Hooks, state, performance, types, and how the UI talks to Java APIs.

---

### 1. What is React's rendering model?

**Short answer:** React renders UI as a function of state and props, reconciling a virtual tree against the DOM. When state changes, React schedules an update, walks the component tree, and computes a minimal set of DOM mutations. Rendering is declarative: you describe what the UI should look like for a given snapshot, not how to imperatively patch the DOM. In a Spring-backed SPA, each screen typically maps to components that consume REST DTOs shaped like your Java records. Understanding this model is the foundation for debugging stale UI, unnecessary re-renders, and effect timing issues.

#### What it is
React's rendering model separates the component tree (your JavaScript functions) from the host tree (browser DOM or native views). On each update, React calls your components to produce React elements—lightweight descriptions of UI. The reconciler compares the new element tree with the previous one (diffing) and commits only the changed host nodes. Props flow down; events bubble up through callbacks you pass as props. For a Java fullstack team, think of components as view-layer adapters over your API contracts, similar to how Thymeleaf templates bind to Spring MVC models.

#### How it works (internals)
A parent re-render triggers child re-renders unless React can bail out early (memo, same props). useState and useReducer schedule updates; React batches them and re-runs affected components during the render phase. The commit phase applies DOM updates and runs layout effects. Strict Mode double-invokes renders in development to surface impure side effects. When integrating with Spring, fetch DTOs in a parent or data hook, pass immutable snapshots to children, and let React reconcile list rows keyed by entity id. Profiler and React DevTools show which components rendered and why.

#### When to use / when NOT to use
Interviewers probe this when candidates confuse rendering with network I/O or DOM events. You need the model when optimizing dashboards fed by paginated Spring endpoints. It matters when debugging why a child shows old data after a PUT returns 200. Senior hires should explain render vs commit vs passive effects without hand-waving. It also frames answers about Fiber, Suspense, and concurrent rendering.

#### Production example
In production SPAs calling Spring Boot REST APIs, we map OrderSummaryDto to <OrderSummary order={dto} /> and keep DTOs immutable after fetch. List screens key rows by orderId from the backend, not array index, so partial refreshes after PATCH /orders/{id} reconcile correctly. We avoid mutating fetched objects in place because React's shallow compare won't detect deep field changes on nested line items. Error and loading states are explicit render branches, not side effects stuffed into render. When Problem Details return validation errors, we lift field errors into form state and re-render controlled inputs. This keeps the UI consistent with server truth after every successful mutation.

#### Common mistakes
- Treating fetch or localStorage writes inside render as acceptable patterns.
- Mutating props or state objects instead of replacing with new references.
- Assuming a child won't re-render because 'only the parent changed'.
- Confusing React re-render with full page reload or browser repaint of unrelated nodes.
- Using array index as key when Spring returns stable UUID primary keys.

#### Interview follow-ups (with model answers)

**Q:** What is the difference between React element, component instance, and DOM node?
**A:** A React element is a plain object describing a type and props—cheap to create on every render. A component is the function or class that returns elements; React does not keep long-lived 'instances' for function components the way class components did. The DOM node is the actual browser element created in the commit phase when React mounts or updates host components. In a Spring SPA, your OrderList function runs on each render and produces elements; only changed text nodes or attributes hit the DOM. Confusing elements with DOM nodes leads juniors to fear re-renders as expensive full-page repaints. Senior answer: render produces a description; commit materializes it.

**Q:** Why can two setState calls in one event handler produce one render?
**A:** React 18 batches state updates inside event handlers, promises, and native hooks so multiple setState calls collapse into one render pass. This avoids inconsistent intermediate UI when updating quantity and subtotal after a cart PATCH. Outside React's batching (legacy patterns, some third-party stores), you might see double renders. flushSync forces synchronous commit when integrating with non-React widgets. For Spring-backed forms, batch field updates before submit so validation messages don't flicker. Knowing batching explains why reading state immediately after setState still shows the old value.

#### Scenario probe
**Situation:** After a successful PUT /api/orders/42 from your Spring service, the order header updates but line items still show the old quantity. The developer says 'React didn't re-render'.

**Model answer:** I'd verify whether state actually changed with a reference the reconciler can detect. If they merged the PUT response into the existing order object with order.lines[0].qty = 3, React's useState setter might receive the same object reference and skip scheduling an update, or child memo might bail out incorrectly. The fix is to replace state: setOrder({ ...response }) or map lines to new objects. I'd also check keys on the line-item list—index keys after reorder cause wrong row reuse. In DevTools, confirm OrderDetail rendered and whether props to LineItem changed. On the Java side, ensure the PUT returns the full updated OrderDto, not 204 No Content, unless the client merges optimistically. This is a render-model issue, not Spring failing.

---

### 2. Fiber and concurrent features (React 18+).

**Short answer:** Fiber is React's reconciler architecture: each component instance is a fiber node in a linked tree React can pause, resume, and prioritize. Concurrent features (startTransition, useDeferredValue, Suspense) let React interrupt low-priority work to keep input responsive. Time-slicing breaks render work into chunks so long lists from /api/products don't freeze the main thread. Strictly speaking, concurrent rendering is a scheduling strategy, not parallelism across threads. For Java teams shipping admin UIs over heavy Spring aggregations, Fiber explains why deferring filter updates feels smoother than blocking renders.

#### What it is
Before Fiber, React reconciled synchronously in one pass. Fiber models each unit of work as a node with alternate and child pointers, enabling incremental rendering. Lanes and priorities classify updates: user typing is urgent; background search results can wait. Suspense integrates with this scheduler to throw promises during render and resume when data resolves. Understanding Fiber clarifies why startTransition doesn't make network faster—it deprioritizes the expensive re-filter of 10k rows.

#### How it works (internals)
When you wrap setSearchResults in startTransition, React marks the resulting update as transition priority. If the user types again, the in-flight transition can be discarded and a new one started. useDeferredValue lags behind a fast-changing value so the UI shows stale-but-responsive input while deferred child trees catch up. Suspense boundaries catch thrown promises from lazy() or data routers and show fallbacks until children resolve. With Spring, pair deferred search with server-side pagination rather than client-filtering huge DTO arrays.

#### When to use / when NOT to use
Discuss Fiber when optimizing search-as-you-type against GET /api/orders?q=. Interviewers want to hear you won't put every keystroke on the critical path. Also relevant for code-split route transitions and skeleton UIs while JWT refresh runs. Skip deep Fiber internals unless asked—focus on user-visible concurrent APIs.

#### Production example
Our operations dashboard debounces Spring calls but still renders 500-row tables client-side for offline sort. We wrap the filtered view in startTransition so checkbox toggles on facets stay instant while the table re-renders. Route-level React.lazy boundaries show skeletons during chunk load; Suspense wraps the outlet. We don't enable experimental concurrent features on financial confirm modals—those stay synchronous to avoid double-submit ambiguity. Backend still owns authoritative totals; concurrent UI never commits optimistic ledger numbers without server ack.

#### Common mistakes
- Believing startTransition speeds up Spring API latency.
- Using useDeferredValue without measuring—sometimes debounce + server pagination is simpler.
- Wrapping every setState in startTransition, masking real performance bugs.
- Assuming Suspense replaces error boundaries for 401/500 from JWT-protected endpoints.
- Client-filtering massive lists because Fiber 'handles it'.

#### Interview follow-ups (with model answers)

**Q:** What happens to an in-flight transition when state updates again?
**A:** React can discard stale transition work when a higher-priority update arrives—typically user input. The deferred tree never commits outdated filter results if the user changed the query. This prevents showing order search results for 'foo' after they typed 'food'. Network requests need separate abort logic; Fiber doesn't cancel fetch. Use AbortController on GET /api/orders and ignore responses whose query doesn't match current input. Senior teams coordinate transition priority with request cancellation for consistent UX.

**Q:** How does Suspense differ from a loading boolean?
**A:** A loading flag is manual state you set before fetch and clear after—easy to forget on error paths. Suspense declaratively wraps children that suspend (lazy components, future data APIs) and shows fallback until resolved. Multiple suspending children can coordinate through nested boundaries. With Spring data, many teams still use TanStack Query isPending alongside route Suspense for chunks only. Suspense doesn't replace handling Problem Details—wrap error boundaries outside Suspense for 422 responses.

#### Scenario probe
**Situation:** Users report the order search box stutters when results return from Spring. The team added useMemo but latency persists during typing.

**Model answer:** Stutter usually means render work on the critical input path, not just missing memo. I'd profile: if each keystroke synchronously filters 5k OrderDto rows, Fiber won't help until we deprioritize that work with startTransition or push filtering to GET /api/orders?query= with debounce. useDeferredValue on the query string keeps the input snappy while the table catches up. Ensure list virtualization so commit phase doesn't touch hundreds of DOM nodes. Separate network race handling with AbortController so late responses don't trigger extra renders. Java side: add indexed search and page size limits. Concurrent React improves scheduling; it doesn't replace backend pagination.

---

### 3. `useState` vs `useReducer` vs external store.

**Short answer:** useState is ideal for independent, simple values like modal open flags or a single form field. useReducer centralizes transitions on an action dispatch model—excellent when next state depends on previous state with multiple branches. External stores (Zustand, Redux, TanStack Query cache) suit shared or server-derived state accessed outside the React tree. Pick based on update shape, colocation, and whether non-React code must read the data. Spring JWT claims and order workflow status often land in a reducer or store, not scattered useState calls.

#### What it is
useState returns a value and setter; updates are replaced via functional updaters when deriving from prior state. useReducer exposes state and dispatch; the reducer is a pure function (state, action) => newState, familiar to Java engineers from event sourcing lite. External stores subscribe components via useSyncExternalStore or library hooks, decoupling state from the component hierarchy. Server cache libraries treat GET responses as state with invalidation policies—different from UI toggles. The choice affects testability and how you replay user flows in RTL tests.

#### How it works (internals)
Start with useState until update logic sprawls across handlers—then extract useReducer. Define action types as discriminated unions: { type: 'SUBMIT_SUCCESS'; payload: OrderDto }. For cross-route cart state, a Zustand slice with persist middleware beats prop drilling through layout routes. TanStack Query holds GET /api/orders/{id} with staleTime; local useState holds draft edits until PATCH. Never duplicate the same entity in two sources without a clear owner—server cache wins after mutation invalidation.

#### When to use / when NOT to use
useReducer shines for multi-step wizards mirroring Spring state machine endpoints. External store when header cart count and checkout page must stay in sync. useState for ephemeral UI: tooltip, accordion, inline edit mode. Interview signal: candidate names tradeoffs, not 'always Redux'.

#### Production example
Checkout uses useReducer for { step, shipping, payment, errors } with actions mapped from Problem Details field errors on 422. Product catalog uses TanStack Query with queryKey ['products', filters] backed by Spring Page<OrderSummaryDto>. Auth tokens live in memory + httpOnly refresh pattern; Zustand holds display name from JWT claims parse, not the raw token. Draft order notes use local useState until explicit save POST. Reducer tests are pure functions—easy CI without jsdom.

#### Common mistakes
- Redux for a single boolean modal flag.
- Storing entire Spring Page in useState without pagination strategy.
- Duplicating order entity in Context and React Query cache with divergent copies.
- Dispatching reducer actions from useEffect without understanding ordering vs render.
- Putting JWT refresh logic inside useReducer instead of an auth module.

#### Interview follow-ups (with model answers)

**Q:** When would you lift useReducer into a custom hook?
**A:** When multiple components need the same state machine—useOrderWorkflow encapsulates reducer, dispatch, and selectors. The hook can accept initialOrderId, wire TanStack Query prefetch, and expose imperative methods like submitForApproval(). Tests import the hook via renderHook and dispatch actions without mounting a full page. Keep the reducer in a separate file for Java-minded reviewers who want pure functions. Don't hide side effects inside the reducer—only compute next state; effects stay in the hook.

**Q:** How does TanStack Query differ from useState for API data?
**A:** Query cache handles deduplication, background refetch, stale-while-revalidate, and invalidation after mutations—useState is manual. Calling GET /api/orders in useEffect + useState repeats boilerplate and race bugs Query solves. Still use useState for optimistic draft fields not yet on server. queryKey ties to Spring resource identity; mutation onSuccess invalidates ['orders', id]. Senior answer: server state in Query, client UI state in useState/reducer.

#### Scenario probe
**Situation:** A checkout page has twelve useState hooks and bugs when applying a coupon code updates total but not tax.

**Model answer:** Interdependent fields are a smell for useReducer or a small computed selector layer. I'd model CheckoutState with lines, coupon, taxRate from Spring config endpoint, and derive total in one place—either reducer on APPLY_COUPON or useMemo from normalized state. If tax comes from POST /api/tax/estimate, trigger that in an effect keyed on [lines, coupon], not scattered setters. Problem Details on invalid coupon map to errors.coupon in state. Long term, TanStack Query for server quotes plus reducer for wizard step prevents inconsistent snapshots. Java parallel: replace primitive obsession with a cohesive DTO and single service method calculateTotals().

---

### 4. Stale closures.

**Short answer:** A stale closure captures variables from an older render cycle; async callbacks and effects often close over outdated state or props. Classic symptom: setInterval or debounced search still filters on the initial query string. Functional updaters setCount(c => c + 1) and ref mirrors (useRef for latest value) break the stale read. Effects must list dependencies so the closure refreshes when JWT expiry or orderId changes. Java seniors recognize this as capturing an old variable in a lambda passed to ExecutorService—same bug, different runtime.

#### What it is
Each render creates new function identities with lexical bindings to that render's props and state. A handler registered once in useEffect(() => { window.addEventListener(...) }, []) sees frozen values from mount. Closures aren't wrong—they're how JavaScript works; React's hook model makes the timing visible. eslint-plugin-react-hooks flags missing deps but can't catch ref staleness misuse. Understanding closures separates mid from senior frontend debugging.

#### How it works (internals)
Prefer functional state updates when the new value depends on the previous: setItems(prev => [...prev, item]). Store volatile values needed in stable callbacks inside useRef updated each render: ref.current = orderId. For subscriptions, re-bind when deps change or use the event pattern from useEffect cleanup. With Spring polling, include token and resource id in effect deps or abort when they change. useCallback deps must list every closed-over value that can change.

#### When to use / when NOT to use
Every interview loop question on broken useEffect or 'works once then fails'. Audit custom hooks exporting memoized callbacks for hidden stale captures. Critical for auth refresh timers closing over an expired access token.

#### Production example
Our auto-save debounce closed over draftVersion; concurrent edits sent stale If-Match headers to Spring. Fix: ref for latest version, functional merge on save response. WebSocket order status handler now reads connectionParams from ref updated when JWT rotates. Code review checklist: empty deps + external variable = explain in comment or fix. Integration tests simulate rapid filter changes to catch stale fetch responses.

#### Common mistakes
- eslint-disable react-hooks/exhaustive-deps without documenting why.
- Using useCallback(fn, []) while fn reads props.orderId.
- Assuming useRef initialization fixes staleness without assigning ref.current each render.
- setInterval cleanup missing, interval runs with mount-time closure forever.
- Ignoring stale closure when implementing optimistic rollback on 409 Conflict.

#### Interview follow-ups (with model answers)

**Q:** Why does setCount(count + 1) fail in rapid clicks?
**A:** Each handler closes over the same count from that render; batched clicks read the same snapshot before re-render. setCount(c => c + 1) queues updaters that receive the latest pending state. Same issue when incrementing line quantity twice before Spring PATCH returns—use functional updates or merge server etag. For Java devs: like AtomicInteger.updateAndGet vs reading a local int twice. In async handlers after await fetch, always use functional update or ref for counters touched post-await.

**Q:** How do refs help without causing re-renders?
**A:** useRef holds a mutable box; updating ref.current doesn't schedule render. Pattern: keep latest orderId in ref for WebSocket onMessage while subscription effect deps stay stable. Don't store derived UI in ref to 'avoid re-renders'—that's premature optimization. Imperative handles (focus, scroll) are legitimate ref uses. Contrast: state triggers render when users need to see new data from Spring.

#### Scenario probe
**Situation:** A debounced search always queries the first character typed; network tab shows q=a even after user typed 'apple'.

**Model answer:** The debounce callback likely closed over query from effect mount with empty deps. Fix: include query in deps and cancel prior debounce on cleanup, or read query from ref updated each render. Better: useDeferredValue + TanStack Query with queryKey ['search', query] so cache tracks each term. Abort in-flight GET when query changes. On Spring, ensure parameter binding matches URL encoding. I'd demonstrate in DevTools by logging closure values inside the timeout. This is textbook stale closure—not a backend bug.

---

### 5. `useEffect` mental model.

**Short answer:** useEffect runs after paint (layout effects excepted) to synchronize React state with external systems: DOM APIs, subscriptions, non-React widgets. It is not a lifecycle replacement for 'on mount fetch'—that's a common abuse when a data library fits better. The mental model: render computes UI; effects bridge to the outside world. Cleanup functions undo subscriptions to prevent leaks when orderId route param changes. Spring integrations belong here for one-off DOM integrations, not as default data layer.

#### What it is
useEffect(setup, deps) schedules setup after commit when deps changed since last run. Cleanup runs before next setup and on unmount—symmetric teardown like try/finally. Effects are async-friendly but don't await React; race handling is your job. Strict Mode remounts in dev to surface missing cleanup. Distinguish event handlers (user gesture → action) from effects (display changed → sync external).

#### How it works (internals)
Ask: could this run in an event handler? If user clicked Save, use onClick not useEffect. For document.title from route, effect is appropriate. Fetch on mount: prefer TanStack Query useQuery(['order', id], () => api.getOrder(id)). If stuck with useEffect fetch, guard with ignore flag or AbortController; set state only if !aborted. Map Spring 401 to auth logout in a global interceptor, not per-component effect.

#### When to use / when NOT to use
Legitimate: analytics page view, third-party chart init, syncing scroll position. Suspect: 'whenever X changes, POST to Spring' without debounce—often belongs in mutation callback. Interviewers listen for 'effects for synchronization, events for actions'.

#### Production example
We removed useEffect(() => fetchOrders(), []) from list pages in favor of useQuery with staleTime 30s aligned to Spring cache headers. Remaining effects: attach ResizeObserver to dashboard grid, subscribe to STOMP after JWT connect. Effect on [orderId] resets local draft state when navigating between orders. Never chain multiple setState in effects without deps discipline—it caused cascading PATCH loops. Problem Details parsing happens in mutation onError, not effects watching errors object.

#### Common mistakes
- useEffect without deps that fetches on every render.
- Using effect to derive state from props—use render or useMemo instead.
- Missing cleanup on intervals polling GET /api/status.
- Treating useEffect as componentDidMount only—ignoring update path.
- Fetching in effect when user action should trigger mutation.

#### Interview follow-ups (with model answers)

**Q:** What's wrong with useEffect(() => setFullName(first + last), [first, last])?
**A:** That's derived state—compute fullName during render: const fullName = `${first} ${last}`; no effect needed. Extra effect causes double render and flash risk. Same anti-pattern: syncing selectedOrderId from URL via effect instead of reading useParams() directly. Effects for derivation usually mean missing colocation. Exception: pushing to external system (localStorage) where render can't write.

**Q:** When is useLayoutEffect appropriate?
**A:** When you must measure DOM or mutate layout before browser paint to avoid flicker—tooltip position, scroll restore. Runs synchronously after DOM updates, before paint—blocks visual update. Most Spring data UIs don't need it; misuse hurts performance. Prefer CSS for layout when possible. useLayoutEffect SSR warning: server has no layout—guard with typeof window.

#### Scenario probe
**Situation:** Order detail fires duplicate GET /api/orders/5 requests on every parent re-render.

**Model answer:** Almost certainly fetch inside useEffect with missing or unstable deps—maybe [order] where order is new object reference each parent render. Stabilize with orderId string dep, or move to TanStack Query which dedupes by queryKey. If parent passes inline arrow onSave causing child remount, fix composition not effect. Check Strict Mode double mount in dev only. Spring side: ETag caching is fine; duplicate GETs are a client scheduling bug. I'd trace with React DevTools 'why did this render' and network waterfall.

---

### 6. Effect dependency arrays.

**Short answer:** The dependency array tells React when to re-run an effect: values from component scope that change between renders and are read inside the effect. Omitting the array runs every render; empty [] runs once after mount (with Strict Mode caveats). Stable primitives and referentially stable functions from useCallback belong; objects recreated each render cause excessive runs. Exhaustive-deps lint encodes this contract—disabling it requires a written invariant. For Spring fetches, deps should be resource ids and filter primitives, not entire DTO graphs.

#### What it is
React compares deps with Object.is from the previous effect run. Functions and objects compare by reference—inline {} in deps is always 'changed'. useMemo can stabilize object deps when truly needed. Custom hooks should return stable callbacks or document dep requirements. Mismatch between mental model and actual deps causes the majority of effect bugs in enterprise SPAs.

#### How it works (internals)
List every reactive value read in the effect: orderId, accessToken, pageIndex. Extract primitives from objects: order?.id not order. For debounced API calls, debounce function in useMemo with [apiBase] deps. Cleanup should handle the case when deps change mid-request—abort fetch. Align queryKey in TanStack Query with the same logical deps for consistency.

#### When to use / when NOT to use
Code review any useEffect touching JWT, WebSocket, or polling. Interview scenario: fix infinite loop from setState in effect with [data] dep. Teaching moment for Java devs: deps are like @Cacheable key expressions.

#### Production example
Audit found effects depending on filters object recreated in render—polling /api/metrics every 16ms. Fixed with useMemo filters and JSON-stable serialize for dep. Auth effect deps [tokenExpiry] schedules refresh 60s before exp claim from JWT parse. Documented exception: mount-only analytics with ref guard for double Strict Mode. CI runs eslint-plugin-react-hooks on all src.

#### Common mistakes
- Dep array [] while reading props.orderId inside.
- Including setState function in deps (unnecessary, stable).
- Depending on entire location object instead of location.pathname.
- Infinite loop: effect sets state that is also a dep without guard.
- Copy-pasting deps from another effect without reading the setup body.

#### Interview follow-ups (with model answers)

**Q:** Why does [order] cause repeated effect runs?
**A:** Parent likely passes new order object reference each render even if fields unchanged—Object.is sees change. Depend on order.id and order.version for If-Match sync. Or select stable slice from React Query data. Deep compare in deps is an anti-pattern—fix data flow. Spring immutable DTOs help if parent only replaces state on actual fetch.

**Q:** Can you omit deps intentionally?
**A:** Running every render is almost always wrong except syncing ref.current. Empty deps mean effect closure is mount snapshot—document invariant if reading refs updated elsewhere. eslint-disable-next-line needs comment: 'only subscribe once to STOMP; token read from ref'. Reviewers should reject silent disables. Prefer event-driven or query library over clever omit.

#### Scenario probe
**Situation:** useEffect logs 'subscribing' infinitely when filters state updates from a facet checkbox.

**Model answer:** Effect probably calls setFilters or triggers parent setState that changes a dep without cleanup guard. Or effect depends on filters and also POSTs which returns updated facets mutating filters reference. Separate: user toggles facet in handler; effect only subscribes to SSE with [categoryId] dep. Use functional updates to avoid reading stale filters in effect. If using Spring search POST, debounce in handler not effect loop. I'd log dep values across runs to see which reference flips.

---

### 7. Fetching in useEffect vs React Query / SWR.

**Short answer:** useEffect + fetch is manual: loading/error state, deduplication, cache, refetch on focus, and invalidation are all bespoke. TanStack Query (React Query) models server state with policies matching HTTP semantics and Spring cache-control. useEffect fits one-off imperative integrations; Query fits CRUD screens against REST resources. Query integrates mutations with optimistic updates and rolls back on Problem Details 409. Senior teams standardize on Query for API data and ban fetch-in-effect for resource reads.

#### What it is
useQuery returns { data, isPending, error, refetch } keyed by queryKey array. staleTime controls when data is fresh; gcTime retains unused cache. Mutations use useMutation with onSuccess invalidating related queries. Effect fetch lacks shared cache—navigating away and back refetches blindly. Query DevTools visualize cache aligned with microservice boundaries.

#### How it works (internals)
Define api client with axios/fetch wrapper attaching JWT Authorization header. useQuery({ queryKey: ['orders', page], queryFn: () => orderApi.list(page) }). Map Spring Page content to table; keep page in queryKey. useMutation for POST; onSuccess invalidate ['orders'] and setQueryData for detail. Global QueryClient onError handles 401 redirect to login.

#### When to use / when NOT to use
Any list/detail screen backed by Spring Data REST. useEffect fetch only for non-REST: config.json, third-party script. Interview: articulate cache invalidation after command operations.

#### Production example
Order service BFF exposes OpenAPI; frontend queryKeys mirror resource paths. staleTime 60s for catalog; 0 for checkout quote requiring fresh tax. Mutations parse application/problem+json into toast + field errors. Prefetch on hover for order row via queryClient.prefetchQuery. Removed 40+ copy-paste useEffect fetches—incident rate dropped.

#### Common mistakes
- useEffect fetch without abort on unmount.
- Not handling 304 or caching headers Query could respect.
- Storing Query data duplicated into useState on every success.
- queryKey missing filter params causing wrong cache hits.
- Ignoring enabled: !!orderId for optional route params.

#### Interview follow-ups (with model answers)

**Q:** How do you refetch when JWT is refreshed?
**A:** Attach new token to axios interceptor; failed queries with 401 queue retry after refresh promise resolves. queryClient.invalidateQueries() after auth refresh if claims changed visible data scope. Don't store token in queryKey—it busts entire cache on every refresh. Use global onUnauthorized handler. Spring opaque refresh endpoint returns new access token; Query retries in flight requests.

**Q:** When is useEffect fetch still acceptable?
**A:** Fire-and-forget analytics beacon, loading non-JSON config, integrating legacy script tags. Prototypes before Query setup—migrate before production. If data isn't server cacheable entity state. Even then, consider useQuery with staleTime: Infinity for static config. Senior default: Query unless strong reason documented.

#### Scenario probe
**Situation:** Navigating order list → detail → back list shows stale status until hard refresh.

**Model answer:** Classic missing cache invalidation or detail mutation not updating list query data. After PATCH status, call invalidateQueries(['orders']) or setQueriesData to patch list row. If list used mount-only useEffect fetch, remount doesn't refetch—stale by design. Adopt Query with staleTime and refetchOnWindowFocus for ops dashboards. Spring should return updated status in PATCH response to avoid extra GET. I'd verify queryKeys include tenant id from JWT for multi-tenant isolation.

---

### 8. Race in fetch:

**Short answer:** Fetch races occur when slower responses arrive after faster ones and overwrite newer UI state. Common with rapid filter changes or tab switching on slow Spring queries. Fix with AbortController, request sequence tokens, or ignoring stale responses. TanStack Query cancels in-flight queries when queryKey changes if queryFn uses signal. Java parallel: compare If-None-Match or request id header server-side for idempotent reads.

#### What it is
Two GETs for q=a and q=ab both in flight; if a returns last, UI shows wrong results. setState doesn't order async completions—last write wins regardless of intent. Unmount without abort wastes bandwidth and may setState on unmounted component (React 18 warns less but still wrong). Race bugs are intermittent—hard to reproduce without throttled network.

#### How it works (internals)
Pass AbortSignal from effect cleanup: fetch(url, { signal }). Increment requestId per search; only apply if response.requestId === latest. React Query: queryFn({ signal }) => api.search(q, { signal }). For mutations, disable submit while pending; use idempotency-key header on Spring POST. Debounce reduces races but doesn't eliminate them.

#### When to use / when NOT to use
Every autocomplete against GET /api/customers. Tab panels each fetching detail—only active tab's result should commit. Optimistic UI must reconcile with latest server version on 409.

#### Production example
Customer search uses Query with 300ms debounce and abort—no more wrong customer selected. Order timeline tab keeps ref latestOrderId; stale responses discarded in interceptor. Spring added X-Request-Seq echo for audit; client logs mismatches. Load tests with Chrome slow 3G caught races before release.

#### Common mistakes
- Boolean isLoading only—doesn't prevent stale overwrite.
- Forgetting abort on route change unmount.
- Assuming debounce alone fixes tab-switch races.
- Parallel POST creates duplicate orders without idempotency key.
- Ignoring race in optimistic rollback path.

#### Interview follow-ups (with model answers)

**Q:** How does React Query handle cancellation?
**A:** When queryKey changes or query unmounts, Query aborts prior queryFn signal. Your api layer must wire signal to fetch abort. Cancelled queries don't call onError if configured ignore. Ensures only latest search term wins. Mutations aren't auto-cancelled—use mutationKey or disable double submit.

**Q:** Server-side help for races?
**A:** ETag on GET for conditional fetch; short cache on search endpoints. Cursor pagination instead of offset when data mutates during browse. Idempotency-Key on POST /orders from mobile flaky networks. Problem Details 409 when version mismatch on PUT. Client still owns ignoring stale responses—server can't fix wrong UI state alone.

#### Scenario probe
**Situation:** Fast typists see flickering wrong order search results from Spring.

**Model answer:** Implement abort or sequence guard immediately; debounce alone insufficient. Migrate to TanStack Query with signal in queryFn; verify network tab shows cancelled requests. Log applied query term vs response term in dev. Spring: ensure search is deterministic and indexed—slow queries widen race window. Consider server-side minimum query length. RTL test: rapid userEvent.type with mocked delayed responses asserting final DOM matches last term.

#### Code / config (when useful)
```ts
useEffect(() => {
  let cancelled = false;
  fetch(`/api/users/${id}`).then(r => r.json()).then(u => { if (!cancelled) setUser(u); });
  return () => { cancelled = true; };
}, [id]);
```

---

### 9. Keys in lists.

**Short answer:** Keys tell React which list items match across renders—identity for reconciliation, not just DOM id attribute. Stable unique keys from Spring primary keys (orderId, lineId) preserve component state and focus. Index keys break when sorting, filtering, or inserting rows—wrong row keeps edited state. Keys must be unique among siblings; duplicates cause undefined behavior. Never generate keys with Math.random() on each render.

#### What it is
When key changes, React unmounts old fiber and mounts new—state resets. Same key with moved position reuses instance—state travels with item (sometimes desired, often not). Key is not passed as prop unless you spread specially—use item.id directly. Fragment lists need keys on Fragment: <Fragment key={id}>.

#### How it works (internals)
Map orders with key={order.id} from UUID returned by JPA entity. If id is temporary client-only before POST, use crypto.randomUUID() once at creation, not per render. For two lists of same entity type in one parent, keys still unique globally among all siblings in that array. Combining id + type when mixing entity kinds in one list.

#### When to use / when NOT to use
Any Spring Data Page rendered as table rows. Drag-and-drop reorder lists. Accordion of shipment legs each with inline edit.

#### Production example
Bug: index keys on order lines caused edited quantity on line 2 to jump after sort by SKU. Fixed with line.id from backend. New draft lines get clientLineKey until POST returns persisted id—state merge on success. Virtualized lists pass key to row renderer from data id. QA checklist includes reorder scenario.

#### Common mistakes
- key={index} on mutable sorted lists.
- key={item.name} when names duplicate.
- Random key forcing full remount every render.
- Using key to force reset instead of controlled reset via prop/version.
- Duplicate keys after merge from two API calls.

#### Interview follow-ups (with model answers)

**Q:** When is index key acceptable?
**A:** Static never-reordered list with no item state—rare in enterprise apps. Even then, stable id is safer if Spring adds rows later. If list is read-only labels from enum, index might suffice. Interview answer: default to entity id; justify index exceptions. Virtualizer still wants stable keys for measurement cache.

**Q:** How to reset child state when orderId route changes?
**A:** key={orderId} on detail subtree forces remount—simple but loses scroll. Prefer explicit useEffect reset or React Query key change swapping data. key on route outlet is common pattern for master-detail. Balance remount cost vs bug risk. Don't key entire app on user—use auth boundary instead.

#### Scenario probe
**Situation:** Editing quantity on one order line updates a different line after applying sort.

**Model answer:** Classic index key bug during reorder. Switch to lineItem.id from OrderLineDto; verify backend always sends id for persisted lines. For new lines, assign stable temp id in reducer on ADD_LINE. Check sort doesn't mutate array in place without new references confusing memo. Spring should not reuse ids across orders. Reproduce with sort toggle while input focused—wrong row confirms key issue.

---

### 10. Controlled vs uncontrolled inputs.

**Short answer:** Controlled inputs: React state owns value via value + onChange—single source of truth for forms posting to Spring. Uncontrolled: DOM holds value; read via ref on submit—less boilerplate, harder live validation. React recommends controlled for dynamic validation against Bean Validation mirrors. File inputs are effectively uncontrolled. Hybrid defaultValue + key reset is an escape hatch, not default pattern.

#### What it is
Controlled ties input to useState or react-hook-form field state. Each keystroke re-renders unless optimized with RHF uncontrolled registration. Uncontrolled uses name and ref; FormData maps to MultiValueMap for Spring @ModelAttribute. Checkbox controlled needs checked not value. Select multiple and custom components need explicit value plumbing.

#### How it works (internals)
For small forms: useState per field or one object state with handlers. Production: React Hook Form + Zod schema matching OpenAPI constraints. Map Problem Details errors to setError('field', { message }). Read-only display from GET; switch to controlled on Edit click. defaultValue only for uncontrolled initial paint.

#### When to use / when NOT to use
Controlled when showing inline errors from 422 validation. Uncontrolled rare—native form post without SPA routing. Interview: discuss RHF performance on large order entry grids.

#### Production example
Checkout uses RHF controlled mode for payment fields with Zod maxLength matching @Size on Java DTO. Search box is controlled debounced to Query. Admin bulk edit uses uncontrolled pattern only inside shadow DOM legacy widget. Accessibility: label htmlFor tied to id from useId().

#### Common mistakes
- value={x} without onChange—read-only warning.
- Mixing defaultValue and value on same input.
- Controlled number input returning string without parse.
- Forgetting checked on checkbox controlled binding.
- Resetting form by changing key instead of reset() wiping errors.

#### Interview follow-ups (with model answers)

**Q:** How does React Hook Form reduce re-renders?
**A:** Registers fields via ref subscribing to native input—validation runs without parent state per keystroke. Controller wraps custom MUI components for controlled third-party inputs. Still integrates Zod resolver for schema parity with Spring. watch() triggers re-render only on watched fields. Senior teams align RHF defaultValues with GET DTO on edit forms.

**Q:** Map Spring @Valid errors to fields?
**A:** Problem Details extension fieldErrors: [{ path: 'shipping.zip', message }]. Loop setError(path, { type: 'server', message }). Path convention must match RHF name attributes—agree contract in OpenAPI. Global errors on root or toast for non-field failures. Clear server errors on field change to avoid stale red borders.

#### Scenario probe
**Situation:** Edit order form shows saved data but Submit sends empty strings to PUT /api/orders.

**Model answer:** Likely uncontrolled inputs without ref read, or controlled state never initialized from GET response. On load success, reset(dto) in RHF or setState from mapOrderToForm. Verify name attributes match JSON payload keys expected by Jackson. Check disabled fields excluded from submit logic. Network tab: inspect PUT body vs form UI. Add integration test filling form from fixture DTO and asserting request body.

---

### 11. `useMemo` / `useCallback` — when they help.

**Short answer:** useMemo caches expensive computation results between renders when deps unchanged. useCallback caches function identity—useful when passing callbacks to memoized children. Neither prevents re-renders by themselves; they reduce work or stabilize references. Over-memoization adds complexity without measurable gain on typical Spring DTO transforms. Profile before memoizing; React Compiler may auto-memo in future.

#### What it is
useMemo(() => compute(), [deps]) returns memoized value; skips compute if deps same. useCallback(fn, deps) is useMemo for functions. Child React.memo compares props shallowly—stable onSave reference avoids child re-render. Deriving filtered orders from props rarely needs useMemo unless filter is O(n²) on large pages. Java analogy: memoization like @Cacheable on pure service method—key must be correct.

#### How it works (internals)
Memoize: heavy sort of 10k rows, parsed JWT claims object, chart data transformation. useCallback for handlers passed to memo(OrderRow) when parent re-renders often. Don't wrap every handler—measure with Profiler. Deps must include every closed-over changing value. Prefer moving computation to server or Web Worker for truly heavy aggregates from Spring reports.

#### When to use / when NOT to use
Profiler shows child re-rendering costly pure component. Custom comparison in memo needs stable callback deps. Not for simple string concat or mapping 20-row tables.

#### Production example
Memoized orderLineTotals only after profiling showed 40ms filter on client Page of 500 items—then we added server-side filter. useCallback onRowSelect stable for virtualized grid. Removed blanket useCallback in codebase during lint cleanup. JWT permission set parsed once per token change via useMemo. Document when memo is intentional in PR description.

#### Common mistakes
- useCallback with wrong deps causing stale handlers.
- useMemo returning new object literal inside anyway.
- Memoizing to fix bugs that are actually key or state bugs.
- React.memo on every component—comparison cost adds up.
- Empty deps on useCallback reading props.

#### Interview follow-ups (with model answers)

**Q:** Does useMemo guarantee no re-computation?
**A:** Only between renders with same deps; React may discard cache anytime. Don't use useMemo for side effects—only pure derivation. Strict Mode double render may compute twice in dev. For correctness-critical totals, trust Spring recalculation on submit not client memo alone. Treat as performance hint, not semantic guarantee.

**Q:** When is inline arrow in JSX fine?
**A:** When child isn't memoized or render cost is negligible—most buttons. Premature useCallback everywhere hurts readability. List of 500 memo rows with inline onClick each render defeats memo—stabilize or remove memo. Event delegation patterns rare in React—stabilize callback or pass id. Pragmatic senior: memo at measured hotspots only.

#### Scenario probe
**Situation:** Team added useMemo everywhere; bundle size and complexity grew; performance unchanged.

**Model answer:** I'd run React Profiler on realistic order list with Spring data volume. Likely bottleneck is unvirtualized DOM or fetch, not missing memo. Remove speculative useMemo; keep only proven wins like expensive chart transform. Push filtering to GET query params. Educate that useMemo doesn't block parent re-render—child still renders if parent does. Establish team rule: memo requires Profiler screenshot in PR.

---

### 12. `React.memo` and why it fails.

**Short answer:** React.memo wraps a component to skip re-render if props are shallow-equal to previous. Pairs with useCallback/useMemo for reference stability. Custom arePropsEqual can compare deep fields on order DTO when parent recreates wrapper object. Memo is pointless if parent always passes new object props. Use on hot paths: virtualized rows, heavy chart leaves.

#### What it is
memo(Component) returns wrapped component with same API. Default comparator checks each prop with Object.is/shallow equality. Function components don't have shouldComponentUpdate—memo provides it. Context changes still re-render memo children if they consume context. displayName helps DevTools identify memo wrappers.

#### How it works (internals)
Export const OrderRow = memo(function OrderRow({ order, onSelect }) { ... }). Pass order id + primitives if full DTO reference unstable from Query. Custom compare: prev.order.version === next.order.version for read-only rows. Don't memo layout shells that always change with route. Combine with virtualization library row renderer memo.

#### When to use / when NOT to use
Virtualized list row rendering 10k Spring records. Chart leaf receiving same data reference from parent dashboard polling. Skip memo on infrequently rendered admin forms.

#### Production example
OrderRow memo cut render time 60% in profiler for 200 visible virtual rows. Parent passes onSelect wrapped in useCallback keyed by handler logic not order. Removed memo from FormField—always re-renders on any form change anyway. Context split: ThemeContext vs OrderContext so rows don't subscribe to theme churn.

#### Common mistakes
- memo child consuming Context that updates every parent render.
- Passing style={{ width: 100 }} new object each render.
- Deep compare in arePropsEqual more expensive than re-render.
- Memo export default anonymous losing DevTools name.
- Expecting memo to fix fetch-in-render anti-pattern.

#### Interview follow-ups (with model answers)

**Q:** memo vs useMemo for a child component?
**A:** memo prevents entire component re-execution when props equal. useMemo inside parent returns cached element or value—different layer. Rare pattern: useMemo(() => <Expensive />, [deps])—memo on component cleaner. Choose memo for reusable exported components. Both need stable props to matter.

**Q:** Does memo help with React 19 Compiler?
**A:** Compiler auto-inserts memoization where proven safe—manual memo may become redundant. Until adopted, explicit memo still valid on measured paths. Don't remove memo preemptively without Compiler enabled in build. Teams on Vite SPA may wait before dropping patterns. Watch React release notes for migration guidance.

#### Scenario probe
**Situation:** Memoized OrderRow still re-renders on every parent tick from global clock context.

**Model answer:** Memo doesn't block context updates—OrderRow likely useContext(ClockContext). Split contexts: move clock to layout only or pass formatted time as prop to header not rows. Alternatively select minimal context slice with use-context-selector library. Verify with why-did-you-render which prop/context changed. Architecture fix beats more memo layers. Spring data unchanged—this is React composition issue.

---

### 13. Context pitfalls.

**Short answer:** Context propagates values without prop drilling but causes all consumers to re-render when value reference changes. Split contexts by update frequency: AuthContext vs ThemeContext. Memoize context value object or pass state and dispatch separately to limit churn. Context is poor man's global store—not a replacement for server cache. JWT user profile in context is fine; entire order catalog is not.

#### What it is
Provider value={{ user, setUser }} new object each render re-renders all consumers. useContext subscribes component to provider updates—no selector by default. Multiple providers nest; order matters for override. Default context undefined requires guard or default value. Performance pitfall #1 in large enterprise trees.

#### How it works (internals)
Split: AuthProvider (rare updates), LocaleProvider, FeatureFlagsProvider. useMemo value from [user, token] not entire app state. Dispatch-only context can hold stable setState from useState. For frequent data use Zustand or TanStack Query not Context. Test consumer count with React DevTools highlight updates.

#### When to use / when NOT to use
Theme, auth display name, i18n locale—low churn. Avoid order list data unless read-only snapshot refreshed rarely. Interview: explain re-render mechanism not just API.

#### Production example
Merged User+Cart context caused full app flash on add-to-cart. Cart moved to Zustand; AuthContext holds { user, roles } from JWT parse only. Feature flags from Spring /api/config fetched once, context value memoized. RBAC checks use roles array in context; fine-grained perms fetched per route via Query.

#### Common mistakes
- Single AppContext with everything.
- Creating new callbacks in provider value each render.
- Storing TanStack Query cache duplicate in context.
- Using context for form state on multi-field wizard.
- Not memoizing provider children when only value changed.

#### Interview follow-ups (with model answers)

**Q:** Context vs Zustand for auth?
**A:** Auth rarely changes—Context works with memoized value. Zustand better if many selectors, devtools, persist middleware for non-sensitive prefs. Never persist access token in localStorage via either—httpOnly refresh pattern. JWT claims for display ok in memory store. Logout clears both Query cache and auth store.

**Q:** How to avoid provider hell?
**A:** Compose providers in AppProviders.tsx single file. Order: QueryClient, Auth, Router, Theme. Don't nest 15 providers—consolidate related concerns. Some libraries offer single provider wrapper. Code split providers only needed for admin routes.

#### Scenario probe
**Situation:** Adding one item to cart re-renders entire order management module.

**Model answer:** Cart state likely in broad Context consumed by layout ancestors. Move cart to colocated Zustand with selector useCartCount in header only. Order module subscribes to Query keys not cart context. Audit useContext calls—remove unnecessary subscriptions. Profiler confirm render cascade. Spring cart API unchanged; fix React state architecture.

---

### 14. Lifting state vs composition.

**Short answer:** Lifting state moves shared state to common ancestor—simple but can bloat parent and cause wide re-renders. Composition passes JSX children or render props to avoid owning state unnecessarily. Prefer colocation: keep state closest to where it's used. Container/presentational split maps well to Spring service + dumb view components. Senior design favors composition (slots, children) over prop drilling ten levels.

#### What it is
Lift when two siblings need same draft filter state. Composition: <Modal><OrderForm /></Modal> modal doesn't own form state. Compound components share implicit context internally—Tabs, Accordion patterns. Inversion: parent supplies renderItem callback; child owns list scroll state. Aligns with 'prefer configuration over inheritance' from Java design.

#### How it works (internals)
Start with state in leaf; lift only when sibling sync required. Extract custom hook before lifting to parent. Use URL search params for shareable filter state instead of root state. React Query shares server state without lifting fetch to App. children prop for layout slots in shell around Spring-driven pages.

#### When to use / when NOT to use
Master-detail selection: lift selectedId or use URL /orders/:id. Wizard steps might use reducer at route level not App root. Interview scenario: refactor God component OrderPage.

#### Production example
Order filters moved from App to route loader + URL sync—shareable links for support. Modal composition: trigger in row, portal renders Form without lifting modal open state to table. useOrderFilters hook colocates filter state + Query integration. Reduced App.tsx from 800 to 120 lines.

#### Common mistakes
- Lifting all form state to page when sections independent.
- Prop drilling 8 levels instead of hook or context slice.
- Composition overuse creating unreadable render prop nesting.
- Duplicating lifted state and URL params out of sync.
- Global event bus instead of React patterns.

#### Interview follow-ups (with model answers)

**Q:** URL state vs lifted React state?
**A:** URL enables deep links, refresh survival, back button—ideal for list filters on GET APIs. React state for ephemeral UI: open accordion, hover. useSearchParams sync with Spring query params naming. Validate URL params with Zod before fetch. Senior default: server-backed filters in URL.

**Q:** Compound component example for orders?
**A:** <OrderCard><OrderCard.Header /><OrderCard.Lines /></OrderCard> with internal context for order dto. Consumer doesn't pass order to each subpart. Encapsulates layout; parent passes single order prop to root. Matches design system patterns in MUI. Test subparts via context provider in RTL.

#### Scenario probe
**Situation:** OrderPage has 30 props passed through Layout to deep child LineActions.

**Model answer:** Refactor: LineActions uses useParams orderId + useQuery for order slice it needs. Or OrderActionsContext scoped to OrderDetail subtree only. Extract useOrderActions hook colocated with API module. Composition: render actions slot from parent with closure over order. Eliminate Layout as prop tunnel. Java parallel: don't pass entire AggregatedRoot through every helper—fetch scope locally.

---

### 15. Controlled components from a Java API.

**Short answer:** Controlled components from Java API means UI state mirrors Spring DTO fields with explicit sync on load and submit. GET returns OrderEditDto; form reset(dto) establishes controlled values. PUT sends same shape; Jackson validates server-side; Problem Details return to fields. Optimistic UI optional but server remains source of truth after response. Version/etag fields enable optimistic concurrency headers.

#### What it is
Flow: fetch → map to form model → user edits controlled fields → submit mutation → invalidate cache. Read-only fields from server displayed as text, not disabled inputs that confuse submit payload. Enum selects map to Java enum strings in JSON. DateTime fields: agree ISO-8601 instant vs local date with @JsonFormat. Money as string or number—match BigDecimal serialization contract.

#### How it works (internals)
RHF defaultValues from query data; useEffect reset when query succeeds. zodResolver(schemaFromOpenApi) client-side first pass. Submit: mutateAsync(formValues) with If-Match: etag header from loaded dto. On 409 show merge dialog fetching latest GET. Disable submit while isPending; show spinner on button.

#### When to use / when NOT to use
Every edit screen for Spring @RestController resources. Partial PATCH forms with only changed fields need different pattern. Interview: contrast with Thymeleaf form binding.

#### Production example
Order edit uses generated types from OpenAPI springdoc. Concurrent edit detection via version field Problem Details type about:blank/conflict. Select options from GET /api/reference/countries cached 24h. Audit log shows who changed field—UI displays read-only metadata from dto.audit.

#### Common mistakes
- Submitting entire form including untouched server fields that fail validation.
- Timezone bugs on LocalDate vs Instant.
- Not resetting form after successful save—stale dirty state.
- Missing If-Match on versioned resources.
- Controlled select with value not in options after enum deprecation.

#### Interview follow-ups (with model answers)

**Q:** Handle partial PATCH from form?
**A:** Track dirtyFields in RHF; build payload with only changed keys. Spring @PatchMapping with JsonMergePatch or custom DTO. Document which fields PATCHable in OpenAPI. Clear client validation on optional partial updates. Query invalidation still on success.

**Q:** Null vs undefined for optional Java fields?
**A:** JSON null clears nullable field; omit key means no change on PATCH. Align with Jackson NON_NULL vs ALWAYS settings. Zod optional() vs nullable() must match. Integration tests with WireMock assert payload shape. Document in API guide for frontend team.

#### Scenario probe
**Situation:** Saving order edit returns 422 but UI shows generic toast, fields not highlighted.

**Model answer:** Parse application/problem+json violations or fieldErrors extension from Spring MethodArgumentNotValidException handler. Map each to setError(field, message). Ensure GlobalExceptionHandler returns consistent ProblemDetail schema. Toast only for non-field errors. Add contract test between sample 422 response and mapper function. Senior fullstack owns both ProblemDetails producer and consumer.

---

### 16. Error boundaries.

**Short answer:** Error boundaries catch render-phase errors in child tree and show fallback UI without crashing the whole SPA. They do not catch event handler errors, async errors, or errors in the boundary itself. Pair with route-level boundaries around major features calling Spring services. Log to observability with correlation id from MDC. Different from try/catch around fetch—that handles API failures, not component throws.

#### What it is
Class component or react-error-boundary library with componentDidCatch/getDerivedStateFromError equivalent. Fallback can offer retry resetting error state or navigate home. react-router errorElement is boundary-like for loader errors. 500 from API doesn't trigger boundary unless throw during render from error state misuse. Boundaries don't replace Problem Details handling in mutations.

#### How it works (internals)
Wrap <Outlet /> in AppErrorBoundary; nested boundary around OrderModule. onError callback sends to Sentry with user id from JWT sub claim. Reset boundary key on navigation to retry. Throw in render only for unrecoverable invariant violations—prefer error state UI for API errors. Test with component that throws when flag set.

#### When to use / when NOT to use
Third-party chart library throws on bad data shape from Spring. Lazy route chunk load failure. Not for form validation or 401—handle explicitly.

#### Production example
Order detail boundary shows 'Unable to display order' with support link; rest of nav works. Chunk load error suggests hard refresh—detect import() failure message. Correlates frontend error id with backend traceId from Problem Details when available. On-call runbook distinguishes boundary spike vs API 5xx.

#### Common mistakes
- Expecting boundary to catch onClick handler throw.
- Single boundary at root with useless generic page.
- Not resetting boundary after fix navigation.
- Throwing in render for expected 404 order.
- Swallowing errors without logging.

#### Interview follow-ups (with model answers)

**Q:** How handle 404 from GET order?
**A:** Query isError with status 404 renders NotFound component—no throw. Or router loader returns notFound(). Boundary for unexpected throws only. Spring Problem Details type about:blank/not-found with clear title. Distinguish 404 from network offline in UI copy.

**Q:** Error boundary vs Suspense?
**A:** Suspense handles loading async render; boundary handles thrown errors. Nest boundary outside Suspense so render errors in resolved child caught. Suspense fallback not for API error states. Combine: Suspense for lazy route, boundary for module failures. Data errors stay in query error UI.

#### Scenario probe
**Situation:** Null pointer in line item component crashes entire admin app white screen.

**Model answer:** Add module-level error boundary around order components immediately. Fix root cause: guard optional line.sku with optional chaining; validate DTO with Zod at API boundary. Spring shouldn't send null sku if contract says required—fix backend or mark optional in OpenAPI. Log stack to observability. RTL test renders boundary fallback when child throws. Prevent recurrence with strict null checks and generated types.

---

### 17. Suspense and data.

**Short answer:** Suspense lets components 'wait' for async data or code by throwing a promise during render, showing fallback until resolved. Today most Spring SPAs use Suspense primarily for React.lazy route chunks, not official data fetching API yet. TanStack Query doesn't suspend by default—use useSuspenseQuery in v5 for integration. Nested Suspense boundaries enable progressive page shell + detail loading. Coordinate with error boundaries for failed lazy imports.

#### What it is
Child suspends → nearest Suspense shows fallback → promise resolves → React retries render. Multiple suspending children can trigger single boundary fallback. Streaming SSR in Next.js uses Suspense heavily—less in Vite SPA. use() in React 19 reads promises during render with Suspense integration. Distinct from isLoading boolean pattern.

#### How it works (internals)
const OrderPage = lazy(() => import('./OrderPage')); wrap <Suspense fallback={<Skeleton />}><OrderPage /></Suspense>. useSuspenseQuery(['order', id], fetchOrder) throws to Suspense until data ready. Waterfall risk: nested serial suspends—parallelize with single query or prefetch. Router lazy + Suspense at layout level. JWT-protected routes still need auth gate before suspend fetch.

#### When to use / when NOT to use
Code-split admin modules. Experimental Suspense data with React 19 + framework support. Interview: honest about current TanStack + Suspense adoption.

#### Production example
Route Suspense shows layout skeleton; page uses Query isPending for data—hybrid approach. Pilot useSuspenseQuery on read-only reference data endpoints. Avoid suspense waterfall on order detail requiring sequential GETs—BFF aggregates. Fallback components match design system shimmer.

#### Common mistakes
- Suspense boundary with no fallback.
- Serial suspend queries multiplying Spring round trips.
- Using Suspense without error boundary for rejected promises.
- Expecting Suspense to cache like React Query.
- Suspense inside event handlers—invalid.

#### Interview follow-ups (with model answers)

**Q:** Suspense waterfall problem?
**A:** Parent suspends on user, child suspends on orders—serial latency sums. Fix: parallel fetch in loader, single BFF GET /dashboard, or prefetch on hover. GraphQL-style batch or Spring @RestController aggregation endpoint. Measure TTFB vs render waterfall separately. Senior architects push parallelization to API layer.

**Q:** useSuspenseQuery vs useQuery?
**A:** Suspense version removes isPending branch—assumes boundary handles loading. Error throws to error boundary on failure unless errorElement. Cleaner component code for read paths. Mutations still use useMutation. Enable gradually per route with team standards.

#### Scenario probe
**Situation:** Lazy-loaded reports page shows blank 2s then content; users think app frozen.

**Model answer:** Add Suspense fallback skeleton at route level immediately—not blank. Prefetch reports chunk on nav hover via router preload. Consider smaller chunk split if bundle huge. Show layout chrome instantly from parent route. Spring data loading separate: skeleton table rows via Query isPending. Measure LCP; blank screen fails Core Web Vitals perception even if fast.

---

### 18. Code splitting.

**Short answer:** Code splitting breaks the JS bundle into chunks loaded on demand via dynamic import(). React.lazy wraps default export components for route-level splitting. Vite and Webpack emit hashed chunks cached by CDN; deploy new API version without forcing full reload if chunks versioned. Split by route and heavy vendors (charts, pdf) not every component. Balance initial JWT login bundle size vs chunk request waterfall.

#### What it is
import('./Admin') returns promise resolving module; lazy suspends until loaded. Route-based splitting maps to Spring security roles—admin chunk only for ROLE_ADMIN. Manual chunks in vite.config for node_modules separation. Prefetch link rel modulepreload for critical paths. Source maps for production Sentry deobfuscation.

#### How it works (internals)
React Router: { path: 'admin', lazy: () => import('./AdminRoutes') }. Analyze bundle with rollup-plugin-visualizer. Don't lazy load design system used everywhere. Error boundary on import failure (deploy race old HTML new chunks). Align cache-control: index.html no-cache, assets immutable.

#### When to use / when NOT to use
Admin vs customer app surfaces. PDF export library 500kb used on one page. Interview: initial bundle budget for mobile field apps.

#### Production example
Main chunk 180kb gzip; reports lazy 90kb. Nginx serves static from Spring Boot jar resources or separate CDN. Version.json poll detects stale chunk 404 after deploy—prompt refresh. Role-based route guard prevents downloading admin chunk for customers.

#### Common mistakes
- Lazy loading every button component.
- No loading UI during chunk fetch.
- Default export mismatch breaking lazy().
- Circular dynamic imports.
- Deploy without CDN cache bust on index.html.

#### Interview follow-ups (with model answers)

**Q:** Splitting vs tree shaking?
**A:** Tree shaking removes dead exports at build time within analyzed module graph. Code splitting creates separate network requests for runtime load. import { fn } from 'lodash-es' shakes; import whole lodash doesn't. Both reduce bytes; splitting defers load. Audit barrel files blocking shake.

**Q:** Module federation relation?
**A:** Federation loads remote bundles from another deploy at runtime—micro-frontend scale splitting. Lazy is same-app chunks. Java teams may host shell in Spring and remotes on separate pipelines. Shared react dependency version critical. Question 58 dives deeper.

#### Scenario probe
**Situation:** First load after login takes 8s on 3G; monolithic bundle 2MB.

**Model answer:** Profile bundle: split routes, remove unused MUI icons import storm, dynamic import charts. Server gzip/brotli on static assets from Spring. Critical path: auth + dashboard only; defer reports. HTTP/2 multiplexing for parallel chunks. Consider BFF pagination reducing client libs if duplicate date libs. Set performance budget in CI failing PR over limit.

---

### 19. TypeScript: `interface` vs `type`.

**Short answer:** interface declares object shape; type alias can represent unions, primitives, tuples, and mapped types. Both model Spring OpenAPI-generated DTOs; interfaces support declaration merging for module augmentation. Prefer interface for public object contracts; type for unions like ProblemDetail | OrderDto. Neither exists at runtime—erased like Java generics. Consistency in codebase matters more than religious preference.

#### What it is
interface Order { id: string } extends implicitly; type Order = { id: string } is equivalent for objects. type Status = 'DRAFT' | 'SUBMITTED' matches Java enum JSON. interface can't express union of string | number easily. extends with interface vs intersection with type: & combinator. OpenAPI generator often emits interfaces or types per config.

#### How it works (internals)
Generate from springdoc OpenAPI npm script in CI. Hand-written UI-only props: interface OrderRowProps. API errors: type ApiError = ProblemDetail & { fieldErrors?: FieldError[] }. Avoid duplicate manual DTOs—regenerate on API bump. eslint consistent-type-definitions rule picks one style.

#### When to use / when NOT to use
Codegen picks for you mostly. Interview: explain union/discriminated types need type keyword. Library augmentation needs interface.

#### Production example
openapi-typescript generates types from /v3/api-docs. Custom ProblemDetail interface aligned with Spring 6 RFC7807 handler. Props interfaces in design system package shared monorepo. Breaking API change fails TS build in UI pipeline before deploy.

#### Common mistakes
- Duplicating OrderDto manually diverging from Java record.
- Using type when interface merging needed for MUI theme.
- any instead of generating types.
- Union too wide losing autocomplete.
- Ignoring deprecated fields in OpenAPI.

#### Interview follow-ups (with model answers)

**Q:** interface extends vs type intersection?
**A:** interface extends checks override compatibility explicitly. type A & B intersects properties; conflicts on same key must be compatible. For composing DTO + UI fields, intersection common: OrderDto & { isSelected: boolean }. Pick readable form for team. Performance of compiler negligible either way.

**Q:** Model Java Optional fields?
**A:** TS optional ? or union with undefined depending on generator. Jackson absent vs null: Zod refine at boundary. Don't assume undefined means null on POST. Document in OpenAPI required array. Strict optionalPropertyTypes tsconfig tightens.

#### Scenario probe
**Situation:** Frontend OrderDto missing new Java field; runtime undefined access crashes.

**Model answer:** Regenerate types from OpenAPI in CI gate on API module merge. Zod safeParse at fetch boundary catches schema drift before render. Optional chain in UI as defense; fix contract first. semver or consumer-driven contract tests. Monorepo: shared openapi artifact published from Spring build. Senior process prevents manual DTO copy.

---

### 20. Narrowing and discriminated unions.

**Short answer:** Narrowing refines broad types to specific variants using typeof, in, instanceof, or discriminant property checks. Discriminated unions tag variants with literal type field—mirrors Java sealed classes pattern. Essential for rendering different UI per ProblemDetail type or payment method. Exhaustive switch with never check catches missing cases at compile time. Prefer discriminated unions over optional fields soup on DTOs when variants differ structurally.

#### What it is
type Result = { status: 'ok'; data: OrderDto } | { status: 'error'; problem: ProblemDetail }. if (result.status === 'ok') narrows to data branch in TS control flow. in operator checks property existence. Assertion functions: function isOrder(x: unknown): x is OrderDto. Zod parse returns narrowed type.

#### How it works (internals)
Map Spring payment types CREDIT_CARD | INVOICE to union components. switch (action.type) with default assertNever for reducer actions. Parse API unknown with Zod schema discriminated on type field. Avoid as OrderDto without validation at boundary. Codegen enums as union of literals.

#### When to use / when NOT to use
Polymorphic JSON from Spring @JsonSubTypes. UI state machines with distinct step shapes. Interview: write narrowing without as keyword.

#### Production example
Webhook event payload union on eventType from Kafka bridge endpoint. Problem Details extension types narrowed before display component. Compiler errors when new Java enum value added without UI case. Table driven tests per variant.

#### Common mistakes
- Optional fields for mutually exclusive shapes.
- as casting instead of narrowing after guard.
- Non-exhaustive switch silently falling through.
- Discriminant field optional losing narrowing.
- Trusting API shape without runtime parse.

#### Interview follow-ups (with model answers)

**Q:** assertNever pattern?
**A:** function assertNever(x: never): never { throw new Error(); } in switch default. If new action type added, compile error in default branch. Same for exhaustive enum handling matching Java switch on sealed types. Keeps reducers maintainable. Pair with eslint no-fallthrough.

**Q:** Narrow unknown from fetch?
**A:** const json: unknown = await res.json(); then Zod safeParse or type guards. Check res.ok before assuming success shape. Problem Details on error has different schema than success DTO. Never assume 200 body is OrderDto without check. Centralize in apiClient.parseResponse.

#### Scenario probe
**Situation:** Payment component accesses cardToken on invoice payment type causing undefined error.

**Model answer:** Model PaymentMethod as discriminated union on methodType from Spring. Render CreditCardForm | InvoiceForm after switch narrow. Backend @JsonSubTypes should match frontend union. Zod discriminatedUnion at API parse. Remove optional cardToken on invoice variant at type level—impossible state unrepresentable. Tests per variant fixture from Java sample JSON.

---

### 21. Generics in TS vs Java.

**Short answer:** TypeScript generics parametrize types like Java generics but erase at compile time with structural typing. TS generics are duck-typed: T extends { id: string } accepts any matching shape, not declared implements. Common patterns: ApiResponse<T>, useQuery<TData>, Record<K,V> like Map types. Variance differs—TS bivariant method params historically; strictFunctionTypes helps. Use generics for reusable hooks wrapping Spring paginated responses.

#### What it is
function fetchPage<T>(url): Promise<Page<T>> mirrors Spring Page<T>. Constraints: <T extends BaseEntity> requires id field. Inference: map doesn't need explicit T when callback typed. Default type params: ApiError = ProblemDetail. No reified generics at runtime—need Zod for T validation.

#### How it works (internals)
Generic useApiQuery<T>(key, url) with parse: (json: unknown) => T via Zod. Table component <T, K extends keyof T> columns config type-safe. Avoid generic any default. Mirror Java generic bounds in TS extends clauses. Document generic params on exported hooks.

#### When to use / when NOT to use
Shared data table, form field components, API client layer. Interview: compare to Java List<OrderDto> erasure. Don't over-generic simple one-off components.

#### Production example
PaginatedTable<OrderSummaryDto> reused across modules. OpenAPI operations generate generic call signatures per operation. Generic constraints prevent column accessor keys not on DTO. Unit tests instantiate with test DTO types.

#### Common mistakes
- Generic T = any defeating purpose.
- Too many type params on components.
- Assuming runtime typeof T exists.
- Complex conditional types when simple union suffices.
- Ignoring strict null on generic returns.

#### Interview follow-ups (with model answers)

**Q:** Generics vs unknown at API boundary?
**A:** Fetch returns unknown; generic function accepts ZodSchema<T> to output T. Generic documents caller expected type after validation. Without parse, generic is lie—only satisfies compiler. Pattern: fetchJson<T>(schema: ZodType<T>). Matches Java: cast after instanceof check.

**Q:**  keyof and generics together?
**A:** function pluck<T, K extends keyof T>(obj: T, key: K): T[K] type-safe property access. Table sortColumn: keyof OrderDto prevents typo sort fields. Mapped types generate form keys from DTO. Powerful for reducing stringly typed accessors. Keep readable—don't meta-program excessively.

#### Scenario probe
**Situation:** Shared hook returns any; callers assume OrderDto and ship bugs.

**Model answer:** Refactor hook to useApiQuery<T>(schema: ZodSchema<T>) returning typed data or error. Callers pass orderSchema; inference provides OrderDto. Remove any from eslint ban list exceptions. Align with Java generic service method signatures in OpenAPI. CI typecheck blocks merge. Runtime validation catches API drift generics can't.

---

### 22. `unknown` vs `any` vs `never`.

**Short answer:** unknown is type-safe top type—you must narrow before use; prefer for JSON from Spring. any disables checking—escape hatch only at legacy boundaries with immediate parse. never is uninhabitable—used for exhaustive checks and functions that always throw. Senior code minimizes any; eslint @typescript-eslint/no-explicit-any enforced. Java parallel: unknown like Object you must cast after instanceof.

#### What it is
let x: unknown = await res.json(); x.id // error until narrowed. any propagates silently—y = x; y.foo(). never in never-returning functions or bottom of switch. void for no return; undefined for missing optional. strict tsconfig noImplicitAny catches untyped params.

#### How it works (internals)
API layer: json unknown → Zod → OrderDto. Catch (e: unknown) with instanceof Error check. Third-party lib without types: declare minimal module.d.ts not any everywhere. Gradual migration: any at one import boundary then narrow. never for assertNever default.

#### When to use / when NOT to use
Every fetch response body. JSON.parse results. Interview: refactor any to unknown + guard.

#### Production example
eslint error on explicit any in src/. Legacy chart lib wrapped in typed facade. Problem Details parser accepts unknown. PR review blocks any without ticket justification.

#### Common mistakes
- as any to silence compiler.
- any on Spring DTO 'temporary' forever.
- Confusing never with void return.
- unknown without narrowing still unsafe via double cast.
- any in dependencies leaking to app types.

#### Interview follow-ups (with model answers)

**Q:** Type JSON.parse?
**A:** Returns any by default—assign to unknown immediately. JSON.parse(text) as unknown then Zod. Never trust localStorage parse without schema. JWT payload decode to unknown before z.object parse claims. Prevents prototype pollution surprises.

**Q:** When is any acceptable?
**A:** Prototyping spike deleted before merge—not production. Interop with untyped JS one line thick wrapper. Migration bridge with TODO and deadline. Prefer unknown + type guard even if verbose. Senior accountability for any count metric.

#### Scenario probe
**Situation:** Developer used any for axios response; production crash on null nested field.

**Model answer:** Type axios with generic or wrapper returning Zod-validated T. Response interceptor parses unknown body. Spring null fields explicit in OpenAPI nullable. Revert any commit; add test with null payload fixture. Enable strictNullChecks if off. Culture: unknown at boundary is default pattern in style guide.

---

### 23. Zod (or similar) at the API boundary.

**Short answer:** Zod validates unknown runtime data against schema—critical at SPA boundary with Spring JSON. Schemas document constraints mirroring Bean Validation @NotNull, @Size, @Email. safeParse returns success or ZodError without throw—map to UI errors. Share schemas with React Hook Form via zodResolver. Codegen from OpenAPI to Zod emerging; hand-maintain until then for critical paths.

#### What it is
const OrderSchema = z.object({ id: z.string().uuid(), total: z.number().nonnegative() }). Infer type: z.infer<typeof OrderSchema> stays DRY with validation. coerce for query string numbers. refine for cross-field rules matching @AssertTrue. transform normalize phone before submit to Spring.

#### How it works (internals)
api.getOrder: safeParse(json); log ZodError to Sentry on failure—signals contract break. Form: same schema client-side before POST saving round trip. Partial schemas for PATCH dirty fields. discriminatedUnion for polymorphic events. Version schema with apiVersion field if needed.

#### When to use / when NOT to use
Every external JSON: REST, WebSocket message, localStorage JWT claims parse. Not for internal props already typed. Interview: contrast compile-time TS vs runtime Zod.

#### Production example
Central schemas/order.ts imported by api and forms. Contract test: Java sample JSON fixtures in repo validated by Zod in Jest. Mismatch alerts before deploy. Problem Details schema separate from success DTO.

#### Common mistakes
- Zod only on form not GET response.
- Schema drift from OpenAPI unnoticed.
- parse() throwing uncaught in render path.
- Over-coercion hiding invalid server data.
- Duplicating unrelated schemas per component.

#### Interview follow-ups (with model answers)

**Q:** Zod vs class-validator on backend?
**A:** Java Bean Validation runs server-side authoritative. Zod is client first line—never replaces server validation. Align error messages UX consistency optional. OpenAPI is contract source of truth both sides. Duplicate rules cost—consider schema generation pipeline.

**Q:** Handle ZodError in UI?
**A:** Flatten field errors for form setError. Global fetch failure: toast 'data format unexpected' + log details. Dev mode show path in error overlay. Don't expose raw Zod paths to end users in prod. Retry fetch once on schema fail in case CDN glitch.

#### Scenario probe
**Situation:** Spring added enum value SHIPPED; UI crashes in switch default.

**Model answer:** Zod enum or nativeEnum with catchall or string fallback + monitoring. Exhaustive UI switch with assertNever; build fails when schema updated if codegen tied. Contract test in CI with new enum sample from Java test fixture. Display raw status string fallback label 'Unknown' gracefully. Process: API changelog triggers frontend schema PR in same release train.

---

### 24. `strict` tsconfig.

**Short answer:** strict tsconfig enables strictNullChecks, strictFunctionTypes, noImplicitAny—catches null and any bugs before runtime. strict: true is baseline for enterprise SPAs integrating with Spring DTOs. Additional flags: noUncheckedIndexedAccess, exactOptionalPropertyTypes for maximum safety. Incremental adoption on legacy codebases via per-module strict islands. CI tsc --noEmit gate on PR matches Java compile step.

#### What it is
strictNullChecks: OrderDto | null must be handled before .lines access. noImplicitReturns ensures all code paths return in typed functions. useUnknownInCatchVariables: catch (e: unknown). skipLibCheck speeds build skipping node_modules d.ts errors. paths aliases for monorepo @company/api-types.

#### How it works (internals)
tsconfig.json strict true; extends base in monorepo root. Vite uses esbuild for transpile but tsc for typecheck script. Fix errors from enabling strictNullChecks before noUncheckedIndexedAccess. Generated OpenAPI types may need skipLibCheck or post-process. IDE respects same config.

#### When to use / when NOT to use
Greenfield React + Spring projects day one. Legacy migration milestone per package. Interview: name three strict flags and what they catch.

#### Production example
noImplicitAny blocked merge of untyped axios wrapper. strictNullChecks forced optional chain on order.customer?.name. CI parallel: mvn test + npm run typecheck. Gradual exactOptionalPropertyTypes on api package only.

#### Common mistakes
- strict false with @ts-ignore sprinkled.
- Only IDE checking not CI tsc.
- as assertions to bypass strict null instead of fixing.
- Disabling strict in test files only—leaks patterns.
- Ignoring generated type errors with skipLibCheck abuse.

#### Interview follow-ups (with model answers)

**Q:** noUncheckedIndexedAccess impact?
**A:** arr[i] returns T | undefined—forces guard on array access. Catches order.lines[i] without bounds check. Noisier code but fewer production undefined crashes. Enable after strictNullChecks stable. Record access also undefined if key missing.

**Q:** TS vs Java compile in pipeline?
**A:** Both must pass before deploy artifact promote. OpenAPI break fails TS when types regenerated in same pipeline stage. Docker multi-stage: frontend typecheck layer cached. Parallel jobs shorten feedback. Single monorepo workflow dispatch.

#### Scenario probe
**Situation:** Production TypeError on undefined; TS not run in CI.

**Model answer:** Add npm run typecheck to CI immediately with strict true roadmap. Fix immediate bug with null guard; enable strictNullChecks if off. Sentry stack shows line—add test reproducing undefined access. Zod at boundary prevents bad data propagation. Gate releases on typecheck like mvn verify. Senior owns toolchain quality parity with backend.

---

### 25. Utility types.

**Short answer:** Utility types transform types: Partial<T>, Pick<T,K>, Omit<T,K>, Record<K,V>, ReturnType<F>. Mirror Java patterns: Partial like builder optional setters; Pick for list view subset of entity DTO. Use for form draft types Omit<OrderDto, 'id' | 'audit'> & { id?: string }. Mapped types power advanced generics; know common utilities for interviews. Don't recreate—import from TypeScript lib.

#### What it is
Partial<OrderDto> for PATCH payloads with only changed fields typed optional. Pick<OrderDto, 'id' | 'status'> for table row props. Record<string, FieldError> for Problem Details map. Exclude union members: Exclude<Status, 'DELETED'>. Parameters<typeof fetchOrder> extracts args.

#### How it works (internals)
Define OrderFormValues = Omit<OrderDto, 'createdAt'> for editable subset. NonNullable<T> after filter guard. Awaited<ReturnType<typeof api.save>> for mutation result type. satisfies operator TS 4.9 validates object literal against type. Compose utilities rather than duplicate field lists.

#### When to use / when NOT to use
Mapping between API DTO and form model. Typing dispatch actions Pick<Fields>. Interview: write Pick/Omit without looking up docs.

#### Production example
OrderUpdate = Partial<Pick<OrderDto, 'status' | 'notes'>> matches PATCH contract. Column defs use accessor keyof OrderDto with Pick patterns. Shared utilities.d.ts in monorepo types package. Codegen sometimes emits helper types—prefer native utilities when simpler.

#### Common mistakes
- Manual duplicate interface instead of Pick from generated DTO.
- Partial everywhere losing required field enforcement on POST.
- Deep Partial when only top level needed.
- Wrong Omit keys missing nested object.
- Over-engineering conditional types for simple Omit.

#### Interview follow-ups (with model answers)

**Q:** Partial vs DeepPartial custom?
**A:** Partial only optional top-level keys. Nested order.shipping still required as object unless custom recursive mapped type. For nested PATCH rare—flatten DTO or send whole nested object. Spring JsonNullable or optional wrappers affect design. Keep forms flat where possible.

**Q:** satisfies vs type annotation?
**A:** const cols = [...] satisfies ColumnDef<OrderDto>[] checks literal without widening to general type. Preserves narrow literal inference while validating shape. Useful for config arrays with const string literals. Annotation ColumnDef[] widens literals. Modern TS pattern for route configs and action maps.

#### Scenario probe
**Situation:** Form type manually maintained diverged from OrderDto after API change.

**Model answer:** Derive OrderFormValues = Pick<Omit<OrderDto,...>> from generated type. Single source OpenAPI; utilities compose view-specific slices. CI regenerates types on springdoc publish. Remove duplicate interface file. Document which fields editable via Pick list in one constants file. Java record change automatically flows to TS compile errors in form mapper.

---

### 26. Event handler types.

**Short answer:** Event handler types tie DOM events to React's SyntheticEvent wrappers with correct target typing. ChangeEvent<HTMLInputElement> for controlled inputs; FormEvent<HTMLFormElement> for onSubmit. MouseEvent<HTMLButtonElement> for button clicks posting to Spring. Avoid Event or any—use specific generic from @types/react. Custom components should accept standard handler props typed explicitly.

#### What it is
React.SyntheticEvent pools events for performance—don't read async after await without persist (deprecated pattern). currentTarget typed on form; target may need cast for inputs. KeyboardEvent for shortcuts in admin grids. DragEvent rare for file drop to Spring multipart upload. Handler signature (e: ChangeEvent<HTMLInputElement>) => void.

#### How it works (internals)
onChange={(e) => setName(e.currentTarget.value)} for text input. onSubmit={(e) => { e.preventDefault(); mutate(values); }} prevents full page POST. Pass handlers as props: onSave: (order: OrderDto) => void not raw click event to parent. MUI TextField onChange signature differs—use Controller types. Global keydown in useEffect with typed handler.

#### When to use / when NOT to use
Typing custom Input component onChange prop. Interview: difference currentTarget vs target. Accessibility keyboard handlers on modal.

#### Production example
Strict handler types in design system Button onClick?: MouseEventHandler<HTMLButtonElement>. File upload onChange validates File type before presigned S3 or Spring multipart. Stop propagation on row click vs checkbox click in order table. No implicit any on event params in eslint.

#### Common mistakes
- e.target.value on FormEvent without cast.
- Async handler reading e.target after await without capturing value.
- Wrong element generic on delegated events.
- onClick expecting MouseEvent when keyboard activation differs.
- PreventDefault forgotten on form submit causing page reload.

#### Interview follow-ups (with model answers)

**Q:** Type children with onClick?
**A:** ComponentProps<'button'>['onClick'] or React.ButtonHTMLAttributes. Extend interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>. Polymorphic as prop patterns in design systems. Don't re-export any Event type. Forward ref for focus management typed.

**Q:** React 19 form action typing?
**A:** form action prop accepts function receiving FormData—typed in React 19 types. Integrates with useFormStatus pending state. Still validate FormData before Spring POST. Progressive enhancement path for non-JS fallback rare in internal SPAs. See question 51 for depth.

#### Scenario probe
**Situation:** TypeScript error on e.target.value in generic onChange handler shared across input types.

**Model answer:** Over-generic handler—split TextInputChange vs SelectChange or use union with discrimination. Or generic <T extends HTMLInputElement | HTMLSelectElement> with proper extends. RHF Controller provides typed field.onChange. Capture value synchronously: const v = e.currentTarget.value before async. Don't cast to any—fix component API. Design system documents event prop contracts.

---

### 27. Avoid `as` except at boundaries.

**Short answer:** Type assertions (as) tell compiler to trust you—bypasses safety; use only at validated boundaries. After Zod safeParse success, data is typed without as. as const for literal narrowing in action types and query keys. Double cast as unknown as Foo is code smell—fix types or parse. Java parallel: unchecked cast warning suppressed only with proof.

#### What it is
response as OrderDto is lie if not validated. as const makes ['orders', id] readonly tuple for queryKey. Assertion functions preferred: function assertOrder(x: unknown): OrderDto. Satisfies operator reduces need for as on object literals. DOM refs: useRef<HTMLInputElement>(null) not as on mount.

#### How it works (internals)
Boundary pattern: parse unknown → T; inner app never uses as on API data. as const on discriminated action literals in reducer. Third-party gap: minimal interface assertion once in adapter file documented. eslint consistent-type-assertions style. Code review flags new as keyword.

#### When to use / when NOT to use
DOM APIs without perfect lib types—narrow with instanceof first. Test mocks may use satisfies over as. Interview: refactor as OrderDto to Zod.

#### Production example
Zero as on fetch bodies policy—Zod only. as const on ROUTES and query keys. Legacy migration adapter layer quarantined as usage. SonarQube or eslint count trending down.

#### Common mistakes
- as any chain spreading.
- Asserting non-null with as instead of guard.
- as on JSON.parse direct.
- Casting error to AxiosError without check.
- Using as to silence exhaustive switch.

#### Interview follow-ups (with model answers)

**Q:** Non-null assertion operator !?
**A:** order!.lines assumes order defined—runtime crash if wrong. Prefer if (!order) return null; early in component. Ref.current! after useEffect focus ok with null check. Same boundary rule: avoid ! on API data. strictNullChecks exists to eliminate ! abuse.

**Q:** as const use cases?
**A:** const STATUS = { DRAFT: 'DRAFT' } as const → readonly literal types. queryKey: ['orders', id] as const for TanStack inference. Action types in reducer { type: 'SAVE' } as const. Prevents accidental widening to string. Pairs with satisfies for config objects.

#### Scenario probe
**Situation:** Codebase has 200 'as OrderDto' after axios calls.

**Model answer:** Introduce apiClient.getOrder returning Zod-validated OrderDto; delete casts in one migration PR. eslint ban-type-assertion rule with exceptions file shrinking weekly. Training: as is debt; Zod is investment. Wire contract tests so casts aren't 'needed' for wrong optional fields. Measure incident reduction post-migration. Senior sets boundary architecture once.

---

### 28. Hooks rules.

**Short answer:** Hooks rules: only call hooks at top level of function components or custom hooks—never in loops, conditions, or nested functions. Only call from React function components or custom hooks starting with use. Rules preserve hook call order across renders for fiber hook list. eslint-plugin-react-hooks enforces rules-of-hooks and exhaustive-deps. Custom hooks extract reusable stateful logic—useOrder, useAuth.

#### What it is
Violating rules causes 'Rendered more hooks than previous render' crash. Conditional useState breaks hook index alignment. Hooks compose: custom hook can call useQuery + useReducer. Naming convention use* signals hook to linter and humans. Class components can't use hooks—legacy only.

#### How it works (internals)
Extract conditional logic inside hook body after unconditional hook calls. if (!enabled) skip effect work inside useEffect with guard, not skip useEffect. useQuery({ enabled: !!id }) instead of conditional useQuery call. Custom hooks return stable API object memoized if needed. Test hooks with @testing-library/react renderHook.

#### When to use / when NOT to use
Code review any hook in if statement. Interview: fix broken component with hook in loop. Designing shared data hooks for Spring resources.

#### Production example
CI eslint rules-of-hooks error level. Custom hooks folder by domain: orders/, auth/. No hooks in utility.ts plain functions. Storybook stories use hooks only in render function components.

#### Common mistakes
- useState inside if (isAdmin).
- Calling useOrder from regular async function.
- Hooks in class component convert missed.
- Dynamic hook name anti-pattern.
- Copy-paste hook block into non-component helper.

#### Interview follow-ups (with model answers)

**Q:** Conditional fetching pattern?
**A:** useQuery({ queryKey: ['order', id], enabled: Boolean(id) }) always called. When id undefined, query idle not running. Same for useEffect with early return inside callback. Never wrap useQuery in if (id). Document enabled flag in hook JSDoc.

**Q:** Custom hook naming without use?
**A:** Must start with use for rules-of-hooks to apply when it calls hooks internally. getOrderData() calling useQuery violates rules if called from component inconsistently. Rename to useOrderData. Pure functions without hooks don't need use prefix. Clear separation api/order.ts vs hooks/useOrder.ts.

#### Scenario probe
**Situation:** Component crashes with hooks order error after adding feature flag conditional useState.

**Model answer:** Move useState unconditional; store flag value in state or read flag then compute render branch. const [x, setX] = useState(flag ? a : b) initializer ok; not conditional hook call. Feature flags from context still use hooks at top. Run eslint rules-of-hooks—it catches this. Explain fiber linked list hook slots to junior. Add regression test rendering both flag values.

---

### 29. Custom hook example: `useOrder(id)`.

**Short answer:** Custom hook useOrder encapsulates fetching, mutations, and derived state for order domain—single API for components. Combines useQuery for GET, useMutation for PATCH, selectors for line totals. Hides queryKey conventions and Problem Details mapping from UI. Returns { order, isLoading, updateStatus, error } stable interface. Java parallel: facade service over OrderRepository + OrderValidator.

#### What it is
function useOrder(orderId: string) { const query = useQuery(...); const mutation = useMutation(...); return { ... }; }. Can accept options: refetchInterval for tracking page. Internal useMemo for derived flags isShippable. Throws or returns error state—team convention. Colocated tests with MSW mocking Spring endpoints.

#### How it works (internals)
queryKey ['orders', orderId] aligned with invalidation on mutation. updateStatus calls mutate with If-Match header from query.data.version. Parse errors with mapProblemToFieldErrors helper. Prefetch related useOrderLines in same hook or separate useOrderLines. Document hook contract in TSDoc with Spring endpoint mapping.

#### When to use / when NOT to use
Third component needs same order logic—extract hook. Interview: implement useOrder sketch with Query. Avoid hook returning 30 fields—split hooks.

#### Production example
useOrder used by detail page, header badge, print modal. Optimistic status update in mutation onMutate rolled back on 409. Hook file imports only from api/orders module. MSW handlers shared between hook tests and RTL page tests.

#### Common mistakes
- Hook doing unrelated auth logic.
- Unstable return object new {} each render causing effect deps churn.
- Exposing raw query object leaking abstraction.
- Missing enabled guard for empty orderId.
- Side effects in hook body outside useEffect.

#### Interview follow-ups (with model answers)

**Q:** Split useOrder vs useOrderList?
**A:** Separate hooks per resource operation keeps API focused. useOrderList handles pagination filters; useOrder single entity. Shared queryClient invalidation links them. Optional useOrdersModule combining for convenience export barrel. Avoid god hook anti-pattern.

**Q:** Test useOrder without full page?
**A:** renderHook with QueryClientProvider wrapper. MSW returns fixture OrderDto JSON. Assert isLoading transitions and data after waitFor. Mutation test triggers PATCH and checks invalidate called. Faster than E2E; complements contract tests.

#### Scenario probe
**Situation:** Three components duplicate order fetch and diverge on error handling.

**Model answer:** Extract useOrder now; migrate components one PR. Centralize Problem Details mapping and 404 handling. Single queryKey ensures cache sharing—no triple GET. Export types UseOrderResult for consumers. Delete duplicate useEffect fetches. Document in README hooks pattern for other entities like useShipment.

---

### 30. State machines for UI (XState or reducer).

**Short answer:** State machines model UI as explicit states and events—eliminates impossible UI like Submit on already-submitted order. XState or useReducer with discriminated union actions implement finite states matching Spring workflow. Visualize transitions: DRAFT → SUBMITTED → APPROVED aligned with backend OrderStatus enum. Side effects on transitions (API call) live outside reducer or in XState invoke services. Senior alternative to boolean flag soup: isSubmitting && !isError && canEdit.

#### What it is
State chart defines guards: canSubmit when lines.length > 0. Context holds orderId, error ProblemDetail. Parallel states for loading vs form editing rare—prefer single sequential machine. Java Spring StateMachine or Camunda may mirror frontend for long workflows. Testing: assert transition table.

#### How it works (internals)
useReducer with OrderWorkflowState and exhaustive action union. Or useMachine(orderMachine) from @xstate/react. SUBMIT event triggers invoke POST; onDone transition to SUBMITTED. onError store problem in context, stay in editable with error banner. UI renders by state: switch(state) { case 'draft': return <Form /> }.

#### When to use / when NOT to use
Multi-step checkout, approval flows, connection states (connecting/connected/error). Simple toggle doesn't need machine. Interview: model order cancel flow with guards.

#### Production example
Order approval UI machine synced with GET /api/orders/{id}/allowed-actions from Spring. Server sends available transitions; client machine intersects for safety. Stately inspector in dev only. Reduced bug where cancel button visible after ship.

#### Common mistakes
- Machine duplicated server rules diverging.
- Side effects inside reducer breaking purity.
- Too granular states for simple form.
- Not handling 409 transition conflict from Spring.
- Unreachable states without monitoring.

#### Interview follow-ups (with model answers)

**Q:** XState vs useReducer machine?
**A:** XState gives visualization, invoke, delays, parallel regions—worth dependency for complex flows. useReducer sufficient for 4-state wizard with team preferring zero deps. Both beat ad-hoc booleans. Pick based on complexity and team familiarity. Java devs often appreciate explicit transition table docs.

**Q:** Sync machine with server status?
**A:** On GET success, send SYNC action with server status to reset machine state if drift. WebSocket event ORDER_APPROVED triggers external transition. Don't fight server—display conflict if local transition illegal. Polling fallback for status on tracking page. Idempotent event handling.

#### Scenario probe
**Situation:** Order UI shows Submit and Cancel simultaneously after network error confusing users.

**Model answer:** Replace boolean flags with explicit states: editing, submitting, submitError, submitted. Only editing shows Submit; submitting disables all; submitError shows retry. Map Spring status + client transient state in machine context. Reducer purity: SUBMIT_START vs async in useEffect listening to state. Diagram transitions for QA test cases. Align button visibility with backend allowed-actions endpoint long term.

---

### 31. Performance: virtualize long lists.

**Short answer:** Virtualization renders only visible rows of long lists—essential for Spring pages returning hundreds or thousands of order lines. Libraries: TanStack Virtual, react-window, react-virtuoso with dynamic row heights. Pair with server pagination for data beyond client memory; virtualize within fetched page. Stable row keys and memoized row components critical for smooth scroll. Measure before virtualizing—200 rows may not need it.

#### What it is
Virtual list calculates offset translateY for visible slice; DOM node count ~20 not 5000. overscan renders extra rows for fast scroll. Variable height requires measure pass or estimateSize callback. Accessibility: focus management and aria-rowindex need attention. Grid virtualization for spreadsheet-style order entry.

#### How it works (internals)
useVirtualizer on scroll container ref with count: orders.length. Row renderer receives virtualItem.index → orders[index] from Spring Page content. Infinite scroll: fetchNextPage when near end intersecting sentinel. Keep header/footer outside virtualizer. Test scroll performance with Chrome performance panel.

#### When to use / when NOT to use
Order line editor 500+ lines. Audit log infinite history. Client-side sort of large dataset—prefer server sort first.

#### Production example
Order lines virtualized after perf complaint; 60fps scroll restored. Spring Page size 100 with virtual window; load more on scroll. Memo OrderLineRow + stable onChange per line id. Known issue: nested expand row disables virtualization for that mode.

#### Common mistakes
- Virtualizing without fixed or measured height breaking scroll.
- Index key breaking focus on edit.
- Fetching all pages client-side then virtualizing—memory blowup.
- Nested tables virtualized incorrectly.
- Ignoring keyboard navigation a11y.

#### Interview follow-ups (with model answers)

**Q:** Virtualization vs pagination?
**A:** Pagination reduces server load and JSON size—first choice for Spring Data. Virtualization solves DOM cost within loaded page. Combine: paginated API + virtual render per page for 100 dense rows. Infinite query merges pages in cache while virtualizing total loaded. SEO irrelevant in authenticated SPA.

**Q:** Dynamic row height challenge?
**A:** Measure element after mount with virtualizer.measureElement ref. Cache heights by row id. Expandable rows complicate—consider separate detail panel not inline expand. react-virtuoso handles dynamic well. Profile remeasure thrashing on content change.

#### Scenario probe
**Situation:** Order list 2000 rows from single GET freezes browser.

**Model answer:** Immediate: server pagination GET ?page=&size=50; never load 2000 at once. Within page, add virtualization if rows complex. Backend Spring Pageable mandatory; fix API allowing unbounded findAll. Query useInfiniteQuery for UX smooth scroll. Profiler confirm main thread blocked on render not network. Product cap export separately not in grid.

---

### 32. Web Vitals.

**Short answer:** Web Vitals measure real user experience: LCP, INP, CLS core metrics Google uses for ranking signals. LCP: largest content paint—optimize hero/skeleton on dashboard loading Spring data. INP replaces FID: responsiveness to interactions—batching, transitions, avoid long tasks. CLS: layout shift from async data pop-in—reserve space for tables and fonts. Report via web-vitals library to analytics endpoint or Datadog RUM.

#### What it is
LCP elements often image or text block—slow JWT bootstrap delaying first API hurts. INP captures slow click handlers synchronously filtering huge arrays. CLS from MUI DataGrid loading without skeleton height. TTFB includes Spring API; LCP may be client-rendered content after fetch. Field vs lab data differ—monitor production.

#### How it works (internals)
import { onLCP, onINP, onCLS } from 'web-vitals'; sendBeacon to /api/rum (Spring ingest). Skeleton loaders with min-height matching final table. Font display swap; preload critical CSS. Code split; defer non-critical charts. useTransition for search per question 56.

#### When to use / when NOT to use
Customer-facing SPA SLA. Interview: name vitals and one fix each. Before blaming Spring, measure client contribution.

#### Production example
RUM dashboard correlates slow LCP with region and API latency. CLS fix: fixed table header row skeleton. INP improved after virtualizing order list. Performance budget in Lighthouse CI on PR for main routes.

#### Common mistakes
- Loading spinner without layout reservation causing CLS.
- Huge sync JSON parse blocking main thread hurting INP.
- Ignoring vitals on internal admin apps still matters for productivity.
- Optimizing bundle only ignoring slow Spring TTFB.
- No production RUM—only local Lighthouse once.

#### Interview follow-ups (with model answers)

**Q:** LCP optimization for data-heavy dashboard?
**A:** SSR/edge less common in Vite SPA—optimize critical path: shell HTML, font, first meaningful skeleton fast. Parallelize JWT refresh and initial GET; don't waterfall auth then data. BFF aggregates dashboard widgets one round trip. Lazy below-fold widgets. CDN cache static assets from Spring Boot.

**Q:** INP vs debounce?
**A:** Debounce helps INP by reducing work per keystroke but perceived latency if overdone. INP measures full interaction until next paint—includes handler + render. startTransition lowers priority of heavy render improving INP. Profile long tasks >50ms. Balance UX responsiveness with server load.

#### Scenario probe
**Situation:** Google Search Console reports poor CLS on login redirect to order dashboard.

**Model answer:** Audit layout shifts: banner ad?, font swap?, table appearing without reserved height?. Add dashboard skeleton matching grid dimensions before Query resolves. Avoid injecting notification bar pushing content down after load. Measure CLS in staging with web-vitals. Spring response speed helps LCP element data but CLS is mostly CSS structure. Fix font loading strategy first quick win.

---

### 33. Accessibility.

**Short answer:** Accessibility ensures keyboard, screen reader, and contrast usability—legal requirement in many jurisdictions. Semantic HTML first: button not div onClick, label associated with inputs posting to Spring. ARIA sparingly when semantics insufficient: aria-live for async validation errors from Problem Details. Focus management on modal open/close and route change. Test with axe-core in CI and manual VoiceOver spot checks.

#### What it is
WCAG 2.1 AA common target: contrast 4.5:1, focus visible, name-role-value. React: useId for label htmlFor, ref focus trap in modals. Live regions announce save success after PUT. Data tables need th scope, caption, keyboard nav. Skip links for main content in shell layout.

#### How it works (internals)
eslint-plugin-jsx-a11y on PR. MUI components mostly accessible if used correctly—don't strip labels. Error summary at form top linking to fields with aria-describedby. Loading states aria-busy on region. Don't rely on color alone for order status—icon + text.

#### When to use / when NOT to use
Government or enterprise procurement a11y requirements. Interview: make modal accessible sketch. Every custom component library review.

#### Production example
axe CI fails on critical violations. Order status badges include text not color-only. Date pickers keyboard navigable; ISO format displayed clearly. VPAT documentation for customer audits. Spring errors mapped to accessible inline messages.

#### Common mistakes
- div with onClick no keyboard support.
- Missing alt on decorative vs informative images.
- Focus lost behind modal backdrop.
- aria-hidden on focusable elements.
- Dynamic content without live region announcement.

#### Interview follow-ups (with model answers)

**Q:** Accessible data grid for orders?
**A:** Use established pattern MUI DataGrid or AG Grid a11y mode. Announce sort changes via aria-live polite. Row actions keyboard reachable—not hover-only menus. Pagination controls labeled. Virtualized lists need aria-rowcount carefully.

**Q:** Testing a11y in RTL?
**A:** jest-axe toHaveNoViolations on rendered form. Testing Library getByRole preferred over testId. tab userEvent keyboard navigation tests. Not full screen reader simulation—supplement manual. Include 422 error state in a11y tests.

#### Scenario probe
**Situation:** QA reports screen reader doesn't announce order save failure from Spring 422.

**Model answer:** Add aria-live='assertive' region updating with error summary text on mutation error. Link each field error with aria-describedby. Focus first invalid field on submit failure. Map Problem Details messages to visible and announced text. Test with VoiceOver on Mac. Don't toast-only for critical form errors—toast may not announce reliably.

---

### 34. Routing (React Router).

**Short answer:** React Router handles client-side navigation, URL state, and data loading in SPA served by Spring Boot static or separate host. v6+ uses nested routes, loaders, and errorElement patterns. URL reflects resource ids matching REST /orders/:orderId for shareable links. Protected routes wrap JWT auth guard before rendering children. Browser history integration without full server round trip.

#### What it is
createBrowserRouter with route tree: /login public, /app/* authenticated layout. useParams, useSearchParams for Spring query sync. Navigate component for redirects after login. Outlet renders child routes in layout shell. Data routers can loader fetch before render—coordinate with Query.

#### How it works (internals)
Auth guard: if (!token) return <Navigate to='/login' />. Lazy route components for code split. loader optional—often useQuery in component instead. Basename if deployed under /app context path in Spring. 404 catch-all route for unknown paths.

#### When to use / when NOT to use
Multi-page feel in SPA. Deep linking to order detail from email notification. Interview: protect route and pass id to useOrder.

#### Production example
Spring forwards /* to index.html for SPA fallback except /api/**. Router basename matches server context. Role-based route elements check JWT roles claim. Breadcrumb from route handle metadata. Analytics page view on location change.

#### Common mistakes
- No SPA fallback—refresh 404 on /orders/1.
- Auth guard only client-side—server must still enforce JWT.
- State in router that belongs in URL filters.
- Missing error boundary on route errorElement.
- Hardcoded paths not using route constants.

#### Interview follow-ups (with model answers)

**Q:** Loader vs useQuery?
**A:** Loader runs before route renders—good for critical path data waterfall risk. useQuery colocates with component, cache shared globally. Many teams use Query only for simpler mental model. Hybrid: loader prefetchQuery into cache. Pick one pattern per codebase.

**Q:** Spring context path deployment?
**A:** Vite base: '/myapp/' and Router basename='/myapp'. API calls absolute /myapp/api or env VITE_API_URL. Asset paths must align or chunks 404. Test refresh on nested route in staging. Document in deployment guide.

#### Scenario probe
**Situation:** Refresh on /orders/42 returns 404 from Spring Tomcat.

**Model answer:** Configure ResourceHandler or WebMvcConfigurer forward to index.html for non-api routes. Or nginx in front routing /api to Spring and /* to static index. Verify context path and router basename match. Don't rely only on HashRouter unless legacy constraint. Integration test curl accepts HTML for SPA routes. Common Spring Boot + React deployment gotcha.

---

### 35. Auth in SPA + Java JWT.

**Short answer:** Auth SPA stores access token in memory; refresh via httpOnly cookie or secure backend exchange—avoid localStorage XSS theft. Java Spring Security OAuth2 resource server validates JWT on /api/**; React attaches Bearer header. Login flow: POST /auth/login or OIDC redirect; store tokens per security policy. Silent refresh before exp claim; 401 interceptor triggers refresh or logout. RBAC from JWT roles drives route guards and UI feature flags—not authorization source of truth.

#### What it is
Spring JwtDecoder validates signature issuer audience; method security @PreAuthorize on controllers. React decodes JWT payload for display only—never trust for security decisions without server check. Axios interceptor adds Authorization and handles 401 queue. Logout clears Query cache and auth context. CSRF less critical for pure Bearer SPA; cookie refresh needs CSRF token.

#### How it works (internals)
AuthProvider holds accessToken state; login mutation sets token. setInterval or schedule refresh at exp - 60s. ProtectedRoute checks isAuthenticated. Spring exposes /api/me for fresh user profile beyond JWT claims. PKCE for public SPA OIDC clients.

#### When to use / when NOT to use
Every enterprise SPA on Spring Security. Interview: token storage tradeoffs. Multi-tenant JWT tenant claim routing.

#### Production example
Access token memory; refresh httpOnly SameSite=Strict. Spring Resource Server + Keycloak or custom JWT. Role ADMIN sees admin routes; API still 403 if forged UI. Token refresh rotation detected server-side. Security audit passed on XSS token exfiltration test.

#### Common mistakes
- localStorage accessToken.
- Trusting client-side role check only.
- No refresh handling—random logouts at exp.
- JWT in URL query string.
- Logging tokens in console.

#### Interview follow-ups (with model answers)

**Q:** Handle 403 vs 401?
**A:** 401 unauthenticated—redirect login refresh token. 403 authenticated but forbidden—show permission denied stay logged in. Spring sends both correctly; client must not treat same. Problem Details type can distinguish. Log 403 for audit user attempted restricted action.

**Q:** OIDC with Spring?
**A:** SPA uses authorization code + PKCE with identity provider. Spring as resource server validating access token from IdP. Or Spring Authorization Server issuing tokens. React oidc-client-ts or Auth0 SDK patterns. Align token claims with @PreAuthorize expressions.

#### Scenario probe
**Situation:** Security scan flags JWT in localStorage; team asks migration path.

**Model answer:** Move access token to memory variable module; refresh via httpOnly cookie endpoint Spring controls. Short-lived access 15min; refresh rotation. XSS still dangerous but token not persistent in storage. Implement axios interceptor refresh queue. Coordinate Spring Set-Cookie flags Secure HttpOnly. Phased rollout with forced re-login acceptable.

---

### 36. CORS and why the SPA origin matters.

**Short answer:** CORS governs browser cross-origin requests from SPA origin to Spring API origin—server must emit Access-Control-Allow-Origin. Development: Vite proxy /api → localhost:8080 avoids CORS during dev. Production: explicit allowed origins not * when credentials. Preflight OPTIONS for JSON PUT with custom headers like Authorization. CORS is browser-only—curl and mobile apps unaffected.

#### What it is
Spring @CrossOrigin or WebMvcConfigurer addCorsMappings registry. allowCredentials true requires specific origins not wildcard. Expose headers for ETag, X-Request-Id if client reads them. Same-site deployment SPA and API one origin simplest—no CORS. Misconfigured CORS shows browser console error not 404.

#### How it works (internals)
Spring Security cors configurationSource bean integrated with security filter chain. Vite server proxy in vite.config for local. Env VITE_API_URL full URL when cross-origin prod. Test preflight with curl -X OPTIONS. JWT Authorization header triggers preflight—ensure allowed.

#### When to use / when NOT to use
SPA on CDN domain api.company.com separate from app.company.com. Interview: fix CORS error after deploy. Cookie refresh cross-origin needs SameSite=None Secure.

#### Production example
Allowed origins whitelist from config property spring.cors.allowed-origins. Same origin preferred via reverse proxy /api route. Staging CORS includes preview deploy URLs. No Access-Control-Allow-Origin * with credentials.

#### Common mistakes
- Disabling CORS security in prod with permitAll origins *.
- Forgetting OPTIONS permit in Security filter.
- Mismatch http vs https origin.
- Trying to fix CORS in React axios—server only.
- Wildcards with allowCredentials true invalid.

#### Interview follow-ups (with model answers)

**Q:** Vite proxy vs CORS?
**A:** Proxy makes browser think same origin—requests to /api forwarded to Spring dev port. Production build has no Vite proxy—need real CORS or same host. Don't ship proxy config to prod. Document dev vs prod networking for Java teammates. E2E tests may use similar proxy.

**Q:** CORS error but Postman works?
**A:** Postman not browser—no CORS enforcement. Proves API up; fix server headers for browser. Check exact Origin header value case-sensitive. Spring logs may show rejected preflight. Classic fullstack interview trap.

#### Scenario probe
**Situation:** New staging SPA cannot call Spring API; browser CORS blocked.

**Model answer:** Add staging SPA URL to Spring cors allowedOrigins list in config for that environment. Verify Security chain cors() enabled and OPTIONS permitted. Check Authorization header in allowedHeaders. If using cookies, allowCredentials and specific origin. Alternative: nginx same host /api proxy eliminating CORS. Reproduce with browser devtools network preflight inspect.

---

### 37. Environment config.

**Short answer:** Environment config injects API base URL, feature flags, and OIDC client id per deploy without rebuilding secrets into bundle. Vite uses import.meta.env.VITE_* prefixed vars from .env files at build time. Never embed DB passwords in frontend—only public config. Spring uses application-{profile}.yml; align profile naming dev/staging/prod. Runtime config via /api/config endpoint for flags that change without redeploy.

#### What it is
.env.development local; .env.production in CI with injected secrets for build not client secrets. import.meta.env.MODE distinguishes development production. Type env in env.d.ts for autocomplete. Spring @ConfigurationProperties for server-side only secrets. 12-factor config parity across stack.

#### How it works (internals)
VITE_API_BASE_URL=https://api.staging.example.com in CI pipeline. apiClient reads import.meta.env.VITE_API_BASE_URL. Feature flags: GET /api/features returns toggles from Spring Cloud Config. Docker build-arg passes VITE vars at image build. gitignore .env.local with developer overrides.

#### When to use / when NOT to use
Multi-environment deploy pipeline. Interview: what must not be in VITE_ vars. Switching OIDC issuer per tenant.

#### Production example
CI injects env per branch deploy. No secrets in git history—gitleaks scan. Runtime /api/config for kill switches. Spring profiles activate datasource; frontend only knows API URL. Config drift alert if staging points prod API.

#### Common mistakes
- REACT_APP_ prefix wrong for Vite projects.
- Committing .env.production with keys.
- Expecting runtime change of VITE_ without rebuild.
- Hardcoding localhost:8080 in source.
- Client-side API keys for private services.

#### Interview follow-ups (with model answers)

**Q:** Runtime vs build-time config?
**A:** VITE_ baked at npm run build—change needs rebuild. Runtime fetch /api/config or window.__ENV__ from server-injected index.html for rare dynamic needs. Spring can serve config.json from controller templated per deploy. Tradeoff: flexibility vs simplicity. Public OIDC client ids ok build-time.

**Q:** Align Java and React environments?
**A:** Same profile names in pipeline: deploy staging runs spring staging profile + Vite staging env file. Helm values or K8s config maps coordinate URLs. Smoke test hits correct API from built SPA. Documentation matrix environment × URL. Prevent manual mismatches.

#### Scenario probe
**Situation:** Production build still calls localhost:8080 API.

**Model answer:** CI missing VITE_API_BASE_URL injection—falls back to dev default in code smell. Fail build if env var unset in prod pipeline. grep dist assets for localhost before promote. Spring not involved in wrong URL—pure frontend build config. Add env.d.ts and config module single source getApiBase(). Post-deploy smoke test from external runner.

---

### 38. Forms and validation.

**Short answer:** Forms collect user input validated client and server before Spring persistence. React Hook Form + Zod provides performant controlled/uncontrolled hybrid and schema parity with Bean Validation. Server remains authoritative—422 Problem Details map to field errors. Complex forms: multi-step wizard, array fields for order lines FieldArray. Disable double submit; show pending state on mutation.

#### What it is
RHF register, control, handleSubmit, formState.errors. zodResolver shares schema with API parse layer where possible. Spring @Valid on @RequestBody returns standardized errors. Dirty/touched state drives unsaved navigation guard. reset on load from GET DTO.

#### How it works (internals)
useForm({ resolver: zodResolver(orderSchema), defaultValues }). onSubmit → mutateAsync → toast success → invalidate queries. onError parse Problem Details extensions. useFieldArray for dynamic lines matching List<OrderLineDto>. mode: 'onBlur' or 'onSubmit' per UX.

#### When to use / when NOT to use
Create order, settings profile, admin config screens. Interview: wire form to Spring POST with errors. Not for search box alone—simpler state ok.

#### Production example
Order create form 40 fields with Zod max matching @Size. Unsaved prompt react-router blocker when formState.isDirty. Submit idempotency-key header on create. Accessibility error summary component shared. E2E Playwright happy path + validation path.

#### Common mistakes
- Client-only validation skipping server round trip trust.
- Not clearing server errors on field edit.
- defaultValues missing on async load flash empty.
- Submit without preventDefault native form.
- Nested object path mismatch Jackson vs RHF names.

#### Interview follow-ups (with model answers)

**Q:** Field array for order lines?
**A:** useFieldArray({ name: 'lines' }) append remove move. Each line Zod object schema min 1 line validation. Spring expects JSON array matching DTO list. Key stable client ids for new lines. Performance ok RHF for dozens lines; virtualize display if needed.

**Q:** Async server validation?
**A:** zod refine async checking SKU exists GET /api/sku/{code}. Debounce async validators. Spring unique constraint violation returns 409 map to field error. setError from mutation onError. Don't block submit on slow async—show inline checking spinner.

#### Scenario probe
**Situation:** Users double-click Submit creating duplicate orders in Spring.

**Model answer:** Disable button isSubmitting from mutation.isPending immediately. Spring Idempotency-Key header on POST dedupe server-side. Optimistic UI lock form during submit. Debounce not enough—explicit pending guard. Audit logs show duplicate timing—confirm client fix + server idempotency belt and suspenders. RTL test double click submits once.

---

### 39. Optimistic concurrency in UI.

**Short answer:** Optimistic concurrency UI updates immediately assuming success, rolling back on server rejection—improves perceived speed for Spring mutations. Use If-Match etag or version field for optimistic locking matching JPA @Version. TanStack Query onMutate snapshot cache, onError restore, onSettled invalidate. 409 Conflict shows merge UI fetching latest entity. Don't optimistically update financial totals without server ack.

#### What it is
Client sets status SHIPPED in cache before PATCH returns; rollback if 409. Spring returns Problem Details with current version on conflict. Pessimistic UI waits for response—safer for payments. Linearizability vs UX tradeoff. User sees instant feedback; server truth wins on error.

#### How it works (internals)
useMutation({ onMutate: async (vars) => { await queryClient.cancelQueries; snapshot = getQueryData; setQueryData optimistic; return { snapshot }; }, onError: (err, vars, ctx) => setQueryData(ctx.snapshot), onSettled: invalidate }). Send If-Match: etag from loaded dto. UI shows pending indicator on optimistic row. Conflict modal: reload latest GET merge user edits.

#### When to use / when NOT to use
Toggle favorite, status chip, quantity stepper low risk. Avoid optimistic money movement. Interview: implement rollback on 409.

#### Production example
Order status optimistic with version check; 409 opens diff dialog. Comment add optimistic append rolled back on failure. Metrics track optimistic rollback rate signaling UX or API issues. Spring ConcurrentModificationException mapped to 409 Problem Detail.

#### Common mistakes
- Optimistic without version header—silent overwrite.
- No rollback leaving wrong UI until refresh.
- Optimistic on create without temp id strategy.
- Ignoring onSettled invalidate stale cache.
- Double optimistic from rapid clicks.

#### Interview follow-ups (with model answers)

**Q:** ETag vs version field?
**A:** Spring can emit ETag from entity version hash; client sends If-Match. Or explicit version integer in JSON body and header. Align OpenAPI docs which pattern. Both achieve optimistic locking. Frontend stores from GET response headers or body.

**Q:** User education on conflict?
**A:** Modal explains another user changed order; show diff fields. Actions: take theirs, retry mine, manual merge. Don't silent refresh losing user work. Log conflict for support. Reduce conflicts with short edit locks optional server feature.

#### Scenario probe
**Situation:** Two users edit order notes; last write wins losing first user's text silently.

**Model answer:** Add JPA @Version and require If-Match on PUT; second save gets 409. UI optimistic with rollback plus conflict modal showing both versions. Optional field-level merge for notes simple text. Real-time presence indicator advanced. At minimum: 409 toast with reload button not silent loss. Senior fullstack implements locking on Java and conflict UX on React together.

---

### 40. Realtime: poll vs SSE vs websocket.

**Short answer:** Realtime updates: polling simple; SSE server-push one-way; WebSocket bidirectional for chat or collaborative edit. Spring supports SseEmitter, STOMP over WebSocket, or reactive Flux. Choose by latency needs, infrastructure, and firewall compatibility. JWT auth on WebSocket via query param or STOMP headers—security review required. React Query refetchInterval is polling; EventSource for SSE.

#### What it is
Polling: GET /api/orders/{id}/status every 5s—easy, wasteful. SSE: text/event-stream push status changes; auto reconnect. WebSocket: STOMP subscriptions to topic /orders/{id}. SSE through HTTP proxies easier than WS sometimes. Backpressure and scale differ—Kafka behind Spring for fanout.

#### How it works (internals)
Polling: useQuery refetchInterval when tracking tab active only. SSE: useEffect EventSource with JWT in cookie same-origin. WebSocket @stomp/stompjs connect headers Authorization Bearer. Invalidate Query cache on message event ORDER_UPDATED. Cleanup close connection on unmount.

#### When to use / when NOT to use
Order tracking page minutes latency ok → polling or SSE. Live dashboard metrics → SSE or WS. Chat support widget → WS. Interview: tradeoffs table.

#### Production example
Shipment tracking SSE from Spring SseEmitter; reconnect backoff. Ops dashboard 30s polling sufficient reduced load. WS for internal admin live notifications with Redis pub/sub backend. Load balancer sticky sessions or shared message broker for WS scale.

#### Common mistakes
- Polling every 1s hammering Spring.
- WebSocket without reconnect on token refresh.
- SSE not handling browser connection limit.
- Not invalidating cache on push—stale UI.
- WS auth token in URL logged in server access logs.

#### Interview follow-ups (with model answers)

**Q:** SSE auth with JWT?
**A:** Cookie session same-origin simplest. Or short-lived SSE token from POST /api/sse-token. EventSource no custom headers in browser—limitation drives cookie pattern. Spring Security filter on SSE endpoint validates. Document security tradeoffs.

**Q:** When polling enough?
**A:** Low update frequency, few concurrent users, simplicity priority. refetchIntervalInBackground false saves battery. ETag conditional GET reduces payload. Upgrade to push when scale or latency requirements grow. Measure server load before adopting WS complexity.

#### Scenario probe
**Situation:** Order status page polls every second; DB CPU spiked.

**Model answer:** Increase interval to 15-30s with exponential backoff when status terminal. Migrate to SSE push on status change event from Spring domain listener. Pause polling when tab hidden Page Visibility API. Cache status in Query staleTime. Backend: index status query; don't full table scan per poll. Right-size transport before micro-optimizing React.

---

### 41. Testing: RTL vs enzyme.

**Short answer:** RTL (React Testing Library) tests components as users interact—queries by role, text, label—not implementation details. Enzyme shallow rendering and instance state access are legacy; RTL is standard with Jest/Vitest. MSW mocks Spring REST endpoints for integration-style component tests. Prefer userEvent over fireEvent for realistic keyboard/mouse. Senior tests assert Problem Details errors appear, not mock internal hooks.

#### What it is
render(<OrderForm />, { wrapper: QueryClientProvider }). screen.getByRole('button', { name: /submit/i }). waitFor expects async Query resolution. Enzyme find('.class') couples to structure—brittle. RTL encourages accessibility-aligned selectors.

#### How it works (internals)
Setup MSW handler GET /api/orders/1 returns fixture JSON. userEvent.type and click submit; expect PUT body. renderHook for useOrder with providers. Vitest + @testing-library/jest-dom matchers. Avoid testing useState call counts.

#### When to use / when NOT to use
Regression tests for forms, auth guard, error mapping. Interview: test login form validation. Not E2E replacement—Playwright for full stack.

#### Production example
80% RTL component + hook; 20% Playwright smoke. MSW shared fixtures from Java sample JSON in repo. CI parallel vitest run on PR. Removed Enzyme during migration 2023. Coverage on critical checkout path.

#### Common mistakes
- getByTestId everywhere ignoring roles.
- Not awaiting waitFor on async Query.
- Mocking axios instead MSW realistic HTTP.
- Testing implementation state not visible outcome.
- Snapshot-only tests low value.

#### Interview follow-ups (with model answers)

**Q:** MSW vs mocking useQuery?
**A:** MSW intercepts fetch at network layer—tests real api client and Query integration. Mocking useQuery skips hook logic under test. MSW handlers document API contract. Reset handlers between tests. Combine with unhandled request error in strict mode.

**Q:** Test 422 Problem Details?
**A:** MSW POST returns 422 application/problem+json body. Assert getByText field error message visible. aria-describedby linkage optional check. Ensures mapper function works end-to-end. Fixture matches Spring GlobalExceptionHandler output.

#### Scenario probe
**Situation:** Tests pass but production form error mapping broken after refactor.

**Model answer:** Tests mocked setError directly—didn't test Problem Details mapper. Rewrite integration test MSW 422 real payload through submit handler. Add contract test JSON fixture from Java integration test @Sql. Reduce enzyme-style shallow snapshots. RTL tests should fail when mapper breaks. Senior values realistic boundaries in tests.

---

### 42. `useRef` vs state.

**Short answer:** useRef holds mutable value across renders without triggering re-render—DOM refs, latest id for callbacks, interval ids. useState triggers re-render when UI must reflect new value. Don't store display data in ref to skip renders—users won't see updates. ref.current updated each render for stale closure escape hatch. forwardRef passes refs to child inputs for focus after Spring validation error.

#### What it is
const inputRef = useRef<HTMLInputElement>(null); inputRef.current?.focus(). Instance variable pattern in function components. Refs not for values that should appear on screen. useImperativeHandle exposes limited API on ref. Callback refs for dynamic mount measurement.

#### How it works (internals)
Track previous orderId in ref compare route changes side effects. WebSocket handler reads tokenRef.current. Avoid ref + forceUpdate hack—use state. RHF register merges ref with field ref. Cleanup clear interval stored in ref on unmount.

#### When to use / when NOT to use
Focus first invalid field on 422. Integrate non-React chart imperative API. Interview: ref vs state for timer count display.

#### Production example
Modal focuses primary button via ref on open. latestRequestId ref discards stale fetch. Scroll position restoration ref not state. No anti-pattern storing order list in ref.

#### Common mistakes
- Reading ref during render expecting reactive UI.
- ref as default useState lazy initializer confusion.
- Not null checking ref.current before DOM ops.
- Replacing state with ref to avoid re-renders on visible data.
- Stale ref not updated each render in callbacks.

#### Interview follow-ups (with model answers)

**Q:** useRef initial value only once?
**A:** useRef(initial) sets .current only on mount; changing initial prop doesn't update ref automatically. Assign ref.current = prop in render if need latest without re-render schedule. Different from useState prop sync via key remount. Document pattern in team guide. Lazy init useRef(() => expensive()) runs once.

**Q:** Ref forwarding to MUI TextField?
**A:** MUI inputRef or slotProps input ref depending version. Focus management for a11y after server error. Controller from RHF handles ref merge. Test focus in RTL jest.spyOn HTMLElement focus. Consistent pattern in design system wrapper.

#### Scenario probe
**Situation:** Counter display stuck at 0 while ref increments in setInterval.

**Model answer:** Display requires useState not ref—ref changes don't render. setCount(c => c + 1) in interval with cleanup clearInterval on unmount. If avoiding re-render for non-UI metric, ref ok but don't show ref value in JSX. Classic interview conflating ref persistence with reactivity. Fix interval deps and Strict Mode double mount awareness.

---

### 43. Batching.

**Short answer:** Batching groups multiple setState calls into one render for performance and consistency. React 18 batches in promises, timeouts, native events—not only React event handlers. Automatic batching reduces flicker updating multiple fields after single Spring response. flushSync escapes batching when integrating third-party DOM needing immediate paint. unstable_batchedUpdates legacy—default now.

#### What it is
Three setState in onClick → one render. await fetch then two setStates → batched React 18. Microtask batch improves INP. Concurrent features may interleave but state updates batch per event. React DOM legacy had more synchronous double renders.

#### How it works (internals)
Trust default batching; don't micro-optimize. After await mutate, multiple setStates batch—read state via functional updater not immediate read. flushSync rare: scroll sync measurement. startTransition updates batch separately low priority lane. Test rapid updates don't show intermediate inconsistent totals.

#### When to use / when NOT to use
Explaining why state not updated immediately after setState. Debugging double render in Strict Mode dev only. Interview: batching scope React 18.

#### Production example
Mapped Problem Details field errors loop setError—RHF batches internally. Removed manual unstable_batchedUpdates from React 17 migration. No flushSync in production paths except chart lib bug workaround documented.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Expecting synchronous state read after setState in same function.
- flushSync everywhere killing performance.
- Assuming React 17 behavior in async handlers.
- Multiple renders from separate roots not batched together.
- Confusing batching with concurrent interrupt.

#### Interview follow-ups (with model answers)

**Q:** setState in setTimeout batched?
**A:** React 18 yes in setTimeout and promise chains. React 17 only in React synthetic events. Upgrade motivation for enterprise apps. Still use functional updates after async. Test under 18 createRoot not legacy render.

**Q:** Multiple Query cache updates batch renders?
**A:** Each notify may schedule render but React batches in same tick. setQueryData multiple keys in onSuccess—usually one render pass. Profiler verify if perf issue split updates. Optimistic onMutate single setQueryData preferred. Align with React 18 root API.

#### Scenario probe
**Situation:** After await saveOrder(), logging orderStatus still shows old value before second log line.

**Model answer:** setState async scheduling—orderStatus variable is closure from render before update. Use functional setOrder or read from mutation response directly for next logic. useEffect on success flag if chained actions needed. Not a Spring delay—client state timing. Educate team on render snapshot vs pending update. Pattern: const saved = await mutateAsync(); use saved.status.

---

### 44. Portals and modals.

**Short answer:** Portals render children into DOM node outside parent hierarchy—modals, tooltips, toast overlays. createPortal(child, document.body) escapes overflow:hidden ancestors. Event bubbling still follows React tree not DOM tree—onClick on portal content bubbles to React parent. Focus trap and aria-modal on dialog portals for a11y. MUI Modal uses portal internally.

#### What it is
Modal markup lands under body; CSS z-index stacking controlled. React 17+ event delegation attaches to root—portal events work. Multiple portals compose z-index layers. Server HTML single root; portals client-only. Nested modal focus management complex.

#### How it works (internals)
Dialog component wraps children in createPortal with backdrop. useEffect focus first focusable on open return focus on close. Escape key closes calling onClose reset form. Confirm delete order portal over table still table in DOM underneath. ReactDOM.createRoot same for portal content.

#### When to use / when NOT to use
Any overlay blocking interaction with Spring-backed page beneath. Dropdown clipped by table container. Interview: why portal for modal.

#### Production example
Order cancel confirm portal; focus trapped. Toast notifications portal top-right aria-live. Print preview portal optional. z-index tokens design system 1300 modal 1400 toast.

#### Common mistakes
- Modal without focus trap tab escapes to background.
- Portal without aria-modal role dialog.
- Backdrop click closes losing unsaved form without confirm.
- z-index wars arbitrary 99999.
- SSR portal mismatch hydration—delay client only.

#### Interview follow-ups (with model answers)

**Q:** Portal event bubbling example?
**A:** Click button inside portal still triggers parent OrderPage onClick if not stopped—React fiber tree. stopPropagation in handler if unintended. Understand for debugging mysterious handlers. DOM parent is body but React parent is Modal wrapper. Differs from native DOM bubble only to body.

**Q:** Modal form submit to Spring?
**A:** Form inside portal submits via RHF handleSubmit same as inline. Portal doesn't affect fetch. onSuccess close portal invalidate queries. Keep portal mounted vs conditional render for animation libraries. Focus return to trigger button after close.

#### Scenario probe
**Situation:** Dropdown menu clipped inside scrollable order table container.

**Model answer:** Render menu via portal to document.body with position fixed calculated from anchor getBoundingClientRect. Or MUI Popper disablePortal false default portals. Don't only raise z-index inside overflow hidden parent. Close on scroll reposition. Keyboard navigation preserved. Common data grid UX fix.

---

### 45. CSS strategy.

**Short answer:** CSS strategy choices: CSS Modules, Tailwind utility, CSS-in-JS (Emotion), or design system (MUI) atop Spring-served SPA. Co-locate styles with components; avoid global leakage breaking admin tables. Design tokens for spacing color align with company brand Java PDF reports optional. Performance: Tailwind purge; avoid runtime CSS-in-JS cost if vitals matter. Senior pick one primary approach per monorepo consistency.

#### What it is
CSS Modules: import styles from './Order.module.css' scoped class names. Tailwind: utility classes in JSX rapid prototyping. MUI sx prop theme-driven consistent enterprise look. BEM legacy less common new React work. Dark mode via CSS variables or MUI theme palette.

#### How it works (internals)
Establish ADR: MUI + CSS modules for custom layouts. Theme provider wraps app matching corporate palette. Responsive breakpoints for field ops tablet order entry. Print stylesheet @media print for invoice view. Avoid !important wars; use theme overrides.

#### When to use / when NOT to use
Greenfield vs legacy global bootstrap.css migration. Interview: scale theming across micro-frontends. CLS fixes via consistent skeleton styles.

#### Production example
MUI theme from shared @company/ui-theme package monorepo. Tailwind only in marketing microsite separate deploy. CSS modules for performance-critical virtualized grid row height. Lint style import order. No inline style objects unmemoized on hot rows.

#### Common mistakes
- Three CSS paradigms in one repo.
- Global selectors breaking third-party widgets.
- Hardcoded hex not theme tokens.
- Runtime styled-components on 10k rows.
- Ignoring contrast a11y in custom CSS.

#### Interview follow-ups (with model answers)

**Q:** MUI vs Tailwind for Spring admin?
**A:** MUI gives accessible DataGrid DatePicker out of box—faster enterprise delivery. Tailwind more flexible brand unique marketing sites. Java teams often prefer MUI familiarity to Bootstrap. Bundle size tradeoff tree-shake imports. Hybrid: MUI components Tailwind layout grid rare.

**Q:** CSS modules with Vite?
**A:** Built-in support import styles camelCase locals. composes for variant classes. TypeScript *.module.css.d.ts codegen optional. Works with Spring static resource handler unchanged. Scoped avoids clash with legacy global CSS during migration.

#### Scenario probe
**Situation:** Order table row hover style inconsistent across modules.

**Model answer:** Centralize DataGrid theme overrides and shared TableRow component. Audit direct sx duplicates; extract to theme.components.MuiDataGrid. Design tokens document in Storybook. Deprecate one-off CSS files per feature. Java team consumes same Storybook link for UX review. Consistency via design system not per-dev CSS.

---

### 46. SSR / Next vs CRA/Vite SPA.

**Short answer:** SSR/Next.js renders React on server—faster FCP SEO public pages; hydration matches client. Vite SPA client-only render index.html shell fetch JWT then data—simpler deploy behind Spring. Internal B2B order apps often Vite SPA sufficient; marketing docs maybe Next. Next can BFF API routes; Spring remains system of record REST. Trade deploy complexity hydration bugs vs SEO vitals.

#### What it is
Next App Router RSC server components fetch on server no client bundle for static parts. Vite SPA: empty root div ReactDOM.createRoot render App. SSR needs Node runtime or edge; Spring Boot serves static only cheaper. Auth cookies easier SSR; Bearer SPA common. Hydration mismatch when server HTML != client first render.

#### How it works (internals)
Choose Vite when authenticated SPA no SEO—all users login. Next when public catalog SEO + authenticated enclave. Spring serves Vite dist from classpath or CDN. Next standalone docker separate from Spring API. Shared OpenAPI types monorepo either way.

#### When to use / when NOT to use
Interview: when not to adopt Next for Java shop. Public landing + app split architecture. LCP requirements on marketing.

#### Production example
B2B orders Vite SPA Spring JWT—no SSR need. Public product catalog Next ISR calling Spring public API. Two deployables coordinated release train. Avoid SSR for heavy session-specific dashboards.

#### Common mistakes
- Next for purely internal admin adding ops burden.
- SSR fetch without forwarding auth cookies correctly.
- Hydration error from Date formatting locale server vs client.
- Duplicating business logic Next server and Spring.
- Ignoring Spring team skill gap on Node hosting.

#### Interview follow-ups (with model answers)

**Q:** Serve Vite from Spring Boot?
**A:** Copy dist to src/main/resources/static; mvn package single jar deploy. Or nginx serves static Spring only /api. Cache immutable assets long index.html short. Context path alignment. Simple ops favored by Java teams.

**Q:** RSC impact on Java API?
**A:** Server components fetch Spring REST server-side—no browser CORS. Secrets stay server; client components hydrate interactive parts. Still same DTO contracts Zod optional server parse. Increases Next complexity question 52. Not required for typical internal SPA.

#### Scenario probe
**Situation:** Team proposes Next.js for internal order admin used only after SSO login.

**Model answer:** Push back gently: no SEO benefit; SSR adds hosting Node hydration cost vs Vite+Spring jar. JWT SPA pattern well understood; faster delivery. Suggest Vite unless public pages same repo need ISR. If vitals on login dashboard poor, fix data fetching not necessarily SSR. Document ADR decision criteria. Senior pragmatism over hype.

---

### 47. Monorepo: UI + Java.

**Short answer:** Monorepo houses UI packages and documents Java API contracts—pnpm workspaces Nx Turborepo. Shared @company/api-types from OpenAPI; ui-components; apps/order-spa; services/order-api Spring module. Atomic PRs update DTO and consumer together. CI affected builds only changed packages. Version alignment React types across micro-frontends if federation.

#### What it is
packages/api-client generated fetch wrappers. apps/web Vite depends workspace:*. Java Maven module sibling or separate repo git submodule less ideal. Changesets semver internal packages. Single lint/tsconfig base.

#### How it works (internals)
openapi-generator in packages/api-types triggered by springdoc artifact. Turbo pipeline build dependsOn ^build. Docker multi-stage build web then copy to Spring resources optional. CODEOWNERS frontend backend paths. Local dev concurrently spring-boot:run and vite proxy.

#### When to use / when NOT to use
Multiple SPAs sharing design system. Interview: prevent API drift. Java + TS coordinated releases.

#### Production example
Nx monorepo 3 apps 5 packages Java in /backend folder. PR checks: mvn test + turbo test typecheck. Published internal npm registry for ui-components. OpenAPI break fails both sides CI.

#### Common mistakes
- Monorepo without affected CI—slow builds.
- Duplicated OpenAPI in two packages diverging.
- Java outside repo sync manual.
- Circular deps web imports server code.
- Inconsistent package manager lockfiles.

#### Interview follow-ups (with model answers)

**Q:** Monorepo vs polyrepo?
**A:** Monorepo wins shared types atomic changes small team cohesion. Polyrepo independent deploy cadence larger org boundaries. Java Spring often separate release cycle—contract tests bridge. Monorepo with Maven + pnpm tooling learning curve. Pick org culture fit.

**Q:** Generate TS from springdoc?
**A:** springdoc-openapi exports /v3/api-docs; CI job openapi-typescript generates types. Commit generated or generate on install debatable. Breaking change fails TS build consumer. Same artifact version as Docker image tag. Gold standard for fullstack monorepo.

#### Scenario probe
**Situation:** Frontend OrderDto missing field for two weeks until production bug.

**Model answer:** Implement OpenAPI codegen pipeline gated in monorepo CI. Java PR changing DTO must include regenerated types same PR. Contract test fixture JSON roundtrip. Zod runtime safety net additional. Process fix more than tooling alone. Retro: why manual copy allowed—update contributing guide.

---

### 48. Memory leaks in SPAs.

**Short answer:** Memory leaks in SPAs: uncleared intervals, subscriptions, event listeners, growing caches, detached DOM references. useEffect cleanup mandatory for WebSocket STOMP, EventSource SSE, setInterval polling. TanStack Query gcTime retires unused cache; unbounded setState accumulation in global store leaks. Third-party charts and maps need destroy on unmount. Chrome heap snapshot diagnose retained OrderDto arrays.

#### What it is
Leak symptom: tab slows after hours on order tracking page. Forgotten addEventListener window resize without remove. Closure holding large order history array in module scope. Query cache infinite pages never gc if always mounted observer. Detached DOM nodes from portal bugs rare.

#### How it works (internals)
useEffect return () => { clearInterval; ws.close(); abort.abort() }. Pause polling visibilitychange hidden. Limit infinite query pages maxPages option. Avoid storing full audit log in Zustand append forever. DevTools Memory compare heap after navigate away.

#### When to use / when NOT to use
Long-lived kiosk dashboards. Realtime pages open all day. Interview: find leak in polling effect.

#### Production example
Fixed STOMP not disconnected on route leave—major leak. Query gcTime 5min default tuned. Chart destroy in useEffect cleanup Highcharts. ESLint rule report missing effect cleanup patterns code review.

#### Common mistakes
- setInterval no clear on unmount.
- Global event bus listeners never off.
- Infinite scroll fetchNextPage without max cache.
- Retaining DOM refs in module cache Map.
- Third-party lib init without dispose.

#### Interview follow-ups (with model answers)

**Q:** Query cache memory growth?
**A:** Each queryKey entry holds data; infinite lists accumulate pages. gcTime garbage collects inactive queries after unmount delay. maxPages in useInfiniteQuery trims oldest. select narrow data stored. Monitor Query devtools cache size long session test.

**Q:** Leak vs just large legitimate memory?
**A:** Leak grows unbounded with navigation cycles same action. Large dataset intentional—paginate virtualize instead. Heap snapshot dominators retained size climbing repeated route enter exit signals leak. Performance.memory chrome dev only approximate. Reproduce scripted Playwright loop.

#### Scenario probe
**Situation:** Browser tab RAM 2GB after 8 hours on live order board with WebSocket.

**Model answer:** Profile: WS messages appending to React state array without cap—leak by growth. Replace with ring buffer last 500 events or only latest status map by orderId. Verify WS disconnect on unmount route change. Query invalidate not duplicate push handler registrations. Spring may flood events—client throttle. Heap snapshot dominator tree find retained arrays.

---

### 49. Senior component design.

**Short answer:** Senior component design: single responsibility, colocated state, clear props API, composition over configuration explosion. Container hooks fetch Spring data; presentational components pure render OrderRow. Avoid prop drilling via composition slots; avoid premature abstraction HOC hell. Error loading empty states explicit—not null returns. Document component contract Storybook with MSW fixtures.

#### What it is
Smart OrderDetailPage uses useOrder; dumb OrderHeader receives order DTO. Discriminated props: status='loading' | 'error' | 'success' typed. Children composition for actions toolbar. Stable public API semver internal packages. Align naming with domain ubiquitous language from Java DDD.

#### How it works (internals)
Extract when second use case needs same UI chunk. Props minimal pass ids let child query vs pass full dto tradeoff document. forwardRef and aria props on design system primitives. Co-locate styles tests stories adjacent file. Refactor God component incremental strangler.

#### When to use / when NOT to use
Design system governance. Interview: refactor 600 line component sketch. PR review architecture feedback.

#### Production example
Order module folder features/orders/components hooks api. Barrel exports controlled avoid circular imports. Storybook visual regression Chromatic optional. Architecture decision records for patterns.

#### Common mistakes
- Props booleans isAdmin isEdit isCompact combinatorial explosion.
- Fetching in every leaf component.
- No empty state UX.
- Leaking Query types into design system.
- Over-abstracting SingleButtonFactory.

#### Interview follow-ups (with model answers)

**Q:** Pass DTO vs id prop?
**A:** Pass id when child can Query subscribe independently cache fresh. Pass DTO when parent already has snapshot read-only display avoid waterfall. Pass partial Pick<OrderDto,'id'|'status'> minimal coupling. Document per component. Invalidation updates Query child auto.

**Q:** Feature folder vs type folder?
**A:** Feature colocation scales teams orders team owns folder. Type-based components all together crosses features hard navigate. Shared ui/ for generic Button. Java modular monolith parallel bounded context folders. Consistency beats dogma.

#### Scenario probe
**Situation:** OrderCard has 25 props and 4 boolean mode flags.

**Model answer:** Refactor to composition OrderCard with subcomponents or variant prop discriminated union mode: 'summary' | 'detail'. Move data fetching to parent hook pass single order object. Replace isX flags with single layout enum. Storybook each variant. Apply open-closed principle extend via children slots not new booleans. Java reviewer appreciates smaller public surface.

---

### 50. What they want from a Java senior on React.

**Short answer:** Java senior needs React fluency not framework encyclopedia: rendering model, hooks rules, TypeScript at API boundary, auth JWT SPA, forms validation Problem Details, React Query server state, testing RTL, performance basics virtualization vitals. Map concepts to known patterns: DI→context, DTO→types+Zod, Controller→route+mutation, optimistic lock→If-Match. Read component code review PRs guide juniors on effect bugs. Own fullstack features endpoint to UI without blocking on frontend specialist. Stay current React 19 Query v5 gradually.

#### What it is
Depth on state management split server vs UI. Debug stale closure and effect deps independently. Spring Security + SPA integration hands-on. Not CSS expert but use design system. Architectural tradeoffs SSR monorepo micro-frontend awareness.

#### How it works (internals)
Build one vertical slice order CRUD end to end. Pair with frontend lead on patterns ADR. Run axe and Lighthouse on feature. Participate on-call for UI errors Sentry. Mentor mapping Java layers to React folders.

#### When to use / when NOT to use
Hiring bar fullstack senior. Self-assessment Java lead moving to product team. Interview meta question closing loop.

#### Production example
Successful Java seniors ship React features with review turnaround same as Java. They propose BFF when SPA needs aggregation not blame frontend. They enforce OpenAPI contract discipline both sides.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- Treating React as 'just JS templates' ignoring hooks model.
- Skipping client validation thinking server enough.
- Ignoring browser security CORS XSS token storage.
- Refusing to learn TypeScript strict.
- Over-engineering Redux day one.

#### Interview follow-ups (with model answers)

**Q:** Learning path 30 days?
**A:** Week1 TS strict + React official docs hooks. Week2 TanStack Query build list detail against Spring Boot tutorial API. Week3 RHF Zod forms Problem Details. Week4 RTL tests auth route guard. Daily small commits vertical slice beats tutorial hell.

**Q:** Red flags in React PR from backend dev?
**A:** Fetch in useEffect no cleanup. any types on API responses. JWT localStorage. Missing keys on lists. Constructive review teach patterns not block without guidance.

#### Scenario probe
**Situation:** Java architect asks what minimum React knowledge for team owning UI+API.

**Model answer:** Rendering and hooks mental model, TypeScript boundary validation, Query for REST, forms with server errors, JWT SPA security basics, RTL smoke tests, performance pagination virtualization awareness. Not required: CSS wizard, webpack internals, every new RFC. One shared vertical slice proof standard. Ongoing learning via PR review and incremental features. Parity: expect frontend to read Spring controllers same way.

---

### 51. React 19: `use` hook, Actions, and form `action` prop

**Short answer:** React 19 introduces use() to read promises and context during render with Suspense integration. Actions are functions passed to form action prop or useTransition-wrapped mutations handling pending state automatically. useFormStatus reads parent form pending from action submission. useOptimistic simplifies optimistic UI for lists during server action resolution. Spring teams still POST JSON from actions but gain progressive form UX patterns.

#### What it is
const data = use(orderPromise) suspends until promise resolves—caller provides promise from cache or loader. <form action={submitOrderAction}> where action async receives FormData. useActionState returns [state, dispatch, isPending] for action reducers. Ref callback cleanup and document metadata tags also React 19. Interop with existing axios Spring APIs via wrapping in action function.

#### How it works (internals)
submitOrderAction: async (formData) => { const res = await fetch('/api/orders', { method:'POST', body: JSON.stringify(...) }); if (!res.ok) return { error: await res.json() }; return { success: true }; }. useActionState reducer maps Problem Details to form state. use(promise) in child with Suspense boundary parent. Combine useOptimistic for cart line qty while action pending. Gradual adoption alongside React Query not wholesale replace.

#### When to use / when NOT to use
Greenfield forms wanting built-in pending without manual isSubmitting. Interview: contrast action vs RHF onSubmit. Reading promises from cache with use hook pattern.

#### Production example
Pilot React 19 on internal tool order quick-create form action. Still validate with Zod inside action before Spring call. Query invalidation after successful action in action tail. Feature detect React version in shared libs.

#### Common mistakes
- Assuming actions replace need server validation.
- use promise without Suspense boundary crash UX.
- Mixing uncontrolled form action with conflicting RHF same form.
- Ignoring isPending accessibility disable submit.
- Throwing in action without error boundary handling.

#### Interview follow-ups (with model answers)

**Q:** Actions vs TanStack Query mutation?
**A:** Actions excel form-centric pending useFormStatus native integration. Query mutations superior cache invalidation dedup background refetch enterprise data grids. Hybrid: action calls api module then queryClient.invalidateQueries. Don't rip Query for actions hype. Pick per use case in same app.

**Q:** use hook with Spring fetch?
**A:** Wrap cached promise in Query or context provider parent creates promise once per key. Child use(promise) suspends—coordinate error handling error boundary on reject. Still parse JSON with Zod after resolve inside promise factory. Pattern emerging less mature than useQuery—evaluate stability. Works well with RSC server passing promise prop future architectures.

#### Scenario probe
**Situation:** Team migrating to React 19 asks whether to replace all forms with action prop.

**Model answer:** Selective adoption: simple create forms benefit actions + useFormStatus; complex multi-step order wizard keep RHF+Zod. Actions must still call Spring with JWT and map Problem Details—wrap existing api client. Pilot one form measure DX not big bang. Query remains for reads and cache orchestration. Document standards when action vs mutation. Senior guides incremental migration not rewrite.

---

### 52. React Server Components vs Client Components — when to split

**Short answer:** RSC (React Server Components) run on server only—zero client bundle for static structure fetching Spring on server. Client Components marked 'use client' for hooks interactivity—default in Vite SPA everything client. Split: server fetch OrderSummary list; client OrderActions button mutations. Next App Router primary RSC host; Java API called from Node server component no browser exposure. Boundary discipline prevents leaking hooks into server files.

#### What it is
Server component async function OrderList() { const orders = await fetch(`${SPRING_URL}/api/orders`); return <ul>...</ul> }. Cannot useState useEffect in server component. Client child imports interactivity islands. Serialization props from server to client must be JSON-safe plain objects. Spring credentials on server fetch env not VITE_.

#### How it works (internals)
Mark interactive OrderApproveButton 'use client' receiving orderId prop. Server layout wraps chrome; client providers QueryClient inside client boundary only. Share types monorepo; server may use zod parse before passing props. Revalidate cache tags Next fetch options mapping Spring cache headers optional. Vite SPA teams skip RSC until product needs SEO SSR.

#### When to use / when NOT to use
Next migration public+app combined repo. Interview: explain use client directive why. Not for pure internal Vite deploy.

#### Production example
Hybrid marketing Next RSC product pages; order app remains Vite SPA Spring JWT. Shared OpenAPI types both. Server components call internal Spring VPC URL not public internet.  In production, measure latency, error budgets, and on-call burden. Document rollback paths and test negative paths in CI.

#### Common mistakes
- use client on root wrapping entire app defeating RSC.
- Passing functions class instances server to client props.
- Secrets in client component fetch.
- Expecting RSC in Vite without framework support.
- Waterfall sequential server fetches unoptimized.

#### Interview follow-ups (with model answers)

**Q:** RSC vs BFF Spring?
**A:** RSC server fetch similar BFF aggregation but in React Node layer. Spring BFF still valid Java-centric teams avoid Node server. Can combine Spring BFF for complex orchestration RSC consumes one endpoint. Operational ownership split consideration. Not duplicate business rules both layers.

**Q:** Client boundary placement?
**A:** Push use client leaves deep as possible maximize server tree. Provider shells often thin client wrapper children server when framework allows composition patterns. Interactive leaves only. Bundle analyzer shows client JS size drop. Tradeoff debugging complexity increased.

#### Scenario probe
**Situation:** Developer adds useState to Next server component OrderPage.tsx build fails.

**Model answer:** Extract interactive slice to OrderPageClient.tsx with 'use client' useState; server page fetches data passes props. Or move state to URL search params server readable. Teach server vs client capabilities table. Fetch orders server component pass serializable DTO to client form. Align with Spring call in server async component try catch Problem Details map error page.

---

### 53. TanStack Query v5: query keys, staleTime, invalidation, optimistic updates

**Short answer:** TanStack Query v5 uses queryKey arrays as hierarchical cache identity—include tenant id filters pagination. staleTime fresh window no refetch on mount; gcTime (formerly cacheTime) garbage collection after unused. invalidateQueries marks stale triggers refetch active queries—post mutation standard. Optimistic updates via onMutate setQueryData rollback onError. Align keys with Spring resource model orders list orders detail id.

#### What it is
queryKey: ['orders', { status, page }] serializable stable. staleTime: 0 always stale refetch default; 60000 for reference data. invalidateQueries({ queryKey: ['orders'] }) broad prefix match. setQueryData(['orders', id], updater) surgical cache patch. queryClient.prefetchQuery on hover row.

#### How it works (internals)
Factory keys: orderKeys.list(filters) orderKeys.detail(id) consistency. Mutation createOrder onSuccess invalidateQueries orderKeys.lists() setQueryData detail. Optimistic toggle: onMutate snapshot cancelQueries setQueryData inverted boolean onError restore. placeholderData keepPreviousData pagination UX v5 placeholderData fn. enabled: !!id guard queries.

#### When to use / when NOT to use
Standardize cache patterns code review. Interview: design keys multi-tenant JWT tenantId claim. Debug stale UI after mutation.

#### Production example
Key factory module prevents typos invalidation misses. staleTime per domain catalog 5min orders 30s. Optimistic status with version rollback 409. Devtools staging only. Metrics slow queries correlate Spring latency.

#### Common mistakes
- queryKey missing filter params wrong cache slice.
- invalidateQueries too narrow detail updates list stale.
- Object key unstable new reference each render.
- Optimistic without cancelQueries race.
- Confusing staleTime with gcTime.

#### Interview follow-ups (with model answers)

**Q:** Multi-tenant query keys?
**A:** Include tenantId from JWT first element ['tenant', tenantId, 'orders', id]. Logout removeQueries entire cache prevent leak across tenants same browser. Spring validates tenant server-side keys UX isolation only. Switch tenant invalidate all. Test tenant A data not flash tenant B.

**Q:** optimisticUpdate helper v5?
**A:** Still manual onMutate pattern; community recipes wrap helper. onMutate async cancel snapshot update return context. onError rollback context.snapshot. onSettled invalidate regardless. Type context with TypeScript generic MutationContext.

#### Scenario probe
**Situation:** After creating order list doesn't show new order until manual refresh.

**Model answer:** createOrder mutation missing invalidateQueries(['orders']) or setQueryData on list cache append. Verify queryKey factory list key matches list query exactly including filters. If staleTime infinite list thinks fresh—still invalidate on mutation. onSuccess navigate to detail not enough for list cache. Add test MSW mutation then assert list query refetch. Document invalidation matrix per mutation Java OpenAPI operations.

---

### 54. Zustand vs Redux Toolkit vs React Context for global state

**Short answer:** Zustand minimal global client store subscribe selector no boilerplate—cart UI prefs. Redux Toolkit structured actions slices devtools time-travel—large teams complex client state audit workflows. Context for low-frequency theme auth display—not server data. TanStack Query owns Spring server entities—don't duplicate orders in Redux. Pick Zustand most Java teams for simplicity; RTK if existing investment or middleware needs.

#### What it is
Zustand create((set) => ({ count: 0, inc: () => set(s => ({ count: s.count+1 })) })). RTK createSlice reducers configureStore. Context re-render all consumers on any value change. Zustand useStore(s => s.cart) selector granular. Persist middleware localStorage non-sensitive only.

#### How it works (internals)
Cart slice Zustand addLine removeLine sync optional POST cart Spring session. RTK if undo history command pattern client-side. Auth display user Zustand set on login clear logout Query remove. Avoid three stores same data—diagram state ownership. Devtools Redux for debug; Zustand middleware simpler.

#### When to use / when NOT to use
Cross-route UI state not in URL. Interview: why not Redux for everything. Migration from legacy Redux app.

#### Production example
Zustand cart sidebar badge; Query order entities. Rejected Redux for greenfield 2024. Legacy admin still RTK slowly strangler. Document decision ADR state management.

#### Common mistakes
- Redux storing server list duplicated Query.
- Context for high-frequency cart updates.
- Zustand store god object 50 fields.
- Persist JWT in Zustand localStorage.
- No clear logout cache clear all stores.

#### Interview follow-ups (with model answers)

**Q:** Zustand vs Context performance?
**A:** Zustand selectors prevent unrelated re-renders; Context lacks selector default. Context fine rare auth theme updates. use-context-selector mitigates Context cost. Measure before choosing; Zustand tiny bundle. Java devs appreciate Zustand simplicity vs Redux ceremony.

**Q:** RTK Query vs TanStack Query?
**A:** RTK Query integrates Redux ecosystem; TanStack framework agnostic lighter. Don't run both duplicate caches. TanStack more community SPA Spring examples. RTK Query good if already Redux for UI state heavy app. Pick one data fetching layer.

#### Scenario probe
**Situation:** Team debates Redux for new order SPA with TanStack Query already adopted.

**Model answer:** Skip Redux unless complex client-only workflow state machines undo needing RTK devtools—use Zustand slices for cart filters UI. Query already solves server cache Redux adds boilerplate duplication risk. YAGNI for enterprise CRUD dominant app. If audit action log client-side rare consider RTK middleware. ADR: Query + Zustand default stack. Java parallel: don't add second ORM for same tables.

---

### 55. React Hook Form + Zod resolver pattern with Spring Problem Details errors

**Short answer:** React Hook Form + Zod client validation aligned with Spring @Valid; server returns RFC 7807 Problem Details field errors mapped to setError. Spring 6 ProblemDetail builder type title status detail instance properties extensions fieldErrors. Unified error UX toast global field-level inline. Content-Type application/problem+json negotiation. Senior owns exception handler + frontend mapper contract test.

#### What it is
zodResolver(orderSchema) client; @Valid OrderCreateDto server. ProblemDetail properties fieldErrors: [{ field: 'customer.email', message }]. mapProblemToRHF converts path customer.email to nested RHF name. GlobalExceptionHandler @ControllerAdvice standardizes 422 body. Swagger documents problem schema.

#### How it works (internals)
handleSubmit → mutate → onError if isProblemDetails(err) mapFieldErrors(setError). Spring: problemDetail.setProperty('fieldErrors', list). Show Alert role=alert summary + per field aria-describedby. Clear field server error onChange field.onChange wrap. Log correlation instance URI to Spring trace.

#### When to use / when NOT to use
Every form POST PUT to Spring. Interview: implement mapper function. Harmonize validation messages product copy.

#### Production example
Shared @company/problem-details TS type + Java record. Fixture 422 JSON in both JUnit and vitest. i18n message codes optional extension. Never expose stack trace Problem Details prod.

#### Common mistakes
- Different field path conventions Java bean vs RHF name.
- Generic 400 without structured fieldErrors.
- Client Zod messages English server German mismatch.
- Ignoring non-field errors type business-rule. 
- Parsing HTML error page Spring Security 403.

#### Interview follow-ups (with model answers)

**Q:** Bean Validation to Problem Details?
**A:** MethodArgumentNotValidException handler iterates BindingResult field errors map to fieldErrors array. ObjectError global add to detail or extensions globalErrors. Use field path customer.address.zip consistent JSON serialization. @Valid nested @Valid children errors bubble paths. Unit test handler JSON snapshot.

**Q:** Zod refine cross-field match Spring @AssertTrue?
**A:** Zod superRefine enforces endDate after startDate client; @AssertTrue method on DTO server duplicate rule acceptable defense depth. Map class-level error to root setError or form level banner. Problem Details extension code DATE_RANGE_INVALID. Keep messages aligned copy deck. Server wins if client bypassed.

#### Scenario probe
**Situation:** Spring returns fieldErrors but React form doesn't highlight shipping.zip.

**Model answer:** Debug path mapping: Java may return shipping.zip RHF expects shipping.zip nested object—verify setError path with dots vs bracket notation. Log raw Problem Details body network tab. Add integration test fixture. Fix GlobalExceptionHandler to emit consistent path format documented OpenAPI. useForm shouldUseNativeValidation false. Fullstack fix not frontend-only hack string replace.

---

### 56. `useTransition` and `useDeferredValue` for search/filter UX

**Short answer:** useTransition marks state updates non-urgent—keep search input responsive while deferred filter results re-render heavy table. useDeferredValue lags behind prop/state value letting UI show stale results briefly with isPending indicator. Pair with Spring GET debounced Query queryKey including deferred term. Don't confuse with debounce alone—transition deprioritizes render work browser stays interactive. Essential order search 5k client rows or expensive child memo trees.

#### What it is
const [isPending, startTransition] = useTransition(); startTransition(() => setFilter(q)). const deferredFilter = useDeferredValue(filter); pass deferredFilter to MemoizedTable. isPending true while transition outstanding show subtle spinner in results. Concurrent rendering feature requires createRoot. Input stays synced to filter immediate; table uses deferred.

#### How it works (internals)
Search input onChange updates filter state immediately; startTransition wraps setResultsFilter or derived state. Child OrderTable receives deferredFilter; useMemo filter orders by deferredFilter. Combine Query enabled debounce 300ms queryKey ['orders', deferredFilter]. Show isPending overlay on table not input. Abort prior fetch on new deferred value.

#### When to use / when NOT to use
Typing lag on large in-memory lists post-Spring fetch. Faceted filter multiple dimensions expensive render. Interview: implement search without input stutter.

#### Production example
Order admin search useDeferredValue + server pagination reduced INP 200ms. Removed synchronous filter blocking keystrokes. Profiler confirmed transition moved long task off input path. Still debounce API not every deferred value if costly Spring query.

#### Common mistakes
- Deferring input value itself—users feel lag typing.
- useDeferredValue without memo child still re-renders expensive parent.
- Ignoring isPending UX feedback.
- Transition on server fetch not render—misplaced expectation.
- Client filter huge dataset—fix pagination first.

#### Interview follow-ups (with model answers)

**Q:** useTransition vs debounce?
**A:** Debounce delays state update timing; transition updates state immediately but deprioritizes dependent expensive render. Input uses raw value; list uses deferred—best combo. Debounce API reduces Spring load; transition helps client render. Use both layers appropriately. Measure INP improvement.

**Q:** useDeferredValue vs useMemo filter?
**A:** useDeferredValue delays value seen by children; useMemo recalculates when deps change synchronously unless deps deferred. Pattern: deferredFilter dep in useMemo filtered = orders.filter deferredFilter. Deferred value drives memo dep lagging. Don't double memo unnecessarily. Virtualize filtered output still.

#### Scenario probe
**Situation:** Order filter input lags characters appearing when table has 3000 rows client-side.

**Model answer:** Input must update synchronously—bug likely sets filter only inside transition including input binding wrong variable. Split: queryInput immediate; deferredQuery for table filter via useDeferredValue(queryInput). Virtualize table; push filter to Spring GET ?q= with debounce. Profiler verify input handler <16ms. Remove client 3000 row anti-pattern if possible Pageable server. Transition fixes render scheduling not data volume alone.

---

### 57. React Compiler (React Forget) — what changes for memo/useMemo

**Short answer:** React Compiler (Forget) auto-memoizes components and hooks at compile time proving purity—reduces manual useMemo useCallback React.memo. Rules of React: components hooks must be pure no mutations during render. Adoption via babel-plugin-react-compiler on Vite Babel pipeline experimental flag. Java teams benefit less manual perf boilerplate focus domain code. Still profile; Compiler doesn't replace virtualization or server pagination.

#### What it is
Compiler analyzes data flow inserts memo cache where safe. Impure components opt-out 'use no memo' directive if needed. Requires strict mode patterns no direct mutation props state. Facebook internal production Meta apps; OSS rollout progressing. DevTools may show Memo✨ compiled indicator future.

#### How it works (internals)
Enable plugin gradual module allowlist. Fix violations Compiler flags mutating props during render. Remove redundant manual memo after verified equivalent perf. CI benchmark subset routes regression. Stay on supported React 19 version.

#### When to use / when NOT to use
Evaluating after React 19 upgrade stable Compiler release. Interview: what purity Compiler assumes. Reducing memo noise codebase maintenance.

#### Production example
Pilot enabled on design system package only staging. Keep manual memo hot paths until benchmarks confirm. Document opt-out components integrating mutable third-party libs. Watch release notes breaking changes plugin version pin.

#### Common mistakes
- Assuming Compiler fixes all perf issues.
- Mutating Spring DTO in render breaking Compiler assumptions.
- Removing all memo before measurement.
- Enabling globally day one production without pilot.
- Ignoring purity lint violations.

#### Interview follow-ups (with model answers)

**Q:** Compiler vs manual memo coexistence?
**A:** Manual memo harmless often ignored if redundant Compiler smarter. Remove gradually after Profiler parity. Edge cases custom arePropsEqual may remain manual. Don't fight Compiler with impure patterns. Team training purity rules essential.

**Q:** Purity example violation?
**A:** orders.sort() mutating props array during render—breaks purity and Compiler. Fix: [...orders].sort() new array. Date.now() in render impure—move to state effect. Fetching render impure—use Query. Java immutable DTOs help frontend purity.

#### Scenario probe
**Situation:** Team enabled React Compiler and build warns mutating props in OrderTable sort.

**Model answer:** Fix purity: copy before sort useMemo deps orders sortKey. Never mutate OrderDto[] from Query cache in place—invalidate or setQueryData new sorted copy if needed client-side. Prefer Spring ?sort= param server-side. Compiler warning is gift catching latent bugs. After fix re-run benchmark may remove manual useMemo sort. Educate immutability aligns Java records best practice.

---

### 58. Micro-frontends: module federation basics for Java teams

**Short answer:** Micro-frontends split UI by domain team deploy independently; Module Federation (Webpack/Vite federation plugin) shares runtime react react-dom singletons between shell and remotes. Java teams host shell Spring Boot serving container app loading remoteEntry.js from orders remote CDN. Independent release orders team without redeploying shell if contract versioned shared dependencies aligned. Costs: operational complexity duplicate routing auth consistency integration testing. Use when org scale justifies—not default small team monolith SPA.

#### What it is
Host app exposes nothing remotes expose ./OrderApp ModuleFederationPlugin. import('orders/OrderApp') dynamic remote at runtime. shared: { react: { singleton: true, requiredVersion } } prevents duplicate React invalid hooks. Vite @originjs/vite-plugin-federation or module-federation vite alternative. Spring API remains shared backend; MFEs client only split.

#### How it works (internals)
Shell handles auth JWT pass token via shared auth package workspace monorepo. Route /orders/* loads remote OrderModule federated. Align React 18.3.1 across remotes package.json overrides. Contract integration test shell+remote staging compose. Feature flags disable broken remote fallback message.

#### When to use / when NOT to use
Multiple teams orders billing catalog separate velocity. Interview: federation vs monorepo packages. Legacy Angular island migration gradual React remote.

#### Production example
Shell Spring app static host + 3 remotes S3 CloudFront. Shared @company/ui-theme npm workspace versioned. CI contract test remote exposes mount function signature. Incident runbook remote 404 load failure degrade gracefully.

#### Common mistakes
- Duplicate React versions invalid hook call.
- Incompatible react-router versions across remotes.
- No shared design system visual drift.
- MFE for 5 developer team overhead absurd.
- Independent deploy breaking shared type contract unversioned.

#### Interview follow-ups (with model answers)

**Q:** Federation vs monorepo packages?
**A:** Monorepo packages compile-time deps atomic CI simpler—default choice. Federation runtime deploy independence different teams release cadence. Monorepo can simulate boundaries npm workspaces without federation complexity. Federation when legal org boundaries prevent single repo. Java modular monolith analogy vs true microservices.

**Q:** Auth across MFE?
**A:** Shell owns login JWT memory; pass token via custom event shared Zustand module federated shared package. Or cookie same-site all remotes one domain path routing gateway. Spring validates same Resource Server all API calls. Logout shell clears shared auth remote listeners invalidate Query caches. Security review token propagation.

#### Scenario probe
**Situation:** Orders remote upgrade React 19 shell still React 18 hooks crash.

**Model answer:** shared singleton requiredVersion mismatch—align peer deps coordinated release train or shell upgrades first. Temporary pin remote React 18 until shell ready. Automated CI check shared dependency versions across remotes package manifests. Document breaking React upgrade playbook all MFE teams. Consider monorepo workspace until org matures federation ops. Java API unaffected—client integration discipline issue.

---

## Scenario-based interview drills

### S1. JWT refresh timer fires with stale token

**Situation:** Your Spring-backed order SPA stores the access token in React state. A `useEffect` starts `setInterval` every 14 minutes to call `POST /api/auth/refresh`. After the user leaves the tab idle for an hour, refresh calls return 401 and the UI still shows them as logged in until the next API call fails.

**What they're testing:** Stale closures in effects, interval cleanup, auth state synchronization with Spring Security, and separating display state from credential state.

**How to structure your answer:**
- Reproduce: interval callback closes over initial token
- Explain why React 18 batching does not fix closure capture
- Fix: ref for latest token, or refresh via axios interceptor outside React
- Harden: 401 global handler, logout on refresh failure, visibility API pause
- Mention Spring refresh-token rotation and httpOnly cookie trade-offs

**Model answer:** The classic bug is the interval callback capturing the access token from the render where the effect ran. When Spring rotates the JWT after the first successful refresh, the interval still sends the original bearer string because the closure never saw the updated state. I'd confirm in Network tab: refresh succeeds once, subsequent calls use an old Authorization header. Fix options ranked by senior preference: first, move token attachment to an axios/fetch interceptor that reads from a module-level ref updated synchronously on every login and refresh—effects don't own transport. Second, include `accessToken` in the effect dependency array and clear/restart the interval when it changes, with cleanup on unmount. Third, prefer httpOnly refresh cookie with Spring handling rotation server-side so the SPA never stores bearer tokens in JS—eliminates XSS and stale-closure classes entirely. Regardless, wire a global 401 handler that clears React Query cache, resets auth context, and redirects to login; never let UI show "authenticated" when refresh failed. Add Page Visibility API to pause intervals on hidden tabs and resume with immediate refresh check. On the Java side, verify refresh endpoint returns new access token body and Set-Cookie for refresh token with SameSite=Lax. Integration test: mount component, simulate token rotation, assert interval uses new value. This demonstrates hooks mental model beyond memorizing useEffect syntax.

**Common weak answers:** "Add token to dependency array" without mentioning interval restart/cleanup; storing JWT in localStorage "because it's easier"; blaming Spring Security without inspecting request headers; using `useCallback` on refresh without fixing closure source.

**Follow-up probes (with answers):**

**Q:** Why not store the JWT only in localStorage and read it inside the interval?
**A:** localStorage survives refresh but is vulnerable to XSS exfiltration; reading on each tick avoids stale closure but not XSS. Senior pattern: memory for access token, httpOnly cookie for refresh, interceptor reads ref. If product mandates localStorage, short TTL plus Content-Security-Policy and aggressive logout on 401 are mandatory compensating controls.

---

### S2. Optimistic toggle rolls back on 409 version conflict

**Situation:** Warehouse staff use a React admin screen backed by `PATCH /api/inventory/{sku}` with Spring optimistic locking (`@Version`). You added TanStack Query optimistic update to flip `reserved` instantly. Under concurrent edits, users see the toggle snap back after ~500ms and complain the UI is "broken."

**What they're testing:** Optimistic updates, HTTP 409 handling, If-Match/ETag alignment with JPA version fields, and user messaging for conflict resolution.

**How to structure your answer:**
- Trace mutation `onMutate` → server 409 → `onError` rollback
- Map Spring `ProblemDetail` with current version to refetch
- Offer merge UI vs server-wins vs retry with latest ETag
- Tie to lost-update problem from backend perspective

**Model answer:** Optimistic UI is correct for perceived speed, but rollback on 409 is expected behavior when two operators reserve the same SKU. I'd verify the mutation sends `If-Match` or `version` field matching the DTO snapshot in cache—missing version guarantees 409 on any concurrent write. In `onMutate`, cancel in-flight queries, snapshot previous cache, apply optimistic patch. On 409 response, parse Spring's Problem Details: `type=urn:optimistic-lock`, extensions `currentEntity` or at minimum trigger `invalidateQueries` for that SKU and show toast: "Someone else updated this row—refreshed with latest." Better UX: modal diff showing their intended state vs server state with "Overwrite" (PUT with new version) or "Discard." Never silently rollback without explanation—that feels like a bug. Server should return 409 with current representation body so client can merge without extra GET. Align TypeScript type: `version: number` required on InventoryDto. Add integration test with MSW: two rapid mutations, assert second shows conflict UI not infinite retry loop. Prevent double-submit with `isPending` disabling toggle. Long-term, consider WebSocket or SSE inventory channel for hot SKUs so optimistic assumptions fail less often. Senior signal: connect React rollback to JPA `@Version` semantics and explain why retry without refetch is unsafe.

**Common weak answers:** Disable optimistic updates entirely; retry PATCH in a loop on 409; ignore version field; blame React Query without reading response status.

**Follow-up probes (with answers):**

**Q:** Should you use ETag from GET list response on PATCH?
**A:** Yes if Spring exposes `ETag` on `InventoryDto` via ShallowEtagHeaderFilter or custom—send `If-Match`. Alternatively embed `version` in JSON body matching `@Version`. List endpoint must return version per row; caching list with stale versions worsens conflicts. Document contract in OpenAPI.

---

### S3. Duplicate order rows after navigation remount

**Situation:** Checkout calls `POST /api/orders` inside `useEffect` when `cartId` is present. QA reports duplicate orders when users navigate away mid-request and return via browser back. Spring logs show two POSTs with identical `cartId`; only one should succeed.

**What they're testing:** Effect-driven side effects, Strict Mode double-mount, idempotency keys, and POST-on-mount anti-pattern.

**How to structure your answer:**
- Identify effect firing on mount without guard
- Strict Mode dev double-invoke vs production navigation
- Fix: user-triggered submit or idempotency-Key header
- Server: `@Idempotent` or unique constraint on cartId

**Model answer:** Fetch-on-mount is for reads; creating orders in `useEffect` couples navigation lifecycle to business side effects—a footgun. When the user leaves, the in-flight POST may still complete; returning remounts the component and fires another POST because there's no client-side "already submitted" guard. React 18 Strict Mode in dev intentionally double-mounts to surface this class of bug. Fix client: move order creation to explicit button handler; or persist `submissionState` in sessionStorage keyed by cartId (`pending|completed|failed`); or use React Query `useMutation` triggered once with `mutate` from submit, never from effect. Add `Idempotency-Key: ${cartId}` header; Spring filter dedupes within 24h window storing key in Redis or DB. Return 200 with original order on replay, not 409. If effect is unavoidable (deep link auto-checkout), gate with `useRef` submitted flag and abort on unmount via AbortController—cancel won't stop completed server write, so idempotency is still required. Display loading overlay preventing navigation during POST. Backend unique index on `cart_id` where status != CANCELLED catches duplicates as safety net. Test: RTL test asserting single POST when remounting; Playwright back-button scenario. Senior answer acknowledges client and server defenses together.

**Common weak answers:** "Add empty dependency array" only; disable Strict Mode; dedupe by deleting duplicates in DB manually; use `useEffect` cleanup to "cancel" POST without AbortController.

**Follow-up probes (with answers):**

**Q:** Can AbortController prevent duplicate orders on back navigation?
**A:** Only if the request hasn't finished—abort cancels the fetch client-side but a completed POST still created the order. Abort helps abandoned in-flight requests; idempotency keys handle completed duplicates. Combine both.

---

### S4. Spring Security CORS blocks SPA after environment promotion

**Situation:** React SPA on `https://orders-ui.staging.example.com` calls Spring API on `https://api.staging.example.com`. After promoting the same build to production (`orders-ui.prod`, `api.prod`), browsers show CORS errors on preflight `OPTIONS`. Postman works fine. Release manager insists "the frontend didn't change."

**What they're testing:** CORS vs server reachability, Spring `CorsConfiguration`, environment-specific allowed origins, and debugging browser-only failures.

**How to structure your answer:**
- Distinguish CORS from 401/404
- Inspect preflight response headers
- Map to `WebMvcConfigurer` or Spring Security cors()
- Fix per-environment config, not wildcard in prod

**Model answer:** Postman omits browser same-origin policy, so CORS failures are invisible there. Browser sends `OPTIONS` with `Origin: https://orders-ui.prod.example.com` and `Access-Control-Request-Headers: authorization,content-type`. Spring must respond with `Access-Control-Allow-Origin` matching that exact origin (not staging), `Allow-Methods`, `Allow-Headers` including Authorization, and `Max-Age`. If staging worked, production likely still lists only staging origins in `application-prod.yml` or API Management policy. I'd check Network tab preflight: missing `Allow-Origin` means Spring Security filter chain blocked before controller—often `authorizeHttpRequests` applies before cors and rejects OPTIONS. Fix: `.cors(Customizer.withDefaults())` with `CorsConfigurationSource` bean reading allowed origins from env var `CORS_ALLOWED_ORIGINS`. Never use `*` with credentials. If APIM sits in front, CORS may be configured at gateway layer duplicating or conflicting with Spring—pick one layer. For JWT, ensure `Allow-Headers` includes `Authorization`. After fix, verify credentialed requests with `fetch(..., { credentials: 'include' })` if using cookies. Document promotion checklist: update CORS env, Keycloak redirect URIs, and Content-Security-Policy connect-src together. Regression: smoke test from real browser in CI with Cypress hitting prod-like origins.

**Common weak answers:** Disable CORS globally with `*` in production; fix only in nginx ignoring Spring; assume "API is down" from CORS message; add `@CrossOrigin` on every controller without central config.

**Follow-up probes (with answers):**

**Q:** Why does GET work but POST with Authorization fails CORS?
**A:** Simple GET may skip preflight; JSON POST with Authorization triggers preflight. If OPTIONS isn't configured, browser blocks the actual POST. Fix preflight handling, not the POST mapping.

---

### S5. Admin table freezes scrolling 8k rows from Spring

**Situation:** Operations dashboard fetches `GET /api/audit-events?page=0&size=8000` because product wanted "client-side Excel-like filtering." After Spring upgrade returns data faster, users report typing in the filter box freezes for seconds. Lighthouse shows poor INP.

**What they're testing:** Render performance, virtualization, server-side pagination, and knowing when client-side filtering is inappropriate.

**How to structure your answer:**
- Profile with React DevTools Profiler
- Quantify render cost per keystroke
- Propose TanStack Table + virtualizer or server Pageable
- Keep Spring as source of truth for large datasets

**Model answer:** Fetching 8000 rows is already a smell—Spring `Pageable` exists precisely to bound payload and query cost. The freeze is main-thread render: each filter keystroke re-renders thousands of `<tr>` nodes because the parent holds all rows in state and filters synchronously in render or `useMemo` still processing huge arrays. I'd Profile: confirm FilterInput triggers AuditTable render > 200ms. Immediate mitigation: `useDeferredValue` on filter text so input stays responsive while table catches up—buys time, not a fix. Real fix: server-side filtering `GET /api/audit-events?q=&page=&size=50` with debounced Query; render only current page with `@tanstack/react-virtual` if you must show many visible rows. Reduce column cell complexity—no inline formatters creating new functions per row. Memoize row component with stable `eventId` key. Backend: add DB index on filtered columns; return slim DTO not full entity graph. If export needs 8k rows, separate CSV download endpoint async, not UI table. Set performance budget: INP < 200ms, max 100 DOM rows without virtualization. Senior narrative: Fiber doesn't remove O(n) filter work; it only schedules it—you must reduce n or move work server-side.

**Common weak answers:** `React.memo` on every cell without reducing row count; `useCallback` everywhere; blame Spring for returning JSON too fast; buy users faster laptops.

**Follow-up probes (with answers):**

**Q:** When is client-side filtering acceptable?
**A:** Reference data under ~200 stable rows (status codes, small catalogs) with stable query cache and `staleTime`. Not audit logs, orders, or inventory at enterprise scale.

---

### S6. Silent token expiry mid-checkout loses cart

**Situation:** B2B checkout SPA keeps access token in memory. Spring access TTL is 15 minutes; checkout with 40 line items and approval steps takes 25 minutes. On final `POST /api/orders`, user gets 401, redirect to login, cart state in Zustand is cleared on logout, and they abandon the purchase.

**What they're testing:** Auth UX, proactive refresh, preserving client state across re-auth, and coordinating with Spring refresh-token flow.

**How to structure your answer:**
- Timeline: token expiry during long wizard
- Proactive refresh before expiry vs reactive 401
- Persist cart to sessionStorage or server draft order
- Spring opaque refresh + sliding session

**Model answer:** Reactive 401 handling is necessary but insufficient for long wizards. I'd implement proactive refresh: decode `exp` from JWT (or track issued time + TTL from login response) and schedule refresh at 80% lifetime, coordinated with the interceptor pattern from S1. Before redirect on 401, attempt single silent refresh using httpOnly refresh cookie; only redirect if that fails. Preserve cart: on login mount, persist Zustand cart to `sessionStorage` keyed by tenant+user, restore after re-auth; better, `POST /api/draft-orders` server-side so recovery survives device switch—Spring stores draft linked to principal. Show modal "Session expiring in 2 minutes—click to stay signed in" triggering refresh on user gesture (some browsers require interaction for cookie refresh). Align Spring: refresh token rotation with reuse detection; extend access TTL for checkout scope via step-up token if business allows. React Query: mark checkout mutations `retry: false` on 401 to avoid duplicate submits after refresh. E2E test: mock expired token at step 3, assert cart survives re-login. Senior point: auth is a cross-cutting UX concern, not a login page problem.

**Common weak answers:** Increase TTL to 24h without security review; localStorage cart with JWT; ignore until users complain; full page reload on 401.

**Follow-up probes (with answers):**

**Q:** Is decoding JWT exp in the client safe?
**A:** Reading exp from signed JWT is fine for scheduling refresh; never trust client exp for authorization—that's server's job. Tampering invalidates signature server-side.

---

### S7. WebSocket inventory feed desyncs React Query cache

**Situation:** Spring emits STOMP/WebSocket inventory updates after `PUT /api/inventory/{sku}`. React subscribes and calls `queryClient.setQueryData` on each message. Users report quantities oscillating between old and new values after bulk import jobs run on the server.

**What they're testing:** Cache coherence, event ordering, stale WS messages, and when to invalidate vs patch.

**How to structure your answer:**
- Compare WS patch vs Query fetch timestamps
- Handle out-of-order and full-refresh events
- Version or sequence in message envelope
- Fallback periodic refetch

**Model answer:** Optimistic local patches from WebSocket without versioning lose to stale messages—bulk import may emit thousands of updates out of order or replay buffered events after reconnect. I'd add `sequence` or `updatedAt` to each `InventoryUpdated` message from Spring; client applies `setQueryData` only if incoming version > cached version. On `FULL_SYNC` event type, `invalidateQueries` instead of patch. On WS reconnect, always refetch list query—never assume subscription gap is empty. Debounce high-volume bursts with `requestAnimationFrame` batching to avoid render thrash. If multiple tabs open, WS updates one tab's cache—use `BroadcastChannel` or accept refetch-on-focus via `refetchOnWindowFocus`. Spring side: STOMP user destination vs topic broadcast; ensure import job publishes final checkpoint event. Conflict with in-flight user mutation: if user toggles reserved and WS delivers older state, version gate prevents regression. Metrics: count rejected stale WS updates. Alternative architecture: WS triggers invalidation only, not direct patch—simpler, slightly more HTTP load, often correct for senior teams prioritizing correctness over latency.

**Common weak answers:** Blindly overwrite cache on every message; no reconnect strategy; mix WS updates with paginated cache keys missing SKU in current page; disable WebSocket under load.

**Follow-up probes (with answers):**

**Q:** WS patch vs invalidateQueries—which default?
**A:** Invalidate for low-frequency or complex aggregates; patch with version gate for high-frequency single-entity updates visible on screen. When in doubt, invalidate—correctness first.

---

### S8. Accessibility audit fails order form after RHF migration

**Situation:** Team migrated order form to React Hook Form + shadcn inputs. Automated axe scan reports "form field missing label" and keyboard users cannot reach validation errors. Spring returns Problem Details field errors but screen readers don't announce them.

**What they're testing:** Accessible forms, RHF `aria-*` wiring, error association, and fullstack validation UX.

**How to structure your answer:**
- Map each input to label/`aria-labelledby`
- `aria-invalid`, `aria-describedby` to error element ids
- Live region for summary errors
- Connect Spring `fieldErrors` paths to RHF `setError`

**Model answer:** shadcn `FormField` wraps Label, Control, Description, Message—if migration used raw `<Input {...register('customer.email')}>` without FormField, labels broke. I'd audit one field end-to-end: `<label for>` matches input `id`; on Spring 422, `setError('customer.email', { message })` and render `<p id="customer.email-error" role="alert">`. Input gets `aria-invalid={!!errors.customer?.email}` and `aria-describedby="customer.email-error"`. For form-level business errors from Problem Details `type` extension, add `role="alert"` live region at form top announcing on submit failure. Focus management: move focus to first invalid field on submit—RHF `setFocus` or ref map. Don't rely on color alone for errors—icon + text. Server path `customer.email` must match RHF nested field names exactly (see Q55 territory but scenario is a11y angle). Test with VoiceOver/NVDA in CI via axe-core/playwright. Senior teams treat WCAG as acceptance criteria alongside OpenAPI contract tests.

**Common weak answers:** Placeholder as label; `div` clickable instead of `button`; toast-only errors; ignore axe in CI.

**Follow-up probes (with answers):**

**Q:** Should submit button disable during `isSubmitting`?
**A:** Disable or `aria-busy="true"` with visually hidden "Submitting" text—prevent double POST to Spring and inform assistive tech.

---

### S9. Feature flag hook causes render storm across tree

**Situation:** New `useFeatureFlags()` fetches `GET /api/feature-flags` on every route change, stores in Context, and 60 components consume context. Flipping one flag in admin causes noticeable lag; React Profiler shows entire tree re-rendering.

**What they're testing:** Context performance, selector patterns, splitting context, and caching flag reads.

**How to structure your answer:**
- Prove Context value new object each render
- Split flags context from dispatch
- Selective subscription (Zustand or `use-context-selector`)
- Cache flags with long `staleTime` in Query

**Model answer:** Single Context `{ flags, refreshFlags }` where provider creates new object each fetch forces all consumers to re-render even if their flag unchanged. Fix: store flags in TanStack Query with `staleTime: 5 * 60 * 1000` and `select` per component `useQuery({ select: (d) => d.enableNewCheckout })` so only subscribers to changed data re-render—or Zustand map with per-key selectors. If Context required, split `FeatureFlagsDataContext` and `FeatureFlagsDispatchContext`; memoize value with `useMemo` keyed by serialized flags. Avoid fetching flags on every route change; fetch once at app shell, refetch on interval or WS admin channel. Spring endpoint should return small JSON map, CDN-cacheable per tenant with ETag. For critical flags, server-enforce anyway—client flag is UX only. Measure before/after with Profiler "why did this render?" Senior pattern mirrors backend: don't broadcast config changes to uninterested services.

**Common weak answers:** `React.memo` all 60 components; refetch flags on every navigation; store flags in Redux without selectors; ignore perf until production incident.

**Follow-up probes (with answers):**

**Q:** Server-side vs client-side feature flags for kill switch?
**A:** Kill switch for payments must be enforced in Spring—client flag hides UI only. Client flags OK for gradual UI rollout with server accepting both code paths during migration.

---

### S10. Lazy-loaded admin route white screen in production only

**Situation:** `React.lazy(() => import('./AdminPanel'))` works locally with Vite dev server. Production build behind Spring Boot static resource handler shows blank page after chunk load; console has `ChunkLoadError` after deployment. Users must hard-refresh.

**What they're testing:** Code splitting, cache busting, deployment skew, error boundaries, and static asset hosting from Spring.

**How to structure your answer:**
- Explain hashed chunk filenames and old index.html cached
- Spring `ResourceHandler` cache headers
- Error boundary with retry on chunk failure
- Blue-green deploy chunk compatibility

**Model answer:** After deploy, returning users have old `index.html` referencing `AdminPanel.abc123.js` while server only has `AdminPanel.def456.js`—dynamic import throws `ChunkLoadError`. Local dev serves latest always; prod CDN or browser caches HTML aggressively. Fixes: configure Spring `WebMvcConfigurer` cache control—`index.html` `Cache-Control: no-cache`, hashed assets `max-age=31536000, immutable`. On chunk error, error boundary catches, shows "New version available—refresh", calls `window.location.reload()`. Vite `build.rollupOptions.output.manualChunks` stability helps but doesn't eliminate skew during rolling deploy—keep N-1 chunks one release or use single-bundle for admin if tiny. Spring serving: verify `classpath:/static/` includes all `dist/assets/*` after CI copy; missing MIME or 404 on chunk manifests as white screen. Optionally version API path `/app/v2/` forcing HTML fetch. Monitor Sentry for `ChunkLoadError` spike post-deploy. Senior ops: coordinate frontend deploy with backend or use CDN atomic release; document that lazy routes need cache strategy, not just `React.lazy` one-liner.

**Common weak answers:** Disable code splitting; tell users to clear cache; ignore Spring cache headers; only test dev server.

**Follow-up probes (with answers):**

**Q:** Error boundary catches chunk load failures?
**A:** Yes if error propagates during render/lazy init—wrap `Suspense` sibling with boundary implementing retry. Won't catch event handler errors unrelated to chunk load.

---
