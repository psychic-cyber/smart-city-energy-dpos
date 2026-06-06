import random

from blockchain.dpos.delegate import Delegate


class DPoSConsensus:

    def __init__(self):

        self.delegates = []

    def register_delegate(
        self,
        delegate
    ):

        self.delegates.append(
            delegate
        )

    def get_top_delegate(self):

        return max(
            self.delegates,
            key=lambda d: d.votes
        )

    def select_delegate(self):

        total_votes = sum(
            delegate.votes
            for delegate in self.delegates
        )

        random_number = random.uniform(
            0,
            total_votes
        )

        current = 0

        for delegate in self.delegates:

            current += delegate.votes

            if current >= random_number:

                return delegate

        return self.delegates[0]
