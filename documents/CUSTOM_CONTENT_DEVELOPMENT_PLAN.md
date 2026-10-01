# Custom Content Development Module - Implementation Plan

## Executive Summary

This document outlines the architecture and implementation strategy for adding a "Custom Content Development" module to the Education Intelligence & Content Orchestration Platform. The module enables users to upload files, chat with an AI agent, and generate content using LLM + MCP integration.

---

## 1. Technology Stack Analysis

### Frontend Stack ✅
- **Framework**: Next.js 14 with TypeScript
- **Component Library**: Headless UI + custom components
- **State Management**: Zustand (lightweight, reactive)
- **HTTP Client**: Axios with custom ApiClient wrapper
- **Styling**: Tailwind CSS with design tokens (CSS custom properties)
- **Icons**: Heroicons from @heroicons/react
- **Routing**: Next.js App Router with route groups (authenticated)

### Backend Stack ✅
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: JWT tokens via X-Tenant-ID header
- **File Storage**: Local filesystem (`backend/data/uploads/`)
- **Vector DB**: Chroma for embeddings
- **LLM Provider**: AWS Bedrock (Claude models)
- **Background Tasks**: FastAPI BackgroundTasks (async)
- **Streaming**: Server-Sent Events (SSE) pattern (inferred from agent streaming)

### Design System ✅
- **Colors (Light Mode)**:
  - Primary: `#0f766e` (teal), Hover: `#115e59`
  - Text: `#1e293b` (dark gray)
  - Text Muted: `#64748b`
  - Background: `#f8fafc` (off-white)
  - Surface: `#ffffff`
  - Border: `#e2e8f0` (light gray)
- **Spacing**: 8px unit grid
- **Border Radius**: sm(6px), md(10px), lg(14px)
- **Typography**: System font stack, 15px base size

---

## 2. Proposed Architecture

### 2.1 Frontend Structure

```
frontend/
├── app/(authenticated)/
│   ├── custom-content-development/
│   │   └── page.tsx (main layout with 3-panel grid)
│   └── layout.tsx (add nav item here)
├── components/
│   └── CustomContentDevelopment/
│       ├── FileExplorer.tsx (tree view with folders)
│       ├── Editor.tsx (Monaco with tabs)
│       ├── ChatPanel.tsx (messages + composer)
│       ├── Composer.tsx (textarea + upload)
│       ├── FileUploadChip.tsx
│       ├── AgentStatusStep.tsx
│       ├── ResizablePanels.tsx (draggable dividers)
│       └── EditorTabs.tsx
├── lib/
│   ├── stores/
│   │   ├── custom-content.ts (Zustand: files, messages, UI state)
│   │   └── editor.ts (Zustand: open tabs, unsaved changes)
│   ├── api/
│   │   └── custom-content.ts (API client methods)
│   ├── hooks/
│   │   ├── useCustomContentAgent.ts (SSE listener)
│   │   ├── usePanelResize.ts (panel drag logic)
│   │   └── useEditorState.ts
│   └── utils/
│       └── file-explorer.ts (tree building helpers)
```

### 2.2 Backend Structure

```
backend/
├── api/
│   └── custom_content.py (FastAPI router with endpoints)
├── services/
│   ├── custom_content_agent.py (Main agent orchestrator)
│   ├── custom_content_mcp.py (MCP client for tool calling)
│   └── custom_content_tools.py (File creation, reading tools)
├── database/
│   └── models.py (add: CustomContentConversation, Message, File)
├── workflows/
│   └── custom_content/ (optional: workflow definitions)
└── custom_content_streaming.py (SSE event handlers)
```

---

## 3. Database Models

### New Tables to Create

#### `custom_content_conversations`
```python
class CustomContentConversation(Base):
    __tablename__ = "custom_content_conversations"
    
    id: str (PK, UUID)
    tenant_id: str (FK → tenants)
    user_id: str (FK → users)
    title: str
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    messages: List[Message]
    files: List[CustomContentFile]
```

#### `custom_content_messages`
```python
class CustomContentMessage(Base):
    __tablename__ = "custom_content_messages"
    
    id: str (PK, UUID)
    conversation_id: str (FK)
    role: str ('user' | 'assistant')
    content: str
    message_type: str ('text' | 'status_update')
    metadata: JSON (tool calls, step info)
    created_at: datetime
    
    # Relationships
    conversation: CustomContentConversation
```

#### `custom_content_files`
```python
class CustomContentFile(Base):
    __tablename__ = "custom_content_files"
    
    id: str (PK, UUID)
    conversation_id: str (FK)
    tenant_id: str (FK)
    user_id: str (FK)
    name: str
    file_type: str ('upload' | 'generated')
    mime_type: str
    path: str (on disk)
    size: int
    content: Text (stored for small files)
    is_generated: bool
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    conversation: CustomContentConversation
```

---

## 4. API Endpoints

### File Management

**POST** `/api/custom-content/files/upload`
- Upload file(s) to conversation
- Returns: `{file_id, name, type, size, upload_progress}`

**GET** `/api/custom-content/conversations/{conversation_id}/files`
- List all files (uploads + generated)
- Returns: `{uploads: [...], generated: [...]}`

**GET** `/api/custom-content/files/{file_id}`
- Fetch file content
- Returns: `{id, name, content, mime_type}`

**DELETE** `/api/custom-content/files/{file_id}`
- Delete file from conversation

**PATCH** `/api/custom-content/files/{file_id}`
- Rename, update metadata

### Conversation & Messages

**POST** `/api/custom-content/conversations`
- Create new conversation
- Returns: `{id, title}`

**GET** `/api/custom-content/conversations`
- List user's conversations (paginated)

**GET** `/api/custom-content/conversations/{conversation_id}`
- Get conversation details + message history

**POST** `/api/custom-content/conversations/{conversation_id}/messages`
- Send prompt to agent (request body: prompt, file_ids, context_file_id)
- Returns: **Server-Sent Events stream** with:
  - `status` events (step updates)
  - `message_delta` events (agent text streaming)
  - `file_created` events (new files)
  - `content_delta` events (file content streaming)
  - `file_completed` events
  - `done` event (summary)

**POST** `/api/custom-content/conversations/{conversation_id}/messages/{message_id}/stop`
- Cancel running agent request

### Session Persistence

**GET** `/api/custom-content/session`
- Restore user's active conversation and files
- Returns: `{conversation_id, messages, files, editor_state}`

---

## 5. Component Specifications

### 5.1 ResizablePanels Component
```tsx
<ResizablePanels
  panels={[
    { id: 'explorer', defaultWidth: 240, min: 160, max: 400 },
    { id: 'editor', defaultWidth: undefined, min: 300 }, // flex
    { id: 'chat', defaultWidth: 400, min: 300, max: 600 }
  ]}
  persistKey="custom-content-panel-widths"
>
  {/* children receive layoutState for each panel */}
</ResizablePanels>
```
- Draggable dividers between panels
- Persist widths in localStorage
- Responsive: stack on <1024px screens with tab navigation

### 5.2 FileExplorer Component
```tsx
<FileExplorer
  files={tree}
  selectedFileId={activeFileId}
  onSelectFile={handleFileSelect}
  onRename={handleRename}
  onDelete={handleDelete}
  isLoading={isUploading}
  uploadProgress={uploadStatus}
/>
```
- Two sections: **Uploads** and **Generated**
- Right-click context menu: Open, Rename, Download, Delete
- Show file icons, size, timestamp on hover
- "New" badge on recently generated files
- Tree structure for organization

### 5.3 Editor Component
```tsx
<Editor
  tabs={openFiles} // [{id, name, content, isDirty, isGenerating}]
  activeTabId={activeTab}
  onTabClick={selectTab}
  onTabClose={closeTab}
  onSave={saveFile}
  onContentChange={updateContent}
  onRevise={askAgentToRevise}
/>
```
- Multi-tab interface
- Syntax highlighting (Markdown, JSON, HTML, code, text)
- Markdown preview toggle
- Unsaved changes indicator (dot on tab)
- Toolbar: Copy, Download, Save, Toggle Preview, Ask Revision
- Live streaming: content appends as agent generates with cursor following

### 5.4 ChatPanel Component
```tsx
<ChatPanel
  messages={messageHistory}
  isLoading={isAgentRunning}
  agentSteps={activeSteps}
  onSendMessage={handleSend}
  onStopAgent={handleStop}
  onUpload={handleUpload}
  attachedFiles={selectedFiles}
/>
```
- Scrollable message history, auto-scroll to bottom
- User messages: right-aligned, bubble style
- Agent messages: left-aligned, plain text, Markdown rendered
- Agent steps: collapsible status items with spinner/check icons
- Composer at bottom: textarea + Upload + Send buttons
- Attached file chips with remove buttons

### 5.5 Composer Component
```tsx
<Composer
  value={prompt}
  onChange={setPrompt}
  onSend={handleSend}
  onUpload={handleUpload}
  attachedFiles={files}
  isLoading={isProcessing}
/>
```
- Multi-line textarea, auto-grows
- Enter to send, Shift+Enter for newline
- Upload button (paperclip icon)
- Send button (arrow-up icon); becomes Stop while running
- File chips show upload progress

---

## 6. Streaming Implementation

### Event Schema (Server → Client)

```json
{
  "event_type": "status",
  "data": {
    "step_id": "extract_text_from_file",
    "message": "Analyzing uploaded file...",
    "state": "running"
  }
}

{
  "event_type": "message_delta",
  "data": {
    "text": "The file contains..."
  }
}

{
  "event_type": "file_created",
  "data": {
    "file_id": "uuid",
    "name": "report.md",
    "type": "generated"
  }
}

{
  "event_type": "content_delta",
  "data": {
    "file_id": "uuid",
    "text": "# Report\n\nAnalysis:"
  }
}

{
  "event_type": "file_completed",
  "data": {
    "file_id": "uuid"
  }
}

{
  "event_type": "done",
  "data": {
    "summary": "Generated 2 files and 1 recommendation"
  }
}

{
  "event_type": "error",
  "data": {
    "code": "mcp_unavailable",
    "message": "MCP server unreachable. Retrying...",
    "retry_after": 30
  }
}
```

### SSE Implementation (Backend)

```python
@router.post("/api/custom-content/conversations/{conv_id}/messages")
async def send_message_sse(conv_id: str, request: SendMessageRequest, db: Session):
    async def event_generator():
        try:
            async for event in agent.run_async(prompt, files, context):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event_type': 'error', 'data': {...}})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### SSE Hook (Frontend)

```typescript
const useCustomContentAgent = (conversationId: string) => {
  const [messages, setMessages] = useState([])
  const [agentSteps, setAgentSteps] = useState([])
  const [files, setFiles] = useState([])
  const [isRunning, setIsRunning] = useState(false)

  const sendMessage = async (prompt: string, fileIds: string[]) => {
    setIsRunning(true)
    const eventSource = new EventSource(
      `/api/custom-content/conversations/${conversationId}/messages?prompt=${encodeURIComponent(prompt)}&files=${fileIds.join(',')}`
    )

    eventSource.addEventListener('status', (e) => {
      const data = JSON.parse(e.data)
      setAgentSteps(prev => [...prev, { ...data, id: uuid() }])
    })

    eventSource.addEventListener('message_delta', (e) => {
      const { text } = JSON.parse(e.data)
      setMessages(prev => {
        const last = prev[prev.length - 1]
        if (last?.role === 'assistant') {
          last.content += text
        }
        return [...prev]
      })
    })

    // ... handle other event types

    eventSource.addEventListener('done', () => {
      setIsRunning(false)
      eventSource.close()
    })
  }

  return { messages, agentSteps, files, sendMessage }
}
```

---

## 7. Agent Implementation

### CustomContentCreationAgent Flow

```python
class CustomContentCreationAgent:
    """Orchestrates content creation via LLM + MCP tools."""
    
    def __init__(self, tenant_id: str, user_id: str):
        self.llm_client = BedrockClient()  # AWS Bedrock
        self.mcp_client = MCPClient()
        self.file_tools = FileTools(user_id, tenant_id)
        
    async def run_async(
        self,
        prompt: str,
        file_ids: List[str],
        context_file_id: Optional[str],
        event_sink: Callable[[dict], Awaitable[None]]
    ) -> None:
        """Run agent with streaming."""
        
        # 1. Extract context from uploaded files
        await event_sink({
            'event_type': 'status',
            'data': {'step': 'extract_context', 'message': 'Analyzing uploaded files...', 'state': 'running'}
        })
        
        extracted_content = await self._extract_file_contents(file_ids)
        system_prompt = self._build_system_prompt(extracted_content)
        
        # 2. Build conversation history
        messages = [
            {'role': 'user', 'content': prompt},
            *self._build_context_messages(extracted_content, context_file_id)
        ]
        
        # 3. Agent loop (max 15 iterations)
        for iteration in range(15):
            # Stream LLM response
            await event_sink({
                'event_type': 'status',
                'data': {'step': 'llm_query', 'message': 'Querying LLM...', 'state': 'running'}
            })
            
            response = await self.llm_client.create_message_stream(
                system=system_prompt,
                messages=messages,
                tools=await self._get_available_tools()  # MCP tools
            )
            
            assistant_msg = {'role': 'assistant', 'content': ''}
            
            async for chunk in response:
                if chunk.type == 'text_delta':
                    assistant_msg['content'] += chunk.text
                    await event_sink({
                        'event_type': 'message_delta',
                        'data': {'text': chunk.text}
                    })
                elif chunk.type == 'tool_use':
                    tool_result = await self._execute_tool(chunk, event_sink)
                    messages.append({'role': 'user', 'content': tool_result})
                    
            messages.append(assistant_msg)
            
            # Check for stop condition
            if response.stop_reason == 'end_turn':
                break
        
        await event_sink({
            'event_type': 'done',
            'data': {'summary': f'Generated content with {len(self.created_files)} files'}
        })
    
    async def _execute_tool(self, tool_call, event_sink) -> str:
        """Execute MCP tool or built-in file tool."""
        if tool_call.name in ['create_file', 'update_file', 'read_file']:
            return await self.file_tools.execute(tool_call, event_sink)
        else:
            return await self.mcp_client.execute(tool_call)
```

### Tool Definitions

```python
TOOL_DEFINITIONS = [
    {
        "name": "create_file",
        "description": "Create a new file in the user's workspace",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path (e.g., 'lesson.md')"},
                "content": {"type": "string", "description": "File content"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "update_file",
        "description": "Update content of an existing file",
        "input_schema": {...}
    },
    {
        "name": "read_file",
        "description": "Read content of a file",
        "input_schema": {...}
    },
]
```

---

## 8. MCP Server Configuration

### Configuration File Location
`backend/config/mcp-servers.json` (or environment variables)

```json
{
  "servers": [
    {
      "name": "filesystem",
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/user/workspace"],
      "enabled": true
    },
    {
      "name": "web-search",
      "type": "stdio",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-web-search"],
      "env": {
        "SERPER_API_KEY": "${SERPER_API_KEY}"
      },
      "enabled": true
    },
    {
      "name": "knowledge-base",
      "type": "stdio",
      "command": "python",
      "args": ["-m", "knowledge_base_mcp"],
      "enabled": true
    }
  ]
}
```

---

## 9. Implementation Phases

### Phase 1: Foundation (1-2 weeks)
- [ ] Add navigation item + route
- [ ] Create database models & migrations
- [ ] Build ResizablePanels component
- [ ] Create API stubs (empty endpoints)

### Phase 2: File Management (1-2 weeks)
- [ ] Implement file upload API & progress tracking
- [ ] Build FileExplorer component
- [ ] Create file CRUD API endpoints
- [ ] Persist files to disk

### Phase 3: Editor (1-2 weeks)
- [ ] Integrate Monaco Editor (code) + TipTap (Markdown)
- [ ] Build multi-tab interface
- [ ] Implement save & dirty state tracking
- [ ] Add preview toggle & syntax highlighting

### Phase 4: Chat UI (1-2 weeks)
- [ ] Build ChatPanel & Composer components
- [ ] Implement message history display
- [ ] Add file upload via drag-and-drop + button
- [ ] Create file chip component

### Phase 5: Agent Backend (2-3 weeks)
- [ ] Implement CustomContentCreationAgent
- [ ] Integrate AWS Bedrock LLM client
- [ ] Build MCP client & tool calling
- [ ] Implement file tools (create, update, read)

### Phase 6: Streaming Integration (1-2 weeks)
- [ ] Implement SSE event streaming
- [ ] Build useCustomContentAgent hook
- [ ] Connect agent to frontend
- [ ] Add status step display + live content streaming

### Phase 7: Polish & Testing (1-2 weeks)
- [ ] Error handling & recovery
- [ ] Edge cases (disconnect, cancel, file limits)
- [ ] Unit & component tests
- [ ] End-to-end testing
- [ ] Documentation & README

---

## 10. Key Decisions & Clarifications Needed

### Questions for You

1. **LLM Provider Configuration**
   - AWS Bedrock is currently used. Should I use Bedrock's native client or the Anthropic SDK?
   - Which Claude model(s)? (Opus 5.5, Sonnet 5, etc.)
   - Where should API keys be stored? (Environment variables, .env, secure vault?)

2. **MCP Server Setup**
   - Should I configure MCP servers in `config/mcp-servers.json` or environment variables?
   - Which MCP servers should be enabled by default? (filesystem, web-search, databases, etc.)
   - Should the system gracefully degrade if an MCP server is unavailable?

3. **File Storage**
   - Current pattern: `backend/data/uploads/content/`. Should custom content use the same?
   - Should files be persisted indefinitely or cleaned up after a time period?
   - Maximum file size limits? (currently seems to be 25MB for content uploads)

4. **Streaming Method**
   - SSE (Server-Sent Events) is my proposal. Should I use WebSockets instead if already available?
   - Should I poll `/api/custom-content/status` instead of streaming?

5. **Conversation Persistence**
   - Should conversations be auto-saved or require explicit save?
   - How long should inactive conversations be kept? (forever? 30 days?)

6. **Permissions**
   - Can users share conversations/files with other users?
   - Should admins be able to view user conversations?

7. **Editor Choice**
   - Monaco (VSCode): Heavy, great for code, syntax highlighting
   - TipTap: Lightweight, great for Markdown/rich text
   - Custom lightweight solution?
   - Should I support both or choose one?

---

## 11. Styling Approach

The module will follow your existing design language:
- Use Tailwind classes with design tokens (primary, surface, border, etc.)
- No "heavy" chat bubbles; text flows naturally (Claude Desktop style)
- Rounded corners: lg (14px) for large containers, md (10px) for buttons
- Soft shadows and subtle transitions (150-200ms)
- Respect light/dark mode via CSS custom properties

Example composer styling:
```tailwind
<div className="bg-surface border border-border rounded-lg p-4 shadow-md">
  <textarea className="w-full bg-page text-ink focus:outline-none resize-none" />
  <div className="flex items-center gap-2 mt-3">
    <button className="text-ink-muted hover:text-ink">📎</button>
    <button className="ml-auto bg-primary hover:bg-primary-hover text-white rounded-full p-2">→</button>
  </div>
</div>
```

---

## 12. Testing Strategy

### Unit Tests
- Agent logic (file extraction, prompt building, tool execution)
- File utility functions (tree building, path validation)
- Store reducers (Zustand)

### Component Tests
- FileExplorer (selection, context menu, file operations)
- Editor (tab management, content editing, save)
- Composer (upload, send, validation)
- ResizablePanels (drag, resize, persist)

### Integration Tests
- Upload → File Explorer → Editor (full flow)
- Send message → Agent → Streaming events → Chat display
- Cancel running agent request

### E2E Tests (Playwright)
- Create conversation → Upload file → Send prompt → See generated content
- Edit and save generated file
- Download file
- Create multiple conversations, switch between them

---

## 13. Documentation to Provide

- **Setup Guide**: How to configure LLM provider and MCP servers
- **Component API**: Props, events, usage examples for each custom component
- **Agent Architecture**: How the CustomContentCreationAgent works
- **Streaming Protocol**: Event schema and client-side handling
- **File Storage**: Where files are stored and how to manage them

---

## 14. Success Criteria

✅ Navigation item appears and routes correctly  
✅ Three-panel layout with resizable dividers  
✅ File upload with progress indicator  
✅ Chat messages display with Markdown rendering  
✅ Agent status steps show in real-time  
✅ Generated content streams into editor live  
✅ Generated files appear in File Explorer  
✅ User can edit, save, and download files  
✅ Styling matches Claude Desktop aesthetic  
✅ Works in light and dark mode  
✅ Handles errors and network failures gracefully  

---

## Next Steps

Please review this plan and answer the **10 key questions** above. Once clarified, I can proceed with:

1. **Phase 1 implementation** (navigation, routes, database models)
2. Creating detailed component specifications
3. Writing the agent service
4. Building the streaming layer

Would you like me to start with any particular phase, or would you prefer to clarify the questions first?
