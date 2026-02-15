"""
Script 28: H2 IV 2SLS Regression (Lights -> Deposits) WITH CLUSTERING
Phase 4 - Two-Stage Least Squares with district-clustered standard errors
"""


import pandas as pd
import numpy as np
from scipy.stats import t as t_dist


print("=" * 70)
print("PHASE 4: H2 IV 2SLS REGRESSION (Lights -> Deposits)")
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
print(f"  Loaded: {len(df):,} rows")
print()


# ============================================================================
# STEP 2: Restrict to complete cases AND preserve district_ids
# ============================================================================
print("[2/6] Restricting to complete cases...")
print(f"  Initial: {len(df):,} obs")


# Keep district_gadm AND state_gadm for composite ID
df_reg = df[['deposit_change_qt', 'lights_change_qt', 'flood_exposure_ruleA_qt',
              'district_gadm', 'state_gadm', 'quarter']].dropna().copy()


# CRITICAL: Create composite district-state ID (prevents homonymous district collapse)
# 7 homonymous pairs exist: Aurangabad, Balrampur, Bijapur, Bilaspur, Hamirpur, Pratapgarh, Raigarh
# Without state, 624 districts collapse to 617 FE (wrong); with state, 624 FE (correct)
df_reg['district_state_id'] = df_reg['district_gadm'] + '_' + df_reg['state_gadm']


# Store composite district_ids for clustering
district_ids = df_reg['district_state_id'].values


print(f"  After restrictions: {len(df_reg):,} obs")
print(f"  Districts: {len(np.unique(district_ids))} unique (composite count)")
print(f"  Dropped: {len(df) - len(df_reg):,} obs ({100*(len(df) - len(df_reg))/len(df):.1f}%)")
print()


# ============================================================================
# STEP 3: Encode fixed effects
# ============================================================================
print("[3/6] Encoding fixed effects...")


# Use composite district-state ID for FE
district_dummies = pd.get_dummies(df_reg['district_state_id'], prefix='district', drop_first=True)
quarter_dummies = pd.get_dummies(df_reg['quarter'], prefix='quarter', drop_first=True)


print(f"  District FE: {district_dummies.shape[1]} dummies (composite district_state_id)")
print(f"  Quarter FE: {quarter_dummies.shape[1]} dummies")
print()


# ============================================================================
# STEP 4: FIRST STAGE (Flood -> Lights)
# ============================================================================
print("[4/6] FIRST STAGE: Flood exposure -> Nighttime lights change")


y_first = df_reg['lights_change_qt'].values
X_first = np.column_stack([
    np.ones(len(y_first)),
    df_reg['flood_exposure_ruleA_qt'].values,
    district_dummies.values,
    quarter_dummies.values
])


beta_first = np.linalg.lstsq(X_first, y_first, rcond=None)[0]
lights_hat = X_first @ beta_first


# Calculate clustered SEs for first stage (using composite district_state_id)
residuals_first = y_first - lights_hat
vcov_first_clustered = cluster_robust_vcov(X_first, residuals_first, district_ids)
se_first_clustered = np.sqrt(np.diag(vcov_first_clustered))


coef_first = beta_first[1]
se_first = se_first_clustered[1]
t_first = coef_first / se_first
p_first = 2 * (1 - t_dist.cdf(abs(t_first), df=len(y_first) - X_first.shape[1]))


print(f"  Coefficient on flood: {coef_first:.6f}")
print(f"  Clustered SE: {se_first:.6f}")
print(f"  t-statistic: {t_first:.3f}")
print(f"  p-value: {p_first:.6f}")
print()


# ============================================================================
# STEP 5: SECOND STAGE (Lights_hat -> Deposits)
# ============================================================================
print("[5/6] SECOND STAGE: Predicted lights -> Deposits change")


y_second = df_reg['deposit_change_qt'].values
X_second = np.column_stack([
    lights_hat,
    district_dummies.values,
    quarter_dummies.values
])


beta_second = np.linalg.lstsq(X_second, y_second, rcond=None)[0]


# Calculate clustered SEs for second stage (using composite district_state_id)
residuals_second = y_second - (X_second @ beta_second)
vcov_second_clustered = cluster_robust_vcov(X_second, residuals_second, district_ids)
se_second_clustered = np.sqrt(np.diag(vcov_second_clustered))


# Extract clustered results for lights_hat coefficient
coef = beta_second[0]
se = se_second_clustered[0]
t_stat = coef / se
p_val = 2 * (1 - t_dist.cdf(abs(t_stat), df=len(y_second) - X_second.shape[1]))


sig = '***' if p_val < 0.01 else ('**' if p_val < 0.05 else ('*' if p_val < 0.10 else None))


print(f"  Coefficient (lights_hat): {coef:.6f}")
print(f"  Clustered SE: {se:.6f}")  
print(f"  t-statistic: {t_stat:.3f}")
print(f"  p-value: {p_val:.6f}")
print(f"  Significance: {sig if sig else 'NOT SIGNIFICANT'}")
print()


# ============================================================================
# STEP 6: Output results (CSV with CLUSTERED SEs)
# ============================================================================
print("[6/6] Saving outputs...")


# Save CSV with CLUSTERED standard errors
results = pd.DataFrame({
    'Variable': ['lights_change_qt_hat'],
    'Coefficient': [coef],
    'Std_Error': [se],
    't_statistic': [t_stat],
    'p_value': [p_val],
    'N_obs': [len(y_second)]
})


results.to_csv('05_Outputs/Tables/03_H2_iv2sls.csv', index=False)


# Save detailed log
with open('05_Outputs/Logs/28_H2_regression.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("H2: IV 2SLS REGRESSION (District-Clustered SEs)\n")
    f.write("Composite district_state_id used for FE and clustering\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("[FIRST STAGE: Flood -> Lights]\n")
    f.write(f"  Beta  = {coef_first:.6f}\n")
    f.write(f"  SE    = {se_first:.6f} (clustered by district_state_id)\n")
    f.write(f"  t     = {t_first:.3f}\n")
    f.write(f"  p     = {p_first:.6f}\n")
    f.write(f"  N     = {len(y_first):,}\n\n")
    
    f.write("[SECOND STAGE: Lights_hat -> Deposits]\n")
    f.write(f"  Beta  = {coef:.6f}\n")
    f.write(f"  SE    = {se:.6f} (clustered by district_state_id)\n")
    f.write(f"  t     = {t_stat:.3f}\n")
    f.write(f"  p     = {p_val:.4f}\n")
    f.write(f"  Significance: {sig if sig else 'NOT SIGNIFICANT'}\n")
    f.write(f"  N     = {len(y_second):,}\n\n")
    
    f.write("[FE SPECIFICATION]\n")
    f.write(f"  District FE: {district_dummies.shape[1]} (composite district_state_id)\n")
    f.write(f"  Quarter FE: {quarter_dummies.shape[1]}\n")
    f.write(f"  Clusters: {len(np.unique(district_ids))}\n")


print("[Output] Saving regression table...")
print(f"  Districts: {len(np.unique(district_ids))} clusters (composite)")
print(f"  Observations: {len(y_second):,}")
print()
print(f"Table: 05_Outputs/Tables/03_H2_iv2sls.csv")
print(f"Log:   05_Outputs/Logs/28_H2_regression.txt")
print()
print("Script 28 complete (with composite district FE and clustering)")