"""Reglas del harness: qué puede leer y escribir el agente en cada sesión."""
PROTEGIDO = ("juez/", "vitest.juez.config.ts")
TODAVIA_NO = PROTEGIDO + ("contrato.md",)  # en la sesión directa aún no existen


def permitido(ruta, accion, sesion):
    if accion == "leer":
        return not (sesion == "directo" and ruta.startswith(TODAVIA_NO))
    if sesion == "mapa":  # el mapa es de solo lectura
        return False
    return not ruta.startswith(PROTEGIDO)  # nadie edita el juez


def negar(ruta, accion):
    return {"ok": False, "codigo": "PERMISO_DENEGADO",
            "accion_sugerida": f"No puedes {accion} {ruta} en esta sesión"}


if __name__ == "__main__":
    juez, src = "juez/cobertura.juez.test.tsx", "src/lib/date-utils.ts"
    for sesion in ("directo", "mapa", "limpia"):
        print(f"{sesion:8} leer juez: {permitido(juez, 'leer', sesion)!s:5}  "
              f"escribir juez: {permitido(juez, 'escribir', sesion)!s:5}  "
              f"escribir src: {permitido(src, 'escribir', sesion)}")
    print(negar(juez, "escribir"))
