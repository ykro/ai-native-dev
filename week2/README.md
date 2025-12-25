# Week 2: AI-Native SDLC & Agentic Workflows

Welcome to Week 2. This week we focus on **Orchestration**. You will learn how to break down a complex application into roles and manage a team of AI agents to build "TraveLens," a premium travel planning application.

## Topics Covered
*   **Basics on SDLC and Roles**: Understanding the Software Development Life Cycle and mapping it to AI Roles.
*   **Role-Based Prompting**: 8 distinct roles (Architect, Frontend, Backend, etc.) to prevent context drift.
*   **Sequential Workflows**: How to chain agent outputs to build robust software.
*   **Premium UI Logic**: Implementing Masonry Grids, Glassmorphism, and Bento layouts.

## The AI Native Toolchain
*   **Next.js 16**: The application framework.
*   **Gemini 3 Flash**: Selected for its <1s latency in interactive UI elements.
*   **Unsplash API**: Providing dynamic visual context.
*   **Tailwind CSS v4**: For utility-first styling.

## Directory Structure

*   `slides/`: Contains the presentation deck (`slides.md`).
*   `prompts/`: Contains the master `prompts.md` with the 8-role definition.
*   `travelensapp/`: The reference source code.

## Weekly Project: UI/UX Refinement

**Objective**: The base TraveLens app is functional but lacks "Delight". Your task is to implement features that improve the **Interaction Design**.

**Definition of Done**:
- [ ] **View Transitions**: Implement smooth morphing animations between the Grid and Detail view.
- [ ] **Favorites System**: Create a "Heart" button that persists liked destinations to `localStorage`.
- [ ] **Dark Mode**: Implement a theme toggle that respects the Glassmorphism aesthetic in both modes.
- [ ] **Smart Sharing**: Create a custom "Share" UI that generates a formatted clipboard summary.
- [ ] **Toast Notifications**: Replace native alerts with a proper Toast library (e.g., `sonner`).
