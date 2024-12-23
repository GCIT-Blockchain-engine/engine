import time
import uuid
from flask import request, jsonify
import requests
from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet
from cryptolib.crypto import Crypto


def setup_routes(app, blockchain, port):
    @app.route('/wallet/create', methods=['POST'])
    def create_wallet():
        wallet = Wallet(blockchain)
        return jsonify(wallet.export_keys()), 201

    @app.route('/transaction/create', methods=['POST'])
    def create_transaction():
        data = request.json
        sender = data.get('sender')
        recipient = data.get('recipient')
        amount = data.get('amount')
        private_key = data.get('private_key')
        if not sender or not recipient or not amount or not private_key:
            return jsonify({"error": "Missing fields in request"}), 400
        try:
            transaction = blockchain.validate_and_process_transaction(sender, recipient, amount, private_key)
            for peer in blockchain.peers:
                try:
                    response = requests.post(f'{peer}/transaction/add', json=transaction.to_dict(), timeout=5)
                    if response.status_code != 200:
                        print(f"Failed to broadcast transaction to {peer}: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Error broadcasting transaction to {peer}: {e}")
            return jsonify(transaction.to_dict()), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/transaction/add', methods=['POST'])
    def add_transaction():
        data = request.json
        required_fields = ['sender', 'recipient', 'amount', 'signature']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing fields in transaction data"}), 400
        transaction = Transaction.from_dict(data)
        blockchain.add_transaction(transaction.to_dict())
        return jsonify({"message": "Transaction added"}), 200

    @app.route('/mine', methods=['GET'])
    def mine_block():
        new_block = blockchain.mine()
        if new_block:
            return jsonify(new_block.to_dict()), 200
        return jsonify({"message": "No transactions to mine"}), 200

    @app.route('/chain', methods=['GET'])
    def get_chain():
        chain_data = [block.to_dict() for block in blockchain.chain]
        return jsonify(chain_data), 200

    @app.route('/balance/<wallet_address>', methods=['GET'])
    def get_balance(wallet_address):
        balance = blockchain.get_balance(wallet_address)
        return jsonify({"balance": balance}), 200

    @app.route('/pending_transactions', methods=['GET'])
    def get_pending_transactions():
        pending_transactions = [Transaction.from_dict(tx).to_dict() for tx in list(blockchain.mempool.values())]
        return jsonify({"pending_transactions": pending_transactions}), 200

    @app.route('/ico_funds', methods=['GET'])
    def get_ico_funds():
        return jsonify({"ICO_funds_remaining": blockchain.ico_funds.get("GENESIS_WALLET", 0)}), 200

    @app.route('/sync', methods=['POST'])
    def sync():
        data = request.json
        incoming_chain = data.get('chain')
        incoming_wallets = data.get('wallets')
        incoming_pending_transactions = data.get('pending_transactions')

        if incoming_chain is None or incoming_wallets is None or incoming_pending_transactions is None:
            return jsonify({"message": "Invalid incoming data"}), 400

        incoming_chain_objs = [Block.from_dict(block_data) for block_data in incoming_chain]

        if not blockchain.is_valid_chain(incoming_chain_objs):
            return jsonify({"message": "Invalid incoming chain"}), 400

        if len(incoming_chain_objs) > len(blockchain.chain):
            blockchain.chain = incoming_chain_objs
            blockchain.recalculate_wallets()
            for tx in incoming_pending_transactions:
                blockchain.mempool[tx['transaction_id']] = tx
            blockchain.save_state()
            print("Blockchain synchronized with incoming data.")
            return jsonify({"message": "Blockchain updated"}), 200
        else:
            for tx in incoming_pending_transactions:
                blockchain.mempool[tx['transaction_id']] = tx
            blockchain.save_state()
            print("Mempool merged with incoming data.")
            return jsonify({"message": "Mempool merged"}), 200

    @app.route('/request_chain', methods=['GET'])
    def request_chain():
        chain_data = [block.to_dict() for block in blockchain.chain]
        return jsonify({"chain": chain_data}), 200

    @app.route('/wallets', methods=['GET'])
    def get_wallets():
        return jsonify({"wallets": blockchain.wallets}), 200

    @app.route('/add_block', methods=['POST'])
    def add_block():
        data = request.json
        block = Block.from_dict(data)
        if blockchain.add_block(block):
            return jsonify({"message": "Block added"}), 200
        return jsonify({"message": "Invalid block"}), 400

    @app.route('/transactions/<wallet_address>', methods=['GET'])
    def get_wallet_transactions(wallet_address):
        transactions = []
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx['sender'] == wallet_address or tx['recipient'] == wallet_address:
                    transaction_obj = Transaction.from_dict(tx)
                    transactions.append(transaction_obj.to_dict())
        return jsonify({"transactions": transactions}), 200

    @app.route('/transaction/sign', methods=['POST'])
    def sign_transaction():
        data = request.json
        sender = data.get('sender')
        recipient = data.get('recipient')
        amount = data.get('amount')
        private_key = data.get('private_key')

        if not sender or not recipient or not amount or not private_key:
            return jsonify({"error": "Missing fields in request"}), 400

        try:
            message = f"{sender}{recipient}{amount}"
            signature = Crypto.sign_transaction(private_key, message)

            signed_transaction = {
                "sender": sender,
                "recipient": recipient,
                "amount": amount,
                "signature": signature
            }

            return jsonify(signed_transaction), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/transaction/verify', methods=['POST'])
    def verify_transaction():
        data = request.json
        sender = data.get('sender')
        recipient = data.get('recipient')
        amount = data.get('amount')
        signature = data.get('signature')

        if not sender or not recipient or not amount or not signature:
            return jsonify({"error": "Missing fields in request"}), 400

        message = f"{sender}{recipient}{amount}"
        print(f"Verifying transaction with message: {message}")
        is_valid = Crypto.verify_signature(sender, message, signature)
        verification_result = {
            "is_valid": is_valid
        }
        return jsonify(verification_result), 200

    @app.route('/transaction/submit_offchain', methods=['POST'])
    def submit_offchain_transaction():
        data = request.json
        required_fields = ['sender', 'recipient', 'amount', 'signature']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing fields in transaction data"}), 400

        try:
            transaction = Transaction.from_dict(data)
            message = f"{transaction.sender}{transaction.recipient}{transaction.amount}"
            if not Crypto.verify_signature(transaction.sender, message, transaction.signature):
                return jsonify({"error": "Invalid signature"}), 400

            if blockchain.get_balance(transaction.sender) < transaction.amount:
                return jsonify({"error": "Insufficient funds"}), 400

            blockchain.add_transaction(transaction.to_dict())

            for peer in blockchain.peers:
                try:
                    response = requests.post(f'{peer}/transaction/add', json=transaction.to_dict(), timeout=5)
                    if response.status_code != 200:
                        print(f"Failed to broadcast transaction to {peer}: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Error broadcasting transaction to {peer}: {e}")

            return jsonify({"message": "Off-chain transaction submitted successfully"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route('/transaction/<transaction_id>', methods=['GET'])
    def get_transaction_by_id(transaction_id):
        for block in blockchain.chain:
            for tx in block.transactions:
                if tx.get('transaction_id') == transaction_id:
                    transaction_obj = Transaction.from_dict(tx)
                    return jsonify(transaction_obj.to_dict()), 200
        tx = blockchain.mempool.get(transaction_id)
        if tx:
            transaction_obj = Transaction.from_dict(tx)
            return jsonify(transaction_obj.to_dict()), 200
        return jsonify({"error": "Transaction not found"}), 404
