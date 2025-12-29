/**
 * Creating a sidebar enables you to:
 * - create an ordered group of docs
 * - render a sidebar for each doc of that group
 * - provide next/previous navigation
 *
 * The sidebars can be generated from the filesystem, or explicitly defined here.
 *
 * Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: 'Introduction',
    },
    {
      type: 'category',
      label: 'Part I: Foundations',
      collapsed: false,
      items: [
        'part-01-foundations/ch01-intro-physical-ai',
        'part-01-foundations/ch02-humanoid-robotics',
        'part-01-foundations/ch03-math-fundamentals',
        'part-01-foundations/ch04-physics-robotics',
      ],
    },
    {
      type: 'category',
      label: 'Part II: ROS 2 Fundamentals',
      collapsed: true,
      items: [
        'part-02-ros2/ch05-intro-ros2',
        'part-02-ros2/ch06-ros2-concepts',
        'part-02-ros2/ch07-communication-patterns',
        'part-02-ros2/ch08-ros2-humanoid-control',
      ],
    },
    {
      type: 'category',
      label: 'Part III: Simulation & Visualization',
      collapsed: true,
      items: [
        'part-03-simulation/ch09-gazebo',
        'part-03-simulation/ch10-unity',
        'part-03-simulation/ch11-nvidia-isaac',
      ],
    },
    {
      type: 'category',
      label: 'Part IV: Perception & Sensing',
      collapsed: true,
      items: [
        'part-04-perception/ch12-computer-vision',
        'part-04-perception/ch13-sensor-integration',
        'part-04-perception/ch14-human-detection',
      ],
    },
    {
      type: 'category',
      label: 'Part V: AI & Machine Learning',
      collapsed: true,
      items: [
        'part-05-ai-ml/ch15-ai-fundamentals',
        'part-05-ai-ml/ch16-reinforcement-learning',
        'part-05-ai-ml/ch17-llm-robots',
        'part-05-ai-ml/ch18-vla-models',
      ],
    },
    {
      type: 'category',
      label: 'Part VI: Motion & Control',
      collapsed: true,
      items: [
        'part-06-motion-control/ch19-locomotion',
        'part-06-motion-control/ch20-manipulation',
        'part-06-motion-control/ch21-whole-body-control',
      ],
    },
    {
      type: 'category',
      label: 'Part VII: Human-Robot Interaction',
      collapsed: true,
      items: [
        'part-07-hri/ch22-hri-fundamentals',
        'part-07-hri/ch23-interaction-modalities',
        'part-07-hri/ch24-teleoperation',
      ],
    },
    {
      type: 'category',
      label: 'Part VIII: Deployment & Applications',
      collapsed: true,
      items: [
        'part-08-deployment/ch25-industrial',
        'part-08-deployment/ch26-service-domestic',
        'part-08-deployment/ch27-hardware-electronics',
        'part-08-deployment/ch28-production',
      ],
    },
    {
      type: 'category',
      label: 'Part IX: Advanced Topics',
      collapsed: true,
      items: [
        'part-09-advanced/ch29-embodied-ai',
        'part-09-advanced/ch30-multi-robot',
        'part-09-advanced/ch31-safety-ethics',
        'part-09-advanced/ch32-future-physical-ai',
      ],
    },
    {
      type: 'category',
      label: 'Part X: Hands-On Projects',
      collapsed: true,
      items: [
        'part-10-projects/project-01-ros2-robot',
        'part-10-projects/project-02-humanoid-sim',
        'part-10-projects/project-03-conversational-robot',
        'part-10-projects/project-04-vision-manipulation',
        'part-10-projects/project-05-complete-humanoid',
      ],
    },
    {
      type: 'category',
      label: 'Appendices',
      collapsed: true,
      items: [
        'appendices/appendix-a-ros2-commands',
        'appendices/appendix-b-python-guide',
        'appendices/appendix-c-cpp-guide',
        'appendices/appendix-d-linux-essentials',
        'appendices/appendix-e-hardware-comparison',
        'appendices/appendix-f-datasets-resources',
        'appendices/appendix-g-industry-standards',
        'appendices/appendix-h-troubleshooting',
      ],
    },
  ],
};

module.exports = sidebars;
