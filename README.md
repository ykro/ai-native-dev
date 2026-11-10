# AI Native Dev

Repositorio oficial y código abierto de la serie **AI Native Dev** en YouTube y [Substack](https://ykro1.substack.com) por **Adrián Catalán** (`@adriancs.tech`).

> Los materiales, proyectos y presentaciones de la primera edición (4 semanas) están archivados en [`./2026/`](./2026/).

Durante mucho tiempo aprender a programar con inteligencia artificial se enfocó en escribir instrucciones en una ventana de chat. Hoy el trabajo pasa por entender qué hace un *Coding Agent* entre tu instrucción y su respuesta, cómo cuidar el contexto de una sesión larga y qué necesita un repositorio para que herramientas como Claude Code, Cursor, Codex o Antigravity trabajen con precisión.

La serie se organiza en **10 temas** (00 a 09) que crecen en espiral. El hilo son los cuatro proyectos de la edición 2026 (PawsMatch, TraveLens, Rent My Gear y TraderPulse), actualizados a versiones vigentes. Cada carpeta numerada contiene el código ejecutable que acompaña a los videos y a los artículos.

## Videos y Lecturas en Substack

- **Playlist en YouTube** · [AI Native Dev](https://www.youtube.com/playlist?list=PLADgjqdtJ3Bc)
- **Tema 00 en YouTube** · [Teoría · Modelo mental](https://youtu.be/L7MwTArreqw) · [Práctica · Harness desde cero](https://youtu.be/tFTEsbVYQvE)
- **Artículos relacionados en Substack (`ykro1.substack.com`)**
  - [Cómo delegarle un proyecto a un agente de IA sin perder el control](https://ykro1.substack.com/p/delegar-a-un-agente)
  - [Primero la spec](https://ykro1.substack.com/p/primero-la-spec)
  - [Gemini 4 Argon trabajando en auditar, construir y deployear código](https://ykro1.substack.com/p/gemini-4-argon-trabajando-en-auditar)

## Índice de temas

| # | Carpeta | Tema | Proyecto | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **00** | [`00-engine-y-harness/`](./00-engine-y-harness/) | **Lo que pasa cuando le pides algo a un Coding Agent** | PawsMatch | Disponible ([Teoría](https://youtu.be/L7MwTArreqw) · [Práctica](https://youtu.be/tFTEsbVYQvE) · [`src/mini_agent.py`](./00-engine-y-harness/src/mini_agent.py)) |
| **01** | [`01-contexto-y-juez/`](./01-contexto-y-juez/) | **Sesiones largas, contexto limpio y un juez antes del código** | Rent My Gear | Disponible ([`rent-my-gear/juez/`](./01-contexto-y-juez/rent-my-gear/juez/), [`rent-my-gear/`](./01-contexto-y-juez/rent-my-gear/)) |
| **02** | [`02-lo-que-el-repo-cuenta/`](./02-lo-que-el-repo-cuenta/) | **Lo que el repo le cuenta al agente** | TraveLens | Disponible ([`AGENTS.md`](./02-lo-que-el-repo-cuenta/AGENTS.md), [`travelens/`](./02-lo-que-el-repo-cuenta/travelens/), [`medicion/`](./02-lo-que-el-repo-cuenta/medicion/)) |
| **03** | [`03-localhost-a-cloud-run/`](./03-localhost-a-cloud-run/) | **De localhost a Cloud Run con contratos tipados** | TraderPulse | Próximamente |
| **04** | [`04-tools-para-agentes/`](./04-tools-para-agentes/) | **Tools hechas para agentes, MCP y computer use** | TraderPulse | Próximamente |
| **05** | [`05-lo-que-el-agente-no-toca/`](./05-lo-que-el-agente-no-toca/) | **Lo que el agente no puede tocar** | Rent My Gear | Próximamente |
| **06** | [`06-varios-agentes-un-repo/`](./06-varios-agentes-un-repo/) | **Varios agentes sobre el mismo repo** | TraveLens | Próximamente |
| **07** | [`07-skills-y-headless/`](./07-skills-y-headless/) | **Empaquetar lo que repites con Skills y modo headless** | PawsMatch | Próximamente |
| **08** | [`08-revisar-codigo-ajeno/`](./08-revisar-codigo-ajeno/) | **Revisar código que no escribiste** | TraderPulse | Próximamente |
| **09** | [`09-del-fin-de-semana-a-usuarios/`](./09-del-fin-de-semana-a-usuarios/) | **Del prototipo de fin de semana a usuarios reales** | Los cuatro | Próximamente |

## Estructura del monorepo

```text
ai-native-dev/
├── README.md
├── 00-engine-y-harness/
├── 01-contexto-y-juez/
├── 02-lo-que-el-repo-cuenta/
├── 03-localhost-a-cloud-run/
├── 04-tools-para-agentes/
├── 05-lo-que-el-agente-no-toca/
├── 06-varios-agentes-un-repo/
├── 07-skills-y-headless/
├── 08-revisar-codigo-ajeno/
├── 09-del-fin-de-semana-a-usuarios/
└── 2026/        # Archivo de la edición 2026 (week1 a week4)
```

**Nos vemos en el código.**
