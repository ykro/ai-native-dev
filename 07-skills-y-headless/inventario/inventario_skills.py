"""Inventario de Skills instaladas en una o varias carpetas (sin copiar su contenido).

Para cada skill reporta de dónde viene (carpeta propia o enlace simbólico y a qué raíz
apunta), cuántas líneas tiene su SKILL.md, el largo de su descripción y si trae scripts
o referencias. Sirve para ver qué se carga siempre (nombre y descripción) y qué solo
cuando la skill se usa (el cuerpo y sus archivos).

Uso:
    python3 inventario/inventario_skills.py skills pawsmatch/.claude/skills
    python3 inventario/inventario_skills.py skills --solo sanear-logs,cerrar-con-evidencia --json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def leer_frontmatter(texto: str) -> dict[str, str]:
    """Lee el bloque YAML simple entre las dos primeras líneas '---' (clave: valor)."""
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        return {}
    datos: dict[str, str] = {}
    clave = None
    for linea in lineas[1:]:
        if linea.strip() == "---":
            break
        if ":" in linea and not linea.startswith((" ", "\t")):
            clave, valor = linea.split(":", 1)
            clave = clave.strip()
            datos[clave] = valor.strip().strip('"').strip("'")
        elif clave and linea.strip():
            datos[clave] = (datos[clave] + " " + linea.strip()).strip()
    return datos


def origen(entrada: Path, raices: dict[str, str]) -> str:
    if not entrada.is_symlink():
        return "propia"
    destino = os.path.realpath(entrada)
    for prefijo, nombre in raices.items():
        if destino.startswith(prefijo):
            return f"enlace a {nombre}"
    return "enlace a otra carpeta"


def describir(entrada: Path, raices: dict[str, str]) -> dict | None:
    skill_md = entrada / "SKILL.md"
    if not skill_md.is_file():
        return None
    texto = skill_md.read_text(encoding="utf-8", errors="replace")
    fm = leer_frontmatter(texto)
    real = Path(os.path.realpath(entrada))
    extras = sorted(p.name for p in real.iterdir() if p.is_dir() and not p.name.startswith("."))
    return {
        "skill": entrada.name,
        "origen": origen(entrada, raices),
        "nombre_coincide": fm.get("name") == entrada.name,
        "lineas_skill_md": len(texto.splitlines()),
        "caracteres_descripcion": len(fm.get("description", "")),
        "carpetas": extras,
    }


def inventariar(carpetas: list[Path], solo: set[str] | None = None) -> dict:
    raices = {os.path.realpath(c): c.name if c.name != "skills" else c.parent.name for c in carpetas}
    raices.update({os.path.realpath(Path.home() / ".claude" / "plugins"): "plugin"})
    salida = {}
    for carpeta in carpetas:
        filas = []
        for entrada in sorted(carpeta.iterdir()):
            if solo and entrada.name not in solo:
                continue
            fila = describir(entrada, raices)
            if fila:
                filas.append(fila)
        salida[carpeta.name if carpeta.name != "skills" else carpeta.parent.name] = filas
    return salida


def totales(filas: list[dict]) -> dict:
    return {
        "skills": len(filas),
        "propias": sum(1 for f in filas if f["origen"] == "propia"),
        "enlaces": sum(1 for f in filas if f["origen"] != "propia"),
        "con_scripts": sum(1 for f in filas if "scripts" in f["carpetas"]),
        "con_referencias": sum(1 for f in filas if "references" in f["carpetas"]),
        "caracteres_de_descripciones": sum(f["caracteres_descripcion"] for f in filas),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Inventario de Skills")
    ap.add_argument("carpetas", nargs="+", type=Path)
    ap.add_argument("--solo", help="lista de skills separadas por coma")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    solo = set(a.solo.split(",")) if a.solo else None
    inv = inventariar([c.expanduser() for c in a.carpetas], solo)
    if a.json:
        print(json.dumps({"carpetas": inv, "totales": {k: totales(v) for k, v in inv.items()}},
                         ensure_ascii=False, indent=2))
        return 0
    for carpeta, filas in inv.items():
        t = totales(filas)
        print(f"{carpeta}: {t['skills']} skills, {t['propias']} propias, {t['enlaces']} enlaces,"
              f" {t['con_scripts']} con scripts, {t['caracteres_de_descripciones']:,} caracteres de descripciones")
        for f in filas:
            print(f"  {f['skill']:<28} {f['origen']:<22} {f['lineas_skill_md']:>4} líneas"
                  f"  desc {f['caracteres_descripcion']:>4}  {','.join(f['carpetas'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
