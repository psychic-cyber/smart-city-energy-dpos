from flask import (
    Blueprint,
    jsonify,
    session
)

from database.mongodb.transaction_repository import (
    count_transactions,
    get_transactions,
    get_analytics,
    get_district_analytics
)

from database.mongodb.blockchain_repository import (
    count_blocks,
    get_blocks
)

from blockchain.core.blockchain import (
    Blockchain
)

from database.mongodb.user_repository import (
    get_all_users,
    count_users,
    count_admins,
    count_regular_users,
    get_latest_users,
    get_user_by_username,
    count_role,
)

from database.mongodb.user_transaction_repository import (
    get_all_user_transactions
)

from database.mongodb.mongo_manager import (
    db
)


blockchain_bp = Blueprint(
    "blockchain",
    __name__
)


@blockchain_bp.route(
    "/api/stats",
    methods=["GET"]
)
# def get_stats():

#     blockchain = Blockchain()

#     return jsonify(
#         {
#             "total_transactions":
#                 count_transactions(),

#             "total_blocks":
#                 count_blocks(),

#             "chain_valid":
#                 blockchain.is_chain_valid()
#         }
#     )

def get_stats():

    blockchain = Blockchain()

    return jsonify(
        {
            "total_transactions":
                len(
                    get_all_user_transactions()
                ),

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
        get_all_user_transactions()
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

@blockchain_bp.route(
    "/api/districts",
    methods=["GET"]
)
def districts():

    users = get_all_users()

    role_energy = {}

    for user in users:

        role = user.get(
            "role",
            "Unknown"
        )

        consumed = float(
            user.get(
                "energy_consumed",
                0
            )
        )

        role_energy[role] = (
            role_energy.get(
                role,
                0
            )
            + consumed
        )

    return jsonify(
        [
            {
                "_id": role,
                "energy": energy
            }
            for role, energy
            in role_energy.items()
        ]
    )

@blockchain_bp.route(
    "/api/users",
    methods=["GET"]
)
def users():

    return jsonify(
        get_all_users()
    )


@blockchain_bp.route(
    "/api/users/stats",
    methods=["GET"]
)
def users_stats():

    return jsonify(
        {
            "total_users":
                count_users(),

            "admins":
                count_role("Admin"),

            "houses":
                count_role("House"),

            "hospitals":
                count_role("Hospital"),

            "universities":
                count_role("University"),

            "restaurants":
                count_role("Restaurant"),

            "offices":
                count_role("Office"),

            "factories":
                count_role("Factory"),

            "solarfarms":
                count_role("SolarFarm")
        }
    )


@blockchain_bp.route(
    "/api/users/latest",
    methods=["GET"]
)
def latest_users():

    return jsonify(
        get_latest_users()
    )

# @blockchain_bp.route(
#     "/api/user/dashboard",
#     methods=["GET"]
# )
# def user_dashboard_data():

#     username = session.get(
#         "username"
#     )

#     user = (
#         get_user_by_username(
#             username
#         )
#     )

#     if not user:

#         return jsonify(
#             {
#                 "error":
#                     "User not found"
#             }
#         )

#     generated = (
#         len(username)
#         * 75
#     )

#     consumed = (
#         len(username)
#         * 55
#     )

#     balance = (
#         generated
#         -
#         consumed
#     )

#     revenue = (
#         balance
#         * 25
#     )

#     return jsonify(
#         {
#             "username":
#                 username,

#             "energy_generated":
#                 generated,

#             "energy_consumed":
#                 consumed,

#             "energy_balance":
#                 balance,

#             "revenue":
#                 revenue
#         }
#     )