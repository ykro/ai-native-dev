### 1. Inyección de Errores (Error Injection)

Este prompt introduce fallos lógicos y de validación que parecen correctos a simple vista pero rompen la integridad del negocio.

**Prompt (English):**

> "Modify the current codebase of **Rent my Gear** to introduce the following three subtle bugs for educational purposes:
> 1. **Logic Error:** In `src/lib/date-utils.ts`, modify the price calculation so it misses the final day of the range (an 'off-by-one' error).
> 2. **Validation Error:** In the **Zod** schema for the rental process, set a constraint that incorrectly rejects rentals longer than 7 days, even though the business rule allows them.
> 3. **State Error:** In the `RentalFlow` component, make the 'Confirmar' button stay in a permanent 'loading' state if the user selects a specific category, without showing any error message.
> 
> 
> Do not fix them. Ensure the code still compiles but behaves incorrectly."

---

### 2. Depuración Asistida (Guided Debugging)

Este prompt enseña al estudiante a usar **Claude Code** para diagnosticar problemas basándose en síntomas reportados por el usuario.

**Prompt (English):**

> "Users are reporting that the total price for rentals is lower than expected and that they cannot rent items for more than a week.
> 1. Run the application and use **Claude Code** to inspect the terminal and browser logs.
> 2. Analyze `src/lib/date-utils.ts` and the Zod validation schemas.
> 3. Identify the logical errors and propose a fix that restores the correct price calculation and the 7+ day rental capability."
> 
> 

---

### 3. El Error "Invisible" (The AI-Hard Bug)

Este bug está diseñado para que la IA tenga dificultades al detectarlo mediante análisis estático, ya que es un error de **Hydration Mismatch**.

**Prompt (English):**

> "Introduce a subtle **Hydration Mismatch** error in the `HeroCarousel.tsx` component. Use `Math.random()` or `new Date()` directly inside the component's initial state without `useEffect` or `suppressHydrationWarning`.
> **Challenge:** Ask the AI agent to explain why the UI 'flickers' or shows different content than the server-rendered HTML. If the AI suggests it is a CSS issue, insist on checking the React rendering cycle."

---

### 4. Generación de Pruebas (Testing Suite)

Enfoque en pruebas unitarias para la lógica y pruebas de integración para el flujo.

**Prompt (English):**

> "Using **Vitest** and **React Testing Library**, generate a testing suite for the rental module:
> 1. **Unit Tests:** Create tests for `src/lib/date-utils.ts` to validate price calculations with various date ranges (1 day, 1 week, across different months).
> 2. **Integration Tests:** Simulate the full rental flow: selecting a category, picking a gear item, choosing dates, and clicking 'Confirmar'. Ensure the success toast appears only when data is valid.
> 3. **Edge Cases:** Test how the system handles the 'Nano Banana' fallback if the Unsplash API returns a 404 error."
> 
> 

---

### 5. Documentación y Arquitectura (Mermaid & Onboarding)

Generación de activos técnicos para la mantenibilidad del proyecto.

**Prompt (English):**

> "Generate advanced technical documentation for **Rent my Gear**:
> 1. Create a **Mermaid sequence diagram** showing the 'Image Resolution Flow' (GCS -> Unsplash -> Nano Banana -> GCS Persistence).
> 2. Create a **Mermaid class diagram** for the `inventoryService` and `imageService` interactions.
> 3. Write a 'Senior Developer Onboarding Guide' that explains how to debug the GCS connection and how to add a new category to the system without breaking the existing validation schemas."
> 
> 

---

### 6. Laboratorio de Alucinaciones (Hallucination Demo)

Este ejemplo sirve para mostrar a los estudiantes que la IA puede inventar herramientas o procesos que no existen.

**Prompt (English - Hallucination Trigger):**

> "Integrate the **Nano Banana Pro Local-Offline SDK for Next.js 16** to process images directly on the user's GPU without using API calls. Please provide the exact npm command to install this local SDK and the configuration object for the `offline-gen` mode."

**Consejos para corregirlo (Para el Estudiante):**

* **Verificación Cruzada:** Si la IA sugiere una librería o comando que parece demasiado bueno para ser cierto, búscalo en **npm** o en la documentación oficial de la herramienta.
* **Context Engineering:** Si la IA alucina, reinicia el contexto y proporciona la documentación real (vía **context7**) para "centrar" al modelo en los límites de la realidad técnica actual.
* **Escepticismo Técnico:** Los agentes tienden a ser "complacientes". Si pides algo imposible, intentarán inventar una solución. Siempre valida las dependencias críticas.

