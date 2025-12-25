---
marp: true
theme: gaia
paginate: true
footer: 'AI Native Dev - Universidad Galileo'
math: mathjax
style: |
  section {
    font-family: 'Inter', sans-serif;
    font-size: 26px;
  }
  code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75em;
  }
  blockquote {
    background: #f0f0f0;
    border-left: 10px solid #ccc;
    margin: 1.5em 10px;
    padding: 0.5em 10px;
  }
  h1, h2, h3 {
    color: #2563eb;
  }
  li {
    margin-bottom: 0.5em;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
  }
  th {
    background-color: #f2f2f2;
  }
---

<!-- _class: lead -->

# AI Native Dev
## Week 3
### Adrián Catalan
adriancatalan@galileo.edu

---

<!-- _class: lead -->

# Rent My Gear
## Premium Equipment Marketplace

---

# The Application

"Rent My Gear" is a Next.js 16+ application for renting photography, camping, and water sports equipment.

*   **Stack**: Next.js (App Router), Tailwind CSS, Shadcn UI.
*   **AI Integration**: "Nano Banana" (Gemini) for on-demand image generation.
*   **Problem**: It works... mostly. But it has hidden bugs, missing tests, and zero documentation.

---

# Rent My Gear: Visual Discovery

![bg 80%](../rent-my-gear/assets/home_demo.png)

---

# Rent My Gear: Rental Flow

![bg 80%](../rent-my-gear/assets/detail_demo.png)

---

<!-- _class: lead -->

# Topic 1: Debugging
## The AI as Sherlock Holmes

---

# 1. Why do we need Structured Debugging?

**The "Spray and Pray" Problem**
In traditional development, when a bug appears, we stare at `console.log` for hours.

*   **Cost**: Average developer spends 50% of their time debugging.
*   **Risk**: Fixing one bug often creates two more ("Whac-A-Mole").

**The AI Advantage**
An Agent can analyze the *Logic*, the *State*, and the *Semantics* simultaneously.

---

# 2. Traditional vs AI-Native Debugging

| Feature | Traditional Debugging | AI-Native Debugging |
| :--- | :--- | :--- |
| **Input** | `console.log("here")` | Error Trace + File Context |
| **Analysis** | Manual Stack Trace Reading | Pattern Matching + Semantic Analysis |
| **Hypothesis** | Developer Intuition | Multi-Factor Probability Assessment |
| **Fix** | Trial and Error | Step-by-Step Resolution Plan |

---

# 3. The "Fix-It" Loop

We don't just dump the error. We use a **Loop**:

1.  **Context Injection**: Provide the error logs + relevant file contents.
2.  **Hypothesis Generation**: Ask the AI to list 3 possible causes (Logic, State, Validation).
3.  **Step-by-Step Resolution**: Fix one layer at a time.
4.  **Verify**: Run the code to check if the error persists.

---

# 4. Prompt: Error Injection

To learn, we first break things. We ask the AI to **inject** subtle bugs.

> **Prompt**: "Modify the current codebase of **Rent my Gear** to introduce the following three subtle bugs for educational purposes:
> 1. **Logic Error:** In `src/lib/date-utils.ts`, modify the price calculation so it misses the final day (off-by-one).
> 2. **Validation Error:** In Zod schema, reject rentals > 7 days.
> 3. **State Error:** Make 'Confirmar' button stick in 'loading' state."

---

# 5. Anatomy of the Logic Bug

The AI modifies `date-utils.ts` to be *almost* correct.

```typescript
// src/lib/date-utils.ts (BUGGY VERSION)
export function calculateRentalDays(startDate: Date, endDate: Date): number {
  const days = differenceInDays(startDate, endDate);
  // ERROR: Missing the +1 inclusive day
  return Math.abs(days);
}
```

*   **Impact**: User rents Mon-Tue (2 days). System charges for 1 day.
*   **Business Cost**: 50% revenue loss on short rentals.

---

# 6. Prompt: Guided Debugging

Now we switch roles. We are the Senior Dev guiding the Agent to fix it.

> **Prompt**: "Users are reporting that the total price for rentals is lower than expected...
> 1. Run the application and inspect the terminal and browser logs.
> 2. Analyze `src/lib/date-utils.ts` and the Zod validation schemas.
> 3. Identify the logical errors and propose fixes."

**Note**: We force the agent to *Inspection* before *Action*.

---

# 7. Semantic Analysis

Why does the AI find this faster?
It understands the *intent* of "Rental Days".

*   **Human**: Sees `differenceInDays`. Thinks "Math is correct".
*   **AI**: Sees `Rental Context`. Knows "Rentals are usually date-inclusive". Flags mismatch between `Math` and `Business Domain`.

---

# 8. Key Takeaway: Debugging

> **Don't ask "Fix this Error".**
> **Ask "Explain why this state is reached".**

*   **Rule**: Always force the AI to explain the root cause (Hypothesis) before generating the code fix.
*   **Benefit**: You learn the system while the AI fixes it.

---

<!-- _class: lead -->

# Topic 2: Testing
## Trust, but Verify

---

# 1. The Reality of Testing

**"I'll write tests later"** is the biggest lie in software engineering.

*   **Traditional**: Writing mocks is tedious. Validating edge cases is hard.
*   **Result**: Low coverage, regression bugs on Fridays.

**AI-Driven TDD**:
The AI *loves* writing boilerplate. It makes TDD (Test Driven Development) faster than "coding and praying".

---

# 2. The V-Model in AI

We treat Testing as the mirror of Implementation.

```mermaid
graph TD
    Req[Requirements] --- Acc[Acceptance Tests]
    Des[Design] --- Sys[System Tests]
    Imp[Implementation] --- Unit[Unit Tests]
```

With AI, we generate the **Right Side** (Tests) often *before* or *immediately after* the **Left Side** (Code).

---

# 3. Prompt: Generating a Test Suite

We don't write `expect(x).toBe(y)` manually. We design the *scope*.

> **Prompt**: "Using **Vitest** and **React Testing Library**, generate a testing suite:
> 1. **Unit Tests:** Create tests for `src/lib/date-utils.ts` to validate price calculations with various ranges (1 day, 1 week, cross-month).
> 2. **Integration:** Simulate full rental flow (selecting category -> picking items).
> 3. **Edge Cases:** Handle Unsplash 404 errors."

---

# 4. Example: Variable Logic Testing

The AI generates exhaustive test cases we might miss (e.g., Leap Years).

```typescript
// Generated Test
describe("calculateRentalDays", () => {
  it("should calculate correct days for leap year crossing", () => {
    const start = new Date("2024-02-28");
    const end = new Date("2024-03-01");
    // 2024 is leap year: Feb 28, Feb 29, Mar 1 = 3 days
    expect(calculateRentalDays(start, end)).toBe(3);
  });
});
```

---

# 5. Integration Testing with AI

Testing React Components requires mocking context, router, and API.

*   **Challenge**: Correctly mocking `useRouter()` or `fetch`.
*   **AI Solution**: It generates the `setup` file automatically.

```typescript
// mocks/handlers.ts
export const handlers = [
  http.get('/api/gear', () => {
    return HttpResponse.json(mockInventory)
  }),
]
```

---

# 6. Edge Cases & Resilience

What happens when 3rd party APIs fail?
We ask the AI to simulate "Chaos".

*   **Scenario**: Unsplash API goes down (500 Error).
*   **Test**: Ensure `imageService` switches to "Nano Banana" fallback seamlessly.
*   **Prompt**: "Write a test that mocks a 500 error from Unsplash and asserts that `generateImageWithAI` is called."

---

# 7. Coverage is not Quality

**Warning**: AI can generate 100% coverage tests that check nothing.

*   **Bad Test**: `expect(true).toBe(true)`
*   **Good Test**: `expect(screen.getByText("Confirmar")).toBeDisabled()`

**Rule**: Always review the *assertions* generated by the AI.

---

# 8. Key Takeaway: Testing

> **AI turns Testing from a "chore" into a "spec".**

*   **Workflow**: Write Code -> Prompt for Tests -> Fix Code based on Test Failures.
*   **Benefit**: You get a robust safety net for free.

---

<!-- _class: lead -->

# Topic 3: Documentation
## Code is Temporary, Docs are Forever

---

# 1. The "Bus Factor"

**Bus Factor**: The number of team members that can get "hit by a bus" before the project stalls.
*   **Low Factor (1)**: Only YOU know how the build works.
*   **High Factor**: Anyone can read `ONBOARDING.md` and deploy.

**Documentation is the ultimate scalability tool.**

---

# 2. Types of AI Documentation

1.  **Narrative**: "How-to" guides (Onboarding).
2.  **Structural**: Diagrams (Sequence, Class, Cloud).
3.  **Reference**: API Docs (Swagger/OpenAPI).
4.  **Inline**: JSDoc comments for complex logic.

---

# 3. Prompt: Reverse Engineering

We ask the Agent to read our code and explain it back to us visually.

> **Prompt**: "Generate full technical documentation:
> 1. Create a **Mermaid sequence diagram** showing the 'Image Resolution Flow'.
> 2. Create a **Mermaid class diagram** for `inventoryService`.
> 3. Write an 'Onboarding Guide' explaining how to debug GCS connection."

---

# 4. Diagram: Image Resolution Flow

The AI visualizes the logic we built in Week 2.

```mermaid
sequenceDiagram
    participant C as Client
    participant IS as imageService
    participant AI as Nano Banana
    participant GCS as Google Cloud Storage

    C->>IS: Request Image
    alt Image Exists
        IS-->>C: Return URL
    else Image Missing
        IS->>AI: Generate(prompt)
        AI-->>IS: Base64
        IS->>GCS: Upload
        GCS-->>IS: Public URL
        IS-->>C: Return New URL
    end
```

---

# 5. Diagram: Component Hierarchy

Understanding the React Tree helps identifying re-renders.

```mermaid
graph TD
    HP[HomePage] --> HC[HeroCarousel]
    HP --> CB[CategoryButtons]
    
    subgraph Rental Flow
        RF[RentalFlow] --> DS[DateSelection]
        RF --> PS[PriceSummary]
        RF --> CF[Confirmation]
    end
```

---

# 6. The "Onboarding" Artifact

The `docs/ONBOARDING.md` file is crucial for new hires (or AI Agents).

**Key Sections**:
1.  **Prerequisites**: Node.js, Python 3.10+, `uv`.
2.  **Environment**: How to set up `.env.local`.
3.  **Debugging**: "If GCS fails, check `service-account.json` path".

*The AI writes this by scanning `package.json` and `.env.example`.*

---

# 7. Documentation as "Context"

When you have good docs, you can feed them back into the AI.

*   **Loop**:
    1.  AI writes Code.
    2.  AI writes Docs.
    3.  **Next Session**: You give AI the Docs -> It understands the Code faster.

---

# 8. Key Takeaway: System Memory

> **Documentation is the Long-Term Memory of your Team.**

*   **Rule**: Never merge a PR without updating the relevant `docs/` file.
*   **AI Role**: Use the "Documentation Role" to auto-generate the diff.

---

<!-- _class: lead -->

# Deep Dive
## Architectural Insights

---

# 1. The "Nano Banana" Trap (Hallucinations)

We asked the Agent to install **"Nano Banana Pro Local SDK"**.

*   **The Reality**: It doesn't exist. "Nano Banana" is a made-up name for Gemini.
*   **The Risk**: The Agent might give you `npm install nano-banana-sdk`.
*   **The Lesson**: Agents are "people pleasers". They hallucinate to satisfy requirements.
*   **Defense**: Always ask for "Official Documentation Links" or cross-reference with NPM.

---

# 2. Image Flow Architecture

A Hybrid Strategy using Server Actions and Cloud Storage.

```mermaid
flowchart TD
    User -->|View Item| App
    App -->|Check Cache| DB[(Inventory)]
    DB -->|Found| URL[Return URL]
    DB -->|Missing| Gen[Trigger Generation]
    
    subgraph "AI Pipeline"
        Gen -->|Prompt| Gemini
        Gemini -->|Image| Buffer
        Buffer -->|Stream| GCS[Cloud Storage]
    end
    
    GCS -->|Public Link| DB
    GCS --> URL
```

---

# 3. Code Spotlight: State Machines

We don't use simple booleans for complex flows. We use strict states.

```typescript
// src/components/features/RentalFlow/index.tsx
type RentalFlowStep = 
  | "selecting" 
  | "configuring" 
  | "reviewing" 
  | "confirmed";

// Benefits:
// 1. Impossible States: Can't be 'confirmed' and 'configuring' at once.
// 2. Type Safety: TypeScript ensures we handle every state.
```

---

<!-- _class: lead -->

# Weekly Project
## Feature Expansion with TDD

---

# The Challenge: "Smart Insurance"

**Context**: Users are damaging premium gears. We need an optional "Damage Protection" add-on.

**The Task**:
Implement a **Dynamic Insurance** feature that calculates a fee based on the category:
*   **Photography/Video**: 20% of daily rate (High Risk).
*   **All other categories**: 10% of daily rate.

**The Constraint**:
You must use **AI-Driven TDD**. You cannot write the implementation until the AI has generated a failing test suite.

---

# Definition of Done

- [ ] **Test Suite**: Created `insurance-calculator.test.ts` covering all categories *before* implementation.
- [ ] **Implementation**: `calculateInsurance(dailyRate, category)` logic is pure and verified.
- [ ] **UI Integration**: Added "Add Insurance" toggle to `PriceSummary.tsx`.
- [ ] **Docs Update**: Updated `docs/DIAGRAMS.md` flow chart to include the optional Insurance step.

---

<!-- _class: lead -->

# Resources
## Deep Dive Material

---

# Resources: Debugging & Agents

*   **[The Debugging Decay Index (2025)](https://arxiv.org/abs/2405.08775)** - Why AI struggles with long debugging sessions.
*   **[Debugging with LLMs: A Benchmark (DebugEval)](https://arxiv.org/abs/2401.04620)** - Research on how LLMs perform on Python/C++ bugs.
*   **[Systematic Debugging with AI Agents](https://engineering.atspotify.com/2023/12/how-we-use-ai-for-debugging-at-spotify/)** - Real-world patterns from Spotify usage.
*   **[The Art of Error Injection](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/error-injection/)** - Microsoft Engineering Playbook on learning through breakage.
*   **[Prompt Engineering for Debugging](https://www.promptingguide.ai/applications/coding)** - Techniques to force "Reasoning Trace" before "Code Fix".

---

# Resources: Testing Strategy

*   **[Rethinking Test Efficiency with AI](https://martinfowler.com/articles/2023-test-automation-ai.html)** - Martin Fowler's blog on effective AI testing.
*   **[React Testing Library: Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)** - Kent C. Dodds (Creator) on what NOT to do.
*   **[Vitest vs Jest: A Performance Comparison](https://vitest.dev/guide/comparison.html)** - Why we chose Vitest for the modern stack.
*   **[TDD with GitHub Copilot](https://github.blog/2023-08-30-how-to-use-github-copilot-for-test-driven-development/)** - Official guide on the "Test-First" workflow with AI.
*   **[The V-Model in the Age of AI](https://towardsdatascience.com/the-v-model-for-ai-projects-9f892551525d)** - Adapting traditional verification models to generative AI.

---

# Resources: Documentation & Knowledge

*   **[Docs as Code: A Comprehensive Guide](https://www.writethedocs.org/guide/docs-as-code/)** - The industry standard philosophy we follow.
*   **[The "Bus Factor" and Technical Debt](https://understandlegacycode.com/blog/what-is-the-bus-factor/)** - Why documentation is an asset, not a chore.
*   **[Mermaid.js for Developers](https://mermaid.js.org/intro/getting-started.html)** - Visualizing code without leaving Markdown.
*   **[Technical Debt Records (TDRs)](https://18f.gsa.gov/2015/10/05/managing-technical-debt/)** - 18F's approach to documenting decisions and compromises.
*   **[Google's Style Guide for Developer Documentation](https://developers.google.com/style)** - Gold standard for writing clear technical guides.
