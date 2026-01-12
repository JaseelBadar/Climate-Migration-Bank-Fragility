import pandas as pd
import numpy as np

df = pd.read_csv('02_Data_Intermediate/master_panel_raw.csv')

print("="*70)
print("MASTER PANEL VALIDATION")
print("="*70)

# 1. Panel balance (CORRECTED)
print("\n[1] PANEL BALANCE CHECK")
unique_units = df[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]
unique_quarters = df['quarter'].nunique()
expected = unique_units * unique_quarters
print(f"    Unique (district, state) pairs: {unique_units}")
print(f"    Unique quarters: {unique_quarters}")
print(f"    Expected rows: {expected}")
print(f"    Actual rows: {len(df)}")
print(f"    Balanced: {len(df) == expected}")

# Check for duplicates
dupes = df[df.duplicated(subset=['district_gadm', 'state_gadm', 'quarter'], keep=False)]
if len(dupes) > 0:
    print(f"\n    WARNING: {len(dupes)} duplicate rows found!")
    print("    Sample duplicates:")
    print(dupes.head(10)[['district_gadm', 'state_gadm', 'quarter', 'deposits']])

# 2. Missing data by year
print("\n[2] MISSING DATA BY YEAR")
for year in sorted(df['year'].unique()):
    year_df = df[df['year'] == year]
    missing_deps = year_df['deposits'].isna().sum()
    pct = (missing_deps / len(year_df)) * 100
    print(f"    {year}: {missing_deps:5d} missing ({pct:5.1f}%)")

# 3. 2016 investigation
print("\n[3] 2016 DETAILED BREAKDOWN")
df_2016 = df[df['year'] == 2016]
for q in [1, 2, 3, 4]:
    q_df = df_2016[df_2016['q'] == q]
    missing = q_df['deposits'].isna().sum()
    print(f"    2016Q{q}: {missing}/{len(q_df)} missing ({100*missing/len(q_df):.1f}%)")

# 4. Flood-deposit overlap
print("\n[4] TREATMENT-OUTCOME OVERLAP")
floods = df[df['flood_exposure_ruleA_qt'] > 0]
print(f"    Total flood events: {len(floods)}")
print(f"    Floods WITH deposit data: {floods['deposits'].notna().sum()}")
print(f"    Coverage: {100 * floods['deposits'].notna().sum() / len(floods):.1f}%")

# 5. District-level summary
print("\n[5] DISTRICT-LEVEL COVERAGE")
district_stats = df.groupby(['district_gadm', 'state_gadm']).agg({
    'deposits': lambda x: x.notna().sum(),
    'quarter': 'count'
}).reset_index()
district_stats.columns = ['district_gadm', 'state_gadm', 'quarters_with_data', 'total_quarters']
district_stats['coverage_pct'] = 100 * district_stats['quarters_with_data'] / district_stats['total_quarters']

print(f"    Districts with 100% coverage: {(district_stats['coverage_pct'] == 100).sum()}")
print(f"    Districts with 0% coverage: {(district_stats['coverage_pct'] == 0).sum()}")
print(f"    Mean coverage: {district_stats['coverage_pct'].mean():.1f}%")

# 6. Save validation log
output = f"""MASTER PANEL VALIDATION REPORT
Generated: 2026-01-12

STRUCTURE:
- Rows: {len(df)}
- Unique (district, state) pairs: {unique_units}
- Quarters: {unique_quarters}
- Balanced: {len(df) == expected}

DATA AVAILABILITY:
- Deposits: {df['deposits'].notna().sum()} / {len(df)} ({100*df['deposits'].notna().sum()/len(df):.1f}%)
- Floods (Rule A): {(df['flood_exposure_ruleA_qt'] > 0).sum()} events
- Floods (Rule B): {(df['flood_exposure_ruleB_qt'] > 0).sum()} events

CRITICAL ISSUES:
1. 2016Q3-Q4: 100% missing deposits (RBI data gap)
2. 2017: 29.3% missing deposits
3. Treatment coverage: 88.6% of floods have deposit data

RECOMMENDATIONS:
- DROP 2016Q3-Q4 from analysis (no deposit data)
- INVESTIGATE 2017 gaps (specific districts or states?)
- Use 2015-2024 with 2016Q3-Q4 excluded
"""

with open('02_Data_Intermediate/master_panel_validation_log.txt', 'w') as f:
    f.write(output)

print("\n[6] VALIDATION COMPLETE")
print("    Log saved: 02_Data_Intermediate/master_panel_validation_log.txt")
print("="*70)