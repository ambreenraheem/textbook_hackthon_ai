// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const {themes} = require('prism-react-renderer');
const lightCodeTheme = themes.github;
const darkCodeTheme = themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A Comprehensive Open-Source Textbook on Physical AI, Humanoid Robotics, and ROS 2',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  // Will be your Vercel URL: https://your-project.vercel.app
  url: 'https://textbook-hackthon-ai.vercel.app',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For Vercel: use '/' (root path)
  baseUrl: '/',

  // GitHub pages deployment config (not used with Vercel)
  organizationName: 'ambreenraheem',
  projectName: 'textbook_hackthon_ai',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: 'docs',
          editUrl: 'https://github.com/ambreenraheem/textbook_hackthon_ai/tree/main/frontend/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  plugins: [
    [
      require.resolve("@cmfcmf/docusaurus-search-local"),
      {
        indexDocs: true,
        indexBlog: false,
        indexPages: false,
        language: "en",
        style: undefined,
        maxSearchResults: 8,
        lunr: {
          tokenizerSeparator: /[\s\-]+/,
          b: 0.75,
          k1: 1.2,
          titleBoost: 5,
          contentBoost: 1,
          tagsBoost: 3,
          parentCategoriesBoost: 2,
        },
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Physical AI & Robotics',
        logo: {
          alt: 'Physical AI Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Textbook',
          },
          {
            type: 'dropdown',
            label: 'Parts',
            position: 'left',
            items: [
              {label: 'Part I: Foundations', to: '/docs/part-01-foundations/ch01-intro-physical-ai'},
              {label: 'Part II: ROS 2', to: '/docs/part-02-ros2/ch05-intro-ros2'},
              {label: 'Part III: Simulation', to: '/docs/part-03-simulation/ch09-gazebo'},
              {label: 'Part IV: Perception', to: '/docs/part-04-perception/ch12-computer-vision'},
              {label: 'Part V: AI & ML', to: '/docs/part-05-ai-ml/ch15-ai-fundamentals'},
              {label: 'Part VI: Motion & Control', to: '/docs/part-06-motion-control/ch19-locomotion'},
              {label: 'Part VII: HRI', to: '/docs/part-07-hri/ch22-hri-fundamentals'},
              {label: 'Part VIII: Deployment', to: '/docs/part-08-deployment/ch25-industrial'},
              {label: 'Part IX: Advanced', to: '/docs/part-09-advanced/ch29-embodied-ai'},
              {label: 'Part X: Projects', to: '/docs/part-10-projects/project-01-ros2-robot'},
            ],
          },
          {
            type: 'search',
            position: 'right',
          },
          {
            type: 'html',
            position: 'right',
            value: '<button class="navbar__item navbar__link" style="background:none;border:none;cursor:pointer;">🌙</button>',
          },
          {
            href: 'https://github.com/ambreenraheem/textbook_hackthon_ai',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Textbook',
            items: [
              {
                label: 'Introduction',
                to: '/docs/intro',
              },
              {
                label: 'Foundations',
                to: '/docs/part-01-foundations/ch01-intro-physical-ai',
              },
              {
                label: 'Projects',
                to: '/docs/part-10-projects/project-01-ros2-robot',
              },
              {
                label: 'Appendices',
                to: '/docs/appendices/appendix-a-ros2-commands',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/ambreenraheem/textbook_hackthon_ai',
              },
              {
                label: 'Issues',
                href: 'https://github.com/ambreenraheem/textbook_hackthon_ai/issues',
              },
              {
                label: 'Discussions',
                href: 'https://github.com/ambreenraheem/textbook_hackthon_ai/discussions',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'ROS 2 Docs',
                href: 'https://docs.ros.org/en/humble/',
              },
              {
                label: 'OpenAI',
                href: 'https://openai.com/',
              },
              {
                label: 'Panaversity',
                href: 'https://www.panaversity.com',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Licensed under CC BY-NC-SA 4.0. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'cpp', 'c', 'yaml', 'json'],
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      announcementBar: {
        id: 'support_us',
        content:
          '⭐️ If you find this textbook useful, please give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/ambreenraheem/textbook_hackthon_ai">GitHub</a>!',
        backgroundColor: '#fafbfc',
        textColor: '#091E42',
        isCloseable: true,
      },
    }),
};

module.exports = config;
