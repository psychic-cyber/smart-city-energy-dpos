from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    jsonify,
    request
)

from database.mongodb.energy_record_repository import (
    get_pending_records,
    approve_record,
    decline_record,
    get_pending_record_by_username
)

from database.mongodb.user_repository import (
    get_user_by_username,
    update_energy_stats
)

from blockchain.core.blockchain import (
    Blockchain
)

from database.mongodb.blockchain_repository import (
    save_chain,
    save_block
)

from blockchain.storage.storage_manager import (
    save_blockchain
)

from ml.anomaly_detector import (
    predict_anomaly
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/admin-dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "Admin":
        return redirect("/user-dashboard")

    return render_template(
        "dashboard.html",
        username=session.get(
            "username",
            "Admin"
        )
    )


@dashboard_bp.route("/analytics")
def analytics_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "analytics.html"
    )


@dashboard_bp.route("/blockchain")
def blockchain_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "blockchain.html"
    )


@dashboard_bp.route("/transactions")
def transactions_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "transactions.html"
    )


@dashboard_bp.route("/ai-monitoring")
def ai_monitoring_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "ai_monitoring.html"
    )


@dashboard_bp.route("/reports")
def reports_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "reports.html"
    )

@dashboard_bp.route("/users")
def users_page():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "Admin":
        return redirect("/user-dashboard")

    return render_template(
        "users.html"
    )

@dashboard_bp.route(
    "/api/pending-readings"
)
def pending_readings():

    if session.get("role") != "Admin":

        return jsonify(
            []
        )

    return jsonify(
        get_pending_records()
    )

@dashboard_bp.route(
    "/api/approve-reading",
    methods=["POST"]
)
def approve_reading():

    if session.get("role") != "Admin":

        return jsonify(
            {
                "success": False,
                "message": "Unauthorized"
            }
        )

    data = request.get_json()

    username = data[
        "username"
    ]

    record = (
        get_pending_record_by_username(
            username
        )
    )

    if not record:

        return jsonify(
            {
                "success": False,
                "message": "Reading Not Found"
            }
        )

    user = get_user_by_username(
        username
    )

    generated = float(
        record["energy_generated"]
    )

    consumed = float(
        record["energy_consumed"]
    )

    is_anomaly = predict_anomaly(
        consumed,
        generated
    )

    current_generated = float(
        user.get(
            "energy_generated",
            0
        )
    )

    current_consumed = float(
        user.get(
            "energy_consumed",
            0
        )
    )

    new_generated = (
        current_generated
        + generated
    )

    new_consumed = (
        current_consumed
        + consumed
    )

    new_balance = (
        new_generated
        - new_consumed
    )

    update_energy_stats(
        username,
        new_generated,
        new_consumed,
        new_balance
    )

    approve_record(
        username
    )

    blockchain = Blockchain()

    transaction_type = (
        "AI_ALERT"
        if is_anomaly == 1
        else "ENERGY_READING_APPROVED"
    )

    blockchain.add_block(
        {
            "type":
                transaction_type,

            "username":
                username,

            "generated":
                generated,

            "consumed":
                consumed,

            "anomaly":
                bool(is_anomaly)
        }
    )

    save_block(
        blockchain.get_latest_block()
    )

    save_chain(
        blockchain.chain
    )

    save_blockchain(
        blockchain.chain
    )

    return jsonify(
        {
            "success": True,
            "message":
                "Reading Approved Successfully"
        }
    )
    
@dashboard_bp.route(
    "/api/decline-reading",
    methods=["POST"]
)
def decline_reading():

    if session.get("role") != "Admin":

        return jsonify(
            {
                "success": False,
                "message": "Unauthorized"
            }
        )

    data = request.get_json()

    username = data["username"]

    decline_record(username)

    return jsonify(
        {
            "success": True,
            "message":
                "Reading Declined Successfully"
        }
    )