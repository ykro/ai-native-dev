# Frontend Architecture

## Component Strategy

We use **Next.js 16 App Router** which creates a clear separation between Server Components and Client Components.

### Server Components
- Used for the initial HTML shell (`layout.tsx`) and SEO-critical content.
- Our usage is currently minimal as the dashboard is highly interactive, but the skeleton is server-rendered.

### Client Components (`'use client'`)
- Most dashboard widgets (`TickerTape`, `MarketChart`, `SentimentWidget`) are client components.
- They handle browser-side interactivity (state, effects, event listeners).

## Key Architectural Decisions

### 1. Framework: Next.js App Router
**Decision**: Adopt the App Router model instead of Pages Router.
**Reasoning**: Future-proofing. The App Router represents the future of React (Server Components). Even though our dashboard is client-heavy, using the modern directory structure (`src/app`) ensures better streaming capabilities and easier layout composition.

### 2. UI Library: Shadcn/UI ("Copy-Paste")
**Decision**: Use **shadcn/ui** instead of a pre-bundled library like MUI or Bootstrap.
**Reasoning**:
- **Ownership**: Components are copied into our `src/components/ui` folder. We own the code. If we need to change how a Button looks or behaves, we just edit the file.
- **Performance**: We only include the code we use. There is no massive bundle overhead.
- **Styling**: It integrates natively with Tailwind CSS, avoiding style conflicts or the need for a separate CSS-in-JS runtime.

### 3. Data Fetching: SWR (Stale-While-Revalidate)
**Decision**: Use **SWR** for client-side data fetching instead of Redux or WebSockets.
**Reasoning**:
- **Simplicity**: For a dashboard, "polling" every 60 seconds is often indistinguishable from "real-time" but significantly less complex to implement than WebSockets.
- **Resilience**: SWR handles caching, revalidation on window focus, and error retries out of the box. The "stale" data strategy ensures the user always sees *something* while new data loads, making the app feel faster.

### 4. Styling: Tailwind CSS v4
**Decision**: Utility-first CSS.
**Reasoning**: Speed of development. Co-locating styles with markup reduces context switching. Version 4 provides a highly optimized engine with no build-time overhead for unused styles.

## State Management Strategy

1.  **URL State**: We use the URL largely for navigation.
2.  **Server State**: `swr` handles the "state" of remote data (stock prices, sentiment). This avoids the need for complex global stores like Redux.
3.  **Local UI State**: `useState` is used for inputs (search bar) and toggle states.
