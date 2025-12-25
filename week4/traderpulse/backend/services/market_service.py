import yfinance as yf
from ..config import get_settings

settings = get_settings()

async def get_realtime_stock_data(symbol: str):
    """
    Fetches real-time stock data from yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        # fast_info provides basic realtime data without full download
        info = ticker.fast_info
        
        # yfinance fast_info keys: 
        # last_price, previous_close, open, day_high, day_low, year_high, year_low...
        # We need to calculate change percent manually or fetch from ticker.info (slower)
        # Using fast_info for speed.
        
        price = info.last_price
        prev_close = info.previous_close
        
        if prev_close and prev_close != 0:
            change_percent = ((price - prev_close) / prev_close) * 100
        else:
            change_percent = 0.0
            
        return {
            "symbol": symbol.upper(),
            "price": str(price), # preserving string format for frontend consistency if needed, checking existing impl
            "change_percent": f"{change_percent:.4f}%",
            "volume": str(int(info.last_volume)) if hasattr(info, 'last_volume') else "0"
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

async def get_historical_data(symbol: str):
    """
    Fetches daily time series for charting using yfinance.
    """
    try:
        # Download last 1 month of data, 1 day interval
        df = yf.download(symbol, period="1mo", interval="1d", progress=False)
        
        if df.empty:
            return []

        chart_data = []
        
        # yfinance returns a DataFrame with DatetimeIndex
        # Iterating directly to handle the index (Date) correctly
        for date, row in df.iterrows():
            # date is typically a Timestamp
            try:
                date_str = date.strftime('%Y-%m-%d')
            except AttributeError:
                # Fallback if date is not a timestamp (unlikely with yfinance)
                date_str = str(date).split(' ')[0]

            # Depending on yfinance version, columns could be MultiIndex or simple.
            # Usually 'Close' is the column name.
            close_val = row['Close']
            
            # handle potential multi-index (e.g. if multiple tickers downloaded) or scalar
            if hasattr(close_val, 'item'): 
                val = close_val.item()
            else:
                val = float(close_val)
                
            chart_data.append({
                "date": date_str,
                "close": val
            })
            
        # Ensure standard order if needed, but 'download' usually returns chronological.
        # The frontend likely expects chronological or reverse.
        # Original code: reversed(dates) -> forward order (oldest to newest).
        # yfinance returns oldest to newest by default.
        return chart_data
        
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return []
