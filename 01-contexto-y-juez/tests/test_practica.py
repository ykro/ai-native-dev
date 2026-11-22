"""Un test por fragmento de practica/ (lo que se escribe en el video de práctica).

Los tests corren sobre una copia de rent-my-gear en una carpeta temporal (con node_modules enlazado),
así que nunca ensucian la app del repo. Necesitan `make instalar` antes."""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from practica import contexto, harness, juez, motor, permisos, sesion  # noqa: E402


@pytest.fixture()
def app(tmp_path, monkeypatch):
    """Copia de rent-my-gear en su estado inicial (juez en rojo); las tools y el juez trabajan ahí."""
    copia = tmp_path / "rent-my-gear"
    shutil.copytree(ROOT / "rent-my-gear", copia, ignore=shutil.ignore_patterns("node_modules", ".next"))
    os.symlink(ROOT / "rent-my-gear" / "node_modules", copia / "node_modules")
    # src/ como está en el último commit, aunque la app del repo tenga cambios de una sesión a medias
    shutil.rmtree(copia / "src")
    archivo = subprocess.run(["git", "archive", "HEAD", "rent-my-gear/src"], cwd=ROOT, capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", str(tmp_path)], input=archivo, check=True)
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(juez, "APP", str(copia))
    monkeypatch.setattr(harness, "RAIZ", copia)
    return copia


def test_juez_empieza_en_rojo(app) -> None:
    v = juez.correr_juez()
    assert v["ok"] is False and v["pasan"] == 0 and v["fallan"] == 5
    assert v["fallas"][0] == "fotografía y video paga 20 % sobre el subtotal -> expected undefined to be 450"


def test_juez_en_verde_con_la_entrega(app) -> None:
    subprocess.run(["patch", "-s", "-p1", "-i", str(ROOT / "entrega" / "cobertura.patch")], cwd=app, check=True)
    v = juez.correr_juez()
    assert v == {"ok": True, "pasan": 5, "fallan": 0, "fallas": []}


def test_permisos_protegen_el_juez() -> None:
    assert permisos.permitido("src/lib/date-utils.ts", "escribir", "limpia") is True
    assert permisos.permitido("juez/cobertura.juez.test.tsx", "escribir", "limpia") is False
    assert permisos.permitido("src/lib/date-utils.ts", "escribir", "mapa") is False
    assert permisos.permitido("juez/cobertura.juez.test.tsx", "leer", "directo") is False
    assert permisos.permitido("juez/cobertura.juez.test.tsx", "leer", "mapa") is True
    assert permisos.negar("juez/x", "escribir")["codigo"] == "PERMISO_DENEGADO"
    out = subprocess.run([sys.executable, "-m", "practica.permisos"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    assert "limpia   leer juez: True   escribir juez: False  escribir src: True" in out
    assert "directo  leer juez: False  escribir juez: False  escribir src: True" in out


def test_harness_aplica_los_permisos(app) -> None:
    assert harness.editar("juez/cobertura.juez.test.tsx", "Juez", "X", sesion="limpia")["codigo"] == "PERMISO_DENEGADO"
    assert harness.leer("juez/cobertura.juez.test.tsx", sesion="directo")["codigo"] == "PERMISO_DENEGADO"
    assert harness.correr("rm -rf src", sesion="limpia")["codigo"] == "PERMISO_DENEGADO"
    assert harness.correr("npm run juez", sesion="directo")["codigo"] == "PERMISO_DENEGADO"
    assert "juez/cobertura.juez.test.tsx" not in harness.listar(".", sesion="directo")["archivos"]


def _repetir(ses: str) -> list[dict]:
    traza = ROOT / "sesiones" / f"{ses}.jsonl"
    return [json.loads(l) for l in traza.read_text(encoding="utf-8").splitlines()]


def test_sesion_limpia_grabada_deja_el_juez_en_verde(app, capsys) -> None:
    engine = motor.grabado(str(ROOT / "sesiones" / "limpia.jsonl"), "limpia")
    harness.lanzar("limpia", (ROOT / "prompts" / "03-iterar.txt").read_text(encoding="utf-8"), engine)
    out = capsys.readouterr().out
    assert "[final]" in out and "MAX_TURNOS" not in out
    assert juez.correr_juez()["ok"] is True


def test_sesion_directo_grabada_repite_la_corrida(app, capsys) -> None:
    pasos = _repetir("directo")
    sesion.directo(motor.grabado(str(ROOT / "sesiones" / "directo.jsonl"), "directo"), None)
    out = capsys.readouterr().out
    assert out.count("[turno") == len(pasos)
    assert out.count("[juez] pasan 0 de 5") == 3
    assert "expected 100.05000000000001 to be 100.05" in out


def test_contexto_dibuja_cada_turno(capsys) -> None:
    contexto.barras(str(ROOT / "sesiones" / "directo.jsonl"))
    out = capsys.readouterr().out.splitlines()
    pasos = _repetir("directo")
    assert out[0].startswith(f"turno  1  {pasos[0]['input_tokens']:6}")
    assert out[-1] == f"{len(pasos)} turnos, {sum(p['input_tokens'] for p in pasos)} tokens de entrada en total"


def test_sin_credenciales_sugiere_grabada(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(tmp_path / "no-existe.json"))
    with pytest.raises(SystemExit) as exc:
        motor.gemini()
    assert "--grabada" in str(exc.value)
