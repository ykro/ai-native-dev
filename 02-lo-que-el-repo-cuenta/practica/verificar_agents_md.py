"""Audita AGENTS.md o CLAUDE.md contra los scripts y rutas del repositorio."""
import json
import pathlib
import re
import sys


def auditar_guia(guia_path, app="travelens", pkg_path=None):
    guia = pathlib.Path(guia_path)
    texto = guia.read_text(encoding="utf-8")
    importa = None
    if texto.strip().startswith("@") and "\n" not in texto.strip():
        importa = texto.strip()[1:]
        destino = guia.parent / importa
        if not destino.is_file():
            return {"archivo": guia.name, "ok": False, "import_roto": importa}
        texto = destino.read_text(encoding="utf-8")
    pkg = pathlib.Path(pkg_path) if pkg_path else pathlib.Path(app) / "package.json"
    scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
    cmds = list(dict.fromkeys(re.findall(r"npm run ([a-zA-Z0-9:_-]+)", texto)))
    pat_ruta = r"`((?:src|tests|public|juez)/[^`\s]+)`"
    rutas = list(dict.fromkeys(re.findall(pat_ruta, texto)))
    cmds_rotos = [c for c in cmds if c not in scripts]
    rutas_rotas = [r for r in rutas if not (pathlib.Path(app) / r).exists()]
    lineas = len(texto.splitlines())
    return {"archivo": guia.name, "importa": importa, "lineas": lineas,
            "tokens_aprox": len(texto) // 4, "comandos_rotos": cmds_rotos,
            "rutas_rotas": rutas_rotas,
            "ok": lineas <= 100 and not cmds_rotos and not rutas_rotas}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(auditar_guia(sys.argv[1]), ensure_ascii=False, indent=2))
    else:
        casos = [
            ("medicion/antes/CLAUDE.inflado.md",
             "medicion/antes/package.antes.json"),
            ("travelens/AGENTS.md", "travelens/package.json"),
            ("travelens/CLAUDE.md", "travelens/package.json"),
        ]
        for g, p in casos:
            print(json.dumps(auditar_guia(g, "travelens", p), ensure_ascii=False))
