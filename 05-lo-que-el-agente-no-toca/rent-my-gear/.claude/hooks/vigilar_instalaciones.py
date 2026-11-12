#!/usr/bin/env python3
"""Hook PreToolUse para Bash: revisa las instalaciones de paquetes contra el registro.

Recibe por stdin el JSON del harness (tool_name, tool_input.command). Decide:
  - pasa: sale con código 0 y sin salida.
  - bloquea: código 2 y un mensaje en stderr que el agente lee.
  - pregunta: código 0 y JSON con permissionDecision "ask" (en headless se deniega
    y el agente lee la razón).

Un paquete aprobado (dependencias-permitidas.json) pasa. Uno que el registro no conoce se
bloquea. Uno que existe pero nadie aprobó pregunta, con su antigüedad. Si el registro no
responde, pregunta. Solo usa la biblioteca estándar.

GUARDAS_REGISTRO=simulado lee juez/registro-simulado.json (sin red); es lo que usa el juez.
"""
from __future__ import annotations

import json
import os
import shlex
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROYECTO = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
APROBADAS = PROYECTO / "dependencias-permitidas.json"
SIMULADO = Path(os.environ.get("GUARDAS_REGISTRO_ARCHIVO")
                or PROYECTO.parent / "juez" / "registro-simulado.json")

SEPARADORES = {"&&", "||", ";", "|", "&", "\n", "(", ")"}
CON_VALOR = {"--registry", "--prefix", "--workspace", "-w", "--tag", "--filter", "-F", "-C",
             "--dir", "--cwd", "--python", "-p", "--index", "--index-url", "-i", "--extra-index-url",
             "--group", "--extra", "--target", "-t", "--cache", "--userconfig", "--with"}
ARCHIVOS = {"-r", "--requirement", "-c", "--constraint", "-e", "--editable"}


# ------------------------------------------------------------------ análisis del comando

def segmentos(comando: str) -> list[list[str]]:
    """Separa un comando compuesto en comandos simples, respetando las comillas."""
    lexer = shlex.shlex(comando, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    salida: list[list[str]] = [[]]
    for tok in lexer:
        if tok in SEPARADORES or set(tok) <= set("&|;()"):
            salida.append([])
        else:
            salida[-1].append(tok)
    return [s for s in salida if s]


def sin_prefijos(palabras: list[str]) -> list[str]:
    """Quita VAR=valor, env, sudo, time, exec y similares del inicio."""
    i = 0
    while i < len(palabras):
        p = palabras[i]
        if "=" in p and not p.startswith("-") and p.split("=")[0].replace("_", "").isalnum():
            i += 1
        elif p in {"env", "sudo", "time", "exec", "nohup", "command"}:
            i += 1
        else:
            break
    return palabras[i:]


def instalaciones(comando: str, nivel: int = 0) -> list[tuple[str, str]]:
    """Devuelve [(ecosistema, nombre)] de todos los paquetes que el comando instala."""
    if nivel > 3:
        return []
    encontrados: list[tuple[str, str]] = []
    for seg in segmentos(comando):
        p = sin_prefijos(seg)
        if not p:
            continue
        cmd = os.path.basename(p[0])
        if cmd in {"bash", "sh", "zsh"} and "-c" in p and p.index("-c") + 1 < len(p):
            encontrados += instalaciones(p[p.index("-c") + 1], nivel + 1)
            continue
        eco, resto = clasificar(cmd, p[1:])
        if eco:
            encontrados += [(eco, n) for n in nombres(eco, resto)]
    return encontrados


def clasificar(cmd: str, args: list[str]) -> tuple[str | None, list[str]]:
    """Dice si el comando instala paquetes y devuelve los argumentos después del subcomando."""
    def despues_de(subs: set[str], desde: list[str]) -> list[str] | None:
        i = 0
        while i < len(desde):
            a = desde[i]
            if a in subs:
                return desde[i + 1:]
            if a.startswith("-"):
                i += 2 if a in CON_VALOR else 1
                continue
            return None  # otro subcomando (run, test, ci...)
        return None

    if cmd in {"npm", "pnpm", "bun"}:
        r = despues_de({"install", "i", "add", "isntall"}, args)
        return ("npm", r) if r is not None else (None, [])
    if cmd == "yarn":
        r = despues_de({"add"}, args)
        return ("npm", r) if r is not None else (None, [])
    if cmd == "uv":
        r = despues_de({"add"}, args)
        if r is not None:
            return "pypi", r
        if args[:2] == ["pip", "install"]:
            return "pypi", args[2:]
        return None, []
    if cmd in {"pip", "pip3"} or (cmd.startswith("python") and args[:3] == ["-m", "pip", "install"]):
        base = args[3:] if cmd.startswith("python") else args
        r = despues_de({"install"}, base) if not cmd.startswith("python") else base
        return ("pypi", r) if r is not None else (None, [])
    return None, []


def nombres(eco: str, args: list[str]) -> list[str]:
    salida: list[str] = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in ARCHIVOS or a in CON_VALOR:
            i += 2
            continue
        i += 1
        if a.startswith("-") or a.isdigit() or set(a) <= set("<>&"):
            continue
        n = nombre_de_spec(eco, a)
        if n:
            salida.append(n)
    return salida


def nombre_de_spec(eco: str, spec: str) -> str | None:
    """Extrae el nombre del paquete de una especificación (quita versión y extras)."""
    if spec.startswith((".", "/", "~", "file:", "git+", "http:", "https:", "github:", "link:")):
        return None
    if spec.endswith((".whl", ".tgz", ".tar.gz", ".zip")):
        return None
    if eco == "npm":
        if spec.startswith("npm:"):
            spec = spec[4:]
        if spec.startswith("@"):
            nombre = "@" + spec[1:].split("@")[0]
            return nombre if "/" in nombre else None
        if "/" in spec:  # atajo usuario/repo de GitHub
            return None
        return spec.split("@")[0] or None
    nombre = spec
    for corte in "[=<>~!; ":
        nombre = nombre.split(corte)[0]
    return nombre.lower().replace("_", "-").replace(".", "-") if nombre else None


# ----------------------------------------------------------------------------- registro

def cargar_aprobadas() -> dict[str, set[str]]:
    try:
        datos = json.loads(APROBADAS.read_text())
    except (OSError, json.JSONDecodeError):
        return {"npm": set(), "pypi": set()}
    return {k: set(datos.get(k, [])) for k in ("npm", "pypi")}


def dias_desde(fecha_iso: str) -> int:
    fecha = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00"))
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - fecha).days)


def consultar(eco: str, nombre: str) -> dict:
    """Devuelve {"estado": "existe", "dias": n} | {"estado": "no_existe"} | {"estado": "error", ...}."""
    if os.environ.get("GUARDAS_REGISTRO") == "simulado":
        datos = json.loads(SIMULADO.read_text())
        ficha = datos.get(eco, {}).get(nombre)
        if ficha is None:
            return {"estado": "no_existe"}
        return {"estado": "existe", "dias": ficha["creado_hace_dias"]}
    try:
        if eco == "npm":
            url = "https://registry.npmjs.org/" + urllib.parse.quote(nombre, safe="@").replace("/", "%2F")
        else:
            url = f"https://pypi.org/pypi/{urllib.parse.quote(nombre)}/json"
        req = urllib.request.Request(url, headers={"User-Agent": "vigilar-instalaciones/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            doc = json.loads(r.read(8_000_000))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"estado": "no_existe"}
        return {"estado": "error", "motivo": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
        return {"estado": "error", "motivo": type(e).__name__}
    try:
        if eco == "npm":
            return {"estado": "existe", "dias": dias_desde(doc["time"]["created"])}
        subidas = [f["upload_time_iso_8601"] for fs in doc.get("releases", {}).values() for f in fs]
        return {"estado": "existe", "dias": dias_desde(min(subidas))} if subidas else {"estado": "existe", "dias": 0}
    except (KeyError, ValueError):
        return {"estado": "error", "motivo": "respuesta inesperada"}


# ------------------------------------------------------------------------------ decisión

def decidir(comando: str) -> tuple[str, str]:
    """Devuelve ("pasa" | "bloquea" | "pregunta", mensaje)."""
    pedidos = instalaciones(comando)
    if not pedidos:
        return "pasa", ""
    aprobadas = cargar_aprobadas()
    inventados, desconocidos, sin_respuesta = [], [], []
    for eco, nombre in pedidos:
        if nombre in aprobadas[eco]:
            continue
        r = consultar(eco, nombre)
        if r["estado"] == "no_existe":
            inventados.append(f"{nombre} ({eco})")
        elif r["estado"] == "error":
            sin_respuesta.append(f"{nombre} ({r['motivo']})")
        else:
            desconocidos.append(f"{nombre} ({eco}, creado hace {r['dias']} días)")
    if inventados:
        return "bloquea", ("Ese paquete no existe en el registro: " + ", ".join(inventados) +
                           ". No lo inventes: busca la documentación oficial del producto o "
                           "pregunta a una persona cuál es el paquete correcto.")
    if sin_respuesta:
        return "pregunta", ("No se pudo consultar el registro para: " + ", ".join(sin_respuesta) +
                            ". Una persona debe decidir si se instala.")
    if desconocidos:
        return "pregunta", ("Existe en el registro pero no está en dependencias-permitidas.json: " +
                            ", ".join(desconocidos) + ". Una persona debe aprobarlo antes de instalarlo.")
    return "pasa", ""


def main() -> int:
    try:
        evento = json.load(sys.stdin)
        comando = evento.get("tool_input", {}).get("command", "")
        decision, mensaje = decidir(comando)
    except Exception as e:  # ante un fallo del hook, que decida una persona
        decision, mensaje = "pregunta", f"El hook de instalaciones falló ({type(e).__name__}); decide una persona."
    if decision == "bloquea":
        print(mensaje, file=sys.stderr)
        return 2
    if decision == "pregunta":
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "ask",
            "permissionDecisionReason": mensaje}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
