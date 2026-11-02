# System Diagrams

## Image Resolution Flow

This sequence diagram shows the complete flow from checking the JSON inventory file, through Nano Banana AI generation, to GCS persistence.

```mermaid
sequenceDiagram
    participant C as Client (GearImage)
    participant API as /api/generate-image
    participant IS as imageService
    participant INV as inventoryService
    participant JSON as inventory.json
    participant AI as Nano Banana (Gemini)
    participant GCS as Google Cloud Storage

    C->>API: POST { gearId }
    API->>IS: getOrGenerateImage(gearId)
    IS->>INV: getGearById(gearId)
    INV->>JSON: Read inventory
    JSON-->>INV: GearItem data
    INV-->>IS: GearItem (with imageURL: null)

    alt imageURL exists
        IS-->>API: Return existing imageURL
        API-->>C: { imageURL, generated: false }
    else imageURL is null (Unsplash 404)
        IS->>IS: generateImagePrompt(item)
        IS->>AI: generateContent(prompt)
        Note over AI: Generate product image<br/>using item details
        AI-->>IS: base64 image data

        IS->>GCS: uploadImageFromBase64(base64, gearId)
        Note over GCS: Store as<br/>gear-{id}.png
        GCS-->>IS: Public URL

        IS->>INV: updateGearImage(gearId, url)
        INV->>JSON: Write updated inventory
        JSON-->>INV: Success
        INV-->>IS: Updated

        IS-->>API: Return new imageURL
        API-->>C: { imageURL, generated: true }
    end

    C->>C: Display image
```

## Image Resolution Decision Tree

```mermaid
flowchart TD
    A[Client requests gear image] --> B{Check item.imageURL}
    B -->|URL exists| C[Return URL directly]
    B -->|URL is null| D[Trigger AI Generation]

    D --> E[Create image prompt]
    E --> F[Call Nano Banana API]
    F --> G{Generation successful?}

    G -->|Yes| H[Upload to GCS]
    G -->|No| I[Return null / Show error]

    H --> J{Upload successful?}
    J -->|Yes| K[Update inventory.json]
    J -->|No| I

    K --> L[Return new GCS URL]

    C --> M[Display image]
    L --> M
    I --> N[Show placeholder]

    style D fill:#f9f,stroke:#333
    style H fill:#9cf,stroke:#333
    style K fill:#9f9,stroke:#333
```

## Service Class Diagram

This diagram shows the interactions between `inventoryService` and `imageService`.

```mermaid
classDiagram
    class GearItem {
        +string id
        +string name
        +CategoryId category
        +string description
        +Record~string, string|number~ specs
        +number dailyRate
        +string|null imageURL
    }

    class inventoryService {
        -GearItem[] inventoryCache
        -number cacheTimestamp
        -number CACHE_TTL
        +loadInventory() Promise~GearItem[]~
        +getAllGear() Promise~GearItem[]~
        +getGearById(id: string) Promise~GearItem|null~
        +getGearByCategory(categoryId: string) Promise~GearItem[]~
        +getRandomGear(count: number) Promise~GearItem[]~
        +searchGear(query: string) Promise~GearItem[]~
        +updateGearImage(gearId: string, imageURL: string) Promise~void~
    }

    class imageService {
        -GoogleGenerativeAI genAI
        +getGenAIClient() GoogleGenerativeAI
        +generateImagePrompt(item: GearItem) string
        +generateImageWithAI(item: GearItem) Promise~string~
        +getOrGenerateImage(gearId: string) Promise~string|null~
        +resolveImageUrl(item: GearItem) string
        +isImageUrlValid(url: string) Promise~boolean~
        +batchGenerateImages(items: GearItem[]) Promise~Result~
    }

    class storageService {
        -Storage storageClient
        +getStorageClient() Storage
        +uploadImageFromBase64(base64: string, filename: string, contentType: string) Promise~string~
        +deleteImage(filename: string) Promise~void~
        +getPublicUrl(filename: string) string
    }

    class validation {
        +CATEGORY_IDS CategoryId[]
        +CATEGORIES Record~CategoryId, CategoryInfo~
        +gearItemSchema ZodSchema
        +rentalDatesSchema ZodSchema
        +validateGearItem(data: unknown) GearItem
        +validateRentalDates(start: Date, end: Date) Result
        +isValidCategory(id: string) boolean
    }

    inventoryService --> GearItem : manages
    imageService --> inventoryService : uses
    imageService --> storageService : uses
    imageService --> GearItem : processes
    storageService --> GearItem : stores images for
    validation --> GearItem : validates
```

## Rental Flow State Machine

```mermaid
stateDiagram-v2
    [*] --> Selecting: Component Mount

    Selecting --> Configuring: Click "Seleccionar Fechas"
    Configuring --> Selecting: Click Back
    Configuring --> Reviewing: Select dates + Click "Continuar"
    Reviewing --> Configuring: Click Back
    Reviewing --> Confirmed: API Success
    Reviewing --> Reviewing: API Error (stay + show error)
    Confirmed --> Selecting: Click "Hacer otra reservación"

    state Selecting {
        [*] --> ShowInitialUI
        ShowInitialUI --> WaitingForClick
    }

    state Configuring {
        [*] --> ShowCalendar
        ShowCalendar --> DatesSelected
        DatesSelected --> ShowCalendar: Change selection
    }

    state Reviewing {
        [*] --> ShowSummary
        ShowSummary --> Loading: Click "Confirmar"
        Loading --> ShowSummary: Error
    }

    state Confirmed {
        [*] --> ShowConfirmation
        ShowConfirmation --> DisplayNumber
    }
```

## Component Hierarchy

```mermaid
graph TD
    subgraph "Pages (Server Components)"
        HP[HomePage]
        CP[CategoryPage]
        GP[GearPage]
    end

    subgraph "Feature Components (Client)"
        HC[HeroCarousel]
        CB[CategoryButtons]
        GG[GearGrid]
        GI[GearImage]
        RF[RentalFlow]
    end

    subgraph "RentalFlow Children"
        DS[DateSelection]
        PS[PriceSummary]
        CF[Confirmation]
    end

    subgraph "UI Components (shadcn)"
        BTN[Button]
        CRD[Card]
        CAL[Calendar]
        CRS[Carousel]
        SKL[Skeleton]
        BGD[Badge]
        INP[Input]
    end

    HP --> HC
    HP --> CB
    CP --> GG
    GP --> GI
    GP --> RF

    RF --> DS
    RF --> PS
    RF --> CF

    HC --> CRS
    HC --> CRD
    GG --> CRD
    GG --> BGD
    GG --> INP
    DS --> CAL
    DS --> BTN
    PS --> CRD
    PS --> BTN
    CF --> CRD
    CF --> BTN
    GI --> SKL
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph "Client Layer"
        Browser[Browser]
        React[React Components]
    end

    subgraph "Next.js Server"
        Router[App Router]
        API[API Routes]
        SC[Server Components]
    end

    subgraph "Services Layer"
        IS[inventoryService]
        ImS[imageService]
        SS[storageService]
    end

    subgraph "External Services"
        JSON[(inventory.json)]
        GCS[(Google Cloud Storage)]
        AI[Gemini AI]
    end

    Browser <--> React
    React <--> Router
    React <--> API
    Router --> SC
    SC --> IS
    API --> IS
    API --> ImS
    ImS --> IS
    ImS --> SS
    ImS --> AI
    IS --> JSON
    SS --> GCS

    style Browser fill:#e1f5fe
    style GCS fill:#fff3e0
    style AI fill:#f3e5f5
    style JSON fill:#e8f5e9
```

## Environment Configuration Flow

```mermaid
flowchart TD
    ENV[.env.local] --> ZOD[Zod Validation]
    ZOD --> |Valid| CONFIG[Configuration Object]
    ZOD --> |Invalid| ERROR[Throw Error + Exit]

    CONFIG --> GCS_CONFIG[GCS Configuration]
    CONFIG --> AI_CONFIG[AI Configuration]

    GCS_CONFIG --> |GCS_BUCKET_NAME| SS[storageService]
    GCS_CONFIG --> |GCS_PROJECT_ID| SS
    GCS_CONFIG --> |GOOGLE_APPLICATION_CREDENTIALS| SS

    AI_CONFIG --> |NANO_BANANA_API_KEY| ImS[imageService]

    subgraph "Required Variables"
        GCS_BUCKET_NAME
        GCS_PROJECT_ID
        GOOGLE_APPLICATION_CREDENTIALS
        NANO_BANANA_API_KEY
    end
```
