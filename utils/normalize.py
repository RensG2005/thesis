def normalize(serie, col):
        """
        serie: pd.Dataframe
        col: to be normalized column

        returns: dataframe["normalized_col"]
        """

        min_value = serie[col].min()
        max_value = serie[col].max()

        # Normalize to range [-5, 5]
        normalized_series = -5 + 2 * (serie[col] - min_value) / (max_value - min_value) * 5

        # Add normalized data to the DataFrame for plotting
        serie[f'normalized_{col}'] = normalized_series

        return serie