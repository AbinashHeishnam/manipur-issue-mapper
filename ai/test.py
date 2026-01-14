# ai/test.py
from predict_fraud import predict_fraud

examples = [
    ("Garbage not collected", "Garbage everywhere, people complain"),
    ("asdf qwer zxcv", "random nonsense text"),
]

for title, desc in examples:
    result = predict_fraud(title, desc)
    print(f"Title: {title}\nDescription: {desc}\nFraud Prediction: {result}\n")
