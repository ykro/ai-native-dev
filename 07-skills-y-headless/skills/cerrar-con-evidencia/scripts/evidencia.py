"""Corre los comandos de verificación y escribe EVIDENCIA.md. Ver ../SKILL.md."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

POR_DEFECTO = ["npm run lint", "npm test", "npm run build"]


def correr(comando: str, cwd: Path) -> dict:
    t0 = time.time()
    r = subprocess.run(comando, shell=True, cwd=cwd, text=True, capture_output=True)
    salida = (r.stdout + r.stderr).strip().splitlines()
    return {"comando": comando, "codigo": r.returncode, "segundos": round(time.time() - t0, 1),
            "cola": [l.rstrip() for l in salida[-6:]]}


def a_markdown(resultados: list[dict], cambios: str) -> str:
    ok = all(r["codigo"] == 0 for r in resultados)
    lineas = ["# Evidencia", "", f"Resultado: {'todo en verde' if ok else 'hay comandos en rojo'}", "",
              "| Comando | Código | Segundos |", "|---|---|---|"]
    lineas += [f"| `{r['comando']}` | {r['codigo']} | {r['segundos']} |" for r in resultados]
    for r in resultados:
        lineas += ["", f"## {r['comando']}", "", "```text", *r["cola"], "```"]
    lineas += ["", "## Archivos cambiados", "", "```text", cambios.strip() or "(sin cambios)", "```", ""]
    return "\n".join(lineas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Escribe EVIDENCIA.md")
    ap.add_argument("--comando", action="append", help="reemplaza la lista por defecto")
    ap.add_argument("--juez", action="append", default=[])
    ap.add_argument("--salida", type=Path, default=Path("EVIDENCIA.md"))
    a = ap.parse_args(argv)
    cwd = Path.cwd()
    comandos = (a.comando or POR_DEFECTO) + a.juez
    resultados = [correr(c, cwd) for c in comandos]
    cambios = subprocess.run(["git", "status", "--short", "--", "."], cwd=cwd, text=True,
                             capture_output=True).stdout
    a.salida.write_text(a_markdown(resultados, cambios), encoding="utf-8")
    for r in resultados:
        print(f"{r['codigo']:>3}  {r['segundos']:>6}s  {r['comando']}")
    return 0 if all(r["codigo"] == 0 for r in resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
