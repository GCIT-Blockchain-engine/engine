# routes.py

from flask import request, jsonify
import requests
from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from blockchain.wallet import Wallet


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
            # Broadcast the transaction to peers
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
        return jsonify({"pending_transactions": list(blockchain.mempool.values())}), 200

    @app.route('/ico_funds', methods=['GET'])
    def get_ico_funds():
        return jsonify({"ICO_funds_remaining": blockchain.ico_funds.get("GENESIS_WALLET", 0)}), 200

    @app.route('/sync', methods=['POST'])
    def sync():
        data = request.json
        incoming_chain = data.get('chain')
        incoming_wallets = data.get('wallets')
        incoming_pending_transactions = data.get('pending_transactions')
        
        # Validate incoming data
        if incoming_chain is None or incoming_wallets is None or incoming_pending_transactions is None:
            return jsonify({"message": "Invalid incoming data"}), 400

        # Convert incoming chain data to Block objects
        incoming_chain_objs = [Block.from_dict(block_data) for block_data in incoming_chain]

        # Validate the incoming chain
        if not blockchain.is_valid_chain(incoming_chain_objs):
            return jsonify({"message": "Invalid incoming chain"}), 400

        # Check if the incoming chain is longer
        if len(incoming_chain_objs) > len(blockchain.chain):
            blockchain.chain = incoming_chain_objs
            blockchain.recalculate_wallets()
            # Merge incoming pending transactions with existing mempool
            for tx in incoming_pending_transactions:
                blockchain.mempool[tx['signature']] = tx
            blockchain.save_state()
            print("Blockchain synchronized with incoming data.")
            return jsonify({"message": "Blockchain updated"}), 200
        else:
            # Optionally, you can also merge mempools even if chains are same length
            for tx in incoming_pending_transactions:
                blockchain.mempool[tx['signature']] = tx
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
                    transactions.append(tx)
        return jsonify({"transactions": transactions}), 200
