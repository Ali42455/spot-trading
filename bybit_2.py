# -*- coding: utf-8 -*-
"""
BYBIT SPOT BOT — EMA20 SCALPING (BUY KALIYA, 5M CANDLES / 30M SCAN INTERVAL)
=============================================================================
- Waxay Isticmaashaa Shumaca 5-Daqiiqo (5M)
- Baadhitaanka suuqa (Scan Cycle) wuxuu dhacayaa 30 daqiiqaba mar
- Marka coin buuxiyo shuruudaha BUY, waxay furaysaa hal trade (50 USDT)
- TP = LIMIT, SL = MARKET (Bybit lafteeda ayaa ilaalisa)
- Ugu badnaan 3 trade ayaa furan isku mar
- API key iyo secret waxay ka imanayaan faylka .env

Ku shaqeynta:
    pip install pybit python-dotenv
    python bybit_spot_bot.py
"""

import os
import sys
import json
import time
import logging
import traceback
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from pybit.unified_trading import HTTP

load_dotenv()

# =========================================================
# 1) DEJINTA — halkan ka beddel
# =========================================================
# True = trade dhab ah | False = tijaabo (waxba ma iibsado, log kaliya)
LIVE_TRADING = os.getenv("LIVE_TRADING", "true").strip().lower() == "true"
TESTNET = os.getenv("BYBIT_TESTNET", "false").strip().lower() == "true"

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "LINKUSDT",
    "NEARUSDT", "SUIUSDT", "AAVEUSDT", "UNIUSDT", "DOGEUSDT", "ADAUSDT",
    "TRXUSDT", "ONDOUSDT", "MNTUSDT", "LTCUSDT", "WLDUSDT", "HYPEUSDT",
    "QNTUSDT",
]

TRADE_USDT = 50          # lacagta trade kasta
MAX_OPEN_TRADES = 3      # ugu badnaan trade furan
COOLDOWN_MIN = 30        # daqiiqado: coin xidhmay kadib dib looma furo (0 = demi)

# TIME FRAME & SCAN INTERVAL
INTERVAL = "5"           # Shumaca waa 5M (5 daqiiqo)
CANDLE_SEC = 300         # 5 daqiiqo
SCAN_INTERVAL_SEC = 1800 # Bot-ku 30 minit (1800 sec) kasta ayuu suuqa baadhayaa
KLINE_LIMIT = 200
FRESH_SEC = 90           # shumaca xaqiijinta waa inuu ka xirmay ugu badnaan 90 ilbiriqsi

# Strategy
EMA_PERIOD = 20
EMA_SLOPE_BARS = 5       # EMA20 la barbar dhig 5 shumac ka hor
EMA_SLOPE_MIN_PCT = 0.10 # ugu yaraan +0.10%
TREND_CANDLES = 4        # 4 shumac oo aan EMA20 taaban
PULLBACK_MAX = 6         # pullback-ka ugu badnaan 6 shumac
BODY_MIN = 0.60          # jirka shumaca >= 60%

# Khatarta
RR = 2.0                 # 1:2
SL_BUFFER_PCT = 0.10     # SL wax yar ka hooseeya swing low (0.10%)
MIN_RISK_PCT = 0.30      # SL aad u dhow = khidmad (fee) ayaa cuntaa faa'iidada
MAX_RISK_PCT = 2.00      # khatarta trade-ka ma dhaafi karto 2%
MAX_CHASE_PCT = 0.30     # qiimuhu haddii uu 0.30% kor u kacay, laga boodo
CLOSE_IF_UNPROTECTED = True  # haddii TP/SL aan la dhigin, coin-ka isla markiiba iibi

STATE_FILE = "bot_state.json"
LOG_FILE = "bot.log"

# =========================================================
# 2) GLOBALS
# =========================================================
session = None
instruments = {}
state = {"trades": {}, "cooldown": {}}
log = logging.getLogger("bybit_bot")


def setup_logging():
    log.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    fh = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


# =========================================================
# 3) INDICATORS
# =========================================================
def ema(values, period):
    out = [None] * len(values)
    if len(values) < period:
        return out
    k = 2.0 / (period + 1)
    e = sum(values[:period]) / period
    out[period - 1] = e
    for i in range(period, len(values)):
        e = values[i] * k + e * (1 - k)
        out[i] = e
    return out


# =========================================================
# 4) HELPERS
# =========================================================
def fmt_step(value, step, rounding):
    """Qiimaha ku koobo tick/step-ka Bybit (tusaale 0.01)."""
    v = Decimal(str(value))
    s = Decimal(str(step))
    q = (v / s).to_integral_value(rounding=rounding) * s
    return format(q.normalize(), "f")


def api(fn, retries=3, **kw):
    """Wicitaan API ah oo isku day ah (kaliya wixii aan lacag furi karin)."""
    for n in range(retries):
        try:
            r = fn(**kw)
            if r.get("retCode") == 0:
                return r
            raise RuntimeError(f"{r.get('retCode')}: {r.get('retMsg')}")
        except Exception:
            if n == retries - 1:
                raise
            time.sleep(2 * (n + 1))


def save_state():
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def load_state():
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["trades"] = data.get("trades", {})
        state["cooldown"] = data.get("cooldown", {})
    except Exception as e:
        log.error("%s waa xumaaday (%s). Hubi ama tirtir, kadib dib u bilow.", STATE_FILE, e)
        sys.exit(1)


def get_balance(coin):
    """Soo celi (wadarta, bilaash ah) ee coin-ka."""
    last_err = None
    for acct in ("UNIFIED", "SPOT"):
        try:
            r = api(session.get_wallet_balance, accountType=acct, coin=coin)
            lst = r["result"]["list"]
            if not lst:
                continue
            for c in lst[0].get("coin", []):
                if c.get("coin") == coin:
                    total = float(c.get("walletBalance") or 0)
                    locked = float(c.get("locked") or 0)
                    return total, max(total - locked, 0.0)
            return 0.0, 0.0
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Balance lama helin: {last_err}")


def get_price(sym):
    r = api(session.get_tickers, category="spot", symbol=sym)
    return float(r["result"]["list"][0]["lastPrice"])


def load_instruments():
    ok = []
    for sym in SYMBOLS:
        try:
            r = api(session.get_instruments_info, retries=2, category="spot", symbol=sym)
            lst = r["result"]["list"]
            if not lst or lst[0].get("status") != "Trading":
                log.warning("%s: Bybit SPOT kuma jiro (ama lama ganacsan karo) — waa laga boodayaa", sym)
                continue
            i = lst[0]
            instruments[sym] = {
                "base": i["baseCoin"],
                "tick": i["priceFilter"]["tickSize"],
                "base_step": i["lotSizeFilter"]["basePrecision"],
                "min_amt": float(i["lotSizeFilter"].get("minOrderAmt") or 0),
            }
            ok.append(sym)
        except Exception as e:
            log.warning("%s: xog lama helin (%s) — waa laga boodayaa", sym, e)
    return ok


def get_candles(sym):
    """Shumacyo xiran oo kaliya (kan socda lama tixgelinayo)."""
    r = api(session.get_kline, category="spot", symbol=sym, interval=INTERVAL, limit=KLINE_LIMIT)
    rows = r["result"]["list"][::-1]  # hore -> dambe
    now_ms = int(time.time() * 1000)
    out = []
    for row in rows:
        start = int(row[0])
        if start + CANDLE_SEC * 1000 > now_ms:
            continue
        out.append({"t": start, "o": float(row[1]), "h": float(row[2]),
                    "l": float(row[3]), "c": float(row[4])})
    return out


# =========================================================
# 5) STRATEGY — EMA20 PULLBACK (BUY)
# =========================================================
def analyze(sym):
    """Soo celi (signal, sabab). Signal = None haddii shuruudaha aan la buuxin."""
    cs = get_candles(sym)
    need = EMA_PERIOD + EMA_SLOPE_BARS + PULLBACK_MAX + TREND_CANDLES + 5
    if len(cs) < need:
        return None, "xog ku filan ma jirto"

    i = len(cs) - 1
    last = cs[i]

    # 0) shumaca xaqiijintu waa inuu hadda xirmay (laga fogaado shumacyada hore)
    age = time.time() - (last["t"] / 1000.0 + CANDLE_SEC)
    if age > FRESH_SEC:
        return None, "shumaca xaqiijinta waa duug"

    closes = [c["c"] for c in cs]
    e = ema(closes, EMA_PERIOD)

    # 1) EMA20 jiirad
    base = e[i - EMA_SLOPE_BARS]
    slope = (e[i] - base) / base * 100
    if slope < EMA_SLOPE_MIN_PCT:
        return None, f"EMA20 jiirad {slope:.3f}% (aad u yar)"

    # 2) shumaca xaqiijinta: bullish, EMA20 korkeeda, jir >= 60%
    rng = last["h"] - last["l"]
    body = last["c"] - last["o"]
    if rng <= 0 or body <= 0:
        return None, "shumaca xaqiijinta bullish ma aha"
    if last["c"] <= e[i]:
        return None, "shumaca wuxuu ku xirmay EMA20 hoosteeda"
    body_ratio = body / rng
    if body_ratio < BODY_MIN:
        return None, f"jirka shumaca {body_ratio*100:.0f}% (<60%)"

    # 3) pullback: shumac EMA20 taabtay (kan xaqiijinta ah ama kii ka horreeyay)
    def touched(k):
        return cs[k]["l"] <= e[k]

    if touched(i):
        end = i
    elif touched(i - 1):
        end = i - 1
    else:
        return None, "pullback ma jiro"
    start = end
    while touched(start - 1):
        start -= 1
        if end - start + 1 > PULLBACK_MAX:
            return None, "pullback aad u dheer"

    # 4) 4 shumac oo trend ah ka hor pullback-ka (Low-gooda EMA20 ka sarreeyo)
    for k in range(start - TREND_CANDLES, start):
        if cs[k]["l"] <= e[k]:
            return None, f"ma jiraan {TREND_CANDLES} shumac oo trend ah"

    # 5) SL / khatar (qiimo tixraac = close)
    swing_low = min(c["l"] for c in cs[start:i + 1])
    price = last["c"]
    sl = swing_low * (1 - SL_BUFFER_PCT / 100)
    if sl >= price:
        return None, "SL lama xisaabin karo"
    risk_pct = (price - sl) / price * 100
    if risk_pct < MIN_RISK_PCT:
        return None, f"khatarta {risk_pct:.2f}% aad u yar"
    if risk_pct > MAX_RISK_PCT:
        return None, f"khatarta {risk_pct:.2f}% aad u weyn"

    return {
        "symbol": sym, "close": price, "swing_low": swing_low,
        "slope": slope, "body_ratio": body_ratio, "risk_pct": risk_pct,
    }, "OK"


# =========================================================
# 6) ORDERS
# =========================================================
def find_order_by_link(sym, link):
    """Haddii order-ku khalad ka dhigay, ogow in uu dhab ahaan furmay iyo in kale."""
    time.sleep(2)
    try:
        r = api(session.get_order_history, retries=2, category="spot", symbol=sym, orderLinkId=link)
        lst = r["result"]["list"]
        if lst:
            return lst[0]["orderId"]
    except Exception as e:
        log.warning("%s: order lama hubin karo (%s)", sym, e)
    return None


def wait_fill(sym, order_id):
    """Soo celi (qty, avgPrice) ama None."""
    status = None
    for _ in range(8):
        time.sleep(1)
        try:
            r = api(session.get_order_history, retries=1, category="spot", symbol=sym, orderId=order_id)
            lst = r["result"]["list"]
            if not lst:
                continue
            o = lst[0]
            status = o.get("orderStatus")
            if status in ("Filled", "Cancelled", "PartiallyFilledCanceled", "Rejected"):
                qty = float(o.get("cumExecQty") or 0)
                if qty > 0:
                    return qty, float(o.get("avgPrice") or 0)
                return None
        except Exception:
            continue
    return None


def has_protection(sym):
    """True = TP/SL jira | False = ma jiro | None = lama hubin karo."""
    ok_calls = 0
    for flt in ("Order", "tpslOrder", "StopOrder"):
        try:
            r = api(session.get_open_orders, retries=2, category="spot", symbol=sym, orderFilter=flt)
            ok_calls += 1
            for o in r["result"]["list"]:
                if o.get("side") == "Sell":
                    return True
        except Exception as e:
            log.debug("%s: get_open_orders(%s) khalad: %s", sym, flt, e)
    return False if ok_calls else None


def emergency_sell(sym, qty_hint):
    inst = instruments[sym]
    total, free = get_balance(inst["base"])
    qty = min(free, qty_hint) if qty_hint else free
    qty_s = fmt_step(qty, inst["base_step"], ROUND_DOWN)
    if float(qty_s) <= 0:
        log.error("%s: wax lagu iibiyo lama helin", sym)
        return
    session.place_order(category="spot", symbol=sym, side="Sell", orderType="Market",
                        qty=qty_s, marketUnit="baseCoin")
    log.warning("%s: coin-ka waa la iibiyay (market) si loo ilaaliyo", sym)


def open_trade(sig):
    sym = sig["symbol"]
    inst = instruments[sym]
    try:
        price = get_price(sym)
    except Exception as e:
        log.warning("%s: qiimaha lama helin (%s)", sym, e)
        return False

    if price > sig["close"] * (1 + MAX_CHASE_PCT / 100):
        log.info("%s: qiimuhu aad ayuu kor u kacay (%.6g > %.6g) — laga boodo", sym, price, sig["close"])
        return False

    sl = sig["swing_low"] * (1 - SL_BUFFER_PCT / 100)
    if sl >= price:
        return False
    risk = price - sl
    risk_pct = risk / price * 100
    if risk_pct < MIN_RISK_PCT or risk_pct > MAX_RISK_PCT:
        log.info("%s: khatarta %.2f%% xadka ma gelin — laga boodo", sym, risk_pct)
        return False
    tp = price + RR * risk

    sl_s = fmt_step(sl, inst["tick"], ROUND_DOWN)
    tp_s = fmt_step(tp, inst["tick"], ROUND_UP)

    if TRADE_USDT < inst["min_amt"]:
        log.warning("%s: %s USDT waa ka yar yahay ugu yaraan Bybit (%s)", sym, TRADE_USDT, inst["min_amt"])
        return False

    if not LIVE_TRADING:
        log.info("[TIJAABO] BUY %s | %s USDT | qiimo %.6g | SL %s | TP %s | EMA jiirad %.2f%%",
                 sym, TRADE_USDT, price, sl_s, tp_s, sig["slope"])
        state["cooldown"][sym] = time.time() + COOLDOWN_MIN * 60
        save_state()
        return True

    link = f"cali{int(time.time())}{sym[:8]}"
    try:
        r = session.place_order(
            category="spot", symbol=sym, side="Buy", orderType="Market",
            qty=str(TRADE_USDT), marketUnit="quoteCoin",
            takeProfit=tp_s, tpOrderType="Limit", tpLimitPrice=tp_s,   # TP = LIMIT
            stopLoss=sl_s, slOrderType="Market",                       # SL = MARKET
            orderLinkId=link,
        )
        order_id = r["result"]["orderId"]
    except Exception as e:
        log.error("%s: order khalad (%s) — hubinayaa in uu furmay iyo in kale", sym, e)
        order_id = find_order_by_link(sym, link)
        if not order_id:
            return False

    fill = wait_fill(sym, order_id)
    if fill is None:
        log.error("%s: order lama xaqiijin — la ilaalinayaa/la baajinayaa", sym)
        try:
            session.cancel_order(category="spot", symbol=sym, orderId=order_id)
        except Exception:
            pass
        fill = wait_fill(sym, order_id)
        if fill is None:
            return False
    qty, avg = fill

    state["trades"][sym] = {
        "entry": avg or price, "qty": qty, "sl": float(sl_s), "tp": float(tp_s),
        "ts_ms": int(time.time() * 1000) - 10_000, "order_id": order_id,
    }
    save_state()
    log.info("FURMAY BUY %s | %s USDT | gelitaan %.6g | SL %s | TP %s",
             sym, TRADE_USDT, avg or price, sl_s, tp_s)

    # Hubi in TP/SL Bybit gashay
    prot = None
    for _ in range(3):
        time.sleep(2)
        prot = has_protection(sym)
        if prot:
            break
    if prot:
        log.info("%s: TP/SL waa la dhigay (Bybit ayaa ilaalinaysa)", sym)
    elif prot is False:
        log.critical("%s: TP/SL LAMA DHIGIN — trade-ku ilaalin la'aan ayuu yahay!", sym)
        if CLOSE_IF_UNPROTECTED:
            try:
                emergency_sell(sym, qty)
                state["trades"].pop(sym, None)
                state["cooldown"][sym] = time.time() + COOLDOWN_MIN * 60
                save_state()
            except Exception as e:
                log.critical("%s: IIBINTII DEGDEGGA AH WAY FASHILANTAY (%s) — ISLA MARKIIBA GACAN KU XIDH!", sym, e)
    else:
        log.warning("%s: TP/SL lama hubin karo — hubi gacanta Bybit app-ka", sym)
    return True


def check_closed(sym, t):
    """Soo celi (sabab, qiimo_bax) haddii trade-ku xidhmay, haddii kale None."""
    r = api(session.get_order_history, category="spot", symbol=sym, limit=50)
    for o in r["result"]["list"]:
        if (o.get("side") == "Sell" and o.get("orderStatus") == "Filled"
                and int(o.get("createdTime", 0)) >= t["ts_ms"]):
            avg = float(o.get("avgPrice") or 0)
            return ("TP" if avg >= t["tp"] * 0.997 else "SL"), avg
    base = instruments.get(sym, {}).get("base") or sym.replace("USDT", "")
    total, _ = get_balance(base)
    if total < t["qty"] * 0.5:
        return "GACAN/LAMA YAQAAN", None
    return None


def sync_trades():
    changed = False
    for sym, t in list(state["trades"].items()):
        try:
            res = check_closed(sym, t)
        except Exception as e:
            log.warning("%s: xaaladda trade-ka lama hubin karo (%s)", sym, e)
            continue
        if res:
            reason, exit_price = res
            if exit_price:
                pnl = (exit_price - t["entry"]) * t["qty"]
                log.info("XIDHMAY %s | %s | %.6g -> %.6g | PnL ~ %+.2f USDT",
                         sym, reason, t["entry"], exit_price, pnl)
            else:
                log.info("XIDHMAY %s | %s", sym, reason)
            del state["trades"][sym]
            state["cooldown"][sym] = time.time() + COOLDOWN_MIN * 60
            changed = True
    if changed:
        save_state()


# =========================================================
# 7) SCAN
# =========================================================
def scan_cycle(symbols):
    sync_trades()

    n_open = len(state["trades"])
    if n_open >= MAX_OPEN_TRADES:
        log.info("%d/%d trade ayaa furan — scan lama sameynayo ilaa mid xidhmo", n_open, MAX_OPEN_TRADES)
        return

    if LIVE_TRADING:
        _, free = get_balance("USDT")
        if free < TRADE_USDT:
            log.warning("USDT ma filna (%.2f < %s)", free, TRADE_USDT)
            return

    candidates = []
    now = time.time()
    for sym in symbols:
        if sym in state["trades"]:
            continue
        if now < state["cooldown"].get(sym, 0):
            continue
        try:
            sig, why = analyze(sym)
        except Exception as e:
            log.warning("%s: baaris khalad (%s)", sym, e)
            continue
        if sig:
            log.info("FURSAD %s | EMA jiirad %.2f%% | jir %.0f%% | khatar %.2f%%",
                     sym, sig["slope"], sig["body_ratio"] * 100, sig["risk_pct"])
            candidates.append(sig)
        else:
            log.debug("%s: %s", sym, why)
        time.sleep(0.15)

    if not candidates:
        log.info("Scan dhammaaday (%d coin): fursad ma jirto", len(symbols))
        return

    # Hal trade scan kasta — kan trend-kiisu ugu xoogga badan
    candidates.sort(key=lambda s: s["slope"], reverse=True)
    for sig in candidates:
        if open_trade(sig):
            break


def wait_next_scan():
    """Wuxuu sugayaa 30 daqiiqo (1800 sec) ka hor inta uusan scan-ka xiga samayn."""
    log.info("Scan-kii waa dhamaaday. Bot-ku wuxuu sugayaa 30 daqiiqo (1800 sec) scan-ka xiga...")
    time.sleep(SCAN_INTERVAL_SEC)


def main():
    global session
    setup_logging()

    key = os.getenv("BYBIT_API_KEY", "").strip()
    secret = os.getenv("BYBIT_API_SECRET", "").strip()
    if not key or not secret:
        log.error("BYBIT_API_KEY / BYBIT_API_SECRET ma jiraan faylka .env")
        sys.exit(1)

    session = HTTP(testnet=TESTNET, api_key=key, api_secret=secret, recv_window=10000)
    log.info("=== BYBIT SPOT BOT | LIVE=%s | TESTNET=%s | %s USDT/trade | SCAN INTERVAL = 30 MIN ===",
             LIVE_TRADING, TESTNET, TRADE_USDT)

    try:
        total, free = get_balance("USDT")
    except Exception as e:
        log.error("Ku xidhmi waayay Bybit — hubi API key, permission iyo IP: %s", e)
        sys.exit(1)
    log.info("USDT: wadar %.2f | bilaash %.2f", total, free)

    symbols = load_instruments()
    if not symbols:
        log.error("Coin lama helin")
        sys.exit(1)
    log.info("Coin-ka la baadhayo: %d", len(symbols))

    load_state()
    sync_trades()
    log.info("Trade-yada furan: %s", list(state["trades"].keys()) or "ma jiraan")

    try:
        while True:
            try:
                scan_cycle(symbols)
            except Exception:
                log.error("Khalad scan-ka ah:\n%s", traceback.format_exc())
            
            # Wuxuu sugayaa 30 minit
            wait_next_scan()
    except KeyboardInterrupt:
        log.info("Bot-ka waa la joojiyay. TP/SL ee Bybit way sii shaqaynayaan.")


if __name__ == "__main__":
    main()