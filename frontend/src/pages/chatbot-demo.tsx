/**
 * Chatbot Demo Page
 * Showcases the chatbot widget features and provides testing interface
 */

import React from 'react';
import Layout from '@theme/Layout';
import styles from './chatbot-demo.module.css';

export default function ChatbotDemo(): JSX.Element {
  return (
    <Layout
      title="Chatbot Demo"
      description="Interactive demo of the AI-powered chatbot widget"
    >
      <div className={styles.demoPage}>
        {/* Hero Section */}
        <section className={styles.hero}>
          <div className={styles.container}>
            <h1 className={styles.title}>🤖 AI Chatbot Assistant</h1>
            <p className={styles.subtitle}>
              Your intelligent companion for learning Physical AI and Humanoid Robotics
            </p>
            <div className={styles.notice}>
              <span className={styles.noticeIcon}>💬</span>
              <span>
                Click the chat button in the bottom-right corner to start a conversation!
              </span>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section className={styles.features}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Features</h2>

            <div className={styles.featureGrid}>
              {/* Real-time Streaming */}
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>⚡</div>
                <h3>Real-time Streaming</h3>
                <p>
                  Watch responses appear word-by-word as the AI generates answers,
                  providing a natural conversational experience.
                </p>
              </div>

              {/* Smart Citations */}
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>📚</div>
                <h3>Smart Citations</h3>
                <p>
                  Click citation badges to jump directly to relevant textbook sections,
                  with automatic highlighting and smooth scrolling.
                </p>
              </div>

              {/* Conversation History */}
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>💾</div>
                <h3>Conversation History</h3>
                <p>
                  Your conversations are automatically saved and persist across page
                  navigations within the same session.
                </p>
              </div>

              {/* Responsive Design */}
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>📱</div>
                <h3>Responsive Design</h3>
                <p>
                  Works seamlessly on desktop (floating widget) and mobile devices
                  (full-screen modal) with touch-friendly controls.
                </p>
              </div>

              {/* Dark Mode */}
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>🌙</div>
                <h3>Dark Mode Support</h3>
                <p>
                  Automatically adapts to your theme preference with beautiful styling
                  in both light and dark modes.
                </p>
              </div>

              {/* Accessibility */}
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>♿</div>
                <h3>Accessibility First</h3>
                <p>
                  Full keyboard navigation, screen reader support, and ARIA labels
                  ensure everyone can use the chatbot.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Try It Out */}
        <section className={styles.tryItOut}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Try It Out</h2>

            <div className={styles.exampleQuestions}>
              <p className={styles.exampleIntro}>
                Not sure what to ask? Try these example questions:
              </p>

              <div className={styles.questionList}>
                <div className={styles.questionItem}>
                  <span className={styles.questionIcon}>💡</span>
                  <span className={styles.questionText}>
                    What is Physical AI and how does it differ from traditional AI?
                  </span>
                </div>

                <div className={styles.questionItem}>
                  <span className={styles.questionIcon}>🤖</span>
                  <span className={styles.questionText}>
                    How do I get started with ROS 2 for humanoid robotics?
                  </span>
                </div>

                <div className={styles.questionItem}>
                  <span className={styles.questionIcon}>🚶</span>
                  <span className={styles.questionText}>
                    Explain the principles of bipedal locomotion in humanoid robots
                  </span>
                </div>

                <div className={styles.questionItem}>
                  <span className={styles.questionIcon}>👁️</span>
                  <span className={styles.questionText}>
                    What computer vision techniques are used in physical AI?
                  </span>
                </div>

                <div className={styles.questionItem}>
                  <span className={styles.questionIcon}>🧠</span>
                  <span className={styles.questionText}>
                    How does reinforcement learning apply to robot control?
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Technical Details */}
        <section className={styles.technical}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>Technical Details</h2>

            <div className={styles.techGrid}>
              <div className={styles.techCard}>
                <h4>🔧 Technology Stack</h4>
                <ul>
                  <li>React 18 with TypeScript</li>
                  <li>CSS Modules for scoped styling</li>
                  <li>Server-Sent Events (SSE) for streaming</li>
                  <li>Docusaurus 3.x integration</li>
                </ul>
              </div>

              <div className={styles.techCard}>
                <h4>⚡ Performance</h4>
                <ul>
                  <li>~30KB bundle size (gzipped)</li>
                  <li>No heavy dependencies</li>
                  <li>Lazy loading ready</li>
                  <li>Optimized animations</li>
                </ul>
              </div>

              <div className={styles.techCard}>
                <h4>🔒 Privacy & Security</h4>
                <ul>
                  <li>Client-side session management</li>
                  <li>No user authentication required</li>
                  <li>XSS protection built-in</li>
                  <li>CORS-compliant API</li>
                </ul>
              </div>

              <div className={styles.techCard}>
                <h4>⌨️ Keyboard Shortcuts</h4>
                <ul>
                  <li><kbd>Enter</kbd> - Send message</li>
                  <li><kbd>Shift</kbd> + <kbd>Enter</kbd> - New line</li>
                  <li><kbd>Tab</kbd> - Navigate elements</li>
                  <li><kbd>Esc</kbd> - Close (when focused)</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Developer Info */}
        <section className={styles.developer}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>For Developers</h2>

            <div className={styles.devInfo}>
              <div className={styles.codeBlock}>
                <h4>📦 Installation</h4>
                <pre>
                  <code>{`cd frontend
npm install
npm start`}</code>
                </pre>
              </div>

              <div className={styles.codeBlock}>
                <h4>⚙️ Configuration</h4>
                <pre>
                  <code>{`# .env.local
REACT_APP_API_URL=http://localhost:8000`}</code>
                </pre>
              </div>

              <div className={styles.links}>
                <h4>📚 Documentation</h4>
                <ul>
                  <li>
                    <a href="/docs/intro">Textbook Introduction</a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/ambreenraheem/textbook_hackthon_ai/blob/main/frontend/CHATBOT_INTEGRATION.md"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Integration Guide
                    </a>
                  </li>
                  <li>
                    <a
                      href="https://github.com/ambreenraheem/textbook_hackthon_ai"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      GitHub Repository
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
