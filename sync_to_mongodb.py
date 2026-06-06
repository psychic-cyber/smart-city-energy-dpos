from blockchain.core.blockchain import Blockchain

from database.mongodb.blockchain_repository import (
    save_chain,
    count_blocks
)


blockchain = Blockchain()

save_chain(
    blockchain.chain
)

print(
    "Blockchain Blocks:",
    len(blockchain.chain)
)

print(
    "MongoDB Blocks:",
    count_blocks()
)
