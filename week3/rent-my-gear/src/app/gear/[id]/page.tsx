import { Suspense } from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { RentalFlow } from "@/components/features/RentalFlow";
import { GearImage } from "@/components/features/GearImage";
import { getGearById } from "@/services/inventoryService";
import { CATEGORIES } from "@/lib/validation";
import { formatPrice } from "@/lib/date-utils";

interface GearPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: GearPageProps) {
  const { id } = await params;
  const item = await getGearById(id);

  if (!item) {
    return { title: "Equipo no encontrado" };
  }

  return {
    title: `${item.name} | Rent my Gear`,
    description: item.description,
  };
}

async function GearDetails({ id }: { id: string }) {
  const item = await getGearById(id);

  if (!item) {
    notFound();
  }

  const category = CATEGORIES[item.category];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Image */}
      <div className="relative aspect-[4/3] lg:aspect-square rounded-2xl overflow-hidden bg-neutral-100">
        <GearImage
          gearId={item.id}
          gearName={item.name}
          initialImageURL={item.imageURL}
        />
      </div>

      {/* Details */}
      <div className="space-y-6">
        <div>
          <Link
            href={`/category/${item.category}`}
            className="inline-block mb-3"
          >
            <Badge variant="secondary" className="hover:bg-secondary/80">
              {category.name}
            </Badge>
          </Link>
          <h1 className="text-3xl md:text-4xl font-bold">{item.name}</h1>
          <p className="text-lg text-muted-foreground mt-2">
            {item.description}
          </p>
        </div>

        {/* Price */}
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-primary">
            {formatPrice(item.dailyRate)}
          </span>
          <span className="text-lg text-muted-foreground">/ día</span>
        </div>

        {/* Specifications */}
        <Card>
          <CardContent className="p-4">
            <h2 className="font-semibold mb-3">Especificaciones Técnicas</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Object.entries(item.specs).map(([key, value]) => (
                <div key={key} className="flex justify-between sm:flex-col">
                  <dt className="text-sm text-muted-foreground capitalize">
                    {key}
                  </dt>
                  <dd className="font-medium">{String(value)}</dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>

        {/* Rental Flow */}
        <RentalFlow item={item} />
      </div>
    </div>
  );
}

function GearDetailsSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <Skeleton className="aspect-[4/3] lg:aspect-square rounded-2xl" />
      <div className="space-y-6">
        <div>
          <Skeleton className="h-6 w-32 mb-3" />
          <Skeleton className="h-10 w-3/4 mb-2" />
          <Skeleton className="h-6 w-full" />
        </div>
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-48 w-full rounded-lg" />
        <Skeleton className="h-32 w-full rounded-lg" />
      </div>
    </div>
  );
}

export default async function GearPage({ params }: GearPageProps) {
  const { id } = await params;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back link */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Volver al catálogo
      </Link>

      <Suspense fallback={<GearDetailsSkeleton />}>
        <GearDetails id={id} />
      </Suspense>
    </div>
  );
}
