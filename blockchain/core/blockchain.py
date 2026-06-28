from blockchain.core.block import Block

from database.mongodb.blockchain_repository import (
    load_chain_from_mongo
)

from app.services.dpos_service import (
    get_current_validator
)


class Blockchain:

    def __init__(self):

        try:

            loaded_chain = load_chain_from_mongo()

            if len(loaded_chain) > 0:

                self.chain = loaded_chain

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

        validator = get_current_validator(
            fallback=validator or "SYSTEM"
        )

        latest_block = self.get_latest_block()

        next_index = (
            latest_block.index + 1
        )

        previous_hash = (
            latest_block.hash
        )

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

        for i in range(1, len(self.chain)):

            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return False

            if (
                current_block.hash != current_block.generate_hash()
            ):
                return False

        return True

    def display_chain(self):

        for block in self.chain:

            print(
                block.to_dict()
            )
