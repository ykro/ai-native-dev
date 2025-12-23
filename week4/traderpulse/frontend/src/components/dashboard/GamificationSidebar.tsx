'use client';

import useSWR from 'swr';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Star, TrendingUp } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

const fetcher = (url: string) => fetch(url).then(r => r.json());

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function GamificationSidebar() {
    const { data, error, isLoading } = useSWR(`${API_URL}/gamification/status`, fetcher);

    if (error) return (
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
            <CardContent className="pt-6 text-red-400 text-sm">Error cargando perfil</CardContent>
        </Card>
    );

    return (
        <Card className="bg-slate-900 border-slate-800 text-slate-100 h-full">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-lg">
                    <Trophy className="text-yellow-500" size={20} />
                    <span>Tu Perfil</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {isLoading ? (
                    <div className="space-y-2">
                        <Skeleton className="h-4 w-[100px] bg-slate-800" />
                        <Skeleton className="h-20 w-full bg-slate-800" />
                    </div>
                ) : (
                    <>
                        <div className="text-center p-4 bg-slate-800/50 rounded-lg">
                            <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Nivel Actual</p>
                            <h3 className="text-xl font-bold text-blue-400">{data.investor_level}</h3>
                            <div className="mt-2 text-xs text-slate-500">Próximo nivel: {data.next_level_progress}%</div>
                        </div>

                        <div className="flex items-center justify-between p-3 bg-slate-800/30 rounded-lg border border-slate-700">
                            <span className="flex items-center text-sm text-slate-300">
                                <Star className="text-purple-400 mr-2" size={16} /> Puntos
                            </span>
                            <span className="font-mono font-bold text-lg">{data.analysis_points}</span>
                        </div>

                        <div>
                            <p className="text-xs text-slate-500 mb-3 uppercase font-semibold">Insignias</p>
                            <div className="flex flex-wrap gap-2">
                                {data.badges.map((badge: string) => (
                                    <Badge key={badge} variant="secondary" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 border-yellow-500/20">
                                        {badge}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </CardContent>
        </Card>
    );
}
