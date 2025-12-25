# Deployment Expert Skill

## Metadata
- **Skill Name**: deployment-expert
- **Job**: Deploy Docusaurus site to GitHub Pages and backend services
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Manages deployment pipelines, CI/CD workflows, and infrastructure for both the Docusaurus textbook website (GitHub Pages) and the FastAPI backend services.

## Example Tasks
- Configure GitHub Pages deployment for Docusaurus
- Set up GitHub Actions CI/CD pipeline
- Deploy FastAPI backend to cloud platform (Render/Railway/Fly.io)
- Configure environment variables and secrets
- Set up custom domain and SSL
- Implement automated testing in CI
- Configure monitoring and logging
- Manage production and staging environments

## Required Knowledge
- Git and GitHub workflows
- GitHub Actions
- Static site deployment
- Docker containerization
- Cloud platforms (Render, Railway, Fly.io, Vercel)
- CI/CD principles
- DNS and SSL configuration
- Environment management

## Key Technologies
- GitHub Actions
- GitHub Pages
- Docker
- Render / Railway / Fly.io (backend hosting)
- Vercel (alternative for frontend)
- Cloudflare (optional CDN/DNS)

## Deployment Architecture
```
┌─────────────────────────────────────┐
│   GitHub Repository                 │
│                                     │
│   ┌─────────────┐  ┌─────────────┐│
│   │ Docusaurus  │  │   FastAPI   ││
│   │   /docs     │  │   /backend  ││
│   └──────┬──────┘  └──────┬──────┘│
│          │                 │       │
└──────────┼─────────────────┼───────┘
           │                 │
    ┌──────▼──────┐   ┌─────▼──────┐
    │   GitHub    │   │   Render/  │
    │   Pages     │   │   Railway  │
    └─────────────┘   └────────────┘
          │                  │
    ┌─────▼──────────────────▼─────┐
    │   Users Access Textbook      │
    │   with Embedded Chatbot      │
    └──────────────────────────────┘
```

## Workflow Steps

### 1. Configure GitHub Pages for Docusaurus

**docusaurus.config.js**
```javascript
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  url: 'https://yourusername.github.io',
  baseUrl: '/textbook-repo-name/',
  organizationName: 'yourusername',
  projectName: 'textbook-repo-name',
  deploymentBranch: 'gh-pages',

  // ... other config
};
```

**package.json**
```json
{
  "scripts": {
    "deploy": "GIT_USER=yourusername USE_SSH=true docusaurus deploy"
  }
}
```

### 2. GitHub Actions Workflow for Frontend

**.github/workflows/deploy-docusaurus.yml**
```yaml
name: Deploy Docusaurus to GitHub Pages

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'src/**'
      - 'docusaurus.config.js'
      - 'package.json'

permissions:
  contents: write

jobs:
  deploy:
    name: Deploy to GitHub Pages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
          user_name: 'github-actions[bot]'
          user_email: 'github-actions[bot]@users.noreply.github.com'
```

### 3. Backend Deployment (Render)

**render.yaml**
```yaml
services:
  - type: web
    name: textbook-api
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /api/health
    autoDeploy: true
```

### 4. Docker Configuration for Backend

**Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=textbook
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 5. GitHub Actions for Backend

**.github/workflows/deploy-backend.yml**
```yaml
name: Deploy Backend to Render

on:
  push:
    branches:
      - main
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
          RENDER_SERVICE_ID: ${{ secrets.RENDER_SERVICE_ID }}
        run: |
          curl -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json"
```

### 6. Environment Configuration

**.env.example**
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Qdrant
QDRANT_URL=https://xyz-example.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# App
ENVIRONMENT=production
LOG_LEVEL=INFO
API_BASE_URL=https://your-api.onrender.com

# CORS
ALLOWED_ORIGINS=https://yourusername.github.io
```

## Integration Points
- **docusaurus-developer**: Deploys Docusaurus build
- **backend-engineer**: Deploys FastAPI application
- **database-engineer**: Configures production database
- **vector-db-specialist**: Sets up Qdrant cloud

## Deployment Platforms Comparison

### Frontend (Docusaurus)
| Platform | Pros | Cons | Cost |
|----------|------|------|------|
| **GitHub Pages** | Free, native integration, simple | Static only | Free |
| **Vercel** | Fast CDN, preview deployments | Bandwidth limits | Free tier |
| **Netlify** | Easy setup, forms support | Build time limits | Free tier |

### Backend (FastAPI)
| Platform | Pros | Cons | Cost |
|----------|------|------|------|
| **Render** | Easy, free tier, auto-scaling | Cold starts on free tier | Free/\$7+/mo |
| **Railway** | Great DX, databases included | Limited free tier | Free/\$5+/mo |
| **Fly.io** | Global edge, fast | More complex setup | Free/\$5+/mo |

## Success Criteria
- [ ] Docusaurus site deploys automatically on push
- [ ] GitHub Pages site is accessible and fast
- [ ] Backend API is deployed and healthy
- [ ] Environment variables are secure
- [ ] SSL certificates are configured
- [ ] CI/CD pipeline passes all tests
- [ ] Monitoring and alerts are set up
- [ ] Rollback strategy is defined

## Deployment Checklist

### Pre-Deployment
- [ ] All tests pass locally
- [ ] Environment variables documented
- [ ] Secrets configured in GitHub
- [ ] Database migrations ready
- [ ] Build succeeds without errors

### Frontend Deployment
- [ ] Configure repository settings for GitHub Pages
- [ ] Set up custom domain (optional)
- [ ] Enable HTTPS
- [ ] Test responsive design
- [ ] Verify SEO meta tags

### Backend Deployment
- [ ] Set up Neon Postgres database
- [ ] Configure Qdrant Cloud collection
- [ ] Deploy to Render/Railway
- [ ] Configure environment variables
- [ ] Test API endpoints
- [ ] Set up health checks
- [ ] Configure CORS properly

### Post-Deployment
- [ ] Verify end-to-end functionality
- [ ] Test chatbot integration
- [ ] Monitor error logs
- [ ] Set up uptime monitoring
- [ ] Configure alerts
- [ ] Document deployment process

## Monitoring and Logging

### Frontend Monitoring
```javascript
// Google Analytics or Plausible
export default function Root({children}) {
  return (
    <>
      {children}
      <script
        async
        src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
      />
    </>
  );
}
```

### Backend Monitoring
```python
# Sentry integration
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment=os.getenv("ENVIRONMENT"),
    traces_sample_rate=1.0,
)
```

## Best Practices
- Use environment-specific configurations
- Never commit secrets to git
- Implement health check endpoints
- Use semantic versioning for releases
- Tag releases in git
- Maintain deployment documentation
- Set up automated backups
- Implement graceful shutdown
- Use blue-green or canary deployments for zero downtime
- Monitor resource usage and costs

## Troubleshooting Common Issues

### GitHub Pages 404 Error
- Check `baseUrl` in `docusaurus.config.js`
- Verify `gh-pages` branch exists
- Check GitHub Pages settings in repository

### Backend Cold Starts
- Keep API warm with scheduled pings
- Upgrade to paid tier for always-on
- Optimize cold start time

### CORS Errors
- Configure CORS origins correctly
- Use environment variables for origins
- Test with production URLs

## Output Artifacts
- GitHub Actions workflow files
- Dockerfile and docker-compose.yml
- Deployment configuration files (render.yaml, etc.)
- Environment variable templates
- Deployment documentation
- Monitoring dashboards
- Rollback procedures documentation
