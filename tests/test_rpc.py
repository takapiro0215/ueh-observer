from web3 import Web3

# public RPC（まずはこれでOK）
RPC_URL = "https://eth.llamarpc.com"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

print("Connected:", w3.is_connected())

if w3.is_connected():
    block = w3.eth.block_number
    print("Latest block:", block)