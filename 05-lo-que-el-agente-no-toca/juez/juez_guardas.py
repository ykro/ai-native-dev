#!/usr/bin/env python3
"""Juez determinista de las barreras: corre cada caso de casos.json contra los hooks.

Lee .claude/settings.json del proyecto, elige los hooks que corresponden a la herramienta de
cada caso (igual que el harness, por `matcher`), los ejecuta con el mismo JSON que recibirían
y compara la decisión con la esperada. Sin red: usa registro-simulado.json.

    python3 juez/juez_guardas.py --proyecto rent-my-gear
    python3 juez/juez_guardas.py --proyecto rent-my-gear --registro real --casos 4,5,8

Un proyecto sin .claude/ (sin guardas) pasa todo, y por eso los casos de bloqueo salen en rojo.
Los casos con `cubierto_por` no cuentan como falla del hook: se anotan como cubiertos por otra capa.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORDEN = {"bloquea": 3, "pregunta": 2, "pasa": 1}


def hooks_para(proyecto: Path, herramienta: str) -> list[str]:
    ajustes = proyecto / ".claude" / "settings.json"
    if not ajustes.exists():
        return []
    config = json.loads(ajustes.read_text())
    comandos = []
    for grupo in config.get("hooks", {}).get("PreToolUse", []):
        matcher = grupo.get("matcher", "*")
        if matcher in ("", "*") or re.fullmatch(matcher, herramienta):
            comandos += [h["command"] for h in grupo.get("hooks", []) if h.get("type") == "command"]
    return comandos


def decision_de(proceso: subprocess.CompletedProcess) -> str:
    if proceso.returncode == 2:
        return "bloquea"
    if proceso.returncode == 0 and proceso.stdout.strip():
        try:
            d = json.loads(proceso.stdout)["hookSpecificOutput"]["permissionDecision"]
        except (json.JSONDecodeError, KeyError):
            return "pasa"
        return {"deny": "bloquea", "ask": "pregunta"}.get(d, "pasa")
    return "pasa"


def evaluar(caso: dict, proyecto: Path, registro: str) -> tuple[str, str]:
    if caso.get("tipo") == "archivo":
        f = proyecto / caso["archivo"]
        ok = f.exists() and caso["contiene"] in f.read_text()
        return ("pasa" if ok else "ausente"), ("" if ok else f"{caso['archivo']} no contiene {caso['contiene']}")
    entrada = json.loads(json.dumps(caso["entrada"]).replace("{proyecto}", str(proyecto)))
    evento = json.dumps({"hook_event_name": "PreToolUse", "tool_name": caso["herramienta"],
                         "tool_input": entrada, "cwd": str(proyecto)})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(proyecto), "GUARDAS_REGISTRO": registro}
    mejor, motivo = "pasa", ""
    for cmd in hooks_para(proyecto, caso["herramienta"]):
        p = subprocess.run(["sh", "-c", cmd], input=evento, capture_output=True, text=True,
                           env=env, cwd=proyecto)
        d = decision_de(p)
        if ORDEN[d] > ORDEN[mejor]:
            mejor = d
            motivo = (p.stderr.strip() if d == "bloquea" else p.stdout.strip())
    return mejor, motivo


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", type=Path, required=True)
    ap.add_argument("--casos", default="", help="números separados por coma; por defecto todos")
    ap.add_argument("--registro", choices=["simulado", "real"], default="simulado")
    ap.add_argument("--grupo", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    proyecto = a.proyecto.resolve()
    casos = json.loads((AQUI / "casos.json").read_text())
    if a.casos:
        elegidos = {int(x) for x in a.casos.split(",")}
        casos = [c for c in casos if c["n"] in elegidos]
    if a.grupo:
        casos = [c for c in casos if c["grupo"] == a.grupo]
    os.environ.setdefault("GUARDAS_REGISTRO_ARCHIVO", str(AQUI / "registro-simulado.json"))
    resultados = []
    for c in casos:
        obtenida, motivo = evaluar(c, proyecto, a.registro)
        cubierto = c.get("cubierto_por")
        if registro_real := (a.registro == "real" and "esperado_vivo" in c):
            c = {**c, "esperado": c["esperado_vivo"]}
        ok = obtenida == c["esperado"]
        resultados.append({"n": c["n"], "grupo": c["grupo"], "esperado": c["esperado"],
                           "obtenida": obtenida, "ok": ok, "cubierto_por": cubierto, "motivo": motivo})
        if not a.json:
            marca = "PASA" if ok else "FALLA"
            extra = f"  (cubierto por el {cubierto}; el hook de texto no lo ve)" if cubierto else ""
            etiqueta = (c.get("entrada", {}).get("command") or c.get("entrada", {}).get("file_path")
                        or c.get("archivo", ""))
            print(f"{marca:5} #{c['n']:<2} {c['grupo']:<14} esperado={c['esperado']:<8} obtenido={obtenida:<8} {etiqueta.replace("{proyecto}", "~/rent-my-gear")[:60]}{extra}")
    pasan = sum(r["ok"] for r in resultados)
    de_hook = [r for r in resultados if not r["cubierto_por"]]
    pasan_hook = sum(r["ok"] for r in de_hook)
    resumen = {"pasan": pasan, "total": len(resultados), "pasan_sin_anotados": pasan_hook,
               "total_sin_anotados": len(de_hook),
               "instalaciones_pasan": sum(r["ok"] for r in resultados if r["grupo"] == "instalaciones"),
               "instalaciones_total": sum(r["grupo"] == "instalaciones" for r in resultados)}
    if a.json:
        print(json.dumps({"resultados": resultados, "resumen": resumen}, ensure_ascii=False, indent=2))
    else:
        print(f"\nPasan {pasan} de {len(resultados)} casos "
              f"({pasan_hook} de {len(de_hook)} sin contar los anotados como cubiertos por otra capa).")
        print(f"Instalaciones: {resumen['instalaciones_pasan']} de {resumen['instalaciones_total']}.")
    return 0 if pasan == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
