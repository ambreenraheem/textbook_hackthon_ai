# Content Writer Skill

## Metadata
- **Skill Name**: content-writer
- **Job**: Technical content creation for Physical AI & Humanoid Robotics textbook
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Creates, organizes, and maintains high-quality educational content for the Physical AI & Humanoid Robotics textbook, ensuring technical accuracy and pedagogical effectiveness.

## Example Tasks
- Write comprehensive chapters on robotics fundamentals
- Create tutorials and hands-on exercises
- Develop code examples and demonstrations
- Write glossary and reference materials
- Create learning objectives and assessment questions
- Structure content with proper headings and organization
- Add diagrams, images, and multimedia references

## Required Knowledge
- Physical AI and Humanoid Robotics domain expertise
- Technical writing and pedagogy
- Markdown and MDX syntax
- Educational content design
- Code documentation standards
- Academic citation practices

## Key Technologies
- Markdown/MDX
- Mermaid diagrams
- LaTeX for mathematical notation
- Code syntax highlighting
- Image optimization tools

## Content Structure
```
docs/
├── 01-introduction/
│   ├── index.md
│   ├── what-is-physical-ai.md
│   └── course-overview.md
├── 02-fundamentals/
│   ├── robotics-basics.md
│   ├── sensors-actuators.md
│   └── control-systems.md
├── 03-ai-integration/
│   ├── machine-learning-basics.md
│   ├── computer-vision.md
│   └── reinforcement-learning.md
├── 04-humanoid-robotics/
│   ├── bipedal-locomotion.md
│   ├── manipulation.md
│   └── human-robot-interaction.md
├── 05-practical-projects/
│   └── ...
└── glossary.md
```

## Workflow Steps
1. **Plan Content**
   - Define learning objectives
   - Create content outline
   - Identify prerequisites

2. **Write Content**
   - Follow MDX best practices
   - Include code examples
   - Add diagrams and visuals
   - Write clear explanations

3. **Add Interactive Elements**
   - Code sandboxes
   - Quizzes and exercises
   - Interactive diagrams
   - Video embeds

4. **Review and Edit**
   - Technical accuracy check
   - Grammar and clarity review
   - Code validation
   - Accessibility check

## Front Matter Template
```yaml
---
id: topic-name
title: Chapter Title
sidebar_label: Short Label
sidebar_position: 1
description: Brief description for SEO
keywords: [physical ai, robotics, humanoid]
---
```

## Integration Points
- **docusaurus-developer**: Receives content structure requirements
- **frontend-designer**: Collaborates on content presentation
- **chatbot-engineer**: Provides content for RAG system
- **rag-specialist**: Ensures content is RAG-optimized

## Success Criteria
- [ ] All chapters have clear learning objectives
- [ ] Content follows consistent style guide
- [ ] Code examples are tested and working
- [ ] All images have alt text
- [ ] Mathematical notation renders correctly
- [ ] Links and references are valid
- [ ] Content is optimized for RAG retrieval

## Writing Guidelines
- Use clear, concise language
- Define technical terms on first use
- Include practical examples
- Add cross-references between chapters
- Use consistent terminology
- Follow academic citation standards
- Optimize headings for search and RAG

## MDX Components Usage
```mdx
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import CodeBlock from '@theme/CodeBlock';

## Example Section

<Tabs>
  <TabItem value="python" label="Python">
    ```python
    # Code example
    ```
  </TabItem>
  <TabItem value="cpp" label="C++">
    ```cpp
    // Code example
    ```
  </TabItem>
</Tabs>
```

## Best Practices
- Write for diverse learning styles
- Include real-world applications
- Provide graduated difficulty
- Add summaries and key takeaways
- Use active voice
- Break complex topics into digestible chunks
- Include troubleshooting sections

## Output Artifacts
- Markdown/MDX files for each chapter
- Code examples in `/src/examples`
- Images and diagrams in `/static/img`
- Glossary and reference materials
- Assessment questions and exercises
