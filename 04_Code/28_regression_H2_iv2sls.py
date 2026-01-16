"""
Script 28: H2 IV 2SLS Regression (Lights -> Deposits)
Phase 4 - Two-Stage Least Squares with flood exposure as instrument
"""

import pandas as pd
import numpy as np
from scipy.stats import t as t_dist

print("=" * 70)
print("PHASE 4: H2 IV 2SLS REGRESSION (Lights -> Deposits)")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Load data
# ============================================================================
print("[1/6] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
print()

# ============================================================================
# STEP 2: Restrict to complete cases
# ============================================================================
print("[2/6] Restricting to complete cases...")
print(f"  Initial: {len(df):,} obs")

# Keep only obs with all variables non-missing
df_reg = df[['deposit_change_qt', 'lights_change_qt', 'flood_exposure_ruleA_qt', 
              'district_gadm', 'quarter']].dropna()

print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Dropped: {len(df) - len(df_reg):,} obs ({100*(len(df) - len(df_reg))/len(df):.1f}%)")
print()

# ============================================================================
# STEP 3: Encode fixed effects
# ============================================================================
print("[3/6] Encoding fixed effects...")

# Convert to categorical and get dummies
district_dummies = pd.get_dummies(df_reg['district_gadm'], prefix='district', drop_first=True)
quarter_dummies = pd.get_dummies(df_reg['quarter'], prefix='quarter', drop_first=True)

print(f"  ✓ District FE: {district_dummies.shape[1]} dummies")
print(f"  ✓ Quarter FE: {quarter_dummies.shape[1]} dummies")
print()

# ============================================================================
# STEP 4: First Stage (Floods -> Lights)
# ============================================================================
print("[4/6] Running First Stage (Floods -> Lights)...")

# Construct design matrix (instrument + FE)
X_first = np.column_stack([
    df_reg['flood_exposure_ruleA_qt'].values,
    district_dummies.values,
    quarter_dummies.values
])

# Ensure float64 dtype
X_first = X_first.astype(np.float64)

y_first = df_reg['lights_change_qt'].values.astype(np.float64)

# Estimate via OLS
from numpy.linalg import lstsq
beta_first = lstsq(X_first, y_first, rcond=None)[0]

# Predicted lights (fitted values)
lights_hat = X_first @ beta_first

print(f"  ✓ First stage complete")
print(f"  ✓ Coefficient on flood_exposure_ruleA_qt: {beta_first[0]:.6f}")
print()

# ============================================================================
# STEP 5: Second Stage (Lights_hat -> Deposits)
# ============================================================================
print("[5/6] Running Second Stage (Lights_hat -> Deposits)...")

# Construct design matrix (fitted lights + FE)
X_second = np.column_stack([
    lights_hat,
    district_dummies.values,
    quarter_dummies.values
])

# Ensure float64 dtype
X_second = X_second.astype(np.float64)

y_second = df_reg['deposit_change_qt'].values.astype(np.float64)

# Estimate via OLS
beta_second = lstsq(X_second, y_second, rcond=None)[0]

# Calculate residuals for SE
residuals = y_second - (X_second @ beta_second)
sigma2 = np.sum(residuals**2) / (len(y_second) - X_second.shape[1])

# Variance-covariance matrix
XtX_inv = np.linalg.inv(X_second.T @ X_second)
var_beta = sigma2 * np.diag(XtX_inv)
se_beta = np.sqrt(var_beta)

# Extract coefficient on lights_hat
coef = beta_second[0]
se = se_beta[0]
t_stat = coef / se
p_val = 2 * (1 - t_dist.cdf(abs(t_stat), df=len(y_second) - X_second.shape[1]))

print(f"  ✓ Second stage complete")
print()

# ============================================================================
# STEP 6: Output results
# ============================================================================
print("[6/6] Extracting results...")
print()
print("  [FIRST STAGE: Floods -> Lights]")
print(f"    β̂  = {beta_first[0]:.6f}")
print()
print("  [SECOND STAGE: Lights_hat -> Deposits]")
print(f"    β̂  = {coef:.6f}")
print(f"    SE = {se:.6f}")
print(f"    t  = {t_stat:.3f}")
print(f"    p  = {p_val:.4f}")

if p_val < 0.001:
    sig = '***'
elif p_val < 0.01:
    sig = '**'
elif p_val < 0.05:
    sig = '*'
else:
    sig = ''

print(f"    Significance: {sig if sig else 'NOT SIGNIFICANT'}")
print()

# Save results table
results = pd.DataFrame({
    'Variable': ['lights_change_qt_hat'],
    'Coefficient': [coef],
    'Std_Error': [se],
    't_statistic': [t_stat],
    'p_value': [p_val],
    'N_obs': [len(y_second)]
})

results.to_csv('05_Outputs/Tables/03_H2_iv2sls.csv', index=False)

# Save log
with open('05_Outputs/Logs/28_H2_regression.txt', 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("H2: IV 2SLS REGRESSION (Migration -> Deposits)\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"N observations: {len(y_second):,}\n")
    f.write(f"District FE: {district_dummies.shape[1]}\n")
    f.write(f"Quarter FE: {quarter_dummies.shape[1]}\n\n")
    f.write("[FIRST STAGE]\n")
    f.write("flood_exposure_ruleA_qt -> lights_change_qt: {:.6f}\n\n".format(beta_first[0]))
    f.write("[SECOND STAGE]\n")
    f.write(f"lights_change_qt_hat -> deposit_change_qt:\n")
    f.write(f"  Coefficient: {coef:.6f} {sig}\n")
    f.write(f"  Std Error: {se:.6f}\n")
    f.write(f"  t-statistic: {t_stat:.3f}\n")
    f.write(f"  p-value: {p_val:.4f}\n")

print("[Output] Saving regression table...")
print("=" * 70)
print("H2 IV 2SLS COMPLETE")
print("=" * 70)
print(f"Table: 05_Outputs/Tables/03_H2_iv2sls.csv")
print(f"Log:   05_Outputs/Logs/28_H2_regression.txt")
print("=" * 70)
print()
print("NEXT STEP: Run Script 29 (H3: Timing effects)")
print("=" * 70)