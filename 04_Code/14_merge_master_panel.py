import pandas as pd


print("="*70)
print("MASTER PANEL MERGE - PHASE 3d")
print("CORRECTED 2026-03-06")
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
assert len(master) == len(skeleton), \
    f"Row explosion after flood merge: {len(master)} != {len(skeleton)}"
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
assert len(master) == len(skeleton), \
    f"Row explosion after RBI merge: {len(master)} != {len(skeleton)}"
print(f"    After RBI merge: {len(master)} rows")
print(f"    Deposit coverage: {master['deposits'].notna().sum()} district-quarters")


# [4] Coverage analysis
print("\n[4] COVERAGE ANALYSIS")
total_districts   = master[['district_gadm','state_gadm']].drop_duplicates().shape[0]
dists_any_deposit = master.groupby(['district_gadm','state_gadm'])['deposits'].apply(lambda x: x.notna().any()).sum()
dists_no_deposit  = master.groupby(['district_gadm','state_gadm'])['deposits'].apply(lambda x: x.isna().all()).sum()
print(f"    Total districts in skeleton:              {total_districts}")
print(f"    Districts with ANY deposit data:          {dists_any_deposit}")
print(f"    Districts with NO deposit data:           {dists_no_deposit}  (expected ~35-42)")
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


# [7] SUMMARY STATISTICS
print("\n[7] SUMMARY STATISTICS")
print(f"    Total district-state pairs:   {total_districts}")
print(f"    Total quarters:               {master['quarter'].nunique()}")
print(f"    Date range:                   {master['year'].min()}-{master['year'].max()}")
print(f"    Total deposits (Rs Crores):   {master['deposits'].sum():,.0f}")
print(f"    Mean deposits per dist-qtr:   {master['deposits'].mean():,.0f}")
print(f"    Median deposits per dist-qtr: {master['deposits'].median():,.0f}")


# [8] MANUAL VALIDATION CHECKS
print("\n[8] MANUAL VALIDATION CHECKS")

# CHECK 1: Row count must equal skeleton exactly (666 districts x 40 quarters)
assert len(master) == 26640, \
    f"FAIL CHECK 1: {len(master)} rows, expected 26,640"
print(f"    CHECK 1 PASS: Row count = {len(master):,} (expected 26,640)")

# CHECK 2: Structural RBI publication gap — 2016Q3, 2016Q4, 2017Q1 must be 100% missing
for gap_q in ['2016Q3', '2016Q4', '2017Q1']:
    gap_cov = master[master['quarter'] == gap_q]['deposits'].notna().mean() * 100
    assert gap_cov == 0.0, \
        f"FAIL CHECK 2: {gap_q} deposit coverage = {gap_cov:.1f}% (expected 0.0%)"
    print(f"    CHECK 2 PASS: {gap_q} deposit coverage = 0.0% (structural gap confirmed)")

# CHECK 3: BALOD 2022Q4 deposit value must survive merge intact (~3,296 Crores)
balod_val = master[
    (master['district_gadm'] == 'BALOD') &
    (master['quarter'] == '2022Q4')
]['deposits'].values
assert len(balod_val) == 1, \
    f"FAIL CHECK 3: BALOD 2022Q4 returned {len(balod_val)} rows (expected 1)"
assert 3200 < balod_val[0] < 3400, \
    f"FAIL CHECK 3: BALOD 2022Q4 = {balod_val[0]:,.0f} Crores (expected 3,200-3,400)"
print(f"    CHECK 3 PASS: BALOD 2022Q4 = {balod_val[0]:,.0f} Crores (expected ~3,296)")

# CHECK 4: 2022Q4 median must be in realistic Crores range (not contaminated office counts)
median_2022q4 = master[
    (master['year'] == 2022) & (master['q'] == 4)
]['deposits'].median()
assert 5000 < median_2022q4 < 12000, \
    f"FAIL CHECK 4: 2022Q4 median = {median_2022q4:,.0f} Crores — outside 5,000-12,000 range"
print(f"    CHECK 4 PASS: 2022Q4 median = {median_2022q4:,.0f} Crores (expected 7,000-9,000)")

print("\n    DO NOT PROCEED TO SCRIPT 15 UNLESS ALL CHECKS 1-4 PASS.")
print("="*70)
print("MASTER PANEL MERGE COMPLETE")
print("="*70)