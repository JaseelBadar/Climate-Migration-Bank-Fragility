import pandas as pd
import numpy as np
import logging
import os

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/25_descriptive_summary.txt',
    level=logging.INFO,
    format='%(message)s'  # Plain text for readability
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 3d: Descriptive Statistics")
print("="*70)
log.info("="*70)
log.info("DESCRIPTIVE STATISTICS SUMMARY")
log.info("="*70)

# === LOAD REGRESSION-READY PANEL ===
print(f"\n[1/5] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
print(f"  ✓ Districts: {df['district_gadm'].nunique()}")
print(f"  ✓ Quarters: {df['quarter'].nunique()}")
log.info(f"Panel loaded: {len(df):,} rows")
log.info(f"Districts: {df['district_gadm'].nunique()}")
log.info(f"Quarters: {df['quarter'].nunique()}\n")

# === PANEL STRUCTURE ===
print(f"\n[2/5] Panel structure...")
log.info("PANEL STRUCTURE")
log.info("-" * 50)

# Time coverage
years = df['year'].unique()
quarters = df['quarter'].unique()
print(f"  ✓ Years: {df['year'].min()} - {df['year'].max()}")
print(f"  ✓ Quarters: {len(quarters)} ({quarters[0]} to {quarters[-1]})")
log.info(f"Time period: {df['year'].min()}-{df['year'].max()}")
log.info(f"Quarters: {len(quarters)} ({quarters[0]} to {quarters[-1]})")

# District-quarter balance
district_quarter_counts = df.groupby('district_gadm').size()
print(f"  ✓ Obs per district: min={district_quarter_counts.min()}, max={district_quarter_counts.max()}, mean={district_quarter_counts.mean():.1f}")
log.info(f"Obs per district: min={district_quarter_counts.min()}, max={district_quarter_counts.max()}, mean={district_quarter_counts.mean():.1f}\n")

# === VARIABLE COVERAGE ===
print(f"\n[3/5] Variable coverage (% non-missing)...")
log.info("VARIABLE COVERAGE")
log.info("-" * 50)

key_vars = [
    'deposits_crores',
    'log_deposits_crores',
    'mean_radiance',
    'log_lights_qt',
    'lights_change_qt',
    'deposit_change_qt',
    'flood_exposure_ruleA_qt',
    'flood_exposure_ruleB_qt'
]

coverage_stats = []
for var in key_vars:
    if var in df.columns:
        coverage = df[var].notna().sum() / len(df) * 100
        print(f"  {var:30s}: {coverage:5.1f}%")
        log.info(f"{var:30s}: {coverage:5.1f}%")
        coverage_stats.append({'variable': var, 'coverage_pct': coverage})

# === SUMMARY STATISTICS ===
print(f"\n[4/5] Summary statistics (continuous variables)...")
log.info("\nSUMMARY STATISTICS")
log.info("-" * 50)

continuous_vars = [
    'deposits_crores',
    'log_deposits_crores',
    'mean_radiance',
    'log_lights_qt',
    'lights_change_qt',
    'deposit_change_qt'
]

summary_stats = []
for var in continuous_vars:
    if var in df.columns and df[var].notna().sum() > 0:
        stats = df[var].describe()
        summary_stats.append({
            'variable': var,
            'mean': stats['mean'],
            'std': stats['std'],
            'min': stats['min'],
            'p25': stats['25%'],
            'p50': stats['50%'],
            'p75': stats['75%'],
            'max': stats['max'],
            'n': df[var].notna().sum()
        })
        
        print(f"\n  {var}:")
        print(f"    Mean: {stats['mean']:.4f}, Std: {stats['std']:.4f}")
        print(f"    Min: {stats['min']:.4f}, Max: {stats['max']:.4f}")
        print(f"    N: {df[var].notna().sum():,}")
        
        log.info(f"\n{var}:")
        log.info(f"  Mean: {stats['mean']:.4f}, Std: {stats['std']:.4f}")
        log.info(f"  Min: {stats['min']:.4f}, Max: {stats['max']:.4f}")
        log.info(f"  N: {df[var].notna().sum():,}")

# === FLOOD EXPOSURE SUMMARY ===
print(f"\n[5/5] Flood exposure summary...")
log.info("\nFLOOD EXPOSURE SUMMARY")
log.info("-" * 50)

# Rule A
ruleA_exposed = df['flood_exposure_ruleA_qt'].sum()
ruleA_pct = (ruleA_exposed / len(df)) * 100
print(f"  Rule A (state fallback):")
print(f"    Exposed obs: {int(ruleA_exposed):,} ({ruleA_pct:.2f}%)")
log.info(f"Rule A (state fallback):")
log.info(f"  Exposed obs: {int(ruleA_exposed):,} ({ruleA_pct:.2f}%)")

# Rule B
ruleB_exposed = df['flood_exposure_ruleB_qt'].sum()
ruleB_pct = (ruleB_exposed / len(df)) * 100
print(f"  Rule B (district-only):")
print(f"    Exposed obs: {int(ruleB_exposed):,} ({ruleB_pct:.2f}%)")
log.info(f"Rule B (district-only):")
log.info(f"  Exposed obs: {int(ruleB_exposed):,} ({ruleB_pct:.2f}%)")

# Districts ever exposed
districts_ever_exposed_A = df[df['flood_exposure_ruleA_qt'] == 1]['district_gadm'].nunique()
districts_ever_exposed_B = df[df['flood_exposure_ruleB_qt'] == 1]['district_gadm'].nunique()
print(f"  Districts ever exposed:")
print(f"    Rule A: {districts_ever_exposed_A}")
print(f"    Rule B: {districts_ever_exposed_B}")
log.info(f"Districts ever exposed:")
log.info(f"  Rule A: {districts_ever_exposed_A}")
log.info(f"  Rule B: {districts_ever_exposed_B}")

# === SAVE TABLE ===
print(f"\n[Output] Saving descriptive statistics table...")
os.makedirs('05_Outputs/Tables', exist_ok=True)
summary_df = pd.DataFrame(summary_stats)
output_path = '05_Outputs/Tables/01_descriptive_stats.csv'
summary_df.to_csv(output_path, index=False)

# === SUMMARY ===
print("="*70)
print("DESCRIPTIVE STATISTICS COMPLETE")
print("="*70)
print(f"Table saved: {output_path}")
print(f"Log saved: 05_Outputs/Logs/25_descriptive_summary.txt")
log.info("\n" + "="*70)
log.info("END OF SUMMARY")
log.info("="*70)
print("="*70)
print("\nPHASE 3d COMPLETE - Analysis panel ready for Phase 4 regressions")
print("="*70)