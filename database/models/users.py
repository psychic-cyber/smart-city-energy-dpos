from datetime import datetime


class User:

    def __init__(
    self,
    username,
    email,
    password,
    role="user",
    energy_balance=0,
    wallet_address="",
    private_key=""
):

        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.energy_balance = energy_balance

        self.wallet_address = wallet_address
        self.private_key = private_key

        self.created_at = str(
            datetime.utcnow()
        )

    def to_dict(self):

        return {
            "username":
                self.username,

            "email":
                self.email,

            "password":
                self.password,

            "role":
                self.role,

            "energy_balance":
                self.energy_balance,

            "wallet_address":
                self.wallet_address,

            "private_key":
                self.private_key,

            "created_at":
                self.created_at,
            
            "total_revenue":
                0,

            "energy_generated":
                0,

            "energy_consumed":
                0
        }