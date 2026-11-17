"""El juez como tool: corre sus pruebas y regresa un resumen corto."""
import json
import pathlib
import subprocess
import tempfile

APP = "rent-my-gear"


def correr_juez():
    reporte = pathlib.Path(tempfile.gettempdir()) / "juez.json"
    subprocess.run(["npx", "vitest", "run", "--config", "vitest.juez.config.ts",
                    "--reporter=json", f"--outputFile={reporte}"],
                   cwd=APP, capture_output=True, timeout=180)
    r = json.loads(reporte.read_text(encoding="utf-8"))
    primera = lambda m: m.split("\n")[0].split(": ", 1)[-1].split(" //")[0][:46]
    fallas = [t["title"] + " -> " + primera(t["failureMessages"][0])
              for f in r["testResults"] for t in f["assertionResults"]
              if t["status"] == "failed"]
    return {"ok": r["success"], "pasan": r["numPassedTests"],
            "fallan": r["numFailedTests"], "fallas": fallas}


if __name__ == "__main__":
    print(json.dumps(correr_juez(), ensure_ascii=False, indent=1))
