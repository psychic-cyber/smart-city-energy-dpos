import csv

from blockchain.core.blockchain import Blockchain

from blockchain.dpos.delegate import Delegate
from blockchain.dpos.consensus import DPoSConsensus

from blockchain.storage.storage_manager import save_blockchain

from database.models.energy_transaction import EnergyTransaction


def load_dataset():

    blockchain = Blockchain()

    consensus = DPoSConsensus()

    consensus.register_delegate(
        Delegate(1, "District-A", 150)
    )

    consensus.register_delegate(
        Delegate(2, "District-B", 300)
    )

    consensus.register_delegate(
        Delegate(3, "District-C", 450)
    )

    consensus.register_delegate(
        Delegate(4, "District-D", 250)
    )

    consensus.register_delegate(
        Delegate(5, "District-E", 100)
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

            selected_delegate = (
                consensus.select_delegate()
            )

            blockchain.add_block(
                transaction.to_dict(),
                selected_delegate.district
            )

            count += 1

            if count >= 10:
                break

    print(
        f"\nTotal Blocks: {len(blockchain.chain)}"
    )

    save_blockchain(
        blockchain.chain
        )
    
    print(
        "\nBlockchain saved successfully."
        )

    blockchain.display_chain()

    print(
        "\nChain Valid:",
        blockchain.is_chain_valid()
    )


if __name__ == "__main__":
    load_dataset()
