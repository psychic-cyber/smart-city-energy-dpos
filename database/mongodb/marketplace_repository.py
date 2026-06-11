from datetime import datetime

from database.mongodb.mongo_manager import (
    db,
)


def get_marketplace_collection():

    return db[
        "marketplace_listings"
    ]


def create_listing(
    seller,
    energy,
    price
):

    listing = {

        "seller":
            seller,

        "energy":
            energy,

        "price_per_kwh":
            price,

        "total_price":
            energy * price,

        "status":
            "Available",

        "buyer":
            None,

        "created_at":
            str(
                datetime.now()
            )
    }

    get_marketplace_collection().insert_one(
        listing
    )


def get_available_listings():

    return list(
        get_marketplace_collection()
        .find(
            {
                "status":
                    "Available"
            },
            {
                "_id": 0
            }
        )
    )


def complete_listing(
    seller,
    buyer
):

    get_marketplace_collection().update_one(
        {
            "seller":
                seller,

            "status":
                "Available"
        },
        {
            "$set":
                {
                    "status":
                        "Completed",

                    "buyer":
                        buyer
                }
        }
    )


def has_active_listing(
    seller
):

    return (
        get_marketplace_collection()
        .count_documents(
            {
                "seller": seller,
                "status": "Available"
            }
        ) > 0
    )

def get_listing_by_seller(
    seller
):

    return get_marketplace_collection().find_one(
        {
            "seller": seller,
            "status": "Available"
        }
    )