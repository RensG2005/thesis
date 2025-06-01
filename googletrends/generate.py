import pandas as pd
import glob
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.signal import detrend

# Get list of all CSV files in current directory
csv_files = glob.glob(os.path.join(os.getcwd() + "/googletrends/data", "*.csv"))

# Read and merge all CSV files on the first column
merged_df = None
for file in csv_files:
    df = pd.read_csv(file)
    key_column = df.columns[0]  # first column assumed to be date
    if merged_df is None:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on=key_column, how='outer')

# Rename and parse date
merged_df = merged_df.rename(columns={merged_df.columns[0]: "date"})
merged_df["date"] = pd.to_datetime(merged_df["date"])

# Drop rows with missing values
df_clean = merged_df.dropna()

# Select feature columns (excluding date)
columns = [col for col in merged_df.columns if col != 'date']
features = df_clean[columns].copy()

# Apply linear detrending to each column
for col in features.columns:
    features[col] = detrend(features[col].values)

# Standardize
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# PCA
pca = PCA(n_components=1)
principal_component = pca.fit_transform(scaled_features)

# Create result DataFrame
df_pca = pd.DataFrame({
    'date': df_clean['date'].values,
    'googletrends_pca': principal_component.flatten()
})

# Save to CSV
output_csv_path = os.path.join(os.getcwd(), "googletrends_pca_output.csv")
df_pca.to_csv(output_csv_path, index=False)
print(f"\nPCA results saved to: {output_csv_path}")

# Explained variance
explained_variance = pca.explained_variance_ratio_[0]
print(f"PCA Explained Variance: {explained_variance:.4f} ({explained_variance*100:.2f}%)")

# Loadings
loadings = pd.DataFrame(
    pca.components_.T,
    columns=['PC1'],
    index=features.columns
)
print("\nComponent Loadings:")
print(loadings)

# Optionally merge with original for inspection
df_pca = pd.merge(df_pca, df_clean[['date'] + columns], on='date')
