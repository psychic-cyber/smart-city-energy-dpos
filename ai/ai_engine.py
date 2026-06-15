def generate_ai_insight(
    anomaly_rate,
    efficiency
):

    if anomaly_rate > 20:

        risk = "HIGH"

        insight = (
            "Abnormal energy activity detected."
        )

        recommendation = (
            "Inspect high-consumption entities."
        )

        action = (
            "Immediate investigation required."
        )

    elif anomaly_rate > 10:

        risk = "MEDIUM"

        insight = (
            "Energy usage pattern is unstable."
        )

        recommendation = (
            "Monitor energy trends closely."
        )

        action = (
            "Schedule maintenance review."
        )

    else:

        risk = "LOW"

        insight = (
            "System operating normally."
        )

        recommendation = (
            "Maintain current energy strategy."
        )

        action = (
            "No immediate action required."
        )

    return {
        "risk": risk,
        "insight": insight,
        "recommendation": recommendation,
        "action": action
    }
