from pymongo import MongoClient


client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client[
    "smart_city_db"
]


def get_blocks_collection():

    return db[
        "blockchain_blocks"
    ]


def get_transactions_collection():

    return db[
        "energy_transactions"
    ]

def get_delegate_collection():

    return db[
        "delegates"
    ]