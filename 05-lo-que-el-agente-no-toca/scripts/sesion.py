#!/usr/bin/env python3
"""Lanza una sesión headless de Claude Code sobre una copia de Rent My Gear y guarda su log.

    python3 scripts/sesion.py sin 01-paquete-inventado B1-sin-guardas-paquete
    python3 scripts/sesion.py con 03-editar-el-juez   D3-con-guardas-editar-juez

`sin` copia la app sin .claude/ y sin .npmrc (solo queda la instrucción en AGENTS.md); `con` la
copia completa. En los dos casos la copia vive fuera del monorepo (TRABAJO, por defecto
~/ai-native-05) y lleva el .env.local con el canario falso. Nada de tu entorno llega al agente:
claude corre con un entorno vacío salvo HOME y PATH. Para que ninguna instalación ocurra de
verdad, las sesiones `sin` llevan un sandbox con la red cerrada (sin hooks ni reglas de archivos).
El log se guarda saneado (rutas de la laptop fuera) en logs/.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TRABAJO = Path(os.environ.get("TRABAJO", Path.home() / "ai-native-05"))
HERRAMIENTAS = ["Bash", "Read", "Edit", "Write", "Glob", "Grep"]
# Credenciales reales de quien graba: ninguna sesión las lee, con o sin barreras de la demo.
NEGAR_PERSONALES = ["Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.config/**)", "Read(~/.claude/**)",
                    "Read(~/.gnupg/**)", "Read(~/Library/Keychains/**)"]
SANDBOX_DE_RED_CERRADA = {"sandbox": {"enabled": True, "failIfUnavailable": True,
                                      "allowUnsandboxedCommands": False,
                                      "autoAllowBashIfSandboxed": True,
                                      "network": {"allowedDomains": ["localhost"]}}}
CAMPOS_INIT_FUERA = ("mcp_servers", "slash_commands", "agents", "skills", "plugins", "apiKeySource",
                     "output_style", "memory_paths", "uuid", "session_id")


def preparar(modo: str) -> Path:
    destino = TRABAJO / modo / "rent-my-gear"
    if destino.exists():
        shutil.rmtree(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    excluir = ["node_modules", ".next", "*.tsbuildinfo"] + ([".claude", ".npmrc", "dependencias-permitidas.json"] if modo == "sin" else [])
    shutil.copytree(RAIZ / "rent-my-gear", destino, ignore=shutil.ignore_patterns(*excluir))
    nm = RAIZ / "rent-my-gear" / "node_modules"
    if not nm.exists():
        nm = RAIZ.parent / "01-contexto-y-juez" / "rent-my-gear" / "node_modules"
    os.symlink(nm.resolve(), destino / "node_modules")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=destino, check=True)
    subprocess.run(["git", "add", "-A"], cwd=destino, check=True)
    subprocess.run(["git", "-c", "user.email=d@example.com", "-c", "user.name=demo", "commit", "-qm", "base"],
                   cwd=destino, check=True)
    return destino


def comando(modo: str, prompt: str, max_turnos: int) -> list[str]:
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--model", "sonnet", "--max-turns", str(max_turnos), "--max-budget-usd", "2",
           "--permission-mode", "acceptEdits", "--setting-sources", "project",
           "--strict-mcp-config", "--allowedTools", *HERRAMIENTAS,
           "--disallowedTools", *NEGAR_PERSONALES]
    if modo == "sin":
        cmd += ["--settings", json.dumps(SANDBOX_DE_RED_CERRADA)]
    return cmd


def sanear(texto: str, trabajo: Path) -> str:
    pares = [(str(trabajo.resolve()), "~/rent-my-gear"), (str(trabajo), "~/rent-my-gear"),
             (str(TRABAJO.resolve()), "~"), (str(RAIZ.parent.resolve()), "~/ai-native-dev"),
             (str(Path.home()), "~"), (Path.home().name, "dev")]
    if str(trabajo.resolve()).startswith("/private"):
        pares.insert(0, (str(trabajo.resolve()).removeprefix("/private"), "~/rent-my-gear"))
    for viejo, nuevo in pares:
        texto = texto.replace(viejo, nuevo)
    return texto


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in {"sin", "con"}:
        print(__doc__)
        return 2
    modo, prompt_id, nombre = argv[1:]
    prompt = (RAIZ / "prompts" / f"{prompt_id}.txt").read_text().strip()
    trabajo = preparar(modo)
    entorno = {"HOME": str(Path.home()), "PATH": os.environ["PATH"], "USER": os.environ.get("USER", ""),
               "LANG": "es_GT.UTF-8", "TERM": "dumb"}
    crudo = TRABAJO / f"{nombre.replace(chr(47), chr(95))}.raw.jsonl"
    t0 = time.time()
    with crudo.open("w") as fh:
        r = subprocess.run(comando(modo, prompt, 12), cwd=trabajo, env=entorno, stdin=subprocess.DEVNULL, stdout=fh,
                           stderr=subprocess.PIPE, text=True)
    lineas = []
    for linea in crudo.read_text().splitlines():
        if not linea.strip():
            continue
        linea = sanear(linea, trabajo)
        try:
            ev = json.loads(linea)
            if ev.get("type") == "system" and ev.get("subtype") == "init":
                for campo in CAMPOS_INIT_FUERA:
                    ev.pop(campo, None)
            linea = json.dumps(ev, ensure_ascii=False)
        except json.JSONDecodeError:
            pass
        lineas.append(linea)
    (RAIZ / "logs" / nombre).parent.mkdir(parents=True, exist_ok=True)
    (RAIZ / "logs" / f"{nombre}.jsonl").write_text("\n".join(lineas) + "\n")
    print(f"{nombre}: salida {r.returncode}, {round(time.time() - t0)} s, {len(lineas)} eventos")
    if r.stderr.strip():
        print(sanear(r.stderr.strip(), trabajo)[:500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
