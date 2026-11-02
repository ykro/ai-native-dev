"""Juez externo pre-commit para Rent My Gear: valida contratos, MCP dry_run y Vitest."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    date_utils = (ROOT / "src" / "lib" / "date-utils.ts").read_text(encoding="utf-8")
    validation = (ROOT / "src" / "lib" / "validation.ts").read_text(encoding="utf-8")
    mcp_code = (ROOT / "mcp_server.py").read_text(encoding="utf-8")

    errors: list[str] = []
    if not re.search(r"Math\.abs\(days\)\s*\+\s*1", date_utils):
        errors.append("date-utils.ts: falta Math.abs(days) + 1 inclusivo en calculateRentalDays")
    if "export function getInsuranceRateForCategory" not in date_utils:
        errors.append("date-utils.ts: falta getInsuranceRateForCategory (seguro por categoria 20% / 10%)")
    if not re.search(r"MAX_RENTAL_DAYS\s*=\s*30\b", validation):
        errors.append("validation.ts: MAX_RENTAL_DAYS debe ser 30 dias")
    if "dry_run: bool = True" not in mcp_code:
        errors.append("mcp_server.py: falta freno dry_run: bool = True por defecto")

    mcp_run = subprocess.run(
        [sys.executable, str(ROOT / "mcp_server.py"), "--self-test"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if mcp_run.returncode != 0:
        errors.append(f"mcp_server.py --self-test fallo: {mcp_run.stderr or mcp_run.stdout}")

    if "--with-vitest" in sys.argv:
        vt = subprocess.run(["npm", "run", "test:run"], cwd=ROOT, capture_output=True, text=True)
        if vt.returncode != 0:
            errors.append("Vitest fallo al ejecutar npm run test:run")

    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        return 1

    print("PASS: Contratos de negocio, seguro por categoria (20%/10%), tope 30 dias y MCP dry_run verificados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
