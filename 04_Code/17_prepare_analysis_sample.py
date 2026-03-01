import pandas as pd

df = pd.read_csv('02_Data_Intermediate/master_panel_raw.csv')

print("="*70)
print("ANALYSIS SAMPLE PREPARATION")
print("="*70)

# Option 1: Drop blackout quarters (2016Q3, 2016Q4, 2017Q1)
print("\n[OPTION 1] DROP 2016Q3-2017Q1 (3-quarter gap)")
df_opt1 = df[~df['quarter'].isin(['2016Q3', '2016Q4', '2017Q1'])].copy()
print(f"    Rows:             {len(df_opt1)} (vs original {len(df)})")
print(f"    Districts:        {df_opt1[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]}")
print(f"    Quarters:         {df_opt1['quarter'].nunique()}")
print(f"    Deposit coverage: {100*df_opt1['deposits'].notna().sum()/len(df_opt1):.1f}%")
print(f"    Flood events:     {(df_opt1['flood_exposure_ruleA_qt'] > 0).sum()}")

# Build valid district index from original df (pre-quarter-filter)
district_coverage = df.groupby(['district_gadm', 'state_gadm'])['deposits'].apply(
    lambda x: x.notna().sum()
)
valid_districts = district_coverage[district_coverage > 0].index
n_zero = (district_coverage == 0).sum()

# Option 2: Drop zero-coverage districts only
df_opt2 = df.set_index(['district_gadm', 'state_gadm']).loc[valid_districts].reset_index()
print(f"\n[OPTION 2] DROP {n_zero} ZERO-COVERAGE DISTRICTS")
print(f"    Rows:             {len(df_opt2)} (vs original {len(df)})")
print(f"    Districts:        {df_opt2[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]}")
print(f"    Quarters:         {df_opt2['quarter'].nunique()}")
print(f"    Deposit coverage: {100*df_opt2['deposits'].notna().sum()/len(df_opt2):.1f}%")
print(f"    Flood events:     {(df_opt2['flood_exposure_ruleA_qt'] > 0).sum()}")

# Option 3: Both restrictions (RECOMMENDED)
df_opt3 = df_opt1.set_index(['district_gadm', 'state_gadm']).loc[valid_districts].reset_index()
n_districts = df_opt3[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]
n_excluded  = 666 - n_districts
floods_opt3     = df_opt3[df_opt3['flood_exposure_ruleA_qt'] > 0]
floods_with_dep = floods_opt3['deposits'].notna().sum()

print(f"\n[OPTION 3] BOTH RESTRICTIONS (RECOMMENDED)")
print(f"    Rows:             {len(df_opt3)} (vs original {len(df)})")
print(f"    Districts:        {n_districts} (excluded {n_excluded} zero-coverage)")
print(f"    Quarters:         {df_opt3['quarter'].nunique()}")
print(f"    Deposit coverage: {100*df_opt3['deposits'].notna().sum()/len(df_opt3):.1f}%")
print(f"    Flood events:     {len(floods_opt3)}")
print(f"    Floods WITH dep:  {floods_with_dep}/{len(floods_opt3)} ({100*floods_with_dep/len(floods_opt3):.1f}%)")

# Save Option 3
output_path = '02_Data_Intermediate/master_panel_analysis.csv'
df_opt3.to_csv(output_path, index=False)

print(f"\n[RECOMMENDED SAMPLE SAVED]")
print(f"    File:        {output_path}")
print(f"    Time period: 2015Q1-2016Q2, 2017Q2-2024Q4")
print(f"    Districts:   {n_districts} (excluded {n_excluded} zero-coverage)")
print(f"    Total obs:   {len(df_opt3):,}")

print(f"\n[SUMMARY STATS]")
print(f"    Mean deposits:   ₹{df_opt3['deposits'].mean():.1f} crores")
print(f"    Median deposits: ₹{df_opt3['deposits'].median():.1f} crores")
print(f"    Flood rate:      {100*(df_opt3['flood_exposure_ruleA_qt']>0).sum()/len(df_opt3):.2f}%")

print("="*70)