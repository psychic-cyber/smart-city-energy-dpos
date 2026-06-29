import unittest
import sys
from types import SimpleNamespace
from types import ModuleType
from unittest.mock import MagicMock, patch

try:
    import pymongo  # noqa: F401
except ModuleNotFoundError:
    pymongo_stub = ModuleType("pymongo")
    pymongo_stub.MongoClient = MagicMock(return_value=MagicMock())
    pymongo_stub.ReturnDocument = SimpleNamespace(AFTER=True)
    sys.modules["pymongo"] = pymongo_stub

from app.services.energy_service import (
    calculate_total,
    create_marketplace_listing,
    get_marketplace_summary_data,
    get_user_marketplace_stats,
    purchase_energy,
)


class MarketplaceServiceTests(unittest.TestCase):
    def test_calculate_total_uses_price_per_kwh(self):
        self.assertEqual(calculate_total(75, 15), 1125.0)

    def test_listing_rejects_non_positive_and_decimal_quantities(self):
        for energy in (0, -1, 1.5, "2.2"):
            success, message, result = create_marketplace_listing(
                "seller",
                energy,
                10
            )
            self.assertFalse(success)
            self.assertIsNone(result)
            self.assertTrue(message)

    def test_listing_rejects_non_positive_price(self):
        for price in (0, -5):
            success, message, result = create_marketplace_listing(
                "seller",
                10,
                price
            )
            self.assertFalse(success)
            self.assertIsNone(result)

    @patch("app.services.energy_service.has_active_listing", return_value=False)
    @patch("app.services.energy_service.get_user_by_username")
    def test_listing_rejects_quantity_exceeding_balance(
        self,
        get_user,
        has_active_listing
    ):
        get_user.return_value = {
            "username": "seller",
            "energy_balance": 50
        }

        success, message, result = create_marketplace_listing(
            "seller",
            75,
            10
        )

        self.assertFalse(success)
        self.assertIn("Insufficient Energy Balance", message)
        self.assertIsNone(result)

    @patch("app.services.energy_service._record_blockchain_transaction")
    @patch("app.services.energy_service.match_requests_for_listing", return_value=0)
    @patch("app.services.energy_service.create_listing")
    @patch("app.services.energy_service.has_active_listing", return_value=False)
    @patch("app.services.energy_service.get_user_by_username")
    def test_listing_creates_when_validation_passes(
        self,
        get_user,
        has_active_listing,
        create_listing,
        match_requests,
        record_block
    ):
        get_user.return_value = {
            "username": "seller",
            "energy_balance": 100
        }
        create_listing.return_value = {
            "_id": "listing-id",
            "seller": "seller",
            "energy": 100,
            "price_per_kwh": 12,
            "status": "Available"
        }

        success, message, result = create_marketplace_listing(
            "seller",
            100,
            12
        )

        self.assertTrue(success)
        self.assertEqual(result["listing"]["energy"], 100)
        create_listing.assert_called_once_with("seller", 100, 12.0)
        record_block.assert_called_once()

    def test_purchase_rejects_non_positive_and_decimal_quantities(self):
        for quantity in (0, -1, 1.5, "2.2"):
            success, _, result = purchase_energy("buyer", "seller", quantity)
            self.assertFalse(success)
            self.assertIsNone(result)

    def test_purchase_rejects_self_purchase(self):
        success, message, result = purchase_energy(
            "seller",
            "seller",
            10
        )

        self.assertFalse(success)
        self.assertIn("own listing", message.lower())
        self.assertIsNone(result)

    @patch("app.services.energy_service.get_inactive_listing_by_seller")
    @patch("app.services.energy_service.get_listing_by_seller", return_value=None)
    def test_purchase_rejects_missing_listing(
        self,
        get_listing,
        get_inactive_listing
    ):
        get_inactive_listing.return_value = None

        success, message, result = purchase_energy("buyer", "seller", 10)

        self.assertFalse(success)
        self.assertIn("no longer available", message.lower())
        self.assertIsNone(result)

    @patch("app.services.energy_service.get_inactive_listing_by_seller")
    @patch("app.services.energy_service.get_listing_by_seller", return_value=None)
    def test_purchase_rejects_inactive_listing(
        self,
        get_listing,
        get_inactive_listing
    ):
        get_inactive_listing.return_value = {
            "seller": "seller",
            "status": "Sold"
        }

        success, message, result = purchase_energy("buyer", "seller", 10)

        self.assertFalse(success)
        self.assertIn("no longer active", message.lower())
        self.assertIsNone(result)

    @patch("app.services.energy_service.get_listing_by_seller")
    def test_purchase_rejects_more_than_available(self, get_listing):
        get_listing.return_value = {"energy": 10, "price_per_kwh": 15}
        success, message, _ = purchase_energy("buyer", "seller", 11)
        self.assertFalse(success)
        self.assertIn("10 kWh", message)

    @patch("app.services.energy_service.get_user_by_username")
    @patch("app.services.energy_service.get_listing_by_seller")
    def test_purchase_rejects_insufficient_buyer_balance(
        self,
        get_listing,
        get_user
    ):
        get_listing.return_value = {
            "seller": "seller",
            "energy": 100,
            "price_per_kwh": 15
        }
        get_user.side_effect = lambda username: {
            "buyer": {
                "username": "buyer",
                "total_revenue": 100
            },
            "seller": {
                "username": "seller",
                "energy_balance": 100
            }
        }[username]

        success, message, result = purchase_energy("buyer", "seller", 10)

        self.assertFalse(success)
        self.assertIn("Insufficient balance", message)
        self.assertIsNone(result)

    @patch("app.services.energy_service.complete_matched_requests")
    @patch("app.services.energy_service.save_user_transaction")
    @patch("app.services.energy_service.save_marketplace_transaction")
    @patch("app.services.energy_service._record_blockchain_transaction")
    @patch("app.services.energy_service.adjust_revenue")
    @patch("app.services.energy_service.debit_revenue")
    @patch("app.services.energy_service.adjust_energy_balance")
    @patch("app.services.energy_service.debit_energy_balance")
    @patch("app.services.energy_service.purchase_listing")
    @patch("app.services.energy_service.get_user_by_username")
    @patch("app.services.energy_service.get_listing_by_seller")
    def test_partial_purchase_updates_balances_and_transaction(
        self,
        get_listing,
        get_user,
        reserve_listing,
        debit_balance,
        adjust_balance,
        debit_revenue,
        adjust_revenue,
        record_block,
        save_transaction,
        save_user_transaction,
        complete_requests,
    ):
        get_listing.return_value = {
            "seller": "seller",
            "energy": 200,
            "original_energy": 200,
            "price_per_kwh": 15,
        }
        get_user.side_effect = lambda username: {
            "buyer": {
                "username": "buyer",
                "total_revenue": 5000
            },
            "seller": {
                "username": "seller",
                "energy_balance": 200
            }
        }[username]
        reserve_listing.return_value = {
            "_id": "listing-id",
            "energy": 125,
            "status": "Available"
        }
        debit_balance.return_value = SimpleNamespace(modified_count=1)
        debit_revenue.return_value = SimpleNamespace(modified_count=1)
        record_block.return_value = SimpleNamespace(
            data={"validator": "validator-one"}, hash="block-hash"
        )

        success, _, result = purchase_energy("buyer", "seller", 75)

        self.assertTrue(success)
        self.assertEqual(result["remaining_amount"], 125)
        self.assertEqual(result["total_amount"], 1125.0)
        self.assertEqual(result["listing_status"], "Available")
        debit_balance.assert_called_once_with("seller", 75)
        debit_revenue.assert_called_once_with("buyer", 1125.0)
        adjust_balance.assert_called_once_with("buyer", 75)
        adjust_revenue.assert_called_once_with("seller", 1125.0)
        transaction = save_transaction.call_args.args[0]
        self.assertEqual(transaction["buyer"], "buyer")
        self.assertEqual(transaction["seller"], "seller")
        self.assertEqual(transaction["quantity"], 75)
        self.assertEqual(transaction["price_per_kwh"], 15)
        self.assertEqual(transaction["total_price"], 1125.0)
        self.assertEqual(transaction["original_listing_amount"], 200)
        self.assertEqual(transaction["remaining_amount"], 125)
        self.assertEqual(transaction["validator"], "validator-one")
        self.assertEqual(transaction["hash"], "block-hash")
        self.assertIsNotNone(transaction["timestamp"])
        self.assertEqual(save_user_transaction.call_count, 2)
        complete_requests.assert_called_once_with("buyer", "seller", 75)

    @patch("app.services.energy_service.complete_matched_requests")
    @patch("app.services.energy_service.save_user_transaction")
    @patch("app.services.energy_service.save_marketplace_transaction")
    @patch("app.services.energy_service._record_blockchain_transaction")
    @patch("app.services.energy_service.adjust_revenue")
    @patch("app.services.energy_service.debit_revenue")
    @patch("app.services.energy_service.adjust_energy_balance")
    @patch("app.services.energy_service.debit_energy_balance")
    @patch("app.services.energy_service.purchase_listing")
    @patch("app.services.energy_service.get_user_by_username")
    @patch("app.services.energy_service.get_listing_by_seller")
    def test_complete_purchase_marks_listing_sold(
        self,
        get_listing,
        get_user,
        reserve_listing,
        debit_balance,
        adjust_balance,
        debit_revenue,
        adjust_revenue,
        record_block,
        save_transaction,
        save_user_transaction,
        complete_requests,
    ):
        get_listing.return_value = {
            "seller": "seller",
            "energy": 50,
            "original_energy": 50,
            "price_per_kwh": 10,
        }
        get_user.side_effect = lambda username: {
            "buyer": {
                "username": "buyer",
                "total_revenue": 1000
            },
            "seller": {
                "username": "seller",
                "energy_balance": 50
            }
        }[username]
        reserve_listing.return_value = {
            "_id": "listing-id",
            "energy": 0,
            "status": "Sold"
        }
        debit_balance.return_value = SimpleNamespace(modified_count=1)
        debit_revenue.return_value = SimpleNamespace(modified_count=1)
        record_block.return_value = SimpleNamespace(
            data={"validator": "validator-one"}, hash="sold-hash"
        )

        success, _, result = purchase_energy("buyer", "seller", 50)

        self.assertTrue(success)
        self.assertEqual(result["remaining_amount"], 0)
        self.assertEqual(result["listing_status"], "Sold")
        transaction = save_transaction.call_args.args[0]
        self.assertEqual(transaction["remaining_amount"], 0)

    @patch("app.services.energy_service.restore_listing_energy")
    @patch("app.services.energy_service.refund_revenue")
    @patch("app.services.energy_service.adjust_revenue")
    @patch("app.services.energy_service.adjust_energy_balance")
    @patch("app.services.energy_service.debit_revenue")
    @patch("app.services.energy_service.debit_energy_balance")
    @patch("app.services.energy_service._record_blockchain_transaction")
    @patch("app.services.energy_service.purchase_listing")
    @patch("app.services.energy_service.get_user_by_username")
    @patch("app.services.energy_service.get_listing_by_seller")
    def test_blockchain_failure_rolls_back_marketplace_changes(
        self,
        get_listing,
        get_user,
        reserve_listing,
        record_block,
        debit_balance,
        debit_revenue,
        adjust_balance,
        adjust_revenue,
        refund_revenue,
        restore_listing,
    ):
        get_listing.return_value = {
            "seller": "seller",
            "energy": 100,
            "original_energy": 100,
            "price_per_kwh": 10,
        }
        get_user.side_effect = lambda username: {
            "buyer": {
                "username": "buyer",
                "total_revenue": 1000
            },
            "seller": {
                "username": "seller",
                "energy_balance": 100
            }
        }[username]
        reserve_listing.return_value = {
            "_id": "listing-id",
            "energy": 70,
            "status": "Available"
        }
        debit_balance.return_value = SimpleNamespace(modified_count=1)
        debit_revenue.return_value = SimpleNamespace(modified_count=1)
        record_block.side_effect = RuntimeError("blockchain unavailable")

        with self.assertRaises(RuntimeError):
            purchase_energy("buyer", "seller", 30)

        adjust_revenue.assert_any_call("seller", 300.0)
        adjust_revenue.assert_any_call("seller", -300.0)
        refund_revenue.assert_called_once_with("buyer", 300.0)
        adjust_balance.assert_any_call("buyer", 30)
        adjust_balance.assert_any_call("buyer", -30)
        adjust_balance.assert_any_call("seller", 30)
        restore_listing.assert_called_once_with("listing-id", 30)

    @patch("app.services.energy_service.get_marketplace_summary")
    def test_marketplace_summary_api_data(self, get_summary):
        get_summary.return_value = {
            "active_listings": 3,
            "completed_trades": 8,
            "total_energy_traded": 420,
            "market_volume": 6300,
            "average_price": 15,
            "highest_price": 20,
            "lowest_price": 10,
        }

        summary = get_marketplace_summary_data()

        self.assertEqual(summary["active_listings"], 3)
        self.assertEqual(summary["completed_trades"], 8)
        self.assertEqual(summary["total_energy_traded"], 420)
        self.assertEqual(summary["market_volume"], 6300)
        self.assertEqual(summary["average_price"], 15)

    @patch("app.services.energy_service.get_user_marketplace_statistics")
    def test_user_marketplace_statistics(self, get_statistics):
        get_statistics.return_value = {
            "total_energy_bought": 120,
            "total_energy_sold": 80,
            "total_revenue": 2400,
            "total_spending": 1800,
            "active_listings": 1,
            "completed_trades": 5,
        }

        stats = get_user_marketplace_stats("buyer")

        self.assertEqual(stats["total_energy_bought"], 120)
        self.assertEqual(stats["total_energy_sold"], 80)
        self.assertEqual(stats["total_revenue"], 2400)
        self.assertEqual(stats["total_spending"], 1800)
        self.assertEqual(stats["active_listings"], 1)
        self.assertEqual(stats["completed_trades"], 5)

    @patch(
        "database.mongodb.user_repository.get_user_by_username"
    )
    @patch(
        "database.mongodb.marketplace_repository.get_marketplace_transactions"
    )
    @patch(
        "database.mongodb.marketplace_repository.count_user_active_listings",
        return_value=1
    )
    def test_repository_user_statistics_from_transaction_history(
        self,
        count_active_listings,
        get_transactions,
        get_user
    ):
        from database.mongodb.marketplace_repository import (
            get_user_marketplace_statistics
        )

        get_transactions.return_value = [
            {
                "buyer": "buyer",
                "seller": "seller",
                "quantity": 30,
                "price_per_kwh": 10,
                "total_price": 300,
                "timestamp": "2026-06-29 10:00:00"
            },
            {
                "buyer": "other",
                "seller": "buyer",
                "quantity": 20,
                "price_per_kwh": 12,
                "total_price": 240,
                "timestamp": "2026-06-29 11:00:00"
            }
        ]
        get_user.return_value = {
            "username": "buyer",
            "total_revenue": 500
        }

        stats = get_user_marketplace_statistics("buyer")

        self.assertEqual(stats["total_energy_bought"], 30)
        self.assertEqual(stats["total_energy_sold"], 20)
        self.assertEqual(stats["total_spending"], 300)
        self.assertEqual(stats["total_revenue"], 500)
        self.assertEqual(stats["completed_trades"], 2)
        self.assertEqual(stats["active_listings"], 1)


if __name__ == "__main__":
    unittest.main()
