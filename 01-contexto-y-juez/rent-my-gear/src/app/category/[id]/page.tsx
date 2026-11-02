import { Suspense } from "react";
import { notFound } from "next/navigation";
import { GearGrid, GearGridSkeleton } from "@/components/features/GearGrid";
import { getGearByCategory } from "@/services/inventoryService";
import { CATEGORIES, isValidCategory, CategoryId } from "@/lib/validation";

interface CategoryPageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: CategoryPageProps) {
  const { id } = await params;

  if (!isValidCategory(id)) {
    return { title: "Categoría no encontrada" };
  }

  const category = CATEGORIES[id as CategoryId];
  return {
    title: `${category.name} | Rent my Gear`,
    description: category.description,
  };
}

async function CategoryGear({ categoryId }: { categoryId: CategoryId }) {
  const items = await getGearByCategory(categoryId);
  return <GearGrid items={items} showCategory={false} />;
}

export default async function CategoryPage({ params }: CategoryPageProps) {
  const { id } = await params;

  if (!isValidCategory(id)) {
    notFound();
  }

  const category = CATEGORIES[id as CategoryId];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-3xl md:text-4xl font-bold mb-3">{category.name}</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {category.description}
        </p>
      </div>

      {/* Gear grid */}
      <Suspense fallback={<GearGridSkeleton count={8} />}>
        <CategoryGear categoryId={id as CategoryId} />
      </Suspense>
    </div>
  );
}
