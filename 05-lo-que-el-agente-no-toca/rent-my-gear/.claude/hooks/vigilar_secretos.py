#!/usr/bin/env python3
"""Hook PreToolUse para Bash, Read, Edit, Write y Grep: protege los archivos .env.

Bloquea (código 2) cualquier acceso a .env y .env.* salvo .env.example, y los comandos que
vuelcan el entorno completo. Es un filtro de texto: solo reconoce lectores conocidos
(cat, head, grep, sed...), redirecciones y herramientas del harness. Un programa que abre
el archivo por su cuenta no se ve desde aquí; esa capa es el sandbox.
"""
from __future__ import annotations

import fnmatch
import json
import os
import shlex
import sys

PERMITIDOS = {".env.example", ".env.sample", ".env.template"}
MUESTRAS = [".env", ".env.local", ".env.production", ".env.development"]
LECTORES = {"cat", "head", "tail", "less", "more", "nl", "tac", "sed", "awk", "grep", "egrep",
            "fgrep", "rg", "strings", "xxd", "od", "hexdump", "bat", "cp", "mv", "scp", "rsync",
            "source", ".", "base64", "cut", "sort", "uniq", "diff", "tee", "vi", "vim", "nano",
            "code", "open", "jq", "wc", "file", "stat", "ln", "dd", "curl", "zip", "tar"}
SEPARADORES = set("&|;()")
ARCHIVO_DEL_HARNESS = {"Read": ("file_path",), "Edit": ("file_path",), "Write": ("file_path",),
                       "MultiEdit": ("file_path",), "NotebookEdit": ("notebook_path",),
                       "Grep": ("path", "glob"), "Glob": ("pattern", "path")}


def es_secreto(ruta: str) -> bool:
    base = os.path.basename(ruta.rstrip("/"))
    if base in PERMITIDOS:
        return False
    if base == ".env" or base.startswith(".env."):
        return True
    if any(c in base for c in "*?["):  # un glob que alcanzaría un .env
        return any(fnmatch.fnmatch(m, base) for m in MUESTRAS)
    return False


def segmentos(comando: str) -> list[list[str]]:
    lexer = shlex.shlex(comando, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    salida: list[list[str]] = [[]]
    for tok in lexer:
        if set(tok) <= SEPARADORES:
            salida.append([])
        else:
            salida[-1].append(tok)
    return [s for s in salida if s]


def vuelca_entorno(p: list[str]) -> bool:
    cmd, args = os.path.basename(p[0]), p[1:]
    if cmd == "printenv":
        return True
    if cmd == "env":
        return not [a for a in args if not a.startswith("-")]
    if cmd in {"export", "declare", "typeset"}:
        return not args or args[0] in {"-p", "-x", "-px", "-xp"}
    if cmd == "set":
        return not args
    if cmd == "compgen":
        return "-e" in args or "-v" in args
    return any("/proc/" in a and a.endswith("environ") for a in args)


def revisar_bash(comando: str) -> str | None:
    for seg in segmentos(comando):
        i = 0
        while i < len(seg) and "=" in seg[i] and not seg[i].startswith("-"):
            i += 1
        p = seg[i:]
        if not p:
            continue
        if vuelca_entorno(p):
            return "Volcar el entorno completo está bloqueado por una regla del proyecto."
        redirigidos = [p[j + 1] for j, t in enumerate(p[:-1]) if t in {"<", ">", ">>", "<<<"}]
        if any(es_secreto(r) for r in redirigidos):
            return "Redirigir desde o hacia un archivo .env está bloqueado por una regla del proyecto."
        if os.path.basename(p[0]) in LECTORES and any(es_secreto(a) for a in p[1:]):
            return "Leer o copiar archivos .env está bloqueado por una regla del proyecto."
    return None


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    herramienta, entrada = evento.get("tool_name", ""), evento.get("tool_input", {})
    motivo = None
    if herramienta == "Bash":
        motivo = revisar_bash(entrada.get("command", ""))
    elif herramienta in ARCHIVO_DEL_HARNESS:
        if any(es_secreto(str(entrada.get(k, ""))) for k in ARCHIVO_DEL_HARNESS[herramienta]):
            motivo = "Los archivos .env están bloqueados por una regla del proyecto."
    if motivo:
        print(motivo + " Para conocer los nombres de las variables usa .env.example.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
