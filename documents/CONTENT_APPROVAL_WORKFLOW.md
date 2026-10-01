# Content Approval & Publishing Workflow

## Overview

Content goes through a **multi-stage approval process** from upload to publication. This ensures quality control and governance compliance before content is made available to users.

---

## Content Status Lifecycle

```
UPLOAD
  ↓
PENDING (file saved)
  ↓
PROCESSING (background task)
  ├─ Extract text
  ├─ Index in vector DB
  └─ Run governance review
  ↓
INGESTED (no text extracted)
  ↓
INDEXED (text extracted & indexed)
  ├─ Auto-run governance review
  ↓
REVIEW_REQUIRED (governance review complete)
  ├─ Awaits human approval
  │
  ├─→ APPROVED → PUBLISHED (available to users)
  │
  └─→ REJECTED (content deleted)
  
FAILED (processing error)
  └─ Retry or delete
```

---

## Status Definitions

| Status | Meaning | Auto? | Manual? | Next Step |
|--------|---------|-------|---------|-----------|
| `pending` | File uploaded, waiting to process | ❌ | ❌ | Wait for background job |
| `ingested` | Processed, no text extracted | ✅ | ❌ | Manual re-upload if needed |
| `indexed` | Text extracted and indexed in vector DB | ✅ | ❌ | Auto-run governance review |
| `review_required` | Governance checks complete, awaiting approval | ✅ | ✅ | Approve or Reject |
| `published` | Approved and available to users | ❌ | ✅ | Content is live |
| `failed` | Processing error occurred | ❌ | ❌ | Manual troubleshooting |

---

## Who Makes Changes?

### Automatic Transitions (Handled by System)

1. **PENDING → INGESTED/INDEXED**
   - Background task runs automatically after upload
   - Text extraction and vector indexing
   - Takes 5-30 seconds depending on file size

2. **INDEXED → REVIEW_REQUIRED**
   - Governance review runs automatically
   - Checks: file exists, has text, has title, has subject, has grade
   - Recommendations: "approve" or "review"

### Manual Transitions (Requires User Action)

3. **REVIEW_REQUIRED → PUBLISHED**
   - **Who**: Admin/Editor with approval permission
   - **How**: Call `/v1/content/{content_id}/approve` endpoint
   - **Notes**: Optional approval notes can be added

4. **REVIEW_REQUIRED → REJECTED**
   - **Who**: Admin/Editor with rejection permission
   - **How**: Call `/v1/content/{content_id}/reject` endpoint
   - **Effect**: Content deleted from storage and vector DB
   - **Requires**: Rejection reason

---

## API Endpoints

### 1. Upload Content

**Endpoint**: `POST /v1/content/upload`

```json
{
  "file": "<file>",
  "title": "Chemistry",
  "description": "Introduction to Chemistry",
  "subject": "science",
  "grade": "9",
  "tags": "chemistry,elements,periodic-table"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Content uploaded and queued for processing",
  "job": {
    "id": "job-uuid",
    "content_id": "content-uuid",
    "status": "queued",
    "progress": 0,
    "stage": "queued",
    "title": "Chemistry"
  }
}
```

**Automatically**: Content status becomes "pending" → processing starts

---

### 2. Get Content Status

**Endpoint**: `GET /v1/content/{content_id}`

Returns current status, metadata, and governance results.

```json
{
  "id": "content-uuid",
  "title": "Chemistry",
  "status": "review_required",
  "content_metadata": {
    "description": "...",
    "subject": "science",
    "grade": "9",
    "governance": {
      "recommendation": "approve",
      "confidence": 1.0,
      "checks": {
        "source_file_exists": true,
        "has_extracted_text": true,
        "has_title": true,
        "has_subject": true,
        "has_grade": true
      }
    }
  }
}
```

---

### 3. Approve Content

**Endpoint**: `POST /v1/content/{content_id}/approve`

**Request**:
```json
{
  "notes": "Approved. High-quality chemistry resource."
}
```

**Response**:
```json
{
  "id": "content-uuid",
  "title": "Chemistry",
  "status": "published",
  "version": 1
}
```

**Effect**:
- Content status: `review_required` → `published`
- Content becomes available to all users
- Approval metadata stored with timestamp

---

### 4. Reject Content

**Endpoint**: `POST /v1/content/{content_id}/reject`

**Request**:
```json
{
  "reason": "Content does not meet academic standards",
  "notes": "Please provide peer-reviewed sources"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Content rejected and deleted",
  "content_id": "content-uuid"
}
```

**Effect**:
- Removes file from storage
- Deletes vectors from database
- Deletes content record from database
- Cannot be recovered

---

### 5. Run Governance Review

**Endpoint**: `POST /v1/content/{content_id}/governance-review`

Manually trigger governance review (usually automatic).

**Response**:
```json
{
  "status": "success",
  "content_id": "content-uuid",
  "content_status": "review_required",
  "governance": {
    "agent": "Content Governance Agent",
    "recommendation": "approve",
    "confidence": 1.0,
    "checks": {...},
    "reason": "All automated governance checks passed..."
  }
}
```

---

## Governance Review Checks

The system automatically checks:

✅ **source_file_exists** - File is on disk  
✅ **has_extracted_text** - Text was successfully extracted  
✅ **has_title** - Content has a title  
✅ **has_subject** - Content has a subject category  
✅ **has_grade** - Content has a grade level  

**Recommendation Logic**:
- ✅ All 5 checks pass → **"approve"** (confidence: 1.0)
- ⚠️ 1+ checks fail → **"review"** (confidence: < 1.0)

**What This Means**:
- "approve" = automation is confident, ready for human approval
- "review" = automation flagged issues, review carefully before approving

---

## Complete Workflow Examples

### Scenario 1: Standard Approval Flow

```
1. User uploads Chemistry.docx
   Status: pending

2. Background job processes file (5 sec)
   ✓ Extracts text (5,234 chars)
   ✓ Creates 6 chunks
   ✓ Indexes in vector DB
   Status: indexed

3. Auto-run governance review
   ✓ All 5 checks pass
   Recommendation: "approve" (100% confidence)
   Status: review_required

4. Admin reviews in UI
   Sees: "All governance checks passed"
   Decision: Approve

5. Admin calls: POST /v1/content/{id}/approve
   With notes: "High quality resource, approved for 9th grade"
   Status: published
   
6. Content available to all students and teachers
```

### Scenario 2: Rejection Flow

```
1. User uploads LowQuality.txt
   Status: pending

2. Background job processes file (2 sec)
   ✓ Extracts text (523 chars)
   ✓ Creates 1 chunk
   ✓ Indexes in vector DB
   Status: indexed

3. Auto-run governance review
   ✓ 4 of 5 checks pass
   ✗ Content too short (< 1000 chars)
   Recommendation: "review" (80% confidence)
   Status: review_required

4. Admin reviews in UI
   Sees: "Content is very brief"
   Decision: Reject as insufficient content

5. Admin calls: POST /v1/content/{id}/reject
   With reason: "Content is too brief for this grade level"
   
6. System:
   - Deletes file from storage
   - Removes vectors from database
   - Deletes content record
   - Cannot be recovered
```

### Scenario 3: Processing Error

```
1. User uploads Corrupted.pdf
   Status: pending

2. Background job attempts processing
   ✗ PDF is corrupted/malformed
   Error: "Cannot read PDF header"
   Status: failed
   Error stored in metadata

3. User sees: "Processing Error - Please review and try again"

4. Options:
   a) Re-upload the file (fix corruption)
   b) Upload different format (DOCX instead)
   c) Delete and try again
```

---

## User Roles & Permissions

| Role | Upload | Approve | Reject | Delete |
|------|--------|---------|--------|--------|
| Viewer | ❌ | ❌ | ❌ | ❌ |
| Editor | ✅ | ⚠️ Own content only | ⚠️ Own only | ⚠️ Own only |
| Admin | ✅ | ✅ All | ✅ All | ✅ All |
| Content Manager | ✅ | ✅ All | ✅ All | ❌ |

---

## Timeline Examples

### Fast Path (Well-formatted document)
```
Upload → Pending (0 sec)
       → Indexed (5 sec) [text extraction + indexing]
       → Review Required (6 sec) [governance review]
       → Published (N sec) [manual approval by admin]
       
Total automatic: ~6 seconds
Total with approval: ~30 seconds (depends on admin availability)
```

### Slow Path (Large document or complex governance)
```
Upload → Pending (0 sec)
       → Indexed (30 sec) [large file, more text to process]
       → Review Required (32 sec) [governance check]
       → Awaiting Approval... [pending human review]
       → Published (minutes/hours) [admin reviews and approves]
```

### Error Path (Corrupted file)
```
Upload → Pending (0 sec)
       → Failed (3 sec) [extraction error]
       → User sees error message
       → User re-uploads fixed file or different format
```

---

## Monitoring & Checking Status

### In the UI
- Dashboard shows content with status badges
- Filter by: pending, ingested, indexed, review_required, published, failed
- Clicking content shows full details including governance results

### Via API

```python
from database.db import SessionLocal
from database.models import Content

db = SessionLocal()

# Get all content in review_required status
pending_approval = db.query(Content).filter(
    Content.status == "review_required"
).all()

for content in pending_approval:
    print(f"Title: {content.title}")
    print(f"Status: {content.status}")
    governance = content.content_metadata.get("governance", {})
    print(f"Recommendation: {governance.get('recommendation')}")
    print(f"Confidence: {governance.get('confidence')}")
    print()

db.close()
```

### Via Database Query

```sql
-- Content awaiting approval
SELECT id, title, created_at, content_metadata
FROM content
WHERE status = 'review_required'
ORDER BY created_at DESC;

-- All published content
SELECT id, title, status, created_at
FROM content
WHERE status = 'published'
ORDER BY created_at DESC;

-- Failed uploads (need fixing)
SELECT id, title, content_metadata
FROM content
WHERE status = 'failed'
ORDER BY created_at DESC;
```

---

## Key Points

✅ **Automatic Processing**: Upload → Indexed → Review Required (no manual action needed)

✅ **Manual Approval**: Only the REVIEW_REQUIRED → PUBLISHED step requires human action

✅ **Two Decisions**: Approve (publish) or Reject (delete)

✅ **Governance Check**: Automated quality checks with recommendation

✅ **Audit Trail**: Approval/rejection decisions stored with timestamps

✅ **No Partial Publish**: Content is either fully published or not at all

✅ **Admin Control**: Only admins can approve/reject; editors can only upload

---

## Summary Table

| Step | Automatic? | Who? | Time | Reversible? |
|------|-----------|------|------|------------|
| Upload | Manual | User | Now | ✅ Delete |
| Extract & Index | Auto | System | 5-30s | ✅ Delete |
| Governance Review | Auto | System | 1s | ✅ Re-run |
| Approve | Manual | Admin | N/A | ❌ Unpublish not available |
| Reject | Manual | Admin | N/A | ❌ Permanently deleted |

---

## Related Documentation

- `backend/api_routes.py` - Upload and approval endpoints
- `backend/services/content_governance.py` - Governance review logic
- `backend/database/models.py` - Content model schema
- `backend/CONTENT_UPLOAD_FIX_GUIDE.md` - Upload processing details
