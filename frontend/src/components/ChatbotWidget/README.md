# Chatbot Widget

Production-ready React chatbot widget for the Physical AI & Humanoid Robotics textbook.

## Overview

The chatbot widget provides an interactive AI assistant that helps users navigate and understand the textbook content. It features real-time streaming responses, citation links to relevant sections, and a clean, accessible UI.

## Architecture

### Components

1. **ChatbotWidget** (`index.tsx`)
   - Main container component
   - State management (messages, session, streaming)
   - SSE event handling
   - Session persistence

2. **MessageList** (`MessageList.tsx`)
   - Displays conversation history
   - Auto-scroll to latest message
   - Typing indicator
   - Empty state with suggestions

3. **InputArea** (`InputArea.tsx`)
   - Multiline text input with auto-resize
   - Character count (max 2000)
   - Keyboard shortcuts (Enter to send, Shift+Enter for newline)
   - Send button with loading state

4. **CitationLink** (`CitationLink.tsx`)
   - Clickable citation badges
   - Navigates to referenced textbook sections
   - Highlights target section temporarily
   - Tooltips with chapter/section info

### Services

**API Client** (`services/api.ts`)
- SSE streaming implementation
- Event parsing (token, citation, done, error)
- Session ID generation
- Message validation
- Reconnection logic

### Types

**TypeScript Definitions** (`types/chat.ts`)
- Message, Citation, ChatSession
- SSEEvent, ChatRequest, ChatError
- WidgetState, ChatbotConfig

## Features

### Core Functionality
- ✅ Real-time streaming responses via SSE
- ✅ Citation links to textbook sections
- ✅ Session persistence (localStorage + sessionStorage)
- ✅ Conversation history
- ✅ Clear conversation option

### UI/UX
- ✅ Minimizable/expandable widget
- ✅ Smooth animations and transitions
- ✅ Responsive design (mobile: full screen, desktop: floating)
- ✅ Dark mode support
- ✅ Typing indicator
- ✅ Character count with warnings
- ✅ Empty state with suggestions

### Accessibility
- ✅ ARIA labels and roles
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Focus management
- ✅ Reduced motion support

### Error Handling
- ✅ Network error handling
- ✅ Validation errors
- ✅ Stream errors
- ✅ User-friendly error messages
- ✅ Graceful degradation

## Configuration

### Environment Variables

Set the backend API URL (optional):

```js
// In docusaurus.config.js
module.exports = {
  scripts: [
    {
      innerHTML: `window.CHATBOT_API_URL = 'https://your-api.com';`,
    },
  ],
};
```

Or use the default: `http://localhost:8000`

### Widget Configuration

```tsx
<ChatbotWidget
  initialState="minimized"  // or "expanded"
  sessionId="custom-session-id"  // optional
/>
```

## Backend API Contract

### Endpoint
```
POST /api/chat
Content-Type: application/json
Accept: text/event-stream
```

### Request Body
```json
{
  "message": "What is Physical AI?",
  "session_id": "uuid-v4-string"
}
```

### SSE Response Events

**Token Event** (streaming response text)
```
event: token
data: Hello
```

**Citation Event** (reference to textbook section)
```
event: citation
data: {"id":"cit1","chapter":"Chapter 1","section":"Section 1.1","url":"/docs/part-01/ch01#intro","text":"Introduction to Physical AI"}
```

**Done Event** (stream complete)
```
event: done
data:
```

**Error Event** (error occurred)
```
event: error
data: Error message text
```

## Usage

### Integration with Docusaurus

The widget is automatically injected into all pages via the `Root.tsx` theme wrapper.

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

### Standalone Usage

```tsx
import ChatbotWidget from './components/ChatbotWidget';

function App() {
  return (
    <div>
      <YourContent />
      <ChatbotWidget />
    </div>
  );
}
```

## Styling

All styles are in `styles.module.css` using CSS Modules for scoping.

### Custom Theming

Override CSS variables:

```css
:root {
  --ifm-color-primary: #2e8555;
  --ifm-font-family-base: 'Inter', sans-serif;
}
```

### Dark Mode

Dark mode is automatically supported via Docusaurus theme:

```css
[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
  --ifm-background-color: #1a1a1a;
}
```

## State Persistence

### Session Storage
- Conversation messages (cleared on tab close)
- Persisted automatically after each message

### Local Storage
- Session ID (persists across tabs/sessions)
- Generated once and reused

### Clear State

```js
// Programmatically clear
sessionStorage.removeItem('chatbot_messages');
localStorage.removeItem('chatbot_session_id');
```

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line
- `Esc` - Close widget (when focused)
- `Tab` - Navigate between elements

## Accessibility

### ARIA Labels
- All interactive elements have proper ARIA labels
- Dialog role for expanded widget
- Live regions for status updates

### Screen Readers
- Announces new messages
- Character count updates
- Error messages
- Loading states

### Keyboard Navigation
- Full keyboard support
- Visible focus indicators
- Logical tab order

## Performance

### Optimizations
- React.memo for expensive components
- useCallback for stable function references
- Debounced auto-resize
- Lazy loading (can be added)

### Bundle Size
- No heavy dependencies
- CSS Modules (scoped, minimal)
- Tree-shakeable API client

## Browser Support

- Chrome/Edge: ✅ Latest 2 versions
- Firefox: ✅ Latest 2 versions
- Safari: ✅ Latest 2 versions
- Mobile browsers: ✅ iOS Safari, Chrome Mobile

## Development

### Run Locally

```bash
cd frontend
npm start
```

The widget will appear in the bottom-right corner.

### Mock Backend

For development without backend:

```tsx
// Mock the API
const mockSendMessage = async (message, sessionId, callbacks) => {
  // Simulate streaming
  const response = "Mock response";
  for (const char of response) {
    await new Promise(r => setTimeout(r, 50));
    callbacks.onToken(char);
  }
  callbacks.onDone();
};
```

## Testing

### Manual Testing Checklist

- [ ] Send message and receive response
- [ ] Citations link to correct sections
- [ ] Minimize/expand widget
- [ ] Clear conversation
- [ ] Character limit enforcement
- [ ] Keyboard shortcuts work
- [ ] Mobile responsive design
- [ ] Dark mode support
- [ ] Session persistence
- [ ] Error handling

### Automated Tests (TODO)

```bash
npm test
```

## Troubleshooting

### Widget not appearing
- Check console for errors
- Verify `Root.tsx` is being used
- Check z-index conflicts

### SSE not connecting
- Verify backend URL in browser console
- Check CORS configuration
- Ensure `/api/chat` endpoint exists

### Citations not working
- Verify citation URL format
- Check for hash navigation issues
- Ensure target elements have IDs

### Style conflicts
- Check for CSS specificity issues
- Verify CSS Modules are working
- Check for theme overrides

## Future Enhancements

- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Conversation export
- [ ] Feedback mechanism (thumbs up/down)
- [ ] Suggested questions
- [ ] Conversation search
- [ ] Bookmark messages
- [ ] Share conversation

## License

This component is part of the Physical AI & Humanoid Robotics Textbook project.
Licensed under CC BY-NC-SA 4.0.

## Support

For issues or questions:
- GitHub Issues: https://github.com/ambreenraheem/textbook_hackthon_ai/issues
- Discussions: https://github.com/ambreenraheem/textbook_hackthon_ai/discussions
