import { GoogleGenerativeAI } from "@google/generative-ai";
import { getEnv } from "@/config/env";
import { uploadImageFromBase64 } from "./storageService";
import { getGearById, updateGearImage } from "./inventoryService";
import { GearItem, CATEGORIES } from "@/lib/validation";

// Lazy-initialized Gemini client
let genAI: GoogleGenerativeAI | null = null;

/**
 * Get the Gemini AI client
 */
function getGenAIClient(): GoogleGenerativeAI {
  if (genAI === null) {
    const env = getEnv();
    genAI = new GoogleGenerativeAI(env.NANO_BANANA_API_KEY);
  }
  return genAI;
}

/**
 * Generate an image prompt for a gear item
 */
function generateImagePrompt(item: GearItem): string {
  const categoryName = CATEGORIES[item.category].name;

  return `Professional product photography of ${item.name}.
Category: ${categoryName}.
Description: ${item.description}.
Style: Clean white background, studio lighting, high-end commercial photography style.
The image should be photorealistic, well-lit, and suitable for an e-commerce rental marketplace.
Show the product from a 3/4 angle that highlights its features and build quality.`;
}

/**
 * Generate an image using Nano Banana (Gemini) AI
 * Returns the base64 image data
 */
async function generateImageWithAI(item: GearItem): Promise<string> {
  const client = getGenAIClient();
  const model = client.getGenerativeModel({ model: "gemini-2.0-flash-exp" });

  const prompt = generateImagePrompt(item);

  try {
    const result = await model.generateContent({
      contents: [
        {
          role: "user",
          parts: [
            {
              text: prompt,
            },
          ],
        },
      ],
      generationConfig: {
        responseModalities: ["image", "text"],
      },
    } as Parameters<typeof model.generateContent>[0]);

    const response = result.response;
    const parts = response.candidates?.[0]?.content?.parts;

    if (!parts || parts.length === 0) {
      throw new Error("No image generated in response");
    }

    // Find the image part in the response
    for (const part of parts) {
      if ("inlineData" in part && part.inlineData?.data) {
        return part.inlineData.data;
      }
    }

    throw new Error("No image data found in response");
  } catch (error) {
    console.error("AI image generation failed:", error);
    throw new Error(`Failed to generate image for ${item.name}`);
  }
}

/**
 * Get or generate an image for a gear item
 *
 * Strategy:
 * 1. If item has imageURL, return it
 * 2. If no imageURL, generate with AI
 * 3. Upload to GCS
 * 4. Update inventory.json with new URL
 * 5. Return the new URL
 */
export async function getOrGenerateImage(gearId: string): Promise<string | null> {
  const item = await getGearById(gearId);

  if (!item) {
    console.error(`Gear item not found: ${gearId}`);
    return null;
  }

  // If image exists, return it
  if (item.imageURL) {
    return item.imageURL;
  }

  console.log(`Generating image for: ${item.name} (${gearId})`);

  try {
    // Generate image with AI
    const base64Image = await generateImageWithAI(item);

    // Upload to GCS
    const imageURL = await uploadImageFromBase64(base64Image, gearId, "image/png");

    // Update inventory with new URL
    await updateGearImage(gearId, imageURL);

    console.log(`Image generated and saved: ${imageURL}`);
    return imageURL;
  } catch (error) {
    console.error(`Failed to generate/save image for ${gearId}:`, error);
    return null;
  }
}

/**
 * Resolve image URL for display
 * Returns the image URL or a placeholder if not available
 */
export function resolveImageUrl(item: GearItem): string {
  if (item.imageURL) {
    return item.imageURL;
  }

  // Return a placeholder for items without images
  // The actual generation happens on-demand via API
  return `/api/generate-image?id=${item.id}`;
}

/**
 * Check if an image URL is valid and accessible
 */
export async function isImageUrlValid(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, { method: "HEAD" });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Batch generate images for all items without images
 * Useful for pre-warming the cache
 */
export async function batchGenerateImages(
  items: GearItem[],
  onProgress?: (completed: number, total: number, item: GearItem) => void
): Promise<{ success: string[]; failed: string[] }> {
  const itemsWithoutImages = items.filter((item) => !item.imageURL);
  const success: string[] = [];
  const failed: string[] = [];

  for (let i = 0; i < itemsWithoutImages.length; i++) {
    const item = itemsWithoutImages[i];

    try {
      await getOrGenerateImage(item.id);
      success.push(item.id);
    } catch {
      failed.push(item.id);
    }

    onProgress?.(i + 1, itemsWithoutImages.length, item);

    // Rate limiting - wait between generations
    if (i < itemsWithoutImages.length - 1) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  }

  return { success, failed };
}
