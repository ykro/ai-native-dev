"""Orquestador del tema 06 · varios agentes sobre el mismo repo (TraveLens).

Un agente reparte el pedido en tareas, cada una con su juez. Cada tarea se construye
en su propio git worktree con un agente en modo headless. Después se mide qué pasa al
juntar las ramas (conflictos de texto y regresiones de los jueces) y un integrador con
contexto limpio fusiona y corre todos los jueces.

Subcomandos:
    preparar   crea el repo de trabajo (copia de travelens + pedido) con un commit base
    repartir   corre el agente que reparte (prompts/01-repartir.txt)
    congelar   hace commit del reparto y de los jueces revisados
    construir  un worktree y un agente por tarea, en paralelo
    medir      fusiona por pares y en secuencia, cuenta conflictos y corre los jueces
    integrar   corre el integrador en un worktree limpio (prompts/03-integrar.txt)
    exportar   copia parches, reparto, jueces, medición y logs saneados al repo público

Los agentes se lanzan con Claude Code (`claude -p ... --output-format stream-json`).
Nada de este archivo llama a un modelo por su cuenta.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TEMA = AQUI.parent
APP = "travelens"
JUEZ_BASE = "juez/ai-plan.juez.test.ts"

BUILDER_TOOLS = [
    "Read", "Glob", "Grep", "Edit", "Write",
    "Bash(npm run check)", "Bash(npm run typecheck)", "Bash(npm run lint)",
    "Bash(npm run test:run)", "Bash(npx vitest run *)", "Bash(npm run juez)",
]
BUILDER_DENIED = ["Edit(juez/**)", "Write(juez/**)", "Bash(git *)", "Bash(npm install *)"]
SPLITTER_TOOLS = ["Read", "Glob", "Grep", "Write(reparto/**)", "Write(travelens/juez/**)",
                  "Edit(reparto/**)", "Edit(travelens/juez/**)", "Bash(npx vitest run *)"]
INTEGRATOR_TOOLS = [
    "Read", "Glob", "Grep", "Edit", "Write",
    "Bash(git merge *)", "Bash(git status*)", "Bash(git diff*)", "Bash(git log*)",
    "Bash(git add *)", "Bash(git commit *)", "Bash(git branch*)",
    "Bash(npm run check)", "Bash(npm run typecheck)", "Bash(npm run lint)",
    "Bash(npm run test:run)", "Bash(npx vitest run *)", "Bash(npm run juez)",
]
INTEGRATOR_DENIED = ["Edit(travelens/juez/**)", "Write(travelens/juez/**)",
                     "Bash(git push*)", "Bash(git reset*)", "Bash(git checkout*)"]


# --------------------------------------------------------------------------- git

def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=check, text=True,
                          capture_output=True)


def ramas_de_tareas(tareas: list[dict]) -> list[str]:
    return [f"tarea/{t['id']}" for t in tareas]


def contar_bloques_en_conflicto(texto: str) -> int:
    """Cuenta los bloques <<<<<<< que deja git en un archivo en conflicto."""
    return sum(1 for linea in texto.splitlines() if linea.startswith("<<<<<<< "))


@dataclass
class Fusion:
    ramas: list[str]
    limpia: bool
    archivos_en_conflicto: list[str] = field(default_factory=list)
    bloques: int = 0
    rama_que_choco: str | None = None

    def a_dict(self) -> dict:
        return {"ramas": self.ramas, "limpia": self.limpia,
                "archivos_en_conflicto": self.archivos_en_conflicto,
                "bloques": self.bloques, "rama_que_choco": self.rama_que_choco}


def probar_fusion(repo: Path, base: str, ramas: list[str], destino: Path,
                  despues=None) -> Fusion:
    """Fusiona `ramas` en orden sobre `base` en un worktree desechable.

    Se detiene en la primera rama que choca y cuenta archivos y bloques en conflicto.
    Si todas entran limpias y se pasa `despues`, lo llama con el worktree antes de borrarlo
    (ahí se corren los jueces). El repo original nunca cambia.
    """
    if destino.exists():
        shutil.rmtree(destino)
    git(repo, "worktree", "add", "--detach", str(destino), base)
    try:
        git(destino, "config", "user.email", "orquestador@example.com")
        git(destino, "config", "user.name", "orquestador")
        for rama in ramas:
            r = git(destino, "merge", "--no-ff", "--no-edit", rama, check=False)
            if r.returncode != 0:
                archivos = git(destino, "diff", "--name-only", "--diff-filter=U").stdout.split()
                bloques = sum(contar_bloques_en_conflicto((destino / a).read_text(errors="replace"))
                              for a in archivos if (destino / a).exists())
                git(destino, "merge", "--abort", check=False)
                return Fusion(ramas, False, archivos, bloques, rama)
        if despues is not None:
            despues(destino)
        return Fusion(ramas, True)
    finally:
        git(repo, "worktree", "remove", "--force", str(destino), check=False)


def matriz_por_pares(repo: Path, base: str, ramas: list[str], tmp: Path) -> list[dict]:
    salida = []
    for i, a in enumerate(ramas):
        for b in ramas[i + 1:]:
            f = probar_fusion(repo, base, [a, b], tmp / "par")
            salida.append(f.a_dict())
    return salida


def solapes_declarados(tareas: list[dict]) -> list[dict]:
    """Archivos que el reparto le asignó a más de una tarea (debería ser vacío)."""
    duenos: dict[str, list[str]] = {}
    for t in tareas:
        for a in t.get("archivos", []):
            duenos.setdefault(a, []).append(t["id"])
    return [{"archivo": a, "tareas": ids} for a, ids in sorted(duenos.items()) if len(ids) > 1]


def desde_de(tarea: dict) -> str:
    """Punto de partida de la rama de una tarea: `base/<id>` si dependía de otras, si no `reparto`."""
    return f"base/{tarea['id']}" if tarea.get("depende_de") else "reparto"


def archivos_tocados(repo: Path, base: str, rama: str) -> list[str]:
    return git(repo, "diff", "--name-only", f"{base}...{rama}").stdout.split()


def tocados_fuera_de_lo_asignado(tarea: dict, tocados: list[str]) -> list[str]:
    asignados = {a if a.startswith(f"{APP}/") else f"{APP}/{a}" for a in tarea.get("archivos", [])}
    return sorted(a for a in tocados if a not in asignados)


# ------------------------------------------------------------------------ jueces

def leer_reporte_vitest(texto: str) -> dict:
    """Extrae aprobadas y totales del reporte JSON de Vitest (--reporter=json)."""
    inicio = texto.find("{")
    if inicio < 0:
        return {"aprobadas": 0, "total": 0, "ok": False}
    datos = json.loads(texto[inicio:])
    total = datos.get("numTotalTests", 0)
    aprobadas = datos.get("numPassedTests", 0)
    ok = bool(datos.get("success")) and total > 0 and aprobadas == total
    return {"aprobadas": aprobadas, "total": total, "ok": ok}


def correr_juez(app: Path, archivo: str) -> dict:
    """Corre un juez con el reporte JSON de Vitest escrito fuera del repo."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        salida = Path(tmp) / "juez.json"
        subprocess.run(["npx", "vitest", "run", "--config", "vitest.juez.config.ts", archivo,
                        "--reporter=json", f"--outputFile={salida}"],
                       cwd=app, text=True, capture_output=True)
        if not salida.exists():
            return {"aprobadas": 0, "total": 0, "ok": False}
        try:
            return leer_reporte_vitest(salida.read_text())
        except json.JSONDecodeError:
            return {"aprobadas": 0, "total": 0, "ok": False}


def correr_check(app: Path) -> bool:
    return subprocess.run(["npm", "run", "check"], cwd=app, capture_output=True).returncode == 0


def jueces_de(tareas: list[dict]) -> list[str]:
    return [JUEZ_BASE] + [t["juez"].removeprefix(f"{APP}/") for t in tareas]


def regresiones(en_su_rama: dict[str, bool], juntos: dict[str, dict]) -> list[str]:
    """Jueces que pasaban en la rama de su tarea y fallan con las ramas juntas."""
    return sorted(j for j, ok in en_su_rama.items() if ok and not juntos.get(j, {}).get("ok"))


# ------------------------------------------------------------------------ agentes

MAX_TURNOS = 40
PRESUPUESTO_USD = "6"
# Ningún agente de la demo lee credenciales ni configuración personal de quien graba.
NEGAR_SECRETOS = ["Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.config/**)", "Read(~/.claude/**)",
                  "Read(~/.gnupg/**)", "Read(**/.env)", "Read(**/.env.*)"]


def comando_claude(prompt: str, permitidas: list[str], negadas: list[str],
                   modelo: str = "sonnet", max_turnos: int = MAX_TURNOS) -> list[str]:
    negadas = [*negadas, *NEGAR_SECRETOS]
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--model", modelo, "--permission-mode", "acceptEdits",
           "--max-turns", str(max_turnos), "--max-budget-usd", PRESUPUESTO_USD,
           "--setting-sources", "project", "--strict-mcp-config",
           "--allowedTools", *permitidas]
    if negadas:
        cmd += ["--disallowedTools", *negadas]
    return cmd


def correr_agente(cmd: list[str], cwd: Path, log: Path) -> dict:
    log.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with log.open("w") as fh:
        r = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.PIPE, text=True)
    return {"log": log.name, "segundos": round(time.time() - t0, 1), "salida": r.returncode}


def prompt_constructor(tarea: dict) -> str:
    plantilla = (TEMA / "prompts" / "02-construir.txt").read_text()
    sin_app = [a.removeprefix(f"{APP}/") for a in tarea["archivos"]]
    return plantilla.format(id=tarea["id"], titulo=tarea["titulo"],
                            juez=tarea["juez"].removeprefix(f"{APP}/"),
                            archivos=", ".join(sin_app))


# --------------------------------------------------------------------- saneado

CAMPOS_INIT_FUERA = ("mcp_servers", "slash_commands", "agents", "skills", "plugins",
                     "apiKeySource", "output_style", "memory_paths", "uuid", "session_id")


def sanear_linea(linea: str, reemplazos: list[tuple[str, str]]) -> str:
    for viejo, nuevo in reemplazos:
        linea = linea.replace(viejo, nuevo)
    try:
        ev = json.loads(linea)
    except json.JSONDecodeError:
        return linea
    if ev.get("type") == "system" and ev.get("subtype") == "init":
        for campo in CAMPOS_INIT_FUERA:
            ev.pop(campo, None)
    return json.dumps(ev, ensure_ascii=False)


def sanear_log(origen: Path, destino: Path, reemplazos: list[tuple[str, str]]) -> None:
    lineas = [sanear_linea(l, reemplazos) for l in origen.read_text().splitlines() if l.strip()]
    destino.write_text("\n".join(lineas) + "\n")


def reemplazos_para(trabajo: Path) -> list[tuple[str, str]]:
    casa = str(Path.home())
    pares = [(str(trabajo.resolve()), "~/travelens-06"), (str(trabajo), "~/travelens-06")]
    if str(trabajo.resolve()).startswith("/private"):
        pares.append((str(trabajo.resolve()).removeprefix("/private"), "~/travelens-06"))
    pares += [(str(trabajo.parent.resolve()), "~"), (casa, "~"), (Path.home().name, "dev")]
    return pares


# ------------------------------------------------------------------- subcomandos

def preparar(trabajo: Path, node_modules: Path) -> None:
    if trabajo.exists():
        sys.exit(f"{trabajo} ya existe")
    trabajo.mkdir(parents=True)
    shutil.copytree(TEMA / APP, trabajo / APP,
                    ignore=shutil.ignore_patterns("node_modules", ".next", "*.tsbuildinfo"))
    shutil.copy(TEMA / "pedido.md", trabajo / "pedido.md")
    (trabajo / "reparto").mkdir()
    (trabajo / ".gitignore").write_text("node_modules\n.next\n*.tsbuildinfo\n")
    os.symlink(node_modules.resolve(), trabajo / APP / "node_modules")
    git(trabajo, "init", "-q", "-b", "main")
    git(trabajo, "config", "user.email", "orquestador@example.com")
    git(trabajo, "config", "user.name", "orquestador")
    git(trabajo, "add", "-A")
    git(trabajo, "commit", "-qm", "base")


def repartir(trabajo: Path) -> dict:
    prompt = (TEMA / "prompts" / "01-repartir.txt").read_text()
    cmd = comando_claude(prompt, SPLITTER_TOOLS, ["Edit(travelens/src/**)", "Write(travelens/src/**)"])
    return correr_agente(cmd, trabajo, trabajo / "logs" / "01-repartir.jsonl")


def congelar(trabajo: Path) -> None:
    git(trabajo, "add", "reparto", f"{APP}/juez")
    git(trabajo, "commit", "-qm", "reparto y jueces revisados")
    git(trabajo, "tag", "-f", "reparto")


def cargar_tareas(trabajo: Path) -> list[dict]:
    datos = json.loads((trabajo / "reparto" / "tareas.json").read_text())
    return datos["tareas"] if isinstance(datos, dict) else datos


def olas(tareas: list[dict]) -> list[list[dict]]:
    """Agrupa las tareas en olas: cada una arranca cuando terminaron sus dependencias."""
    pendientes = {t["id"]: t for t in tareas}
    hechas: set[str] = set()
    salida: list[list[dict]] = []
    while pendientes:
        ola = [t for t in pendientes.values() if set(t.get("depende_de", [])) <= hechas]
        if not ola:
            raise ValueError(f"dependencias circulares o inexistentes: {sorted(pendientes)}")
        salida.append(ola)
        for t in ola:
            hechas.add(t["id"])
            del pendientes[t["id"]]
    return salida


def punto_de_partida(trabajo: Path, tarea: dict) -> tuple[str, dict | None]:
    """La rama de una tarea arranca en `reparto` más las ramas de sus dependencias.

    Si tiene dependencias, el orquestador las fusiona en una rama `base/<id>` y mide si chocan.
    """
    deps = tarea.get("depende_de", [])
    if not deps:
        return "reparto", None
    base = f"base/{tarea['id']}"
    git(trabajo, "branch", "-f", base, "reparto")
    wt = trabajo.parent / f"wt-base-{tarea['id']}"
    git(trabajo, "worktree", "add", "-q", str(wt), base)
    try:
        git(wt, "config", "user.email", "orquestador@example.com")
        git(wt, "config", "user.name", "orquestador")
        for d in deps:
            r = git(wt, "merge", "--no-ff", "--no-edit", f"tarea/{d}", check=False)
            if r.returncode != 0:
                archivos = git(wt, "diff", "--name-only", "--diff-filter=U").stdout.split()
                git(wt, "merge", "--abort", check=False)
                return base, {"choco_con": d, "archivos": archivos}
    finally:
        git(trabajo, "worktree", "remove", "--force", str(wt), check=False)
    return base, None


def construir(trabajo: Path) -> list[dict]:
    tareas = cargar_tareas(trabajo)
    nm = (trabajo / APP / "node_modules").resolve()

    def una(t: dict, ola: int) -> dict:
        desde, choque = punto_de_partida(trabajo, t)
        wt = trabajo.parent / f"wt-{t['id']}"
        git(trabajo, "worktree", "add", "-q", "-b", f"tarea/{t['id']}", str(wt), desde)
        os.symlink(nm, wt / APP / "node_modules")
        cmd = comando_claude(prompt_constructor(t), BUILDER_TOOLS, BUILDER_DENIED)
        res = correr_agente(cmd, wt / APP, trabajo / "logs" / f"02-construir-{t['id']}.jsonl")
        git(wt, "add", "-A")
        git(wt, "commit", "-qm", f"tarea {t['id']}", check=False)
        res.update({"tarea": t["id"], "ola": ola, "desde": desde, "choque_al_arrancar": choque,
                    "juez": correr_juez(wt / APP, t["juez"].removeprefix(f"{APP}/")),
                    "check": correr_check(wt / APP)})
        return res

    resultados: list[dict] = []
    reloj = time.time()
    for n, ola in enumerate(olas(tareas), start=1):
        with ThreadPoolExecutor(max_workers=len(ola)) as pool:
            resultados += list(pool.map(lambda t: una(t, n), ola))
    resumen = {"tareas": resultados, "segundos_de_reloj": round(time.time() - reloj, 1),
               "segundos_sumados": round(sum(r["segundos"] for r in resultados), 1)}
    (trabajo / "logs" / "construir.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    return resultados


def medir(trabajo: Path) -> dict:
    tareas = cargar_tareas(trabajo)
    ramas = ramas_de_tareas(tareas)
    tmp = trabajo.parent / "wt-medir"
    jueces = jueces_de(tareas)

    en_su_rama = {}
    for t, rama in zip(tareas, ramas):
        en_su_rama[t["juez"].removeprefix(f"{APP}/")] = None
    construidas = json.loads((trabajo / "logs" / "construir.json").read_text())["tareas"]
    for c in construidas:
        t = next(t for t in tareas if t["id"] == c["tarea"])
        en_su_rama[t["juez"].removeprefix(f"{APP}/")] = c["juez"]["ok"]
    en_su_rama[JUEZ_BASE] = True

    resultados_juntos: dict[str, dict] = {}

    def correr_todos(wt: Path) -> None:
        os.symlink((trabajo / APP / "node_modules").resolve(), wt / APP / "node_modules")
        for j in jueces:
            resultados_juntos[j] = correr_juez(wt / APP, j)
        resultados_juntos["check"] = {"ok": correr_check(wt / APP)}

    secuencia = probar_fusion(trabajo, "reparto", ramas, tmp, despues=correr_todos)
    medicion = {
        "tareas": [t["id"] for t in tareas],
        "solapes_declarados": solapes_declarados(tareas),
        "fuera_de_lo_asignado": {t["id"]: tocados_fuera_de_lo_asignado(
            t, archivos_tocados(trabajo, desde_de(t), f"tarea/{t['id']}")) for t in tareas},
        "por_pares": matriz_por_pares(trabajo, "reparto", ramas, trabajo.parent / "wt-pares"),
        "secuencia": secuencia.a_dict(),
        "jueces_en_su_rama": en_su_rama,
        "jueces_juntos": resultados_juntos or None,
        "regresiones": regresiones(en_su_rama, resultados_juntos) if resultados_juntos else None,
    }
    (trabajo / "logs" / "medicion.json").write_text(json.dumps(medicion, indent=2, ensure_ascii=False))
    return medicion


def integrar(trabajo: Path) -> dict:
    wt = trabajo.parent / "wt-integracion"
    git(trabajo, "worktree", "add", "-q", "-b", "integracion", str(wt), "reparto")
    os.symlink((trabajo / APP / "node_modules").resolve(), wt / APP / "node_modules")
    tareas = cargar_tareas(trabajo)
    prompt = (TEMA / "prompts" / "03-integrar.txt").read_text().format(
        ramas=" ".join(ramas_de_tareas(tareas)))
    cmd = comando_claude(prompt, INTEGRATOR_TOOLS, INTEGRATOR_DENIED)
    res = correr_agente(cmd, wt, trabajo / "logs" / "03-integrar.jsonl")
    res["jueces"] = {j: correr_juez(wt / APP, j) for j in jueces_de(tareas)}
    res["check"] = correr_check(wt / APP)
    res["commits"] = git(wt, "log", "--oneline", "reparto..HEAD").stdout.splitlines()
    (trabajo / "logs" / "integrar.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    return res


def exportar(trabajo: Path) -> None:
    tareas = cargar_tareas(trabajo)
    rep = reemplazos_para(trabajo)
    shutil.copytree(trabajo / "reparto", TEMA / "reparto", dirs_exist_ok=True)
    for t in tareas:
        rel = t["juez"].removeprefix(f"{APP}/")
        shutil.copy(trabajo / APP / rel, TEMA / APP / rel)
        diff = git(trabajo, "diff", "--binary", desde_de(t), f"tarea/{t['id']}", "--", APP).stdout
        (TEMA / "entrega" / f"{t['id']}.patch").write_text(diff)
    if git(trabajo, "rev-parse", "--verify", "integracion", check=False).returncode == 0:
        diff = git(trabajo, "diff", "--binary", "reparto", "integracion", "--", APP).stdout
        (TEMA / "entrega" / "integracion.patch").write_text(diff)
    for log in sorted((trabajo / "logs").glob("*")):
        destino = TEMA / "logs" / log.name
        if log.suffix == ".jsonl":
            sanear_log(log, destino, rep)
        else:
            texto = log.read_text()
            for viejo, nuevo in rep:
                texto = texto.replace(viejo, nuevo)
            destino.write_text(texto)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("subcomando", choices=["preparar", "repartir", "congelar", "construir",
                                           "medir", "integrar", "exportar"])
    ap.add_argument("--trabajo", type=Path, required=True,
                    help="carpeta del repo de trabajo (fuera del monorepo)")
    ap.add_argument("--node-modules", type=Path, default=TEMA / APP / "node_modules")
    a = ap.parse_args(argv)
    trabajo = a.trabajo
    if a.subcomando == "preparar":
        preparar(trabajo, a.node_modules)
    else:
        fn = {"repartir": repartir, "congelar": congelar, "construir": construir,
              "medir": medir, "integrar": integrar, "exportar": exportar}[a.subcomando]
        salida = fn(trabajo)
        if salida is not None:
            print(json.dumps(salida, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
