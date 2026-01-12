import pandas as pd

print("="*70)
print("MASTER PANEL MERGE - PHASE 3d")
print("="*70)

# Load all datasets
print("\n[1] Loading datasets...")
skeleton = pd.read_csv('02_Data_Intermediate/district_quarter_skeleton.csv')
floods = pd.read_csv('02_Data_Intermediate/flood_exposure_panel.csv')
rbi = pd.read_csv('02_Data_Intermediate/rbi_deposits_panel.csv')

print(f"    Skeleton: {len(skeleton)} rows")
print(f"    Floods:   {len(floods)} rows")
print(f"    RBI:      {len(rbi)} rows")

# Merge floods onto skeleton (use district + state + quarter)
print("\n[2] Merging flood exposure...")
master = skeleton.merge(
    floods[['district_gadm', 'state_gadm', 'quarter', 'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt']],
    on=['district_gadm', 'state_gadm', 'quarter'],
    how='left',
    validate='1:1'
)
print(f"    After flood merge: {len(master)} rows")
print(f"    Flood coverage: {master['flood_exposure_ruleA_qt'].sum()} events (Rule A)")

# Merge RBI deposits (use district + state + quarter)
print("\n[3] Merging RBI deposits...")
master = master.merge(
    rbi[['district_gadm', 'state_gadm', 'quarter', 'deposits']],
    on=['district_gadm', 'state_gadm', 'quarter'],
    how='left',
    validate='1:1'
)
print(f"    After RBI merge: {len(master)} rows")
print(f"    Deposit coverage: {master['deposits'].notna().sum()} district-quarters")

# Check coverage
print("\n[4] COVERAGE ANALYSIS")
print(f"    Districts with ANY deposit data: {master.groupby(['district_gadm', 'state_gadm'])['deposits'].apply(lambda x: x.notna().any()).sum()}")
print(f"    District-quarters with BOTH floods + deposits: {((master['flood_exposure_ruleA_qt'] > 0) & (master['deposits'].notna())).sum()}")

# Temporal coverage breakdown
print("\n[5] TEMPORAL COVERAGE BY YEAR")
for year in sorted(master['year'].unique()):
    year_data = master[master['year'] == year]
    deposits_pct = (year_data['deposits'].notna().sum() / len(year_data)) * 100
    floods_count = year_data['flood_exposure_ruleA_qt'].sum()
    print(f"    {year}: {deposits_pct:5.1f}% deposits coverage | {floods_count:3.0f} flood events")

# Save
output_path = '02_Data_Intermediate/master_panel_raw.csv'
master.to_csv(output_path, index=False)

print(f"\n[6] OUTPUT SAVED")
print(f"    File: {output_path}")
print(f"    Rows: {len(master)}")
print(f"    Columns: {list(master.columns)}")

print("="*70)
print("MASTER PANEL MERGE COMPLETE")
print("="*70)