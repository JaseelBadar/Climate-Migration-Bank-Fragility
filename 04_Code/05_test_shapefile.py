import geopandas as gpd

# Load district shapefile
districts = gpd.read_file('01_Data_Raw/District_Boundaries/gadm41_IND_2.shp')

print(f"Total districts loaded: {len(districts)}")
print(f"\nColumn names:")
print(list(districts.columns))
print(f"\nFirst 5 districts:")
print(districts[['NAME_1', 'NAME_2']].head())