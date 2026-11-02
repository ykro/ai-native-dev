"use client";

import { useEffect, useState } from "react";
import { Sparkles, MapPin, Utensils, Share2 } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
// Actually I'll use simple alert or just console if toast isn't available. 
// Checking package.json would be good, but I'll stick to safe vanilla JS alerts or check later.
// I will assume no toast library for now and just use console/alert fallback or UI feedback if needed.
// Update: User has shadcn/ui, usually comes with sonner or toaster. I'll stick to simple logic first.

import { Destination } from "@/services/unsplash";

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

interface AiTravelSidebarProps {
    destination: Destination;
}

export function AiTravelSidebar({ destination }: AiTravelSidebarProps) {
    const [plan, setPlan] = useState<TravelPlan | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPlan = async () => {
            try {
                const res = await fetch("/api/ai-plan", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        destination: destination.title,
                        context: destination.cityName || destination.location
                    }),
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
    }, [destination]);

    const handleShare = async () => {
        if (typeof navigator.share !== 'function') {
            alert("Tu navegador no soporta compartir nativo.");
            return;
        }

        let shareText = `¡Mira este destino increíble: ${destination.title}!\n\n`;
        shareText += `${destination.description}\n\n`;

        if (plan) {
            shareText += `✨ Plan de Viaje AI:\n${plan.intro}\n\n`;
            plan.days.forEach(day => {
                shareText += `📅 Día ${day.day}: ${day.title}\n`;
                day.activities.forEach(act => shareText += `• ${act}\n`);
                shareText += "\n";
            });
            shareText += `💎 Joya Oculta: ${plan.hiddenGem.title}\n`;
            shareText += `🍽️ Sabor Local: ${plan.localFood.dish}\n`;
        } else {
            shareText += "Descúbrelo en TraveLens.";
        }

        try {
            await navigator.share({
                title: `Viaje a ${destination.title}`,
                text: shareText,
                url: window.location.href,
            });
        } catch (error) {
            console.log("Error sharing:", error);
        }
    };

    return (
        <div className="w-full h-full bg-background border-r border-border flex flex-col relative z-10 shadow-2xl lg:shadow-none">
            {/* Sticky Header */}
            <div className="p-6 border-b border-border bg-background/95 backdrop-blur z-10 flex justify-between items-center sticky top-0">
                <h2 className="font-semibold text-lg flex items-center gap-2 text-primary">
                    <Sparkles className="h-4 w-4 text-purple-500" />
                    <span>Plan de Viaje AI</span>
                </h2>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={handleShare}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Compartir Plan"
                >
                    <Share2 className="h-4 w-4" />
                </Button>
            </div>

            <ScrollArea className="flex-1 p-6">
                <div className="space-y-6 pb-20">


                    {/* AI Plan Content */}
                    {loading ? (
                        <div className="space-y-4 pt-4">
                            <div className="flex items-center gap-2 text-primary animate-pulse mb-6">
                                <Sparkles className="h-4 w-4" />
                                <span className="text-sm font-medium">Diseñando experiencia única...</span>
                            </div>
                            {[1, 2, 3].map((i) => (
                                <Skeleton key={i} className="h-32 w-full rounded-xl bg-secondary/30 mb-4" />
                            ))}
                        </div>
                    ) : plan ? (
                        <div className="animate-in fade-in duration-700 space-y-6">
                            {/* Intro */}
                            <div className="bg-primary/5 p-4 rounded-lg border border-primary/10">
                                <p className="text-sm text-foreground/80 italic leading-relaxed">
                                    &quot;{plan.intro}&quot;
                                </p>
                            </div>

                            {/* Days */}
                            <div className="space-y-4">
                                {plan.days.map((day) => (
                                    <Card key={day.day} className="bg-card border-border/50 shadow-sm overflow-hidden group hover:border-primary/20 transition-all">
                                        <CardHeader className="py-3 px-4 bg-muted/30 border-b border-border/50">
                                            <CardTitle className="text-sm font-bold flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <Badge variant="outline" className="bg-background text-primary border-primary/20">Día {day.day}</Badge>
                                                </div>
                                                <span className="text-foreground/70 font-normal truncate max-w-[150px] text-right text-xs">{day.title}</span>
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
                    ) : (
                        <div className="p-6 rounded-lg bg-destructive/5 border border-destructive/20 text-destructive text-sm text-center">
                            <p className="font-semibold mb-1">¡Ups!</p>
                            <p>Nuestros guías virtuales están ocupados. Intenta recargar.</p>
                        </div>
                    )}
                </div>
            </ScrollArea>
        </div>
    );
}
