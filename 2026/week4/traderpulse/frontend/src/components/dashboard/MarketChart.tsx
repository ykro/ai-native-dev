'use client';

import useSWR from 'swr';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

const fetcher = (url: string) => fetch(url).then(r => r.json());
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface Props {
    symbol: string;
}

export default function MarketChart({ symbol }: Props) {
    const { data, error, isLoading } = useSWR(`${API_URL}/stocks/${symbol}`, fetcher);

    if (error) return <div className="text-red-500 text-sm">Error cargando gráfico</div>;
    if (isLoading) return <Skeleton className="h-[300px] w-full bg-slate-800 rounded-xl" />;

    if (!data?.historical || data.historical.length === 0) {
        return <div className="text-slate-400 text-sm p-4">Datos históricos no disponibles</div>;
    }

    const chartData = [...data.historical].sort((a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime());
    const latestPrice = data.realtime?.price ? parseFloat(data.realtime.price) : 0;
    const changeColor = "#22c55e"; // Green default for now

    return (
        <Card className="bg-slate-900 border-slate-800 text-slate-100 h-full">
            <CardHeader>
                <CardTitle className="flex justify-between items-end">
                    <span>{symbol} / USD</span>
                    {latestPrice > 0 && (
                        <span className="text-2xl font-mono text-slate-100">${latestPrice.toFixed(2)}</span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor={changeColor} stopOpacity={0.3} />
                                    <stop offset="95%" stopColor={changeColor} stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis
                                dataKey="date"
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                tickLine={false}
                                axisLine={false}
                                minTickGap={30}
                            />
                            <YAxis
                                domain={['auto', 'auto']}
                                tick={{ fill: '#64748b', fontSize: 12 }}
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={(val) => `$${val}`}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f8fafc' }}
                                itemStyle={{ color: '#22c55e' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="close"
                                stroke={changeColor}
                                fillOpacity={1}
                                fill="url(#colorPrice)"
                                strokeWidth={2}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
