# blockchain/block.py

import time
from cryptolib.crypto import Crypto
from blockchain.merkle_tree import MerkleTree


class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0, merkle_root=None):
        self.index = index
        self.transactions = self._prepare_transactions(transactions)
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = merkle_root or self.calculate_merkle_root()

    def _prepare_transactions(self, transactions):
        if isinstance(transactions, list):
            return [tx if isinstance(tx, dict) else tx.to_dict() for tx in transactions]
        return []

    def calculate_merkle_root(self):
        merkle_tree = MerkleTree(self.transactions)
        return merkle_tree.root

    def compute_hash(self):
        data = (
            str(self.index)
            + str(self.merkle_root)
            + str(self.timestamp)
            + str(self.previous_hash)
            + str(self.nonce)
        )
        return Crypto.hash(data)

    def mine(self, difficulty=4):
        target = '0' * difficulty
        while not self.compute_hash().startswith(target):
            self.nonce += 1

    def to_dict(self):
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root
        }

    @classmethod
    def from_dict(cls, block_data):
        return cls(
            index=block_data['index'],
            transactions=block_data['transactions'],
            previous_hash=block_data['previous_hash'],
            timestamp=block_data['timestamp'],
            nonce=block_data['nonce'],
            merkle_root=block_data.get('merkle_root')
        )
