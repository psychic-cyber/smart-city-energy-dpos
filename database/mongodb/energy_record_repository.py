from datetime import datetime

from database.mongodb.mongo_manager import db


def get_energy_records_collection():

    return db[
        "energy_records"
    ]


def save_energy_record(
    username,
    generated,
    consumed
):

    get_energy_records_collection().insert_one(
        {
            "username":
                username,

            "energy_generated":
                generated,

            "energy_consumed":
                consumed,

            "status":
                "Pending",

            "created_at":
                str(
                    datetime.now()
                )
        }
    )


def get_pending_records():

    return list(
        get_energy_records_collection()
        .find(
            {
                "status":
                    "Pending"
            },
            {
                "_id": 0
            }
        )
    )


def approve_record(
    username
):

    get_energy_records_collection().update_one(
        {
            "username":
                username,

            "status":
                "Pending"
        },
        {
            "$set":
                {
                    "status":
                        "Approved"
                }
        }
    )

def decline_record(
    username
):

    get_energy_records_collection().update_one(
        {
            "username":
                username,

            "status":
                "Pending"
        },
        {
            "$set":
                {
                    "status":
                        "Declined"
                }
        }
    )


def get_latest_approved_record(
    username
):

    return get_energy_records_collection().find_one(
        {
            "username":
                username,

            "status":
                "Approved"
        },
        sort=[
            (
                "created_at",
                -1
            )
        ]
    )

def get_pending_record_by_username(
    username
):

    return (
        get_energy_records_collection()
        .find_one(
            {
                "username": username,
                "status": "Pending"
            }
        )
    )