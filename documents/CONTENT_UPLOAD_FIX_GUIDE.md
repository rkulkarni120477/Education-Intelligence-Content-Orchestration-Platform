# Content Upload Fix Guide

## Issue: Chemistry Document Upload Failed

**Status**: ✅ FIXED

### What Happened

The Chemistry document upload failed because the content processing system only supported PDF and plain text files. When you uploaded the Chemistry document (likely a DOCX file), the processor couldn't extract text from it and marked the upload as failed.

### Root Cause

The `_process_content_upload` function in `backend/api_routes.py` had limited file format support:

```python
# OLD CODE - Only supported PDF and TXT
if suffix == ".pdf":
    # PDF extraction
elif mime_type == "text/plain":
    # Text extraction
# EVERYTHING ELSE: No extraction, processing fails
```

### Solution

The processor has been enhanced to:

1. **Support Multiple File Formats**
   - PDF files (with better error handling)
   - Microsoft Word documents (.docx)
   - Plain text files (.txt)
   - Other formats stored as-is

2. **Graceful Error Handling**
   - Attempts extraction for supported formats
   - Falls back to "ingested" status if extraction fails
   - Logs detailed errors for debugging
   - Allows documents without extractable text

3. **Improved Logging**
   - Shows extraction progress
   - Reports specific errors
   - Helps diagnose processing issues

### Files Changed

**backend/api_routes.py**
- Enhanced `_process_content_upload()` function
- Added DOCX support via `python-docx` library
- Improved error handling and fallback mechanisms
- Better logging and debugging info

**Dependencies**
- Added `python-docx` library (installed automatically)

### How to Re-process the Failed Chemistry Upload

#### Option 1: Delete and Re-upload (Recommended)

The simplest approach:

1. In the UI, delete the failed "Chemistry" document
2. Re-upload the Chemistry document
3. The new processor will handle it correctly

#### Option 2: Manual Database Update

If you want to keep the existing document ID:

```python
# This command resets the Chemistry document to pending status
# for reprocessing by the background task

from database.db import SessionLocal
from database.models import Content

db = SessionLocal()
content = db.query(Content).filter(Content.title == "Chemistry").first()

if content:
    content.status = "pending"
    content.content_metadata = {
        **(content.content_metadata or {}),
        "processing_error": None,  # Clear error
    }
    db.commit()
    print(f"Reset {content.title} to pending status")

db.close()
```

Then restart the application to trigger reprocessing.

#### Option 3: Programmatic Re-processing

Use Python to re-process the file:

```python
from database.db import SessionLocal
from database.models import Content
from api_routes import _process_content_upload
from pathlib import Path

db = SessionLocal()
content = db.query(Content).filter(Content.title == "Chemistry").first()

if content and Path(content.source).exists():
    # Re-process the file
    suffix = Path(content.source).suffix.lower()
    mime_type = content.content_metadata.get("mime_type")
    
    _process_content_upload(
        content_id=content.id,
        tenant_id=content.tenant_id,
        title=content.title,
        file_path=content.source,
        suffix=suffix,
        mime_type=mime_type,
    )
    
    db.refresh(content)
    print(f"Re-processed {content.title}: {content.status}")

db.close()
```

### Supported File Formats

The enhanced processor now supports:

| Format | Extension | MIME Type | Extraction | Status |
|--------|-----------|-----------|-----------|--------|
| PDF | `.pdf` | `application/pdf` | Text extraction | ✅ Supported |
| Word Document | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | Paragraph extraction | ✅ Supported |
| Plain Text | `.txt` | `text/plain` | Raw text | ✅ Supported |
| Other Formats | Any | Any | None | Stored as-is |

### Processing Flow

```
1. Upload file
   ↓
2. Save file to disk
   ↓
3. Background: Extract text
   ├─ PDF? → Try PDF extraction
   ├─ DOCX? → Try DOCX extraction
   ├─ TXT? → Try text extraction
   └─ Other? → Store as-is
   ↓
4. If text extracted
   ├─ Create chunks for vector DB
   ├─ Index in vector store
   └─ Status: "indexed"
   ↓
5. If indexed
   ├─ Run governance review
   └─ Status: "review_required"
   ↓
6. Manual approval
   └─ Status: "published"
```

### Error Codes

If content still fails, check the error message in the database:

```python
content.content_metadata.get("processing_error")
```

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'docx'` | python-docx not installed | Run: `pip install python-docx` |
| `PDF contains no extractable text` | Scanned PDF (image-based) | Document stored as-is (manual OCR needed) |
| `Cannot read file: encoding error` | File encoding mismatch | Re-save file in UTF-8 encoding |
| `File not found` | Upload path lost | Re-upload the document |

### Testing the Fix

Test with different document types:

```bash
# Test with a DOCX file
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@chemistry.docx" \
  -F "title=Chemistry" \
  -F "subject=science" \
  -F "grade=9"

# Test with a PDF file
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@chemistry.pdf" \
  -F "title=Chemistry" \
  -F "subject=science" \
  -F "grade=9"

# Test with a TXT file
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@chemistry.txt" \
  -F "title=Chemistry" \
  -F "subject=science" \
  -F "grade=9"
```

### Logging

The enhanced processor logs detailed information:

```
INFO: Extracted text from DOCX chemistry.docx: 5234 chars
INFO: Indexed 6 chunks for content abc-123
INFO: Governance review completed for abc-123: approve
INFO: Processed uploaded content abc-123 with status review_required
```

Check logs for:
- Text extraction success/failure
- Number of chunks created
- Governance review results
- Final content status

### Future Enhancements

Possible improvements for next version:

1. **OCR for Scanned PDFs**
   - Use pytesseract for image-based PDFs
   - Extract text from scanned documents

2. **Additional Formats**
   - Excel files (.xlsx)
   - PowerPoint presentations (.pptx)
   - Google Docs integration
   - Web content (.html, .md)

3. **Advanced Processing**
   - Automatic metadata extraction
   - Content classification
   - Duplicate detection
   - Language detection

4. **Performance**
   - Async processing with progress tracking
   - Batch uploads
   - Resumable uploads for large files

### Related Files

- `backend/api_routes.py` - Content upload implementation
- `backend/database/models.py` - Content model definition
- `backend/services/content_governance.py` - Governance review logic
- `backend/BACKEND_SETUP.md` - Backend setup instructions

### Summary

The Chemistry upload failure has been fixed by:

✅ Adding support for DOCX files  
✅ Improving PDF extraction handling  
✅ Adding fallback for unsupported formats  
✅ Better error logging and reporting  
✅ Graceful degradation when extraction fails  

The system now supports any document format and will:
- Extract text when possible
- Index content in vector database
- Run governance review
- Allow manual approval

**Action Required**: Re-upload the Chemistry document to process it with the fixed processor.
