import threading
from web3 import Web3
import json
import logging
import time
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Import centralized configuration
from .config import (
    BLOCKCHAIN_RPC,
    BLOCKCHAIN_PRIVATE_KEY as PRIVATE_KEY,
    CONTRACT_ADDRESS,
    GAS_LIMIT,
    GAS_PRICE_GWEI,
    BLOCKCHAIN_TX_TIMEOUT as TRANSACTION_TIMEOUT,
    BLOCKCHAIN_CONN_TIMEOUT as CONNECTION_TIMEOUT
)

# Set up logging
logger = logging.getLogger(__name__)

# Import the BlockchainError exception
from .exceptions import BlockchainError

# Initialize Web3 connection
w3 = None

def get_web3_connection():
    """
    Get or initialize the Web3 connection with timeout.
    
    Returns:
        Web3: Web3 instance connected to the blockchain
        
    Raises:
        BlockchainError: If connection fails or times out
    """
    global w3
    if w3 is None or not w3.is_connected():
        try:
            logger.info(f"Connecting to blockchain at {BLOCKCHAIN_RPC}")
            
            # Create a provider with timeout
            provider = Web3.HTTPProvider(
                BLOCKCHAIN_RPC,
                request_kwargs={'timeout': CONNECTION_TIMEOUT}
            )
            
            # Initialize Web3 with the provider
            w3 = Web3(provider)
            
            # Check connection with timeout
            def check_connection():
                if not w3.is_connected():
                    raise BlockchainError("Failed to connect to the blockchain")
                return True
                
            # Execute with timeout
            with ThreadPoolExecutor() as executor:
                future = executor.submit(check_connection)
                try:
                    future.result(timeout=CONNECTION_TIMEOUT)
                except FutureTimeoutError:
                    logger.error(f"Connection to blockchain timed out after {CONNECTION_TIMEOUT} seconds")
                    raise BlockchainError(f"Connection to blockchain timed out after {CONNECTION_TIMEOUT} seconds")
                
            # Set default account
            w3.eth.default_account = w3.eth.account.from_key(PRIVATE_KEY).address
            
            logger.info(f"Successfully connected to blockchain. Network ID: {w3.eth.chain_id}")
        except Exception as e:
            logger.error(f"Error connecting to blockchain: {str(e)}")
            raise BlockchainError(f"Failed to connect to blockchain: {str(e)}")
    
    return w3

# 直接在代码中定义合约ABI
CONTRACT_ABI = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "AuthorizedUserAdded",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "AuthorizedUserRemoved",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "by",
				"type": "address"
			}
		],
		"name": "ContractPaused",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "by",
				"type": "address"
			}
		],
		"name": "ContractUnpaused",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			}
		],
		"name": "ImageDeleted",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "uploader",
				"type": "address"
			}
		],
		"name": "ImageFeaturesStored",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"name": "ImageFeaturesUpdated",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "bool",
				"name": "isVerified",
				"type": "bool"
			}
		],
		"name": "ImageVerificationStatusChanged",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "addAuthorizedUser",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			}
		],
		"name": "deleteImageFeatures",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getImageCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			}
		],
		"name": "getImageFeatures",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "uploader",
				"type": "address"
			},
			{
				"internalType": "bool",
				"name": "isVerified",
				"type": "bool"
			},
			{
				"internalType": "string",
				"name": "deepfakeLabel",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "deepfakeConfidence",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "start",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "limit",
				"type": "uint256"
			}
		],
		"name": "getImageHashesPaginated",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			}
		],
		"name": "imageExists",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "isAuthorized",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "isPaused",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "pauseContract",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "removeAuthorizedUser",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "deepfakeLabel",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "deepfakeConfidence",
				"type": "uint256"
			}
		],
		"name": "storeImageFeatures",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "unpauseContract",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "deepfakeLabel",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "deepfakeConfidence",
				"type": "uint256"
			}
		],
		"name": "updateImageFeatures",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "sha256Hash",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "verified",
				"type": "bool"
			}
		],
		"name": "verifyImage",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

def get_contract_instance():
    """
    Get the smart contract instance.
    
    Returns:
        Contract: Smart contract instance
    """
    try:
        web3 = get_web3_connection()
        contract_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
        
        # 直接使用定义好的ABI
        contract = web3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
        return contract
    except Exception as e:
        logger.error(f"Error getting contract instance: {str(e)}")
        raise BlockchainError(f"Failed to get contract instance: {str(e)}")

# Diagnostic functions to help troubleshoot blockchain issues
def check_blockchain_connection():
    """
    Check if the blockchain connection is working properly.
    
    Returns:
        dict: Connection status and details
    """
    try:
        web3 = get_web3_connection()
        
        if not web3.is_connected():
            return {
                "status": "error",
                "message": "Cannot connect to blockchain RPC endpoint",
                "rpc_url": BLOCKCHAIN_RPC
            }
        
        # Get network information
        chain_id = web3.eth.chain_id
        gas_price = web3.eth.gas_price
        block_number = web3.eth.block_number
        
        return {
            "status": "success",
            "chain_id": chain_id,
            "gas_price_gwei": web3.from_wei(gas_price, 'gwei'),
            "block_number": block_number,
            "rpc_url": BLOCKCHAIN_RPC
        }
    except Exception as e:
        logger.error(f"Error checking blockchain connection: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "rpc_url": BLOCKCHAIN_RPC
        }

def check_wallet_balance():
    """
    Check the balance of the wallet used for transactions.
    
    Returns:
        dict: Wallet balance information
    """
    try:
        web3 = get_web3_connection()
        
        if not web3.is_connected():
            return {
                "status": "error",
                "message": "Cannot connect to blockchain"
            }
        
        # Get wallet address from private key
        account = web3.eth.account.from_key(PRIVATE_KEY)
        address = account.address
        
        # Get balance
        balance_wei = web3.eth.get_balance(address)
        balance_eth = web3.from_wei(balance_wei, 'ether')
        
        # Check if balance is sufficient for transactions
        gas_price = web3.eth.gas_price
        estimated_tx_cost_wei = gas_price * GAS_LIMIT
        estimated_tx_cost_eth = web3.from_wei(estimated_tx_cost_wei, 'ether')
        
        is_sufficient = balance_wei > estimated_tx_cost_wei
        
        return {
            "status": "success",
            "address": address,
            "balance_wei": balance_wei,
            "balance_eth": float(balance_eth),
            "estimated_tx_cost_eth": float(estimated_tx_cost_eth),
            "is_sufficient": is_sufficient
        }
    except Exception as e:
        logger.error(f"Error checking wallet balance: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def get_recommended_gas_price():
    """
    Get recommended gas price for transactions.
    
    Returns:
        dict: Recommended gas prices
    """
    try:
        web3 = get_web3_connection()
        
        if not web3.is_connected():
            return {
                "status": "error",
                "message": "Cannot connect to blockchain"
            }
        
        # Get current gas price
        current_gas_price = web3.eth.gas_price
        
        # Calculate recommended gas prices
        slow_price = current_gas_price
        average_price = int(current_gas_price * 1.2)  # 20% higher
        fast_price = int(current_gas_price * 1.5)     # 50% higher
        
        return {
            "status": "success",
            "current_gas_price_gwei": web3.from_wei(current_gas_price, 'gwei'),
            "recommended": {
                "slow_gwei": web3.from_wei(slow_price, 'gwei'),
                "average_gwei": web3.from_wei(average_price, 'gwei'),
                "fast_gwei": web3.from_wei(fast_price, 'gwei')
            }
        }
    except Exception as e:
        logger.error(f"Error getting recommended gas price: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def check_image_exists_on_blockchain(sha256_hash):
    """
    Check if an image with the given SHA256 hash already exists on the blockchain.
    
    Args:
        sha256_hash: SHA256 hash of the image
        
    Returns:
        bool: True if image exists, False otherwise
        
    Raises:
        BlockchainError: If blockchain interaction fails (excluding "image not found" cases)
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Try to get image features - if it returns without error, the image exists
        try:
            timestamp, uploader, is_verified, deepfake_label, deepfake_confidence = contract.functions.getImageFeatures(sha256_hash).call()
            # If we get here, the image exists
            logger.info(f"Image with hash {sha256_hash} already exists on blockchain")
            return True
        except Exception as e:
            error_str = str(e).lower()
            # Check if the error message indicates the image doesn't exist
            # Treat "Image not found" or "does not exist" as expected results, not errors
            if "image not found" in error_str or "does not exist" in error_str:
                logger.info(f"Image with hash {sha256_hash} does not exist on blockchain")
                return False
            # For other errors, re-raise
            logger.error(f"Unexpected error when checking image on blockchain: {str(e)}")
            raise
            
    except Exception as e:
        # Only raise BlockchainError for actual blockchain interaction failures
        # not for "image not found" cases which are expected results
        logger.error(f"Error checking if image exists on blockchain: {str(e)}")
        raise BlockchainError(f"Failed to check if image exists on blockchain: {str(e)}")

def store_image_on_blockchain(sha256_hash, deepfake_label="Unknown", deepfake_confidence=0, max_retries=3, retry_delay=2):
    """
    Store image features on the blockchain with enhanced error handling and retry mechanism.
    
    Args:
        sha256_hash: SHA256 hash of the image
        deepfake_label: Deepfake detection label ("Real" or "Fake")
        deepfake_confidence: Deepfake detection confidence (0-1)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 2)
        
    Returns:
        Transaction hash if successful, or special value "IMAGE_EXISTS" if image already exists
        
    Raises:
        BlockchainError: If blockchain interaction fails or times out
    """
    # First, check if the image already exists on the blockchain
    try:
        if check_image_exists_on_blockchain(sha256_hash):
            logger.info(f"Image with hash {sha256_hash} already exists on blockchain. Skipping storage.")
            return "IMAGE_EXISTS"
    except Exception as e:
        logger.warning(f"Error checking if image exists on blockchain: {str(e)}. Will attempt to store anyway.")
    
    start_time = time.time()
    retry_count = 0
    last_error = None
    
    # Print diagnostic information
    logger.info("=== BLOCKCHAIN UPLOAD DIAGNOSTICS ===")
    
    # Check blockchain connection first, before any other operations
    conn_status = check_blockchain_connection()
    if conn_status["status"] == "error":
        logger.error(f"Blockchain connection check failed: {conn_status['message']}")
        raise BlockchainError(f"Blockchain connection failed: {conn_status['message']}")
    else:
        logger.info(f"Blockchain connection OK: Chain ID {conn_status['chain_id']}, Gas Price {conn_status['gas_price_gwei']} Gwei")
    
    # Check wallet balance
    balance_info = check_wallet_balance()
    if balance_info["status"] == "error":
        logger.error(f"Wallet balance check failed: {balance_info['message']}")
    elif not balance_info["is_sufficient"]:
        logger.warning(f"Wallet balance may be insufficient: {balance_info['balance_eth']} ETH, estimated tx cost: {balance_info['estimated_tx_cost_eth']} ETH")
    else:
        logger.info(f"Wallet balance OK: {balance_info['balance_eth']} ETH")
    
    # Validate and sanitize input parameters
    try:
        # Validate deepfake_label
        if deepfake_label not in ["Real", "Fake", "Unknown"]:
            logger.warning(f"Unexpected deepfake_label: {deepfake_label}. Expected 'Real' or 'Fake'.")
        
        # Validate deepfake_confidence
        if not isinstance(deepfake_confidence, (int, float)) or deepfake_confidence < 0 or deepfake_confidence > 1:
            logger.warning(f"Unexpected deepfake_confidence: {deepfake_confidence}. Expected value between 0 and 1.")
            # Ensure it's within valid range
            deepfake_confidence = max(0, min(1, float(deepfake_confidence) if isinstance(deepfake_confidence, (int, float)) else 0))
    
        # Convert confidence to uint256 (multiply by 100 to preserve 2 decimal places)
        confidence_uint = int(deepfake_confidence * 100)
        
        logger.info(f"Parameters validated: sha256_hash={sha256_hash}, deepfake_label={deepfake_label}, deepfake_confidence={deepfake_confidence}")
    except Exception as e:
        logger.error(f"Error validating parameters: {str(e)}")
        raise BlockchainError(f"Parameter validation failed: {str(e)}")
    
    # Retry loop
    while retry_count <= max_retries:
        current_retry = retry_count
        retry_count += 1
        
        try:
            # Log retry attempt
            if current_retry > 0:
                logger.info(f"Retry attempt {current_retry}/{max_retries} for storing image {sha256_hash}")
            
            # Get Web3 connection
            logger.info("Step 1: Establishing blockchain connection...")
            web3 = get_web3_connection()
            
            # Get contract instance
            logger.info("Step 2: Getting contract instance...")
            contract = get_contract_instance()
            
            # Log the parameters being sent to the blockchain
            logger.info(f"Step 3: Preparing transaction with parameters: sha256_hash={sha256_hash}, deepfake_label={deepfake_label}, deepfake_confidence={confidence_uint}")
            
            # Get recommended gas price
            gas_info = get_recommended_gas_price()
            if gas_info["status"] == "success":
                recommended_gas_price = web3.to_wei(gas_info["recommended"]["average_gwei"], 'gwei')
                logger.info(f"Using recommended gas price: {gas_info['recommended']['average_gwei']} Gwei")
            else:
                recommended_gas_price = web3.eth.gas_price
                logger.info(f"Using current gas price: {web3.from_wei(recommended_gas_price, 'gwei')} Gwei")
            
            # Get nonce with retry mechanism
            nonce = None
            nonce_retries = 3
            for i in range(nonce_retries):
                try:
                    nonce = web3.eth.get_transaction_count(web3.eth.default_account)
                    break
                except Exception as nonce_err:
                    if i == nonce_retries - 1:
                        raise
                    logger.warning(f"Error getting nonce (attempt {i+1}/{nonce_retries}): {str(nonce_err)}")
                    time.sleep(1)
            
            logger.info(f"Using nonce: {nonce}")
            
            # Build transaction
            logger.info("Step 4: Building transaction...")
            tx = contract.functions.storeImageFeatures(
                sha256_hash,
                deepfake_label,
                confidence_uint
            ).build_transaction({
                'from': web3.eth.default_account,
                'nonce': nonce,
                'gas': GAS_LIMIT,
                'gasPrice': recommended_gas_price
            })
            
            # Sign transaction
            logger.info("Step 5: Signing transaction...")
            signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
            
            # Send transaction with timeout
            logger.info("Step 6: Sending transaction...")
            def send_transaction():
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                logger.info(f"Transaction sent: {tx_hash.hex()}")
                return tx_hash
                
            with ThreadPoolExecutor() as executor:
                future = executor.submit(send_transaction)
                try:
                    tx_hash = future.result(timeout=TRANSACTION_TIMEOUT)
                    logger.info(f"Transaction hash: {tx_hash.hex()}")
                except FutureTimeoutError:
                    elapsed = time.time() - start_time
                    logger.error(f"Transaction submission timed out after {elapsed:.2f} seconds")
                    raise BlockchainError(f"Transaction submission timed out after {elapsed:.2f} seconds")
            
            # Wait for transaction receipt with timeout
            logger.info("Step 7: Waiting for transaction confirmation...")
            def wait_for_receipt():
                return web3.eth.wait_for_transaction_receipt(tx_hash)
                
            with ThreadPoolExecutor() as executor:
                future = executor.submit(wait_for_receipt)
                try:
                    remaining_timeout = max(1, TRANSACTION_TIMEOUT - (time.time() - start_time))
                    logger.info(f"Waiting up to {remaining_timeout:.2f} seconds for confirmation...")
                    tx_receipt = future.result(timeout=remaining_timeout)
                except FutureTimeoutError:
                    elapsed = time.time() - start_time
                    logger.warning(f"Transaction confirmation timed out after {elapsed:.2f} seconds")
                    logger.warning(f"Transaction may still be pending. Transaction hash: {tx_hash.hex()}")
                    # Return the transaction hash even if confirmation times out
                    return tx_hash.hex()
            
            if tx_receipt.status == 1:
                elapsed = time.time() - start_time
                logger.info(f"Success! Image features stored on blockchain: {sha256_hash} (took {elapsed:.2f} seconds)")
                return tx_receipt.transactionHash.hex()
            else:
                logger.error(f"Transaction failed with status: {tx_receipt.status}")
                raise BlockchainError(f"Transaction failed with status: {tx_receipt.status}")
                
        except Exception as e:
            elapsed = time.time() - start_time
            last_error = e
            
            if current_retry >= max_retries:
                logger.error(f"Final attempt failed after {elapsed:.2f} seconds: {str(e)}")
                break
                
            # Calculate exponential backoff delay
            delay = retry_delay * (2 ** current_retry)
            logger.warning(f"Attempt {current_retry} failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)
    
    # If we get here, all retries failed
    if last_error:
        # Check if the error is due to the image already existing
        if "Image with this hash already exists" in str(last_error):
            logger.info(f"Image with hash {sha256_hash} already exists on blockchain. This is not an error.")
            return "IMAGE_EXISTS"
        else:
            logger.error(f"All {max_retries} retry attempts failed. Last error: {str(last_error)}")
            raise BlockchainError(f"Failed to store image on blockchain after {max_retries} attempts: {str(last_error)}")
    else:
        logger.error(f"All {max_retries} retry attempts failed with unknown errors")
        raise BlockchainError(f"Failed to store image on blockchain after {max_retries} attempts")

def get_image_from_blockchain(sha256_hash):
    """
    Get image features from the blockchain.
    
    Args:
        sha256_hash: SHA256 hash of the image
        
    Returns:
        dict: Dictionary with image features
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Call contract function
        timestamp, uploader, is_verified, deepfake_label, deepfake_confidence = contract.functions.getImageFeatures(sha256_hash).call()
        
        # Convert timestamp to datetime
        timestamp_dt = datetime.fromtimestamp(timestamp)
        
        # Convert confidence from uint256 (with 2 decimal places) to float
        confidence_float = deepfake_confidence / 100.0
        
        return {
            'sha256_hash': sha256_hash,
            'timestamp': timestamp_dt,
            'uploader': uploader,
            'is_verified': is_verified,
            'deepfake_label': deepfake_label,
            'deepfake_confidence': confidence_float
        }
    except Exception as e:
        logger.error(f"Error getting image from blockchain: {str(e)}")
        raise BlockchainError(f"Failed to get image from blockchain: {str(e)}")

def image_exists_on_blockchain(sha256_hash):
    """
    Check if an image exists on the blockchain.
    
    Args:
        sha256_hash: SHA256 hash of the image
        
    Returns:
        bool: True if image exists, False otherwise
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Call contract function
        result = contract.functions.imageExists(sha256_hash).call()
        
        return result
    except Exception as e:
        logger.error(f"Error checking if image exists on blockchain: {str(e)}")
        raise BlockchainError(f"Failed to check if image exists on blockchain: {str(e)}")

def update_image_on_blockchain(sha256_hash, deepfake_label, deepfake_confidence):
    """
    Update image features on the blockchain.
    
    Args:
        sha256_hash: SHA256 hash of the image
        deepfake_label: Deepfake detection label ("Real" or "Fake")
        deepfake_confidence: Deepfake detection confidence (0-1)
        
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Convert confidence to uint256 (multiply by 100 to preserve 2 decimal places)
        confidence_uint = int(deepfake_confidence * 100)
        
        # Log the parameters being sent to the blockchain
        logger.info(f"Updating image on blockchain with parameters: sha256_hash={sha256_hash}, deepfake_label={deepfake_label}, deepfake_confidence={deepfake_confidence}")
        
        # Build transaction
        tx = contract.functions.updateImageFeatures(
            sha256_hash,
            deepfake_label,
            confidence_uint
        ).build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"Image features updated on blockchain: {sha256_hash}")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Update transaction failed: {tx_receipt}")
            raise BlockchainError("Update transaction failed")
            
    except Exception as e:
        logger.error(f"Error updating image on blockchain: {str(e)}")
        raise BlockchainError(f"Failed to update image on blockchain: {str(e)}")

def delete_image_from_blockchain(sha256_hash):
    """
    Delete image features from the blockchain.
    
    Args:
        sha256_hash: SHA256 hash of the image
        
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Build transaction
        tx = contract.functions.deleteImageFeatures(sha256_hash).build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"Image features deleted from blockchain: {sha256_hash}")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Delete transaction failed: {tx_receipt}")
            raise BlockchainError("Delete transaction failed")
            
    except Exception as e:
        logger.error(f"Error deleting image from blockchain: {str(e)}")
        raise BlockchainError(f"Failed to delete image from blockchain: {str(e)}")

def get_image_count():
    """
    Get the total number of images stored on the blockchain.
    
    Returns:
        int: Number of images
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Call contract function
        count = contract.functions.getImageCount().call()
        
        return count
    except Exception as e:
        logger.error(f"Error getting image count from blockchain: {str(e)}")
        raise BlockchainError(f"Failed to get image count from blockchain: {str(e)}")

def get_image_hashes_paginated(start, limit):
    """
    Get a paginated list of image hashes from the blockchain.
    
    Args:
        start: Starting index
        limit: Maximum number of hashes to return
        
    Returns:
        list: List of SHA256 hashes
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Call contract function
        hashes = contract.functions.getImageHashesPaginated(start, limit).call()
        
        return hashes
    except Exception as e:
        logger.error(f"Error getting paginated image hashes from blockchain: {str(e)}")
        raise BlockchainError(f"Failed to get paginated image hashes from blockchain: {str(e)}")

def is_authorized(user_address):
    """
    Check if a user is authorized to interact with the contract.
    
    Args:
        user_address: Ethereum address of the user
        
    Returns:
        bool: True if authorized, False otherwise
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Convert address to checksum address
        checksum_address = Web3.to_checksum_address(user_address)
        
        # Call contract function
        is_auth = contract.functions.isAuthorized(checksum_address).call()
        
        return is_auth
    except Exception as e:
        logger.error(f"Error checking authorization status: {str(e)}")
        raise BlockchainError(f"Failed to check authorization status: {str(e)}")

def is_contract_paused():
    """
    Check if the contract is paused.
    
    Returns:
        bool: True if paused, False otherwise
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Call contract function
        is_paused = contract.functions.isPaused().call()
        
        return is_paused
    except Exception as e:
        logger.error(f"Error checking if contract is paused: {str(e)}")
        raise BlockchainError(f"Failed to check if contract is paused: {str(e)}")

def pause_contract():
    """
    Pause the contract.
    
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Build transaction
        tx = contract.functions.pauseContract().build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info("Contract paused successfully")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Pause contract transaction failed: {tx_receipt}")
            raise BlockchainError("Pause contract transaction failed")
            
    except Exception as e:
        logger.error(f"Error pausing contract: {str(e)}")
        raise BlockchainError(f"Failed to pause contract: {str(e)}")

def unpause_contract():
    """
    Unpause the contract.
    
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Build transaction
        tx = contract.functions.unpauseContract().build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info("Contract unpaused successfully")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Unpause contract transaction failed: {tx_receipt}")
            raise BlockchainError("Unpause contract transaction failed")
            
    except Exception as e:
        logger.error(f"Error unpausing contract: {str(e)}")
        raise BlockchainError(f"Failed to unpause contract: {str(e)}")

def add_authorized_user(user_address):
    """
    Add a user to the authorized users list.
    
    Args:
        user_address: Ethereum address of the user to authorize
        
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Convert address to checksum address
        checksum_address = Web3.to_checksum_address(user_address)
        
        # Build transaction
        tx = contract.functions.addAuthorizedUser(checksum_address).build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"User {user_address} added to authorized users")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Add authorized user transaction failed: {tx_receipt}")
            raise BlockchainError("Add authorized user transaction failed")
            
    except Exception as e:
        logger.error(f"Error adding authorized user: {str(e)}")
        raise BlockchainError(f"Failed to add authorized user: {str(e)}")

def remove_authorized_user(user_address):
    """
    Remove a user from the authorized users list.
    
    Args:
        user_address: Ethereum address of the user to remove
        
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Convert address to checksum address
        checksum_address = Web3.to_checksum_address(user_address)
        
        # Build transaction
        tx = contract.functions.removeAuthorizedUser(checksum_address).build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"User {user_address} removed from authorized users")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Remove authorized user transaction failed: {tx_receipt}")
            raise BlockchainError("Remove authorized user transaction failed")
            
    except Exception as e:
        logger.error(f"Error removing authorized user: {str(e)}")
        raise BlockchainError(f"Failed to remove authorized user: {str(e)}")

def transfer_ownership(new_owner_address):
    """
    Transfer ownership of the contract to a new address.
    
    Args:
        new_owner_address: Ethereum address of the new owner
        
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Convert address to checksum address
        checksum_address = Web3.to_checksum_address(new_owner_address)
        
        # Build transaction
        tx = contract.functions.transferOwnership(checksum_address).build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"Ownership transferred to {new_owner_address}")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Transfer ownership transaction failed: {tx_receipt}")
            raise BlockchainError("Transfer ownership transaction failed")
            
    except Exception as e:
        logger.error(f"Error transferring ownership: {str(e)}")
        raise BlockchainError(f"Failed to transfer ownership: {str(e)}")

def verify_image(sha256_hash, verified):
    """
    Set the verification status of an image.
    
    Args:
        sha256_hash: SHA256 hash of the image
        verified: Boolean indicating if the image is verified
        
    Returns:
        Transaction hash if successful
        
    Raises:
        BlockchainError: If blockchain interaction fails
    """
    try:
        # Get contract instance
        contract = get_contract_instance()
        
        # Log the verification attempt
        logger.info(f"Setting verification status for image: sha256_hash={sha256_hash}, verified={verified}")
        
        # Build transaction
        tx = contract.functions.verifyImage(sha256_hash, verified).build_transaction({
            'from': w3.eth.default_account,
            'nonce': w3.eth.get_transaction_count(w3.eth.default_account),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"Image verification status set: {sha256_hash}, verified={verified}")
            return tx_receipt.transactionHash.hex()
        else:
            logger.error(f"Verify image transaction failed: {tx_receipt}")
            raise BlockchainError("Verify image transaction failed")
            
    except Exception as e:
        logger.error(f"Error setting image verification status: {str(e)}")
        raise BlockchainError(f"Failed to set image verification status: {str(e)}")