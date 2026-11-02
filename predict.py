
from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "expense_classifier.joblib"

model = joblib.load(MODEL_PATH)

# Initial heuristic only; tune this on held-out validation data.
CONFIDENCE_THRESHOLD = 0.40

while True:
    description = input(
        "\nTransaction description (or exit): "
    ).strip()

    if description.lower() == "exit":
        break

    if not description:
        print("Please enter a transaction description.")
        continue

    probabilities = model.predict_proba([description])[0]
    best_index = probabilities.argmax()

    category = model.classes_[best_index]
    confidence = probabilities[best_index]

    if confidence < CONFIDENCE_THRESHOLD:
        print("Category: Needs Review")
        print(f"Suggested category: {category}")
        print(f"Model confidence: {confidence:.1%}")
    else:
        print("Category:", category)
        print(f"Model confidence: {confidence:.1%}")
