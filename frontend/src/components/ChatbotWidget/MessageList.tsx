/**
 * MessageList Component
 * Displays conversation history with user/assistant messages and citations
 */

import React, { useEffect, useRef } from 'react';
import { Message } from '../../types/chat';
import CitationLink from './CitationLink';
import styles from './styles.module.css';

interface MessageListProps {
  messages: Message[];
  isStreaming?: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isStreaming = false }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  /**
   * Auto-scroll to bottom when new messages arrive
   */
  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  /**
   * Smooth scroll to bottom of messages
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Format timestamp for display
   */
  const formatTime = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  };

  /**
   * Render empty state when no messages
   */
  const renderEmptyState = () => (
    <div className={styles.emptyState}>
      <div className={styles.emptyStateIcon}>🤖</div>
      <h3 className={styles.emptyStateTitle}>Welcome to Textbook Assistant</h3>
      <p className={styles.emptyStateText}>
        Ask me anything about Physical AI, Humanoid Robotics, or ROS 2. I can help you
        understand concepts, find relevant sections, and answer your questions.
      </p>
      <div className={styles.emptyStateSuggestions}>
        <button
          className={styles.suggestionButton}
          onClick={() => handleSuggestionClick('What is Physical AI?')}
        >
          What is Physical AI?
        </button>
        <button
          className={styles.suggestionButton}
          onClick={() => handleSuggestionClick('How do I get started with ROS 2?')}
        >
          How do I get started with ROS 2?
        </button>
        <button
          className={styles.suggestionButton}
          onClick={() => handleSuggestionClick('Explain humanoid robot locomotion')}
        >
          Explain humanoid robot locomotion
        </button>
      </div>
    </div>
  );

  /**
   * Handle suggestion click (placeholder - parent should handle)
   */
  const handleSuggestionClick = (suggestion: string) => {
    // This would need to be passed from parent component
    console.log('Suggestion clicked:', suggestion);
  };

  /**
   * Render typing indicator
   */
  const renderTypingIndicator = () => (
    <div className={`${styles.messageWrapper} ${styles.assistant}`}>
      <div className={`${styles.avatar} ${styles.assistant}`}>🤖</div>
      <div className={styles.typingIndicator}>
        <div className={styles.typingDot}></div>
        <div className={styles.typingDot}></div>
        <div className={styles.typingDot}></div>
      </div>
    </div>
  );

  /**
   * Render individual message
   */
  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';

    return (
      <div
        key={message.id}
        className={`${styles.messageWrapper} ${isUser ? styles.user : styles.assistant}`}
      >
        <div className={`${styles.avatar} ${isUser ? styles.user : styles.assistant}`}>
          {isUser ? '👤' : '🤖'}
        </div>

        <div className={styles.messageContent}>
          <div className={`${styles.messageBubble} ${isUser ? styles.user : styles.assistant}`}>
            {message.content}
          </div>

          {/* Render citations if present */}
          {!isUser && message.citations && message.citations.length > 0 && (
            <div className={styles.citations}>
              {message.citations.map((citation, index) => (
                <CitationLink
                  key={citation.id}
                  citation={citation}
                  index={index}
                />
              ))}
            </div>
          )}

          {/* Timestamp */}
          <div className={styles.messageTime}>
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={styles.messagesContainer} ref={containerRef}>
      {messages.length === 0 ? (
        renderEmptyState()
      ) : (
        <>
          {messages.map(renderMessage)}
          {isStreaming && renderTypingIndicator()}
        </>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
