"""Servidor MCP ergonómico para Rent My Gear (cotización con seguro por categoría y auditoría de catálogo)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Literal

CategoryLiteral = Literal["fotografia-video", "montana-camping", "deportes-acuaticos"]
INSURANCE_RATES: dict[str, float] = {
    "fotografia-video": 0.20,
    "montana-camping": 0.10,
    "deportes-acuaticos": 0.10,
}

INVENTORY_PATH = Path(__file__).resolve().parent / "src" / "data" / "inventory.json"


def _load_items() -> list[dict]:
    if INVENTORY_PATH.exists():
        return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return [
        {"id": "gear-001", "name": "Canon EOS R5", "category": "fotografia-video", "dailyRate": 150},
        {"id": "gear-018", "name": "Tienda MSR Hubba Hubba NX 2", "category": "montana-camping", "dailyRate": 35},
        {"id": "gear-035", "name": "Kayak Travesía Pro", "category": "deportes-acuaticos", "dailyRate": 60},
    ]


def cotizar_reserva(
    categoria: CategoryLiteral,
    gear_id: str,
    dias: int,
    dry_run: bool = True,
) -> dict:
    """Calcula tarifa, seguro por categoría (20% foto/video, 10% resto) y valida rango de 1 a 30 días."""
    if dias < 1 or dias > 30:
        return {
            "error": "rango_1_a_30_dias",
            "detail": f"Se recibieron {dias} días; la regla de negocio permite de 1 a 30 días inclusivos.",
            "retry": False,
        }
    items = {item["id"]: item for item in _load_items()}
    item = items.get(gear_id)
    if not item:
        return {"error": "equipo_no_encontrado", "gear_id": gear_id, "retry": False}
    if item["category"] != categoria:
        return {"error": "categoria_no_coincide", "esperada": item["category"], "retry": False}

    subtotal = round(float(item["dailyRate"]) * dias, 2)
    tasa_seguro = INSURANCE_RATES[categoria]
    seguro = round(subtotal * tasa_seguro, 2)
    return {
        "modo": "simulacion" if dry_run else "confirmado",
        "gear_id": gear_id,
        "nombre": item["name"],
        "dias": dias,
        "subtotal": subtotal,
        "tasa_seguro": tasa_seguro,
        "seguro": seguro,
        "total": round(subtotal + seguro, 2),
    }


def auditar_catalogo(dry_run: bool = True) -> dict:
    """Verifica que todos los equipos del catálogo pertenezcan a categorías con seguro configurado."""
    items = _load_items()
    invalid = [it["id"] for it in items if it.get("category") not in INSURANCE_RATES]
    return {
        "modo": "simulacion" if dry_run else "confirmado",
        "total_equipos": len(items),
        "categorias_validas": list(INSURANCE_RATES.keys()),
        "equipos_fuera_de_contrato": invalid,
        "status": "OK" if not invalid else "ERROR",
    }


def main() -> int:
    if "--self-test" in sys.argv:
        ok_quote = cotizar_reserva("fotografia-video", "gear-001", 2, dry_run=True)
        bad_range = cotizar_reserva("fotografia-video", "gear-001", 35, dry_run=True)
        audit = auditar_catalogo(dry_run=True)
        assert ok_quote["modo"] == "simulacion" and ok_quote["seguro"] == 60.0 and ok_quote["total"] == 360.0
        assert bad_range.get("error") == "rango_1_a_30_dias" and bad_range.get("retry") is False
        assert audit["status"] == "OK" and audit["total_equipos"] > 0
        print(json.dumps({"mcp_self_test": "PASS", "sample_quote": ok_quote, "audit": audit}, ensure_ascii=False))
        return 0
    print(json.dumps(cotizar_reserva("fotografia-video", "gear-001", 2, dry_run=True), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
