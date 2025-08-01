#!/usr/bin/env python3
"""
Test script to verify environment variable loading
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_variables():
    """Test that environment variables are loaded correctly"""
    etherscan_key = os.getenv('ETHERSCAN_API_KEY')
    
    print("Environment Variable Test:")
    print(f"ETHERSCAN_API_KEY: {'✓ Set' if etherscan_key else '✗ Not set'}")
    
    if etherscan_key:
        print(f"Key length: {len(etherscan_key)} characters")
        print(f"Key starts with: {etherscan_key[:8]}...")
    else:
        print("Please set ETHERSCAN_API_KEY in your .env file")

if __name__ == "__main__":
    test_env_variables() 