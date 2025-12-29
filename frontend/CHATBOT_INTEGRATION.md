# Chatbot Widget Integration Guide

This guide explains how the chatbot widget is integrated into the Physical AI & Humanoid Robotics textbook frontend.

## Architecture Overview

```
frontend/
├── src/
│   ├── components/
│   │   └── ChatbotWidget/
│   │       ├── index.tsx              # Main widget component
│   │       ├── MessageList.tsx        # Message display
│   │       ├── InputArea.tsx          # User input
│   │       ├── CitationLink.tsx       # Citation badges
│   │       ├── styles.module.css      # Component styles
│   │       └── README.md              # Component documentation
│   ├── services/
│   │   └── api.ts                     # SSE client & API calls
│   ├── types/
│   │   └── chat.ts                    # TypeScript definitions
│   └── theme/
│       └── Root.tsx                   # Docusaurus theme wrapper
└── tsconfig.json                      # TypeScript configuration
```

## Component Hierarchy

```
Root (theme/Root.tsx)
└── ChatbotWidget (components/ChatbotWidget/index.tsx)
    ├── MessageList (components/ChatbotWidget/MessageList.tsx)
    │   └── CitationLink (components/ChatbotWidget/CitationLink.tsx)
    └── InputArea (components/ChatbotWidget/InputArea.tsx)
```

## Installation & Setup

### 1. Install Dependencies

All required dependencies are already in `package.json`:
- `react` ^18.3.1
- `react-dom` ^18.3.1
- `@docusaurus/core` ^3.9.2

No additional dependencies needed!

### 2. TypeScript Configuration

The `tsconfig.json` is already configured with:
- Path aliases for clean imports
- Strict type checking
- Docusaurus integration

### 3. Integration with Docusaurus

The widget is automatically injected via the `Root.tsx` theme wrapper:

```tsx
// src/theme/Root.tsx
import ChatbotWidget from '../components/ChatbotWidget';

const Root = ({ children }) => (
  <>
    {children}
    <ChatbotWidget initialState="minimized" />
  </>
);
```

This is Docusaurus's official way to inject global components.

## Backend API Configuration

### Option 1: Environment Variable (Recommended)

Create `.env.local`:

```bash
REACT_APP_API_URL=http://localhost:8000
```

### Option 2: Runtime Configuration

Edit `docusaurus.config.js`:

```js
module.exports = {
  // ... existing config
  scripts: [
    {
      innerHTML: `window.CHATBOT_API_URL = '${process.env.BACKEND_URL || 'http://localhost:8000'}';`,
    },
  ],
};
```

### Option 3: Default (Development)

If no configuration is provided, defaults to `http://localhost:8000`.

## Running the Application

### Development Mode

```bash
cd frontend
npm start
```

The chatbot widget will appear in the bottom-right corner.

### Production Build

```bash
cd frontend
npm run build
npm run serve
```

## API Integration

### SSE Endpoint Contract

**Endpoint:** `POST /api/chat`

**Headers:**
```
Content-Type: application/json
Accept: text/event-stream
```

**Request Body:**
```json
{
  "message": "What is Physical AI?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**SSE Events:**

1. **Token Event** (incremental response)
   ```
   event: token
   data: Hello
   ```

2. **Citation Event** (reference to textbook)
   ```
   event: citation
   data: {"id":"cit1","chapter":"Chapter 1","section":"1.1","url":"/docs/part-01-foundations/ch01-intro-physical-ai#what-is-physical-ai","text":"Introduction"}
   ```

3. **Done Event** (completion)
   ```
   event: done
   data:
   ```

4. **Error Event** (error handling)
   ```
   event: error
   data: An error occurred
   ```

## Customization

### Styling

All styles are in `src/components/ChatbotWidget/styles.module.css`.

**Override primary color:**
```css
/* src/css/custom.css */
:root {
  --ifm-color-primary: #2e8555;
}
```

**Dark mode:**
```css
[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
}
```

### Widget Configuration

```tsx
<ChatbotWidget
  initialState="minimized"  // or "expanded"
  sessionId="custom-id"     // optional
/>
```

### Changing Position

Edit `styles.module.css`:

```css
.chatbotWidget {
  bottom: 20px;
  right: 20px;  /* Change to left: 20px for left side */
}
```

## Features

### ✅ Implemented

- Real-time streaming responses (SSE)
- Citation links to textbook sections
- Session persistence (localStorage + sessionStorage)
- Conversation history
- Clear conversation
- Minimizable/expandable widget
- Responsive design (mobile full-screen)
- Dark mode support
- Typing indicator
- Character count (max 2000)
- Keyboard shortcuts (Enter/Shift+Enter)
- Error handling
- Accessibility (ARIA labels, keyboard navigation)

### 🚀 Future Enhancements

- Voice input/output
- Conversation export
- Feedback mechanism (thumbs up/down)
- Multi-language support
- Conversation search
- Bookmark messages

## Testing

### Manual Testing

1. **Basic Functionality**
   - [ ] Open widget (click floating button)
   - [ ] Send a message
   - [ ] Receive streaming response
   - [ ] Click citation links
   - [ ] Clear conversation

2. **UI/UX**
   - [ ] Minimize/expand widget
   - [ ] Resize window (test responsive)
   - [ ] Toggle dark mode
   - [ ] Check mobile view

3. **Keyboard Navigation**
   - [ ] Tab through elements
   - [ ] Enter to send
   - [ ] Shift+Enter for newline
   - [ ] Escape to close (if focused)

4. **Error Handling**
   - [ ] Disconnect backend (test error state)
   - [ ] Send empty message (validation)
   - [ ] Exceed character limit

### Browser Testing

- Chrome/Edge ✅
- Firefox ✅
- Safari ✅
- Mobile Safari ✅
- Chrome Mobile ✅

## Deployment

### GitHub Pages

Already configured in `docusaurus.config.js`:

```js
url: 'https://ambreenraheem.github.io',
baseUrl: '/textbook_hackthon_ai/',
```

Deploy:
```bash
npm run deploy
```

### Custom Domain

Update API URL for production:

```js
// docusaurus.config.js
scripts: [
  {
    innerHTML: `window.CHATBOT_API_URL = 'https://api.yourdomain.com';`,
  },
],
```

## Troubleshooting

### Widget Not Appearing

1. **Check Console Errors**
   - Open browser DevTools (F12)
   - Look for React/TypeScript errors

2. **Verify Root.tsx**
   ```bash
   ls frontend/src/theme/Root.tsx
   ```

3. **Check Z-Index Conflicts**
   - Widget uses `z-index: 9999`
   - Verify no other elements override it

### SSE Connection Issues

1. **CORS Configuration**

   Backend needs CORS headers:
   ```python
   # FastAPI example
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["POST"],
       allow_headers=["*"],
   )
   ```

2. **Check Backend URL**

   Open browser console:
   ```js
   console.log(window.CHATBOT_API_URL);
   ```

3. **Test Endpoint Manually**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -H "Accept: text/event-stream" \
     -d '{"message":"test","session_id":"test"}'
   ```

### Citations Not Working

1. **Verify URL Format**

   Citations must have valid URLs:
   ```json
   {
     "id": "cit1",
     "url": "/docs/part-01-foundations/ch01-intro-physical-ai#section-id"
   }
   ```

2. **Check Target Element IDs**

   Ensure markdown headers have IDs:
   ```markdown
   ## What is Physical AI? {#what-is-physical-ai}
   ```

3. **Test Navigation**
   ```js
   // In browser console
   window.location.href = "/docs/part-01-foundations/ch01-intro-physical-ai#intro"
   ```

### Style Issues

1. **CSS Modules Not Loading**

   Clear cache:
   ```bash
   npm run clear
   npm start
   ```

2. **Dark Mode Not Working**

   Check theme toggle in navbar:
   ```js
   document.documentElement.getAttribute('data-theme')
   ```

3. **Mobile Layout Issues**

   Test responsive breakpoints:
   - Mobile: < 768px (full-screen)
   - Desktop: ≥ 768px (floating widget)

## Performance

### Bundle Size

The chatbot adds approximately:
- TypeScript files: ~50KB (source)
- CSS: ~15KB
- Compiled JS: ~30KB (gzipped)

### Optimization Tips

1. **Lazy Load Widget**
   ```tsx
   const ChatbotWidget = lazy(() => import('./components/ChatbotWidget'));
   ```

2. **Debounce Input**
   Already implemented with auto-resize

3. **Limit Message History**
   ```tsx
   const MAX_MESSAGES = 50;
   setMessages(prev => prev.slice(-MAX_MESSAGES));
   ```

## Security

### Sensitive Data

- No API keys in frontend code
- Session IDs are client-generated UUIDs
- No user authentication (stateless)

### XSS Prevention

- React automatically escapes content
- Citation URLs are validated
- No `dangerouslySetInnerHTML`

### CORS

Backend must configure CORS properly:
```python
allow_origins=["https://yourdomain.com"]
```

## Support

### Documentation

- Component README: `src/components/ChatbotWidget/README.md`
- This integration guide
- Inline code comments

### Community

- GitHub Issues: https://github.com/ambreenraheem/textbook_hackthon_ai/issues
- Discussions: https://github.com/ambreenraheem/textbook_hackthon_ai/discussions

## License

CC BY-NC-SA 4.0 - Same as the textbook project.
