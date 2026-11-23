"""Tool de terminal del agente: un modo watch sin salida agota el timeout."""
import json
import subprocess
import sys
import time

CODIGO_WATCH = (
    "import time; print('WATCH esperando tecla...', flush=True); time.sleep(10)"
)
WATCH_DEMO = [sys.executable, "-c", CODIGO_WATCH]


def correr_comando(cmd, cwd="travelens", timeout=1.5):
    inicio = time.monotonic()
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout)
        return {"ok": r.returncode == 0, "exit": r.returncode,
                "segundos": round(time.monotonic() - inicio, 2)}
    except subprocess.TimeoutExpired as exc:
        crudo = exc.stdout or ""
        out = crudo.decode() if isinstance(crudo, bytes) else crudo
        lineas = out.strip().splitlines()
        return {"ok": False, "codigo": "TIMEOUT", "segundos": timeout,
                "salida": lineas[0] if lineas else ""}


if __name__ == "__main__":
    print(json.dumps(correr_comando(WATCH_DEMO), ensure_ascii=False, indent=2))
