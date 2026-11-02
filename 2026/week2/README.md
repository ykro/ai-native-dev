# Week 2: AI-Native SDLC & Agentic Workflows

Welcome to Week 2. This week we focus on **Orchestration**. You will learn how to break down a complex application into roles and manage a team of AI agents to build "TraveLens," a premium travel planning application.

## Topics Covered
*   **Basics on SDLC and Roles**: Understanding the Software Development Life Cycle.
*   **Role-Based Prompting**: 8 distinct roles (Architect, Frontend, Backend, etc.).
*   **Agentic Workflows**: The "Agentic Loop" (Draft -> Review -> Refine) and Immutable Context.
*   **Deep Dive (Code Spotlight)**: Analyzing AI-generated code decisions (CSS Masonry, `cn` utility).
*   **Premium UI Logic**: Prompting for "Masonry Grids", "Glassmorphism", and "Visual Hierarchy".

## The AI Native Toolchain
*   **Next.js 16**: The application framework.
*   **Gemini 3 Flash**: Selected for its <1s latency.
*   **Unsplash API**: Providing dynamic visual context.
*   **Tailwind CSS v4**: For utility-first styling.

## Directory Structure

*   `slides/`: Contains the presentation deck (`slides.md`).
*   `prompts/`: Contains the master `prompts.md` with the 8-role definition.
*   `travelensapp/`: The reference source code.

## The Challenge: Polish to Perfection

**Objective**: The current app is functional. Your job is to make it delightful.

**Definition of Done**:
- [ ] **Favorites**: Implement "Save" button with `localStorage` persistence.
- [ ] **UI Animation**: Clicking "Save" triggers a Heart/Confetti scale effect.
- [ ] **UI Polish**: Grid items load with a "Staggered Fade-in" effect.
- [ ] **UX**: Masonry Grid supports Keyboard Navigation (Arrow Keys).
- [ ] **UX**: "Recent Searches" chips appear below the search bar.

## Resources
*   [Software Engineering at Google](https://abseil.io/resources/swe-book)
*   [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)
*   [Strategies for rigorous agentic workflows (Anthropic)](https://www.anthropic.com/research/building-effective-agents)
*   [SWE-agent: Agent-Computer Interfaces (Princeton)](https://swe-agent.com/)
*   [Generative UI & Vercel AI SDK](https://vercel.com/blog/ai-sdk-3-generative-ui)
