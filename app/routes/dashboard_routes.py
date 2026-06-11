from flask import (
    Blueprint,
    render_template,
    session,
    redirect
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/admin-dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
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

    if session.get("role") != "admin":
        return redirect("/user-dashboard")

    return render_template(
        "users.html"
    )