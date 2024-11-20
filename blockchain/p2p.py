import threading
import asyncio
import json
from blockchain.block import Block
import websockets
from blockchain.transaction import Transaction

class P2PNetwork:
    def __init__(self, host='0.0.0.0', port=5001, blockchain=None):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []
        self.loop = None
        self.loop_ready = threading.Event()

    def start(self):
        """Start the WebSocket server in a separate event loop."""
        self.loop = asyncio.new_event_loop()
        self.loop_ready = threading.Event()  # Add this line

        def run_server():
            asyncio.set_event_loop(self.loop)
            start_server = websockets.serve(self.handle_connection, self.host, self.port)
            self.loop.run_until_complete(start_server)
            self.loop_ready.set()  # Signal that the loop is ready
            self.loop.run_forever()

        threading.Thread(target=run_server, daemon=True).start()
        print(f"P2P Network server started on {self.host}:{self.port}")





    async def handle_connection(self, websocket, path):
        """Handle incoming connections from peers."""
        self.peers.append(websocket)
        try:
            async for message in websocket:
                await self.handle_message(message, websocket)
        except websockets.ConnectionClosed:
            self.peers.remove(websocket)


    async def handle_message(self, message, websocket):
        """Handle incoming messages."""

        try:
            data = json.loads(message)
            msg_type = data.get('type')
            print(f"Received message of type {msg_type}")
            if msg_type == 'TRANSACTION':
                await self.handle_incoming_transaction(data['transaction'], websocket)
            elif msg_type == 'BLOCK':
                await self.handle_incoming_block(data['block'])
            elif msg_type == 'TRANSACTION':
                await self.handle_incoming_transaction(data['transaction'])
            elif msg_type == 'WALLET':
                await self.handle_incoming_wallet(data['public_key'])
            elif msg_type == 'SYNC':
                await self.handle_sync(data['chain'])
            elif msg_type == 'PENDING_TRANSACTIONS':
                await self.handle_incoming_pending_transactions(data['transactions'])
            elif msg_type == 'REQUEST_CHAIN':
                await self.handle_chain_request(websocket)
            elif msg_type == 'RESPONSE_CHAIN':
                await self.handle_chain_response(data['chain'])
            elif msg_type == 'REQUEST_PENDING_TRANSACTIONS':
                await self.handle_pending_transactions_request(websocket)
            elif msg_type == 'RESPONSE_PENDING_TRANSACTIONS':
                await self.handle_incoming_pending_transactions(data['transactions'])
        except Exception as e:
            print(f"Error handling message: {e}")

        

        

    async def handle_incoming_block(self, block_data):
        block = Block.from_dict(block_data)
        if self.blockchain.add_block(block):
            print("Block added to the chain.")
            # Broadcast the block to peers
            await self.broadcast_block(block.to_dict())
        else:
            print("Invalid block received. Requesting full chain sync.")
            await self.request_full_chain()



    async def handle_incoming_transaction(self, transaction_data, websocket):
        print(f"Received transaction: {transaction_data}")
        if transaction_data not in self.blockchain.pending_transactions:
            self.blockchain.pending_transactions.append(transaction_data)
            self.blockchain.save_state()
            print("Transaction added to the pending pool.")
            # Broadcast the transaction to peers, excluding the sender
            await self.broadcast_transaction(transaction_data, exclude_peers=[websocket])
        else:
            print("Transaction already in pending pool.")

    async def broadcast_transaction(self, transaction_data):
        """Broadcast transaction to all connected peers."""
        message = json.dumps({"type": "TRANSACTION", "transaction": transaction_data})
        await self._broadcast_message(message)

    async def handle_incoming_wallet(self, public_key):
        if public_key not in self.blockchain.wallets:
            self.blockchain.wallets[public_key] = 10
            self.blockchain.save_state()
            print(f"Received new wallet: {public_key}")
            await self.broadcast_wallet(public_key)

    async def broadcast_block(self, block_data):
        """Broadcast block to all connected peers."""
        message = json.dumps({"type": "BLOCK", "block": block_data})
        await self._broadcast_message(message)

    async def _broadcast_message(self, message, exclude_peers=None):
        """Internal method to broadcast messages to all peers."""
        if exclude_peers is None:
            exclude_peers = []
        print(f"Peers: {self.peers}")
        for peer in self.peers:
            if peer in exclude_peers:
                continue
            try:
                await peer.send(message)
                print(f"Message sent to peer {peer.remote_address}")
            except Exception as e:
                print(f"Failed to send message to peer: {e}")


    async def broadcast_wallet(self, public_key):
        """Broadcast wallet creation to all connected peers."""
        message = json.dumps({"type": "WALLET", "public_key": public_key})
        await self._broadcast_message(message)

    async def _broadcast_message(self, message, exclude_peers=None):
        """Internal method to broadcast messages to all peers."""
        if exclude_peers is None:
            exclude_peers = []
        for peer in self.peers:
            if peer in exclude_peers:
                continue
            try:
                await peer.send(message)
                print(f"Message sent to peer {peer.remote_address}")
            except Exception as e:
                print(f"Failed to send message to peer: {e}")


    async def request_full_chain(self):
        """Request the full chain from all peers."""
        message = json.dumps({"type": "REQUEST_CHAIN"})
        await self._broadcast_message(message)

    async def request_pending_transactions(self):
        """Request pending transactions from all peers."""
        message = json.dumps({"type": "REQUEST_PENDING_TRANSACTIONS"})
        await self._broadcast_message(message)

    async def handle_sync(self, incoming_chain_data):
        """Handle incoming chain sync request."""
        incoming_chain = [self.blockchain.create_block_from_dict(block) for block in incoming_chain_data]
        if len(incoming_chain) > len(self.blockchain.chain):
            self.blockchain.chain = incoming_chain
            self.blockchain.save_state()
            print("Blockchain synchronized with peer.")

    async def handle_incoming_pending_transactions(self, transactions):
        """Handle incoming pending transactions from peers."""
        for transaction in transactions:
            if transaction not in self.blockchain.pending_transactions:
                self.blockchain.pending_transactions.append(transaction)
        self.blockchain.save_state()
        print("Pending transactions synchronized with peer.")

    def connect_to_peer(self, host, port):
        """Connect to a new peer via WebSocket."""
        self.loop_ready.wait()  # Wait until the event loop is ready

        async def connect():
            try:
                uri = f"ws://{host}:{port}"
                websocket = await websockets.connect(uri)
                self.peers.append(websocket)
                print(f"Connected to peer at {host}:{port}")
                await self.request_full_chain()
                await self.request_pending_transactions()
            except Exception as e:
                print(f"Failed to connect to peer at {host}:{port}: {e}")

        # Schedule the coroutine in the P2P network's event loop
        asyncio.run_coroutine_threadsafe(connect(), self.loop)




    def get_connected_peers(self):
     return [f"{peer.remote_address[0]}:{peer.remote_address[1]}" for peer in self.peers if peer.open]



    async def handle_chain_request(self, websocket):
        chain_data = [block.to_dict() for block in self.blockchain.chain]
        message = json.dumps({'type': 'RESPONSE_CHAIN', 'chain': chain_data})
        await websocket.send(message)

    async def handle_chain_response(self, chain_data):
        incoming_chain = [self.blockchain.create_block_from_dict(block_data) for block_data in chain_data]
        if len(incoming_chain) > len(self.blockchain.chain) and self.blockchain.is_valid_chain(incoming_chain):
            self.blockchain.replace_chain(incoming_chain)
            print("Blockchain synchronized with peer.")

    async def handle_pending_transactions_request(self, websocket):
        """Send pending transactions to the requesting peer."""
        message = json.dumps({'type': 'RESPONSE_PENDING_TRANSACTIONS', 'transactions': self.blockchain.pending_transactions})
        await websocket.send(message)