"""
Centralized configuration module for environment variables.
This module provides a single source of truth for all configuration values
used across the application, ensuring consistency and easier management.
"""

import os
from pathlib import Path

# Base directory for absolute paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# Blockchain configuration
BLOCKCHAIN_RPC = os.environ.get("BLOCKCHAIN_RPC", "http://127.0.0.1:7545")
BLOCKCHAIN_PRIVATE_KEY = os.environ.get("BLOCKCHAIN_PRIVATE_KEY", "0x4d31993960007b5948176b95dba7c49c081fe59ebc49aa5c42472611877c5389")  # Replace in production
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS", "0x1B76D3aAF8D286179cCB2BD359bBb9B63B15f9AD")  # Replace in production
GAS_LIMIT = int(os.environ.get("GAS_LIMIT", "6000000"))  # Increased from 3000000 to 6000000
GAS_PRICE_GWEI = int(os.environ.get("GAS_PRICE_GWEI", "1"))
BLOCKCHAIN_TX_TIMEOUT = int(os.environ.get("BLOCKCHAIN_TX_TIMEOUT", "30"))  # 30 seconds default timeout
BLOCKCHAIN_CONN_TIMEOUT = int(os.environ.get("BLOCKCHAIN_CONN_TIMEOUT", "10"))  # 10 seconds default connection timeout



