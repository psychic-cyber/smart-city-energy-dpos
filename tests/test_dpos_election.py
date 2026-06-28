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
    cast_delegate_vote,
    elect_active_validator,
    ensure_highest_validator
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

    @patch("app.services.dpos_service.elect_active_validator")
    @patch("app.services.dpos_service.vote_delegate")
    def test_every_successful_vote_runs_election(
        self,
        vote_delegate,
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
            "hospital"
        )

        self.assertTrue(success)
        self.assertEqual(
            validator["username"],
            "hospital"
        )
        elect_active_validator.assert_called_once_with()

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
