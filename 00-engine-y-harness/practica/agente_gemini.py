"""El mismo loop con un engine real: Gemini en Vertex AI.
Antes: gcloud auth application-default login, habilitar Vertex AI y
export GOOGLE_CLOUD_PROJECT=tu-proyecto (los comandos están en el README)."""
from src.gemini_engine import make_gemini_engine
from src.mini_agent import run_agent_loop

TAREA = ("Cuenta las funciones de sandbox_app/catalog_filter.py y corre "
         "sus tests con pytest. Responde en una línea.")

if __name__ == "__main__":
    engine = make_gemini_engine("gemini-3.8-flash")
    resultado = run_agent_loop(TAREA, engine, max_turns=6)
    print("turnos:", resultado["turns"], resultado.get("codigo", ""))
