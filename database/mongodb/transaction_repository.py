from database.mongodb.mongo_manager import (
    get_transactions_collection
)


def save_transaction(
    transaction
):

    collection = (
        get_transactions_collection()
    )

    collection.insert_one(
        transaction
    )


def count_transactions():

    collection = (
        get_transactions_collection()
    )

    return collection.count_documents(
        {}
    )
