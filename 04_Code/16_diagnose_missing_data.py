import pandas as pd

df = pd.read_csv('02_Data_Intermediate/master_panel_raw.csv')

print("="*70)
print("MISSING DATA DIAGNOSTICS")
print("="*70)

# 1. Districts with 0% coverage
print("\n[1] DISTRICTS WITH NO DEPOSIT DATA (n=35)")
district_coverage = df.groupby(['district_gadm', 'state_gadm']).agg({
    'deposits': lambda x: x.notna().sum()
}).reset_index()
district_coverage.columns = ['district_gadm', 'state_gadm', 'quarters_with_data']

zero_coverage = district_coverage[district_coverage['quarters_with_data'] == 0]
print(zero_coverage.to_string(index=False))

# 2. 2017 gap by state
print("\n\n[2] 2017 MISSING DATA BY STATE")
df_2017 = df[df['year'] == 2017]
state_2017 = df_2017.groupby('state_gadm').agg({
    'deposits': lambda x: x.isna().sum(),
    'quarter': 'count'
}).reset_index()
state_2017.columns = ['state_gadm', 'missing', 'total']
state_2017['missing_pct'] = 100 * state_2017['missing'] / state_2017['total']
state_2017 = state_2017[state_2017['missing'] > 0].sort_values('missing', ascending=False)
print(state_2017.to_string(index=False))

# 3. 2017 gap by quarter
print("\n\n[3] 2017 MISSING DATA BY QUARTER")
for q in [1, 2, 3, 4]:
    q_df = df_2017[df_2017['q'] == q]
    missing = q_df['deposits'].isna().sum()
    print(f"    2017Q{q}: {missing}/{len(q_df)} missing ({100*missing/len(q_df):.1f}%)")

# 4. Overall coverage by state (all years)
print("\n\n[4] OVERALL COVERAGE BY STATE (2015-2024)")
state_overall = df.groupby('state_gadm').agg({
    'deposits': lambda x: x.notna().sum(),
    'quarter': 'count'
}).reset_index()
state_overall.columns = ['state_gadm', 'with_data', 'total']
state_overall['coverage_pct'] = 100 * state_overall['with_data'] / state_overall['total']
state_overall = state_overall.sort_values('coverage_pct')
print(state_overall.to_string(index=False))

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)