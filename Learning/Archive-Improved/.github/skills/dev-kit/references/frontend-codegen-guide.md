# Frontend Codegen Guide

## Implementing UX Stubs

UX stubs have `// TODO:` markers. This is the contract for dev-kit.

### TODO Marker Types

| Marker | What to implement |
|--------|------------------|
| `// TODO: wire to API` | Add useQuery/service call |
| `// TODO: implement submit` | Add form submit + mutation/service call |
| `// TODO: add state management` | Add useState/useQuery/NgRx/Signals |
| `// TODO: define from db-schema.yaml` | Add TypeScript interface from `db-schema.yaml` |
| `// TODO: add validation` | Add zod schema / reactive form validators |
| `// TODO: implement navigation` | Add router.push / router.navigate |
| `// TODO: add error handling` | Add error state and display |

## API Client Setup

### React — Axios Instance
```typescript
// shared/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1',
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // redirect to login
    }
    return Promise.reject(error);
  }
);
```

### Angular — HTTP Interceptor
```typescript
// core/interceptors/auth.interceptor.ts
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    const authReq = token
      ? req.clone({ headers: req.headers.set('Authorization', `Bearer ${token}`) })
      : req;
    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) this.router.navigate(['/login']);
        return throwError(() => error);
      })
    );
  }
}
```

## TypeScript Types from DB Schema

Generate TypeScript interfaces from `db-schema.yaml`:

```typescript
// entities/order/types.ts — generated from db-schema.yaml
export interface Order {
  id: string;           // uuid PRIMARY KEY
  userId: string;       // uuid FK → users.id
  status: OrderStatus;  // PENDING | CONFIRMED | SHIPPED | DELIVERED | CANCELLED
  total: number;        // decimal
  createdAt: string;    // timestamptz
  updatedAt: string;
}

export type OrderStatus = 'PENDING' | 'CONFIRMED' | 'SHIPPED' | 'DELIVERED' | 'CANCELLED';
```

## Form Validation from Business Rules

Map business rules (BR-NNN) to form validators:

```typescript
// BR-001: Order quantity must be between 1 and 100
// BR-003: Product must be selected
const schema = z.object({
  productId: z.string().uuid('Must select a valid product'),   // BR-003
  quantity: z
    .number({ required_error: 'Quantity is required' })
    .min(1, 'Minimum 1 item')
    .max(100, 'Maximum 100 items per order'),                  // BR-001
  deliveryNote: z.string().max(500).optional(),
});
```

## Loading & Error States

Every page that fetches data must handle:
```tsx
if (isLoading) return <LoadingSkeleton />;
if (isError) return <ErrorMessage message={error.message} onRetry={refetch} />;
if (!data || data.length === 0) return <EmptyState message="No orders yet" />;
```

## Environment Variables

```
# .env.development
VITE_API_BASE_URL=http://localhost:8080/api/v1   # React/Vite
NG_APP_API_BASE_URL=http://localhost:8080/api/v1  # Angular
```

## Route Guards

```typescript
// Protect routes that require authentication
// Read auth requirement from stories.md security section
const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};
```
