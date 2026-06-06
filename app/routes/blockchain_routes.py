from flask import (
    Blueprint,
    jsonify
)

from database.mongodb.transaction_repository import (
    count_transactions,
    get_transactions,
    get_analytics
)

from database.mongodb.blockchain_repository import (
    count_blocks,
    get_blocks
)

from blockchain.core.blockchain import (
    Blockchain
)


blockchain_bp = Blueprint(
    "blockchain",
    __name__
)


@blockchain_bp.route(
    "/api/stats",
    methods=["GET"]
)
def get_stats():

    blockchain = Blockchain()

    return jsonify(
        {
            "total_transactions":
                count_transactions(),

            "total_blocks":
                count_blocks(),

            "chain_valid":
                blockchain.is_chain_valid()
        }
    )


@blockchain_bp.route(
    "/api/transactions",
    methods=["GET"]
)
def transactions():

    return jsonify(
        get_transactions()
    )

@blockchain_bp.route(
    "/api/blocks",
    methods=["GET"]
)
def blocks():

    return jsonify(
        get_blocks()
    )


@blockchain_bp.route(
    "/api/analytics",
    methods=["GET"]
)
def analytics():

    return jsonify(
        get_analytics()
    )
