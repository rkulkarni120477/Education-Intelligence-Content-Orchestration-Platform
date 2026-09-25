# Phase 1 Implementation Guide

**Frontend Modernization - Phase 1: Foundation**

This guide explains what was built in Phase 1 and how to use it.

---

## Phase 1 Overview

**Goal:** Establish real API integration, role-aware navigation, and shared layout components.

**Timeline:** Completed September 24, 2026

**What's Delivered:** 17 files, ~1,500 lines of code, 100% typed with TypeScript

---

## Architecture

```
┌─────────────────────────────────────────┐
│      React Components (UI Layer)        │
│  (Phase 2+: Home, Library, etc)         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Design System Components (Phase 1)     │
│  Button, Card, Badge, Skeleton          │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  React Query Hooks (Phase 1)            │
│  useStandards, useAlignments, etc       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Zustand State Stores (Phase 1)         │
│  useAuthStore, useTenantStore           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  API Client Layer (Phase 1)             │
│  Axios instance with interceptors       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  HTTP: localhost:8000 API               │
│  Tenant ID injection via header         │
└─────────────────────────────────────────┘
```

---

## How to Use Phase 1 Foundation

### 1. API Calls (react-query hooks)

```typescript
// In any React component
import { useFrameworks, useStandards } from '@/lib/api/standards'

export function StandardsExplorer() {
  const { data: frameworks, isLoading, error } = useFrameworks()
  const { data: standards } = useStandards(selectedFramework?.id || '')

  if (isLoading) return <Skeleton />
  if (error) return <div>Error: {error.message}</div>

  return (
    <>
      <h1>Standards ({frameworks?.length})</h1>
      <ul>
        {standards?.map(s => <li key={s.id}>{s.code}: {s.description}</li>)}
      </ul>
    </>
  )
}
```

### 2. Authentication

```typescript
import { useAuthStore } from '@/lib/stores/auth'

export function LoginForm() {
  const { login, isLoading, error } = useAuthStore()

  const handleSubmit = async (email: string, password: string) => {
    try {
      await login(email, password)
      // Auto-redirected to /home by middleware
    } catch (err) {
      // Error already in store
    }
  }

  return (
    <form onSubmit={...}>
      {error && <div className="error">{error}</div>}
      {/* form fields */}
    </form>
  )
}
```

### 3. Protecting Routes

```typescript
'use client'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'

export default function HomePage() {
  const { user, isAuthenticated } = useAuthRequired()

  if (!isAuthenticated) return null // Redirects to login

  return <h1>Welcome, {user?.name}</h1>
}
```

### 4. Using Design Components

```typescript
import { Button, Card, Badge, Skeleton } from '@/components/Common'

export function ExampleCard() {
  const [isLoading, setIsLoading] = useState(false)

  return (
    <Card variant="outlined">
      <Card.Header>
        <h2>Item Title</h2>
        <Badge variant="success">Approved</Badge>
      </Card.Header>
      
      <Card.Body>
        {isLoading ? (
          <Skeleton count={3} />
        ) : (
          <p>Content here</p>
        )}
      </Card.Body>
      
      <Card.Footer>
        <Button 
          variant="primary" 
          isLoading={isLoading}
          onClick={() => setIsLoading(true)}
        >
          Save Changes
        </Button>
      </Card.Footer>
    </Card>
  )
}
```

### 5. Mutations (Creating/Updating)

```typescript
import { useCreateLesson, usePublishLesson } from '@/lib/api/lessons'

export function CreateLessonForm() {
  const createMutation = useCreateLesson()
  const publishMutation = usePublishLesson()

  const handleCreate = async (data: Lesson) => {
    const lesson = await createMutation.mutateAsync(data)
    // Lesson created
  }

  const handlePublish = async (lessonId: string) => {
    const updated = await publishMutation.mutateAsync({ id: lessonId })
    // Lesson published
  }

  return (
    <>
      <Button 
        isLoading={createMutation.isLoading}
        onClick={() => handleCreate(...)}
      >
        Create
      </Button>
      <Button 
        isLoading={publishMutation.isLoading}
        onClick={() => handlePublish(lesson.id)}
      >
        Publish
      </Button>
    </>
  )
}
```

---

## Available Hooks (All in lib/api/)

### Standards
- `useFrameworks()` – Get all frameworks
- `useStandards(frameworkId)` – Standards in framework
- `useStandardHierarchy(frameworkId)` – Hierarchical view
- `useStandard(standardId)` – Single standard detail
- `useSearchStandards(query, frameworkId?)` – Search
- `useStandardsByGradeSubject(frameworkId, grade?, subject?)` – Filter
- `useCreateFramework()` – Mutation: create framework
- `useCreateStandard()` – Mutation: create standard

### Curriculum
- `useCurricula()` – Get all curricula
- `useCurriculum(id)` – Single curriculum
- `useCurriculumStructure(id)` – Full structure with units/objectives
- `useCurriculumUnits(id)` – Units in curriculum
- `useUnitObjectives(unitId)` – Objectives in unit
- `useLearningObjectives()` – All objectives
- `useCurriculumCoverage(id, frameworkId?)` – Coverage analysis
- `useCreateCurriculum()` – Mutation
- `useCreateCurriculumUnit()` – Mutation
- `useCreateObjective()` – Mutation

### Alignments
- `useAlignments(sourceType?, sourceId?)` – List alignments
- `useAlignmentDetail(id)` – Alignment with evidence
- `useAlignmentsForStandard(standardId)` – Alignments for a standard
- `useCandidateAlignments(contentId, frameworkId?)` – Candidates for content
- `useAlignmentCoverage(curriculumId, frameworkId?)` – Coverage stats
- `useCreateAlignment()` – Mutation
- `useUpdateAlignmentStatus()` – Mutation
- `useReviewAlignment()` – Mutation: approve/reject/defer
- `useApproveAlignment()` – Mutation
- `useRejectAlignment()` – Mutation

### Lessons
- `useLessons(curriculumId?)` – List lessons
- `useLesson(id)` – Lesson with activities
- `useLessonActivities(id)` – Activities in lesson
- `useCreateLesson()` – Mutation
- `useUpdateLesson()` – Mutation
- `useAddActivity()` – Mutation
- `useUpdateActivity()` – Mutation
- `usePublishLesson()` – Mutation
- `useRegenerateSection(id, section, context?)` – Mutation
- `useDeleteLesson()` – Mutation

### Assessments
- `useAssessments(status?)` – List assessments
- `useAssessment(id)` – Assessment with items
- `useAssessmentItems(id)` – Items in assessment
- `useValidateAssessment()` – Mutation
- `useCreateAssessment()` – Mutation
- `useUpdateAssessment()` – Mutation
- `useAddAssessmentItem()` – Mutation
- `useUpdateAssessmentItem()` – Mutation
- `useDeleteAssessmentItem()` – Mutation
- `usePublishAssessment()` – Mutation

---

## Design System

### Colors
```
Primary Brand (Brown):
- Dark: #6B4423
- Medium: #8B5A3C
- Light: #D2B48C
- Background: #FFF8F0

Status:
- Success: #10b981
- Warning: #f59e0b
- Error: #ef4444
- Info: #3b82f6

Neutral:
- Slate 50-900 (light to dark)
```

### Components
```
Button
├── Variants: primary | secondary | tertiary | danger | success
├── Sizes: sm | md | lg
└── Props: isLoading, disabled, onClick, className

Card
├── Card.Header
├── Card.Body
├── Card.Footer
└── Variants: default | outlined | elevated

Badge
├── Variants: default | success | warning | error | info
├── Sizes: sm | md
├── StatusBadge: auto-detect from status string
└── ConfidenceBadge: color-coded by percentage

Skeleton
├── Variants: text | rect | circle
├── CardSkeleton: pre-made card loader
├── ListSkeleton: pre-made list loader
└── TableRowSkeleton: pre-made row loader
```

---

## State Management (Zustand)

### Auth Store
```typescript
import { useAuthStore } from '@/lib/stores/auth'

const {
  user,                         // User | null
  token,                        // JWT token
  isLoading,                    // boolean
  error,                        // string | null
  
  login(email, password),       // Promise<void>
  logout(),                     // void
  setUser(user),                // void
  setToken(token),              // void
  clearError(),                 // void
  isAuthenticated(),            // boolean
  hasRole(role),                // boolean (checks user role)
} = useAuthStore()
```

### Tenant Store
```typescript
import { useTenantStore } from '@/lib/stores/tenant'

const {
  tenant,                       // Tenant | null
  organization,                 // Organization | null
  tenants,                      // Tenant[]
  organizations,                // Organization[]
  
  setTenant(tenant),            // void
  setOrganization(org),         // void
  switchTenant(tenantId),       // Promise<void>
  switchOrganization(orgId),    // void
} = useTenantStore()
```

---

## Error Handling

### API Errors
```typescript
import { ApiClientError } from '@/lib/api/client'

try {
  const result = await something()
} catch (error) {
  if (error instanceof ApiClientError) {
    console.log(error.message)      // User-friendly message
    console.log(error.status)       // HTTP status
    console.log(error.code)         // Error code
  }
}
```

### Component Errors
```typescript
import { ErrorBoundary } from '@/components/Common'

<ErrorBoundary 
  fallback={(error, reset) => (
    <div>Something failed. <button onClick={reset}>Try again</button></div>
  )}
>
  <YourComponent />
</ErrorBoundary>
```

---

## Integration Checklist

Before building UI in Phase 2, verify:

- [ ] Backend API running on http://localhost:8000
- [ ] POST /api/v1/auth/login implemented and working
- [ ] All GET endpoints return correct data structure
- [ ] X-Tenant-ID header accepted by API
- [ ] Tenant context properly set from login response
- [ ] JWT token stored and sent with requests
- [ ] Error responses follow expected format
- [ ] CORS configured if frontend on different port

---

## Common Patterns

### Loading States
```typescript
const { data, isLoading, error } = useStandards(frameworkId)

if (isLoading) return <Skeleton />
if (error) return <div className="error">Error loading standards</div>
return <StandardsList standards={data} />
```

### Error Messages
```typescript
const mutation = useCreateLesson()

const handleCreate = async (data) => {
  try {
    await mutation.mutateAsync(data)
  } catch (error: any) {
    toast.error(error.message)
  }
}
```

### Conditional Rendering by Role
```typescript
const { user, hasRole } = useAuthStore()

return (
  <>
    {hasRole('curriculum_admin') && <CurriculumAdmin />}
    {hasRole('instructional_designer') && <AuthoringStudio />}
    {hasRole(['reviewer', 'approver']) && <ReviewInbox />}
  </>
)
```

### Combining Multiple Queries
```typescript
const { data: curriculum } = useCurriculum(curriculumId)
const { data: standards } = useStandards(frameworkId)
const { data: alignments } = useAlignments('curriculum', curriculumId)

const isReady = curriculum && standards && alignments
```

---

## Performance Tips

1. **Query Stale Time:** Already optimized (2-10 minutes depending on endpoint)
2. **Deduplication:** react-query automatically dedupes identical queries
3. **Caching:** Query results cached in memory (default 30 minutes)
4. **Pagination:** Available in query hooks (use `?page=1&limit=20`)
5. **Selective Fetching:** Only fetch what you need (query hooks are granular)

---

## Next Phase (Phase 2)

Phase 1 foundation is ready for Phase 2 UI development:

**Phase 2 Focus:**
- Home page dashboard
- Content library interface
- Upload widget
- Quick actions

All Phase 2 components will use Phase 1 hooks and design system.

---

## Troubleshooting

### Issue: API returning 401
- Check X-Tenant-ID header is being sent
- Verify JWT token is valid
- Run `apiClient.getToken()` to check token exists

### Issue: Mutations not working
- Check network tab (DevTools) for request/response
- Verify endpoint URL is correct
- Check request body matches API expectations
- Look at backend logs for server-side errors

### Issue: Components not rendering
- Verify QueryClientProvider in layout.tsx
- Check Zustand stores initialized
- Look for TypeScript errors in console
- Verify API data structure matches interface types

### Issue: TypeScript errors
- All types are exported from lib/api/ (import them)
- Hover over errors in VSCode for hints
- Check that API responses match interface definitions

---

**Phase 1 is complete and ready for Phase 2 development!**
