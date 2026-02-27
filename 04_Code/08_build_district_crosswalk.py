import pandas as pd
import geopandas as gpd
from rapidfuzz import fuzz, process
import os
from datetime import datetime


start_time = datetime.now()
print("=" * 70)
print("DISTRICT CROSSWALK BUILD - Phase 3c Day 3 (CORRECTED 2026-02-28)")
print("=" * 70)
print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")


# === [1/5] GADM DISTRICTS ===
print("\n[1/5] LOADING GADM DISTRICT BOUNDARIES...")
gadm_path = '01_Data_Raw/District_Boundaries/gadm41_IND_2.shp'
gadm = gpd.read_file(gadm_path)
print(f"   GADM rows loaded: {len(gadm)}")

gadm_districts = gadm[['NAME_2', 'NAME_1']].drop_duplicates().copy()
gadm_districts.columns = ['district_gadm', 'state_gadm']
gadm_districts = gadm_districts.sort_values(['state_gadm', 'district_gadm']).reset_index(drop=True)
print(f"   Unique GADM district-state pairs: {len(gadm_districts)}")

# Verify homonymous pairs are present in GADM
homonyms = ['Aurangabad', 'Balrampur', 'Bijapur', 'Bilaspur', 'Hamirpur', 'Pratapgarh', 'Raigarh']
print(f"\n   Homonymous district check in GADM:")
for d in homonyms:
    rows = gadm_districts[gadm_districts['district_gadm'] == d]
    states = rows['state_gadm'].tolist()
    print(f"      {d}: {len(rows)} row(s) → {states}")


# === [2/5] RBI DISTRICTS ===
print("\n[2/5] LOADING RBI DISTRICT NAMES...")
rbi_path = '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xlsx'
rbi = pd.read_excel(rbi_path, sheet_name=0, skiprows=5)
print(f"   RBI file loaded: {rbi.shape}")

if 'DISTRICT' in rbi.columns:
    rbi_districts_raw = rbi['DISTRICT'].dropna().astype(str).unique()
    rbi_unique = sorted([d.strip().upper() for d in rbi_districts_raw if len(d.strip()) > 0])
    print(f"   Unique RBI districts parsed: {len(rbi_unique)}")
else:
    print("   ERROR: 'DISTRICT' column not found!")
    print(f"   Available columns: {list(rbi.columns)}")
    rbi_unique = []

# Also extract RBI state column to carry forward for state-aware matching
if 'STATE' in rbi.columns:
    rbi_district_state = rbi[['STATE', 'DISTRICT']].dropna().drop_duplicates().copy()
    rbi_district_state.columns = ['state_rbi', 'district_rbi']
    rbi_district_state['district_rbi'] = rbi_district_state['district_rbi'].str.strip().str.upper()
    rbi_district_state['state_rbi'] = rbi_district_state['state_rbi'].str.strip().str.upper()
    print(f"   RBI district-state pairs extracted: {len(rbi_district_state)}")
else:
    rbi_district_state = None
    print("   WARNING: 'STATE' column not found — state-aware matching unavailable")


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


# === [4/5] FUZZY MATCH RBI → GADM ===
print("\n[4/5] FUZZY MATCHING RBI → GADM...")


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
    best_match, score, matched = fuzzy_match_best(rbi_dist, gadm_choices, threshold=80)
    rbi_gadm_matches.append({
        'district_rbi': rbi_dist,
        'district_gadm': best_match,
        'match_score_rbi_gadm': score,
        'matched_rbi_gadm': matched
    })

df_crosswalk = pd.DataFrame(rbi_gadm_matches)

match_rate_rbi_gadm = (df_crosswalk['matched_rbi_gadm'].sum() / len(df_crosswalk)) * 100
print(f"   RBI → GADM match rate: {match_rate_rbi_gadm:.1f}% ({df_crosswalk['matched_rbi_gadm'].sum()}/{len(df_crosswalk)})")

if match_rate_rbi_gadm < 80:
    print("\n" + "!" * 70)
    print("STOP CONDITION TRIGGERED")
    print(f"Match rate ({match_rate_rbi_gadm:.1f}%) is below 80% threshold.")
    print("!" * 70)


# Join ALL GADM state rows (one per district-state pair).
# CRITICAL FIX: Do NOT deduplicate here.
# Homonymous districts (e.g. AURANGABAD) will correctly produce 2 rows:
#   one for Bihar, one for Maharashtra.
# Script 13 uses the RBI state column to filter to the correct row.
df_crosswalk = df_crosswalk.merge(
    gadm_districts[['district_gadm', 'state_gadm']],
    on='district_gadm',
    how='left'
)

# Flag ambiguous (homonymous) matches — rows with multiple state options
ambiguity_counts = df_crosswalk.groupby('district_rbi')['state_gadm'].transform('count')
df_crosswalk['is_ambiguous_match'] = ambiguity_counts > 1

# Report homonymous districts (informational — do NOT remove)
duplicate_check = df_crosswalk.groupby('district_rbi').size()
duplicates_found = duplicate_check[duplicate_check > 1]

if len(duplicates_found) > 0:
    print(f"\n   INFO: {len(duplicates_found)} homonymous RBI districts have multiple GADM state rows:")
    print(f"   These are KEPT — Script 13 resolves them via RBI state column.")
    for rbi_dist in duplicates_found.index:
        matches = df_crosswalk[df_crosswalk['district_rbi'] == rbi_dist][['district_gadm', 'state_gadm']]
        states = matches['state_gadm'].tolist()
        print(f"      {rbi_dist}: {len(matches)} rows → {states}")
else:
    print(f"\n   No homonymous districts detected")

print(f"\n   Final crosswalk rows: {len(df_crosswalk)}")
print(f"   (includes {len(duplicates_found)} homonymous districts with 2 rows each)")


# === [5/5] EM-DAT MATCHING ===
print("\n[5/5] MATCHING EM-DAT DISTRICTS (informational)...")

emdat_gadm_matches = []
for emdat_dist in emdat_unique:
    best_match, score, matched = fuzzy_match_best(emdat_dist, gadm_choices, threshold=75)
    emdat_gadm_matches.append({
        'district_emdat': emdat_dist,
        'district_gadm_match': best_match,
        'match_score_emdat_gadm': score,
        'matched_emdat_gadm': matched
    })

df_emdat_matches = pd.DataFrame(emdat_gadm_matches)
match_rate_emdat = (df_emdat_matches['matched_emdat_gadm'].sum() / len(df_emdat_matches)) * 100
print(f"   EM-DAT → GADM match rate: {match_rate_emdat:.1f}% ({df_emdat_matches['matched_emdat_gadm'].sum()}/{len(df_emdat_matches)})")


# === SAVE OUTPUTS ===
output_path = '02_Data_Intermediate/district_crosswalk_draft.csv'
df_crosswalk.to_csv(output_path, index=False)
print(f"\n✓ Crosswalk saved: {output_path} ({len(df_crosswalk)} rows)")

emdat_output_path = '02_Data_Intermediate/emdat_district_matches.csv'
df_emdat_matches.to_csv(emdat_output_path, index=False)
print(f"✓ EM-DAT matches saved: {emdat_output_path}")


# === LOG ===
end_time = datetime.now()
log_lines = [
    "=" * 70,
    "DISTRICT CROSSWALK BUILD LOG (CORRECTED 2026-02-28)",
    "=" * 70,
    f"Script: 08_build_district_crosswalk.py",
    f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"Duration: {(end_time - start_time).seconds} seconds",
    "",
    "CRITICAL FIX APPLIED:",
    "  Old behaviour: drop_duplicates(subset=['district_rbi'], keep='first')",
    "  This silently dropped the second state row for all 7 homonymous pairs,",
    "  causing Maharashtra/UP/Karnataka/HP copies to have 0 deposits in",
    "  rbi_deposits_panel → dropped by Script 17 → only 624 districts in panel.",
    "  New behaviour: retain ALL rows; flag with is_ambiguous_match=True.",
    "  Script 13 resolves ambiguity via state_rbi column.",
    "",
    "INPUTS:",
    f"  - GADM: {gadm_path} ({len(gadm_districts)} unique district-state pairs)",
    f"  - RBI: {rbi_path} ({len(rbi_unique)} unique districts)",
    f"  - EM-DAT: {emdat_path} ({len(emdat_unique)} unique districts)",
    "",
    "OUTPUTS:",
    f"  - Crosswalk: {output_path} ({len(df_crosswalk)} rows)",
    f"  - EM-DAT matches: {emdat_output_path} ({len(df_emdat_matches)} rows)",
    "",
    "MATCH RATES:",
    f"  - RBI → GADM: {match_rate_rbi_gadm:.1f}% (threshold: 80%)",
    f"  - EM-DAT → GADM: {match_rate_emdat:.1f}% (informational, threshold: 75%)",
    "",
    "STOP CONDITION:",
    f"  - {'PASSED' if match_rate_rbi_gadm >= 80 else 'FAILED'} - RBI match rate {'≥' if match_rate_rbi_gadm >= 80 else '<'} 80%",
    "",
    "HOMONYMOUS DISTRICTS (2 rows each — intentional):",
]

for rbi_dist in duplicates_found.index:
    matches = df_crosswalk[df_crosswalk['district_rbi'] == rbi_dist][['district_gadm', 'state_gadm']]
    for _, row in matches.iterrows():
        log_lines.append(f"  - {rbi_dist} → {row['district_gadm']}, {row['state_gadm']}")

log_lines += [
    "",
    "UNMATCHED DISTRICTS (RBI → GADM):",
]
unmatched = df_crosswalk[~df_crosswalk['matched_rbi_gadm']].drop_duplicates('district_rbi').sort_values('match_score_rbi_gadm')
for _, row in unmatched.iterrows():
    log_lines.append(f"  - {row['district_rbi']} (score: {row['match_score_rbi_gadm']})")

log_lines.append("")
log_lines.append("=" * 70)

log_path = '05_Outputs/Logs/08_build_crosswalk_log.txt'
os.makedirs('05_Outputs/Logs', exist_ok=True)
with open(log_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
print(f"✓ Log saved: {log_path}")

print("\n" + "=" * 70)
print("CROSSWALK BUILD COMPLETE (CORRECTED 2026-02-28)")
print("=" * 70)