import pandas as pd
def normalize(serie, col):
    values = serie[col]
    mean = values.mean()
    std = values.std()

    if std == 0 or pd.isna(std):
        raise ValueError(f"Standard deviation is zero or NaN for column '{col}' — cannot normalize.")

    standardized = (values - mean) / std

    serie[f'normalized_{col}'] = standardized
    return serie
