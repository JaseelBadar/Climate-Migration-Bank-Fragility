"""
29_regression_H3_timing.py - Phase 4 Regression Analysis

H3: Timing of deposit responses (distributed lag model)

TESTS:
  1. Immediate effect (t=0): Same-quarter flood → deposit change
  2. Delayed effect (t-1): Previous-quarter flood → current deposit change
  3. Shadow banking signature: Deposits decline immediately, recover slowly

SPECIFICATION:
  deposit_change_qt = β₀ + β₁·flood_qt + β₂·flood_lag1_qt + δ_d + δ_t + ε

OUTPUTS:
  - 05_Outputs/Tables/04_H3_timing.csv
  - 05_Outputs/Logs/29_H3_timing_results.txt

ESTIMATED RUNTIME: 3-5 minutes
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import logging
import os

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/29_H3_timing_results.txt',
    level=logging.INFO,
    format='%(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 4: H3 TIMING ANALYSIS (Distributed Lags)")
print("="*70)
log.info("="*70)
log.info("H3: TIMING OF DEPOSIT RESPONSES")
log.info("Distributed lag model: Floods (t, t-1) → Deposit change")
log.info("="*70)

# === LOAD DATA ===
print(f"\n[1/5] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_ready_panel.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
log.info(f"\nPanel loaded: {len(df):,} rows")

# === RESTRICT TO NON-MISSING ===
print(f"\n[2/5] Restricting to complete cases...")
initial_n = len(df)

df_reg = df[
    df['deposit_change_qt'].notna() & 
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_lag1_qt'].notna()
].copy()

print(f"  Initial: {initial_n:,} obs")
print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Dropped: {initial_n - len(df_reg):,} obs")
log.info(f"Initial: {initial_n:,} obs")
log.info(f"After restrictions: {len(df_reg):,} obs")

# === ENCODE FIXED EFFECTS ===
print(f"\n[3/5] Encoding fixed effects...")
df_reg['district_fe'] = pd.Categorical(df_reg['district_gadm'])
df_reg['quarter_fe'] = pd.Categorical(df_reg['quarter'])

print(f"  ✓ District FE: {df_reg['district_fe'].nunique()} categories")
print(f"  ✓ Quarter FE: {df_reg['quarter_fe'].nunique()} categories")

# === REGRESSION: DISTRIBUTED LAG MODEL ===
print(f"\n[4/5] Running distributed lag regression...")
log.info("\n" + "="*70)
log.info("REGRESSION SPECIFICATION")
log.info("="*70)
log.info("DV: deposit_change_qt (Δ log deposits)")
log.info("IVs: flood_exposure_ruleA_qt (contemporaneous)")
log.info("     flood_lag1_qt (lagged one quarter)")
log.info("FE: District + Quarter")

formula = 'deposit_change_qt ~ flood_exposure_ruleA_qt + flood_lag1_qt + C(district_fe) + C(quarter_fe)'

try:
    model = ols(formula, data=df_reg).fit(cov_type='HC1')
    print(f"  ✓ Model fitted")
    print(f"  ✓ N obs: {model.nobs:,.0f}")
    print(f"  ✓ R²: {model.rsquared:.4f}")
    log.info(f"\nModel fitted successfully")
    log.info(f"N obs: {model.nobs:,.0f}")
    log.info(f"R²: {model.rsquared:.4f}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    log.error(f"Model fitting failed: {e}")
    exit(1)

# === EXTRACT RESULTS ===
print(f"\n[5/5] Extracting timing coefficients...")

# Contemporaneous effect (t=0)
flood_t0_coef = model.params.get('flood_exposure_ruleA_qt', np.nan)
flood_t0_se = model.bse.get('flood_exposure_ruleA_qt', np.nan)
flood_t0_pval = model.pvalues.get('flood_exposure_ruleA_qt', np.nan)

# Lagged effect (t-1)
flood_t1_coef = model.params.get('flood_lag1_qt', np.nan)
flood_t1_se = model.bse.get('flood_lag1_qt', np.nan)
flood_t1_pval = model.pvalues.get('flood_lag1_qt', np.nan)

print(f"\n  CONTEMPORANEOUS (t=0): flood_exposure_ruleA_qt")
print(f"    β̂  = {flood_t0_coef:.6f}")
print(f"    SE = {flood_t0_se:.6f}")
print(f"    p  = {flood_t0_pval:.4f}")

print(f"\n  LAGGED (t-1): flood_lag1_qt")
print(f"    β̂  = {flood_t1_coef:.6f}")
print(f"    SE = {flood_t1_se:.6f}")
print(f"    p  = {flood_t1_pval:.4f}")

log.info("\n" + "="*70)
log.info("TIMING RESULTS")
log.info("="*70)
log.info(f"Contemporaneous (t=0):")
log.info(f"  Coefficient: {flood_t0_coef:.6f}")
log.info(f"  Std Error:   {flood_t0_se:.6f}")
log.info(f"  p-value:     {flood_t0_pval:.4f}")
log.info(f"\nLagged (t-1):")
log.info(f"  Coefficient: {flood_t1_coef:.6f}")
log.info(f"  Std Error:   {flood_t1_se:.6f}")
log.info(f"  p-value:     {flood_t1_pval:.4f}")

# Interpretation: Shadow banking signature
print(f"\n[Interpretation] Shadow Banking Signature:")
if flood_t0_coef < 0 and flood_t0_pval < 0.05:
    print(f"  ✓ Immediate decline (t=0): Significant negative effect")
    log.info("Immediate effect: SIGNIFICANT negative (supports shadow-run hypothesis)")
else:
    print(f"  ⚠ Immediate decline (t=0): Not significant or wrong sign")
    log.info("Immediate effect: Not significant")

if abs(flood_t1_coef) < abs(flood_t0_coef):
    print(f"  ✓ Attenuation: |β_t-1| < |β_t0| (recovery signal)")
    log.info("Lagged effect smaller: Consistent with temporary shock")
else:
    print(f"  ⚠ No attenuation: Persistent or amplifying effect")
    log.info("Lagged effect not smaller: Persistent shock")

# === SAVE RESULTS ===
print(f"\n[Output] Saving timing analysis table...")
os.makedirs('05_Outputs/Tables', exist_ok=True)

results_df = pd.DataFrame({
    'lag': ['t=0 (contemporaneous)', 't-1 (lagged 1Q)'],
    'coefficient': [flood_t0_coef, flood_t1_coef],
    'std_error': [flood_t0_se, flood_t1_se],
    'p_value': [flood_t0_pval, flood_t1_pval]
})

results_df.to_csv('05_Outputs/Tables/04_H3_timing.csv', index=False)

# Save full model summary
with open('05_Outputs/Logs/29_H3_timing_full.txt', 'w') as f:
    f.write(str(model.summary()))

# === SUMMARY ===
print("="*70)
print("H3 TIMING ANALYSIS COMPLETE")
print("="*70)
print(f"Table: 05_Outputs/Tables/04_H3_timing.csv")
print(f"Log:   05_Outputs/Logs/29_H3_timing_results.txt")
log.info("\n" + "="*70)
log.info("TIMING ANALYSIS COMPLETE")
log.info("="*70)
print("="*70)
print("\nPHASE 4 REGRESSION PIPELINE COMPLETE")
print("Ready for robustness checks and paper drafting")
print("="*70)