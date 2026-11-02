import { Skeleton } from "@/components/ui/skeleton";
import { GearGridSkeleton } from "@/components/features/GearGrid";

export default function CategoryLoading() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header skeleton */}
      <div className="text-center mb-10">
        <Skeleton className="h-10 w-64 mx-auto mb-3" />
        <Skeleton className="h-6 w-96 mx-auto" />
      </div>

      {/* Search skeleton */}
      <div className="max-w-md mx-auto mb-8">
        <Skeleton className="h-12 w-full" />
      </div>

      {/* Grid skeleton */}
      <GearGridSkeleton count={8} />
    </div>
  );
}
