"""Filtro de catálogo de productos para demostrar edición quirúrgica con Coding Agents."""

from __future__ import annotations

from typing import Any


def filter_by_category(items: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    """Filtra productos activos que coincidan con la categoría solicitada."""
    target_cat = category.strip().lower()
    if not items or not target_cat:
        return []
    return [
        item
        for item in items
        if item.get("active", True) and str(item.get("category", "")).strip().lower() == target_cat
    ]


def filter_available_under_price(items: list[dict[str, Any]], max_price: float) -> list[dict[str, Any]]:
    """Filtra productos activos cuyo precio sea menor o igual a max_price."""
    if not items or max_price < 0:
        return []
    return [
        item
        for item in items
        if item.get("active", True) and float(item.get("price", 0.0)) <= max_price
    ]


def count_exact_category_legacy(items: list[dict[str, Any]], category: str) -> int:
    """Cuenta coincidencias exactas heredadas sin normalizar mayúsculas."""
    return len([
        item
        for item in items
        if item.get("active", True) and item.get("category") == category
    ])
