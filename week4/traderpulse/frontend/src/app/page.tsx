'use client';

import { useState } from 'react';
import TickerTape from '@/components/dashboard/TickerTape';
import MarketChart from '@/components/dashboard/MarketChart';
import SentimentWidget from '@/components/dashboard/SentimentWidget';
import GamificationSidebar from '@/components/dashboard/GamificationSidebar';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export default function Home() {
    const [symbol, setSymbol] = useState("AAPL");
    const [searchInput, setSearchInput] = useState("");

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchInput.trim()) {
            setSymbol(searchInput.trim().toUpperCase());
        }
    };

    return (
        <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30">
            {/* Header */}
            <header className="border-b border-slate-800 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
                <div className="container mx-auto px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="bg-gradient-to-tr from-cyan-500 to-blue-600 w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white">
                            TP
                        </div>
                        <h1 className="text-xl font-bold tracking-tight text-white">
                            Trader<span className="text-cyan-400">Pulse</span>
                        </h1>
                    </div>

                    <div className="flex items-center space-x-4">
                        {/* Simple user avatar or menu could go here */}
                    </div>
                </div>
            </header>

            <TickerTape />

            <div className="container mx-auto px-4 py-6 flex-1">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">

                    {/* Main Content Area - Left/Center */}
                    <div className="lg:col-span-3 space-y-6">

                        {/* Search Bar */}
                        <form onSubmit={handleSearch} className="flex gap-2 max-w-md">
                            <Input
                                placeholder="Buscar símbolo (ej. AAPL, BTC, TSLA)..."
                                className="bg-slate-900 border-slate-800 text-slate-100 focus-visible:ring-cyan-500"
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                            />
                            <Button type="submit" className="bg-cyan-600 hover:bg-cyan-700 text-white">
                                <Search size={18} />
                            </Button>
                        </form>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Chart takes up 2 columns */}
                            <div className="lg:col-span-2 h-[450px]">
                                <MarketChart symbol={symbol} />
                            </div>
                            {/* Sentiment takes up 1 column next to chart */}
                            <div className="lg:col-span-1 h-full">
                                <SentimentWidget symbol={symbol} />
                            </div>
                        </div>

                        {/* Additional Metrics or News could go here */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Placeholders for future metrics */}
                        </div>
                    </div>

                    {/* Right Sidebar - Gamification */}
                    <div className="lg:col-span-1">
                        <GamificationSidebar />
                    </div>

                </div>
            </div>
        </main>
    );
}
