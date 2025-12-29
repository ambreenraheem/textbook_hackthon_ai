/**
 * TypeScript type definitions for the chatbot widget
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  isStreaming?: boolean;
}

export interface Citation {
  id: string;
  chapter: string;
  section: string;
  url: string;
  text: string;
}

export interface ChatSession {
  sessionId: string;
  messages: Message[];
  createdAt: Date;
  lastUpdatedAt: Date;
}

export interface SSEEvent {
  type: 'token' | 'citation' | 'done' | 'error';
  data: string;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatError {
  message: string;
  code?: string;
  details?: string;
}

export type WidgetState = 'minimized' | 'expanded' | 'hidden';

export interface ChatbotConfig {
  apiUrl?: string;
  maxMessageLength?: number;
  placeholder?: string;
  welcomeMessage?: string;
  enableCitations?: boolean;
  position?: 'bottom-right' | 'bottom-left';
}
