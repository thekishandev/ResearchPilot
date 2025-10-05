# Testing Voice Input with Cerebras Backend

## ✅ Quick Test Guide

### 1. Access Application
```bash
Frontend: http://localhost:5173
Backend:  http://localhost:8000
```

### 2. Visual Test Checklist

**Initial State:**
- [ ] Microphone button visible (bottom-right of textarea)
- [ ] Icon is gray (idle state)
- [ ] Hover shows tooltip: "Click to speak your research query"

**Click Microphone:**
- [ ] Browser prompts for microphone permission (first time)
- [ ] Icon turns red with pulsing animation
- [ ] Background becomes red-tinted
- [ ] Header shows "Listening..." text
- [ ] Tooltip changes to "Listening... Click to stop"

**Speak Query:**
- [ ] Speak clearly: "Explain quantum computing in simple terms"
- [ ] Wait for silence detection (~1 second)

**Auto-Submit:**
- [ ] Query appears in textarea
- [ ] Red icon stops pulsing
- [ ] "Listening..." disappears
- [ ] Query auto-submits to backend (100ms delay)
- [ ] Orchestration panel appears
- [ ] 6 data sources show "processing" status
- [ ] Results stream in real-time via SSE

**Synthesis Display:**
- [ ] Cerebras synthesis appears paragraph by paragraph
- [ ] Source attribution shows at bottom
- [ ] "Follow Up" button appears after completion
- [ ] Conversation history updates in sidebar

### 3. Follow-Up Test

**After First Query Completes:**
- [ ] Click microphone button again
- [ ] Speak: "What are some real-world applications?"
- [ ] Query auto-submits
- [ ] Backend includes parent_research_id
- [ ] Cerebras references previous answer
- [ ] Conversation shows both queries stacked

### 4. Error Scenarios

**No Speech Detected:**
1. Click microphone
2. Wait 5+ seconds without speaking
3. [ ] Alert: "No speech detected. Please try again."

**Query Too Short:**
1. Click microphone
2. Say only "Hi" (3 characters)
3. [ ] Alert: "Please speak at least 10 characters..."

**Microphone Denied:**
1. Block microphone in browser settings
2. Refresh page
3. Click microphone
4. [ ] Alert: "Microphone access denied..."

### 5. Backend Integration Test

**Check Backend Receives Voice Query:**
```bash
# Watch backend logs while speaking
docker compose logs -f backend | grep "Processing research query"

# Expected output:
# INFO: Processing research query: "Explain quantum computing in simple terms"
# INFO: Orchestrating 6 MCP sources...
# INFO: Calling Cerebras for synthesis...
```

**Verify Cerebras API Called:**
```bash
# Check for Cerebras API calls
docker compose logs backend | grep -i cerebras | tail -5

# Expected:
# INFO: Cerebras synthesis completed
# INFO: Streaming results via SSE
```

### 6. Performance Test

**Measure End-to-End Latency:**

1. Start timer when you finish speaking
2. Note when synthesis appears
3. **Expected:** <2.5 seconds total
   - Speech capture: ~0.5s
   - Auto-submit delay: 0.1s
   - Backend orchestration: 0.8s
   - Cerebras synthesis: 0.9s
   - SSE streaming: real-time

### 7. Browser Compatibility

**Chrome/Edge (Recommended):**
- [ ] Microphone button enabled
- [ ] Voice recognition works
- [ ] Auto-submit works
- [ ] ✅ Full support

**Safari:**
- [ ] Microphone button enabled
- [ ] Voice recognition works (on-device)
- [ ] Auto-submit works
- [ ] ✅ Full support

**Firefox:**
- [ ] Microphone button disabled
- [ ] Typing still works
- [ ] ❌ Voice not supported (graceful fallback)

## 🎬 Demo Script (2 minutes)

### Opening (15 seconds):
- "ResearchPilot features hands-free voice input"
- "Powered by Web Speech API and Cerebras AI"
- "Watch as I ask a complex research question..."

### First Query (60 seconds):
1. Click microphone button
2. Say clearly: "What are the latest breakthroughs in artificial intelligence in 2024?"
3. Show:
   - Red pulsing icon
   - Query transcription
   - Auto-submission
   - 6 sources processing
   - Cerebras streaming synthesis
   - Source attribution

### Follow-Up Query (45 seconds):
1. Click microphone again
2. Say: "How do these compare to previous years?"
3. Show:
   - Context awareness (references first answer)
   - Coherent multi-turn conversation
   - Both queries in history

### Closing (30 seconds):
- "Sub-2 second response from voice to AI synthesis"
- "6 data sources orchestrated in parallel"
- "Context-aware follow-ups"
- "All powered by Cerebras Llama 3.3 70B"

## 🐛 Common Issues

### Issue: Button shows but clicking does nothing
**Fix:** Check browser console for errors, may need HTTPS in production

### Issue: "Listening..." stays forever
**Fix:** Speak louder or check microphone is working in system settings

### Issue: Query doesn't auto-submit
**Fix:** Check browser console, may be <10 characters or API error

### Issue: Backend error after voice input
**Fix:** Check CEREBRAS_API_KEY is set in backend/.env

## 📊 Success Criteria

✅ **Voice Capture:** Query transcribed accurately  
✅ **Auto-Submit:** Query sent to backend automatically  
✅ **Orchestration:** 6 MCP sources queried  
✅ **Synthesis:** Cerebras Llama 3.3 70B generates report  
✅ **Streaming:** Real-time SSE display  
✅ **Follow-ups:** Context-aware multi-turn  
✅ **Performance:** <2.5s voice to synthesis  
✅ **UX:** Clear visual feedback at all stages  

## 🎯 Next Steps After Testing

If all tests pass:
1. ✅ Voice input is production-ready
2. ✅ Backend integration working
3. ✅ Cerebras synthesis functioning
4. ✅ Ready for demo/deployment

If tests fail:
1. Check browser console for errors
2. Verify backend logs for API issues
3. Confirm CEREBRAS_API_KEY is valid
4. Test with different queries/browsers
5. Review VOICE_INPUT_INTEGRATION.md troubleshooting

## 🚀 Final Verification Command

```bash
# Complete system health check
cd /home/kishan/Downloads/Projects/Github/ResearchPilot

# Check all services
docker compose ps

# Check backend health (including Cerebras)
curl http://localhost:8000/api/v1/health | jq

# Check frontend is running
curl -s http://localhost:5173 | grep -i "researchpilot"

# All should return healthy/running status
```

**If all services healthy → Voice input ready for testing! 🎤**
