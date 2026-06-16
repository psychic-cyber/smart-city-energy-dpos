import os
import pandas as pd

from database.mongodb.mongo_manager import db

os.makedirs(
    "powerbi",
    exist_ok=True
)

users = list(
    db.users.find(
        {},
        {
            "_id": 0,
            "password": 0
        }
    )
)

transactions = list(
    db.user_transactions.find(
        {},
        {"_id": 0}
    )
)

energy_records = list(
    db.energy_records.find(
        {},
        {"_id": 0}
    )
)

blocks = list(
    db.blockchain_blocks.find(
        {},
        {"_id": 0}
    )
)

pd.DataFrame(users).to_csv(
    "powerbi/users.csv",
    index=False
)

pd.DataFrame(transactions).to_csv(
    "powerbi/transactions.csv",
    index=False
)

pd.DataFrame(energy_records).to_csv(
    "powerbi/energy_records.csv",
    index=False
)

pd.DataFrame(blocks).to_csv(
    "powerbi/blocks.csv",
    index=False
)

print(
    "Power BI files exported successfully."
)
