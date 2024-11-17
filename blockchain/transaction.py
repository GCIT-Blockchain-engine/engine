# blockchain/transaction.py

import uuid

class Transaction:
    def __init__(self, sender, recipient, amount, signature, transaction_id=None, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.transaction_id = transaction_id or self.generate_transaction_id()
        self.timestamp = timestamp  # Do not set timestamp at creation

    def generate_transaction_id(self):
        # Generate a unique transaction ID using UUID4
        return str(uuid.uuid4())

    def to_dict(self):
        # Start with mandatory fields
        transaction_dict = {
            "transaction_id": self.transaction_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
        }
        # Conditionally add 'timestamp' if it's not None
        if self.timestamp is not None:
            transaction_dict["timestamp"] = self.timestamp
        return transaction_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount'],
            signature=data['signature'],
            transaction_id=data.get('transaction_id'),
            timestamp=data.get('timestamp')  # Can be None
        )
