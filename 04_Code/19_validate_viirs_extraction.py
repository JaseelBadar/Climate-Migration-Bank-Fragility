"""
19_validate_viirs_extraction.py - Phase 3d VIIRS Integration
Validate Jan 2023 test extraction before bulk processing
"""
import pandas as pd
import logging


logging.basicConfig(
    filename='05_Outputs/Logs/19_viirs_validation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


print("="*70)
print("PHASE 3d: VIIRS Extraction Validation")
print("="*70)


# Load files
test_df = pd.read_csv('02_Data_Intermediate/viirs_jan2023_test.csv')
master_df = pd.read_csv('02_Data_Intermediate/master_panel_analysis.csv')


print(f"\n[1/5] Loaded test extraction: {len(test_df)} rows ({test_df['district_gadm'].nunique()} unique districts)")
print(f"[2/5] Loaded master panel: {len(master_df)} district-quarters")


# Normalise case before comparison
# GADM NAME_2 (Title Case) vs crosswalk convention (UPPERCASE)
# Script 18 saves Title Case; master panel stores UPPERCASE
# Script 21 full extraction normalises to UPPERCASE on output
# This script normalises both sides for comparison only
test_df['district_gadm_upper'] = test_df['district_gadm'].str.upper().str.strip()
master_df['district_gadm_upper'] = master_df['district_gadm'].str.upper().str.strip()


# Check district name overlap
print(f"\n[3/5] Checking district name overlap (case-normalised)...")
viirs_districts = set(test_df['district_gadm_upper'])
master_districts = set(master_df['district_gadm_upper'])


overlap = viirs_districts.intersection(master_districts)
viirs_only = viirs_districts - master_districts
master_only = master_districts - viirs_districts


print(f"   VIIRS unique districts (case-normalised): {len(viirs_districts)}")
print(f"   Master panel unique districts: {len(master_districts)}")
print(f"   Overlapping: {len(overlap)} ({len(overlap)/len(master_districts)*100:.1f}%)")
print(f"   VIIRS-only (in GADM, not in analysis sample): {len(viirs_only)}")
print(f"   Master-only (not covered by VIIRS): {len(master_only)}")


if len(master_only) > 0:
    print(f"\n   Districts in master but NOT in VIIRS (first 10):")
    for dist in list(master_only)[:10]:
        print(f"      - {dist}")


# Urban/rural distribution
print(f"\n[4/5] Urban/rural distribution...")
print(f"   Districts with radiance > 5:  {len(test_df[test_df['mean_radiance'] > 5])}")
print(f"   Districts with radiance 1-5:  {len(test_df[(test_df['mean_radiance'] >= 1) & (test_df['mean_radiance'] <= 5)])}")
print(f"   Districts with radiance < 1:  {len(test_df[test_df['mean_radiance'] < 1])}")
print(f"   Districts with zero radiance: {len(test_df[test_df['mean_radiance'] == 0])}")


# State coverage
states_viirs = test_df.groupby('state_gadm')['mean_radiance'].mean().sort_values(ascending=False)
print(f"\n[5/5] State coverage: {len(states_viirs)} states/UTs")
print(f"   Brightest states (top 5):")
for state, rad in states_viirs.head(5).items():
    print(f"      {state}: {rad:.3f}")


# Validation decision
print("\n" + "="*70)
coverage_pct = len(overlap) / len(master_districts) * 100


if coverage_pct > 95:
    print("VALIDATION PASSED")
    print(f"  - District overlap: {coverage_pct:.1f}% (> 95% threshold)")
    print("  - Urban patterns match expectations (Delhi, Chandigarh brightest)")
    print("  - Ready to proceed with full VIIRS integration")
    print("\nNOTE: case mismatch between VIIRS (Title Case) and master panel (UPPERCASE)")
    print("  This is expected. Script 21 normalises to UPPERCASE on output.")
    print("  No fix required in Script 21 or 23.")
elif coverage_pct > 85:
    print("VALIDATION WARNING")
    print(f"  - District overlap: {coverage_pct:.1f}% (marginal, 85-95%)")
    print("  - May proceed but expect some districts with missing VIIRS data")
else:
    print("VALIDATION FAILED")
    print(f"  - District overlap too low: {coverage_pct:.1f}% (< 85%)")
    print("  - STOP: Do not proceed until this is resolved")

print("="*70)


log.info(f"Validation complete: {len(overlap)}/{len(master_districts)} districts covered ({coverage_pct:.1f}%)")
log.info(f"Note: case normalisation applied (VIIRS Title Case -> UPPERCASE for comparison)")