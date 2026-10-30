import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://api.pionex.com"
STATE_FILE = Path(os.getenv("STATE_FILE", "bot_state.json"))

# Live trading wuxuu shaqaynayaa oo keliya haddii labada qiime si cad loo dejiyo.
LIVE_TRADING = os.getenv("LIVE_TRADING", "NO").upper() == "YES"
LIVE_CONFIRM = os.getenv("LIVE_CONFIRM", "")
REQUIRED_CONFIRM = "I_ACCEPT_LIVE_CRYPTO_LOSS_RISK"

API_KEY = os.getenv("PIONEX_API_KEY", "")
API_SECRET = os.getenv("PIONEX_API_SECRET", "")

ORDER_USDT = 50.0
MAX_OPEN_TRADES = 3
MIN_24H_USDT = 8_000_000.0
MAX_SPREAD_PERCENT = 0.10
MAX_CANDIDATES = 20
MAX_RISK_USDT = float(os.getenv("MAX_RISK_USDT", "1.0"))
STOP_BUFFER_PERCENT = 0.05
SCAN_SECONDS = 300
MONITOR_SECONDS = 10
ENTRY_WINDOW_SECONDS = 45
EMA_PERIOD = 20
KLINE_MS = 5 * 60 * 1000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def load_state():
    if not STATE_FILE.exists():
        return {
            "positions": {},
            "traded_symbols": [],
            "last_scan_slot": None,
            "pending": None,
        }

    try:
        state = json.loads(STATE_FILE.read_text())
        state.setdefault("positions", {})
        state.setdefault("traded_symbols", [])
        state.setdefault("last_scan_slot", None)
        state.setdefault("pending", None)
        return state
    except Exception as exc:
        raise RuntimeError(
            f"State file lama akhrin karin; bot-ku wuu istaagay: {exc}"
        )


def save_state(state):
    temp_file = STATE_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(STATE_FILE)


class Pionex:
    def __init__(self):
        self.session = requests.Session()

    def request(self, method, path, params=None, body=None, private=False):
        method = method.upper()
        query_params = {k: str(v) for k, v in (params or {}).items()}
        body_text = (
            json.dumps(body, separators=(",", ":"), ensure_ascii=False)
            if body is not None
            else ""
        )

        headers = {"Accept": "application/json"}

        if private:
            if not API_KEY or not API_SECRET:
                raise RuntimeError("API key/secret kuma jiraan .env")

            query_params["timestamp"] = str(int(time.time() * 1000))
            sorted_params = sorted(query_params.items())
            query_string = "&".join(f"{key}={value}" for key, value in sorted_params)

            signed_path = path
            if query_string:
                signed_path += "?" + query_string

            message = method + signed_path + body_text
            signature = hmac.new(
                API_SECRET.encode(),
                message.encode(),
                hashlib.sha256,
            ).hexdigest()

            headers["PIONEX-KEY"] = API_KEY
            headers["PIONEX-SIGNATURE"] = signature
            if body is not None:
                headers["Content-Type"] = "application/json"

            query_params = sorted_params

        response = self.session.request(
            method=method,
            url=BASE_URL + path,
            params=sorted(query_params.items())
            if isinstance(query_params, dict)
            else query_params,
            data=body_text if body is not None else None,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("result") is False:
            raise RuntimeError(
                f"Pionex API error: {result.get('code')} — {result.get('message')}"
            )
        return result

    def public(self, path, params=None):
        return self.request("GET", path, params=params, private=False)

    def private(self, method, path, params=None, body=None):
        return self.request(
            method, path, params=params, body=body, private=True
        )

    def get_order(self, order_id):
        result = self.private(
            "GET",
            "/api/v1/trade/order",
            params={"orderId": order_id},
        )
        return result.get("data", {})

    def wait_for_closed_order(self, order_id, timeout_seconds=12):
        end = time.time() + timeout_seconds
        while time.time() < end:
            order = self.get_order(order_id)
            if str(order.get("status", "")).upper() == "CLOSED":
                return order
            time.sleep(1)
        raise RuntimeError(
            f"Order {order_id} lama la xaqiijin inuu xirmay. "
            "Pending-ka waa la hayaa si aan amar labaad loo dirin."
        )

    def free_usdt(self):
        result = self.private("GET", "/api/v1/account/balances")
        balances = result.get("data", {}).get("balances", [])
        for balance in balances:
            if balance.get("coin") == "USDT":
                return float(balance.get("free", 0))
        return 0.0


def get_market_snapshot(api):
    tickers_result = api.public(
        "/api/v1/market/tickers",
        params={"type": "SPOT"},
    )
    books_result = api.public(
        "/api/v1/market/bookTickers",
        params={"type": "SPOT"},
    )

    tickers = {
        item["symbol"]: item
        for item in tickers_result.get("data", {}).get("tickers", [])
        if item.get("symbol")
    }
    books = {
        item["symbol"]: item
        for item in books_result.get("data", {}).get("tickers", [])
        if item.get("symbol")
    }
    return tickers, books


def ema_series(values, period):
    alpha = 2.0 / (period + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(alpha * value + (1 - alpha) * result[-1])
    return result


def find_buy_signal(api, symbol):
    now_ms = int(time.time() * 1000)
    next_candle_open = (now_ms // KLINE_MS) * KLINE_MS

    # Haddii furitaanka shumaca xiga waqti badan ka soo wareegay, ha gelin.
    if now_ms - next_candle_open > ENTRY_WINDOW_SECONDS * 1000:
        return None

    result = api.public(
        "/api/v1/market/klines",
        params={"symbol": symbol, "interval": "5M", "limit": 100},
    )
    rows = result.get("data", {}).get("klines", [])
    rows = sorted(rows, key=lambda row: int(row["time"]))

    # Ka saar shumaca hadda socda; go'aanka wuxuu ku salaysan yahay shumacyo xirmay.
    candles = [
        row for row in rows
        if int(row["time"]) < next_candle_open
    ]

    if len(candles) < EMA_PERIOD + 6:
        return None

    closes = [float(candle["close"]) for candle in candles]
    ema = ema_series(closes, EMA_PERIOD)

    # EMA-ga ugu dambeeya waa inuu ugu yaraan 0.10% ka sarreeyaa kii 5 shumac ka hor.
    slope_percent = (ema[-1] / ema[-6] - 1) * 100
    if slope_percent < 0.10:
        return None

    # Afarta shumac ee ka horreeya pullback-ka: low kastaa waa inuu EMA ka sarreeyaa.
    prior_four = candles[-6:-2]
    prior_ema = ema[-6:-2]
    if len(prior_four) != 4:
        return None

    for candle, ema_value in zip(prior_four, prior_ema):
        if float(candle["low"]) <= ema_value:
            return None

    # Shumaca ka horreeya xaqiijinta waa inuu EMA taabtay.
    pullback = candles[-2]
    pullback_ema = ema[-2]
    if not (
        float(pullback["low"]) <= pullback_ema
        and float(pullback["high"]) >= pullback_ema
    ):
        return None

    # Shumaca xaqiijintu waa bullish, wuxuu ku xirmayaa EMA korkiisa,
    # jirkiisuna waa ugu yaraan 60% baaxadda shumaca.
    confirm = candles[-1]
    open_price = float(confirm["open"])
    close_price = float(confirm["close"])
    high_price = float(confirm["high"])
    low_price = float(confirm["low"])
    candle_range = high_price - low_price

    if candle_range <= 0:
        return None
    if close_price <= open_price or close_price <= ema[-1]:
        return None
    if abs(close_price - open_price) / candle_range < 0.60:
        return None

    return {
        "pullback_low": float(pullback["low"]),
        "next_candle_open": next_candle_open,
        "slope_percent": slope_percent,
    }


def place_live_market_buy(api, state, symbol, pullback_low, ask_price):
    stop_price = pullback_low * (1 - STOP_BUFFER_PERCENT / 100)
    estimated_qty = ORDER_USDT / ask_price
    estimated_risk = estimated_qty * (ask_price - stop_price)

    if ask_price <= stop_price or stop_price <= 0:
        logging.info("%s: SL sax ah lama xisaabin karo; waa la dhaafay.", symbol)
        return

    if estimated_risk > MAX_RISK_USDT:
        logging.info(
            "%s: khatarta la qiyaasay %.4f USDT waxay ka badan tahay xadka %.2f; waa la dhaafay.",
            symbol, estimated_risk, MAX_RISK_USDT
        )
        return

    if LIVE_TRADING and api.free_usdt() < ORDER_USDT:
        logging.info("%s: balance-ka USDT kuma filna.", symbol)
        return

    if not LIVE_TRADING:
        entry = ask_price
        qty = ORDER_USDT / entry
        position = {
            "qty": qty,
            "entry": entry,
            "stop": stop_price,
            "target": entry + 2 * (entry - stop_price),
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "mode": "paper",
        }
        state["positions"][symbol] = position
        state["traded_symbols"].append(symbol)
        save_state(state)
        logging.info(
            "PAPER BUY %s entry=%.8f SL=%.8f TP=%.8f",
            symbol, entry, position["stop"], position["target"]
        )
        return

    client_order_id = uuid.uuid4().hex
    state["pending"] = {
        "side": "BUY",
        "symbol": symbol,
        "clientOrderId": client_order_id,
    }
    save_state(state)

    response = api.private(
        "POST",
        "/api/v1/trade/order",
        body={
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "amount": str(ORDER_USDT),
            "clientOrderId": client_order_id,
        },
    )
    order_id = response.get("data", {}).get("orderId")
    if not order_id:
        raise RuntimeError("Buy order jawaabtiisa orderId ma lahayn; hubi Pionex.")

    state["pending"]["orderId"] = order_id
    save_state(state)

    order = api.wait_for_closed_order(order_id)
    qty = float(order.get("filledSize", 0))
    filled_amount = float(order.get("filledAmount", 0))
    if qty <= 0 or filled_amount <= 0:
        raise RuntimeError("Buy order fill-kiisa lama xaqiijin; hubi Pionex.")

    entry = filled_amount / qty
    if entry <= stop_price:
        raise RuntimeError(
            "Qiimaha fill-ku SL-ga ayuu la siman yahay ama ka hooseeyaa. "
            "Pending state waa la hayaa; hubi oo maamul booska gacanta."
        )

    position = {
        "qty": qty,
        "entry": entry,
        "stop": stop_price,
        "target": entry + 2 * (entry - stop_price),
        "opened_at": datetime.now(timezone.utc).isoformat(),
        "mode": "live",
    }
    state["positions"][symbol] = position
    state["traded_symbols"].append(symbol)
    state["pending"] = None
    save_state(state)

    logging.info(
        "LIVE BUY %s qty=%.8f entry=%.8f SL=%.8f TP=%.8f",
        symbol, qty, entry, position["stop"], position["target"]
    )


def close_position(api, state, symbol, current_bid, reason):
    position = state["positions"][symbol]

    if position.get("mode") == "paper":
        del state["positions"][symbol]
        save_state(state)
        logging.info("PAPER SELL %s price=%.8f sabab=%s", symbol, current_bid, reason)
        return

    qty = float(position["qty"])
    client_order_id = uuid.uuid4().hex

    state["pending"] = {
        "side": "SELL",
        "symbol": symbol,
        "clientOrderId": client_order_id,
        "qty": qty,
    }
    save_state(state)

    response = api.private(
        "POST",
        "/api/v1/trade/order",
        body={
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "size": f"{qty:.8f}",
            "clientOrderId": client_order_id,
        },
    )
    order_id = response.get("data", {}).get("orderId")
    if not order_id:
        raise RuntimeError("Sell order jawaabtiisa orderId ma lahayn; hubi Pionex.")

    state["pending"]["orderId"] = order_id
    save_state(state)

    order = api.wait_for_closed_order(order_id)
    filled_qty = float(order.get("filledSize", 0))
    if filled_qty <= 0:
        raise RuntimeError("Sell order fill-kiisa lama xaqiijin; hubi Pionex.")

    remaining = max(0.0, qty - filled_qty)
    if remaining < 0.00000001:
        del state["positions"][symbol]
    else:
        state["positions"][symbol]["qty"] = remaining

    state["pending"] = None
    save_state(state)
    logging.info("LIVE SELL %s price≈%.8f sabab=%s", symbol, current_bid, reason)


def monitor_positions(api, state):
    if not state["positions"]:
        return

    _, books = get_market_snapshot(api)

    for symbol, position in list(state["positions"].items()):
        book = books.get(symbol)
        if not book:
            continue

        bid = float(book.get("bidPrice", 0))
        if bid <= 0:
            continue

        if bid <= float(position["stop"]):
            close_position(api, state, symbol, bid, "stop-loss")
        elif bid >= float(position["target"]):
            close_position(api, state, symbol, bid, "take-profit")


def scan_and_trade(api, state):
    if len(state["positions"]) >= MAX_OPEN_TRADES:
        logging.info("Waxaa jira 3 trade oo furan; scan cusub lama gelinayo.")
        return

    tickers, books = get_market_snapshot(api)
    candidates = []

    for symbol, ticker in tickers.items():
        if not symbol.endswith("_USDT"):
            continue

        # "amount" waxaa halkan loogu adeegsaday 24h turnover-ka quote/USDT.
        turnover = float(ticker.get("amount", 0))
        book = books.get(symbol)
        if turnover < MIN_24H_USDT or not book:
            continue

        bid = float(book.get("bidPrice", 0))
        ask = float(book.get("askPrice", 0))
        if bid <= 0 or ask <= 0:
            continue

        mid = (bid + ask) / 2
        spread_percent = ((ask - bid) / mid) * 100
        if spread_percent <= MAX_SPREAD_PERCENT:
            candidates.append({
                "symbol": symbol,
                "turnover": turnover,
                "ask": ask,
            })

    candidates.sort(key=lambda item: item["turnover"], reverse=True)
    candidates = candidates[:MAX_CANDIDATES]

    for candidate in candidates:
        symbol = candidate["symbol"]

        if symbol in state["traded_symbols"] or symbol in state["positions"]:
            continue

        signal = find_buy_signal(api, symbol)
        if not signal:
            continue

        # Hubi in entry-ga shumaca xiga weli ku jiro waqtiga loo oggol yahay.
        if (
            int(time.time() * 1000) - signal["next_candle_open"]
            > ENTRY_WINDOW_SECONDS * 1000
        ):
            logging.info("%s: entry window wuu dhaafay; waa la dhaafay.", symbol)
            continue

        logging.info(
            "BUY signal %s, EMA slope=%.3f%%",
            symbol, signal["slope_percent"]
        )
        place_live_market_buy(
            api,
            state,
            symbol,
            signal["pullback_low"],
            candidate["ask"],
        )
        return  # Hal trade oo keliya scan kasta.


def main():
    if LIVE_TRADING:
        if LIVE_CONFIRM != REQUIRED_CONFIRM:
            raise SystemExit(
                "Live trading lama bilaabin: LIVE_CONFIRM si sax ah u deji."
            )
        if not API_KEY or not API_SECRET:
            raise SystemExit("PIONEX_API_KEY iyo PIONEX_API_SECRET ayaa loo baahan yahay.")

    state = load_state()

    # Haddii amar hore xaaladdiisa aan la xaqiijin, bot-ku ma dirayo amar kale.
    if state.get("pending"):
        raise SystemExit(
            "Waxaa jira order pending ah oo aan la xaqiijin. "
            "Ka hubi Pionex ka hor intaadan bot-ka dib u bilaabin."
        )

    api = Pionex()
    logging.info(
        "Bot-ku wuu bilaabmay; mode=%s",
        "LIVE" if LIVE_TRADING else "PAPER"
    )

    while True:
        monitor_positions(api, state)

        scan_slot = int(time.time() // SCAN_SECONDS)
        if state.get("last_scan_slot") != scan_slot:
            state["last_scan_slot"] = scan_slot
            save_state(state)
            scan_and_trade(api, state)

        time.sleep(MONITOR_SECONDS)


if __name__ == "__main__":
    main()
