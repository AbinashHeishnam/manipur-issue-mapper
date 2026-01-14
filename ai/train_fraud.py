# ai/train_fraud.py
from ai.fraud import train_fraud_model

if __name__ == "__main__":
    train_fraud_model(threshold=0.65)
