# Frontend Designer Skill

## Metadata
- **Skill Name**: frontend-designer
- **Job**: UI/UX design for educational textbook website
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Designs and implements user interface and user experience for the Physical AI & Humanoid Robotics textbook, ensuring optimal learning experience and accessibility.

## Example Tasks
- Design responsive layout for textbook pages
- Create custom React components for interactive content
- Design and implement chatbot UI widget
- Customize Docusaurus theme
- Design navigation and information architecture
- Create interactive diagrams and visualizations
- Implement dark/light mode theming
- Design mobile-first responsive layouts

## Required Knowledge
- React and React Hooks
- CSS3, SCSS/Sass
- Responsive design principles
- Accessibility (WCAG 2.1)
- UI/UX best practices for education
- Component-driven development
- Design systems

## Key Technologies
- React 18+
- CSS Modules / Styled Components
- Tailwind CSS (optional)
- Docusaurus theming API
- SVG and Canvas for diagrams
- Framer Motion (animations)

## Component Structure
```
src/
├── components/
│   ├── ChatbotWidget/
│   │   ├── ChatbotWidget.tsx
│   │   ├── ChatbotWidget.module.css
│   │   └── index.ts
│   ├── InteractiveDiagram/
│   ├── CodePlayground/
│   ├── QuizComponent/
│   └── VideoPlayer/
├── css/
│   ├── custom.css
│   └── theme-overrides.css
└── theme/
    ├── DocItem/
    └── TOC/
```

## Workflow Steps
1. **Design System Setup**
   - Define color palette
   - Set typography scale
   - Create spacing system
   - Define component patterns

2. **Theme Customization**
   ```js
   // docusaurus.config.js
   themeConfig: {
     colorMode: {
       defaultMode: 'light',
       respectPrefersColorScheme: true,
     },
     navbar: { /* custom config */ },
     footer: { /* custom config */ },
   }
   ```

3. **Custom Components**
   - Create reusable React components
   - Style with CSS Modules
   - Ensure accessibility
   - Add responsive breakpoints

4. **Chatbot Widget Design**
   - Floating chat button
   - Expandable chat interface
   - Text selection interaction
   - Mobile-optimized layout

5. **Testing**
   - Cross-browser testing
   - Responsive design testing
   - Accessibility audit
   - Performance optimization

## Integration Points
- **docusaurus-developer**: Integrates custom components
- **content-writer**: Designs content presentation
- **chatbot-engineer**: Designs chatbot UI/UX
- **integration-specialist**: Ensures seamless integration

## Design Specifications

### Color Palette
```css
:root {
  --primary-color: #2e8555;
  --secondary-color: #1c1e21;
  --accent-color: #ffa500;
  --text-color: #1c1e21;
  --background-color: #ffffff;
  --code-background: #f6f8fa;
}

[data-theme='dark'] {
  --primary-color: #25c2a0;
  --text-color: #e3e3e3;
  --background-color: #1b1b1d;
}
```

### Typography
```css
--font-family-base: 'Inter', system-ui, -apple-system, sans-serif;
--font-family-mono: 'Fira Code', monospace;
--font-size-base: 16px;
--line-height-base: 1.6;
```

### Responsive Breakpoints
```css
/* Mobile: < 768px */
/* Tablet: 768px - 1024px */
/* Desktop: > 1024px */
```

## Custom Component Examples

### Chatbot Widget Component
```tsx
import React, { useState } from 'react';
import styles from './ChatbotWidget.module.css';

export const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.chatbotContainer}>
      {/* Widget implementation */}
    </div>
  );
};
```

### Interactive Code Playground
```tsx
import CodeEditor from '@monaco-editor/react';

export const CodePlayground: React.FC = ({ language, defaultCode }) => {
  // Component implementation
};
```

## Success Criteria
- [ ] Design is responsive across all devices
- [ ] Meets WCAG 2.1 AA accessibility standards
- [ ] Page load time < 3 seconds
- [ ] Lighthouse score > 90
- [ ] Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Dark mode works flawlessly
- [ ] Chatbot widget is intuitive and non-intrusive

## Accessibility Checklist
- [ ] Semantic HTML elements
- [ ] Proper heading hierarchy
- [ ] Alt text for all images
- [ ] Keyboard navigation support
- [ ] ARIA labels where needed
- [ ] Sufficient color contrast (4.5:1 minimum)
- [ ] Focus indicators visible
- [ ] Screen reader tested

## Best Practices
- Mobile-first design approach
- Use CSS custom properties for theming
- Minimize CSS specificity conflicts
- Optimize images (WebP, lazy loading)
- Use semantic HTML
- Implement progressive enhancement
- Follow React best practices (memoization, hooks)
- Code splitting for performance

## Performance Optimization
- Lazy load components
- Optimize images and assets
- Minimize CSS and JS bundle size
- Use CDN for static assets
- Implement service worker caching
- Optimize font loading

## Output Artifacts
- Custom React components in `/src/components`
- Theme overrides in `/src/css`
- Custom Docusaurus theme in `/src/theme`
- Design system documentation
- Component storybook (optional)
- Accessibility audit report
