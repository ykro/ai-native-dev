import { SearchBar } from "@/components/features/SearchBar";
import { MasonryGrid } from "@/components/features/MasonryGrid";
import { UnsplashService } from "@/services/unsplash";

// Use Revalidation to keep "Popular" fresh but not realtime
export const revalidate = 0; // Disable cache as requested

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const query = (await searchParams).q;

  // Server-side Fetching (Directly calling Service, not via API Route)
  // This is better for Performance in App Router (Server Components)
  let items = [];

  if (query) {
    items = await UnsplashService.searchDestinations(query);
  } else {
    items = await UnsplashService.fetchPopular();
  }

  return (
    <main className="min-h-screen bg-background relative selection:bg-primary/20">
      {/* Hero Section */}
      <div className="sticky top-0 z-50 w-full bg-background/80 backdrop-blur-xl border-b border-border transition-all duration-300">
        <div className="container mx-auto px-4 py-4 flex flex-col items-center gap-4">
          <div className="text-center space-y-1">
            <h1 className="text-2xl font-bold tracking-tight text-primary">TraveLens</h1>
            <p className="text-xs text-muted-foreground uppercase tracking-[0.2em]">Explora. Sueña. Descubre.</p>
          </div>
          <div className="w-full">
            {/* SearchBar needs to update URL query params to trigger re-render */}
            <SearchBar />
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="container mx-auto px-0 sm:px-4 py-6">
        <MasonryGrid items={items} />

        {items.length === 0 && (
          <div className="py-20 text-center">
            <p className="text-muted-foreground">No se encontraron destinos.</p>
          </div>
        )}

        <div className="py-12 text-center text-muted-foreground/50 text-sm">
          ~ Fin de los resultados ~
        </div>
      </div>
    </main>
  );
}
