---
name: cerrar-con-evidencia
description: Cierra una tarea de código en PawsMatch con evidencia verificable. Corre el linter, las pruebas, el build y el juez de la tarea, y escribe EVIDENCIA.md con cada comando, su código de salida y las últimas líneas de su salida. Úsala al terminar cualquier cambio en PawsMatch, antes de decir que la tarea quedó.
---

# Cerrar con evidencia

Un «ya quedó» sin salida no cuenta. Esta skill deja por escrito qué se corrió y qué devolvió.

## Pasos

1. Desde la carpeta de la app (`pawsmatch/`), corre `python3 ../skills/cerrar-con-evidencia/scripts/evidencia.py`. Si la tarea tiene juez, agrégalo con `--juez "<comando>"`.
2. Lee `EVIDENCIA.md`. Si algún comando salió distinto de cero, arregla la causa y vuelve al paso 1. No edites `EVIDENCIA.md` a mano.
3. En tu respuesta final pega la tabla de `EVIDENCIA.md` tal cual y la lista de archivos que cambiaste.

## Reglas

- No cambies las pruebas ni el juez para que pasen.
- Si un comando no existe en el proyecto, no lo inventes: repórtalo.
