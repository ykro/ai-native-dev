### 1. Error Injection

Modify the current codebase of **Rent my Gear** to introduce the following three subtle bugs for educational purposes:
* 1. **Logic Error:** In `src/lib/date-utils.ts`, modify the price calculation so it misses the final day of the range (an 'off-by-one' error).
* 2. **Validation Error:** In the **Zod** schema for the rental process, set a constraint that incorrectly rejects rentals longer than 7 days, even though the business rule allows them.
* 3. **State Error:** In the `RentalFlow` component, make the 'Confirmar' button stay in a permanent 'loading' state if the user selects a specific category, without showing any error message.
* 4. Introduce a subtle **Hydration Mismatch** error in the `HeroCarousel.tsx` component. Use `Math.random()` or `new Date()` directly inside the component's initial state without `useEffect` or `suppressHydrationWarning`.

Do not fix them. Ensure the code still compiles but behaves incorrectly.

---

### 2. Guided Debugging
Users are reporting that the total price for rentals is lower than expected, that they cannot rent items for more than a week, and that the "Confirmar" button gets stuck in a permanent loading state when trying to rent water sports equipment.
                                                                                                                                    
* 1. Run the application and inspect the terminal and browser logs.
* 2. Analyze src/lib/date-utils.ts and the Zod validation schemas for pricing and date issues.
* 3. Analyze the RentalFlow component and its children (PriceSummary.tsx) for state management issues related to the confirm button.
* 4. Identify the logical errors and propose fixes that restore the correct price calculation, the 7+ day rental capability, and proper confirmation flow for all categories.
                                                                                                                                    
Fix the code and show me a summary of the fixes. 
---

### 3. Fixing the "invisible" error
The UI 'flickers' or shows different content than the server-rendered HTML. Why does this happens? Investigate components that render dynamic content on the home page.  

**Note for students:**
If the AI suggests it is a CSS issue, insist on checking the React rendering cycle and values used in initial state (useState).

---

### 4. Testing Suite

Using **Vitest** and **React Testing Library**, generate a testing suite for the rental module:
* 1. **Unit Tests:** Create tests for `src/lib/date-utils.ts` to validate price calculations with various date ranges (1 day, 1 week, across different months).
* 2. **Integration Tests:** Simulate the full rental flow: selecting a category, picking a gear item, choosing dates, and clicking 'Confirmar'. Ensure the success toast appears only when data is valid.
* 3. **Edge Cases:** Test how the system handles the 'Nano Banana' fallback if the Unsplash API returns a 404 error.

Run all the tests, make a document summarizing the results and reference in the `README.md`
---

### 5. Documentation

Generate full technical documentation for **Rent my Gear**:
* 1. Document everything that's needed for project understanding
* 2. Create a **Mermaid sequence diagram** showing the 'Image Resolution Flow' (JSON file -> Nano Banana -> GCS Persistence).
* 3. Create a **Mermaid class diagram** for the `inventoryService` and `imageService` interactions.
* 4. Write an 'Onboarding Guide' that explains code, architecture, all that's needed for a new developer to join the project, how to debug the GCS connection and how to add a new category to the system without breaking the existing validation schemas."

Reference all the documents in the `README.md`
---

### 6. Hallucination Demo

We want to integrate the **Nano Banana Pro Local-Offline SDK for Next.js 16** to process images directly on the user's GPU without using API calls. Do not change the project yet, but provide the exact npm command to install this local SDK, configuration and show the code needed for the `offline-gen` mode.

**Note for students:**
* If the AI suggest a command or library that seems "too good to be true", perform some class of cross-verification, do a web search or npm look-up and ask for official documentation.
* If you're convinced it's an hallucination, reset the session and provide the agent proper documentation(i.e. **context7**) to bound it to current technical scope.
* Agents are usually "obliging", if you request something "impossible" they will try to find a solution, and might hallucinate something(library, command, code, etc) that seems very real. Always check the dependencies.

