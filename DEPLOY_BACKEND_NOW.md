# 🚀 Deploy Backend to Vercel - SIMPLE GUIDE

## ⚠️ Your Chatbot is NOT Working Because:
- Frontend is deployed ✅ (https://textbook-hackthon-ai-f1hj.vercel.app/)
- Backend is NOT deployed ❌ (trying to connect to localhost:8000)

## 📋 What You Need (Check These First!)

Before deploying, make sure you have:

1. ✅ **Vercel Account** - Already created (you deployed frontend)
2. ⚠️ **OpenAI API Key** - Do you have this?
3. ⚠️ **Qdrant Cloud Account** - Do you have this? (Free tier)
4. ⚠️ **Neon Postgres Database** - Do you have this? (Free tier)

**If you don't have these**, tell me and I'll help you create them!

---

## 🎯 OPTION 1: Quick Deploy (Recommended)

### Step 1: Go to Vercel Dashboard
Open: https://vercel.com/dashboard

### Step 2: Click "Add New..." → "Project"

### Step 3: Import Your Repository
- Find: `ambreenraheem/textbook_hackthon_ai`
- Click **"Import"**

### Step 4: Configure Project Settings

**IMPORTANT: Click "Configure Project" before deploying!**

1. **Framework Preset**: Select **"Other"**

2. **Root Directory**:
   - Click **"Edit"**
   - Type: `backend`
   - Click **"Continue"**

3. **Build Settings**:
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

4. **Environment Variables** - Click "Add" for EACH:

   **REQUIRED (Copy from your .env file):**
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-qdrant-key
   DATABASE_URL=postgresql://user:pass@host/db
   ```

   **ALSO ADD THESE:**
   ```
   ENVIRONMENT=production
   CORS_ORIGINS=https://textbook-hackthon-ai-f1hj.vercel.app
   ```

### Step 5: Deploy!
Click the big **"Deploy"** button

⏳ Wait 2-3 minutes...

---

## 🎯 OPTION 2: Tell Me What's Wrong

If you already tried and got an error, **copy the error message** and send it to me!

Common errors:
- ❌ "Build failed" → Missing environment variables
- ❌ "Dependencies error" → We already fixed this (openai version)
- ❌ "500 Internal Server Error" → Database connection issue

---

## ✅ After Backend Deploys Successfully

You'll get a URL like: `https://textbook-hackthon-ai-backend-abc123.vercel.app`

**Copy that URL** and tell me! I'll update your frontend to connect to it.

---

## 🆘 QUICK HELP

**Don't have API keys?** Tell me which one and I'll guide you:
1. OpenAI: https://platform.openai.com/api-keys
2. Qdrant: https://cloud.qdrant.io/
3. Neon: https://neon.tech/

**Deployment failing?** Send me:
- The error message from Vercel
- Screenshot if possible

**Not sure about .env file?** Show me the file (hide sensitive parts)

---

## 🎉 Success Checklist

After deployment:
- [ ] Backend deployed without errors
- [ ] Got backend URL from Vercel
- [ ] Told Claude the backend URL
- [ ] Frontend updated and redeployed
- [ ] Chatbot works! 🤖

---

**Ready? Let's do this! Tell me:**
1. Do you have all the API keys?
2. OR: What error are you getting?
3. OR: Do you need help creating the accounts?
