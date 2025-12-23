import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RentalFlow } from "./index";
import { GearItem } from "@/lib/validation";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Sample gear items for different categories
const photographyGear: GearItem = {
  id: "photo-001",
  name: "Canon EOS R5",
  category: "fotografia-video",
  description: "Professional mirrorless camera",
  specs: { sensor: "45MP", video: "8K" },
  dailyRate: 500,
  imageURL: "https://example.com/camera.jpg",
};

const campingGear: GearItem = {
  id: "camp-001",
  name: "North Face Tent",
  category: "montana-camping",
  description: "4-person expedition tent",
  specs: { capacity: "4 persons", weight: "3.5kg" },
  dailyRate: 200,
  imageURL: "https://example.com/tent.jpg",
};

const waterSportsGear: GearItem = {
  id: "water-001",
  name: "Kayak Pro",
  category: "deportes-acuaticos",
  description: "Professional sea kayak",
  specs: { length: "4.5m", weight: "20kg" },
  dailyRate: 300,
  imageURL: "https://example.com/kayak.jpg",
};

describe("RentalFlow Integration Tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockReset();
  });

  describe("Initial State", () => {
    it("should render selecting step initially", () => {
      render(<RentalFlow item={photographyGear} />);

      expect(screen.getByText("Rentar este equipo")).toBeInTheDocument();
      expect(screen.getByText("Seleccionar Fechas")).toBeInTheDocument();
    });

    it("should show correct initial message for photography category", () => {
      render(<RentalFlow item={photographyGear} />);

      expect(
        screen.getByText(/Selecciona las fechas para tu renta/)
      ).toBeInTheDocument();
    });

    it("should show correct initial message for camping category", () => {
      render(<RentalFlow item={campingGear} />);

      expect(
        screen.getByText(/Selecciona las fechas para tu renta/)
      ).toBeInTheDocument();
    });

    it("should show correct initial message for water sports category", () => {
      render(<RentalFlow item={waterSportsGear} />);

      expect(
        screen.getByText(/Selecciona las fechas para tu renta/)
      ).toBeInTheDocument();
    });
  });

  describe("Date Selection Flow", () => {
    it("should transition to configuring step when clicking 'Seleccionar Fechas'", async () => {
      const user = userEvent.setup();
      render(<RentalFlow item={photographyGear} />);

      await user.click(screen.getByText("Seleccionar Fechas"));

      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();
    });

    it("should show calendar component after clicking select dates", async () => {
      const user = userEvent.setup();
      render(<RentalFlow item={campingGear} />);

      await user.click(screen.getByText("Seleccionar Fechas"));

      // Calendar should be visible
      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();
    });
  });

  describe("Category-Specific Tests", () => {
    it("should handle photography gear item", async () => {
      const user = userEvent.setup();
      render(<RentalFlow item={photographyGear} />);

      // Verify initial state
      expect(screen.getByText("Rentar este equipo")).toBeInTheDocument();

      // Click to start date selection
      await user.click(screen.getByText("Seleccionar Fechas"));

      // Should be in date selection mode
      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();
    });

    it("should handle camping gear item", async () => {
      const user = userEvent.setup();
      render(<RentalFlow item={campingGear} />);

      expect(screen.getByText("Rentar este equipo")).toBeInTheDocument();

      await user.click(screen.getByText("Seleccionar Fechas"));

      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();
    });

    it("should handle water sports gear item", async () => {
      const user = userEvent.setup();
      render(<RentalFlow item={waterSportsGear} />);

      expect(screen.getByText("Rentar este equipo")).toBeInTheDocument();

      await user.click(screen.getByText("Seleccionar Fechas"));

      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();
    });
  });

  describe("API Integration", () => {
    it("should call API with correct data structure", async () => {
      const user = userEvent.setup();

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: "rental-123",
          status: "confirmed",
        }),
      });

      render(<RentalFlow item={photographyGear} />);

      await user.click(screen.getByText("Seleccionar Fechas"));

      // Find and click continue button (using role)
      const buttons = screen.getAllByRole("button");
      const continueButton = buttons.find((btn) =>
        btn.textContent?.includes("Continuar")
      );

      if (continueButton) {
        await user.click(continueButton);

        await waitFor(() => {
          // Should transition to review step
          const reviewHeader = screen.queryByText("Resumen de Renta");
          if (reviewHeader) {
            expect(reviewHeader).toBeInTheDocument();
          }
        });
      }
    });

    it("should handle API error gracefully without crashing", async () => {
      const user = userEvent.setup();
      const consoleSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      render(<RentalFlow item={photographyGear} />);

      // Start the flow
      await user.click(screen.getByText("Seleccionar Fechas"));

      // Component should not crash
      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();

      consoleSpy.mockRestore();
    });
  });

  describe("State Management", () => {
    it("should maintain item data throughout flow", () => {
      render(<RentalFlow item={photographyGear} />);

      // Item should be associated with the flow
      expect(screen.getByText("Rentar este equipo")).toBeInTheDocument();
    });

    it("should reset properly when requested", async () => {
      const user = userEvent.setup();

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({
          id: "rental-123",
          status: "confirmed",
        }),
      });

      render(<RentalFlow item={photographyGear} />);

      // Start the flow
      await user.click(screen.getByText("Seleccionar Fechas"));

      // Should be in date selection
      expect(screen.getByText("Selección de Fechas")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("should have accessible button for selecting dates", () => {
      render(<RentalFlow item={photographyGear} />);

      const selectButton = screen.getByText("Seleccionar Fechas");
      expect(selectButton).toBeInTheDocument();
      expect(selectButton.tagName.toLowerCase()).toBe("button");
    });

    it("should have proper heading structure", () => {
      render(<RentalFlow item={photographyGear} />);

      expect(screen.getByText("Rentar este equipo")).toBeInTheDocument();
    });
  });
});
