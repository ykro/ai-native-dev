"""Sanea un log de sesión JSONL para publicarlo. Ver ../SKILL.md."""
from __future__ import annotations

import argparse
import getpass
import json
import re
import socket
import sys
from pathlib import Path

CAMPOS_DE_LA_MAQUINA = ("plugins", "mcp_servers", "slash_commands", "agents", "skills",
                        "memory_paths", "session_id", "uuid", "apiKeySource", "output_style")
CORREO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def reemplazos(raices: list[str], ocultar: list[str], casa: str, usuario: str, host: str) -> list[tuple[str, str]]:
    pares: list[tuple[str, str]] = []
    for r in raices:
        ruta, _, alias = r.partition("=")
        pares.append((ruta.rstrip("/"), alias or "~/trabajo"))
        if ruta.startswith("/private/"):
            pares.append((ruta.removeprefix("/private").rstrip("/"), alias or "~/trabajo"))
    pares.append((casa, "~"))
    pares += [(o, "[oculto]") for o in ocultar]
    if host:
        pares.append((host, "host"))
    if usuario:
        pares.append((usuario, "dev"))
    # Primero las cadenas largas, para que la carpeta de trabajo gane sobre la carpeta personal.
    return sorted(pares, key=lambda p: len(p[0]), reverse=True)


def sanear_evento(ev: object) -> object:
    if isinstance(ev, dict) and ev.get("type") == "system" and ev.get("subtype") == "init":
        return {k: v for k, v in ev.items() if k not in CAMPOS_DE_LA_MAQUINA}
    return ev


def sanear_texto(texto: str, pares: list[tuple[str, str]]) -> str:
    salida = []
    for linea in texto.splitlines():
        if not linea.strip():
            continue
        for viejo, nuevo in pares:
            linea = linea.replace(viejo, nuevo)
        linea = CORREO.sub("correo@ejemplo.com", linea)
        try:
            linea = json.dumps(sanear_evento(json.loads(linea)), ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        salida.append(linea)
    return "\n".join(salida) + "\n"


def hallazgos(texto: str, casa: str, usuario: str, host: str) -> list[str]:
    malos = []
    for n, linea in enumerate(texto.splitlines(), start=1):
        if "/Users/" in linea or "/home/" in linea or casa in linea:
            malos.append(f"{n}: ruta local")
        elif usuario and re.search(rf"\b{re.escape(usuario)}\b", linea):
            malos.append(f"{n}: usuario")
        elif host and host in linea:
            malos.append(f"{n}: hostname")
        elif CORREO.search(linea.replace("correo@ejemplo.com", "")):
            malos.append(f"{n}: correo")
    return malos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sanea un log JSONL")
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path, nargs="?")
    ap.add_argument("--raiz", action="append", default=[], help="RUTA=ALIAS")
    ap.add_argument("--ocultar", action="append", default=[])
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args(argv)
    casa, usuario = str(Path.home()), getpass.getuser()
    host = socket.gethostname().split(".")[0]
    if a.verificar:
        malos = hallazgos(a.entrada.read_text(errors="replace"), casa, usuario, host)
        for m in malos:
            print(m)
        return 1 if malos else 0
    if a.salida is None:
        ap.error("falta la salida")
    pares = reemplazos(a.raiz, a.ocultar, casa, usuario, host)
    a.salida.write_text(sanear_texto(a.entrada.read_text(errors="replace"), pares))
    return 0


if __name__ == "__main__":
    sys.exit(main())
