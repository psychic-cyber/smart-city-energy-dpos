from datetime import datetime

from database.mongodb.delegate_repository import (
    activate_validator,
    count_active_validators,
    get_active_validator,
    get_all_delegates,
    get_top_delegates,
    get_total_delegate_votes,
    get_validator_history,
    save_validator_change,
    vote_delegate
)


def elect_active_validator():

    delegates = get_top_delegates(1)

    if not delegates:
        return None

    elected = delegates[0]
    previous = get_active_validator()
    election_time = str(
        datetime.now()
    )

    activate_validator(
        elected["username"],
        election_time
    )

    if (
        not previous
        or previous.get("username")
        != elected["username"]
    ):
        save_validator_change(
            previous.get("username")
            if previous else None,
            elected["username"],
            previous.get("votes", 0)
            if previous else 0,
            elected.get("votes", 0),
            election_time
        )

    elected["is_active"] = True
    elected["elected_at"] = election_time

    return elected


def cast_delegate_vote(username):

    result = vote_delegate(
        username
    )

    if result.matched_count == 0:
        return (
            False,
            "Delegate not found",
            None
        )

    elected = elect_active_validator()

    return (
        True,
        "Vote Cast Successfully",
        elected
    )


def get_current_validator(fallback="SYSTEM"):

    active = ensure_highest_validator()

    return (
        active["username"]
        if active
        else fallback
    )


def get_dpos_status():

    delegates = get_all_delegates()
    active = ensure_highest_validator()

    total_votes = get_total_delegate_votes()

    if not delegates:
        election_status = "No Delegates"
    elif not active:
        election_status = "Awaiting Election"
    else:
        election_status = "Validator Elected"

    return {
        "current_validator":
            active.get("username")
            if active else None,
        "current_validator_votes":
            active.get("votes", 0)
            if active else 0,
        "total_delegate_votes": total_votes,
        "last_election_time":
            active.get("elected_at")
            if active else None,
        "election_status": election_status
    }


def get_recent_validator_history(limit=10):

    return get_validator_history(
        limit
    )


def ensure_highest_validator():

    delegates = get_top_delegates(1)

    if not delegates:
        return None

    highest = delegates[0]
    active = get_active_validator()

    if (
        not active
        or count_active_validators() != 1
        or active.get("username")
        != highest["username"]
    ):
        return elect_active_validator()

    return active
