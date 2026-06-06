from blockchain.core.blockchain import Blockchain


blockchain = Blockchain()

blockchain.add_block(
    {
        "user": "Hospital-01",
        "energy": 500
    },
    "District-A"
)

blockchain.add_block(
    {
        "user": "School-02",
        "energy": 250
    },
    "District-C"
)

blockchain.display_chain()

print(
    "\nChain Valid:",
    blockchain.is_chain_valid()
)
