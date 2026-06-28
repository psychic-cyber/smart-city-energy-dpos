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

    delegate.setdefault("votes", 0)
    delegate.setdefault("is_active", False)

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

    return collection.update_one(
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
        .sort([
            ("votes", -1),
            ("username", 1)
        ])
        .limit(limit)
    )


def get_active_validator():

    return get_delegate_collection().find_one(
        {
            "is_active": True
        },
        {
            "_id": 0
        }
    )


def count_active_validators():

    return get_delegate_collection().count_documents(
        {
            "is_active": True
        }
    )


def activate_validator(username, election_time):

    username_match = {
        "$eq": [
            "$username",
            username
        ]
    }

    return get_delegate_collection().update_many(
        {},
        [
            {
                "$set": {
                    "is_active": username_match,
                    "elected_at": {
                        "$cond": [
                            username_match,
                            election_time,
                            "$elected_at"
                        ]
                    }
                }
            }
        ]
    )


def get_validator_history_collection():

    return db[
        "validator_history"
    ]


def save_validator_change(
    previous_validator,
    new_validator,
    previous_votes,
    new_votes,
    election_time
):

    history = {
        "previous_validator": previous_validator,
        "new_validator": new_validator,
        "previous_votes": previous_votes,
        "new_votes": new_votes,
        "election_time": election_time
    }

    get_validator_history_collection().insert_one(
        history
    )

    return history


def get_validator_history(limit=10):

    return list(
        get_validator_history_collection()
        .find(
            {},
            {
                "_id": 0
            }
        )
        .sort(
            "election_time",
            -1
        )
        .limit(limit)
    )


def get_total_delegate_votes():

    result = list(
        get_delegate_collection().aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "total": {
                            "$sum": "$votes"
                        }
                    }
                }
            ]
        )
    )

    return result[0]["total"] if result else 0
