import os

import requests

NODE_BLOCKCHAIN_BASE_URL = os.environ.get(
    "NODE_BLOCKCHAIN_URL",
    "http://localhost:3001/api/blockchain"
)


class BlockchainClientError(Exception):
    pass


def _url(path: str) -> str:
    return f"{NODE_BLOCKCHAIN_BASE_URL.rstrip('/')}/{path.lstrip('/')}"


def _request(method: str, path: str, **kwargs):
    try:
        response = requests.request(method, _url(path), timeout=10, **kwargs)
    except requests.RequestException as error:
        raise BlockchainClientError(
            f"Unable to reach Node blockchain backend: {error}"
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        raise BlockchainClientError(
            f"Invalid JSON response from Node blockchain backend: {error}"
        ) from error

    if response.status_code >= 400 or not data.get("success", True):
        message = data.get("message") or data.get("error") or response.text
        raise BlockchainClientError(
            f"Node blockchain backend error: {message}"
        )

    return data.get("data", data)


def get_token_info():
    return _request("GET", "/token/info")


def get_token_balance(address: str):
    if not address:
        raise BlockchainClientError("Address is required")
    return _request("GET", f"/token/balance/{address}")


def transfer(to: str, amount):
    if not to or amount is None:
        raise BlockchainClientError("Recipient and amount are required")
    return _request(
        "POST",
        "/token/transfer",
        json={"to": to, "amount": amount},
    )


def marketplace_orders():
    return _request("GET", "/marketplace/orders")


def marketplace_sell(seller: str, energy_amount, price):
    if seller is None:
        raise BlockchainClientError("Seller is required")
    if energy_amount is None:
        raise BlockchainClientError("Energy amount is required")
    if price is None:
        raise BlockchainClientError("Price is required")
    return _request(
        "POST",
        "/marketplace/sell",
        json={
            "seller": seller,
            "energyAmount": energy_amount,
            "price": price,
        },
    )


def marketplace_buy(listing_id, buyer: str):
    if listing_id is None:
        raise BlockchainClientError("Listing id is required")
    if not buyer:
        raise BlockchainClientError("Buyer is required")
    return _request(
        "POST",
        "/marketplace/buy",
        json={"listingId": listing_id, "buyer": buyer},
    )


def get_validators():
    return _request("GET", "/voting/validators")


def get_delegate(address: str):
    if not address:
        raise BlockchainClientError("Address is required")
    return _request("GET", f"/voting/delegates/{address}")


def vote(delegate_id):
    if delegate_id is None:
        raise BlockchainClientError("Delegate id is required")
    return _request(
        "POST",
        "/voting/vote",
        json={"delegate": delegate_id},
    )


def health():
    return _request("GET", "/health")
