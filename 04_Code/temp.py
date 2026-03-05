import pandas as pd

# Load current emdat_district_matches
current = pd.read_csv('02_Data_Intermediate/emdat_district_matches.csv')

# How many matched in current run?
print(f"Current matches: {current['matched_emdat_gadm'].sum()} / {len(current)}")

# Which districts are matched now?
matched = current[current['matched_emdat_gadm'] == True][
    ['district_emdat', 'district_gadm_match', 'match_score_emdat_gadm']
].sort_values('district_emdat')
print(matched.to_string())