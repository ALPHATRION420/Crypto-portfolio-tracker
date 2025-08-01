from web3 import Web3
import json

INFURA_URL = "https://mainnet.infura.io/v3/255fbca1623843f7bd621af3b85f3584"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}, {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}, {"constant":true,"inputs":[{"name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')

def get_eth_balance(address):
    try:
        balance = web3.eth.get_balance(address)
        return round(web3.fromWei(balance, 'ether'), 5)
    except:
        return 0

def get_wallet_tokens(address):
    return {
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eb48',
        'DAI':  '0x6B175474E89094C44Da98b954EedeAC495271d0F',
        'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
        'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA'
    }

def get_token_balances(address, tokens):
    balances = []
    for symbol, token_address in tokens.items():
        try:
            token = web3.eth.contract(address=token_address, abi=ERC20_ABI)
            decimals = token.functions.decimals().call()
            balance = token.functions.balanceOf(address).call() / (10 ** decimals)
            balances.append({
                'symbol': symbol,
                'balance': round(balance, 4)
            })
        except Exception as e:
            print(f"Error: {symbol} - {e}")
    return balances
