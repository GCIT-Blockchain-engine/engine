# blockchain/transaction.py

import base64
import json
import time

class Transaction:
    def __init__(self, sender, recipient, amount, signature, transaction_id=None, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.timestamp = timestamp  # Will be added when the transaction is mined
        self.transaction_id = transaction_id or self.generate_transaction_id()
        
    def generate_transaction_id(self):
        # Create a dictionary with the transaction data
        tx_data = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature
        }
        # Convert to JSON string with compact separators
        tx_json = json.dumps(tx_data, separators=(',', ':'))
        # Base64 encode the JSON string without padding
        tx_id = base64.urlsafe_b64encode(tx_json.encode()).decode().rstrip('=')
        return tx_id
        
    def to_dict(self):
        tx_dict = {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature
        }
        if self.timestamp:
            tx_dict["timestamp"] = self.timestamp
        return tx_dict
        
    @classmethod
    def from_transaction_id(cls, transaction_id):
        try:
            # Add padding back for decoding
            padding = '=' * (-len(transaction_id) % 4)
            tx_json_str = base64.urlsafe_b64decode(transaction_id + padding).decode()
            tx_data = json.loads(tx_json_str)
            return cls(
                sender=tx_data['sender'],
                recipient=tx_data['recipient'],
                amount=tx_data['amount'],
                signature=tx_data['signature'],
                transaction_id=transaction_id,
                timestamp=None  # Will be added when mined
            )
        except Exception as e:
            raise ValueError(f"Invalid transaction_id: {e}")
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount'],
            signature=data['signature'],
            transaction_id=data.get('transaction_id'),
            timestamp=data.get('timestamp')
        )