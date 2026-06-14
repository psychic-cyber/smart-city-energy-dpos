from database.mongodb.mongo_manager import (
    get_blocks_collection
)


def save_block(block):

    collection = (
        get_blocks_collection()
    )

    existing_block = (
        collection.find_one(
            {
                "hash": block.hash
            }
        )
    )

    if existing_block:

        return

    collection.insert_one(
        block.to_dict()
    )


def save_chain(chain):

    for block in chain:

        save_block(
            block
        )


def count_blocks():

    collection = (
        get_blocks_collection()
    )

    return collection.count_documents(
        {}
    )

def get_blocks(limit=20):

    collection = (
        get_blocks_collection()
    )

    blocks = list(
        collection.find(
            {},
            {"_id": 0}
        )
        .sort("index", 1)
        .limit(limit)
    )

    return blocks

def count_blocks():

    collection = (
        get_blocks_collection()
    )

    return collection.count_documents(
        {}
    )

def get_latest_block():

    collection = get_blocks_collection()

    return collection.find_one(
        {},
        sort=[("index", -1)]
    )

def block_index_exists(index):

    collection = (
        get_blocks_collection()
    )

    return (
        collection.find_one(
            {
                "index": index
            }
        )
        is not None
    )