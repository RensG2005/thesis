import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

cs_df = pd.read_csv('consumersentiment/consumer_sentiment_pca.csv')
google_df= pd.read_csv('googletrends/googletrends_pca_output.csv')
vaex_df= pd.read_csv('vaex/investing.comVAEXmonthly.csv')

ipo_df= pd.read_csv('ipo/euronextIPOAms.csv')
ipo_df = ipo_df[["count", "date"]]

merged_df = pd.merge(cs_df, google_df, on='date', how='outer')
merged_df = pd.merge(merged_df, vaex_df, on='date', how='outer')
merged_df = pd.merge(merged_df, ipo_df, on='date', how='outer')

merged_df.set_index('date', inplace=True)

count_col = merged_df['count']

imputer = SimpleImputer(strategy='mean')
cols_to_impute = merged_df.columns.difference(['count'])
merged_df[cols_to_impute] = imputer.fit_transform(merged_df[cols_to_impute])

merged_df['count'] = count_col.fillna(0)

merged_df = merged_df.drop(columns=['Price', 'Open', 'High', 'Low'])

print(merged_df)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(merged_df)

# print(X_scaled[:200])

pca = PCA(n_components=1)
first_pc = pca.fit_transform(X_scaled)

df_pc1 = pd.DataFrame(first_pc, columns=['PC1'])

df_pc1.index = merged_df.index
merged_df['PC1'] = df_pc1['PC1']

print(merged_df.head())

explained_var_ratio = pca.explained_variance_ratio_[0]
print(f"Explained variance by PC1: {explained_var_ratio:.4f} ({explained_var_ratio * 100:.2f}%)")