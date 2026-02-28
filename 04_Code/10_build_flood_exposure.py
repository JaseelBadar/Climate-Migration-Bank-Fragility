import pandas as pd
import numpy as np
import geopandas as gpd


# Load inputs
emdat          = pd.read_csv('02_Data_Intermediate/emdat_districts_parsed.csv')
gadm_crosswalk = pd.read_csv('02_Data_Intermediate/district_crosswalk_draft.csv')
emdat_matches  = pd.read_csv('02_Data_Intermediate/emdat_district_matches.csv')
skeleton       = pd.read_csv('02_Data_Intermediate/district_quarter_skeleton.csv')

print(f"EM-DAT events loaded:     {len(emdat)}")
print(f"EM-DAT district matches:  {len(emdat_matches)}")
print(f"Skeleton rows:            {len(skeleton)}")


# Convert start date to calendar quarter
def date_to_quarter(year, month):
    if pd.isna(month):
        return None
    return f"{int(year)}Q{((int(month) - 1) // 3) + 1}"

emdat['quarter'] = emdat.apply(
    lambda r: date_to_quarter(r['Start Year'], r['Start Month']), axis=1
)


# State-to-district lookup from GADM
gadm = gpd.read_file('01_Data_Raw/District_Boundaries/gadm41_IND_2.shp')
state_districts = gadm[['NAME_1', 'NAME_2']].drop_duplicates().copy()
state_districts.columns = ['state', 'district_gadm']


# State name aliases for known variations in EM-DAT text
state_aliases = {
    'delhi':       'NCT of Delhi',
    'orissa':      'Odisha',
    'pondicherry': 'Puducherry'
}


def normalize_state_token(token):
    """Lowercase, strip trailing 'state'/'states', apply aliases."""
    t = token.lower().strip()
    t = t.replace(' states', '').replace(' state', '').strip()
    if t in state_aliases:
        return state_aliases[t]
    return t


# Initialize flood exposure columns
skeleton['flood_exposure_ruleA_qt'] = 0
skeleton['flood_exposure_ruleB_qt'] = 0

# NOTE ON HOMONYMOUS DISTRICTS:
# emdat_matches has no state column, so district-level flood assignment uses
# district_gadm name only. For the 7 homonymous pairs (e.g. Aurangabad Bihar
# and Aurangabad Maharashtra), both state copies in the skeleton will be coded
# as flooded if either appears in EM-DAT. This is an accepted limitation —
# measurement error attenuates treatment effects toward zero (conservative bias).

skipped_no_quarter = 0
warnings_unmatched = []

for idx, event in emdat.iterrows():
    qtr = event['quarter']
    if pd.isna(qtr):
        print(f"WARNING: Event {event['DisNo.']} has no quarter (missing month), skipping")
        skipped_no_quarter += 1
        continue

    districts_str = event['districts_final_str']
    if pd.isna(districts_str):
        continue

    tokens = [d.strip() for d in str(districts_str).split(';')]

    for token in tokens:
        # Step 1: Check emdat_matches for district-level match
        match_row = emdat_matches[
            emdat_matches['district_emdat'].str.lower() == token.lower()
        ]

        if not match_row.empty and match_row.iloc[0]['matched_emdat_gadm']:
            # District-level match — eligible for both Rule A and Rule B
            gadm_dist = match_row.iloc[0]['district_gadm_match']
            skeleton.loc[
                (skeleton['quarter'] == qtr) &
                (skeleton['district_gadm'] == gadm_dist),
                ['flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt']
            ] = 1

        else:
            # Step 2: Check if token is a state name — Rule A only
            normalized = normalize_state_token(token)
            state_match = state_districts[
                state_districts['state'].str.lower() == normalized.lower()
            ]
            if not state_match.empty:
                affected_dists = state_match['district_gadm'].unique()
                skeleton.loc[
                    (skeleton['quarter'] == qtr) &
                    (skeleton['district_gadm'].isin(affected_dists)),
                    'flood_exposure_ruleA_qt'
                ] = 1
                # Rule B: state-level not eligible — do not assign
            else:
                warnings_unmatched.append(
                    f"  Event {event['DisNo.']}: '{token}'"
                )


# Report unmatched tokens
if warnings_unmatched:
    print(f"\nUNMATCHED TOKENS ({len(warnings_unmatched)}):")
    for w in warnings_unmatched:
        print(w)

if skipped_no_quarter > 0:
    print(f"\nEvents skipped (missing month): {skipped_no_quarter}")


# Summary statistics
ruleA_exposed = (skeleton['flood_exposure_ruleA_qt'] == 1).sum()
ruleB_exposed = (skeleton['flood_exposure_ruleB_qt'] == 1).sum()
print(f"\nFLOOD EXPOSURE SUMMARY:")
print(f"  Rule A district-quarters exposed: {ruleA_exposed} "
      f"({ruleA_exposed / len(skeleton) * 100:.1f}% of panel)")
print(f"  Rule B district-quarters exposed: {ruleB_exposed} "
      f"({ruleB_exposed / len(skeleton) * 100:.1f}% of panel)")
print(f"  Rule B <= Rule A: "
      f"{'PASS' if ruleB_exposed <= ruleA_exposed else 'FAIL'}")


# Save
output_path = '02_Data_Intermediate/flood_exposure_panel.csv'
skeleton.to_csv(output_path, index=False)
print(f"\nSaved: {output_path} ({len(skeleton)} rows)")