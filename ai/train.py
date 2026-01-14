# ai/train.py
import pickle
from sklearn.naive_bayes import MultinomialNB
from ai.preprocess import load_and_vectorize

X, y_cat, y_sev, vectorizer = load_and_vectorize()

cat_model = MultinomialNB()
sev_model = MultinomialNB()

cat_model.fit(X, y_cat)
sev_model.fit(X, y_sev)

with open("ai/artifacts/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("ai/artifacts/category_model.pkl", "wb") as f:
    pickle.dump(cat_model, f)

with open("ai/artifacts/severity_model.pkl", "wb") as f:
    pickle.dump(sev_model, f)

print("✅ AI models trained and saved")
