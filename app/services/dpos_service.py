from datetime import datetime

from database.mongodb.delegate_repository import (
    activate_validator,
    count_active_validators,
    get_active_validator,
    get_all_delegates,
    get_current_leader,
    get_top_delegates,
    get_total_delegate_votes,
    get_validator_history,
    reset_delegate_votes,
    save_validator_change,
    vote_delegate
)

from database.mongodb.election_repository import (
    create_first_election,
    get_current_election,
    get_total_votes,
    has_user_voted,
    save_vote,
    start_new_election
)

from database.mongodb.user_repository import (
    count_users
)


def elect_active_validator():

    delegates = get_top_delegates(1)

    if not delegates:
        return None

    elected = delegates[0]

    if elected.get("votes", 0) <= 0:
        return None

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


def cast_delegate_vote(
    voter_username,
    delegate_username
):

    create_first_election()

    if has_user_voted(voter_username):

        return (
            False,
            "You have already voted in this election.",
            None
        )

    result = vote_delegate(
        delegate_username
    )

    if result.matched_count == 0:

        return (
            False,
            "Delegate not found",
            None
        )

    save_vote(
        voter_username,
        delegate_username
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
    active = get_active_validator()
    current = get_current_election() or {}
    total_votes = get_total_votes()
    total_users = count_users()
    leader = get_current_leader()

    if total_users > 0:
        participation = round(
            (total_votes / total_users) * 100,
            2
        )
    else:
        participation = 0.0

    if not delegates:
        election_status = "No Delegates"
    elif not active:
        election_status = "Awaiting Election"
    else:
        election_status = "Validator Elected"

    started_at = current.get(
        "started_at",
        current.get("start_time")
    )
    ended_at = current.get(
        "ended_at",
        current.get("end_time")
    )

    return {
        "current_validator":
            active.get("username")
            if active else None,

        "current_validator_votes":
            active.get("votes", 0)
            if active else 0,

        "total_delegate_votes":
            get_total_delegate_votes(),

        "last_election_time":
            active.get("elected_at")
            if active else None,

        "election_status":
            election_status,

        "current_election":
            current.get("election_id"),

        "election_state":
            current.get("status"),

        "election_started":
            started_at,

        "election_ended":
            ended_at,

        "total_votes":
            total_votes,

        "participation_percentage":
            participation,

        "current_leader":
            leader.get("username")
            if leader and leader.get("votes", 0) > 0
            else None
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

    if highest.get("votes", 0) <= 0:
        return None

    active = get_active_validator()

    if (
        not active
        or count_active_validators() != 1
        or active.get("username")
        != highest["username"]
    ):
        return elect_active_validator()

    return active


def begin_new_election():

    leader = get_current_leader()
    winner = None

    if leader and leader.get("votes", 0) > 0:
        winner = leader["username"]

    total_votes = get_total_votes()

    start_new_election(
        winner,
        total_votes
    )

    reset_delegate_votes()

    return get_dpos_status()
