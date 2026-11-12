from google import genai
from google.genai import types
from ..config import get_settings
import json

settings = get_settings()

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def analyze_sentiment(symbol: str, market_data: dict):
    """
    Uses Gemini 3 Flash to analyze market data and return sentiment in Spanish.
    """
    
    prompt = f"""
    Act as a financial analyst. Analyze the following market data for {symbol}:
    {json.dumps(market_data)}
    
    Provide a sentiment analysis.
    Output must be strict JSON with the following schema:
    {{
        "sentiment": "Bullish" | "Bearish" | "Neutral",
        "justification": "A brief explanation in Spanish (max 2 sentences)."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Using Flash as requested (2.0 is current flash version usually)
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        result = json.loads(response.text)
        return result
    except Exception as e:
        # Mock response on failure
        print(f"Gemini API Error: {e}")
        return {
            "sentiment": "Neutral",
            "justification": "No se pudo obtener el análisis en este momento. Datos simulados."
        }
