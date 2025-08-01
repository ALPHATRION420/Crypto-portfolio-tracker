from flask import Flask, render_template, jsonify, request, Response
from crypt_1 import get_eth_balance, get_eth_price, track_wallet
from price_history import get_price_history, COINGECKO_IDS
import requests
import json
import time
import threading
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store for active SSE connections and transaction monitoring
active_connections = {}
transaction_monitors = {}

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/wallet')
def wallet():
    return render_template('wallet.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/price/<coin_id>')
def get_coin_price(coin_id):
    """Get current price for a specific coin"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                return jsonify({
                    'success': True,
                    'price': data[coin_id]['usd'],
                    'coin': coin_id
                })
        return jsonify({'success': False, 'error': 'Failed to fetch price'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/chart/<coin_id>')
def get_chart_data(coin_id):
    """Get historical price data for charting"""
    try:
        days = request.args.get('days', '30')
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            prices = data['prices']
            labels = [p[0] for p in prices]  # timestamps
            values = [p[1] for p in prices]  # prices
            
            return jsonify({
                'success': True,
                'labels': labels,
                'values': values,
                'coin': coin_id,
                'days': days
            })
        return jsonify({'success': False, 'error': 'Failed to fetch chart data'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wallet/<address>')
def get_wallet_data(address):
    """Get wallet balance and value"""
    logger.info(f"Getting wallet data for address: {address}")
    try:
        eth_balance = get_eth_balance(address)
        if eth_balance is None:
            logger.error(f"Failed to get ETH balance for address: {address}")
            return jsonify({'success': False, 'error': 'Invalid wallet address or API error'})
        
        eth_price = get_eth_price()
        if eth_price is None:
            logger.error(f"Failed to get ETH price")
            return jsonify({'success': False, 'error': 'Failed to retrieve ETH price'})
        
        total_value = eth_balance * eth_price
        logger.info(f"Wallet data retrieved successfully - Balance: {eth_balance}, Price: {eth_price}, Total: {total_value}")
        
        return jsonify({
            'success': True,
            'address': address,
            'eth_balance': eth_balance,
            'eth_price': eth_price,
            'total_value': total_value
        })
    except Exception as e:
        logger.error(f"Error getting wallet data for {address}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/transactions/<address>')
def get_transactions(address):
    """Get recent transactions for a wallet address"""
    logger.info(f"Getting transactions for address: {address}")
    try:
        etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
        if not etherscan_api_key:
            logger.error("ETHERSCAN_API_KEY not found in environment variables")
            return jsonify({'success': False, 'error': 'API key not configured'})
            
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={etherscan_api_key}"
        response = requests.get(url)
        
        logger.info(f"Etherscan API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Etherscan API response: {data}")
            
            if data["status"] == "1":
                transactions = data["result"][:10]  # Get first 10 transactions
                logger.info(f"Retrieved {len(transactions)} transactions for {address}")
                return jsonify({
                    'success': True,
                    'transactions': transactions
                })
            else:
                logger.error(f"Etherscan API error for {address}: {data}")
                return jsonify({'success': False, 'error': 'Failed to fetch transactions'})
        else:
            logger.error(f"Etherscan API HTTP error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': 'API request failed'})
    except Exception as e:
        logger.error(f"Error getting transactions for {address}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/eth-price-history')
def get_eth_price_history():
    """Get ETH price history for the last 24 hours"""
    logger.info("Getting ETH price history")
    try:
        url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=1"
        response = requests.get(url)
        
        logger.info(f"CoinGecko API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            prices = data['prices']
            logger.info(f"Retrieved {len(prices)} price points for ETH")
            return jsonify({
                'success': True,
                'prices': prices
            })
        else:
            logger.error(f"CoinGecko API HTTP error: {response.status_code} - {response.text}")
            return jsonify({'success': False, 'error': 'Failed to fetch price history'})
    except Exception as e:
        logger.error(f"Error getting ETH price history: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stream/transactions/<address>')
def stream_transactions(address):
    """Server-Sent Events endpoint for real-time transaction streaming"""
    def generate():
        # Add this connection to active connections
        if address not in active_connections:
            active_connections[address] = []
        active_connections[address].append(generate)
        
        # Start monitoring if not already monitoring
        if address not in transaction_monitors:
            start_transaction_monitor(address)
        
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'address': address})}\n\n"
            
            # Keep connection alive and send updates
            last_check = datetime.now()
            while True:
                time.sleep(1)  # Check every second
                
                # Send heartbeat every 30 seconds
                if (datetime.now() - last_check).seconds >= 30:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    last_check = datetime.now()
                    
        except GeneratorExit:
            # Remove connection when client disconnects
            if address in active_connections and generate in active_connections[address]:
                active_connections[address].remove(generate)
            if address in active_connections and not active_connections[address]:
                stop_transaction_monitor(address)
    
    return Response(generate(), mimetype='text/event-stream')

def start_transaction_monitor(address):
    """Start monitoring transactions for a specific address"""
    if address in transaction_monitors:
        return
    
    def monitor_transactions():
        last_tx_hash = None
        while address in transaction_monitors:
            try:
                # Get latest transactions
                etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
                if not etherscan_api_key:
                    logger.error("ETHERSCAN_API_KEY not found in environment variables")
                    time.sleep(10)  # Wait longer on error
                    continue
                    
                url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={etherscan_api_key}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "1" and data["result"]:
                        latest_tx = data["result"][0]
                        
                        # Check if this is a new transaction
                        if last_tx_hash != latest_tx["hash"]:
                            last_tx_hash = latest_tx["hash"]
                            
                            # Send to all connected clients
                            if address in active_connections:
                                tx_data = {
                                    'type': 'new_transaction',
                                    'transaction': {
                                        'hash': latest_tx["hash"],
                                        'from': latest_tx["from"],
                                        'to': latest_tx["to"],
                                        'value': float(latest_tx["value"]) / 1e18,
                                        'timestamp': latest_tx["timeStamp"],
                                        'gas': latest_tx["gas"],
                                        'gasPrice': latest_tx["gasPrice"]
                                    }
                                }
                                
                                for connection in active_connections[address]:
                                    try:
                                        connection.send(f"data: {json.dumps(tx_data)}\n\n")
                                    except:
                                        # Remove dead connections
                                        active_connections[address].remove(connection)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error monitoring transactions for {address}: {e}")
                time.sleep(10)  # Wait longer on error
    
    # Start monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_transactions, daemon=True)
    transaction_monitors[address] = monitor_thread
    monitor_thread.start()

def stop_transaction_monitor(address):
    """Stop monitoring transactions for a specific address"""
    if address in transaction_monitors:
        del transaction_monitors[address]

@app.route('/api/coins')
def get_available_coins():
    """Get list of available coins for the frontend"""
    return jsonify({
        'success': True,
        'coins': [
            {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'ETH'},
            {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'BTC'},
            {'id': 'solana', 'name': 'Solana', 'symbol': 'SOL'},
            {'id': 'tether', 'name': 'Tether', 'symbol': 'USDT'},
            {'id': 'usd-coin', 'name': 'USD Coin', 'symbol': 'USDC'},
            {'id': 'dai', 'name': 'Dai', 'symbol': 'DAI'}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 