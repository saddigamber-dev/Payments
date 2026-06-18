import os
import time
import hmac
import hashlib
import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load Environment Variables from Render
load_dotenv()

app = FastAPI()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

def fetch_binance_address(coin: str, network: str):
    """Securely fetches dynamic deposit address directly from Binance."""
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        return "ERROR: API Keys Missing in Backend"

    base_url = "https://api.binance.com"
    endpoint = "/sapi/v1/capital/deposit/address"
    
    timestamp = int(time.time() * 1000)
    query_string = f"coin={coin}&network={network}&timestamp={timestamp}"
    
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
        
        if "address" in data:
            return data["address"]
        return data.get("msg", "Network Unvailable on Binance")
    except Exception as e:
        return "Backend Connection Error"

# Dynamic Route for All Crypto Coins
@app.get("/api/address")
def get_address(coin: str = Query(...), network: str = Query(...)):
    """API Endpoint for Frontend to fetch ANY coin address."""
    address = fetch_binance_address(coin.upper(), network.upper())
    return {"coin": coin, "network": network, "address": address}

# SPA Router to serve the static frontend without 404 errors
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("static/index.html")
    
