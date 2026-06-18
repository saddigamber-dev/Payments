import os
import time
import hmac
import hashlib
import requests
from fastapi import FastAPI
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load Environment Variables (API Keys)
load_dotenv()

app = FastAPI()

# Your API Keys from Render Environment
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Binance API Protocol
def fetch_binance_address(coin: str, network: str = "BSC"):
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        return "Backend API Keys Not Configured"

    base_url = "https://api.binance.com"
    endpoint = "/sapi/v1/capital/deposit/address"
    
    # Binance requires a timestamp to prevent replay attacks
    timestamp = int(time.time() * 1000)
    query_string = f"coin={coin}&network={network}&timestamp={timestamp}"
    
    # Generate cryptographic signature
    signature = hmac.new(
        BINANCE_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        # Returns the dynamic address or error message from Binance
        return data.get("address", data.get("msg", "Address Not Found"))
    except Exception as e:
        return "Error Communicating with Binance"

# Secure API Endpoint for your Frontend
@app.get("/api/get-crypto-addresses")
def get_crypto_addresses():
    return {
        "usdt": fetch_binance_address("USDT"),
        "btcb": fetch_binance_address("BTC"),
        "eth": fetch_binance_address("ETH"),
        "bnb": fetch_binance_address("BNB")
    }

# SPA Catch-All Router (Prevents Render 404s for /upi, /crypto etc.)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("static/index.html")
