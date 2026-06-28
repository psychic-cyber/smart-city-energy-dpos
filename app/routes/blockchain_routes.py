from flask import (
    Blueprint,
    jsonify,
    session,
    send_file
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

from ml.ai_engine import (
    get_ai_monitoring_data,
    should_create_ai_alert
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

from app.services.dpos_service import (
    cast_delegate_vote,
    close_election,
    get_dpos_status,
    get_recent_validator_history,
    start_next_election
)

from database.mongodb.election_repository import (
    get_election_history
)

from database.mongodb.ai_alert_repository import (
    get_latest_ai_alert,
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

    data = get_ai_monitoring_data()

    latest_alert = (
        get_latest_ai_alert()
    )

    create_alert = False

    if should_create_ai_alert(
        data["risk_level"]
    ):

        if not latest_alert:

            create_alert = True

        else:

            old_score = (
                latest_alert["data"]
                ["transaction"]
                ["risk_score"]
            )

            if old_score != data["risk_score"]:

                create_alert = True

        if create_alert:

            blockchain = Blockchain()

            blockchain.add_block(
                {
                    "type": "AI_ALERT",
                    "risk_level":
                        data["risk_level"],
                    "risk_score":
                        data["risk_score"],
                    "anomalies":
                        data["anomalies"],
                    "anomaly_rate":
                        data["anomaly_rate"]
                }
            )

            save_block(
                blockchain.get_latest_block()
            )

            save_blockchain(
                blockchain.chain
            )
    
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
    "/api/election/close",
    methods=["POST"]
)
def close_election_route():

    return jsonify(
        close_election()
    )


@blockchain_bp.route(
    "/api/election/start",
    methods=["POST"]
)
def start_election():

    return jsonify(
        start_next_election()
    )


@blockchain_bp.route(
    "/api/election/history",
    methods=["GET"]
)
def election_history():

    return jsonify(
        get_election_history()
    )


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
    "/api/delegates/vote/<username>",
    methods=["POST"]
)
def cast_vote(username):

    voter = session.get(
        "username"
    )

    if not voter:

        return jsonify(
            {
                "success": False,
                "message": "Login Required"
            }
        )

    success, message, validator = cast_delegate_vote(
        voter,
        username
    )

    if not success:

        return jsonify(
            {
                "success": False,
                "message": message
            }
        )

    return jsonify(
        {
            "success": True,
            "message": message,
            "active_validator":
                validator["username"]
                if validator else None
        }
    )
