import hashlib


def calculate_hash(data):

    return hashlib.sha256(
        str(data).encode()
    ).hexdigest()
