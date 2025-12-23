'use client';

import { ArrowUp, ArrowDown } from "lucide-react";

// Mock data for the ticker to avoid API rate limits on simple visual components
const TICKER_DATA = [
    { symbol: "AAPL", price: 154.32, change: 1.25, changePercent: 0.8 },
    { symbol: "GOOGL", price: 175.40, change: -0.50, changePercent: -0.28 },
    { symbol: "MSFT", price: 410.15, change: 3.20, changePercent: 0.78 },
    { symbol: "AMZN", price: 180.90, change: 1.10, changePercent: 0.6 },
    { symbol: "TSLA", price: 178.00, change: -5.20, changePercent: -2.8 },
    { symbol: "BTC", price: 68500, change: 1200, changePercent: 1.7 },
    { symbol: "ETH", price: 3800, change: 50, changePercent: 1.3 },
    { symbol: "SPY", price: 520.10, change: 2.15, changePercent: 0.4 },
];

export default function TickerTape() {
    return (
        <div className="w-full bg-slate-950 border-b border-slate-800 overflow-hidden py-2 whitespace-nowrap flex">
            <div className="animate-ticker flex space-x-8 px-4">
                {[...TICKER_DATA, ...TICKER_DATA].map((stock, idx) => (
                    <div key={`${stock.symbol}-${idx}`} className="flex items-center space-x-2">
                        <span className="font-bold text-slate-200">{stock.symbol}</span>
                        <span className="text-slate-400">${stock.price.toFixed(2)}</span>
                        <span className={`flex items-center text-xs font-medium ${stock.change >= 0 ? "text-green-500" : "text-red-500"}`}>
                            {stock.change >= 0 ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                            {Math.abs(stock.changePercent)}%
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
