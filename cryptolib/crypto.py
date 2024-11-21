import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
import hashlib
import uuid


class Crypto:
    @staticmethod
    def generate_keypair():
        signing_key = SigningKey.generate(curve=SECP256k1)
        verifying_key = signing_key.get_verifying_key()

        private_key = base64.urlsafe_b64encode(signing_key.to_string()).decode('utf-8').rstrip('=')
        public_key = base64.urlsafe_b64encode(verifying_key.to_string("compressed")).decode('utf-8').rstrip('=')
        return private_key, public_key

    @staticmethod
    def sign_transaction(private_key, message):
        try:
            uuid_str = str(uuid.uuid4())
            message_with_uuid = message + uuid_str
            padding = '=' * (-len(private_key) % 4)
            signing_key_bytes = base64.urlsafe_b64decode(private_key.encode('utf-8') + padding.encode('utf-8'))
            signing_key = SigningKey.from_string(signing_key_bytes, curve=SECP256k1)
            signature = signing_key.sign(message_with_uuid.encode('utf-8'))
            signature_encoded = base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
            signature_with_uuid = f"{signature_encoded}({uuid_str})"
            return signature_with_uuid
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {e}")

    @staticmethod
    def verify_signature(public_key, message, signature_with_uuid):
        try:
            print(f"Verifying signature: public_key={public_key}, message={message}, signature_with_uuid={signature_with_uuid}")
            if '(' in signature_with_uuid and signature_with_uuid.endswith(')'):
                signature_encoded, uuid_str = signature_with_uuid.rsplit('(', 1)
                uuid_str = uuid_str[:-1]
            else:
                raise ValueError("Invalid signature format. UUID not found.")

            message_with_uuid = message + uuid_str

            padding_pk = '=' * (-len(public_key) % 4)
            verifying_key_bytes = base64.urlsafe_b64decode(public_key.encode('utf-8') + padding_pk.encode('utf-8'))
            verifying_key = VerifyingKey.from_string(verifying_key_bytes, curve=SECP256k1)

            padding_sig = '=' * (-len(signature_encoded) % 4)
            signature_bytes = base64.urlsafe_b64decode(signature_encoded.encode('utf-8') + padding_sig.encode('utf-8'))

            is_valid = verifying_key.verify(signature_bytes, message_with_uuid.encode('utf-8'))
            print(f"Signature valid: {is_valid}")
            return is_valid
        except (BadSignatureError, Exception) as e:
            print(f"Signature verification error: {e}")
            return False

    @staticmethod
    def hash(data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
