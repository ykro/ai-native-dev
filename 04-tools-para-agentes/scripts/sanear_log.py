"""Quita de un log stream-json lo que no debe publicarse: rutas de la laptop, lista de plugins y
slash commands, URLs de Cloud Run (llevan el número de proyecto) e IDs de proyecto de GCP.

Uso:  python3 scripts/sanear_log.py <entrada.jsonl> <salida.jsonl> [--ocultar valor=reemplazo ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

VISIBLE = "~/ai-native-dev/04-tools-para-agentes"
CLAVES_INIT = {"type", "subtype", "cwd", "tools", "mcp_servers", "model", "permissionMode",
               "claude_code_version"}


def limpiar(texto: str, reemplazos: dict[str, str]) -> str:
    for valor, nuevo in reemplazos.items():
        texto = texto.replace(valor, nuevo)
    texto = re.sub(r"/private/var/folders/[^\"\s\\]*", "~/tmp", texto)
    texto = re.sub(r"/private/tmp/[^\"\s\\]*", "~/tmp", texto)
    texto = re.sub(r"/var/folders/[^\"\s\\]*", "~/tmp", texto)
    texto = re.sub(r"https://[a-z0-9-]+-\d{6,}\.[a-z0-9-]+\.run\.app", "{{URL_CLOUD_RUN}}", texto)
    return re.sub(r"/Users/[^/\"\s\\]+", "~", texto)


def sanear(entrada: Path, salida: Path, reemplazos: dict[str, str]) -> None:
    lineas = []
    for linea in entrada.read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        ev = json.loads(linea)
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            ev = {k: v for k, v in ev.items() if k in CLAVES_INIT}
            ev["cwd"] = VISIBLE
        elif ev.get("type") == "system":
            continue  # hooks y mensajes de plugins de la máquina
        lineas.append(limpiar(json.dumps(ev, ensure_ascii=False), reemplazos))
    salida.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    extra = dict(a.split("=", 1) for a in sys.argv[3:] if "=" in a)
    sanear(Path(sys.argv[1]), Path(sys.argv[2]), extra)
