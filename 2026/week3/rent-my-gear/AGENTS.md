# Rent My Gear — AGENTS.md (enlazado desde CLAUDE.md)
Next.js 16 + TypeScript + Zod + Vitest (`github.com/ykro/rentmygear-ai-native` + `week3/rent-my-gear`).

## Comandos de verificación y entorno
- `npm run test:run`: ejecuta las 61 pruebas en Vitest (`date-utils`, `imageService`, `RentalFlow`).
- `python3 hooks/pre_commit_check.py`: juez determinista (contratos Zod + seguro 20%/10% + MCP `dry_run`).
- `python3 mcp_server.py --self-test`: valida `cotizar_reserva` y `auditar_catalogo` en modo simulación.
- `python3 demo_reset.py --broken` / `--solved`: alterna entre el estado inicial (47/57) y final (61/61).

## Arquitectura por capas
- `src/lib/date-utils.ts`: cálculo inclusivo (`+ 1` día en `calculateRentalDays`) y seguro por categoría (`getInsuranceRateForCategory`, `calculateInsuranceFee`).
- `src/lib/validation.ts`: esquemas Zod (`CATEGORY_IDS`, `MAX_RENTAL_DAYS = 30`, `rentalDatesSchema`, `rentalConfirmationSchema`).
- `src/app/api/rental/route.ts`: endpoint POST `/api/rental` que devuelve `subtotal`, `insuranceRate`, `insuranceFee` y `totalPrice`.
- `src/components/features/RentalFlow/`: flujo de reserva (`DateSelection.tsx`, `PriceSummary.tsx`, `Confirmation.tsx`).

## Herramientas MCP (`mcp_server.py`)
- `cotizar_reserva(categoria: CategoryLiteral, gear_id: str, dias: int, dry_run: bool = True) -> dict`
- `auditar_catalogo(dry_run: bool = True) -> dict`

## Guardrails y contratos de negocio
- Nunca calcular tarifas ni seguros dentro de `src/components/`; toda fórmula vive en `src/lib/date-utils.ts`.
- El seguro por categoría cobra `20%` en `fotografia-video` y `10%` en `montana-camping` y `deportes-acuaticos`.
- Mantener el rango permitido de alquiler entre `1` y `30` días inclusivos (`MAX_RENTAL_DAYS = 30`).
- Devolver errores de negocio como datos estructurados con `retry: False` en `mcp_server.py`.
- Conservar `dry_run: bool = True` por defecto en todas las herramientas expuestas al agente.
