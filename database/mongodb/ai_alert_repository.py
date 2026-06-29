from database.mongodb.mongo_manager import (
    db
)

VALID_SEVERITY_LEVELS = (
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
)


def get_ai_alert_collection():

    return db[
        "ai_alerts"
    ]


def _normalize_severity(level):
    normalized = str(level or "LOW").upper()
    if normalized not in VALID_SEVERITY_LEVELS:
        return "LOW"
    return normalized


def save_ai_alert(alert):
    alert = dict(alert)
    severity = _normalize_severity(
        alert.get("severity", alert.get("risk_level"))
    )
    alert["severity"] = severity
    alert["risk_level"] = severity

    get_ai_alert_collection().insert_one(
        alert
    )

    return alert


def count_ai_alerts():

    return (
        get_ai_alert_collection()
        .count_documents({})
    )


def count_alerts_by_severity(severity):
    normalized = _normalize_severity(severity)
    return get_ai_alert_collection().count_documents(
        {
            "$or": [
                {"severity": normalized},
                {"risk_level": normalized},
            ]
        }
    )


def count_critical_alerts():
    return count_alerts_by_severity("CRITICAL")


def get_latest_ai_alert():

    return (
        get_ai_alert_collection()
        .find_one(
            {},
            sort=[
                (
                    "timestamp",
                    -1
                )
            ]
        )
    )


def get_all_ai_alerts(limit=None):

    cursor = (
        get_ai_alert_collection()
        .find(
            {},
            {
                "_id": 0
            }
        )
        .sort(
            "timestamp",
            -1
        )
    )

    if limit:
        cursor = cursor.limit(limit)

    alerts = list(cursor)

    for alert in alerts:
        alert["severity"] = _normalize_severity(
            alert.get("severity", alert.get("risk_level"))
        )
        alert["risk_level"] = alert["severity"]

    return alerts


def get_alerts_by_severity(severity, limit=20):
    normalized = _normalize_severity(severity)
    alerts = list(
        get_ai_alert_collection()
        .find(
            {
                "$or": [
                    {"severity": normalized},
                    {"risk_level": normalized},
                ]
            },
            {"_id": 0},
        )
        .sort("timestamp", -1)
        .limit(limit)
    )

    for alert in alerts:
        alert["severity"] = normalized
        alert["risk_level"] = normalized

    return alerts
