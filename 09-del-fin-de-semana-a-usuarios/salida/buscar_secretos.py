#!/usr/bin/env python3
"""Simple secret scanner (regular expressions, no dependencies).

Scans the files that Git would version (tracked or not ignored) of a folder and checks that .env is ignored.
Usage: python3 salida/buscar_secretos.py <carpeta>
Exit code 1 if it finds something. It never prints the secret itself, only file, line and rule.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RULES = {
    "llave de Google (AIza...)": re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    "llave privada": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "llave tipo sk-": re.compile(r"\bsk-[A-Za-z0-9]{20,}"),
    "token de GitHub": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "asignación de secreto": re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9_\-/+]{16,}['\"]"),
    "variable de llave con valor": re.compile(r"\b[A-Z_]*(?:API_KEY|SECRET|TOKEN)=[A-Za-z0-9_\-]{16,}"),
}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".lock", ".svg", ".woff", ".woff2", ".pdf"}


def listed_files(folder: Path) -> list[Path]:
    git = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=folder, capture_output=True, text=True)
    if git.returncode == 0 and git.stdout.strip():
        return [folder / line for line in git.stdout.splitlines()]
    skip = {"node_modules", ".next", ".venv", "dist", "__pycache__", ".git"}
    return [p for p in folder.rglob("*") if p.is_file() and not (set(p.relative_to(folder).parts) & skip)]


def env_is_ignored(folder: Path) -> bool:
    for gitignore in [folder / ".gitignore", *folder.glob("*/.gitignore")]:
        if gitignore.exists() and re.search(r"^\s*\.env(\*|\.local)?\s*$|^\s*\.env\*", gitignore.read_text(encoding="utf-8"), re.M):
            return True
    return False


def scan(folder: Path) -> dict:
    findings = []
    tracked_env = []
    for path in listed_files(folder):
        rel = path.relative_to(folder).as_posix()
        if re.search(r"(^|/)\.env(\.local|\.production)?$", rel):
            tracked_env.append(rel)
        if path.suffix.lower() in SKIP_SUFFIX or not path.is_file() or "package-lock.json" in rel:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if re.search(r"--set-secrets|secretKeyRef|secretmanager|\$\{[A-Z_]+\}|:latest|\.\.\.", line):
                continue  # reference to a secret in Secret Manager or an env substitution, not a value
            for name, rule in RULES.items():
                if rule.search(line):
                    findings.append({"archivo": rel, "linea": number, "regla": name})
    return {"hallazgos": findings, "env_versionado": tracked_env, "env_ignorado": env_is_ignored(folder)}


if __name__ == "__main__":
    result = scan(Path(sys.argv[1]).resolve())
    for f in result["hallazgos"]:
        print(f"SECRETO? {f['archivo']}:{f['linea']} ({f['regla']})")
    for e in result["env_versionado"]:
        print(f"ARCHIVO .env versionable: {e}")
    if not result["env_ignorado"]:
        print("El .gitignore no ignora .env")
    ok = not result["hallazgos"] and not result["env_versionado"] and result["env_ignorado"]
    print("OK: sin secretos y .env ignorado" if ok else "FALLA")
    sys.exit(0 if ok else 1)
