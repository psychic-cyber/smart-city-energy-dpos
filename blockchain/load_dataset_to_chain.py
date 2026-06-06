import csv

from blockchain.core.blockchain import Blockchain
from database.models.energy_transaction import EnergyTransaction


def load_dataset():

    blockchain = Blockchain()

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

            blockchain.add_block(
                transaction.to_dict()
            )

            count += 1

            if count >= 10:
                break

    print(
        f"\nTotal Blocks: {len(blockchain.chain)}"
    )

    blockchain.display_chain()

    print(
        "\nChain Valid:",
        blockchain.is_chain_valid()
    )


if __name__ == "__main__":
    load_dataset()
