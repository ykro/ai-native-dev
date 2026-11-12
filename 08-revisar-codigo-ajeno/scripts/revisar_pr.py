#!/usr/bin/env python3
"""Reviews a branch in a disposable worktree, running the checks in order. Only command output counts.

Stages: 1 the PR's own tests, 2 the judge (juez/), 3 touched files against contrato.json,
4 removed or weakened assertions in existing test files, 5 new dependencies against the registry.
Writes revision/informe.json (or --salida) and exits 1 if any stage fails.

Usage: python3 scripts/revisar_pr.py --rama pr/rsi-y-noticias [--repo .work/repo] [--salida revision/informe.json]
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv/bin/python")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True).stdout


def pytest(cwd: Path, target: str, extra_env: dict[str, str] | None = None) -> dict:
    env = {**os.environ, "GEMINI_API_KEY": "test-key-no-real-calls", "PYTHONDONTWRITEBYTECODE": "1", **(extra_env or {})}
    run = subprocess.run([PY, "-m", "pytest", target, "-q", "-rf", "--tb=line", "-p", "no:cacheprovider"],
                         cwd=cwd, capture_output=True, text=True, env=env)
    out = run.stdout
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", out)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", out)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", out)) else 0
    failures = [l[len("FAILED "):] for l in out.splitlines() if l.startswith("FAILED ")]
    return {"aprobadas": passed, "falladas": failed + errors, "total": passed + failed + errors,
            "fallas": failures, "ok": run.returncode == 0}


def stage_contract(repo: Path, base: str, branch: str) -> dict:
    contract = json.loads((ROOT / "contrato.json").read_text(encoding="utf-8"))
    status = [l.split("\t") for l in git(repo, "diff", "--name-status", f"{base}..{branch}").splitlines()]
    allowed = set(contract["archivos_permitidos"])
    globs = contract["archivos_nuevos_permitidos_glob"]
    outside = []
    for code, path in status:
        if path in allowed:
            continue
        if code == "A" and any(fnmatch.fnmatch(path, g) for g in globs):
            continue
        reason = "prueba existente editada" if path.startswith("backend/tests/") and code == "M" else \
            "no está en la lista del contrato"
        outside.append({"archivo": path, "estado": code, "motivo": reason})
    return {"archivos_tocados": [p for _, p in status], "fuera_del_contrato": outside, "ok": not outside}


def stage_assertions(repo: Path, base: str, branch: str) -> dict:
    status = [l.split("\t") for l in git(repo, "diff", "--name-status", f"{base}..{branch}").splitlines()]
    existing_tests = [p for c, p in status if c == "M" and re.search(r"(^|/)tests?/.*\.py$", p)]
    removed = []
    for path in existing_tests:
        diff = git(repo, "diff", "-U0", f"{base}..{branch}", "--", path)
        for line in diff.splitlines():
            if line.startswith("-") and not line.startswith("---") and re.search(r"\bassert\b|pytest\.raises", line):
                removed.append({"archivo": path, "linea_quitada": line[1:].strip()})
    return {"aserciones_quitadas_o_debilitadas": len(removed), "detalle": removed, "ok": not removed}


def stage_dependencies(repo: Path, base: str, branch: str) -> dict:
    run = subprocess.run([sys.executable, str(ROOT / "scripts/verificar_dependencias.py"), "--desde", base, "--hasta", branch,
                          "--repo", str(repo), "--json"], capture_output=True, text=True)
    packages = json.loads(run.stdout) if run.stdout.strip() else []
    return {"dependencias_nuevas": len(packages), "no_existen": [p["paquete"] for p in packages if p["existe"] is False],
            "detalle": packages, "ok": run.returncode == 0}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rama", required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--repo", default=str(ROOT / ".work/repo"))
    parser.add_argument("--salida", default="revision/informe.json")
    args = parser.parse_args()
    repo = Path(args.repo)
    worktree = ROOT / ".work" / ("wt-" + args.rama.replace("/", "-"))
    shutil.rmtree(worktree, ignore_errors=True)
    git(repo, "worktree", "prune")
    git(repo, "worktree", "add", "--detach", str(worktree), args.rama)
    print(f"Worktree desechable de {args.rama} creado.")
    started = time.time()
    report: dict = {"rama": args.rama, "base": args.base, "etapas": {}}
    try:
        stages = [
            ("1_pruebas_del_pr", lambda: pytest(worktree, "backend/tests")),
            ("2_juez", lambda: pytest(ROOT, "juez", {"TP_ROOT": str(worktree)})),
            ("3_archivos_contra_contrato", lambda: stage_contract(repo, args.base, args.rama)),
            ("4_aserciones", lambda: stage_assertions(repo, args.base, args.rama)),
            ("5_dependencias", lambda: stage_dependencies(repo, args.base, args.rama)),
        ]
        for name, fn in stages:
            t0 = time.time()
            result = fn()
            result["segundos"] = round(time.time() - t0, 1)
            report["etapas"][name] = result
            print(f"[{'OK' if result['ok'] else 'FALLA'}] {name}")
    finally:
        git(repo, "worktree", "remove", "--force", str(worktree))
    report["segundos_total"] = round(time.time() - started, 1)
    report["ok"] = all(s["ok"] for s in report["etapas"].values())
    out = ROOT / args.salida
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Informe en {out.relative_to(ROOT)}; resultado: {'APRUEBA' if report['ok'] else 'RECHAZA'}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
