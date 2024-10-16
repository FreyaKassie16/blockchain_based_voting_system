import hashlib
import json
import time
import socket
import threading

class Block:
    def __init__(self, index, previous_hash, votes, timestamp, proof):
        self.index = index
        self.previous_hash = previous_hash
        self.votes = votes
        self.timestamp = timestamp
        self.proof = proof
        self.hash = None

    def compute_hash(self):
        block_dict = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "votes": self.votes,
            "timestamp": self.timestamp,
            "proof": self.proof
        }
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    

class Blockchain:
    def __init__(self):
        self.unconfirmed_votes = []
        self.chain = []
        self.voter_whitelist = {"Voter1", "Voter2", "Voter3", "Voter4"}
        self.voted_voters = set()
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], time.time(), 0)
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]
    
    def add_block(self, block: Block, proof):
        previous_hash = self.get_last_block().hash
        if previous_hash != block.previous_hash:
            return False
        
        if not self.is_valid_proof(block, proof):
            return False
        
        block.hash = proof
        self.chain.append(block)
        return True
    
    def proof_of_work(self, block: Block):
        block.proof = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith("0000"):
            block.proof += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
    def add_new_vote(self, voter_id: str, candidate: str):
        if voter_id not in self.voter_whitelist:
            print(f"Voter ID {voter_id} is not authorized to vote!")
            return False
        
        if voter_id in self.voted_voters:
            print(f"Voter ID {voter_id} has already voted!")
            return False
        
        vote = {"voter_id": voter_id, "candidate": candidate}
        self.unconfirmed_votes.append(vote)
        self.voted_voters.add(voter_id)
        print(f"Vote accepted from {voter_id} for {candidate}")
        return True

    def mine(self):
        if not self.unconfirmed_votes:
            print("No votes to mine.")
            return False
        
        last_block = self.get_last_block()
        new_block = Block(index=last_block.index + 1,
                          previous_hash=last_block.hash,
                          votes=self.unconfirmed_votes,
                          timestamp=time.time(),
                          proof=0)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_votes = []
        return new_block.index
    
    def is_valid_proof(self, block, block_hash):
        return (
            block_hash.startswith("0000") 
            and block_hash == block.compute_hash()
        )
    
    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.compute_hash():
                print(f"Block {current_block.index} has been tampered with!")
                return False
            
            if current_block.previous_hash != previous_block.hash:
                print(
                    f"Block {current_block.index}'s previous hash doesn't "
                    "match the hash of the previous block!"
                )
                return False
            
        return True
    
def broadcast_new_block(block):
    peers = [("127.0.0.1", 5001), ("127.0.0.1", 5002)]
    block_data = json.dumps(block.__dict__)
    for peer in peers:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(peer)
                s.sendall(block_data.encode())
                print(f"Block broadcasted to {peer}")
            except ConnectionRefusedError:
                print(f"Failed to connect to {peer}")

def listen_for_blocks(blockchain, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen()
        print(f"Listening for new blocks on port {port}...")
        while True:
            conn, addr = s.accept()
            with conn:
                block_data = conn.recv(1024)
                if block_data:
                    new_block_dict = json.loads(block_data.decode())
                    if new_block_dict['index'] == 0:  # Genesis block
                        new_genesis_block = Block(
                            index=new_block_dict['index'],
                            previous_hash=new_block_dict['previous_hash'],
                            votes=new_block_dict['votes'],
                            timestamp=new_block_dict['timestamp'],
                            proof=new_block_dict['proof']
                        )
                        new_genesis_block.hash = new_genesis_block.compute_hash()
                        blockchain.chain.append(new_genesis_block)
                        print(f"Genesis block added from {addr}")
                    else:
                        new_block = Block(
                            index=new_block_dict["index"],
                            previous_hash=new_block_dict["previous_hash"],
                            votes=new_block_dict["votes"],
                            timestamp=new_block_dict["timestamp"],
                            proof=new_block_dict["proof"]
                        )
                        new_block.hash = new_block.compute_hash()

                        if blockchain.add_block(new_block, new_block.hash):
                            print(f"New block added from {addr}")
                        else:
                            print(f"Block from {addr} is invalid")

def run_node(blockchain, port):
    thread = threading.Thread(
        target=listen_for_blocks, 
        args=(blockchain, port)
    )
    thread.start()

    if len(blockchain.chain) == 1:
        genesis_block = blockchain.chain[0]
        broadcast_new_block(genesis_block)

    while True:
        command = input(
            "Enter 'mine' to mine a block, 'vote' to cast a vote: "
        ).strip()

        if command == "mine":
            blockchain.mine()
            last_block = blockchain.get_last_block()
            broadcast_new_block(last_block)

        elif command == "vote":
            voter_id = input("Enter your voter ID: ")
            candidate = input("Enter your candidate: ")
            blockchain.add_new_vote(voter_id, candidate)

        elif command == "show":
            for block in voting_chain.chain:
                print(
                    f"Block {block.index}:\n"
                    f"Hash: {block.hash}\n"
                    f"Previous Hash: {block.previous_hash}\n"
                    f"Votes: {block.votes}\n"
                )

voting_chain = Blockchain()
run_node(voting_chain, 5002)


