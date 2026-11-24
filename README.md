# AI Native Dev

Repositorio oficial y código abierto de la serie **AI Native Dev** en YouTube y [Substack](https://ykro1.substack.com) por **Adrián Catalán** (`@adriancs.tech`).

> Los materiales, proyectos y presentaciones de la primera edición (4 semanas) están archivados en [`./2026/`](./2026/).

Durante mucho tiempo aprender a programar con inteligencia artificial se enfocó en escribir instrucciones en una ventana de chat. Hoy el trabajo pasa por entender qué hace un *Coding Agent* entre tu instrucción y su respuesta, cómo cuidar el contexto de una sesión larga y qué necesita un repositorio para que herramientas como Claude Code, Cursor, Codex o Antigravity trabajen con precisión.

La serie se organiza en **10 temas** que crecen en espiral. El hilo son los cuatro proyectos de la edición 2026 (PawsMatch, TraveLens, Rent My Gear y TraderPulse), actualizados a versiones vigentes. Cada carpeta numerada contiene el código ejecutable que acompaña a los videos y a los artículos.

## Videos y Lecturas en Substack

- **Playlist en YouTube** · [AI Native Dev](https://www.youtube.com/playlist?list=PLADgjqdtJ3Bc)
- **Lo que pasa cuando le pides algo a un Coding Agent (`00-engine-y-harness`)**
  - **YouTube** · [Video de Teoría](https://youtu.be/L7MwTArreqw) · [Video de Práctica](https://youtu.be/lDB4Uw_k9X4)
  - **Substack** · [Un Coding Agent completo en 180 líneas](https://ykro1.substack.com/p/un-coding-agent-completo-en-180-lineas) · [Cuando el agente no encuentra el texto que acaba de leer](https://ykro1.substack.com/p/cuando-el-agente-no-encuentra-el-texto)
- **Sesiones largas, contexto limpio y un juez antes del código (`01-contexto-y-juez`)**
  - **YouTube** · [Video de Práctica](https://youtu.be/FUN_xw-XOI8)
  - **Substack** · [Tu sesión pierde precisión antes de llenar la ventana](https://ykro1.substack.com/p/tu-sesion-pierde-precision-antes-de-llenar-la-ventana) · [El archivo que el agente leyó cuatro veces y nunca vio completo](https://ykro1.substack.com/p/el-archivo-que-el-agente-leyo-cuatro-veces)
- **Lo que el repo le cuenta al agente (`02-lo-que-el-repo-cuenta`)**
  - **YouTube** · [Video de Práctica](https://youtu.be/RVuZikv8u5Y)
  - **Substack** · [El repositorio es la interfaz de tu Coding Agent](https://ykro1.substack.com/p/el-repositorio-es-la-interfaz-de-tu-coding-agent) · [Cuando AGENTS.md pide Zod y nadie lo importa](https://ykro1.substack.com/p/cuando-agents-md-pide-zod-y-nadie-lo-importa)

## Índice de temas

| Tema | Carpeta | Proyecto | Estado |
| :--- | :--- | :--- | :--- |
| **Lo que pasa cuando le pides algo a un Coding Agent** | [`00-engine-y-harness/`](./00-engine-y-harness/) | PawsMatch | Disponible ([Teoría](https://youtu.be/L7MwTArreqw) · [Práctica](https://youtu.be/lDB4Uw_k9X4) · [`src/mini_agent.py`](./00-engine-y-harness/src/mini_agent.py)) |
| **Sesiones largas, contexto limpio y un juez antes del código** | [`01-contexto-y-juez/`](./01-contexto-y-juez/) | Rent My Gear | Disponible ([Práctica](https://youtu.be/FUN_xw-XOI8) · [`rent-my-gear/juez/`](./01-contexto-y-juez/rent-my-gear/juez/), [`rent-my-gear/`](./01-contexto-y-juez/rent-my-gear/)) |
| **Lo que el repo le cuenta al agente** | [`02-lo-que-el-repo-cuenta/`](./02-lo-que-el-repo-cuenta/) | TraveLens | Disponible ([Práctica](https://youtu.be/RVuZikv8u5Y) · [`AGENTS.md`](./02-lo-que-el-repo-cuenta/AGENTS.md), [`travelens/`](./02-lo-que-el-repo-cuenta/travelens/), [`medicion/`](./02-lo-que-el-repo-cuenta/medicion/)) |
| **De localhost a Cloud Run con contratos tipados** | [`03-localhost-a-cloud-run/`](./03-localhost-a-cloud-run/) | TraderPulse | Próximamente |
| **Tools hechas para agentes, MCP y computer use** | [`04-tools-para-agentes/`](./04-tools-para-agentes/) | TraderPulse | Próximamente |
| **Lo que el agente no puede tocar** | [`05-lo-que-el-agente-no-toca/`](./05-lo-que-el-agente-no-toca/) | Rent My Gear | Próximamente |
| **Varios agentes sobre el mismo repo** | [`06-varios-agentes-un-repo/`](./06-varios-agentes-un-repo/) | TraveLens | Próximamente |
| **Empaquetar lo que repites con Skills y modo headless** | [`07-skills-y-headless/`](./07-skills-y-headless/) | PawsMatch | Próximamente |
| **Revisar código que no escribiste** | [`08-revisar-codigo-ajeno/`](./08-revisar-codigo-ajeno/) | TraderPulse | Próximamente |
| **Del prototipo de fin de semana a usuarios reales** | [`09-del-fin-de-semana-a-usuarios/`](./09-del-fin-de-semana-a-usuarios/) | Los cuatro | Próximamente |

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
