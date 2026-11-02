"use client";

import Link from "next/link";
import { Camera, Mountain, Waves } from "lucide-react";
import { CATEGORIES, CategoryId } from "@/lib/validation";
import { cn } from "@/lib/utils";

interface CategoryButtonProps {
  categoryId: CategoryId;
  icon: React.ReactNode;
  className?: string;
}

function CategoryButton({ categoryId, icon, className }: CategoryButtonProps) {
  const category = CATEGORIES[categoryId];

  return (
    <Link
      href={`/category/${categoryId}`}
      className={cn(
        "group relative flex flex-col items-center justify-center",
        "p-8 rounded-2xl",
        "bg-gradient-to-br transition-all duration-300",
        "hover:scale-[1.02] hover:shadow-xl",
        "min-h-[200px] md:min-h-[240px]",
        className
      )}
    >
      <div className="absolute inset-0 rounded-2xl bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity" />

      <div className="relative z-10 flex flex-col items-center text-center">
        <div className="mb-4 p-4 rounded-full bg-white/20 backdrop-blur-sm">
          {icon}
        </div>
        <h3 className="text-xl md:text-2xl font-bold text-white mb-2">
          {category.name}
        </h3>
        <p className="text-sm md:text-base text-white/80 max-w-[250px]">
          {category.description}
        </p>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-4 right-4 w-20 h-20 rounded-full bg-white/10 blur-2xl" />
      <div className="absolute bottom-4 left-4 w-16 h-16 rounded-full bg-white/10 blur-xl" />
    </Link>
  );
}

export function CategoryButtons() {
  return (
    <section className="w-full py-12">
      <div className="container mx-auto px-4">
        <h2 className="text-2xl md:text-3xl font-semibold mb-8 text-center">
          Explora por Categoría
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <CategoryButton
            categoryId="fotografia-video"
            icon={<Camera className="w-10 h-10 text-white" strokeWidth={1.5} />}
            className="from-violet-600 to-purple-700"
          />

          <CategoryButton
            categoryId="montana-camping"
            icon={<Mountain className="w-10 h-10 text-white" strokeWidth={1.5} />}
            className="from-emerald-600 to-teal-700"
          />

          <CategoryButton
            categoryId="deportes-acuaticos"
            icon={<Waves className="w-10 h-10 text-white" strokeWidth={1.5} />}
            className="from-blue-600 to-cyan-700"
          />
        </div>
      </div>
    </section>
  );
}
