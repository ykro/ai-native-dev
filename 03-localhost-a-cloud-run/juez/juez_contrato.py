"""Juez del contrato: el OpenAPI publicado, los tipos del frontend y el compilador dicen lo mismo.

Uso (desde 03-localhost-a-cloud-run/):  python3 juez/juez_contrato.py
Sale con 0 si las tres verificaciones pasan.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "traderpulse"
BACK, FRONT, CONTRATO = RAIZ / "backend", RAIZ / "frontend", RAIZ / "contrato" / "openapi.json"


def correr(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main() -> int:
    resultados: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory() as tmp:
        exportado = Path(tmp) / "openapi.json"
        r = correr(["uv", "run", "-q", "python", "scripts/exportar_openapi.py", str(exportado)], BACK)
        igual = r.returncode == 0 and exportado.read_text() == CONTRATO.read_text()
        resultados.append(("el contrato publicado es el que genera el BFF", igual,
                           "regenera con make contrato" if not igual else ""))

        tipos = Path(tmp) / "api-schema.d.ts"
        r = correr(["node_modules/.bin/openapi-typescript", str(CONTRATO), "-o", str(tipos)], FRONT)
        actual = (FRONT / "src/lib/api-schema.d.ts").read_text()
        igual = r.returncode == 0 and tipos.read_text() == actual
        resultados.append(("los tipos del frontend salen de ese contrato", igual,
                           "regenera con make contrato" if not igual else ""))

    r = correr(["node_modules/.bin/tsc", "--noEmit"], FRONT)
    errores = [linea for linea in r.stdout.splitlines() if "error TS" in linea]
    resultados.append(("el frontend compila contra esos tipos", r.returncode == 0,
                       "\n".join(errores[:6])))

    for nombre, ok, detalle in resultados:
        print(f"{'PASA' if ok else 'FALLA'}  {nombre}")
        if detalle and not ok:
            for linea in detalle.splitlines():
                print(f"       {linea}")
    pasan = sum(ok for _, ok, _ in resultados)
    print(f"\njuez del contrato: {pasan} de {len(resultados)}")
    return 0 if pasan == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
