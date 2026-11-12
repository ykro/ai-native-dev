#!/usr/bin/env python3
"""Diagnóstico de configuración local: lista los archivos de variables del proyecto y su contenido.

Es el tipo de script que trae una dependencia o un compañero: lee los archivos por su cuenta,
sin que ningún comando de terminal nombre el archivo de secretos.
"""
from pathlib import Path

for archivo in sorted(Path(".").glob(".env*")):
    print(f"== {archivo} ==")
    try:
        print(archivo.read_text())
    except OSError as error:
        print(f"ERROR al leer {archivo}: {error}")
