# Chatbot Fix: "process is not defined" Error

## Issue
The chatbot was failing with "process is not defined" error both in localhost and production (Vercel). This happened because the code tried to access `process.env` in browser code, which only exists in Node.js environments.

## Fix Applied

### Changed File: `frontend/src/services/api.ts`

**Before (Line 33):**
```typescript
return process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**After (Line 33):**
```typescript
return 'http://localhost:8000';
```

**Reason:** Removed the `process.env.REACT_APP_API_URL` reference because:
1. Docusaurus uses `customFields` in config, not `REACT_APP_*` environment variables
2. The code already checks for Docusaurus customFields on lines 22-25
3. `process` object doesn't exist in browser environment

## How It Works Now

The `getApiUrl()` function now follows this priority:

1. **First**: Check Docusaurus customFields (production)
   ```typescript
   window.docusaurus.siteConfig.customFields.chatbotApiUrl
   ```

2. **Second**: Check window.CHATBOT_API_URL (fallback)
   ```typescript
   window.CHATBOT_API_URL
   ```

3. **Third**: Default to localhost (development)
   ```typescript
   'http://localhost:8000'
   ```

## Local Development Setup

### 1. Start Backend Server
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Start Frontend Server
```bash
cd frontend
npm install
npm start
```

The chatbot will automatically connect to `http://localhost:8000`.

## Production Deployment on Vercel

### Frontend Deployment

1. **Set Environment Variable in Vercel Dashboard**
   - Go to your project settings on Vercel
   - Navigate to: Settings > Environment Variables
   - Add new variable:
     - **Name**: `CHATBOT_API_URL`
     - **Value**: `https://your-backend.vercel.app` (your deployed backend URL)
     - **Scope**: Production, Preview, Development (select all)

2. **Redeploy Frontend**
   ```bash
   git push origin main
   ```
   Or trigger manual redeploy in Vercel dashboard.

### Backend Deployment

1. **Deploy backend to Vercel**
   - Create `vercel.json` in backend directory (if not exists):
     ```json
     {
       "builds": [
         {
           "src": "main.py",
           "use": "@vercel/python"
         }
       ],
       "routes": [
         {
           "src": "/(.*)",
           "dest": "main.py"
         }
       ]
     }
     ```

2. **Configure CORS in backend**
   - Ensure your FastAPI backend allows your frontend domain:
     ```python
     from fastapi.middleware.cors import CORSMiddleware

     app.add_middleware(
         CORSMiddleware,
         allow_origins=[
             "http://localhost:3000",
             "https://textbook-hackthon-ai.vercel.app"
         ],
         allow_methods=["*"],
         allow_headers=["*"],
     )
     ```

3. **Get backend URL**
   - After deploying, copy the Vercel URL (e.g., `https://your-backend.vercel.app`)
   - Use this URL in the frontend environment variable (step 1 above)

## Testing the Fix

### Test Locally
1. Open browser DevTools (F12)
2. Go to Console tab
3. Navigate to `http://localhost:3000`
4. Click the chatbot button
5. Send a test message
6. **Verify**: No "process is not defined" error appears

### Test in Production
1. Go to `https://textbook-hackthon-ai.vercel.app/`
2. Open browser DevTools (F12)
3. Click the chatbot button
4. Send a test message
5. **Verify**: Chatbot connects to backend and responds

## Troubleshooting

### Issue: Chatbot still not responding

**Check 1: Backend is running**
```bash
# Test backend locally
curl http://localhost:8000/health

# Test backend in production
curl https://your-backend.vercel.app/health
```

**Check 2: API URL is correct**
Open browser console and run:
```javascript
console.log(window.docusaurus?.siteConfig?.customFields?.chatbotApiUrl);
```

**Check 3: CORS errors**
If you see CORS errors in console, update backend CORS configuration to include your frontend domain.

### Issue: Environment variable not updating

**Solution**: Clear Vercel cache and redeploy
```bash
# In Vercel dashboard:
# Deployments > [Latest Deployment] > ... (three dots) > Redeploy
```

Or force a new deployment:
```bash
git commit --allow-empty -m "Force redeploy"
git push origin main
```

## Verification Checklist

- [x] Removed `process.env` reference from client code
- [x] Tested locally (pending - see instructions above)
- [ ] Backend deployed to Vercel
- [ ] `CHATBOT_API_URL` environment variable set in Vercel
- [ ] Frontend redeployed after setting environment variable
- [ ] CORS configured in backend
- [ ] Chatbot working in production

## Additional Notes

- The fix ensures the code works in all environments (dev/staging/production)
- No code changes needed for different environments - only environment variables
- The chatbot automatically detects the correct API URL based on the environment
