# Architecture Documentation

## Overview

Rent my Gear is a Next.js 16+ application using the App Router pattern. The application follows a layered architecture with clear separation between presentation, business logic, and data access layers.

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | Next.js 16+ | Full-stack React framework with App Router |
| UI Library | React 19 | Component-based UI |
| Styling | Tailwind CSS + shadcn/ui | Utility-first CSS with pre-built components |
| Validation | Zod | Runtime type validation and schema definition |
| AI | Google Generative AI | Image generation (Nano Banana) |
| Storage | Google Cloud Storage | Persistent image storage |
| Date Handling | date-fns | Date manipulation and formatting |

## Directory Structure

```
rent-my-gear/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Home page
│   │   ├── error.tsx             # Global error boundary
│   │   ├── category/[id]/        # Dynamic category pages
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx
│   │   │   └── error.tsx
│   │   ├── gear/[id]/            # Dynamic gear detail pages
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx
│   │   │   └── error.tsx
│   │   └── api/                  # API routes
│   │       ├── rental/route.ts
│   │       └── generate-image/route.ts
│   │
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── calendar.tsx
│   │   │   ├── carousel.tsx
│   │   │   └── ...
│   │   └── features/             # Feature-specific components
│   │       ├── HeroCarousel.tsx
│   │       ├── CategoryButtons.tsx
│   │       ├── GearGrid.tsx
│   │       ├── GearImage.tsx
│   │       └── RentalFlow/
│   │           ├── index.tsx
│   │           ├── DateSelection.tsx
│   │           ├── PriceSummary.tsx
│   │           └── Confirmation.tsx
│   │
│   ├── services/                 # Business logic layer
│   │   ├── inventoryService.ts   # Inventory CRUD operations
│   │   ├── imageService.ts       # Image resolution and generation
│   │   └── storageService.ts     # GCS operations
│   │
│   ├── lib/                      # Utilities
│   │   ├── validation.ts         # Zod schemas
│   │   ├── date-utils.ts         # Date utilities
│   │   └── utils.ts              # General utilities
│   │
│   ├── config/
│   │   └── env.ts                # Environment validation
│   │
│   ├── data/
│   │   └── inventory.json        # Mock inventory data
│   │
│   └── test/
│       └── setup.tsx             # Test configuration
│
├── scripts/                      # Python utilities
│   ├── generate_inventory.py     # Inventory generation script
│   ├── setup_gcs.py              # GCS setup script
│   └── pyproject.toml            # Python dependencies
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md
│   ├── TESTING.md
│   └── ONBOARDING.md
│
└── public/                       # Static assets
```

## Component Architecture

### Page Components (Server Components)

```
┌─────────────────────────────────────────────────────────┐
│                    RootLayout                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │                   Header                           │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │                   Content                          │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  HomePage / CategoryPage / GearDetailPage   │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │                   Footer                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Feature Components (Client Components)

```
HeroCarousel ─────► CarouselItem ─────► GearCard
     │
     └── Uses: Carousel (shadcn), Image (next/image)

CategoryButtons ──► CategoryButton ───► Link (next/link)

GearGrid ─────────► GearCard ──────────► Image, Badge, Card

RentalFlow ───────► DateSelection ────► Calendar (shadcn)
     │              PriceSummary ─────► Card, Button
     │              Confirmation ─────► Card
     │
     └── State: step, dates, confirmationId
```

## Data Flow

### Request Flow

```
Client Request
     │
     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Next.js   │───►│   Service   │───►│    Data     │
│   Router    │    │   Layer     │    │   Layer     │
└─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │
     │                   │                   │
     ▼                   ▼                   ▼
  App Router       inventoryService     inventory.json
  API Routes       imageService         GCS Bucket
                   storageService       Gemini AI
```

### State Management

The application uses React's built-in state management:

- **Server State**: Fetched in Server Components, passed as props
- **Client State**: useState/useEffect in Client Components
- **URL State**: Dynamic route parameters ([id])

## API Routes

### POST /api/rental

Creates a new rental reservation.

**Request:**
```typescript
{
  gearId: string;
  startDate: string; // ISO 8601
  endDate: string;   // ISO 8601
}
```

**Response:**
```typescript
{
  id: string;
  gearId: string;
  gearName: string;
  startDate: string;
  endDate: string;
  totalDays: number;
  dailyRate: number;
  totalPrice: number;
  status: "confirmed";
  createdAt: string;
}
```

### POST /api/generate-image

Generates an image using Nano Banana AI.

**Request:**
```typescript
{
  gearId: string;
}
```

**Response:**
```typescript
{
  gearId: string;
  imageURL: string;
  generated: boolean;
  message: string;
}
```

## Error Handling

### Error Boundaries

Each route group has its own error boundary:

```
src/app/
├── error.tsx              # Global error boundary
├── category/[id]/
│   └── error.tsx          # Category-specific errors
└── gear/[id]/
    └── error.tsx          # Gear detail errors
```

### Error Recovery

```typescript
// error.tsx pattern
export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

## Caching Strategy

### Inventory Cache

```typescript
// inventoryService.ts
let inventoryCache: GearItem[] | null = null;
let cacheTimestamp: number = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
```

### Image Optimization

Next.js Image component handles:
- Lazy loading
- Responsive sizing
- Format optimization (WebP)
- Caching via CDN

## Security Considerations

1. **Environment Variables**: Sensitive keys stored in `.env.local` (gitignored)
2. **Input Validation**: All inputs validated with Zod schemas
3. **API Security**: Server-side validation before processing
4. **XSS Prevention**: React's automatic escaping
5. **CORS**: Handled by Next.js API routes

## Performance Optimizations

1. **Server Components**: Default for static content
2. **Streaming**: Suspense boundaries for progressive loading
3. **Image Optimization**: next/image with responsive sizes
4. **Code Splitting**: Automatic per-route splitting
5. **Caching**: Inventory cache with TTL
