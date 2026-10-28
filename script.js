
"use strict";

// Glowing cursor follows the pointer.
const cursorGlow = document.querySelector(".cursor-glow");

if (cursorGlow && window.matchMedia("(pointer: fine)").matches) {
  let pointerX = 0;
  let pointerY = 0;
  let frameRequested = false;

  document.addEventListener("pointermove", (event) => {
    pointerX = event.clientX;
    pointerY = event.clientY;

    if (!frameRequested) {
      frameRequested = true;

      requestAnimationFrame(() => {
        cursorGlow.style.left = `${pointerX}px`;
        cursorGlow.style.top = `${pointerY}px`;
        frameRequested = false;
      });
    }
  });
}

// Reveal sections as they enter the viewport.
const revealItems = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.12,
      rootMargin: "0px 0px -35px 0px"
    }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("visible"));
}

// Keep in-page navigation smooth.
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", (event) => {
    const targetId = link.getAttribute("href");
    const target = targetId ? document.querySelector(targetId) : null;

    if (target) {
      event.preventDefault();
      target.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
        block: "start"
      });
    }
  });
});

// Frontend-only form test. No AI prediction is made here.
const fraudForm = document.querySelector("#fraud-form");
const resultBox = document.querySelector("#result");
const resultTitle = document.querySelector("#result-title");
const resultDescription = document.querySelector("#result-description");
const resultScore = document.querySelector("#result-score");

if (fraudForm && resultBox) {
  fraudForm.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!fraudForm.reportValidity()) return;

    const formData = new FormData(fraudForm);
    const amount = Number(formData.get("transaction_amount"));
    const hour = Number(formData.get("transaction_hour"));
    const failedAttempts = Number(formData.get("failed_attempts"));
    const accountAge = Number(formData.get("account_age_days"));

    if (
      !Number.isFinite(amount) ||
      !Number.isFinite(hour) ||
      !Number.isFinite(failedAttempts) ||
      !Number.isFinite(accountAge) ||
      amount < 0 ||
      !Number.isInteger(hour) ||
      hour < 0 ||
      hour > 23 ||
      !Number.isInteger(failedAttempts) ||
      failedAttempts < 0 ||
      !Number.isInteger(accountAge) ||
      accountAge < 0
    ) {
      resultBox.hidden = false;
      resultTitle.textContent = "Check your inputs";
      resultDescription.textContent =
        "Enter valid non-negative values and a whole-number transaction hour from 0 to 23.";
      resultScore.textContent = "";
      return;
    }

    resultBox.hidden = false;
    resultTitle.textContent = "Interface test successful";
    resultDescription.textContent =
      "Your six transaction fields were collected and validated by the website.";
    resultScore.textContent =
      "Next step: connect this form to the Python Random Forest API for actual model predictions.";

    resultBox.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });
  });
}
