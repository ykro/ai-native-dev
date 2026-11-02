# Week 3: Debugging, Testing & Documentation

Welcome to Week 3. This week we focus on **Reliability**. You will learn how to use AI Agents not just to write code, but to debug it, test it, and document it professionally.

## Topics Covered

*   **Debugging**: Structured workflows (Context Injection -> Hypothesis -> Fix) to solve logic and state bugs.
*   **Testing**: AI-Driven TDD with Vitest and React Testing Library.
*   **Documentation**: Generating architectural diagrams (Mermaid) and Onboarding guides automatically.
*   **Hallucinations**: Identifying and avoiding "Ghost Libraries" (The Nano Banana Trap).

## Project Preview

| Visual Discovery | Rental Flow |
| :---: | :---: |
| ![Home](rent-my-gear/assets/home_demo.png) | ![Detail](rent-my-gear/assets/detail_demo.png) |


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

## The Challenge: Feature Expansion (TDD)

**Objective**: Add a new "Smart Insurance" feature to the application using Strict AI-Driven TDD.

**Context**: Users are breaking equipment. We need an optional protection plan.
*   **Photography**: 20% fee.
*   **Others**: 10% fee.

**Definition of Done**:
- [ ] **100% Base Coverage**: Ensure existing demo app tests pass with 100% coverage.
- [ ] **Feature TDD**: Implement "Smart Insurance" maintaining 100% coverage.
- [ ] **Documentation**: Update `docs/DIAGRAMS.md`, `docs/ONBOARDING.md`, and `README.md`.
- [ ] **Verification**: Submit proof of 100% coverage from `npm run test:coverage`.

## Resources

### Debugging & Agents
*   [The Debugging Decay Index (2025)](https://arxiv.org/abs/2405.08775)
*   [Debugging with LLMs (DebugEval)](https://arxiv.org/abs/2401.04620)
*   [Prompt Engineering for Debugging](https://www.promptingguide.ai/applications/coding)

### Testing Strategy
*   [Rethinking Test Efficiency with AI (Martin Fowler)](https://martinfowler.com/articles/2023-test-automation-ai.html)
*   [React Testing Library: Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
*   [TDD with GitHub Copilot](https://github.blog/2023-08-30-how-to-use-github-copilot-for-test-driven-development/)

### Documentation & Knowledge
*   [Docs as Code: A Comprehensive Guide](https://www.writethedocs.org/guide/docs-as-code/)
*   [The "Bus Factor" and Technical Debt](https://understandlegacycode.com/blog/what-is-the-bus-factor/)
*   [Google's Style Guide for Dev Docs](https://developers.google.com/style)
