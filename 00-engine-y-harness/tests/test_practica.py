"""Un test por fragmento de practica/ (lo que se escribe en el video de práctica)."""

from __future__ import annotations

import pathlib
import runpy
import sys

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from practica import agente, editar, herramientas  # noqa: E402


def test_herramientas_devuelven_diccionarios(monkeypatch) -> None:
    monkeypatch.chdir(ROOT_DIR)
    ok = herramientas.read_file("sandbox_app/catalog_filter.py", max_lines=1)
    assert ok["ok"] is True and ok["total_lines"] > 1 and "\n" not in ok["content"]
    falta = herramientas.read_file("no-existe.py")
    assert falta == {"ok": False, "codigo": "ARCHIVO_NO_ENCONTRADO", "accion_sugerida": "Lista los archivos con ls"}
    roto = herramientas.run_bash(f"{sys.executable} -c 'print(1/0)'")
    assert roto["ok"] is False and roto["exit_code"] == 1 and "ZeroDivisionError" in roto["stderr"]


def test_run_bash_pasado_de_tiempo_devuelve_datos() -> None:
    r = herramientas.run_bash("sleep 2", timeout_sec=1)
    assert r == {"ok": False, "codigo": "TIEMPO_AGOTADO",
                 "accion_sugerida": "Corre un comando más corto o sube timeout_sec"}


def test_editar_roto_se_niega(capsys) -> None:
    runpy.run_module("practica.editar_roto", run_name="__main__")
    out = capsys.readouterr().out
    assert "'codigo': 'BLOQUE_AMBIGUO'" in out and "'coincidencias': 2" in out


def test_editar_con_contexto_cambia_solo_una_funcion() -> None:
    archivo = editar.catalogo_temporal()
    viejo = 'return [i for i in items if i["cat"] == cat]'
    nuevo = 'return [i for i in items if i["cat"].lower() == cat.lower()]'
    assert editar.edit_file(archivo, "no aparece", "x")["codigo"] == "BLOQUE_NO_COINCIDE"
    assert editar.edit_file(archivo, viejo, nuevo) == {"ok": True, "replaced": 1}
    texto = archivo.read_text(encoding="utf-8")
    assert nuevo in texto and 'return len([i for i in items if i["cat"] == cat])' in texto


def test_agente_el_mensaje_crece_en_cada_turno(monkeypatch, capsys) -> None:
    monkeypatch.chdir(ROOT_DIR)
    plan = [[{"name": "read_file", "input": {"path": "sandbox_app/catalog_filter.py", "max_lines": 20}}],
            [{"name": "run_bash", "input": {"command": "echo listo"}}], []]
    motor = lambda messages: plan[sum(m["role"] == "assistant" for m in messages)]  # noqa: E731
    messages = agente.correr("tarea", motor)
    assert [m["role"] for m in messages] == ["user", "assistant", "tool", "assistant", "tool"]
    sizes = [int(line.split()[4]) for line in capsys.readouterr().out.splitlines() if line.startswith("turno")]
    assert len(sizes) == 3 and sizes[0] < sizes[1] < sizes[2]


def test_agente_gemini_usa_el_loop_del_harness(monkeypatch, capsys) -> None:
    import src.gemini_engine as ge

    def falso(model, **_):
        assert model == "gemini-3.8-flash"
        return lambda messages, tools: {"stop_reason": "end_turn", "text": "3 funciones, tests en verde"}

    monkeypatch.setattr(ge, "make_gemini_engine", falso)
    runpy.run_module("practica.agente_gemini", run_name="__main__")
    out = capsys.readouterr().out
    assert "[AGENT_FINAL] 3 funciones, tests en verde" in out and "turnos: 1" in out
