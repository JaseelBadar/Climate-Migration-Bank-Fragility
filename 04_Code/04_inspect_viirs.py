import rasterio
import numpy as np
import os

print("="*70)
print("VIIRS NIGHTTIME LIGHTS DATA INSPECTION - PHASE 3c")
print("="*70)

# File path
viirs_folder = "01_Data_Raw/VIIRS_NightLights"
filename = "SVDNB_npp_20230101-20230131_75N060E_vcmcfg_v10_c202302080600.avg_rade9h.tif"
file_path = os.path.join(viirs_folder, filename)

print(f"\n[0] LOCATING VIIRS FILE")
print(f"    Path: {file_path}")

if not os.path.exists(file_path):
    print(f"    ERROR: File not found")
    print(f"    Current working directory: {os.getcwd()}")
    exit()

# Get file size
file_size_gb = os.path.getsize(file_path) / (1024**3)
print(f"    ✓ File found")
print(f"    File size: {file_size_gb:.2f} GB")

# Open with rasterio
print(f"\n[1] OPENING FILE WITH RASTERIO")
try:
    with rasterio.open(file_path) as src:
        print(f"    ✓ File opened successfully")
        
        # Metadata
        print(f"\n[2] FILE METADATA")
        print(f"    Dimensions: {src.width} columns × {src.height} rows")
        print(f"    Number of bands: {src.count}")
        print(f"    Data type: {src.dtypes[0]}")
        print(f"    CRS: {src.crs}")
        print(f"    NoData value: {src.nodata}")
        
        # Resolution
        print(f"\n[3] PIXEL RESOLUTION")
        print(f"    X resolution: {src.res[0]} degrees")
        print(f"    Y resolution: {src.res[1]} degrees")
        print(f"    Pixel size: ~{abs(src.res[0] * 111):.2f} km (at equator)")
        
        # Bounding box
        bounds = src.bounds
        print(f"\n[4] GEOGRAPHIC EXTENT (Bounding Box)")
        print(f"    West:  {bounds.left:.2f}°E")
        print(f"    East:  {bounds.right:.2f}°E")
        print(f"    North: {bounds.top:.2f}°N")
        print(f"    South: {bounds.bottom:.2f}°N")
        
        # Check if India is covered (8°N-37°N, 68°E-97°E)
        india_covered = (bounds.left <= 68 and bounds.right >= 97 and 
                        bounds.bottom <= 8 and bounds.top >= 37)
        
        if india_covered:
            print(f"    ✓ INDIA IS COVERED (8-37°N, 68-97°E)")
        else:
            print(f"    ⚠ WARNING: India may not be fully covered")
        
        # Read a small subset (center 100x100 pixels)
        print(f"\n[5] READING SAMPLE DATA (100×100 pixel subset)")
        center_x = src.width // 2
        center_y = src.height // 2
        
        window = rasterio.windows.Window(
            col_off=center_x - 50,
            row_off=center_y - 50,
            width=100,
            height=100
        )
        
        sample_data = src.read(1, window=window)
        
        print(f"    Sample array shape: {sample_data.shape}")
        print(f"    Data type: {sample_data.dtype}")
        
        # Statistics
        print(f"\n[6] RADIANCE VALUES (Sample Subset)")
        
        # Filter out NoData values
        valid_data = sample_data[sample_data != src.nodata] if src.nodata else sample_data
        valid_data = valid_data[~np.isnan(valid_data)]
        
        if len(valid_data) > 0:
            print(f"    Valid pixels: {len(valid_data)} / {sample_data.size}")
            print(f"    Min radiance: {valid_data.min():.4f} nW/cm²/sr")
            print(f"    Max radiance: {valid_data.max():.4f} nW/cm²/sr")
            print(f"    Mean radiance: {valid_data.mean():.4f} nW/cm²/sr")
            print(f"    Median radiance: {np.median(valid_data):.4f} nW/cm²/sr")
            print(f"    Std deviation: {valid_data.std():.4f} nW/cm²/sr")
            
            # Check for reasonable range
            if valid_data.max() < 0:
                print(f"    ⚠ WARNING: Negative radiance values detected")
            elif valid_data.max() > 10000:
                print(f"    ⚠ WARNING: Unusually high radiance values")
            else:
                print(f"    ✓ Radiance values in expected range")
        else:
            print(f"    ⚠ WARNING: No valid data in sample")
        
        # Sample individual pixels
        print(f"\n[7] INDIVIDUAL PIXEL SAMPLES (First 10)")
        flat_valid = valid_data.flatten()[:10]
        for i, val in enumerate(flat_valid, 1):
            print(f"    Pixel {i}: {val:.4f} nW/cm²/sr")
        
        # Full array statistics (metadata only, don't load)
        print(f"\n[8] FULL TILE INFORMATION")
        print(f"    Total pixels: {src.width * src.height:,}")
        print(f"    Total data points: {src.width * src.height * src.count:,}")
        print(f"    Estimated memory if fully loaded: {(src.width * src.height * 4) / (1024**3):.2f} GB")
        
except Exception as e:
    print(f"    ERROR: Could not open file")
    print(f"    Error message: {e}")
    exit()

# Summary
print(f"\n{'='*70}")
print("VIIRS DATA VALIDATION - SUMMARY")
print(f"{'='*70}")
print(f"✓ File readable: YES")
print(f"✓ Format: GeoTIFF (single-band radiance)")
print(f"✓ Dimensions: {src.width} × {src.height} pixels")
print(f"✓ India coverage: {'YES' if india_covered else 'PARTIAL'}")
print(f"✓ Data validity: {'CONFIRMED' if len(valid_data) > 0 else 'QUESTIONABLE'}")
print(f"✓ Radiance range: {valid_data.min():.2f} to {valid_data.max():.2f} nW/cm²/sr")

print(f"\n⚠️ NEXT STEPS:")
print(f"   1. If data is valid → Proceed to Phase 3d (download remaining 119 tiles)")
print(f"   2. Test spatial subsetting (extract India bounding box)")
print(f"   3. Build district-level aggregation pipeline")
print(f"   4. Calculate monthly mean radiance per district")

print(f"\n⚠️ PHASE 3d DOWNLOAD SCOPE:")
print(f"   - Tile: 75N060E (same as this test file)")
print(f"   - Time period: Jan 2015 - Dec 2024 (120 months)")
print(f"   - Total size: ~240 GB (120 files × 2GB each)")
print(f"   - Download source: Colorado School of Mines (eogdata.mines.edu)")
print(f"{'='*70}")