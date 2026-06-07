from flask import Blueprint, render_template

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

@dashboard_bp.route("/")
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/analytics")
def analytics_page():
    return render_template("analytics.html")


@dashboard_bp.route("/blockchain")
def blockchain_page():
    return render_template("blockchain.html")


@dashboard_bp.route("/transactions")
def transactions_page():
    return render_template("transactions.html")


@dashboard_bp.route("/ai-monitoring")
def ai_monitoring_page():
    return render_template("ai_monitoring.html")


@dashboard_bp.route("/reports")
def reports_page():
    return render_template("reports.html")