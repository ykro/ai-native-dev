# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PawsMatch is a pet adoption web app with a Tinder-like swiping interface. The UI is fully localized in Spanish (es-GT).

## Commands

All commands run from the `app/` directory:

```bash
npm run dev      # Start Vite dev server (localhost:5173)
npm run build    # TypeScript check + Vite production build
npm run lint     # ESLint on .ts/.tsx files
npm run preview  # Preview production build locally
```

**Asset generation** (from `asset-generation/` directory):
```bash
export GEMINI_API_KEY="your_key"
uv run main.py   # Generates pets.json, copy to app/src/data/
```

## Tech Stack

- React 19 + TypeScript (strict mode)
- Vite 7 with HMR
- Tailwind CSS 4 (CSS-first config in `src/index.css` using `@theme` block)
- Framer Motion for swipe animations and micro-interactions
- Lucide React for icons

## Architecture

```
app/src/
├── components/
│   ├── PetCard.tsx              # Swipeable card with drag gestures
│   └── AdoptionConfirmation.tsx # Shelter info and scheduling screen
├── hooks/
│   └── usePetStack.ts           # Pre-fetch buffer (FIFO queue of 3 pets)
├── services/
│   └── petProvider.ts           # Merges local bios with Dog API images
├── types/
│   └── pet.ts                   # Pet and PetProfile interfaces
└── data/
    ├── mockData.ts              # Loads pets.json
    └── pets.json                # 50 dog profiles (Spanish)
```

**App Flow**: Browse (swipe) → Adoption Info → Success → Continue Browsing

**Screen state** managed via `useState<AppScreen>` in `App.tsx` (no router).

## Key Patterns

### Pre-fetch Stack (`usePetStack.ts`)
Maintains a buffer of 3 pets. On swipe: removes first item (FIFO), background-fetches a new one. The next pet's image is preloaded via a hidden `<img>` element in `App.tsx:129-136` for zero-latency transitions.

Uses `useRef` guard to prevent double initialization in React StrictMode.

### Pet Provider (`petProvider.ts`)
- Selects random local pet bio from `pets.json`
- Fetches random image from `https://dog.ceo/api/breeds/image/random`
- Falls back to golden retriever image on API failure
- Returns `PetProfile` (Pet + imageUrl)

### Type Extension
`PetProfile extends Pet` adds `imageUrl` to the base `Pet` interface (id, name, bio).

## Styling

Custom color palettes defined in `src/index.css` `@theme` block:
- `primary-*`: Sunny yellows
- `warm-*`: Earthy oranges/browns
- `friendly-*`: Soft greens

Custom utilities for mobile safe areas: `safe-top`, `safe-bottom`, `safe-left`, `safe-right`.

Uses `dvh` units for mobile browser chrome handling.

## No Test Framework

Testing is not configured. Would need to add Vitest or Jest if tests are required.
