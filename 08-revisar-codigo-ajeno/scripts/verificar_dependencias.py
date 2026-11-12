#!/usr/bin/env python3
"""Checks every dependency added to requirements.txt against the public Python package registry.

For each added line it reports whether the package exists, when it was first published and who
publishes it. Exit code 1 if any added package does not exist.

Usage: python3 scripts/verificar_dependencias.py --desde main --hasta pr/rsi-y-noticias [--repo .work/repo] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ = "backend/requirements.txt"


def added_requirements(repo: Path, base: str, head: str) -> list[str]:
    diff = subprocess.run(["git", "diff", f"{base}..{head}", "--", REQ], cwd=repo, capture_output=True, text=True, check=True).stdout
    names = []
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            m = re.match(r"\+\s*([A-Za-z0-9][A-Za-z0-9._-]*)", line)
            if m:
                names.append(m.group(1))
    return names


def lookup(name: str) -> dict:
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"paquete": name, "existe": False, "respuesta": "HTTP 404 (no existe en el registro)"}
        return {"paquete": name, "existe": None, "respuesta": f"HTTP {exc.code}"}
    dates = [f["upload_time_iso_8601"] for files in data["releases"].values() for f in files]
    info = data["info"]
    return {
        "paquete": name,
        "existe": True,
        "primera_publicacion": min(dates) if dates else None,
        "publicador": info.get("author") or info.get("maintainer") or info.get("author_email") or "desconocido",
        "respuesta": "HTTP 200",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--desde", required=True)
    parser.add_argument("--hasta", required=True)
    parser.add_argument("--repo", default=str(ROOT / ".work/repo"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = [lookup(n) for n in added_requirements(Path(args.repo), args.desde, args.hasta)]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif not results:
        print("Sin dependencias nuevas.")
    for r in results:
        if not args.json:
            if r["existe"]:
                print(f"{r['paquete']}: existe, primera publicación {r['primera_publicacion']}, publicador {r['publicador']}")
            else:
                print(f"{r['paquete']}: NO EXISTE en el registro público ({r['respuesta']})")
    return 1 if any(r["existe"] is not True for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
