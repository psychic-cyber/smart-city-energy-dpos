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

def get_transactions(limit=20):

    collection = (
        get_transactions_collection()
    )

    transactions = list(
        collection.find(
            {},
            {"_id": 0}
        ).limit(limit)
    )

    return transactions

def get_analytics():

    collection = (
        get_transactions_collection()
    )

    transactions = list(
        collection.find(
            {},
            {"_id": 0}
        )
    )

    total_energy_consumed = 0
    total_energy_generated = 0
    total_bill_amount = 0
    anomalies_detected = 0

    for transaction in transactions:

        total_energy_consumed += float(
            transaction.get(
                "energy_consumed",
                0
            )
        )

        total_energy_generated += float(
            transaction.get(
                "energy_generated",
                0
            )
        )

        total_bill_amount += float(
            transaction.get(
                "bill_amount",
                0
            )
        )

        if (
            transaction.get(
                "anomaly"
            )
            ==
            "Yes"
        ):
            anomalies_detected += 1

    return {
        "total_energy_consumed":
            round(
                total_energy_consumed,
                2
            ),

        "total_energy_generated":
            round(
                total_energy_generated,
                2
            ),

        "total_bill_amount":
            round(
                total_bill_amount,
                2
            ),

        "anomalies_detected":
            anomalies_detected
    }
