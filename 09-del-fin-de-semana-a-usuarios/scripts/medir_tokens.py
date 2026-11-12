#!/usr/bin/env python3
"""Measures the tokens one real request uses in the two projects that call the model per request.

TraderPulse: runs the project's own analyze_sentiment with a client that forwards to Vertex AI and records usage.
TraveLens: takes the prompt template of src/services/gemini.ts, fills it in and sends it with the same model and config.
Writes medicion/tokens-por-peticion-<project>.jsonl (one line per request). Needs GOOGLE_CLOUD_PROJECT in the environment.

Usage: GOOGLE_CLOUD_PROJECT=<id> .venv/bin/python scripts/medir_tokens.py
"""
from __future__ import annotations

import asyncio
import datetime
import json
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace

from google import genai

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get("EVAL_MODEL", "gemini-3.8-flash")
client = genai.Client(vertexai=True, project=os.environ["GOOGLE_CLOUD_PROJECT"], location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"))


def usage_record(project: str, case: str, response) -> dict:
    u = response.usage_metadata
    return {"fecha": datetime.date.today().isoformat(), "proyecto": project, "caso": case, "modelo": MODEL,
            "tokens_entrada": u.prompt_token_count, "tokens_salida": (u.candidates_token_count or 0) + (u.thoughts_token_count or 0),
            "detalle": {"candidatos": u.candidates_token_count, "razonamiento": u.thoughts_token_count}}


def traderpulse() -> list[dict]:
    sys.path.insert(0, str(ROOT / "proyectos/traderpulse"))
    os.environ.setdefault("GEMINI_API_KEY", "test-key-no-real-calls")
    from backend.services import ai_service

    records = []

    class Forward:
        def __init__(self):
            self.models = SimpleNamespace(generate_content=self.call)

        def call(self, **kw):
            kw["model"] = MODEL
            response = client.models.generate_content(**kw)
            records.append(response)
            return response

    ai_service.client = Forward()
    cases = [("ACME", {"symbol": "ACME", "price": "152.30", "change_percent": "3.2100%", "volume": "4800000"}),
             ("BOLT", {"symbol": "BOLT", "price": "48.10", "change_percent": "-4.7000%", "volume": "9100000"}),
             ("CORE", {"symbol": "CORE", "price": "310.00", "change_percent": "0.0500%", "volume": "2100000"})]
    out = []
    for symbol, data in cases:
        asyncio.run(ai_service.analyze_sentiment(symbol, data))
        out.append(usage_record("traderpulse", symbol, records[-1]))
    return out


def travelens() -> list[dict]:
    source = (ROOT / "proyectos/travelens/src/services/gemini.ts").read_text(encoding="utf-8")
    template = re.search(r"const prompt = `(.*?)`;", source, re.S).group(1)
    out = []
    for destination, context in [("Antigua Guatemala", ""), ("Lisboa", "viaje en pareja"), ("Kioto", "primavera")]:
        prompt = template.replace("${destinationName}", destination).replace("${context ? `(${context})` : ''}", f"({context})" if context else "")
        response = client.models.generate_content(model=MODEL, contents=prompt,
                                                  config=genai.types.GenerateContentConfig(response_mime_type="application/json"))
        out.append(usage_record("travelens", destination, response))
    return out


if __name__ == "__main__":
    for name, fn in (("traderpulse", traderpulse), ("travelens", travelens)):
        rows = fn()
        (ROOT / f"medicion/tokens-por-peticion-{name}.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        print(name, [(r["tokens_entrada"], r["tokens_salida"]) for r in rows])
