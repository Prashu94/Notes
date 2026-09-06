# React + TypeScript — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) — 33 exercises total.

---

## Part A — Basic (10)

### Exercise A1 — Typed functional component

**Task:** Create a `Greeting` component that accepts `name: string` and optional `title?: string`.

**Solution:**

```tsx
import React from "react";

type GreetingProps = {
  name: string;
  title?: string;
};

export function Greeting({ name, title = "Hello" }: GreetingProps) {
  return (
    <h1>
      {title}, {name}!
    </h1>
  );
}

// Usage
// <Greeting name="Prashant" />
// <Greeting name="Prashant" title="Welcome" />
```

**Expected output (React Testing Library):**

```
Welcome, Prashant!
```

**Senior takeaway:** Prefer `type` for props unions; use `interface` when you expect declaration merging.

---

### Exercise A2 — useState counter

**Task:** Build a counter with increment, decrement, and reset. Type the state as `number`.

**Solution:**

```tsx
import { useState } from "react";

export function Counter() {
  const [count, setCount] = useState<number>(0);

  return (
    <div>
      <p data-testid="count">{count}</p>
      <button onClick={() => setCount((c) => c + 1)}>+</button>
      <button onClick={() => setCount((c) => c - 1)}>-</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

**Expected output:** After three `+` clicks, `count` displays `3`.

---

### Exercise A3 — useEffect with cleanup

**Task:** Subscribe to `window` `resize` and display viewport width. Clean up on unmount.

**Solution:**

```tsx
import { useEffect, useState } from "react";

export function ViewportWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const onResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return <span data-testid="width">{width}px</span>;
}
```

**Expected output:** Resizing from 1280 → 1024 updates text to `1024px`. No listener leak in DevTools.

---

### Exercise A4 — Conditional rendering

**Task:** Show a loading spinner, error message, or user name based on fetch status.

**Solution:**

```tsx
type User = { id: string; name: string };
type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; user: User };

export function UserCard({ state }: { state: State }) {
  if (state.status === "loading") return <div>Loading…</div>;
  if (state.status === "error") return <div role="alert">{state.message}</div>;
  return <div>Hello, {state.user.name}</div>;
}
```

**Expected output:**

```
Hello, Priya
```

when `state = { status: "ready", user: { id: "1", name: "Priya" } }`.

---

### Exercise A5 — List rendering with stable keys

**Task:** Render an order list. Use `order.id` as key, not index.

**Solution:**

```tsx
type Order = { id: string; sku: string; qty: number };

export function OrderList({ orders }: { orders: Order[] }) {
  return (
    <ul>
      {orders.map((o) => (
        <li key={o.id}>
          {o.sku} × {o.qty}
        </li>
      ))}
    </ul>
  );
}
```

**Expected output (orders `[{id:"a",sku:"WIDGET",qty:2}]`):**

```html
<li>WIDGET × 2</li>
```

**Senior takeaway:** Index keys break focus/state when the list reorders.

---

### Exercise A6 — Controlled form input

**Task:** Single text field bound to state. Log value on submit.

**Solution:**

```tsx
import { FormEvent, useState } from "react";

export function SearchBox({ onSearch }: { onSearch: (q: string) => void }) {
  const [q, setQ] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSearch(q.trim());
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search orders"
        aria-label="Search orders"
      />
      <button type="submit">Search</button>
    </form>
  );
}
```

**Expected output:** Typing `ORD-42` and submitting calls `onSearch("ORD-42")`.

---

### Exercise A7 — Event handler typing

**Task:** Type `onChange` for a checkbox that toggles `isActive: boolean`.

**Solution:**

```tsx
import { ChangeEvent, useState } from "react";

export function ActiveToggle() {
  const [isActive, setIsActive] = useState(false);

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    setIsActive(e.target.checked);
  };

  return (
    <label>
      <input type="checkbox" checked={isActive} onChange={onChange} />
      {isActive ? "Active" : "Inactive"}
    </label>
  );
}
```

**Expected output:** Checking the box shows `Active`.

---

### Exercise A8 — Union props for button variants

**Task:** `Button` accepts `variant: "primary" | "danger"` and maps to CSS classes exhaustively.

**Solution:**

```tsx
type ButtonProps = {
  variant: "primary" | "danger";
  children: React.ReactNode;
  onClick?: () => void;
};

const classByVariant: Record<ButtonProps["variant"], string> = {
  primary: "btn btn-primary",
  danger: "btn btn-danger",
};

export function Button({ variant, children, onClick }: ButtonProps) {
  return (
    <button className={classByVariant[variant]} onClick={onClick}>
      {children}
    </button>
  );
}
```

**Expected output:** `<Button variant="danger">Cancel</Button>` renders with `btn-danger` class.

---

### Exercise A9 — Children and composition

**Task:** `Card` wraps arbitrary children; `CardHeader` is a separate small component.

**Solution:**

```tsx
type CardProps = { children: React.ReactNode };
type CardHeaderProps = { title: string };

export function Card({ children }: CardProps) {
  return <section className="card">{children}</section>;
}

export function CardHeader({ title }: CardHeaderProps) {
  return <header className="card-header">{title}</header>;
}

// <Card><CardHeader title="Orders" /><p>3 pending</p></Card>
```

**Expected output:** Section contains header `Orders` and body `3 pending`.

---

### Exercise A10 — Simple fetch on mount

**Task:** Fetch `/api/health` once on mount; show JSON `status`.

**Solution:**

```tsx
import { useEffect, useState } from "react";

type Health = { status: string };

export function HealthBadge() {
  const [health, setHealth] = useState<Health | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const res = await fetch("/api/health");
      const json: Health = await res.json();
      if (!cancelled) setHealth(json);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!health) return <span>…</span>;
  return <span data-testid="health">{health.status}</span>;
}
```

**Expected output (mock returns `{ status: "UP" }`):**

```
UP
```

---

## Part B — Intermediate (10)

### Exercise B1 — Stale closure counter

**Task:** Fix a `setInterval` that reads stale state. Compare bad vs good.

**Solution:**

```tsx
import { useEffect, useState } from "react";

function Bad() {
  const [n, setN] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setN(n + 1), 1000); // stale n — stuck at 1
    return () => clearInterval(id);
  }, []);
  return <div>{n}</div>;
}

function Good() {
  const [n, setN] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setN((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, []);
  return <div>{n}</div>;
}
```

**Expected output:** After 5 s, `Good` shows `5`; `Bad` shows `1`.

---

### Exercise B2 — Fetch race with AbortController

**Task:** Two buttons switch `userId` quickly. Only the latest response should win.

**Solution:**

```tsx
import { useEffect, useState } from "react";

type User = { id: string; name: string };

async function fetchUser(id: string, signal: AbortSignal): Promise<User> {
  const r = await fetch(`/api/users/${id}`, { signal });
  if (!r.ok) throw new Error(String(r.status));
  return r.json();
}

export function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    setError(null);
    fetchUser(userId, ac.signal)
      .then(setUser)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => ac.abort();
  }, [userId]);

  if (error) return <div role="alert">{error}</div>;
  if (!user) return <div>Loading…</div>;
  return <div>{user.name}</div>;
}
```

**Test sketch (Vitest + fake timers):**

```ts
it("aborts stale fetch", async () => {
  // click user 1, then user 2 before 1 resolves — only user 2 name shown
});
```

**Expected output:** Fast toggle `1` → `2` shows user 2's name, never user 1's.

---

### Exercise B3 — Discriminated API result

**Task:** Model load state as a discriminated union. Render exhaustively with `switch`. No `data!`.

**Solution:**

```tsx
type Load<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; message: string };

type Order = { id: string; total: number };

export function OrderView({ load }: { load: Load<Order> }) {
  switch (load.status) {
    case "idle":
      return <p>Pick an order</p>;
    case "loading":
      return <p>Loading…</p>;
    case "success":
      return <p>Total: {load.data.total}</p>;
    case "error":
      return <p role="alert">{load.message}</p>;
  }
}
```

**Expected output (`success`, total 9900):**

```
Total: 9900
```

TypeScript errors if you access `load.data` without narrowing.

---

### Exercise B4 — Zod at the boundary

**Task:** Parse unknown JSON from `fetch` with Zod before it enters React state.

**Solution:**

```ts
import { z } from "zod";

const Order = z.object({
  id: z.string(),
  status: z.enum(["PENDING", "PAID", "SHIPPED"]),
  version: z.number(),
});
type Order = z.infer<typeof Order>;

export async function getOrder(id: string): Promise<Order> {
  const r = await fetch(`/api/orders/${id}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  const json: unknown = await r.json();
  return Order.parse(json);
}
```

**Expected output:** Invalid payload `{ id: 1 }` throws `ZodError` before render. Valid payload parses to typed `Order`.

---

### Exercise B5 — If-Match optimistic concurrency from UI

**Task:** `PUT` order with `If-Match: "${version}"`. On 412, show conflict and refetch.

**Solution:**

```tsx
import { useCallback, useState } from "react";
import { getOrder } from "./api";

type Order = { id: string; status: string; version: number };

export function OrderEditor({ orderId }: { orderId: string }) {
  const [order, setOrder] = useState<Order | null>(null);
  const [conflict, setConflict] = useState(false);

  const save = useCallback(
    async (nextStatus: string) => {
      if (!order) return;
      const r = await fetch(`/api/orders/${orderId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "If-Match": `"${order.version}"`,
        },
        body: JSON.stringify({ status: nextStatus }),
      });
      if (r.status === 412) {
        setConflict(true);
        setOrder(await getOrder(orderId));
        return;
      }
      if (!r.ok) throw new Error(String(r.status));
      setConflict(false);
      setOrder(await r.json());
    },
    [order, orderId]
  );

  return (
    <div>
      {conflict && <p role="alert">Updated elsewhere — refreshed.</p>}
      {order && (
        <>
          <p>{order.status}</p>
          <button onClick={() => save("PAID")}>Mark paid</button>
        </>
      )}
    </div>
  );
}
```

**Expected output:** Concurrent edit returns 412 → alert shown → UI shows server version.

---

### Exercise B6 — Memo that doesn't work (fix useCallback)

**Task:** Parent passes inline `onClick` to `React.memo(Child)`. Fix re-renders.

**Solution:**

```tsx
import React, { useCallback, useState } from "react";

const Child = React.memo(function Child({
  id,
  onSave,
}: {
  id: string;
  onSave: (id: string) => void;
}) {
  console.log("Child render", id);
  return <button onClick={() => onSave(id)}>Save {id}</button>;
});

export function Parent({ ids }: { ids: string[] }) {
  const [tick, setTick] = useState(0);
  const save = useCallback((id: string) => console.log("save", id), []);

  return (
    <div>
      <button onClick={() => setTick((t) => t + 1)}>tick {tick}</button>
      {ids.map((id) => (
        <Child key={id} id={id} onSave={save} />
      ))}
    </div>
  );
}
```

**Expected output:** Clicking `tick` does **not** log `Child render` for each child (Profiler shows skipped renders).

---

### Exercise B7 — Map Problem Details to react-hook-form

**Task:** On 400, map RFC 7807 `errors[]` to field errors.

**Solution:**

```tsx
import { useForm } from "react-hook-form";

type Problem = {
  title: string;
  errors?: { field: string; code: string; message: string }[];
};

type Form = { email: string; amount: number };

export function TransferForm() {
  const { register, handleSubmit, setError, formState } = useForm<Form>();

  const onSubmit = handleSubmit(async (data) => {
    const r = await fetch("/api/transfers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (r.status === 400) {
      const problem: Problem = await r.json();
      problem.errors?.forEach((e) =>
        setError(e.field as keyof Form, { message: e.message })
      );
      return;
    }
    if (!r.ok) throw new Error(String(r.status));
  });

  return (
    <form onSubmit={onSubmit}>
      <input {...register("email")} />
      {formState.errors.email && <span>{formState.errors.email.message}</span>}
      <input type="number" {...register("amount", { valueAsNumber: true })} />
      <button type="submit">Send</button>
    </form>
  );
}
```

**Expected output:** Server returns `errors: [{ field: "email", message: "invalid" }]` → inline error under email field.

---

### Exercise B8 — Custom hook useLocalStorage

**Task:** Persist theme preference with typed `useLocalStorage<"light" | "dark">`.

**Solution:**

```tsx
import { useCallback, useState } from "react";

export function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : initial;
  });

  const set = useCallback(
    (next: T | ((prev: T) => T)) => {
      setValue((prev) => {
        const v = typeof next === "function" ? (next as (p: T) => T)(prev) : next;
        localStorage.setItem(key, JSON.stringify(v));
        return v;
      });
    },
    [key]
  );

  return [value, set] as const;
}

export function ThemeToggle() {
  const [theme, setTheme] = useLocalStorage<"light" | "dark">("theme", "light");
  return (
    <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
      {theme}
    </button>
  );
}
```

**Expected output:** Reload page — button still shows `dark` after toggle.

---

### Exercise B9 — Context + useReducer cart

**Task:** Global cart with `add` / `remove` actions, fully typed.

**Solution:**

```tsx
import React, { createContext, useContext, useReducer } from "react";

type Item = { sku: string; qty: number };
type State = { items: Item[] };
type Action =
  | { type: "add"; sku: string }
  | { type: "remove"; sku: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "add": {
      const existing = state.items.find((i) => i.sku === action.sku);
      if (existing) {
        return {
          items: state.items.map((i) =>
            i.sku === action.sku ? { ...i, qty: i.qty + 1 } : i
          ),
        };
      }
      return { items: [...state.items, { sku: action.sku, qty: 1 }] };
    }
    case "remove":
      return { items: state.items.filter((i) => i.sku !== action.sku) };
  }
}

const CartCtx = createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, { items: [] });
  return <CartCtx.Provider value={{ state, dispatch }}>{children}</CartCtx.Provider>;
}

export function useCart() {
  const ctx = useContext(CartCtx);
  if (!ctx) throw new Error("useCart outside provider");
  return ctx;
}
```

**Expected output:** `dispatch({ type: "add", sku: "A" })` twice → one item qty 2.

---

### Exercise B10 — RTL test with MSW

**Task:** Login form: type credentials, submit, assert `fetch` body; mock 401 and assert error.

**Solution:**

```tsx
// LoginForm.tsx
import { FormEvent, useState } from "react";

export function LoginForm() {
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const r = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: fd.get("email"),
        password: fd.get("password"),
      }),
    });
    if (r.status === 401) {
      setError("Invalid credentials");
      return;
    }
  };

  return (
    <form onSubmit={onSubmit}>
      <input name="email" aria-label="email" />
      <input name="password" type="password" aria-label="password" />
      <button type="submit">Sign in</button>
      {error && <div role="alert">{error}</div>}
    </form>
  );
}
```

```ts
// LoginForm.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { LoginForm } from "./LoginForm";

const server = setupServer(
  http.post("/api/login", () => HttpResponse.json({}, { status: 401 }))
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("shows error on 401", async () => {
  render(<LoginForm />);
  await userEvent.type(screen.getByLabelText("email"), "a@b.com");
  await userEvent.type(screen.getByLabelText("password"), "wrong");
  await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Invalid credentials");
});
```

**Expected output:**

```
✓ shows error on 401
```

---

## Part C — Hard (8)

### Exercise C1 — Virtualized list (performance)

**Task:** Render 10 000 rows with `@tanstack/react-virtual`. Only visible DOM nodes exist.

**Solution:**

```tsx
import { useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

type Row = { id: string; label: string };

export function VirtualList({ rows }: { rows: Row[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 32,
    overscan: 8,
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: "auto" }}>
      <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
        {virtualizer.getVirtualItems().map((item) => (
          <div
            key={item.key}
            style={{
              position: "absolute",
              top: 0,
              transform: `translateY(${item.start}px)`,
              height: item.size,
            }}
          >
            {rows[item.index].label}
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Expected output:** DevTools shows ~20 `<div>` rows, not 10 000. Scroll stays smooth.

---

### Exercise C2 — Error boundary + Suspense data

**Task:** Wrap async child in `Suspense` fallback and class error boundary.

**Solution:**

```tsx
import React, { Component, Suspense } from "react";

class ErrorBoundary extends Component<
  { fallback: React.ReactNode; children: React.ReactNode },
  { error: Error | null }
> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  render() {
    if (this.state.error) return this.props.fallback;
    return this.props.children;
  }
}

const LazyOrders = React.lazy(() => import("./OrdersPage"));

export function AppShell() {
  return (
    <ErrorBoundary fallback={<p>Something went wrong</p>}>
      <Suspense fallback={<p>Loading orders…</p>}>
        <LazyOrders />
      </Suspense>
    </ErrorBoundary>
  );
}
```

**Expected output:** Chunk load failure → `Something went wrong`. Slow network → `Loading orders…` then content.

---

### Exercise C3 — useTransition for search filter

**Task:** Filter 5 000 items without blocking input typing.

**Solution:**

```tsx
import { useMemo, useState, useTransition } from "react";

export function SearchList({ items }: { items: string[] }) {
  const [q, setQ] = useState("");
  const [pending, startTransition] = useTransition();

  const filtered = useMemo(() => {
    const lower = q.toLowerCase();
    return items.filter((i) => i.toLowerCase().includes(lower));
  }, [items, q]);

  return (
    <div>
      <input
        value={q}
        onChange={(e) => {
          const v = e.target.value;
          setQ(v);
          startTransition(() => {
            /* trigger deferred render of filtered list */
          });
        }}
      />
      {pending && <span aria-live="polite">Filtering…</span>}
      <ul>
        {filtered.slice(0, 100).map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>
    </div>
  );
}
```

**Expected output:** Input stays responsive at 60 fps while list updates with `Filtering…` briefly visible.

---

### Exercise C4 — Compound Tabs component

**Task:** `<Tabs><Tabs.List>…</Tabs.List><Tabs.Panel>…</Tabs.Panel></Tabs>` with shared context.

**Solution:**

```tsx
import React, { createContext, useContext, useState } from "react";

type TabsCtx = { active: string; setActive: (id: string) => void };
const Ctx = createContext<TabsCtx | null>(null);

function useTabs() {
  const c = useContext(Ctx);
  if (!c) throw new Error("Tabs compound misuse");
  return c;
}

function Tabs({ defaultId, children }: { defaultId: string; children: React.ReactNode }) {
  const [active, setActive] = useState(defaultId);
  return <Ctx.Provider value={{ active, setActive }}>{children}</Ctx.Provider>;
}

function List({ children }: { children: React.ReactNode }) {
  return <div role="tablist">{children}</div>;
}

function Tab({ id, children }: { id: string; children: React.ReactNode }) {
  const { active, setActive } = useTabs();
  return (
    <button role="tab" aria-selected={active === id} onClick={() => setActive(id)}>
      {children}
    </button>
  );
}

function Panel({ id, children }: { id: string; children: React.ReactNode }) {
  const { active } = useTabs();
  if (active !== id) return null;
  return <div role="tabpanel">{children}</div>;
}

Tabs.List = List;
Tabs.Tab = Tab;
Tabs.Panel = Panel;
export { Tabs };
```

**Expected output:** Clicking `Settings` tab shows only settings panel; ARIA `aria-selected` toggles.

---

### Exercise C5 — Generic data table

**Task:** `DataTable<T>` with typed column accessors.

**Solution:**

```tsx
type Column<T> = {
  header: string;
  cell: (row: T) => React.ReactNode;
};

export function DataTable<T extends { id: string }>({
  rows,
  columns,
}: {
  rows: T[];
  columns: Column<T>[];
}) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c.header}>{c.header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            {columns.map((c) => (
              <td key={c.header}>{c.cell(row)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// <DataTable<Order> rows={orders} columns={[{ header: "ID", cell: (o) => o.id }]} />
```

**Expected output:** Type error if `cell` returns wrong shape or `rows` missing `id`.

---

### Exercise C6 — TanStack Query optimistic update

**Task:** Cancel order with rollback on error.

**Solution:**

```tsx
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

type Order = { id: string; status: string };

export function useCancelOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const r = await fetch(`/api/orders/${id}/cancel`, { method: "POST" });
      if (!r.ok) throw new Error(String(r.status));
      return r.json() as Promise<Order>;
    },
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: ["orders"] });
      const prev = qc.getQueryData<Order[]>(["orders"]);
      qc.setQueryData<Order[]>(["orders"], (old) =>
        old?.map((o) => (o.id === id ? { ...o, status: "CANCELLED" } : o))
      );
      return { prev };
    },
    onError: (_e, _id, ctx) => {
      if (ctx?.prev) qc.setQueryData(["orders"], ctx.prev);
    },
    onSettled: () => qc.invalidateQueries({ queryKey: ["orders"] }),
  });
}
```

**Expected output:** UI shows `CANCELLED` instantly; on 500 reverts to previous list after refetch.

---

### Exercise C7 — Route-level code splitting with preload

**Task:** Lazy-load `/orders` route; preload on nav hover.

**Solution:**

```tsx
import React from "react";
import { createBrowserRouter, RouterProvider, Link } from "react-router-dom";

const OrdersPage = React.lazy(() => import("./OrdersPage"));

const ordersImport = () => import("./OrdersPage");

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Link to="/orders" onMouseEnter={() => void ordersImport()}>
        Orders
      </Link>
    ),
  },
  {
    path: "/orders",
    element: (
      <React.Suspense fallback={<p>Loading…</p>}>
        <OrdersPage />
      </React.Suspense>
    ),
  },
]);

export function App() {
  return <RouterProvider router={router} />;
}
```

**Expected output:** Network tab shows chunk fetched on hover before click; route renders without full-page spinner on fast network.

---

### Exercise C8 — Mini app: orders + idempotent cancel + 409

**Task:** Vite app listing orders from stub API; cancel with `Idempotency-Key`; handle 409 conflict.

**Solution:**

```tsx
// api.ts
export type Order = { id: string; status: "OPEN" | "CANCELLED"; version: number };

export async function listOrders(): Promise<Order[]> {
  const r = await fetch("/api/orders");
  return r.json();
}

export async function cancelOrder(id: string, key: string): Promise<Order> {
  const r = await fetch(`/api/orders/${id}/cancel`, {
    method: "POST",
    headers: { "Idempotency-Key": key },
  });
  if (r.status === 409) throw new Error("CONFLICT");
  if (!r.ok) throw new Error(String(r.status));
  return r.json();
}

// OrdersPage.tsx
import { useEffect, useState } from "react";
import { cancelOrder, listOrders, Order } from "./api";

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    listOrders().then(setOrders);
  }, []);

  const onCancel = async (id: string) => {
    const key = crypto.randomUUID();
    try {
      const updated = await cancelOrder(id, key);
      setOrders((os) => os.map((o) => (o.id === id ? updated : o)));
    } catch (e) {
      setMsg(e instanceof Error && e.message === "CONFLICT" ? "Already cancelled" : "Failed");
    }
  };

  return (
    <div>
      {msg && <p role="alert">{msg}</p>}
      <ul>
        {orders.map((o) => (
          <li key={o.id}>
            {o.id} — {o.status}
            {o.status === "OPEN" && <button onClick={() => onCancel(o.id)}>Cancel</button>}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**MSW handler:**

```ts
http.post("/api/orders/:id/cancel", ({ request }) => {
  const key = request.headers.get("Idempotency-Key");
  if (!key) return HttpResponse.json({}, { status: 400 });
  // second call with same key returns same body; different state → 409
});
```

**Expected output:**

```
ORD-1 — OPEN [Cancel]
→ ORD-1 — CANCELLED
→ double-click Cancel on stale row: "Already cancelled"
```

**Senior takeaway:** Idempotency keys belong in the client for user-initiated writes; server stores key → response mapping.

---


### Exercise A29 — React 19 `use()` with Suspense

**Task:** Wrap a child that calls `use(promise)` in `<Suspense>`. Pass a promise from a parent cache so the child reads resolved data without `useEffect`.

**Solution:**

```tsx
import { Suspense, use, cache } from "react";

type Order = { id: string; total: number };

const getOrder = cache(async (id: string): Promise<Order> => {
  const res = await fetch(`/api/orders/${id}`);
  if (!res.ok) throw new Error(String(res.status));
  return res.json();
});

function OrderTotal({ orderPromise }: { orderPromise: Promise<Order> }) {
  const order = use(orderPromise);
  return <p data-testid="total">${order.total.toFixed(2)}</p>;
}

export function OrderPanel({ id }: { id: string }) {
  const orderPromise = getOrder(id);
  return (
    <Suspense fallback={<p>Loading order…</p>}>
      <OrderTotal orderPromise={orderPromise} />
    </Suspense>
  );
}
```

**Expected output (mock `/api/orders/42` → `{ id: "42", total: 129.99 }`):**

```
Loading order…
→ $129.99
```

**Senior takeaway:** `use()` turns async data into render-time reads; pair with `cache()` so sibling components share one in-flight promise without prop drilling.

---

### Exercise A30 — React 19 Actions with `useActionState`

**Task:** Build a cancel-order form using a Server Action (or mock async action). Show pending state and returned validation errors without manual `useState` for each field.

**Solution:**

```tsx
"use client";

import { useActionState } from "react";

type State = { ok: boolean; message: string };

async function cancelOrder(_prev: State, formData: FormData): Promise<State> {
  const id = String(formData.get("orderId") ?? "");
  if (!id) return { ok: false, message: "Order ID required" };

  const res = await fetch(`/api/orders/${id}/cancel`, { method: "POST" });
  if (res.status === 409) return { ok: false, message: "Already cancelled" };
  if (!res.ok) return { ok: false, message: `Error ${res.status}` };
  return { ok: true, message: `Order ${id} cancelled` };
}

export function CancelForm() {
  const [state, action, pending] = useActionState(cancelOrder, {
    ok: false,
    message: "",
  });

  return (
    <form action={action}>
      <input name="orderId" placeholder="ORD-1" />
      <button disabled={pending}>{pending ? "Cancelling…" : "Cancel"}</button>
      {state.message && (
        <p role="status" data-testid="msg">
          {state.message}
        </p>
      )}
    </form>
  );
}
```

**Expected output:**

```
[Cancel] click with ORD-1 → "Order ORD-1 cancelled"
Double submit while pending → button shows "Cancelling…", disabled
Empty submit → "Order ID required"
```

**Senior takeaway:** Actions serialize mutations through the transition scheduler — pending UI is built-in; prefer them over ad-hoc `onSubmit` + three `useState` flags.

---

### Exercise B29 — RSC split: server fetch, client interactivity

**Task:** In a Next.js App Router page, fetch orders on the server (no `"use client"`). Pass serializable props to a client `CancelButton` that calls an API route.

**Solution:**

```tsx
// app/orders/page.tsx — Server Component
import { CancelButton } from "./CancelButton";

type Order = { id: string; status: "OPEN" | "SHIPPED" };

async function getOrders(): Promise<Order[]> {
  const res = await fetch("https://api.internal/orders", { cache: "no-store" });
  return res.json();
}

export default async function OrdersPage() {
  const orders = await getOrders();
  return (
    <ul>
      {orders.map((o) => (
        <li key={o.id}>
          {o.id} — {o.status}
          {o.status === "OPEN" && <CancelButton orderId={o.id} />}
        </li>
      ))}
    </ul>
  );
}
```

```tsx
// app/orders/CancelButton.tsx — Client Component
"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

export function CancelButton({ orderId }: { orderId: string }) {
  const router = useRouter();
  const [pending, start] = useTransition();

  return (
    <button
      disabled={pending}
      onClick={() =>
        start(async () => {
          await fetch(`/api/orders/${orderId}/cancel`, { method: "POST" });
          router.refresh(); // re-run Server Component fetch
        })
      }
    >
      {pending ? "…" : "Cancel"}
    </button>
  );
}
```

**Expected output:** HTML from server includes order list (view source shows data). Click Cancel → row updates after `router.refresh()` without full client-side data layer.

**Senior takeaway:** Server Components shrink the JS bundle — only ship `"use client"` islands that need events, hooks, or browser APIs.

---

### Exercise B30 — TanStack Query v5 + `useTransition`

**Task:** List orders with `@tanstack/react-query` v5. Filter by status using local state wrapped in `useTransition` so typing stays responsive while the filtered list defers.

**Solution:**

```tsx
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { useMemo, useState, useTransition } from "react";

type Order = { id: string; status: "OPEN" | "SHIPPED" };

const qc = new QueryClient();

function OrdersInner() {
  const queryClient = useQueryClient();
  const { data = [], isPending } = useQuery({
    queryKey: ["orders"],
    queryFn: async () => (await fetch("/api/orders")).json() as Order[],
  });

  const [filter, setFilter] = useState<"ALL" | "OPEN">("ALL");
  const [deferredFilter, setDeferredFilter] = useState(filter);
  const [isPendingTransition, startTransition] = useTransition();

  const visible = useMemo(
    () =>
      deferredFilter === "ALL"
        ? data
        : data.filter((o) => o.status === deferredFilter),
    [data, deferredFilter]
  );

  const cancel = useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/orders/${id}/cancel`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["orders"] }),
  });

  return (
    <div>
      <select
        value={filter}
        onChange={(e) => {
          const v = e.target.value as "ALL" | "OPEN";
          setFilter(v);
          startTransition(() => setDeferredFilter(v));
        }}
      >
        <option value="ALL">All</option>
        <option value="OPEN">Open only</option>
      </select>
      {(isPending || isPendingTransition) && <span aria-busy>Updating…</span>}
      <ul>
        {visible.map((o) => (
          <li key={o.id}>
            {o.id} — {o.status}
            <button onClick={() => cancel.mutate(o.id)}>Cancel</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function OrdersApp() {
  return (
    <QueryClientProvider client={qc}>
      <OrdersInner />
    </QueryClientProvider>
  );
}
```

**Expected output:** Switching filter on 500-row list keeps select snappy; list briefly shows `Updating…` then filtered rows. Cancel invalidates cache and refetches.

**Senior takeaway:** TanStack Query owns server cache; `useTransition` marks filter recomputation as non-urgent — combine them instead of blocking the main thread.

---

### Exercise C29 — RHF + Zod + Problem Details, Zustand vs Redux, Compiler, Module Federation

**Task:** Build an order-cancel flow: React Hook Form + Zod parse RFC 9457 `application/problem+json` errors; Zustand for ephemeral toast UI; document when Redux Toolkit fits; enable React Compiler; expose `CancelPanel` as a Module Federation remote consumed by a host shell.

**Solution:**

```tsx
// schemas/order.ts
import { z } from "zod";

export const cancelSchema = z.object({
  orderId: z.string().regex(/^ORD-\d+$/, "Format: ORD-123"),
  reason: z.string().min(3, "Reason required"),
});
export type CancelInput = z.infer<typeof cancelSchema>;

// api/problem.ts — RFC 9457 Problem Details
export type Problem = {
  type: string;
  title: string;
  status: number;
  detail?: string;
  errors?: Record<string, string[]>;
};

export async function cancelOrder(input: CancelInput): Promise<void> {
  const res = await fetch("/api/orders/cancel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (res.ok) return;
  const problem: Problem = await res.json();
  throw problem;
}
```

```tsx
// store/toast.ts — Zustand: ephemeral UI, no time-travel needed
import { create } from "zustand";

type ToastState = {
  message: string | null;
  show: (msg: string) => void;
  clear: () => void;
};

export const useToast = create<ToastState>((set) => ({
  message: null,
  show: (message) => set({ message }),
  clear: () => set({ message: null }),
}));

// Redux fits when: cross-tab audit log, middleware (RTK Query + listeners),
// undo/redo on order workflow — NOT for a single toast string.
```

```tsx
// CancelForm.tsx — RHF + Zod resolver
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { cancelSchema, CancelInput } from "./schemas/order";
import { cancelOrder, Problem } from "./api/problem";
import { useToast } from "./store/toast";

export function CancelForm() {
  const toast = useToast();
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<CancelInput>({ resolver: zodResolver(cancelSchema) });

  const onSubmit = handleSubmit(async (data) => {
    try {
      await cancelOrder(data);
      toast.show(`Cancelled ${data.orderId}`);
    } catch (e) {
      const p = e as Problem;
      if (p.errors) {
        Object.entries(p.errors).forEach(([field, msgs]) =>
          setError(field as keyof CancelInput, { message: msgs[0] })
        );
      } else {
        setError("root", { message: p.detail ?? p.title });
      }
    }
  });

  return (
    <form onSubmit={onSubmit}>
      <input {...register("orderId")} placeholder="ORD-1" />
      {errors.orderId && <span role="alert">{errors.orderId.message}</span>}
      <input {...register("reason")} placeholder="Customer request" />
      {errors.reason && <span role="alert">{errors.reason.message}</span>}
      {errors.root && <span role="alert">{errors.root.message}</span>}
      <button disabled={isSubmitting}>Cancel order</button>
    </form>
  );
}
```

```js
// vite.config.ts — React Compiler (babel plugin)
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [["babel-plugin-react-compiler", { target: "19" }]],
      },
    }),
  ],
});
// Compiler auto-memoizes — remove manual useMemo/useCallback where profiler shows no benefit.
```

```js
// webpack.config.js — Module Federation remote `cancel_mfe`
const { ModuleFederationPlugin } = require("webpack").container;

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: "cancel_mfe",
      filename: "remoteEntry.js",
      exposes: { "./CancelPanel": "./src/CancelForm.tsx" },
      shared: { react: { singleton: true }, "react-dom": { singleton: true } },
    }),
  ],
};
```

```tsx
// host-shell/src/App.tsx — dynamic import remote
import React, { lazy, Suspense } from "react";

const CancelPanel = lazy(() => import("cancel_mfe/CancelPanel"));

export function App() {
  return (
    <Suspense fallback={<p>Loading MFE…</p>}>
      <CancelPanel />
    </Suspense>
  );
}
```

**Mock 422 Problem Details:**

```json
{
  "type": "https://api.example.com/problems/validation",
  "title": "Validation failed",
  "status": 422,
  "errors": { "orderId": ["Order not found"] }
}
```

**Expected output:**

```
Submit ORD-999 → inline "Order not found" under orderId (not alert())
Submit ORD-1 + reason → toast "Cancelled ORD-1"
Host shell at localhost:3000 loads remoteEntry.js; CancelPanel renders without duplicating React
```

**Senior takeaway:** Validate on the client for UX, on the server for truth; map Problem Details field errors to RHF with `setError`. Use Zustand for local UI chrome, Redux when multiple teams need predictable global event reducers. Federation shares UI, not business rules — keep cancel API auth on the BFF.

---

## Stats

| Section | Count |
|---------|------:|
| Part A — Basic | 12 |
| Part B — Intermediate | 12 |
| Part C — Hard | 9 |
| **Total** | **33** |
