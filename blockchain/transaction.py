# blockchain/transaction.py

class Transaction:
    def __init__(self, sender, recipient, amount, signature, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.timestamp = timestamp  # Assigned during mining

    def to_dict(self):
        # Start with mandatory fields
        transaction_dict = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
        }
        # Conditionally add 'timestamp' if it is not None
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
            timestamp=data.get('timestamp')  # Can be None
        )
