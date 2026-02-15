import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime


# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
log_path = '05_Outputs/Logs/26_viirs_quarterly_validation.txt'


# Clear previous log
with open(log_path, 'w') as f:
    f.write("")


logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(message)s'
)
log = logging.getLogger(__name__)


print("="*70)
print("PHASE 3d: VIIRS QUARTERLY PANEL VALIDATION")
print("="*70)
log.info("="*70)
log.info("VIIRS QUARTERLY PANEL VALIDATION REPORT")
log.info(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log.info("="*70)


# === LOAD DATA ===
print(f"\n[Loading] viirs_quarterly_panel_clean.csv...")
try:
    df = pd.read_csv('02_Data_Intermediate/viirs_quarterly_panel_clean.csv')
    print(f"  Loaded: {len(df):,} rows")
    log.info(f"\nFile loaded successfully: {len(df):,} rows")
except FileNotFoundError:
    print(f"  ERROR: File not found. Script 22b may not have completed.")
    log.error("ERROR: viirs_quarterly_panel_clean.csv not found")
    exit(1)


# === VALIDATION FLAGS ===
validation_passed = True


# === CHECK 1: EXPECTED DIMENSIONS ===
print(f"\n[Check 1/9] Expected dimensions...")
log.info("\n" + "="*70)
log.info("CHECK 1: EXPECTED DIMENSIONS")
log.info("="*70)


expected_rows = 624 * 40  # 24,960
actual_rows = len(df)


print(f"  Expected: {expected_rows:,} rows (624 districts x 40 quarters)")
print(f"  Actual:   {actual_rows:,} rows")
log.info(f"Expected: {expected_rows:,} rows (624 districts x 40 quarters)")
log.info(f"Actual:   {actual_rows:,} rows")


if actual_rows == expected_rows:
    print(f"  PASS: Dimensions match")
    log.info("RESULT: PASS")
else:
    print(f"  WARNING: Difference of {abs(expected_rows - actual_rows):,} rows")
    log.warning(f"RESULT: FAIL - Difference of {abs(expected_rows - actual_rows):,} rows")
    validation_passed = False


# === CHECK 2: REQUIRED COLUMNS ===
print(f"\n[Check 2/9] Required columns...")
log.info("\n" + "="*70)
log.info("CHECK 2: REQUIRED COLUMNS")
log.info("="*70)


required_cols = ['district_gadm', 'state_gadm', 'year', 'quarter', 'mean_radiance', 'pixel_count']
missing_cols = [col for col in required_cols if col not in df.columns]


if not missing_cols:
    print(f"  PASS: All required columns present")
    log.info("RESULT: PASS - All required columns present")
else:
    print(f"  FAIL: Missing columns: {missing_cols}")
    log.error(f"RESULT: FAIL - Missing columns: {missing_cols}")
    validation_passed = False


# === CHECK 3: COMPOSITE DISTRICT COVERAGE ===
print(f"\n[Check 3/9] Composite district coverage...")
log.info("\n" + "="*70)
log.info("CHECK 3: COMPOSITE DISTRICT COVERAGE")
log.info("="*70)


# Create composite ID
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']


unique_districts_name = df['district_gadm'].nunique()
unique_districts_composite = df['district_state_id'].nunique()
expected_districts = 624


print(f"  Expected: {expected_districts} districts (composite count)")
print(f"  Actual (name only): {unique_districts_name} (should be 617 if homonyms exist)")
print(f"  Actual (composite): {unique_districts_composite}")
log.info(f"Expected: {expected_districts} districts")
log.info(f"Actual (name only): {unique_districts_name}")
log.info(f"Actual (composite): {unique_districts_composite}")


if unique_districts_composite == expected_districts:
    print(f"  PASS: All {expected_districts} districts present (composite ID)")
    log.info("RESULT: PASS")
    
    # Check homonymous districts
    if unique_districts_name < unique_districts_composite:
        homonym_count = unique_districts_composite - unique_districts_name
        print(f"  INFO: {homonym_count} homonymous district pairs detected (expected: 7)")
        log.info(f"Homonymous pairs detected: {homonym_count}")
else:
    print(f"  FAIL: Expected {expected_districts}, got {unique_districts_composite}")
    log.warning(f"RESULT: FAIL - District count mismatch")
    validation_passed = False


# === CHECK 4: TEMPORAL COVERAGE ===
print(f"\n[Check 4/9] Temporal coverage...")
log.info("\n" + "="*70)
log.info("CHECK 4: TEMPORAL COVERAGE")
log.info("="*70)


unique_quarters = df['quarter'].nunique()
expected_quarters = 40  # 2015Q1-2024Q4


print(f"  Expected: {expected_quarters} unique quarters (2015Q1-2024Q4)")
print(f"  Actual:   {unique_quarters} quarters")
print(f"  Year range: {df['year'].min()} - {df['year'].max()}")
log.info(f"Expected: {expected_quarters} unique quarters")
log.info(f"Actual:   {unique_quarters} quarters")
log.info(f"Year range: {df['year'].min()} - {df['year'].max()}")


# Check for temporal gaps
expected_quarters_list = [f"{y}Q{q}" for y in range(2015, 2025) for q in range(1, 5)]
actual_quarters_list = sorted(df['quarter'].unique())
missing_quarters = [q for q in expected_quarters_list if q not in actual_quarters_list]


if not missing_quarters:
    print(f"  PASS: All quarters present (2015Q1 to 2024Q4)")
    log.info("RESULT: PASS - No temporal gaps")
else:
    print(f"  WARNING: Missing {len(missing_quarters)} quarters: {missing_quarters[:5]}")
    log.warning(f"RESULT: FAIL - Missing quarters: {missing_quarters}")
    validation_passed = False


# === CHECK 5: DATA QUALITY (NaN) ===
print(f"\n[Check 5/9] Missing values (NaN)...")
log.info("\n" + "="*70)
log.info("CHECK 5: MISSING VALUES (NaN)")
log.info("="*70)


nan_counts = df[['mean_radiance', 'pixel_count']].isna().sum()
print(f"  mean_radiance NaN: {nan_counts['mean_radiance']:,} ({nan_counts['mean_radiance']/len(df)*100:.2f}%)")
print(f"  pixel_count NaN:   {nan_counts['pixel_count']:,} ({nan_counts['pixel_count']/len(df)*100:.2f}%)")
log.info(f"mean_radiance NaN: {nan_counts['mean_radiance']:,} ({nan_counts['mean_radiance']/len(df)*100:.2f}%)")
log.info(f"pixel_count NaN:   {nan_counts['pixel_count']:,} ({nan_counts['pixel_count']/len(df)*100:.2f}%)")


if nan_counts['mean_radiance'] == 0:
    print(f"  PASS: No missing radiance values")
    log.info("RESULT: PASS - No missing values")
else:
    print(f"  WARNING: {nan_counts['mean_radiance']} NaN values in mean_radiance")
    log.warning(f"RESULT: FAIL - {nan_counts['mean_radiance']} NaN values detected")
    validation_passed = False


# === CHECK 6: DATA QUALITY (Inf) ===
print(f"\n[Check 6/9] Infinite values (Inf)...")
log.info("\n" + "="*70)
log.info("CHECK 6: INFINITE VALUES (Inf)")
log.info("="*70)


inf_count = np.isinf(df['mean_radiance']).sum()
print(f"  Inf values: {inf_count}")
log.info(f"Inf values: {inf_count}")


if inf_count == 0:
    print(f"  PASS: No infinite values")
    log.info("RESULT: PASS")
else:
    print(f"  FAIL: {inf_count} Inf values detected")
    log.error(f"RESULT: FAIL - {inf_count} Inf values")
    validation_passed = False


# === CHECK 7: DATA RANGE ===
print(f"\n[Check 7/9] Radiance value range...")
log.info("\n" + "="*70)
log.info("CHECK 7: RADIANCE VALUE RANGE")
log.info("="*70)


radiance_stats = df['mean_radiance'].describe()
print(f"  Min:    {radiance_stats['min']:.4f}")
print(f"  Mean:   {radiance_stats['mean']:.4f}")
print(f"  Median: {radiance_stats['50%']:.4f}")
print(f"  Max:    {radiance_stats['max']:.4f}")
log.info(f"Min:    {radiance_stats['min']:.4f}")
log.info(f"Mean:   {radiance_stats['mean']:.4f}")
log.info(f"Median: {radiance_stats['50%']:.4f}")
log.info(f"Max:    {radiance_stats['max']:.4f}")


# Check for negative values (invalid)
negative_count = (df['mean_radiance'] < 0).sum()
if negative_count > 0:
    print(f"  WARNING: {negative_count} negative radiance values (should be >= 0)")
    log.warning(f"RESULT: FAIL - {negative_count} negative values")
    validation_passed = False
else:
    print(f"  PASS: All radiance values >= 0")
    log.info("RESULT: PASS - No negative values")


# Sanity check: reasonable max (VIIRS typically < 100 nW/cm²/sr)
if radiance_stats['max'] > 100:
    print(f"  WARNING: Max radiance {radiance_stats['max']:.2f} exceeds typical VIIRS range")
    log.warning(f"WARNING: Max radiance {radiance_stats['max']:.2f} unusually high")


# === CHECK 8: DISTRICT-QUARTER BALANCE ===
print(f"\n[Check 8/9] District-quarter balance...")
log.info("\n" + "="*70)
log.info("CHECK 8: DISTRICT-QUARTER BALANCE")
log.info("="*70)


obs_per_district = df.groupby('district_state_id').size()
print(f"  Expected obs per district: 40 (one per quarter)")
print(f"  Actual obs per district:")
print(f"    Min:  {obs_per_district.min()}")
print(f"    Max:  {obs_per_district.max()}")
print(f"    Mean: {obs_per_district.mean():.1f}")
log.info(f"Expected: 40 obs per district")
log.info(f"Actual: Min={obs_per_district.min()}, Max={obs_per_district.max()}, Mean={obs_per_district.mean():.1f}")


if obs_per_district.min() == obs_per_district.max() == 40:
    print(f"  PASS: Balanced panel (all districts have 40 quarters)")
    log.info("RESULT: PASS - Balanced panel")
else:
    print(f"  WARNING: Unbalanced panel detected")
    imbalanced_districts = obs_per_district[obs_per_district != 40]
    print(f"    {len(imbalanced_districts)} districts with != 40 observations")
    log.warning(f"RESULT: FAIL - {len(imbalanced_districts)} districts unbalanced")
    log.warning(f"Unbalanced districts:\n{imbalanced_districts.head(10)}")
    validation_passed = False


# === CHECK 9: HOMONYMOUS DISTRICT VERIFICATION ===
print(f"\n[Check 9/9] Homonymous district verification...")
log.info("\n" + "="*70)
log.info("CHECK 9: HOMONYMOUS DISTRICT VERIFICATION")
log.info("="*70)


# Identify districts with same name but different states
district_counts = df.groupby('district_gadm')['state_gadm'].nunique()
homonymous_districts = district_counts[district_counts > 1]


print(f"  Homonymous district pairs found: {len(homonymous_districts)}")
log.info(f"Homonymous district pairs found: {len(homonymous_districts)}")


if len(homonymous_districts) > 0:
    print(f"  Homonymous districts:")
    log.info("Homonymous districts:")
    for district in homonymous_districts.index:
        states = df[df['district_gadm'] == district]['state_gadm'].unique()
        print(f"    {district}: {', '.join(states)}")
        log.info(f"  {district}: {', '.join(states)}")
    
    # Verify Aurangabad has different radiance values (litmus test)
    if 'Aurangabad' in homonymous_districts.index:
        print(f"\n  Aurangabad litmus test:")
        aug_bihar = df[(df['district_gadm'] == 'Aurangabad') & (df['state_gadm'] == 'Bihar')]['mean_radiance'].mean()
        aug_maha = df[(df['district_gadm'] == 'Aurangabad') & (df['state_gadm'] == 'Maharashtra')]['mean_radiance'].mean()
        print(f"    Bihar mean radiance:       {aug_bihar:.4f}")
        print(f"    Maharashtra mean radiance: {aug_maha:.4f}")
        log.info(f"Aurangabad Bihar mean: {aug_bihar:.4f}")
        log.info(f"Aurangabad Maharashtra mean: {aug_maha:.4f}")
        
        if abs(aug_bihar - aug_maha) > 0.01:
            print(f"    PASS: Distinct radiance values (no contamination)")
            log.info("RESULT: PASS - Aurangabad values distinct")
        else:
            print(f"    WARNING: Similar radiance values (possible contamination)")
            log.warning("RESULT: FAIL - Aurangabad values too similar")
            validation_passed = False
else:
    print(f"  WARNING: No homonymous districts detected (expected 7 pairs)")
    log.warning("WARNING: Expected 7 homonymous pairs, found 0")


# === FINAL SUMMARY ===
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)
log.info("\n" + "="*70)
log.info("FINAL VALIDATION SUMMARY")
log.info("="*70)


if validation_passed:
    print("  ALL CHECKS PASSED")
    print("  Data quality: EXCELLENT")
    print("  Ready for regression analysis (Scripts 27-30)")
    log.info("STATUS: ALL CHECKS PASSED")
    log.info("Data ready for regression analysis")
else:
    print("  VALIDATION FAILED")
    print("  Review issues above before proceeding")
    print("  Check log: 05_Outputs/Logs/26_viirs_quarterly_validation.txt")
    log.error("STATUS: VALIDATION FAILED")
    log.error("Review issues before proceeding")


print("="*70)
log.info("="*70)
log.info("END OF VALIDATION REPORT")
log.info("="*70)