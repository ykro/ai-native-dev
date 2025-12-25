# Week 3: Debugging, Testing & Documentation

Welcome to Week 3. This week we focus on **Reliability**. You will learn how to use AI Agents not just to write code, but to debug it, test it, and document it professionally.

## Topics Covered

*   **Debugging**: Structured workflows (Context Injection -> Hypothesis -> Fix) to solve logic and state bugs.
*   **Testing**: AI-Driven TDD with Vitest and React Testing Library.
*   **Documentation**: Generating architectural diagrams (Mermaid) and Onboarding guides automatically.
*   **Hallucinations**: Identifying and avoiding "Ghost Libraries" (The Nano Banana Trap).

## The AI Native Toolchain
*   **Vitest**: Blazing fast unit test framework.
*   **React Testing Library**: Testing UI components by user interaction.
*   **Mermaid.js**: Diagramming complex flows as code.
*   **Google Cloud Storage**: Asset persistence for our "Smart Image" strategy.
*   **Zod**: Runtime schema validation.

## Directory Structure

### `rent-my-gear/`
The Next.js Application source code.
*   **Stack**: Next.js 16, Tailwind, Shadcn.
*   **Docs**: See `docs/` folder for Architecture and Diagrams.

### `prompts/`
Contains the **Prompt Library** for this week.
*   **`prompts.md`**: Includes specific prompt chains for "Guided Debugging", "Generating Test Suites", and "Reverse Engineering Architecture".

### `slides/`
Contains the **Course Materials**.
*   **`slides.md`**: The lecture slides in MARP Markdown format.

## The Challenge: Reliability & Polish

**Objective**: The current app works but has critical bugs and no safety net. Fix it and prove it works.

**Definition of Done**:
- [ ] **Fix Logic Error**: `date-utils.ts` calculates exact day range (fix off-by-one).
- [ ] **Fix Validation**: Zod schema allows rentals > 7 days.
- [ ] **Fix State**: `RentalFlow` button stops loading after error/success.
- [ ] **Test Coverage**: > 80% coverage on `date-utils` and `RentalFlow`.
- [ ] **Docs**: Complete `ONBOARDING.md` and `DIAGRAMS.md` (Mermaid).

## Resources
*   [Vitest Documentation](https://vitest.dev/)
*   [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)
*   [Mermaid.js Documentation](https://mermaid.js.org/intro/)
*   [Google Cloud Storage Docs](https://cloud.google.com/storage/docs)
