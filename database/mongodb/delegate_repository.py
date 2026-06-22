from database.mongodb.mongo_manager import db


def get_delegate_collection():

    return db["delegates"]


def save_delegate(delegate):

    collection = get_delegate_collection()

    existing = collection.find_one(
        {
            "username":
                delegate["username"]
        }
    )

    if existing:
        return

    collection.insert_one(delegate)


def get_all_delegates():

    collection = get_delegate_collection()

    return list(
        collection.find(
            {},
            {"_id": 0}
        )
    )


def vote_delegate(username):

    collection = get_delegate_collection()

    collection.update_one(
        {
            "username": username
        },
        {
            "$inc": {
                "votes": 1
            }
        }
    )


def get_top_delegates(limit=3):

    collection = get_delegate_collection()

    return list(
        collection.find(
            {},
            {"_id": 0}
        )
        .sort("votes", -1)
        .limit(limit)
    )