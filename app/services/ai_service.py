import os
from datetime import datetime

import joblib
import pandas as pd

from ai.ai_engine import generate_ai_insight
from database.mongodb.ai_alert_repository import (
    count_ai_alerts,
    count_alerts_by_severity,
    count_critical_alerts,
    get_latest_ai_alert,
    save_ai_alert,
)
from database.mongodb.ai_history_repository import (
    count_predictions,
    get_ai_history,
    get_history_statistics,
    save_ai_history,
)
from database.mongodb.energy_record_repository import (
    get_approved_records,
)
from database.mongodb.marketplace_repository import (
    get_marketplace_summary,
    get_marketplace_transactions,
)
from database.mongodb.user_repository import (
    get_all_users,
)
from database.mongodb.user_transaction_repository import (
    get_all_user_transactions,
)

MODEL_PATH = "ml/anomaly_model.pkl"
ACCURACY_PATH = "ml/model_accuracy.pkl"
FEATURES_PATH = "ml/model_features.pkl"
DATASET_PATH = "ml/datasets/smart_city_energy_data.csv"
MODEL_VERSION = "RandomForestClassifier-v1"
ALGORITHM_NAME = "RandomForestClassifier"

ROLE_ENTITY_MAP = {
    "House": "House",
    "Hospital": "Hospital",
    "University": "University",
    "SolarFarm": "SolarFarm",
    "Factory": "Factory",
    "Office": "Office",
    "Restaurant": "Apartment",
    "Admin": "Office",
}

_model_cache = {}
_historical_cache = None


def _ml_engine():
    from ml.ai_engine import (
        calculate_risk_score,
        generate_recommendation,
        get_ai_monitoring_data,
        get_risk_level,
        predict_anomaly,
        should_create_ai_alert,
    )

    return {
        "calculate_risk_score": calculate_risk_score,
        "generate_recommendation": generate_recommendation,
        "get_ai_monitoring_data": get_ai_monitoring_data,
        "get_risk_level": get_risk_level,
        "predict_anomaly": predict_anomaly,
        "should_create_ai_alert": should_create_ai_alert,
    }


def _get_analytics():
    from database.mongodb.transaction_repository import get_analytics

    return get_analytics()


def _get_model_assets():
    if not _model_cache:
        _model_cache["model"] = joblib.load(MODEL_PATH)
        _model_cache["accuracy"] = float(joblib.load(ACCURACY_PATH))
        _model_cache["features"] = joblib.load(FEATURES_PATH)
        _model_cache["training_date"] = datetime.fromtimestamp(
            os.path.getmtime(MODEL_PATH)
        ).strftime("%Y-%m-%d %H:%M:%S")
        _model_cache["training_samples"] = len(_load_historical_dataframe())
        _model_cache["feature_count"] = len(_model_cache["features"])
    return _model_cache


def _load_historical_dataframe():
    global _historical_cache
    if _historical_cache is None:
        dataframe = pd.read_csv(DATASET_PATH)
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"])
        _historical_cache = dataframe
    return _historical_cache.copy()


def _collect_live_context():
    users = get_all_users()
    historical = _load_historical_dataframe()
    marketplace_summary = get_marketplace_summary()
    marketplace_transactions = get_marketplace_transactions()
    energy_transactions = get_all_user_transactions()
    approved_records = get_approved_records()

    current_consumption = sum(
        float(user.get("energy_consumed", 0))
        for user in users
    )
    current_generation = sum(
        float(user.get("energy_generated", 0))
        for user in users
    )
    record_consumption = sum(
        float(record.get("energy_consumed", 0))
        for record in approved_records
    )
    record_generation = sum(
        float(record.get("energy_generated", 0))
        for record in approved_records
    )

    current_consumption = round(
        current_consumption + record_consumption,
        2,
    )
    current_generation = round(
        current_generation + record_generation,
        2,
    )

    trade_volume = sum(
        float(transaction.get("total_price", transaction.get("total_amount", 0)))
        for transaction in marketplace_transactions
    )
    traded_energy = sum(
        float(
            transaction.get(
                "quantity",
                transaction.get("purchased_amount", transaction.get("energy", 0)),
            )
        )
        for transaction in marketplace_transactions
    )

    return {
        "users": users,
        "historical": historical,
        "marketplace_summary": marketplace_summary,
        "marketplace_transactions": marketplace_transactions,
        "energy_transactions": energy_transactions,
        "approved_records": approved_records,
        "current_consumption": current_consumption,
        "current_generation": current_generation,
        "grid_usage": round(
            max(current_consumption - current_generation, 0),
            2,
        ),
        "average_marketplace_price": float(
            marketplace_summary.get("average_price", 0)
        ),
        "market_volume": float(
            marketplace_summary.get("market_volume", 0)
        ),
        "trade_volume": round(trade_volume, 2),
        "traded_energy": round(traded_energy, 2),
        "user_count": len(users),
    }


def _live_scale_factor(context):
    historical = context["historical"]
    user_count = max(context["user_count"], 1)
    historical_mean = float(historical["energy_consumed_kwh"].mean())
    live_mean = context["current_consumption"] / user_count
    if historical_mean <= 0:
        return 1.0
    return max(live_mean / historical_mean, 0.1)


def _expected_consumption(context):
    historical = context["historical"]
    current_hour = datetime.now().hour
    hourly_data = historical[
        historical["timestamp"].dt.hour == current_hour
    ]

    if len(hourly_data):
        baseline = float(hourly_data["energy_consumed_kwh"].mean())
    else:
        baseline = float(historical["energy_consumed_kwh"].mean())

    scale = _live_scale_factor(context)
    user_count = max(context["user_count"], 1)
    return round(baseline * user_count * scale, 2)


def _build_model_feature_frame(context):
    assets = _get_model_assets()
    historical = context["historical"]
    recent = historical.tail(100)

    row = {
        "entity_id": float(recent["entity_id"].mean()),
        "temperature": float(recent["temperature"].mean()),
        "energy_consumed_kwh": float(context["current_consumption"]),
        "energy_generated_kwh": float(context["current_generation"]),
        "grid_usage_kwh": float(context["grid_usage"]),
        "energy_price": float(
            context["average_marketplace_price"]
            or recent["energy_price"].mean()
        ),
        "carbon_emission_kg": float(
            recent["carbon_emission_kg"].mean()
            * max(context["current_consumption"] / max(recent["energy_consumed_kwh"].mean(), 1), 0.1)
        ),
    }

    dataframe = pd.DataFrame([row])
    feature_frame = pd.DataFrame(
        0,
        index=[0],
        columns=assets["features"],
    )

    for column in dataframe.columns:
        if column in feature_frame.columns:
            feature_frame[column] = dataframe[column].values[0]

    current_hour = datetime.now().hour
    peak_value = "Yes" if current_hour in [8, 9, 10, 17, 18, 19, 20] else "No"
    dominant_entity = (
        recent["entity_type"].mode().iloc[0]
        if len(recent["entity_type"].mode())
        else "House"
    )
    dominant_district = (
        recent["district"].mode().iloc[0]
        if len(recent["district"].mode())
        else "District-A"
    )
    dominant_weather = (
        recent["weather"].mode().iloc[0]
        if len(recent["weather"].mode())
        else "Cloudy"
    )

    for column in feature_frame.columns:
        if column == f"entity_type_{dominant_entity}":
            feature_frame[column] = 1
        if column == f"district_{dominant_district}":
            feature_frame[column] = 1
        if column == f"weather_{dominant_weather}":
            feature_frame[column] = 1
        if column == f"peak_hour_{peak_value}":
            feature_frame[column] = 1

    return feature_frame


def compute_prediction(context=None):
    context = context or _collect_live_context()
    assets = _get_model_assets()
    model = assets["model"]
    feature_frame = _build_model_feature_frame(context)

    anomaly_prediction = int(model.predict(feature_frame)[0])
    probabilities = model.predict_proba(feature_frame)[0]
    confidence = round(float(max(probabilities)) * 100, 2)

    expected = _expected_consumption(context)
    marketplace_factor = 1 + min(
        context["traded_energy"] / max(context["current_consumption"], 1),
        0.15,
    )
    anomaly_factor = 1.12 if anomaly_prediction == 1 else 1.0
    predicted = round(expected * marketplace_factor * anomaly_factor, 2)
    difference = round(predicted - context["current_consumption"], 2)

    return {
        "current_consumption": context["current_consumption"],
        "expected_consumption": expected,
        "prediction": predicted,
        "prediction_difference": difference,
        "confidence": confidence,
        "anomaly_signal": anomaly_prediction,
    }


def compute_forecast(context=None):
    context = context or _collect_live_context()
    historical = context["historical"]
    scale = _live_scale_factor(context)
    user_count = max(context["user_count"], 1)

    historical = historical.copy()
    historical["hour"] = historical["timestamp"].dt.hour
    hourly_totals = historical.groupby("hour")["energy_consumed_kwh"].sum()
    daily_totals = historical.groupby(
        historical["timestamp"].dt.date
    )["energy_consumed_kwh"].sum()

    next_hour = float(
        hourly_totals.get(
            (datetime.now().hour + 1) % 24,
            hourly_totals.mean(),
        )
    ) * scale
    next_day = float(daily_totals.tail(7).mean()) * scale * user_count
    next_week = float(daily_totals.tail(7).mean()) * 7 * scale * user_count

    recent = float(daily_totals.tail(7).mean())
    prior = float(daily_totals.tail(14).head(7).mean())
    if recent > prior * 1.05:
        trend = "Increasing"
    elif recent < prior * 0.95:
        trend = "Decreasing"
    else:
        trend = "Stable"

    peak_hour = int(hourly_totals.idxmax())
    lowest_hour = int(hourly_totals.idxmin())

    return {
        "next_hour_prediction": round(next_hour, 2),
        "next_day_prediction": round(next_day, 2),
        "next_week_prediction": round(next_week, 2),
        "trend": trend,
        "peak_hour": peak_hour,
        "lowest_demand_hour": lowest_hour,
    }


def _evaluate_user_anomaly(user):
    consumed = float(user.get("energy_consumed", 0))
    generated = float(user.get("energy_generated", 0))

    if consumed > generated * 5:
        return "Critical", "Abnormally high consumption compared to generation"
    if generated > consumed * 10 and generated > 500:
        return "Warning", "Abnormally high generation compared to consumption"
    if consumed > 2000:
        return "Critical", "Critical energy consumption threshold exceeded"
    if consumed > 1200:
        return "Warning", "Elevated energy consumption detected"
    return "Normal", "Operating within expected consumption range"


def _predict_user_ml_signal(user, historical, system_confidence=0):
    role = ROLE_ENTITY_MAP.get(user.get("role", "House"), "House")
    consumed = float(user.get("energy_consumed", 0))
    generated = float(user.get("energy_generated", 0))
    grid_usage = max(consumed - generated, 0)
    role_rows = historical[historical["entity_type"] == role]

    if len(role_rows):
        reference = role_rows
    else:
        reference = historical

    district = reference["district"].mode().iloc[0]
    weather = reference["weather"].mode().iloc[0]
    temperature = float(reference["temperature"].mean())
    energy_price = float(reference["energy_price"].mean())
    carbon = float(reference["carbon_emission_kg"].mean())
    peak_hour = (
        "Yes"
        if datetime.now().hour in [8, 9, 10, 17, 18, 19, 20]
        else "No"
    )

    prediction = int(
        _ml_engine()["predict_anomaly"](
            entity_id=1,
            entity_type=role,
            district=district,
            weather=weather,
            peak_hour=peak_hour,
            temperature=temperature,
            consumed=consumed,
            generated=generated,
            grid_usage=grid_usage,
            energy_price=energy_price,
            carbon=carbon,
        )
    )

    assets = _get_model_assets()
    confidence = system_confidence or round(float(assets["accuracy"]) * 100, 2)

    if prediction == 1 and consumed > generated * 2:
        return "Critical", "Machine learning model flagged critical anomaly", confidence
    if prediction == 1:
        return "Warning", "Machine learning model flagged unusual activity", confidence
    return "Normal", "No machine learning anomaly detected", confidence


def detect_anomalies(context=None):
    context = context or _collect_live_context()
    historical = context["historical"]
    prediction = compute_prediction(context)
    system_confidence = prediction["confidence"]
    anomalies = []

    for user in context["users"]:
        rule_status, rule_reason = _evaluate_user_anomaly(user)
        ml_status, ml_reason, confidence = _predict_user_ml_signal(
            user,
            historical,
            system_confidence,
        )

        if rule_status == "Critical" or ml_status == "Critical":
            status = "Critical"
            reason = rule_reason if rule_status == "Critical" else ml_reason
        elif rule_status == "Warning" or ml_status == "Warning":
            status = "Warning"
            reason = rule_reason if rule_status == "Warning" else ml_reason
        else:
            continue

        latest_record = next(
            (
                record
                for record in context["approved_records"]
                if record.get("username") == user.get("username")
            ),
            None,
        )

        anomalies.append({
            "status": status,
            "reason": reason,
            "confidence": confidence,
            "affected_user": user.get("username"),
            "energy_generated": float(
                latest_record.get("energy_generated", user.get("energy_generated", 0))
                if latest_record else user.get("energy_generated", 0)
            ),
            "energy_consumed": float(
                latest_record.get("energy_consumed", user.get("energy_consumed", 0))
                if latest_record else user.get("energy_consumed", 0)
            ),
            "timestamp": (
                latest_record.get("created_at", str(datetime.now()))
                if latest_record else str(datetime.now())
            ),
        })

    return anomalies


def generate_smart_recommendations(
    context,
    prediction,
    forecast,
    anomalies,
):
    recommendations = []
    marketplace = context["marketplace_summary"]
    avg_price = float(marketplace.get("average_price", 0))
    highest_price = float(marketplace.get("highest_price", 0))
    lowest_price = float(marketplace.get("lowest_price", 0))

    if prediction["prediction_difference"] > 0:
        recommendations.append({
            "type": "possible_grid_overload",
            "message": "Predicted demand exceeds current consumption. Prepare for higher grid load.",
            "priority": "HIGH",
        })

    if prediction["current_consumption"] > prediction["expected_consumption"] * 1.1:
        recommendations.append({
            "type": "reduce_consumption",
            "message": "Current consumption is above the expected baseline. Reduce peak-hour usage.",
            "priority": "HIGH",
        })

    total_balance = sum(
        float(user.get("energy_balance", 0))
        for user in context["users"]
    )
    if total_balance > 250:
        recommendations.append({
            "type": "sell_excess_energy",
            "message": "Aggregate surplus energy is available. Consider listing energy on the marketplace.",
            "priority": "MEDIUM",
        })

    if context["current_generation"] < context["current_consumption"] * 0.5:
        recommendations.append({
            "type": "buy_additional_energy",
            "message": "Generation is lagging consumption. Purchase additional energy from the marketplace.",
            "priority": "HIGH",
        })

    if context["current_generation"] < prediction["expected_consumption"] * 0.4:
        recommendations.append({
            "type": "solar_generation_low",
            "message": "Solar and local generation levels are below forecast expectations.",
            "priority": "MEDIUM",
        })

    if total_balance > 100 and avg_price > 0:
        recommendations.append({
            "type": "store_battery_energy",
            "message": "Stored surplus energy can be reserved for peak pricing periods.",
            "priority": "LOW",
        })

    if highest_price > 0 and avg_price > 0 and highest_price >= avg_price * 1.25:
        recommendations.append({
            "type": "high_marketplace_prices",
            "message": "Marketplace prices are elevated. Selling surplus energy is favorable.",
            "priority": "MEDIUM",
        })

    if lowest_price > 0 and avg_price > 0 and lowest_price <= avg_price * 0.75:
        recommendations.append({
            "type": "low_marketplace_prices",
            "message": "Marketplace prices are low. Consider buying energy for future demand.",
            "priority": "MEDIUM",
        })

    if forecast["trend"] == "Increasing":
        recommendations.append({
            "type": "monitor_demand_trend",
            "message": "Demand trend is increasing. Monitor consumption across high-usage entities.",
            "priority": "MEDIUM",
        })

    if anomalies:
        recommendations.append({
            "type": "investigate_anomalies",
            "message": f"{len(anomalies)} anomalous energy profile(s) require review.",
            "priority": "CRITICAL" if any(a["status"] == "Critical" for a in anomalies) else "HIGH",
        })

    if not recommendations:
        recommendations.append({
            "type": "maintain_operations",
            "message": "System metrics are stable. Maintain current energy strategy.",
            "priority": "LOW",
        })

    return recommendations


def _system_health_score(risk_score, confidence, efficiency):
    return round(
        min(
            (confidence * 0.45)
            + ((100 - risk_score) * 0.35)
            + (min(efficiency, 100) * 0.20),
            100,
        ),
        2,
    )


def _system_status(risk_level):
    if risk_level in {"CRITICAL", "HIGH"}:
        return "WARNING"
    return "ACTIVE"


def get_model_information():
    assets = _get_model_assets()
    return {
        "algorithm": ALGORITHM_NAME,
        "accuracy": round(assets["accuracy"] * 100, 2),
        "training_samples": assets["training_samples"],
        "feature_count": assets["feature_count"],
        "last_training_time": assets["training_date"],
        "model_status": "READY",
        "model_version": MODEL_VERSION,
    }


def get_monitoring_data():
    return _ml_engine()["get_ai_monitoring_data"]()


def get_ai_dashboard():
    context = _collect_live_context()
    prediction = compute_prediction(context)
    forecast = compute_forecast(context)
    anomalies = detect_anomalies(context)
    recommendations = generate_smart_recommendations(
        context,
        prediction,
        forecast,
        anomalies,
    )
    monitoring = get_monitoring_data()
    model_info = get_model_information()
    analytics = _get_analytics()

    risk_score = _ml_engine()["calculate_risk_score"](
        prediction["current_consumption"],
        context["current_generation"],
        context["grid_usage"],
        context["historical"]["carbon_emission_kg"].tail(100).mean(),
    )
    risk_level = _ml_engine()["get_risk_level"](risk_score)
    primary_recommendation = recommendations[0]["message"]
    suggested_action = _ml_engine()["generate_recommendation"](risk_level)
    insight = generate_ai_insight(
        monitoring["anomaly_rate"],
        analytics.get("energy_efficiency", 0),
    )

    return {
        "ai_accuracy": model_info["accuracy"],
        "prediction_confidence": prediction["confidence"],
        "system_health_score": _system_health_score(
            risk_score,
            prediction["confidence"],
            analytics.get("energy_efficiency", 0),
        ),
        "risk_level": risk_level,
        "current_demand": prediction["current_consumption"],
        "predicted_demand": prediction["prediction"],
        "prediction_difference": prediction["prediction_difference"],
        "detected_anomalies": len(anomalies),
        "recommendation": primary_recommendation,
        "suggested_action": suggested_action,
        "system_status": _system_status(risk_level),
        "total_ai_alerts": count_ai_alerts(),
        "model_version": model_info["model_version"],
        "training_date": model_info["last_training_time"],
        "model_accuracy": model_info["accuracy"],
        "insights": insight,
        "forecast": forecast,
        "recommendations": recommendations,
        "anomalies": anomalies,
    }


def get_ai_statistics():
    history_stats = get_history_statistics()
    model_info = get_model_information()

    return {
        "total_predictions": count_predictions(),
        "total_alerts": count_ai_alerts(),
        "critical_alerts": count_critical_alerts(),
        "average_confidence": history_stats["average_confidence"],
        "average_accuracy": round(model_info["accuracy"], 2),
        "highest_risk": history_stats["highest_risk"],
        "lowest_risk": history_stats["lowest_risk"],
        "alerts_by_severity": {
            "LOW": count_alerts_by_severity("LOW"),
            "MEDIUM": count_alerts_by_severity("MEDIUM"),
            "HIGH": count_alerts_by_severity("HIGH"),
            "CRITICAL": count_alerts_by_severity("CRITICAL"),
        },
    }


def _store_analysis_history(
    prediction,
    forecast,
    recommendations,
    risk_level,
):
    primary = recommendations[0] if recommendations else {}
    record = {
        "prediction": prediction["prediction"],
        "confidence": prediction["confidence"],
        "risk_level": risk_level,
        "recommendation": primary.get("message", ""),
        "timestamp": str(datetime.now()),
        "model_version": MODEL_VERSION,
        "forecast": forecast,
    }
    return save_ai_history(record)


def _create_alerts_from_analysis(anomalies, risk_level, prediction):
    created = []

    for anomaly in anomalies:
        severity = "CRITICAL" if anomaly["status"] == "Critical" else "HIGH"
        alert = save_ai_alert({
            "username": anomaly["affected_user"],
            "generated": anomaly["energy_generated"],
            "consumed": anomaly["energy_consumed"],
            "reason": anomaly["reason"],
            "severity": severity,
            "confidence": anomaly["confidence"],
            "timestamp": anomaly["timestamp"],
        })
        created.append(alert)

    if _ml_engine()["should_create_ai_alert"](risk_level) and not anomalies:
        alert = save_ai_alert({
            "username": "SYSTEM",
            "generated": 0,
            "consumed": prediction["current_consumption"],
            "reason": _ml_engine()["generate_recommendation"](risk_level),
            "severity": risk_level,
            "confidence": prediction["confidence"],
            "timestamp": str(datetime.now()),
        })
        created.append(alert)

    return created


def run_full_analysis():
    context = _collect_live_context()
    prediction = compute_prediction(context)
    forecast = compute_forecast(context)
    anomalies = detect_anomalies(context)
    recommendations = generate_smart_recommendations(
        context,
        prediction,
        forecast,
        anomalies,
    )

    risk_score = _ml_engine()["calculate_risk_score"](
        prediction["current_consumption"],
        context["current_generation"],
        context["grid_usage"],
        context["historical"]["carbon_emission_kg"].tail(100).mean(),
    )
    risk_level = _ml_engine()["get_risk_level"](risk_score)
    history = _store_analysis_history(
        prediction,
        forecast,
        recommendations,
        risk_level,
    )
    alerts = _create_alerts_from_analysis(
        anomalies,
        risk_level,
        prediction,
    )

    return {
        "prediction": prediction,
        "forecast": forecast,
        "anomalies": anomalies,
        "recommendations": recommendations,
        "risk_level": risk_level,
        "alerts_created": len(alerts),
        "history": history,
        "model_version": MODEL_VERSION,
    }


def process_monitoring_blockchain_alert(data):
    from blockchain.core.blockchain import Blockchain
    from blockchain.storage.storage_manager import save_blockchain
    from database.mongodb.blockchain_repository import save_block

    latest_alert = get_latest_ai_alert()
    create_alert = False

    if _ml_engine()["should_create_ai_alert"](data["risk_level"]):
        if not latest_alert:
            create_alert = True
        else:
            old_score = latest_alert.get("data", {}).get("transaction", {}).get(
                "risk_score",
                latest_alert.get("risk_score"),
            )
            if old_score != data["risk_score"]:
                create_alert = True

        if create_alert:
            blockchain = Blockchain()
            blockchain.add_block({
                "type": "AI_ALERT",
                "risk_level": data["risk_level"],
                "risk_score": data["risk_score"],
                "anomalies": data["anomalies"],
                "anomaly_rate": data["anomaly_rate"],
            })
            save_block(blockchain.get_latest_block())
            save_blockchain(blockchain.chain)

    return create_alert
