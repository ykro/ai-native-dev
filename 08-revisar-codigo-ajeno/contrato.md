# Contrato del cambio · RSI y titulares en TraderPulse

## Qué se pide

1. Calcular el RSI de 14 días de una acción y devolverlo junto con los datos del endpoint `GET /api/v1/stocks/{symbol}`, en el campo `rsi`.
2. Pasar titulares de noticias de la acción al análisis de sentimiento (`GET /api/v1/sentiment/{symbol}`).

## Interfaz acordada

- `indicators.calculate_rsi(closes, period=14) -> float`, entre 0 y 100. `closes` va en orden cronológico, el más reciente al final.
- `ai_service.analyze_sentiment(symbol, market_data, headlines=None) -> dict` con `sentiment` (`Bullish`, `Bearish` o `Neutral`) y `justification`.
- `news_service.get_headlines(symbol, limit=5) -> list[str]`.

## Archivos permitidos

- `backend/services/indicators.py` (nuevo)
- `backend/services/news_service.py` (nuevo)
- `backend/services/ai_service.py`
- `backend/routers/api.py`
- Pruebas nuevas: `backend/tests/test_*.py` (solo archivos nuevos)

## Prohibido

- Agregar dependencias (`requirements.txt` no cambia).
- Tocar `docker-compose.yml` ni `backend/config.py`.
- Editar pruebas existentes. Solo se pueden agregar pruebas nuevas.

## Qué decide

`python3 scripts/revisar_pr.py --rama pr/rsi-y-noticias`: sale con 0 solo si todas las etapas pasan. Lo que el agente reporte no cuenta.
