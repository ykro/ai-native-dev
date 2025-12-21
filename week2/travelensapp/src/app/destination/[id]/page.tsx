import Link from "next/link";
import Image from "next/image";
import { ArrowLeft, Share2, MapPin } from "lucide-react"; // Restored MapPin for context usage if needed, usually just Compass
import { Button } from "@/components/ui/button";
import { UnsplashService } from "@/services/unsplash";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { TravelPlanPanel } from "@/components/features/TravelPlanPanel";

// Using real data fetching
export default async function DestinationPage({
   params,
}: {
   params: Promise<{ id: string }>;
}) {
   const { id } = await params;
   const destination = await UnsplashService.fetchById(id);

   // Handle Not Found
   if (!destination) {
      return <div className="p-10 text-center">Destino no encontrado.</div>;
   }

   // Fetch related using smart context
   const baseContext = destination.location || destination.title;
   const related = await UnsplashService.fetchRelated(
      baseContext,
      destination.tags,
      destination.id, // exclude current
      destination.cityName // fallback city for second query!
   );

   return (
      <div className="h-screen w-full bg-background flex flex-col lg:flex-row overflow-hidden">

         {/* LEFT PANEL: Immersive Image (50%) */}
         <div className="w-full lg:w-1/2 h-[40vh] lg:h-full relative group">
            <Link
               href="/"
               className="absolute top-6 left-6 z-20"
            >
               <Button variant="outline" size="icon" className="rounded-full bg-white/20 backdrop-blur-md border-white/30 text-white hover:bg-white/40 hover:text-white transition-all">
                  <ArrowLeft className="h-5 w-5" />
               </Button>
            </Link>

            <Image
               src={destination.urls.regular}
               alt={destination.title}
               fill
               className="object-cover transition-transform duration-1000 lg:group-hover:scale-105"
               priority
               sizes="(max-width: 768px) 100vw, 50vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20" />

            <div className="absolute bottom-0 left-0 p-8 lg:p-12 w-full text-white">
               {/* Location / Compass Removed as requested for Main Photo */}
               {/* Just Title and Tags */}

               <h1 className="text-4xl lg:text-6xl font-bold mb-4 tracking-tight leading-none line-clamp-2 shadow-black drop-shadow-lg">
                  {destination.title}
               </h1>

               <div className="flex flex-wrap gap-2">
                  {destination.tags.map(tag => (
                     <Badge key={tag} variant="secondary" className="bg-white/20 hover:bg-white/30 text-white backdrop-blur-md border-0 uppercase tracking-widest text-[10px]">
                        {tag}
                     </Badge>
                  ))}
               </div>
            </div>
         </div>

         {/* CENTER PANEL: AI Travel Plan (30%) */}
         <div className="w-full lg:w-[30%] h-full bg-background border-r border-border flex flex-col relative z-10 shadow-2xl lg:shadow-none">
            <div className="p-6 border-b border-border bg-background/95 backdrop-blur z-10 flex justify-between items-center sticky top-0">
               <h2 className="font-semibold text-lg flex items-center gap-2 text-primary">
                  ✨ Plan de Viaje AI
               </h2>
               <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary">
                  <Share2 className="h-4 w-4" />
               </Button>
            </div>

            <ScrollArea className="flex-1 p-6">
               <div className="space-y-6 pb-20">
                  <div className="space-y-2">
                     <p className="text-lg leading-relaxed text-foreground font-light">
                        {destination.description}
                     </p>
                     <p className="text-sm text-muted-foreground italic">
                        Foto por <span className="text-primary">{destination.user.name}</span> en Unsplash.
                     </p>
                  </div>

                  {/* AI Integrated Panel */}
                  <TravelPlanPanel
                     destination={destination.title}
                     context={destination.cityName || destination.location} // Pass more context if available
                  />

               </div>
            </ScrollArea>
         </div>

         {/* RIGHT PANEL: Similar Destinations (20%) */}
         <div className="hidden lg:flex w-[20%] h-full bg-sidebar border-l border-sidebar-border flex-col">
            <div className="p-6 border-b border-sidebar-border">
               <h3 className="text-xs font-bold uppercase tracking-widest text-sidebar-foreground/70">Destinos Similares</h3>
            </div>
            <ScrollArea className="flex-1 p-2">
               {/* Bento Grid: 2 Columns, variable spans. Pattern repeats every 6 items or so. */}
               <div className="grid grid-cols-2 gap-2 auto-rows-[80px]">
                  {related.map((item, index) => {
                     // Bento Logic: Define classes based on index to create visual rhythm
                     // 0: Big Hero (2x2)
                     // 1, 2: Standard (1x1)
                     // 3: Tall (1x2)
                     // 4, 5: Standard (1x1)
                     // 6: Wide (2x1)
                     // 7: Standard (1x1)
                     const spans = [
                        "col-span-2 row-span-2", // 0: Big
                        "col-span-1 row-span-1", // 1
                        "col-span-1 row-span-1", // 2
                        "col-span-1 row-span-2", // 3: Tall side
                        "col-span-1 row-span-1", // 4
                        "col-span-1 row-span-1", // 5
                        "col-span-2 row-span-1", // 6: Wide strip
                        "col-span-1 row-span-1"  // 7
                     ];
                     const spanClass = spans[index] || "col-span-1 row-span-1";

                     return (
                        <Link key={item.id} href={`/destination/${item.id}`} className={`block group relative overflow-hidden rounded-md ${spanClass}`}>
                           <Image
                              src={index === 0 ? item.urls.small : item.urls.thumb} // First one gets better resolution
                              alt={item.title}
                              fill
                              className="object-cover transition-transform duration-700 group-hover:scale-110"
                              sizes="(max-width: 1200px) 25vw, 15vw"
                           />
                           <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors" />
                        </Link>
                     );
                  })}
               </div>
            </ScrollArea>
         </div>
      </div>
   );
}
