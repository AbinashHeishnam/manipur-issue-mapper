#!/usr/bin/env python3

import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DATA_PATH = "ai/data/veracity_1500.csv"
ART_DIR = "ai/artifacts"

MODEL_PATH = os.path.join(ART_DIR, "veracity_model.pkl")
VECT_PATH  = os.path.join(ART_DIR, "veracity_vectorizer.pkl")

def train():
    os.makedirs(ART_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    # Expecting columns: text,label
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("CSV must contain columns: text,label")

    df["text"] = df["text"].astype(str).fillna("")
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    # map labels
    label_map = {"legit": 0, "fake": 1, "spam": 2}
    y = df["label"].map(label_map)

    # Drop bad/unknown labels safely
    bad = y.isna().sum()
    if bad > 0:
        print(f"⚠️ Dropping {bad} rows with unknown labels (not in {list(label_map.keys())})")
        df = df[~y.isna()].copy()
        y = y[~y.isna()].astype(int)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=8000
    )

    X = vectorizer.fit_transform(df["text"])

    # IMPORTANT: remove multi_class (your sklearn build rejects it)
    # We use multinomial behavior by choosing solver that supports multiclass well
    model = LogisticRegression(
        max_iter=2000,
        solver="lbfgs"
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECT_PATH)

    print("✅ Veracity model trained")
    print("Saved:", MODEL_PATH)
    print("Saved:", VECT_PATH)

if __name__ == "__main__":
    train()
