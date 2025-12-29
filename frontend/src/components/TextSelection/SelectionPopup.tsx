import React from 'react';
import styles from './styles.module.css';

interface SelectionPopupProps {
  position: { x: number; y: number };
  onAskAbout: () => void;
}

export default function SelectionPopup({ position, onAskAbout }: SelectionPopupProps) {
  return (
    <div
      className={styles.selectionPopup}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <button
        className={styles.askButton}
        onClick={onAskAbout}
        aria-label="Ask chatbot about this text"
      >
        💬 Ask about this
      </button>
    </div>
  );
}
