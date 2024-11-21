from cryptolib.crypto import Crypto
from blockchain.transaction import Transaction


class Wallet:
    def __init__(self, blockchain):
        self.private_key, self.public_key = Crypto.generate_keypair()
        try:
            blockchain.create_wallet_transaction(self.public_key, 10)
            print(f"Wallet created with public key: {self.public_key}")
        except Exception as e:
            print(f"Error creating wallet transaction: {e}")

    def export_keys(self):
        return {
            'private_key': self.private_key,
            'public_key': self.public_key
        }
