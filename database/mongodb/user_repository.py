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


def find_user_by_username(username):

    collection = (
        get_users_collection()
    )

    return collection.find_one(
        {
            "username": username
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