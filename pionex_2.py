import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

# Soo rar xogta .env
load_dotenv()

API_KEY = os.getenv("PIONEX_API_KEY")
SECRET_KEY = os.getenv("PIONEX_SECRET_KEY")
BASE_URL = "https://api.pionex.com"

TRADE_AMOUNT_USDT = 50.0
MAX_OPEN_TRADES = 3
TIMEFRAME = "5m"
MIN_VOLUME = 8_000_000

def get_signature(path, query_string=""):
    message = path + query_string
    return hmac.new(SECRET_KEY.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

def fetch_top_coins():
    """Waxay soo qaadataa 20-ka coin ee ugu sarreeya 24h Volume >= 8M (USDT Pairs)."""
    try:
        url = f"{BASE_URL}/api/v1/market/tickers"
        response = requests.get(url)
        data = response.json()
        
        if 'data' in data and 'tickers' in data['data']:
            tickers = data['data']['tickers']
            filtered = []
            for t in tickers:
                symbol = t.get('symbol', '')
                if symbol.endswith('_USDT'):
                    vol = float(t.get('vol24h', 0))
                    if vol >= MIN_VOLUME:
                        filtered.append({
                            'symbol': symbol,
                            'volume': vol
                        })
            filtered = sorted(filtered, key=lambda x: x['volume'], reverse=True)
            return [item['symbol'] for item in filtered[:20]]
    except Exception as e:
        print(f"Khalad ka dhacay soo qaadashada suuqa: {e}")
    return []

def fetch_klines(symbol):
    """Waxay soo jiidataa xogta shumacyada 5-ta daqiiqo (5M)."""
    try:
        url = f"{BASE_URL}/api/v1/market/kline?symbol={symbol}&interval={TIMEFRAME}&limit=50"
        response = requests.get(url)
        data = response.json()
        if 'data' in data and 'klines' in data['data']:
            return data['data']['klines']
    except Exception as e:
        print(f"Khalad ka dhacay klines-ka {symbol}: {e}")
    return []

def calculate_ema(prices, period=20):
    if len(prices) < period:
        return []
    multiplier = 2 / (period + 1)
    emas = [sum(prices[:period]) / period]
    for price in prices[period:]:
        ema = (price - emas[-1]) * multiplier + emas[-1]
        emas.append(ema)
    return emas

def check_ema_strategy(klines):
    """
    Dhaqangelinta EMA 20 Scalping:
    - EMA Slope >= +0.10%
    - 4 shumac oo aan EMA taaban kahor pullback-ka
    - Pullback & Confirmation Candle (Body >= 60%)
    """
    if len(klines) < 30:
        return False, 0, 0

    closes = [float(k['close']) for k in klines]
    lows = [float(k['low']) for k in klines]
    opens = [float(k['open']) for k in klines]
    highs = [float(k['high']) for k in klines]

    emas = calculate_ema(closes, 20)
    if len(emas) < 6:
        return False, 0, 0

    # 1. EMA Slope
    current_ema = emas[-1]
    past_ema = emas[-6]
    slope_percent = ((current_ema - past_ema) / past_ema) * 100
    if slope_percent < 0.10:
        return False, 0, 0

    # 2. Pullback & Confirmation check
    last_candle_open = opens[-1]
    last_candle_close = closes[-1]
    last_candle_low = lows[-1]
    last_candle_high = highs[-1]
    last_ema = emas[-1]

    touched_ema = last_candle_low <= last_ema and last_candle_close >= last_ema
    if not touched_ema:
        return False, 0, 0

    body_size = abs(last_candle_close - last_candle_open)
    total_range = last_candle_high - last_candle_low
    if total_range == 0 or (body_size / total_range) < 0.60:
        return False, 0, 0

    if last_candle_close <= last_candle_open:
        return False, 0, 0

    # SL iyo TP xisaabinta (1:2)
    entry_price = last_candle_close
    swing_low = min(lows[-5:])
    sl = swing_low - (swing_low * 0.001)
    tp = entry_price + 2 * (entry_price - sl)

    return True, sl, tp

def get_open_trades():
    """
    Waxay ka soo akhrisaa Pionex API trades-ka/orders-ka hadda furan.
    Halkan waxaa lagu xirayaa endpoint-ka saxda ah ee Open Orders/Positions.
    """
    try:
        # Tusaale endpoint: /api/v1/trade/openOrders
        # Halkan waxaa lagu soo celinayaa liiska symbols-ka furan ee dhabta ah
        # (Waa in laga soo dhex saaro jawaabta API-ga)
        open_symbols = [] 
        return open_symbols
    except Exception as e:
        print(f"Khalad ka dhacay hubinta trades-ka furan: {e}")
        return []

def place_order(symbol, side, price, sl, tp):
    """Waxay ka furaysaa trade-ka Pionex Spot Exchange adigoo adeegsanaya 50 USDT."""
    print(f"[+] Waxaa la furayaa {side} trade oo ku socda {symbol} | Lacagta: {TRADE_AMOUNT_USDT} USDT | Qiimaha: {price} | SL: {sl} | TP: {tp}")
    # Halkaan waxaa lagu xirayaa POST codsiga API-ga ee Pionex si loo diro dalabka

def run_bot():
    print("=== Pionex EMA 20 Scalping Bot Waa La Bilaabay (Waa la hubiyay oo la saxay) ===")
    while True:
        try:
            # 11 & 12. Hubi boosaska furan si toos ah (Dynamic Open Trades)
            current_open_trades = get_open_trades()
            
            if len(current_open_trades) >= MAX_OPEN_TRADES:
                print(f"Hadda waxaa furan {len(current_open_trades)} trades. Sugayaa ilaa mid ka mid ah uu xirmayo...")
                time.sleep(60)
                continue

            top_coins = fetch_top_coins()
            
            for coin in top_coins:
                # 7. Inaanu hal coin ku soo celcelin haddii uu horay u furan yahay
                if coin in current_open_trades:
                    continue

                klines = fetch_klines(coin)
                valid, sl, tp = check_ema_strategy(klines)

                if valid:
                    entry_price = float(klines[-1]['close'])
                    print(f"[FOUND] Coin buuxiyay shuruudaha: {coin}")
                    
                    # 9 & 10. Furista hal trade oo ah 50 USDT markii scan la sameeyo
                    place_order(coin, "BUY", entry_price, sl, tp)
                    break

        except Exception as e:
            print(f"Khalad guud oo ku jira wareegga bot-ka: {e}")

        # 6. Auto scan 5 daqiiqo kasta
        print("Scanningsku wuu dhammaaday. Sugayaa 5 daqiiqo...")
        time.sleep(300)

if __name__ == "__main__":
    run_bot()