    return []


def fetch_top_coins(tickers):
    """20-ka coin ee ugu sarreeya 24h Volume >= 8M (USDT Pairs)."""
    filtered = []
    for t in tickers:
        symbol = t.get("symbol", "")
        if symbol.endswith("_USDT"):
            # 'amount' = qiimaha USDT ee la ganacsaday (vol24h Pionex ma haysto)
            vol = float(t.get("amount", 0) or 0)
            if vol >= MIN_VOLUME:
                filtered.append({"symbol": symbol, "volume": vol})
    filtered.sort(key=lambda x: x["volume"], reverse=True)
    return [item["symbol"] for item in filtered[:20]]


def fetch_klines(symbol):
    """Xogta shumacyada 5M (ugu da'da weyn -> ugu cusub)."""
    try:
        data = public_get(
            "/api/v1/market/klines",
            {"symbol": symbol, "interval": TIMEFRAME, "limit": 50},
        )
        if data.get("result") and "klines" in data.get("data", {}):
            klines = data["data"]["klines"]
            klines.sort(key=lambda k: int(k.get("time", 0)))
            # Ka tag shumaca weli socda (aan xirmin): strategy-gu wuxuu isticmaalaa shumacyo xiran oo kaliya
            now_ms = int(time.time() * 1000)
            klines = [k for k in klines if int(k.get("time", 0)) + 300_000 <= now_ms]
            return klines
        print(f"Klines jawaab xun {symbol}: {data}")
    except Exception as e:
        print(f"Khalad ka dhacay klines-ka {symbol}: {e}")
    return []

