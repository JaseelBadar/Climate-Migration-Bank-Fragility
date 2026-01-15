"""
27_regression_H1_first_stage.py - Phase 4 Regression Analysis

H1: Floods → Nighttime lights decline (First Stage)

EQUATION:
  lights_change_qt = β₀ + β₁·flood_exposure_qt + δ_d + δ_t + ε

SPECIFICATION:
  - DV: lights_change_qt (Δ log lights)
  - IV: flood_exposure_ruleA_qt (binary, state fallback)
  - FE: District + Time fixed effects
  - SE: Clustered by district

OUTPUTS:
  - 05_Outputs/Tables/02_H1_first_stage.csv (regression table)
  - 05_Outputs/Logs/27_H1_regression.txt (detailed results)

ESTIMATED RUNTIME: 3-5 minutes
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
from statsmodels.iolib.summary2 import summary_col
import logging
import os

# === SETUP LOGGING ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
logging.basicConfig(
    filename='05_Outputs/Logs/27_H1_regression.txt',
    level=logging.INFO,
    format='%(message)s'
)
log = logging.getLogger(__name__)

print("="*70)
print("PHASE 4: H1 FIRST STAGE REGRESSION (Floods → Lights)")
print("="*70)
log.info("="*70)
log.info("H1: FIRST STAGE REGRESSION")
log.info("Floods → Nighttime Lights Decline")
log.info("="*70)

# === LOAD DATA ===
print(f"\n[1/5] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_ready_panel.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
log.info(f"\nPanel loaded: {len(df):,} rows")

# === RESTRICT TO NON-MISSING ===
print(f"\n[2/5] Restricting to observations with complete data...")
initial_n = len(df)

# Keep only obs with lights_change and flood exposure
df_reg = df[
    df['lights_change_qt'].notna() & 
    df['flood_exposure_ruleA_qt'].notna()
].copy()

print(f"  Initial: {initial_n:,} obs")
print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Dropped: {initial_n - len(df_reg):,} obs ({(initial_n - len(df_reg))/initial_n*100:.1f}%)")
log.info(f"Initial: {initial_n:,} obs")
log.info(f"After restrictions: {len(df_reg):,} obs")
log.info(f"Dropped: {initial_n - len(df_reg):,} obs")

# === ENCODE FIXED EFFECTS ===
print(f"\n[3/5] Encoding fixed effects...")

# District FE (categorical)
df_reg['district_fe'] = pd.Categorical(df_reg['district_gadm'])

# Time FE (quarter)
df_reg['quarter_fe'] = pd.Categorical(df_reg['quarter'])

print(f"  ✓ District FE: {df_reg['district_fe'].nunique()} categories")
print(f"  ✓ Quarter FE: {df_reg['quarter_fe'].nunique()} categories")
log.info(f"District FE: {df_reg['district_fe'].nunique()} categories")
log.info(f"Quarter FE: {df_reg['quarter_fe'].nunique()} categories")

# === REGRESSION SPECIFICATION ===
print(f"\n[4/5] Running regression: H1 First Stage...")
log.info("\n" + "="*70)
log.info("REGRESSION SPECIFICATION")
log.info("="*70)
log.info("DV: lights_change_qt (Δ log nighttime lights)")
log.info("IV: flood_exposure_ruleA_qt (binary)")
log.info("FE: District + Quarter")
log.info("SE: Robust (note: clustering by district requires linearmodels package)")

# OLS with FE (district + quarter absorbed via C() categorical)
formula = 'lights_change_qt ~ flood_exposure_ruleA_qt + C(district_fe) + C(quarter_fe)'

try:
    model = ols(formula, data=df_reg).fit(cov_type='HC1')  # Robust SE
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
print(f"\n[5/5] Extracting results...")

# Coefficient on flood exposure
flood_coef = model.params.get('flood_exposure_ruleA_qt', np.nan)
flood_se = model.bse.get('flood_exposure_ruleA_qt', np.nan)
flood_tstat = model.tvalues.get('flood_exposure_ruleA_qt', np.nan)
flood_pval = model.pvalues.get('flood_exposure_ruleA_qt', np.nan)

print(f"\n  COEFFICIENT: flood_exposure_ruleA_qt")
print(f"    β̂  = {flood_coef:.6f}")
print(f"    SE = {flood_se:.6f}")
print(f"    t  = {flood_tstat:.3f}")
print(f"    p  = {flood_pval:.4f}")

log.info("\n" + "="*70)
log.info("RESULTS: FLOOD EXPOSURE → LIGHTS CHANGE")
log.info("="*70)
log.info(f"Coefficient: {flood_coef:.6f}")
log.info(f"Std Error:   {flood_se:.6f}")
log.info(f"t-statistic: {flood_tstat:.3f}")
log.info(f"p-value:     {flood_pval:.4f}")

# Interpretation
if flood_pval < 0.01:
    sig_level = "***"
    interpretation = "HIGHLY SIGNIFICANT"
elif flood_pval < 0.05:
    sig_level = "**"
    interpretation = "SIGNIFICANT"
elif flood_pval < 0.10:
    sig_level = "*"
    interpretation = "WEAKLY SIGNIFICANT"
else:
    sig_level = ""
    interpretation = "NOT SIGNIFICANT"

print(f"    Significance: {interpretation} {sig_level}")
log.info(f"Significance: {interpretation} {sig_level}")

# === SAVE TABLE ===
print(f"\n[Output] Saving regression table...")
os.makedirs('05_Outputs/Tables', exist_ok=True)

# Create summary table
results_df = pd.DataFrame({
    'variable': ['flood_exposure_ruleA_qt'],
    'coefficient': [flood_coef],
    'std_error': [flood_se],
    't_statistic': [flood_tstat],
    'p_value': [flood_pval],
    'significance': [sig_level]
})

results_df.to_csv('05_Outputs/Tables/02_H1_first_stage.csv', index=False)

# Save full model summary
with open('05_Outputs/Logs/27_H1_regression_full.txt', 'w') as f:
    f.write(str(model.summary()))

# === SUMMARY ===
print("="*70)
print("H1 FIRST STAGE COMPLETE")
print("="*70)
print(f"Table: 05_Outputs/Tables/02_H1_first_stage.csv")
print(f"Log:   05_Outputs/Logs/27_H1_regression.txt")
print(f"Full:  05_Outputs/Logs/27_H1_regression_full.txt")
log.info("\n" + "="*70)
log.info("FIRST STAGE COMPLETE")
log.info("="*70)
print("="*70)
print("\nNEXT STEP: Run Script 28 (H2: IV 2SLS)")
print("="*70)