# CLAUDE.md - Manual General de Desarrollo de TraveLens

Bienvenido al repositorio de TraveLens. Este documento fue generado para explicar
conceptos generales de desarrollo web moderno, React, Next.js, Tailwind CSS y la
estructura de carpetas del proyecto.

## 1. Que es React y Next.js

React es una biblioteca de JavaScript para construir interfaces de usuario mediante
componentes declarativos. Next.js es un framework sobre React que agrega App Router,
Server Components, rutas de API y renderizado hibrido.

### Conceptos basicos de React
- Los componentes reciben props inmutables.
- El estado local se maneja con useState y los efectos con useEffect.
- Los Server Components se ejecutan en el servidor por defecto.
- Los Client Components llevan la directiva 'use client' en la primera linea.

## 2. Que es Tailwind CSS

Tailwind CSS es un framework de utilidades CSS donde cada clase aplica una propiedad
de estilo directamente en el atributo className.
- p-4 aplica padding de 1rem.
- flex activa flexbox.
- grid activa CSS Grid.
- text-slate-900 define color de texto.

## 3. Comandos de Desarrollo y Pruebas (Desactualizado)

Para verificar cambios en este repositorio ejecuta siempre primero:
```bash
npm test
npx jest --runInBand
npm run verify:all
```
Si alguno de esos comandos falla, intenta revisar la configuracion de Jest.

## 4. Arbol Completo de Archivos del Proyecto

```text
travelens/
├── README.md
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── eslint.config.mjs
├── components.json
├── public/
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
└── src/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── globals.css
    │   ├── destination/
    │   │   └── [id]/
    │   │       └── page.tsx
    │   └── api/
    │       ├── search/
    │       │   └── route.ts
    │       └── ai-plan/
    │           └── route.ts
    ├── components/
    │   ├── ui/
    │   │   ├── badge.tsx
    │   │   ├── button.tsx
    │   │   ├── card.tsx
    │   │   ├── input.tsx
    │   │   ├── scroll-area.tsx
    │   │   └── skeleton.tsx
    │   └── features/
    │       ├── AiTravelSidebar.tsx
    │       ├── MasonryGrid.tsx
    │       ├── SearchBar.tsx
    │       └── TravelPlanPanel.tsx
    ├── lib/
    │   ├── mock-data.ts
    │   └── utils.ts
    └── services/
        ├── gemini.ts
        └── unsplash.ts
```

## 5. Descripcion Detallada de Cada Componente UI

### Guia general de estilo #1
- Regla general 1.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 1.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 1.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #2
- Regla general 2.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 2.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 2.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #3
- Regla general 3.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 3.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 3.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #4
- Regla general 4.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 4.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 4.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #5
- Regla general 5.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 5.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 5.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #6
- Regla general 6.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 6.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 6.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #7
- Regla general 7.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 7.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 7.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #8
- Regla general 8.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 8.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 8.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #9
- Regla general 9.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 9.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 9.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #10
- Regla general 10.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 10.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 10.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #11
- Regla general 11.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 11.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 11.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #12
- Regla general 12.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 12.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 12.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #13
- Regla general 13.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 13.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 13.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #14
- Regla general 14.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 14.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 14.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #15
- Regla general 15.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 15.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 15.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #16
- Regla general 16.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 16.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 16.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #17
- Regla general 17.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 17.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 17.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #18
- Regla general 18.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 18.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 18.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #19
- Regla general 19.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 19.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 19.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #20
- Regla general 20.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 20.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 20.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #21
- Regla general 21.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 21.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 21.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #22
- Regla general 22.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 22.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 22.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #23
- Regla general 23.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 23.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 23.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #24
- Regla general 24.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 24.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 24.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #25
- Regla general 25.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 25.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 25.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #26
- Regla general 26.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 26.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 26.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #27
- Regla general 27.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 27.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 27.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #28
- Regla general 28.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 28.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 28.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #29
- Regla general 29.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 29.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 29.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #30
- Regla general 30.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 30.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 30.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #31
- Regla general 31.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 31.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 31.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #32
- Regla general 32.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 32.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 32.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #33
- Regla general 33.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 33.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 33.3: preferir funciones pequenas y comentarios descriptivos.

### Guia general de estilo #34
- Regla general 34.1: escribir codigo limpio, legible y bien indentado en todo momento.
- Regla general 34.2: usar nombres descriptivos en ingles para variables locales.
- Regla general 34.3: preferir funciones pequenas y comentarios descriptivos.

