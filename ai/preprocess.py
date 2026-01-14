# ai/preprocess.py
import pandas as pd
from sklearn.model_selection import train_test_split

REQUIRED = {"title", "description", "category", "severity"}

def preprocess(csv_path="ai/data/training_data.csv"):
    df = pd.read_csv(csv_path)

    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}. Required: {REQUIRED}")

    # Clean
    df["title"] = df["title"].astype(str).fillna("")
    df["description"] = df["description"].astype(str).fillna("")
    df["category"] = df["category"].astype(str).fillna("")
    df["severity"] = df["severity"].astype(int)

    # Remove spam rows from category/severity training (fraud model handles spam)
    df = df[df["category"].str.lower() != "spam"].copy()

    df["text"] = df["title"] + " " + df["description"]

    X = df["text"]
    y_cat = df["category"]
    y_sev = df["severity"]

    # ONE split for everything
    X_train, X_test, y_cat_train, y_cat_test, y_sev_train, y_sev_test = train_test_split(
        X, y_cat, y_sev,
        test_size=0.2,
        random_state=42,
        stratify=y_cat
    )

    return X_train, X_test, y_cat_train, y_cat_test, y_sev_train, y_sev_test
