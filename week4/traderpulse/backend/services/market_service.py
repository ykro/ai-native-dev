import httpx
from ..config import get_settings

settings = get_settings()
BASE_URL = "https://www.alphavantage.co/query"

async def get_realtime_stock_data(symbol: str):
    """
    Fetches real-time stock data (Global Quote) from Alpha Vantage.
    """
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
    quote = data.get("Global Quote", {})
    if not quote:
        return None

    return {
        "symbol": quote.get("01. symbol"),
        "price": quote.get("05. price"),
        "change_percent": quote.get("10. change percent"),
        "volume": quote.get("06. volume")
    }

async def get_historical_data(symbol: str):
    """
    Fetches daily time series for charting.
    """
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"--- DEBUG ALPHA VANTAGE RESPONSE ({symbol}) ---")
        print(data)
        print("-------------------------------------------------")

    # Process into a simpler format for the frontend
    # Alpha Vantage returns "Time Series (Daily)"
    series = data.get("Time Series (Daily)", {})
    chart_data = []
    
    # Take last 30 days
    dates = sorted(series.keys(), reverse=True)[:30]
    
    for date in reversed(dates): # forward order
        val = series[date]
        chart_data.append({
            "date": date,
            "close": float(val["4. close"])
        })
        
    return chart_data
