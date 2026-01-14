# ai/preprocessor_fraud.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

def load_and_vectorize(csv_path="ai/data/training_data.csv"):
    """
    Load CSV, clean text, and vectorize for ML model.
    Expects columns: title, description, label (0=legit, 1=fraud)
    """
    df = pd.read_csv(csv_path)
    df['text'] = df['title'].astype(str) + " " + df['description'].astype(str)
    X = df['text'].values
    y = df['label'].values

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y, test_size=0.2, random_state=42, stratify=y
    )
    return X_train, X_test, y_train, y_test, vectorizer
