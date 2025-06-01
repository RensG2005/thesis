import pandas as pd


df = pd.read_csv("marketbasedindicators/closedendfunds/lista-if-nl.csv")

df = df[df["INVESTMENT POLICY"] == "Equities"]

df = df[df["CAPITAL VARIABILITY"] == "Closed"]

print(df["ISIN CODE"])
