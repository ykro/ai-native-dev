import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  formatDate,
  formatDateRange,
  calculateRentalDays,
  calculateTotalPrice,
  calculateRentalPrice,
  formatPrice,
  isDateInPast,
  isValidRentalRange,
  getMinSelectableDate,
  getDefaultEndDate,
  parseDateSafe,
} from "./date-utils";

describe("date-utils", () => {
  describe("calculateRentalDays", () => {
    it("should return 1 day for same start and end date", () => {
      const date = new Date("2024-01-15");
      expect(calculateRentalDays(date, date)).toBe(1);
    });

    it("should return 2 days for consecutive dates", () => {
      const start = new Date("2024-01-15");
      const end = new Date("2024-01-16");
      expect(calculateRentalDays(start, end)).toBe(2);
    });

    it("should return 7 days for a week rental", () => {
      const start = new Date("2024-01-15");
      const end = new Date("2024-01-21");
      expect(calculateRentalDays(start, end)).toBe(7);
    });

    it("should return 31 days for a full month (January)", () => {
      const start = new Date("2024-01-01");
      const end = new Date("2024-01-31");
      expect(calculateRentalDays(start, end)).toBe(31);
    });

    it("should handle dates across different months", () => {
      const start = new Date("2024-01-28");
      const end = new Date("2024-02-03");
      expect(calculateRentalDays(start, end)).toBe(7);
    });

    it("should handle dates across different years", () => {
      const start = new Date("2024-12-30");
      const end = new Date("2025-01-02");
      expect(calculateRentalDays(start, end)).toBe(4);
    });

    it("should handle leap year February", () => {
      const start = new Date("2024-02-28");
      const end = new Date("2024-03-01");
      expect(calculateRentalDays(start, end)).toBe(3); // Feb 28, Feb 29, Mar 1
    });
  });

  describe("calculateTotalPrice", () => {
    it("should calculate price for 1 day", () => {
      expect(calculateTotalPrice(100, 1)).toBe(100);
    });

    it("should calculate price for 7 days", () => {
      expect(calculateTotalPrice(150, 7)).toBe(1050);
    });

    it("should calculate price for 30 days", () => {
      expect(calculateTotalPrice(200, 30)).toBe(6000);
    });

    it("should handle decimal daily rates", () => {
      expect(calculateTotalPrice(99.99, 3)).toBeCloseTo(299.97);
    });
  });

  describe("calculateRentalPrice", () => {
    it("should return correct breakdown for 1 day rental", () => {
      const start = new Date("2024-01-15");
      const end = new Date("2024-01-15");
      const result = calculateRentalPrice(100, start, end);

      expect(result.days).toBe(1);
      expect(result.dailyRate).toBe(100);
      expect(result.subtotal).toBe(100);
      expect(result.total).toBe(100);
    });

    it("should return correct breakdown for 1 week rental", () => {
      const start = new Date("2024-01-15");
      const end = new Date("2024-01-21");
      const result = calculateRentalPrice(150, start, end);

      expect(result.days).toBe(7);
      expect(result.dailyRate).toBe(150);
      expect(result.subtotal).toBe(1050);
      expect(result.total).toBe(1050);
    });

    it("should return correct breakdown for rental across months", () => {
      const start = new Date("2024-01-28");
      const end = new Date("2024-02-10");
      const result = calculateRentalPrice(200, start, end);

      expect(result.days).toBe(14);
      expect(result.subtotal).toBe(2800);
    });
  });

  describe("formatPrice", () => {
    it("should format price in Mexican Pesos", () => {
      const formatted = formatPrice(1000);
      expect(formatted).toContain("1,000");
      expect(formatted).toContain("$");
    });

    it("should format large prices correctly", () => {
      const formatted = formatPrice(10000);
      expect(formatted).toContain("10,000");
    });

    it("should handle zero", () => {
      const formatted = formatPrice(0);
      expect(formatted).toContain("0");
    });
  });

  describe("formatDate", () => {
    it("should format date in Spanish locale", () => {
      const date = new Date("2024-01-15");
      const formatted = formatDate(date);
      expect(formatted).toContain("15");
      expect(formatted).toContain("enero");
      expect(formatted).toContain("2024");
    });

    it("should return 'Fecha inválida' for invalid date", () => {
      const invalidDate = new Date("invalid");
      expect(formatDate(invalidDate)).toBe("Fecha inválida");
    });
  });

  describe("formatDateRange", () => {
    it("should format date range correctly", () => {
      const start = new Date("2024-01-15");
      const end = new Date("2024-01-20");
      const formatted = formatDateRange(start, end);
      expect(formatted).toContain("-");
      expect(formatted).toContain("15");
      expect(formatted).toContain("20");
    });
  });

  describe("isDateInPast", () => {
    beforeEach(() => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date("2024-06-15"));
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("should return true for past dates", () => {
      expect(isDateInPast(new Date("2024-06-14"))).toBe(true);
      expect(isDateInPast(new Date("2024-01-01"))).toBe(true);
    });

    it("should return false for today", () => {
      expect(isDateInPast(new Date("2024-06-15"))).toBe(false);
    });

    it("should return false for future dates", () => {
      expect(isDateInPast(new Date("2024-06-16"))).toBe(false);
      expect(isDateInPast(new Date("2024-12-31"))).toBe(false);
    });
  });

  describe("isValidRentalRange", () => {
    beforeEach(() => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date("2024-06-15"));
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("should return true for valid future range", () => {
      const start = new Date("2024-06-20");
      const end = new Date("2024-06-25");
      expect(isValidRentalRange(start, end)).toBe(true);
    });

    it("should return true for same day rental starting today", () => {
      const today = new Date("2024-06-15");
      expect(isValidRentalRange(today, today)).toBe(true);
    });

    it("should return false for past start date", () => {
      const start = new Date("2024-06-10");
      const end = new Date("2024-06-20");
      expect(isValidRentalRange(start, end)).toBe(false);
    });

    it("should return false for end date before start date", () => {
      const start = new Date("2024-06-20");
      const end = new Date("2024-06-15");
      expect(isValidRentalRange(start, end)).toBe(false);
    });
  });

  describe("getMinSelectableDate", () => {
    beforeEach(() => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date("2024-06-15T14:30:00"));
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("should return today at start of day", () => {
      const minDate = getMinSelectableDate();
      expect(minDate.getFullYear()).toBe(2024);
      expect(minDate.getMonth()).toBe(5); // June (0-indexed)
      expect(minDate.getDate()).toBe(15);
      expect(minDate.getHours()).toBe(0);
      expect(minDate.getMinutes()).toBe(0);
    });
  });

  describe("getDefaultEndDate", () => {
    it("should return start date + 2 days", () => {
      const start = new Date("2024-06-15");
      const end = getDefaultEndDate(start);
      expect(end.getDate()).toBe(17);
    });
  });

  describe("parseDateSafe", () => {
    it("should parse valid ISO date string", () => {
      const result = parseDateSafe("2024-06-15T00:00:00.000Z");
      expect(result).toBeInstanceOf(Date);
      expect(result?.getFullYear()).toBe(2024);
    });

    it("should return null for invalid date string", () => {
      expect(parseDateSafe("invalid-date")).toBeNull();
    });

    it("should return null for empty string", () => {
      expect(parseDateSafe("")).toBeNull();
    });
  });
});
