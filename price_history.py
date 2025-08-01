import requests
import logging

logger = logging.getLogger(__name__)

COINGECKO_IDS = {
    'ETH': 'ethereum',
    'BTC': 'bitcoin',
    'SOL': 'solana',
    'USDT': 'tether',
    'USDC': 'usd-coin',
    'DAI': 'dai'
}

def get_price_history(tokens, days=30):
    """Get price history for multiple tokens"""
    results = {}
    for symbol in tokens:
        if symbol not in COINGECKO_IDS:
            results[symbol] = {"error": f"Token {symbol} not supported"}
            continue
        try:
            coin_id = COINGECKO_IDS[symbol]
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                prices = [round(p[1], 2) for p in data['prices']]
                timestamps = [p[0] for p in data['prices']]
                results[symbol] = {
                    "prices": prices, 
                    "timestamps": timestamps,
                    "success": True
                }
            else:
                results[symbol] = {"error": f"API request failed with status {response.status_code}"}
        except Exception as e:
            results[symbol] = {"error": str(e)}
    return results

def get_single_token_history(coin_id, days=30):
    """Get price history for a single token by coin ID"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            prices = data['prices']
            return {
                "success": True,
                "prices": prices,
                "coin_id": coin_id,
                "days": days
            }
        else:
            return {"error": f"API request failed with status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_current_price(coin_id):
    """Get current price for a specific coin"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                return {
                    "success": True,
                    "price": data[coin_id]["usd"],
                    "coin_id": coin_id
                }
        return {"error": "Failed to fetch price data"}
    except Exception as e:
        return {"error": str(e)}

def get_supported_tokens():
    """Get list of supported tokens"""
    return {
        "success": True,
        "tokens": [
            {"symbol": "ETH", "name": "Ethereum", "id": "ethereum"},
            {"symbol": "BTC", "name": "Bitcoin", "id": "bitcoin"},
            {"symbol": "SOL", "name": "Solana", "id": "solana"},
            {"symbol": "USDT", "name": "Tether", "id": "tether"},
            {"symbol": "USDC", "name": "USD Coin", "id": "usd-coin"},
            {"symbol": "DAI", "name": "Dai", "id": "dai"}
        ]
    }
