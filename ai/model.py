# ai/model.py
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

ART_DIR = "ai/artifacts"
VECT_PATH = os.path.join(ART_DIR, "vectorizer.pkl")
CAT_PATH  = os.path.join(ART_DIR, "category_model.pkl")
SEV_PATH  = os.path.join(ART_DIR, "severity_model.pkl")

def train_models():
    from ai.preprocess import preprocess

    os.makedirs(ART_DIR, exist_ok=True)

    X_train, X_test, y_cat_train, y_cat_test, y_sev_train, y_sev_test = preprocess()

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1,2),
        max_features=8000
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    # Category model
    cat_model = LogisticRegression(max_iter=1500, class_weight="balanced")
    cat_model.fit(X_train_vec, y_cat_train)
    cat_preds = cat_model.predict(X_test_vec)
    print("Category Accuracy:", accuracy_score(y_cat_test, cat_preds))

    # Severity model (multiclass)
    sev_model = LogisticRegression(max_iter=1500, class_weight="balanced")
    sev_model.fit(X_train_vec, y_sev_train)
    sev_preds = sev_model.predict(X_test_vec)
    print("Severity Accuracy:", accuracy_score(y_sev_test, sev_preds))

    joblib.dump(vectorizer, VECT_PATH)
    joblib.dump(cat_model, CAT_PATH)
    joblib.dump(sev_model, SEV_PATH)
    print("AI models saved:", VECT_PATH, CAT_PATH, SEV_PATH)

def predict_issue(title: str, description: str):
    if not (os.path.exists(VECT_PATH) and os.path.exists(CAT_PATH) and os.path.exists(SEV_PATH)):
        raise FileNotFoundError("AI models not trained. Run: python -m ai.model")

    vectorizer = joblib.load(VECT_PATH)
    cat_model  = joblib.load(CAT_PATH)
    sev_model  = joblib.load(SEV_PATH)

    text = f"{title} {description}"
    X = vectorizer.transform([text])

    category = cat_model.predict(X)[0]
    severity = int(sev_model.predict(X)[0])

    return category, severity

if __name__ == "__main__":
    train_models()
