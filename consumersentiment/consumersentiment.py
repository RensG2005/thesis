import pandas as pd
from utils.normalize import normalize
import os

module_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(module_dir, "consumentenconfidenceCBS.csv")

cs_sentiment_df = pd.read_csv(csv_path)

cs_sentiment_df["date"] = pd.to_datetime(cs_sentiment_df["date"])

cs_sentiment_df = normalize(cs_sentiment_df, "Consumer confidence")
cs_sentiment_df = normalize(cs_sentiment_df, "Economic climate")
cs_sentiment_df = normalize(cs_sentiment_df, "Willingness to buy")
cs_sentiment_df = normalize(cs_sentiment_df, "Economic situation next 12 months")

#TODO composite the above indices

def load_df():
    return cs_sentiment_df