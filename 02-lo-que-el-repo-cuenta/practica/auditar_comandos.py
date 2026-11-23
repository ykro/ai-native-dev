"""Audita y ejecuta los comandos no interactivos prometidos al agente."""
import json
import pathlib
import sys

from practica.comando_colgado_roto import correr_comando

REQUERIDOS = ("typecheck", "lint", "test:run")


def leer_scripts(pkg_path):
    datos = json.loads(pathlib.Path(pkg_path).read_text(encoding="utf-8"))
    return datos.get("scripts", {})


def auditar_scripts(pkg_path, requeridos=REQUERIDOS):
    scripts = leer_scripts(pkg_path)
    faltan = [n for n in requeridos if n not in scripts]
    return {"ok": not faltan, "faltan": faltan,
            "presentes": {k: scripts[k] for k in requeridos if k in scripts}}


def ejecutar_verificacion(app="travelens", nombres=REQUERIDOS):
    scripts = leer_scripts(pathlib.Path(app) / "package.json")
    resultados = []
    for nombre in nombres:
        if nombre not in scripts:
            resultados.append({"comando": nombre, "ok": False,
                               "codigo": "SCRIPT_INEXISTENTE"})
            continue
        r = correr_comando(["npm", "run", nombre], cwd=app, timeout=30)
        resultados.append({"comando": nombre, **r})
    return resultados


if __name__ == "__main__":
    nombres = tuple(sys.argv[1:]) if len(sys.argv) > 1 else REQUERIDOS
    print("antes  ", auditar_scripts("medicion/antes/package.antes.json", nombres))
    print("después", auditar_scripts("travelens/package.json", nombres))
    for r in ejecutar_verificacion("travelens", nombres):
        print(" ", json.dumps(r, ensure_ascii=False))
