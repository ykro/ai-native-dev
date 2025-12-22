# Role-Based Development Prompt: TraveLens App

Execute a multi-agent collaborative workflow to develop **TraveLens**, an AI-native Pinterest-style travel explorer. You must follow a sequential **Agentic Workflow**, providing the output for each role one by one. Do not proceed to the next role until the previous one's architecture is defined.

## Role 1: System Architect 
- Use **context7** to fetch the latest stable documentation for **Next.js v16+ (App Router)** and **shadcn/ui** installation for December 2025.
- Initialize the project and install `shadcn/ui` along with `lucide-react` for iconography.
- **Architectural Requirements:**
  - **BFF Pattern:** Implement `src/app/api/` for Backend Route Handlers to proxy external requests and protect API keys.
  - **Services Layer:** Create `src/services/unsplash.ts` and `src/services/gemini.ts` for core logic.
  - **Component Hierarchy:** Separate `src/components/ui/` (shadcn) from `src/components/features/` (Masonry Grid, Detail Panel).
- Define the global Tailwind theme with a "premium travel" aesthetic.

## Role 2: UI/UX Frontend Developer
- Build the main interface in **Spanish** using **shadcn/ui** components.
- **Homepage:** Responsive Masonry Grid (Pinterest-style) using Tailwind `columns` or a dedicated layout component.
  - **Grid Items:** Use `urls.small` for performance. Text overlay (Title/City) must be visible **only on hover**.
- **Configuration:** Update `next.config.ts` to allow images from `images.unsplash.com`.
- **Search Bar:** A centered shadcn `Input` with a search icon that updates the grid in real-time (Syncs with URL query params).
- **Detail View (`/destination/[id]`):**
  - **Route:** Use the specific route `/destination/[id]` (not `/destino`).
  - **Left panel (Hero):** Selected high-res photo (`urls.regular`). Overlay must be **clean**: Display only **Title** and **Tags** (Remove location text and Compass/Map icons).
  - **Right panel (Plan):** AI-generated plan using `Card` and `Skeleton` for loading states.
  - **Far-right sidebar (Similar):** "Destinos Similares" presented as a **Bento Grid / Mosaic**.
    - **Layout:** Use CSS Grid (e.g., `grid-cols-2` with `auto-rows`) to create a "mosaic" effect with varied spans (1x1, 2x2, 1x2).
    - **Content:** Display **Images Only** (`urls.thumb`). Do NOT show titles, subtitles, or icons.
    - **Capacity:** Display up to **8 items** without requiring scrolling.

## Role 3: Backend Developer
- Implement the **Unsplash API** integration in `src/services/unsplash.ts`
- Create functions for: 
  - `fetchPopular()`: Initial grid loading (Use randomized selection from a curated list of 30 top tourist cities, unclude "travel" in the query).
    - **Display Logic (Mode: 'home'):**
      - **Title:** Uses the **Context City Name** (e.g., "Paris", "Tokyo") to ensure relevance.
      - **Subtitle:** Uses the **Photo Description** (or `alternative_slugs.es`), ensuring no IDs are shown.  
  - `searchDestinations(query)`: Search bar logic.
  - `fetchRelated(location, tags, excludedId, fallbackCity)`: To populate the sidebar.
    - **Advanced Logic:** Execute **Primary Query** (`Specific Location` + First 3 Tags). If results are **< 8**, automatically execute a **Secondary Query** using (`fallbackCity` + "landmark travel") to fill the grid. Combine results, deduplicate by ID, and limit to 8.
    - **Display Logic (Mode: 'search'):**
      - **Title:** Uses **Photo Description** (or `alternative_slugs.es`) to be descriptive.
      - **Subtitle:** Uses **Tags** (e.g., "Nature • City • Travel").
      - *Note for Sidebar:* The UI currently overrides this to show **Images Only** (Bento Grid), but the data structure supports this fallback.    
- **Data Mapping:**
  - **Text Cleaning:** Ensure `title` or `description` NEVER contains the Photo ID or filenames. Use `alternative_slugs.es` as a priority fallback for description.
  - **Title Refinement:** Deduplicate city names in titles (e.g., convert "Sydney, Sydney" to "Sydney").
  - **Fields:** Extract `cityName` separately for use in fallback queries. Map `urls.thumb`, `small`, and `regular`.
- Ensure all calls are executed server-side (BFF) to prevent exposing the UNSPLASH_ACCESS_KEY.

## Role 4: Data Specialist (AI Integration)
- **Service:** Implement `src/services/gemini.ts` using `@google/generative-ai`.
  - **Model:** Use `gemini-3-flash-preview` (or latest experimental flash) for fast responses.
  - **Function:** `generateTravelPlan(destination, context)` returning a **Structured JSON** object (Intro, Days, HiddenGem, LocalFood).
- **Backend:** Create a BFF route `src/app/api/ai-plan/route.ts` (POST) to proxy requests securely.
- **Frontend Interaction:**
  - Create a **Client Component** `TravelPlanPanel.tsx` to handle async fetching and state.
  - **Rendering:** Render the JSON data using dedicated UI components (e.g., shadcn `Card` for days, `Badge` for local tips). 
  - Integrate into `DestinationPage` (Right Panel).

## Role 5: QA & Code Reviewer
- Audit the code from previous roles.
- **Requirements:** Check for hydration errors, accessibility (ARIA labels), and API error handling.
- **Pedagogical Note:** Add inline comments titled 'REVIEWER_NOTE' explaining complex sections of the code to help the user "read what the AI wrote."

## Role 6: API Connection Explanation
- Analyze the final implementation of `src/services/unsplash.ts` and `src/services/gemini.ts`. 
- Provide a detailed explanation of:
  - How the connection with Unsplash API and Gemini API is established.
  - The process of building a request and fetching data including how the specific JSON path is used to retrieve content.
  - The logic used to synchronize external images with Gemini-generated plans.

## Role 7: Automated Media Capture & Documentation
- Launch the development server and open the application. 
- **Automated Task:** Take a high-quality screenshot of the initial state and record a short video/GIF demonstrating the search and interactions.
- Save these assets in the project folder.

## Role 8: Technical Documentation Specialist
- Generate a comprehensive `README.md`.
- **Content:** Remove all Next.js boilerplate, include Project architecture, API Connection Explanation, setup guide (env variables), and a "Role Contribution Log".
- **Visuals:** Create an "assets/" folder, copy the files from role 7 and embed the screenshot and video captured in the README, describing the main UI/UX features implemented.

---

**Final Instruction:** Start now by acting as the **System Architect (Role 1)**. Define the folder structure, install shadcn/ui, and set up the base Next.js configuration. Stop and wait for my 'Next Role' command after completing the foundation.