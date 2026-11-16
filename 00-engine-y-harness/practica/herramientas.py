"""Dos tools: funciones que devuelven un diccionario, también si fallan."""
import pathlib
import subprocess


def read_file(path, max_lines=200):
    p = pathlib.Path(path)
    if not p.exists():
        return {"ok": False, "codigo": "ARCHIVO_NO_ENCONTRADO",
                "accion_sugerida": "Lista los archivos con ls"}
    lineas = p.read_text(encoding="utf-8").splitlines()
    return {"ok": True, "total_lines": len(lineas),
            "content": "\n".join(lineas[:max_lines])}


def run_bash(command, timeout_sec=15):
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True,
                           timeout=timeout_sec, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "codigo": "TIEMPO_AGOTADO",
                "accion_sugerida": "Corre un comando más corto o sube timeout_sec"}
    return {"ok": r.returncode == 0, "exit_code": r.returncode,
            "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]}


TOOLS = {"read_file": read_file, "run_bash": run_bash}

if __name__ == "__main__":
    print(TOOLS["read_file"]("sandbox_app/catalog_filter.py", max_lines=1))
    print(TOOLS["read_file"]("no-existe.py"))
    print(TOOLS["run_bash"]("ls sandbox_app"))
