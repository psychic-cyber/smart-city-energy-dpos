from datetime import datetime
from decimal import Decimal, InvalidOperation

from blockchain.core.blockchain import Blockchain
from blockchain.storage.storage_manager import save_blockchain
from blockchain.utils.hash_utils import calculate_hash
from database.mongodb.blockchain_repository import save_block
from database.mongodb.marketplace_repository import (
    complete_matched_requests,
    create_energy_request,
    create_listing,
    get_listing_by_seller,
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
    get_user_by_username,
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

    listing = create_listing(seller, energy, price)
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
        return False, "This listing is no longer available", None
    available = float(listing.get("energy", 0))
    if quantity > available:
        return False, f"Only {available:g} kWh is currently available", None
    if not get_user_by_username(buyer) or not get_user_by_username(seller):
        return False, "Buyer or seller account was not found", None

    updated_listing = purchase_listing(seller, quantity, buyer)
    if not updated_listing:
        return False, "The available energy changed. Please try again", None

    amount = calculate_total(quantity, listing["price_per_kwh"])
    original_energy = float(listing.get("original_energy", available))
    remaining = float(updated_listing["energy"])
    seller_adjusted = buyer_adjusted = revenue_adjusted = False
    try:
        debit_result = debit_energy_balance(seller, quantity)
        if debit_result.modified_count != 1:
            restore_listing_energy(updated_listing["_id"], quantity)
            return False, "Seller no longer has enough energy for this purchase", None
        seller_adjusted = True
        adjust_energy_balance(buyer, quantity)
        buyer_adjusted = True
        adjust_revenue(seller, amount)
        revenue_adjusted = True

        timestamp = str(datetime.now())
        transaction = {
            "type": "MARKETPLACE_TRADE",
            "seller": seller,
            "buyer": buyer,
            "original_listing_amount": original_energy,
            "purchased_amount": quantity,
            "remaining_amount": remaining,
            "energy": quantity,
            "price_per_kwh": float(listing["price_per_kwh"]),
            "total_amount": amount,
            "timestamp": timestamp,
        }
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
