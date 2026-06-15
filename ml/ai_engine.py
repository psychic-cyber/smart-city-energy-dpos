import joblib

import pandas as pd

MODEL = joblib.load(
    "ml/anomaly_model.pkl"
)

MODEL_ACCURACY = joblib.load(
    "ml/model_accuracy.pkl"
)

def calculate_risk_score(
    consumed,
    generated,
    grid_usage,
    carbon
):

    score = 0

    if consumed > 1500:
        score += 40

    elif consumed > 800:
        score += 20

    if grid_usage > 1200:
        score += 30

    elif grid_usage > 500:
        score += 15

    if carbon > 500:
        score += 30

    elif carbon > 200:
        score += 15

    return min(
        score,
        100
    )


def get_risk_level(score):

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 30:
        return "MEDIUM"

    return "LOW"


def generate_recommendation(level):

    recommendations = {

        "LOW":
            "System operating normally",

        "MEDIUM":
            "Monitor energy usage trends",

        "HIGH":
            "Reduce peak-hour consumption",

        "CRITICAL":
            "Immediate investigation required"
    }

    return recommendations[level]

def should_create_ai_alert(level):

    return level in [
        "HIGH",
        "CRITICAL"
    ]

def predict_anomaly(
    entity_id,
    entity_type,
    district,
    weather,
    peak_hour,
    temperature,
    consumed,
    generated,
    grid_usage,
    energy_price,
    carbon
):

    row = {
        "entity_id": entity_id,
        "temperature": temperature,
        "energy_consumed_kwh": consumed,
        "energy_generated_kwh": generated,
        "grid_usage_kwh": grid_usage,
        "energy_price": energy_price,
        "carbon_emission_kg": carbon,

        "entity_type_Apartment": 0,
        "entity_type_Factory": 0,
        "entity_type_Hospital": 0,
        "entity_type_House": 0,
        "entity_type_Office": 0,
        "entity_type_School": 0,
        "entity_type_SolarFarm": 0,
        "entity_type_University": 0,

        "district_District-A": 0,
        "district_District-B": 0,
        "district_District-C": 0,
        "district_District-D": 0,
        "district_District-E": 0,

        "weather_Cloudy": 0,
        "weather_Rainy": 0,
        "weather_Sunny": 0,
        "weather_Windy": 0,

        "peak_hour_No": 0,
        "peak_hour_Yes": 0
    }

    row[f"entity_type_{entity_type}"] = 1
    row[f"district_{district}"] = 1
    row[f"weather_{weather}"] = 1
    row[f"peak_hour_{peak_hour}"] = 1

    df = pd.DataFrame([row])

    prediction = MODEL.predict(df)[0]

    return prediction

def get_ai_monitoring_data():

    data = pd.read_csv(
        "ml/datasets/smart_city_energy_data.csv"
    )

    data["anomaly"] = (
        (
            data["grid_usage_kwh"] > 1000
        )
        |
        (
            data["carbon_emission_kg"] > 400
        )
        |
        (
            data["energy_consumed_kwh"] > 1500
        )
    ).astype(int)

    total_records = len(data)

    anomalies = int(
        data["anomaly"].sum()
    )

    anomaly_rate = round(
        (anomalies / total_records) * 100,
        2
    )

    if anomaly_rate > 20:

        score = 90

    elif anomaly_rate > 10:

        score = 60

    elif anomaly_rate > 5:

        score = 30

    else:

        score = 10

    level = get_risk_level(
        score
    )

    recommendation = (
        generate_recommendation(
            level
        )
    )

    return {
    "accuracy": round(
        MODEL_ACCURACY * 100,
        2
    ),
    "anomalies": anomalies,
    "anomaly_rate": anomaly_rate,
    "risk_score": score,
    "risk_level": level,
    "recommendation": recommendation,
    "confidence": round(
        100 - anomaly_rate,
        2
    ),
    "total_records": total_records,
    "insight": f"{anomalies} anomalies detected in the smart grid",
    "action": recommendation
}