'use client';

import { ArrowUp, ArrowDown } from "lucide-react";
import useSWR from 'swr';

// Symbols to track in the ticker
const TICKER_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "BTC-USD", "ETH-USD", "SPY"];

const fetcher = async (url: string) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch");
    return res.json();
};

interface TickerTapeProps {
    onSelectSymbol?: (symbol: string) => void;
}

export default function TickerTape({ onSelectSymbol }: TickerTapeProps) {
    // We use a simple approach: fetch all data. In production, we might batch this.
    // Here we use SWR's useSWR with a custom key function or multiple hooks is tricky.
    // Instead we'll make a wrapper component or just map and fetch individually 
    // BUT fetching individually is bad for rate limits/performance.
    // Given the constraints and the backend endpoint /api/v1/stocks/{symbol},
    // we will create a simple internal component for each item to handle its own state/SWR.

    return (
        <div className="w-full bg-slate-950 border-b border-slate-800 overflow-hidden py-2 whitespace-nowrap flex">
            <div className="animate-ticker flex space-x-8 px-4">
                {/* Duplicate the list for infinite scroll effect */}
                {[...TICKER_SYMBOLS, ...TICKER_SYMBOLS].map((symbol, idx) => (
                    <TickerItem
                        key={`${symbol}-${idx}`}
                        symbol={symbol}
                        onClick={() => onSelectSymbol?.(symbol)}
                    />
                ))}
            </div>
        </div>
    );
}

function TickerItem({ symbol, onClick }: { symbol: string, onClick?: () => void }) {
    const { data, error } = useSWR(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/stocks/${symbol}`,
        fetcher,
        { refreshInterval: 60000 } // Refresh every minute
    );

    if (error) return <div className="flex items-center space-x-2"><span className="font-bold text-slate-500">{symbol}</span></div>;
    if (!data) return <div className="flex items-center space-x-2"><span className="font-bold text-slate-500">{symbol}...</span></div>;

    const stock = data.realtime;
    // Assuming API returns string "XX.XX%" or similar, we parse it or use directly.
    // API returns: { price: "273.81", change_percent: "0.6137%", ... }

    const changePercentStr = stock.change_percent.replace('%', '');
    const changePercent = parseFloat(changePercentStr);
    const isPositive = changePercent >= 0;

    return (
        <div
            className="flex items-center space-x-2 cursor-pointer hover:bg-slate-900 px-2 py-1 rounded transition-colors"
            onClick={onClick}
        >
            <span className="font-bold text-slate-200">{stock.symbol}</span>
            <span className="text-slate-400">${parseFloat(stock.price).toFixed(2)}</span>
            <span className={`flex items-center text-xs font-medium ${isPositive ? "text-green-500" : "text-red-500"}`}>
                {isPositive ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                {Math.abs(changePercent).toFixed(2)}%
            </span>
        </div>
    );
}
