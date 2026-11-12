import { promises as fs } from "fs";
import path from "path";
import { GearItem, CategoryId, validateGearItem, isValidCategory } from "@/lib/validation";

// Path to the inventory JSON file
const INVENTORY_PATH = path.join(process.cwd(), "src", "data", "inventory.json");

// In-memory cache for inventory
let inventoryCache: GearItem[] | null = null;

/**
 * Load inventory from JSON file
 * Uses caching to avoid repeated file reads
 */
export async function loadInventory(): Promise<GearItem[]> {
  if (inventoryCache !== null) {
    return inventoryCache;
  }

  try {
    const data = await fs.readFile(INVENTORY_PATH, "utf-8");
    const rawItems = JSON.parse(data);

    // Validate each item
    const items: GearItem[] = rawItems.map((item: unknown) => validateGearItem(item));

    inventoryCache = items;
    return items;
  } catch (error) {
    console.error("Failed to load inventory:", error);
    throw new Error("Could not load inventory data");
  }
}

/**
 * Save inventory to JSON file
 * Used when AI generates new images
 */
export async function saveInventory(items: GearItem[]): Promise<void> {
  try {
    const data = JSON.stringify(items, null, 2);
    await fs.writeFile(INVENTORY_PATH, data, "utf-8");
    inventoryCache = items;
  } catch (error) {
    console.error("Failed to save inventory:", error);
    throw new Error("Could not save inventory data");
  }
}

/**
 * Get all gear items
 */
export async function getAllGear(): Promise<GearItem[]> {
  return loadInventory();
}

/**
 * Get gear items by category
 */
export async function getGearByCategory(categoryId: string): Promise<GearItem[]> {
  if (!isValidCategory(categoryId)) {
    throw new Error(`Invalid category: ${categoryId}`);
  }

  const items = await loadInventory();
  return items.filter((item) => item.category === categoryId);
}

/**
 * Get a single gear item by ID
 */
export async function getGearById(id: string): Promise<GearItem | null> {
  const items = await loadInventory();
  return items.find((item) => item.id === id) || null;
}

/**
 * Get random gear items for the carousel
 */
export async function getRandomGear(count: number = 5): Promise<GearItem[]> {
  const items = await loadInventory();

  // Fisher-Yates shuffle
  const shuffled = [...items];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }

  return shuffled.slice(0, count);
}

/**
 * Search gear items by name or description
 */
export async function searchGear(query: string): Promise<GearItem[]> {
  const items = await loadInventory();
  const lowerQuery = query.toLowerCase().trim();

  if (!lowerQuery) return items;

  return items.filter(
    (item) =>
      item.name.toLowerCase().includes(lowerQuery) ||
      item.description.toLowerCase().includes(lowerQuery)
  );
}

/**
 * Get gear items that need image generation (no imageURL)
 */
export async function getGearWithoutImages(): Promise<GearItem[]> {
  const items = await loadInventory();
  return items.filter((item) => !item.imageURL);
}

/**
 * Update a gear item's imageURL
 * Used after AI image generation
 */
export async function updateGearImage(gearId: string, imageURL: string): Promise<GearItem | null> {
  const items = await loadInventory();
  const index = items.findIndex((item) => item.id === gearId);

  if (index === -1) return null;

  items[index] = { ...items[index], imageURL };
  await saveInventory(items);

  return items[index];
}

/**
 * Get category statistics
 */
export async function getCategoryStats(): Promise<
  Record<CategoryId, { count: number; withImages: number; withoutImages: number }>
> {
  const items = await loadInventory();

  const stats: Record<CategoryId, { count: number; withImages: number; withoutImages: number }> = {
    "fotografia-video": { count: 0, withImages: 0, withoutImages: 0 },
    "montana-camping": { count: 0, withImages: 0, withoutImages: 0 },
    "deportes-acuaticos": { count: 0, withImages: 0, withoutImages: 0 },
  };

  for (const item of items) {
    stats[item.category].count++;
    if (item.imageURL) {
      stats[item.category].withImages++;
    } else {
      stats[item.category].withoutImages++;
    }
  }

  return stats;
}

/**
 * Clear the inventory cache
 * Useful for development/testing
 */
export function clearInventoryCache(): void {
  inventoryCache = null;
}
