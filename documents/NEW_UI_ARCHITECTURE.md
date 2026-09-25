# New UI Architecture - Visual Guide

## Page Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ STICKY HEADER                                                    │
│ ┌───────────────────────────────────────────────────────────────┤
│ │ 🚀 Multi-Agent Platform      [📚 AI Content Studio        ▼] │
│ │ Select a workflow to begin                                    │
│ └───────────────────────────────────────────────────────────────┘
├─────────────────────────────────────────────────────────────────┤
│ MAIN CONTENT AREA (max-width: 7xl)                              │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ WORKFLOW HEADER CARD                                        │ │
│ │ ┌─────────────────────────────────────────────────────────┐ │ │
│ │ │ 📚 AI Content Studio                                    │ │ │
│ │ │ Build structured course packages from PDFs, videos...   │ │ │
│ │ │ [Beginner] [Content Creation]                           │ │ │
│ │ └─────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌───────────────────────────────┬──────────────────────────────┐ │
│ │ WORKFLOW DETAILS SECTION      │ UPLOAD FILES SECTION         │ │
│ │                               │                              │ │
│ │ 🤖 Participating Agents       │ 📤 Upload Input Files        │ │
│ │ • Content Studio Agent        │                              │ │
│ │ • QA Agent                    │ [📦 Drag & drop or click]   │ │
│ │ • Knowledge Intelligence      │                              │ │
│ │                               │                              │ │
│ │ 📥 Expected Inputs            │ Selected Files:              │ │
│ │ • Content Files               │ □ file1.zip (2.5 MB)        │ │
│ │   PDF, Video, Audio           │ □ file2.zip (1.2 MB) ✕      │ │
│ │   Course materials...         │                              │ │
│ │                               │ [Upload & Process]          │ │
│ │ • Curriculum Standards        │                              │ │
│ │   Text                        │ ✓ Files under review...     │ │
│ │   Learning objectives...      │                              │ │
│ └───────────────────────────────┴──────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ EXPECTED OUTPUTS SECTION                                    │ │
│ │ ┌─────────────────┬─────────────────┬──────────────────┐   │ │
│ │ │ Structured      │ Assessment      │ Learning Paths   │   │ │
│ │ │ Modules         │ Questions       │                  │   │ │
│ │ │ Organized       │ Auto-generated  │ Recommended      │   │ │
│ │ │ course content  │ quizzes and...  │ learning seq...  │   │ │
│ │ │ [JSON]          │ [JSON]          │ [JSON]           │   │ │
│ │ └─────────────────┴─────────────────┴──────────────────┘   │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Dropdown Menu Detail

```
┌──────────────────────────────────────┐
│ Workflow Selector Button (Clicked)   │
└──────────────────────────────────────┘
        │ (Opens)
        ▼
┌──────────────────────────────────────┐
│ DROPDOWN MENU (Scrollable)           │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐  │
│ │ 📚 AI Content Studio           │  │
│ │ Build structured course...     │  │ ✓ Selected
│ │                                │  │
│ └────────────────────────────────┘  │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐  │
│ │ 👥 Workforce Skills Agent      │  │
│ │ Map employee job data...       │  │
│ │                                │  │
│ └────────────────────────────────┘  │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐  │
│ │ ✓ Skills & Standards Intel.    │  │
│ │ Cross-walk curriculum...       │  │
│ │                                │  │
│ └────────────────────────────────┘  │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐  │
│ │ ♿ Accessibility Audit & Rem.  │  │
│ │ Audit content for WCAG...      │  │
│ │                                │  │
│ └────────────────────────────────┘  │
├──────────────────────────────────────┤
│ ┌────────────────────────────────┐  │
│ │ 🧠 Knowledge Intelligence      │  │
│ │ Build an AI-powered Q&A...     │  │
│ │                                │  │
│ └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

## Component Hierarchy

```
page.tsx (Root)
│
└── WorkflowsHomeNew.tsx
    ├── State Management
    │   ├── selectedWorkflow: Workflow | null
    │   └── isDropdownOpen: boolean
    │
    ├── Header Section
    │   ├── Title & Subtitle
    │   └── Workflow Dropdown
    │       ├── Dropdown Button
    │       └── Menu (Conditional)
    │           └── Workflow List
    │               └── Workflow Item (x5)
    │
    └── Main Content Section
        └── WorkflowExecutionDashboard.tsx (Conditional)
            ├── Workflow Header Card
            ├── Workflow Details Grid
            │   ├── Left: Workflow Details Section
            │   │   ├── Agents List
            │   │   └── Inputs List
            │   └── Right: File Upload Section
            │       ├── Upload Area
            │       ├── File Input (Hidden)
            │       ├── Selected Files List
            │       ├── Upload Button
            │       └── Status Messages
            │
            └── Expected Outputs Grid
                └── Output Cards (3-5 per workflow)
```

## State Flow

```
User Lands on Page
│
├─ Set selectedWorkflow = workflows[0]
│  (AI Content Studio by default)
│
└─ Render WorkflowsHomeNew
   │
   ├─ Render Dropdown with selectedWorkflow
   │
   └─ Render WorkflowExecutionDashboard
      with selectedWorkflow props

User Clicks Dropdown
│
├─ Set isDropdownOpen = true
│
└─ Show Menu with all workflows

User Clicks Different Workflow
│
├─ Set selectedWorkflow = clicked workflow
│
├─ Set isDropdownOpen = false
│
└─ WorkflowExecutionDashboard re-renders
   with new workflow details

User Uploads Files
│
├─ Set uploadedFiles = [file1, file2, ...]
│
└─ Render file list

User Clicks Upload
│
├─ Set uploading = true
│
├─ Simulate processing (2 seconds)
│
├─ Set uploadMessage = "✓ Input files under review..."
│
├─ Set uploading = false
│
└─ After 5 seconds:
   ├─ Clear uploadedFiles
   ├─ Clear uploadMessage
   └─ Reset file input
```

## Responsive Breakpoints

```
┌─────────────────────────────────────────────────────────┐
│ MOBILE (< 768px)                                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🚀 Multi-Agent Platform                             │ │
│ │ Select a workflow to begin                          │ │
│ │                                                      │ │
│ │ [📚 AI Content Studio                            ▼] │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Workflow Header Card                                │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Workflow Details (Full Width)                       │ │
│ │ • Agents                                            │ │
│ │ • Inputs                                            │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ File Upload (Full Width)                            │ │
│ │ • Drag & Drop                                       │ │
│ │ • Selected Files                                    │ │
│ │ • Upload Button                                     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Expected Outputs (Stacked)                          │ │
│ │ • Output 1                                          │ │
│ │ • Output 2                                          │ │
│ │ • Output 3                                          │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ TABLET (768px - 1024px)                                │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Header with Dropdown                               │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Workflow Header Card                               │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ ┌──────────────────┬──────────────────────────────┐  │
│ │ Workflow Details │ File Upload                  │  │
│ │ (Left, 50%)      │ (Right, 50%)                 │  │
│ └──────────────────┴──────────────────────────────┘  │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Expected Outputs (2 columns)                       │ │
│ │ [Output 1] [Output 2]                             │ │
│ │ [Output 3]                                        │ │
│ └────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ DESKTOP (1024px+)                                      │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Header with Dropdown                               │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Workflow Header Card                               │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ ┌──────────────────┬──────────────────────────────┐  │
│ │ Workflow Details │ File Upload                  │  │
│ │ (Left, 50%)      │ (Right, 50%)                 │  │
│ └──────────────────┴──────────────────────────────┘  │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Expected Outputs (3 columns)                       │ │
│ │ [Output 1] [Output 2] [Output 3]                  │ │
│ │ [Output 4] [Output 5] [Output 6]                  │ │
│ └────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

## Color Scheme

```
Primary Colors:
├─ Blue: #2563eb (text-blue-600)
├─ Indigo: #4f46e5 (text-indigo-600)
└─ Gradient: from-blue-600 to-indigo-600

Status Colors:
├─ Success: Green (#10b981)
├─ Error: Red (#ef4444)
├─ Warning: Amber (#f59e0b)
└─ Info: Blue (#3b82f6)

Complexity Badges:
├─ Beginner: Green (bg-green-100, text-green-800)
├─ Intermediate: Blue (bg-blue-100, text-blue-800)
└─ Advanced: Purple (bg-purple-100, text-purple-800)

Backgrounds:
├─ Primary: White (#ffffff)
├─ Secondary: Slate-50 (#f8fafc)
├─ Tertiary: Slate-100 (#f1f5f9)
└─ Hover: Blue-50 (#eff6ff)
```

## Key Differences from Previous UI

```
OLD UI                          │ NEW UI
────────────────────────────────┼────────────────────────────────
Projects Dashboard              │ Workflows Dashboard
Grid of Projects                │ Dropdown of Workflows
Project Creation Form           │ Automatic Workflow Selection
Project Details Page            │ Integrated Dashboard
Separate Pages                  │ Single Page with Components
Static Navigation               │ Sticky Header Dropdown
No File Upload                  │ Multi-Select File Upload
Project CRUD Operations         │ Workflow Execution Focus
Multiple Pages/Routes           │ Simplified Single-Page Focus
```

---

**Architecture Version**: 1.0
**Last Updated**: 2026-09-22
**Status**: Production Ready
