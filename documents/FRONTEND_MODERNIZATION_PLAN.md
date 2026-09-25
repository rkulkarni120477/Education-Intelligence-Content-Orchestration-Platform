# Frontend Modernization Plan
## Education Intelligence & Content Orchestration Platform

**Document Status:** Analysis Complete | Ready for Implementation  
**Last Updated:** September 24, 2026  
**Frontend Framework:** Next.js 14 + React 18 + Tailwind CSS  

---

## Executive Summary

The existing frontend has:
- ✅ Basic authentication and layout structure (Next.js 14, React 18)
- ✅ Responsive Tailwind CSS design system (brown/tan theme)
- ✅ Dashboard entry point with navigation
- ✅ Environment-based API configuration pointing to http://localhost:8000

**Current Gaps:**
- No connection to actual backend API
- Navigation structure doesn't align with product workflows (education-focused, not generic)
- Missing: content library, standards browsing, alignment workspace, authoring studio, review inbox, analytics
- No state management for complex workflows
- Placeholder UI without real data integration

**Recommendation:** Modernize incrementally, preserving the Next.js/Tailwind stack and adding real API integration, role-based navigation, and education-specific workflows.

---

## Current Frontend Inventory

### Project Structure
```
frontend/
├── app/
│   ├── page.tsx              # Login page (basic form)
│   ├── layout.tsx            # Root layout with color tokens
│   ├── globals.css           # Base styles
│   └── dashboard/
│       ├── page.tsx          # Dashboard placeholder
│       └── layout.tsx        # Dashboard layout with navigation
├── components/               # (currently empty - ready for reuse)
├── utils/
│   └── errorHandler.ts       # Basic error handler
├── public/                   # Assets
├── package.json              # Dependencies (axios, tailwind, zustand, react-query)
├── tailwind.config.js        # Tailwind theme (brown/tan palette)
└── tsconfig.json             # TypeScript config
```

### Current Stack
- **Framework:** Next.js 14.2 (App Router)
- **UI:** React 18.2
- **Styling:** Tailwind CSS 3.3 + PostCSS
- **HTTP:** axios 1.6
- **State:** zustand 4.4 (installed but unused)
- **Data:** react-query 3.39 (installed but unused)
- **Components:** @headlessui/react, @heroicons/react (installed but unused)

### Current Authentication
- **Method:** localStorage-based (hardcoded email/password)
- **Flow:** Simple login → redirect to /dashboard
- **Status:** Mock implementation, no API integration

### Current Design System
- **Color Palette:** Brown/tan theme (brand colors in HTML)
  - Dark brown: #6B4423
  - Medium brown: #8B5A3C
  - Light tan: #D2B48C
  - Cream: #FFF8F0
- **Typography:** Tailwind defaults (no custom scale)
- **Components:** None yet (basic HTML + Tailwind classes)

---

## Product Context Alignment

### Education Workflows to Support
1. **Content Management** → Content Library + Ingestion
2. **Standards Browsing** → Standards Explorer
3. **Curriculum Navigation** → Curriculum Structure
4. **Evidence-Based Alignment** → Alignment Workspace
5. **Draft Generation** → Authoring Studio
6. **Human Review** → Review Inbox
7. **Analytics & Reporting** → Analytics Dashboard
8. **User & Tenant Management** → Administration

### Primary Personas
- Tenant Administrator (full access)
- Curriculum Designer (curriculum + alignment + authoring)
- Content Administrator (library + ingestion)
- Instructional Designer (authoring + alignment)
- Reviewer/Approver (review inbox + analytics)
- Teacher (view published content, optional)

---

## Proposed Information Architecture

```
Navigation (Role-Based):

Home
├── Recent Work
├── Pending Reviews
├── Processing Jobs
└── Quick Actions (role-based)

Content Library
├── Collections
├── Search & Filter
├── Upload Interface
└── Asset Preview

Ingestion
├── Job Status
├── Processing Stages
├── Extraction Review
└── Error Handling

Standards Explorer
├── Framework Selector
├── Searchable Hierarchy
├── Grade/Subject Filter
└── Standard Details

Curriculum Structure
├── Curriculum Browser
├── Units & Objectives
├── Scope & Sequence
└── Validation Issues

Alignment Workspace
├── Content Selection
├── Candidate Standards (ranked)
├── Evidence Inspector
└── Review Actions (accept/reject/edit)

Authoring Studio
├── Artifact Type Selector (lesson/activity/assessment)
├── Content & Objectives Picker
├── Structured Editor
├── Citations & References
└── Generate/Regenerate

Review Inbox
├── Assigned Tasks
├── Artifact Preview
├── Comments & History
└── Approve/Return Actions

Analytics
├── Coverage Reports
├── Gap Analysis
├── Curriculum Maps
└── Export Options

Administration
├── Members & Roles
├── Tenant Settings
├── Integration Status
└── Audit History
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1)
**Goal:** Establish real API integration, role-aware navigation, and shared layout components.

**Tasks:**
1. Add API service layer (hooks for standards, curriculum, alignments, lessons, assessments)
2. Create shared layout components (header, sidebar navigation, footer)
3. Implement role-based route protection
4. Add tenant context to all API requests (X-Tenant-ID header)
5. Build design system components (buttons, cards, forms, status badges)
6. Create API client with error handling and loading states

**Files to Create:**
- `lib/api/client.ts` – Axios instance with tenant context
- `lib/api/standards.ts` – Standards API hooks
- `lib/api/curriculum.ts` – Curriculum API hooks
- `lib/api/alignments.ts` – Alignment API hooks
- `lib/api/lessons.ts` – Lesson API hooks
- `lib/api/assessments.ts` – Assessment API hooks
- `lib/auth.ts` – Auth context and token management
- `lib/tenant.ts` – Tenant context management
- `components/Layout/Header.tsx` – Navigation header
- `components/Layout/Sidebar.tsx` – Role-based sidebar
- `components/Common/Button.tsx` – Reusable button
- `components/Common/Card.tsx` – Card component
- `components/Common/Badge.tsx` – Status/tag badges
- `components/Common/Skeleton.tsx` – Loading placeholder
- `app/layout.tsx` (updated) – Add auth/tenant providers
- `tailwind.config.js` (updated) – Extend design system

**Deliverable:** Role-aware navigation, real API calls, design system foundation.

---

### Phase 2: Home & Content Library (Week 2)
**Goal:** Create a functional home page showing recent work and content library interface.

**Tasks:**
1. Build home page with recent work, pending reviews, processing jobs
2. Implement content library with search, filter, and upload
3. Add content asset preview modal
4. Create upload interface with progress tracking
5. Display asset metadata and version history

**Files to Create:**
- `app/home/page.tsx` – Home dashboard
- `app/content/page.tsx` – Content library
- `components/Content/LibraryGrid.tsx` – Content grid/table
- `components/Content/AssetPreview.tsx` – Preview modal
- `components/Content/UploadWidget.tsx` – Upload interface
- `components/Content/SearchBar.tsx` – Search & filter

**Deliverable:** Home page showing recent work; content library with functional upload.

---

### Phase 3: Standards & Curriculum Explorer (Week 3)
**Goal:** Build standards and curriculum browsing interfaces.

**Tasks:**
1. Implement searchable standards hierarchy browser
2. Create curriculum structure navigator (tree view)
3. Add framework version selector
4. Build standard detail view with related items
5. Implement curriculum unit and objective views

**Files to Create:**
- `app/standards/page.tsx` – Standards explorer
- `app/curriculum/page.tsx` – Curriculum navigator
- `components/Standards/HierarchyBrowser.tsx` – Tree view
- `components/Standards/StandardDetail.tsx` – Detail panel
- `components/Curriculum/CurriculumTree.tsx` – Curriculum tree
- `components/Curriculum/ObjectiveDetail.tsx` – Objective info
- `components/Common/SearchableTree.tsx` – Reusable tree component

**Deliverable:** Functional standards and curriculum browsing.

---

### Phase 4: Alignment Workspace (Week 4)
**Goal:** Build evidence-centered alignment review interface.

**Tasks:**
1. Create alignment workspace with content and curriculum context
2. Display ranked candidate standards with confidence
3. Build evidence inspector showing source excerpts and rationale
4. Implement accept/reject/edit/defer actions
5. Add confirmation and status updates

**Files to Create:**
- `app/alignment/page.tsx` – Alignment workspace
- `components/Alignment/WorkspaceLayout.tsx` – Main layout
- `components/Alignment/CandidatesList.tsx` – Ranked candidates
- `components/Alignment/EvidenceInspector.tsx` – Evidence view
- `components/Alignment/ActionButtons.tsx` – Review actions
- `components/Common/ConfidenceBadge.tsx` – Confidence display
- `components/Common/SourceReference.tsx` – Source citation

**Deliverable:** Evidence-based alignment review workflow.

---

### Phase 5: Authoring Studio (Week 5)
**Goal:** Build lesson/activity/assessment creation interface.

**Tasks:**
1. Create artifact type selector and metadata form
2. Build structured editor for different artifact types
3. Implement section-level editing and regeneration
4. Add citation display and source references
5. Create draft comparison and version history

**Files to Create:**
- `app/authoring/page.tsx` – Studio launcher
- `app/authoring/[type]/page.tsx` – Type-specific editor
- `components/Authoring/TypeSelector.tsx` – Artifact selection
- `components/Authoring/MetadataForm.tsx` – Metadata input
- `components/Authoring/StructuredEditor.tsx` – Editor interface
- `components/Authoring/CitationDisplay.tsx` – Citations panel
- `components/Authoring/RegenerateSection.tsx` – Regenerate UI

**Deliverable:** Functional authoring studio with draft management.

---

### Phase 6: Review Inbox (Week 6)
**Goal:** Build review and approval workflow interface.

**Tasks:**
1. Create review task list with filters
2. Build artifact preview for different types
3. Implement comment and change request system
4. Add approve/return/reject actions
5. Display review history and timeline

**Files to Create:**
- `app/review/page.tsx` – Review inbox
- `app/review/[id]/page.tsx` – Review detail
- `components/Review/TaskList.tsx` – Task listing
- `components/Review/ArtifactPreview.tsx` – Preview modal
- `components/Review/CommentSection.tsx` – Comments
- `components/Review/ReviewActions.tsx` – Approve/return/reject
- `components/Review/Timeline.tsx` – History timeline

**Deliverable:** Complete review and approval workflow.

---

### Phase 7: Analytics & Administration (Week 7)
**Goal:** Build reporting, analytics, and admin interfaces.

**Tasks:**
1. Create coverage and gap analysis dashboard
2. Build curriculum maps and alignment reports
3. Implement export functionality
4. Create member and role management interface
5. Add tenant configuration and integration setup

**Files to Create:**
- `app/analytics/page.tsx` – Analytics dashboard
- `app/analytics/coverage/page.tsx` – Coverage reports
- `app/analytics/gaps/page.tsx` – Gap analysis
- `app/admin/page.tsx` – Admin console
- `app/admin/members/page.tsx` – Member management
- `app/admin/settings/page.tsx` – Tenant settings
- `components/Analytics/CoverageChart.tsx` – Coverage visualization
- `components/Analytics/GapTable.tsx` – Gap listing
- `components/Admin/MemberForm.tsx` – Member CRUD
- `components/Admin/RoleSelector.tsx` – Role assignment

**Deliverable:** Analytics, reporting, and administration interfaces.

---

### Phase 8: Polish & Testing (Week 8)
**Goal:** Complete accessibility, responsiveness, and error handling.

**Tasks:**
1. Audit keyboard navigation and screen reader support (WCAG 2.2 AA)
2. Test responsive layouts at tablet and desktop sizes
3. Implement comprehensive error states and empty states
4. Add loading and processing indicators
5. Test all role-based access controls
6. Document API contracts and missing endpoints
7. Create user guide and accessibility statement

**Deliverable:** Fully accessible, responsive, tested application.

---

## API Integration Points

### Required Backend Endpoints (Verify with Backend)

**Standards API:**
- `GET /api/v1/standards/frameworks` – List frameworks
- `GET /api/v1/standards/frameworks/{id}/standards` – Standards in framework
- `GET /api/v1/standards/{id}` – Standard details
- `POST /api/v1/standards/search` – Search standards

**Curriculum API:**
- `GET /api/v1/curricula` – List curricula
- `GET /api/v1/curricula/{id}` – Curriculum structure
- `GET /api/v1/curricula/{id}/units` – Curriculum units
- `GET /api/v1/objectives` – Learning objectives

**Alignment API:**
- `GET /api/v1/alignments` – List alignments
- `POST /api/v1/alignments` – Create alignment
- `PUT /api/v1/alignments/{id}` – Update alignment
- `GET /api/v1/alignments/{id}/evidence` – Evidence details

**Lessons API:**
- `GET /api/v1/lessons` – List lessons
- `POST /api/v1/lessons` – Create lesson
- `PUT /api/v1/lessons/{id}` – Update lesson
- `POST /api/v1/lessons/{id}/regenerate` – Regenerate section

**Assessments API:**
- `GET /api/v1/assessments` – List assessments
- `POST /api/v1/assessments` – Create assessment
- `PUT /api/v1/assessments/{id}` – Update assessment

**Content API:**
- `GET /api/v1/content` – List content
- `POST /api/v1/content/upload` – Upload content
- `GET /api/v1/content/{id}/ingestion-status` – Ingestion progress

**Review API:**
- `GET /api/v1/reviews` – Assigned reviews
- `POST /api/v1/reviews/{id}/approve` – Approve
- `POST /api/v1/reviews/{id}/return` – Return for changes
- `POST /api/v1/reviews/{id}/reject` – Reject

**Admin API:**
- `GET /api/v1/users` – List users
- `POST /api/v1/users` – Create user
- `PUT /api/v1/users/{id}/role` – Update role
- `GET /api/v1/tenants/{id}/settings` – Tenant settings

### API Assumptions
- All endpoints require `X-Tenant-ID` header
- Authentication uses JWT Bearer tokens
- Responses follow consistent error format
- Pagination uses `?page=1&limit=20`

---

## Design System Implementation

### Color Palette (Keep Existing)
```
Primary Brown: #6B4423
Secondary Brown: #8B5A3C  
Accent Tan: #D2B48C
Background Cream: #FFF8F0

Neutral Grays (for UI):
- Slate 50: #f8fafc (lightest)
- Slate 100: #f1f5f9
- Slate 200: #e2e8f0
- Slate 500: #64748b (medium)
- Slate 700: #334155
- Slate 900: #0f172a (darkest)

Status Colors:
- Success: #10b981 (green)
- Warning: #f59e0b (amber)
- Error: #ef4444 (red)
- Info: #3b82f6 (blue)
```

### Component Library (Create)
```
Button
├── Variant: primary, secondary, tertiary, danger
├── Size: sm, md, lg
└── State: default, loading, disabled

Card
├── Header, body, footer sections
└── Variant: default, outlined, elevated

Badge
├── Variant: default, success, warning, error, info
└── Size: sm, md

Input
├── Text, email, password, number
└── State: default, error, disabled, loading

Select
├── Single, multi-select
└── Search support

Modal
├── Header, body, footer
└── Dismiss and action buttons

Tabs
├── Tab list and content
└── Keyboard navigation

Loading Skeleton
└── Animated placeholder

Status Indicator
├── Status: processing, success, error, pending
└── With label and icon
```

### Tailwind Configuration
```js
// Update tailwind.config.js with:
colors: {
  brand: { /* brown theme */ },
  status: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  }
},
spacing: {
  // Use 4px base unit
  'gutter': '1.5rem',
},
typography: {
  // Define heading scales
  // Body: 16px/24px
  // Labels: 14px/20px
}
```

---

## State Management Strategy

### Zustand Stores (Already Installed)
```typescript
// stores/auth.ts
interface AuthStore {
  user: User | null
  token: string | null
  login: (email, password) => Promise<void>
  logout: () => void
  setTenantId: (id: string) => void
}

// stores/tenant.ts
interface TenantStore {
  tenantId: string
  switchTenant: (id: string) => void
}

// stores/alignment.ts
interface AlignmentStore {
  selectedContent: string | null
  selectedCurriculum: string | null
  candidates: Alignment[]
  setSelectedContent: (id: string) => void
  setCandidates: (items: Alignment[]) => void
}

// stores/authoring.ts
interface AuthoringStore {
  draft: Lesson | Activity | Assessment | null
  sections: Section[]
  updateSection: (id: string, content: string) => void
  saveDraft: () => Promise<void>
}
```

### Data Fetching with react-query
```typescript
// queries/standards.ts
export const useStandards = (frameworkId: string) => {
  return useQuery(['standards', frameworkId], 
    () => api.getStandards(frameworkId))
}

export const useSearchStandards = (query: string) => {
  return useQuery(['standards-search', query],
    () => api.searchStandards(query))
}

// Similar hooks for curriculum, alignments, lessons, etc.
```

---

## Routing Structure

```
/                           # Login
/home                       # Home dashboard (auth required)
/content                    # Content library
/content/upload            # Upload interface
/ingestion                 # Ingestion status
/standards                 # Standards explorer
/standards/[id]           # Standard detail
/curriculum               # Curriculum navigator
/curriculum/[id]          # Curriculum detail
/alignment                # Alignment workspace
/alignment/[id]           # Alignment detail
/authoring                # Authoring launcher
/authoring/lesson         # Lesson editor
/authoring/activity       # Activity editor
/authoring/assessment     # Assessment editor
/review                   # Review inbox
/review/[id]             # Review detail
/analytics                # Analytics dashboard
/analytics/coverage       # Coverage reports
/analytics/gaps           # Gap analysis
/admin                    # Administration console
/admin/members            # Member management
/admin/settings           # Tenant settings
/settings/profile         # User profile
/settings/notifications   # Notification preferences
```

---

## Key Implementation Decisions

### 1. Keep Existing Stack
- ✅ Next.js 14 with App Router
- ✅ React 18 functional components
- ✅ Tailwind CSS for styling
- ✅ zustand for state management
- ✅ react-query for data fetching
- ✅ axios for HTTP

### 2. Authentication
- Replace mock auth with real JWT flow
- Store token in httpOnly cookie (next-auth or custom)
- Validate on every protected route
- Include X-Tenant-ID header in all API requests

### 3. API Integration
- Create reusable service layer (lib/api/)
- Use react-query hooks for data fetching
- Implement error boundaries with user-friendly messages
- Show loading and empty states for all data views

### 4. Tenant Context
- Add middleware to extract and validate tenant from request
- Pass tenant ID in X-Tenant-ID header for all API calls
- Show tenant name in header
- Allow switching tenants (if user has multiple)

### 5. Role-Based Access
- Define role enum (Admin, Standards Admin, Curriculum Admin, Instructional Designer, Teacher, Reviewer, Approver)
- Use role to show/hide navigation items
- Implement route protection with role checks
- Backend remains authoritative for permission checks

### 6. Component Architecture
- Presentational components (UI only, no data fetching)
- Container components (data fetching with react-query hooks)
- Page components (route-level, layout + container logic)
- Shared components in `components/Common/`
- Feature-specific components in `components/{Feature}/`

### 7. Error Handling
- Try/catch wrapper for async operations
- Error boundary component for React errors
- Toast notifications for user feedback
- Retry buttons for failed data loads
- Fallback UI for permission denied states

### 8. Accessibility
- Semantic HTML (headings, landmarks, labels)
- ARIA attributes for dynamic content
- Keyboard navigation throughout
- Color + icons for status (not color alone)
- Focus indicators on all interactive elements
- Screen reader testing with NVDA/JAWS

---

## Success Criteria

- ✅ Navigation reflects all 10 product areas
- ✅ Users can log in and see role-appropriate interface
- ✅ Content library functional (list, search, upload)
- ✅ Standards and curriculum browsing work
- ✅ Alignment workspace shows evidence and allows decisions
- ✅ Authoring studio creates and edits drafts
- ✅ Review inbox shows assigned work with approval flow
- ✅ Analytics and admin sections accessible to authorized users
- ✅ All major workflows support keyboard navigation
- ✅ Responsive at desktop and tablet widths
- ✅ Loading, error, empty, and permission states visible
- ✅ API contracts documented; missing endpoints flagged
- ✅ Design system reusable across all pages

---

## Next Steps

1. **Review & Approval:** Share this plan with product and engineering
2. **Backend Verification:** Confirm API endpoints match this plan
3. **Week 1 Kickoff:** Start Phase 1 (foundation + API integration)
4. **Weekly Reviews:** Demo each phase, iterate based on feedback
5. **Testing Throughout:** Accessibility, keyboard nav, responsiveness
6. **Documentation:** Update as implementation proceeds

---

**Prepared by:** Claude Haiku 4.5  
**Framework:** Next.js 14, React 18, Tailwind CSS  
**Timeline:** 8 weeks for complete implementation  
**Status:** Ready for approval and Phase 1 start
