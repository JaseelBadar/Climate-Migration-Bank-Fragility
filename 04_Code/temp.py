import pandas as pd

crosswalk = pd.read_csv('02_Data_Intermediate/district_crosswalk_draft.csv')

homonyms = ['AURANGABAD', 'BALRAMPUR', 'BIJAPUR', 'BILASPUR', 'HAMIRPUR', 'PRATAPGARH', 'RAIGARH']

print("=== CROSSWALK ROWS FOR HOMONYMOUS DISTRICTS ===")
print(f"Crosswalk columns: {list(crosswalk.columns)}\n")

for d in homonyms:
    subset = crosswalk[crosswalk['district_rbi'].str.upper().str.strip() == d]
    print(f"{d}: {len(subset)} row(s)")
    print(subset[['district_rbi', 'district_gadm', 'state_gadm', 'matched_rbi_gadm']].to_string())
    print()