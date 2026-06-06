from datetime import datetime

from blockchain.utils.hash_utils import calculate_hash


class Block:

    def __init__(
        self,
        index,
        data,
        previous_hash
    ):

        self.index = index

        self.timestamp = str(
            datetime.now()
        )

        self.data = data

        self.previous_hash = previous_hash

        self.hash = self.generate_hash()

    def generate_hash(self):

        block_data = (
            str(self.index)
            + self.timestamp
            + str(self.data)
            + self.previous_hash
        )

        return calculate_hash(
            block_data
        )

    def to_dict(self):

        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }
