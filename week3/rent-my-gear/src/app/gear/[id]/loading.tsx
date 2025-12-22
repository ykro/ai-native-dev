import { Skeleton } from "@/components/ui/skeleton";

export default function GearLoading() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back link skeleton */}
      <Skeleton className="h-5 w-36 mb-6" />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Image skeleton */}
        <Skeleton className="aspect-[4/3] lg:aspect-square rounded-2xl" />

        {/* Details skeleton */}
        <div className="space-y-6">
          <div>
            <Skeleton className="h-6 w-32 mb-3" />
            <Skeleton className="h-10 w-3/4 mb-2" />
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-2/3 mt-1" />
          </div>

          {/* Price skeleton */}
          <Skeleton className="h-10 w-40" />

          {/* Specs skeleton */}
          <div className="rounded-lg border p-4 space-y-3">
            <Skeleton className="h-6 w-48" />
            <div className="grid grid-cols-2 gap-3">
              {[1, 2, 3, 4].map((i) => (
                <div key={i}>
                  <Skeleton className="h-4 w-20 mb-1" />
                  <Skeleton className="h-5 w-24" />
                </div>
              ))}
            </div>
          </div>

          {/* Rental flow skeleton */}
          <div className="space-y-4">
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-12 w-full rounded-lg" />
          </div>
        </div>
      </div>
    </div>
  );
}
