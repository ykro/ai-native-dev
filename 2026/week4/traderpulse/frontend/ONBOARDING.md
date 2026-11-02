# Frontend Developer Onboarding

Welcome to the TraderPulse Frontend! This guide provides a comprehensive overview of our Next.js architecture and development practices.

## 1. Quick Setup

### Prerequisites
- **Node.js 20+**
- **npm** (comes with Node)

### Environment Setup
1.  **Navigate**:
    ```bash
    cd frontend
    ```
2.  **Install**:
    ```bash
    npm install
    ```
3.  **Environment**:
    (Optional) Create `.env.local`:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ```
4.  **Run**:
    ```bash
    npm run dev
    ```
    Open `http://localhost:3000`.

---

## 2. Understanding the Tech Stack

- **Next.js 16 (App Router)**: We use the modern App Router.
    - **Server Components (RSC)**: The default. Used for layouts and initial page shells.
    - **Client Components (`'use client'`)**: Used for anything interactive (hooks, state, event listeners).
- **Styling**: **Tailwind CSS v4** + **shadcn/ui**.
    - We don't write custom CSS files (mostly). We use utility classes.
- **Data Fetching**: **SWR**.
    - We use `useSWR` in Client Components for real-time polling and caching.

## 3. Project Structure Deep Dive

```
frontend/
├── public/              # Static assets (images, icons).
├── src/
│   ├── app/             # App Router Pages.
│   │   ├── layout.tsx   # Root layout (Html, Body, Providers).
│   │   ├── page.tsx     # Homepage (Dashboard).
│   │   └── globals.css  # Global styles & Tailwind directives.
│   ├── components/
│   │   ├── ui/          # Generic UI (Button, Input, Card). From shadcn.
│   │   └── dashboard/   # Domain Components.
│   │       ├── MarketChart.tsx
│   │       ├── TickerTape.tsx
│   │       └── SentimentWidget.tsx
│   └── lib/             # Utilities.
│       └── utils.ts     # Helper for tailwind class merging (cn).
```

## 4. Common Workflows

### How to Create a New Page?
1.  Create a folder in `src/app/`, e.g., `src/app/news/`.
2.  Add a `page.tsx` inside it.
3.  Export a default React component.
4.  It will be accessible at `/news`.

### How to Create a Component?
1.  **Generic UI**: If it's a button, card, or input, check `src/components/ui`. If missing, check [shadcn/ui docs](https://ui.shadcn.com/) to see if we can add it.
2.  **Feature Component**: Create in `src/components/dashboard/` (or a new feature folder).
3.  **Client vs Server**:
    - If it uses `useState`, `useEffect`, `useSWR`, or `onClick`: Add `'use client'` at the very top.
    - Otherwise, keep it as a Server Component.

### How to Fetch Data?
- **Client Side (Recommended for Dashboard)**:
    ```tsx
    'use client';
    import useSWR from 'swr';
    
    // fetcher function wrapper
    const fetcher = (url) => fetch(url).then(res => res.json());

    export default function MyWidget() {
        const { data, error } = useSWR('http://.../api', fetcher);
        if (!data) return <div>Loading...</div>;
        return <div>{data.value}</div>;
    }
    ```

## 5. Styling Guide

- **Utility First**: Use utility classes (e.g., `flex`, `p-4`, `text-red-500`).
- **Colors**: Use semantic names from our theme (defined in `globals.css`):
    - `bg-background`, `text-foreground`
    - `border-border`
    - `text-primary`, `bg-secondary`
- **Conditionals**: Use the `cn()` utility to merge classes conditionally.
    ```tsx
    import { cn } from "@/lib/utils";
    
    <div className={cn("base-class", isActive && "active-class")} />
    ```

## 6. Debugging

- **Chrome DevTools**: The Console is your best friend for Client Components.
- **React DevTools Extension**: Highly recommended to inspect Component props and state.
- **Network Tab**: Inspect API calls to ensure the Backend is returning what you expect.
