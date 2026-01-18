"""
Script 29: H3 Timing Effects Regression (Flood Lags -> Deposits) WITH CLUSTERING
Phase 4 - Test immediate vs. lagged effects with district-clustered standard errors
"""

import pandas as pd
import numpy as np
from scipy.stats import t as t_dist

print("=" * 70)
print("PHASE 4: H3 TIMING EFFECTS (Flood Lags -> Deposits)")
print("=" * 70)
print()

# ============================================================================
# CLUSTERING FUNCTION
# ============================================================================
def cluster_robust_vcov(X, residuals, cluster_ids):
    """
    Calculate cluster-robust variance-covariance matrix.
    
    Parameters:
    -----------
    X : np.array (n x k)
        Design matrix including intercept
    residuals : np.array (n x 1)
        Regression residuals
    cluster_ids : np.array (n x 1)
        Cluster identifiers (e.g., district codes)
    
    Returns:
    --------
    vcov : np.array (k x k)
        Cluster-robust variance-covariance matrix
    """
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    
    unique_clusters = np.unique(cluster_ids)
    n_clusters = len(unique_clusters)
    
    meat = np.zeros((k, k))
    for cluster in unique_clusters:
        cluster_mask = (cluster_ids == cluster)
        X_c = X[cluster_mask]
        e_c = residuals[cluster_mask].reshape(-1, 1)
        meat += (X_c.T @ e_c) @ (e_c.T @ X_c)
    
    dof_correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    vcov = XtX_inv @ meat @ XtX_inv * dof_correction
    
    return vcov

# ============================================================================
# STEP 1: Load data
# ============================================================================
print("[1/6] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
print()

# ============================================================================
# STEP 2: Create lagged flood variables
# ============================================================================
print("[2/6] Engineering lagged flood variables...")

# Sort by district and quarter to ensure proper ordering
df = df.sort_values(['district_gadm', 'quarter']).reset_index(drop=True)

# Create lags within each district
df['flood_t1_lag'] = df.groupby('district_gadm')['flood_exposure_ruleA_qt'].shift(1)
df['flood_t2_lag'] = df.groupby('district_gadm')['flood_exposure_ruleA_qt'].shift(2)

# Rename current flood to flood_t0 for clarity
df['flood_t0'] = df['flood_exposure_ruleA_qt']

print(f"  ✓ Created flood_t0 (current quarter)")
print(f"  ✓ Created flood_t1_lag (1 quarter lag)")
print(f"  ✓ Created flood_t2_lag (2 quarter lag)")
print()

# ============================================================================
# STEP 3: Restrict to complete cases AND preserve district_ids
# ============================================================================
print("[3/6] Restricting to complete cases...")
print(f"  Initial: {len(df):,} obs")

# Keep only obs with all variables non-missing
required_cols = ['deposit_change_qt', 'flood_t0', 'flood_t1_lag', 'flood_t2_lag',
                 'district_gadm', 'quarter']
df_reg = df[required_cols].dropna().copy()

# Store district_ids BEFORE creating dummies
district_ids = df_reg['district_gadm'].values

print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Districts: {len(np.unique(district_ids))} unique")
print(f"  Dropped: {len(df) - len(df_reg):,} obs ({100*(len(df) - len(df_reg))/len(df):.1f}%)")
print()

# ============================================================================
# STEP 4: Encode fixed effects
# ============================================================================
print("[4/6] Encoding fixed effects...")

district_dummies = pd.get_dummies(df_reg['district_gadm'], prefix='district', drop_first=True)
quarter_dummies = pd.get_dummies(df_reg['quarter'], prefix='quarter', drop_first=True)

print(f"  ✓ District FE: {district_dummies.shape[1]} dummies")
print(f"  ✓ Quarter FE: {quarter_dummies.shape[1]} dummies")
print()

# ============================================================================
# STEP 5: Run regression with all lags simultaneously
# ============================================================================
print("[5/6] Regression: Deposits ~ flood_t0 + flood_t1_lag + flood_t2_lag + FEs")

y = df_reg['deposit_change_qt'].values
X = np.column_stack([
    np.ones(len(y)),
    df_reg['flood_t0'].values,
    df_reg['flood_t1_lag'].values,
    df_reg['flood_t2_lag'].values,
    district_dummies.values,
    quarter_dummies.values
])

# OLS estimation
beta = np.linalg.lstsq(X, y, rcond=None)[0]

# Calculate clustered standard errors
residuals = y - (X @ beta)
vcov_clustered = cluster_robust_vcov(X, residuals, district_ids)
se_clustered = np.sqrt(np.diag(vcov_clustered))

# Extract coefficients and clustered SEs for the 3 flood variables
coef_t0 = beta[1]
coef_t1 = beta[2]
coef_t2 = beta[3]

se_t0 = se_clustered[1]
se_t1 = se_clustered[2]
se_t2 = se_clustered[3]

# Calculate t-stats and p-values using clustered SEs
df_resid = len(y) - X.shape[1]

t_t0 = coef_t0 / se_t0
p_t0 = 2 * (1 - t_dist.cdf(abs(t_t0), df=df_resid))

t_t1 = coef_t1 / se_t1
p_t1 = 2 * (1 - t_dist.cdf(abs(t_t1), df=df_resid))

t_t2 = coef_t2 / se_t2
p_t2 = 2 * (1 - t_dist.cdf(abs(t_t2), df=df_resid))

# Significance stars
sig_t0 = '***' if p_t0 < 0.01 else ('**' if p_t0 < 0.05 else ('*' if p_t0 < 0.10 else ''))
sig_t1 = '***' if p_t1 < 0.01 else ('**' if p_t1 < 0.05 else ('*' if p_t1 < 0.10 else ''))
sig_t2 = '***' if p_t2 < 0.01 else ('**' if p_t2 < 0.05 else ('*' if p_t2 < 0.10 else ''))

print(f"\n[t0] Current Quarter:")
print(f"  Coefficient: {coef_t0:.6f}")
print(f"  Clustered SE: {se_t0:.6f}")
print(f"  t-stat: {t_t0:.3f}")
print(f"  p-value: {p_t0:.6f}")
print(f"  Significance: {sig_t0 if sig_t0 else 'NOT SIGNIFICANT'}")

print(f"\n[t-1] 1 Quarter Lag:")
print(f"  Coefficient: {coef_t1:.6f}")
print(f"  Clustered SE: {se_t1:.6f}")
print(f"  t-stat: {t_t1:.3f}")
print(f"  p-value: {p_t1:.6f}")
print(f"  Significance: {sig_t1 if sig_t1 else 'NOT SIGNIFICANT'}")

print(f"\n[t-2] 2 Quarter Lag:")
print(f"  Coefficient: {coef_t2:.6f}")
print(f"  Clustered SE: {se_t2:.6f}")
print(f"  t-stat: {t_t2:.3f}")
print(f"  p-value: {p_t2:.6f}")
print(f"  Significance: {sig_t2 if sig_t2 else 'NOT SIGNIFICANT'}")
print()

# ============================================================================
# STEP 6: Output results (CSV with CLUSTERED SEs)
# ============================================================================
print("[6/6] Saving outputs...")

# Save CSV with CLUSTERED standard errors
results = pd.DataFrame({
    'Variable': ['flood_t0', 'flood_t1_lag', 'flood_t2_lag'],
    'Coefficient': [coef_t0, coef_t1, coef_t2],
    'Std_Error': [se_t0, se_t1, se_t2],  # <-- CLUSTERED
    't_statistic': [t_t0, t_t1, t_t2],
    'p_value': [p_t0, p_t1, p_t2],
    'N_obs': [len(y), len(y), len(y)]
})

results.to_csv('05_Outputs/Tables/04_H3_timing.csv', index=False)

# Save detailed log
with open('05_Outputs/Logs/29_H3_timing.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("H3: TIMING EFFECTS (District-Clustered SEs)\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("[t0] Current Quarter:\n")
    f.write(f"  β̂  = {coef_t0:.6f}\n")
    f.write(f"  SE = {se_t0:.6f} (clustered)\n")
    f.write(f"  t  = {t_t0:.3f}\n")
    f.write(f"  p  = {p_t0:.6f}\n")
    f.write(f"  Sig: {sig_t0 if sig_t0 else 'NOT SIGNIFICANT'}\n\n")
    
    f.write("[t-1] 1 Quarter Lag:\n")
    f.write(f"  β̂  = {coef_t1:.6f}\n")
    f.write(f"  SE = {se_t1:.6f} (clustered)\n")
    f.write(f"  t  = {t_t1:.3f}\n")
    f.write(f"  p  = {p_t1:.6f}\n")
    f.write(f"  Sig: {sig_t1 if sig_t1 else 'NOT SIGNIFICANT'}\n\n")
    
    f.write("[t-2] 2 Quarter Lag:\n")
    f.write(f"  β̂  = {coef_t2:.6f}\n")
    f.write(f"  SE = {se_t2:.6f} (clustered)\n")
    f.write(f"  t  = {t_t2:.3f}\n")
    f.write(f"  p  = {p_t2:.6f}\n")
    f.write(f"  Sig: {sig_t2 if sig_t2 else 'NOT SIGNIFICANT'}\n\n")
    
    f.write(f"N = {len(y):,}\n")
    f.write(f"Districts: {len(np.unique(district_ids))} clusters\n")

print("[Output] Saving regression table...")
print(f"  Districts: {len(np.unique(district_ids))} clusters")
print(f"  Observations: {len(y):,}")
print()
print(f"Table: 05_Outputs/Tables/04_H3_timing.csv")
print(f"Log:   05_Outputs/Logs/29_H3_timing.txt")
print()
print("✓ Script 29 complete (with district-clustered SEs)")