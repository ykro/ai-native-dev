# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Linting
npm run lint

# Run all tests
npm run test:run

# Run tests in watch mode
npm run test

# Run tests with coverage
npm run test:coverage

# Run a single test file
npx vitest run src/lib/date-utils.test.ts

# Python scripts (from scripts/ directory)
uv run generate_inventory.py    # Generate inventory with Unsplash images
uv run setup_gcs.py             # Configure GCS bucket
```

## Architecture Overview

This is a Next.js 16+ equipment rental marketplace with App Router. The UI is in Spanish.

### Layered Architecture

```
Presentation Layer     → src/app/ (pages), src/components/
Business Logic Layer   → src/services/
Data Layer            → src/data/inventory.json, GCS bucket, Gemini AI
Configuration Layer   → src/config/env.ts
Validation Layer      → src/lib/validation.ts (Zod schemas)
```

### Key Services

- **inventoryService**: Gear CRUD with in-memory caching (5-minute TTL). Uses Fisher-Yates shuffle for random selection.
- **imageService**: Resolves images from inventory or generates via Nano Banana (Gemini AI), persists to GCS, updates inventory.json.
- **storageService**: Google Cloud Storage operations for image persistence.

### Image Resolution Strategy

Items without `imageURL` trigger on-demand generation:
1. Call Nano Banana API to generate image
2. Upload base64 result to GCS bucket
3. Get public URL from GCS
4. Update `inventory.json` with new URL (permanent persistence)
5. Return image to client

### Rental Flow State Machine

The `RentalFlow` component is a multi-step wizard with states:
- `selection` → `configuration` → `summary` → `confirmation`

### Categories (Hardcoded)

| ID | Display Name |
|----|--------------|
| `fotografia-video` | Fotografía y Video |
| `montana-camping` | Montaña y Camping |
| `deportes-acuaticos` | Deportes Acuáticos |

## Key Patterns

### Validation with Zod

All data validation uses Zod schemas in `src/lib/validation.ts`. Types are inferred:
```typescript
export type GearItem = z.infer<typeof gearItemSchema>;
```

Use `safeParse()` for graceful error handling in UI code.

### Environment Configuration

Environment variables are validated lazily via `getEnv()` in `src/config/env.ts`. Required variables:
- `GCS_BUCKET_NAME`
- `GCS_PROJECT_ID`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `NANO_BANANA_API_KEY`

### Component Organization

- `src/components/ui/` - shadcn/ui primitives (Button, Card, Calendar, etc.)
- `src/components/features/` - Feature-specific components (GearImage, RentalFlow, HeroCarousel)

### API Routes

- `POST /api/rental` - Create rental (validates with `rentalRequestSchema`)
- `GET/POST /api/generate-image` - Generate or retrieve image for a gear item

### Testing

Tests use Vitest + React Testing Library. Test files live alongside source files:
- `src/lib/date-utils.test.ts`
- `src/services/imageService.test.ts`
- `src/components/features/RentalFlow/RentalFlow.test.ts`

Mock Next.js components (Image, Link, useRouter) are configured in `src/test/setup.tsx`.

## Path Aliases

Use `@/` for imports from `src/`:
```typescript
import { GearItem } from "@/lib/validation";
```
