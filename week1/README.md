# Week 1: Foundations & Terminology

Welcome to the first week of the **AI Native Dev** course. This week focuses on establishing the core terminology, understanding the "AI Native" toolchain, and mastering basic prompt engineering strategies.

## Topics Covered

*   **Terminology**: LLM Internals (Tokens, Context Window), Transformer Architecture, and Key Concepts (Hallucinations, Stochasticity).
*   **Models**: Gemini 3 Pro, Claude Opus 4.5, GPT-5.2.
*   **Prompt Engineering**: Moving from basic Zero-Shot to advanced ReAct loops and Chain-of-Thought.

## The AI Native Toolchain
*   **Claude Code (Anthropic)**: The "Deep Thinker" for reasoning and architecture.
*   **Antigravity (Google DeepMind)**: The "Agentic Engineer" for execution and file manipulation.
*   **Cursor**: The "AI-Native IDE" for speed, polish, and vibe coding.
*   **Gemini CLI**: Utility for quick prototyping and API testing.

## Prompting Strategies
We cover 9 specific phases of interaction with LLMs, moving from basic to advanced:
1.  **Zero-Shot**
2.  **Few-Shot (K-Shot)**
3.  **Context-Augmented**
4.  **Chain of Thought (CoT)**
5.  **Tree of Thoughts (ToT)**
6.  **ReAct (Reasoning + Acting)**
7.  **Feedback Loops**
8.  **Explanation**
9.  **Verification**

## Directory Structure

### `pawsmatch/`
Contains the **Introduction Demo App** ("Tinder for Pets").
*   **Stack**: React, Vite, Tailwind CSS, Framer Motion.
*   **Features**: Glassmorphism UI, Zero-latency swiping (pre-fetch stack).
*   **Goal**: This is the reference app you will re-build in the Weekly Project using a *different* stack.

### `prompts/`
Contains the **Prompt Library**.
*   **`prompts.md`**: A comprehensive markdown file detailing the 9 phases of interaction. It includes exact prompts used to build the PawsMatch app, serving as a practical reference for your own workflows.

### `slides/`
Contains the **Course Materials**.
*   **`slides.md`**: The lecture slides in MARP Markdown format. Cover all theoretical concepts, diagrams, and project requirements.

## The Challenge

**Objective**: Re-build the PawsMatch demo app using a **different technology stack**.

**Definition of Done**:
- [ ] Project compiles/runs without errors.
- [ ] Swiping right "Likes", swiping left "Passes".
- [ ] Pets are fetched from Dog CEO API + merged with local JSON.
- [ ] **Pre-fetch buffer** is implemented (no loading between swipes).
- [ ] Responsive mobile-first design.
- [ ] README.md documents the new stack and how to run it.

**Constraints**:
1.  **Functionality**: Must have 100% feature parity.
2.  **Design**: Must look *exactly* the same (Glassmorphism).
3.  **Tech**: You cannot use React.

## Resources
*   [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/)
*   [The AI-Native Developer: A manifest](https://www.swyx.io/ai-native-dev)
*   [Chain-of-Thought Prompting Elicits Reasoning](https://arxiv.org/abs/2201.11903)
*   [Building LLM Applications for Production](https://huyenchip.com/2023/04/11/llm-engineering.html)
*   [My Experience with Claude Code 2.0](https://sankalp.bearblog.dev/my-experience-with-claude-code-20-and-how-to-get-better-at-using-coding-agents/)

Good luck!
