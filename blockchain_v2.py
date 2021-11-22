# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 22:18:55 2021

@author: Somesh Banerjee
"""

#importing libraries
import datetime #to get the date & time of block mined
import hashlib #to hash the block
import json #to encode blocks using DOM
from flask import Flask, jsonify #for web interaction 

#building a blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        gproof = self.proof_of_work('0')
        self.create_block(proof = gproof, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'proof': proof,
                 'previous_hash': previous_hash}
        current_hash = self.hash(block)
        block['timestamp'] = str(datetime.datetime.now())
        block['current_hash'] = current_hash
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_hash):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            block = {'index': len(self.chain) + 1,
                 'proof': new_proof,
                 'previous_hash': previous_hash}
            encoded_block = json.dumps(block, sort_keys = True).encode()
            hash_operation = hashlib.sha256(encoded_block).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                 new_proof += 1
        return new_proof
    
    def hash(self, block):
        proof = block['proof']
        previous_hash = block['previous_hash']
        tblock = {'index': block['index'],
                 'proof': proof,
                 'previous_hash': previous_hash}
        encoded_block = json.dumps(tblock, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def validate_chain(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            proof = block['proof']
            tblock = {'index': block_index + 1,
                 'proof': proof,
                 'previous_hash': self.hash(previous_block)}
            encoded_block = json.dumps(tblock, sort_keys = True).encode()
            hash_operation = hashlib.sha256(encoded_block).hexdigest()
            if hash_operation[0:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True
    
#Creating Web App
app = Flask(__name__)


#creating a Blockchain object
blockchain = Blockchain()

#Mining blocks
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = blockchain.hash(previous_block)
    proof = blockchain.proof_of_work(previous_hash)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Block is mined',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

#getting the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'chain_length': len(blockchain.chain)}
    return jsonify(response), 200

#Checking if the blockchain is valid
@app.route('/isvalid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.validate_chain(blockchain.chain)
    if is_valid:
        response = {'message':'Blockchain valid.'}
    else:
        response = {'message':'Blockhain invalid'}
    return jsonify(response), 200

#Running the app
app.run(host = '0.0.0.0',port = 5000)