
"""FastAPI backend for the Sentinel AI fraud detection website."""

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "fraud_model.joblib"
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Sentinel AI — Fraud Detection",
    version="1.0.0",
    description="Educational fraud detection prototype using a synthetic-data model.",
)

# Serve CSS and JavaScript from /assets/...
app.mount(
    "/assets",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="assets",
)


class Transaction(BaseModel):
    transaction_amount: float = Field(ge=0)
    transaction_hour: int = Field(ge=0, le=23)
    new_device: int = Field(ge=0, le=1)
    international_transaction: int = Field(ge=0, le=1)
    failed_attempts: int = Field(ge=0)
    account_age_days: int = Field(ge=0)


@app.get("/", include_in_schema=False)
def homepage():
    """Display the custom frontend."""
    index_file = FRONTEND_DIR / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=500,
            detail="frontend/index.html was not found.",
        )

    return FileResponse(index_file)


@app.get("/health")
def health():
    """Check whether the model file is present."""
    return {
        "status": "ok",
        "model_loaded": MODEL_PATH.exists(),
        "frontend_found": (FRONTEND_DIR / "index.html").exists(),
    }


@app.post("/predict")
def predict(transaction: Transaction):
    """Predict using the existing saved model."""
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Model file missing. Run python train_model.py first.",
        )

    try:
        bundle = joblib.load(MODEL_PATH)
        model = bundle["model"]
        features = bundle["features"]

        row = pd.DataFrame(
            [transaction.model_dump()],
            columns=features,
        )

        prediction = int(model.predict(row)[0])
        fraud_score = float(model.predict_proba(row)[0][1])

        return {
            "prediction": prediction,
            "label": (
                "potentially_fraudulent"
                if prediction == 1
                else "legitimate"
            ),
            "model_estimated_fraud_score": round(fraud_score, 4),
            "warning": (
                "Educational synthetic-data model only. "
                "Not suitable for real financial decisions."
            ),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        ) from exc
