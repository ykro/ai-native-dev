import { GoogleGenAI } from "@google/genai";

export const PLAN_MODEL = "gemini-3.8-flash";

let client: GoogleGenAI | null = null;

function getClient(): GoogleGenAI {
    if (client === null) {
        client = new GoogleGenAI({ apiKey: process.env.GOOGLE_GENAI_API_KEY || "" });
    }
    return client;
}

export interface TravelPlan {
    intro: string;
    days: {
        day: number;
        title: string;
        activities: string[];
    }[];
    hiddenGem: {
        title: string;
        description: string;
    };
    localFood: {
        dish: string;
        description: string;
    };
}

export const GeminiService = {
    generateTravelPlan: async (destinationName: string, context?: string): Promise<TravelPlan | null> => {
        try {
            if (!process.env.GOOGLE_GENAI_API_KEY) {
                console.error("Gemini Service: Missing GOOGLE_GENAI_API_KEY");
                throw new Error("Missing Google API Key");
            }

            const prompt = `
        Act as an expert travel guide. Create a 3-day itinerary for ${destinationName} ${context ? `(${context})` : ''}.
        
        Requirements:
        - Tone: Enthusiastic, immersive, and practical.
        - Language: Spanish (Español).
        - Output Format: JSON ONLY. Do not use Markdown code blocks.
        
        JSON Schema:
        {
          "intro": "1 sentence hook",
          "days": [
            { "day": 1, "title": "Theme of the day (e.g. Historic Center)", "activities": ["Activity 1", "Activity 2", "Activity 3"] }
          ],
          "hiddenGem": { "title": "Name", "description": "Why it is special" },
          "localFood": { "dish": "Name", "description": "What is it" }
        }
      `;

            const response = await getClient().models.generateContent({
                model: PLAN_MODEL,
                contents: prompt,
                config: { responseMimeType: "application/json" },
            });
            const text = response.text ?? "";

            // console.log("Gemini JSON Response:", text); // Debug removed per user request

            return JSON.parse(text) as TravelPlan;

        } catch (error) {
            console.error("Gemini AI Error:", error);
            return null;
        }
    }
};
