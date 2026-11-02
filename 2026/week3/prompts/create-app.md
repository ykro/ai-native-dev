**Objective:**
Build "Rent my Gear", a premium equipment rental marketplace. The app must implement an **Image Strategy** where images are served via their `imageURL`. If an image is missing, Nano Banana generates it and the result is persisted in **Google Cloud Storage (GCS)**, which then provides the new `imageURL`. The code must be architected for high-level debugging and testing.

**Tech Stack:**

* **Framework:** Next.js 16+ (App Router).
* **Styling:** Tailwind CSS + shadcn/ui (Modern/Apple aesthetic).
* **Persistence:** Google Cloud Storage (GCS).
* **AI:** Nano Banana Pro (`gemini-3-pro-image-preview`)
* **Validation:** Zod for data and environment variables.
* **Language:** UI in **Spanish**; code/comments in **English**.

**1. Environment Variable Validation (Critical):**

* Create `src/config/env.ts`. Use **Zod** to define a schema for: `GCS_BUCKET_NAME`, `GCS_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, and `NANO_BANANA_API_KEY`.
* The app must validate these at runtime (Server-side) and throw a clear, descriptive error if any are missing or malformed, preventing the server from starting with a broken configuration.

**2. Detailed Application Structure:**

* `src/app/`: Root layout with Global Error Boundary. Sub-folders for `(home)`, `category/[id]`, and `gear/[id]`, each with its own `error.tsx` and `loading.tsx`.
* `src/components/ui/`: Base shadcn components.
* `src/components/features/`:
* `HeroCarousel.tsx`: Logic for the 5-item random display.
* `CategoryButtons.tsx`: Large, high-impact buttons for category navigation.
* `GearGrid.tsx`: Performance-optimized grid with Streaming.
* `RentalFlow/`: Multi-step component (Date Selection -> Price Summary -> Mock Confirmation).
* `src/services/`:
* `imageService.ts`: Logic to handle `imageURL` usage and Nano Banana fallback.
* `inventoryService.ts`: Logic to fetch the 50 mock items.
* `storageService.ts`: Wrapper for GCS upload/download (used only for AI generated content).
* `src/lib/`: `validation.ts` (Zod schemas for rentals), `date-utils.ts` (price and range logic).

**3. Navigation & User Flow:**

* **Home (Página Principal):** - Top section: A **Carousel** displaying 5 random items from the inventory.
* Mid section: **Three Large Action Buttons** for the categories: *Fotografía y Video*, *Montaña y Camping*, and *Deportes Acuáticos*.
* **Inventory (Inventario):** Grid view filtered by category with real-time search.
* **Rental Flow (Flujo de Renta):**

1. **Selection:** View technical specs and real-time availability.
2. **Configuration:** Select date range using a shadcn Calendar (Zod validation for no-past dates).
3. **Summary:** Display line-item price calculation (Daily rate * Total days).
4. **Confirmation:** A "Confirmar Renta" button that triggers a mock API call, a success toast, and a final "Rental Confirmed" state.

**4. Image Persistence Strategy:**

* **Logic:** Use the item's `imageURL` as the primary source. For items without an image, trigger Nano Banana -> Save the generated image to GCS -> Convert the resulting GCS public URL into the item's `imageURL` for subsequent use.
* **GCS Setup:** Include `setup_gcs.py` (Using Python, `uv` and `python-dotenv` ) to:
* Create the bucket and set public access.
* **Smoke Test:** Upload a dummy file, verify the public URL, and delete it to validate IAM permissions.

**5. Mock Data Requirements:**

* Generate a JSON of **50 items** distributed across the 3 categories. For each item, use the generated item name to search Unsplash and use the first result as the imageURL.
* Ensure **8 items** have no initial image to force the Nano Banana fallback.

**6. Documentation:**

* Generate a `README.md` including project description, setup and basic architecture.