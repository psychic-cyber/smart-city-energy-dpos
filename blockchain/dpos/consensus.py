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

        if not self.delegates:
            return None

        return sorted(
            self.delegates,
            key=lambda delegate: (
                -delegate.votes,
                str(delegate.delegate_id)
            )
        )[0]

    def select_delegate(self):

        return self.get_top_delegate()
