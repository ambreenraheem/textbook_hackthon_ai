# Chatbot Widget - Quick Start Guide

Get the chatbot widget running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- Backend API running on port 8000 (or configured URL)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Backend URL (Optional)

Copy the example environment file:

```bash
cp .env.example .env.local
```

Edit `.env.local` if your backend is not on `http://localhost:8000`:

```bash
REACT_APP_API_URL=http://your-backend-url:port
```

### 3. Start Development Server

```bash
npm start
```

The application will open at `http://localhost:3000`.

### 4. Test the Chatbot

1. Look for the floating chat button in the bottom-right corner (💬)
2. Click it to open the chat widget
3. Type a message and press Enter
4. You should see a streaming response!

## That's It! 🎉

The chatbot widget is now integrated and running.

## What Just Happened?

The chatbot widget was automatically injected into your Docusaurus site through:

1. **Theme Wrapper** (`src/theme/Root.tsx`)
   - Wraps all pages
   - Injects `<ChatbotWidget />` globally

2. **Auto-Detection**
   - Session ID generated and stored in localStorage
   - Conversation persisted in sessionStorage

3. **SSE Connection**
   - Connects to `POST /api/chat` endpoint
   - Streams responses in real-time

## Project Structure

```
frontend/
├── src/
│   ├── components/ChatbotWidget/   ← Chatbot components
│   ├── services/api.ts             ← SSE client
│   ├── types/chat.ts               ← TypeScript types
│   └── theme/Root.tsx              ← Global injection
├── .env.example                    ← Environment template
└── tsconfig.json                   ← TypeScript config
```

## Testing Without Backend

Want to test the UI without a backend? Use this mock:

```tsx
// src/services/api.ts - add at the top

export const MOCK_MODE = true; // Toggle this

// Then in sendChatMessage function:
if (MOCK_MODE) {
  const mockResponse = "This is a mock response. The backend is not connected.";
  for (const char of mockResponse) {
    await new Promise(r => setTimeout(r, 50));
    callbacks.onToken(char);
  }

  // Mock citation
  callbacks.onCitation(JSON.stringify({
    id: "cit1",
    chapter: "Chapter 1",
    section: "Section 1.1",
    url: "/docs/part-01-foundations/ch01-intro-physical-ai",
    text: "Introduction to Physical AI"
  }));

  callbacks.onDone();
  return;
}
```

## Common Commands

```bash
# Development
npm start                 # Start dev server
npm run build            # Production build
npm run serve            # Serve production build
npm run clear            # Clear cache

# Deployment
npm run deploy           # Deploy to GitHub Pages
```

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in input
- `Tab` - Navigate between elements

## Features Available

✅ Real-time streaming responses
✅ Citation links to textbook sections
✅ Conversation history
✅ Dark mode support
✅ Mobile responsive
✅ Session persistence
✅ Clear conversation
✅ Character limit (2000)
✅ Typing indicator
✅ Error handling

## Troubleshooting

### Widget Not Appearing?

1. Check browser console for errors (F12)
2. Verify `src/theme/Root.tsx` exists
3. Clear cache: `npm run clear && npm start`

### Backend Connection Failed?

1. Verify backend is running: `curl http://localhost:8000/api/chat`
2. Check CORS configuration in backend
3. Verify `.env.local` has correct URL

### Citations Not Working?

1. Ensure backend returns proper citation format
2. Check citation URLs match your docs structure
3. Verify markdown headers have IDs

## Next Steps

- Read full documentation: `CHATBOT_INTEGRATION.md`
- Component details: `src/components/ChatbotWidget/README.md`
- Customize styles: `src/components/ChatbotWidget/styles.module.css`
- Configure backend: See Backend API Contract below

## Backend API Contract

Your backend needs to implement:

**Endpoint:** `POST /api/chat`

**Request:**
```json
{
  "message": "user question",
  "session_id": "uuid-v4-string"
}
```

**Response:** Server-Sent Events (SSE)

```
event: token
data: response text

event: citation
data: {"id":"cit1","chapter":"Ch1","section":"1.1","url":"/docs/...","text":"..."}

event: done
data:
```

See `CHATBOT_INTEGRATION.md` for complete API specification.

## Support

- 📖 Full Documentation: [CHATBOT_INTEGRATION.md](CHATBOT_INTEGRATION.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/ambreenraheem/textbook_hackthon_ai/issues)
- 💬 Ask Questions: [GitHub Discussions](https://github.com/ambreenraheem/textbook_hackthon_ai/discussions)

## License

CC BY-NC-SA 4.0
