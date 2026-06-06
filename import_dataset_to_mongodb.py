import csv

from database.models.energy_transaction import (
    EnergyTransaction
)

from database.mongodb.transaction_repository import (
    save_transaction,
    count_transactions
)


with open(
    "ml/datasets/smart_city_energy_data.csv",
    "r"
) as file:

    reader = csv.DictReader(file)

    count = 0

    for row in reader:

        bill_amount = (
            float(row["grid_usage_kwh"])
            *
            float(row["energy_price"])
        )

        transaction = EnergyTransaction(
            entity_id=row["entity_id"],
            entity_type=row["entity_type"],
            district=row["district"],
            energy_consumed=row["energy_consumed_kwh"],
            energy_generated=row["energy_generated_kwh"],
            anomaly=row["anomaly"],
            energy_price=row["energy_price"],
            bill_amount=round(
                bill_amount,
                2
            )
        )

        save_transaction(
            transaction.to_dict()
        )

        count += 1

print(
    "Imported Records:",
    count
)

print(
    "Total MongoDB Transactions:",
    count_transactions()
)
