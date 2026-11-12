#!/usr/bin/env python3
"""Review of salida/<project>: scripted stages (judge, touched files, removed assertions, new dependencies
against the public registry) plus a clean read-only agent session. Writes medicion/<project>-revision.json."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / ".work"
JS_SUBDIR = {"pawsmatch": "app", "travelens": "", "rent-my-gear": "", "traderpulse": ""}
FORBIDDEN = re.compile(r"(^|/)(\.env[^/]*|\.claude/.*|salida/.*|BRECHAS\.md)$")


def sh(*a, cwd, check=True):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=check).stdout


def registry(kind: str, name: str) -> dict:
    url = f"https://pypi.org/pypi/{name}/json" if kind == "pip" else f"https://registry.npmjs.org/{name.replace('/', '%2f')}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.load(r)
    except urllib.error.HTTPError as exc:
        return {"paquete": name, "existe": exc.code != 404 and None, "respuesta": f"HTTP {exc.code}"}
    if kind == "pip":
        dates = [f["upload_time_iso_8601"] for fs in data["releases"].values() for f in fs]
        return {"paquete": name, "existe": True, "primera_publicacion": min(dates) if dates else None}
    return {"paquete": name, "existe": True, "primera_publicacion": data.get("time", {}).get("created")}


def new_dependencies(base: Path, project: str) -> list[dict]:
    found = []
    for rel, kind in ((f"{JS_SUBDIR[project] + '/' if JS_SUBDIR[project] else ''}package.json", "npm"), ("backend/requirements.txt", "pip")):
        try:
            before = sh("git", "show", f"main:{rel}", cwd=base, check=True)
            after = sh("git", "show", f"salida/{project}:{rel}", cwd=base, check=True)
        except subprocess.CalledProcessError:
            continue
        if kind == "npm":
            def names(t):
                d = json.loads(t)
                return set(d.get("dependencies", {})) | set(d.get("devDependencies", {}))
            added = names(after) - names(before)
        else:
            def names(t):
                return {m.group(1).lower() for l in t.splitlines() if (m := re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", l))}
            added = names(after) - names(before)
        found += [registry(kind, n) for n in sorted(added)]
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proyecto", required=True)
    args = parser.parse_args()
    p = args.proyecto
    base = WORK / p
    rev = WORK / f"{p}-rev"
    shutil.rmtree(rev, ignore_errors=True)
    sh("git", "worktree", "prune", cwd=base)
    sh("git", "worktree", "add", "-q", "--detach", str(rev), f"salida/{p}", cwd=base)
    nm_src = ROOT / "proyectos" / p / JS_SUBDIR[p] / "node_modules"
    if nm_src.exists():
        (rev / JS_SUBDIR[p] / "node_modules").symlink_to(nm_src)
    if p == "traderpulse":
        (rev / ".venv").symlink_to(ROOT / ".venv")
    t0 = time.time()
    judge = json.loads(subprocess.run([sys.executable, str(ROOT / "salida/juez_salida.py"), "--proyecto", p, "--ruta", str(rev), "--json"],
                                      capture_output=True, text=True).stdout)
    status = [l.split("\t") for l in sh("git", "diff", "--name-status", "main", f"salida/{p}", cwd=base).splitlines()]
    touched_forbidden = [path for code, path in status if FORBIDDEN.search(path)]
    removed = []
    for code, path in status:
        if code == "M" and re.search(r"(\.test\.|\.spec\.|/tests?/|test_)", path):
            for line in sh("git", "diff", "-U0", "main", f"salida/{p}", "--", path, cwd=base).splitlines():
                if line.startswith("-") and not line.startswith("---") and re.search(r"\b(expect|assert|toBe|toEqual|raises)\b", line):
                    removed.append({"archivo": path, "linea_quitada": line[1:].strip()})
    deps = new_dependencies(base, p)
    shortstat = sh("git", "diff", "--shortstat", "main", f"salida/{p}", cwd=base).strip()
    numstat = [l.split("\t") for l in sh("git", "diff", "--numstat", "main", f"salida/{p}", cwd=base).splitlines()]
    scripted = {
        "juez_de_salida": {"aprobadas": judge["aprobadas"], "aplicadas": judge["aplicadas"], "falladas": judge["falladas"]},
        "archivos_tocados": [path for _, path in status], "archivos_prohibidos_tocados": touched_forbidden,
        "aserciones_quitadas_o_debilitadas": len(removed), "detalle_aserciones": removed,
        "dependencias_nuevas": deps, "dependencias_que_no_existen": [d["paquete"] for d in deps if d["existe"] is False],
        "diff": {"resumen": shortstat, "archivos": len(status), "lineas_agregadas": sum(int(a) for a, _, _ in numstat if a.isdigit()),
                 "lineas_quitadas": sum(int(b) for _, b, _ in numstat if b.isdigit())},
    }
    informe = json.dumps({k: v for k, v in scripted.items() if not k.startswith("detalle")}, ensure_ascii=False, indent=1)
    prompt = (ROOT / "prompts/revisar-salida.txt").read_text(encoding="utf-8").format(proyecto=p, informe=informe)
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--max-turns", "25", "--model", "sonnet", "--setting-sources", "project",
           "--max-budget-usd", "3.00", "--allowedTools", "Read", "Glob", "Grep", "Bash(git diff *)", "Bash(git log *)", "Bash(git show *)"]
    s0 = time.time()
    out = subprocess.run(cmd, cwd=rev, capture_output=True, text=True)
    agent_seconds = round(time.time() - s0, 1)
    try:
        result = json.loads(out.stdout)
    except json.JSONDecodeError:
        result = {"result": out.stdout[-300:]}
    m = re.search(r"\{.*\}", result.get("result", ""), re.S)
    try:
        findings = json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        findings = {"error": "respuesta no JSON", "texto": result.get("result", "")}
    record = {"proyecto": p, "automaticas": scripted, "agente_revisor": findings,
              "medicion": {"segundos_etapas_automaticas": round(s0 - t0, 1), "segundos_agente": agent_seconds,
                           "turnos": result.get("num_turns"), "costo_usd": result.get("total_cost_usd"), "usage": result.get("usage")}}
    for link in (rev / JS_SUBDIR[p] / "node_modules", rev / ".venv"):
        if link.is_symlink():
            link.unlink()
    sh("git", "worktree", "remove", "--force", str(rev), cwd=base)
    (ROOT / f"medicion/{p}-revision.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{p}] juez {judge['aprobadas']}/{judge['aplicadas']}; deps nuevas {len(deps)} (no existen: {len(scripted['dependencias_que_no_existen'])}); "
          f"aserciones quitadas {len(removed)}; hallazgos del agente {len(findings.get('hallazgos', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
