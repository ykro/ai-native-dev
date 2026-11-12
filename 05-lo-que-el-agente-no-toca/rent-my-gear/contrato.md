# Contrato · cobertura por daños

Qué cambia
- Cobertura por categoría: `fotografia-video` 20 %, `montana-camping` y `deportes-acuaticos` 10 %. Una sola tabla tipada por `CategoryId`.
- Una sola función de precio, en `src/lib/date-utils.ts`, que usan el servidor y `PriceSummary`. Trabaja en centavos enteros y redondea la cobertura al centavo, con las mitades hacia arriba.
- `POST /api/rental` devuelve además `subtotal`, `coverageRate` y `coverageFee`; `totalPrice` = subtotal + cobertura. `rentalConfirmationSchema` incluye los campos nuevos.
- `PriceSummary` muestra una línea «Cobertura por daños (N %)» entre el subtotal y el total.
- Precios con centavos en todo el sitio: `formatPrice` pasa a dos decimales. Solo se actualizan las pruebas de `formatPrice`.

Qué no se toca
- `juez/` y `vitest.juez.config.ts`.
- El request de `POST /api/rental` (sigue siendo `gearId`, `startDate`, `endDate`).
- El tope de 30 días y el resto de las pruebas existentes.

Quién decide
- `npm run juez` en verde, y después `npm run test:run` y `npx tsc --noEmit` en verde.
