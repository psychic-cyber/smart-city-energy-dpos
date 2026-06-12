import joblib
import pandas as pd

model = joblib.load(
    "ml/anomaly_model.pkl"
)

def predict_anomaly(
    consumed,
    generated
):

    sample = pd.DataFrame(
        {
            "energy_consumed_kwh": [consumed],
            "energy_generated_kwh": [generated]
        }
    )

    prediction = model.predict(
        sample
    )[0]

    return int(
        prediction
    )
