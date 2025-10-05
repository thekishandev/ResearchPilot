# 🎨 Frontend Deployment on Render

## What I Just Added:

✅ **Frontend service** to `render.yaml`
✅ **Environment variable** `VITE_API_URL` pointing to backend
✅ Also added optional env vars for `NEWS_API_KEY` and `GITHUB_TOKEN`

## 🚀 Next Steps in Render Dashboard:

### Option 1: Re-sync Blueprint (Recommended)
1. Go to your **Blueprint page** in Render
2. Click **"Manual Sync"** button
3. Render will detect the new frontend service
4. Click **"Apply Changes"**
5. Frontend will start building automatically

### Option 2: Add Frontend Manually
If auto-sync doesn't work:
1. In Render Dashboard, click **"+ New"** → **"Web Service"**
2. Connect to **thekishandev/ResearchPilot**
3. Configure:
   - **Name**: `researchpilot-frontend`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./frontend/Dockerfile`
   - **Docker Context**: `.` (root directory)
4. Add environment variable:
   - `VITE_API_URL` = `https://researchpilot-backend.onrender.com`
   - (Replace with your actual backend URL)
5. Click **"Create Web Service"**

## 📍 After Deployment:

You'll have TWO URLs:
- **Backend API**: `https://researchpilot-backend.onrender.com`
- **Frontend App**: `https://researchpilot-frontend.onrender.com`

## ⚡ Important Notes:

1. **Update Backend URL**: Once your backend is live, copy its actual URL and update `VITE_API_URL` in frontend environment variables

2. **CORS Settings**: Make sure your backend allows the frontend URL in CORS settings (should be automatic)

3. **First Load**: Free tier services sleep after 15 min inactivity - first load may take 30-60 seconds

## 🧪 Test Your Frontend:

Once deployed, open: `https://researchpilot-frontend.onrender.com`

You should see your ResearchPilot interface! 🎉

---

## Alternative: Deploy Frontend to Vercel (Faster & Better for Static Sites)

If Render frontend is slow, deploy to Vercel instead:

```bash
cd frontend
npm install -g vercel
vercel --prod
```

When prompted:
- Set `VITE_API_URL` to your Render backend URL
- Vercel is optimized for frontend and never sleeps!

