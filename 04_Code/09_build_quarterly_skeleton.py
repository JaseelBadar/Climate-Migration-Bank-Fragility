import pandas as pd
import geopandas as gpd


# Load GADM
gadm = gpd.read_file('01_Data_Raw/District_Boundaries/gadm41_IND_2.shp')
gadm_districts = gadm[['NAME_2', 'NAME_1']].drop_duplicates().copy()
gadm_districts.columns = ['district_gadm', 'state_gadm']
print(f"GADM unique district-state pairs: {len(gadm_districts)}")


# Create 40 quarters: 2015Q1 through 2024Q4
quarters = pd.DataFrame({
    'year': [y for y in range(2015, 2025) for q in range(1, 5)],
    'q':    [q for y in range(2015, 2025) for q in range(1, 5)]
})
quarters['quarter']     = quarters['year'].astype(str) + 'Q' + quarters['q'].astype(str)
quarters['quarter_num'] = range(1, len(quarters) + 1)
print(f"Quarters generated: {len(quarters)} ({quarters['quarter'].min()} to {quarters['quarter'].max()})")


# Cross product: every district x every quarter
skeleton = gadm_districts.merge(quarters, how='cross')
expected_rows = len(gadm_districts) * len(quarters)
print(f"Skeleton: {len(skeleton)} district-quarters "
      f"({len(gadm_districts)} districts x {len(quarters)} quarters = {expected_rows} expected)")

assert len(skeleton) == expected_rows, (
    f"Row count mismatch: got {len(skeleton)}, expected {expected_rows}"
)


# Save
output_path = '02_Data_Intermediate/district_quarter_skeleton.csv'
skeleton.to_csv(output_path, index=False)
print(f"Saved: {output_path}")