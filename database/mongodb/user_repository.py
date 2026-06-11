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