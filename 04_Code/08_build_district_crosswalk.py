import pandas as pd
import geopandas as gpd
from rapidfuzz import fuzz, process
import os
from datetime import datetime


start_time = datetime.now()
print("=" * 70)
print("DISTRICT CROSSWALK BUILD - Phase 3c (PERMANENT FIX 2026-03-05)")
print("=" * 70)
print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")


# ============================================================
# DESIGN NOTE (2026-03-05 permanent fix)
# ============================================================
# Feb 28 rewrite changed design to retain 769 rows, relying on
# Script 13 state filtering to resolve homonyms downstream.
# This broke Script 12 (flood exposure), which has no state
# filtering and produced 10 artificial flood matches.
#
# Correct design (restores Feb 11 intent):
#   Script 8  -> outputs EXACTLY 762 rows (one row per RBI district)
#   Script 13 -> state filtering resolves deposit assignment for
#                7 homonymous pairs (already implemented Feb 11)
#   Script 12 -> sees 762 rows, no duplicates, no artificial matches
#
# Detection fix (Feb 28 already correct):
#   Use .groupby('district_rbi').size() to count ROWS per district.
#   Never use .nunique() on district_gadm names -- homonyms share
#   the same name in both states, so nunique=1 and detection fails.
# ============================================================


# === [1/5] GADM DISTRICTS ===
print("\n[1/5] LOADING GADM DISTRICT BOUNDARIES...")
gadm_path = '01_Data_Raw/District_Boundaries/gadm41_IND_2.shp'
gadm = gpd.read_file(gadm_path)
print(f"   GADM rows loaded: {len(gadm)}")

gadm_districts = gadm[['NAME_2', 'NAME_1']].drop_duplicates().copy()
gadm_districts.columns = ['district_gadm', 'state_gadm']
gadm_districts = gadm_districts.sort_values(
    ['state_gadm', 'district_gadm']
).reset_index(drop=True)
print(f"   Unique GADM district-state pairs: {len(gadm_districts)}")

homonyms_expected = [
    'Aurangabad', 'Balrampur', 'Bijapur',
    'Bilaspur', 'Hamirpur', 'Pratapgarh', 'Raigarh'
]
print(f"\n   Homonymous district check in GADM (expected: 7 pairs):")
for d in homonyms_expected:
    rows = gadm_districts[gadm_districts['district_gadm'] == d]
    states = rows['state_gadm'].tolist()
    print(f"      {d}: {len(rows)} row(s) -> {states}")


# === [2/5] RBI DISTRICTS ===
print("\n[2/5] LOADING RBI DISTRICT NAMES...")
rbi_path = '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xlsx'
rbi = pd.read_excel(rbi_path, sheet_name=0, skiprows=5)
print(f"   RBI file loaded: {rbi.shape}")

if 'DISTRICT' in rbi.columns:
    rbi_districts_raw = rbi['DISTRICT'].dropna().astype(str).unique()
    rbi_unique = sorted([
        d.strip().upper()
        for d in rbi_districts_raw
        if len(d.strip()) > 0
    ])
    print(f"   Unique RBI districts parsed: {len(rbi_unique)}")
else:
    print("   ERROR: 'DISTRICT' column not found!")
    print(f"   Available columns: {list(rbi.columns)}")
    rbi_unique = []

if 'STATE' in rbi.columns:
    rbi_district_state = rbi[['STATE', 'DISTRICT']].dropna().drop_duplicates().copy()
    rbi_district_state.columns = ['state_rbi', 'district_rbi']
    rbi_district_state['district_rbi'] = (
        rbi_district_state['district_rbi'].str.strip().str.upper()
    )
    rbi_district_state['state_rbi'] = (
        rbi_district_state['state_rbi'].str.strip().str.upper()
    )
    print(f"   RBI district-state pairs extracted: {len(rbi_district_state)}")
else:
    rbi_district_state = None
    print("   WARNING: 'STATE' column not found -- state-aware matching unavailable")


# === [3/5] EM-DAT DISTRICTS ===
print("\n[3/5] LOADING EM-DAT PARSED DISTRICTS...")
emdat_path = '02_Data_Intermediate/emdat_districts_parsed.csv'
emdat = pd.read_csv(emdat_path)
print(f"   EM-DAT events loaded: {len(emdat)}")

emdat_all_districts = set()
for districts_str in emdat['districts_final_str'].dropna():
    for d in str(districts_str).split(';'):
        d_clean = d.strip()
        if d_clean and d_clean not in ['state', 'states', 'districts', 'district']:
            emdat_all_districts.add(d_clean.title())

emdat_unique = sorted(emdat_all_districts)
print(f"   Unique EM-DAT districts: {len(emdat_unique)}")


# === [4/5] FUZZY MATCH RBI -> GADM ===
print("\n[4/5] FUZZY MATCHING RBI -> GADM...")


def fuzzy_match_best(query, choices, threshold=80):
    if not choices or not query:
        return (None, 0, False)
    result = process.extractOne(
        query.upper(),
        [c.upper() for c in choices],
        scorer=fuzz.ratio
    )
    if result and result[1] >= threshold:
        original_match = choices[result[2]]
        return (original_match, result[1], True)
    else:
        return (None, result[1] if result else 0, False)


gadm_choices = gadm_districts['district_gadm'].tolist()
rbi_gadm_matches = []

for rbi_dist in rbi_unique:
    best_match, score, matched = fuzzy_match_best(
        rbi_dist, gadm_choices, threshold=80
    )
    rbi_gadm_matches.append({
        'district_rbi':         rbi_dist,
        'district_gadm':        best_match,
        'match_score_rbi_gadm': score,
        'matched_rbi_gadm':     matched
    })

df_crosswalk = pd.DataFrame(rbi_gadm_matches)

match_rate_rbi_gadm = (
    df_crosswalk['matched_rbi_gadm'].sum() / len(df_crosswalk)
) * 100
print(f"   RBI -> GADM match rate: {match_rate_rbi_gadm:.1f}% "
      f"({df_crosswalk['matched_rbi_gadm'].sum()}/{len(df_crosswalk)})")

if match_rate_rbi_gadm < 80:
    print("\n" + "!" * 70)
    print("STOP CONDITION TRIGGERED")
    print(f"Match rate ({match_rate_rbi_gadm:.1f}%) is below 80% threshold.")
    print("!" * 70)


# --- Merge ALL GADM state rows (this intentionally creates duplicate rows
#     for homonymous districts -- detected and removed in the block below).
df_crosswalk = df_crosswalk.merge(
    gadm_districts[['district_gadm', 'state_gadm']],
    on='district_gadm',
    how='left'
)

# --- Detect duplicates using row count per district_rbi (.size()).
#     NEVER use .nunique() on district_gadm names:
#     homonyms share the same name across states, so nunique=1
#     and duplicates are silently missed (root cause of Feb 27 failure).
rows_before_dedup = len(df_crosswalk)
duplicate_check = df_crosswalk.groupby('district_rbi').size()
duplicates_found = duplicate_check[duplicate_check > 1]

if len(duplicates_found) > 0:
    print(f"\n   WARNING: {len(duplicates_found)} RBI districts match "
          f"multiple GADM states (homonymous pairs):")
    for rbi_dist in duplicates_found.index:
        matches = df_crosswalk[
            df_crosswalk['district_rbi'] == rbi_dist
        ][['district_gadm', 'state_gadm']]
        states = matches['state_gadm'].tolist()
        print(f"      {rbi_dist}: {len(matches)} rows -> {states}")

    # Flag before dedup (preserve audit trail).
    df_crosswalk['is_ambiguous_match'] = (
        df_crosswalk['district_rbi'].isin(duplicates_found.index)
    )

    # Deduplicate: keep first match per RBI district.
    # Script 13 state filtering (applied Feb 11) ensures deposits are
    # assigned to the correct state regardless of which row is kept here.
    print(f"\n   APPLYING DEDUPLICATION: keeping first match per district_rbi")
    df_crosswalk = df_crosswalk.drop_duplicates(
        subset='district_rbi', keep='first'
    ).reset_index(drop=True)

    rows_after_dedup = len(df_crosswalk)
    print(f"   Before dedup: {rows_before_dedup} rows")
    print(f"   After dedup:  {rows_after_dedup} rows")
    print(f"   Removed:      {rows_before_dedup - rows_after_dedup} duplicate mappings")
else:
    df_crosswalk['is_ambiguous_match'] = False
    print(f"\n   No homonymous districts detected")

# --- HARD ASSERT: crosswalk must be exactly 762 rows before save.
#     If this fails, script aborts and writes nothing to disk.
#     762 = unique RBI districts after resolving 7 homonymous pairs.
assert len(df_crosswalk) == 762, (
    f"FATAL: crosswalk has {len(df_crosswalk)} rows, expected exactly 762. "
    f"Deduplication failed or RBI source district count has changed. "
    f"Do not proceed. Investigate before re-running."
)
print(f"\n   ASSERT PASSED: crosswalk = {len(df_crosswalk)} rows (expected 762)")
print(f"   Final crosswalk: {len(df_crosswalk)} rows, "
      f"{df_crosswalk['district_rbi'].nunique()} unique RBI districts")


# === [5/5] EM-DAT MATCHING ===
print("\n[5/5] MATCHING EM-DAT DISTRICTS (informational)...")

emdat_gadm_matches = []
for emdat_dist in emdat_unique:
    best_match, score, matched = fuzzy_match_best(
        emdat_dist, gadm_choices, threshold=75
    )
    emdat_gadm_matches.append({
        'district_emdat':         emdat_dist,
        'district_gadm_match':    best_match,
        'match_score_emdat_gadm': score,
        'matched_emdat_gadm':     matched
    })

df_emdat_matches = pd.DataFrame(emdat_gadm_matches)
match_rate_emdat = (
    df_emdat_matches['matched_emdat_gadm'].sum() / len(df_emdat_matches)
) * 100
print(f"   EM-DAT -> GADM match rate: {match_rate_emdat:.1f}% "
      f"({df_emdat_matches['matched_emdat_gadm'].sum()}/{len(df_emdat_matches)})")


# === SAVE OUTPUTS (only reached if assert passes) ===
output_path = '02_Data_Intermediate/district_crosswalk_draft.csv'
df_crosswalk.to_csv(output_path, index=False)
print(f"\nCrosswalk saved: {output_path} ({len(df_crosswalk)} rows)")

emdat_output_path = '02_Data_Intermediate/emdat_district_matches.csv'
df_emdat_matches.to_csv(emdat_output_path, index=False)
print(f"EM-DAT matches saved: {emdat_output_path}")


# === LOG ===
end_time = datetime.now()

# Build homonym summary for log.
homonym_log_lines = []
for rbi_dist in duplicates_found.index:
    all_rows = pd.DataFrame(rbi_gadm_matches)
    all_rows = all_rows.merge(
        gadm_districts[['district_gadm', 'state_gadm']],
        on='district_gadm', how='left'
    )
    all_rows = all_rows[all_rows['district_rbi'] == rbi_dist]
    states = all_rows['state_gadm'].tolist()
    kept = df_crosswalk[
        df_crosswalk['district_rbi'] == rbi_dist
    ]['state_gadm'].values[0]
    dropped = [s for s in states if s != kept]
    homonym_log_lines.append(
        f"  - {rbi_dist}: kept {kept}, dropped {dropped}"
    )

unmatched = (
    df_crosswalk[~df_crosswalk['matched_rbi_gadm']]
    .drop_duplicates('district_rbi')
    .sort_values('match_score_rbi_gadm')
)

log_lines = [
    "=" * 70,
    "DISTRICT CROSSWALK BUILD LOG (PERMANENT FIX 2026-03-05)",
    "=" * 70,
    f"Script:    08_build_district_crosswalk.py",
    f"Start:     {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"End:       {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"Duration:  {(end_time - start_time).seconds} seconds",
    "",
    "FIX HISTORY:",
    "  Feb 07: dedup used .nunique() on district_gadm names -- failed silently",
    "          because homonyms share the same name; reported 0 duplicates.",
    "  Feb 11: corrected to .groupby().size(); detected 7 pairs; deduped to 762.",
    "  Feb 28: design changed to retain 769 rows; broke Script 12 (flood exposure)",
    "          which has no state filtering; produced 10 artificial flood matches.",
    "  Mar 05: reverted to 762-row output; added hard assert before save.",
    "          Script 13 state filtering (Feb 11) handles deposit disambiguation.",
    "",
    "DESIGN:",
    "  Script 8  -> 762 rows (one per RBI district, homonyms deduplicated)",
    "  Script 12 -> uses 762-row crosswalk, no artificial flood matches",
    "  Script 13 -> state filtering resolves deposit assignment for 7 pairs",
    "",
    "ASSERT:",
    f"  len(df_crosswalk) == 762: PASSED ({len(df_crosswalk)} rows)",
    "",
    "INPUTS:",
    f"  - GADM:   {gadm_path} ({len(gadm_districts)} unique district-state pairs)",
    f"  - RBI:    {rbi_path} ({len(rbi_unique)} unique districts)",
    f"  - EM-DAT: {emdat_path} ({len(emdat_unique)} unique districts)",
    "",
    "OUTPUTS:",
    f"  - Crosswalk:    {output_path} ({len(df_crosswalk)} rows)",
    f"  - EM-DAT match: {emdat_output_path} ({len(df_emdat_matches)} rows)",
    "",
    "MATCH RATES:",
    f"  - RBI -> GADM:   {match_rate_rbi_gadm:.1f}% (threshold: 80%)",
    f"  - EM-DAT -> GADM: {match_rate_emdat:.1f}% (informational, threshold: 75%)",
    "",
    "STOP CONDITION:",
    f"  - {'PASSED' if match_rate_rbi_gadm >= 80 else 'FAILED'} -- "
    f"RBI match rate {'at or above' if match_rate_rbi_gadm >= 80 else 'below'} 80%",
    "",
    f"HOMONYMOUS DISTRICTS RESOLVED ({len(duplicates_found)} pairs, "
    f"{rows_before_dedup - len(df_crosswalk)} rows removed):",
] + homonym_log_lines + [
    "",
    "UNMATCHED DISTRICTS (RBI -> GADM):",
] + [
    f"  - {row['district_rbi']} (score: {row['match_score_rbi_gadm']})"
    for _, row in unmatched.iterrows()
] + [
    "",
    "=" * 70,
]

log_path = '05_Outputs/Logs/08_build_crosswalk_log.txt'
os.makedirs('05_Outputs/Logs', exist_ok=True)
with open(log_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
print(f"Log saved: {log_path}")


print("\n" + "=" * 70)
print("CROSSWALK BUILD COMPLETE (PERMANENT FIX 2026-03-05)")
print(f"Crosswalk: {len(df_crosswalk)} rows | Assert: PASSED")
print("=" * 70)