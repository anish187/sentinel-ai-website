from pathlib import Path
import joblib
import pandas as pd

model_path = Path("fraud_model.joblib")
bundle = joblib.load(model_path)

model = bundle["model"]
features = bundle["features"]

tests = [
    {
        "transaction_amount": 999999,
        "transaction_hour": 3,
        "new_device": 1,
        "international_transaction": 1,
        "failed_attempts": 20,
        "account_age_days": 0,
    },
    {
        "transaction_amount": 5000,
        "transaction_hour": 2,
        "new_device": 1,
        "international_transaction": 1,
        "failed_attempts": 5,
        "account_age_days": 3,
    },
    {
        "transaction_amount": 100000,
        "transaction_hour": 23,
        "new_device": 1,
        "international_transaction": 1,
        "failed_attempts": 10,
        "account_age_days": 1,
    },
]

for i, transaction in enumerate(tests, start=1):
    row = pd.DataFrame([transaction], columns=features)
    prediction = int(model.predict(row)[0])
    score = float(model.predict_proba(row)[0][1])

    print(f"\nTest {i}")
    print(f"Prediction: {prediction}")
    print(f"Fraud score: {score:.2%}")
    print(f"Inputs: {transaction}")
