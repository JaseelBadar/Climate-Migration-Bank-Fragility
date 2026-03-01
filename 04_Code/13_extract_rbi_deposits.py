import pandas as pd
import os


print("=" * 70)
print("RBI DEPOSITS EXTRACTION - Phase 3d (CORRECTED 2026-02-11 - Two-Bug Cascade Fix)")
print("=" * 70)


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
# Crosswalk has 769 rows: 762 unique RBI names + 7 extra for homonymous pairs.
# Each homonymous district (e.g. AURANGABAD) has 2 rows, one per GADM state.
# This script resolves ambiguity via state_rbi from the Excel files.


# Storage for all quarters
all_data = []


for file_idx, filepath in enumerate(rbi_files, 1):
    print(f"\n[2.{file_idx}] Processing: {os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        print(f"    WARNING: File not found, skipping")
        continue

    # Load Excel (header at row 5, 0-indexed = skiprows 5 equivalent)
    # Verified against manual audit (Feb 4 2026):
    # All 3 files: header row at index 5, data from row 8
    # Index 0=Blank, 1=Region, 2=State, 3=District
    df = pd.read_excel(filepath, sheet_name=0, header=5)
    print(f"    Loaded: {df.shape[0]} rows x {df.shape[1]} cols")

    # Identify key columns by index (consistent across all 3 files)
    state_col    = df.columns[2]
    district_col = df.columns[3]

    # Detect file format
    has_fiscal_quarters = any(':Q' in str(col) for col in df.columns[:20])

    if has_fiscal_quarters:
        # ============================================================
        # HISTORICAL FORMAT: Fiscal quarters (2017-22, 2004-17 files)
        # Audit-verified structure (Feb 4 2026):
        #   Index 2 = "State or UTs" (title-case state names)
        #   Index 3 = "District"
        #   Index 4 = "2022-23:Q3" (quarter label, contains ':Q')
        #   Index 5 = Deposit (q_idx + 1)
        #   Index 6 = Credit  (q_idx + 2)
        # BALOD row 8: E8=87 (Offices), F8=3296 Crores (Deposit) confirmed
        # ============================================================
        print(f"    Format: Historical (fiscal quarters in column names)")

        quarter_label_cols = [i for i, col in enumerate(df.columns) if ':Q' in str(col)]
        print(f"    Quarter label columns found: {len(quarter_label_cols)}")

        print(f"    File structure check (first 3 quarters):")
        for i, q_idx in enumerate(quarter_label_cols[:3]):
            dep_idx = q_idx + 1
            if dep_idx < len(df.columns):
                print(f"      [{q_idx}] {df.columns[q_idx]} -> "
                      f"Deposit at [{dep_idx}] {df.columns[dep_idx]}")

        for q_idx in quarter_label_cols:
            col_name = str(df.columns[q_idx])

            # Deposit is the NEXT column after the quarter label.
            # Audit-confirmed: q_idx=Offices label, q_idx+1=Deposit, q_idx+2=Credit
            dep_idx = q_idx + 1

            if dep_idx >= len(df.columns):
                print(f"    WARNING: Skipping '{col_name}': "
                      f"no deposit column (index {dep_idx} out of range)")
                continue

            try:
                # Parse "2022-23:Q3" -> calendar year and quarter
                year_part, q_part = col_name.split(':Q')
                year_start = int(year_part.split('-')[0])
                fiscal_q   = int(q_part)

                # Indian fiscal year -> calendar year conversion:
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

            temp = temp.dropna(subset=['district_rbi', 'deposits'])

            temp_agg = temp.groupby(
                ['state_rbi', 'district_rbi', 'quarter', 'year', 'q'],
                as_index=False
            )['deposits'].sum()

            all_data.append(temp_agg)

    else:
        # ============================================================
        # CURRENT FORMAT: Calendar dates (2023-24 file)
        # Audit-verified structure (Feb 4 2026):
        #   Index 2 = "STATE" (uppercase state names)
        #   Index 3 = "DISTRICT"
        #   Index 5 = quarter label (timestamp, e.g. 2025-09-30)
        #   Index 6 = Accounts
        #   Index 7 = Deposit Amount  <- range(7,...,3) correct
        # ============================================================
        print(f"    Format: Current (calendar dates as timestamps)")

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

            temp = temp.dropna(subset=['district_rbi', 'deposits'])

            temp_agg = temp.groupby(
                ['state_rbi', 'district_rbi', 'quarter', 'year', 'q'],
                as_index=False
            )['deposits'].sum()

            all_data.append(temp_agg)


# Combine all quarters
print(f"\n[3] Combining all files...")
rbi_panel = pd.concat(all_data, ignore_index=True)
print(f"    Total rows before crosswalk: {len(rbi_panel)}")
print(f"    Unique district names: {rbi_panel['district_rbi'].nunique()}")
print(f"    Quarters range: {rbi_panel['quarter'].min()} to {rbi_panel['quarter'].max()}")


# [3b] HOMONYMOUS DISTRICT DIAGNOSTIC
# Print exact state_rbi values present in RBI data for each of the 7 pairs.
# Identifies any name mismatch between RBI data and state_mapping_rbi_to_gadm keys.
print(f"\n[3b] HOMONYMOUS DISTRICT DIAGNOSTIC")
for d in ['AURANGABAD', 'BALRAMPUR', 'BIJAPUR', 'BILASPUR',
          'HAMIRPUR', 'PRATAPGARH', 'RAIGARH']:
    rows   = rbi_panel[rbi_panel['district_rbi'] == d]
    states = sorted(rows['state_rbi'].str.upper().str.strip().unique().tolist())
    print(f"    {d}: {states}")

# Check known rename aliases that RBI may use instead of the homonymous name
for alias in ['RAIGAD', 'VIJAYAPURA', 'VIJAYAPURAM']:
    rows = rbi_panel[rbi_panel['district_rbi'] == alias]
    if len(rows) > 0:
        states = sorted(rows['state_rbi'].str.upper().str.strip().unique().tolist())
        print(f"    {alias} (alias): {states}")

# RBI uses "RAIGAD" for the Maharashtra district that GADM names "Raigarh".
# Normalise to RAIGARH so the crosswalk merge and state filter resolve correctly.
# All other district names match between RBI and GADM without normalisation.
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
print(f"    Name normalisation applied: RAIGAD/MAHARASHTRA -> RAIGARH/MAHARASHTRA")

# Map RBI districts to GADM using crosswalk
print(f"\n[4] Mapping RBI -> GADM districts...")

# State mapping for 7 homonymous districts.
# Keys: (district_rbi UPPERCASE, state_rbi UPPERCASE) -> GADM state (title case)
# state_rbi.upper().strip() normalises both "MAHARASHTRA" (File 1) and
# "Maharashtra" (Files 2-3, "State or UTs" column) to the same key.
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

# Merge with crosswalk (left join on district_rbi).
# Homonymous districts get duplicated: 2 crosswalk rows -> 2 result rows per quarter.
# Non-homonymous districts get 1 result row per quarter (unchanged).
rbi_panel = rbi_panel.merge(
    crosswalk[['district_rbi', 'district_gadm', 'state_gadm', 'matched_rbi_gadm']],
    on='district_rbi',
    how='left'
)

# Filter homonymous districts: keep only the row where state_gadm matches
# the expected state derived from state_rbi. Non-homonymous: keep all rows.
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

print(f"    After state filtering for homonymous districts:")
matched_count = rbi_panel['matched_rbi_gadm'].sum()
total_count   = len(rbi_panel)
print(f"    Matched: {matched_count}/{total_count} "
      f"({matched_count / total_count * 100:.1f}%)")

# Drop unmatched — replace fillna(False) to avoid FutureWarning
matched_mask = rbi_panel['matched_rbi_gadm'].notna() & rbi_panel['matched_rbi_gadm'].astype(bool)
rbi_panel    = rbi_panel[matched_mask].copy()
rbi_panel    = rbi_panel.drop(columns=['matched_rbi_gadm'])
print(f"    After dropping unmatched: {len(rbi_panel)} rows")

# DIAGNOSTIC: count both unique names AND unique district-state pairs.
# Unique names will be 624 (7 homonymous names counted once each).
# Unique pairs should be 631 (617 non-homonymous + 7 pairs x 2 states = 631).
# If pairs = 630, exactly one homonymous pair has only 1 state in RBI data.
unique_names = rbi_panel['district_gadm'].nunique()
unique_pairs = rbi_panel[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]
print(f"    Unique GADM district names:        {unique_names}")
print(f"    Unique GADM district-state pairs:  {unique_pairs}  "
      f"(target: 631 if homonymous fix propagated)")

# Add quarter_num (sequential index)
rbi_panel = rbi_panel.sort_values(['district_gadm', 'year', 'q'])
quarter_map              = {q: i + 1 for i, q in
                            enumerate(sorted(rbi_panel['quarter'].unique()))}
rbi_panel['quarter_num'] = rbi_panel['quarter'].map(quarter_map)


# [4b] Aggregate to GADM district-state-quarter level
print(f"\n[4b] Aggregating to unique GADM district-state-quarters...")
print(f"    Before aggregation: {len(rbi_panel)} rows")
rbi_panel = rbi_panel.groupby(
    ['district_gadm', 'state_gadm', 'quarter', 'year', 'q', 'quarter_num'],
    as_index=False
).agg({
    'deposits':     'sum',
    'district_rbi': lambda x: '; '.join(sorted(set(x))),
    'state_rbi':    'first'
})
print(f"    After aggregation: {len(rbi_panel)} rows")

unique_names_post = rbi_panel['district_gadm'].nunique()
unique_pairs_post = rbi_panel[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]
print(f"    Unique GADM district names:        {unique_names_post}")
print(f"    Unique GADM district-state pairs:  {unique_pairs_post}  "
      f"(target: 631)")

if unique_pairs_post < 631:
    print(f"    WARNING: Expected 631 pairs, got {unique_pairs_post}. "
          f"Check [3b] diagnostic for which pair is missing.")
elif unique_pairs_post == 631:
    print(f"    PASS: 631 district-state pairs confirmed.")
else:
    print(f"    WARNING: Got {unique_pairs_post} pairs, expected 631. "
          f"Unexpected extra pairs detected.")


# Reorder columns
rbi_panel = rbi_panel[[
    'district_gadm', 'state_gadm', 'quarter', 'year', 'q', 'quarter_num',
    'deposits', 'district_rbi', 'state_rbi'
]]


# Save
output_path = '02_Data_Intermediate/rbi_deposits_panel.csv'
rbi_panel.to_csv(output_path, index=False)

print(f"\n[5] OUTPUT SAVED")
print(f"    File: {output_path}")
print(f"    Rows: {len(rbi_panel)}")
print(f"    Columns: {rbi_panel.columns.tolist()}")


# [6] SUMMARY STATISTICS
print(f"\n[6] SUMMARY STATISTICS")
print(f"    District names:        {rbi_panel['district_gadm'].nunique()}")
print(f"    District-state pairs:  "
      f"{rbi_panel[['district_gadm', 'state_gadm']].drop_duplicates().shape[0]}")
print(f"    Quarters:              {rbi_panel['quarter'].nunique()}")
print(f"    Date range:            {rbi_panel['year'].min()}-{rbi_panel['year'].max()}")
print(f"    Total deposits (Rs Crores): {rbi_panel['deposits'].sum():,.0f}")
print(f"    Mean deposits per district-quarter: "
      f"{rbi_panel['deposits'].mean():,.0f}")


# [7] TEMPORAL COVERAGE CHECK
print(f"\n[7] TEMPORAL COVERAGE CHECK")
for year in sorted(rbi_panel['year'].unique()):
    quarters_present = sorted(rbi_panel[rbi_panel['year'] == year]['q'].unique())
    print(f"    {int(year)}: Q{[int(q) for q in quarters_present]}")


print("=" * 70)
print("RBI EXTRACTION COMPLETE (CORRECTED VERSION 2026-02-11)")
print("=" * 70)