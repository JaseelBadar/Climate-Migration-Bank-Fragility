import pandas as pd

# Load the monthly panel
monthly = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel.csv')

# Identify districts that might span multiple tiles
# (Himalayan border districts)
himalayan_states = ['Arunachal Pradesh', 'Sikkim', 'Uttarakhand']
border_districts = monthly[monthly['gadm_state'].isin(himalayan_states)]

# Check pixel_count variation
# If pixel counts vary a LOT within same district, 
# it suggests data from different tiles with different coverage
pixel_variance = border_districts.groupby(['gadm_district', 'gadm_state'])['pixel_count'].agg(['mean', 'std', 'min', 'max'])
pixel_variance['cv'] = pixel_variance['std'] / pixel_variance['mean']  # Coefficient of variation

print("Districts with high pixel count variation (potential multi-tile):")
print(pixel_variance[pixel_variance['cv'] > 0.1].sort_values('cv', ascending=False))

# For Anjaw specifically (mentioned in Script 21b)
anjaw = monthly[(monthly['gadm_district'] == 'Anjaw') & 
                (monthly['gadm_state'] == 'Arunachal Pradesh')]
print(f"\nAnjaw pixel_count range: {anjaw['pixel_count'].min()} to {anjaw['pixel_count'].max()}")
print(f"Anjaw pixel_count unique values: {anjaw['pixel_count'].nunique()}")