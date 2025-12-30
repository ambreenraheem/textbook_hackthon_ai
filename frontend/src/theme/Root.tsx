/**
 * Root Theme Wrapper
 * Injects ChatbotWidget and TextSelection globally into all Docusaurus pages
 * Handles session management, state persistence, and text selection integration
 *
 * Performance: Uses React.lazy for code splitting to reduce initial bundle size
 */

import React, { ReactNode, useState, useCallback, lazy, Suspense } from 'react';
import { WidgetState } from '../types/chat';

// Lazy load components for code splitting
const ChatbotWidget = lazy(() => import('../components/ChatbotWidget'));
const TextSelection = lazy(() => import('../components/TextSelection'));

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

      {/* Lazy-loaded components with Suspense for code splitting */}
      <Suspense fallback={null}>
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
      </Suspense>
    </>
  );
};

export default Root;
