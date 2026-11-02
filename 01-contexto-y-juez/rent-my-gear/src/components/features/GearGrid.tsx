"use client";

import { useState, useMemo } from "react";
import Image from "next/image";
import Link from "next/link";
import { Search } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { GearItem, CATEGORIES } from "@/lib/validation";
import { formatPrice } from "@/lib/date-utils";

interface GearGridProps {
  items: GearItem[];
  showSearch?: boolean;
  showCategory?: boolean;
}

export function GearGrid({
  items,
  showSearch = true,
  showCategory = true,
}: GearGridProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const filteredItems = useMemo(() => {
    if (!searchQuery.trim()) return items;

    const query = searchQuery.toLowerCase();
    return items.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query)
    );
  }, [items, searchQuery]);

  return (
    <div className="w-full">
      {showSearch && (
        <div className="relative max-w-md mx-auto mb-8">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Buscar equipo..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 h-12 text-base"
          />
        </div>
      )}

      {filteredItems.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground text-lg">
            No se encontró equipo que coincida con tu búsqueda.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredItems.map((item) => (
            <GearCard key={item.id} item={item} showCategory={showCategory} />
          ))}
        </div>
      )}
    </div>
  );
}

interface GearCardProps {
  item: GearItem;
  showCategory?: boolean;
}

function GearCard({ item, showCategory = true }: GearCardProps) {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  return (
    <Link href={`/gear/${item.id}`}>
      <Card className="overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer h-full group">
        <div className="relative aspect-[4/3] bg-neutral-100">
          {item.imageURL && !imageError ? (
            <>
              {imageLoading && (
                <Skeleton className="absolute inset-0" />
              )}
              <Image
                src={item.imageURL}
                alt={item.name}
                fill
                className={`object-cover transition-opacity duration-300 group-hover:scale-105 transition-transform ${
                  imageLoading ? "opacity-0" : "opacity-100"
                }`}
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                onLoad={() => setImageLoading(false)}
                onError={() => {
                  setImageError(true);
                  setImageLoading(false);
                }}
              />
            </>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center bg-neutral-100">
              <div className="text-center p-4">
                <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-neutral-200 flex items-center justify-center">
                  <span className="text-2xl">📷</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  Imagen no disponible
                </span>
              </div>
            </div>
          )}

          {showCategory && (
            <Badge variant="secondary" className="absolute top-3 left-3">
              {CATEGORIES[item.category].name}
            </Badge>
          )}
        </div>

        <CardContent className="p-4">
          <h3 className="font-semibold text-base line-clamp-1 group-hover:text-primary transition-colors">
            {item.name}
          </h3>
          <p className="text-sm text-muted-foreground line-clamp-2 mt-1 min-h-[40px]">
            {item.description}
          </p>
          <div className="mt-3 flex items-baseline gap-1">
            <span className="text-lg font-bold text-primary">
              {formatPrice(item.dailyRate)}
            </span>
            <span className="text-sm text-muted-foreground">/día</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

// Loading skeleton for the grid
export function GearGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} className="overflow-hidden">
          <Skeleton className="aspect-[4/3]" />
          <CardContent className="p-4">
            <Skeleton className="h-5 w-3/4 mb-2" />
            <Skeleton className="h-4 w-full mb-1" />
            <Skeleton className="h-4 w-2/3 mb-3" />
            <Skeleton className="h-6 w-1/3" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
