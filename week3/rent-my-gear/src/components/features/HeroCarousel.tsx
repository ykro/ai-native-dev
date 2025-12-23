"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import Image from "next/image";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  type CarouselApi,
} from "@/components/ui/carousel";
import { GearItem, CATEGORIES } from "@/lib/validation";
import { formatPrice } from "@/lib/date-utils";

interface HeroCarouselProps {
  items: GearItem[];
}

export function HeroCarousel({ items }: HeroCarouselProps) {
  const [api, setApi] = useState<CarouselApi>();
  const [current, setCurrent] = useState(Math.floor(Math.random() * items.length));
  const isInitialized = useRef(false);

  const onSelect = useCallback(() => {
    if (!api) return;
    setCurrent(api.selectedScrollSnap());
  }, [api]);

  useEffect(() => {
    if (!api) return;

    // Only set initial state once
    if (!isInitialized.current) {
      isInitialized.current = true;
      // Defer to avoid setState in effect
      requestAnimationFrame(() => {
        setCurrent(api.selectedScrollSnap());
      });
    }

    api.on("select", onSelect);
    return () => {
      api.off("select", onSelect);
    };
  }, [api, onSelect]);

  // Autoplay
  useEffect(() => {
    if (!api) return;

    const interval = setInterval(() => {
      api.scrollNext();
    }, 5000);

    return () => clearInterval(interval);
  }, [api]);

  if (items.length === 0) {
    return null;
  }

  return (
    <section className="w-full py-8">
      <div className="container mx-auto px-4">
        <h2 className="text-2xl font-semibold mb-6 text-center">
          Equipo Destacado
        </h2>

        <Carousel
          setApi={setApi}
          opts={{
            align: "center",
            loop: true,
          }}
          className="w-full max-w-5xl mx-auto"
        >
          <CarouselContent className="-ml-2 md:-ml-4">
            {items.map((item, index) => (
              <CarouselItem
                key={item.id}
                className="pl-2 md:pl-4 md:basis-1/2 lg:basis-1/3"
              >
                <Link href={`/gear/${item.id}`}>
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer h-full">
                    <div className="relative aspect-[4/3] bg-neutral-100">
                      {item.imageURL ? (
                        <Image
                          src={item.imageURL}
                          alt={item.name}
                          fill
                          className="object-cover"
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                          priority={index < 2}
                        />
                      ) : (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-neutral-400 text-sm">
                            Cargando imagen...
                          </div>
                        </div>
                      )}
                      <Badge
                        variant="secondary"
                        className="absolute top-3 left-3"
                      >
                        {CATEGORIES[item.category].name}
                      </Badge>
                    </div>
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-lg line-clamp-1">
                        {item.name}
                      </h3>
                      <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                        {item.description}
                      </p>
                      <div className="mt-3 flex items-center justify-between">
                        <span className="text-lg font-bold text-primary">
                          {formatPrice(item.dailyRate)}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          /día
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious className="hidden md:flex -left-12" />
          <CarouselNext className="hidden md:flex -right-12" />
        </Carousel>

        {/* Dots indicator */}
        <div className="flex justify-center gap-2 mt-4">
          {items.map((_, index) => (
            <button
              key={index}
              className={`w-2 h-2 rounded-full transition-colors ${
                index === current ? "bg-primary" : "bg-neutral-300"
              }`}
              onClick={() => api?.scrollTo(index)}
              aria-label={`Ir al slide ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
