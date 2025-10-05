# ResearchPilot Enhancement Plan - Advanced Cerebras Capabilities

## 🎯 Implementation Roadmap

### Phase 1: Advanced Cerebras Capabilities ✅ (Current Focus)

#### 1.1 Structured Outputs (HIGH PRIORITY)
**Goal:** Enforce consistent JSON schema for research synthesis

**Implementation:**
- Create Pydantic models for structured synthesis response
- Define JSON schema for research results
- Update `cerebras_service.py` to use `response_format` with JSON schema
- Add structured credibility scoring
- Add structured source attribution

**Models to create:**
```python
class SourceCitation(BaseModel):
    source_name: str
    url: Optional[str]
    confidence: float
    relevance: str

class ResearchSynthesis(BaseModel):
    summary: str
    key_findings: List[str]
    sources: List[SourceCitation]
    credibility_score: float
    confidence_level: str  # "high", "medium", "low"
    follow_up_questions: List[str]
```

**Benefits:**
- Consistent API responses
- Type-safe frontend parsing
- Better error handling
- Improved reliability

---

#### 1.2 Streaming Enhancements (MEDIUM PRIORITY)
**Goal:** Already implemented, but optimize for better UX

**Current Status:** ✅ Already streaming SSE responses

**Optimizations:**
- Add structured streaming (JSON chunks with metadata)
- Stream synthesis sections separately:
  - Stream summary first
  - Then stream key findings
  - Finally stream detailed analysis
- Add progress indicators for each section

---

#### 1.3 Tool Use / Function Calling (HIGH IMPACT)
**Goal:** Let Cerebras dynamically choose which MCP sources to query

**Implementation:**
```python
# Define tools for Cerebras
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "strict": True,
            "description": "Search the web for current information",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_arxiv",
            "strict": True,
            "description": "Search academic papers on ArXiv",
            "parameters": {...}
        }
    },
    # ... define all 6 MCP sources as tools
]
```

**Flow:**
1. User submits query
2. Cerebras analyzes query and decides which tools to call
3. Backend executes selected MCP sources (not all 6)
4. Cerebras synthesizes results
5. If needed, Cerebras calls more tools (multi-turn)

**Benefits:**
- **Intelligent source selection** (only query relevant sources)
- **Faster responses** (fewer unnecessary API calls)
- **Multi-turn refinement** (Cerebras can request more data)
- **Cost savings** (fewer MCP calls)

---

#### 1.4 Reasoning Support (NICE TO HAVE)
**Goal:** Add reasoning_effort parameter for complex queries

**Implementation:**
```python
# Detect query complexity and adjust reasoning effort
if is_complex_query(query):
    reasoning_effort = "high"  # More thorough analysis
else:
    reasoning_effort = "medium"  # Balanced
```

**Use Cases:**
- Complex research questions → high reasoning
- Simple factual queries → low reasoning
- Analysis/comparison tasks → medium-high reasoning

---

### Phase 2: Multi-turn Conversation Threading ✅ (ALREADY IMPLEMENTED!)

**Current Status:** ✅ **COMPLETE**
- `parent_research_id` column in database
- Frontend conversation history UI
- Backend context passing to Cerebras
- Conversation state management

**What's Working:**
- User can click "Follow Up" button
- New query includes `parent_research_id`
- Backend fetches parent research
- Cerebras receives previous Q&A in prompt
- AI references prior answers

**Possible Enhancements:**
- Show full conversation thread in sidebar (not just list)
- Add "Continue Conversation" input at bottom of results
- Add conversation export (PDF/Markdown)
- Add conversation branching (explore different angles)

---

### Phase 3: Nice to Have Features

#### 3.1 Knowledge Graph Visualization
**Status:** Not started  
**Priority:** Medium  
**Effort:** High (3-4 days)

**Description:**
- Visualize connections between research topics
- Use D3.js or Cytoscape.js
- Show relationships between sources
- Interactive node exploration

**Implementation:**
```typescript
// Frontend: D3.js graph visualization
interface KnowledgeNode {
  id: string
  label: string
  type: 'topic' | 'source' | 'finding'
  relevance: number
}

interface KnowledgeEdge {
  source: string
  target: string
  relationship: string
  weight: number
}
```

---

#### 3.2 Custom Source Management
**Status:** Not started  
**Priority:** Low  
**Effort:** Medium (2-3 days)

**Description:**
- Allow users to add custom MCP servers
- UI for managing source preferences
- Enable/disable specific sources
- Set source priority/weights

**Implementation:**
```python
class CustomSource(BaseModel):
    name: str
    url: str
    api_key: Optional[str]
    enabled: bool
    priority: int  # 1-10
```

---

#### 3.3 Research Templates
**Status:** Not started  
**Priority:** Medium  
**Effort:** Low (1 day)

**Description:**
- Pre-built query templates for common use cases
- "Market Research", "Literature Review", "Competitive Analysis"
- Customizable parameters
- Save custom templates

**Templates:**
```python
TEMPLATES = {
    "market_research": {
        "prompt_template": "Analyze the market for {product} including key players, market size, growth trends, and competitive landscape",
        "sources": ["web-search", "news", "database"],
        "synthesis_format": "executive_summary"
    },
    "literature_review": {
        "prompt_template": "Provide a comprehensive literature review on {topic} from the past {years} years",
        "sources": ["arxiv", "database", "web-search"],
        "synthesis_format": "academic"
    }
}
```

---

#### 3.4 Collaborative Research
**Status:** Not started  
**Priority:** Low  
**Effort:** Very High (1-2 weeks)

**Description:**
- Share research sessions with team
- Real-time collaboration
- Comments and annotations
- Version history

**Tech Stack:**
- WebSockets for real-time updates
- User authentication (JWT)
- Shared sessions in database
- Access control (view/edit permissions)

---

### Phase 4: Stretch Goals

#### 4.1 Fact-Checking Integration
**Priority:** Medium  
**Effort:** High

- Verify claims against multiple sources
- Highlight conflicting information
- Show source agreement/disagreement

#### 4.2 Browser Extension
**Priority:** Low  
**Effort:** Medium

- Research from any webpage
- Highlight text → right-click → "Research with ResearchPilot"
- Quick lookup popup

#### 4.3 API Documentation with Examples
**Priority:** Medium  
**Effort:** Low

- Interactive API docs (Swagger/ReDoc already exists)
- Add more code examples
- Add rate limiting info
- Add authentication guide (if implemented)

#### 4.4 Export Formats
**Priority:** Medium  
**Effort:** Low

- Export to PDF (with citations)
- Export to Markdown
- Export to Google Docs
- Export conversation history

---

## 📊 Priority Matrix

| Feature | Impact | Effort | Priority | Status |
|---------|--------|--------|----------|--------|
| **Structured Outputs** | 🔥 High | Low | **NOW** | ⏳ Next |
| **Tool Use (Smart Source Selection)** | 🔥 High | Medium | **NOW** | ⏳ Next |
| Multi-turn Conversation | 🔥 High | Medium | HIGH | ✅ Done |
| Reasoning Support | 🟡 Medium | Low | Medium | ⏳ Next |
| Streaming Optimization | 🟡 Medium | Low | Medium | ⏳ Next |
| Knowledge Graph | 🟢 Nice | High | Low | ❌ Not Started |
| Custom Sources | 🟢 Nice | Medium | Low | ❌ Not Started |
| Research Templates | 🟡 Medium | Low | Medium | ❌ Not Started |
| Collaborative Research | 🟢 Nice | Very High | Low | ❌ Not Started |
| Fact-Checking | 🟡 Medium | High | Low | ❌ Not Started |
| Browser Extension | 🟢 Nice | Medium | Low | ❌ Not Started |
| Export Formats | 🟡 Medium | Low | Medium | ❌ Not Started |

---

## 🎯 Immediate Action Items (Next 2 Hours)

### 1. Implement Structured Outputs (45 min)
- [ ] Create Pydantic models for synthesis
- [ ] Update `cerebras_service.py` with JSON schema
- [ ] Add structured response parsing
- [ ] Test with sample query

### 2. Implement Tool Use (60 min)
- [ ] Define tool schemas for 6 MCP sources
- [ ] Update Cerebras API call to include tools
- [ ] Handle tool calls in backend
- [ ] Implement multi-turn tool calling loop
- [ ] Test dynamic source selection

### 3. Add Reasoning Support (15 min)
- [ ] Add `reasoning_effort` parameter
- [ ] Implement query complexity detection
- [ ] Update Cerebras API call
- [ ] Test with complex vs simple queries

### 4. Update README (30 min)
- [ ] Document new Cerebras capabilities
- [ ] Add architecture diagram update
- [ ] Add usage examples
- [ ] Update API documentation
- [ ] Add conversation threading docs

---

## 🚀 Expected Impact

### With Structured Outputs:
- ✅ Consistent JSON responses
- ✅ Type-safe frontend
- ✅ Better error handling
- ✅ Easier testing

### With Tool Use:
- ✅ **2-3x faster queries** (only query relevant sources)
- ✅ **50% cost reduction** (fewer MCP calls)
- ✅ **Smarter research** (AI decides what's needed)
- ✅ **Multi-turn refinement** (AI can request more data)

### With Reasoning Support:
- ✅ Better quality for complex queries
- ✅ Faster responses for simple queries
- ✅ Optimized resource usage

---

## 📝 Next Steps

**Immediate (Today):**
1. Implement Structured Outputs
2. Implement Tool Use
3. Add Reasoning Support
4. Update README

**Short-term (This Week):**
1. Add research templates
2. Optimize streaming
3. Add export formats
4. Improve error handling

**Long-term (Future):**
1. Knowledge graph visualization
2. Custom source management
3. Collaborative features
4. Browser extension

---

**Let's start with Structured Outputs and Tool Use - these will have the biggest immediate impact!** 🚀
