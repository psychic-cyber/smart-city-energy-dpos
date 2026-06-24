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


def mark_user_voted(
    username,
    delegate_username
):

    collection = get_users_collection()

    collection.update_one(
        {
            "username": username
        },
        {
            "$set": {
                "has_voted": True,
                "voted_for": delegate_username
            }
        }
    )

def vote_for_delegate(voter_username, delegate_username):

    collection = get_users_collection()

    collection.update_one(
        {
            "username": voter_username
        },
        {
            "$set": {
                "has_voted": True,
                "voted_for": delegate_username
            }
        }
    )


def has_user_voted(username):

    collection = get_users_collection()

    user = collection.find_one(
        {
            "username": username
        }
    )

    return user.get(
        "has_voted",
        False
    )