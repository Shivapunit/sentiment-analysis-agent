import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(texts):
    df = pd.DataFrame(texts, columns=["text"])
    df["compound"] = df["text"].apply(lambda t: analyzer.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].apply(lambda c: "Positive" if c >= 0.05 else "Negative" if c <= -0.05 else "Neutral")
    return df
