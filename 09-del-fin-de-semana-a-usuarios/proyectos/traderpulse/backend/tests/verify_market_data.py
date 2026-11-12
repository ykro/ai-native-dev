
import asyncio
import sys
import os

from backend.services.market_service import get_realtime_stock_data, get_historical_data

async def verify():
    symbol = "AAPL"
    print(f"Verifying data for {symbol}...")
    
    print("\n--- Realtime Data ---")
    realtime = await get_realtime_stock_data(symbol)
    print(realtime)
    
    if realtime and "price" in realtime and "change_percent" in realtime:
        print("✅ Realtime data structure looks correct.")
    else:
        print("❌ Realtime data structure is incorrect or empty.")

    print("\n--- Historical Data ---")
    historical = await get_historical_data(symbol)
    if historical:
        print(f"Retrieved {len(historical)} data points.")
        print(f"First point: {historical[0]}")
        print(f"Last point: {historical[-1]}")
        
        if "date" in historical[0] and "close" in historical[0]:
             print("✅ Historical data structure looks correct.")
        else:
             print("❌ Historical data structure is incorrect.")
    else:
        print("❌ Historical data is empty.")

if __name__ == "__main__":
    asyncio.run(verify())
