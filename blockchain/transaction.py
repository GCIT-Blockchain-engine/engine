class Transaction:
    def __init__(self, sender, recipient, amount, signature, timestamp=None, transaction_id=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature
        self.timestamp = timestamp
        self.transaction_id = transaction_id  

    def to_dict(self):
        transaction_dict = {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature,
        }
        if self.timestamp is not None:
            transaction_dict["timestamp"] = self.timestamp
        if self.transaction_id is not None:
            transaction_dict["transaction_id"] = self.transaction_id 
        return transaction_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=data['amount'],
            signature=data['signature'],
            timestamp=data.get('timestamp'),
            transaction_id=data.get('transaction_id')  
        )
