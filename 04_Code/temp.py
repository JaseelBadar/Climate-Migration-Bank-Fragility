import pandas as pd

# Check the actual master panel file
master = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')
print(f"Master panel actual rows: {len(master)}")
print(f"Master panel districts: {master['district_gadm'].nunique()}")
print(f"Master panel quarters: {master.groupby(['year', 'q']).ngroups}")

# Check the output
final = pd.read_csv('03_Data_Clean/analysis_panel_final.csv')
print(f"\nFinal panel rows: {len(final)}")
print(f"Final panel districts: {final['district_gadm'].nunique()}")

# Check for duplicates
duplicates = final.groupby(['district_gadm', 'state_gadm', 'year', 'q']).size()
duplicates = duplicates[duplicates > 1]
print(f"\nDuplicate district-quarter combos: {len(duplicates)}")
if len(duplicates) > 0:
    print("\nFirst 5 duplicates:")
    print(duplicates.head())