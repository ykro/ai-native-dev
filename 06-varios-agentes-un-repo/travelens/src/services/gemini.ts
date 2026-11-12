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

function isNonEmptyString(value: unknown): value is string {
    return typeof value === "string" && value.trim().length > 0;
}

function isTravelPlan(value: unknown): value is TravelPlan {
    if (typeof value !== "object" || value === null) return false;
    const plan = value as Record<string, unknown>;
    if (!isNonEmptyString(plan.intro) || !Array.isArray(plan.days) || plan.days.length !== 3) return false;
    if (!plan.days.every((day) => {
        if (typeof day !== "object" || day === null) return false;
        const candidate = day as Record<string, unknown>;
        return typeof candidate.day === "number" && isNonEmptyString(candidate.title) &&
            Array.isArray(candidate.activities) && candidate.activities.length > 0 &&
            candidate.activities.every(isNonEmptyString);
    })) return false;
    if (typeof plan.hiddenGem !== "object" || plan.hiddenGem === null ||
        typeof plan.localFood !== "object" || plan.localFood === null) return false;
    const hiddenGem = plan.hiddenGem as Record<string, unknown>;
    const localFood = plan.localFood as Record<string, unknown>;
    return isNonEmptyString(hiddenGem.title) && isNonEmptyString(hiddenGem.description) &&
        isNonEmptyString(localFood.dish) && isNonEmptyString(localFood.description);
}

function cleanJsonBlock(text: string): string {
    const trimmed = text.trim();
    const block = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
    return block ? block[1].trim() : trimmed;
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

            const parsed: unknown = JSON.parse(cleanJsonBlock(text));
            return isTravelPlan(parsed) ? parsed : null;

        } catch (error) {
            console.error("Gemini AI Error:", error);
            return null;
        }
    }
};
