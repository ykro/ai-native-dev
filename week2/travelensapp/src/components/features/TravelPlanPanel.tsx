"use client";

import { useEffect, useState } from "react";
import { Sparkles, Map, Leaf, Coffee, MapPin, Utensils } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

// Import the interface (or duplicate it if sharing is hard across file boundaries in this context)
interface TravelPlan {
    intro: string;
    days: {
        day: number;
        title: string;
        activities: string[];
    }[];
    hiddenGem: {
        title: string;
        description: string;
    };
    localFood: {
        dish: string;
        description: string;
    };
}

interface TravelPlanPanelProps {
    destination: string;
    context?: string;
}

export function TravelPlanPanel({ destination, context }: TravelPlanPanelProps) {
    const [plan, setPlan] = useState<TravelPlan | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPlan = async () => {
            try {
                const res = await fetch("/api/ai-plan", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ destination, context }),
                });
                const data = await res.json();
                if (data.plan) {
                    setPlan(data.plan);
                }
            } catch (error) {
                console.error("Failed to load plan", error);
            } finally {
                setLoading(false);
            }
        };

        fetchPlan();
    }, [destination, context]);

    if (loading) {
        return (
            <div className="space-y-4 pt-4">
                <div className="flex items-center gap-2 text-primary animate-pulse mb-6">
                    <Sparkles className="h-4 w-4" />
                    <span className="text-sm font-medium">Diseñando experiencia única...</span>
                </div>
                {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-32 w-full rounded-xl bg-secondary/30 mb-4" />
                ))}
            </div>
        );
    }

    if (!plan) {
        return (
            <div className="p-6 rounded-lg bg-destructive/5 border border-destructive/20 text-destructive text-sm text-center">
                <p className="font-semibold mb-1">¡Ups!</p>
                <p>Nuestros guías virtuales están ocupados. Intenta recargar.</p>
            </div>
        );
    }

    return (
        <div className="animate-in fade-in duration-700 space-y-6">

            {/* Intro */}
            <div className="bg-primary/5 p-4 rounded-lg border border-primary/10">
                <p className="text-sm text-foreground/80 italic leading-relaxed">
                    "{plan.intro}"
                </p>
            </div>

            {/* Days */}
            <div className="space-y-4">
                {plan.days.map((day) => (
                    <Card key={day.day} className="bg-card border-border/50 shadow-sm overflow-hidden">
                        <CardHeader className="py-3 px-4 bg-muted/30 border-b border-border/50">
                            <CardTitle className="text-sm font-bold flex items-center justify-between">
                                <span className="text-primary">Día {day.day}</span>
                                <span className="text-foreground/70 font-normal truncate max-w-[180px] text-right">{day.title}</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-4">
                            <ul className="space-y-2">
                                {day.activities.map((activity, idx) => (
                                    <li key={idx} className="text-xs text-muted-foreground flex items-start gap-2">
                                        <span className="mt-1.5 h-1 w-1 rounded-full bg-primary shrink-0" />
                                        <span>{activity}</span>
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Recommendations Grid */}
            <div className="grid grid-cols-1 gap-4 pt-2">

                {/* Hidden Gem */}
                <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-xl p-4 border border-indigo-500/20">
                    <div className="flex items-center gap-2 mb-2 text-indigo-600 dark:text-indigo-400">
                        <MapPin className="h-4 w-4" />
                        <h4 className="text-xs font-bold uppercase tracking-wider">Joya Oculta</h4>
                    </div>
                    <p className="text-sm font-semibold text-foreground mb-1">{plan.hiddenGem.title}</p>
                    <p className="text-xs text-muted-foreground leading-relaxed">{plan.hiddenGem.description}</p>
                </div>

                {/* Local Food */}
                <div className="bg-gradient-to-br from-orange-500/10 to-amber-500/10 rounded-xl p-4 border border-orange-500/20">
                    <div className="flex items-center gap-2 mb-2 text-orange-600 dark:text-orange-400">
                        <Utensils className="h-4 w-4" />
                        <h4 className="text-xs font-bold uppercase tracking-wider">Sabor Local</h4>
                    </div>
                    <p className="text-sm font-semibold text-foreground mb-1">{plan.localFood.dish}</p>
                    <p className="text-xs text-muted-foreground leading-relaxed">{plan.localFood.description}</p>
                </div>
            </div>

        </div>
    );
}
