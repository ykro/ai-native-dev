# Phase 1: One Shot + Tool Calling (using Claude Code)

We are building a web app called PawsMatch, that presents the picture of a dog and allows the user to either "Like"(to adopt) or "Pass".

We are going to generate some assets. Use uv to initialize a new Python project inside a folder named asset-generation/. Install google-genai and create a script named main.py. This script must use gemini-3-flash-preview to generate a pets.json file containing 50 dog profiles (id, name, and a 3-line adoption-focused bio in spanish). Create an .env.example file(and add .env to .gitignore) and I will add the API key there. Create a README.md file documenting the project, the structure, the data generation process, and the stack used. Verify the existence of both files using terminal tools and run the script.

---

# Phase 2: K-shot (using Claude Code)

I want to define the coding standards for PawsMatch. Here are 3 examples of how I structure services and types in my projects:

**Example 1 (Types):**
```typescript
export interface User { id: string; email: string; role: 'admin' | 'user'; }
```

**Example 2 (Service):**
```typescript
export const fetchUsers = async (): Promise<User[]> => { const res = await fetch('/api/users'); if (!res.ok) throw new Error('Failed'); return res.json(); }
```

**Example 3 (Custom Hook):**
```typescript
export const useAuth = () => { const [user, setUser] = useState<User | null>(null); return { user, isAuthenticated: !!user }; }
```

Based on these examples and the @pets.json, generate pet.ts file and a mockData.ts file that imports the JSON. Ensure the naming conventions match the examples provided. Update the README.md file accordingly.

---

# Phase 3: One shot + Context (using Antigravity)

Using context7, fetch the latest stable documentation for Vite, React, and Tailwind CSS. Initialize a project named PawsMatch inside a new folder called "app/" using these versions.

Follow this project structure:

```
src/components/ # UI components.
src/hooks/      # Custom hooks.
src/services/   # API and data fetching.
src/types/      # TypeScript definitions in pet.ts
src/data/       # mock data in mockData.ts and pets.json
```

Make sure the entry point displays a clean, centered layout with the app name. Ensure the Tailwind configuration uses a 'warm and friendly' color palette suitable for a pet adoption app. Use the existing @pet.ts, @pets.json and @mockData.ts. Update README.md with the tech stack and architecture details but preserve the content from the asset generation script.

---

# Phase 4: CoT (using Antigravity) + Context

Search the web for the official documentation for The Dog API (dog.ceo/dog-api/). Based on that, I need to implement the pet loading logic. Before coding, perform an analysis to:

1. Read the local pets.json and the src/types/pet.ts file. Use their structure as the absolute source of truth for the following analysis.

2. Identify the exact JSON path from The Dog API response that holds the image URL (e.g., is it $.message, $.url, or $.data.image?) and explain how you will map it to our local interface.

3. Detail how to fetch a random image and map it to a bio from our local pets.json.

4. Explain the TypeScript interface that will merge both data sources.

5. Describe the error handling strategy if the API or the JSON fails. Once the logic is clear, implement src/services/petProvider.ts.

Do not write the code yet; provide the analysis first and wait for my confirmation. After my confirmation, use the analysis to implement all the React componentents needed to interact with the API, showing one card (dog picture and bio) on the main page. Remember to update the README.

---

# Phase 5. ToT (using Antigravity)

Explore three technical approaches for the card stack behavior:

- **Simple state:** Only the current pet is in memory.
- **Pre-fetch stack:** Keep a buffer of 3 upcoming pets (including images) for zero-latency swiping.
- **Virtualized list:** For high-performance rendering of many cards.

Compare them regarding network usage and UX fluidity. Wait for my decision before implementing. After my confirmation, write all the code and update the README.

---

# Phase 6. ReAct (using Claude Code)

Analyze the entire codebase. Focus on src/services/petProvider.ts and the README.md

Your task is to refactor the UI into a modern, mobile-first application.

1. Before refactoring, review README.md to ensure the new components follow the established architecture.
2. Install lucide-react for modern iconography and framer-motion for animations.
3. Create a PetCard.tsx component with a polished 'glassmorphism' style, rounded corners, and clear 'Like/Pass' actions.
4. Use useRef guards in useEffect hooks that perform one-time initialization to prevent double execution in React StrictMode
5. Implement the swipe animations.
6. Ensure the UI feels like a premium native app. Act on all necessary files to achieve this.
7. All UI text must be in Spanish. (es-GT)
8. When a user clicks "Like/Adopt", navigate to an adoption details screen showing shelter contact info, location, and visiting hours. Include a "Schedule Visit" action and a "Keep Browsing" option.
9. Update the README.md (keep it in english)

---

# Phase 7. Feedback loop (using Claude Code)

The application is currently throwing an error in the console when running "npm run build". Run it, capture the full stack trace from the terminal, and use that information to fix the bug.

---

# Phase 8. Explanation (using Antigravity)

Analyze the implementation in src/services/petProvider.ts. Explain in detail how the connection with 'The Dog API' works. Your explanation must include:

- The lifecycle of the fetch request.
- How the JSON path from the API is handled and mapped to our local Pet interface.
- How the synchronization between the external image and the local pets.json bio is managed.

Use a technical but accessible tone, suitable for the project's documentation.

Your explanation must be in spanish.

---

# Phase 9. (using Antigravity)

Use your tools to launch the development server and access the application in a browser.

- Take a high-quality screenshot of the landing state.
- Record a short video demonstrating the swiping interactions, the transition between pets and all the actions available.

Save these files in a "assets/" folder and update the README.md by adding an 'App Showcase' section as first section. Embed the screenshot and the video, and provide a technical summary of the UI/UX features implemented."
