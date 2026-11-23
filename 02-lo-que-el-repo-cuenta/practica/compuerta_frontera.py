"""Compuerta ejecutable: todo servicio que llama al modelo valida con Zod."""
import json
import pathlib
import re
import sys

SERVICIOS = pathlib.Path("travelens/src/services")
USA_MODELO = re.compile(r"@google/genai|generateContent")
IMPORTA_ZOD = re.compile(
    r'import\s+(?!type\b)[^;]*from\s+["\'](?:\./|@/services/)schemas["\']'
)
EJECUTA_ZOD = re.compile(r"\b\w+Schema\.(?:safeParse|parse)\s*\(")
REGLAS = (("importar schemas", IMPORTA_ZOD),
          ("ejecutar Schema.parse/safeParse", EJECUTA_ZOD))


def verificar_frontera(carpeta=SERVICIOS):
    violaciones = []
    for ruta in sorted(pathlib.Path(carpeta).glob("*.ts")):
        if ruta.name.endswith(".test.ts") or ruta.name == "schemas.ts":
            continue
        texto = ruta.read_text(encoding="utf-8")
        limpio = re.sub(r"//.*|/\*[\s\S]*?\*/", "", texto)
        if not USA_MODELO.search(limpio):
            continue
        faltan = [nombre for nombre, pat in REGLAS if not pat.search(limpio)]
        if faltan:
            violaciones.append({"archivo": ruta.name, "faltan": faltan})
    return {"ok": not violaciones, "violaciones": violaciones}


if __name__ == "__main__":
    carpeta = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SERVICIOS
    print(json.dumps(verificar_frontera(carpeta), ensure_ascii=False, indent=2))
