# database/couchdb_handler.py

import os
import couchdb
from blockchain.block import Block


class CouchDBHandler:
    def __init__(self, db_name):
        couchdb_url = os.getenv('COUCHDB_URL', 'http://admin:admin@localhost:5984/')
        try:
            self.server = couchdb.Server(couchdb_url)
            if db_name not in self.server:
                self.db = self.server.create(db_name)
                print(f"Created '{db_name}' database in CouchDB.")
            else:
                self.db = self.server[db_name]
                print(f"Connected to existing '{db_name}' database.")
        except Exception as e:
            print(f"Error connecting to CouchDB at {couchdb_url}: {e}")

    def save_block(self, block):
        try:
            # Use block index as document ID to prevent duplicates
            doc_id = f"block_{block.index}"
            if doc_id not in self.db:
                self.db.save({"_id": doc_id, **block.to_dict()})
                print(f"Block {block.index} saved to CouchDB.")
            else:
                print(f"Block {block.index} already exists in CouchDB.")
        except Exception as e:
            print(f"Error saving block: {e}")

    def save_blockchain_state(self, blockchain_state):
        try:
            doc_id = "blockchain_state"
            if doc_id in self.db:
                doc = self.db[doc_id]
                doc.update(blockchain_state)
                self.db.save(doc)
                print("Blockchain state updated in CouchDB.")
            else:
                self.db.save({"_id": doc_id, **blockchain_state})
                print("Blockchain state saved to CouchDB.")
        except Exception as e:
            print(f"Error saving blockchain state: {e}")

    def load_blockchain_state(self):
        try:
            doc_id = "blockchain_state"
            if doc_id in self.db:
                print("Blockchain state loaded from CouchDB.")
                return self.db[doc_id]
            else:
                print("No blockchain state found in CouchDB.")
                return None
        except Exception as e:
            print(f"Error loading blockchain state: {e}")
            return None

    def delete_blockchain_state(self):
        try:
            doc_id = "blockchain_state"
            if doc_id in self.db:
                del self.db[doc_id]
                print("Blockchain state deleted from CouchDB.")
            else:
                print("No blockchain state found to delete.")
        except Exception as e:
            print(f"Error deleting blockchain state: {e}")
