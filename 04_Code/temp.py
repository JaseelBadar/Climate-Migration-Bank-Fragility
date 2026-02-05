import pandas as pd
import numpy as np

# ============================================================
# TASK 2: MANUAL VALIDATION OF CORRECTED RBI EXTRACTION
# ============================================================

# Load corrected panel
df = pd.read_csv('02_Data_Intermediate/rbi_deposits_panel.csv')

# ============================================================
# STEP 2.1: Basic Statistics
# ============================================================
print("="*70)
print("CORRECTED PANEL - BASIC STATISTICS")
print("="*70)
print(f"Total rows: {len(df):,}")
print(f"Districts: {df['district_gadm'].nunique()}")
print(f"Quarters: {df['quarter'].nunique()}")
print(f"\nDeposit statistics (Crores):")
print(df['deposits'].describe())
print(f"\nMedian by year:")
print(df.groupby('year')['deposits'].median().sort_index())

# ============================================================
# STEP 2.2: BALOD Test Case
# ============================================================
balod = df[(df['district_gadm'].str.contains('Balod', case=False, na=False)) & 
           (df['year'] == 2022) & 
           (df['q'] == 4)]

print("\n" + "="*70)
print("BALOD DISTRICT - 2022Q4 (Fiscal 2022-23:Q3)")
print("="*70)
print(balod[['district_gadm', 'state_gadm', 'quarter', 'deposits', 'district_rbi']])
print(f"\nExpected: 3,296 Crores (from audit)")
print(f"Actual: {balod['deposits'].values[0]:,.0f} Crores" if len(balod) > 0 else "NOT FOUND")

# ============================================================
# STEP 2.3: Random Sample Validation
# ============================================================
np.random.seed(42)  # Reproducible random sample

sample_2022q4 = df[(df['year'] == 2022) & (df['q'] == 4)].sample(5)

print("\n" + "="*70)
print("RANDOM SAMPLE - 2022Q4 (5 districts for manual verification)")
print("="*70)
print(sample_2022q4[['district_gadm', 'state_gadm', 'quarter', 'deposits', 'district_rbi']].to_string(index=False))
print("\nVerify these values against Excel file: RBI_Deposits_2017_2022.xlsx")
print("Look for fiscal quarter 2022-23:Q3 (Oct-Dec 2022)")

# ============================================================
# STEP 2.4: Check for Anomalous Spike Disappearance
# ============================================================
print("\n" + "="*70)
print("MEDIAN DEPOSIT TREND (2022-2023)")
print("="*70)

trend = df[df['year'].isin([2022, 2023])].groupby('quarter')['deposits'].median().sort_index()
print(trend)

print("\n2022Q4 → 2023Q1 change:")
q4_2022 = df[(df['year']==2022) & (df['q']==4)]['deposits'].median()
q1_2023 = df[(df['year']==2023) & (df['q']==1)]['deposits'].median()
print(f"2022Q4: {q4_2022:,.0f} Crores")
print(f"2023Q1: {q1_2023:,.0f} Crores")
print(f"Growth: {(q1_2023/q4_2022 - 1)*100:.1f}%")
print("\nExpected: Normal growth 8-12% (not 4,600%)")

print("\n" + "="*70)
print("VALIDATION COMPLETE")
print("="*70)