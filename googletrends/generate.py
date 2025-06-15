import pandas as pd
import glob
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.signal import detrend

csv_files = glob.glob(os.path.join(os.getcwd() + "/googletrends/data", "*.csv"))

merged_df = None
for file in csv_files:
    df = pd.read_csv(file)
    key_column = df.columns[0]  # first column assumed to be date
    if merged_df is None:
        merged_df = df
    else:
        merged_df = pd.merge(merged_df, df, on=key_column, how='outer')

merged_df = merged_df.rename(columns={merged_df.columns[0]: "date"})
merged_df["date"] = pd.to_datetime(merged_df["date"])

df_clean = merged_df.dropna()

columns = [col for col in merged_df.columns if col != 'date']
features = df_clean[columns].copy()

for col in features.columns:
    features[col] = detrend(features[col].values)

scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

pca = PCA(n_components=1)
principal_component = pca.fit_transform(scaled_features)

df_pca = pd.DataFrame({
    'date': df_clean['date'].values,
    'googletrends_pca': principal_component.flatten()
})

output_csv_path = os.path.join(os.getcwd(), "googletrends_pca_output.csv")
df_pca.to_csv(output_csv_path, index=False)
print(f"\nPCA results saved to: {output_csv_path}")

explained_variance = pca.explained_variance_ratio_[0]
print(f"PCA Explained Variance: {explained_variance:.4f} ({explained_variance*100:.2f}%)")

loadings = pd.DataFrame(
    pca.components_.T,
    columns=['PC1'],
    index=features.columns
)
print("\nComponent Loadings:")
print(loadings)

df_pca = pd.merge(df_pca, df_clean[['date'] + columns], on='date')
