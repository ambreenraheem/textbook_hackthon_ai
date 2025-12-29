/**
 * Root Theme Wrapper
 * Injects ChatbotWidget and TextSelection globally into all Docusaurus pages
 * Handles session management, state persistence, and text selection integration
 */

import React, { ReactNode, useState, useCallback } from 'react';
import ChatbotWidget from '../components/ChatbotWidget';
import TextSelection from '../components/TextSelection';
import { WidgetState } from '../types/chat';

interface RootProps {
  children: ReactNode;
}

/**
 * Root wrapper component for Docusaurus theme
 * This component wraps all pages and injects the chatbot widget and text selection
 */
const Root: React.FC<RootProps> = ({ children }) => {
  // State for managing selected text and widget state
  const [selectedText, setSelectedText] = useState<string>('');
  const [widgetState, setWidgetState] = useState<WidgetState>('minimized');

  /**
   * Handle text selection from TextSelection component
   * Opens chatbot and passes selected text as context
   */
  const handleTextSelected = useCallback((text: string) => {
    setSelectedText(text);
    setWidgetState('expanded'); // Open chatbot widget
  }, []);

  /**
   * Clear selected text after it's been used
   */
  const handleClearSelectedText = useCallback(() => {
    setSelectedText('');
  }, []);

  return (
    <>
      {children}

      {/* Text Selection popup - shows "Ask about this" when text is selected */}
      <TextSelection
        onTextSelected={handleTextSelected}
        minLength={10}
        maxLength={500}
        enabled={true}
      />

      {/* Chatbot Widget with selected text context */}
      <ChatbotWidget
        initialState={widgetState}
        selectedText={selectedText}
        onSelectedTextUsed={handleClearSelectedText}
      />
    </>
  );
};

export default Root;
