import pandas as pd
import numpy as np
import os

module_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(module_dir, "sharesdebtissue.csv", )

df = pd.read_csv(csv_path, sep=';')
df['Issue Date'] = pd.to_datetime(df['Dates: Issue Date'], format="%d-%m-%Y", errors='coerce')
# df = df.dropna(subset=["Dates: Issue Date"])

def classify_issue(issue_type):
    if pd.isna(issue_type):
        return 'Unknown'
    
    issue_type = issue_type.strip().lower()
    if issue_type in ['ipo', 'follow-on']:
        return 'Equity'
    return 'Debt'

df["Issuance Type"] = df["Issue Type"].apply(classify_issue)
# df = df.dropna(subset=["Proceeds"])

df["Proceeds"] = pd.to_numeric(
    df["Proceeds Amount Incl Overallotment Sold All Markets"].str.replace(',', '.', regex=False),
    errors='coerce'
)
df["Month"] = df["Issue Date"].dt.to_period("M")

monthly = df.groupby(["Month", "Issuance Type"])["Proceeds"].sum().unstack(fill_value=0)
monthly["Equity-to-Debt Ratio"] = monthly.get("Equity", 0) / monthly.get("Debt", 1)

monthly = monthly.reset_index()
monthly["Month"] = monthly["Month"].astype(str)

print(monthly)

monthly.to_csv("./monthlyequitytodebtratio.csv")