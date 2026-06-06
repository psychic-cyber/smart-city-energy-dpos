import csv
import random
from datetime import datetime, timedelta

ENTITY_TYPES = [
    "House",
    "Apartment",
    "School",
    "University",
    "Hospital",
    "Office",
    "Factory",
    "SolarFarm"
]

NUM_RECORDS = 10000

OUTPUT_FILE = "ml/datasets/smart_city_energy_data.csv"


def generate_record(record_id):
    entity_type = random.choice(ENTITY_TYPES)

    timestamp = datetime.now() - timedelta(
        hours=random.randint(0, 720)
    )

    energy_consumed = round(random.uniform(5, 500), 2)

    if entity_type == "SolarFarm":
        energy_generated = round(random.uniform(100, 1000), 2)
    else:
        energy_generated = round(random.uniform(0, 200), 2)

    grid_usage = round(
        max(0, energy_consumed - energy_generated),
        2
    )

    carbon_emission = round(
        grid_usage * random.uniform(0.3, 0.8),
        2
    )

    return [
        record_id,
        entity_type,
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        energy_consumed,
        energy_generated,
        grid_usage,
        carbon_emission
    ]


def generate_dataset():
    with open(OUTPUT_FILE, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "entity_id",
            "entity_type",
            "timestamp",
            "energy_consumed_kwh",
            "energy_generated_kwh",
            "grid_usage_kwh",
            "carbon_emission_kg"
        ])

        for i in range(1, NUM_RECORDS + 1):
            writer.writerow(generate_record(i))

    print(f"Dataset saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_dataset()
