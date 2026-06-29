from database.mongodb.mongo_manager import db


def get_ai_history_collection():
    return db["ai_prediction_history"]


def save_ai_history(record):
    get_ai_history_collection().insert_one(record)
    record.pop("_id", None)
    return record


def get_ai_history(limit=50):
    return list(
        get_ai_history_collection()
        .find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )


def count_predictions():
    return get_ai_history_collection().count_documents({})


def get_history_statistics():
    records = list(
        get_ai_history_collection().find(
            {},
            {
                "_id": 0,
                "confidence": 1,
                "risk_level": 1,
                "prediction": 1,
            },
        )
    )

    if not records:
        return {
            "average_confidence": 0,
            "average_accuracy": 0,
            "highest_risk": None,
            "lowest_risk": None,
        }

    confidences = [
        float(record.get("confidence", 0))
        for record in records
        if record.get("confidence") is not None
    ]
    risks = [
        record.get("risk_level")
        for record in records
        if record.get("risk_level")
    ]
    risk_rank = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    highest_risk = None
    lowest_risk = None
    if risks:
        highest_risk = max(risks, key=lambda level: risk_rank.get(level, 0))
        lowest_risk = min(risks, key=lambda level: risk_rank.get(level, 99))

    return {
        "average_confidence": round(
            sum(confidences) / len(confidences),
            2,
        ) if confidences else 0,
        "average_accuracy": round(
            sum(confidences) / len(confidences),
            2,
        ) if confidences else 0,
        "highest_risk": highest_risk,
        "lowest_risk": lowest_risk,
    }
