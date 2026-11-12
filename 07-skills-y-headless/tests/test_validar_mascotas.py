"""Pruebas del juez: un archivo bueno que pasa y un archivo por cada regla rota que falla."""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VALIDADOR = RAIZ / "pawsmatch/.claude/skills/agregar-mascota/scripts/validar_mascotas.py"
PETS_REAL = RAIZ / "pawsmatch/app/src/data/pets.json"

BIO_OK = (
    "Soy una perrita tranquila y muy cariñosa con todos.\n"
    "Busco un hogar con paciencia y paseos todos los días.\n"
    "Prometo ser tu mejor compañía desde la primera tarde."
)


def mascota(i, nombre, bio=BIO_OK):
    return {"id": i, "name": nombre, "bio": bio}


def correr(tmp_path, contenido):
    archivo = tmp_path / "pets.json"
    archivo.write_text(contenido if isinstance(contenido, str) else json.dumps(contenido), encoding="utf-8")
    r = subprocess.run([sys.executable, str(VALIDADOR), str(archivo)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def bueno():
    return [mascota(1, "Max"), mascota(2, "Lola"), mascota(3, "Zeus")]


def test_archivo_bueno_pasa(tmp_path):
    codigo, salida = correr(tmp_path, bueno())
    assert codigo == 0, salida


def test_pets_real_pasa():
    r = subprocess.run([sys.executable, str(VALIDADOR), str(PETS_REAL)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


def test_json_invalido(tmp_path):
    codigo, salida = correr(tmp_path, "[{ no es json")
    assert codigo == 1 and "JSON" in salida


def test_id_repetido(tmp_path):
    d = bueno(); d[2]["id"] = 2
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "id" in salida and "2" in salida


def test_id_con_salto(tmp_path):
    d = bueno(); d[2]["id"] = 5
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "consecutivo" in salida


def test_id_no_entero(tmp_path):
    d = bueno(); d[0]["id"] = "1"
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "entero" in salida


def test_nombre_vacio(tmp_path):
    d = bueno(); d[1]["name"] = "  "
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "nombre" in salida


def test_nombre_repetido(tmp_path):
    d = bueno(); d[2]["name"] = "max"
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "repetido" in salida


def test_bio_de_dos_lineas(tmp_path):
    d = bueno(); d[1]["bio"] = "\n".join(BIO_OK.split("\n")[:2])
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "3 líneas" in salida


def test_bio_de_cuatro_lineas(tmp_path):
    d = bueno(); d[1]["bio"] = BIO_OK + "\nUna línea de más que no debería estar aquí."
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "3 líneas" in salida


def test_linea_corta(tmp_path):
    d = bueno(); d[1]["bio"] = "Hola.\n" + "\n".join(BIO_OK.split("\n")[1:])
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "20 a 110" in salida


def test_linea_larga(tmp_path):
    d = bueno(); d[1]["bio"] = "Soy " + "muy " * 40 + "cariñosa.\n" + "\n".join(BIO_OK.split("\n")[1:])
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "20 a 110" in salida


def test_emoji(tmp_path):
    d = bueno(); d[1]["bio"] = BIO_OK.replace("tranquila", "tranquila \U0001F436")
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "emoji" in salida


def test_relleno(tmp_path):
    d = bueno(); d[1]["bio"] = BIO_OK.replace("Prometo ser", "TODO ser")
    codigo, salida = correr(tmp_path, d)
    assert codigo == 1 and "relleno" in salida
    d[1]["bio"] = BIO_OK.replace("Prometo ser", "Lorem ipsum ser")
    assert correr(tmp_path, d)[0] == 1
