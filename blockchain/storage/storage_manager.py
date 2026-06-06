import json

from blockchain.core.block import Block


BLOCKCHAIN_FILE = (
    "blockchain/storage/blockchain_data.json"
)


def save_blockchain(chain):

    blockchain_data = []

    for block in chain:

        blockchain_data.append(
            block.to_dict()
        )

    with open(
        BLOCKCHAIN_FILE,
        "w"
    ) as file:

        json.dump(
            blockchain_data,
            file,
            indent=4
        )


def load_blockchain():

    with open(
        BLOCKCHAIN_FILE,
        "r"
    ) as file:

        blockchain_data = json.load(
            file
        )

    chain = []

    for block_data in blockchain_data:

        chain.append(
            Block.from_dict(
                block_data
            )
        )

    return chain
