from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "synthetic_transactions.csv"
MODEL_PATH = BASE_DIR / "fraud_model_candidate.joblib"

FEATURES = [
    "transaction_amount",
    "transaction_hour",
    "new_device",
    "international_transaction",
    "failed_attempts",
    "account_age_days",
]
TARGET = "is_fraud"

# Generate reproducible EDUCATIONAL synthetic data.
rng = np.random.default_rng(42)
n = 12000

df = pd.DataFrame({
    "transaction_amount": rng.lognormal(7.5, 1.2, n).clip(10, 500000),
    "transaction_hour": rng.integers(0, 24, n),
    "new_device": rng.integers(0, 2, n),
    "international_transaction": rng.integers(0, 2, n),
    "failed_attempts": rng.poisson(0.7, n).clip(0, 10),
    "account_age_days": rng.integers(0, 2001, n),
})

# Synthetic labeling rule; this is not a real-world fraud detector.
risk = (
    1.0 * df["new_device"]
    + 0.8 * df["international_transaction"]
    + 0.35 * df["failed_attempts"]
    + 0.9 * (df["account_age_days"] < 14)
    + 0.7 * ((df["transaction_hour"] <= 4) | (df["transaction_hour"] >= 23))
    + 0.5 * (df["transaction_amount"] > 20000)
)
probability = 1 / (1 + np.exp(-(risk - 2.0)))
df[TARGET] = rng.binomial(1, probability)

df.to_csv(DATA_PATH, index=False)

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = Pipeline([
    ("classifier", RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    ))
])

model.fit(X_train, y_train)
predictions = model.predict(X_test)
scores = model.predict_proba(X_test)[:, 1]

print("Synthetic dataset created:", DATA_PATH.name)
print("Fraud rate in generated data:", f"{y.mean():.2%}")
print("\nEvaluation on held-out synthetic examples:")
print(classification_report(y_test, predictions, zero_division=0))
print("ROC-AUC:", round(roc_auc_score(y_test, scores), 3))

joblib.dump(
    {"model": model, "features": FEATURES, "target": TARGET},
    MODEL_PATH,
)
print("\nCandidate model saved as:", MODEL_PATH.name)
print("Your current fraud_model.joblib has NOT been changed.")
print("Reminder: this model learns synthetic labeling rules, not real fraud.")
