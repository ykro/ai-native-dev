#!/usr/bin/env python3
"""Exit judge: seven promises made to a user, deterministic, no model.

Usage: python3 salida/juez_salida.py --proyecto <nombre> [--ruta <carpeta>] [--json]
Prints applied, passed and failed checks with the reason. Exit code 1 if any applied check fails.
Weak checks (they only look for the existence of something) are marked as such in the output.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "salida"))
import buscar_secretos  # noqa: E402

NAMES = {
    "1": "comando único de verificación en verde",
    "2": "sin secretos versionados y .env ignorado",
    "3": "auditoría de dependencias de producción sin hallazgos altos",
    "4": "tiempo agotado y respuesta rota del modelo con error controlado (con prueba)",
    "5": "tope de salida del modelo y límite de peticiones por cliente (con prueba)",
    "6": "registros sin datos personales y ruta de salud (con prueba)",
    "7": "sección «Cómo volver atrás» en el README",
}
WEAK = {"7": "solo comprueba que la sección y un comando existen, no que el comando funcione",
        "6": "los registros sin datos personales se comprueban solo con la prueba que escribió el proyecto"}


def run(cmd: str, cwd: Path, timeout: int = 900) -> subprocess.CompletedProcess:
    env = {**os.environ, "CI": "1", "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "test-key-no-real-calls"),
           "PY": str(ROOT / ".venv/bin/python")}
    return subprocess.run(cmd.replace("{PY}", str(ROOT / ".venv/bin/python")), shell=True, cwd=cwd, capture_output=True,
                          text=True, timeout=timeout, env=env)


def tagged_tests(spec: dict, cwd: Path) -> tuple[bool, str]:
    """Runs every tagged test group of the profile; each must have at least `min` passing tests."""
    for group in spec["pruebas"]:
        out = run(spec["runner"].replace("{filtro}", group["filtro"]), cwd)
        text = out.stdout + out.stderr
        passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", text)) else 0
        if out.returncode != 0 or passed < group["min"]:
            return False, f"las pruebas con la etiqueta «{group['filtro']}» no alcanzan el mínimo ({passed} de {group['min']} aprobadas)"
    return True, "pruebas etiquetadas aprobadas: " + ", ".join(g["filtro"] for g in spec["pruebas"])


def check_1(spec, cwd):
    out = run(spec["comando"], cwd)
    return out.returncode == 0, "comando de verificación en verde" if out.returncode == 0 else f"`{spec['comando']}` falló: " + (out.stdout + out.stderr).strip().splitlines()[-1][:160]


def check_2(spec, cwd):
    r = buscar_secretos.scan(cwd)
    if r["hallazgos"] or r["env_versionado"] or not r["env_ignorado"]:
        reasons = [f"{h['archivo']}:{h['linea']}" for h in r["hallazgos"]] + r["env_versionado"] + ([] if r["env_ignorado"] else [".gitignore no ignora .env"])
        return False, "; ".join(reasons)
    return True, "sin secretos y .env ignorado"


def check_3(spec, cwd):
    documented = (cwd / "docs/hallazgos-dependencias.md")
    if spec["tipo"] == "npm":
        out = run("npm audit --omit=dev --json", cwd)
        try:
            data = json.loads(out.stdout)
        except json.JSONDecodeError:
            return False, "npm audit no devolvió un resultado legible (¿sin red?)"
        vulns = data.get("vulnerabilities", {})
        high = sorted(n for n, v in vulns.items() if v.get("severity") in ("high", "critical"))
    else:
        out = run("uv pip compile backend/requirements.txt -q -o /tmp/_pinned_req.txt && uvx pip-audit -r /tmp/_pinned_req.txt --no-deps --disable-pip --format json", cwd)
        try:
            data = json.loads(out.stdout)
        except json.JSONDecodeError:
            return False, "pip-audit no devolvió un resultado legible: " + (out.stdout + out.stderr).strip()[-120:]
        high = sorted({d["name"] for d in data.get("dependencies", []) if d.get("vulns")})
    if not high:
        return True, "sin hallazgos altos o críticos en producción"
    if documented.exists() and all(name in documented.read_text(encoding="utf-8") for name in high):
        return True, "hallazgos documentados en docs/hallazgos-dependencias.md: " + ", ".join(high)
    return False, "hallazgos sin resolver ni documentar en: " + ", ".join(high)


def check_4(spec, cwd):
    return tagged_tests(spec, cwd)


def check_5(spec, cwd):
    src = cwd / spec["directorio_fuente"]
    cap = re.compile(spec["tope_regex"])
    has_cap = any(cap.search(p.read_text(encoding="utf-8", errors="ignore")) for p in src.rglob("*")
                  if p.is_file() and ".test." not in p.name and "test_" not in p.name and p.suffix in {".ts", ".tsx", ".py"})
    if not has_cap:
        return False, "no hay tope de salida del modelo configurado en el código de producción"
    return tagged_tests(spec, cwd)


def check_6(spec, cwd):
    return tagged_tests(spec, cwd)


def check_7(spec, cwd):
    readme = (cwd / spec.get("readme", "README.md"))
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    m = re.search(r"^#{1,4}\s*Cómo volver atrás\s*$(.*?)(?=^#{1,4}\s|\Z)", text, re.I | re.M | re.S)
    if not m:
        return False, "el README no tiene la sección «Cómo volver atrás»"
    if not re.search(r"```[\s\S]*?(git (revert|checkout|reset|switch)|gcloud run (services )?(update-traffic|deploy)|vercel (rollback|promote)|rollback)[\s\S]*?```", m.group(1)):
        return False, "la sección existe pero no trae un comando para volver a la versión anterior"
    return True, "sección con comando de reversa"


CHECKS = {"1": check_1, "2": check_2, "3": check_3, "4": check_4, "5": check_5, "6": check_6, "7": check_7}


def judge(project: str, folder: Path) -> dict:
    profile = json.loads((ROOT / f"salida/perfiles/{project}.json").read_text(encoding="utf-8"))
    cwd = folder / profile.get("subcarpeta", "")
    applied, passed, failed, n_a = [], [], [], []
    detail = {}
    for cid, spec in profile["comprobaciones"].items():
        if not spec.get("aplica", True):
            n_a.append({"id": cid, "nombre": NAMES[cid], "razon": spec["razon"]})
            continue
        applied.append(cid)
        try:
            ok, reason = CHECKS[cid](spec, folder if cid in {"2", "7"} else cwd)
        except Exception as exc:  # a broken check counts as failed, never as passed
            ok, reason = False, f"la comprobación lanzó {type(exc).__name__}: {exc}"
        detail[cid] = {"nombre": NAMES[cid], "ok": ok, "motivo": reason, **({"debil": WEAK[cid]} if cid in WEAK else {})}
        (passed if ok else failed).append(cid)
    return {"proyecto": project, "aplicadas": len(applied), "aprobadas": len(passed), "falladas": failed,
            "no_aplica": n_a, "detalle": detail}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proyecto", required=True)
    parser.add_argument("--ruta")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    folder = Path(args.ruta) if args.ruta else ROOT / "proyectos" / args.proyecto
    result = judge(args.proyecto, folder)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Juez de salida · {args.proyecto}: {result['aprobadas']} de {result['aplicadas']} aplicadas aprobadas")
        for cid, d in result["detalle"].items():
            print(f"  [{'OK' if d['ok'] else 'FALLA'}] {cid}. {d['nombre']} — {d['motivo']}" + (f"  (comprobación débil: {d['debil']})" if d.get("debil") else ""))
        for n in result["no_aplica"]:
            print(f"  [N/A ] {n['id']}. {n['nombre']} — {n['razon']}")
    return 1 if result["falladas"] else 0


if __name__ == "__main__":
    sys.exit(main())
