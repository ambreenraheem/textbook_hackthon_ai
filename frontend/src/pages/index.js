import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Learning
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            to="/docs/part-10-projects/project-01-ros2-robot"
            style={{marginLeft: '1rem'}}>
            View Projects
          </Link>
        </div>
      </div>
    </header>
  );
}

function FeatureList() {
  const features = [
    {
      title: 'Comprehensive Coverage',
      icon: '📚',
      description: (
        <>
          From foundational concepts to advanced topics in Physical AI, Humanoid Robotics,
          ROS 2, perception, motion control, and human-robot interaction.
        </>
      ),
    },
    {
      title: 'Hands-On Projects',
      icon: '🤖',
      description: (
        <>
          5 comprehensive projects including ROS 2 robot control, computer vision,
          autonomous navigation, and full humanoid robot implementation.
        </>
      ),
    },
    {
      title: 'Open Source & Free',
      icon: '💡',
      description: (
        <>
          Licensed under CC BY-NC-SA 4.0, completely free to use, share, and adapt
          for non-commercial educational purposes.
        </>
      ),
    },
    {
      title: 'AI-Powered Learning',
      icon: '🧠',
      description: (
        <>
          Interactive chatbot with RAG (Retrieval-Augmented Generation) for instant
          answers to your questions directly from the textbook content.
        </>
      ),
    },
    {
      title: 'Industry-Relevant',
      icon: '🏭',
      description: (
        <>
          Covers real-world applications in manufacturing, healthcare, service robotics,
          and emerging deployment strategies.
        </>
      ),
    },
    {
      title: 'Modern Stack',
      icon: '⚡',
      description: (
        <>
          Built with ROS 2 Humble, Gazebo simulation, Python/C++, PyTorch,
          and cutting-edge AI/ML frameworks.
        </>
      ),
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {features.map((feature, idx) => (
            <div key={idx} className={clsx('col col--4', styles.feature)}>
              <div className={styles.featureCard}>
                <div className={styles.featureIcon}>{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function TextbookParts() {
  const parts = [
    {
      title: 'Part I: Foundations',
      chapters: '4 Chapters',
      description: 'Introduction to Physical AI, robotics history, mathematics, and Linux essentials',
      link: '/docs/part-01-foundations/ch01-intro-physical-ai',
    },
    {
      title: 'Part II: ROS 2 Fundamentals',
      chapters: '4 Chapters',
      description: 'Master ROS 2 architecture, nodes, topics, services, and actions',
      link: '/docs/part-02-ros2/ch05-intro-ros2',
    },
    {
      title: 'Part III: Simulation',
      chapters: '3 Chapters',
      description: 'Learn Gazebo simulation, URDF modeling, and Isaac Sim',
      link: '/docs/part-03-simulation/ch09-gazebo',
    },
    {
      title: 'Part IV: Perception',
      chapters: '3 Chapters',
      description: 'Computer vision, depth sensing, and sensor fusion techniques',
      link: '/docs/part-04-perception/ch12-computer-vision',
    },
    {
      title: 'Part V: AI & Machine Learning',
      chapters: '4 Chapters',
      description: 'Deep learning, RL, transformers, and multimodal models',
      link: '/docs/part-05-ai-ml/ch15-ai-fundamentals',
    },
    {
      title: 'Part VI: Motion & Control',
      chapters: '3 Chapters',
      description: 'Locomotion, manipulation, trajectory planning, and control systems',
      link: '/docs/part-06-motion-control/ch19-locomotion',
    },
    {
      title: 'Part VII: Human-Robot Interaction',
      chapters: '3 Chapters',
      description: 'HRI fundamentals, NLP, speech recognition, and dialogue systems',
      link: '/docs/part-07-hri/ch22-hri-fundamentals',
    },
    {
      title: 'Part VIII: Deployment',
      chapters: '4 Chapters',
      description: 'Industrial applications, healthcare, service robotics, and ethics',
      link: '/docs/part-08-deployment/ch25-industrial',
    },
    {
      title: 'Part IX: Advanced Topics',
      chapters: '4 Chapters',
      description: 'Embodied AI, swarm robotics, space robotics, and future trends',
      link: '/docs/part-09-advanced/ch29-embodied-ai',
    },
    {
      title: 'Part X: Hands-On Projects',
      chapters: '5 Projects',
      description: 'Build complete systems from basic ROS 2 robots to full humanoid implementations',
      link: '/docs/part-10-projects/project-01-ros2-robot',
    },
  ];

  return (
    <section className={styles.partsSection}>
      <div className="container">
        <h2 className={styles.sectionTitle}>Textbook Structure</h2>
        <p className={styles.sectionSubtitle}>
          10 comprehensive parts covering 32 chapters and 5 hands-on projects
        </p>
        <div className="row">
          {parts.map((part, idx) => (
            <div key={idx} className="col col--6">
              <Link to={part.link} className={styles.partCard}>
                <div className={styles.partNumber}>Part {idx + 1}</div>
                <h3>{part.title}</h3>
                <div className={styles.partChapters}>{part.chapters}</div>
                <p>{part.description}</p>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section className={styles.ctaSection}>
      <div className="container">
        <h2>Ready to Build the Future of Robotics?</h2>
        <p>
          Join thousands of students, researchers, and engineers learning Physical AI
          and Humanoid Robotics through this comprehensive open-source textbook.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--primary button--lg"
            to="/docs/intro">
            Get Started Now
          </Link>
          <Link
            className="button button--outline button--primary button--lg"
            to="https://github.com/ambreenraheem/textbook_hackthon_ai"
            style={{marginLeft: '1rem'}}>
            View on GitHub
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A Comprehensive Open-Source Textbook on Physical AI, Humanoid Robotics, and ROS 2">
      <HomepageHeader />
      <main>
        <FeatureList />
        <TextbookParts />
        <CTASection />
      </main>
    </Layout>
  );
}
