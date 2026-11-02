"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { Loader2 } from "lucide-react";

interface GearImageProps {
  gearId: string;
  gearName: string;
  initialImageURL: string | null;
}

export function GearImage({ gearId, gearName, initialImageURL }: GearImageProps) {
  const [imageURL, setImageURL] = useState<string | null>(initialImageURL);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only trigger generation if there's no image
    if (initialImageURL) return;

    const generateImage = async () => {
      setIsGenerating(true);
      setError(null);

      try {
        const response = await fetch("/api/generate-image", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ gearId }),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.error || "Failed to generate image");
        }

        const data = await response.json();
        setImageURL(data.imageURL);
      } catch (err) {
        console.error("Image generation failed:", err);
        setError(err instanceof Error ? err.message : "Error generating image");
      } finally {
        setIsGenerating(false);
      }
    };

    generateImage();
  }, [gearId, initialImageURL]);

  // Show loading spinner while generating
  if (isGenerating) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-neutral-50">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 mx-auto animate-spin text-primary" />
          <div className="space-y-1">
            <p className="font-medium text-neutral-700">Generando imagen con IA...</p>
            <p className="text-sm text-muted-foreground">
              Esto puede tomar unos segundos
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !imageURL) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-neutral-50">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
            <span className="text-4xl">⚠️</span>
          </div>
          <p className="text-muted-foreground">No se pudo generar la imagen</p>
          <p className="text-sm text-red-500 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  // Show image if available
  if (imageURL) {
    return (
      <Image
        src={imageURL}
        alt={gearName}
        fill
        className="object-cover"
        sizes="(max-width: 1024px) 100vw, 50vw"
        priority
      />
    );
  }

  // Fallback: No image available
  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="text-center">
        <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-neutral-200 flex items-center justify-center">
          <span className="text-4xl">📷</span>
        </div>
        <p className="text-muted-foreground">Imagen no disponible</p>
      </div>
    </div>
  );
}
