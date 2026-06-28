import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    import pymongo  # noqa: F401
except ModuleNotFoundError:
    pymongo_stub = ModuleType("pymongo")
    pymongo_stub.MongoClient = MagicMock(return_value=MagicMock())
    pymongo_stub.ReturnDocument = SimpleNamespace(AFTER=True)
    sys.modules["pymongo"] = pymongo_stub

from app.services.dpos_service import (
    begin_new_election,
    cast_delegate_vote,
    elect_active_validator,
    ensure_highest_validator,
    get_dpos_status
)
from blockchain.core.blockchain import Blockchain
from blockchain.dpos.consensus import DPoSConsensus
from blockchain.dpos.delegate import Delegate
from database.mongodb.delegate_repository import activate_validator


class DPoSElectionTests(unittest.TestCase):

    @patch("app.services.dpos_service.elect_active_validator")
    @patch("app.services.dpos_service.count_active_validators", return_value=2)
    @patch("app.services.dpos_service.get_active_validator")
    @patch("app.services.dpos_service.get_top_delegates")
    def test_duplicate_active_flags_trigger_normalized_election(
        self,
        get_top_delegates,
        get_active_validator,
        count_active_validators,
        elect_active_validator
    ):
        highest = {
            "username": "solar-farm",
            "votes": 20
        }
        get_top_delegates.return_value = [highest]
        get_active_validator.return_value = highest
        elect_active_validator.return_value = highest

        active = ensure_highest_validator()

        self.assertEqual(active, highest)
        elect_active_validator.assert_called_once_with()

    @patch("database.mongodb.delegate_repository.get_delegate_collection")
    def test_activation_updates_all_delegates_in_one_operation(
        self,
        get_delegate_collection
    ):
        collection = MagicMock()
        get_delegate_collection.return_value = collection

        activate_validator(
            "solar-farm",
            "2026-06-28 12:00:00"
        )

        collection.update_many.assert_called_once()
        query, pipeline = collection.update_many.call_args.args
        self.assertEqual(query, {})
        self.assertEqual(
            pipeline[0]["$set"]["is_active"],
            {
                "$eq": [
                    "$username",
                    "solar-farm"
                ]
            }
        )

    @patch("app.services.dpos_service.save_validator_change")
    @patch("app.services.dpos_service.activate_validator")
    @patch("app.services.dpos_service.get_active_validator")
    @patch("app.services.dpos_service.get_top_delegates")
    def test_highest_voted_delegate_becomes_active(
        self,
        get_top_delegates,
        get_active_validator,
        activate_validator,
        save_validator_change
    ):
        get_top_delegates.return_value = [
            {
                "username": "solar-farm",
                "votes": 12,
                "role": "SolarFarm"
            }
        ]
        get_active_validator.return_value = {
            "username": "hospital",
            "votes": 8
        }

        elected = elect_active_validator()

        self.assertEqual(
            elected["username"],
            "solar-farm"
        )
        activate_validator.assert_called_once()
        self.assertEqual(
            activate_validator.call_args.args[0],
            "solar-farm"
        )
        save_validator_change.assert_called_once()
        self.assertEqual(
            save_validator_change.call_args.args[:4],
            (
                "hospital",
                "solar-farm",
                8,
                12
            )
        )

    @patch("app.services.dpos_service.save_validator_change")
    @patch("app.services.dpos_service.activate_validator")
    @patch("app.services.dpos_service.get_active_validator")
    @patch("app.services.dpos_service.get_top_delegates")
    def test_unchanged_validator_does_not_duplicate_history(
        self,
        get_top_delegates,
        get_active_validator,
        activate_validator,
        save_validator_change
    ):
        delegate = {
            "username": "university",
            "votes": 15,
            "role": "University"
        }
        get_top_delegates.return_value = [delegate]
        get_active_validator.return_value = delegate

        elect_active_validator()

        activate_validator.assert_called_once()
        save_validator_change.assert_not_called()

    @patch("app.services.dpos_service.has_user_voted", return_value=True)
    @patch("app.services.dpos_service.create_first_election")
    def test_vote_once_per_election(
        self,
        create_first_election,
        has_user_voted
    ):
        success, message, validator = cast_delegate_vote(
            "voter-one",
            "hospital"
        )

        self.assertFalse(success)
        self.assertIn("already voted", message.lower())
        self.assertIsNone(validator)

    @patch("app.services.dpos_service.elect_active_validator")
    @patch("app.services.dpos_service.save_vote")
    @patch("app.services.dpos_service.vote_delegate")
    @patch("app.services.dpos_service.has_user_voted", return_value=False)
    @patch("app.services.dpos_service.create_first_election")
    def test_successful_vote_records_history_and_elects_validator(
        self,
        create_first_election,
        has_user_voted,
        vote_delegate,
        save_vote,
        elect_active_validator
    ):
        vote_delegate.return_value = SimpleNamespace(
            matched_count=1
        )
        elect_active_validator.return_value = {
            "username": "hospital",
            "votes": 10
        }

        success, _, validator = cast_delegate_vote(
            "voter-one",
            "hospital"
        )

        self.assertTrue(success)
        self.assertEqual(
            validator["username"],
            "hospital"
        )
        save_vote.assert_called_once_with(
            "voter-one",
            "hospital"
        )
        elect_active_validator.assert_called_once_with()

    @patch("app.services.dpos_service.get_dpos_status")
    @patch("app.services.dpos_service.reset_delegate_votes")
    @patch("app.services.dpos_service.start_new_election")
    @patch("app.services.dpos_service.get_total_votes", return_value=3)
    @patch("app.services.dpos_service.get_current_leader")
    def test_begin_new_election_closes_saves_winner_and_resets_votes(
        self,
        get_current_leader,
        get_total_votes,
        start_new_election,
        reset_delegate_votes,
        get_dpos_status
    ):
        get_current_leader.return_value = {
            "username": "solar-farm",
            "votes": 5
        }
        get_dpos_status.return_value = {
            "current_election": 2,
            "election_state": "Active"
        }

        status = begin_new_election()

        start_new_election.assert_called_once_with(
            "solar-farm",
            3
        )
        reset_delegate_votes.assert_called_once_with()
        self.assertEqual(status["current_election"], 2)

    @patch("app.services.dpos_service.get_active_validator")
    @patch("app.services.dpos_service.get_all_delegates")
    @patch("app.services.dpos_service.get_current_leader")
    @patch("app.services.dpos_service.count_users", return_value=10)
    @patch("app.services.dpos_service.get_total_votes", return_value=4)
    @patch("app.services.dpos_service.get_current_election")
    @patch("app.services.dpos_service.get_total_delegate_votes", return_value=4)
    def test_dpos_status_includes_election_fields(
        self,
        get_total_delegate_votes,
        get_current_election,
        get_total_votes,
        count_users,
        get_current_leader,
        get_all_delegates,
        get_active_validator
    ):
        get_current_election.return_value = {
            "election_id": 2,
            "status": "Active",
            "started_at": "2026-06-29 10:00:00",
            "ended_at": None
        }
        get_current_leader.return_value = {
            "username": "university",
            "votes": 4
        }
        get_all_delegates.return_value = [
            {"username": "university", "votes": 4}
        ]
        get_active_validator.return_value = {
            "username": "university",
            "votes": 4,
            "elected_at": "2026-06-29 10:05:00"
        }

        status = get_dpos_status()

        self.assertEqual(status["current_election"], 2)
        self.assertEqual(status["election_state"], "Active")
        self.assertEqual(
            status["election_started"],
            "2026-06-29 10:00:00"
        )
        self.assertIsNone(status["election_ended"])
        self.assertEqual(status["total_votes"], 4)
        self.assertEqual(status["participation_percentage"], 40.0)
        self.assertEqual(status["current_leader"], "university")

    @patch(
        "database.mongodb.election_repository.get_vote_history_collection"
    )
    @patch(
        "database.mongodb.election_repository.get_election_collection"
    )
    def test_election_history_persists_winner_and_totals(
        self,
        get_election_collection,
        get_vote_history_collection
    ):
        from database.mongodb.election_repository import (
            close_current_election,
            get_election_history
        )

        elections = MagicMock()
        get_election_collection.return_value = elections

        elections.find_one.return_value = {
            "election_id": 1,
            "status": "Active",
            "started_at": "2026-06-29 09:00:00"
        }

        vote_history = MagicMock()
        get_vote_history_collection.return_value = vote_history
        vote_history.count_documents.return_value = 2

        closed = close_current_election(
            "solar-farm",
            2
        )

        self.assertEqual(closed["winner"], "solar-farm")
        self.assertEqual(closed["total_votes"], 2)
        elections.update_one.assert_called_once()

        update_fields = elections.update_one.call_args.args[1]["$set"]
        self.assertEqual(update_fields["winner"], "solar-farm")
        self.assertEqual(update_fields["total_votes"], 2)
        self.assertEqual(update_fields["status"], "Closed")
        self.assertIsNotNone(update_fields["ended_at"])

        elections.find.return_value.sort.return_value = [
            {
                "election_id": 1,
                "status": "Closed",
                "winner": "solar-farm",
                "total_votes": 2,
                "started_at": "2026-06-29 09:00:00",
                "ended_at": "2026-06-29 12:00:00"
            }
        ]

        history = get_election_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["winner"], "solar-farm")
        self.assertEqual(history[0]["total_votes"], 2)

    @patch(
        "database.mongodb.election_repository.get_vote_history_collection"
    )
    @patch(
        "database.mongodb.election_repository.get_current_election"
    )
    def test_user_can_vote_again_in_next_election(
        self,
        get_current_election,
        get_vote_history_collection
    ):
        from database.mongodb.election_repository import has_user_voted

        vote_history = MagicMock()
        get_vote_history_collection.return_value = vote_history

        get_current_election.return_value = {
            "election_id": 1,
            "status": "Active"
        }
        vote_history.count_documents.return_value = 1

        self.assertTrue(has_user_voted("voter-one"))

        get_current_election.return_value = {
            "election_id": 2,
            "status": "Active"
        }
        vote_history.count_documents.return_value = 0

        self.assertFalse(has_user_voted("voter-one"))

    def test_consensus_selects_highest_votes(self):
        consensus = DPoSConsensus()
        consensus.register_delegate(
            Delegate("hospital", "Hospital", 7)
        )
        consensus.register_delegate(
            Delegate("solar-farm", "SolarFarm", 18)
        )
        consensus.register_delegate(
            Delegate("university", "University", 11)
        )

        selected = consensus.select_delegate()

        self.assertEqual(
            selected.delegate_id,
            "solar-farm"
        )

    @patch(
        "blockchain.core.blockchain.get_current_validator",
        return_value="active-validator"
    )
    @patch(
        "blockchain.core.blockchain.load_chain_from_mongo",
        return_value=[]
    )
    def test_new_blocks_use_active_validator(
        self,
        load_chain,
        get_current_validator
    ):
        blockchain = Blockchain()

        blockchain.add_block(
            {"type": "TEST"},
            validator="hardcoded-validator"
        )

        self.assertEqual(
            blockchain.get_latest_block().data["validator"],
            "active-validator"
        )
        get_current_validator.assert_called_once_with(
            fallback="hardcoded-validator"
        )


if __name__ == "__main__":
    unittest.main()
