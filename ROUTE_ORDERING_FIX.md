# ✅ CRITICAL FIX: Route Ordering Bug

**Fixed Date:** October 5, 2025  
**Issue:** FastAPI route conflict causing `/history` endpoint to match as `/{research_id}`

---

## 🐛 Root Cause

### The Problem
FastAPI routes are matched in the order they are defined. The `/history` endpoint was defined AFTER the catch-all `/{research_id}` route, causing FastAPI to interpret "history" as a research_id parameter.

### Evidence from Logs
```
WHERE research.id = $1::VARCHAR
[cached since 118.7s ago] ('history',)  ← FastAPI treating "history" as an ID!
"GET /api/v1/research/history?limit=10 HTTP/1.1" 404 Not Found
```

### Route Definition Order (WRONG)
```python
# Line 112: Catch-all route defined first
@router.get("/{research_id}")
async def get_research_status(research_id: str):
    ...

# Line 213: Specific route defined last - NEVER REACHED!
@router.get("/history")
async def get_research_history():
    ...
```

**Result:** Any request to `/history` matched `/{research_id}` with `research_id="history"`

---

## ✅ The Fix

### Route Definition Order (CORRECT)
```python
# Line 78: Streaming endpoint (specific path)
@router.get("/stream/{research_id}")

# Line 113: History endpoint (specific path) - MOVED UP!
@router.get("/history")
async def get_research_history():
    ...

# Line 152: Catch-all route defined LAST
@router.get("/{research_id}")
async def get_research_status(research_id: str):
    ...
```

**Rule:** More specific routes MUST come before generic catch-all routes.

---

## 🔧 Changes Made

### 1. Moved `/history` Endpoint
**File:** `backend/app/api/v1/endpoints/research.py`

**Before:**
```python
Line 112: @router.get("/{research_id}")  ← Matches everything
Line 213: @router.get("/history")        ← Never reached
```

**After:**
```python
Line 113: @router.get("/history")        ← Matches first (specific)
Line 152: @router.get("/{research_id}")  ← Matches after (generic)
```

### 2. Removed Duplicate Definition
Deleted the second `/history` endpoint definition at line 213 to avoid function name collision.

---

## ✅ Verification

### Before Fix
```bash
curl http://localhost:8000/api/v1/research/history?limit=5
# Result: 404 Not Found
# SQL Query: WHERE research.id = 'history'  ← Wrong!
```

### After Fix
```bash
curl http://localhost:8000/api/v1/research/history?limit=5
# Result: 200 OK
# Response: [{"id":"74b15806...","status":"completed","query":"which is best at coding problems","created_at":"2025-10-05T09:58:17..."}]
```

### Backend Logs - Success
```
SELECT research.* FROM research 
ORDER BY research.created_at DESC 
LIMIT $1::INTEGER OFFSET $2::INTEGER
[generated in 0.00051s] (10, 0)
"GET /api/v1/research/history?limit=10 HTTP/1.1" 200 OK ✅
```

---

## 📊 Impact

### Frontend Impact
- ✅ **Research History Sidebar** now loads past queries
- ✅ Timestamps display correctly ("5m ago", "2h ago")
- ✅ Clicking history items loads previous research
- ✅ Auto-refresh every 30 seconds works

### User Experience
- ✅ Users can see their research history immediately
- ✅ No more empty "No research history yet" message (when data exists)
- ✅ Sidebar properly populated on page load

---

## 🎓 Lessons Learned

### FastAPI Route Ordering Rules
1. **Specific before generic**: `/history` must come before `/{research_id}`
2. **Path parameters are greedy**: `/{research_id}` matches ANY string
3. **Order matters**: Routes are matched top-to-bottom
4. **No overlapping**: Don't define the same route twice

### Route Ordering Best Practices
```python
# ✅ CORRECT ORDER:
@router.post("/query")              # Static path
@router.get("/history")             # Static path
@router.get("/stream/{id}")         # Path param with prefix
@router.get("/{research_id}")       # Catch-all last

# ❌ WRONG ORDER:
@router.get("/{research_id}")       # Catch-all first - blocks everything!
@router.get("/history")             # Never reached
```

---

## 🔍 How to Debug Similar Issues

### 1. Check Route Order
```bash
# List all routes in registration order
grep -n "@router\." backend/app/api/v1/endpoints/*.py
```

### 2. Test with curl
```bash
# Test specific endpoint
curl -v http://localhost:8000/api/v1/research/history

# Check what parameter is being matched
# Look for SQL WHERE clauses in logs
```

### 3. Check FastAPI Logs
```bash
docker compose logs backend --tail=50 | grep "research.id"
# If you see WHERE research.id = 'history', route order is wrong!
```

### 4. Use FastAPI Docs
```bash
# Visit http://localhost:8000/docs
# Check if /history endpoint appears separately from /{research_id}
```

---

## 📦 Files Modified

1. **backend/app/api/v1/endpoints/research.py**
   - Moved `/history` endpoint from line 213 → line 113
   - Removed duplicate definition at line 213
   - `/history` now comes BEFORE `/{research_id}`

---

## 🚀 Deployment Checklist

- [x] Backend rebuilt with fixed route ordering
- [x] Backend restarted successfully (6.7s)
- [x] `/history` endpoint returns 200 OK
- [x] Frontend sidebar loads research history
- [x] Timestamps display correctly
- [x] Follow-up conversation threading works
- [x] No duplicate route definitions
- [x] All tests passing

---

## 🎯 Status

**FIXED ✅**

- Research history sidebar now shows past queries with timestamps
- Follow-up button maintains conversation context
- Route ordering corrected for proper endpoint matching
- Both issues resolved and deployed

---

## 🧪 Test Procedure

1. **Open application:** http://localhost:3000
2. **Submit a query:** Enter any research question
3. **Check sidebar:** "Recent Research" should show your query with "just now"
4. **Wait 2 minutes:** Refresh sidebar should show "2m ago"
5. **Click follow-up:** "Ask Follow-up Question" should keep previous research visible
6. **Submit follow-up:** New query should link to parent research in database
7. **Verify in DB:**
   ```sql
   SELECT id, query, parent_research_id FROM research ORDER BY created_at DESC LIMIT 5;
   ```

**All tests passing!** ✅
