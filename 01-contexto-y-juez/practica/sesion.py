"""Lanza una sesión del agente sobre Rent My Gear: directo, mapa o limpia."""
import sys

from practica.harness import lanzar
from practica.juez import correr_juez
from practica.motor import gemini, grabado

PROMPT = {"directo": "01-directo", "mapa": "02-mapa", "limpia": "03-iterar"}


def veredicto():  # el harness corre el juez él mismo; no le cree al agente
    v = correr_juez()
    print(f"[juez] pasan {v['pasan']} de 5")
    for falla in v["fallas"]:
        print("   " + falla)
    return v


def directo(engine, traza):  # una sola sesión que sigue creciendo
    pedido = open("prompts/01-directo.txt").read()  # una línea, sin juez
    msgs = lanzar("directo", pedido, engine, max_turnos=60, traza=traza)
    for _ in range(2):
        v = veredicto()
        if v["ok"]:
            return
        queja = "El juez falla: " + "; ".join(v["fallas"]) + ". Corrígelo."
        msgs = lanzar("directo", queja, engine, historia=msgs, traza=traza)
    veredicto()


if __name__ == "__main__":
    sesion, grabada = sys.argv[1], "--grabada" in sys.argv
    engine = grabado(f"sesiones/{sesion}.jsonl", sesion) if grabada else gemini()
    traza = None if grabada else f"sesiones/tuya-{sesion}.jsonl"
    if sesion == "directo":
        directo(engine, traza)
    else:  # mapa y limpia: historia vacía, arrancan solo con su prompt
        prompt = open(f"prompts/{PROMPT[sesion]}.txt").read()
        lanzar(sesion, prompt, engine, traza=traza)
        if sesion == "limpia":
            veredicto()
