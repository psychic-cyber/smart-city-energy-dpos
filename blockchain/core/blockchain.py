from blockchain.core.block import Block

from blockchain.storage.storage_manager import (
    load_blockchain
)

from database.mongodb.blockchain_repository import (
    get_latest_block
)


class Blockchain:

    def __init__(self):

        try:

            loaded_chain = (
                load_blockchain()
            )

            if len(
                loaded_chain
            ) > 0:

                self.chain = (
                    loaded_chain
                )

            else:

                self.chain = [
                    self.create_genesis_block()
                ]

        except Exception:

            self.chain = [
                self.create_genesis_block()
            ]

    def create_genesis_block(self):

        return Block(
            0,
            "Genesis Block",
            "0"
        )

    def get_latest_block(self):

        return self.chain[-1]

    def add_block(
        self,
        transaction,
        validator=None
    ):

        mongo_latest = get_latest_block()

        if mongo_latest:

            next_index = (
                mongo_latest["index"] + 1
            )

            previous_hash = (
                mongo_latest["hash"]
            )

        else:

            next_index = 1

            previous_hash = "0"

        block_data = {
            "validator": validator,
            "transaction": transaction
        }

        new_block = Block(
            next_index,
            block_data,
            previous_hash
    )

        self.chain.append(
            new_block
        )

    def is_chain_valid(self):

        for i in range(
            1,
            len(self.chain)
        ):

            current_block = (
                self.chain[i]
            )

            previous_block = (
                self.chain[i - 1]
            )

            if (
                current_block.previous_hash
                != previous_block.hash
            ):
                return False

        return True

    def display_chain(self):

        for block in self.chain:

            print(
                block.to_dict()
            )
