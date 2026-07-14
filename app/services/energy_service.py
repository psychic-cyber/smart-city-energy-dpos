from datetime import datetime
from decimal import Decimal, InvalidOperation

from blockchain.core.blockchain import Blockchain
from blockchain.storage.storage_manager import save_blockchain
from blockchain.utils.hash_utils import calculate_hash
from app.services.blockchain_client import (
    marketplace_sell,
    marketplace_buy,
)
from database.mongodb.blockchain_repository import save_block
from database.mongodb.marketplace_repository import (
    complete_matched_requests,
    create_energy_request,
    create_listing,
    get_inactive_listing_by_seller,
    get_listing_by_seller,
    get_marketplace_summary,
    get_user_marketplace_statistics,
    has_active_listing,
    match_requests_for_listing,
    purchase_listing,
    restore_listing_energy,
    save_marketplace_transaction,
)
from database.mongodb.user_repository import (
    adjust_energy_balance,
    adjust_revenue,
    debit_energy_balance,
    debit_revenue,
    get_user_by_username,
    refund_revenue,
)
from database.mongodb.user_transaction_repository import save_user_transaction


def _positive_number(value, field_name, integer=False, optional=False):
    if optional and (value is None or value == ""):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number")
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{field_name} must be greater than zero")
    if integer and number != number.to_integral_value():
        raise ValueError(f"{field_name} must be a whole number")
    return int(number) if integer else float(number)


def calculate_total(quantity, price_per_kwh):
    return round(float(Decimal(str(quantity)) * Decimal(str(price_per_kwh))), 2)


def _build_trade_record(
    buyer,
    seller,
    quantity,
    price_per_kwh,
    total_price,
    timestamp,
    original_listing_amount=None,
    remaining_amount=None,
):
    record = {
        "type": "MARKETPLACE_TRADE",
        "buyer": buyer,
        "seller": seller,
        "quantity": quantity,
        "price_per_kwh": float(price_per_kwh),
        "total_price": total_price,
        "timestamp": timestamp,
        "purchased_amount": quantity,
        "energy": quantity,
        "total_amount": total_price,
    }

    if original_listing_amount is not None:
        record["original_listing_amount"] = original_listing_amount
    if remaining_amount is not None:
        record["remaining_amount"] = remaining_amount

    return record


def _record_blockchain_transaction(transaction):
    transaction = dict(transaction)
    transaction.setdefault("timestamp", str(datetime.now()))
    transaction["hash"] = calculate_hash(str(sorted(transaction.items())))
    blockchain = Blockchain()
    blockchain.add_block(transaction)
    block = blockchain.get_latest_block()
    save_block(block)
    save_blockchain(blockchain.chain)
    return block


def create_marketplace_listing(seller, energy_value, price_value):
    if not seller:
        return False, "Please log in to create a listing", None
    try:
        energy = _positive_number(energy_value, "Energy", integer=True)
        price = _positive_number(price_value, "Price per kWh")
    except ValueError as error:
        return False, str(error), None

    user = get_user_by_username(seller)
    if not user:
        return False, "User not found", None
    if energy > float(user.get("energy_balance", 0)):
        return False, "Insufficient Energy Balance", None
    if has_active_listing(seller):
        return False, "You already have an active listing", None

    try:
        blockchain_listing = marketplace_sell(
            seller,
            energy,
            price
        )
    except Exception as error:
        return False, f"Unable to create on-chain marketplace listing: {error}", None

    listing = create_listing(seller, energy, price, blockchain_listing["listingId"])
    matched_count = match_requests_for_listing(seller, energy, price)
    _record_blockchain_transaction({
        "type": "ENERGY_LISTED",
        "seller": seller,
        "energy": energy,
        "price_per_kwh": price,
    })
    listing.pop("_id", None)
    return True, "Listing Created Successfully", {
        "listing": listing,
        "matched_requests": matched_count,
    }


def purchase_energy(buyer, seller, quantity_value):
    if not buyer:
        return False, "Please log in to buy energy", None
    if not seller:
        return False, "Seller is required", None
    if buyer == seller:
        return False, "You cannot buy your own listing", None
    try:
        quantity = _positive_number(quantity_value, "Quantity", integer=True)
    except ValueError as error:
        return False, str(error), None

    listing = get_listing_by_seller(seller)
    if not listing:
        if get_inactive_listing_by_seller(seller):
            return False, "This listing is no longer active", None
        return False, "This listing is no longer available", None

    available = float(listing.get("energy", 0))
    if quantity > available:
        return False, f"Only {available:g} kWh is currently available", None

    buyer_user = get_user_by_username(buyer)
    seller_user = get_user_by_username(seller)
    if not buyer_user or not seller_user:
        return False, "Buyer or seller account was not found", None

    amount = calculate_total(quantity, listing["price_per_kwh"])
    buyer_balance = float(buyer_user.get("total_revenue", 0))
    if buyer_balance < amount:
        return False, "Insufficient balance to complete this purchase", None

    updated_listing = purchase_listing(seller, quantity, buyer)

    if not updated_listing:
        return False, "The available energy changed. Please try again", None

    try:
        marketplace_buy(
            updated_listing["blockchain_listing_id"],
            buyer
        )
    except Exception as error:
        restore_listing_energy(
            updated_listing["_id"],
            quantity
        )
        return (
            False,
            f"Blockchain purchase failed: {error}",
            None
        )

    original_energy = float(listing.get("original_energy", available))
    remaining = float(updated_listing["energy"])
    seller_adjusted = buyer_adjusted = revenue_adjusted = buyer_paid = False
    try:
        debit_result = debit_energy_balance(seller, quantity)
        if debit_result.modified_count != 1:
            restore_listing_energy(updated_listing["_id"], quantity)
            return False, "Seller no longer has enough energy for this purchase", None
        seller_adjusted = True

        payment_result = debit_revenue(buyer, amount)
        if payment_result.modified_count != 1:
            adjust_energy_balance(seller, quantity)
            restore_listing_energy(updated_listing["_id"], quantity)
            return False, "Insufficient balance to complete this purchase", None
        buyer_paid = True

        adjust_energy_balance(buyer, quantity)
        buyer_adjusted = True
        adjust_revenue(seller, amount)
        revenue_adjusted = True

        timestamp = str(datetime.now())
        transaction = _build_trade_record(
            buyer,
            seller,
            quantity,
            listing["price_per_kwh"],
            amount,
            timestamp,
            original_listing_amount=original_energy,
            remaining_amount=remaining,
        )
        block = _record_blockchain_transaction(transaction)
        transaction["validator"] = block.data["validator"]
        transaction["hash"] = block.hash
        save_marketplace_transaction(transaction)

        save_user_transaction(seller, buyer, quantity, amount)
        save_user_transaction(buyer, seller, quantity, amount)
        complete_matched_requests(buyer, seller, quantity)
    except Exception:
        if revenue_adjusted:
            adjust_revenue(seller, -amount)
        if buyer_paid:
            refund_revenue(buyer, amount)
        if buyer_adjusted:
            adjust_energy_balance(buyer, -quantity)
        if seller_adjusted:
            adjust_energy_balance(seller, quantity)
        restore_listing_energy(updated_listing["_id"], quantity)
        raise

    return True, "Energy Purchased Successfully", {
        "seller": seller,
        "purchased_amount": quantity,
        "remaining_amount": remaining,
        "total_amount": amount,
        "listing_status": updated_listing["status"],
        "block_hash": block.hash,
    }


def submit_energy_request(buyer, energy_value, maximum_price_value, message):
    if not buyer:
        return False, "Please log in to create a request", None
    try:
        requested_energy = _positive_number(
            energy_value, "Requested energy", integer=True
        )
        maximum_price = _positive_number(
            maximum_price_value, "Maximum price per kWh", optional=True
        )
    except ValueError as error:
        return False, str(error), None

    request_data = create_energy_request(
        buyer,
        requested_energy,
        maximum_price,
        (message or "").strip(),
    )
    return True, "Energy request created", request_data


def get_marketplace_summary_data():
    return get_marketplace_summary()


def get_user_marketplace_stats(username):
    if not username:
        return None
    return get_user_marketplace_statistics(username)
