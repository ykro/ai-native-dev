# AI Native Dev

Repositorio oficial y código abierto de la serie **AI Native Dev** en YouTube y [Substack](https://ykro1.substack.com) por **Adrián Catalán** (`@adriancs.tech`).

> Si buscas los materiales, proyectos y presentaciones de la primera edición del curso (4 semanas), todo ese contenido se encuentra archivado en la carpeta [`./2026/`](./2026/).

Durante mucho tiempo aprender a programar con inteligencia artificial se enfocó en escribir instrucciones en una ventana de chat. Hoy el trabajo de ingeniería pasa por entender cómo operan por dentro los *Coding Agents*, cómo estructurar el contexto sin degradar la sesión y cómo preparar nuestros repositorios para que herramientas como Claude Code, Cursor, Codex o Antigravity trabajen con precisión.

Esta nueva etapa está organizada como una serie abierta de **10 temas** que crecen en espiral. Cada carpeta numerada contiene el código ejecutable, los scripts y las configuraciones que acompañan a los videos de teoría y práctica en YouTube y a los artículos en Substack.

## Índice de Temas

| # | Carpeta | Tema | Estado |
| :--- | :--- | :--- | :--- |
| **01** | [`01-coding-agents-internals/`](./01-coding-agents-internals/) | **Anatomía, Harnesses y Engines de los Coding Agents** | Disponible ([`src/mini_agent.py`](./01-coding-agents-internals/src/mini_agent.py), [`src/http_trace_inspector.py`](./01-coding-agents-internals/src/http_trace_inspector.py), [`tests/`](./01-coding-agents-internals/tests/)) |
| **02** | [`02-context-engineering-specs/`](./02-context-engineering-specs/) | **Context Engineering, Compaction y Spec-Driven Development** | Próximamente |
| **03** | [`03-agent-ready-repos/`](./03-agent-ready-repos/) | **Repositorios Agent-Ready, Arquitectura y `AGENTS.md`** | Próximamente |
| **04** | [`04-guardrails-hooks-sandboxing/`](./04-guardrails-hooks-sandboxing/) | **Guardrails Deterministas, Hooks y Sandboxing** | Próximamente |
| **05** | [`05-agent-skills-cli/`](./05-agent-skills-cli/) | **Agent Skills, Slash Commands y Workflows desde el CLI** | Próximamente |
| **06** | [`06-mcp-ergonomia-computer-use/`](./06-mcp-ergonomia-computer-use/) | **MCP, Computer Use y Diseño de Tools con Ergonomía Agéntica** | Próximamente |
| **07** | [`07-subagents-worktrees/`](./07-subagents-worktrees/) | **Orquestación de Subagents y Desarrollo en Paralelo (Worktrees)** | Próximamente |
| **08** | [`08-verification-evals-code-review/`](./08-verification-evals-code-review/) | **Closed-Loop Verification, Evals y Agentic Code Review** | Próximamente |
| **09** | [`09-agentic-security-bff-deploy/`](./09-agentic-security-bff-deploy/) | **Seguridad Agéntica, Contratos Tipados y Deploy a Producción** | Próximamente |
| **10** | [`10-background-agents-software-factories/`](./10-background-agents-software-factories/) | **Background Agents, Model Routing y Software Factories** | Próximamente |

## Estructura del Monorepo

```text
ai-native-dev/
├── README.md                                  # Índice general de la serie
├── 01-coding-agents-internals/                # Tema 01: Harness mínimo, 4 primitivas e inspector HTTP
├── 02-context-engineering-specs/              # Tema 02: Context Engineering y RePPIT
├── 03-agent-ready-repos/                      # Tema 03: Auditor Agent-Ready y AGENTS.md
├── 04-guardrails-hooks-sandboxing/            # Tema 04: Hooks y aislamiento
├── 05-agent-skills-cli/                       # Tema 05: SKILL.md y automatización CLI
├── 06-mcp-ergonomia-computer-use/             # Tema 06: Servidores MCP y Browser MCP
├── 07-subagents-worktrees/                    # Tema 07: Subagents y git worktree
├── 08-verification-evals-code-review/         # Tema 08: Verificación y revisión en capas
├── 09-agentic-security-bff-deploy/            # Tema 09: Seguridad, OpenAPI BFF y Cloud Run
├── 10-background-agents-software-factories/   # Tema 10: Background Agents y Software Factories
└── 2026/                                      # Archivo completo de la edición 2026 (Week 1 a Week 4)
```

**Nos vemos en el código.**
