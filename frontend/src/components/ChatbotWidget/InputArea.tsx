/**
 * InputArea Component
 * Handles user input with multiline support, character limit, and keyboard shortcuts
 */

import React, { useState, useRef, useEffect, KeyboardEvent, ChangeEvent } from 'react';
import styles from './styles.module.css';

interface InputAreaProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

const InputArea: React.FC<InputAreaProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = 'Ask a question about the textbook...',
  maxLength = 2000,
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-resize textarea based on content
   */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  /**
   * Focus input when component mounts
   */
  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  /**
   * Handle input change
   */
  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;

    // Enforce max length
    if (value.length <= maxLength) {
      setMessage(value);
    }
  };

  /**
   * Handle send message
   */
  const handleSend = () => {
    const trimmedMessage = message.trim();

    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  /**
   * Handle keyboard shortcuts
   * - Enter: Send message (if not composing IME input)
   * - Shift+Enter: New line
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Handle IME composition (for languages like Chinese, Japanese)
    if (isComposing) return;

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * Calculate character count percentage
   */
  const getCharacterCountClass = (): string => {
    const percentage = (message.length / maxLength) * 100;

    if (percentage >= 90) {
      return `${styles.characterCount} ${styles.warning}`;
    }

    return styles.characterCount;
  };

  /**
   * Check if send button should be disabled
   */
  const isSendDisabled = (): boolean => {
    return disabled || !message.trim() || message.length > maxLength;
  };

  return (
    <div className={styles.inputContainer}>
      <div className={styles.inputWrapper}>
        <div className={styles.textareaWrapper}>
          <textarea
            ref={textareaRef}
            className={styles.textarea}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onCompositionStart={() => setIsComposing(true)}
            onCompositionEnd={() => setIsComposing(false)}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            aria-label="Message input"
            aria-describedby="character-count"
          />
          <div
            id="character-count"
            className={getCharacterCountClass()}
            aria-live="polite"
          >
            {message.length}/{maxLength}
          </div>
        </div>

        <button
          className={`${styles.sendButton} ${disabled ? styles.loading : ''}`}
          onClick={handleSend}
          disabled={isSendDisabled()}
          aria-label="Send message"
          title={disabled ? 'Please wait...' : 'Send message (Enter)'}
        >
          {disabled ? '' : '➤'}
        </button>
      </div>

      {/* Screen reader instructions */}
      <span className={styles.srOnly}>
        Press Enter to send, Shift+Enter for new line
      </span>
    </div>
  );
};

export default InputArea;
