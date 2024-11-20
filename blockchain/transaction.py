import uuid

class Transaction:
    def __init__(self, sender, recipient, amount, signature, transaction_id=None, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.transaction_id = transaction_id  # Do not generate here
        self.timestamp = timestamp  # Do not set timestamp at creation

    def to_dict(self):
        # Start with mandatory fields
        transaction_dict = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
        }
        # Conditionally add 'transaction_id' and 'timestamp' if they are not None
        if self.transaction_id is not None:
            transaction_dict["transaction_id"] = self.transaction_id
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
            transaction_id=data.get('transaction_id'),  # Do not generate
            timestamp=data.get('timestamp')  # Can be None
        )
