from fastapi import APIRouter, HTTPException
from ..services import market_service, ai_service

router = APIRouter(prefix="/api/v1")

@router.get("/stocks/{symbol}")
async def get_stock_data(symbol: str):
    """
    Returns current price, change, volume, and historical data for charting.
    """
    try:
        realtime_data = await market_service.get_realtime_stock_data(symbol)
        if not realtime_data:
            raise HTTPException(status_code=404, detail="Symbol not found")
            
        historical_data = await market_service.get_historical_data(symbol)
        
        return {
            "realtime": realtime_data,
            "historical": historical_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """
    Returns AI-generated sentiment analysis.
    """
    try:
        # We need some market data context for the AI
        realtime_data = await market_service.get_realtime_stock_data(symbol)
        if not realtime_data:
            raise HTTPException(status_code=404, detail="Symbol not found")
            
        analysis = await ai_service.analyze_sentiment(symbol, realtime_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gamification/status")
async def get_gamification_status():
    """
    Returns mock data for user points and badges.
    """
    # Mock data as per requirements
    return {
        "investor_level": "Intermedio",
        "analysis_points": 1250,
        "badges": ["Primer Análisis", "Toro de Oro", "Visualizador"],
        "next_level_progress": 75 # percent
    }
