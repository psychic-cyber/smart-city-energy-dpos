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

    total_transactions = len(
        transactions
    )

    total_energy_consumed = 0
    total_energy_generated = 0
    total_bill_amount = 0
    anomalies_detected = 0

    district_totals = {}

    entity_counts = {}

    entity_consumption = {
        "House": 0,
        "School": 0,
        "Office": 0
    }

    for transaction in transactions:

        consumed = float(
            transaction.get(
                "energy_consumed",
                0
            )
        )

        generated = float(
            transaction.get(
                "energy_generated",
                0
            )
        )

        bill = float(
            transaction.get(
                "bill_amount",
                0
            )
        )

        district = transaction.get(
            "district",
            "Unknown"
        )

        entity_type = transaction.get(
            "entity_type",
            "Unknown"
        )

        total_energy_consumed += consumed
        total_energy_generated += generated
        total_bill_amount += bill

        district_totals[
            district
        ] = (
            district_totals.get(
                district,
                0
            )
            + consumed
        )

        entity_counts[
            entity_type
        ] = (
            entity_counts.get(
                entity_type,
                0
            )
            + 1
        )

        if entity_type in entity_consumption:

            entity_consumption[
                entity_type
            ] += consumed

        if (
            transaction.get(
                "anomaly"
            )
            ==
            "Yes"
        ):
            anomalies_detected += 1

    avg_energy_consumed = (
        total_energy_consumed /
        total_transactions
        if total_transactions
        else 0
    )

    avg_energy_generated = (
        total_energy_generated /
        total_transactions
        if total_transactions
        else 0
    )

    avg_bill = (
        total_bill_amount /
        total_transactions
        if total_transactions
        else 0
    )

    anomaly_percentage = (
        (
            anomalies_detected /
            total_transactions
        ) * 100
        if total_transactions
        else 0
    )

    top_district = (
        max(
            district_totals,
            key=district_totals.get
        )
        if district_totals
        else "N/A"
    )

    highest_district = (
        max(
            district_totals,
            key=district_totals.get
        )
        if district_totals
        else "N/A"
    )

    lowest_district = (
        min(
            district_totals,
            key=district_totals.get
        )
        if district_totals
        else "N/A"
    )

    energy_efficiency = (
        (
            total_energy_generated
            /
            total_energy_consumed
        ) * 100
        if total_energy_consumed
        else 0
    )

    if energy_efficiency > 100:
        energy_efficiency = 100

    carbon_saved = (
        total_energy_generated
        * 0.4
    )

    health_score = (
        (
            energy_efficiency
            * 0.7
        )
        +
        (
            (
                100
                -
                anomaly_percentage
            )
            * 0.3
        )
    )

    return {

        "total_transactions":
            total_transactions,

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
            anomalies_detected,

        "anomaly_percentage":
            round(
                anomaly_percentage,
                2
            ),

        "avg_energy_consumed":
            round(
                avg_energy_consumed,
                2
            ),

        "avg_energy_generated":
            round(
                avg_energy_generated,
                2
            ),

        "avg_bill":
            round(
                avg_bill,
                2
            ),

        "top_district":
            top_district,

        "highest_district":
            highest_district,

        "lowest_district":
            lowest_district,

        "district_count":
            len(
                district_totals
            ),

        "entity_distribution":
            entity_counts,

        "house_consumption":
            round(
                entity_consumption[
                    "House"
                ],
                2
            ),

        "school_consumption":
            round(
                entity_consumption[
                    "School"
                ],
                2
            ),

        "office_consumption":
            round(
                entity_consumption[
                    "Office"
                ],
                2
            ),

        "energy_efficiency":
            round(
                energy_efficiency,
                2
            ),

        "carbon_saved":
            round(
                carbon_saved,
                2
            ),

        "health_score":
            round(
                health_score,
                2
            )
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