# generate_genesis_keys.py

from cryptolib.crypto import Crypto

def main():
    private_key, public_key = Crypto.generate_keypair()
    print(f"Fixed Genesis Private Key (Base64): {private_key}")
    print(f"Fixed Genesis Public Key (Base64): {public_key}")

if __name__ == "__main__":
    main()
