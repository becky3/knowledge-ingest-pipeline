This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## UI/UX Design Implementation

This project features a modern, premium design system built with **Tailwind CSS**.

### Design System
- **Color Palette**: 
  - **Background**: Zinc 50 (#fafafa) / Zinc 950 (#09090b) for dark mode.
  - **Accent**: Indigo 600 (#4f46e5) / Indigo 500 (#6366f1).
  - Designed for high contrast and readability.
- **Typography**: Uses `Geist Sans` and `Geist Mono` for a clean, technical aesthetic.
- **Glassmorphism**: Header and other overlay elements use backdrop blur (`.glass` utility) for a modern feel.

### Components
- **ArticleCard**:
  - Displays article metadata (Title, Date, Summary).
  - Interactive hover state (Lift effect, Shadow, "Read Article" animation).
  - Fully responsive grid layout (1 col mobile, 2 col tablet, 3 col desktop).
- **Header/Footer**:
  - Sticky header for easy navigation.
  - Consistent branding.

### Responsiveness
- The layout is fully responsive, adapting from mobile phones to large desktop screens.
- Grid systems automatically adjust column counts.

## Notion Integration Setup

Create a `.env.local` file in the project root and add the following values:

1.  **NOTION_TOKEN**: Your Notion Internal Integration Token.
2.  **NOTION_DATABASE_ID**: The ID of the Notion database to display.

Example `.env.local`:

```bash
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=...
```
