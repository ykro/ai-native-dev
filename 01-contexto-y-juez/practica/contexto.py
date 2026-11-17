"""Cuánto contexto carga cada turno de una sesión, leído de su traza."""
import json
import sys


def barras(traza, escala=2000):
    turnos = [json.loads(linea) for linea in open(traza, encoding="utf-8")]
    for t in turnos:
        barra = "#" * (t["input_tokens"] // escala)
        print(f"turno {t['turno']:2}  {t['input_tokens']:6}  {barra}")
    total = sum(t["input_tokens"] for t in turnos)
    print(f"{len(turnos)} turnos, {total} tokens de entrada en total")


if __name__ == "__main__":
    for traza in sys.argv[1:]:
        print(traza)
        barras(traza)
