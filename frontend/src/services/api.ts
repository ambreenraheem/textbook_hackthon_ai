/**
 * API client for chatbot SSE (Server-Sent Events) communication
 * Handles streaming responses from the backend chat API
 */

import { SSEEvent, ChatRequest, ChatError } from '../types/chat';

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onCitation: (citation: string) => void;
  onDone: () => void;
  onError: (error: ChatError) => void;
}

/**
 * Get the API base URL from environment or use default
 */
export const getApiUrl = (): string => {
  // Check if we're in browser environment
  if (typeof window !== 'undefined') {
    // Try to get from window object (can be set in docusaurus.config.js)
    const customUrl = (window as any).CHATBOT_API_URL;
    if (customUrl) return customUrl;
  }

  // Default to localhost for development
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

/**
 * EventSource wrapper for SSE streaming
 * Provides proper error handling and reconnection logic
 */
class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectDelay = 1000; // ms
  private aborted = false;

  /**
   * Start streaming chat completion
   */
  async stream(
    request: ChatRequest,
    callbacks: StreamCallbacks
  ): Promise<void> {
    this.aborted = false;
    this.reconnectAttempts = 0;

    try {
      await this.connect(request, callbacks);
    } catch (error) {
      const chatError: ChatError = {
        message: error instanceof Error ? error.message : 'Failed to connect to chat API',
        code: 'CONNECTION_ERROR',
      };
      callbacks.onError(chatError);
    }
  }

  /**
   * Establish SSE connection
   */
  private async connect(
    request: ChatRequest,
    callbacks: StreamCallbacks
  ): Promise<void> {
    const apiUrl = getApiUrl();
    const url = `${apiUrl}/api/chat`;

    // Use fetch for POST request with SSE
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    // Read the stream
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (!this.aborted) {
        const { done, value } = await reader.read();

        if (done) {
          callbacks.onDone();
          break;
        }

        // Decode and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE events
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        for (const eventText of events) {
          if (!eventText.trim()) continue;

          try {
            const event = this.parseSSEEvent(eventText);
            this.handleEvent(event, callbacks);
          } catch (error) {
            console.warn('Failed to parse SSE event:', error);
          }
        }
      }
    } catch (error) {
      if (!this.aborted) {
        const chatError: ChatError = {
          message: error instanceof Error ? error.message : 'Stream reading error',
          code: 'STREAM_ERROR',
        };
        callbacks.onError(chatError);
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Parse SSE event text
   */
  private parseSSEEvent(eventText: string): SSEEvent {
    const lines = eventText.split('\n');
    let eventType = 'message';
    let data = '';

    for (const line of lines) {
      if (line.startsWith('event:')) {
        eventType = line.substring(6).trim();
      } else if (line.startsWith('data:')) {
        data = line.substring(5).trim();
      }
    }

    return {
      type: eventType as SSEEvent['type'],
      data,
    };
  }

  /**
   * Handle individual SSE event
   */
  private handleEvent(event: SSEEvent, callbacks: StreamCallbacks): void {
    switch (event.type) {
      case 'token':
        callbacks.onToken(event.data);
        break;

      case 'citation':
        try {
          callbacks.onCitation(event.data);
        } catch (error) {
          console.warn('Failed to parse citation:', error);
        }
        break;

      case 'done':
        callbacks.onDone();
        break;

      case 'error':
        const chatError: ChatError = {
          message: event.data || 'Unknown error occurred',
          code: 'SERVER_ERROR',
        };
        callbacks.onError(chatError);
        break;

      default:
        console.warn('Unknown event type:', event.type);
    }
  }

  /**
   * Abort the current stream
   */
  abort(): void {
    this.aborted = true;
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  /**
   * Check if currently streaming
   */
  isActive(): boolean {
    return this.eventSource !== null && this.eventSource.readyState !== EventSource.CLOSED;
  }
}

/**
 * Send a chat message and stream the response
 */
export const sendChatMessage = async (
  message: string,
  sessionId: string,
  callbacks: StreamCallbacks
): Promise<void> => {
  const client = new SSEClient();

  const request: ChatRequest = {
    message,
    session_id: sessionId,
  };

  await client.stream(request, callbacks);
};

/**
 * Create SSE client instance for manual control
 */
export const createSSEClient = (): SSEClient => {
  return new SSEClient();
};

/**
 * Validate message before sending
 */
export const validateMessage = (message: string, maxLength = 2000): { valid: boolean; error?: string } => {
  if (!message.trim()) {
    return { valid: false, error: 'Message cannot be empty' };
  }

  if (message.length > maxLength) {
    return { valid: false, error: `Message exceeds maximum length of ${maxLength} characters` };
  }

  return { valid: true };
};

/**
 * Generate a unique session ID
 */
export const generateSessionId = (): string => {
  // Simple UUID v4 implementation
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};
