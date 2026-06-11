from datetime import datetime
from database.mongodb.mongo_manager import db


def get_transactions_collection():

    return db[
        "user_transactions"
    ]


def save_user_transaction(
    username,
    buyer,
    energy_sold,
    revenue
):

    transaction = {

        "username":
            username,

        "buyer":
            buyer,

        "energy_sold":
            energy_sold,

        "revenue":
            revenue,

        "status":
            "Completed",

        "timestamp":
            str(
                datetime.now()
            )
    }

    get_transactions_collection().insert_one(
        transaction
    )


def get_user_transactions(
    username
):

    return list(
        get_transactions_collection()
        .find(
            {
                "username": username
            },
            {
                "_id": 0
            }
        )
        .sort(
            "timestamp",
            -1
        )
        .limit(10)
    )
