"""Un test por fragmento de practica/ y por cada «prueba esto» del video."""
from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from practica import (  # noqa: E402
    auditar_comandos,
    comando_colgado_roto,
    comparar_corridas,
    compuerta_frontera,
    verificar_agents_md,
)


def test_comando_colgado_agota_timeout(monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    r = comando_colgado_roto.correr_comando(comando_colgado_roto.WATCH_DEMO, timeout=0.4)
    assert r["ok"] is False
    assert r["codigo"] == "TIMEOUT"
    assert "WATCH" in r["salida"]


def test_auditar_comandos_antes_y_despues(monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    antes = auditar_comandos.auditar_scripts("medicion/antes/package.antes.json")
    assert antes["ok"] is False
    assert antes["faltan"] == ["typecheck", "test:run"]

    despues = auditar_comandos.auditar_scripts("travelens/package.json")
    assert despues["ok"] is True
    assert despues["faltan"] == []

    corrida = auditar_comandos.ejecutar_verificacion("travelens")
    assert [c["comando"] for c in corrida] == ["typecheck", "lint", "test:run"]
    assert all(c["ok"] is True and c["exit"] == 0 for c in corrida)


def test_prueba_esto_script_inexistente(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    corrida = auditar_comandos.ejecutar_verificacion("travelens", ("typecheck", "verify:all"))
    assert corrida[0]["ok"] is True
    assert corrida[1] == {"comando": "verify:all", "ok": False, "codigo": "SCRIPT_INEXISTENTE"}

    guia = tmp_path / "AGENTS.md"
    guia.write_text((ROOT / "travelens" / "AGENTS.md").read_text(encoding="utf-8") + "\n`npm run verify:all`\n",
                    encoding="utf-8")
    audit = verificar_agents_md.auditar_guia(guia, app=str(ROOT / "travelens"))
    assert audit["ok"] is False
    assert audit["comandos_rotos"] == ["verify:all"]


def test_verificar_agents_md_inflado_contra_quirurgico(monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    inflado = verificar_agents_md.auditar_guia(
        "medicion/antes/CLAUDE.inflado.md", "travelens", "medicion/antes/package.antes.json"
    )
    assert inflado["lineas"] == 260
    assert inflado["comandos_rotos"] == ["verify:all"]
    assert inflado["ok"] is False

    quirurgico = verificar_agents_md.auditar_guia("travelens/AGENTS.md", "travelens")
    assert quirurgico["lineas"] == 31
    assert quirurgico["comandos_rotos"] == []
    assert quirurgico["rutas_rotas"] == []
    assert quirurgico["ok"] is True

    claude_import = verificar_agents_md.auditar_guia("travelens/CLAUDE.md", "travelens")
    assert claude_import["importa"] == "AGENTS.md"
    assert claude_import["lineas"] == 31
    assert claude_import["ok"] is True


def test_prueba_esto_ruta_borrada_en_agents_md(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    copia = tmp_path / "AGENTS.md"
    base = (ROOT / "travelens" / "AGENTS.md").read_text(encoding="utf-8")
    copia.write_text(base + "\n- Cliente legado en `src/services/viejo.ts`.\n", encoding="utf-8")
    r = verificar_agents_md.auditar_guia(copia, app=str(ROOT / "travelens"))
    assert r["ok"] is False
    assert r["rutas_rotas"] == ["src/services/viejo.ts"]


def test_compuerta_frontera_atrapa_desvio_y_aprueba_zod(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    actual = compuerta_frontera.verificar_frontera()
    assert actual == {
        "ok": False,
        "violaciones": [
            {"archivo": "gemini.ts", "faltan": ["importar schemas", "ejecutar Schema.parse/safeParse"]}
        ],
    }

    # Un import solo de tipos no engaña a la compuerta
    solo_tipo = tmp_path / "solo_tipo"
    solo_tipo.mkdir()
    (solo_tipo / "gemini.ts").write_text(
        'import { GoogleGenAI } from "@google/genai";\n'
        'import type { TravelPlan } from "./schemas";\n',
        encoding="utf-8",
    )
    assert compuerta_frontera.verificar_frontera(solo_tipo)["ok"] is False

    # «Prueba esto»: al validar con ItineraryResponseSchema.safeParse, pasan la compuerta y el juez
    copia = tmp_path / "travelens"
    shutil.copytree(ROOT / "travelens", copia, ignore=shutil.ignore_patterns("node_modules", ".next"))
    os.symlink(ROOT / "travelens" / "node_modules", copia / "node_modules")
    gemini_path = copia / "src" / "services" / "gemini.ts"
    codigo = gemini_path.read_text(encoding="utf-8")
    codigo = 'import { ItineraryResponseSchema, type TravelPlan } from "./schemas";\n' + codigo
    codigo = codigo.replace("export interface TravelPlan {", "interface LegacyTravelPlan {")
    codigo = codigo.replace(
        "return isTravelPlan(parsed) ? parsed : null;",
        "const check = ItineraryResponseSchema.safeParse(parsed);\n"
        "            return check.success ? check.data : null;",
    )
    gemini_path.write_text(codigo, encoding="utf-8")

    assert compuerta_frontera.verificar_frontera(copia / "src" / "services") == {"ok": True, "violaciones": []}
    juez = subprocess.run(["npm", "run", "juez"], cwd=copia, capture_output=True, text=True)
    assert juez.returncode == 0 and "7 passed" in juez.stdout


def test_comparar_corridas_y_prueba_esto_fallos(monkeypatch) -> None:
    monkeypatch.chdir(ROOT)
    antes = comparar_corridas.resumir_traza("medicion/logs/01-antes.jsonl")
    despues = comparar_corridas.resumir_traza("medicion/logs/02-despues.jsonl")

    assert antes["pasos"] == 23
    assert len(antes["fallidos"]) == 4
    assert antes["entrada"] == 408_027
    assert antes["salida"] == 4_037
    assert antes["segundos"] == 140.0

    assert despues["pasos"] == 10
    assert despues["fallidos"] == []
    assert despues["entrada"] == 201_000
    assert despues["salida"] == 1_910
    assert despues["segundos"] == 27.0

    out = subprocess.run(
        [sys.executable, "-m", "practica.comparar_corridas", "--fallos"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    for cmd in ("npm run verify:all", "npm test", "npm run build", "npx tsc --noEmit"):
        assert cmd in out
