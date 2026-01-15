"""
21_extract_viirs_full_panel.py - Phase 3d VIIRS Integration

Extract mean nighttime radiance for all 676 GADM districts across 120 months (2015-2024).

INPUT:
  - 120 VIIRS tiles (.avg_rade9h.tif files) from F:\Jaseel\VIIRS_Raw_Data_75N060E\
  - GADM districts (01_Data_Raw/District_Boundaries/gadm41_IND_2.shp)

OUTPUT:
  - 02_Data_Intermediate/viirs_monthly_panel.csv (81,120 rows expected)

ESTIMATED RUNTIME: 6-8 hours (overnight execution)
"""

import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
import numpy as np
import logging
import os
from pathlib import Path
from glob import glob
import time

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/21_viirs_full_extraction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: VIIRS FULL EXTRACTION (2015-2024)")
print("="*70)
log.info("Starting 21_extract_viirs_full_panel.py")

# === PATHS ===
gadm_path = '01_Data_Raw/District_Boundaries/gadm41_IND_2.shp'
viirs_base = Path('F:/Jaseel/VIIRS_Raw_Data_75N060E')

# === LOAD GADM DISTRICTS (once) ===
print(f"\n[Step 1/3] Loading GADM districts...")
districts_gdf = gpd.read_file(gadm_path)
print(f"  ✓ Loaded: {len(districts_gdf)} districts")
print(f"  ✓ CRS: {districts_gdf.crs}")
log.info(f"GADM districts loaded: {len(districts_gdf)}")

# === BUILD LIST OF ALL 120 VIIRS FILES ===
print(f"\n[Step 2/3] Scanning for VIIRS tiles...")
years = range(2015, 2025)  # 2015-2024
months = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']

tile_files = []
for year in years:
    for month_idx, month_name in enumerate(months, start=1):
        month_folder = viirs_base / str(year) / month_name
        
        # Find the .avg_rade9h.tif file in this folder
        tif_files = list(month_folder.glob('*.avg_rade9h.tif'))
        
        if tif_files:
            tile_files.append({
                'year': year,
                'month': month_idx,
                'month_name': month_name,
                'path': tif_files[0]  # Take the first .tif file found
            })

print(f"  ✓ Found: {len(tile_files)} VIIRS tiles")
log.info(f"VIIRS tiles found: {len(tile_files)}/120")

if len(tile_files) < 120:
    print(f"  ⚠ Warning: Expected 120, found {len(tile_files)}")
    log.warning(f"Only {len(tile_files)}/120 tiles found; proceeding with available tiles")

# === EXTRACT DISTRICT MEANS FOR ALL 120 MONTHS ===
print(f"\n[Step 3/3] Extracting district means (120 months × 676 districts)...")
print(f"  This will take 6-8 hours. Progress updates every month.\n")

all_results = []
start_time = time.time()

for tile_idx, tile_info in enumerate(tile_files, start=1):
    year = tile_info['year']
    month = tile_info['month']
    tile_path = tile_info['path']
    
    print(f"[{tile_idx}/120] Processing {year}-{month:02d} ({tile_info['month_name']})...")
    log.info(f"Processing {year}-{month:02d}")
    
    try:
        with rasterio.open(tile_path) as src:
            # Reproject districts to match raster CRS if needed
            if districts_gdf.crs != src.crs:
                districts_reproj = districts_gdf.to_crs(src.crs)
            else:
                districts_reproj = districts_gdf
            
            # Extract for each district
            for idx, row in districts_reproj.iterrows():
                district_name = row['NAME_2']
                state_name = row['NAME_1']
                
                try:
                    geom = [row.geometry]
                    out_image, out_transform = mask(src, geom, crop=True, nodata=src.nodata)
                    data = out_image[0]  # First band
                    
                    # Calculate mean (exclude nodata and negatives)
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
                    
                    all_results.append({
                        'gadm_district': district_name,
                        'gadm_state': state_name,
                        'year': year,
                        'month': month,
                        'mean_radiance': mean_radiance,
                        'pixel_count': pixel_count
                    })
                
                except Exception as e:
                    log.warning(f"Failed district {district_name}, {state_name} in {year}-{month}: {e}")
                    all_results.append({
                        'gadm_district': district_name,
                        'gadm_state': state_name,
                        'year': year,
                        'month': month,
                        'mean_radiance': np.nan,
                        'pixel_count': 0
                    })
            
            # Progress indicator
            elapsed = time.time() - start_time
            avg_time_per_month = elapsed / tile_idx
            remaining = (120 - tile_idx) * avg_time_per_month
            print(f"  ✓ Complete ({elapsed/60:.1f} min elapsed, ~{remaining/60:.1f} min remaining)")
    
    except Exception as e:
        print(f"  ✗ Failed to open tile: {e}")
        log.error(f"Failed to open {tile_path}: {e}")

# === SAVE OUTPUT ===
print(f"\n[4/4] Saving results...")
df = pd.DataFrame(all_results)

os.makedirs('02_Data_Intermediate', exist_ok=True)
output_path = '02_Data_Intermediate/viirs_monthly_panel.csv'
df.to_csv(output_path, index=False)

# === SUMMARY ===
print("="*70)
print("EXTRACTION COMPLETE")
print("="*70)
print(f"Total rows: {len(df):,}")
print(f"Expected: {120 * len(districts_gdf):,}")
print(f"Districts: {df['gadm_district'].nunique()}")
print(f"Months: {df[['year', 'month']].drop_duplicates().shape[0]}")
print(f"Date range: {df['year'].min()}-{df['month'].min():02d} to {df['year'].max()}-{df['month'].max():02d}")
print(f"\nOutput saved: {output_path}")
print(f"Total runtime: {(time.time() - start_time)/3600:.2f} hours")
log.info(f"Extraction complete: {len(df)} rows saved to {output_path}")
print("="*70)
print("\nNEXT STEP: Run Script 22 (aggregate to quarterly)")
print("="*70)