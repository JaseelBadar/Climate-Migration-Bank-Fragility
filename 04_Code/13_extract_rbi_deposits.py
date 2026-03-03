import pandas as pd
import os


print("=" * 70)
print("RBI DEPOSITS EXTRACTION - Phase 3d")
print("CORRECTED 2026-02-11 (Two-Bug Cascade Fix)")
print("Reviewed and finalised 2026-03-03")
print("=" * 70)

# Bug 1 fixed: dep_idx = q_idx + 1 (column offset for historical files)
# Bug 2 fixed: state-based filter for 7 homonymous district pairs
# RAIGAD normalisation added 2026-03-03: RBI Maharashtra uses RAIGAD,
# GADM uses Raigarh. Normalise before crosswalk merge.


# Input files
rbi_files = [
    '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xlsx',
    '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2017_2022.xlsx',
    '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2004_2017.xlsx'
]


# Load crosswalk
crosswalk = pd.read_csv('02_Data_Intermediate/district_crosswalk_draft.csv')
print(f"\n[1] Crosswalk loaded: {len(crosswalk)} rows")
print(f"    RBI->GADM matches: {crosswalk['matched_rbi_gadm'].sum()}")
# Expected: 769 rows (762 unique + 7 duplicates for homonymous pairs)
# Script 08 deduplication confirmed 762 unique RBI names, 7 pairs each with 2 rows


# Storage for all quarters
all_data = []


for file_idx, filepath in enumerate(rbi_files, 1):
    print(f"\n[2.{file_idx}] Processing: {os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        print(f"    WARNING: File not found, skipping")
        continue

    # Load Excel with header at row index 5 (0-indexed).
    # Manual audit Feb 4 2026 confirmed for all 3 files:
    #   Row 6 (index 5): merged quarter headers -> column names
    #   Row 7 (index 6): sub-headers (Offices / Deposit / Credit) -> df.iloc[0]
    #   Row 8 (index 7): first data row (BALOD: E8=87, F8=3296, G8=1289)
    # The sub-header row (df.iloc[0]) is removed via pd.to_numeric coercion + dropna.
    df = pd.read_excel(filepath, sheet_name=0, header=5)
    print(f"    Loaded: {df.shape[0]} rows x {df.shape[1]} cols")

    # Key columns consistent across all 3 files by positional index
    state_col    = df.columns[2]   # "State or UTs" (historical) / "STATE" (current)
    district_col = df.columns[3]   # "District" / "DISTRICT"

    # Detect file format by presence of fiscal quarter notation in column names
    has_fiscal_quarters = any(':Q' in str(col) for col in df.columns[:20])


    if has_fiscal_quarters:
        # ============================================================
        # HISTORICAL FORMAT: 2017-22 and 2004-17 files
        # Manual audit Feb 4 2026 confirmed structure:
        #   Index 4 = "2022-23:Q3"  <- quarter label (contains ':Q')
        #   Index 5 = Deposit       <- dep_idx = q_idx + 1   BUG 1 FIX
        #   Index 6 = Credit
        # BALOD row 8: E8=87 (Offices), F8=3,296 Crores (Deposit)
        # Script previously extracted E8 (Offices). Fix: extract F8 (Deposit).
        # ============================================================
        print(f"    Format: Historical (fiscal quarters)")

        quarter_label_cols = [i for i, col in enumerate(df.columns)
                              if ':Q' in str(col)]
        print(f"    Quarter label columns found: {len(quarter_label_cols)}")

        print(f"    File structure check (first 3 quarters):")
        for q_idx in quarter_label_cols[:3]:
            dep_idx = q_idx + 1
            if dep_idx < len(df.columns):
                print(f"      [{q_idx}] {df.columns[q_idx]} -> "
                      f"Deposit at [{dep_idx}] {df.columns[dep_idx]}")

        for q_idx in quarter_label_cols:
            col_name = str(df.columns[q_idx])

            # CORE FIX: Deposit is always the NEXT column after the quarter label.
            # q_idx points to "2022-23:Q3" (Offices column in Excel).
            # q_idx + 1 points to the Deposit column in Excel.
            dep_idx = q_idx + 1

            if dep_idx >= len(df.columns):
                print(f"    WARNING: Skipping '{col_name}': "
                      f"deposit index {dep_idx} out of range")
                continue

            try:
                # Parse "2022-23:Q3" -> calendar year and quarter
                year_part, q_part = col_name.split(':Q')
                year_start = int(year_part.split('-')[0])
                fiscal_q   = int(q_part)

                # Indian fiscal year to calendar year conversion:
                # Fiscal Q1 (Apr-Jun) = Calendar Q2
                # Fiscal Q2 (Jul-Sep) = Calendar Q3
                # Fiscal Q3 (Oct-Dec) = Calendar Q4
                # Fiscal Q4 (Jan-Mar) = Calendar Q1 of NEXT calendar year
                if fiscal_q == 4:
                    calendar_year = year_start + 1
                    calendar_q    = 1
                else:
                    calendar_year = year_start
                    calendar_q    = fiscal_q + 1

                quarter_str = f"{calendar_year}Q{calendar_q}"

            except Exception as e:
                print(f"    WARNING: Skipping column '{col_name}': {e}")
                continue

            temp = df[[state_col, district_col, df.columns[dep_idx]]].copy()
            temp.columns = ['state_rbi', 'district_rbi', 'deposits']
            temp['quarter'] = quarter_str
            temp['year']    = calendar_year
            temp['q']       = calendar_q

            # Coerce deposits to numeric. This drops the sub-header text row
            # (df.iloc[0] contains "Deposit" string, not a number) and any
            # subtotal rows (bold rows with blank district names).
            temp['deposits'] = pd.to_numeric(temp['deposits'], errors='coerce')
            temp = temp.dropna(subset=['district_rbi', 'deposits'])

            temp_agg = temp.groupby(
                ['state_rbi', 'district_rbi', 'quarter', 'year', 'q'],
                as_index=False
            )['deposits'].sum()

            all_data.append(temp_agg)


    else:
        # ============================================================
        # CURRENT FORMAT: 2023-24 file
        # Manual audit Feb 4 2026 confirmed structure:
        #   Index 5 = quarter label (timestamp e.g. 2025-09-30)
        #   Index 6 = No. of Accounts
        #   Index 7 = Deposit Amount  <- range(7, ..., 3) is correct
        # Population group rows (Rural/Semi-urban/Urban/Metro) are summed
        # via groupby to produce district totals, consistent with Files 2-3.
        # ============================================================
        print(f"    Format: Current (calendar date timestamps)")

        deposit_indices = list(range(7, len(df.columns), 3))
        print(f"    Deposit columns found: {len(deposit_indices)}")

        for dep_idx in deposit_indices:
            if dep_idx >= len(df.columns):
                break

            # Date label is 2 columns before deposit
            date_idx     = dep_idx - 2
            quarter_date = df.columns[date_idx]

            try:
                dt            = pd.to_datetime(quarter_date)
                calendar_year = dt.year
                calendar_q    = (dt.month - 1) // 3 + 1
                quarter_str   = f"{calendar_year}Q{calendar_q}"
            except Exception:
                continue

            temp = df[[state_col, district_col, df.columns[dep_idx]]].copy()
            temp.columns = ['state_rbi', 'district_rbi', 'deposits']
            temp['quarter'] = quarter_str
            temp['year']    = calendar_year
            temp['q']       = calendar_q

            # Coerce deposits to numeric. Drops sub-header and total rows.
            temp['deposits'] = pd.to_numeric(temp['deposits'], errors='coerce')
            temp = temp.dropna(subset=['district_rbi', 'deposits'])

            # groupby sums across population groups (Rural + Semi-urban +
            # Urban + Metro) to produce one district total per quarter,
            # consistent with the format of the historical files.
            temp_agg = temp.groupby(
                ['state_rbi', 'district_rbi', 'quarter', 'year', 'q'],
                as_index=False
            )['deposits'].sum()

            all_data.append(temp_agg)


# Combine all quarters
print(f"\n[3] Combining all files...")
rbi_panel = pd.concat(all_data, ignore_index=True)
print(f"    Total rows before crosswalk: {len(rbi_panel)}")
print(f"    Unique district names:       {rbi_panel['district_rbi'].nunique()}")
print(f"    Quarters range:              "
      f"{rbi_panel['quarter'].min()} to {rbi_panel['quarter'].max()}")


# [3b] HOMONYMOUS DISTRICT DIAGNOSTIC
# Prints exact state_rbi strings present in raw RBI data for each of the
# 7 homonymous pairs. Must match state_mapping_rbi_to_gadm keys after
# .upper().strip(). Any mismatch here causes silent filter failure.
print(f"\n[3b] HOMONYMOUS DISTRICT DIAGNOSTIC")
for d in ['AURANGABAD', 'BALRAMPUR', 'BIJAPUR', 'BILASPUR',
          'HAMIRPUR', 'PRATAPGARH', 'RAIGARH']:
    rows   = rbi_panel[rbi_panel['district_rbi'] == d]
    states = sorted(rows['state_rbi'].str.upper().str.strip().unique().tolist())
    print(f"    {d}: {states}")

# Check aliases that RBI may use in place of the standard homonymous name.
# RAIGAD: Maharashtra coastal district. GADM names it Raigarh.
# If RAIGAD (alias) prints ['MAHARASHTRA'], the normalisation below is confirmed necessary.
# If it prints nothing (len=0), RBI already uses RAIGARH and normalisation is a no-op.
for alias in ['RAIGAD', 'VIJAYAPURA', 'VIJAYAPURAM']:
    rows = rbi_panel[rbi_panel['district_rbi'] == alias]
    if len(rows) > 0:
        states = sorted(rows['state_rbi'].str.upper().str.strip().unique().tolist())
        print(f"    {alias} (alias check): {states}")

# RAIGAD -> RAIGARH normalisation.
# RBI uses "RAIGAD" for Maharashtra coastal district.
# Crosswalk and state_mapping use "RAIGARH" to match GADM naming.
# Applied BEFORE merge and state filter so the crosswalk lookup succeeds.
rbi_name_normalise = {
    ('RAIGAD', 'MAHARASHTRA'): 'RAIGARH',
}
rbi_panel['district_rbi'] = rbi_panel.apply(
    lambda row: rbi_name_normalise.get(
        (row['district_rbi'], row['state_rbi'].upper().strip()),
        row['district_rbi']
    ),
    axis=1
)
print(f"    Normalisation applied: RAIGAD/MAHARASHTRA -> RAIGARH/MAHARASHTRA")
print(f"    (No-op if RAIGAD alias check above printed nothing)")


# [4] Map RBI districts to GADM via crosswalk
print(f"\n[4] Mapping RBI -> GADM districts...")

# State disambiguation for 7 homonymous district pairs.
# Keys: (district_rbi UPPERCASE, state_rbi UPPERCASE) -> GADM state (title case)
# .upper().strip() on state_rbi normalises:
#   "MAHARASHTRA" (2023-24 file, STATE column uppercase)
#   "Maharashtra"  (2017-22, 2004-17 files, "State or UTs" column title-case)
# Both resolve to key 'MAHARASHTRA' correctly.
state_mapping_rbi_to_gadm = {
    ('AURANGABAD',  'BIHAR'):            'Bihar',
    ('AURANGABAD',  'MAHARASHTRA'):      'Maharashtra',
    ('BALRAMPUR',   'CHHATTISGARH'):     'Chhattisgarh',
    ('BALRAMPUR',   'UTTAR PRADESH'):    'Uttar Pradesh',
    ('BIJAPUR',     'CHHATTISGARH'):     'Chhattisgarh',
    ('BIJAPUR',     'KARNATAKA'):        'Karnataka',
    ('BILASPUR',    'CHHATTISGARH'):     'Chhattisgarh',
    ('BILASPUR',    'HIMACHAL PRADESH'): 'Himachal Pradesh',
    ('HAMIRPUR',    'HIMACHAL PRADESH'): 'Himachal Pradesh',
    ('HAMIRPUR',    'UTTAR PRADESH'):    'Uttar Pradesh',
    ('PRATAPGARH',  'RAJASTHAN'):        'Rajasthan',
    ('PRATAPGARH',  'UTTAR PRADESH'):    'Uttar Pradesh',
    ('RAIGARH',     'CHHATTISGARH'):     'Chhattisgarh',
    ('RAIGARH',     'MAHARASHTRA'):      'Maharashtra',
}

rbi_panel['state_gadm_expected'] = rbi_panel.apply(
    lambda row: state_mapping_rbi_to_gadm.get(
        (row['district_rbi'], row['state_rbi'].upper().strip()),
        None
    ),
    axis=1
)

# Left join on district_rbi.
# Homonymous districts produce 2 rows per observation (one per crosswalk entry).
# Non-homonymous districts produce 1 row (unchanged).
rbi_panel = rbi_panel.merge(
    crosswalk[['district_rbi', 'district_gadm', 'state_gadm', 'matched_rbi_gadm']],
    on='district_rbi',
    how='left'
)

# State filter: for homonymous districts keep only the row where crosswalk
# state_gadm matches the state derived from state_rbi.
# For non-homonymous districts all rows pass through unchanged.
homonymous_districts = [
    'AURANGABAD', 'BALRAMPUR', 'BIJAPUR', 'BILASPUR',
    'HAMIRPUR', 'PRATAPGARH', 'RAIGARH'
]
is_homonymous      = rbi_panel['district_rbi'].isin(homonymous_districts)
has_expected_state = rbi_panel['state_gadm_expected'].notna()

rbi_panel = rbi_panel[
    (~is_homonymous) |
    (is_homonymous & has_expected_state &
     (rbi_panel['state_gadm'] == rbi_panel['state_gadm_expected']))
]

rbi_panel = rbi_panel.drop(columns=['state_gadm_expected'])

matched_count = rbi_panel['matched_rbi_gadm'].sum()
total_count   = len(rbi_panel)
print(f"    After state filter - Matched: {matched_count}/{total_count} "
      f"({matched_count / total_count * 100:.1f}%)")

# Drop rows with no crosswalk match
matched_mask = rbi_panel['matched_rbi_gadm'].notna() & rbi_panel['matched_rbi_gadm'].astype(bool)
rbi_panel    = rbi_panel[matched_mask].copy()
rbi_panel    = rbi_panel.drop(columns=['matched_rbi_gadm'])
print(f"    After dropping unmatched: {len(rbi_panel)} rows")

# District count diagnostics.
# Unique names: 624 (7 homonymous names each counted once).
# Unique pairs: 631 = 617 non-homonymous + (7 pairs x 2 states).
# If pairs = 630: one homonymous pair has only 1 state in RBI data (acceptable).
# If pairs < 624: filter is dropping both copies of a pair (bug).
unique_names = rbi_panel['district_gadm'].nunique()
unique_pairs = rbi_panel[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]
print(f"    Unique GADM district names:       {unique_names}")
print(f"    Unique GADM district-state pairs: {unique_pairs}  (target: 631)")


# Add sequential quarter index
rbi_panel = rbi_panel.sort_values(['district_gadm', 'year', 'q'])
quarter_map              = {q: i + 1 for i, q in
                            enumerate(sorted(rbi_panel['quarter'].unique()))}
rbi_panel['quarter_num'] = rbi_panel['quarter'].map(quarter_map)


# [4b] Aggregate to unique GADM district-state-quarter level
# Required because some GADM districts map to multiple RBI district names
# (e.g. renamed districts). Sum their deposits.
print(f"\n[4b] Aggregating to GADM district-state-quarter level...")
print(f"    Before aggregation: {len(rbi_panel)} rows")
rbi_panel = rbi_panel.groupby(
    ['district_gadm', 'state_gadm', 'quarter', 'year', 'q', 'quarter_num'],
    as_index=False
).agg({
    'deposits':     'sum',
    'district_rbi': lambda x: '; '.join(sorted(set(x))),
    'state_rbi':    'first'
})
print(f"    After aggregation:  {len(rbi_panel)} rows")

unique_names_post = rbi_panel['district_gadm'].nunique()
unique_pairs_post = rbi_panel[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]
print(f"    Unique GADM district names:       {unique_names_post}")
print(f"    Unique GADM district-state pairs: {unique_pairs_post}  (target: 631)")

if unique_pairs_post == 631:
    print(f"    PASS: 631 district-state pairs confirmed.")
elif unique_pairs_post == 630:
    print(f"    ACCEPTABLE: 630 pairs. One homonymous pair has single RBI state entry.")
    print(f"    Cross-check [3b] output to identify which pair.")
elif unique_pairs_post < 630:
    print(f"    WARNING: {unique_pairs_post} pairs, expected 631. "
          f"Cross-check [3b] output. State filter may be dropping both copies of a pair.")
else:
    print(f"    WARNING: {unique_pairs_post} pairs exceeds 631. Unexpected extra pairs.")


# Reorder columns
rbi_panel = rbi_panel[[
    'district_gadm', 'state_gadm', 'quarter', 'year', 'q', 'quarter_num',
    'deposits', 'district_rbi', 'state_rbi'
]]


# Save
output_path = '02_Data_Intermediate/rbi_deposits_panel.csv'
rbi_panel.to_csv(output_path, index=False)

print(f"\n[5] OUTPUT SAVED")
print(f"    File:    {output_path}")
print(f"    Rows:    {len(rbi_panel)}")
print(f"    Columns: {rbi_panel.columns.tolist()}")


# [6] SUMMARY STATISTICS
print(f"\n[6] SUMMARY STATISTICS")
print(f"    District names:        {rbi_panel['district_gadm'].nunique()}")
print(f"    District-state pairs:  "
      f"{rbi_panel[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]}")
print(f"    Quarters:              {rbi_panel['quarter'].nunique()}")
print(f"    Date range:            {rbi_panel['year'].min()}-{rbi_panel['year'].max()}")
print(f"    Total deposits (Rs Crores): {rbi_panel['deposits'].sum():,.0f}")
print(f"    Mean deposits per district-quarter: {rbi_panel['deposits'].mean():,.0f}")
print(f"    Median deposits per district-quarter: {rbi_panel['deposits'].median():,.0f}")


# [7] TEMPORAL COVERAGE CHECK
print(f"\n[7] TEMPORAL COVERAGE CHECK")
for year in sorted(rbi_panel['year'].unique()):
    quarters_present = sorted(rbi_panel[rbi_panel['year'] == year]['q'].unique())
    print(f"    {int(year)}: Q{[int(q) for q in quarters_present]}")
# Expected structural gap: 2016Q3, 2016Q4, 2017Q1 missing.
# This is RBI publication schedule gap, confirmed Jan 31 2026. Not a data error.


# [8] MANUAL VALIDATION CHECKS
# These checks replicate the Feb 4 2026 manual Excel inspection.
# Both must pass before proceeding to Script 14.
# If either fails, the extraction logic has a new bug. Do not proceed.
print(f"\n[8] MANUAL VALIDATION CHECKS")

# Check 1: BALOD 2022Q4 litmus test
# Manual audit Feb 4 2026: File 2 (2017-22), Row 8, 2022-23:Q3
# Excel cell F8 = 3,296 Crores (Deposit). This is calendar 2022Q4.
# If Bug 1 is still active, BALOD will show 87 (Offices from cell E8).
balod = rbi_panel[
    (rbi_panel['district_gadm'].str.upper().str.strip() == 'BALOD') &
    (rbi_panel['year'] == 2022) &
    (rbi_panel['q'] == 4)
]
if len(balod) > 0:
    balod_val = balod['deposits'].values[0]
    if 3000 <= balod_val <= 3600:
        print(f"    CHECK 1 PASS: BALOD 2022Q4 = {balod_val:,.0f} Crores "
              f"(expected ~3,296 from Excel F8)")
    elif balod_val < 500:
        print(f"    CHECK 1 FAIL: BALOD 2022Q4 = {balod_val:,.0f} Crores. "
              f"Expected ~3,296. Got office count. Bug 1 still active.")
    else:
        print(f"    CHECK 1 WARN: BALOD 2022Q4 = {balod_val:,.0f} Crores. "
              f"Not in expected range 3,000-3,600. Investigate before proceeding.")
else:
    print(f"    CHECK 1 FAIL: BALOD district not found in 2022Q4. "
          f"Check crosswalk for BALOD -> GADM mapping.")

# Check 2: 2022Q4 median deposits
# Post-fix Feb 11 2026 validated median: 7,865 Crores (realistic banking range).
# Pre-fix contaminated median: 162 Crores (was office count, not deposits).
# Acceptable range: 1,500-10,000 Crores for district-level quarterly deposits.
q2022q4 = rbi_panel[(rbi_panel['year'] == 2022) & (rbi_panel['q'] == 4)]
if len(q2022q4) > 0:
    median_val = q2022q4['deposits'].median()
    if 1500 <= median_val <= 10000:
        print(f"    CHECK 2 PASS: 2022Q4 median = {median_val:,.0f} Crores "
              f"(acceptable range: 1,500-10,000)")
    elif median_val < 500:
        print(f"    CHECK 2 FAIL: 2022Q4 median = {median_val:,.0f} Crores. "
              f"Expected 1,500-10,000. Still extracting office counts.")
    else:
        print(f"    CHECK 2 WARN: 2022Q4 median = {median_val:,.0f} Crores. "
              f"Outside expected range. Investigate before proceeding.")
else:
    print(f"    CHECK 2 FAIL: No 2022Q4 observations found.")

# Check 3: Aurangabad Bihar contamination check
# Post-fix Feb 11 2026: Aurangabad Bihar 2015Q1 = 4,422 Crores.
# Pre-fix contaminated: 18,652 Crores (Bihar + Maharashtra summed).
# If Bug 2 state filter is still active, this will return ~18,652.
aur_bih = rbi_panel[
    (rbi_panel['district_gadm'].str.upper().str.strip() == 'AURANGABAD') &
    (rbi_panel['state_gadm'] == 'Bihar') &
    (rbi_panel['year'] == 2015) &
    (rbi_panel['q'] == 1)
]
if len(aur_bih) > 0:
    aur_val = aur_bih['deposits'].values[0]
    if aur_val < 10000:
        print(f"    CHECK 3 PASS: Aurangabad (Bihar) 2015Q1 = {aur_val:,.0f} Crores "
              f"(expected ~4,422, Bihar-only)")
    else:
        print(f"    CHECK 3 FAIL: Aurangabad (Bihar) 2015Q1 = {aur_val:,.0f} Crores. "
              f"Expected ~4,422. Likely Bihar + Maharashtra still summed. Bug 2 active.")
else:
    print(f"    CHECK 3 WARN: Aurangabad Bihar 2015Q1 not found. "
          f"Check crosswalk and state filter.")

print(f"\n    DO NOT PROCEED TO SCRIPT 14 UNLESS CHECKS 1, 2, AND 3 ALL PASS.")


print("=" * 70)
print("RBI EXTRACTION COMPLETE (CORRECTED VERSION 2026-03-03)")
print("=" * 70)