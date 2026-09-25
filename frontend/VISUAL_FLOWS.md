# Visual Flows & Page Layouts

## User Journey Flowchart

```
┌─────────────────────┐
│   Open Application  │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────────────┐
│   Projects Dashboard (/home)         │
│  ┌────────────────────────────────┐  │
│  │ Header: My Projects            │  │
│  │ [+ New Project Button]         │  │
│  ├────────────────────────────────┤  │
│  │                                │  │
│  │  [Project Card] [Project Card] │  │
│  │  [Project Card] [Project Card] │  │
│  │                                │  │
│  └────────────────────────────────┘  │
└──────────┬──────────────────────────┘
           │
      [Click New Project]
           │
           ▼
┌──────────────────────────────────────┐
│  Create Project Form (Inline)        │
│  ┌────────────────────────────────┐  │
│  │ Project Name: ___________      │  │
│  │ Description: ____________      │  │
│  │                                │  │
│  │ [Create & Configure Button]    │  │
│  └────────────────────────────────┘  │
└──────────┬──────────────────────────┘
           │
      [Submit]
           │
           ▼
┌──────────────────────────────────────────────┐
│  Project Configuration Page                  │
│  (/projects/[projectId]/configure)          │
│                                              │
│  ┌────────────┬──────────────────────────┐  │
│  │Action Menu │ Config Dashboard         │  │
│  ├────────────┤──────────────────────────┤  │
│  │ ○ Action 1 │ [Overview Card]          │  │
│  │ ○ Action 2 │ ┌────────────────────┐  │  │
│  │ ○ Action 3 │ │ Inputs Section     │  │  │
│  │ ○ Action 4 │ ├────────────────────┤  │  │
│  │ ○ Action 5 │ │ Upload Files       │  │  │
│  │ ○ Action 6 │ ├────────────────────┤  │  │
│  │            │ │ Outputs Section    │  │  │
│  │            │ ├────────────────────┤  │  │
│  │            │ │ Workflow Info      │  │  │
│  │            │ ├────────────────────┤  │  │
│  │            │ │[▶ Proceed Button]  │  │  │
│  │            │ └────────────────────┘  │  │
│  └────────────┴──────────────────────────┘  │
│                                              │
└──────────┬─────────────────────────────────┘
           │
      [Select Action & Upload Files]
           │
           ▼
       [Click Proceed]
           │
           ▼
┌──────────────────────────────────────────────┐
│  Workflow Progress Monitor                   │
│  (/projects/[projectId]/workflow/[id])      │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Overall Progress:  65%                 │ │
│  │ ████████████░░░░░░░░░░░░░░░░░░░░░░░░ │ │
│  │                                        │ │
│  │ Current Agent: Content Generation     │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Agent Timeline                         │ │
│  │ ✓ Requirements Understanding          │ │
│  │ ✓ Input Validation                    │ │
│  │ ⚙ Content Generation [ACTIVE]         │ │
│  │ ◯ Accessibility Audit                 │ │
│  │ ◯ Final Packaging                     │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Requirements Understanding             │ │
│  │ Purpose: Generate course materials...  │ │
│  │ Deliverables:                          │ │
│  │  • Course modules                      │ │
│  │  • Assessment quizzes                  │ │
│  │ Timeline: ~30 minutes                  │ │
│  └────────────────────────────────────────┘ │
│                                              │
└──────────┬─────────────────────────────────┘
           │
      [Monitor updates every 2 seconds]
           │
           ▼
┌──────────────────────────────────────────────┐
│  Completion Screen (100%)                    │
│                                              │
│           🎉 Workflow Complete! 🎉          │
│                                              │
│  Your workflow has been executed             │
│  successfully. All outputs are ready.        │
│                                              │
│     [Back to Dashboard Button]               │
│                                              │
└──────────────────────────────────────────────┘
```

---

## Projects Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER (Sticky)                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 📊 My Projects                    [+ New Project Button] │   │
│  │ Manage your AI agent projects                            │   │
│  └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  │  PROJECT CARD    │  │  PROJECT CARD    │  │  PROJECT CARD    │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│  │ 🟢 Title         │  │ 📝 Title         │  │ 📦 Title         │
│  │                  │  │                  │  │                  │
│  │ Description text │  │ Description text │  │ Description text │
│  │ here...          │  │ here...          │  │ here...          │
│  │                  │  │                  │  │                  │
│  │ Content: 12      │  │ Content: 8       │  │ Content: 5       │
│  │                  │  │                  │  │                  │
│  │ Created: 2026... │  │ Created: 2026... │  │ Created: 2026... │
│  │                  │  │                  │  │                  │
│  │ [Open] [Delete]  │  │ [Open] [Delete]  │  │ [Open] [Delete]  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘
│
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  │  PROJECT CARD    │  │  PROJECT CARD    │  │  PROJECT CARD    │
│  │ [Similar layout] │  │ [Similar layout] │  │ [Similar layout] │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘
│
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Configuration Page Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                    │
│  Breadcrumb: Projects / Configure                                         │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────────────────┐  ┌─────────────────────────────────────────┐ │
│  │   ACTION MENU          │  │  CONFIGURATION DASHBOARD                 │ │
│  ├────────────────────────┤  ├─────────────────────────────────────────┤ │
│  │                        │  │                                         │ │
│  │  Primary Action Menu   │  │ ┌─────────────────────────────────────┐ │ │
│  │                        │  │ │ Action Title                        │ │ │
│  │ [◆ Action 1]           │  │ │ Description...                      │ │ │
│  │ [◆ Action 2]           │  │ │ Agent: Specific Agent Name          │ │ │
│  │ [◆ Action 3] SELECTED  │  │ └─────────────────────────────────────┘ │ │
│  │ [◆ Action 4]           │  │                                         │ │
│  │ [◆ Action 5]           │  │ ┌─────────────────────────────────────┐ │ │
│  │ [◆ Action 6]           │  │ │ 📥 INPUTS                          │ │ │
│  │                        │  │ │ • Required file 1                  │ │ │
│  │                        │  │ │ • Required file 2                  │ │ │
│  │                        │  │ │                                     │ │ │
│  │                        │  │ │ [📁 Upload Files Area]              │ │ │
│  │                        │  │ │                                     │ │ │
│  │                        │  │ │ ✓ Uploaded: File 1 [x]             │ │ │
│  │                        │  │ │ ✓ Uploaded: File 2 [x]             │ │ │
│  │                        │  │ └─────────────────────────────────────┘ │ │
│  │                        │  │                                         │ │
│  │                        │  │ ┌─────────────────────────────────────┐ │ │
│  │                        │  │ │ 📤 OUTPUTS                         │ │ │
│  │                        │  │ │ • Deliverable 1                    │ │ │
│  │                        │  │ │ • Deliverable 2                    │ │ │
│  │                        │  │ └─────────────────────────────────────┘ │ │
│  │                        │  │                                         │ │
│  │                        │  │ ┌─────────────────────────────────────┐ │ │
│  │                        │  │ │ ⚙️ WORKFLOW INFO                    │ │ │
│  │                        │  │ │ Agent: Primary Agent                │ │ │
│  │                        │  │ │ Type: Multi-Agent Pipeline          │ │ │
│  │                        │  │ │ Duration: 15-45 minutes             │ │ │
│  │                        │  │ └─────────────────────────────────────┘ │ │
│  │                        │  │                                         │ │
│  │                        │  │ ┌─────────────────────────────────────┐ │ │
│  │                        │  │ │ [▶️  PROCEED TO MONITOR]            │ │ │
│  │                        │  │ │ Click to start the workflow        │ │ │
│  │                        │  │ └─────────────────────────────────────┘ │ │
│  │                        │  │                                         │ │
│  └────────────────────────┘  └─────────────────────────────────────────┘ │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Progress Monitor Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│  HEADER (Sticky)                                                         │
│  Breadcrumb: Projects / Monitor        [← Back to Dashboard Button]      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ MAIN PROGRESS CARD                                                 │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │ Overall Progress                               Progress: 65%        │  │
│  │ Status: Running                                          │          │  │
│  │                                                          ▼          │  │
│  │ ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  │
│  │                                                                    │  │
│  │ 🤖 Currently Processing: Content Generation Agent                 │  │
│  │    Working on transformation...                                   │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ AGENT EXECUTION TIMELINE                                           │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │ ✓ COMPLETED                                                       │  │
│  │ ├─ [✓ Green] Requirements Understanding                           │  │
│  │ ├─ [✓ Green] Input Validation                                    │  │
│  │ └─ [✓ Green] Knowledge Retrieval                                 │  │
│  │                                                                    │  │
│  │ ⏳ IN PROGRESS                                                     │  │
│  │ └─ [⚙️ Blue] Content Generation                                    │  │
│  │                                                                    │  │
│  │ ◯ PENDING                                                         │  │
│  │ ├─ [◯ Gray] Accessibility Audit                                  │  │
│  │ ├─ [◯ Gray] Final Validation                                     │  │
│  │ └─ [◯ Gray] Output Packaging                                     │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ ▼ REQUIREMENTS UNDERSTANDING (Collapsible)                         │  │
│  ├────────────────────────────────────────────────────────────────────┤  │
│  │                                                                    │  │
│  │ Workflow Purpose:                                                │  │
│  │ Generate comprehensive course materials including modules,       │  │
│  │ transcripts, slide decks, and assessment quizzes from provided   │  │
│  │ curriculum and source materials.                                 │  │
│  │                                                                    │  │
│  │ Expected Deliverables:                                            │  │
│  │ • Structured course package (8 modules)                          │  │
│  │ • Video transcripts and speaker notes                            │  │
│  │ • Professional slide decks (75+ slides)                          │  │
│  │ • Assessment quizzes (8 quizzes, 12+ questions each)            │  │
│  │ • Review draft in approval queue                                 │  │
│  │                                                                    │  │
│  │ Timeline:                                                         │  │
│  │ ~30-40 minutes for processing and generation, pending on file    │  │
│  │ sizes and complexity.                                             │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

```
MOBILE (< 768px)
├─ Single column layout
├─ Full-width cards
├─ Stacked action menu above dashboard
└─ Touch-friendly button sizes (44x44px)

TABLET (768px - 1024px)
├─ Two-column grid for cards
├─ Side menu and dashboard
├─ Optimized spacing
└─ Medium button sizes

DESKTOP (> 1024px)
├─ Three-column grid for cards
├─ Fixed sticky header
├─ Full three-panel layout (menu, dashboard, actions)
├─ Maximum width container (1280px)
└─ Full-size buttons and interactions
```

---

## Color Indicators in UI

```
STATUS INDICATORS:
├─ 🟢 Active       (Green #10b981)
├─ 📝 Draft        (Amber #f59e0b)
├─ 📦 Archived     (Slate #64748b)
├─ ✓ Complete      (Green #10b981)
├─ ⚙️ In Progress  (Blue #2563eb)
├─ ◯ Pending       (Slate #64748b)
└─ ✕ Error        (Red #ef4444)

SECTION COLORS:
├─ Input Cards   (Blue backgrounds)
├─ Output Cards  (Blue backgrounds)
├─ Info Cards    (Indigo backgrounds)
├─ Success States (Green backgrounds)
├─ Error States   (Red backgrounds)
└─ Warning States (Amber backgrounds)
```

---

## Interactive Elements

```
BUTTONS:
├─ Primary: Gradient Blue→Indigo with shadow
├─ Secondary: Slate border with white background
├─ Danger: Red background for deletions
└─ Loading: Disabled state with spinner

INPUTS:
├─ Text fields: Slate border, blue focus ring
├─ Dropdowns: Same as text inputs
├─ File upload: Dashed blue border, drag-and-drop
└─ Text areas: Multi-line with resize disabled

CARDS:
├─ Default: White with slate border
├─ Highlighted: Blue/indigo tint background
├─ Success: Green background
└─ Error: Red background

PROGRESS:
├─ Bar: Gradient fill with smooth animation
├─ Percentage: Large bold display
└─ Timeline: Vertical list with status colors
```

