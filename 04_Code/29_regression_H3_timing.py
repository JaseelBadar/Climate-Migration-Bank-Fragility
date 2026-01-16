"""
Script 29: H3 Timing Analysis (Distributed Lags)
Phase 4 - Test timing of flood effects on deposits
"""

import pandas as pd
import numpy as np
from scipy.stats import t as t_dist

print("=" * 70)
print("PHASE 4: H3 TIMING ANALYSIS (Distributed Lags)")
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
# STEP 2: Create lag variables
# ============================================================================
print("[2/6] Creating lag variables...")

# Sort by district and quarter to ensure proper lagging
df = df.sort_values(['district_gadm', 'quarter']).reset_index(drop=True)

# Create lags of flood exposure within each district
df['flood_lag1_qt'] = df.groupby('district_gadm')['flood_exposure_ruleA_qt'].shift(1)
df['flood_lag2_qt'] = df.groupby('district_gadm')['flood_exposure_ruleA_qt'].shift(2)

print(f"  ✓ Created flood_lag1_qt (1 quarter lag)")
print(f"  ✓ Created flood_lag2_qt (2 quarters lag)")
print()

# ============================================================================
# STEP 3: Restrict to complete cases
# ============================================================================
print("[3/6] Restricting to complete cases...")
print(f"  Initial: {len(df):,} obs")

# Keep only obs with all variables non-missing
df_reg = df[[
    'deposit_change_qt',
    'flood_exposure_ruleA_qt',  # t=0 (contemporaneous)
    'flood_lag1_qt',             # t-1 (1 quarter lag)
    'flood_lag2_qt',             # t-2 (2 quarters lag)
    'district_gadm',
    'quarter'
]].dropna()

print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Dropped: {len(df) - len(df_reg):,} obs ({100*(len(df) - len(df_reg))/len(df):.1f}%)")
print()

# ============================================================================
# STEP 4: Encode fixed effects
# ============================================================================
print("[4/6] Encoding fixed effects...")

# Convert to categorical and get dummies
district_dummies = pd.get_dummies(df_reg['district_gadm'], prefix='district', drop_first=True)
quarter_dummies = pd.get_dummies(df_reg['quarter'], prefix='quarter', drop_first=True)

print(f"  ✓ District FE: {district_dummies.shape[1]} dummies")
print(f"  ✓ Quarter FE: {quarter_dummies.shape[1]} dummies")
print()

# ============================================================================
# STEP 5: Run distributed lag regression
# ============================================================================
print("[5/6] Running distributed lag regression...")

# Construct design matrix (contemporaneous + 2 lags + FE)
X = np.column_stack([
    df_reg['flood_exposure_ruleA_qt'].values,  # t=0
    df_reg['flood_lag1_qt'].values,            # t-1
    df_reg['flood_lag2_qt'].values,            # t-2
    district_dummies.values,
    quarter_dummies.values
])

# Ensure float64 dtype
X = X.astype(np.float64)

y = df_reg['deposit_change_qt'].values.astype(np.float64)

# Estimate via OLS
from numpy.linalg import lstsq
beta = lstsq(X, y, rcond=None)[0]

# Calculate residuals for SE
residuals = y - (X @ beta)
sigma2 = np.sum(residuals**2) / (len(y) - X.shape[1])

# Variance-covariance matrix
XtX_inv = np.linalg.inv(X.T @ X)
var_beta = sigma2 * np.diag(XtX_inv)
se_beta = np.sqrt(var_beta)

# Extract coefficients for the 3 flood timing variables
coef_t0 = beta[0]
coef_t1 = beta[1]
coef_t2 = beta[2]

se_t0 = se_beta[0]
se_t1 = se_beta[1]
se_t2 = se_beta[2]

# Calculate t-stats and p-values
df_resid = len(y) - X.shape[1]
t_t0 = coef_t0 / se_t0
t_t1 = coef_t1 / se_t1
t_t2 = coef_t2 / se_t2

p_t0 = 2 * (1 - t_dist.cdf(abs(t_t0), df=df_resid))
p_t1 = 2 * (1 - t_dist.cdf(abs(t_t1), df=df_resid))
p_t2 = 2 * (1 - t_dist.cdf(abs(t_t2), df=df_resid))

print(f"  ✓ Regression complete")
print()

# ============================================================================
# STEP 6: Output results
# ============================================================================
print("[6/6] Extracting results...")
print()
print("  TIMING EFFECTS (Floods -> Deposits):")
print()
print(f"  [t=0] Contemporaneous:")
print(f"    β̂  = {coef_t0:.6f}")
print(f"    SE = {se_t0:.6f}")
print(f"    t  = {t_t0:.3f}")
print(f"    p  = {p_t0:.4f}")

if p_t0 < 0.001:
    sig_t0 = '***'
elif p_t0 < 0.01:
    sig_t0 = '**'
elif p_t0 < 0.05:
    sig_t0 = '*'
else:
    sig_t0 = ''

print(f"    Significance: {sig_t0 if sig_t0 else 'NOT SIGNIFICANT'}")
print()

print(f"  [t-1] 1 Quarter Lag:")
print(f"    β̂  = {coef_t1:.6f}")
print(f"    SE = {se_t1:.6f}")
print(f"    t  = {t_t1:.3f}")
print(f"    p  = {p_t1:.4f}")

if p_t1 < 0.001:
    sig_t1 = '***'
elif p_t1 < 0.01:
    sig_t1 = '**'
elif p_t1 < 0.05:
    sig_t1 = '*'
else:
    sig_t1 = ''

print(f"    Significance: {sig_t1 if sig_t1 else 'NOT SIGNIFICANT'}")
print()

print(f"  [t-2] 2 Quarter Lag:")
print(f"    β̂  = {coef_t2:.6f}")
print(f"    SE = {se_t2:.6f}")
print(f"    t  = {t_t2:.3f}")
print(f"    p  = {p_t2:.4f}")

if p_t2 < 0.001:
    sig_t2 = '***'
elif p_t2 < 0.01:
    sig_t2 = '**'
elif p_t2 < 0.05:
    sig_t2 = '*'
else:
    sig_t2 = ''

print(f"    Significance: {sig_t2 if sig_t2 else 'NOT SIGNIFICANT'}")
print()

# Calculate cumulative effect
cumulative = coef_t0 + coef_t1 + coef_t2
print(f"  [CUMULATIVE] Sum of coefficients: {cumulative:.6f}")
print()

# Save results table
results = pd.DataFrame({
    'Variable': ['flood_t0', 'flood_t1_lag', 'flood_t2_lag'],
    'Coefficient': [coef_t0, coef_t1, coef_t2],
    'Std_Error': [se_t0, se_t1, se_t2],
    't_statistic': [t_t0, t_t1, t_t2],
    'p_value': [p_t0, p_t1, p_t2],
    'N_obs': [len(y), len(y), len(y)]
})

results.to_csv('05_Outputs/Tables/04_H3_timing.csv', index=False)

# Save log
with open('05_Outputs/Logs/29_H3_timing.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("H3: TIMING ANALYSIS (Distributed Lags)\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"N observations: {len(y):,}\n")
    f.write(f"District FE: {district_dummies.shape[1]}\n")
    f.write(f"Quarter FE: {quarter_dummies.shape[1]}\n\n")
    f.write("TIMING EFFECTS:\n\n")
    f.write(f"[t=0] Contemporaneous flood:\n")
    f.write(f"  Coefficient: {coef_t0:.6f} {sig_t0}\n")
    f.write(f"  Std Error: {se_t0:.6f}\n")
    f.write(f"  t-statistic: {t_t0:.3f}\n")
    f.write(f"  p-value: {p_t0:.4f}\n\n")
    f.write(f"[t-1] 1 Quarter Lag:\n")
    f.write(f"  Coefficient: {coef_t1:.6f} {sig_t1}\n")
    f.write(f"  Std Error: {se_t1:.6f}\n")
    f.write(f"  t-statistic: {t_t1:.3f}\n")
    f.write(f"  p-value: {p_t1:.4f}\n\n")
    f.write(f"[t-2] 2 Quarter Lag:\n")
    f.write(f"  Coefficient: {coef_t2:.6f} {sig_t2}\n")
    f.write(f"  Std Error: {se_t2:.6f}\n")
    f.write(f"  t-statistic: {t_t2:.3f}\n")
    f.write(f"  p-value: {p_t2:.4f}\n\n")
    f.write(f"Cumulative effect: {cumulative:.6f}\n")

print("[Output] Saving regression table...")
print("=" * 70)
print("H3 TIMING ANALYSIS COMPLETE")
print("=" * 70)
print(f"Table: 05_Outputs/Tables/04_H3_timing.csv")
print(f"Log:   05_Outputs/Logs/29_H3_timing.txt")
print("=" * 70)
print()
print("NEXT STEP: Run Script 30 (H4: Heterogeneity analysis)")
print("=" * 70)