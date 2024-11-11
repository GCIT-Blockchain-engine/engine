# main.py

import threading
import requests
import time
from werkzeug.serving import make_server
from flask import Flask
from routes import setup_routes
from blockchain.blockchain import Blockchain
from database.couchdb_handler import CouchDBHandler


def create_app(blockchain, port):
    app = Flask(__name__)
    # Exclude current node from its peers list to prevent self-synchronization
    blockchain.peers = [peer for peer in blockchain.peers if peer != f'http://127.0.0.1:{port}']
    setup_routes(app, blockchain, port)
    return app


def run_app(blockchain, port):
    app = create_app(blockchain, port)
    server = make_server('0.0.0.0', port, app)
    server.serve_forever()


def sync_with_peers(blockchain, port, peers):
    while True:
        time.sleep(10)  # Sync every 10 seconds
        for peer in peers:
            try:
                # Fetch data from the peer
                response_chain = requests.get(f'{peer}/request_chain', timeout=5)
                response_wallets = requests.get(f'{peer}/wallets', timeout=5)
                response_pending_transactions = requests.get(f'{peer}/pending_transactions', timeout=5)
                
                if (response_chain.status_code == 200 and 
                    response_wallets.status_code == 200 and 
                    response_pending_transactions.status_code == 200):
                    
                    chain = response_chain.json().get('chain')
                    wallets = response_wallets.json().get('wallets')
                    pending_transactions = response_pending_transactions.json().get('pending_transactions')
                    
                    if chain is not None and wallets is not None and pending_transactions is not None:
                        sync_data = {
                            'chain': chain,
                            'wallets': wallets,
                            'pending_transactions': pending_transactions
                        }
                        # Send synchronization data to self
                        sync_response = requests.post(f'http://127.0.0.1:{port}/sync', json=sync_data, timeout=5)
                        if sync_response.status_code == 200:
                            message = sync_response.json().get('message')
                            if message in ["Blockchain updated", "Blockchain state updated"]:
                                print(f"Synchronized blockchain with peer {peer}: {message}")
                            elif message == "No update needed":
                                print(f"No synchronization needed with peer {peer}")
                            else:
                                print(f"Received unexpected message from peer {peer}: {message}")
                        else:
                            print(f"Failed to synchronize with peer {peer}: {sync_response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error syncing with peer {peer}: {e}")


def main():
    # Fixed Genesis Wallet Key Pair (Replace with your fixed keys)
    fixed_genesis_private_key = "JyXpXRvosvED7QaijlzENRK0F0cbViheekZ3U+kBQfo="  # Replace with your actual fixed private key
    fixed_genesis_public_key = "A/yH130TSm3zCX7tEffvTmJDYSeq4uYo79WkkY4El23x"    # Replace with your actual fixed public key

    configs = [
        (5000, 'blockchain_node1', ['http://127.0.0.1:5001', 'http://127.0.0.1:5002']),
        (5001, 'blockchain_node2', ['http://127.0.0.1:5000', 'http://127.0.0.1:5002']),
        (5002, 'blockchain_node3', ['http://127.0.0.1:5000', 'http://127.0.0.1:5001'])
    ]
    threads = []
    for port, db_name, peers in configs:
        db_handler = CouchDBHandler(db_name)
        blockchain = Blockchain(db_handler, fixed_genesis_private_key, fixed_genesis_public_key)
        #blockchain.wallets = {blockchain.genesis_public_key: 1000000}
        blockchain.peers = peers  # Assign peers
        # Start Flask app thread
        app_thread = threading.Thread(target=run_app, args=(blockchain, port), daemon=True)
        app_thread.start()
        threads.append(app_thread)
        # Start synchronization thread
        sync_thread = threading.Thread(target=sync_with_peers, args=(blockchain, port, peers), daemon=True)
        sync_thread.start()
        threads.append(sync_thread)
    # Keep the main thread alive to allow daemon threads to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down blockchain nodes.")


if __name__ == '__main__':
    main()
