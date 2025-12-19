"use client";

import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";

export function SearchBar() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [term, setTerm] = useState(searchParams.get("q") || "");

    // Debounce effect could go here, but for simplicity we use Enter key or standard form behavior
    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (term.trim()) {
            router.push(`/?q=${encodeURIComponent(term)}`);
        } else {
            router.push('/');
        }
    };

    return (
        <form onSubmit={handleSearch} className="relative w-full max-w-xl mx-auto group">
            <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-muted-foreground group-focus-within:text-primary transition-colors">
                <Search className="h-5 w-5" />
            </div>
            <Input
                type="text"
                value={term}
                onChange={(e) => setTerm(e.target.value)}
                placeholder="¿A dónde sueñas viajar hoy?..."
                className="pl-10 h-12 rounded-full border-border/60 bg-background/50 backdrop-blur-md shadow-sm 
                   focus-visible:ring-primary/20 focus-visible:border-primary transition-all text-lg
                   placeholder:text-muted-foreground/70"
            />
        </form>
    );
}
