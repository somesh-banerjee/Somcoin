# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 18:48:54 2021

@author: Somesh
"""

#importing libraries
import datetime #to get the date & time of block mined
import hashlib #to hash the block
import json #to encode blocks using DOM
from flask import Flask, jsonify, request #for web interaction 
import requests
from uuid import uuid4
from urllib.parse import urlparse

#building a blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                 new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def validate_chain(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[0:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if(response.status_code == 200):
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and blockchain.validate_chain(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
#Creating Web App
app = Flask(__name__)

# creating an adress for node on port 5000
node_address = str(uuid4()).replace('-', '')

#creating a Blockchain object
blockchain = Blockchain()

#Mining blocks
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender = node_address, receiver = 'Master', amount = 7)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Block is mined',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'transactions':block['transactions'],
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

#addingnew transactions
@app.route('/add_transactions',methods = ['POST'])
def add_transactions():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transactions(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to block {index}'}
    return jsonify(response), 201

#Decentralizing blockchain

#Connecting new nodes
@app.route('/connect_node',methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes are now connected',
                'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201

#replacing chain with longest chain
@app.route('/replacechain', methods = ['GET'])
def replace_chain():
    is_replace = blockchain.replace_chain()
    if is_replace:
        response = {'message':'Blockchain replaced with longest one.',
                    'new_chain':blockchain.chain}
    else:
        response = {'message':'Blockhain not replaced'}
    return jsonify(response), 200

#Running the app
app.run(host = '0.0.0.0',port = 5000)