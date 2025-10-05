# Voice Input Debugging & Testing Guide

## 🔍 How to Test Voice Input (Step-by-Step)

### 1. Open Browser Console First!
**This is CRITICAL for debugging**

```
1. Open Chrome/Edge browser
2. Go to http://localhost:5173
3. Press F12 to open Developer Tools
4. Click "Console" tab
5. Keep this open while testing
```

### 2. Check Web Speech API Availability

In the browser console, type:
```javascript
console.log('webkitSpeechRecognition:', 'webkitSpeechRecognition' in window)
console.log('SpeechRecognition:', 'SpeechRecognition' in window)
```

**Expected output:**
```
webkitSpeechRecognition: true
SpeechRecognition: false  (or true)
```

If both are `false`, Web Speech API is not available in your browser.

### 3. Check if Recognition Initialized

In browser console:
```javascript
// This should show in console automatically when page loads:
// "Web Speech API initialized successfully"
```

If you don't see this message, the recognition object didn't initialize.

### 4. Test Microphone Button Click

**Steps:**
1. Click the microphone button (bottom-right of textarea)
2. Watch the console for these messages:

```
toggleVoiceInput called, recognition: true, isListening: false
Starting recognition...
Speech recognition started
```

3. Browser should prompt for microphone permission (first time)
4. Icon should turn red and pulse
5. Header should show "Listening..."

### 5. Test Voice Recognition

**Steps:**
1. After clicking mic (when red pulsing)
2. Speak clearly: "Explain quantum computing in simple terms"
3. Watch console for:

```
Voice input transcript: "Explain quantum computing in simple terms"
Auto-submitting voice query...
Research submitted: {id: "...", status: "processing"}
```

4. Query should appear in textarea
5. Request should auto-submit to backend

### 6. Common Issues & Solutions

#### Issue: "Voice input is not supported in your browser"
**Cause:** Browser doesn't have Web Speech API  
**Solution:** 
- Use Chrome 25+ (best support)
- Use Edge 79+
- Use Safari 14.1+
- **Don't use Firefox** (not supported)

**Test in console:**
```javascript
if ('webkitSpeechRecognition' in window) {
  console.log('✅ Web Speech API supported!')
} else {
  console.log('❌ Web Speech API NOT supported')
}
```

#### Issue: Button click does nothing
**Debug in console:**
```javascript
// Check if recognition object exists
console.log('Recognition object:', document.querySelector('[title*="voice"]'))
```

**Check console for errors:**
- Look for "Error starting recognition"
- Look for "toggleVoiceInput called, recognition: false"

#### Issue: "Microphone access denied"
**Solutions:**
1. Click the camera/mic icon in browser address bar
2. Change microphone permission to "Allow"
3. Refresh page
4. Try again

**Chrome Settings:**
```
chrome://settings/content/microphone
```

**Edge Settings:**
```
edge://settings/content/microphone
```

#### Issue: Recognition starts but no transcript
**Debug:**
1. Check if mic is working in system settings
2. Speak louder and clearer
3. Wait for the beep/indication that recording started
4. Check console for "Speech recognition error"

**Common errors:**
- `no-speech`: No speech detected (too quiet or mic issue)
- `audio-capture`: Mic not working
- `not-allowed`: Permission denied
- `aborted`: Recognition stopped early

#### Issue: Transcript appears but doesn't submit
**Check console for:**
```
Auto-submitting voice query...
```

If missing, query might be < 10 characters.

**Test in console:**
```javascript
// Manual test submission
console.log('Query length:', document.querySelector('textarea').value.length)
```

Minimum required: 10 characters

### 7. Manual Voice Test (Console)

You can manually test the Web Speech API:

```javascript
// Create recognition instance
const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
const recognition = new SpeechRecognition()

recognition.continuous = false
recognition.interimResults = false
recognition.lang = 'en-US'

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript
  console.log('📝 Transcript:', transcript)
}

recognition.onerror = (event) => {
  console.error('❌ Error:', event.error)
}

recognition.onend = () => {
  console.log('⏹️ Recognition ended')
}

// Start recognition
console.log('🎤 Starting...')
recognition.start()

// Speak something, then check console for transcript
```

### 8. Backend Connection Test

**Test if backend receives voice query:**

```bash
# In terminal, watch backend logs
docker compose logs -f backend | grep "Processing research query"

# Then use voice input in browser
# You should see:
# INFO: Processing research query: "your spoken query here"
```

### 9. Full End-to-End Test Checklist

- [ ] Browser: Chrome/Edge (not Firefox)
- [ ] Page loaded: http://localhost:5173
- [ ] Console open: F12 → Console tab
- [ ] Message visible: "Web Speech API initialized successfully"
- [ ] Click mic button
- [ ] Console shows: "Starting recognition..."
- [ ] Icon turns red with pulse animation
- [ ] Header shows: "Listening..."
- [ ] Speak query (min 10 chars)
- [ ] Console shows: "Voice input transcript: ..."
- [ ] Console shows: "Auto-submitting voice query..."
- [ ] Orchestration panel appears
- [ ] 6 sources start processing
- [ ] Cerebras synthesis streams in
- [ ] Results display with sources

### 10. Performance Monitoring

**In browser console:**
```javascript
// Monitor all voice input events
const textarea = document.querySelector('textarea')
const micButton = document.querySelector('[title*="voice"]')

console.log('Textarea:', !!textarea)
console.log('Mic button:', !!micButton)
console.log('Button disabled:', micButton?.disabled)
```

### 11. Network Monitoring

**Check API calls:**
1. F12 → Network tab
2. Click mic and speak
3. Look for:
   - POST `/api/v1/research/query`
   - Should see status 201 Created
   - GET `/api/v1/research/stream/{id}`
   - Should see EventStream

### 12. Debugging Failed Recognition

**Add detailed logging:**
```javascript
// In browser console, override the recognition for debugging
window.addEventListener('load', () => {
  setTimeout(() => {
    const testRecognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)()
    
    testRecognition.onstart = () => console.log('🟢 START')
    testRecognition.onend = () => console.log('🔴 END')
    testRecognition.onerror = (e) => console.log('❌ ERROR:', e.error, e)
    testRecognition.onresult = (e) => console.log('✅ RESULT:', e.results[0][0].transcript)
    
    console.log('Test recognition created:', testRecognition)
    console.log('Try: testRecognition.start()')
  }, 1000)
})
```

### 13. Quick Fixes

**If nothing works, try:**

1. **Hard refresh:** Ctrl+Shift+R (Chrome) or Cmd+Shift+R (Mac)
2. **Clear cache:** 
   ```javascript
   // In console
   localStorage.clear()
   sessionStorage.clear()
   location.reload(true)
   ```
3. **Restart browser completely**
4. **Check microphone permissions system-wide**
5. **Try incognito mode** (to rule out extensions)

### 14. Expected Console Output (Success)

When voice input works perfectly, you should see:

```
Web Speech API initialized successfully
toggleVoiceInput called, recognition: true, isListening: false
Starting recognition...
Speech recognition started
Voice input transcript: "Explain quantum computing in simple terms"
Auto-submitting voice query...
Submit clicked, query length: 43
Submitting research query: Explain quantum computing in simple terms
Research submitted: {id: "abc-123", status: "processing"}
Starting SSE stream for research abc-123
SSE connection opened
SSE message #1 received, length: 234
...
```

### 15. HTTPS Requirement (Production)

⚠️ **Important:** Web Speech API requires HTTPS in production!

**Local testing:** Works on `localhost` (HTTP is OK)  
**Production:** MUST use `https://` domain

**Test if HTTPS is required:**
```javascript
console.log('Is secure context:', window.isSecureContext)
// Should be true for voice input to work in production
```

### 16. Browser Compatibility Check

**Run this in console:**
```javascript
const features = {
  'Web Speech API': ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window),
  'Microphone access': navigator.mediaDevices?.getUserMedia !== undefined,
  'Secure context (HTTPS)': window.isSecureContext,
  'Browser': navigator.userAgent.includes('Chrome') ? 'Chrome ✅' : 
             navigator.userAgent.includes('Edg') ? 'Edge ✅' : 
             navigator.userAgent.includes('Safari') ? 'Safari ✅' : 
             navigator.userAgent.includes('Firefox') ? 'Firefox ❌' : 'Unknown'
}

console.table(features)
```

Expected output:
```
┌─────────────────────────┬───────────┐
│ Web Speech API          │ true      │
│ Microphone access       │ true      │
│ Secure context (HTTPS)  │ true      │
│ Browser                 │ Chrome ✅  │
└─────────────────────────┴───────────┘
```

### 17. Final Test Script

**Copy-paste this into browser console:**
```javascript
(function testVoiceInput() {
  console.log('=== VOICE INPUT TEST ===')
  
  const checks = {
    'Web Speech API': ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window),
    'Textarea exists': !!document.querySelector('textarea'),
    'Mic button exists': !!document.querySelector('[title*="voice"]'),
    'Recognition initialized': localStorage.getItem('voiceRecognitionInit') === 'true'
  }
  
  console.table(checks)
  
  const allPass = Object.values(checks).every(v => v === true)
  
  if (allPass) {
    console.log('✅ ALL CHECKS PASSED - Voice input should work!')
    console.log('Try clicking the microphone button and speaking.')
  } else {
    console.log('❌ SOME CHECKS FAILED - Voice input may not work.')
    console.log('Failed checks:', Object.entries(checks).filter(([k,v]) => !v).map(([k]) => k))
  }
})()
```

---

## 🎯 Quick Troubleshooting Decision Tree

```
Voice input not working?
│
├─ Mic button doesn't exist?
│  └─ Refresh page (Ctrl+Shift+R)
│
├─ Button disabled (grayed out)?
│  └─ Check browser: Must be Chrome/Edge/Safari (not Firefox)
│
├─ Button works but nothing happens?
│  ├─ Check console for "Web Speech API initialized successfully"
│  ├─ If missing → Web Speech API not available
│  └─ If present → Check for JavaScript errors
│
├─ Red pulse shows but no transcript?
│  ├─ Check mic permissions (browser + system)
│  ├─ Try speaking louder
│  └─ Check for "no-speech" error in console
│
├─ Transcript appears but doesn't submit?
│  ├─ Check query length (must be ≥10 chars)
│  ├─ Check console for "Auto-submitting voice query..."
│  └─ Check backend is running (docker compose ps)
│
└─ Everything seems to work but no results?
   ├─ Check backend logs: docker compose logs backend
   ├─ Check Cerebras API key is set
   └─ Check network tab for API errors
```

---

## 📞 Support

If voice input still doesn't work after following this guide:

1. Share console output (F12 → Console → copy all text)
2. Share network errors (F12 → Network → filter by "research")
3. Share browser version (Help → About)
4. Share backend logs: `docker compose logs backend --tail=50`

---

**Remember: Voice input requires Chrome/Edge/Safari and microphone permissions!** 🎤
