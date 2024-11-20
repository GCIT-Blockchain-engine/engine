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
        
        # Serialize keys in compressed format with URL-safe Base64 encoding
        private_key = base64.urlsafe_b64encode(signing_key.to_string()).decode('utf-8').rstrip('=')  # Remove padding
        public_key = base64.urlsafe_b64encode(verifying_key.to_string("compressed")).decode('utf-8').rstrip('=')  # Remove padding
        return private_key, public_key

    @staticmethod
    def sign_transaction(private_key, message):
        try:
            # Add padding back for decoding
            padding = '=' * (-len(private_key) % 4)
            signing_key_bytes = base64.urlsafe_b64decode(private_key.encode('utf-8') + padding.encode('utf-8'))
            signing_key = SigningKey.from_string(signing_key_bytes, curve=SECP256k1)
            signature = signing_key.sign(message.encode('utf-8'))
            signature_encoded = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')  # Remove padding
            return signature_encoded
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {e}")

    @staticmethod
    def verify_signature(public_key, message, signature):
        try:
            # Add padding back for decoding
            padding_pk = '=' * (-len(public_key) % 4)
            verifying_key_bytes = base64.urlsafe_b64decode(public_key.encode('utf-8') + padding_pk.encode('utf-8'))
            verifying_key = VerifyingKey.from_string(verifying_key_bytes, curve=SECP256k1)
            
            padding_sig = '=' * (-len(signature) % 4)
            signature_bytes = base64.urlsafe_b64decode(signature.encode('utf-8') + padding_sig.encode('utf-8'))
            return verifying_key.verify(signature_bytes, message.encode('utf-8'))
        except BadSignatureError:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False

    @staticmethod
    def hash(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
