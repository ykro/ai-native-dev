"""Suite de pruebas para sandbox_app/catalog_filter.py."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sandbox_app.catalog_filter import filter_available_under_price, filter_by_category  # noqa: E402

SAMPLE_ITEMS = [
    {"id": "p1", "name": "Worker Queue SDK", "category": "backend", "price": 49.0, "active": True},
    {"id": "p2", "name": "Trace Inspector CLI", "category": "backend", "price": 79.0, "active": True},
    {"id": "p3", "name": "Legacy Adapter", "category": "backend", "price": 29.0, "active": False},
    {"id": "p4", "name": "UI Grid Kit", "category": "frontend", "price": 35.0, "active": True},
]


def test_filter_by_category_exact_lowercase() -> None:
    res = filter_by_category(SAMPLE_ITEMS, "backend")
    assert [item["id"] for item in res] == ["p1", "p2"]


def test_filter_by_category_case_insensitive_and_whitespace() -> None:
    res = filter_by_category(SAMPLE_ITEMS, "  Backend ")
    assert [item["id"] for item in res] == ["p1", "p2"]


def test_filter_available_under_price() -> None:
    res = filter_available_under_price(SAMPLE_ITEMS, 50.0)
    assert [item["id"] for item in res] == ["p1", "p4"]
