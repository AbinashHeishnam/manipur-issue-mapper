def predict_issue(title: str, description: str):
    text = f"{title}. {description}".lower()

    if "road" in text or "pothole" in text:
        return "Road Infrastructure", 4
    elif "electric" in text or "power" in text:
        return "Electricity", 3
    elif "water" in text or "pipe" in text:
        return "Water Supply", 3
    elif "garbage" in text:
        return "Municipal", 2
    else:
        return "General", 1
