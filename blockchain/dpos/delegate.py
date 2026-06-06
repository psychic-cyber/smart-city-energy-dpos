class Delegate:

    def __init__(
        self,
        delegate_id,
        district,
        votes
    ):

        self.delegate_id = delegate_id
        self.district = district
        self.votes = votes

    def to_dict(self):

        return {
            "delegate_id": self.delegate_id,
            "district": self.district,
            "votes": self.votes
        }
