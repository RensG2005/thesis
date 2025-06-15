import pandas as pd
import numpy as np

df = pd.read_csv("./marketbasedindicators/filtered_output.csv")

dividend_cols = [col for col in df.columns if col.endswith('- DIVIDEND YIELD')]
mtb_cols = [col for col in df.columns if col.endswith('- MRKT VALUE TO BOOK')]

dividend_premium = []

for idx, row in df.iterrows():
    mtb_payers = []
    mtb_nonpayers = []

    for div_col in dividend_cols:
        firm = div_col.replace(' - DIVIDEND YIELD', '')
        mtb_col = f'{firm} - MRKT VALUE TO BOOK'
        if mtb_col not in df.columns:
            continue

        div_yield = row[div_col]
        mtb_ratio = row[mtb_col]

        if pd.isna(mtb_ratio):
            continue

        if pd.notna(div_yield) and div_yield > 0:
            mtb_payers.append(mtb_ratio)
        else:
            mtb_nonpayers.append(mtb_ratio)

    # Calculate average for each group if not empty
    avg_payers = sum(mtb_payers) / len(mtb_payers) if mtb_payers else None
    avg_nonpayers = sum(mtb_nonpayers) / len(mtb_nonpayers) if mtb_nonpayers else None

    premium = 0
    if avg_payers is not None and avg_nonpayers is not None:
        premium = np.log(avg_payers / avg_nonpayers)

    dividend_premium.append(premium)

# Add the dividend premium to the original DataFrame
df['Dividend Premium'] = dividend_premium

print(df['Dividend Premium'])

df[['Dividend Premium', 'date']].to_csv("dividendpremium.csv")