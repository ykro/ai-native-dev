# AGENTS.md — Guía Operativa del Repositorio (`travelensapp`)

> Este archivo es la fuente de verdad compartida para `CLAUDE.md` y cualquier *Coding Agent* operando en este repositorio. Mantener siempre por debajo de 100 líneas.

## 1. Comandos únicos de verificación (no interactivos)

Ejecuta siempre estos tres comandos en orden antes de dar por completada cualquier tarea

```bash
npm run typecheck    # tsc --noEmit (debe devolver 0 errores)
npm run lint         # eslint src/ --max-warnings=0
npm run test:run     # vitest run (ejecución única sin modo watch, < 3s)
```

## 2. Arquitectura y fronteras de módulos

- **`src/services/`** — Única capa autorizada para comunicarse con APIs externos ([Vertex AI / Gemini](https://cloud.google.com/vertex-ai/generative-ai/docs) y Unsplash). Todo retorno de un servicio debe validarse con su esquema en `src/services/schemas.ts` (Zod) antes de cruzar hacia la interfaz.
- **`src/components/features/`** — Componentes de interfaz en React 19 / Next.js 16. Tienen prohibido invocar `fetch` directo a servicios externos o instanciar clientes del modelo.
- **`src/services/__fixtures__/`** — Datos semilla deterministas para pruebas unitarias y desarrollo sin red.

## 3. Invariantes de código y pruebas

- Toda funcionalidad nueva en `src/services/` o `src/lib/` incluye su prueba unitaria en Vitest usando los *fixtures* locales sin realizar llamadas de red reales.
- No utilizar `any`, `@ts-ignore` ni conversiones `as unknown as T` para silenciar errores del compilador.
- Los errores provenientes de servicios externos se devuelven como objetos tipados `{ ok: false, code, message }` en lugar de lanzar excepciones sin captura en la capa de UI.

## 4. Restricciones operativas del agente

- **Prohibido** ejecutar pruebas en modo interactivo (`vitest` sin `run`) o levantar servidores bloqueantes sin límite de tiempo.
- **Prohibido** leer, imprimir o modificar archivos `.env`, `.env.local` o credenciales.
- Si una especificación en `specs/` entra en conflicto con el código existente, detén la edición y reporta la discrepancia indicando archivo y línea.
