"""Harness de la práctica: el loop del video anterior, con tools para Rent My Gear,
reglas de permiso por sesión y una traza por turno (tokens y tools pedidas)."""
import json
import pathlib
import subprocess

from practica.juez import APP, correr_juez
from practica.permisos import negar, permitido

RAIZ = pathlib.Path(APP)
COMANDOS = ("npm run test:run", "npm run lint", "npx tsc --noEmit", "npx vitest run")
JUEZ = "npm run juez"  # solo existe para las sesiones que pueden leer el juez
FUERA = ("node_modules", ".next", ".git")


def _limpia(ruta):
    ruta = str(ruta or ".").strip().removeprefix("./") or "."
    return ruta[len(APP) + 1:] if ruta.startswith(APP + "/") else ruta


def _dentro(ruta):
    p = (RAIZ / ruta).resolve()
    return p if p.is_relative_to(RAIZ.resolve()) else None


def listar(carpeta=".", sesion=""):
    carpeta = _limpia(carpeta)
    base = _dentro(carpeta)
    if base is None or not base.is_dir():
        return {"ok": False, "codigo": "CARPETA_NO_ENCONTRADA", "accion_sugerida": "Lista '.' para ver la raíz"}
    rutas = sorted(str(p.relative_to(RAIZ.resolve())) for p in base.rglob("*")
                   if p.is_file() and not any(x in p.parts for x in FUERA))
    rutas = [r for r in rutas if permitido(r, "leer", sesion)]
    return {"ok": True, "archivos": rutas[:150], "total": len(rutas)}


def leer(ruta, sesion=""):
    ruta = _limpia(ruta)
    if not permitido(ruta, "leer", sesion):
        return negar(ruta, "leer")
    p = _dentro(ruta)
    if p is None or not p.is_file():
        return {"ok": False, "codigo": "ARCHIVO_NO_ENCONTRADO", "accion_sugerida": "Usa listar para ver las rutas"}
    texto = p.read_text(encoding="utf-8")
    return {"ok": True, "lineas": texto.count("\n") + 1, "contenido": texto[:16000]}


def buscar(texto, sesion=""):
    r = subprocess.run(["grep", "-rnF", "--exclude-dir=node_modules", "--exclude-dir=.next", texto, "src", "juez"],
                       cwd=RAIZ, capture_output=True, text=True, timeout=20)
    hits = [h for h in r.stdout.splitlines() if permitido(h.split(":", 1)[0], "leer", sesion)]
    return {"ok": True, "coincidencias": hits[:40], "total": len(hits)}


def editar(ruta, viejo, nuevo, sesion=""):
    ruta = _limpia(ruta)
    if not permitido(ruta, "escribir", sesion):
        return negar(ruta, "escribir")
    p = _dentro(ruta)
    if p is None or not p.is_file():
        return {"ok": False, "codigo": "ARCHIVO_NO_ENCONTRADO", "accion_sugerida": "Usa listar para ver las rutas"}
    texto = p.read_text(encoding="utf-8")
    n = texto.count(viejo)
    if n != 1:
        return {"ok": False, "codigo": "BLOQUE_NO_COINCIDE" if n == 0 else "BLOQUE_AMBIGUO", "coincidencias": n,
                "accion_sugerida": "Copia el texto exacto y agrega líneas vecinas hasta que aparezca una sola vez"}
    p.write_text(texto.replace(viejo, nuevo), encoding="utf-8")
    return {"ok": True, "reemplazos": 1}


def escribir(ruta, contenido, sesion=""):
    ruta = _limpia(ruta)
    if not permitido(ruta, "escribir", sesion):
        return negar(ruta, "escribir")
    p = _dentro(ruta)
    if p is None:
        return negar(ruta, "escribir")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(contenido, encoding="utf-8")
    return {"ok": True, "lineas": contenido.count("\n") + 1}


def _comandos(sesion):
    return COMANDOS + ((JUEZ,) if permitido("juez/", "leer", sesion) else ())


def correr(comando, sesion=""):
    comando = " ".join(str(comando).split())
    validos = _comandos(sesion)
    if not comando.startswith(validos) or any(c in comando for c in ";&|`$><"):
        return {"ok": False, "codigo": "PERMISO_DENEGADO",
                "accion_sugerida": "Solo puedes correr: " + ", ".join(validos)}
    try:
        r = subprocess.run(comando, shell=True, cwd=RAIZ, capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        return {"ok": False, "codigo": "TIEMPO_AGOTADO", "accion_sugerida": "Corre un comando más corto"}
    return {"ok": r.returncode == 0, "exit_code": r.returncode, "salida": (r.stdout + r.stderr)[-1800:]}


def juez(sesion=""):
    if not permitido("juez/", "leer", sesion):
        return negar("juez/", "correr")
    return correr_juez()


_S = lambda **p: {"type": "object", "properties": {k: {"type": v} for k, v in p.items()}, "required": list(p)}
ESQUEMAS = {
    "listar": ("Lista los archivos de una carpeta de rent-my-gear.", _S(carpeta="string")),
    "leer": ("Lee un archivo de rent-my-gear (ruta relativa a esa carpeta).", _S(ruta="string")),
    "buscar": ("Busca un texto exacto en src/ y regresa archivo:línea:texto.", _S(texto="string")),
    "editar": ("Reemplaza un texto exacto que aparece una sola vez en el archivo.",
               _S(ruta="string", viejo="string", nuevo="string")),
    "escribir": ("Crea o reemplaza un archivo completo.", _S(ruta="string", contenido="string")),
    "correr": ("Corre un comando de verificación.", _S(comando="string")),
    "juez": ("Corre el juez de la cobertura y regresa cuántas pruebas pasan y cuáles fallan.", _S()),
}
TOOLS = {"listar": listar, "leer": leer, "buscar": buscar, "editar": editar,
         "escribir": escribir, "correr": correr, "juez": juez}
POR_SESION = {
    "directo": ["listar", "leer", "buscar", "editar", "escribir", "correr"],
    "mapa": ["listar", "leer", "buscar"],
    "limpia": ["listar", "leer", "buscar", "editar", "escribir", "correr", "juez"],
}


def esquemas(sesion):
    desc = lambda n: ESQUEMAS[n][0] + (" Permitidos: " + ", ".join(_comandos(sesion)) + "." if n == "correr" else "")
    return [{"name": n, "description": desc(n), "input_schema": ESQUEMAS[n][1]} for n in POR_SESION[sesion]]


def _corto(nombre, args):
    if nombre in ("editar", "escribir", "leer", "listar"):
        return f"{nombre} {_limpia(args.get('ruta', args.get('carpeta', '.')))}"
    if nombre == "buscar":
        return f'buscar "{args.get("texto", "")[:40]}"'
    if nombre == "correr":
        return f"correr {args.get('comando', '')}"
    return nombre


def _resultado(r):
    if not r.get("ok"):
        return f"ok=False {r.get('codigo', '')}{' exit=' + str(r['exit_code']) if 'exit_code' in r else ''}".rstrip()
    if "pasan" in r:
        return f"ok=True pasan {r['pasan']} de {r['pasan'] + r['fallan']}"
    return "ok=True"


def lanzar(sesion, prompt, engine, historia=None, max_turnos=40, traza=None):
    """Una sesión: historia vacía (sesión limpia) o la de antes (la misma sesión sigue creciendo)."""
    messages = list(historia or []) + [{"role": "user", "content": prompt}]
    if traza and not historia:  # una sesión nueva empieza su traza desde cero
        open(traza, "w").close()
    tools = esquemas(sesion)
    n0 = sum(m["role"] == "assistant" for m in messages)
    for turno in range(n0 + 1, n0 + max_turnos + 1):
        resp = engine(messages, tools)
        u = resp["usage"]
        print(f"[turno {turno:2}] entrada {u['input_tokens']:6} tokens")
        if traza:
            with open(traza, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sesion": sesion, "turno": turno, **u,
                                    "tool_calls": [{k: c[k] for k in ("name", "input")} for c in resp.get("tool_calls", [])],
                                    "text": resp.get("text", "")}, ensure_ascii=False) + "\n")
        calls = resp.get("tool_calls") or []
        messages.append({"role": "assistant", "tool_calls": calls, "text": resp.get("text", ""), "raw": resp.get("raw")})
        if not calls:
            print(f"[final] {resp.get('text', '')}")
            return messages
        for c in calls:
            fn = TOOLS.get(c["name"]) if c["name"] in POR_SESION[sesion] else None
            try:
                r = fn(**c["input"], sesion=sesion) if fn else {"ok": False, "codigo": "HERRAMIENTA_DESCONOCIDA"}
            except TypeError as e:
                r = {"ok": False, "codigo": "ARGUMENTOS_INVALIDOS", "accion_sugerida": str(e)}
            print(f"   {_corto(c['name'], c['input'])} -> {_resultado(r)}")
            messages.append({"role": "tool", "name": c["name"], "tool_use_id": c["id"], "content": r})
    print("[final] MAX_TURNOS")
    return messages
