
const fraudForm = document.querySelector("#fraud-form");
const resultBox = document.querySelector("#result");
const resultTitle = document.querySelector("#result-title");
const resultDescription = document.querySelector("#result-description");
const resultScore = document.querySelector("#result-score");

if (fraudForm && resultBox) {
  fraudForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!fraudForm.reportValidity()) return;

    const formData = new FormData(fraudForm);

    const transaction = {
      transaction_amount: Number(formData.get("transaction_amount")),
      transaction_hour: Number(formData.get("transaction_hour")),
      new_device: Number(formData.get("new_device")),
      international_transaction: Number(
        formData.get("international_transaction")
      ),
      failed_attempts: Number(formData.get("failed_attempts")),
      account_age_days: Number(formData.get("account_age_days"))
    };

    resultBox.hidden = false;
    resultTitle.textContent = "Analyzing transaction...";
    resultDescription.textContent = "Contacting the Sentinel AI model...";
    resultScore.textContent = "";

    try {
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transaction)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Prediction request failed.");
      }

      const score = Number(data.model_estimated_fraud_score);

      resultTitle.textContent =
        data.prediction === 1
          ? "Potential Fraud Detected"
          : "Likely Legitimate";

      resultDescription.textContent =
        data.prediction === 1
          ? "The model flagged this transaction as potentially fraudulent."
          : "The model classified this transaction as likely legitimate.";

      resultScore.textContent =
        `Model-estimated fraud score: ${(score * 100).toFixed(2)}%. ` +
        (data.warning || "Educational model only.");

    } catch (error) {
      resultTitle.textContent = "Analysis unavailable";
      resultDescription.textContent =
        `${error.message} Check that the API is running.`;
      resultScore.textContent = "";
    }

    resultBox.scrollIntoView({
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth",
      block: "nearest"
    });
  });
}
