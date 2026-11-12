import { describe, it, expect, vi, beforeEach } from "vitest";
import { GearItem } from "@/lib/validation";

// Sample gear items
const gearWithoutImage: GearItem = {
  id: "gear-no-image",
  name: "Canon EOS R5",
  category: "fotografia-video",
  description: "Professional mirrorless camera",
  specs: { sensor: "45MP" },
  dailyRate: 500,
  imageURL: null,
};

const gearWithImage: GearItem = {
  id: "gear-with-image",
  name: "North Face Tent",
  category: "montana-camping",
  description: "4-person tent",
  specs: { capacity: "4 persons" },
  dailyRate: 200,
  imageURL: "https://images.unsplash.com/photo-tent.jpg",
};

describe("imageService - Nano Banana Fallback", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("resolveImageUrl", () => {
    it("should return existing imageURL if available", async () => {
      const { resolveImageUrl } = await import("./imageService");
      const result = resolveImageUrl(gearWithImage);
      expect(result).toBe("https://images.unsplash.com/photo-tent.jpg");
    });

    it("should return API endpoint for on-demand generation when no imageURL (Unsplash 404 scenario)", async () => {
      const { resolveImageUrl } = await import("./imageService");
      const result = resolveImageUrl(gearWithoutImage);
      expect(result).toBe("/api/generate-image?id=gear-no-image");
    });
  });

  describe("isImageUrlValid", () => {
    beforeEach(() => {
      global.fetch = vi.fn();
    });

    it("should return true for valid accessible URL", async () => {
      vi.mocked(global.fetch).mockResolvedValue({
        ok: true,
      } as Response);

      const { isImageUrlValid } = await import("./imageService");
      const result = await isImageUrlValid("https://example.com/image.jpg");
      expect(result).toBe(true);
    });

    it("should return false for 404 response (Unsplash image not found)", async () => {
      vi.mocked(global.fetch).mockResolvedValue({
        ok: false,
        status: 404,
      } as Response);

      const { isImageUrlValid } = await import("./imageService");
      const result = await isImageUrlValid("https://images.unsplash.com/404.jpg");
      expect(result).toBe(false);
    });

    it("should return false for network error", async () => {
      vi.mocked(global.fetch).mockRejectedValue(new Error("Network Error"));

      const { isImageUrlValid } = await import("./imageService");
      const result = await isImageUrlValid("https://example.com/image.jpg");
      expect(result).toBe(false);
    });
  });

  describe("Edge Cases - Unsplash 404 Simulation", () => {
    it("should handle item where Unsplash originally returned 404 (null imageURL)", async () => {
      const itemWithUnsplash404: GearItem = {
        id: "unsplash-404-item",
        name: "Rare Equipment",
        category: "deportes-acuaticos",
        description: "Equipment with no Unsplash match",
        specs: { type: "rare" },
        dailyRate: 1000,
        imageURL: null,
      };

      const { resolveImageUrl } = await import("./imageService");
      const resolvedUrl = resolveImageUrl(itemWithUnsplash404);
      expect(resolvedUrl).toBe("/api/generate-image?id=unsplash-404-item");
    });

    it("should identify items needing Nano Banana fallback by null imageURL", () => {
      const itemsNeedingFallback = [gearWithoutImage, gearWithImage].filter(
        (item) => item.imageURL === null
      );

      expect(itemsNeedingFallback).toHaveLength(1);
      expect(itemsNeedingFallback[0].id).toBe("gear-no-image");
    });

    it("should generate correct API endpoint pattern for fallback", async () => {
      const { resolveImageUrl } = await import("./imageService");

      const testCases = [
        { id: "photo-001", expected: "/api/generate-image?id=photo-001" },
        { id: "camp-special", expected: "/api/generate-image?id=camp-special" },
        { id: "water-123", expected: "/api/generate-image?id=water-123" },
      ];

      for (const testCase of testCases) {
        const item: GearItem = {
          ...gearWithoutImage,
          id: testCase.id,
          imageURL: null,
        };
        expect(resolveImageUrl(item)).toBe(testCase.expected);
      }
    });
  });

  describe("Image URL Validation for Fallback Decision", () => {
    beforeEach(() => {
      global.fetch = vi.fn();
    });

    it("should detect when Unsplash URL becomes invalid (simulating 404)", async () => {
      // First, URL is valid
      vi.mocked(global.fetch).mockResolvedValueOnce({ ok: true } as Response);

      const { isImageUrlValid } = await import("./imageService");
      let result = await isImageUrlValid("https://images.unsplash.com/photo.jpg");
      expect(result).toBe(true);

      // Later, URL becomes invalid (Unsplash removed the image)
      vi.mocked(global.fetch).mockResolvedValueOnce({ ok: false, status: 404 } as Response);

      result = await isImageUrlValid("https://images.unsplash.com/photo.jpg");
      expect(result).toBe(false);
    });

    it("should handle timeout when checking Unsplash URL", async () => {
      vi.mocked(global.fetch).mockRejectedValue(new Error("Timeout"));

      const { isImageUrlValid } = await import("./imageService");
      const result = await isImageUrlValid("https://images.unsplash.com/slow.jpg");
      expect(result).toBe(false);
    });
  });
});
