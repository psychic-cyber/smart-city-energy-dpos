from datetime import datetime

from pymongo import ReturnDocument

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
    price,
    blockchain_listing_id
):

    listing = {

        "seller":
            seller,

        "blockchain_listing_id": 
            blockchain_listing_id,

        "energy":
            energy,

        "original_energy":
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

    return listing


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


def purchase_listing(seller, quantity, buyer):
    """Atomically reserve energy and return the listing after the purchase."""
    listing = get_marketplace_collection().find_one_and_update(
        {
            "seller": seller,
            "status": "Available",
            "energy": {"$gte": quantity},
        },
        {
            "$inc": {"energy": -quantity},
            "$set": {"last_buyer": buyer},
        },
        return_document=ReturnDocument.AFTER,
    )

    if listing and listing["energy"] == 0:
        get_marketplace_collection().update_one(
            {"_id": listing["_id"], "energy": 0},
            {"$set": {"status": "Sold", "buyer": buyer}},
        )
        listing["status"] = "Sold"
        listing["buyer"] = buyer

    return listing


def restore_listing_energy(listing_id, quantity):
    """Compensate a reserved listing if a later trade operation fails."""
    get_marketplace_collection().update_one(
        {"_id": listing_id, "status": {"$in": ["Available", "Sold"]}},
        {
            "$inc": {"energy": quantity},
            "$set": {"status": "Available", "buyer": None},
        },
    )


def save_marketplace_transaction(transaction):
    db["marketplace_transactions"].insert_one(transaction)


def get_marketplace_transactions(start_date=None):
    query = {}
    if start_date:
        query["timestamp"] = {"$gte": str(start_date)}

    return list(
        db["marketplace_transactions"]
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
    )


def get_energy_requests_collection():
    return db["energy_requests"]


def create_energy_request(buyer, requested_energy, maximum_price, message):
    energy_request = {
        "buyer": buyer,
        "requested_energy": requested_energy,
        "maximum_price_per_kwh": maximum_price,
        "message": message,
        "status": "Open",
        "matching_seller": None,
        "created_at": str(datetime.now()),
    }
    result = get_energy_requests_collection().insert_one(energy_request)
    energy_request["request_id"] = str(result.inserted_id)
    energy_request.pop("_id", None)
    return energy_request


def get_energy_requests():
    requests = list(
        get_energy_requests_collection()
        .find({}, {"_id": 1, "buyer": 1, "requested_energy": 1,
                   "maximum_price_per_kwh": 1, "message": 1, "status": 1,
                   "matching_seller": 1, "created_at": 1})
        .sort("created_at", -1)
    )
    for energy_request in requests:
        energy_request["request_id"] = str(energy_request.pop("_id"))
    return requests


def match_requests_for_listing(seller, energy, price):
    query = {
        "status": {"$in": ["Open", "Matched"]},
        "requested_energy": {"$lte": energy},
        "$or": [
            {"maximum_price_per_kwh": None},
            {"maximum_price_per_kwh": {"$gte": price}},
        ],
    }
    result = get_energy_requests_collection().update_many(
        query,
        {"$set": {"status": "Matched", "matching_seller": seller}},
    )
    return result.modified_count


def complete_matched_requests(buyer, seller, quantity):
    return get_energy_requests_collection().update_many(
        {
            "buyer": buyer,
            "matching_seller": seller,
            "status": "Matched",
            "requested_energy": {"$lte": quantity},
        },
        {"$set": {"status": "Completed", "completed_at": str(datetime.now())}},
    ).modified_count


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


def get_inactive_listing_by_seller(seller):

    return get_marketplace_collection().find_one(
        {
            "seller": seller,
            "status": {
                "$ne": "Available"
            }
        }
    )


def count_active_listings():

    return get_marketplace_collection().count_documents(
        {
            "status": "Available"
        }
    )


def count_user_active_listings(username):

    return get_marketplace_collection().count_documents(
        {
            "seller": username,
            "status": "Available"
        }
    )


def _transaction_quantity(transaction):

    return float(
        transaction.get(
            "quantity",
            transaction.get(
                "purchased_amount",
                transaction.get("energy", 0)
            )
        )
    )


def _transaction_total_price(transaction):

    return float(
        transaction.get(
            "total_price",
            transaction.get("total_amount", 0)
        )
    )


def get_marketplace_summary():

    transactions = get_marketplace_transactions()
    prices = [
        float(transaction["price_per_kwh"])
        for transaction in transactions
        if transaction.get("price_per_kwh") is not None
    ]
    total_energy_traded = sum(
        _transaction_quantity(transaction)
        for transaction in transactions
    )
    market_volume = round(
        sum(
            _transaction_total_price(transaction)
            for transaction in transactions
        ),
        2
    )

    return {
        "active_listings": count_active_listings(),
        "completed_trades": len(transactions),
        "total_energy_traded": total_energy_traded,
        "market_volume": market_volume,
        "average_price": round(
            sum(prices) / len(prices),
            2
        ) if prices else 0,
        "highest_price": max(prices) if prices else 0,
        "lowest_price": min(prices) if prices else 0,
    }


def get_user_marketplace_statistics(username):

    transactions = get_marketplace_transactions()
    user_transactions = [
        transaction
        for transaction in transactions
        if transaction.get("buyer") == username
        or transaction.get("seller") == username
    ]

    total_energy_bought = sum(
        _transaction_quantity(transaction)
        for transaction in user_transactions
        if transaction.get("buyer") == username
    )
    total_energy_sold = sum(
        _transaction_quantity(transaction)
        for transaction in user_transactions
        if transaction.get("seller") == username
    )
    total_spending = round(
        sum(
            _transaction_total_price(transaction)
            for transaction in user_transactions
            if transaction.get("buyer") == username
        ),
        2
    )

    from database.mongodb.user_repository import get_user_by_username

    user = get_user_by_username(username) or {}

    return {
        "total_energy_bought": total_energy_bought,
        "total_energy_sold": total_energy_sold,
        "total_revenue": float(user.get("total_revenue", 0)),
        "total_spending": total_spending,
        "active_listings": count_user_active_listings(username),
        "completed_trades": len(user_transactions),
    }
