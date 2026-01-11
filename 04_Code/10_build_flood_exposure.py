import pandas as pd
import numpy as np
import geopandas as gpd

# Load
emdat = pd.read_csv('02_Data_Intermediate/emdat_districts_parsed.csv')
gadm_crosswalk = pd.read_csv('02_Data_Intermediate/district_crosswalk_draft.csv')
emdat_matches = pd.read_csv('02_Data_Intermediate/emdat_district_matches.csv')
skeleton = pd.read_csv('02_Data_Intermediate/district_quarter_skeleton.csv')

# Date to quarter
def date_to_quarter(year, month):
    if pd.isna(month):
        return None  # Handle missing month
    return f"{int(year)}Q{((int(month)-1)//3)+1}"

emdat['quarter'] = emdat.apply(lambda r: date_to_quarter(r['Start Year'], r['Start Month']), axis=1)

# Load state-to-districts lookup
gadm = gpd.read_file('01_Data_Raw/District_Boundaries/gadm41_IND_2.shp')
state_districts = gadm[['NAME_1', 'NAME_2']].drop_duplicates()
state_districts.columns = ['state', 'district_gadm']

# Add state name aliases to handle historical names and variations
state_aliases = {
    'delhi': 'NCT of Delhi',
    'orissa': 'Odisha',
    'pondicherry': 'Puducherry'
}

# Strip common suffixes
def normalize_state_token(token):
    t = token.lower().strip()
    # Remove "state"/"states" suffix
    t = t.replace(' state', '').replace(' states', '').strip()
    # Check alias
    if t in state_aliases:
        return state_aliases[t]
    return t


# Initialize exposure columns
skeleton['flood_exposure_ruleA_qt'] = 0
skeleton['flood_exposure_ruleB_qt'] = 0

# Loop over events
for idx, event in emdat.iterrows():
    qtr = event['quarter']
    if pd.isna(qtr):
        print(f"WARNING: Event {event['DisNo.']} has no quarter (missing month), skipping")
        continue
    
    districts_str = event['districts_final_str']
    if pd.isna(districts_str):
        continue
    
    tokens = [d.strip() for d in str(districts_str).split(';')]
    
    for token in tokens:
        # Try exact match in emdat_district_matches
        match_row = emdat_matches[emdat_matches['district_emdat'].str.lower() == token.lower()]
        
        if not match_row.empty and match_row.iloc[0]['matched_emdat_gadm']:
            # District-level match (Rule B eligible)
            gadm_dist = match_row.iloc[0]['district_gadm_match']
            skeleton.loc[(skeleton['quarter'] == qtr) & 
                        (skeleton['district_gadm'] == gadm_dist), 
                        ['flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt']] = 1
        else:
            # Check if token is a state name (Rule A only)
            normalized_token = normalize_state_token(token)
            state_match = state_districts[state_districts['state'].str.lower() == normalized_token.lower()]
            if not state_match.empty:
                affected_dists = state_match['district_gadm'].unique()
                skeleton.loc[(skeleton['quarter'] == qtr) & 
                            (skeleton['district_gadm'].isin(affected_dists)), 
                            'flood_exposure_ruleA_qt'] = 1
                # Rule B: do nothing (state-level not eligible)
            else:
                print(f"WARNING: Unmatched token '{token}' in event {event['DisNo.']}")

# Output
skeleton.to_csv('02_Data_Intermediate/flood_exposure_panel.csv', index=False)