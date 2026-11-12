"""Quita de un log stream-json lo que no debe publicarse: rutas de la laptop, lista de plugins,
slash commands, IDs de proyecto de GCP y números de proyecto.

Uso:  python3 scripts/sanear_log.py <entrada.jsonl> <salida.jsonl> <ruta-de-trabajo> [<valor-a-ocultar> ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

VISIBLE = "~/ai-native-dev/03-localhost-a-cloud-run"
CLAVES_INIT = {"type", "subtype", "cwd", "tools", "model", "permissionMode", "claude_code_version"}


def limpiar(texto: str, trabajo: str, ocultos: list[str]) -> str:
    texto = texto.replace(trabajo, VISIBLE)
    texto = re.sub(r"/private/tmp/[^\"\s\\]*?/(?=ai-native-dev)", "", texto)
    texto = re.sub(r"/Users/[^/\"\s\\]+", "~", texto)
    for valor in ocultos:
        texto = texto.replace(valor, "{{OCULTO}}")
    return texto


def main(entrada: str, salida: str, trabajo: str, ocultos: list[str]) -> None:
    lineas = []
    for linea in Path(entrada).read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        ev = json.loads(linea)
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            ev = {k: v for k, v in ev.items() if k in CLAVES_INIT}
            ev["cwd"] = VISIBLE
        elif ev.get("type") == "system":
            continue  # hooks y mensajes de plugins de la máquina
        lineas.append(limpiar(json.dumps(ev, ensure_ascii=False), trabajo, ocultos))
    Path(salida).write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
