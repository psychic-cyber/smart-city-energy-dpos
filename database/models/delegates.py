class Delegate:

    def __init__(
        self,
        username,
        role,
        votes=0,
        is_active=True
    ):

        self.username = username
        self.role = role
        self.votes = votes
        self.is_active = is_active

    def to_dict(self):

        return {
            "username":
                self.username,

            "role":
                self.role,

            "votes":
                self.votes,

            "is_active":
                self.is_active
        }