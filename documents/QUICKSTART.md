# Quick Start Guide

## 🚀 Getting Started

### Installation

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Set environment variables:**
Create a `.env.local` file in the frontend directory:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Application

**Development mode:**
```bash
npm run dev
```

Application will be available at `http://localhost:3000`

**Production build:**
```bash
npm run build
npm start
```

---

## 📊 User Quick Start

### Creating Your First Project

1. **Open Application**
   - Navigate to `http://localhost:3000`
   - You'll see the Projects Dashboard

2. **Create New Project**
   - Click "+ New Project" button in top right
   - Enter project name and description
   - Click "Create & Configure"

3. **Configure Workflow**
   - Select a workflow action from the left menu
   - Review inputs, outputs, and workflow information
   - Upload required files
   - Click "Proceed to Monitor"

4. **Monitor Workflow**
   - Watch real-time progress updates
   - See which agents are working
   - View requirements understanding
   - Wait for completion

### Available Workflow Actions

| Action | Description | Duration |
|--------|-------------|----------|
| BSIT Cybersecurity Concentration | Curriculum alignment with workforce skills | 30-60 min |
| Content Generation | Create courses from blueprints | 20-40 min |
| Skills Extraction | Build skills taxonomy from job data | 15-30 min |
| Standards Ingestion | Align content with standards | 20-45 min |
| Accessibility Audit | WCAG compliance checking | 15-30 min |
| Knowledge Intelligence | Index and retrieve content | 10-25 min |

---

## 🎨 Developer Quick Start

### Understanding the Structure

```
frontend/
├── app/                          # Next.js app directory
│   ├── page.tsx                  # Home/Dashboard
│   ├── layout.tsx                # Root layout
│   ├── globals.css               # Global styles
│   └── projects/[projectId]/
│       ├── configure/page.tsx    # Configuration page
│       └── workflow/[workflowId]/page.tsx  # Monitor page
│
├── components/                   # React components
│   ├── ProjectsDashboardNew.tsx  # Main dashboard
│   ├── ProjectConfiguration.tsx   # Configuration UI
│   └── WorkflowProgressMonitor.tsx # Progress tracking
│
├── context/                      # React Context (if needed)
├── utils/                        # Utility functions
│
└── Documentation files:
    ├── UI_ARCHITECTURE.md        # System overview
    ├── DESIGN_GUIDELINES.md      # Design specifications
    ├── VISUAL_FLOWS.md           # Page layouts
    └── QUICKSTART.md             # This file
```

### Adding a New Component

1. **Create component file** in `components/`:
```tsx
'use client'

import { useState } from 'react'

interface Props {
  title: string
}

export default function MyComponent({ title }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h2 className="text-xl font-bold text-slate-900">{title}</h2>
    </div>
  )
}
```

2. **Use in pages** with proper imports:
```tsx
import MyComponent from '@/components/MyComponent'

export default function Page() {
  return <MyComponent title="My Title" />
}
```

### Styling Convention

Follow Tailwind CSS utility classes:

```tsx
// ✅ Good - Use Tailwind utilities
<button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
  Click me
</button>

// ❌ Avoid - Custom CSS
<button style={{ background: 'blue', color: 'white' }}>
  Click me
</button>
```

### Common Patterns

**Card Component:**
```tsx
<div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
  {content}
</div>
```

**Button Primary:**
```tsx
<button className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700">
  Action
</button>
```

**Button Secondary:**
```tsx
<button className="border border-slate-300 text-slate-700 px-6 py-3 rounded-lg hover:bg-slate-50">
  Cancel
</button>
```

**Input Field:**
```tsx
<input
  type="text"
  className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
  placeholder="Enter text..."
/>
```

### Making API Calls

Use Axios for API requests:

```tsx
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Fetch data
const response = await axios.get(`${API_URL}/api/projects`)

// Post data
const response = await axios.post(`${API_URL}/api/projects`, {
  name: 'Project Name',
  description: 'Description'
})

// Handle errors
try {
  const response = await axios.get(url)
  setData(response.data)
} catch (err: any) {
  setError(err.response?.data?.detail || 'Error occurred')
}
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change default port
npm run dev -- -p 3001
```

### API Connection Failed
- Ensure backend is running on configured URL
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify CORS is enabled on backend

### Styling Not Applied
- Run `npm run dev` again to rebuild
- Clear `.next` folder: `rm -rf .next`
- Restart development server

### Build Errors
```bash
# Clear and rebuild
rm -rf .next node_modules
npm install
npm run build
```

---

## 📱 Testing

### Manual Testing Checklist

- [ ] Dashboard loads without auth
- [ ] Create project works
- [ ] Configuration shows all actions
- [ ] File upload works
- [ ] Progress monitor updates
- [ ] Mobile layout responsive
- [ ] Error states display correctly
- [ ] Navigation works seamlessly

### Running Tests

```bash
# Run unit tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

---

## 🔧 Environment Setup

### Required Backend Endpoints

```
GET    /api/projects                    - List projects
POST   /api/projects                    - Create project
DELETE /api/projects/{id}               - Delete project

POST   /api/projects/{id}/workflow      - Start workflow
GET    /api/projects/{id}/workflow/{wfId}/status - Get status
```

### Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: For analytics, monitoring, etc.
NEXT_PUBLIC_APP_NAME=Academian
NEXT_PUBLIC_VERSION=1.0.0
```

---

## 📚 Documentation Reference

| Document | Purpose | Audience |
|----------|---------|----------|
| UI_ARCHITECTURE.md | System overview | Developers |
| DESIGN_GUIDELINES.md | Design system specs | Designers, Developers |
| VISUAL_FLOWS.md | Page layouts | All users |
| QUICKSTART.md | Getting started | New users/developers |
| UI_REDESIGN_SUMMARY.md | Changes made | Project managers |

---

## 🎯 Next Steps

1. **Run the application:**
```bash
npm run dev
```

2. **Test the user flow:**
   - Create a project
   - Configure a workflow
   - Monitor progress

3. **Review documentation:**
   - Read `DESIGN_GUIDELINES.md` for styling
   - Check `UI_ARCHITECTURE.md` for architecture
   - See `VISUAL_FLOWS.md` for layouts

4. **Connect backend:**
   - Ensure all API endpoints are available
   - Test with sample data
   - Verify real-time updates

5. **Deploy:**
   - Build production version: `npm run build`
   - Deploy to hosting platform
   - Monitor in production

---

## 💡 Tips & Best Practices

### Code Style
- Use TypeScript for type safety
- Follow ESLint rules
- Keep components small and focused
- Use meaningful variable names

### Performance
- Lazy load images
- Code split large components
- Optimize bundle size
- Monitor Core Web Vitals

### Accessibility
- Use semantic HTML
- Include alt text for images
- Ensure proper color contrast
- Provide keyboard navigation

### User Experience
- Show loading states
- Provide clear error messages
- Confirm destructive actions
- Remember user preferences

---

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request
5. Get code review
6. Merge and deploy

---

## 📞 Support

For questions or issues:
1. Check the documentation files
2. Review existing issues
3. Contact the development team
4. Check application logs

---

## Version Information

- **React:** 18.2.0
- **Next.js:** 14.0.0
- **Tailwind CSS:** 3.3.0
- **TypeScript:** 5.2.0
- **Axios:** 1.6.0

---

Last updated: 2026-09-22
