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
    start_new_election,
    close_current_election,
    get_user_vote
)

from database.mongodb.user_repository import (
    count_users
)

def cast_delegate_vote(voter_username, delegate_username):

    current = get_current_election()

    if not current:
        return (
            False,
            "No active election.",
            None
        )

    if current.get("status") != "Active":
        return (
            False,
            "Election is not active.",
            None
        )

    if has_user_voted(voter_username):
        return (
            False,
            "You have already voted in this election.",
            None
        )

    result = vote_delegate(delegate_username)

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

    return (
        True,
        "Vote Cast Successfully",
        None
    )

def get_dpos_status():

    delegates = get_all_delegates()

    active_validator = get_active_validator()

    current_election = get_current_election()

    leader = get_current_leader()

    total_votes = get_total_votes()

    total_users = count_users()

    participation = 0

    if total_users > 0:
        participation = round(
            (total_votes / total_users) * 100,
            2
        )

    return {

        "current_validator":
            active_validator["username"]
            if active_validator else None,

        "current_validator_votes":
            active_validator.get("votes", 0)
            if active_validator else 0,

        "total_delegate_votes":
            get_total_delegate_votes(),

        "last_election_time":
            active_validator.get("elected_at")
            if active_validator else None,

        "current_election":
            current_election["election_id"]
            if current_election else None,

        "election_state":
            current_election["status"]
            if current_election else "Inactive",

        "election_started":
            current_election.get("started_at")
            if current_election else None,

        "election_ended":
            current_election.get("ended_at")
            if current_election else None,

        "current_leader":
            leader["username"]
            if leader else None,

        "leader_votes":
            leader.get("votes", 0)
            if leader else 0,

        "total_votes":
            total_votes,

        "participation_percentage":
            participation,

        "election_status":
            (
                "Election Running"
                if current_election
                else "Ready To Start"
            )
    }


def get_recent_validator_history(limit=10):

    return get_validator_history(
        limit
    )

def begin_new_election():

    current = get_current_election()

    if current:
        return {
            "success": False,
            "message": "An election is already active."
        }

    reset_delegate_votes()

    start_new_election()

    return {
        "success": True,
        "message": "Election started successfully.",
        "status": get_dpos_status()
    }

def finish_current_election():

    current = get_current_election()

    if not current:
        return {
            "success": False,
            "message": "No active election."
        }

    previous_validator = get_active_validator()

    leader = get_current_leader()

    winner = None
    winner_votes = 0

    if leader and leader.get("votes", 0) > 0:

        winner = leader["username"]
        winner_votes = leader["votes"]

        activate_validator(
            winner,
            str(datetime.now())
        )

        save_validator_change(
            previous_validator["username"] if previous_validator else None,
            winner,
            previous_validator.get("votes", 0) if previous_validator else 0,
            winner_votes,
            str(datetime.now())
        )

    close_current_election(
        winner,
        get_total_votes()
    )

    return {
        "success": True,
        "winner": winner,
        "winner_votes": winner_votes,
        "message": "Election finished successfully.",
        "status": get_dpos_status()
    }

def get_current_validator(fallback="SYSTEM"):

    active = get_active_validator()

    if active:
        return active["username"]

    return fallback