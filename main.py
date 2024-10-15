import hashlib
import json
import time

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
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", [], time.time(), 0)
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]
    
    def add_block(self, block, proof):
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
    
    def add_new_vote(self, voter_id, candidate):
        vote = {"voter_id": voter_id, "candidate": candidate}
        self.unconfirmed_votes.append(vote)

    def mine(self):
        if not self.unconfirmed_votes:
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
    

voting_chain = Blockchain()

voting_chain.add_new_vote("Voter1", "CandidateA")
voting_chain.add_new_vote("Voter2", "CandidateB")

voting_chain.mine()

voting_chain.add_new_vote("Voter3", "CandidateA")
voting_chain.add_new_vote("Voter4", "CandidateC")

voting_chain.mine()

is_valid = voting_chain.validate_chain()

print("Blockchain is valid:", is_valid)

for block in voting_chain.chain:
    print(
        f"Block {block.index}:\n"
        f"Hash: {block.hash}\n"
        f"Previous Hash: {block.previous_hash}\n"
        f"Votes: {block.votes}\n"
    )
