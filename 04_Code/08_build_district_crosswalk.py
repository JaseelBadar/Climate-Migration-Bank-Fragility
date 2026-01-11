import pandas as pd
import geopandas as gpd
from rapidfuzz import fuzz, process
import os
from datetime import datetime

# Start log
start_time = datetime.now()
print("="*70)
print("DISTRICT CROSSWALK BUILD - Phase 3c Day 3")
print("="*70)
print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

# A. Load GADM district boundaries
print("\n[1/5] LOADING GADM DISTRICT BOUNDARIES...")
gadm_path = '01_Data_Raw/District_Boundaries/gadm41_IND_2.shp'
gadm = gpd.read_file(gadm_path)
print(f"   GADM districts loaded: {len(gadm)}")
print(f"   Columns: {list(gadm.columns)}")

# Extract unique district-state pairs
gadm_districts = gadm[['NAME_2', 'NAME_1']].drop_duplicates().copy()
gadm_districts.columns = ['district_gadm', 'state_gadm']
gadm_districts = gadm_districts.sort_values(['state_gadm', 'district_gadm']).reset_index(drop=True)
print(f"   Unique GADM district-state pairs: {len(gadm_districts)}")

# B. Load RBI district names from 2023-2024 file
print("\n[2/5] LOADING RBI DISTRICT NAMES...")
rbi_path = '01_Data_Raw/RBI_Bank_Data/RBI_Deposits_2023_2024.xlsx'
rbi = pd.read_excel(rbi_path, sheet_name=0, skiprows=5)
print(f"   RBI file loaded: {rbi.shape}")
print(f"   Columns found: {list(rbi.columns[:5])}")  # Show first 5 columns

# Extract unique districts from the 'DISTRICT' column (column 3)
if 'DISTRICT' in rbi.columns:
    rbi_districts_raw = rbi['DISTRICT'].dropna().astype(str).unique()
    print(f"   Raw unique district values: {len(rbi_districts_raw)}")
    
    # Clean district names: uppercase and strip whitespace
    rbi_unique = sorted([d.strip().upper() for d in rbi_districts_raw if len(d.strip()) > 0])
    print(f"   Unique RBI districts parsed: {len(rbi_unique)}")
    print(f"   Sample RBI districts (first 10): {rbi_unique[:10]}")
else:
    print("   ERROR: 'DISTRICT' column not found!")
    print(f"   Available columns: {list(rbi.columns)}")
    rbi_unique = []

# C. Load EM-DAT parsed districts
print("\n[3/5] LOADING EM-DAT PARSED DISTRICTS...")
emdat_path = '02_Data_Intermediate/emdat_districts_parsed.csv'
emdat = pd.read_csv(emdat_path)
print(f"   EM-DAT events loaded: {len(emdat)}")

# Extract all district names from 'districts_final_str' column
# Format: semicolon-separated list
emdat_all_districts = set()
for districts_str in emdat['districts_final_str'].dropna():
    districts = str(districts_str).split(';')
    for d in districts:
        d_clean = d.strip()
        if d_clean and d_clean not in ['state', 'states', 'districts', 'district']:
            emdat_all_districts.add(d_clean.title())  # Normalize to title case

emdat_unique = sorted(emdat_all_districts)
print(f"   Unique EM-DAT districts: {len(emdat_unique)}")

print("\n[4/5] FUZZY MATCHING RBI → GADM...")

# Define fuzzy matching function
def fuzzy_match_best(query, choices, threshold=80):
    """
    Returns best match from choices using rapidfuzz
    Returns (best_match, score, match_found_flag)
    """
    if not choices or not query:
        return (None, 0, False)
    
    result = process.extractOne(
        query.upper(),
        [c.upper() for c in choices],
        scorer=fuzz.ratio
    )
    
    if result and result[1] >= threshold:
        # Find original case version
        original_match = choices[result[2]]
        return (original_match, result[1], True)
    else:
        return (None, result[1] if result else 0, False)

# Match RBI → GADM
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

# Calculate match rate
match_rate_rbi_gadm = (df_crosswalk['matched_rbi_gadm'].sum() / len(df_crosswalk)) * 100
print(f"   RBI → GADM match rate: {match_rate_rbi_gadm:.1f}% ({df_crosswalk['matched_rbi_gadm'].sum()}/{len(df_crosswalk)})")

# STOP CONDITION CHECK
if match_rate_rbi_gadm < 80:
    print("\n" + "!"*70)
    print("STOP CONDITION TRIGGERED")
    print(f"Match rate ({match_rate_rbi_gadm:.1f}%) is below 80% threshold.")
    print("Review unmatched districts before proceeding.")
    print("!"*70)

    # Join state names from GADM
df_crosswalk = df_crosswalk.merge(
    gadm_districts[['district_gadm', 'state_gadm']],
    on='district_gadm',
    how='left'
)

print("\n[5/5] MATCHING EM-DAT DISTRICTS (informational)...")

# Match EM-DAT → GADM
emdat_gadm_matches = []
for emdat_dist in emdat_unique:
    best_match, score, matched = fuzzy_match_best(emdat_dist, gadm_choices, threshold=75)  # Lower threshold
    emdat_gadm_matches.append({
        'district_emdat': emdat_dist,
        'district_gadm_match': best_match,
        'match_score_emdat_gadm': score,
        'matched_emdat_gadm': matched
    })

df_emdat_matches = pd.DataFrame(emdat_gadm_matches)
match_rate_emdat = (df_emdat_matches['matched_emdat_gadm'].sum() / len(df_emdat_matches)) * 100
print(f"   EM-DAT → GADM match rate: {match_rate_emdat:.1f}% ({df_emdat_matches['matched_emdat_gadm'].sum()}/{len(df_emdat_matches)})")

# Save crosswalk
output_path = '02_Data_Intermediate/district_crosswalk_draft.csv'
df_crosswalk.to_csv(output_path, index=False)
print(f"\n✓ Crosswalk saved: {output_path}")

# Save EM-DAT matches separately (for manual review)
emdat_output_path = '02_Data_Intermediate/emdat_district_matches.csv'
df_emdat_matches.to_csv(emdat_output_path, index=False)
print(f"✓ EM-DAT matches saved: {emdat_output_path}")

# Generate log
end_time = datetime.now()
log_lines = [
    "="*70,
    "DISTRICT CROSSWALK BUILD LOG",
    "="*70,
    f"Script: 08_build_district_crosswalk.py",
    f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
    f"Duration: {(end_time - start_time).seconds} seconds",
    "",
    "INPUTS:",
    f"  - GADM: {gadm_path} ({len(gadm_districts)} unique districts)",
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
    "UNMATCHED DISTRICTS (RBI → GADM):",
]

# Add unmatched districts to log
unmatched = df_crosswalk[~df_crosswalk['matched_rbi_gadm']].sort_values('match_score_rbi_gadm')
for idx, row in unmatched.iterrows():
    log_lines.append(f"  - {row['district_rbi']} (score: {row['match_score_rbi_gadm']})")

log_lines.append("")
log_lines.append("="*70)

# Save log
log_path = '05_Outputs/Logs/08_build_crosswalk_log.txt'
os.makedirs('05_Outputs/Logs', exist_ok=True)
with open(log_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
print(f"✓ Log saved: {log_path}")

print("\n" + "="*70)
print("CROSSWALK BUILD COMPLETE")
print("="*70)