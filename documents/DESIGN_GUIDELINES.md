# Design Guidelines - Academian Education Platform

## Visual Identity

### Color System

#### Primary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Blue 600 | #2563eb | Primary CTA buttons, links, highlights |
| Indigo 600 | #4f46e5 | Secondary buttons, accents |
| Blue 700 | #1d4ed8 | Hover states for blue |
| Indigo 700 | #4338ca | Hover states for indigo |

#### Semantic Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Green 50 | #f0fdf4 | Success backgrounds |
| Green 600 | #16a34a | Success text, check marks |
| Red 50 | #fef2f2 | Error backgrounds |
| Red 600 | #dc2626 | Error text, warnings |
| Amber 50 | #fffbeb | Warning backgrounds |
| Amber 600 | #d97706 | Warning text |
| Blue 50 | #eff6ff | Info backgrounds |
| Blue 600 | #2563eb | Info text |

#### Neutral Colors (Slate)
| Variant | Hex | Usage |
|---------|-----|-------|
| Slate 50 | #f8fafc | Light backgrounds |
| Slate 100 | #f1f5f9 | Secondary backgrounds |
| Slate 200 | #e2e8f0 | Borders, dividers |
| Slate 300 | #cbd5e1 | Secondary borders |
| Slate 600 | #475569 | Secondary text |
| Slate 700 | #334155 | Primary text |
| Slate 900 | #0f172a | Heading text |

### Typography

#### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
```

#### Font Sizes & Weights

| Component | Size | Weight | Example |
|-----------|------|--------|---------|
| Page Heading (h1) | 30px (1.875rem) | Bold (700) | "My Projects" |
| Section Heading (h2) | 24px (1.5rem) | Bold (700) | "Configuration" |
| Card Heading (h3) | 20px (1.25rem) | Bold (700) | "Overall Progress" |
| Subheading | 18px (1.125rem) | Semibold (600) | "Inputs" |
| Body | 16px (1rem) | Regular (400) | Paragraph text |
| Small | 14px (0.875rem) | Regular (400) | Helper text |
| Extra Small | 12px (0.75rem) | Regular (400) | Dates, badges |

### Spacing

#### Consistent Spacing Scale
```
4px   (0.25rem)  - Minimal gaps
6px   (0.375rem) - Small gaps between elements
8px   (0.5rem)   - Standard gap between elements
12px  (0.75rem)  - Medium gaps
16px  (1rem)     - Card padding, section spacing
24px  (1.5rem)   - Major section spacing
32px  (2rem)     - Page section breaks
```

#### Applied Rules
- **Card Padding**: 24px (1.5rem) or 32px (2rem)
- **Between Cards**: 24px (1.5rem) gap
- **Button Padding**: 12px (0.75rem) vertical, 16px (1rem) horizontal
- **Input Padding**: 12px (0.75rem)

### Borders & Shadows

#### Border Radius
- Small components: 8px (rounded-lg)
- Cards: 12px (rounded-xl)
- Large containers: 16px (rounded-2xl)

#### Shadows
| Type | Usage | CSS |
|------|-------|-----|
| Shadow SM | Light elevation | 0 1px 2px rgb(0 0 0 / 5%) |
| Shadow MD | Standard cards | 0 4px 6px rgb(0 0 0 / 10%) |
| Shadow LG | Hover states | 0 10px 15px rgb(0 0 0 / 10%) |

#### Borders
- **Default**: 1px solid slate-200
- **Focus**: 2px solid blue-500
- **Active**: 2px solid blue-500
- **Error**: 1px solid red-200

## Component Patterns

### Buttons

#### Primary Button (CTA)
```
Background: Gradient (Blue 600 → Indigo 600)
Text: White
Padding: 12px vertical, 24px horizontal
Hover: Darker gradient
Icon spacing: 8px gap
```

#### Secondary Button
```
Background: Slate 50 / White with border
Text: Slate 700
Padding: 12px vertical, 24px horizontal
Border: 1px slate-300
Hover: Slate 100 background
```

#### Icon Button
```
Background: Color 50 or Color 100
Text: Color 600
Padding: 8px
Hover: Color 200 background
```

### Input Fields

#### Text Input / Textarea
```
Border: 1px slate-300
Background: White
Focus: Ring 2px blue-200
Border color on focus: Blue 500
Padding: 12px horizontal, 10px vertical
```

#### Dropdown / Select
```
Border: 1px slate-300
Background: White
Focus: Ring 2px blue-200
Padding: 12px horizontal, 10px vertical
```

### Cards

#### Standard Card
```
Background: White
Border: 1px slate-200
Border radius: 12px (rounded-xl)
Padding: 24px (1.5rem)
Shadow: 0 1px 2px (shadow-sm)
Hover shadow: 0 4px 6px (shadow-md)
```

#### Colored Background Card
```
Background: Color 50 (light tint)
Border: 1px Color 200
Text: Color 900
```

Examples:
- Blue info card: bg-blue-50, border-blue-200, text-blue-900
- Green success: bg-green-50, border-green-200, text-green-800
- Red error: bg-red-50, border-red-200, text-red-700

### Progress Bar

#### Design
- Background: Slate 200
- Fill: Gradient (Blue → Indigo)
- Height: 16px (h-4)
- Border radius: 9999px (rounded-full)

```html
<div className="w-full bg-slate-200 rounded-full h-4 overflow-hidden">
  <div 
    className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full rounded-full"
    style={{ width: `${progress}%` }}
  />
</div>
```

### Badges & Status Indicators

#### Status Badge
```
Padding: 4px horizontal, 1px vertical (text-xs)
Border radius: 9999px (rounded-full)
Font weight: Semibold (600)
```

Status colors:
- Active: Green 100 bg, Green 800 text
- Draft: Amber 100 bg, Amber 800 text
- Archived: Slate 100 bg, Slate 800 text

### Forms

#### Form Section
```
Spacing between sections: 16px (gap-4)
Label: Text sm, Font semibold, Margin bottom 8px
Input: Full width
```

#### File Upload Area
```
Border: 2px dashed blue-300
Background: Blue 50
Padding: 24px (1.5rem)
Border radius: 12px (rounded-lg)
Hover: Border-blue-500, bg-blue-100
```

## Layout Patterns

### Container Width
- Standard: max-w-7xl (1280px)
- Full: No max-width constraint
- Narrow: max-w-3xl (768px)

### Responsive Grid
```
Mobile (1 column):    grid-cols-1
Tablet (2 columns):   md:grid-cols-2
Desktop (3 columns):  lg:grid-cols-3
Gap: gap-6 (24px)
```

### Sticky Header
```
position: sticky
top: 0
z-index: 40
Background: white
Border-bottom: 1px slate-200
Padding: 16px vertical, 24px horizontal
Box shadow: Light shadow
```

### Page Layout Structure
```
┌─ Header (Sticky) ────────────────────┐
│ Breadcrumbs / Title / Actions        │
├──────────────────────────────────────┤
│                                      │
│ Content Area                         │
│ - Max width container                │
│ - Padding: 32px (2rem)               │
│ - Background: Gradient slate         │
│                                      │
└──────────────────────────────────────┘
```

## Animation & Transitions

### Standard Transitions
```css
transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Hover Effects
- Button scale: slight increase in shadow, color darken
- Card: increase in shadow
- Link: color change

### Loading States
- Spinner: Animation spin (1s linear infinite)
- Progress: Smooth width transition (300ms)
- Pulsing: Animation pulse (2s cubic-bezier)

### Micro-interactions
- Successful action: Brief green flash
- Error state: Shake or red flash
- File upload: Progress indication
- Form submission: Button disabled state, loading text

## Accessibility

### Color Contrast
- WCAG AA compliance (4.5:1 for normal text)
- WCAG AAA compliance (7:1 recommended for headers)
- Never use color alone for information

### Focus States
```css
All interactive elements have:
- Visible focus ring (2px blue-500)
- Minimum 44x44px touch target
- Clear focus indicators
```

### Text Sizing
- Minimum 16px for body text
- Clear hierarchy with heading sizes
- Readable line length (50-75 chars)

## Code Examples

### Button Patterns

**Primary Button:**
```tsx
<button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition shadow-lg">
  Primary Action
</button>
```

**Secondary Button:**
```tsx
<button className="border border-slate-300 text-slate-700 px-6 py-3 rounded-lg font-semibold hover:bg-slate-50 transition">
  Secondary Action
</button>
```

### Card Pattern:
```tsx
<div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
  <h3 className="text-lg font-bold text-slate-900 mb-4">Card Title</h3>
  <p className="text-slate-600">Card content</p>
</div>
```

### Input Pattern:
```tsx
<input 
  type="text"
  placeholder="Enter text..."
  className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
/>
```

## Brand Voice & Tone

- **Friendly**: Conversational language, not technical jargon
- **Clear**: Direct actions, specific instructions
- **Professional**: Polished design, consistent styling
- **Helpful**: Guidance at each step, clear success/error states

## Design Principles

1. **Consistency**: Same patterns throughout the app
2. **Clarity**: Clear visual hierarchy and action buttons
3. **Efficiency**: Minimal clicks to complete tasks
4. **Feedback**: Immediate response to user actions
5. **Aesthetics**: Modern, clean, professional appearance
6. **Accessibility**: Inclusive design for all users
