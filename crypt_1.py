import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
if not ETHERSCAN_API_KEY:
    print("WARNING: ETHERSCAN_API_KEY not found in environment variables. Please set it in your .env file.")

def get_eth_balance(address):
    """Get ETH balance for a given address"""
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "1":
                eth_balance = int(result["result"]) / 10**18  # Convert Wei to ETH
                return eth_balance
        return None
    except Exception as e:
        print(f"Error getting ETH balance: {e}")
        return None

def get_token_balances(address):
    """Get token balances for a given address"""
    url = f"https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress={{contract}}&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
    return url  # You can expand this for specific token contracts

def get_eth_price():
    """Get current ETH price in USD"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["ethereum"]["usd"]
        return None
    except Exception as e:
        print(f"Error getting ETH price: {e}")
        return None

def get_coin_price(coin_id):
    """Get current price for any supported coin"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                return data[coin_id]["usd"]
        return None
    except Exception as e:
        print(f"Error getting {coin_id} price: {e}")
        return None

def track_wallet(address):
    """Track wallet balance and value - returns data instead of printing"""
    eth_balance = get_eth_balance(address)
    if eth_balance is None:
        return {"error": "Invalid wallet address or API error."}

    eth_price = get_eth_price()
    if eth_price is None:
        return {"error": "Failed to retrieve ETH price."}

    total_value = eth_balance * eth_price
    
    return {
        "address": address,
        "eth_balance": eth_balance,
        "eth_price": eth_price,
        "total_value": total_value,
        "portfolio": [{
            'Coin': 'ETH',
            'Amount': eth_balance,
            'Price (USD)': eth_price,
            'Value (USD)': total_value
        }]
    }

def get_wallet_summary(address):
    """Get a formatted summary of wallet data"""
    data = track_wallet(address)
    if "error" in data:
        return data
    
    df = pd.DataFrame(data["portfolio"])
    return {
        "summary": df.to_string(index=False),
        "total_value": data["total_value"],
        "data": data
    }

# Keep the original main execution for backward compatibility
if __name__ == "__main__":
    wallet = input("Enter your Ethereum wallet address: ").strip()
    result = track_wallet(wallet)
    if "error" in result:
        print(result["error"])
    else:
        df = pd.DataFrame(result["portfolio"])
        print(df.to_string(index=False))
        print(f"\nTotal Wallet Value: ${result['total_value']:.2f}")