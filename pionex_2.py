
/
Notion AI · 2:24 PM
ii qor code ka BYBIT bot
BYBIT SPOT TRADING BOT — SHURUUCDA IYO SIFOYINKA RASMIGA AH
SIFOOYINKA BOT KA
1- in uu uu yaha python
2- in uu furo trade trade si uatomatic ah
3- in uu aqbali karo api iyo sicretka ku jira .env
4-in uu ku xidhmi karo api pionex si uu trade uga furo
6- in uu auto scan sameeyo 5 min
7-in aanu hal coin ku soo celcelin
8-in fursadaha uu ka faaidan karo
9-lacagta halkii 50 usdt
10.marku hal  scan sameeyo in uu furo hal trade oo macquula
11-hadii sadex trade furanyuhiin in uu ka fogaado in mid afraad la furo ilaa midi xidhmayo.
12.haduu  trade xidhmo in uu raadiyo trade kale
13-  in uu si fudud u furi karo trade marku soo helo trade waafaqsan shuruuda buy
14-exchange waa bybit
1. ha doorto coinska uu baadhay coinka buuxiyay dhammaan shuruudaha buyga
2. ka dhig TAKE PROFIT:LIMIT   STOPLOSS:MARKET labadan u isticmaal sl iyo tp
3. live trading:true
EMA 20 SCALPING STRATEGY — BUY ONLY
⚙️ 1. Dejinta Guud
• Indicator: EMA 20
• Timeframe: 5 Minutes (5M)
• Trend Measurement: Isbeddelka EMA 20 marka la barbar dhigo 5 shumac ka hor.
• EMA Slope: Ugu yaraan +0.10%.
• Trend Candles: Ugu yaraan 4 shumac oo aan EMA 20 taaban.
• Confirmation Candle: Jirka shumaca ≥ 60% baaxaddiisa.
• Risk-to-Reward: 1:2.
• Entry: Furitaanka shumaca xiga marka xaqiijintu dhammaato.
🟢 2. BUY— Shuruudaha BUY
Shuruudaha gelitaanka
• ✅ Trend: EMA 20 wuxuu kor ugu kacay ugu yaraan +0.10% marka la barbar dhigo qiimihiisii 5 shumac ka hor.
• ✅ Trend Candles: Ugu yaraan 4 shumac oo dhammaaday, mid kastaana Low-giisu ka sarreeyo EMA 20.
• ✅ Pullback: Qiimuhu dib ayuu ugu soo noqdaa EMA 20, shumacuna wuu taabtaa.
• ✅ Confirmation: Shumac bullish ah ayaa ku xirma EMA 20 korkiisa.
• ✅ Candle Strength: Jirka shumaca waa ugu yaraan 60% baaxadda shumaca oo dhan.
• ✅ Entry: BUY ka gal furitaanka shumaca xiga.
🛡️ Stop Loss (SL)
• Dhig wax yar ka hooseeya Swing Low-ga pullback-ka.
🎯 Take Profit (TP)
• TP = 2 jeer masaafada Entry ilaa SL.
• Risk-to-Reward = 1:2.
🧮 3. Qaacidooyinka SL iyo TPQodobkaBUYEntryFuritaanka shumaca xigaSLSwing Low − hoostiisaTPEntry + 2 × (Entry − SL)
🚫 4. Goorma ayaan BUY la gelayn?
• ❌ EMA 20 ma laha jiirad ku filan.
• ❌ Afarta shumac midkood ayaa taabtay EMA 20.
• ❌ Qiimuhu ma samayn pullback.
• ❌ Shumaca xaqiijintu ma buuxin shuruudda 60%.
• ❌ Shumaca xaqiijintu wuxuu ku xirmay dhinaca khaldan ee EMA 20.
• ❌ SL-ga lama xisaabin karo ama khatarta trade-ku waxay ka badan tahay xadka loo oggol yahay.
• 
coinska laga baadhayo trade
20 coin coin kii buuxiya  shuruuda buy ka fur trade
2:24 PM
Worked for 4m 19s
Waxaan kuu diyaariyey Python bot-ka Bybit Spot, iyo faylasha dejinta:

bybit_spot_bot
.py
.env.bybit
.example
requirements-bybit
.txt
Waxyaabaha ku jira: 20 coin oo default ah, EMA 20/5M buy-only shuruudahaaga, $50 trade kasta, ugu badnaan 3 trade oo furan, hal trade scan kasta, iyo inuusan coin hore loo trade-gareeyay dib u isticmaalin (xogtaas state ayuu kaydiyaa). Waxa kale oo uu leeyahay xad khatar oo caadi ahaan ah $1 trade kasta; trade-ka wuu dhaafayaa haddii SL-ku ka sarreeyo xadkaas.

Ogow: Waxaan u qaatay Bybit inuu yahay exchange-ka saxda ah, maadaama aad sidaas ku sheegtay qodobka 14; Pionex kuma xidhna. Bybit Spot wuxuu taageeraa market buy lagu qeexo qiime USDT ah, sidaas darteed bot-ku wuxuu adeegsadaa quoteCoin marka uu $50 gelinayo.⁠

⁠ Laakiin bot-kani wuxuu TP Limit iyo SL Market ku maamulaa barnaamijka laftiisa: waa inuu socdaa oo internet haystaa. Haddii uu istaago ama xiriirku go’o, SL-ku ma aha amar server-ka Bybit yaalla. Tani waa muhiim sababtoo ah dukumentiga Bybit wuxuu TP/SL ku xidhayaa Spot limit entry, halka bot-kani market entry adeegsado.⁠

⁠

Sida loo bilaabo:

Ku rakib: pip install -r requirements-bybit.txt
Nuqul ka samee .env.bybit.example oo u bixi .env, geli API key-gaaga.
Marka hore ku tijaabi BYBIT_TESTNET=true. API key-ga sii oo keliya oggolaanshaha Spot Trading; dami withdrawals.
Haddii aad rabto mainnet, BYBIT_TESTNET=false ka dhig oo geli CONFIRM_LIVE=YES_I_ACCEPT_REAL_TRADING_RISK. Bot-ku wuxuu leeyahay hubin dheeraad ah si looga hortago live orders si kama’ ah.
Faylka Python-ka waan syntax-check gareeyay; ma aanan ku tijaabin akoon ama API key dhab ah.⁠

⁠

2:29 PM
No file chosen
bybit_spot_bot.py
"""EMA20 5m spot BUY-only bot for Bybit Unified Trading Account.
​
Entry: market BUY using 50 USDT quote value.
Exits: bot-monitored TP limit sell and SL market sell.
Important: exits are not exchange-hosted brackets; keep this process online.
"""
from __future__ import annotations
​
import json
import logging
import os
import time
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from pathlib import Path
from typing import Any
​
from dotenv import load_dotenv
from pybit.unified_trading import HTTP
​
load_dotenv()
​
# ---- Configuration (.env) ----
API_KEY = os.getenv("BYBIT_API_KEY", "").strip()
API_SECRET = os.getenv("BYBIT_API_SECRET", "").strip()
TESTNET = os.getenv("BYBIT_TESTNET", "true").lower() == "true"
LIVE_TRADING = os.getenv("LIVE_TRADING", "false").lower() == "true"
CONFIRM_LIVE = os.getenv("CONFIRM_LIVE", "")
QUOTE_PER_TRADE = Decimal(os.getenv("QUOTE_PER_TRADE", "50"))
MAX_OPEN_TRADES = int(os.getenv("MAX_OPEN_TRADES", "3"))
MAX_RISK_USDT = Decimal(os.getenv("MAX_RISK_USDT", "1.00"))
SL_BUFFER_PCT = Decimal(os.getenv("SL_BUFFER_PCT", "0.05")) / Decimal("100")
LOOP_SECONDS = float(os.getenv("LOOP_SECONDS", "2"))
SYMBOLS = [s.strip().upper() for s in os.getenv(
    "SYMBOLS",
    "BTCUSDT,ETHUSDT,SOLUSDT,XRPUSDT,DOGEUSDT,ADAUSDT,LINKUSDT,AVAXUSDT,"
    "DOTUSDT,LTCUSDT,BCHUSDT,TRXUSDT,UNIUSDT,NEARUSDT,APTUSDT,ARBUSDT,"
    "OPUSDT,SUIUSDT,FILUSDT,ETCUSDT"
).split(",") if s.strip()]
STATE_FILE = Path(os.getenv("STATE_FILE", str(Path(__file__).with_name("bybit_bot_state.json"))))
​
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("bybit_bot.log", encoding="utf-8")],
)
log = logging.getLogger("bybit-spot-bot")
​
​
def D(value: Any) -> Decimal:
    return Decimal(str(value))
​
​
def api_result(response: dict) -> dict:
    if response.get("retCode") != 0:
        raise RuntimeError(f"Bybit error {response.get('retCode')}: {response.get('retMsg')}")
    return response.get("result", {})
​
​
def round_step(value: Decimal, step: Decimal, rounding=ROUND_DOWN) -> str:
    if step <= 0:
        return format(value, "f")
    units = (value / step).to_integral_value(rounding=rounding)
    return format(units * step, "f")
​
​
def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(STATE_FILE.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)
​
​
def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"positions": {}, "used_symbols": [], "pending_entry": None}
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    state.setdefault("positions", {})
    state.setdefault("used_symbols", [])
    state.setdefault("pending_entry", None)
    if state["pending_entry"]:
        raise RuntimeError(
            "State file shows an unfinished entry request. Reconcile Bybit orders/balances "
            "manually, then clear pending_entry only after confirming the account."
        )
    return state
​
​
if LIVE_TRADING and not TESTNET and CONFIRM_LIVE != "YES_I_ACCEPT_REAL_TRADING_RISK":
    raise SystemExit(
        "Mainnet orders blocked. Set CONFIRM_LIVE=YES_I_ACCEPT_REAL_TRADING_RISK "
        "after checking keys and risks."
    )
if LIVE_TRADING and (not API_KEY or not API_SECRET):
    raise SystemExit("LIVE_TRADING=true requires BYBIT_API_KEY and BYBIT_API_SECRET in .env")
​
session = HTTP(testnet=TESTNET, api_key=API_KEY or None, api_secret=API_SECRET or None)
state = load_state()
​
​
def load_instruments() -> dict[str, dict]:
    result = api_result(session.get_instruments_info(category="spot", limit=1000))
    rows = result.get("list", [])
    found = {}
    for row in rows:
        symbol = row.get("symbol", "").upper()
        if symbol not in SYMBOLS or row.get("status") != "Trading" or row.get("quoteCoin") != "USDT":
            continue
        lot = row.get("lotSizeFilter", {})
        price = row.get("priceFilter", {})
        found[symbol] = {
            "qty_step": D(lot.get("qtyStep", "0.00000001")),
            "min_qty": D(lot.get("minOrderQty", "0")),
            "min_amount": D(lot.get("minOrderAmt", "0")),
            "tick": D(price.get("tickSize", "0.00000001")),
        }
    missing = [s for s in SYMBOLS if s not in found]
    if missing:
        log.warning("Skipped unsupported/non-trading spot symbols: %s", ",".join(missing))
    if not found:
        raise RuntimeError("No configured USDT spot symbols are currently tradable")
    return found
​
​
INSTRUMENTS = load_instruments()
​
​
def get_tickers() -> dict[str, dict]:
    result = api_result(session.get_tickers(category="spot"))
    return {row["symbol"].upper(): row for row in result.get("list", [])}
​
​
def candles_for(symbol: str) -> list[dict]:
    result = api_result(session.get_kline(category="spot", symbol=symbol, interval="5", limit=100))
    # Bybit returns newest first. Exclude only a candle whose start is in the current 5m bucket.
    current_bucket_ms = int(time.time() // 300) * 300_000
    raw = list(reversed(result.get("list", [])))
    closed = [r for r in raw if int(r[0]) < current_bucket_ms]
    return [{"open": D(r[1]), "high": D(r[2]), "low": D(r[3]), "close": D(r[4])} for r in closed]
​
​
def ema(values: list[Decimal], period: int = 20) -> list[Decimal]:
    alpha = Decimal("2") / Decimal(period + 1)
    out = [values[0]]
    for value in values[1:]:
        out.append(value * alpha + out[-1] * (Decimal("1") - alpha))
    return out
​
​
def buy_signal(bars: list[dict]) -> dict | None:
    # Pattern: 4 completed candles with lows above EMA, one EMA-touch pullback,
    # then a strong bullish confirmation candle above EMA.
    if len(bars) < 30:
        return None
    closes = [b["close"] for b in bars]
    avgs = ema(closes, 20)
    i = len(bars) - 1                 # latest fully closed confirmation candle
    pull_i = i - 1
    trend_ids = list(range(i - 5, i - 1))  # four candles before pullback
    if trend_ids[0] < 5:
        return None
​
    slope = (avgs[i] / avgs[i - 5] - Decimal("1")) * Decimal("100")
    if slope < Decimal("0.10"):
        return None
    if not all(bars[j]["low"] > avgs[j] for j in trend_ids):
        return None
​
    pullback = bars[pull_i]
    if not (pullback["low"] <= avgs[pull_i] <= pullback["high"]):
        return None
​
    confirm = bars[i]
    candle_range = confirm["high"] - confirm["low"]
    if candle_range <= 0 or confirm["close"] <= confirm["open"]:
        return None
    body_ratio = (confirm["close"] - confirm["open"]) / candle_range
    if body_ratio < Decimal("0.60") or confirm["close"] <= avgs[i]:
        return None
​
    swing_low = pullback["low"]
    stop = swing_low * (Decimal("1") - SL_BUFFER_PCT)
    return {"stop": stop, "slope_pct": slope, "body_pct": body_ratio * Decimal("100")}
​
​
def get_order(symbol: str, order_id: str) -> dict | None:
    # Check real-time open orders first; order history can lag for newly submitted orders.
    try:
        result = api_result(session.get_open_orders(category="spot", symbol=symbol, orderId=order_id))
        rows = result.get("list", [])
        if rows:
            return rows[0]
    except Exception as exc:
        log.debug("Open-order lookup for %s failed: %s", order_id, exc)
    try:
        result = api_result(session.get_order_history(category="spot", symbol=symbol, orderId=order_id, limit=1))
        rows = result.get("list", [])
        return rows[0] if rows else None
    except Exception as exc:
        log.warning("Could not read order %s for %s: %s", order_id, symbol, exc)
        return None
​
​
def wait_for_order(symbol: str, order_id: str, seconds: float = 12) -> dict | None:
    end = time.time() + seconds
    latest = None
    while time.time() < end:
        latest = get_order(symbol, order_id) or latest
        if latest and latest.get("orderStatus") in {
            "Filled", "Cancelled", "Rejected", "PartiallyFilledCanceled", "Deactivated"
        }:
            return latest
        time.sleep(0.5)
    return latest
​
​
def order_fill_qty(order: dict | None) -> Decimal:
    return D((order or {}).get("cumExecQty", "0") or "0")
​
​
def close_position(symbol: str, pos: dict, qty: Decimal, reason: str) -> Decimal:
    meta = INSTRUMENTS[symbol]
    qty_text = round_step(qty, meta["qty_step"], ROUND_DOWN)
    qty = D(qty_text)
    if qty <= 0 or qty < meta["min_qty"]:
        log.error("%s remaining qty %s below min order; manual review needed", symbol, qty)
        return Decimal("0")
    if not LIVE_TRADING:
        log.warning("DRY RUN: would market-sell %s %s (%s)", qty_text, symbol, reason)
        return qty
    resp = api_result(session.place_order(
        category="spot", symbol=symbol, side="Sell", orderType="Market", qty=qty_text,
        marketUnit="baseCoin", isLeverage=0, orderLinkId=f"bot-exit-{int(time.time())}-{symbol[:6]}",
        slippageToleranceType="Percent", slippageTolerance="0.50",
    ))
    order = wait_for_order(symbol, resp["orderId"], seconds=12)
    sold = order_fill_qty(order)
    log.info("%s market sell %s/%s; reason=%s status=%s", symbol, sold, qty, reason,
             (order or {}).get("orderStatus", "unknown"))
    return sold
​
​
def manage_positions(tickers: dict[str, dict]) -> None:
    changed = False
    for symbol in list(state["positions"].keys()):
        pos = state["positions"].get(symbol)
        if not pos or symbol not in tickers:
            continue
        last = D(tickers[symbol].get("lastPrice", "0"))
        qty = D(pos.get("qty", "0"))
        stop, target = D(pos["stop"]), D(pos["target"])
        tp_id = pos.get("tp_order_id")
​
        # If a TP limit is active, update its filled quantity and avoid double-selling.
        if tp_id:
            order = get_order(symbol, tp_id)
            status = (order or {}).get("orderStatus", "")
            filled = order_fill_qty(order)
            if status == "Filled" or (qty - filled) <= 0:
                log.info("%s take-profit filled; position closed", symbol)
                state["positions"].pop(symbol, None)
                changed = True
                continue
            if status in {"Cancelled", "Rejected", "PartiallyFilledCanceled", "Deactivated"}:
                qty = max(Decimal("0"), qty - filled)
                pos["qty"] = str(qty)
                pos["tp_order_id"] = None
                pos.pop("tp_order_qty", None)
                changed = True
                if qty <= 0:
                    state["positions"].pop(symbol, None)
                    continue
                tp_id = None
            elif last <= stop:
                # Stop has priority: cancel TP first, then market-sell only the remainder.
                try:
                    api_result(session.cancel_order(category="spot", symbol=symbol, orderId=tp_id))
                except Exception as exc:
                    log.warning("Cancel TP failed for %s: %s; will re-check order", symbol, exc)
                latest = wait_for_order(symbol, tp_id, seconds=3) or order
                latest_status = (latest or {}).get("orderStatus", "")
                if latest_status == "Filled":
                    log.info("%s TP filled while cancelling; position closed", symbol)
                    state["positions"].pop(symbol, None)
                    changed = True
                    continue
                if latest_status not in {"Cancelled", "Rejected", "PartiallyFilledCanceled", "Deactivated"}:
                    # Never risk selling twice while the TP order may still be live.
                    log.error("%s TP cancellation not confirmed; will retry before SL sale", symbol)
                    continue
                filled = order_fill_qty(latest)
                qty = max(Decimal("0"), qty - filled)
                pos["qty"] = str(qty)
                pos["tp_order_id"] = None
                pos.pop("tp_order_qty", None)
                changed = True
                if qty <= 0:
                    state["positions"].pop(symbol, None)
                    continue
                sold = close_position(symbol, pos, qty, "stop-loss")
                remaining = max(Decimal("0"), qty - sold)
                if remaining <= 0:
                    state["positions"].pop(symbol, None)
                else:
                    pos["qty"] = str(remaining)
                    pos["tp_order_id"] = None
                    log.error("%s SL partially/unfilled; remaining %s still monitored", symbol, remaining)
                changed = True
                continue
            else:
                # Still-open TP order holds the base asset; do not submit another exit.
                continue
​
        if last <= stop:
            sold = close_position(symbol, pos, qty, "stop-loss")
            remaining = max(Decimal("0"), qty - sold)
            if remaining <= 0:
                state["positions"].pop(symbol, None)
            else:
                pos["qty"] = str(remaining)
                log.error("%s SL partially/unfilled; remaining %s still monitored", symbol, remaining)
            changed = True
            continue
​
        if last >= target and not pos.get("tp_order_id"):
            meta = INSTRUMENTS[symbol]
            qty_text = round_step(qty, meta["qty_step"], ROUND_DOWN)
            tp_text = round_step(target, meta["tick"], ROUND_UP)
            if not LIVE_TRADING:
                log.info("DRY RUN: %s TP limit sell qty=%s price=%s", symbol, qty_text, tp_text)
                continue
            try:
                result = api_result(session.place_order(
                    category="spot", symbol=symbol, side="Sell", orderType="Limit",
                    qty=qty_text, price=tp_text, timeInForce="GTC", isLeverage=0,
                    orderLinkId=f"bot-tp-{int(time.time())}-{symbol[:6]}",
                ))
                pos["tp_order_id"] = result["orderId"]
                pos["tp_order_qty"] = qty_text
                changed = True
                log.info("%s TP limit submitted qty=%s price=%s", symbol, qty_text, tp_text)
            except Exception as exc:
                log.exception("Could not submit TP limit for %s: %s", symbol, exc)
    if changed:
        save_state(state)
​
​
def scan_once(tickers: dict[str, dict]) -> None:
    if len(state["positions"]) >= MAX_OPEN_TRADES:
        log.info("Open trade limit reached (%s/%s)", len(state["positions"]), MAX_OPEN_TRADES)
        return
    open_symbols = set(state["positions"])
    used_symbols = set(state["used_symbols"])
    for symbol in SYMBOLS:
        if symbol not in INSTRUMENTS or symbol in open_symbols or symbol in used_symbols:
            continue
        try:
            signal = buy_signal(candles_for(symbol))
            if not signal:
                continue
            ticker = tickers.get(symbol, {})
            estimate = D(ticker.get("ask1Price") or ticker.get("lastPrice") or "0")
            stop = signal["stop"]
            if estimate <= stop or estimate <= 0:
                continue
            estimated_risk = QUOTE_PER_TRADE * (estimate - stop) / estimate
            if estimated_risk > MAX_RISK_USDT:
                log.info("Skip %s: estimated stop risk %.4f USDT exceeds cap %.2f",
                         symbol, estimated_risk, MAX_RISK_USDT)
                continue
            meta = INSTRUMENTS[symbol]
            if QUOTE_PER_TRADE < meta["min_amount"]:
                log.info("Skip %s: trade value below exchange min amount", symbol)
                continue
​
            log.info("BUY signal %s slope=%.3f%% body=%.1f%% est-risk=%.3f USDT",
                     symbol, signal["slope_pct"], signal["body_pct"], estimated_risk)
            if not LIVE_TRADING:
                log.warning("DRY RUN: no order sent for %s (set LIVE_TRADING=true to enable)", symbol)
                return  # one qualifying candidate max per scan
​
            # Persist a pending marker before sending an order to prevent duplicate buys after a crash.
            state["pending_entry"] = {"symbol": symbol, "created_at": int(time.time())}
            save_state(state)
            try:
                result = api_result(session.place_order(
                    category="spot", symbol=symbol, side="Buy", orderType="Market",
                    qty=str(QUOTE_PER_TRADE), marketUnit="quoteCoin", isLeverage=0,
                    orderLinkId=f"bot-entry-{int(time.time())}-{symbol[:6]}",
                    slippageToleranceType="Percent", slippageTolerance="0.50",
                ))
                entry_id = result["orderId"]
                order = wait_for_order(symbol, entry_id, seconds=12)
                if not order or order_fill_qty(order) <= 0:
                    try:
                        api_result(session.cancel_order(category="spot", symbol=symbol, orderId=entry_id))
                    except Exception:
                        pass
                    order = get_order(symbol, entry_id) or order
                filled_qty = order_fill_qty(order)
                avg_price = D((order or {}).get("avgPrice", "0") or "0")
                if filled_qty <= 0 or avg_price <= 0:
                    raise RuntimeError("Entry order has no confirmed fill; check Bybit before restarting")
​
                target = avg_price + Decimal("2") * (avg_price - stop)
                actual_risk = filled_qty * (avg_price - stop)
                # Approximate quote risk from actual filled base quantity; do not leave an oversized trade.
                if stop >= avg_price or actual_risk > MAX_RISK_USDT:
                    log.error("Actual fill violates risk cap; emergency market exit for %s", symbol)
                    sold = close_position(symbol, {"qty": str(filled_qty)}, filled_qty, "risk-cap breach")
                    remaining = max(Decimal("0"), filled_qty - sold)
                    state["pending_entry"] = None
                    if remaining > 0:
                        # Keep any unsold amount tracked instead of leaving it unmanaged.
                        state["positions"][symbol] = {
                            "qty": str(remaining), "entry": str(avg_price),
                            "stop": str(stop), "target": str(target),
                            "tp_order_id": None, "opened_at": int(time.time()),
                        }
                    state["used_symbols"].append(symbol)
                    save_state(state)
                    return
​
                state["positions"][symbol] = {
                    "qty": str(filled_qty), "entry": str(avg_price),
                    "stop": str(stop), "target": str(target),
                    "tp_order_id": None, "opened_at": int(time.time()),
                }
                state["used_symbols"].append(symbol)
                state["pending_entry"] = None
                save_state(state)
                log.info("OPEN %s qty=%s entry=%s SL=%s TP=%s", symbol, filled_qty, avg_price, stop, target)
            except Exception:
                # Keep pending marker if submission status is uncertain; never auto-repeat blindly.
                log.exception("Entry failed/uncertain for %s; reconcile pending_entry manually", symbol)
                raise
            return  # exactly one new trade per scan
        except Exception as exc:
            log.warning("Scan error for %s: %s", symbol, exc)
            if state.get("pending_entry"):
                log.error("Pending entry is uncertain; stopping further scans to avoid a duplicate buy")
                return
​
​
def main() -> None:
    mode = "LIVE MAINNET" if LIVE_TRADING and not TESTNET else ("TESTNET" if LIVE_TRADING else "DRY RUN")
    log.warning("Starting Bybit spot bot | mode=%s | symbols=%d | stake=%s USDT | max trades=%d",
                mode, len(SYMBOLS), QUOTE_PER_TRADE, MAX_OPEN_TRADES)
    log.warning("Bot-managed exits only: keep this process and internet connection running")
    last_scan_bucket = int(time.time() // 300)  # wait for next 5-minute boundary
    while True:
        try:
            tickers = get_tickers()
            manage_positions(tickers)
            bucket = int(time.time() // 300)
            if bucket != last_scan_bucket:
                last_scan_bucket = bucket
                scan_once(tickers)
        except KeyboardInterrupt:
            log.info("Stopped by user")
            return
        except Exception as exc:
            log.exception("Main loop error: %s", exc)
            time.sleep(5)
        time.sleep(LOOP_SECONDS)
​
​
if __name__ == "__main__":
    main()
​
