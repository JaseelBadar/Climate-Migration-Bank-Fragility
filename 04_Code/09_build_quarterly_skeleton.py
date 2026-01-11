import pandas as pd
import geopandas as gpd

# Load GADM
gadm = gpd.read_file('01_Data_Raw/District_Boundaries/gadm41_IND_2.shp')
gadm_districts = gadm[['NAME_2', 'NAME_1']].drop_duplicates()
gadm_districts.columns = ['district_gadm', 'state_gadm']

# Create 40 quarters
quarters = pd.DataFrame({
    'year': [y for y in range(2015, 2025) for q in range(1, 5)],
    'q': [q for y in range(2015, 2025) for q in range(1, 5)]
})
quarters = quarters[(quarters['year'] < 2024) | (quarters['q'] <= 4)]  # exactly 40
quarters['quarter'] = quarters['year'].astype(str) + 'Q' + quarters['q'].astype(str)
quarters['quarter_num'] = range(1, len(quarters)+1)

# Cross product
skeleton = gadm_districts.merge(quarters, how='cross')
print(f"Skeleton: {len(skeleton)} district-quarters")

# Output
skeleton.to_csv('02_Data_Intermediate/district_quarter_skeleton.csv', index=False)