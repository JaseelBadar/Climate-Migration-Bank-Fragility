import pandas as pd

# Load parsed file
df = pd.read_csv('02_Data_Intermediate/emdat_districts_parsed.csv')

print(f"Total events: {len(df)}")
print(f"Events with districts: {len(df[df['districts_final_str'] != ''])}")
print(f"\nSample rows with districts:")
print(df[df['districts_final_str'] != ''][['DisNo.', 'districts_final_str']].head(10))