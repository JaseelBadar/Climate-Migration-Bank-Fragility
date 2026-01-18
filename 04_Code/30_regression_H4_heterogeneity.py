"""
Script 30: H4 Heterogeneity Tests (Interaction Effects) WITH CLUSTERING
Phase 4 - Test differential effects by urban/rural, exposure level, season
"""

import pandas as pd
import numpy as np
from scipy.stats import t as t_dist

print("=" * 70)
print("PHASE 4: H4 HETEROGENEITY (Interaction Effects)")
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
print("[1/7] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
print(f"  ✓ Loaded: {len(df):,} rows")
print()

# ============================================================================
# STEP 2: Engineer heterogeneity variables
# ============================================================================
print("[2/7] Engineering heterogeneity variables...")

# H4a: Urban indicator (if district is in top 50% by log_lights)
df_district_lights = df.groupby('district_gadm')['log_lights_qt'].mean().reset_index()
df_district_lights['urban'] = (df_district_lights['log_lights_qt'] > 
                                df_district_lights['log_lights_qt'].median()).astype(int)
df = df.merge(df_district_lights[['district_gadm', 'urban']], on='district_gadm', how='left')

# H4b: High exposure indicator (if district is in top 50% by cumulative flood exposure)
df_district_exposure = df.groupby('district_gadm')['flood_exposure_ruleA_qt'].sum().reset_index()
df_district_exposure.columns = ['district_gadm', 'cum_exposure']
df_district_exposure['high_exposure'] = (df_district_exposure['cum_exposure'] > 
                                         df_district_exposure['cum_exposure'].median()).astype(int)
df = df.merge(df_district_exposure[['district_gadm', 'high_exposure']], on='district_gadm', how='left')

# H4c: Monsoon season indicator (Q3 = Jul-Sep)
# Quarter is stored as "2015Q1", "2015Q2", etc.
# Extract the quarter number (last character) and check if it's 3
df['q_num'] = df['quarter'].str[-1].astype(int)  # Extract "3" from "2015Q3"
df['monsoon'] = (df['q_num'] == 3).astype(int)   # Q3 = monsoon season

print(f"  ✓ Created urban indicator (based on median nighttime lights)")
print(f"  ✓ Created high_exposure indicator (based on median cumulative floods)")
print(f"  ✓ Created monsoon indicator (Q3 = Jul-Sep monsoon season)")
print()

# ============================================================================
# STEP 3: Restrict to complete cases AND preserve district_ids
# ============================================================================
print("[3/7] Restricting to complete cases...")
print(f"  Initial: {len(df):,} obs")

required_cols = ['deposit_change_qt', 'flood_exposure_ruleA_qt', 'urban', 
                 'high_exposure', 'monsoon', 'district_gadm', 'quarter']
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
print("[4/7] Encoding fixed effects...")

district_dummies = pd.get_dummies(df_reg['district_gadm'], prefix='district', drop_first=True)
quarter_dummies = pd.get_dummies(df_reg['quarter'], prefix='quarter', drop_first=True)

print(f"  ✓ District FE: {district_dummies.shape[1]} dummies")
print(f"  ✓ Quarter FE: {quarter_dummies.shape[1]} dummies")
print()

# ============================================================================
# STEP 5: Run H4a (Urban × Flood)
# ============================================================================
print("[5/7] H4a: Urban × Flood Interaction")

y = df_reg['deposit_change_qt'].values
X_h4a = np.column_stack([
    np.ones(len(y)),
    df_reg['flood_exposure_ruleA_qt'].values,
    df_reg['urban'].values * df_reg['flood_exposure_ruleA_qt'].values,  # Interaction
    district_dummies.values,
    quarter_dummies.values
])

beta_h4a = np.linalg.lstsq(X_h4a, y, rcond=None)[0]
residuals_h4a = y - (X_h4a @ beta_h4a)
vcov_h4a = cluster_robust_vcov(X_h4a, residuals_h4a, district_ids)
se_h4a = np.sqrt(np.diag(vcov_h4a))

baseline_h4a = beta_h4a[1]
interaction_h4a = beta_h4a[2]
se_baseline_h4a = se_h4a[1]
se_interaction_h4a = se_h4a[2]
t_h4a = interaction_h4a / se_interaction_h4a
p_h4a = 2 * (1 - t_dist.cdf(abs(t_h4a), df=len(y) - X_h4a.shape[1]))

sig_h4a = '***' if p_h4a < 0.01 else ('**' if p_h4a < 0.05 else ('*' if p_h4a < 0.10 else ''))

print(f"  Baseline (rural): {baseline_h4a:.6f} (SE: {se_baseline_h4a:.6f})")
print(f"  Interaction coef: {interaction_h4a:.6f}")
print(f"  Clustered SE: {se_interaction_h4a:.6f}")
print(f"  t-stat: {t_h4a:.3f}")
print(f"  p-value: {p_h4a:.6f}")
print(f"  Significance: {sig_h4a if sig_h4a else 'NOT SIGNIFICANT'}")
print()

# ============================================================================
# STEP 6: Run H4b (HighExp × Flood)
# ============================================================================
print("[6/7] H4b: HighExp × Flood Interaction")

X_h4b = np.column_stack([
    np.ones(len(y)),
    df_reg['flood_exposure_ruleA_qt'].values,
    df_reg['high_exposure'].values * df_reg['flood_exposure_ruleA_qt'].values,
    district_dummies.values,
    quarter_dummies.values
])

beta_h4b = np.linalg.lstsq(X_h4b, y, rcond=None)[0]
residuals_h4b = y - (X_h4b @ beta_h4b)
vcov_h4b = cluster_robust_vcov(X_h4b, residuals_h4b, district_ids)
se_h4b = np.sqrt(np.diag(vcov_h4b))

baseline_h4b = beta_h4b[1]
interaction_h4b = beta_h4b[2]
se_baseline_h4b = se_h4b[1]
se_interaction_h4b = se_h4b[2]
t_h4b = interaction_h4b / se_interaction_h4b
p_h4b = 2 * (1 - t_dist.cdf(abs(t_h4b), df=len(y) - X_h4b.shape[1]))

sig_h4b = '***' if p_h4b < 0.01 else ('**' if p_h4b < 0.05 else ('*' if p_h4b < 0.10 else ''))

print(f"  Baseline (low exp): {baseline_h4b:.6f} (SE: {se_baseline_h4b:.6f})")
print(f"  Interaction coef: {interaction_h4b:.6f}")
print(f"  Clustered SE: {se_interaction_h4b:.6f}")
print(f"  t-stat: {t_h4b:.3f}")
print(f"  p-value: {p_h4b:.6f}")
print(f"  Significance: {sig_h4b if sig_h4b else 'NOT SIGNIFICANT'}")
print()

# ============================================================================
# STEP 7: Run H4c (Monsoon × Flood)
# ============================================================================
print("[7/7] H4c: Monsoon × Flood Interaction")

X_h4c = np.column_stack([
    np.ones(len(y)),
    df_reg['flood_exposure_ruleA_qt'].values,
    df_reg['monsoon'].values * df_reg['flood_exposure_ruleA_qt'].values,
    district_dummies.values,
    quarter_dummies.values
])

beta_h4c = np.linalg.lstsq(X_h4c, y, rcond=None)[0]
residuals_h4c = y - (X_h4c @ beta_h4c)
vcov_h4c = cluster_robust_vcov(X_h4c, residuals_h4c, district_ids)
se_h4c = np.sqrt(np.diag(vcov_h4c))

baseline_h4c = beta_h4c[1]
interaction_h4c = beta_h4c[2]
se_baseline_h4c = se_h4c[1]
se_interaction_h4c = se_h4c[2]
t_h4c = interaction_h4c / se_interaction_h4c
p_h4c = 2 * (1 - t_dist.cdf(abs(t_h4c), df=len(y) - X_h4c.shape[1]))

sig_h4c = '***' if p_h4c < 0.01 else ('**' if p_h4c < 0.05 else ('*' if p_h4c < 0.10 else ''))

print(f"  Baseline (non-monsoon): {baseline_h4c:.6f} (SE: {se_baseline_h4c:.6f})")
print(f"  Interaction coef: {interaction_h4c:.6f}")
print(f"  Clustered SE: {se_interaction_h4c:.6f}")
print(f"  t-stat: {t_h4c:.3f}")
print(f"  p-value: {p_h4c:.6f}")
print(f"  Significance: {sig_h4c if sig_h4c else 'NOT SIGNIFICANT'}")
print()

# ============================================================================
# STEP 8: Output results (CSV with CLUSTERED SEs)
# ============================================================================
print("[Output] Saving outputs...")

results = pd.DataFrame({
    'Test': ['H4a: Urban×Flood', 'H4b: HighExp×Flood', 'H4c: Monsoon×Flood'],
    'Baseline_Effect': [baseline_h4a, baseline_h4b, baseline_h4c],
    'Baseline_SE': [se_baseline_h4a, se_baseline_h4b, se_baseline_h4c],
    'Interaction_Coef': [interaction_h4a, interaction_h4b, interaction_h4c],
    'Interaction_SE': [se_interaction_h4a, se_interaction_h4b, se_interaction_h4c],
    'Interaction_t': [t_h4a, t_h4b, t_h4c],
    'Interaction_p': [p_h4a, p_h4b, p_h4c],
    'N_obs': [len(y), len(y), len(y)]
})

results.to_csv('05_Outputs/Tables/05_H4_heterogeneity.csv', index=False)

# Save detailed log
with open('05_Outputs/Logs/30_H4_heterogeneity.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("H4: HETEROGENEITY TESTS (District-Clustered SEs)\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("[H4a: Urban × Flood]\n")
    f.write(f"  Baseline (rural): {baseline_h4a:.6f} (SE: {se_baseline_h4a:.6f})\n")
    f.write(f"  Interaction: {interaction_h4a:.6f}\n")
    f.write(f"  SE: {se_interaction_h4a:.6f} (clustered)\n")
    f.write(f"  t: {t_h4a:.3f}\n")
    f.write(f"  p: {p_h4a:.6f}\n")
    f.write(f"  Sig: {sig_h4a if sig_h4a else 'NOT SIGNIFICANT'}\n\n")
    
    f.write("[H4b: HighExp × Flood]\n")
    f.write(f"  Baseline (low exp): {baseline_h4b:.6f} (SE: {se_baseline_h4b:.6f})\n")
    f.write(f"  Interaction: {interaction_h4b:.6f}\n")
    f.write(f"  SE: {se_interaction_h4b:.6f} (clustered)\n")
    f.write(f"  t: {t_h4b:.3f}\n")
    f.write(f"  p: {p_h4b:.6f}\n")
    f.write(f"  Sig: {sig_h4b if sig_h4b else 'NOT SIGNIFICANT'}\n\n")
    
    f.write("[H4c: Monsoon × Flood]\n")
    f.write(f"  Baseline (non-monsoon): {baseline_h4c:.6f} (SE: {se_baseline_h4c:.6f})\n")
    f.write(f"  Interaction: {interaction_h4c:.6f}\n")
    f.write(f"  SE: {se_interaction_h4c:.6f} (clustered)\n")
    f.write(f"  t: {t_h4c:.3f}\n")
    f.write(f"  p: {p_h4c:.6f}\n")
    f.write(f"  Sig: {sig_h4c if sig_h4c else 'NOT SIGNIFICANT'}\n\n")
    
    f.write(f"N = {len(y):,}\n")
    f.write(f"Districts: {len(np.unique(district_ids))} clusters\n")

print(f"  Districts: {len(np.unique(district_ids))} clusters")
print(f"  Observations: {len(y):,}")
print()
print(f"Table: 05_Outputs/Tables/05_H4_heterogeneity.csv")
print(f"Log:   05_Outputs/Logs/30_H4_heterogeneity.txt")
print()
print("✓ Script 30 complete (with district-clustered SEs)")