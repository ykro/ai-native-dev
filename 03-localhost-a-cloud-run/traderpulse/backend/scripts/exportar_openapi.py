"""Escribe el contrato OpenAPI del BFF en la ruta indicada (por defecto, ../contrato/openapi.json)."""

import json
import sys
from pathlib import Path

from traderpulse_api.main import app

destino = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else Path(__file__).parents[2] / "contrato" / "openapi.json"
)
esquema = app.openapi()
esquema["info"]["version"] = "contrato"  # la versión del paquete no debe mover el contrato
destino.write_text(
    json.dumps(esquema, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(
    f"contrato escrito en {destino.name}: {len(esquema['paths'])} rutas, {len(esquema['components']['schemas'])} esquemas"
)
