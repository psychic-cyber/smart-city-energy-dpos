from datetime import datetime, timedelta

from database.mongodb.mongo_manager import db
from database.mongodb.user_repository import get_all_users
from database.mongodb.marketplace_repository import get_marketplace_transactions


def clean_user(user):
    return {
        "username": user.get("username"),
        "role": user.get("role"),
        "energy_generated": user.get("energy_generated", 0),
        "energy_consumed": user.get("energy_consumed", 0),
        "total_revenue": user.get("total_revenue", 0),
    }


def get_daily_report():
    today = datetime.now().date()

    records = list(
        db.energy_records.find({}, {"_id": 0})
    )

    transactions = list(
        db.user_transactions.find({}, {"_id": 0})
    )

    daily_records = []

    for r in records:
        created = datetime.fromisoformat(
            r["created_at"]
        ).date()

        if created == today:
            daily_records.append(r)

    daily_transactions = []

    for t in transactions:
        created = datetime.fromisoformat(
            t["timestamp"]
        ).date()

        if created == today:
            daily_transactions.append(t)

    return build_report(
        daily_records,
        daily_transactions,
        [
            transaction for transaction in get_marketplace_transactions()
            if datetime.fromisoformat(transaction["timestamp"]).date() == today
        ],
    )


def get_weekly_report():
    start_date = datetime.now() - timedelta(days=7)

    records = list(
        db.energy_records.find({}, {"_id": 0})
    )

    transactions = list(
        db.user_transactions.find({}, {"_id": 0})
    )

    weekly_records = []

    for r in records:
        created = datetime.fromisoformat(
            r["created_at"]
        )

        if created >= start_date:
            weekly_records.append(r)

    weekly_transactions = []

    for t in transactions:
        created = datetime.fromisoformat(
            t["timestamp"]
        )

        if created >= start_date:
            weekly_transactions.append(t)

    return build_report(
        weekly_records,
        weekly_transactions,
        get_marketplace_transactions(start_date),
    )


def get_monthly_report():
    start_date = datetime.now() - timedelta(days=30)

    records = list(
        db.energy_records.find({}, {"_id": 0})
    )

    transactions = list(
        db.user_transactions.find({}, {"_id": 0})
    )

    monthly_records = []

    for r in records:
        created = datetime.fromisoformat(
            r["created_at"]
        )

        if created >= start_date:
            monthly_records.append(r)

    monthly_transactions = []

    for t in transactions:
        created = datetime.fromisoformat(
            t["timestamp"]
        )

        if created >= start_date:
            monthly_transactions.append(t)

    return build_report(
        monthly_records,
        monthly_transactions,
        get_marketplace_transactions(start_date),
    )


def build_report(records, transactions, marketplace_transactions=None):
    marketplace_transactions = marketplace_transactions or []
    generated = sum(
        float(r.get("energy_generated", 0))
        for r in records
    )

    consumed = sum(
        float(r.get("energy_consumed", 0))
        for r in records
    )

    revenue = sum(
        float(t.get("revenue", 0))
        for t in transactions
    )

    efficiency = (
        generated / consumed * 100
        if consumed
        else 0
    )

    if efficiency > 100:
        efficiency = 100

    co2_saved = generated * 0.7

    users = [
    u
    for u in get_all_users()
    if u.get("role") != "Admin"
]

    top_producers = sorted(
        users,
        key=lambda x: float(
            x.get("energy_generated", 0)
        ),
        reverse=True,
    )[:5]

    top_consumers = sorted(
        users,
        key=lambda x: float(
            x.get("energy_consumed", 0)
        ),
        reverse=True,
    )[:5]

    top_producers = [
        clean_user(u)
        for u in top_producers
    ]

    top_consumers = [
        clean_user(u)
        for u in top_consumers
    ]

    return {
        "revenue": round(revenue, 2),
        "generated": round(generated, 2),
        "consumed": round(consumed, 2),
        "efficiency": round(efficiency, 2),
        "co2_saved": round(co2_saved, 2),
        "transactions": len(transactions),
        "top_producers": top_producers,
        "top_consumers": top_consumers,
        "marketplace_transactions": marketplace_transactions,
    }
