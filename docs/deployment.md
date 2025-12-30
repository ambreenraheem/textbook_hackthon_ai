# Production Deployment Guide

Complete guide for deploying the Physical AI Textbook Platform to production with GitHub Pages (frontend) and Render (backend).

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account with repository access
- ✅ All code committed to `main` branch
- ✅ Environment variables (.env file) configured locally

You will need to create **FREE accounts** for:
- **GitHub Pages** (for frontend hosting)
- **Render** (for backend API hosting)
- **Qdrant Cloud** (vector database)
- **Neon** (PostgreSQL database)
- **OpenAI** (API access)

---

## 🎯 Deployment Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend (GitHub Pages)          Backend (Render)          │
│  ├─ Static Docusaurus Site        ├─ FastAPI Application   │
│  ├─ https://username.github.io    ├─ https://your-app.render.com  │
│  └─ Auto-deploy on push           └─ Auto-deploy on push   │
│                                                              │
│  External Services                                          │
│  ├─ Qdrant Cloud (Vector DB)                               │
│  ├─ Neon (PostgreSQL)                                       │
│  └─ OpenAI (GPT-4 + Embeddings)                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## PART 1: Set Up External Services

### Step 1.1: Qdrant Cloud (Vector Database)

**Purpose**: Store and search textbook embeddings for RAG

1. Go to https://cloud.qdrant.io/
2. Click **"Sign Up"** (free tier available)
3. Create account (email or GitHub)
4. Create new cluster:
   - Click **"+ New Cluster"**
   - Name: `textbook-vectors`
   - Region: Choose closest to you (e.g., `us-east`)
   - Tier: **Free** (1GB storage)
5. Wait for cluster to provision (~2 minutes)
6. **Save credentials**:
   - **URL**: `https://your-cluster.qdrant.io`
   - **API Key**: Click "API Keys" → "Create API Key" → Copy

### Step 1.2: Neon (PostgreSQL Database)

**Purpose**: Store conversation history

1. Go to https://neon.tech/
2. Click **"Sign Up"** (free tier available)
3. Create account (email or GitHub)
4. Create new project:
   - Name: `textbook-platform`
   - Region: Choose closest to you
   - PostgreSQL version: 16 (default)
5. **Save connection string**:
   - Go to "Connection Details"
   - Copy **"Connection string"** (starts with `postgresql://...`)
   - Example: `postgresql://user:pass@ep-xxxx-xxxx.us-east-2.aws.neon.tech/neondb`

### Step 1.3: OpenAI API

**Purpose**: GPT-4 for chat responses + embeddings

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Go to **"API Keys"** (https://platform.openai.com/api-keys)
4. Click **"+ Create new secret key"**
   - Name: `textbook-platform`
   - Permissions: All (default)
5. **Copy and save** the API key immediately (starts with `sk-...`)
6. **Add billing**: Go to "Settings" → "Billing" → Add payment method
   - Recommended: Set spending limit ($10/month is usually sufficient for development)

---

## PART 2: Deploy Backend to Render

### Step 2.1: Create Render Account

1. Go to https://render.com/
2. Click **"Get Started"**
3. Sign up with **GitHub** (recommended for auto-deploy)
4. Authorize Render to access your GitHub repositories

### Step 2.2: Create Web Service

1. From Render Dashboard, click **"+ New"** → **"Web Service"**
2. Connect repository:
   - Click **"Connect a repository"**
   - Find: `your-username/textbook_hackthon_ai`
   - Click **"Connect"**
3. Configure service:

| Field | Value |
|-------|-------|
| **Name** | `physical-ai-backend` (or your choice) |
| **Region** | Choose closest (e.g., Oregon USA) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Instance Type** | **Free** |

4. Click **"Create Web Service"**

### Step 2.3: Configure Environment Variables

In Render dashboard, go to **"Environment"** tab:

Click **"Add Environment Variable"** for each:

| Key | Value | Example |
|-----|-------|---------|
| `OPENAI_API_KEY` | Your OpenAI key | `sk-proj-abc123...` |
| `QDRANT_URL` | Qdrant cluster URL | `https://xxx.qdrant.io` |
| `QDRANT_API_KEY` | Qdrant API key | `abc123...` |
| `DATABASE_URL` | Neon connection string | `postgresql://user:pass@...` |
| `ENVIRONMENT` | `production` | `production` |
| `CORS_ORIGINS` | Frontend URL (see Part 3) | `https://username.github.io` |

**Important**: After adding all variables, click **"Save Changes"**

### Step 2.4: Deploy & Verify

1. Render will automatically start deploying
2. Monitor logs in **"Logs"** tab
3. Wait for: **"Your service is live 🎉"** (5-10 minutes)
4. **Copy your backend URL**: `https://physical-ai-backend.onrender.com`
5. **Test health endpoint**:
   ```bash
   curl https://your-app.onrender.com/api/health
   ```
   Should return JSON with `"status": "healthy"`

### Step 2.5: Configure Health Checks (T075)

1. In Render dashboard, go to **"Settings"** tab
2. Scroll to **"Health Check Path"**
3. Enter: `/api/health`
4. Click **"Save Changes"**

Render will now:
- Ping `/api/health` every 5 minutes
- Alert you if service is down
- Auto-restart if unhealthy

---

## PART 3: Deploy Frontend to GitHub Pages

### Step 3.1: Enable GitHub Pages

1. Go to your GitHub repository: `https://github.com/your-username/textbook_hackthon_ai`
2. Click **"Settings"** (top tabs)
3. Scroll to **"Pages"** (left sidebar)
4. Under **"Source"**:
   - Select **"GitHub Actions"** (not "Deploy from a branch")
5. Save (GitHub will show confirmation)

### Step 3.2: Configure Frontend for Backend URL

1. Edit `frontend/src/services/api.ts`:
   ```typescript
   const BACKEND_URL = 'https://your-app.onrender.com'; // Replace with your Render URL
   ```

2. Commit and push:
   ```bash
   git add frontend/src/services/api.ts
   git commit -m "config: update backend URL for production"
   git push origin main
   ```

### Step 3.3: Trigger Deployment

**Option A: Automatic (Recommended)**
- GitHub Actions workflow (`.github/workflows/frontend-deploy.yml`) triggers automatically on push to `main`

**Option B: Manual Trigger**
1. Go to repository → **"Actions"** tab
2. Click **"Deploy Frontend to GitHub Pages"**
3. Click **"Run workflow"** → **"Run workflow"**

### Step 3.4: Monitor Deployment

1. Go to **"Actions"** tab
2. Click on the running workflow
3. Watch build process (~2-3 minutes)
4. When complete, you'll see: ✅ **"Deploy to GitHub Pages"**

### Step 3.5: Access Your Site

Your site will be live at:
```
https://your-username.github.io/textbook_hackthon_ai/
```

**Note**: If using custom domain:
- Go to Settings → Pages → Custom domain
- Enter your domain (e.g., `textbook.yourdomain.com`)
- Configure DNS records as instructed

---

## PART 4: Update Backend CORS

Now that frontend is deployed, update backend CORS settings:

1. Go to Render dashboard → Your service
2. **"Environment"** tab
3. Find `CORS_ORIGINS` variable
4. Update value to your GitHub Pages URL:
   ```
   https://your-username.github.io
   ```
5. Click **"Save Changes"**
6. Render will auto-redeploy (~2 minutes)

---

## PART 5: Initialize Vector Database

Run ingestion pipeline to populate Qdrant with textbook content.

### Option A: From Local Machine

```bash
cd backend
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
```

### Option B: From Render Shell

1. Render dashboard → Your service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
   ```

This will:
- Parse all 32 chapters + 5 projects
- Generate embeddings (OpenAI)
- Upload to Qdrant
- Takes ~10-15 minutes

---

## PART 6: Verification & Testing

### 6.1 Backend Health Check

```bash
curl https://your-app.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "postgres": {"status": "healthy"},
    "qdrant": {"status": "healthy", "collections": ["textbook_chunks"]},
    "openai": {"status": "healthy"}
  }
}
```

### 6.2 Frontend Access

1. Visit: `https://your-username.github.io/textbook_hackthon_ai/`
2. Verify:
   - ✅ Site loads
   - ✅ Chapters are accessible
   - ✅ Search works
   - ✅ Dark mode toggle works

### 6.3 Chatbot Integration

1. Open chatbot widget (bottom right)
2. Ask question: "What is Physical AI?"
3. Verify:
   - ✅ Streaming response appears
   - ✅ Citations link to chapters
   - ✅ No CORS errors in console

### 6.4 Text Selection Q&A

1. Highlight any text on a chapter page
2. Click **"💬 Ask about this"** popup
3. Verify:
   - ✅ Chatbot opens
   - ✅ Question includes selected text
   - ✅ Response is contextual

---

## 🔧 Troubleshooting

### Issue: Backend Health Check Fails

**Symptoms**: `/api/health` returns 503 or times out

**Solutions**:
1. Check Render logs for errors
2. Verify all environment variables are set
3. Test database connections:
   - Qdrant: Can you access Qdrant dashboard?
   - Neon: Test connection string locally
4. Check Render service status (free tier sleeps after 15 min inactivity)

### Issue: Frontend Shows CORS Error

**Symptoms**: Console shows: `Access to fetch...has been blocked by CORS policy`

**Solutions**:
1. Verify `CORS_ORIGINS` in Render includes your GitHub Pages URL
2. Ensure URL format matches exactly (no trailing slash)
3. Clear browser cache and hard reload

### Issue: Chatbot Doesn't Respond

**Symptoms**: Chatbot opens but no response to questions

**Solutions**:
1. Check backend is running: `/api/health`
2. Verify Qdrant has content: Check collection in Qdrant dashboard
3. Run ingestion pipeline (Part 5)
4. Check OpenAI API key is valid
5. Inspect network tab for failed requests

### Issue: GitHub Pages 404

**Symptoms**: Site shows "404 - Page not found"

**Solutions**:
1. Verify Actions workflow completed successfully
2. Check Settings → Pages shows correct source
3. Ensure `docusaurus.config.js` has correct `baseUrl`:
   ```javascript
   baseUrl: '/textbook_hackthon_ai/', // Repository name
   ```
4. Wait 5 minutes (DNS propagation)

### Issue: Render Service Keeps Sleeping (Free Tier)

**Symptoms**: First request takes 30+ seconds

**Solutions**:
- Expected behavior on free tier (sleeps after 15 min inactivity)
- Upgrade to paid tier ($7/month) for always-on
- Use external uptime monitor to ping every 10 minutes (e.g., UptimeRobot)

---

## 📊 Monitoring

### Render Monitoring

- **Logs**: Render Dashboard → Logs tab (real-time)
- **Metrics**: View CPU, memory, bandwidth usage
- **Alerts**: Configure in Settings → Notifications

### GitHub Pages Monitoring

- **Build Status**: Repository → Actions tab
- **Traffic**: Repository → Insights → Traffic

### External Monitoring (Optional)

1. **UptimeRobot** (https://uptimerobot.com/) - Free uptime monitoring
2. **Better Uptime** (https://betteruptime.com/) - Status pages
3. **Sentry** (https://sentry.io/) - Error tracking

---

## 🔄 Continuous Deployment

### How Auto-Deployment Works

**Frontend**:
1. Push code to `main` branch
2. GitHub Actions detects changes in `frontend/`
3. Workflow builds Docusaurus site
4. Deploys to GitHub Pages automatically

**Backend**:
1. Push code to `main` branch
2. Render detects changes in `backend/`
3. Builds Docker image
4. Deploys new version automatically (~5 min)

### Manual Deployment

**Frontend**:
```bash
cd frontend
npm run build
npm run deploy
```

**Backend**:
- Render Dashboard → Manual Deploy button

---

## 💰 Cost Breakdown

| Service | Free Tier | Paid Tier | Recommendation |
|---------|-----------|-----------|----------------|
| **GitHub Pages** | Unlimited | N/A | Free (sufficient) |
| **Render** | 750 hrs/month (sleeps) | $7/month (always-on) | Free to start |
| **Qdrant Cloud** | 1GB storage | $25/month (10GB) | Free (sufficient) |
| **Neon** | 3GB storage | $19/month | Free (sufficient) |
| **OpenAI** | Pay-as-you-go | N/A | ~$5-10/month |

**Total Monthly Cost**: $5-10 (OpenAI only) for development
**Total Monthly Cost**: $12-20 (with Render paid) for production

---

## 🎯 Next Steps

After successful deployment:

1. ✅ Run Lighthouse audit (see below)
2. ✅ Set up custom domain (optional)
3. ✅ Configure Google Analytics (optional)
4. ✅ Add deployment status badges to README

### Run Lighthouse Audit

```bash
npm install -g lighthouse

lighthouse https://your-username.github.io/textbook_hackthon_ai/ \
  --output html \
  --output-path ./lighthouse-report.html

open lighthouse-report.html
```

Target scores:
- **Performance**: ≥90
- **Accessibility**: ≥90
- **Best Practices**: ≥90
- **SEO**: ≥90

---

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review Render logs for backend errors
3. Check GitHub Actions logs for frontend build errors
4. Search existing issues: https://github.com/your-repo/issues
5. Create new issue with:
   - Error message
   - Steps to reproduce
   - Logs/screenshots

---

## 🔗 Quick Links

- **Frontend**: https://your-username.github.io/textbook_hackthon_ai/
- **Backend**: https://your-app.onrender.com/
- **API Docs**: https://your-app.onrender.com/docs
- **Render Dashboard**: https://dashboard.render.com/
- **GitHub Actions**: https://github.com/your-username/textbook_hackthon_ai/actions
- **Qdrant Dashboard**: https://cloud.qdrant.io/
- **Neon Dashboard**: https://console.neon.tech/

---

**Congratulations! 🎉** Your Physical AI Textbook Platform is now live in production!
