# Rent my Gear

Premium equipment rental marketplace for photography, camping, and water sports.

## Description

Rent my Gear is a web application built with Next.js 16+ that allows users to explore and rent professional equipment. The application implements a smart image strategy where images are served from existing URLs or generated on-demand using Nano Banana (Gemini AI) and persisted to Google Cloud Storage.

## Features

- **Equipment Catalog**: 50 items distributed across 3 categories
- **Real-time Search**: Instant filtering by name and description
- **Rental Flow**: Date selection, price summary, and confirmation
- **AI Image Generation**: Automatic fallback to Nano Banana for items without images
- **GCS Persistence**: Generated images are permanently saved
- **Spanish UI**: Interface fully in Spanish

## Technologies

- **Framework**: Next.js 16+ (App Router)
- **Styling**: Tailwind CSS + shadcn/ui
- **Validation**: Zod
- **AI**: Google Generative AI (Nano Banana / Gemini)
- **Storage**: Google Cloud Storage
- **Utilities**: date-fns

## Project Structure

```
rent-my-gear/
├── src/
│   ├── app/                    # App Router pages
│   │   ├── page.tsx            # Home page
│   │   ├── category/[id]/      # Category pages
│   │   ├── gear/[id]/          # Gear detail pages
│   │   └── api/                # API routes
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components
│   │   └── features/           # Feature components
│   ├── services/               # Business logic
│   ├── lib/                    # Utilities
│   ├── config/                 # Environment config
│   └── data/                   # Mock data
├── scripts/                    # Python utilities
└── README.md
```

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
# Google Cloud Storage
GCS_BUCKET_NAME=your-bucket-name
GCS_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=.gcp/service-account.json

# Nano Banana (Gemini) API
NANO_BANANA_API_KEY=your-api-key

# Unsplash (scripts only)
UNSPLASH_ACCESS_KEY=your-unsplash-key
```

### 2. Installation

```bash
npm install
```

### 3. Configure GCS (Optional)

```bash
cd scripts
uv run setup_gcs.py
```

### 4. Generate Inventory with Images (Optional)

```bash
cd scripts
uv run generate_inventory.py
```

### 5. Run Development Server

```bash
npm run dev
```

## Architecture

### Image Strategy

```
1. Check if item.imageURL exists
   ├─ YES → Use directly with next/image
   └─ NO →
      2. Show loading spinner to user
      3. Call Nano Banana API to generate image
      4. Upload result to GCS bucket
      5. Get public URL from GCS
      6. Update inventory.json with new URL (persistent)
      7. Display generated image
```

### Categories

| ID | Name | Description |
|----|------|-------------|
| `fotografia-video` | Photography & Video | Cameras, lenses, lighting, and audiovisual equipment |
| `montana-camping` | Mountain & Camping | Tents, backpacks, technical mountain gear |
| `deportes-acuaticos` | Water Sports | Kayaks, SUP, diving gear, surfing |

### Rental Flow

1. **Selection**: View equipment details and specifications
2. **Configuration**: Select date range with validation
3. **Summary**: View price breakdown (daily rate × days)
4. **Confirmation**: Confirm rental and receive confirmation number

## API Routes

### POST /api/rental

Create a new rental.

```json
{
  "gearId": "gear-001",
  "startDate": "2024-01-15T00:00:00Z",
  "endDate": "2024-01-18T00:00:00Z"
}
```

### GET /api/generate-image?id=gear-001

Get or generate image for an item. Redirects to the image URL.

### POST /api/generate-image

Generate image for a specific item.

```json
{
  "gearId": "gear-001"
}
```

## Python Scripts

### generate_inventory.py

Generates the `inventory.json` file with 50 items and fetches real images from Unsplash.

```bash
uv run generate_inventory.py
```

### setup_gcs.py

Configures the GCS bucket with public access and runs a smoke test.

```bash
uv run setup_gcs.py
```

## Development

```bash
# Development
npm run dev

# Build
npm run build

# Lint
npm run lint
```

## Testing

The project includes a comprehensive testing suite using **Vitest** and **React Testing Library**.

```bash
# Run all tests
npm run test:run

# Run tests in watch mode
npm run test

# Run with coverage
npm run test:coverage
```

### Test Coverage

| Category | Tests | Pass Rate |
|----------|-------|-----------|
| Unit Tests (date-utils) | 32 | 90.6% |
| Integration Tests (RentalFlow) | 15 | 53.3% |
| Edge Cases (imageService) | 10 | 100% |

For detailed test documentation, see [docs/TESTING.md](docs/TESTING.md).

## Documentation

Comprehensive documentation is available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System architecture, component hierarchy, data flow |
| [Diagrams](docs/DIAGRAMS.md) | Mermaid diagrams (sequence, class, state machine) |
| [Onboarding](docs/ONBOARDING.md) | Developer guide, debugging, adding categories |
| [Testing](docs/TESTING.md) | Test suite documentation and results |

### Quick Links

- **New Developer?** Start with the [Onboarding Guide](docs/ONBOARDING.md)
- **Understanding the codebase?** See [Architecture](docs/ARCHITECTURE.md)
- **Visual learner?** Check [Diagrams](docs/DIAGRAMS.md) for Mermaid diagrams
- **Running tests?** Read [Testing](docs/TESTING.md)

### Key Diagrams

The [Diagrams](docs/DIAGRAMS.md) document includes:

- **Image Resolution Flow**: Sequence diagram showing JSON → Nano Banana → GCS persistence
- **Service Class Diagram**: inventoryService and imageService interactions
- **Rental Flow State Machine**: Multi-step wizard state transitions
- **Component Hierarchy**: React component tree
- **Data Flow Diagram**: Request/response flow through layers

## License

MIT
