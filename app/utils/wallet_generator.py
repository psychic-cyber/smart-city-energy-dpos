from eth_account import Account

Account.enable_unaudited_hdwallet_features()


def create_wallet():
    account = Account.create()

    return {
        "address": account.address,
        "private_key": account.key.hex()
    }
