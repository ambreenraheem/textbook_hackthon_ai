/**
 * ChatbotWidget Component
 * Main chatbot widget with state management, SSE handling, and UI
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Message, Citation, WidgetState, ChatError } from '../../types/chat';
import { sendChatMessage, generateSessionId, validateMessage } from '../../services/api';
import MessageList from './MessageList';
import InputArea from './InputArea';
import styles from './styles.module.css';

interface ChatbotWidgetProps {
  initialState?: WidgetState;
  sessionId?: string;
  selectedText?: string;
  onSelectedTextUsed?: () => void;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({
  initialState = 'minimized',
  sessionId: providedSessionId,
  selectedText,
  onSelectedTextUsed,
}) => {
  // Widget state
  const [widgetState, setWidgetState] = useState<WidgetState>(initialState);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<ChatError | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  // Refs
  const streamingMessageRef = useRef<Message | null>(null);
  const currentCitationsRef = useRef<Citation[]>([]);

  /**
   * Initialize session on mount
   */
  useEffect(() => {
    initializeSession();
    loadPersistedMessages();
  }, []);

  /**
   * Persist messages to sessionStorage
   */
  useEffect(() => {
    if (messages.length > 0) {
      persistMessages();
    }
  }, [messages]);

  /**
   * Initialize or restore session
   */
  const initializeSession = () => {
    // Use provided session ID or get from localStorage
    let sid = providedSessionId;

    if (!sid) {
      sid = localStorage.getItem('chatbot_session_id') || '';
    }

    // Generate new session if none exists
    if (!sid) {
      sid = generateSessionId();
      localStorage.setItem('chatbot_session_id', sid);
    }

    setSessionId(sid);
  };

  /**
   * Load persisted messages from sessionStorage
   */
  const loadPersistedMessages = () => {
    try {
      const stored = sessionStorage.getItem('chatbot_messages');
      if (stored) {
        const parsed = JSON.parse(stored);
        // Convert timestamp strings back to Date objects
        const restored = parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(restored);
      }
    } catch (error) {
      console.error('Failed to load persisted messages:', error);
    }
  };

  /**
   * Persist messages to sessionStorage
   */
  const persistMessages = () => {
    try {
      sessionStorage.setItem('chatbot_messages', JSON.stringify(messages));
    } catch (error) {
      console.error('Failed to persist messages:', error);
    }
  };

  /**
   * Toggle widget state
   */
  const toggleWidget = () => {
    setWidgetState((prev) => (prev === 'minimized' ? 'expanded' : 'minimized'));
    setError(null); // Clear errors when toggling
  };

  /**
   * Clear conversation
   */
  const clearConversation = () => {
    if (window.confirm('Are you sure you want to clear the conversation?')) {
      setMessages([]);
      sessionStorage.removeItem('chatbot_messages');

      // Generate new session ID
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);
      localStorage.setItem('chatbot_session_id', newSessionId);
    }
  };

  /**
   * Generate unique message ID
   */
  const generateMessageId = (): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  /**
   * Handle sending a message
   */
  const handleSendMessage = useCallback(
    async (content: string) => {
      // Validate message
      const validation = validateMessage(content);
      if (!validation.valid) {
        setError({
          message: validation.error || 'Invalid message',
          code: 'VALIDATION_ERROR',
        });
        return;
      }

      // Clear any previous errors
      setError(null);

      // Add user message
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);

      // Initialize streaming assistant message
      const assistantMessage: Message = {
        id: generateMessageId(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        citations: [],
        isStreaming: true,
      };

      streamingMessageRef.current = assistantMessage;
      currentCitationsRef.current = [];
      setIsStreaming(true);

      // Start SSE stream
      try {
        await sendChatMessage(
          content,
          sessionId,
          {
            onToken: handleToken,
            onCitation: handleCitation,
            onDone: handleDone,
            onError: handleError,
          },
          selectedText
        );

        // Clear selected text after use
        if (selectedText && onSelectedTextUsed) {
          onSelectedTextUsed();
        }
      } catch (error) {
        handleError({
          message: error instanceof Error ? error.message : 'Failed to send message',
          code: 'SEND_ERROR',
        });
      }
    },
    [sessionId, selectedText, onSelectedTextUsed]
  );

  /**
   * Handle incoming token from SSE
   */
  const handleToken = useCallback((token: string) => {
    if (streamingMessageRef.current) {
      streamingMessageRef.current.content += token;

      // Update the last message in the array
      setMessages((prev) => {
        const updated = [...prev];
        const lastMessage = updated[updated.length - 1];

        // If last message is not the streaming message, add it
        if (!lastMessage || lastMessage.id !== streamingMessageRef.current?.id) {
          return [...prev, { ...streamingMessageRef.current! }];
        }

        // Update existing streaming message
        updated[updated.length - 1] = { ...streamingMessageRef.current! };
        return updated;
      });
    }
  }, []);

  /**
   * Handle incoming citation from SSE
   */
  const handleCitation = useCallback((citationData: string) => {
    try {
      const citation: Citation = JSON.parse(citationData);
      currentCitationsRef.current.push(citation);

      if (streamingMessageRef.current) {
        streamingMessageRef.current.citations = [...currentCitationsRef.current];

        // Update message with citations
        setMessages((prev) => {
          const updated = [...prev];
          const lastMessage = updated[updated.length - 1];

          if (lastMessage && lastMessage.id === streamingMessageRef.current?.id) {
            updated[updated.length - 1] = { ...streamingMessageRef.current! };
          }

          return updated;
        });
      }
    } catch (error) {
      console.error('Failed to parse citation:', error);
    }
  }, []);

  /**
   * Handle stream completion
   */
  const handleDone = useCallback(() => {
    if (streamingMessageRef.current) {
      // Finalize the streaming message
      streamingMessageRef.current.isStreaming = false;

      setMessages((prev) => {
        const updated = [...prev];
        const lastMessage = updated[updated.length - 1];

        if (lastMessage && lastMessage.id === streamingMessageRef.current?.id) {
          updated[updated.length - 1] = { ...streamingMessageRef.current! };
        }

        return updated;
      });
    }

    // Reset streaming state
    setIsStreaming(false);
    streamingMessageRef.current = null;
    currentCitationsRef.current = [];
  }, []);

  /**
   * Handle error from SSE
   */
  const handleError = useCallback((error: ChatError) => {
    console.error('Chat error:', error);
    setError(error);
    setIsStreaming(false);

    // Clean up streaming message if it exists
    if (streamingMessageRef.current && streamingMessageRef.current.content === '') {
      // Remove empty streaming message
      setMessages((prev) => {
        const filtered = prev.filter(
          (msg) => msg.id !== streamingMessageRef.current?.id
        );
        return filtered;
      });
    } else if (streamingMessageRef.current) {
      // Finalize partial message
      streamingMessageRef.current.isStreaming = false;
      handleDone();
    }

    streamingMessageRef.current = null;
    currentCitationsRef.current = [];
  }, [handleDone]);

  /**
   * Render minimized state (toggle button)
   */
  const renderMinimized = () => (
    <button
      className={styles.toggleButton}
      onClick={toggleWidget}
      aria-label="Open chat assistant"
      title="Open chat assistant"
    >
      💬
    </button>
  );

  /**
   * Render expanded state (full widget)
   */
  const renderExpanded = () => (
    <div className={styles.widgetContainer} role="dialog" aria-label="Chat assistant">
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.headerTitle}>
          <span>🤖</span>
          <span>Textbook Assistant</span>
        </h2>
        <div className={styles.headerActions}>
          <button
            className={styles.headerButton}
            onClick={clearConversation}
            aria-label="Clear conversation"
            title="Clear conversation"
          >
            🗑️
          </button>
          <button
            className={styles.headerButton}
            onClick={toggleWidget}
            aria-label="Minimize chat"
            title="Minimize chat"
          >
            ➖
          </button>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className={styles.errorMessage} role="alert">
          <span className={styles.errorIcon}>⚠️</span>
          <span>{error.message}</span>
        </div>
      )}

      {/* Messages */}
      <MessageList messages={messages} isStreaming={isStreaming} />

      {/* Input */}
      <InputArea
        onSendMessage={handleSendMessage}
        disabled={isStreaming}
        placeholder="Ask about Physical AI, ROS 2, or robotics..."
        selectedText={selectedText}
        onClearSelectedText={onSelectedTextUsed}
      />
    </div>
  );

  return (
    <div className={`${styles.chatbotWidget} ${styles[widgetState]}`}>
      {widgetState === 'minimized' ? renderMinimized() : renderExpanded()}
    </div>
  );
};

export default ChatbotWidget;
