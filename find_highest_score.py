import itertools
import joblib
import pandas as pd

bundle = joblib.load("fraud_model.joblib")
model = bundle["model"]
features = bundle["features"]

# Plausible and extreme test values for each feature
values = {
    "transaction_amount": [100, 1000, 5000, 25000, 100000, 999999],
    "transaction_hour": [0, 1, 2, 3, 4, 8, 12, 18, 22, 23],
    "new_device": [0, 1],
    "international_transaction": [0, 1],
    "failed_attempts": [0, 1, 3, 5, 10, 20],
    "account_age_days": [0, 1, 3, 7, 30, 90, 365, 1000],
}

names = list(values)
combinations = itertools.product(*(values[name] for name in names))
rows = [dict(zip(names, combo)) for combo in combinations]

df = pd.DataFrame(rows, columns=features)
scores = model.predict_proba(df)[:, 1]
df["fraud_score"] = scores

print(f"Transactions tested: {len(df):,}")
print(f"Highest fraud score: {df['fraud_score'].max():.2%}")
print(f"Lowest fraud score: {df['fraud_score'].min():.2%}")
print("\nTop 10 highest-scoring combinations:")
print(
    df.sort_values("fraud_score", ascending=False)
      .head(10)
      .to_string(index=False)
)
