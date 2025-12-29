import React from 'react';

export default function InteractiveDiagram({ title, children }) {
  return (
    <div style={{
      border: '2px dashed #ccc',
      padding: '1rem',
      margin: '1rem 0',
      borderRadius: '8px',
      backgroundColor: '#f9f9f9'
    }}>
      <p style={{ fontStyle: 'italic', color: '#666' }}>
        Interactive Diagram: {title || 'Coming Soon'}
      </p>
      {children}
    </div>
  );
}
