"""Shared helpers for the judge. The judge runs against the tree in TP_ROOT (default: the base copy)."""
import os
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent.parent
# TP_ROOT wins; a judge copied next to a backend/ folder (defense session) tests that folder; otherwise the base copy.
ROOT = Path(os.environ.get("TP_ROOT") or (_here if (_here / "backend").exists() else _here / "traderpulse"))
os.environ.setdefault("GEMINI_API_KEY", "test-key-no-real-calls")
sys.path.insert(0, str(ROOT))
