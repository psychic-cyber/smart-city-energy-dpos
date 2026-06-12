import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

data = pd.read_csv(
    "ml/datasets/smart_city_energy_data.csv"
)

data["anomaly"] = data["anomaly"].map(
    {
        "No": 0,
        "Yes": 1
    }
)

X = data[
    [
        "energy_consumed_kwh",
        "energy_generated_kwh"
    ]
]

y = data["anomaly"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier()

model.fit(
    X_train,
    y_train
)

joblib.dump(
    model,
    "ml/anomaly_model.pkl"
)

print(
    "Model Trained Successfully"
)