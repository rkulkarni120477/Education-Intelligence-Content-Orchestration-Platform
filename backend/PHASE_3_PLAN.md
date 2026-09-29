# Phase 3: LLM Integration & Streaming - Implementation Plan

**Goal**: Enable real-time AI-powered message streaming with file context awareness.

---

## Architecture Overview

```
User Message (with files)
   ↓
ChatPanel → sendMessage(prompt, [fileIds])
   ↓
Backend POST /conversations/{id}/messages
   ↓
LLM Service:
  1. Load file contents from database
  2. Prepare context with files
  3. Call AWS Bedrock (Claude Haiku)
  4. Stream response via SSE
   ↓
SSE Response Stream
   ↓
ChatPanel receives chunks
   ↓
Append to assistant message in real-time
   ↓
Store final message in database
```

---

## Phase 3 Components

### 1. Backend LLM Service
**File**: `backend/services/llm_service.py`

```python
class LLMService:
    @staticmethod
    async def stream_message(
        prompt: str,
        file_ids: List[str],
        conversation_history: List[Message],
        tenant_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response with file context."""
        
        # 1. Load file contents
        # 2. Build system prompt with context
        # 3. Stream from Bedrock
        # 4. Yield chunks
```

### 2. Backend Message Endpoint
**File**: `backend/api/custom_content.py` (update)

```python
@router.post("/conversations/{id}/messages/stream")
async def stream_message(
    id: str,
    request: SendMessageRequest,
    tenant_id: str = Depends(get_current_tenant_id)
) -> StreamingResponse:
    """Stream LLM response via SSE."""
```

### 3. Frontend Streaming Hook
**File**: `frontend/lib/hooks/useMessageStream.ts`

```typescript
export const useMessageStream = (conversationId: string) => {
  const sendMessageStream = async (
    prompt: string,
    fileIds: string[]
  ): Promise<void> => {
    // 1. Open SSE connection
    // 2. Listen for message chunks
    // 3. Update UI in real-time
    // 4. Save message when complete
  }
}
```

### 4. Frontend SSE Handler Component
**File**: `frontend/components/CustomContentDevelopment/StreamingMessage.tsx`

```typescript
export const StreamingMessage: React.FC<{
  isStreaming: boolean
  content: string
}> = ({ isStreaming, content }) => {
  // Display message with streaming indicator
  // Show live updates as content arrives
}
```

---

## Implementation Steps

### Step 1: AWS Bedrock Setup
- [ ] Add AWS credentials to `.env`
- [ ] Test Bedrock connection
- [ ] Verify Claude Haiku model access

### Step 2: LLM Service
- [ ] Create `backend/services/llm_service.py`
- [ ] Implement file context loading
- [ ] Implement prompt building
- [ ] Implement Bedrock streaming
- [ ] Add error handling and retries

### Step 3: Backend Streaming Endpoint
- [ ] Update `POST /conversations/{id}/messages`
- [ ] Return `StreamingResponse` with SSE
- [ ] Send message chunks with type/content
- [ ] Handle errors during streaming
- [ ] Save final message to database

### Step 4: Frontend Streaming Hook
- [ ] Create `useMessageStream.ts` hook
- [ ] Implement EventSource for SSE
- [ ] Handle connection lifecycle
- [ ] Parse SSE event stream
- [ ] Update store with received messages

### Step 5: Frontend UI Updates
- [ ] Update `ChatPanel` to use streaming hook
- [ ] Create streaming message component
- [ ] Show typing indicator during streaming
- [ ] Display content as it arrives
- [ ] Handle stream errors gracefully

### Step 6: Integration Testing
- [ ] Test simple message (no files)
- [ ] Test message with one file
- [ ] Test message with multiple files
- [ ] Test stream interruption
- [ ] Test error recovery

---

## Key Features

### Message Streaming
- Real-time updates as AI generates content
- Visual typing indicator
- Can interrupt mid-stream
- Auto-save when complete

### File Context
- Automatically include uploaded file contents
- Build system prompt with file metadata
- Handle different file types
- Truncate large files if needed

### Error Handling
- Network timeout recovery
- Invalid file handling
- Bedrock API errors
- Graceful degradation

### Performance
- Stream large responses (don't wait for completion)
- Minimal memory footprint
- Auto-cleanup of connections
- No blocking operations

---

## Configuration

### Environment Variables
```bash
# .env (add these)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0

# Optional
LLM_STREAM_CHUNK_SIZE=100
LLM_RESPONSE_TIMEOUT=300
LLM_MAX_FILE_CONTEXT_SIZE=1000000
```

### System Prompt Template
```
You are a helpful AI assistant for content creation.
You have access to the following files:

{FILE_LISTING}

Use the file contents below to inform your responses:

{FILE_CONTENTS}

---

User: {USER_MESSAGE}
```

---

## Database Changes

None required - use existing `custom_content_messages` table.

**Message Schema**:
```python
{
  "id": "uuid",
  "conversation_id": "uuid",
  "role": "user" | "assistant",
  "content": "string (can be partial during streaming)",
  "message_type": "text" | "status_update",
  "metadata": {
    "file_ids": ["id1", "id2"],
    "tokens": {
      "input": 234,
      "output": 456
    },
    "model": "anthropic.claude-3-haiku-...",
    "created_at": "2026-09-29T..."
  },
  "created_at": "2026-09-29T...",
  "updated_at": "2026-09-29T..."
}
```

---

## Testing Plan

### Unit Tests
```python
# test_llm_service.py
- test_load_file_context()
- test_build_system_prompt()
- test_bedrock_connection()
- test_stream_response()
- test_error_handling()
```

### Integration Tests
```typescript
// useMessageStream.test.ts
- test_send_simple_message()
- test_send_with_files()
- test_stream_interruption()
- test_error_recovery()
```

### Manual Testing
1. Open dev tools (Network tab)
2. Send message with file
3. Watch SSE events in real-time
4. Verify message saves
5. Check message history

---

## Success Criteria

✅ Message streaming works (no complete wait)  
✅ File context included in prompts  
✅ Real-time UI updates  
✅ Error handling robust  
✅ No memory leaks  
✅ Message history persists  
✅ Can send multiple messages in sequence  
✅ Can interrupt streaming  

---

## Timeline

| Task | Est. Time |
|------|-----------|
| AWS Setup + LLM Service | 3-4 hours |
| Streaming Endpoint | 2-3 hours |
| Frontend Hook | 2-3 hours |
| UI Components | 2-3 hours |
| Testing | 2-3 hours |
| Polish & Docs | 1-2 hours |
| **Total** | **12-18 hours** |

**Estimated Completion**: 1-2 weeks

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Bedrock API rate limits | Implement backoff + queue |
| Large file context | Truncate/summarize large files |
| Network interruption | Reconnect with retry logic |
| Concurrent streams | Queue messages, process sequentially |
| Memory leaks from SSE | Proper cleanup on unmount |

---

## Ready to Start

All prerequisites from Phase 2 are complete. Phase 3 can begin immediately.

**Next Action**: Implement `backend/services/llm_service.py`
