---
marp: true
theme: gaia
paginate: true
footer: 'AI Native Dev - Universidad Galileo'
style: |
  section {
    font-family: 'Inter', sans-serif;
    font-size: 28px;
  }
  code {
    font-family: 'JetBrains Mono', monospace;
  }
---

<!-- _class: lead -->

# AI Native Dev
## Week 1
### Adrián Catalan
adriancatalan@galileo.edu

---

# Introduction: PawsMatch

PawsMatch is a **pet adoption application** designed to connect loving families with pets in need.

- **Objective**: Tinder-like interface for adopting pets.
- **Tech Stack**: React, Vite, Tailwind CSS, Framer Motion.
- **UX**: Premium, mobile-first, glassmorphism design.

![bg right:40% 80%](../pawsmatch/assets/screenshot.png)

---

# Demo

![width:600px](../pawsmatch/assets/demo.webp)

*Zero-latency swiping implementation with pre-fetch buffer.*

---

<!-- _class: lead -->

# Theme 1: Terminology
## Under the Hood of LLMs

---

# 1. Large Language Model (LLM)

An **LLM** is a probabilistic system trained to predict the next token in a sequence. It does not "know" facts; it understands statistical correlations between words.

> "It's not a search engine, it's a reasoning engine."

*   **Architecture**: Transformer (Attention Is All You Need, 2017).
*   **Scale**: Billions of parameters (weights) learned from massive datasets.

---

# LLM Flow Diagram

How an LLM processes your input:

![width:900px](https://mermaid.ink/img/pako:eNplkUtvwjAMx7_Kya0T2gcelxHaaZOGNglpL1y8Jk0VNUkc1w71u880FRTiF_u_xP62j2hNC0SRF-tS81q_iBHe5dI64K7Cg0Y7D8Z5cIahkZ6M8w0W7wtuTPAkQgMd2kZq3N0Y-6DR0L0n7OEc_9CgIf_O9578278yqK_S4P3Bmj_StGvQ-o73aY5W-OAvmNIVjBkoWJ0V7Ag7sKIVG1iRml7BmtT4CtasJipYiw3s7I72O4N36G_N4KAdGj91f9fgER3S-S1ZkqY5y7KMyTJJM1lkCSs4SzmTUcZSTpI0SXmScbBMH0We3D-9Yg?type=png)

<!-- 
graph LR
    A[Input Text] --> B(Tokenization)
    B --> C(Embeddings)
    C --> D(Transformer Layers)
    D --> E(Probability Dist.)
    E --> F[Next Token]
-->

---

# 2. Transformers: The Engine

Transformers allow models to process entire sequences of data in parallel, rather than sequentially.

**Key Innovation: Self-Attention**
The model assigns a "relevance score" to every word's relationship with every other word.

*Example*: In "The animal didn't cross the street because **it** was too tired", the model knows "**it**" refers to "animal", not "street".

---

# Transformer Architecture

![width:900px](https://mermaid.ink/img/pako:eNp1kMtqwzAQRX9FzKoF2_GqLroIJA8IdNN0EaxRjD0WPFKMjBNC_r1yrJSSQrdzmXunnoky1lSIkoytK83W-lmM8DbX3gM7iwAa7QKY5MCFhUYGMskP2NwuuTfBkwgNDGg7qXF3ZxyCRkP_kXCAc_xHg4b8Kz848q__yqC-S4PPBxs-Stq3aP0dHyY5WuHLv2DKKDBmoGB1UbAnHMCKVmxgRWp6BWtS4ytYsxqpYC02cLAHOu4MPqC_NYCjdmj83P1dgwd0SOe35Cwr8oznOcsLRrKMF6wQsJyzQqSCLHmekCznrMjBCn2WZOXj0ytmZw?type=png)

<!-- 
graph LR
    Inputs --> Embeddings
    Embeddings --> Encoders
    Encoders --> Decoders
    Decoders --> Output
-->

---

# 3. Tokens: The Atoms of Language

LLMs don't read words/letters; they read **tokens**.
A token can be a word, part of a word, or a space.

- **English**: ~0.75 words per token.
- **Code**: High efficiency (keywords usually single tokens).

**Example**:
```
"Ingeniería" -> [Ingen, iería] (2 tokens)
"import" -> [import] (1 token)
```

---

# 4. Context Window (Working Memory)

The **Context Window** is the maximum amount of text (input + output) the model can process at once.

If it falls out of the window, the model forgets it. The industry is racing towards "infinite context".

| Model | Context Window |
| :--- | :--- |
| **Gemini 3 Pro** | 10M Tokens |
| **Claude Opus 4.5** | 5M Tokens |
| **GPT-5.2** | 2M Tokens |

---

<!-- _class: lead -->

# Theme 2: Tech Stack
## The AI Native Toolchain

---

# Primary Tools

### 1. Claude Code (Anthropic)
- **Role**: The "Deep Thinker".
- **Strengths**: Complex reasoning, large context window (200k+), architectural planning.
- **Usage**: Terminology understanding, initial planning, refactoring logic (ReAct loops).

### 2. Antigravity (Google DeepMind)
- **Role**: The "Agentic Engineer".
- **Strengths**: Tool usage, file manipulation, deep context integration, creating artifacts.
- **Usage**: Execution, file creation, systematic modifications.

---

# Other Tools

### 3. Gemini CLI
- **Role**: Specialized tasks and integration with Google ecosystem.

---

# The Workflow

```
+----------------+      +----------------+      +----------------+
|  Idea / Prompt | ---> |   Claude Code  | ---> |   Antigravity  |
+----------------+      | (Reason & Plan)|      | (Exect & Files)|
                        +----------------+      +----------------+
                                                        |
                                                        v
                                                +----------------+
                                                |   Final Code   |
                                                +----------------+
```

---

<!-- _class: lead -->

# Theme 3: Basic Prompting
## Strategies & Prompts

---

# Context Engineering

**Prompt Engineering**: Writing the best letter to get a specific job done (Micro).

**Context Engineering**: Designing the entire office environment, tools, and filing system so the worker succeeds every time (Macro).

It involves curating the "System Prompt", identifying necessary files, and managing the "State" of the conversation.

---

# Tool Calling

**Tool Calling** is the mechanism that allows an LLM to "act" in the real world.

1.  **Intent**: The model recognizes it needs external info (not in its weights).
2.  **Output**: Instead of text, it outputs a structured command (e.g., JSON).
3.  **Execution**: The system runs the command (e.g., `read_file`, `search_web`).
4.  **Feedback**: The result is fed back to the model as context.

---

# 1. Zero-Shot
Asking without examples. Fast, but unpredictable.

# *Example: Project Initialization*
**(From Phase 1)**
One-Shot + Tool Calling

> "We are building a web app called PawsMatch... Use uv to initialize a new Python project... Use gemini-3-flash-preview to generate a pets.json file... Create a README.md... Verify the existence of both files..."

---

# 2. Few-Shot (K-Shot)
Providing examples (shots) to guide the model. Ensures adherence to style/structure.

# *Example: Coding Standards*
**(From Phase 2)**

> "I want to define the coding standards for PawsMatch. Here are 3 examples...
> **Example 1 (Types)**: `export interface User...`
> **Example 2 (Service)**: `export const fetchUsers...`
> Based on these examples... generate pet.ts..."

---

# 3. Context-Augmented
Grounding the AI with external documentation before generating code.

# *Example: Project Scaffolding*
**(From Phase 3)**

> "Using context7, fetch the latest stable documentation for Vite, React, and Tailwind CSS. Initialize a project... using these versions... Follow this project structure: `src/components`, `src/hooks`... Update README.md..."

---

# 4. Chain of Thought (CoT)
Encourages "thinking aloud". Logic: `Input -> Reasoning Steps -> Conclusion`.

# *Example: Architecture Analysis*
**(From Phase 4)**

> "Search the web for The Dog API... Before coding, perform an analysis to:
> 1. Read the local pets.json...
> 2. Identify the exact JSON path...
> 3. Detail how to fetch...
> Do not write the code yet; provide the analysis first."

---

# 5. Tree of Thoughts (ToT)
Explores multiple reasoning paths (branches) before selecting the best one.

# *Example: Key Decisions*
**(From Phase 5)**

> "Explore three technical approaches for the card stack behavior:
> - Simple state
> - Pre-fetch stack
> - Virtualized list
> Compare them regarding network usage and UX fluidity. Wait for my decision before implementing."

---

# 6. ReAct (Reasoning + Acting)
Synergy between logic and tools. Loop: `Thought -> Action -> Observation -> Thought`.

# *Example: Refactoring*
**(From Phase 6)**

> "Analyze the entire codebase... focus on src/services... Your task is to refactor the UI...
> 1. Review README...
> 2. Install lucide-react...
> 4. Use useRef guards...
> 6. Ensure the UI feels like a premium native app..."

---

# 7. Feedback Loop
Using error traces as context.

# *Example: Debugging*
**(From Phase 7)**

> "The application is currently throwing an error in the console... Run it, capture the full stack trace... and use that information to fix the bug."

---

# 8. Explanation Pattern
Asking the AI to explain its own work for documentation.

# *Example: Documentation*
**(From Phase 8)**

> "Analyze the implementation in src/services/petProvider.ts. Explain in detail how the connection works... Lifecycle... JSON path... Synchronization... Use a technical but accessible tone..."

---

# 9. Verification Pattern
Automating the proof of work.

# *Example: Verification*
**(From Phase 9)**

> "Use your tools to launch the development server... Take a high-quality screenshot... Record a short video... Save these files in a 'assets/' folder..."

---

<!-- _class: lead -->

# Deep Dive
## Architecture & Pre-fetching

---

# The Problem: Network Latency

In a "Tinder-like" app, waiting 1-2 seconds between swipes for the next image kills the experience.

**Solution**: The Pre-fetch Stack.

1.  **Buffer**: Keep `N` pets in memory.
2.  **Background Fetch**: When user swipes, immediately fetch `N+1`.
3.  **Image Pre-loading**: Render hidden `<img>` tags to force browser caching.

---

# Implementation: `usePetStack.ts`

```typescript
const BUFFER_SIZE = 3;

export function usePetStack() {
    // ...
    const advance = useCallback(() => {
        setStack((prev) => {
            const [, ...rest] = prev; // Remove first (FIFO)
            return rest;
        });

        // Background fetch to replenish
        fetchRandomPetProfile().then((newPet) => {
            setStack((prev) => [...prev, newPet]);
        });
    }, []);
}
```

---

# Service Layer: `petProvider.ts`

Merging local data (Bios) with Remote API (Images).

```typescript
export const fetchRandomPetProfile = async (): Promise<PetProfile> => {
    // 1. Local Data
    const randomPet = pets[Math.floor(Math.random() * pets.length)];
    
    // 2. Remote Data (with Fallback)
    try {
        const response = await fetch(DOG_API_URL);
        // ... validation ...
        imageUrl = data.message; 
    } catch (error) {
        console.error('Using fallback image');
    }

    // 3. Merge
    return { ...randomPet, imageUrl };
};
```

---

<!-- _class: lead -->

# Weekly Project
## Re-build "PawsMatch"

---

# The Challenge

**Objective**: Re-build the PawsMatch demo app using a **different technology stack**.

**Constraints**:
1.  **Functionality**: Must have 100% feature parity (Swiping, API integration, Adoption flow).
2.  **Design**: Must look *exactly* the same (Glassmorphism, Animations).
3.  **Tech**: You cannot use React.

**Suggested Stacks**:
- Vue 3 + Pinia + Tailwind
- Svelte 5 + Tailwind
- Vanilla JS + CSS Modules (Hard mode)

---

# Definition of Done

- [ ] Project compiles/runs without errors.
- [ ] Swiping right "Likes", swiping left "Passes".
- [ ] Pets are fetched from Dog CEO API + merged with local JSON.
- [ ] **Pre-fetch buffer** is implemented (no loading between swipes).
- [ ] Responsive mobile-first design.
- [ ] README.md documents the new stack and how to run it.

---

# Resources (1/2)

**Visual Guides to LLMs**
- [The Illustrated Transformer (Jay Alammar)](https://jalammar.github.io/illustrated-transformer/) - The classic visual guide to Attention.
- [The Illustrated GPT-2 (Jay Alammar)](https://jalammar.github.io/illustrated-gpt2/) - How GPT models actually generate text.
- [Transformers Explained Visually (Towards Data Science)](https://towardsdatascience.com/transformers-explained-visually-part-1-overview-of-functionality-95a6dd96045b)

**Prompt Engineering & Agents**
- [Chain-of-Thought Prompting Elicits Reasoning (Paper)](https://arxiv.org/abs/2201.11903) - The original Google Research paper.
- [ReAct: Synergizing Reasoning and Acting (Paper)](https://react-lm.github.io/) - The foundation of Agentic AI.
- [Building LLM Applications for Production (Chip Huyen)](https://huyenchip.com/2023/04/11/llm-engineering.html)

---

# Resources (2/2)

**Deep Dive Articles**
- [What is Context Engineering? (Anthropic)](https://www.anthropic.com/context-engineering) - How to design better inputs.
- [Tool Use & Function Calling Guide](https://platform.openai.com/docs/guides/function-calling) - Conceptual overview.
- [The Rise of Agents (Sequoia)](https://www.sequoiacap.com/article/ai-agents/) - Business and tech landscape of agents.

**Tools**
- [Anthropic Claude](https://www.anthropic.com/claude)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

