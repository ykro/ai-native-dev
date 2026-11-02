# Developer Onboarding Guide

Welcome to the Rent my Gear project! This guide will help you understand the codebase, set up your development environment, and start contributing.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [Code Architecture](#code-architecture)
4. [Key Concepts](#key-concepts)
5. [Development Workflow](#development-workflow)
6. [Debugging Guide](#debugging-guide)
7. [Adding a New Category](#adding-a-new-category)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Python 3.10+ with `uv` (for scripts)
- Google Cloud account (for GCS)
- Google AI API key (for Nano Banana)

### Setup Steps

```bash
# 1. Clone and install
git clone <repo-url>
cd rent-my-gear
npm install

# 2. Configure environment
cp .env.example .env.local
# Edit .env.local with your credentials

# 3. Run development server
npm run dev

# 4. Open http://localhost:3000
```

---

## Project Overview

### What is Rent my Gear?

A premium equipment rental marketplace where users can:
- Browse 50+ items across 3 categories
- Search and filter equipment
- Select rental dates and see pricing
- Complete rental reservations

### Technology Choices

| Technology | Why We Use It |
|------------|---------------|
| Next.js 16+ | Modern React framework with App Router for optimal performance |
| Tailwind CSS | Rapid UI development with utility classes |
| shadcn/ui | High-quality, accessible component library |
| Zod | Type-safe runtime validation |
| Google Gemini | AI image generation for missing product photos |
| GCS | Reliable cloud storage for generated images |

### Key Features

1. **Smart Image Strategy**: Uses existing Unsplash images when available, generates with AI when not
2. **Real-time Search**: Instant filtering without page reload
3. **Multi-step Rental Flow**: Guided experience from selection to confirmation
4. **Spanish UI**: Full localization for Spanish-speaking users

---

## Code Architecture

### Directory Structure

```
src/
├── app/           # Next.js pages and API routes
├── components/    # React components
│   ├── ui/        # Reusable UI primitives (shadcn)
│   └── features/  # Feature-specific components
├── services/      # Business logic
├── lib/           # Utilities and validation
├── config/        # Environment configuration
└── data/          # Static data (inventory)
```

### Layer Responsibilities

```
┌─────────────────────────────────────────────┐
│              Presentation Layer              │
│   (app/, components/)                        │
│   - React components                         │
│   - User interaction handling                │
├─────────────────────────────────────────────┤
│              Business Layer                  │
│   (services/)                                │
│   - inventoryService: Gear management        │
│   - imageService: Image resolution           │
│   - storageService: Cloud storage            │
├─────────────────────────────────────────────┤
│              Data Layer                      │
│   (data/, external APIs)                     │
│   - inventory.json                           │
│   - Google Cloud Storage                     │
│   - Gemini AI API                            │
└─────────────────────────────────────────────┘
```

### Key Files to Understand

| File | Purpose | Key Concepts |
|------|---------|--------------|
| `src/lib/validation.ts` | Zod schemas | Type definitions, validation rules |
| `src/services/inventoryService.ts` | Data access | Caching, CRUD operations |
| `src/services/imageService.ts` | Image logic | AI generation, GCS upload |
| `src/components/features/RentalFlow/index.tsx` | Rental wizard | Multi-step form, state machine |

---

## Key Concepts

### 1. Server vs Client Components

```typescript
// Server Component (default) - runs on server
// src/app/page.tsx
export default async function HomePage() {
  const items = await getRandomGear(5); // Server-side fetch
  return <HeroCarousel items={items} />;
}

// Client Component - runs in browser
// src/components/features/HeroCarousel.tsx
"use client"; // This directive makes it a client component

import { useState } from "react";
export function HeroCarousel({ items }) {
  const [current, setCurrent] = useState(0);
  // ...
}
```

### 2. Zod Validation

```typescript
// src/lib/validation.ts

// Define the schema
export const gearItemSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  category: z.enum(CATEGORY_IDS),
  dailyRate: z.number().positive(),
  imageURL: z.string().url().nullable(),
});

// Use for validation
export function validateGearItem(data: unknown): GearItem {
  return gearItemSchema.parse(data); // Throws if invalid
}

// Safe validation (doesn't throw)
const result = gearItemSchema.safeParse(data);
if (result.success) {
  // result.data is typed as GearItem
}
```

### 3. Image Resolution Strategy

```typescript
// src/services/imageService.ts

export async function getOrGenerateImage(gearId: string) {
  const item = await getGearById(gearId);

  // Strategy 1: Use existing URL
  if (item.imageURL) {
    return item.imageURL;
  }

  // Strategy 2: Generate with AI
  const base64 = await generateImageWithAI(item);

  // Strategy 3: Persist to GCS
  const url = await uploadImageFromBase64(base64, gearId);

  // Strategy 4: Update inventory for future requests
  await updateGearImage(gearId, url);

  return url;
}
```

### 4. Rental Flow State Machine

```typescript
// src/components/features/RentalFlow/index.tsx

type RentalFlowStep = "selecting" | "configuring" | "reviewing" | "confirmed";

function RentalFlow({ item }) {
  const [step, setStep] = useState<RentalFlowStep>("selecting");

  // State transitions
  // selecting -> configuring (click "Seleccionar Fechas")
  // configuring -> reviewing (select dates + click "Continuar")
  // reviewing -> confirmed (API success)
}
```

---

## Development Workflow

### Running the App

```bash
# Development mode (with hot reload)
npm run dev

# Production build
npm run build
npm start

# Linting
npm run lint

# Testing
npm run test:run
```

### Making Changes

1. **Create a branch**: `git checkout -b feature/my-feature`
2. **Make changes**: Edit files, add tests
3. **Run tests**: `npm run test:run`
4. **Run lint**: `npm run lint`
5. **Commit**: `git commit -m "feat: add my feature"`
6. **Push**: `git push origin feature/my-feature`

### Code Style

- **TypeScript**: Strict mode enabled
- **Components**: Functional components with hooks
- **Naming**: camelCase for functions, PascalCase for components
- **Files**: kebab-case for files, PascalCase for component files

---

## Debugging Guide

### Debugging GCS Connection

#### Step 1: Verify Environment Variables

```bash
# Check if variables are set
cat .env.local | grep GCS
```

Expected output:
```
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=.gcp/service-account.json
```

#### Step 2: Verify Service Account File

```bash
# Check if file exists
ls -la .gcp/service-account.json

# Verify JSON structure
cat .gcp/service-account.json | head -20
```

Expected structure:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "...",
  "client_id": "...",
  ...
}
```

#### Step 3: Run GCS Smoke Test

```bash
cd scripts
uv run setup_gcs.py
```

Expected output:
```
==================================================
  Rent my Gear - GCS Setup
==================================================

📋 Configuration:
   Bucket:  your-bucket-name
   Project: your-project-id
   Creds:   /path/to/.gcp/service-account.json

📦 Checking bucket: your-bucket-name
   ✅ Bucket already exists

🔓 Configuring public access...
   ✅ Public read access enabled

🧪 Running smoke test...
   1️⃣  Uploading test file...
      ✅ Upload successful
   2️⃣  Verifying public URL...
      🔗 https://storage.googleapis.com/your-bucket/smoke-test.txt
      ✅ Public access verified
   3️⃣  Cleaning up test file...
      ✅ Test file deleted

==================================================
✅ GCS setup completed successfully!
==================================================
```

#### Common GCS Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `GOOGLE_APPLICATION_CREDENTIALS file not found` | Wrong path | Use relative path from project root: `.gcp/service-account.json` |
| `Permission denied` | Missing IAM roles | Add `Storage Admin` role to service account |
| `Bucket name already taken` | Name conflict | Choose a globally unique bucket name |
| `Network error` | Firewall/proxy | Check network connectivity |

#### Step 4: Test Image Upload

```typescript
// Add to a test file or API route
import { uploadImageFromBase64 } from "@/services/storageService";

const testBase64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";

try {
  const url = await uploadImageFromBase64(testBase64, "test-image", "image/png");
  console.log("Upload successful:", url);
} catch (error) {
  console.error("Upload failed:", error);
}
```

---

## Adding a New Category

Adding a new category (e.g., "Equipo de Ski") requires changes in multiple files. Follow these steps carefully to avoid breaking validation schemas.

### Step 1: Update Validation Schema

```typescript
// src/lib/validation.ts

// 1. Add to CATEGORY_IDS array
export const CATEGORY_IDS = [
  "fotografia-video",
  "montana-camping",
  "deportes-acuaticos",
  "ski-snowboard",        // ← Add new category ID
] as const;

// 2. Add to CATEGORIES object
export const CATEGORIES: Record<CategoryId, { name: string; description: string }> = {
  "fotografia-video": {
    name: "Fotografía y Video",
    description: "Cámaras, lentes, iluminación y equipo audiovisual profesional",
  },
  "montana-camping": {
    name: "Montaña y Camping",
    description: "Tiendas, mochilas, equipo técnico de montaña y accesorios",
  },
  "deportes-acuaticos": {
    name: "Deportes Acuáticos",
    description: "Kayaks, SUP, equipo de buceo, surf y deportes náuticos",
  },
  // ↓ Add new category
  "ski-snowboard": {
    name: "Ski y Snowboard",
    description: "Esquís, tablas de snowboard, botas y equipo de nieve",
  },
};
```

### Step 2: Add Category Button

```typescript
// src/components/features/CategoryButtons.tsx

// The component automatically reads from CATEGORIES,
// so no changes needed here if you use the pattern:
Object.entries(CATEGORIES).map(([id, { name, description }]) => (
  // Category button JSX
))

// If you have hardcoded buttons, add:
<CategoryButton
  id="ski-snowboard"
  name="Ski y Snowboard"
  icon={<Snowflake className="w-8 h-8" />}
/>
```

### Step 3: Add Category Page (if needed)

The dynamic route `src/app/category/[id]/page.tsx` already handles any valid category ID. No changes needed if you use the validation:

```typescript
// src/app/category/[id]/page.tsx
export default async function CategoryPage({ params }) {
  const { id } = await params;

  // This validates the category ID automatically
  if (!isValidCategory(id)) {
    notFound();
  }

  const items = await getGearByCategory(id);
  // ...
}
```

### Step 4: Add Inventory Items

Add items to `src/data/inventory.json`:

```json
{
  "id": "ski-001",
  "name": "Esquís Rossignol Experience 88",
  "category": "ski-snowboard",
  "description": "Esquís all-mountain premium para todos los niveles",
  "specs": {
    "longitud": "176cm",
    "radio": "17m",
    "nivel": "Intermedio-Avanzado"
  },
  "dailyRate": 450,
  "imageURL": null
}
```

Or use the Python script:

```python
# scripts/generate_inventory.py

# Add to ITEMS dictionary
"ski-snowboard": [
    ("Esquís Rossignol Experience 88", "Esquís all-mountain premium", {"longitud": "176cm"}, 450, "ski equipment"),
    ("Tabla Burton Custom", "Snowboard freestyle versátil", {"longitud": "158cm"}, 400, "snowboard"),
    # ... more items
],
```

### Step 5: Verify Changes

```bash
# 1. Run type check
npx tsc --noEmit

# 2. Run tests
npm run test:run

# 3. Build project
npm run build

# 4. Test in browser
npm run dev
# Navigate to /category/ski-snowboard
```

### Checklist for New Category

- [ ] Added category ID to `CATEGORY_IDS` in `validation.ts`
- [ ] Added category info to `CATEGORIES` in `validation.ts`
- [ ] TypeScript compiles without errors
- [ ] Added at least one item to inventory
- [ ] Category page loads correctly
- [ ] Items display in category grid
- [ ] Search finds items in new category
- [ ] Rental flow works for new items

---

## Common Tasks

### Adding a New Component

```bash
# 1. Create component file
touch src/components/features/MyComponent.tsx

# 2. Add component code
# 3. Export from index if needed
# 4. Import and use in pages
```

### Adding an API Route

```typescript
// src/app/api/my-route/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  return NextResponse.json({ message: "Hello" });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  // Process request
  return NextResponse.json({ success: true });
}
```

### Adding a New Service

```typescript
// src/services/myService.ts
export async function myFunction(param: string): Promise<Result> {
  // Implementation
}

// Export types if needed
export type MyServiceResult = {
  // ...
};
```

---

## Troubleshooting

### Build Errors

| Error | Solution |
|-------|----------|
| `Cannot find module` | Run `npm install` |
| `Type error` | Check TypeScript types |
| `ESLint error` | Run `npm run lint -- --fix` |

### Runtime Errors

| Error | Solution |
|-------|----------|
| `Environment variable not set` | Check `.env.local` |
| `Image not loading` | Check `next.config.ts` image domains |
| `API returning 500` | Check server logs |

### Testing Issues

| Issue | Solution |
|-------|----------|
| Tests timing out | Increase timeout in test |
| Mock not working | Check mock setup in `setup.tsx` |
| Component not found | Check for client/server mismatch |

---

## Getting Help

1. **Documentation**: Check `docs/` folder
2. **Code Comments**: Read inline comments
3. **Tests**: Look at test files for usage examples
4. **Git History**: Check commit messages for context

---

Welcome to the team! 🎉
