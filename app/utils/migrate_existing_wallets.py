import os

from eth_account import Account
from dotenv import load_dotenv

from app.utils.wallet_generator import create_wallet
from database.mongodb.mongo_manager import db

load_dotenv("contracts/.env")

users = db["users"]


def update_system_wallet(username, private_key):

    if not private_key:
        print(f"Missing key for {username}")
        return

    account = Account.from_key(private_key)

    users.update_one(
        {
            "username": username
        },
        {
            "$set": {
                "wallet_address": account.address,
                "private_key": private_key
            }
        }
    )

    print(f"{username} updated (system wallet)")


# System wallets
update_system_wallet(
    "Admin",
    os.getenv("PRIVATE_KEY_OWNER")
)

update_system_wallet(
    "SmartCity-Hospital01",
    os.getenv("PRIVATE_KEY_HOSPITAL")
)

update_system_wallet(
    "SmartCity-SolarFarm01",
    os.getenv("PRIVATE_KEY_SOLAR")
)

update_system_wallet(
    "SmartCity-University01",
    os.getenv("PRIVATE_KEY_UNIVERSITY")
)


# Generate wallets for all remaining users
for user in users.find():

    if user.get("wallet_address"):
        continue

    wallet = create_wallet()

    users.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": {
                "wallet_address": wallet["address"],
                "private_key": wallet["private_key"]
            }
        }
    )

    print(f"{user['username']} updated (generated wallet)")

print("\nMigration completed successfully.")