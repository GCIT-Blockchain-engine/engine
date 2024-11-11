
import uuid
import time


class Transaction:
    def __init__(self, sender, recipient, amount, signature, transaction_id=None, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.transaction_id = transaction_id or self.generate_transaction_id()
        self.timestamp = timestamp or self.generate_timestamp()
    
    def generate_transaction_id(self):
        return str(uuid.uuid4())
    
    def generate_timestamp(self):
        return time.time()
    
    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
            "timestamp": self.timestamp
        }
    
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
