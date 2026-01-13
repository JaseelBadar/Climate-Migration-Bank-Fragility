"""
18_extract_viirs_district_means.py - Phase 3d VIIRS Integration
Extract mean nighttime radiance per GADM district from VIIRS monthly tiles
Test version: Jan 2023 tile only (will scale to 120 tiles after validation)
Success: 666 districts with non-zero urban radiance values
"""
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
import numpy as np
import logging
import os
from pathlib import Path

# Setup logging
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/18_viirs_extraction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: VIIRS District-Level Extraction (Test)")
print("="*70)
log.info("Starting 18_extract_viirs_district_means.py")

# === INPUT PATHS ===
gadm_path = '01_Data_Raw/District_Boundaries/gadm41_IND_2.shp'
viirs_test = '01_Data_Raw/VIIRS_NightLights/SVDNB_npp_20230101-20230131_75N060E_vcmcfg_v10_c202302080600.avg_rade9h.tif'

# Load GADM districts
print(f"\n[1/4] Loading GADM districts...")
districts_gdf = gpd.read_file(gadm_path)
print(f"   Loaded: {len(districts_gdf)} districts")
log.info(f"GADM districts loaded: {len(districts_gdf)}")

# Verify CRS match
print(f"   GADM CRS: {districts_gdf.crs}")

# === EXTRACT MEAN RADIANCE PER DISTRICT ===
print(f"\n[2/4] Opening VIIRS tile: Jan 2023...")
with rasterio.open(viirs_test) as src:
    print(f"   Raster CRS: {src.crs}")
    print(f"   Raster bounds: {src.bounds}")
    print(f"   Raster shape: {src.height} x {src.width}")
    print(f"   Nodata value: {src.nodata}")
    
    # Reproject districts to match raster CRS if needed
    if districts_gdf.crs != src.crs:
        print(f"   Reprojecting districts to {src.crs}...")
        districts_gdf = districts_gdf.to_crs(src.crs)
        log.info(f"Districts reprojected to {src.crs}")
    
    print(f"\n[3/4] Extracting mean radiance for {len(districts_gdf)} districts...")
    print("   (This may take 2-3 minutes...)")
    
    results = []
    for idx, row in districts_gdf.iterrows():
        district_name = row['NAME_2']
        state_name = row['NAME_1']
        
        # Progress indicator every 50 districts
        if (idx + 1) % 50 == 0:
            print(f"   Processed {idx + 1}/{len(districts_gdf)} districts...")
        
        try:
            # Extract pixels within district polygon
            geom = [row['geometry']]
            out_image, out_transform = mask(src, geom, crop=True, nodata=src.nodata)
            
            # Calculate mean (exclude nodata values)
            data = out_image[0]  # First band
            
            # Filter valid data (exclude nodata and negatives)
            if src.nodata is not None:
                valid_data = data[(data != src.nodata) & (data >= 0)]
            else:
                valid_data = data[data >= 0]
            
            if len(valid_data) > 0:
                mean_radiance = float(np.mean(valid_data))
                pixel_count = len(valid_data)
            else:
                mean_radiance = 0.0
                pixel_count = 0
            
            results.append({
                'gadm_district': district_name,
                'gadm_state': state_name,
                'year': 2023,
                'month': 1,
                'mean_radiance': mean_radiance,
                'pixel_count': pixel_count
            })
            
        except Exception as e:
            log.warning(f"Failed to extract {district_name}, {state_name}: {e}")
            results.append({
                'gadm_district': district_name,
                'gadm_state': state_name,
                'year': 2023,
                'month': 1,
                'mean_radiance': np.nan,
                'pixel_count': 0
            })

# === SAVE OUTPUT ===
print(f"\n[4/4] Saving results...")
df = pd.DataFrame(results)

# Summary statistics
print(f"\n{'='*70}")
print("EXTRACTION SUMMARY (Jan 2023)")
print(f"{'='*70}")
print(f"Total districts processed: {len(df)}")
print(f"Districts with data (radiance > 0): {(df['mean_radiance'] > 0).sum()}")
print(f"Districts with zero radiance: {(df['mean_radiance'] == 0).sum()}")
print(f"Failed extractions (NaN): {df['mean_radiance'].isna().sum()}")
print(f"\nRadiance statistics (valid districts only):")
valid_df = df[df['mean_radiance'] > 0]
print(f"  Mean: {valid_df['mean_radiance'].mean():.4f}")
print(f"  Median: {valid_df['mean_radiance'].median():.4f}")
print(f"  Min: {valid_df['mean_radiance'].min():.4f}")
print(f"  Max: {valid_df['mean_radiance'].max():.4f}")

print(f"\nTop 10 brightest districts (Jan 2023):")
top10 = df.nlargest(10, 'mean_radiance')[['gadm_district', 'gadm_state', 'mean_radiance']]
print(top10.to_string(index=False))

# Save to intermediate
os.makedirs('02_Data_Intermediate', exist_ok=True)
output_path = '02_Data_Intermediate/viirs_jan2023_test.csv'
df.to_csv(output_path, index=False)
print(f"\nOutput saved: {output_path}")
log.info(f"Extraction complete. {len(df)} districts, {(df['mean_radiance'] > 0).sum()} with data")

print(f"\n{'='*70}")
print("NEXT STEP: Validate output")
print("Run: python 04_Code/19_validate_viirs_extraction.py")
print(f"{'='*70}")