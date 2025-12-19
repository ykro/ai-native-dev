import Link from "next/link";
import Image from "next/image";
import { ArrowLeft, MapPin, Share2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UnsplashService } from "@/services/unsplash";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

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

   // Fetch related based on first tag
   const queryTag = destination.tags[0] || 'travel';
   const related = await UnsplashService.fetchRelated(queryTag);

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
               src={destination.urls.full}
               alt={destination.title}
               fill
               className="object-cover transition-transform duration-1000 lg:group-hover:scale-105"
               priority
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20" />

            <div className="absolute bottom-0 left-0 p-8 lg:p-12 w-full text-white">
               {destination.tags.map(tag => (
                  <Badge key={tag} variant="secondary" className="mb-4 mr-2 bg-white/20 hover:bg-white/30 text-white backdrop-blur-md border-0 uppercase tracking-widest text-[10px]">
                     {tag}
                  </Badge>
               ))}
               <h1 className="text-4xl lg:text-6xl font-bold mb-4 tracking-tight leading-none line-clamp-2">{destination.title}</h1>
               <div className="flex items-center gap-2 text-white/80">
                  <MapPin className="h-4 w-4" />
                  <span className="text-sm tracking-wide font-light">{destination.slug}</span>
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
                  {/* Description */}
                  <div className="space-y-2">
                     <p className="text-lg leading-relaxed text-foreground font-light">
                        {destination.description}
                     </p>
                     <p className="text-sm text-muted-foreground italic">
                        Foto por <span className="text-primary">{destination.user.name}</span> en Unsplash.
                     </p>
                  </div>

                  {/* MOCK AI CONTENT: Placeholder until Role 4 */}
                  <div className="space-y-4 pt-4 opacity-50">
                     <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground/80">Esperando Integración AI...</h3>
                     <div className="rounded-xl bg-secondary/30 p-4 mt-6">
                        <p className="text-xs text-muted-foreground/90">
                           La IA Gemini generará el plan aquí en el Rol 4.
                        </p>
                     </div>
                  </div>
               </div>
            </ScrollArea>
         </div>

         {/* RIGHT PANEL: Similar Destinations (20%) */}
         <div className="hidden lg:flex w-[20%] h-full bg-sidebar border-l border-sidebar-border flex-col">
            <div className="p-6 border-b border-sidebar-border">
               <h3 className="text-xs font-bold uppercase tracking-widest text-sidebar-foreground/70">Destinos Similares</h3>
            </div>
            <ScrollArea className="flex-1 p-4">
               <div className="grid gap-4">
                  {related.map(item => (
                     <Link key={item.id} href={`/destino/${item.id}`} className="block group">
                        <div className="aspect-[3/4] rounded-lg overflow-hidden relative mb-2">
                           <Image
                              src={item.urls.small}
                              alt={item.title}
                              fill
                              className="object-cover transition-transform group-hover:scale-110"
                           />
                        </div>
                        <h4 className="text-sm font-medium text-sidebar-foreground truncate group-hover:text-primary transition-colors">{item.title}</h4>
                        <p className="text-[10px] text-muted-foreground">{item.tags[0]}</p>
                     </Link>
                  ))}
               </div>
            </ScrollArea>
         </div>
      </div>
   );
}
