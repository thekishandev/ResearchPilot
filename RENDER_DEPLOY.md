# 🚀 Render Deployment Guide - ResearchPilot

## Quick Deploy (5 Minutes)

### Step 1: Sign Up for Render (1 minute)
1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign in with GitHub
4. Authorize Render to access your repositories

### Step 2: Create Blueprint (2 minutes)
1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect repository: **thekishandev/ResearchPilot**
3. Render will detect `render.yaml` automatically
4. Click **"Apply"**

### Step 3: Set Cerebras API Key (1 minute)
1. Go to **researchpilot-backend** service
2. Click **"Environment"** tab
3. Add variable:
   - Key: `CEREBRAS_API_KEY`
   - Value: `your_actual_cerebras_api_key`
4. Click **"Save Changes"**

### Step 4: Wait for Deploy (1-2 minutes)
- Backend builds and deploys automatically
- Check logs for progress
- Services will be live at:
  - Backend: `https://researchpilot-backend.onrender.com`
  - Frontend: Update VITE_API_URL and redeploy if needed

---

## What's Included (FREE)

✅ PostgreSQL Database (1GB)
✅ Redis Cache (25MB)
✅ Backend API with auto-HTTPS
✅ Auto-deploy from GitHub
✅ 750 hours/month runtime

⚠️ **Note**: Free tier services sleep after 15 min inactivity (30-60s wake time)

---

## Post-Deployment

### Test Your App
```bash
# Check backend health
curl https://researchpilot-backend.onrender.com/health

# Frontend (if deployed separately)
# Update VITE_API_URL to point to your Render backend
```

### Monitor Logs
1. Go to your service in Render
2. Click **"Logs"** tab
3. Watch for errors or issues

### Auto-Deploy
Every push to `main` branch triggers automatic deployment:
```bash
git add .
git commit -m "Update"
git push origin main
```

---

## Troubleshooting

**Build fails?**
- Check logs for specific errors
- Verify Dockerfile paths in `render.yaml`
- Ensure all dependencies are listed

**Backend won't start?**
- Confirm `CEREBRAS_API_KEY` is set
- Check `DATABASE_URL` is connected
- Review environment variables

**Services sleeping?**
- Use paid plan ($7/month per service)
- Or set up free uptime monitor (UptimeRobot)

---

## Cost
- **Current**: 100% FREE
- **Upgrade**: $7/month per service (no sleep)

**You're all set! 🎉**
