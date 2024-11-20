## Overview

The blockchain system implements a peer-to-peer network using Flask as the web server. The blockchain is stored persistently in CouchDB, and transactions are cryptographically secure. Key features include:

- **Genesis Block Initialization**
    
- **Wallet Creation**
    
- **Transaction Handling (On-chain and Off-chain)**
    
- **Blockchain Mining**
    
- **Synchronization with Peers**
    
- **Verification of Transactions**
    

### Key Components:

1. **Block**: Represents a single block in the chain.
    
2. **Blockchain**: Manages the chain of blocks, mempool, and wallets.
    
3. **Merkle Tree**: Creates a hash-based summary of transactions.
    
4. **Transaction**: Defines and encodes transaction details.
    
5. **Crypto**: Handles key generation, signing, verification, and hashing.
    
6. **CouchDBHandler**: Manages persistent storage.
    
7. **Routes**: Defines RESTful endpoints for system interaction.
    
8. **Main Application**: Sets up nodes and synchronization between peers.
    

---

## Detailed Explanation

### **1. Block**

File: `blockchain/block.py`

**Purpose:** Represents a block in the blockchain. Contains transaction data, previous hash, nonce, and timestamp.

- **Key Functions:**
    
    - `compute_hash`: Computes the hash of the block.
        
    - `mine`: Implements Proof-of-Work by solving for a hash with a defined difficulty.
        
    - `calculate_merkle_root`: Computes the Merkle root for transactions.
        
    - `to_dict` and `from_dict`: Serialize and deserialize block data.
        

---

### **2. Blockchain**

File: `blockchain/blockchain.py`

**Purpose:** Manages the blockchain, wallets, transactions, and synchronization.

- **Key Features:**
    
    - **Genesis Block:**
        
        - Initializes the blockchain with a predefined Genesis Wallet and funds.
            
    - **Transaction Handling:**
        
        - Adds transactions to the mempool if valid.
            
        - Validates and processes transactions by checking signatures and balances.
            
    - **Mining:**
        
        - Mines blocks when the mempool reaches a threshold.
            
        - Adds transactions to the blockchain and processes their balances.
            
    - **Synchronization:**
        
        - Syncs with peers by comparing chains and merging mempools.
            
- **Important Methods:**
    
    - `create_wallet_transaction`: Transfers coins to a new wallet from Genesis Wallet.
        
    - `validate_and_process_transaction`: Ensures transaction validity.
        
    - `mine_and_save`: Mines new blocks and saves the blockchain state.
        
    - `recalculate_wallets`: Recomputes balances based on the chain.
        

---

### **3. Merkle Tree**

File: `blockchain/merkle_tree.py`

**Purpose:** Provides a hash-based summary of transactions for quick verification.

- **Key Features:**
    
    - Constructs a binary tree where each leaf node represents a transaction hash.
        
    - The root hash summarizes all transactions in the block.
        

---

### **4. Transaction**

File: `blockchain/transaction.py`

**Purpose:** Represents a single transaction.

- **Key Features:**
    
    - `generate_transaction_id`: Encodes all transaction details into a Base64 transaction ID.
        
    - `from_transaction_id`: Decodes a transaction ID to reconstruct the transaction.
        
    - `to_dict` and `from_dict`: Serialize and deserialize transaction data.
        

---

### **5. Crypto**

File: `cryptolib/crypto.py`

**Purpose:** Handles cryptographic operations like key generation, signing, and verification.

- **Key Functions:**
    
    - `generate_keypair`: Generates a public-private key pair using ECDSA.
        
    - `sign_transaction`: Signs messages using a private key.
        
    - `verify_signature`: Verifies the signature of a transaction.
        
    - `hash`: Generates a SHA-256 hash of the input data.
        

---

### **6. CouchDBHandler**

File: `database/couchdb_handler.py`

**Purpose:** Manages persistent storage of blockchain data in CouchDB.

- **Key Methods:**
    
    - `save_block`: Saves a block to CouchDB.
        
    - `save_blockchain_state`: Saves the entire blockchain state.
        
    - `load_blockchain_state`: Loads the saved blockchain state.
        
    - `delete_blockchain_state`: Deletes the saved blockchain state.
        

---

### **7. Routes**

File: `routes.py`

**Purpose:** Defines RESTful API endpoints to interact with the blockchain system.

#### Key Endpoints:

- **Wallet Endpoints:**
    
    - `/wallet/create` (POST): Creates a new wallet and initializes it with 10 coins.
        
- **Transaction Endpoints:**
    
    - `/transaction/create` (POST): Creates a new transaction.
        
    - `/transaction/add` (POST): Adds a transaction to the mempool.
        
    - `/transaction/sign` (POST): Signs a transaction.
        
    - `/transaction/verify` (POST): Verifies a transaction signature.
        
    - `/transaction/submit_offchain` (POST): Submits an off-chain transaction.
        
    - `/transaction/details` (POST): Retrieves transaction details by `transaction_id`.
        
- **Blockchain Endpoints:**
    
    - `/mine` (GET): Mines a block.
        
    - `/chain` (GET): Retrieves the blockchain.
        
    - `/sync` (POST): Synchronizes with peers.
        
    - `/wallets` (GET): Retrieves all wallet balances.
        
    - `/pending_transactions` (GET): Lists all pending transactions.
        
    - `/ico_funds` (GET): Retrieves the remaining ICO funds.
        

---

### **8. Main Application**

File: `main.py`

**Purpose:** Initializes the nodes, assigns peers, and starts Flask servers.

- **Key Features:**
    
    - Initializes blockchain nodes with a fixed Genesis Wallet.
        
    - Runs Flask applications for each node in separate threads.
        
    - Periodically synchronizes data between peers.
        

---

## How It Works

1. **Initialization:**
    
    - The system creates a Genesis Block with ICO funds allocated to the Genesis Wallet.
        
    - Each node initializes its blockchain state and connects to peers.
        
2. **Creating Wallets:**
    
    - Users generate wallets using the `/wallet/create` endpoint.
        
    - Wallets are assigned a public-private key pair, and 10 coins are transferred from the Genesis Wallet.
        
3. **Processing Transactions:**
    
    - Users submit transactions via `/transaction/create`.
        
    - Transactions are added to the mempool and broadcast to peers.
        
4. **Mining Blocks:**
    
    - When the mempool reaches the threshold, nodes mine a block.
        
    - Transactions in the block are processed, and balances are updated.
        
5. **Synchronization:**
    
    - Nodes periodically sync chains, wallets, and pending transactions with peers.
        

## Layers

### **Network Layer**

The network layer is responsible for the communication between nodes in the blockchain system. The following protocols and methods are used to enable secure, efficient, and reliable networking:

#### **1. HTTP/REST API Protocol**

- **Purpose**: The REST API over HTTP is the primary protocol used for node-to-node communication in this blockchain system.
    
- **Usage**: Each node exposes a set of endpoints (e.g., `/transaction/create`, `/mine`, `/sync`, etc.) which other nodes can call to interact with the blockchain, submit transactions, and synchronize the chain. This enables the nodes to exchange data about the current state of the blockchain.
    
- **Methods**: The standard HTTP methods (`GET`, `POST`) are used:
    
    - **GET** requests are used to retrieve blockchain state, transactions, and balances.
        
    - **POST** requests are used to create transactions, add blocks, and synchronize blockchain state across nodes.
        

#### **2. Peer-to-Peer (P2P) Communication**

- **Purpose**: Nodes in the blockchain communicate with each other using a P2P communication model. Each node maintains a list of peer nodes with which it can share data and receive updates.
    
- **Protocol**: Communication between nodes is done using HTTP over a decentralized network topology to ensure there is no central point of failure. Nodes broadcast newly mined blocks and transactions to their peers to achieve consensus.
    
- **Synchronization**: Peers regularly request the chain state from one another to ensure their ledgers remain in sync. Nodes implement periodic synchronization by making HTTP requests to peer endpoints, such as `/request_chain`.
    

### **Blockchain Layer (Ledger Management)**

The blockchain layer is responsible for maintaining a distributed, immutable ledger. This layer incorporates cryptographic methods to secure transactions and establish consensus among nodes.

#### **1. Proof of Work (PoW)**

- **Purpose**: The consensus mechanism used is Proof of Work (PoW). In PoW, miners compete to solve a computational puzzle by adjusting a `nonce` value such that the hash of the block data meets a specific difficulty target.
    
- **Mechanism**: When a node mines a new block, it broadcasts the block to its peers. Other nodes verify the block by checking if the hash matches the difficulty requirement. If valid, they add it to their blockchain and propagate it further.
    
- **Role in Security**: PoW ensures that altering a block would require re-mining all subsequent blocks, making tampering computationally infeasible.
    

#### **2. Merkle Tree for Data Integrity**

- **Purpose**: Transactions within a block are hashed using a Merkle Tree structure to generate a single root hash.
    
- **Role**: The Merkle root is included in the block header and represents all the transactions within the block. This makes it easy to verify whether a particular transaction exists in the block without storing all individual transaction data. Any changes to a transaction would change the root hash, ensuring tamper-evidence.
    

### **Cryptographic Layer**

The cryptographic layer ensures the security and authenticity of transactions and blocks. This layer involves several cryptographic protocols and algorithms.

#### **1. Elliptic Curve Digital Signature Algorithm (ECDSA)**

- **Purpose**: Used for generating key pairs (public and private keys) and signing transactions.
    
- **Usage**: Each wallet is generated using the ECDSA algorithm. Transactions are signed using the sender's private key, and the signature is verified by other nodes using the sender's public key.
    
- **Role**: Digital signatures ensure that only the rightful owner of a wallet can initiate a transaction, and they prevent unauthorized tampering of transactions.
    

#### **2. SHA-256 Hashing**

- **Purpose**: SHA-256 is used as the hashing algorithm for generating block hashes and Merkle tree hashes.
    
- **Usage**:
    
    - **Block Hashing**: The block's hash is computed by combining data such as the previous block's hash, Merkle root, timestamp, and nonce.
        
    - **Data Integrity**: Hashing ensures that if any piece of data in the block changes, the block hash will change, indicating tampering.
        

### **Persistence Layer**

The persistence layer deals with how the blockchain data is stored. In this project, CouchDB is used for storing blockchain state.

#### **1. CouchDB**

- **Purpose**: A NoSQL database used for maintaining a persistent, decentralized record of the blockchain state.
    
- **Usage**: Each node has an instance of CouchDB that stores its local copy of the blockchain and the mempool. This allows nodes to quickly recover their state after a restart.
    
- **Synchronization**: Nodes use CouchDB to load and save their blockchain state, which can then be synchronized with peer nodes to maintain consistency.
    

### **Data Flow Between Layers**

1. **Network Layer**: Nodes communicate via HTTP/REST and P2P to submit and retrieve data about transactions and blocks.
    
2. **Blockchain Layer**: Handles the core logic of adding new blocks, maintaining the integrity of the ledger using Proof of Work, and propagating the ledger state across nodes.
    
3. **Cryptographic Layer**: Uses hashing (SHA-256) and digital signatures (ECDSA) to secure transactions, generate wallet addresses, and prevent unauthorized changes.
    
4. **Persistence Layer**: Stores the blockchain in CouchDB, ensuring data is preserved across node restarts and allowing for consistent blockchain state among nodes.
    

### **Summary**

The blockchain project involves multiple layers that work together to provide a decentralized, secure, and reliable ledger system:

- The **network layer** facilitates communication between nodes using REST APIs and a P2P model.
    
- The **blockchain layer** ensures the distributed ledger is maintained correctly using consensus mechanisms like PoW and Merkle Trees for integrity.
    
- The **cryptographic layer** provides security through hashing and digital signatures, ensuring authenticity and tamper resistance.
    
- The **persistence layer** uses CouchDB to store blockchain data, making it resilient to node failures.
    

These layers work in tandem to ensure the blockchain's data integrity, reliability, and distributed consensus, thus enabling a secure environment for executing and validating transactions without central authority.


## Blockchain API

Use base URL:localhost:5000 for testing 

---

## 1. **Create Wallet**

### **Endpoint:** `/wallet/create`

**Method:** `POST`

### **Request Body:**

No request body is required.

### **Response Example:**

```
{
  "private_key": "your_private_key",
  "public_key": "your_public_key"
}
```

### **Description:**

Creates a new wallet and returns the public and private keys.

---

## 2. **Create Transaction**

### **Endpoint:** `/transaction/create`

**Method:** `POST`

### **Request Body:**

```
{
  "sender": "your_sender_public_key",
  "recipient": "recipient_public_key",
  "amount": 100,
  "private_key": "your_private_key"
}
```

### **Response Example:**

```
{
  "transaction_id": "generated_transaction_id",
  "sender": "your_sender_public_key",
  "recipient": "recipient_public_key",
  "amount": 100,
  "signature": "generated_signature"
}
```

### **Description:**

Creates and broadcasts a new transaction. Requires the sender's private key to sign the transaction.

---

## 3. **Add Transaction**

### **Endpoint:** `/transaction/add`

**Method:** `POST`

### **Request Body:**

```
{
  "sender": "sender_public_key",
  "recipient": "recipient_public_key",
  "amount": 100,
  "signature": "transaction_signature"
}
```

### **Response Example:**

```
{
  "message": "Transaction added"
}
```

### **Description:**

Adds a transaction directly to the mempool without verifying the signature.

---

## 4. **Mine Block**

### **Endpoint:** `/mine`

**Method:** `GET`

### **Request Body:**

No request body is required.

### **Response Example:**

```
{
  "index": 1,
  "transactions": [...],
  "timestamp": 1701269300.654321,
  "previous_hash": "previous_block_hash",
  "nonce": 12345,
  "merkle_root": "computed_merkle_root"
}
```

### **Description:**

Mines a new block using transactions in the mempool and adds it to the blockchain.

---

## 5. **Get Blockchain**

### **Endpoint:** `/chain`

**Method:** `GET`

### **Request Body:**

No request body is required.

### **Response Example:**

```
[
  {
    "index": 0,
    "transactions": [...],
    "timestamp": 1638316800,
    "previous_hash": "0",
    "nonce": 12345,
    "merkle_root": "computed_merkle_root"
  },
  {
    "index": 1,
    "transactions": [...],
    "timestamp": 1701269300.654321,
    "previous_hash": "previous_block_hash",
    "nonce": 67890,
    "merkle_root": "computed_merkle_root"
  }
]
```

### **Description:**

Returns the entire blockchain as a list of blocks.

---

## 6. **Get Wallet Balance**

### **Endpoint:** `/balance/<wallet_address>`

**Method:** `GET`

### **Request Body:**

No request body is required.

### **Response Example:**

```
{
  "balance": 500
}
```

### **Description:**

Returns the balance of the specified wallet address.

---

## 7. **Get Pending Transactions**

### **Endpoint:** `/pending_transactions`

**Method:** `GET`

### **Request Body:**

No request body is required.

### **Response Example:**

```
{
  "pending_transactions": [
    {
      "transaction_id": "transaction_id",
      "sender": "sender_public_key",
      "recipient": "recipient_public_key",
      "amount": 100,
      "signature": "transaction_signature"
    }
  ]
}
```

### **Description:**

Returns all transactions currently in the mempool.

---

## 8. **Get ICO Funds**

### **Endpoint:** `/ico_funds`

**Method:** `GET`

### **Request Body:**

No request body is required.

### **Response Example:**

```
{
  "ICO_funds_remaining": 1000000
}
```

### **Description:**

Returns the remaining ICO funds in the genesis wallet.

---

## 9. **Verify Transaction**

### **Endpoint:** `/transaction/verify`

**Method:** `POST`

### **Request Body:**

```
{
  "transaction_id": "your_transaction_id"
}
```

### **Response Example:**

```
{
  "is_valid": true
}
```

### **Description:**

Verifies the signature of a transaction using its `transaction_id`.

---

## 10. **Submit Off-Chain Transaction**

### **Endpoint:** `/transaction/submit_offchain`

**Method:** `POST`

### **Request Body:**

```
{
  "transaction_id": "your_transaction_id"
}
```

### **Response Example:**

```
{
  "message": "Off-chain transaction submitted successfully"
}
```

### **Description:**

Submits an off-chain signed transaction to the blockchain.

---

## 11. **Get Transaction Details**

### **Endpoint:** `/transaction/details`

**Method:** `POST`

### **Request Body:**

```
{
  "transaction_id": "your_transaction_id"
}
```

### **Response Example:**

- **Pending Transaction:**
    

```
{
  "transaction_id": "your_transaction_id",
  "sender": "sender_public_key",
  "recipient": "recipient_public_key",
  "amount": 100,
  "signature": "transaction_signature",
  "status": "pending"
}
```

- **Confirmed Transaction:**
    

```
{
  "transaction_id": "your_transaction_id",
  "sender": "sender_public_key",
  "recipient": "recipient_public_key",
  "amount": 100,
  "signature": "transaction_signature",
  "timestamp": 1701269300.654321,
  "status": "confirmed",
  "block_index": 1,
  "block_timestamp": 1701269300.654321
}
```

- **Transaction Not Found:**
    

```
{
  "error": "Transaction not found"
}
```

### **Description:**

Retrieves the details of a transaction using its `transaction_id`. Indicates whether the transaction is pending or confirmed and includes block details if applicable.

---

## **Usage Notes:**

- Ensure that you have the correct headers for `Content-Type` as `application/json` when using POST requests.

