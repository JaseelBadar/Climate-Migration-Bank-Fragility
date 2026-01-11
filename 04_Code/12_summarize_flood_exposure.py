import pandas as pd
import numpy as np

df = pd.read_csv('02_Data_Intermediate/flood_exposure_panel.csv')

log_lines = []
log_lines.append("="*70)
log_lines.append("FLOOD EXPOSURE PANEL SUMMARY")
log_lines.append("Script: 10_build_flood_exposure.py")
log_lines.append(f"Generated: 2026-01-11")
log_lines.append("="*70)

# Overall statistics
log_lines.append("\n[1] PANEL DIMENSIONS")
log_lines.append(f"   Total district-quarters: {len(df):,}")
log_lines.append(f"   Districts: {df['district_gadm'].nunique()}")
log_lines.append(f"   Quarters: {df['quarter'].nunique()}")
log_lines.append(f"   Date range: {df['quarter'].min()} to {df['quarter'].max()}")

# Exposure rates
ruleA_pct = (df['flood_exposure_ruleA_qt'].sum() / len(df)) * 100
ruleB_pct = (df['flood_exposure_ruleB_qt'].sum() / len(df)) * 100

log_lines.append("\n[2] EXPOSURE RATES")
log_lines.append(f"   Rule A (full sample): {df['flood_exposure_ruleA_qt'].sum():,} district-quarters ({ruleA_pct:.2f}%)")
log_lines.append(f"   Rule B (high-precision): {df['flood_exposure_ruleB_qt'].sum():,} district-quarters ({ruleB_pct:.2f}%)")

# Temporal distribution
log_lines.append("\n[3] TEMPORAL DISTRIBUTION")
log_lines.append("   Exposure by year (Rule A):")
yearly = df.groupby('year')['flood_exposure_ruleA_qt'].sum().sort_index()
for year, count in yearly.items():
    if count > 0:
        log_lines.append(f"      {int(year)}: {int(count)} district-quarters")

# Top exposed districts
log_lines.append("\n[4] TOP 15 EXPOSED DISTRICTS (Rule A)")
top_districts_A = df[df['flood_exposure_ruleA_qt']==1].groupby(['district_gadm', 'state_gadm']).size().sort_values(ascending=False).head(15)
for (dist, state), count in top_districts_A.items():
    log_lines.append(f"   {dist:20s} ({state:20s}): {count:2d} quarters")

log_lines.append("\n[5] TOP 15 EXPOSED DISTRICTS (Rule B)")
top_districts_B = df[df['flood_exposure_ruleB_qt']==1].groupby(['district_gadm', 'state_gadm']).size().sort_values(ascending=False).head(15)
for (dist, state), count in top_districts_B.items():
    log_lines.append(f"   {dist:20s} ({state:20s}): {count:2d} quarters")

# State distribution
log_lines.append("\n[6] EXPOSURE BY STATE (Rule A, top 10)")
state_exp = df[df['flood_exposure_ruleA_qt']==1].groupby('state_gadm').size().sort_values(ascending=False).head(10)
for state, count in state_exp.items():
    log_lines.append(f"   {state:25s}: {count:4d} district-quarters")

# Known limitations
log_lines.append("\n[7] KNOWN LIMITATIONS")
log_lines.append("   - 46 unmatched EM-DAT location tokens (typos, J&K data gaps, historical names)")
log_lines.append("   - State-level fallback (Rule A) may introduce measurement error")
log_lines.append("   - Historical district names (e.g., 'Cuddapah' → 'Kadapa') not fully resolved")
log_lines.append("   - Rule B exposure rate (1.02%) reflects EM-DAT district precision limit")

# Validation summary
log_lines.append("\n[8] VALIDATION CHECKS (11_validate_flood_events.py)")
log_lines.append("   ✓ Event 2019-0331-IND: 33 Rule B districts correctly coded")
log_lines.append("   ✓ Event 2023-0428-IND: State fallback triggered for HP, Delhi (Rule A only)")
log_lines.append("   ✓ Event 2015-0504-IND: 9/10 AP/TN districts matched (90% rate)")

log_lines.append("\n" + "="*70)
log_lines.append("SUMMARY COMPLETE")
log_lines.append("="*70)

# Write log
with open('05_Outputs/Logs/12_flood_exposure_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

print('\n'.join(log_lines))
print("\n✓ Summary saved: 05_Outputs/Logs/12_flood_exposure_summary.txt")