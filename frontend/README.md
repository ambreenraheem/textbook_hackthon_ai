# Frontend - Physical AI Textbook Platform

Docusaurus-powered interactive textbook website with integrated AI chatbot for contextual learning assistance.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Docusaurus Frontend                         │
├──────────────────────────────────────────────────────────────┤
│  📚 Textbook Content (32 Chapters + 5 Projects)              │
│  🤖 ChatbotWidget (RAG-powered, SSE streaming)               │
│  ✨ Text Selection Q&A (highlight → ask)                     │
│  🔍 Search (Local Search Plugin)                             │
│  🎨 Custom Theme (Dark/Light mode)                           │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Tech Stack

- **Framework**: Docusaurus 3.9.2
- **UI Library**: React 18.3.1
- **Language**: TypeScript 5.3.3
- **Styling**: CSS Modules + Custom CSS
- **Search**: @cmfcmf/docusaurus-search-local
- **Testing**: Playwright (E2E)

## 📋 Prerequisites

- Node.js 18.x or higher
- npm package manager

## 🛠️ Local Development Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

The site will open at http://localhost:3000

### 3. Development Features

- **Hot Reload**: Changes to docs instantly reflect
- **Live Chatbot**: Connect to local backend at http://localhost:8000
- **Fast Refresh**: React components update without full reload

## 📚 Content Authoring

### Creating New Chapters

1. Create file in appropriate part directory:
```bash
touch docs/part-0X-name/chXX-chapter-title.mdx
```

2. Add frontmatter:
```yaml
---
id: ch01-intro-physical-ai
title: Chapter 1 - Introduction to Physical AI
description: Explore the evolution from digital AI to physical embodied systems
sidebar_label: Ch 1. Intro to Physical AI
sidebar_position: 1
keywords: [physical AI, embodied AI, robotics]
difficulty: beginner
estimatedReadingTime: 15
---
```

3. Write content with MDX features:
```mdx
# Chapter Title

## Section

Regular markdown content...

### Code Blocks

\`\`\`python title="example.py" showLineNumbers
def robot_controller():
    print("Hello, Physical AI!")
\`\`\`

### Interactive Components

import VideoPlayer from '@site/src/components/VideoPlayer';

<VideoPlayer url="https://youtube.com/..." />
```

### Adding Projects

Projects go in `docs/part-10-projects/`:

```mdx
---
id: project-01-ros2-robot
title: Project 1 - Basic ROS 2 Robot
difficulty: beginner
estimatedDuration: 2-4 hours
prerequisites:
  - ch05-intro-ros2
  - ch06-ros2-concepts
---

# Project 1: Basic ROS 2 Robot

## Overview
...

## Learning Objectives
...

## Step-by-Step Instructions
...
```

### Sidebar Configuration

Edit `sidebars.js` to organize chapters:

```javascript
{
  type: 'category',
  label: 'Part I: Foundations',
  collapsed: false,
  items: [
    'part-01-foundations/ch01-intro-physical-ai',
    'part-01-foundations/ch02-humanoid-robotics',
    // ...
  ],
}
```

## 🎨 Customization

### Theme Configuration

Edit `docusaurus.config.js`:

```javascript
themeConfig: {
  colorMode: {
    defaultMode: 'light',
    disableSwitch: false,
    respectPrefersColorScheme: true,
  },
  navbar: {
    title: 'Physical AI Textbook',
    logo: {
      src: 'img/logo.svg',
    },
    items: [
      // Add custom navbar items
    ],
  },
}
```

### Custom CSS

Add styles in `src/css/custom.css`:

```css
:root {
  --ifm-color-primary: #2e8555;
  --ifm-code-font-size: 95%;
}

[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
}
```

### Adding Components

Create React component in `src/components/`:

```tsx
// src/components/MyComponent.tsx
import React from 'react';

export default function MyComponent({ title }) {
  return <div>{title}</div>;
}
```

Use in MDX files:

```mdx
import MyComponent from '@site/src/components/MyComponent';

<MyComponent title="Hello!" />
```

## 🤖 Chatbot Widget

The ChatbotWidget is integrated globally via `src/theme/Root.tsx`.

### Features
- Floating widget (minimizable)
- Streaming responses (SSE)
- Citation links to textbook pages
- Text selection Q&A
- Session persistence

### Configuration

Edit widget in `src/components/ChatbotWidget/index.tsx`:

```tsx
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
```

## 🧪 Testing

### E2E Tests (Playwright)

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run in headed mode
npm run test:headed

# Debug mode
npm run test:debug
```

### Test Structure

```
tests/
└── e2e/
    └── text-selection.spec.ts  # Text selection Q&A flow
```

### Writing Tests

```typescript
import { test, expect } from '@playwright/test';

test('should navigate to chapter', async ({ page }) => {
  await page.goto('/');
  await page.click('text=Chapter 1');
  await expect(page).toHaveURL(/ch01-intro-physical-ai/);
});
```

## 🏗️ Building for Production

### Build Static Site

```bash
npm run build
```

Output: `build/` directory (static HTML/CSS/JS)

### Serve Locally

```bash
npm run serve
```

Preview production build at http://localhost:3000

### Build Optimization

Docusaurus automatically:
- ✅ Minifies JavaScript/CSS
- ✅ Optimizes images
- ✅ Generates sitemaps
- ✅ Creates search index
- ✅ Code splitting

## 🚀 Deployment

### GitHub Pages (Automated)

Push to `main` branch triggers automatic deployment via GitHub Actions.

Workflow: `.github/workflows/frontend-deploy.yml`

**Manual deployment**:
```bash
GIT_USER=<your-username> npm run deploy
```

### Other Platforms

**Vercel**:
```bash
npx vercel --prod
```

**Netlify**:
```bash
npx netlify deploy --prod --dir=build
```

**Static Hosting**:
Upload `build/` directory to any static host (AWS S3, Azure Storage, etc.)

## 📁 Project Structure

```
frontend/
├── docs/                      # Textbook content (MDX)
│   ├── intro.md               # Homepage intro
│   ├── part-01-foundations/   # Part 1 chapters
│   ├── part-02-ros2/          # Part 2 chapters
│   ├── ...                    # Parts 3-9
│   └── part-10-projects/      # Hands-on projects
├── src/
│   ├── components/            # React components
│   │   ├── ChatbotWidget/     # AI chatbot
│   │   └── TextSelection/     # Text selection Q&A
│   ├── css/                   # Custom styles
│   ├── pages/                 # Custom pages
│   │   └── index.js           # Homepage
│   ├── theme/                 # Theme customization
│   │   └── Root.tsx           # Global wrapper
│   └── types/                 # TypeScript types
├── static/                    # Static assets
│   └── img/                   # Images/logos
├── tests/                     # E2E tests
│   └── e2e/
├── docusaurus.config.js       # Docusaurus configuration
├── sidebars.js                # Sidebar structure
├── playwright.config.ts       # Playwright config
├── package.json               # Dependencies
└── README.md                  # This file
```

## 🔧 Common Tasks

### Add New Part

1. Create directory: `mkdir docs/part-XX-name`
2. Add chapters as `.mdx` files
3. Update `sidebars.js`:
```javascript
{
  type: 'category',
  label: 'Part XX: Name',
  items: [
    'part-XX-name/chXX-title',
  ],
}
```

### Update Navbar

Edit `docusaurus.config.js`:

```javascript
navbar: {
  items: [
    {
      type: 'dropdown',
      label: 'Parts',
      items: [
        {label: 'Part I: Foundations', to: '/docs/part-01-foundations/ch01'},
        // Add more...
      ],
    },
  ],
}
```

### Configure Search

Search is pre-configured with `@cmfcmf/docusaurus-search-local`.

Customize in `docusaurus.config.js`:

```javascript
themes: [
  [
    '@cmfcmf/docusaurus-search-local',
    {
      indexDocs: true,
      indexBlog: false,
      language: 'en',
    },
  ],
],
```

### Add Syntax Highlighting

Edit `docusaurus.config.js`:

```javascript
prism: {
  theme: lightCodeTheme,
  darkTheme: darkCodeTheme,
  additionalLanguages: ['python', 'bash', 'cpp', 'yaml'],
},
```

## 🐛 Troubleshooting

### Build Errors

```bash
# Clear cache and rebuild
npm run clear
npm run build
```

### Port Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm start -- --port 3001
```

### Search Not Working

```bash
# Rebuild search index
npm run build
```

### Chatbot Connection Issues

Check backend is running:
```bash
curl http://localhost:8000/api/health
```

## 📝 Scripts Reference

```json
{
  "start": "docusaurus start",              // Dev server
  "build": "docusaurus build",              // Production build
  "serve": "docusaurus serve",              // Serve production build
  "clear": "docusaurus clear",              // Clear cache
  "test": "playwright test",                // Run E2E tests
  "test:ui": "playwright test --ui",        // Test with UI
  "test:headed": "playwright test --headed", // Headed browser
  "test:debug": "playwright test --debug"   // Debug mode
}
```

## 🤝 Contributing

1. Create branch: `git checkout -b content/new-chapter`
2. Write content following MDX guidelines
3. Test locally: `npm start`
4. Build: `npm run build`
5. Commit: `git commit -m "docs: add Chapter XX"`
6. Push & create PR

## 📖 Documentation

- **Docusaurus Docs**: https://docusaurus.io/docs
- **MDX Syntax**: https://mdxjs.com/
- **React Components**: https://react.dev/
- **Playwright Testing**: https://playwright.dev/

## 🔗 Related Documentation

- [Root README](../README.md) - Project overview
- [Backend README](../backend/README.md) - FastAPI backend
- [Deployment Guide](../docs/deployment.md) - Production deployment
- [Content Style Guide](../docs/content-style-guide.md) - Writing guidelines

## 📄 License

See [LICENSE](../LICENSE) in root directory.
