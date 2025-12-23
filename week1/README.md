# Week 1: Foundations & Terminology

Welcome to the first week of the **AI Native Dev** course. This week focuses on establishing the core terminology, understanding the "AI Native" toolchain, and mastering basic prompt engineering strategies.

## 📚 Topics Covered / Tópicos

### 1. Terminology (Terminología)
*   **LLM Internals**: Tokens, Context Window (Memoria de trabajo), Transformer Architecture.
*   **Models**: Gemini 3 Pro, Claude Opus 4.5, GPT-5.2.
*   **Key Concepts**: Hallucinations, Stochasticity (Nondeterministic nature).

### 2. The AI Native Toolchain (Tech Stack)
*   **Claude Code (Anthropic)**: The "Deep Thinker" for reasoning and architecture.
*   **Antigravity (Google DeepMind)**: The "Agentic Engineer" for execution and file manipulation.
*   **Cursor**: The "AI-Native IDE" for speed, polish, and vibe coding.
*   **Gemini CLI**: Utility for quick prototyping and API testing.

### 3. Prompting Strategies (Estrategias de Prompting)
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

---

## 📂 Directory Structure / Estructura de Carpetas

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

---

## 🛠️ Weekly Project

**Objective**: Re-build the PawsMatch demo app using a different technology stack (e.g., Vue, Svelte, or Vanilla JS).
**Constraints**:
1.  100% Feature Parity.
2.  Identical Design (Glassmorphism).
3.  **No React**.

Good luck! / ¡Buena suerte!
