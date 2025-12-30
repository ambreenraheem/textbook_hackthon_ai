# Vercel Deployment Guide

Complete guide for deploying the Physical AI Textbook Platform to Vercel (both frontend and backend).

## 🚀 Why Vercel?

Vercel is perfect for this project because:
- ✅ **Super easy GitHub sign-up** (one-click OAuth)
- ✅ **Generous free tier** (100GB bandwidth/month, unlimited deployments)
- ✅ **No credit card needed** for free tier
- ✅ **Instant deployments** (~30 seconds)
- ✅ **Auto-deploys from GitHub**
- ✅ **Can host both frontend AND backend**

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ GitHub account with your code pushed
- ✅ OpenAI API key
- ✅ Qdrant Cloud account (URL + API key)
- ✅ Neon Postgres database (connection string)

## 🎯 Deployment Strategy

We'll deploy in this order:
1. **Backend** to Vercel (serverless functions)
2. **Frontend** to Vercel (static site)
3. Connect them together

---

## PART 1: Deploy Backend to Vercel

### Step 1: Create Vercel Account

1. Go to https://vercel.com/
2. Click **"Sign Up"** (top right)
3. Click **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub repositories
5. ✅ You're logged in! (No email verification needed)

### Step 2: Import Backend Project

1. From Vercel dashboard, click **"Add New..."** → **"Project"**
2. You'll see: **"Import Git Repository"**
3. Find: `ambreenraheem/textbook_hackthon_ai`
4. Click **"Import"**

### Step 3: Configure Backend Deployment

Vercel will show configuration screen:

**Framework Preset**: Select **"Other"**

**Root Directory**:
- Click **"Edit"**
- Enter: `backend`
- Click **"Continue"**

**Build Settings**:
- Build Command: (leave empty)
- Output Directory: (leave empty)
- Install Command: `pip install -r requirements.txt`

### Step 4: Add Environment Variables

Click **"Environment Variables"** dropdown and add:

```bash
OPENAI_API_KEY=sk-proj-your-key-here
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
DATABASE_URL=postgresql://user:pass@host/db
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

**Important**:
- Add each variable one by one
- For now, use `*` for `CORS_ORIGINS` (we'll update after frontend deployment)
- Click **"Add"** after each variable

### Step 5: Deploy Backend!

1. Click **"Deploy"** button
2. Vercel will:
   - Install dependencies (~2 minutes)
   - Build the project
   - Deploy as serverless functions
3. Wait for: ✅ **"Congratulations!"** message

### Step 6: Get Backend URL

After deployment completes:

1. Vercel shows your deployment URL
2. It looks like: `https://textbook-hackthon-ai-backend.vercel.app`
3. **Copy this URL** - you'll need it!

### Step 7: Test Backend

Open browser and visit:
```
https://your-backend-url.vercel.app/api/health
```

You should see JSON response:
```json
{
  "status": "healthy",
  "services": {
    "postgres": {"status": "healthy"},
    "qdrant": {"status": "healthy"},
    "openai": {"status": "healthy"}
  }
}
```

⚠️ **Note**: First request may be slow (cold start). This is normal for serverless.

---

## PART 2: Deploy Frontend to Vercel

### Step 1: Create New Project for Frontend

1. Back in Vercel dashboard, click **"Add New..."** → **"Project"**
2. Find: `ambreenraheem/textbook_hackthon_ai` (same repo)
3. Click **"Import"** again

### Step 2: Configure Frontend Deployment

**Framework Preset**: Vercel should auto-detect **"Docusaurus"** ✅

**Root Directory**:
- Click **"Edit"**
- Enter: `frontend`
- Click **"Continue"**

**Build Settings** (auto-filled by Vercel):
- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm install`

### Step 3: Add Environment Variables (Frontend)

Add this variable:

```bash
REACT_APP_BACKEND_URL=https://your-backend-url.vercel.app
```

Replace with your actual backend URL from Part 1, Step 6.

### Step 4: Deploy Frontend!

1. Click **"Deploy"**
2. Vercel will:
   - Install dependencies (~1 minute)
   - Build Docusaurus site (~2 minutes)
   - Deploy to edge network
3. Wait for: ✅ **"Congratulations!"**

### Step 5: Get Frontend URL

After deployment:

1. Vercel shows your URL: `https://textbook-hackthon-ai-frontend.vercel.app`
2. Click the URL to visit your live site!
3. ✅ **Your textbook is now live!**

---

## PART 3: Connect Frontend & Backend

### Step 1: Update Backend CORS

Now that frontend is deployed, update backend CORS settings:

1. Go to Vercel dashboard
2. Click on your **backend** project
3. Go to **"Settings"** → **"Environment Variables"**
4. Find `CORS_ORIGINS`
5. Click **"Edit"**
6. Change value to your frontend URL:
   ```
   https://your-frontend-url.vercel.app
   ```
7. Click **"Save"**

### Step 2: Redeploy Backend

1. Go to **"Deployments"** tab
2. Click **"..."** on latest deployment
3. Click **"Redeploy"**
4. Wait for redeployment (~1 minute)

### Step 3: Update Frontend Backend URL (if needed)

If you didn't set `REACT_APP_BACKEND_URL` in Part 2:

**Option 1: Via Vercel Dashboard**
1. Frontend project → Settings → Environment Variables
2. Add: `REACT_APP_BACKEND_URL=https://your-backend-url.vercel.app`
3. Redeploy

**Option 2: Via Code**
1. Edit `frontend/src/services/api.ts`:
   ```typescript
   const BACKEND_URL = 'https://your-backend-url.vercel.app';
   ```
2. Commit and push:
   ```bash
   git add frontend/src/services/api.ts
   git commit -m "config: connect to Vercel backend"
   git push origin main
   ```
3. Vercel auto-redeploys

---

## PART 4: Ingest Content to Qdrant

Now populate the vector database with textbook content:

### Option 1: Run Locally (Recommended)

```bash
cd backend
python -m src.utils.qdrant_setup  # Create collection
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
```

This takes ~10-15 minutes and costs ~$0.50 in OpenAI API usage.

### Option 2: Via Vercel CLI

Install Vercel CLI:
```bash
npm i -g vercel
vercel login
cd backend
vercel env pull .env  # Download env vars
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
```

---

## ✅ Verification Checklist

After deployment, verify everything works:

### 1. Backend Health Check
```
https://your-backend-url.vercel.app/api/health
```
Should return: `{"status": "healthy"}`

### 2. Frontend Loads
```
https://your-frontend-url.vercel.app/
```
Should show: Homepage with chapters

### 3. Chatbot Works
1. Open chatbot widget (bottom right)
2. Ask: "What is Physical AI?"
3. Should get streaming response with citations

### 4. Text Selection Works
1. Highlight any text on a chapter
2. Click "💬 Ask about this"
3. Chatbot opens with context

---

## 🔄 Auto-Deployment

Vercel automatically redeploys when you push to GitHub:

**For Backend**:
```bash
cd backend
# Make changes
git add .
git commit -m "update: backend changes"
git push origin main
```
Vercel detects changes in `backend/` and redeploys backend

**For Frontend**:
```bash
cd frontend
# Make changes
git add .
git commit -m "update: frontend changes"
git push origin main
```
Vercel detects changes in `frontend/` and redeploys frontend

---

## 💰 Vercel Free Tier Limits

**What's included for FREE**:
- ✅ 100GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Automatic SSL certificates
- ✅ Edge network (global CDN)
- ✅ Serverless functions (100GB-hours)

**Limits**:
- ⚠️ Serverless functions: 10-second execution timeout
- ⚠️ Cold starts: First request slow after inactivity
- ⚠️ 4,500 build minutes/month

**For this project**: Free tier is more than enough!

---

## 🐛 Troubleshooting

### Issue: Backend returns 500 error

**Check logs**:
1. Backend project → **"Deployments"** tab
2. Click latest deployment
3. Click **"Functions"** → View logs
4. Look for errors

**Common causes**:
- Missing environment variables
- Database connection failed
- Import errors

**Solution**: Check all environment variables are set correctly

### Issue: Frontend shows blank page

**Check build logs**:
1. Frontend project → **"Deployments"** tab
2. Click latest deployment → **"Building"**
3. Look for build errors

**Common causes**:
- Docusaurus build failed
- Missing dependencies

**Solution**: Check build command is `npm run build`

### Issue: Chatbot doesn't respond

**Symptoms**: Chatbot opens but no response

**Check**:
1. Backend health: `/api/health`
2. Browser console for errors (F12)
3. CORS errors?

**Solutions**:
1. Verify `CORS_ORIGINS` includes frontend URL
2. Verify `REACT_APP_BACKEND_URL` points to backend
3. Check Qdrant has content (run ingestion)

### Issue: "This Serverless Function has crashed"

**Cause**: Function timeout (>10 seconds)

**Common on**:
- First request (cold start)
- Complex RAG queries

**Solutions**:
1. Refresh page and try again
2. For free tier, this is expected
3. Upgrade to Pro plan ($20/month) for longer timeout

---

## 📊 Monitoring

Vercel provides excellent monitoring:

**Access logs**:
1. Project → **"Deployments"**
2. Click deployment → **"Functions"**
3. Click function → **"Logs"**

**View analytics**:
1. Project → **"Analytics"**
2. See: Requests, bandwidth, edge network stats

**Real-time logs**:
```bash
vercel logs <deployment-url> --follow
```

---

## 🔗 Custom Domains (Optional)

Want a custom domain like `textbook.yourdomain.com`?

### For Frontend:
1. Frontend project → **"Settings"** → **"Domains"**
2. Click **"Add"**
3. Enter your domain: `textbook.yourdomain.com`
4. Follow DNS configuration instructions
5. Vercel auto-provisions SSL certificate

### For Backend:
1. Backend project → **"Settings"** → **"Domains"**
2. Add: `api.textbook.yourdomain.com`
3. Update `CORS_ORIGINS` in environment variables
4. Update frontend `REACT_APP_BACKEND_URL`

---

## 🎯 Next Steps

After successful deployment:

1. ✅ **Test all features**: Chatbot, text selection, search
2. ✅ **Share your site**: Send the URL to others!
3. ✅ **Add content**: Write more chapters
4. ✅ **Monitor usage**: Check Vercel analytics
5. ✅ **Optimize**: Review performance insights

---

## 🔗 Quick Reference

**Vercel Dashboard**: https://vercel.com/dashboard

**Your Deployments**:
- Backend: `https://textbook-hackthon-ai-backend.vercel.app`
- Frontend: `https://textbook-hackthon-ai-frontend.vercel.app`

**Useful Commands**:
```bash
# Deploy from CLI
vercel

# View logs
vercel logs

# Pull env vars
vercel env pull

# Production deployment
vercel --prod
```

---

## 💡 Pro Tips

1. **Serverless Optimization**:
   - Keep functions small and focused
   - Cache database connections
   - Use edge caching for static responses

2. **Cost Optimization**:
   - Free tier is sufficient for development
   - Monitor bandwidth usage in analytics
   - Upgrade only if needed

3. **Performance**:
   - Vercel edge network is very fast
   - First request slow (cold start) is normal
   - Subsequent requests are instant

---

**Congratulations! 🎉** Your entire platform is now live on Vercel!

**Frontend**: `https://your-frontend-url.vercel.app`
**Backend**: `https://your-backend-url.vercel.app/api/health`

**Next**: Follow `docs/rag-ingestion-guide.md` to populate Qdrant with all 32 chapters!
