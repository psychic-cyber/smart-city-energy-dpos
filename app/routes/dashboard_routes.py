from datetime import datetime

from database.mongodb.ai_alert_repository import (
    save_ai_alert
)

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
    update_energy_stats,
    delete_user,
    count_admins,
    find_user_by_username
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

from app.services.ai_service import (
    run_full_analysis
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

def evaluate_energy_anomaly(
    current_balance,
    generated,
    consumed,
    previous_consumed
):

    alerts = []

    severity = "LOW"

    new_balance = (
        current_balance
        + generated
        - consumed
    )

    if new_balance < 0:

        alerts.append(
            "Negative Energy Balance"
        )

        severity = "CRITICAL"

    if consumed > generated * 5:

        alerts.append(
            "Consumption exceeds generation"
        )

        if severity != "CRITICAL":
            severity = "HIGH"

    if generated > consumed * 10:

        alerts.append(
            "Abnormally High Generation"
        )

        if severity == "LOW":
            severity = "MEDIUM"

    if previous_consumed > 0:

        increase = (
            consumed
            /
            previous_consumed
        )

        if increase >= 3:

            alerts.append(
                "Sudden Consumption Spike"
            )

            if severity == "LOW":
                severity = "MEDIUM"

    return {

        "is_anomaly":
            len(alerts) > 0,

        "severity":
            severity,

        "reason":
            ", ".join(alerts),

        "new_balance":
            new_balance

    }

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

    current_balance = float(
        user.get(
            "energy_balance",
            0
        )
    )

    analysis = evaluate_energy_anomaly(
        current_balance=current_balance,
        generated=generated,
        consumed=consumed,
        previous_consumed=float(
            user.get(
                "energy_consumed",
                0
            )
        )
    )

    is_anomaly = analysis["is_anomaly"]

    reason = analysis["reason"]

    severity = analysis["severity"]

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

    new_balance = analysis["new_balance"]

    update_energy_stats(
        username,
        new_generated,
        new_consumed,
        new_balance
    )

    approve_record(
        username
    )

    try:

        run_full_analysis()

    except Exception as error:

        print(
            "AI Analysis Error:",
            error
        )

    if is_anomaly:

        save_ai_alert(
            {
                "username": username,

                "generated": generated,

                "consumed": consumed,

                "reason": reason,

                "severity": severity,

                "risk_level": severity,

                "confidence": 95,

                "timestamp": str(
                    datetime.now()
                )
            }
        )

    blockchain = Blockchain()

    if is_anomaly:

        transaction_type = (
            f"AI_ALERT_{severity}"
        )

    else:

        transaction_type = (
            "ENERGY_READING_APPROVED"
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


@dashboard_bp.route(
    "/api/delete-user/<username>",
    methods=["DELETE"]
)
def delete_user_endpoint(username):
    """
    Delete a user account. Only admins can delete users.
    Prevents deletion of the current logged-in admin and the last remaining admin.
    """
    # Check if user is authenticated and is admin
    if "user_id" not in session:
        return jsonify(
            {
                "success": False,
                "message": "Unauthorized"
            }
        ), 401

    if session.get("role") != "Admin":
        return jsonify(
            {
                "success": False,
                "message": "Only admins can delete users"
            }
        ), 403

    current_admin = session.get("username")

    # Prevent deleting own account
    if current_admin == username:
        return jsonify(
            {
                "success": False,
                "message": "You cannot delete your own account"
            }
        ), 400

    # Check if user to delete exists
    user_to_delete = find_user_by_username(username)

    if not user_to_delete:
        return jsonify(
            {
                "success": False,
                "message": "User not found"
            }
        ), 404

    # Check if user is admin
    is_admin = user_to_delete.get("role") == "Admin"

    if is_admin:
        # Count remaining admins
        admin_count = count_admins()

        if admin_count <= 1:
            return jsonify(
                {
                    "success": False,
                    "message": "Cannot delete the last remaining admin"
                }
            ), 400

    # Delete the user
    deleted_user = delete_user(username)

    if not deleted_user:
        return jsonify(
            {
                "success": False,
                "message": "Failed to delete user"
            }
        ), 500

    return jsonify(
        {
            "success": True,
            "message": f"User '{username}' has been deleted successfully"
        }
    ), 200