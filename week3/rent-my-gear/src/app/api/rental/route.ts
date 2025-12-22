import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { getGearById } from "@/services/inventoryService";
import { calculateRentalPrice, formatPrice } from "@/lib/date-utils";

// Request schema
const rentalRequestSchema = z.object({
  gearId: z.string().min(1),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
});

// Mock rental ID generator
function generateRentalId(): string {
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `RMG-${timestamp}-${random}`;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate request
    const validation = rentalRequestSchema.safeParse(body);
    if (!validation.success) {
      return NextResponse.json(
        {
          error: "Invalid request",
          details: validation.error.issues,
        },
        { status: 400 }
      );
    }

    const { gearId, startDate, endDate } = validation.data;

    // Get gear item
    const item = await getGearById(gearId);
    if (!item) {
      return NextResponse.json(
        { error: "Gear item not found" },
        { status: 404 }
      );
    }

    // Calculate pricing
    const start = new Date(startDate);
    const end = new Date(endDate);
    const pricing = calculateRentalPrice(item.dailyRate, start, end);

    // Generate confirmation
    const confirmation = {
      id: generateRentalId(),
      gearId: item.id,
      gearName: item.name,
      startDate,
      endDate,
      totalDays: pricing.days,
      dailyRate: pricing.dailyRate,
      totalPrice: pricing.total,
      formattedTotal: formatPrice(pricing.total),
      status: "confirmed" as const,
      createdAt: new Date().toISOString(),
    };

    // Log the rental (in production, save to database)
    console.log("Rental confirmed:", confirmation);

    // Simulate a small delay for realism
    await new Promise((resolve) => setTimeout(resolve, 500));

    return NextResponse.json(confirmation, { status: 201 });
  } catch (error) {
    console.error("Rental API error:", error);

    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { message: "Use POST to create a rental" },
    { status: 405 }
  );
}
