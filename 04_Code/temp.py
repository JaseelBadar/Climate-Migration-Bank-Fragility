import pandas as pd

monthly = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel.csv')
print(f"Rows: {len(monthly)}")
print(f"Districts (unique names): {monthly['gadm_district'].nunique()}")
print(f"District-state combos: {monthly.groupby(['gadm_district', 'gadm_state']).ngroups}")

obs_per_district = monthly.groupby(['gadm_district', 'gadm_state']).size()
print(f"\nObs per district-state combo:")
print(f"  Min: {obs_per_district.min()}")
print(f"  Max: {obs_per_district.max()}")