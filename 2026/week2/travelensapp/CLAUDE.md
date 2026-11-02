# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Production build
npm run start    # Run production server
npm run lint     # Run ESLint
```

No test framework is configured. Mock data for manual testing is in `/src/lib/mock-data.ts`.

## Environment Variables

Required in `.env.local`:
```
UNSPLASH_ACCESS_KEY=your_key_here
GOOGLE_GENAI_API_KEY=your_key_here
```

## Architecture Overview

TraveLens is a Next.js 16 App Router application for AI-powered travel planning. It combines Unsplash imagery with Google Gemini-generated itineraries.

### Data Flow

1. **Home page** (Server Component): Fetches 3 random cities from Unsplash, displays masonry grid
2. **Search**: URL query param triggers server-side Unsplash search
3. **Destination detail**: Dynamic route `/destination/[id]` loads image + triggers AI plan generation
4. **AI Plan**: Client fetches `/api/ai-plan` → Server calls Gemini → Returns Spanish itinerary

### Service Layer (`/src/services/`)

- **`unsplash.ts`**: Wraps `unsplash-js` with custom node-fetch. Key methods:
  - `fetchPopular()` - 3 random cities for homepage
  - `searchDestinations(query)` - user search
  - `fetchById(id)` - single destination
  - `fetchRelated(location, tags)` - similar destinations (bento grid)

- **`gemini.ts`**: Google Gemini 3 Flash Preview integration. Generates 3-day itineraries with strict JSON output. All responses in Spanish.

### API Routes (`/src/app/api/`)

- **GET `/api/search?q=`**: Proxies Unsplash, returns `Destination[]`
- **POST `/api/ai-plan`**: Body `{ destination, context? }`, returns `{ plan: TravelPlan }`

### Component Organization

- **`/src/components/features/`**: Business logic components (SearchBar, MasonryGrid, AiTravelSidebar)
- **`/src/components/ui/`**: shadcn/ui primitives (Button, Card, Badge, etc.)

### Key Interfaces

```typescript
// From unsplash.ts
interface Destination {
  id: string;
  slug: string;
  title: string;
  description: string;
  urls: { regular, full, small, thumb };
  user: { name, username };
  tags: string[];
  location?: string;
  cityName?: string;
  gridTitle?: string;
  gridSubtitle?: string;
}

// From gemini.ts
interface TravelPlan {
  intro: string;
  days: { day: number; title: string; activities: string[] }[];
  hiddenGem: { title: string; description: string };
  localFood: { dish: string; description: string };
}
```

## Code Conventions

- **Path alias**: `@/*` maps to `./src/*`
- **Styling**: Tailwind CSS v4 with OKLCH color system defined in `globals.css`
- **UI components**: shadcn/ui with "new-york" style variant
- **Language**: All UI text and AI outputs are in Spanish
- **Images**: Use Next.js `<Image>` component; remote pattern configured for `images.unsplash.com`
