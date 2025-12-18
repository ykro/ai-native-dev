"""
Script to generate dog profiles for PawsMatch using Google's Gemini API.
Generates 50 dog profiles with id, name, and a 3-line adoption-focused bio in Spanish.
"""

import json
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def generate_pets():
    """Generate 50 dog profiles using Gemini API."""
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
    client = genai.Client(api_key=api_key)

    prompt = """Generate exactly 50 unique dog profiles for an adoption app called PawsMatch.

    Each profile must have:
    - id: a unique integer starting from 1
    - name: a creative dog name
    - bio: a 3-line adoption-focused biography in Spanish that describes the dog's personality,
      what they're looking for in a home, and why someone should adopt them

    Return ONLY a valid JSON array with no additional text or markdown formatting.
    The response should start with [ and end with ].

    Example format:
    [
      {
        "id": 1,
        "name": "Max",
        "bio": "Soy un golden retriever de 3 años, juguetón y cariñoso.\\nBusco una familia activa que disfrute de paseos largos.\\nPrometo llenar tu hogar de alegría y amor incondicional."
      }
    ]
    """

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    # Parse the response
    response_text = response.text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    pets = json.loads(response_text)

    # Save to pets.json
    with open("pets.json", "w", encoding="utf-8") as f:
        json.dump(pets, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {len(pets)} dog profiles!")
    print("Saved to pets.json")

    return pets

if __name__ == "__main__":
    generate_pets()
