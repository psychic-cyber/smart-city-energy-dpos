from flask import Blueprint, jsonify

from app.services.ai_service import (
    compute_forecast,
    detect_anomalies,
    generate_smart_recommendations,
    get_ai_dashboard,
    get_ai_statistics,
    get_model_information,
    get_monitoring_data,
    run_full_analysis,
)
from database.mongodb.ai_history_repository import get_ai_history
from database.mongodb.ai_alert_repository import get_all_ai_alerts


ai_bp = Blueprint(
    "ai",
    __name__
)


@ai_bp.route(
    "/api/ai/dashboard",
    methods=["GET"]
)
def ai_dashboard():

    return jsonify(
        get_ai_dashboard()
    )


@ai_bp.route(
    "/api/ai/forecast",
    methods=["GET"]
)
def ai_forecast():

    return jsonify(
        compute_forecast()
    )


@ai_bp.route(
    "/api/ai/model",
    methods=["GET"]
)
def ai_model():

    return jsonify(
        get_model_information()
    )


@ai_bp.route(
    "/api/ai/history",
    methods=["GET"]
)
def ai_history():

    return jsonify(
        get_ai_history()
    )


@ai_bp.route(
    "/api/ai/statistics",
    methods=["GET"]
)
def ai_statistics():

    return jsonify(
        get_ai_statistics()
    )


@ai_bp.route(
    "/api/ai/run",
    methods=["POST"]
)
def ai_run():

    return jsonify(
        run_full_analysis()
    )


@ai_bp.route(
    "/api/ai/anomalies",
    methods=["GET"]
)
def ai_anomalies():

    return jsonify(
        detect_anomalies()
    )


@ai_bp.route(
    "/api/ai/recommendations",
    methods=["GET"]
)
def ai_recommendations():
    from app.services.ai_service import (
        _collect_live_context,
        compute_prediction,
        compute_forecast,
    )

    context = _collect_live_context()
    prediction = compute_prediction(context)
    forecast = compute_forecast(context)
    anomalies = detect_anomalies(context)

    return jsonify(
        generate_smart_recommendations(
            context,
            prediction,
            forecast,
            anomalies,
        )
    )


@ai_bp.route(
    "/api/ai/monitoring",
    methods=["GET"]
)
def ai_monitoring_compat():

    from app.services.ai_service import process_monitoring_blockchain_alert

    data = get_monitoring_data()
    process_monitoring_blockchain_alert(data)

    return jsonify(data)


@ai_bp.route(
    "/api/ai/alerts",
    methods=["GET"]
)
def ai_alerts():

    return jsonify(
        get_all_ai_alerts()
    )
