"""Alterna Rent My Gear entre el estado inicial del demo (--broken: 47/57) y el estado resuelto (--solved: 61/61)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = [
    "src/lib/date-utils.ts",
    "src/lib/date-utils.test.ts",
    "src/lib/validation.ts",
    "src/app/api/rental/route.ts",
    "src/components/features/RentalFlow/PriceSummary.tsx",
    "src/components/features/RentalFlow/DateSelection.tsx",
]


def restore(state: str) -> None:
    src_dir = ROOT / ".demo_snapshots" / state
    for rel in FILES:
        shutil.copy2(src_dir / rel, ROOT / rel)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--status"
    if mode == "--broken":
        restore("broken")
        print("Estado restaurado a INICIO DEL DEMO (--broken): 47 de 57 tests pasando, seguro por categoria pendiente.")
        return 0
    if mode == "--solved":
        restore("solved")
        print("Estado restaurado a FINAL DEL DEMO (--solved): 61 de 61 tests pasando y seguro 20%/10% por categoria integrado.")
        res = subprocess.run([sys.executable, str(ROOT / "hooks" / "pre_commit_check.py")], cwd=ROOT)
        return res.returncode
    if mode in ("--status", "--verify"):
        res = subprocess.run([sys.executable, str(ROOT / "hooks" / "pre_commit_check.py")], cwd=ROOT)
        return res.returncode
    print("Uso: python3 demo_reset.py [--broken | --solved | --status]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
