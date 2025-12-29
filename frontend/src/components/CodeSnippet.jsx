import React from 'react';

export default function CodeSnippet({ language, children }) {
  return (
    <pre style={{
      backgroundColor: '#f5f5f5',
      padding: '1rem',
      borderRadius: '8px',
      overflowX: 'auto',
      margin: '1rem 0'
    }}>
      <code className={`language-${language || 'text'}`}>
        {children}
      </code>
    </pre>
  );
}
