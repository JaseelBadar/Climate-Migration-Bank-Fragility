import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
log_path = '05_Outputs/Logs/26_viirs_monthly_validation.txt'

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
print("PHASE 3d: VIIRS MONTHLY PANEL VALIDATION")
print("="*70)
log.info("="*70)
log.info("VIIRS MONTHLY PANEL VALIDATION REPORT")
log.info(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log.info("="*70)

# === LOAD DATA ===
print(f"\n[Loading] viirs_monthly_panel.csv...")
try:
    df = pd.read_csv('02_Data_Intermediate/viirs_monthly_panel.csv')
    print(f"  ✓ Loaded: {len(df):,} rows")
    log.info(f"\nFile loaded successfully: {len(df):,} rows")
except FileNotFoundError:
    print(f"  ✗ ERROR: File not found. Script 21 may not have completed.")
    log.error("ERROR: viirs_monthly_panel.csv not found")
    exit(1)

# === VALIDATION FLAGS ===
validation_passed = True

# === CHECK 1: EXPECTED DIMENSIONS ===
print(f"\n[Check 1/8] Expected dimensions...")
log.info("\n" + "="*70)
log.info("CHECK 1: EXPECTED DIMENSIONS")
log.info("="*70)

expected_rows = 659 * 120 # 79,080
actual_rows = len(df)

print(f"  Expected: {expected_rows:,} rows (659 districts × 120 months)")
print(f"  Actual:   {actual_rows:,} rows")
log.info(f"Expected: {expected_rows:,} rows (659 districts × 120 months)")
log.info(f"Actual:   {actual_rows:,} rows")

if actual_rows == expected_rows:
    print(f"  ✓ PASS: Dimensions match")
    log.info("RESULT: PASS")
else:
    print(f"  ⚠ WARNING: Missing {expected_rows - actual_rows:,} rows ({(expected_rows - actual_rows)/expected_rows*100:.2f}%)")
    log.warning(f"RESULT: FAIL - Missing {expected_rows - actual_rows:,} rows")
    validation_passed = False

# === CHECK 2: REQUIRED COLUMNS ===
print(f"\n[Check 2/8] Required columns...")
log.info("\n" + "="*70)
log.info("CHECK 2: REQUIRED COLUMNS")
log.info("="*70)

required_cols = ['gadm_district', 'gadm_state', 'year', 'month', 'mean_radiance', 'pixel_count']
missing_cols = [col for col in required_cols if col not in df.columns]

if not missing_cols:
    print(f"  ✓ PASS: All required columns present")
    log.info("RESULT: PASS - All required columns present")
else:
    print(f"  ✗ FAIL: Missing columns: {missing_cols}")
    log.error(f"RESULT: FAIL - Missing columns: {missing_cols}")
    validation_passed = False

# === CHECK 3: DISTRICT COVERAGE ===
print(f"\n[Check 3/8] District coverage...")
log.info("\n" + "="*70)
log.info("CHECK 3: DISTRICT COVERAGE")
log.info("="*70)

unique_districts = df['gadm_district'].nunique()
expected_districts = 659

print(f"  Expected: {expected_districts} districts")
print(f"  Actual:   {unique_districts} districts")
log.info(f"Expected: {expected_districts} districts")
log.info(f"Actual:   {unique_districts} districts")

if unique_districts == expected_districts:
    print(f"  ✓ PASS: All districts present")
    log.info("RESULT: PASS")
else:
    print(f"  ⚠ WARNING: Missing {expected_districts - unique_districts} districts")
    log.warning(f"RESULT: FAIL - Missing {expected_districts - unique_districts} districts")
    validation_passed = False

# === CHECK 4: TEMPORAL COVERAGE ===
print(f"\n[Check 4/8] Temporal coverage...")
log.info("\n" + "="*70)
log.info("CHECK 4: TEMPORAL COVERAGE")
log.info("="*70)

# Expected: 2015-2024, months 1-12 each year
year_month_combos = df[['year', 'month']].drop_duplicates()
expected_months = 120  # 10 years × 12 months

print(f"  Expected: {expected_months} unique year-month combinations")
print(f"  Actual:   {len(year_month_combos)} combinations")
print(f"  Year range: {df['year'].min()} - {df['year'].max()}")
log.info(f"Expected: {expected_months} unique year-month combinations")
log.info(f"Actual:   {len(year_month_combos)} combinations")
log.info(f"Year range: {df['year'].min()} - {df['year'].max()}")

# Check for gaps
expected_year_months = [(y, m) for y in range(2015, 2025) for m in range(1, 13)]
actual_year_months = set(zip(df['year'], df['month']))
missing_months = [ym for ym in expected_year_months if ym not in actual_year_months]

if not missing_months:
    print(f"  ✓ PASS: All months present (2015-01 to 2024-12)")
    log.info("RESULT: PASS - No temporal gaps")
else:
    print(f"  ⚠ WARNING: Missing {len(missing_months)} months:")
    print(f"    {missing_months[:5]}..." if len(missing_months) > 5 else f"    {missing_months}")
    log.warning(f"RESULT: FAIL - Missing months: {missing_months}")
    validation_passed = False

# === CHECK 5: DATA QUALITY (NaN) ===
print(f"\n[Check 5/8] Missing values (NaN)...")
log.info("\n" + "="*70)
log.info("CHECK 5: MISSING VALUES (NaN)")
log.info("="*70)

nan_counts = df[['mean_radiance', 'pixel_count']].isna().sum()
print(f"  mean_radiance NaN: {nan_counts['mean_radiance']:,} ({nan_counts['mean_radiance']/len(df)*100:.2f}%)")
print(f"  pixel_count NaN:   {nan_counts['pixel_count']:,} ({nan_counts['pixel_count']/len(df)*100:.2f}%)")
log.info(f"mean_radiance NaN: {nan_counts['mean_radiance']:,} ({nan_counts['mean_radiance']/len(df)*100:.2f}%)")
log.info(f"pixel_count NaN:   {nan_counts['pixel_count']:,} ({nan_counts['pixel_count']/len(df)*100:.2f}%)")

if nan_counts['mean_radiance'] == 0:
    print(f"  ✓ PASS: No missing radiance values")
    log.info("RESULT: PASS - No missing values")
else:
    print(f"  ⚠ WARNING: {nan_counts['mean_radiance']} NaN values in mean_radiance")
    log.warning(f"RESULT: FAIL - {nan_counts['mean_radiance']} NaN values detected")
    validation_passed = False

# === CHECK 6: DATA QUALITY (Inf) ===
print(f"\n[Check 6/8] Infinite values (Inf)...")
log.info("\n" + "="*70)
log.info("CHECK 6: INFINITE VALUES (Inf)")
log.info("="*70)

inf_count = np.isinf(df['mean_radiance']).sum()
print(f"  Inf values: {inf_count}")
log.info(f"Inf values: {inf_count}")

if inf_count == 0:
    print(f"  ✓ PASS: No infinite values")
    log.info("RESULT: PASS")
else:
    print(f"  ✗ FAIL: {inf_count} Inf values detected")
    log.error(f"RESULT: FAIL - {inf_count} Inf values")
    validation_passed = False

# === CHECK 7: DATA RANGE ===
print(f"\n[Check 7/8] Radiance value range...")
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
    print(f"  ⚠ WARNING: {negative_count} negative radiance values (should be ≥ 0)")
    log.warning(f"RESULT: FAIL - {negative_count} negative values")
    validation_passed = False
else:
    print(f"  ✓ PASS: All radiance values ≥ 0")
    log.info("RESULT: PASS - No negative values")

# Sanity check: reasonable max (VIIRS typically < 100 nW/cm²/sr)
if radiance_stats['max'] > 100:
    print(f"  ⚠ WARNING: Max radiance {radiance_stats['max']:.2f} exceeds typical VIIRS range")
    log.warning(f"WARNING: Max radiance {radiance_stats['max']:.2f} unusually high")

# === CHECK 8: DISTRICT-MONTH BALANCE ===
print(f"\n[Check 8/8] District-month balance...")
log.info("\n" + "="*70)
log.info("CHECK 8: DISTRICT-MONTH BALANCE")
log.info("="*70)

obs_per_district = df.groupby('gadm_district').size()
print(f"  Expected obs per district: 120 (one per month)")
print(f"  Actual obs per district:")
print(f"    Min:  {obs_per_district.min()}")
print(f"    Max:  {obs_per_district.max()}")
print(f"    Mean: {obs_per_district.mean():.1f}")
log.info(f"Expected: 120 obs per district")
log.info(f"Actual: Min={obs_per_district.min()}, Max={obs_per_district.max()}, Mean={obs_per_district.mean():.1f}")

if obs_per_district.min() == obs_per_district.max() == 120:
    print(f"  ✓ PASS: Balanced panel (all districts have 120 months)")
    log.info("RESULT: PASS - Balanced panel")
else:
    print(f"  ⚠ WARNING: Unbalanced panel detected")
    imbalanced_districts = obs_per_district[obs_per_district != 120]
    print(f"    {len(imbalanced_districts)} districts with ≠ 120 observations")
    log.warning(f"RESULT: FAIL - {len(imbalanced_districts)} districts unbalanced")
    log.warning(f"Unbalanced districts:\n{imbalanced_districts.head(10)}")
    validation_passed = False

# === FINAL SUMMARY ===
print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)
log.info("\n" + "="*70)
log.info("FINAL VALIDATION SUMMARY")
log.info("="*70)

if validation_passed:
    print("  ✓✓✓ ALL CHECKS PASSED ✓✓✓")
    print("  Data quality: EXCELLENT")
    print("  Proceed to Script 22 (quarterly aggregation)")
    log.info("STATUS: ✓✓✓ ALL CHECKS PASSED ✓✓✓")
    log.info("Data ready for quarterly aggregation (Script 22)")
else:
    print("  ⚠⚠⚠ VALIDATION FAILED ⚠⚠⚠")
    print("  Review issues above before proceeding")
    print("  Check log: 05_Outputs/Logs/26_viirs_monthly_validation.txt")
    log.error("STATUS: ⚠⚠⚠ VALIDATION FAILED ⚠⚠⚠")
    log.error("Review issues before running Script 22")

print("="*70)
log.info("="*70)
log.info("END OF VALIDATION REPORT")
log.info("="*70)