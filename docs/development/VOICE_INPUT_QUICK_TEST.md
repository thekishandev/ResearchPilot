# 🎤 Voice Input - Quick Test Instructions

## ✅ Voice Input is NOW FIXED!

### What Was Wrong:
- Web Speech API initialization happened **before** the mutation object was defined
- This caused a reference error when trying to auto-submit voice queries
- Duplicate function definitions were causing conflicts

### What Was Fixed:
1. ✅ Moved Web Speech API initialization **after** mutation definition
2. ✅ Added proper dependency array `[mutation, currentResearchId]`
3. ✅ Removed duplicate `toggleVoiceInput` function
4. ✅ Added comprehensive console logging for debugging
5. ✅ Added `onstart` handler for better state management

---

## 🧪 How to Test (2 methods)

### Method 1: Standalone Test (Easiest)

**No backend required - just test if Web Speech API works in your browser:**

```bash
# Open the test file in your browser
open test-voice-input.html
# or
google-chrome test-voice-input.html
```

**What you'll see:**
- Big "Start Voice Input" button
- Real-time console log
- Transcript display
- Color-coded status messages

**Test steps:**
1. Click "Start Voice Input"
2. Allow microphone permission
3. Speak: "Hello world this is a test"
4. See transcript appear

✅ If this works → Web Speech API is supported in your browser  
❌ If this doesn't work → Your browser doesn't support Web Speech API

---

### Method 2: Full Application Test

**Test voice input with the full ResearchPilot application:**

```bash
# Make sure services are running
docker compose ps

# If not running, start them:
docker compose up -d

# Open browser
open http://localhost:5173
```

**Test steps:**

1. **Open Browser Console** (IMPORTANT!)
   - Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)
   - Click "Console" tab
   - Keep this open!

2. **Check Initialization**
   - You should see in console:
     ```
     Web Speech API initialized successfully
     ```
   - If you DON'T see this, refresh page (Ctrl+Shift+R)

3. **Click Microphone Button**
   - Located bottom-right of the textarea
   - Console should show:
     ```
     toggleVoiceInput called, recognition: true, isListening: false
     Starting recognition...
     Speech recognition started
     ```

4. **Allow Microphone Permission**
   - Browser will prompt (first time only)
   - Click "Allow"

5. **Check Visual Feedback**
   - ✅ Icon turns red
   - ✅ Icon pulses/animates
   - ✅ Header shows "Listening..."

6. **Speak Your Query**
   - Speak clearly: "Explain quantum computing in simple terms"
   - Wait 1 second after speaking
   - Console should show:
     ```
     Voice input transcript: "Explain quantum computing in simple terms"
     Auto-submitting voice query...
     Research submitted: {id: "...", status: "processing"}
     ```

7. **Verify Backend Processing**
   - Orchestration panel appears
   - 6 data sources start querying
   - Cerebras synthesis streams in
   - Results display with sources

---

## 🔍 Debugging

### If voice button doesn't appear:
```bash
# Check if frontend is running
docker compose ps frontend

# Restart if needed
docker compose restart frontend

# Wait 5 seconds, then refresh browser
```

### If "Web Speech API not initialized" in console:
**Cause:** Your browser doesn't support Web Speech API

**Solution:**
- ✅ Use Chrome 25+ (recommended)
- ✅ Use Edge 79+
- ✅ Use Safari 14.1+
- ❌ Don't use Firefox (not supported)

### If mic button is grayed out (disabled):
**Check console for:**
```
Voice input is not supported in your browser
```

**Solution:** Switch to Chrome, Edge, or Safari

### If mic button works but nothing happens when you speak:
**Check:**
1. Microphone permissions (browser + system level)
2. Speak louder and clearer
3. Wait 1 second after finishing speech
4. Check console for error messages

**Common errors:**
- `no-speech` → Speak louder or check mic is working
- `not-allowed` → Allow microphone in browser settings
- `audio-capture` → Microphone not found/working

### If transcript appears but doesn't submit:
**Check console for:**
```
Auto-submitting voice query...
```

If missing, query might be < 10 characters (minimum required).

---

## 📊 Expected Console Output (Success)

When everything works perfectly:

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
Parsed SSE data status: processing
...
```

---

## 🎯 Quick Verification Commands

**In browser console, paste this:**

```javascript
// Check if Web Speech API is available
console.log('✅ Check Web Speech API:', 'webkitSpeechRecognition' in window)

// Check if mic button exists
console.log('✅ Mic button exists:', !!document.querySelector('[title*="voice"]'))

// Check if button is enabled
const btn = document.querySelector('[title*="voice"]')
console.log('✅ Button enabled:', btn ? !btn.disabled : false)

// Summary
if ('webkitSpeechRecognition' in window && btn && !btn.disabled) {
  console.log('🎉 Voice input should work! Click the mic and speak.')
} else {
  console.log('❌ Voice input not available. Check browser compatibility.')
}
```

---

## 🌍 Browser Support

| Browser | Supported | Notes |
|---------|-----------|-------|
| Chrome 25+ | ✅ YES | Best support, recommended |
| Edge 79+ | ✅ YES | Full support |
| Safari 14.1+ | ✅ YES | On-device recognition |
| Firefox | ❌ NO | Web Speech API not supported |
| Opera 27+ | ✅ YES | Based on Chromium |

**Coverage:** ~85% of global browser users

---

## 🚀 Production Deployment Notes

⚠️ **HTTPS Required:** Web Speech API requires HTTPS in production!

**Local testing:** Works on `localhost` (HTTP OK)  
**Production:** MUST use `https://` domain

---

## 📞 Still Not Working?

1. **First:** Try the standalone test (`test-voice-input.html`)
   - If this doesn't work → Browser compatibility issue
   - If this works → Application integration issue

2. **Check console** for error messages

3. **Check browser compatibility** (must be Chrome/Edge/Safari)

4. **Check microphone permissions** (browser + system)

5. **Try incognito mode** (to rule out extensions)

6. **Hard refresh** (Ctrl+Shift+R) to clear cache

---

## 📚 Additional Resources

- **Full debugging guide:** `VOICE_INPUT_DEBUGGING.md`
- **Complete testing checklist:** `TESTING_VOICE_INPUT.md`
- **Implementation details:** `VOICE_INPUT_INTEGRATION.md`

---

## ✅ Success Checklist

When voice input works:
- [ ] Console shows "Web Speech API initialized successfully"
- [ ] Mic button visible and enabled (not grayed out)
- [ ] Click mic → Icon turns red and pulses
- [ ] Speak → Console shows transcript
- [ ] Auto-submits to backend
- [ ] Orchestration panel appears
- [ ] Cerebras synthesis streams in
- [ ] Results display

**If all ✅ → Voice input is fully working! 🎉**

---

**Quick Start:** Open `test-voice-input.html` in Chrome to test immediately!
