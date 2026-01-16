"""
======================================================================
PHASE 4: H4 HETEROGENEITY ANALYSIS
======================================================================
Purpose: Test if flood effects on deposits vary by:
  - Rural vs urban districts
  - High vs low flood exposure
  - Monsoon (Q3) vs non-monsoon quarters

Model: deposits_change_qt ~ flood_qt × heterogeneity_dummy + FEs
Date: 2026-01-16
Author: Climate-Migration-Bank-Fragility Research Project
======================================================================
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import ols
import os

print("="*70)
print("PHASE 4: H4 HETEROGENEITY ANALYSIS")
print("="*70)

# ============================================================================
# [1/7] LOAD REGRESSION-READY PANEL
# ============================================================================
print("\n[1/7] Loading regression-ready panel...")
panel_path = "02_Data_Intermediate/master_panel_analysis.csv"
df = pd.read_csv(panel_path)
print(f"  ✓ Loaded: {len(df):,} rows")

# ============================================================================
# [2/7] ENGINEER DEPOSIT CHANGE VARIABLE
# ============================================================================
print("\n[2/7] Engineering deposit change variable...")
df = df.sort_values(['district_gadm', 'state_gadm', 'quarter'])
df['deposits_change_qt'] = df.groupby(['district_gadm', 'state_gadm'])['deposits'].pct_change()
print(f"  ✓ Created deposits_change_qt (quarterly % change)")
print(f"  ✓ Non-missing: {df['deposits_change_qt'].notna().sum():,} ({100*df['deposits_change_qt'].notna().mean():.1f}%)")

# ============================================================================
# [3/7] CREATE HETEROGENEITY DUMMIES
# ============================================================================
print("\n[3/7] Creating heterogeneity dummies...")

# H4a: Rural vs Urban (using median deposits as proxy)
median_deposits = df.groupby('district_gadm')['deposits'].median()
df['is_urban'] = df['district_gadm'].map(lambda x: 1 if median_deposits.get(x, 0) > median_deposits.median() else 0)
print(f"  ✓ Urban districts (proxy): {df.groupby('district_gadm')['is_urban'].first().sum()}")

# H4b: High vs Low Flood Exposure (≥3 floods in sample)
flood_count = df.groupby('district_gadm')['flood_exposure_ruleA_qt'].sum()
df['high_flood_exposure'] = df['district_gadm'].map(lambda x: 1 if flood_count.get(x, 0) >= 3 else 0)
print(f"  ✓ High-exposure districts: {df.groupby('district_gadm')['high_flood_exposure'].first().sum()}")

# H4c: Monsoon Season (Q3 = Jul-Sep)
df['monsoon_quarter'] = (df['q'] == 3).astype(int)
print(f"  ✓ Monsoon quarters: {df['monsoon_quarter'].sum():,} obs ({df['monsoon_quarter'].mean()*100:.1f}%)")

# ============================================================================
# [4/7] CREATE INTERACTION TERMS
# ============================================================================
print("\n[4/7] Creating interaction terms...")
df['flood_x_urban'] = df['flood_exposure_ruleA_qt'] * df['is_urban']
df['flood_x_highexp'] = df['flood_exposure_ruleA_qt'] * df['high_flood_exposure']
df['flood_x_monsoon'] = df['flood_exposure_ruleA_qt'] * df['monsoon_quarter']
print("  ✓ Interactions created")

# ============================================================================
# [5/7] RESTRICT TO COMPLETE CASES
# ============================================================================
print("\n[5/7] Restricting to complete cases...")
print(f"  Initial: {len(df):,} obs")

df_reg = df[['deposits_change_qt', 'flood_exposure_ruleA_qt', 
             'is_urban', 'high_flood_exposure', 'monsoon_quarter',
             'flood_x_urban', 'flood_x_highexp', 'flood_x_monsoon',
             'district_gadm', 'quarter']].dropna()

print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Dropped: {len(df) - len(df_reg):,} obs ({100*(len(df) - len(df_reg))/len(df):.1f}%)")

# ============================================================================
# [6/7] ENCODE FIXED EFFECTS
# ============================================================================
print("\n[6/7] Encoding fixed effects...")
df_reg = pd.get_dummies(df_reg, columns=['district_gadm', 'quarter'], drop_first=True, dtype=float)
print(f"  ✓ District FE: {df_reg.filter(regex='^district_gadm_').shape[1]:,} dummies")
print(f"  ✓ Quarter FE: {df_reg.filter(regex='^quarter_').shape[1]:,} dummies")

# ============================================================================
# [7/7] RUN HETEROGENEITY REGRESSIONS
# ============================================================================
print("\n[7/7] Running heterogeneity regressions...")

# Prepare regressors
X_cols_base = ['flood_exposure_ruleA_qt'] + [c for c in df_reg.columns if c.startswith(('district_', 'quarter_'))]

results = {}
y = df_reg['deposits_change_qt']

# H4a: Urban vs Rural
print("\n  [H4a] Urban vs Rural Heterogeneity...")
X_urban = df_reg[X_cols_base + ['is_urban', 'flood_x_urban']]
model_urban = sm.OLS(y, X_urban).fit()
results['urban'] = {
    'flood_coef': model_urban.params.get('flood_exposure_ruleA_qt', np.nan),
    'interaction_coef': model_urban.params.get('flood_x_urban', np.nan),
    'interaction_se': model_urban.bse.get('flood_x_urban', np.nan),
    'interaction_t': model_urban.tvalues.get('flood_x_urban', np.nan),
    'interaction_p': model_urban.pvalues.get('flood_x_urban', np.nan),
}
print("  ✓ Urban model complete")

# H4b: High vs Low Exposure
print("\n  [H4b] High vs Low Flood Exposure...")
X_exp = df_reg[X_cols_base + ['high_flood_exposure', 'flood_x_highexp']]
model_exp = sm.OLS(y, X_exp).fit()
results['exposure'] = {
    'flood_coef': model_exp.params.get('flood_exposure_ruleA_qt', np.nan),
    'interaction_coef': model_exp.params.get('flood_x_highexp', np.nan),
    'interaction_se': model_exp.bse.get('flood_x_highexp', np.nan),
    'interaction_t': model_exp.tvalues.get('flood_x_highexp', np.nan),
    'interaction_p': model_exp.pvalues.get('flood_x_highexp', np.nan),
}
print("  ✓ Exposure model complete")

# H4c: Monsoon vs Non-monsoon
print("\n  [H4c] Monsoon vs Non-Monsoon Quarters...")
X_mon = df_reg[X_cols_base + ['monsoon_quarter', 'flood_x_monsoon']]
model_mon = sm.OLS(y, X_mon).fit()
results['monsoon'] = {
    'flood_coef': model_mon.params.get('flood_exposure_ruleA_qt', np.nan),
    'interaction_coef': model_mon.params.get('flood_x_monsoon', np.nan),
    'interaction_se': model_mon.bse.get('flood_x_monsoon', np.nan),
    'interaction_t': model_mon.tvalues.get('flood_x_monsoon', np.nan),
    'interaction_p': model_mon.pvalues.get('flood_x_monsoon', np.nan),
}
print("  ✓ Monsoon model complete")

# ============================================================================
# [8/7] DISPLAY RESULTS
# ============================================================================
print("\n[8/7] Extracting results...")
print("\n")
print("  HETEROGENEITY EFFECTS (Floods → Deposits):")
print("\n")

# H4a: Urban
print("  [H4a] URBAN vs RURAL:")
print(f"    Main effect (rural baseline):  β̂  = {results['urban']['flood_coef']:.6f}")
print(f"    Interaction (urban × flood):   β̂  = {results['urban']['interaction_coef']:.6f}")
print(f"                                   SE = {results['urban']['interaction_se']:.6f}")
print(f"                                   t  = {results['urban']['interaction_t']:.3f}")
print(f"                                   p  = {results['urban']['interaction_p']:.4f}")
sig = "*" if results['urban']['interaction_p'] < 0.05 else ("†" if results['urban']['interaction_p'] < 0.10 else "NOT SIGNIFICANT")
print(f"    Significance: {sig}\n")

# H4b: Exposure
print("  [H4b] HIGH vs LOW FLOOD EXPOSURE:")
print(f"    Main effect (low-exp baseline): β̂  = {results['exposure']['flood_coef']:.6f}")
print(f"    Interaction (high-exp × flood): β̂  = {results['exposure']['interaction_coef']:.6f}")
print(f"                                    SE = {results['exposure']['interaction_se']:.6f}")
print(f"                                    t  = {results['exposure']['interaction_t']:.3f}")
print(f"                                    p  = {results['exposure']['interaction_p']:.4f}")
sig = "*" if results['exposure']['interaction_p'] < 0.05 else ("†" if results['exposure']['interaction_p'] < 0.10 else "NOT SIGNIFICANT")
print(f"    Significance: {sig}\n")

# H4c: Monsoon
print("  [H4c] MONSOON vs NON-MONSOON:")
print(f"    Main effect (non-monsoon):     β̂  = {results['monsoon']['flood_coef']:.6f}")
print(f"    Interaction (monsoon × flood): β̂  = {results['monsoon']['interaction_coef']:.6f}")
print(f"                                   SE = {results['monsoon']['interaction_se']:.6f}")
print(f"                                   t  = {results['monsoon']['interaction_t']:.3f}")
print(f"                                   p  = {results['monsoon']['interaction_p']:.4f}")
sig = "*" if results['monsoon']['interaction_p'] < 0.05 else ("†" if results['monsoon']['interaction_p'] < 0.10 else "NOT SIGNIFICANT")
print(f"    Significance: {sig}\n")

# ============================================================================
# [OUTPUT] SAVE RESULTS
# ============================================================================
print("\n[Output] Saving results table...")
output_dir = "05_Outputs/Tables"
os.makedirs(output_dir, exist_ok=True)

results_df = pd.DataFrame({
    'Test': ['H4a: Urban×Flood', 'H4b: HighExp×Flood', 'H4c: Monsoon×Flood'],
    'Baseline_Effect': [results['urban']['flood_coef'], 
                        results['exposure']['flood_coef'],
                        results['monsoon']['flood_coef']],
    'Interaction_Coef': [results['urban']['interaction_coef'],
                         results['exposure']['interaction_coef'],
                         results['monsoon']['interaction_coef']],
    'Interaction_SE': [results['urban']['interaction_se'],
                       results['exposure']['interaction_se'],
                       results['monsoon']['interaction_se']],
    'Interaction_t': [results['urban']['interaction_t'],
                      results['exposure']['interaction_t'],
                      results['monsoon']['interaction_t']],
    'Interaction_p': [results['urban']['interaction_p'],
                      results['exposure']['interaction_p'],
                      results['monsoon']['interaction_p']],
})

output_path = os.path.join(output_dir, "05_H4_heterogeneity.csv")
results_df.to_csv(output_path, index=False)

print(f"  ✓ Saved: {output_path}")

print("\n" + "="*70)
print("H4 HETEROGENEITY ANALYSIS COMPLETE")
print("="*70)
print(f"Table: {output_path}")
print("\nNEXT STEP: Review results → Stop coding for the day!")
print("="*70)