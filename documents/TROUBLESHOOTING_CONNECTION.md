# Troubleshooting - Connection Issues

## Error: "Failed to load projects"

If you see the error message **"Unable to load projects"**, this means the frontend cannot connect to the backend API. Here's how to fix it.

---

## 🔍 Step 1: Check the API URL

### Verify Environment Variable
The frontend needs to know where your backend API is running.

**Check your `.env.local` file:**
```bash
cat .env.local
```

**You should see:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**If it's missing or incorrect:**
1. Create/edit `.env.local` in the frontend folder
2. Add: `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Replace `localhost:8000` with your actual backend URL if different
4. Save and restart the dev server: `npm run dev`

---

## 🚀 Step 2: Verify Backend is Running

### Check if Backend Server is Running
```bash
# Test if backend is accessible
curl http://localhost:8000/api/health

# Expected response: 200 OK or some response
# If you get "Connection refused": backend is not running
```

### Start the Backend
```bash
# Navigate to backend folder
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the backend
python main.py
# or
uvicorn main:app --reload
```

**Backend should be running on:** `http://localhost:8000`

---

## 🔌 Step 3: Check API Endpoints

### Verify the Projects Endpoint Exists
```bash
curl http://localhost:8000/api/projects
```

**Expected responses:**
- Success: `{"projects": []}` or `{"projects": [{...}]}`
- 401: `{"detail": "Not authenticated"}` (auth might be required)
- 404: Endpoint doesn't exist (check backend configuration)
- 500: Server error (check backend logs)

### Common Endpoint Paths
The backend might use different API paths. Check which one works:

```bash
# Try these variations:
curl http://localhost:8000/api/projects
curl http://localhost:8000/projects
curl http://localhost:8000/v1/projects
curl http://localhost:8000/api/v1/projects
```

---

## 🛠️ Step 4: Check CORS Issues

If you see a browser console error like **"CORS policy"**, the backend needs to allow requests from the frontend.

### Fix CORS in Backend
Add this to your backend (FastAPI example):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Or allow all origins (development only):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔐 Step 5: Check Authentication

If you get **"Authentication required"** error, the backend might require a token.

### Check Backend Auth Requirements
```bash
# Without auth
curl http://localhost:8000/api/projects

# With token (if required)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/projects
```

### Update Backend for No Auth (Development)
For development without authentication, modify your backend endpoints:

**FastAPI Example:**
```python
@app.get("/api/projects")
async def get_projects():  # No auth parameter needed
    return {"projects": []}
```

**Remove any auth requirements from the projects endpoint.**

---

## 🖥️ Step 6: Check Browser Console

Press **F12** to open browser DevTools and check the Console tab.

**Look for errors like:**
- `GET http://localhost:8000/api/projects 404` → Endpoint wrong
- `GET http://localhost:8000/api/projects 500` → Server error
- `CORS error` → Backend CORS not configured
- `Connection refused` → Backend not running

---

## 📋 Complete Checklist

- [ ] Backend is running (`http://localhost:8000`)
- [ ] `.env.local` has correct `NEXT_PUBLIC_API_URL`
- [ ] Frontend restarted after env change (`npm run dev`)
- [ ] API endpoint exists and returns data
- [ ] CORS is configured in backend
- [ ] Auth is not required (or token is passed)
- [ ] Network requests work in browser console

---

## ✅ Verify Everything Works

Once fixed, test with:

```bash
# 1. Backend running
curl http://localhost:8000/api/projects

# 2. Frontend running
npm run dev
# Open http://localhost:3000

# 3. Should see "No Projects Yet" message
```

---

## 🔧 Quick Fix Commands

### Reset Everything
```bash
# Terminal 1: Frontend
cd frontend
rm .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev

# Terminal 2: Backend
cd backend
python main.py
```

### Test API Connection
```bash
# Simple test
curl -v http://localhost:8000/api/projects

# Pretty JSON output (if jq installed)
curl http://localhost:8000/api/projects | jq

# With headers
curl -i http://localhost:8000/api/projects
```

---

## 📊 Backend API Requirements

The frontend expects these endpoints:

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/projects` | `{"projects": [...]}` |
| POST | `/api/projects` | `{"id": "...", "name": "...", ...}` |
| DELETE | `/api/projects/{id}` | Success or error |

Each project should have:
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "active|draft|archived",
  "created_at": "2026-09-22T...",
  "updated_at": "2026-09-22T...",
  "content_count": 0
}
```

---

## 🆘 Still Having Issues?

### Check Backend Logs
```bash
# Look for error messages in backend output
# Common issues:
# - ImportError: missing dependencies
# - DatabaseError: database not configured
# - ValidationError: endpoint validation failed
```

### Common Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
pip install fastapi uvicorn
```

**Issue:** Database connection error
```bash
# Check database is running and configured
# Update DATABASE_URL in backend config
```

**Issue:** Port already in use
```bash
# Use different port
python main.py --port 8001
# Then update NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## 🎯 Success Indicators

When working correctly, you should see:
- ✅ No error banner on page
- ✅ Either project list or "No Projects Yet" message
- ✅ Can create a new project
- ✅ Project appears in list
- ✅ Can delete project

---

## 💡 Development Tips

### Use Network Tab for Debugging
1. Open DevTools (F12)
2. Go to **Network** tab
3. Refresh page
4. Look for API requests
5. Click request to see:
   - Status code
   - Response body
   - Headers
   - Timing

### Mock Data (If Backend Not Ready)
If your backend is still being built, you can temporarily mock the data:

```tsx
// In ProjectsDashboardNew.tsx
const mockProjects = [
  {
    id: '1',
    name: 'Sample Project',
    description: 'Test project',
    status: 'active',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    content_count: 0
  }
]

// In fetchProjects():
// return setProjects(mockProjects)
```

---

## 📞 Need More Help?

1. Check the browser console (F12)
2. Check backend terminal output
3. Verify URLs match exactly
4. Test with `curl` command
5. Check network requests in DevTools
6. Review this troubleshooting guide

---

**Last Updated:** 2026-09-22
**Version:** 1.0.0
