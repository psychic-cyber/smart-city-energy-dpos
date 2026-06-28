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

from app.services.energy_service import calculate_total, purchase_energy


class MarketplaceServiceTests(unittest.TestCase):
    def test_calculate_total_uses_price_per_kwh(self):
        self.assertEqual(calculate_total(75, 15), 1125.0)

    def test_purchase_rejects_non_positive_and_decimal_quantities(self):
        for quantity in (0, -1, 1.5, "2.2"):
            success, _, result = purchase_energy("buyer", "seller", quantity)
            self.assertFalse(success)
            self.assertIsNone(result)

    @patch("app.services.energy_service.get_listing_by_seller")
    def test_purchase_rejects_more_than_available(self, get_listing):
        get_listing.return_value = {"energy": 10, "price_per_kwh": 15}
        success, message, _ = purchase_energy("buyer", "seller", 11)
        self.assertFalse(success)
        self.assertIn("10 kWh", message)

    @patch("app.services.energy_service.complete_matched_requests")
    @patch("app.services.energy_service.save_user_transaction")
    @patch("app.services.energy_service.save_marketplace_transaction")
    @patch("app.services.energy_service._record_blockchain_transaction")
    @patch("app.services.energy_service.adjust_revenue")
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
        get_user.return_value = {"username": "user"}
        reserve_listing.return_value = {"energy": 125, "status": "Available"}
        debit_balance.return_value = SimpleNamespace(modified_count=1)
        record_block.return_value = SimpleNamespace(
            data={"validator": "validator-one"}, hash="block-hash"
        )

        success, _, result = purchase_energy("buyer", "seller", 75)

        self.assertTrue(success)
        self.assertEqual(result["remaining_amount"], 125)
        self.assertEqual(result["total_amount"], 1125.0)
        debit_balance.assert_called_once_with("seller", 75)
        adjust_balance.assert_called_once_with("buyer", 75)
        adjust_revenue.assert_called_once_with("seller", 1125.0)
        transaction = save_transaction.call_args.args[0]
        self.assertEqual(transaction["original_listing_amount"], 200)
        self.assertEqual(transaction["purchased_amount"], 75)
        self.assertEqual(transaction["remaining_amount"], 125)
        self.assertEqual(transaction["validator"], "validator-one")
        self.assertEqual(transaction["hash"], "block-hash")
        self.assertEqual(save_user_transaction.call_count, 2)
        complete_requests.assert_called_once_with("buyer", "seller", 75)


if __name__ == "__main__":
    unittest.main()
