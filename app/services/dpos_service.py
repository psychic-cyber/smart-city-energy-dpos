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
    close_current_election,
    create_first_election,
    create_next_election,
    get_current_election,
    get_latest_closed_election,
    get_next_election_id,
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
    validator = get_active_validator()
    active_election = get_current_election()
    total_users = count_users()

    if active_election:
        display = active_election
        total_votes = get_total_votes()
        leader = get_current_leader()

        if leader and leader.get("votes", 0) > 0:
            current_leader = leader.get("username")
            leader_votes = leader.get("votes", 0)
        else:
            current_leader = None
            leader_votes = 0

        winner = None
        election_state = active_election.get("status")
        can_close_election = True
        can_start_next_election = False
    else:
        display = get_latest_closed_election() or {}
        total_votes = display.get("total_votes", 0)
        winner = display.get("winner")
        current_leader = winner
        leader_votes = display.get("winner_votes", 0)
        election_state = display.get("status")
        can_close_election = False
        can_start_next_election = True

    if total_users > 0:
        participation = round(
            (total_votes / total_users) * 100,
            2
        )
    else:
        participation = 0.0

    if not delegates:
        election_status = "No Delegates"
    elif not validator:
        election_status = "Awaiting Election"
    else:
        election_status = "Validator Elected"

    started_at = display.get(
        "started_at",
        display.get("start_time")
    )
    ended_at = display.get(
        "ended_at",
        display.get("end_time")
    )

    return {
        "current_validator":
            validator.get("username")
            if validator else None,

        "current_validator_votes":
            validator.get("votes", 0)
            if validator else 0,

        "total_delegate_votes":
            get_total_delegate_votes(),

        "last_election_time":
            validator.get("elected_at")
            if validator else None,

        "election_status":
            election_status,

        "current_election":
            display.get("election_id"),

        "election_state":
            election_state,

        "election_started":
            started_at,

        "election_ended":
            ended_at,

        "total_votes":
            total_votes,

        "total_users":
            total_users,

        "participation_percentage":
            participation,

        "current_leader":
            current_leader,

        "leader_votes":
            leader_votes,

        "winner":
            winner,

        "can_close_election":
            can_close_election,

        "can_start_next_election":
            can_start_next_election
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
    winner_votes = 0

    if leader and leader.get("votes", 0) > 0:
        winner = leader["username"]
        winner_votes = leader.get("votes", 0)

    total_votes = get_total_votes()

    start_new_election(
        winner,
        total_votes
    )

    reset_delegate_votes()

    return get_dpos_status()


def close_election():

    if not get_current_election():
        return get_dpos_status()

    leader = get_current_leader()
    winner = None
    winner_votes = 0

    if leader and leader.get("votes", 0) > 0:
        winner = leader["username"]
        winner_votes = leader.get("votes", 0)

    total_votes = get_total_votes()

    close_current_election(
        winner,
        total_votes,
        winner_votes
    )

    reset_delegate_votes()

    return get_dpos_status()


def start_next_election():

    if get_current_election():
        return get_dpos_status()

    create_next_election(
        get_next_election_id()
    )

    return get_dpos_status()
