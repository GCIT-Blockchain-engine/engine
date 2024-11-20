# blockchain/merkle_tree.py

from cryptolib.crypto import Crypto


class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        transaction_hashes = [Crypto.hash(str(tx)) for tx in transactions]
        self.root = self.build_merkle_tree(transaction_hashes)

    def build_merkle_tree(self, hashes):
        if not hashes:
            return None
        if len(hashes) == 1:
            return hashes[0]
        new_level = []
        for i in range(0, len(hashes), 2):
            left = hashes[i]
            right = hashes[i + 1] if i + 1 < len(hashes) else left
            combined_hash = Crypto.hash(left + right)
            new_level.append(combined_hash)
        return self.build_merkle_tree(new_level) 
