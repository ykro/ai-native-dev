import { NextRequest, NextResponse } from "next/server";
import { getOrGenerateImage } from "@/services/imageService";
import { getGearById } from "@/services/inventoryService";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const gearId = searchParams.get("id");

    if (!gearId) {
      return NextResponse.json(
        { error: "Missing gear ID parameter" },
        { status: 400 }
      );
    }

    // Check if gear exists
    const item = await getGearById(gearId);
    if (!item) {
      return NextResponse.json(
        { error: "Gear item not found" },
        { status: 404 }
      );
    }

    // If image already exists, redirect to it
    if (item.imageURL) {
      return NextResponse.redirect(item.imageURL);
    }

    // Generate new image
    const imageURL = await getOrGenerateImage(gearId);

    if (!imageURL) {
      return NextResponse.json(
        { error: "Failed to generate image" },
        { status: 500 }
      );
    }

    // Redirect to the generated image
    return NextResponse.redirect(imageURL);
  } catch (error) {
    console.error("Generate image API error:", error);

    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { gearId } = body;

    if (!gearId) {
      return NextResponse.json(
        { error: "Missing gearId in request body" },
        { status: 400 }
      );
    }

    // Check if gear exists
    const item = await getGearById(gearId);
    if (!item) {
      return NextResponse.json(
        { error: "Gear item not found" },
        { status: 404 }
      );
    }

    // If image already exists, return it
    if (item.imageURL) {
      return NextResponse.json({
        gearId,
        imageURL: item.imageURL,
        generated: false,
        message: "Image already exists",
      });
    }

    // Generate new image
    const imageURL = await getOrGenerateImage(gearId);

    if (!imageURL) {
      return NextResponse.json(
        { error: "Failed to generate image" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      gearId,
      imageURL,
      generated: true,
      message: "Image generated and saved to GCS",
    });
  } catch (error) {
    console.error("Generate image API error:", error);

    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
