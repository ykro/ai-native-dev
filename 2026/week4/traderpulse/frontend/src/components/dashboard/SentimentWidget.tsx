'use client';

import useSWR from 'swr';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BrainCircuit, ThumbsUp, ThumbsDown, Minus } from "lucide-react";

const fetcher = (url: string) => fetch(url).then(r => r.json());
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Props {
    symbol: string;
}

export default function SentimentWidget({ symbol }: Props) {
    const { data, error, isLoading } = useSWR(`${API_URL}/sentiment/${symbol}`, fetcher, {
        revalidateOnFocus: false,
        shouldRetryOnError: false
    });

    if (!symbol) return null;

    if (error) return (
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
            <CardContent className="pt-6 text-red-400">Error obteniendo análisis</CardContent>
        </Card>
    );

    return (
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-lg">
                    <BrainCircuit className="text-cyan-400" size={20} />
                    <span>Análisis Gemini AI: <span className="text-cyan-400 font-bold">{symbol}</span></span>
                </CardTitle>
            </CardHeader>
            <CardContent>
                {isLoading ? (
                    <div className="space-y-3">
                        <Skeleton className="h-6 w-1/3 bg-slate-800" />
                        <Skeleton className="h-20 w-full bg-slate-800" />
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                            <span className="text-sm text-slate-400 uppercase tracking-wide">Sentimiento:</span>
                            <div className={`px-3 py-1 rounded-full text-sm font-bold flex items-center gap-2 
                                ${data.sentiment === "Bullish" ? "bg-green-500/20 text-green-400 border border-green-500/30" :
                                    data.sentiment === "Bearish" ? "bg-red-500/20 text-red-400 border border-red-500/30" :
                                        "bg-slate-500/20 text-slate-400 border border-slate-500/30"}`}>
                                {data.sentiment === "Bullish" && <ThumbsUp size={14} />}
                                {data.sentiment === "Bearish" && <ThumbsDown size={14} />}
                                {data.sentiment === "Neutral" && <Minus size={14} />}
                                {data.sentiment}
                            </div>
                        </div>
                        <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                            <p className="text-slate-300 text-sm leading-relaxed italic">
                                "{data.justification}"
                            </p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
