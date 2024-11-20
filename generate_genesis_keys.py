# generate_genesis_keys.py

from cryptolib.crypto import Crypto

def main():
    fixed_genesis_private_key, fixed_genesis_public_key = Crypto.generate_keypair()
    print("Fixed Genesis Private Key:", fixed_genesis_private_key)
    print("Fixed Genesis Public Key:", fixed_genesis_public_key)

if __name__ == "__main__":
    main()
