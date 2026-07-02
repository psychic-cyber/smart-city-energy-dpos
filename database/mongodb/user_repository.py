from database.mongodb.mongo_manager import (
    db
)


def get_users_collection():

    return db[
        "users"
    ]


def save_user(user):

    collection = (
        get_users_collection()
    )

    collection.insert_one(
        user
    )


def find_user_by_email(email):

    collection = (
        get_users_collection()
    )

    return collection.find_one(
        {
            "email": email
        }
    )


def get_all_users():

    collection = (
        get_users_collection()
    )

    return list(
        collection.find(
            {},
            {
                "_id": 0
            }
        )
    )


def count_users():

    collection = (
        get_users_collection()
    )

    return collection.count_documents(
        {}
    )

def count_admins():

    collection = get_users_collection()

    return collection.count_documents(
        {
            "role": "admin"
        }
    )


def count_regular_users():

    collection = get_users_collection()

    return collection.count_documents(
        {
            "role": "user"
        }
    )


def get_latest_users(limit=5):

    collection = get_users_collection()

    return list(
        collection.find(
            {},
            {"_id": 0}
        )
        .sort("created_at", -1)
        .limit(limit)
    )

def get_user_by_username(username):

    collection = (
        get_users_collection()
    )

    return collection.find_one(
        {
            "username": username
        }
    )

def update_energy_balance(
    username,
    balance
):
    collection = get_users_collection()

    collection.update_one(
        {"username": username},
        {
            "$set": {
                "energy_balance": balance
            }
        }
    )


def adjust_energy_balance(username, amount):
    return get_users_collection().update_one(
        {"username": username},
        {"$inc": {"energy_balance": amount}},
    )


def debit_energy_balance(username, amount):
    return get_users_collection().update_one(
        {"username": username, "energy_balance": {"$gte": amount}},
        {"$inc": {"energy_balance": -amount}},
    )


def update_revenue(
    username,
    revenue
):
    collection = get_users_collection()

    collection.update_one(
        {"username": username},
        {
            "$set": {
                "total_revenue": revenue
            }
        }
    )


def adjust_revenue(username, amount):
    return get_users_collection().update_one(
        {"username": username},
        {"$inc": {"total_revenue": amount}},
    )


def debit_revenue(username, amount):
    return get_users_collection().update_one(
        {
            "username": username,
            "total_revenue": {"$gte": amount},
        },
        {
            "$inc": {
                "total_revenue": -amount,
                "total_spending": amount,
            }
        },
    )


def refund_revenue(username, amount):
    return get_users_collection().update_one(
        {"username": username},
        {
            "$inc": {
                "total_revenue": amount,
                "total_spending": -amount,
            }
        },
    )

def find_user_by_username(
    username
):

    collection = (
        get_users_collection()
    )

    return collection.find_one(
        {
            "username": username
        }
    )

def update_energy_stats(
    username,
    generated,
    consumed,
    balance
):

    collection = (
        get_users_collection()
    )

    collection.update_one(
        {
            "username": username
        },
        {
            "$set": {
                "energy_generated":
                    generated,

                "energy_consumed":
                    consumed,

                "energy_balance":
                    balance
            }
        }
    )

def count_role(role):

    collection = get_users_collection()

    return collection.count_documents(
        {
            "role": role
        }
    )


def delete_user(username):
    """
    Delete a user from the collection by username.

    Args:
        username (str): The username of the user to delete

    Returns:
        dict: The deleted user data if found, None otherwise
    """
    collection = get_users_collection()

    result = collection.find_one_and_delete(
        {
            "username": username
        }
    )

    return result
