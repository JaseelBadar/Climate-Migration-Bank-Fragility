import pandas as pd
import numpy as np

print("=" * 70)
print("FIXING DUPLICATE DISTRICTS FROM MULTI-TILE OVERLAP")
print("=" * 70)

# Load the raw monthly panel with duplicates
df = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel.csv')

print(f"\nBefore deduplication:")
print(f"  Total rows: {len(df):,}")
print(f"  Unique district-month combinations: {df.groupby(['gadm_district', 'gadm_state', 'year', 'month']).ngroups:,}")

# Calculate weighted mean radiance for districts spanning multiple tiles
# Formula: weighted_mean = sum(mean_radiance * pixel_count) / sum(pixel_count)

df_agg = df.groupby(['gadm_district', 'gadm_state', 'year', 'month']).apply(
    lambda x: pd.Series({
        'mean_radiance': np.average(x['mean_radiance'], weights=x['pixel_count']),
        'pixel_count': x['pixel_count'].sum()
    })
).reset_index()

print(f"\nAfter aggregation:")
print(f"  Total rows: {len(df_agg):,}")
print(f"  Unique district-month combinations: {df_agg.groupby(['gadm_district', 'gadm_state', 'year', 'month']).ngroups:,}")

# Verify no duplicates remain
duplicates = df_agg.groupby(['gadm_district', 'gadm_state', 'year', 'month']).size()
duplicates = duplicates[duplicates > 1]

if len(duplicates) == 0:
    print("\n✅ SUCCESS! All duplicates resolved.")
else:
    print(f"\n❌ PROBLEM! Still {len(duplicates)} duplicates remaining!")

# Show example: Anjaw before and after
print("\n" + "=" * 70)
print("EXAMPLE: Anjaw, Arunachal Pradesh, Jan 2015")
print("=" * 70)

anjaw_before = df[(df['gadm_district'] == 'Anjaw') & 
                  (df['gadm_state'] == 'Arunachal Pradesh') & 
                  (df['year'] == 2015) & 
                  (df['month'] == 1)]

anjaw_after = df_agg[(df_agg['gadm_district'] == 'Anjaw') & 
                     (df_agg['gadm_state'] == 'Arunachal Pradesh') & 
                     (df_agg['year'] == 2015) & 
                     (df_agg['month'] == 1)]

print("\nBEFORE (2 rows from 2 tiles):")
print(anjaw_before.to_string(index=False))

print("\nAFTER (1 aggregated row):")
print(anjaw_after.to_string(index=False))

# Calculate the weighted mean manually to verify
total_radiance = (anjaw_before['mean_radiance'] * anjaw_before['pixel_count']).sum()
total_pixels = anjaw_before['pixel_count'].sum()
weighted_mean = total_radiance / total_pixels

print(f"\nManual verification:")
print(f"  Weighted mean radiance: {weighted_mean:.6f}")
print(f"  Total pixels: {total_pixels:,}")

# Save the fixed version
output_path = '02_Data_Intermediate/viirs_monthly_panel_fixed.csv'
df_agg.to_csv(output_path, index=False)
print(f"\n✅ Fixed data saved to: {output_path}")

print("\n" + "=" * 70)
print("NEXT STEP: Replace viirs_monthly_panel.csv with the fixed version")
print("=" * 70)