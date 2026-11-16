"""edit_file: reemplazo exacto. Si el texto no aparece una sola vez, se niega."""
import pathlib
import tempfile


def edit_file(path, old_str, new_str):
    p = pathlib.Path(path)
    texto = p.read_text(encoding="utf-8")
    n = texto.count(old_str)
    if n == 0:
        return {"ok": False, "codigo": "BLOQUE_NO_COINCIDE",
                "accion_sugerida": "Vuelve a leer el archivo"}
    if n > 1:
        return {"ok": False, "codigo": "BLOQUE_AMBIGUO", "coincidencias": n,
                "accion_sugerida": "Agrega líneas vecinas a old_str"}
    p.write_text(texto.replace(old_str, new_str), encoding="utf-8")
    return {"ok": True, "replaced": 1}


CATALOGO = '''def activos(items, cat):
    return [i for i in items if i["cat"] == cat]

def contar(items, cat):
    return len([i for i in items if i["cat"] == cat])
'''


def catalogo_temporal():
    archivo = pathlib.Path(tempfile.mkdtemp()) / "catalogo.py"
    archivo.write_text(CATALOGO, encoding="utf-8")
    return archivo


if __name__ == "__main__":
    archivo = catalogo_temporal()
    print(edit_file(archivo,
                    'return [i for i in items if i["cat"] == cat]',
                    'return [i for i in items if i["cat"].lower() == cat.lower()]'))
    print(archivo.read_text(encoding="utf-8"))
