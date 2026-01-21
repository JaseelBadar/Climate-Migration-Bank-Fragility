import pandas as pd

print("=" * 70)
print("FINDING THE 10 MISSING DISTRICTS")
print("=" * 70)

# Try to find the crosswalk file
import os
crosswalk_options = [
    '02_Data_Intermediate/district_crosswalk.csv',
    '02_Data_Intermediate/district_crosswalk_draft.csv',
    '03_Output/district_crosswalk_draft.csv'
]

crosswalk_path = None
for path in crosswalk_options:
    if os.path.exists(path):
        crosswalk_path = path
        print(f"✅ Found crosswalk at: {path}\n")
        break

if crosswalk_path is None:
    print("❌ Cannot find crosswalk file! Checking what files exist...")
    print("\nFiles in 02_Data_Intermediate:")
    if os.path.exists('02_Data_Intermediate'):
        print([f for f in os.listdir('02_Data_Intermediate') if 'crosswalk' in f.lower()])
    print("\nFiles in 03_Output:")
    if os.path.exists('03_Output'):
        print([f for f in os.listdir('03_Output') if 'crosswalk' in f.lower()])
    exit()

# Load crosswalk to get the full list of GADM districts
crosswalk = pd.read_csv(crosswalk_path)
print(f"Crosswalk columns: {list(crosswalk.columns)}\n")

gadm_districts = crosswalk[['gadm_district', 'gadm_state']].drop_duplicates()
print(f"GADM districts in crosswalk: {len(gadm_districts)}")

# Load the fixed VIIRS panel
viirs = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel_fixed.csv')
viirs_districts = viirs[['gadm_district', 'gadm_state']].drop_duplicates()

print(f"Districts in VIIRS fixed panel: {len(viirs_districts)}")

# Find missing districts
missing = gadm_districts.merge(
    viirs_districts, 
    on=['gadm_district', 'gadm_state'], 
    how='left', 
    indicator=True
)
missing = missing[missing['_merge'] == 'left_only'][['gadm_district', 'gadm_state']]

print(f"\n❌ Missing districts: {len(missing)}")
if len(missing) > 0:
    print("\nList of missing districts:")
    print(missing.to_string(index=False))
else:
    print("\n✅ All districts accounted for!")

print("\n" + "=" * 70)