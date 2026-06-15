from database.mongodb.mongo_manager import (
    get_transactions_collection
)

from database.mongodb.user_repository import (
    get_all_users,
    count_role
)

from database.mongodb.user_transaction_repository import (
    get_all_user_transactions
)

from database.mongodb.blockchain_repository import (
    count_blocks
)

from ml.ai_engine import (
    get_ai_monitoring_data
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

    users = get_all_users()

    transactions = (
        get_all_user_transactions()
    )

    total_generated = sum(
        float(
            user.get(
                "energy_generated",
                0
            )
        )
        for user in users
    )

    total_consumed = sum(
        float(
            user.get(
                "energy_consumed",
                0
            )
        )
        for user in users
    )

    total_revenue = sum(
        float(
            tx.get(
                "revenue",
                0
            )
        )
        for tx in transactions
    )

    total_transactions = len(
        transactions
    )

    efficiency = (
        (
            total_generated
            /
            total_consumed
        )
        * 100
        if total_consumed
        else 0
    )

    if efficiency > 100:
        efficiency = 100

    entity_distribution = {
        "House":
            count_role("House"),

        "Hospital":
            count_role("Hospital"),

        "University":
            count_role("University"),

        "Restaurant":
            count_role("Restaurant"),

        "Office":
            count_role("Office"),

        "Factory":
            count_role("Factory"),

        "SolarFarm":
            count_role("SolarFarm")
    }

    ai_data = get_ai_monitoring_data()

    return {

        "total_transactions":
            total_transactions,

        "total_energy_generated":
            round(
                total_generated,
                2
            ),

        "total_energy_consumed":
            round(
                total_consumed,
                2
            ),

        "total_bill_amount":
            round(
                total_revenue,
                2
            ),

        "total_blocks":
            count_blocks(),

        "energy_efficiency":
            round(
                efficiency,
                2
            ),

        "entity_distribution":
            entity_distribution,

        "anomalies_detected":
            ai_data["anomalies"],

        "anomaly_percentage":
            ai_data["anomaly_rate"],

        "health_score":
            ai_data["confidence"]
    }


def get_district_analytics():

    collection = (
        get_transactions_collection()
    )

    pipeline = [
        {
            "$group": {
                "_id": "$district",
                "energy": {
                    "$sum": {
                        "$toDouble":
                        "$energy_consumed"
                    }
                }
            }
        }
    ]

    return list(
        collection.aggregate(
            pipeline
        )
    )