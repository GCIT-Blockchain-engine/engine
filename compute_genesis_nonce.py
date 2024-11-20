# compute_genesis_hash.py

import uuid
from blockchain.block import Block
from blockchain.transaction import Transaction
from cryptolib.crypto import Crypto

def calculate_merkle_root(transactions):
    from blockchain.merkle_tree import MerkleTree
    merkle_tree = MerkleTree(transactions)
    return merkle_tree.root

def compute_genesis_hash():
    # Fixed parameters for the genesis block
    index = 0
    transactions = [{
        "sender": "ICO",
        "recipient": "GENESIS_WALLET",
        "amount": 1000000,
        "signature": "genesis",
        "transaction_id": str(uuid.uuid4()),
        "timestamp": 1638316800.0  # Fixed timestamp (e.g., December 1, 2021)
    }]
    previous_hash = "0"
    timestamp = 1638316800.0  # Fixed timestamp
    nonce = 0  # Starting nonce; will be incremented to meet difficulty
    merkle_root = calculate_merkle_root(transactions)
    
    genesis_block = Block(
        index=index,
        transactions=transactions,
        previous_hash=previous_hash,
        timestamp=timestamp,
        nonce=nonce,
        merkle_root=merkle_root
    )
    
    difficulty = 4  # Number of leading zeros required in hash
    target = '0' * difficulty
    
    print("Mining genesis block to find a valid nonce...")
    
    while not genesis_block.compute_hash().startswith(target):
        genesis_block.nonce += 1
        if genesis_block.nonce % 100000 == 0:
            print(f"Current nonce: {genesis_block.nonce}")
    
    genesis_hash = genesis_block.compute_hash()
    print("Genesis Block Mined Successfully!")
    print(f"Nonce: {genesis_block.nonce}")
    print(f"Hash: {genesis_hash}")
    print(f"Merkle Root: {merkle_root}")

if __name__ == "__main__":
    compute_genesis_hash()
