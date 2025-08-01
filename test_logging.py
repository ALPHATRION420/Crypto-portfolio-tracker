#!/usr/bin/env python3
"""
Test script to verify logging functionality
"""

import logging
import sys
from crypt_1 import get_eth_balance, get_eth_price
from price_history import get_price_history

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_logging():
    """Test the logging functionality"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting logging test")
    
    # Test ETH price
    logger.info("Testing ETH price retrieval")
    eth_price = get_eth_price()
    logger.info(f"ETH price result: {eth_price}")
    
    # Test wallet balance (using a test address)
    test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"  # Example address
    logger.info(f"Testing wallet balance for: {test_address}")
    eth_balance = get_eth_balance(test_address)
    logger.info(f"ETH balance result: {eth_balance}")
    
    # Test price history
    logger.info("Testing price history retrieval")
    history = get_price_history(['ETH'], days=1)
    logger.info(f"Price history result: {history}")
    
    logger.info("Logging test completed")

if __name__ == "__main__":
    test_logging() 