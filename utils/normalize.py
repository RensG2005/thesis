def normalize_centered(serie, col):
    """
    Normalize a column to have mean 0 and approximately range [-5, 5].

    Parameters:
    serie: pd.DataFrame
    col: str, column name to normalize

    Returns:
    serie with new column 'normalized_<col>'
    """
    values = serie[col]
    mean = values.mean()
    std = values.std()

    if std == 0 or pd.isna(std):
        raise ValueError(f"Standard deviation is zero or NaN for column '{col}' — cannot normalize.")

    # Standardize (mean 0, std 1)
    standardized = (values - mean) / std

    # Scale to approximately [-5, 5]
    scaled = standardized * 5

    # Clip extreme values beyond the expected range (e.g., 3+ std devs)
    scaled = scaled.clip(-5, 5)

    serie[f'normalized_{col}'] = scaled
    return serie
