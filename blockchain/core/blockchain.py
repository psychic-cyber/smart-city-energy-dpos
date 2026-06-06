from blockchain.core.block import Block


class Blockchain:

    def __init__(self):

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

        previous_block = (
            self.get_latest_block()
        )

        block_data = {
            "validator": validator,
            "transaction": transaction
        }

        new_block = Block(
            len(self.chain),
            block_data,
            previous_block.hash
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
