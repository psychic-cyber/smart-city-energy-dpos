from datetime import datetime

from blockchain.utils.hash_utils import calculate_hash


class Block:

    def __init__(
        self,
        index,
        data,
        previous_hash,
        timestamp=None,
        block_hash=None
    ):

        self.index = index

        self.timestamp = (
            timestamp
            if timestamp
            else str(datetime.now())
        )

        self.data = data

        self.previous_hash = previous_hash

        self.hash = (
            block_hash
            if block_hash
            else self.generate_hash()
        )

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

    @classmethod
    def from_dict(
        cls,
        block_data
    ):

        return cls(
            index=block_data["index"],
            data=block_data["data"],
            previous_hash=block_data["previous_hash"],
            timestamp=block_data["timestamp"],
            block_hash=block_data["hash"]
        )
