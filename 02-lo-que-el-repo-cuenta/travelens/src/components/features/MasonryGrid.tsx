"use client";

import Image from "next/image";
import Link from "next/link";

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
                    href={`/destination/${item.id}`}
                    className="group block relative break-inside-avoid rounded-xl overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
                >
                    <div className="relative">
                        <Image
                            src={item.urls.small} // OPTIMIZATION: Use small as requested
                            alt={item.description || item.title}
                            width={600}
                            height={800}
                            // Increased duration as user seems to like premium feel
                            className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        {/* Overlay Gradient on hover */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                        {/* Text: Hover Only (Reverted as requested) */}
                        <div className="absolute bottom-0 left-0 p-4 w-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 translate-y-2 group-hover:translate-y-0 bg-gradient-to-t from-black/80 to-transparent">
                            {/* Uses gridTitle if available (Custom Logic), falls back to normal title */}
                            <h3 className="text-white font-bold text-lg leading-tight mb-1 font-sans shadow-black drop-shadow-md">
                                {item.gridTitle || item.location || item.title}
                            </h3>
                            {/* Uses gridSubtitle if available */}
                            <p className="text-white/90 text-xs line-clamp-2 font-medium">
                                {item.gridSubtitle || item.tags.slice(0, 3).join(' • ')}
                            </p>
                        </div>
                    </div>
                </Link>
            ))}
        </div>
    );
}
