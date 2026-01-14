# ai/split_training_data.py
import os
import pandas as pd

MASTER = "ai/data/training_data.csv"
OUT_CATSEV = "ai/data/training_category_severity.csv"
OUT_FRAUD = "ai/data/fraud_training_data.csv"

VALID_CATEGORIES = {"Road", "Water", "Electricity", "Sanitation", "Law & Order"}

def main():
    if not os.path.exists(MASTER):
        raise FileNotFoundError(f"Missing: {MASTER}")

    df = pd.read_csv(MASTER)

    # Normalize column names just in case
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"title", "description", "label", "category", "severity"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}. Found: {list(df.columns)}")

    # ---- Fraud dataset (text + label) ----
    fraud_df = df[["title", "description", "label"]].copy()
    fraud_df["text"] = fraud_df["title"].astype(str) + " " + fraud_df["description"].astype(str)
    fraud_df["label"] = fraud_df["label"].astype(int)
    fraud_df = fraud_df[["text", "label"]]
    fraud_df.to_csv(OUT_FRAUD, index=False)

    # ---- Category+Severity dataset (ONLY civic categories) ----
    catsev_df = df[["title", "description", "category", "severity"]].copy()
    catsev_df["category"] = catsev_df["category"].astype(str).str.strip()

    # Keep only valid civic categories (removes Spam automatically)
    catsev_df = catsev_df[catsev_df["category"].isin(VALID_CATEGORIES)].copy()

    # Ensure severity numeric and within 1..5
    catsev_df["severity"] = pd.to_numeric(catsev_df["severity"], errors="coerce")
    catsev_df = catsev_df.dropna(subset=["severity"])
    catsev_df["severity"] = catsev_df["severity"].astype(int)
    catsev_df = catsev_df[(catsev_df["severity"] >= 1) & (catsev_df["severity"] <= 5)]

    catsev_df.to_csv(OUT_CATSEV, index=False)

    print("✅ Done!")
    print(f"Fraud dataset: {OUT_FRAUD}  (rows={len(fraud_df)})")
    print(f"Category+Severity dataset: {OUT_CATSEV} (rows={len(catsev_df)})")

if __name__ == "__main__":
    main()
