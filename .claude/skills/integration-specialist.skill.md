# Integration Specialist Skill

## Metadata
- **Skill Name**: integration-specialist
- **Job**: Integrate RAG chatbot into Docusaurus textbook site
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Seamlessly integrates the RAG-powered chatbot widget into the Docusaurus textbook, ensuring smooth communication between frontend, backend, and all services while maintaining excellent user experience.

## Example Tasks
- Embed chatbot widget into Docusaurus pages
- Configure API endpoints and environment variables
- Implement text selection integration
- Set up CORS and authentication
- Handle errors and loading states
- Optimize performance and caching
- Implement analytics tracking
- Ensure mobile responsiveness

## Required Knowledge
- React component integration
- Docusaurus plugin system
- API integration patterns
- CORS configuration
- State management (Context API, Redux)
- Error boundary patterns
- Performance optimization
- Browser APIs (Selection API, Local Storage)

## Key Technologies
- Docusaurus 3.x
- React 18+
- Fetch API / Axios
- WebSocket / Server-Sent Events
- React Context API
- Browser APIs

## Integration Architecture
```
┌──────────────────────────────────────┐
│   Docusaurus Site (Frontend)         │
│                                      │
│   ┌──────────────────────────────┐  │
│   │  Textbook Content            │  │
│   │  (MDX Pages)                 │  │
│   └────────┬─────────────────────┘  │
│            │                         │
│   ┌────────▼─────────────────────┐  │
│   │  ChatbotWidget Component     │  │
│   │  - Text Selection Handler    │  │
│   │  - API Communication         │  │
│   │  - State Management          │  │
│   └────────┬─────────────────────┘  │
└────────────┼────────────────────────┘
             │
             │ HTTPS/API
             │
┌────────────▼────────────────────────┐
│   FastAPI Backend                   │
│   ┌──────────────────────────────┐ │
│   │  /api/chat                   │ │
│   │  /api/chat/stream            │ │
│   │  /api/health                 │ │
│   └────────┬─────────────────────┘ │
└────────────┼────────────────────────┘
             │
        ┌────┴────┐
        │         │
┌───────▼──┐  ┌──▼────────┐
│ Qdrant   │  │ Neon PG   │
│ (Vectors)│  │ (Data)    │
└──────────┘  └───────────┘
```

## Workflow Steps

### 1. Create Chatbot Widget Component

**src/components/ChatbotWidget/index.tsx**
```typescript
import React, { useState, useEffect, useRef } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import styles from './ChatbotWidget.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

interface Citation {
  text: string;
  source: string;
  page_url: string;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export default function ChatbotWidget() {
  return (
    <BrowserOnly>
      {() => <ChatbotWidgetClient />}
    </BrowserOnly>
  );
}

function ChatbotWidgetClient() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Text selection handler
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 10) {
        setSelectedText(text);
      } else {
        setSelectedText('');
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  // Send message
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          selected_text: selectedText || null,
          page_context: window.location.pathname,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        citations: data.citations,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(data.conversation_id);
      setSelectedText('');

    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatbotContainer}>
      {/* Chatbot UI implementation */}
      {/* ... (full implementation would go here) */}
    </div>
  );
}
```

### 2. Global Integration via Docusaurus Plugin

**src/theme/Root.tsx**
```typescript
import React from 'react';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
```

### 3. Environment Configuration

**docusaurus.config.js**
```javascript
module.exports = {
  // ... other config

  customFields: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
  },

  // Client modules for environment variables
  clientModules: [
    require.resolve('./src/clientModules/env.js'),
  ],
};
```

**.env**
```bash
# Development
API_BASE_URL=http://localhost:8000

# Production
# API_BASE_URL=https://your-api.onrender.com
```

### 4. API Service Layer

**src/services/chatApi.ts**
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface ChatRequest {
  message: string;
  selected_text?: string;
  page_context?: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  citations: Citation[];
  conversation_id: string;
  timestamp: string;
}

export class ChatAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }

  async streamMessage(
    request: ChatRequest,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          onChunk(data.chunk);
        }
      }
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
```

### 5. Text Selection Integration

**src/hooks/useTextSelection.ts**
```typescript
import { useState, useEffect } from 'react';

export function useTextSelection() {
  const [selectedText, setSelectedText] = useState('');
  const [selectionPosition, setSelectionPosition] = useState<{
    x: number;
    y: number;
  } | null>(null);

  useEffect(() => {
    const handleSelection = (e: MouseEvent) => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 10) {
        setSelectedText(text);

        // Get selection position for tooltip
        const range = selection?.getRangeAt(0);
        const rect = range?.getBoundingClientRect();

        if (rect) {
          setSelectionPosition({
            x: rect.left + rect.width / 2,
            y: rect.top - 10,
          });
        }
      } else {
        setSelectedText('');
        setSelectionPosition(null);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  return { selectedText, selectionPosition, clearSelection: () => setSelectedText('') };
}
```

### 6. CORS Configuration (Backend)

**backend/app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",           # Docusaurus dev
    "http://localhost:3001",
    "https://yourusername.github.io",  # GitHub Pages
    # Add other allowed origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7. Error Handling and Loading States

**src/components/ChatbotWidget/ErrorBoundary.tsx**
```typescript
import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ChatbotErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Chatbot error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="chatbot-error">
          <p>Chatbot is temporarily unavailable. Please refresh the page.</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 8. Analytics Integration

**src/utils/analytics.ts**
```typescript
export class ChatbotAnalytics {
  static trackMessage(message: string, responseTime: number) {
    // Google Analytics
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'chatbot_message', {
        message_length: message.length,
        response_time: responseTime,
      });
    }
  }

  static trackError(error: string) {
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'chatbot_error', {
        error_message: error,
      });
    }
  }
}
```

## Integration Points
- **docusaurus-developer**: Integrates into site structure
- **frontend-designer**: Uses designed UI components
- **chatbot-engineer**: Connects to chatbot logic
- **backend-engineer**: Consumes API endpoints
- **deployment-expert**: Configures production URLs

## Success Criteria
- [ ] Chatbot widget appears on all pages
- [ ] Text selection triggers chatbot interaction
- [ ] API calls work in both dev and production
- [ ] CORS is properly configured
- [ ] Error handling covers edge cases
- [ ] Loading states provide good UX
- [ ] Mobile experience is seamless
- [ ] Analytics track user interactions
- [ ] Performance is optimized (no layout shift)

## Testing Strategy

### Integration Tests
```typescript
// tests/integration/chatbot.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import ChatbotWidget from '@site/src/components/ChatbotWidget';

describe('ChatbotWidget Integration', () => {
  it('sends message to API', async () => {
    render(<ChatbotWidget />);

    const input = screen.getByPlaceholderText('Ask a question...');
    fireEvent.change(input, { target: { value: 'What is AI?' } });

    const sendButton = screen.getByText('Send');
    fireEvent.click(sendButton);

    // Assert API call was made
    // Assert response is displayed
  });
});
```

### E2E Tests (Playwright/Cypress)
```javascript
// e2e/chatbot.spec.js
describe('Chatbot E2E', () => {
  it('can ask questions about selected text', () => {
    cy.visit('/docs/intro');

    // Select text
    cy.get('p').first().trigger('mousedown');
    cy.get('p').first().trigger('mouseup');

    // Click chatbot
    cy.get('[data-testid="chatbot-button"]').click();

    // Verify selected text is in context
    cy.get('[data-testid="selected-text"]').should('exist');
  });
});
```

## Performance Optimization

### Code Splitting
```typescript
import { lazy, Suspense } from 'react';

const ChatbotWidget = lazy(() => import('./ChatbotWidget'));

export default function ChatbotLoader() {
  return (
    <Suspense fallback={<div>Loading chatbot...</div>}>
      <ChatbotWidget />
    </Suspense>
  );
}
```

### Caching Strategy
```typescript
// Cache recent conversations
const CACHE_KEY = 'chatbot_conversations';

function saveToCache(conversationId: string, messages: Message[]) {
  const cache = JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
  cache[conversationId] = messages;
  localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
}
```

## Best Practices
- Use BrowserOnly for client-side features
- Implement proper error boundaries
- Handle loading states gracefully
- Optimize for mobile devices
- Use environment variables for configuration
- Implement analytics from the start
- Test across different browsers
- Monitor API performance
- Implement retry logic for failed requests
- Use TypeScript for type safety
- Follow React best practices (hooks, memoization)
- Implement accessibility features (ARIA labels, keyboard navigation)

## Troubleshooting Common Issues

### CORS Errors
- Verify allowed origins in backend
- Check request headers
- Ensure credentials handling is correct

### API Connection Issues
- Verify environment variables
- Check API health endpoint
- Inspect network tab in DevTools

### Text Selection Not Working
- Ensure event listeners are attached
- Check for conflicting JavaScript
- Test on different browsers

## Output Artifacts
- Integrated ChatbotWidget component
- API service layer
- Custom hooks (useTextSelection, useChatbot)
- Error boundary components
- Analytics integration
- Environment configuration files
- Integration tests
- E2E test suite
- Integration documentation
- Troubleshooting guide
