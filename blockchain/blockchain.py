# blockchain/blockchain.py

import time
import requests
from blockchain.block import Block
from blockchain.transaction import Transaction
from cryptolib.crypto import Crypto
from database.couchdb_handler import CouchDBHandler


class Blockchain:
    def __init__(self, db_handler, genesis_private_key=None, genesis_public_key=None):
        self.couchdb = db_handler
        self.chain = []
        self.mempool = {}  # Dictionary to store transactions by their signatures
        self.wallets = {}
        self.peers = []  # List of peer URLs
        self.auto_mine_threshold = 2
        
        if genesis_private_key and genesis_public_key:
            self.genesis_private_key = genesis_private_key
            self.genesis_public_key = genesis_public_key
        else:
            self.genesis_private_key, self.genesis_public_key = Crypto.generate_keypair()
        
        self.ico_funds = {"GENESIS_WALLET": 1000000}  # Initialize ICO funds
        self.load_state()
        
        if not self.chain:
            self.chain = [self.create_genesis_block()]
            self.wallets = {self.genesis_public_key: 1000000}
            self.save_state()
            print("Initialized new blockchain with genesis block")

    def create_genesis_block(self):
        # Transactions: "ICO" sends 1,000,000 to "GENESIS_WALLET"
        ico_transactions = [{
            "sender": "ICO",
            "recipient": self.genesis_public_key,
            "amount": 1000000,
            "signature": "genesis"
        }]
        fixed_timestamp = 1638316800.0  # Fixed timestamp (e.g., December 1, 2021)
        genesis_block = Block(0, ico_transactions, "0", timestamp=fixed_timestamp)
        genesis_block.mine(difficulty=4)
        return genesis_block

    def save_state(self):
        blockchain_state = {
            "chain": [block.to_dict() for block in self.chain],
            "mempool": list(self.mempool.values()),  # Save mempool as a list
            "wallets": self.wallets,
            "ico_funds": self.ico_funds,
            "genesis_public_key": self.genesis_public_key
        }
        self.couchdb.save_blockchain_state(blockchain_state)

    def load_state(self):
        state = self.couchdb.load_blockchain_state()
        if state:
            self.chain = [Block.from_dict(block_data) for block_data in state.get("chain", [])]
            self.mempool = {tx['signature']: tx for tx in state.get("mempool", [])}
            self.wallets = state.get('wallets', {state.get('genesis_public_key', "GENESIS_WALLET"): 1000000})
            self.ico_funds = state.get('ico_funds', {"GENESIS_WALLET": 1000000})
            self.genesis_public_key = state.get('genesis_public_key', "GENESIS_WALLET")
            print("Blockchain state loaded from CouchDB")
        else:
            print("No existing blockchain state found in CouchDB.")

    def create_wallet_transaction(self, recipient_public_key, amount):
        if self.wallets.get(self.genesis_public_key, 0) >= amount:
            message = f"{self.genesis_public_key}{recipient_public_key}{amount}"
            signature = Crypto.sign_transaction(self.genesis_private_key, message)
            transaction = Transaction(
                sender=self.genesis_public_key,
                recipient=recipient_public_key,
                amount=amount,
                signature=signature
            )
            self.add_transaction(transaction.to_dict())
            print(f"Created wallet transaction from GENESIS_WALLET to {recipient_public_key} for {amount} coins")
        else:
            raise ValueError("ICO funds depleted")

    def get_balance(self, wallet_address):
        return self.wallets.get(wallet_address, 0)

    def add_transaction(self, transaction):
        if transaction['signature'] in self.mempool or any(tx['signature'] == transaction['signature'] for block in self.chain for tx in block.transactions):
            print("Duplicate transaction detected; not adding to mempool.")
            return
        self.mempool[transaction['signature']] = transaction
        self.save_state()
        print(f"Transaction added to mempool: {transaction}")
        if len(self.mempool) >= self.auto_mine_threshold:
            self.mine_and_save()


    def mine_and_save(self):
        """Mine a new block and save the blockchain state."""
        new_block = self.mine()
        if new_block:
            self.couchdb.save_block(new_block)
            print("New block mined and saved to CouchDB.")

    def validate_and_process_transaction(self, sender, recipient, amount, private_key):
        message = f"{sender}{recipient}{amount}"
        signature = Crypto.sign_transaction(private_key, message)
        if not Crypto.verify_signature(sender, message, signature):
            raise ValueError("Invalid signature")
        if self.get_balance(sender) < amount:
            raise ValueError("Insufficient funds")
        transaction = Transaction(sender, recipient, amount, signature)
        self.add_transaction(transaction.to_dict())
        return transaction

    def update_balance(self, sender, recipient, amount):
        if self.wallets.get(sender, 0) >= amount:
            self.wallets[sender] -= amount
            self.wallets[recipient] = self.wallets.get(recipient, 0) + amount
            print(f"Transferred {amount} from {sender} to {recipient}")
            self.save_state()
        else:
            raise ValueError("Insufficient funds")

    def mine(self):
        if not self.mempool:
            print("No transactions to mine.")
            return None
        pending_transactions = list(self.mempool.values())
        new_block = Block(len(self.chain), pending_transactions, self.chain[-1].compute_hash())
        new_block.mine(difficulty=4)
        self.chain.append(new_block)
        # Process transactions in the block
        for tx_data in pending_transactions:
            sender = tx_data['sender']
            recipient = tx_data['recipient']
            amount = tx_data['amount']
            self._process_transaction_in_block(sender, recipient, amount)
        self.mempool = {}  # Clear the mempool after mining
        self.save_state()
        # Broadcast the new block to peers
        for peer in self.peers:
            try:
                response = requests.post(f'{peer}/add_block', json=new_block.to_dict(), timeout=5)
                if response.status_code != 200:
                    print(f"Failed to broadcast block to {peer}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error broadcasting new block to {peer}: {e}")
        return new_block

    def _process_transaction_in_block(self, sender, recipient, amount):
        if sender not in self.wallets:
            self.wallets[sender] = 0
        if recipient not in self.wallets:
            self.wallets[recipient] = 0
        self.wallets[sender] -= amount
        self.wallets[recipient] += amount

    def sync_chain(self, incoming_chain):
        new_chain = [Block.from_dict(block) for block in incoming_chain]
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            self.chain = new_chain
            self.recalculate_wallets()
            self.save_state()
            print("Blockchain synchronized with a longer chain from peer.")

    def recalculate_wallets(self):
        """Recalculate wallet balances based on the current chain."""
        self.wallets = {self.genesis_public_key: 1000000}
        for block in self.chain[1:]:  # Skip genesis block
            for tx in block.transactions:
                sender = tx['sender']
                recipient = tx['recipient']
                amount = tx['amount']
                if sender != "ICO":
                    if sender not in self.wallets:
                        self.wallets[sender] = 0
                    self.wallets[sender] -= amount
                if recipient not in self.wallets:
                    self.wallets[recipient] = 0
                self.wallets[recipient] += amount

    def is_valid_new_block(self, new_block, previous_block):
        if previous_block.index + 1 != new_block.index:
            print("Invalid index")
            return False
        elif previous_block.compute_hash() != new_block.previous_hash:
            print("Invalid previous hash")
            return False
        elif not new_block.compute_hash().startswith('0' * 4):
            print("Block does not meet difficulty requirements")
            return False
        return True

    def is_valid_chain(self, chain):
        if not chain:
            print("Empty chain")
            return False
        # Ensure all chains start with the same genesis block
        genesis_block = chain[0]
        if self.chain and len(self.chain) > 0:
            current_genesis = self.chain[0]
            if genesis_block.compute_hash() != current_genesis.compute_hash():
                print("Genesis blocks do not match")
                return False
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]
            if current_block.previous_hash != previous_block.compute_hash():
                print(f"Invalid previous hash at block {i}")
                return False
            # Verify proof of work
            if not current_block.compute_hash().startswith('0' * 4):
                print(f"Block {i} does not meet difficulty requirements")
                return False
        return True

    def replace_chain(self, new_chain):
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            self.chain = new_chain
            self.recalculate_wallets()
            self.save_state()
            print("Chain replaced with the longer valid chain.")
            return True
        return False

    def add_block(self, block):
        if self.is_valid_new_block(block, self.chain[-1]):
            self.chain.append(block)
            # Process transactions in the block
            for tx_data in block.transactions:
                sender = tx_data['sender']
                recipient = tx_data['recipient']
                amount = tx_data['amount']
                if sender != "ICO":
                    self._process_transaction_in_block(sender, recipient, amount)
            # Remove transactions from mempool
            self.mempool = {tx['signature']: tx for tx in self.mempool.values() if tx['signature'] not in [tx['signature'] for tx in block.transactions]}
            self.save_state()
            print(f"Block {block.index} added to the chain.")
            return True
        else:
            print("Invalid block received.")
            return False

    def update_wallets(self, incoming_wallets):
        for wallet, balance in incoming_wallets.items():
            self.wallets[wallet] = balance
        self.save_state()
