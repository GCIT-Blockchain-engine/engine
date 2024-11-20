# cryptolib/crypto.py

import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
import hashlib
import uuid  # Ensure uuid is imported


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
            # Generate UUID
            uuid_str = str(uuid.uuid4())
            # Append UUID to message
            message_with_uuid = message + uuid_str
            # Add padding back for decoding
            padding = '=' * (-len(private_key) % 4)
            signing_key_bytes = base64.urlsafe_b64decode(private_key.encode('utf-8') + padding.encode('utf-8'))
            signing_key = SigningKey.from_string(signing_key_bytes, curve=SECP256k1)
            # Sign the message_with_uuid
            signature = signing_key.sign(message_with_uuid.encode('utf-8'))
            # Encode the signature
            signature_encoded = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
            # Concatenate UUID to the signature
            signature_with_uuid = f"{signature_encoded}({uuid_str})"
            return signature_with_uuid
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {e}")

    @staticmethod
    def verify_signature(public_key, message, signature_with_uuid):
        try:
            print(f"Verifying signature: public_key={public_key}, message={message}, signature_with_uuid={signature_with_uuid}")
            # Extract UUID from the signature
            if '(' in signature_with_uuid and signature_with_uuid.endswith(')'):
                signature_encoded, uuid_str = signature_with_uuid.rsplit('(', 1)
                uuid_str = uuid_str[:-1]  # Remove the closing parenthesis
            else:
                raise ValueError("Invalid signature format. UUID not found.")

            # Reconstruct the message with UUID
            message_with_uuid = message + uuid_str

            # Add padding back for decoding
            padding_pk = '=' * (-len(public_key) % 4)
            verifying_key_bytes = base64.urlsafe_b64decode(public_key.encode('utf-8') + padding_pk.encode('utf-8'))
            verifying_key = VerifyingKey.from_string(verifying_key_bytes, curve=SECP256k1)

            # Decode the signature
            padding_sig = '=' * (-len(signature_encoded) % 4)
            signature_bytes = base64.urlsafe_b64decode(signature_encoded.encode('utf-8') + padding_sig.encode('utf-8'))

            # Verify the signature over the message_with_uuid
            is_valid = verifying_key.verify(signature_bytes, message_with_uuid.encode('utf-8'))
            print(f"Signature valid: {is_valid}")
            return is_valid
        except (BadSignatureError, Exception) as e:
            print(f"Signature verification error: {e}")
            return False

    @staticmethod
    def hash(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
