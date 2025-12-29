/**
 * CitationLink Component
 * Displays clickable citation badges that scroll to referenced sections
 */

import React, { useState } from 'react';
import { Citation } from '../../types/chat';
import styles from './styles.module.css';

interface CitationLinkProps {
  citation: Citation;
  index: number;
}

const CitationLink: React.FC<CitationLinkProps> = ({ citation, index }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  /**
   * Handle citation click - navigate to the referenced section
   */
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();

    // Extract the path from citation URL
    const url = citation.url;

    // Check if we're already on the target page
    const currentPath = window.location.pathname;
    const targetPath = url.split('#')[0];
    const hash = url.split('#')[1];

    if (currentPath === targetPath && hash) {
      // Same page - just scroll to element
      scrollToElement(hash);
    } else {
      // Different page - navigate
      window.location.href = url;
    }
  };

  /**
   * Scroll to element and highlight it
   */
  const scrollToElement = (elementId: string) => {
    const element = document.getElementById(elementId);

    if (element) {
      // Smooth scroll to element
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });

      // Highlight the section temporarily
      highlightElement(element);
    }
  };

  /**
   * Temporarily highlight the target element
   */
  const highlightElement = (element: HTMLElement) => {
    const originalBackground = element.style.backgroundColor;
    const originalTransition = element.style.transition;

    // Add highlight
    element.style.transition = 'background-color 0.3s ease';
    element.style.backgroundColor = 'rgba(46, 133, 85, 0.2)';

    // Remove highlight after 2 seconds
    setTimeout(() => {
      element.style.backgroundColor = originalBackground;

      // Restore original transition after animation
      setTimeout(() => {
        element.style.transition = originalTransition;
      }, 300);
    }, 2000);
  };

  /**
   * Format chapter and section for display
   */
  const getDisplayText = (): string => {
    const chapterNum = citation.chapter.match(/\d+/)?.[0];
    const sectionNum = citation.section.match(/\d+(\.\d+)?/)?.[0];

    if (chapterNum && sectionNum) {
      return `Ch${chapterNum}.${sectionNum}`;
    } else if (chapterNum) {
      return `Ch${chapterNum}`;
    } else {
      return `[${index + 1}]`;
    }
  };

  return (
    <a
      href={citation.url}
      className={styles.citationBadge}
      onClick={handleClick}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      onFocus={() => setShowTooltip(true)}
      onBlur={() => setShowTooltip(false)}
      aria-label={`Citation ${index + 1}: ${citation.chapter}, ${citation.section}`}
      title={`${citation.chapter} - ${citation.section}`}
    >
      <span>📖</span>
      <span>{getDisplayText()}</span>
    </a>
  );
};

export default CitationLink;
