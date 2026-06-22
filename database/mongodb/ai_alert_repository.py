from database.mongodb.mongo_manager import (
    db
)


def get_ai_alert_collection():

    return db[
        "ai_alerts"
    ]


def save_ai_alert(alert):

    get_ai_alert_collection().insert_one(
        alert
    )


def count_ai_alerts():

    return (
        get_ai_alert_collection()
        .count_documents({})
    )


def get_latest_ai_alert():

    return (
        get_ai_alert_collection()
        .find_one(
            {},
            sort=[
                (
                    "timestamp",
                    -1
                )
            ]
        )
    )


def get_all_ai_alerts():

    return list(
        get_ai_alert_collection()
        .find(
            {},
            {
                "_id": 0
            }
        )
        .sort(
            "timestamp",
            -1
        )
    )