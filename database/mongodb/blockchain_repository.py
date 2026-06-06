from database.mongodb.mongo_manager import (
    get_blocks_collection
)


def save_block(block):

    collection = (
        get_blocks_collection()
    )

    collection.insert_one(
        block.to_dict()
    )


def count_blocks():

    collection = (
        get_blocks_collection()
    )

    return collection.count_documents(
        {}
    )
