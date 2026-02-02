import pandas as pd
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print("Column names:")
print(df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3))
print("\nShape:", df.shape)
print("\nMissing values per variable:")
print(df.isnull().sum())