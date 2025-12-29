/**
 * Root Theme Wrapper
 * Injects ChatbotWidget globally into all Docusaurus pages
 * Handles session management and state persistence
 */

import React, { ReactNode } from 'react';
import ChatbotWidget from '../components/ChatbotWidget';

interface RootProps {
  children: ReactNode;
}

/**
 * Root wrapper component for Docusaurus theme
 * This component wraps all pages and injects the chatbot widget
 */
const Root: React.FC<RootProps> = ({ children }) => {
  return (
    <>
      {children}
      <ChatbotWidget initialState="minimized" />
    </>
  );
};

export default Root;
