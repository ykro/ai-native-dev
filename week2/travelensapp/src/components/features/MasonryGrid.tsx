"use client";

import Image from "next/image";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

/* eslint-disable @typescript-eslint/no-explicit-any */
interface MasonryGridProps {
    items: any[];
}

export function MasonryGrid({ items }: MasonryGridProps) {
    return (
        <div className="columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-4 space-y-4 p-4">
            {items.map((item) => (
                <Link
                    key={item.id}
                    href={`/destino/${item.id}`}
                    className="group block relative break-inside-avoid rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                >
                    <div className="relative">
                        <Image
                            src={item.urls.regular}
                            alt={item.description || item.title}
                            width={600}
                            height={800}
                            className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        {/* Overlay Gradient on hover */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                        <div className="absolute bottom-0 left-0 p-4 w-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 translate-y-2 group-hover:translate-y-0">
                            <h3 className="text-white font-medium text-lg leading-tight mb-1 font-sans">{item.title || "Destino Desconocido"}</h3>
                            <p className="text-white/80 text-xs line-clamp-1">{item.user.name}</p>
                        </div>

                        {/* Tag Badge */}
                        {item.tags && item.tags[0] && (
                            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-all duration-300">
                                <Badge variant="secondary" className="bg-white/90 text-foreground backdrop-blur-sm text-[10px] uppercase tracking-wider font-bold shadow-sm">
                                    {item.tags[0]}
                                </Badge>
                            </div>
                        )}
                    </div>
                </Link>
            ))}
        </div>
    );
}
