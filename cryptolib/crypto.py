# cryptolib/crypto.py

import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
import hashlib


class Crypto:
    @staticmethod
    def generate_keypair():
        # Generate ECDSA key pair using the SECP256k1 curve
        signing_key = SigningKey.generate(curve=SECP256k1)
        verifying_key = signing_key.get_verifying_key()
        
        # Serialize keys in compressed format
        private_key = base64.b64encode(signing_key.to_string()).decode('utf-8')  # 32 bytes, 44 base64 chars
        public_key = base64.b64encode(verifying_key.to_string("compressed")).decode('utf-8')  # 33 bytes, 44 base64 chars
        return private_key, public_key

    @staticmethod
    def sign_transaction(private_key, message):
        try:
            signing_key_bytes = base64.b64decode(private_key.encode('utf-8'))
            signing_key = SigningKey.from_string(signing_key_bytes, curve=SECP256k1)
            signature = signing_key.sign(message.encode('utf-8'))
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {e}")

    @staticmethod
    def verify_signature(public_key, message, signature):
        try:
            verifying_key_bytes = base64.b64decode(public_key.encode('utf-8'))
            verifying_key = VerifyingKey.from_string(verifying_key_bytes, curve=SECP256k1)
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            return verifying_key.verify(signature_bytes, message.encode('utf-8'))
        except BadSignatureError:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False

    @staticmethod
    def hash(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
