# Docusaurus Developer Skill

## Metadata
- **Skill Name**: docusaurus-developer
- **Job**: Docusaurus book/documentation site development
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Sets up, configures, and manages Docusaurus-based textbook websites for educational content delivery.

## Example Tasks
- Initialize new Docusaurus project with custom configuration
- Create book structure with chapters and sections
- Configure navigation, sidebars, and table of contents
- Customize theme for educational content
- Add MDX support for interactive components
- Configure search functionality
- Optimize site performance and SEO

## Required Knowledge
- Docusaurus v3.x framework
- React and MDX
- Node.js and npm/yarn
- Markdown authoring
- Static site generation
- Documentation best practices

## Key Technologies
- Docusaurus 3.x
- React 18+
- MDX (Markdown + JSX)
- Node.js
- TypeScript (optional)

## Workflow Steps
1. **Initialize Project**
   ```bash
   npx create-docusaurus@latest textbook-site classic --typescript
   cd textbook-site
   ```

2. **Configure Structure**
   - Set up `docusaurus.config.js` with project metadata
   - Configure sidebar for textbook chapters
   - Set up docs structure in `/docs` directory

3. **Customize Theme**
   - Configure theme colors and branding
   - Add custom CSS for educational layout
   - Configure navbar and footer

4. **Content Organization**
   - Create chapter directories
   - Set up front matter templates
   - Configure versioning if needed

5. **Testing**
   ```bash
   npm start  # Local development
   npm run build  # Production build
   ```

## Integration Points
- **frontend-designer**: Provides UI/UX requirements
- **content-writer**: Receives content to structure
- **deployment-expert**: Hands off build artifacts
- **chatbot-engineer**: Prepares integration points for chatbot

## Success Criteria
- [ ] Docusaurus site runs locally without errors
- [ ] Navigation and sidebar work correctly
- [ ] All pages render properly
- [ ] Search functionality works
- [ ] Build completes without errors
- [ ] Site is optimized for mobile and desktop

## Common Commands
```bash
# Development
npm start

# Build
npm run build

# Serve production build
npm run serve

# Deploy
npm run deploy
```

## Best Practices
- Use semantic versioning for documentation versions
- Follow accessibility guidelines (WCAG 2.1)
- Optimize images and media files
- Use MDX components for interactive elements
- Implement proper meta tags for SEO
- Keep dependencies updated

## Output Artifacts
- `docusaurus.config.js` - Main configuration
- `sidebars.js` - Navigation structure
- `/docs` directory - Content structure
- `/src` directory - Custom components
- `/static` directory - Static assets
