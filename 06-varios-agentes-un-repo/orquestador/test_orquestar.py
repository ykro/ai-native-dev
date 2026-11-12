"""Pruebas del orquestador. Usan repos de git desechables; no llaman a ningún modelo."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import orquestar as o


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, text=True,
                          capture_output=True).stdout


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "user.email", "t@example.com")
    _git(r, "config", "user.name", "t")
    (r / "schemas.ts").write_text("export const dias = 3;\nexport const moneda = 'USD';\n")
    (r / "panel.tsx").write_text("export const Panel = () => null;\n")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "base")
    _git(r, "tag", "reparto")
    return r


def _rama(repo: Path, nombre: str, archivo: str, texto: str) -> None:
    _git(repo, "checkout", "-q", "-b", nombre, "reparto")
    (repo / archivo).write_text(texto)
    _git(repo, "commit", "-qam", nombre)
    _git(repo, "checkout", "-q", "main")


def test_dos_ramas_que_tocan_la_misma_linea_chocan(repo: Path, tmp_path: Path) -> None:
    _rama(repo, "tarea/duracion", "schemas.ts", "export const dias = 7;\nexport const moneda = 'USD';\n")
    _rama(repo, "tarea/presupuesto", "schemas.ts", "export const dias = 3; // con costo\nexport const moneda = 'USD';\n")
    f = o.probar_fusion(repo, "reparto", ["tarea/duracion", "tarea/presupuesto"], tmp_path / "wt")
    assert not f.limpia
    assert f.archivos_en_conflicto == ["schemas.ts"]
    assert f.bloques == 1
    assert f.rama_que_choco == "tarea/presupuesto"


def test_ramas_en_archivos_distintos_entran_limpias_y_corren_los_jueces(repo: Path, tmp_path: Path) -> None:
    _rama(repo, "tarea/duracion", "schemas.ts", "export const dias = 7;\nexport const moneda = 'USD';\n")
    _rama(repo, "tarea/exportar", "panel.tsx", "export const Panel = () => 'descargar';\n")
    vistos: list[str] = []
    f = o.probar_fusion(repo, "reparto", ["tarea/duracion", "tarea/exportar"], tmp_path / "wt",
                        despues=lambda wt: vistos.append((wt / "panel.tsx").read_text()))
    assert f.limpia and f.bloques == 0
    assert vistos == ["export const Panel = () => 'descargar';\n"]


def test_probar_fusion_no_cambia_el_repo(repo: Path, tmp_path: Path) -> None:
    _rama(repo, "tarea/a", "schemas.ts", "x\n")
    antes = _git(repo, "rev-parse", "HEAD")
    o.probar_fusion(repo, "reparto", ["tarea/a"], tmp_path / "wt")
    assert _git(repo, "rev-parse", "HEAD") == antes
    assert "wt" not in _git(repo, "worktree", "list")


def test_matriz_por_pares(repo: Path, tmp_path: Path) -> None:
    _rama(repo, "tarea/a", "schemas.ts", "export const dias = 7;\nexport const moneda = 'USD';\n")
    _rama(repo, "tarea/b", "schemas.ts", "export const dias = 2;\nexport const moneda = 'USD';\n")
    _rama(repo, "tarea/c", "panel.tsx", "c\n")
    pares = o.matriz_por_pares(repo, "reparto", ["tarea/a", "tarea/b", "tarea/c"], tmp_path)
    limpias = {tuple(p["ramas"]): p["limpia"] for p in pares}
    assert limpias == {("tarea/a", "tarea/b"): False, ("tarea/a", "tarea/c"): True,
                       ("tarea/b", "tarea/c"): True}


def test_contar_bloques_en_conflicto() -> None:
    texto = "<<<<<<< HEAD\na\n=======\nb\n>>>>>>> x\nok\n<<<<<<< HEAD\nc\n=======\nd\n>>>>>>> x\n"
    assert o.contar_bloques_en_conflicto(texto) == 2


def test_solapes_declarados() -> None:
    tareas = [{"id": "a", "archivos": ["src/schemas.ts", "src/a.ts"]},
              {"id": "b", "archivos": ["src/schemas.ts"]},
              {"id": "c", "archivos": ["src/c.ts"]}]
    assert o.solapes_declarados(tareas) == [{"archivo": "src/schemas.ts", "tareas": ["a", "b"]}]


def test_tocados_fuera_de_lo_asignado() -> None:
    tarea = {"id": "a", "archivos": ["src/a.ts", "travelens/src/b.ts"]}
    tocados = ["travelens/src/a.ts", "travelens/src/b.ts", "travelens/src/otro.ts"]
    assert o.tocados_fuera_de_lo_asignado(tarea, tocados) == ["travelens/src/otro.ts"]


def test_leer_reporte_vitest() -> None:
    salida = "ruido de npx\n" + json.dumps({"numTotalTests": 5, "numPassedTests": 4, "success": False})
    assert o.leer_reporte_vitest(salida) == {"aprobadas": 4, "total": 5, "ok": False}
    verde = json.dumps({"numTotalTests": 3, "numPassedTests": 3, "success": True})
    assert o.leer_reporte_vitest(verde)["ok"] is True
    assert o.leer_reporte_vitest("sin json")["ok"] is False


def test_un_juez_vacio_no_cuenta_como_verde() -> None:
    vacio = json.dumps({"numTotalTests": 0, "numPassedTests": 0, "success": True})
    assert o.leer_reporte_vitest(vacio)["ok"] is False


def test_regresiones() -> None:
    en_su_rama = {"juez/a.juez.test.ts": True, "juez/b.juez.test.ts": True, "juez/c.juez.test.ts": False}
    juntos = {"juez/a.juez.test.ts": {"ok": True}, "juez/b.juez.test.ts": {"ok": False},
              "juez/c.juez.test.ts": {"ok": False}}
    assert o.regresiones(en_su_rama, juntos) == ["juez/b.juez.test.ts"]


def test_comando_del_constructor_niega_el_juez_y_git() -> None:
    cmd = o.comando_claude("hola", o.BUILDER_TOOLS, o.BUILDER_DENIED)
    assert cmd[:3] == ["claude", "-p", "hola"]
    negadas = cmd[cmd.index("--disallowedTools") + 1:]
    assert "Edit(juez/**)" in negadas and "Bash(git *)" in negadas
    assert "--setting-sources" in cmd and cmd[cmd.index("--setting-sources") + 1] == "project"


def test_el_integrador_no_puede_mover_el_juez_ni_reescribir_historia() -> None:
    assert "Edit(travelens/juez/**)" in o.INTEGRATOR_DENIED
    assert "Bash(git reset*)" in o.INTEGRATOR_DENIED
    assert "Bash(git push*)" in o.INTEGRATOR_DENIED


def test_sanear_linea_quita_rutas_y_campos_de_la_maquina() -> None:
    init = {"type": "system", "subtype": "init", "cwd": "/Users/ana/tmp/t06/travelens-06",
            "plugins": ["x"], "mcp_servers": [], "model": "claude-sonnet"}
    salida = json.loads(o.sanear_linea(json.dumps(init), [("/Users/ana/tmp/t06/travelens-06", "~/travelens-06")]))
    assert salida == {"type": "system", "subtype": "init", "cwd": "~/travelens-06", "model": "claude-sonnet"}


def test_prompt_constructor_usa_rutas_relativas_a_la_app() -> None:
    tarea = {"id": "duracion", "titulo": "Duración", "juez": "travelens/juez/duracion.juez.test.ts",
             "archivos": ["travelens/src/services/schemas.ts"]}
    texto = o.prompt_constructor(tarea)
    assert "juez/duracion.juez.test.ts" in texto and "travelens/juez" not in texto
    assert "src/services/schemas.ts" in texto


def test_olas_respetan_dependencias() -> None:
    tareas = [{"id": "plan", "depende_de": ["presupuesto"]}, {"id": "presupuesto", "depende_de": []},
              {"id": "ui", "depende_de": ["descarga"]}, {"id": "descarga", "depende_de": []}]
    assert [[t["id"] for t in ola] for ola in o.olas(tareas)] == [["presupuesto", "descarga"], ["plan", "ui"]]


def test_olas_detectan_dependencias_circulares() -> None:
    with pytest.raises(ValueError):
        o.olas([{"id": "a", "depende_de": ["b"]}, {"id": "b", "depende_de": ["a"]}])


def test_desde_de_usa_la_base_de_las_dependencias():
    assert o.desde_de({"id": "a", "depende_de": []}) == "reparto"
    assert o.desde_de({"id": "ui", "depende_de": ["api"]}) == "base/ui"
