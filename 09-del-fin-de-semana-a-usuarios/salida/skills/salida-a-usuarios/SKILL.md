---
name: salida-a-usuarios
description: Cierra una brecha de salida a usuarios en un proyecto (secretos, dependencias, fallas del modelo, topes de gasto, registros, ruta de salud, cómo volver atrás) siguiendo Judge-First. Úsala cuando pidan dejar el proyecto listo para usuarios, cerrar comprobaciones del juez de salida o arreglar lo que falla en `salida/juez_salida`.
---

# Cerrar una brecha de salida a usuarios

Cada brecha es una comprobación que el juez de salida marca como fallida. Se trabajan una por una.

## Procedimiento por brecha

1. Lee qué comprobación falla y por qué, en `BRECHAS.md` (copia del resultado del juez). No adivines.
2. Escribe o ajusta primero una prueba que capture la brecha y verifica que falla.
3. Cambia el código lo mínimo para que la prueba pase. Una brecha, un cambio pequeño.
4. Corre el comando único de verificación del proyecto y confirma que sigue en verde.

## Convenciones de nombres que el juez busca

Las pruebas se encuentran por el texto del nombre del test, así que respétalo:

| Brecha | Texto en el nombre de la prueba |
|---|---|
| Modelo no responde a tiempo | `modelo-timeout` (en Python `modelo_timeout`) |
| Modelo responde algo roto | `modelo-respuesta-rota` (en Python `modelo_respuesta_rota`) |
| Límite de peticiones por cliente | `limite-peticiones` (en Python `limite_peticiones`) |
| Ruta de salud | `salud` |
| Registros sin datos personales | `registros-sin-datos-personales` (en Python `registros_sin_datos_personales`) |

El tope de salida del modelo va como parámetro del modelo (`maxOutputTokens` o `max_output_tokens`) en el código de producción.

## Qué no se toca

- Nada dentro de `salida/` ni `BRECHAS.md`.
- Archivos `.env`, `.env.local` o credenciales: no los leas, no los imprimas, no los edites.
- Pruebas que ya existían: puedes agregar pruebas, no debilitar ni borrar aserciones.
- No instales paquetes nuevos sin que una brecha lo exija. Si hace falta uno, usa solo paquetes que existan en el registro público y dilo en el reporte.
- No uses Git.

## Cómo volver atrás

Para la brecha del README agrega una sección «Cómo volver atrás» con el comando exacto de la versión anterior de este proyecto, en un bloque de código.

## Reporte final

Termina con un reporte corto: qué brechas cerraste, qué comandos corriste y su salida real, y qué brechas dejaste abiertas con la razón. No digas «terminado» sin la salida de los comandos.
