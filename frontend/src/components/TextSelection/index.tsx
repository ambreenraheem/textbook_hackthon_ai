import React, { useEffect, useState } from 'react';
import SelectionPopup from './SelectionPopup';
import styles from './styles.module.css';

interface TextSelectionProps {
  onTextSelected: (text: string) => void;
  minLength?: number;
  maxLength?: number;
  enabled?: boolean;
}

export default function TextSelection({
  onTextSelected,
  minLength = 10,
  maxLength = 500,
  enabled = true
}: TextSelectionProps) {
  const [selectedText, setSelectedText] = useState('');
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });
  const [showPopup, setShowPopup] = useState(false);

  useEffect(() => {
    if (!enabled) return;

    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length >= minLength && text.length <= maxLength) {
        setSelectedText(text);

        const range = selection?.getRangeAt(0);
        const rect = range?.getBoundingClientRect();

        if (rect) {
          setPopupPosition({
            x: rect.left + rect.width / 2,
            y: rect.top - 10,
          });
          setShowPopup(true);
        }
      } else {
        setShowPopup(false);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, [enabled, minLength, maxLength]);

  const handleAskAbout = () => {
    onTextSelected(selectedText);
    setShowPopup(false);
    window.getSelection()?.removeAllRanges();
  };

  return (
    <>
      {showPopup && (
        <SelectionPopup
          position={popupPosition}
          onAskAbout={handleAskAbout}
        />
      )}
    </>
  );
}
