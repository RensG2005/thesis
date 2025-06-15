import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import os

def load_df():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv_path = os.path.join(module_dir, "consumer_sentiment_pca.csv")
    csv_path = os.path.join(module_dir, "consumentenconfidenceCBS.csv")
    
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    
    sentiment_columns = [
        "Consumer confidence",
        "Economic climate",
        "Willingness to buy",
        "Economic situation next 12 months",
        "Financial situation next 12 months",
        "Right time to make large purchases"
    ]
    
    features = df[sentiment_columns]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    pca = PCA(n_components=1)  # We want a single time series
    principal_component = pca.fit_transform(scaled_features)
    df_pca = pd.DataFrame({
        'date': df['date'],
        'consumer_sentiment_pca': principal_component.flatten()
    })
    
    df_pca[['date', 'consumer_sentiment_pca']].to_csv(output_csv_path, index=False)
    print(f"PCA results saved to: {output_csv_path}")

    explained_variance = pca.explained_variance_ratio_[0]
    print(f"PCA Explained Variance: {explained_variance:.4f} ({explained_variance*100:.2f}%)")
    
    loadings = pd.DataFrame(
        pca.components_.T,
        columns=['PC1'],
        index=sentiment_columns
    )
    print("\nComponent Loadings (contribution of each feature):")
    print(loadings)
    
    df_pca = pd.merge(df_pca, df[['date'] + sentiment_columns], on='date')
    return df_pca

df_pca = load_df()


module_dir = os.path.dirname(os.path.abspath(__file__))
output_csv_path = os.path.join(module_dir, "consumer_sentiment_pca.csv")
print(f"\nPCA results are available at: {output_csv_path}")


# Display the first few rows
print("\nPCA Results (first 5 rows):")
print(df_pca[['date', 'consumer_sentiment_pca']].head())