from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score

ROOT = Path(__file__).resolve().parent
df = pd.read_csv(ROOT / "data" / "categorization_training.csv")
df = df.dropna(subset=["description", "category"])
df["description"] = df["description"].astype(str).str.strip()
df = df[df["description"] != ""].drop_duplicates()

X_train, X_test, y_train, y_test = train_test_split(
    df["description"], df["category"], test_size=0.2,
    random_state=42, stratify=df["category"]
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
    ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced"))
])
model.fit(X_train, y_train)
pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, pred):.3f}")
print(f"Macro-F1: {f1_score(y_test, pred, average='macro'):.3f}")
print(classification_report(y_test, pred, zero_division=0))

(ROOT / "models").mkdir(exist_ok=True)
joblib.dump(model, ROOT / "models" / "expense_classifier.joblib")
print("Saved models/expense_classifier.joblib")
