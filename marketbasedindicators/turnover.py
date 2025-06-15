import pandas as pd
import re

df = pd.read_csv("./marketbasedindicators/aexturnover1.csv")
turnover_cols = [col for col in df.columns if "TURNOVER BY VOLUME" in col]

shares_cols = [
    col for col in df.columns
    if re.search(r'SHARES OUTSTANDING$', col)
]
print(shares_cols)

df['total_turnover'] = df[turnover_cols].sum(axis=1)
df['total_shares'] = df[shares_cols].sum(axis=1)
df['turnover_per_share'] = df['total_turnover'] / df['total_shares']
df.set_index('date', inplace=True)

df['rolling_avg_turnover'] = df['turnover_per_share'].rolling(window=60, min_periods=1).mean()
df['detrended_turnover'] = df['turnover_per_share'] - df['rolling_avg_turnover']
df['detrended_turnover'] = df['detrended_turnover'] * 50
df = df[['detrended_turnover', 'turnover_per_share','total_turnover', 'total_shares']]
df.to_csv("./marketbasedindicators/aexturnover.csv")