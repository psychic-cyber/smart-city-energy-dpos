from flask import (
    Blueprint,
    jsonify,
    session,
    send_file,
    request
)

from os.path import abspath

from app.utils.pdf_report_generator import (
    generate_report_pdf
)

from database.mongodb.transaction_repository import (
    count_transactions,
    get_transactions,
    get_analytics,
    get_district_analytics
)

from database.mongodb.blockchain_repository import (
    count_blocks,
    get_blocks,
    save_block
)

from blockchain.storage.storage_manager import (
    save_blockchain
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
    count_role
)

from database.mongodb.user_transaction_repository import (
    get_all_user_transactions
)

from database.mongodb.mongo_manager import (
    db
)

from ai.ai_engine import (
    generate_ai_insight
)

from app.services.ai_service import (
    get_monitoring_data,
    process_monitoring_blockchain_alert,
)

from database.mongodb.report_repository import (
    get_daily_report,
    get_weekly_report,
    get_monthly_report
)

from database.mongodb.delegate_repository import (
    get_all_delegates,
    get_top_delegates
)

from database.mongodb.election_repository import (
    has_user_voted
)

from app.services.dpos_service import (
    begin_new_election,
    cast_delegate_vote,
    get_dpos_status,
    get_recent_validator_history,
    finish_current_election
)

from app.services.blockchain_client import (
    get_token_info,
    get_token_balance,
    transfer,
    marketplace_orders,
    marketplace_sell,
    marketplace_buy,
    get_validators,
    get_delegate,
    vote as vote_on_chain,
)

from database.mongodb.ai_alert_repository import (
    get_all_ai_alerts
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
    "/api/ai-monitoring",
    methods=["GET"]
)
def ai_monitoring():

    data = get_monitoring_data()

    process_monitoring_blockchain_alert(data)

    return jsonify(
        data
    )

@blockchain_bp.route(
    "/api/ai-insights",
    methods=["GET"]
)
def ai_insights():

    analytics_data = get_analytics()

    anomaly_rate = (
        analytics_data.get(
            "anomaly_percentage",
            0
        )
    )

    efficiency = (
        analytics_data.get(
            "energy_efficiency",
            0
        )
    )

    ai_result = generate_ai_insight(
        anomaly_rate,
        efficiency
    )

    return jsonify(
        ai_result
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

@blockchain_bp.route(
    "/api/report/daily"
)
def daily_report():

    return jsonify(
        get_daily_report()
    )


@blockchain_bp.route(
    "/api/report/weekly"
)
def weekly_report():

    return jsonify(
        get_weekly_report()
    )


@blockchain_bp.route(
    "/api/report/monthly"
)
def monthly_report():

    return jsonify(
        get_monthly_report()
    )

@blockchain_bp.route(
    "/api/report/pdf/daily"
)
def daily_report_pdf():

    report = get_daily_report()

    filename = "daily_report.pdf"

    generate_report_pdf(
        filename,
        "Daily Smart City Energy Report",
        report
    )

    return send_file(
        abspath(filename),
        as_attachment=True
    )

@blockchain_bp.route(
    "/api/report/pdf/weekly"
)
def weekly_report_pdf():

    report = get_weekly_report()

    filename = "weekly_report.pdf"

    generate_report_pdf(
        filename,
        "Weekly Smart City Energy Report",
        report
    )

    return send_file(
        abspath(filename),
        as_attachment=True
    )

@blockchain_bp.route(
    "/api/report/pdf/monthly"
)
def monthly_report_pdf():

    report = (
        get_monthly_report()
    )

    filename = (
        "monthly_report.pdf"
    )

    generate_report_pdf(
        filename,
        "Monthly Smart City Energy Report",
        report
    )

    return send_file(
        abspath(filename),
        as_attachment=True
    )

@blockchain_bp.route(
    "/api/delegates"
)
def delegates():

    return jsonify(
        get_all_delegates()
    )


def _find_validator_by_name(name):
    if not name:
        return None

    validators = get_validators()

    for validator in validators:
        validator_name = validator.get("name")
        if validator_name and validator_name.strip().lower() == name.strip().lower():
            return validator

    return None


@blockchain_bp.route(
    "/api/vote",
    methods=["POST"]
)
def vote_delegate_route():

    voter = session.get("username")

    if not voter:
        return jsonify(
            {
                "success": False,
                "message": "Login Required"
            }
        ), 401

    data = request.get_json(silent=True) or {}
    delegate_name = data.get("delegate")

    if not delegate_name:
        return jsonify(
            {
                "success": False,
                "message": "Delegate is required"
            }
        ), 400

    if has_user_voted(voter):
        return jsonify(
            {
                "success": False,
                "message": "You have already voted in this election."
            }
        ), 400

    validator = _find_validator_by_name(delegate_name)

    if not validator:
        return jsonify(
            {
                "success": False,
                "message": "Delegate not found"
            }
        ), 404

    try:
        blockchain_vote = vote_on_chain(
            voter,
            validator.get("id")
        )
    except Exception as error:
        return jsonify(
            {
                "success": False,
                "message": str(error)
            }
        ), 400

    success, message, active_validator = cast_delegate_vote(
        voter,
        delegate_name
    )

    if not success:
        return jsonify(
            {
                "success": False,
                "message": message
            }
        ), 400

    response = {
        "success": True,
        "message": message,
        "active_validator":
            active_validator["username"]
            if active_validator else None,
        "blockchain_vote": blockchain_vote
    }

    return jsonify(response)


@blockchain_bp.route(
    "/api/delegates/top"
)
def top_delegates():

    return jsonify(
        get_top_delegates()
    )


@blockchain_bp.route(
    "/api/dpos/status",
    methods=["GET"]
)
def dpos_status():

    return jsonify(
        get_dpos_status()
    )


@blockchain_bp.route(
    "/api/election/start",
    methods=["POST"]
)
def start_election():

    return jsonify(
        begin_new_election()
    )


# @blockchain_bp.route(
#     "/api/election/end",
#     methods=["POST"]
# )
# def end_election():

#     print("=" * 60)
#     print("END ELECTION API CALLED")
#     print("=" * 60)

#     result = finish_current_election()

#     print(result)

#     return jsonify(result)


@blockchain_bp.route(
    "/api/election/end",
    methods=["POST"]
)
def end_election():

    print("=" * 60)
    print("END ELECTION ROUTE HIT")

    try:

        result = finish_current_election()

        print("SERVICE RETURNED:")
        print(result)

        return jsonify(result)

    except Exception as e:

        import traceback

        print("EXCEPTION:")
        traceback.print_exc()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@blockchain_bp.route(
    "/api/dpos/validator-history",
    methods=["GET"]
)
def validator_history():

    return jsonify(
        get_recent_validator_history(10)
    )

@blockchain_bp.route(
    "/api/ai-alerts",
    methods=["GET"]
)
def ai_alerts():

    return jsonify(
        get_all_ai_alerts()
    )


@blockchain_bp.route(
    "/api/blockchain/token/info",
    methods=["GET"]
)
def token_info():
    try:
        return jsonify(get_token_info())
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@blockchain_bp.route(
    "/api/blockchain/token/balance/<address>",
    methods=["GET"]
)
def token_balance(address):
    try:
        return jsonify(get_token_balance(address))
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@blockchain_bp.route(
    "/api/blockchain/token/transfer",
    methods=["POST"]
)
def token_transfer():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(transfer(payload.get("to"), payload.get("amount")))
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@blockchain_bp.route(
    "/api/blockchain/marketplace/orders",
    methods=["GET"]
)
def blockchain_marketplace_orders():
    try:
        return jsonify(marketplace_orders())
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@blockchain_bp.route(
    "/api/blockchain/marketplace/sell",
    methods=["POST"]
)
def blockchain_marketplace_sell():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(marketplace_sell(
            payload.get("seller"),
            payload.get("energyAmount"),
            payload.get("price"),
        ))
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@blockchain_bp.route(
    "/api/blockchain/marketplace/buy",
    methods=["POST"]
)
def blockchain_marketplace_buy():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(marketplace_buy(
            payload.get("listingId"),
            payload.get("buyer"),
        ))
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@blockchain_bp.route(
    "/api/blockchain/voting/validators",
    methods=["GET"]
)
def blockchain_voting_validators():
    try:
        return jsonify(get_validators())
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@blockchain_bp.route(
    "/api/blockchain/voting/delegates/<address>",
    methods=["GET"]
)
def blockchain_voting_delegate_info(address):
    try:
        return jsonify(get_delegate(address))
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@blockchain_bp.route(
    "/api/blockchain/voting/vote",
    methods=["POST"]
)
def blockchain_voting_vote():
    payload = request.get_json(silent=True) or {}
    try:
        return jsonify(vote(payload.get("delegate")))
    except Exception as error:
        return jsonify({"error": str(error)}), 400


