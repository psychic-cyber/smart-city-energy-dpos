from datetime import datetime

from database.mongodb.mongo_manager import db


def get_election_collection():
    return db["elections"]


def get_vote_history_collection():
    return db["vote_history"]


def get_current_election():

    return get_election_collection().find_one(
        {
            "status": "Active"
        },
        {
            "_id": 0
        }
    )


def create_first_election():

    current = get_current_election()

    if current:
        return current

    election = {
        "election_id": 1,
        "status": "Closed",
        "started_at": str(datetime.now()),
        "ended_at": None,
        "winner": None,
        "total_votes": 0
    }

    get_election_collection().insert_one(
        election
    )

    return election


def close_current_election(
    winner=None,
    total_votes=None
):

    current = get_current_election()

    if not current:
        return None

    if total_votes is None:
        total_votes = get_total_votes()

    get_election_collection().update_one(
        {
            "election_id": current["election_id"]
        },
        {
            "$set": {
                "status": "Closed",
                "ended_at": str(datetime.now()),
                "winner": winner,
                "total_votes": total_votes
            }
        }
    )

    closed = dict(current)
    closed["status"] = "Closed"
    closed["ended_at"] = str(datetime.now())
    closed["winner"] = winner
    closed["total_votes"] = total_votes

    return closed


def create_next_election(election_id):

    election = {
        "election_id": election_id,
        "status": "Active",
        "started_at": str(datetime.now()),
        "ended_at": None,
        "winner": None,
        "total_votes": 0
    }

    get_election_collection().insert_one(
        election
    )

    return election


def start_new_election(
    winner=None,
    total_votes=None
):

    current = get_current_election()

    if current:

        if total_votes is None:
            total_votes = get_total_votes()

        close_current_election(
            winner,
            total_votes
        )

    last = get_last_election()

    next_id = 1

    if last:
        next_id = last["election_id"] + 1

    return create_next_election(next_id)


def save_vote(voter, delegate):

    election = get_current_election()

    if not election:
        return

    vote = {
        "election_id": election["election_id"],
        "voter_username": voter,
        "delegate_username": delegate,
        "timestamp": str(datetime.now())
    }

    get_vote_history_collection().insert_one(
        vote
    )


def has_user_voted(voter):

    election = get_current_election()

    if not election:
        return False

    return (
        get_vote_history_collection().count_documents(
            {
                "election_id": election["election_id"],
                "voter_username": voter
            }
        )
        > 0
    )


def get_total_votes():

    election = get_current_election()

    if not election:
        return 0

    return get_vote_history_collection().count_documents(
        {
            "election_id": election["election_id"]
        }
    )


def get_election_history():

    elections = list(
        get_election_collection()
        .find(
            {},
            {
                "_id": 0
            }
        )
        .sort(
            "election_id",
            -1
        )
    )

    for election in elections:
        if not election.get("started_at"):
            election["started_at"] = election.get("start_time")
        if not election.get("ended_at"):
            election["ended_at"] = election.get("end_time")

    return elections


def get_election_by_id(election_id):

    election = get_election_collection().find_one(
        {
            "election_id": election_id
        },
        {
            "_id": 0
        }
    )

    if not election:
        return None

    if not election.get("started_at"):
        election["started_at"] = election.get("start_time")
    if not election.get("ended_at"):
        election["ended_at"] = election.get("end_time")

    return election


def get_user_vote(voter):
    """Get the current election vote for a user"""
    
    election = get_current_election()
    
    if not election:
        return None
    
    vote = get_vote_history_collection().find_one(
        {
            "election_id": election["election_id"],
            "voter_username": voter
        },
        {
            "_id": 0
        }
    )
    
    return vote

def get_last_election():

    return get_election_collection().find_one(
        {},
        {"_id": 0},
        sort=[("election_id", -1)]
    )
