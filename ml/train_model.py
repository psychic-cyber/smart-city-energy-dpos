import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

data = pd.read_csv(
    "ml/datasets/smart_city_energy_data.csv"
)

data["anomaly"] = (
    (
        data["grid_usage_kwh"] > 1000
    )
    |
    (
        data["carbon_emission_kg"] > 400
    )
    |
    (
        data["energy_consumed_kwh"] > 1500
    )
).astype(int)

categorical_cols = [
    "entity_type",
    "district",
    "weather",
    "peak_hour"
]

data = pd.get_dummies(
    data,
    columns=categorical_cols
)

X = data.drop(
    columns=[
        "anomaly",
        "timestamp"
    ]
)

y = data["anomaly"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced"
)

model.fit(
    X_train,
    y_train
)

predictions = model.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\nAccuracy:")
print(accuracy)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        predictions
    )
)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        predictions
    )
)

joblib.dump(
    model,
    "ml/anomaly_model.pkl"
)

joblib.dump(
    X.columns.tolist(),
    "ml/model_features.pkl"
)

print(
    "\nModel Saved Successfully"
)