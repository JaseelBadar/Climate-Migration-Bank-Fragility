import pandas as pd

print("="*70)
print("MASTER PANEL MERGE - PHASE 3d")
print("="*70)

# [1] Load
print("\n[1] Loading datasets...")
skeleton = pd.read_csv('02_Data_Intermediate/district_quarter_skeleton.csv')
floods   = pd.read_csv('02_Data_Intermediate/flood_exposure_panel.csv')
rbi      = pd.read_csv('02_Data_Intermediate/rbi_deposits_panel.csv')
print(f"    Skeleton: {len(skeleton)} rows")
print(f"    Floods:   {len(floods)} rows")
print(f"    RBI:      {len(rbi)} rows")

# [1b] Quarter format check — catches silent all-NaN merge
print("\n[1b] QUARTER FORMAT CHECK")
print(f"    Skeleton sample: {skeleton['quarter'].iloc[0]}")
print(f"    Floods sample:   {floods['quarter'].iloc[0]}")
print(f"    RBI sample:      {rbi['quarter'].iloc[0]}")
assert skeleton['quarter'].dtype == floods['quarter'].dtype == rbi['quarter'].dtype, \
    "Quarter dtype mismatch across files"

# [1c] Key normalisation — whitespace/case guard
for df in [skeleton, floods, rbi]:
    df['district_gadm'] = df['district_gadm'].str.strip().str.upper()
    df['state_gadm']    = df['state_gadm'].str.strip().str.upper()
print("    Key columns stripped and uppercased across all files")

# [1d] Subtotal row check — RBI Excel subtotal rows must not leak through
assert rbi['district_gadm'].isna().sum() == 0,   "NaN district_gadm in RBI — subtotal rows present"
assert floods['district_gadm'].isna().sum() == 0, "NaN district_gadm in floods"
print("    No NaN district rows in RBI or floods inputs")

# [2] Merge floods — state_gadm in key prevents Aurangabad/Bilaspur etc. contamination
# Research log Feb 7: old merge on district+quarter only caused homonym deposit sums
print("\n[2] Merging flood exposure...")
master = skeleton.merge(
    floods[['district_gadm', 'state_gadm', 'quarter',
            'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt']],
    on=['district_gadm', 'state_gadm', 'quarter'],
    how='left',
    validate='1:1'
)
master['flood_exposure_ruleA_qt'] = master['flood_exposure_ruleA_qt'].fillna(0)
master['flood_exposure_ruleB_qt'] = master['flood_exposure_ruleB_qt'].fillna(0)
print(f"    After flood merge: {len(master)} rows")
print(f"    Flood NaN filled with 0 (no event = zero exposure)")
print(f"    Flood coverage: {master['flood_exposure_ruleA_qt'].sum():.0f} events (Rule A)")

# [3] Merge RBI deposits — state_gadm in key prevents homonym contamination
# DO NOT fill NaN — missing deposits are genuinely missing, not zero
print("\n[3] Merging RBI deposits...")
master = master.merge(
    rbi[['district_gadm', 'state_gadm', 'quarter', 'deposits']],
    on=['district_gadm', 'state_gadm', 'quarter'],
    how='left',
    validate='1:1'
)
print(f"    After RBI merge: {len(master)} rows")
print(f"    Deposit coverage: {master['deposits'].notna().sum()} district-quarters")

# [4] Coverage analysis
print("\n[4] COVERAGE ANALYSIS")
total_districts   = master[['district_gadm','state_gadm']].drop_duplicates().shape[0]
dists_any_deposit = master.groupby(['district_gadm','state_gadm'])['deposits'].apply(lambda x: x.notna().any()).sum()
dists_no_deposit  = master.groupby(['district_gadm','state_gadm'])['deposits'].apply(lambda x: x.isna().all()).sum()
print(f"    Total districts in skeleton:              {total_districts}")
print(f"    Districts with ANY deposit data:          {dists_any_deposit}")
print(f"    Districts with NO deposit data:           {dists_no_deposit}  (expected ~35)")
print(f"    Deposit coverage rate by district:        {dists_any_deposit/total_districts*100:.1f}%")
print(f"    District-quarters with BOTH flood + dep:  {((master['flood_exposure_ruleA_qt'] > 0) & (master['deposits'].notna())).sum()}")

# [5] Temporal coverage — 2016Q3/Q4 must show 100% missing (RBI publication gap)
print("\n[5] TEMPORAL COVERAGE BY YEAR")
for year in sorted(master['year'].unique()):
    yr          = master[master['year'] == year]
    dep_pct     = yr['deposits'].notna().sum() / len(yr) * 100
    flood_count = yr['flood_exposure_ruleA_qt'].sum()
    print(f"    {year}: {dep_pct:5.1f}% deposits coverage | {flood_count:4.0f} flood events")

# [6] Save
output_path = '02_Data_Intermediate/master_panel_raw.csv'
master.to_csv(output_path, index=False)
print(f"\n[6] OUTPUT SAVED")
print(f"    File: {output_path}")
print(f"    Rows: {len(master)}")
print(f"    Columns: {list(master.columns)}")

print("="*70)
print("MASTER PANEL MERGE COMPLETE")
print("="*70)