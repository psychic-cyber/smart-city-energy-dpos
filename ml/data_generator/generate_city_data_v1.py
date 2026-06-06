import csv
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "ml/datasets/smart_city_energy_data.csv"
NUM_RECORDS = 10000

DISTRICTS = [
    "District-A",
    "District-B",
    "District-C",
    "District-D",
    "District-E"
]

WEATHER_TYPES = [
    "Sunny",
    "Cloudy",
    "Rainy",
    "Windy"
]

ENTITY_CONFIG = {
    "House": (5, 40),
    "Apartment": (20, 80),
    "School": (100, 300),
    "University": (200, 500),
    "Hospital": (300, 1000),
    "Office": (100, 400),
    "Factory": (500, 3000),
    "SolarFarm": (100, 500)
}


def generate_record(record_id):

    entity_type = random.choice(list(ENTITY_CONFIG.keys()))

    district = random.choice(DISTRICTS)

    weather = random.choice(WEATHER_TYPES)

    temperature = random.randint(15, 45)

    timestamp = datetime.now() - timedelta(
        hours=random.randint(0, 720)
    )

    hour = timestamp.hour

    peak_hour = "Yes" if (
        7 <= hour <= 10 or
        17 <= hour <= 22
    ) else "No"

    min_energy, max_energy = ENTITY_CONFIG[entity_type]

    energy_consumed = round(
        random.uniform(min_energy, max_energy),
        2
    )

    if peak_hour == "Yes":
        energy_consumed *= 1.25

    if weather == "Rainy":
        energy_consumed *= 1.10

    energy_consumed = round(
        energy_consumed,
        2
    )

    if entity_type == "SolarFarm":

        solar_factor = {
            "Sunny": 1.0,
            "Cloudy": 0.60,
            "Windy": 0.80,
            "Rainy": 0.30
        }

        energy_generated = round(
            random.uniform(1000, 10000) *
            solar_factor[weather],
            2
        )

    else:

        energy_generated = round(
            random.uniform(0, energy_consumed * 0.60),
            2
        )

    grid_usage = round(
        max(0, energy_consumed - energy_generated),
        2
    )

    energy_price = round(
        random.uniform(0.15, 0.40),
        2
    )

    carbon_emission = round(
        grid_usage * 0.45,
        2
    )

    anomaly = "Yes" if random.random() < 0.03 else "No"

    return [
        record_id,
        entity_type,
        district,
        weather,
        temperature,
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        peak_hour,
        energy_consumed,
        energy_generated,
        grid_usage,
        energy_price,
        carbon_emission,
        anomaly
    ]


def generate_dataset():

    with open(
        OUTPUT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "entity_id",
            "entity_type",
            "district",
            "weather",
            "temperature",
            "timestamp",
            "peak_hour",
            "energy_consumed_kwh",
            "energy_generated_kwh",
            "grid_usage_kwh",
            "energy_price",
            "carbon_emission_kg",
            "anomaly"
        ])

        for i in range(
            1,
            NUM_RECORDS + 1
        ):
            writer.writerow(
                generate_record(i)
            )

    print(
        f"Dataset generated successfully: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    generate_dataset()