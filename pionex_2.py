import os
import json
import math
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
TIMEFRAME = "5M"                 # Pionex wuxuu u baahan yahay xaraf weyn (5M)
MIN_VOLUME = 8_000_000
SCAN_EVERY = 300                 # scan 5 daqiiqo kasta
MONITOR_EVERY = 10               # hubi SL/TP 10 sekan kasta
STATE_FILE = "pionex_trades.json"

# DRY_RUN=true (.env) = tijaabo, dalab dhab ah ma dirayo
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

_symbol_info = {}


# ---------------------------------------------------------------- API ---
def api_request(method, path, params=None, body=None):
    """Codsi saxiixan (signed) u dira Pionex."""
    params = dict(params or {})
    params["timestamp"] = str(int(time.time() * 1000))
