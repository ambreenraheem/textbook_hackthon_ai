# Chatbot Engineer Skill

## Metadata
- **Skill Name**: chatbot-engineer
- **Job**: Build interactive RAG-powered chatbot for textbook assistance
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Develops and integrates an intelligent RAG (Retrieval-Augmented Generation) chatbot that assists users within the textbook, answering questions about content including user-selected text.

## Example Tasks
- Implement OpenAI Agents/ChatKit SDK integration
- Create conversation management system
- Build text selection-based question answering
- Implement context-aware responses
- Create chat history persistence
- Build streaming response UI
- Implement error handling and fallbacks
- Add conversation analytics

## Required Knowledge
- OpenAI API and Agents SDK
- ChatKit SDK usage
- Conversational AI patterns
- WebSocket/SSE for streaming
- React state management
- Session management
- Natural language processing concepts

## Key Technologies
- OpenAI Agents SDK
- ChatKit SDK
- React/TypeScript
- WebSocket or Server-Sent Events
- REST API integration
- Local storage / Session storage

## Architecture
```
Frontend (Docusaurus)
    ↓
ChatbotWidget Component
    ↓
ChatKit SDK / OpenAI Agents SDK
    ↓
Backend API (FastAPI)
    ↓
RAG Pipeline (Qdrant + Neon)
```

## Workflow Steps
1. **Setup OpenAI Agents SDK**
   ```typescript
   import { Agent } from '@openai/agents-sdk';

   const agent = new Agent({
     apiKey: process.env.OPENAI_API_KEY,
     model: 'gpt-4-turbo-preview',
   });
   ```

2. **Implement ChatKit Integration**
   ```typescript
   import { ChatKit } from '@openai/chatkit';

   const chatkit = new ChatKit({
     agent: agent,
     streamingEnabled: true,
   });
   ```

3. **Create Chat Context Manager**
   ```typescript
   interface ChatContext {
     conversationId: string;
     messages: Message[];
     selectedText?: string;
     currentPage?: string;
   }
   ```

4. **Implement Text Selection Handler**
   ```typescript
   const handleTextSelection = () => {
     const selectedText = window.getSelection()?.toString();
     if (selectedText) {
       setChatContext({
         ...chatContext,
         selectedText,
       });
     }
   };
   ```

5. **Build Message Handler**
   ```typescript
   const sendMessage = async (userMessage: string) => {
     const response = await fetch('/api/chat', {
       method: 'POST',
       body: JSON.stringify({
         message: userMessage,
         context: chatContext,
       }),
     });
     // Handle streaming response
   };
   ```

## Integration Points
- **frontend-designer**: Receives UI/UX specifications
- **backend-engineer**: Connects to FastAPI endpoints
- **rag-specialist**: Uses RAG retrieval results
- **integration-specialist**: Embeds into Docusaurus

## Features Specification

### Core Features
1. **General Q&A**
   - Answer questions about any textbook content
   - Provide citations to source material
   - Handle multi-turn conversations

2. **Text Selection Q&A**
   - Allow users to select text and ask questions about it
   - Provide focused answers based on selected content
   - Show relevance to broader context

3. **Contextual Awareness**
   - Remember conversation history
   - Understand current page context
   - Reference previous questions

4. **Smart Features**
   - Code example generation
   - Concept explanations
   - Related topic suggestions
   - Quiz generation from content

### Chat Interface Components
```typescript
// Components structure
components/
├── ChatbotWidget/
│   ├── ChatWindow.tsx
│   ├── MessageList.tsx
│   ├── MessageInput.tsx
│   ├── TextSelectionButton.tsx
│   ├── TypingIndicator.tsx
│   └── ChatbotWidget.tsx
```

## Implementation Example

### Chat Widget Component
```typescript
import React, { useState, useEffect } from 'react';
import { Agent } from '@openai/agents-sdk';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

export const ChatbotWidget: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [selectedText, setSelectedText] = useState('');

  const handleSendMessage = async () => {
    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);

    // Call backend API with RAG
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: inputValue,
        selectedText,
        pageContext: window.location.pathname,
      }),
    });

    const data = await response.json();

    const assistantMessage: Message = {
      role: 'assistant',
      content: data.response,
      citations: data.citations,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage, assistantMessage]);
    setInputValue('');
  };

  return (
    <div className="chatbot-widget">
      {/* Implementation */}
    </div>
  );
};
```

### Text Selection Integration
```typescript
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 10) {
      setSelectedText(text);
      // Show "Ask about this" button
    }
  };

  document.addEventListener('mouseup', handleSelection);
  return () => document.removeEventListener('mouseup', handleSelection);
}, []);
```

## Success Criteria
- [ ] Chatbot responds accurately to textbook questions
- [ ] Text selection Q&A works seamlessly
- [ ] Response time < 3 seconds
- [ ] Citations link back to source content
- [ ] Conversation history persists across sessions
- [ ] Handles errors gracefully
- [ ] Mobile-responsive interface
- [ ] Streaming responses work smoothly

## Error Handling
```typescript
try {
  const response = await sendMessage(message);
  return response;
} catch (error) {
  if (error.type === 'rate_limit') {
    return 'Too many requests. Please wait a moment.';
  } else if (error.type === 'network') {
    return 'Connection error. Please check your internet.';
  } else {
    return 'Sorry, something went wrong. Please try again.';
  }
}
```

## Best Practices
- Implement retry logic for failed requests
- Cache frequent queries
- Show loading states and typing indicators
- Provide fallback responses
- Log interactions for analytics
- Implement rate limiting on client side
- Sanitize user input
- Show citation sources clearly
- Make conversations exportable
- Add keyboard shortcuts

## Testing Strategy
- Unit tests for message handling
- Integration tests with backend API
- E2E tests for user workflows
- Performance testing for response times
- Accessibility testing for chat interface
- Cross-browser testing
- Mobile device testing

## Output Artifacts
- ChatbotWidget React component
- OpenAI Agents SDK integration code
- Message handling logic
- Context management system
- Error handling utilities
- TypeScript type definitions
- Integration documentation
