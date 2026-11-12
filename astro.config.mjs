import { defineConfig, fontProviders } from 'astro/config';

// SITE_URL and BASE_PATH let a fork or custom domain deploy without editing this file.
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://dhavaldoriya.github.io',
  base: process.env.BASE_PATH ?? '/ipo-update',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  fonts: [
    {
      provider: fontProviders.fontsource(),
      name: 'Roboto',
      cssVariable: '--font-roboto',
      weights: [400, 500, 600],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['Arial', 'sans-serif'],
    },
  ],
});
