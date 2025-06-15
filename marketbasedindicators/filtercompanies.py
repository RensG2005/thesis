import pandas as pd
import re
df = pd.read_csv("./marketbasedindicators/dividendpremium1.csv")
companies = [
    'ABN AMRO BANK',
    'ADYEN',
    'AEGON',
    'KONINKLIJKE AHOLD DELHAIZE',
    'AKZO NOBEL',
    'ARCELORMITTAL',
    'ASM INTERNATIONAL',
    'ASML HOLDING',
    'ASR NEDERLAND',
    'BE SEMICONDUCTOR INDUSTRIES',
    'DSM FIRMENICH',
    'EXOR NV ORD',
    'HEINEKEN',
    'IMCD GROUP',
    'ING GROEP',
    'KPN KON',
    'NN GROUP',
    'PHILIPS ELTN.KONINKLIJKE',
    'PROSUS N',
    'RANDSTAD',
    'RELX (AMS)',
    'SHELL (AMS)',
    'UNIVERSAL MUSIC GROUP',
    'UNILEVER (UK) (AMS)',
    'WOLTERS KLUWER',
]

suffixes = [
    'DIVIDEND YIELD',
    'MRKT VALUE TO BOOK',
]

pattern = re.compile(
    r'^(' + '|'.join(re.escape(c) for c in companies) + r') - (' +
    '|'.join(re.escape(s) for s in suffixes) + r')$'
)

keep_cols = [col for col in df.columns if col == 'date' or col == 'Name' or pattern.match(col)]

print(f"Keeping {len(keep_cols)} columns out of {len(df.columns)} total")

df_filtered = df[keep_cols]
df_filtered.to_csv("filtered_output.csv", index=False)
