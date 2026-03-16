# =============================================================================
# Script 36b: R6b -- Wild Cluster Bootstrap SE for H1 at State Level
# Project:    Climate Shocks, Displacement, and Bank Liquidity Risk
#             Evidence from Night-Lights in India, 2015-2024
# PI:         Jaseel Badar, Harvard University
# Purpose:    Re-run H1 with wild cluster bootstrap SE clustered by state_gadm
#             (34 clusters) to resolve R6 partial failure.
#             Cameron and Miller (2015): below 50 clusters, conventional
#             clustered SEs may be liberal. Script 36 found H1 p = 0.105
#             at 34 state clusters using conventional clustered SEs.
#             Wild bootstrap with Rademacher weights corrects for low
#             cluster count and provides the most defensible SE estimate
#             for H1 at state level.
# Input:      03_Data_Clean/regression_panel_final.csv  (23,347 x 23)
# Outputs:    05_Outputs/Tables/16_H1_wildbootstrap.csv
#             05_Outputs/Logs/36b_wildbootstrap_log.txt
# Method:     Wild cluster bootstrap, Rademacher weights, B = 999
#             OLS with full district + quarter dummies (same as Script 27)
#             Cluster variable: state_gadm (34 clusters)
#             Rule A primary. Rule B reported.
# Reference:  Cameron, A.C. and Miller, D.L. (2015). "A Practitioner's
#             Guide to Cluster-Robust Inference." Journal of Human
#             Resources, 50(2), 317-372.
# Anchor:     H1 main (Script 27):
#               Rule A: beta = -0.0445, SE = 0.0078, t = -5.708, p < 0.001
#               Rule B: beta = -0.0584, SE = 0.0198, t = -2.954, p = 0.003
#             H1 state-cluster (Script 36):
#               Rule A: beta = -0.044468, SE = 0.0274, t = -1.622, p = 0.105
#               Rule B: beta = -0.058446, SE = 0.0468, t = -1.249, p = 0.212
# Created:    2026-03-16
# =============================================================================

import os
import time
import numpy as np
import pandas as pd
from datetime import datetime

# =============================================================================
# [1/9] SETUP AND PATHS
# =============================================================================

BASE_DIR   = r"E:\Climate-Migration-Bank-Fragility"
CLEAN_DIR  = os.path.join(BASE_DIR, "03_Data_Clean")
TABLE_DIR  = os.path.join(BASE_DIR, "05_Outputs", "Tables")
LOG_DIR    = os.path.join(BASE_DIR, "05_Outputs", "Logs")

INPUT_FILE = os.path.join(CLEAN_DIR, "regression_panel_final.csv")
OUTPUT_CSV = os.path.join(TABLE_DIR, "16_H1_wildbootstrap.csv")
OUTPUT_LOG = os.path.join(LOG_DIR,   "36b_wildbootstrap_log.txt")

SEED   = 42
B      = 999
ALPHA  = 0.05

np.random.seed(SEED)
script_start = time.time()
run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

log_lines = []

def log(msg=""):
    print(msg)
    log_lines.append(msg)

log("=" * 70)
log("Script 36b: R6b Wild Cluster Bootstrap -- H1 State-Level SE")
log(f"Run timestamp: {run_ts}")
log(f"Bootstrap iterations (B): {B}")
log(f"Random seed: {SEED}")
log(f"Cluster variable: state_gadm (34 clusters, GADM encoding)")
log(f"Reference: Cameron and Miller (2015), JHR 50(2)")
log("=" * 70)

# =============================================================================
# [2/9] LOAD AND VALIDATE DATA
# =============================================================================

log("\n[2/9] Loading data")

df = pd.read_csv(INPUT_FILE)
log(f"  Rows loaded:    {len(df):,}")
log(f"  Columns loaded: {len(df.columns)}")
log(f"  Columns:        {list(df.columns)}")

# These are the columns that must exist in the CSV.
# district_state_id and quarter_fe are COMPUTED BELOW -- not stored in CSV.
required_cols = [
    "lights_change_qt",
    "flood_exposure_ruleA_qt",
    "flood_exposure_ruleB_qt",
    "district_gadm",
    "state_gadm",
    "year",
    "quarter"
]
missing = [c for c in required_cols if c not in df.columns]
assert len(missing) == 0, (
    f"Missing required columns: {missing}. "
    f"Available columns: {list(df.columns)}"
)
log(f"  Required columns: all present -- PASS")

# =============================================================================
# [3/9] COMPUTE DERIVED IDENTIFIERS
# =============================================================================

log("\n[3/9] Computing derived identifiers")

# district_state_id: composite key to prevent homonymous district collapse.
# Same construction as Scripts 27-30 and Script 36.
df["district_state_id"] = (
    df["district_gadm"].astype(str) + "_" + df["state_gadm"].astype(str)
)

# quarter_fe: 'quarter' column already stores full strings e.g. '2015Q1'.
# Use directly. No reconstruction needed.
df["quarter_fe"] = df["quarter"].astype(str)

n_states = df["state_gadm"].nunique()
assert n_states == 34, (
    f"Expected 34 state_gadm clusters (28 states + 6 UTs, GADM encoding). "
    f"Got {n_states}. Check state_gadm column."
)
log(f"  district_state_id: constructed ({df['district_state_id'].nunique()} unique)")
log(f"  quarter_fe:        from 'quarter' column ({df['quarter_fe'].nunique()} unique)")
log(f"  Sample quarter_fe values: {sorted(df['quarter_fe'].unique())[:4]}")
log(f"  state_gadm:        {n_states} clusters (28 states + 6 UTs, GADM) -- PASS")

# =============================================================================
# [4/9] PREPARE H1 SAMPLE
# =============================================================================

log("\n[4/9] Preparing H1 sample")

# H1 outcome: lights_change_qt (quarterly change in log lights).
# Exactly 631 NaN -- one per district, first quarter has no prior period.
# This matches Script 27 (N = 22,716) and Script 36 (N = 22,716) exactly.

df_h1 = df.dropna(subset=["lights_change_qt", "flood_exposure_ruleA_qt"]).copy()
df_h1 = df_h1.reset_index(drop=True)

n_h1 = len(df_h1)
assert n_h1 == 22716, (
    f"H1 sample size mismatch. Expected 22,716. Got {n_h1}. "
    f"23,347 - 631 (one NaN per district) = 22,716. "
    f"Verify lights_change_qt NaN structure matches Script 27."
)
log(f"  H1 sample (Rule A): N = {n_h1:,} -- PASS")
log(f"  (23,347 total - 631 first-quarter NaN = 22,716)")
log(f"  State clusters in H1 sample: {df_h1['state_gadm'].nunique()}")
log(f"  District FE in H1 sample:    {df_h1['district_state_id'].nunique()}")
log(f"  Quarter FE in H1 sample:     {df_h1['quarter_fe'].nunique()}")

# =============================================================================
# [5/9] DEFINE WILD BOOTSTRAP FUNCTION
# =============================================================================

log("\n[5/9] Defining wild cluster bootstrap (Rademacher weights)")
log("  Rademacher: P(w = +1) = P(w = -1) = 0.5 per cluster.")
log("  H0 imposed via restricted residuals (treatment coef = 0).")
log("  p-value: proportion of |t_b*| >= |t_obs| across B iterations.")
log("  SE_wb: std of bootstrap beta distribution (B = 999).")

def wild_cluster_bootstrap(y, X, cluster_ids, b_index, B=999, seed=42):
    """
    Wild cluster bootstrap with Rademacher weights.

    Parameters
    ----------
    y           : np.ndarray (n,)  outcome vector
    X           : np.ndarray (n,k) regressors (intercept + treatment + FE dummies)
    cluster_ids : np.ndarray (n,)  cluster membership (state_gadm values)
    b_index     : int              column index of treatment variable in X
    B           : int              bootstrap iterations
    seed        : int              random seed

    Returns
    -------
    beta_obs    : float   OLS point estimate (treatment)
    t_obs       : float   observed t-statistic (conventional clustered SE)
    se_conv     : float   conventional clustered SE (for reference)
    p_wb        : float   wild bootstrap p-value (two-tailed)
    se_wb       : float   bootstrap SE (std of bootstrap beta distribution)
    bs_betas    : array   bootstrap beta point estimates (length B)
    bs_t_dist   : array   bootstrap t-distribution (length B)
    """
    rng = np.random.default_rng(seed)
    n   = len(y)
    k   = X.shape[1]

    clusters = np.unique(cluster_ids)
    G        = len(clusters)
    df_res   = n - k

    # --- OLS on observed data ---
    XtX     = X.T @ X
    XtX_inv = np.linalg.inv(XtX)
    beta    = XtX_inv @ (X.T @ y)
    yhat    = X @ beta
    resid   = y - yhat
    beta_obs = beta[b_index]

    # --- Conventional clustered SE (for t_obs reference) ---
    small_samp = (G / (G - 1)) * ((n - 1) / df_res)
    meat = np.zeros((k, k))
    for g in clusters:
        mask  = cluster_ids == g
        Xg    = X[mask]
        eg    = resid[mask]
        score = Xg.T @ eg
        meat += np.outer(score, score)
    V_conv   = small_samp * XtX_inv @ meat @ XtX_inv
    se_conv  = np.sqrt(np.diag(V_conv))[b_index]
    t_obs    = beta_obs / se_conv

    # --- Restricted residuals: regress y on X excluding b_index ---
    # Impose H0: coefficient on treatment = 0.
    X_r       = np.delete(X, b_index, axis=1)
    XtX_r_inv = np.linalg.inv(X_r.T @ X_r)
    beta_r    = XtX_r_inv @ (X_r.T @ y)
    resid_r   = y - X_r @ beta_r

    # --- Bootstrap loop ---
    bs_betas  = np.empty(B)
    bs_t_dist = np.empty(B)

    for b in range(B):
        # Rademacher draw: one weight per cluster, broadcast to observations
        w_cluster = rng.choice([-1.0, 1.0], size=G)
        w_obs     = np.empty(n)
        for i, g in enumerate(clusters):
            w_obs[cluster_ids == g] = w_cluster[i]

        # Bootstrap outcome
        y_star    = X_r @ beta_r + w_obs * resid_r

        # OLS on bootstrap sample
        beta_star   = XtX_inv @ (X.T @ y_star)
        resid_star  = y_star - X @ beta_star
        bs_betas[b] = beta_star[b_index]

        # Clustered SE for bootstrap sample
        meat_star = np.zeros((k, k))
        for i, g in enumerate(clusters):
            mask   = cluster_ids == g
            Xg     = X[mask]
            eg     = resid_star[mask]
            score  = Xg.T @ eg
            meat_star += np.outer(score, score)
        V_star        = small_samp * XtX_inv @ meat_star @ XtX_inv
        se_star       = np.sqrt(np.diag(V_star))[b_index]
        # Bootstrap t: centered at 0 (H0 imposed on restricted residuals)
        bs_t_dist[b] = beta_star[b_index] / se_star

    # Two-tailed p-value
    p_wb = np.mean(np.abs(bs_t_dist) >= np.abs(t_obs))
    se_wb = np.std(bs_betas)

    return beta_obs, t_obs, se_conv, p_wb, se_wb, bs_betas, bs_t_dist

# =============================================================================
# [6/9] BUILD REGRESSOR MATRIX
# =============================================================================

log("\n[6/9] Building regressor matrix")
log("  Formula: lights_change_qt ~ flood_exposure_ruleX_qt")
log("           + C(district_state_id) + C(quarter_fe)")
log("  Identical formula to Scripts 27 and 36.")

def build_X(df_sub, treatment_col):
    """
    Construct OLS design matrix: intercept + treatment + district FE + quarter FE.
    Dummies re-encoded per-subset to avoid empty Categorical level contamination.
    Returns X (np.ndarray, float64) and column index of treatment variable.
    """
    df_sub = df_sub.reset_index(drop=True)
    treat  = df_sub[[treatment_col]].astype(float)

    # Re-encode dummies per-subset
    dist_d = pd.get_dummies(
        df_sub["district_state_id"].astype(str), drop_first=True, dtype=float
    )
    qtr_d  = pd.get_dummies(
        df_sub["quarter_fe"].astype(str), drop_first=True, dtype=float
    )

    const  = pd.DataFrame({"const": np.ones(len(df_sub))})
    X_df   = pd.concat([const, treat, dist_d, qtr_d], axis=1)
    X      = X_df.values.astype(float)
    # treatment is always at index 1
    return X, 1, X_df.columns.tolist()

# =============================================================================
# [7/9] RUN WILD BOOTSTRAP -- RULE A AND RULE B
# =============================================================================

def run_rule(df_full, treatment_col, rule_label, anchor_beta,
             anchor_se_main, anchor_p_main,
             anchor_beta_36, anchor_se_36, anchor_p_36):

    log(f"\n  --- Rule {rule_label} ---")
    log(f"  Anchor Script 27: beta = {anchor_beta:.6f}, "
        f"SE = {anchor_se_main:.4f}, p < {anchor_p_main}")
    log(f"  Anchor Script 36: beta = {anchor_beta_36:.6f}, "
        f"SE = {anchor_se_36:.4f}, p = {anchor_p_36:.3f}")

    df_sub = df_full.dropna(
        subset=["lights_change_qt", treatment_col]
    ).copy().reset_index(drop=True)

    n_sub = len(df_sub)
    assert n_sub == 22716, (
        f"Rule {rule_label} sample mismatch. Expected 22,716. Got {n_sub}. "
        f"Verify {treatment_col} has no additional NaN beyond lights_change_qt."
    )
    log(f"  N = {n_sub:,} -- PASS")

    y           = df_sub["lights_change_qt"].values.astype(float)
    X, b_idx, _ = build_X(df_sub, treatment_col)
    cluster_ids = df_sub["state_gadm"].values

    log(f"  X shape: {X.shape} | State clusters: {len(np.unique(cluster_ids))}")
    log(f"  Running {B} bootstrap iterations...")

    t0 = time.time()
    beta_obs, t_obs, se_conv, p_wb, se_wb, bs_betas, bs_t = (
        wild_cluster_bootstrap(y, X, cluster_ids, b_idx, B=B, seed=SEED)
    )
    elapsed = time.time() - t0

    def stars(p):
        if p < 0.001: return "***"
        if p < 0.01:  return "**"
        if p < 0.05:  return "*"
        if p < 0.10:  return "+"
        return ""

    log(f"  Completed in {elapsed:.1f}s")
    log(f"  beta (OLS):           {beta_obs:.6f}")
    log(f"  SE (conv clustered):  {se_conv:.6f}  [Script 36 reference]")
    log(f"  t_obs:                {t_obs:.4f}")
    log(f"  SE (wild bootstrap):  {se_wb:.6f}")
    log(f"  p  (wild bootstrap):  {p_wb:.4f}  {stars(p_wb)}")

    if p_wb < ALPHA:
        verdict = (
            f"ROBUST. H1 Rule {rule_label} survives wild cluster bootstrap "
            f"at {len(np.unique(cluster_ids))} state clusters "
            f"(p = {p_wb:.4f} {stars(p_wb)}). "
            f"Cameron and Miller (2015) concern resolved. "
            f"H1 is robust to the most conservative available SE specification."
        )
    else:
        verdict = (
            f"NOT ROBUST. H1 Rule {rule_label} does not survive wild cluster "
            f"bootstrap at {len(np.unique(cluster_ids))} state clusters "
            f"(p = {p_wb:.4f}). Coefficient intact: beta = {beta_obs:.6f}. "
            f"Precision limitation only. Writing constraint 13 applies: "
            f"explicit disclosure required. Do not claim H1 is robust to "
            f"the most conservative SE specification."
        )

    log(f"  VERDICT: {verdict}")

    row = {
        "hypothesis"        : "H1",
        "rule"              : rule_label,
        "outcome"           : "lights_change_qt",
        "treatment"         : treatment_col,
        "method"            : "Wild Cluster Bootstrap (Rademacher)",
        "cluster_var"       : "state_gadm",
        "n_clusters"        : int(len(np.unique(cluster_ids))),
        "n_obs"             : int(n_sub),
        "B_iterations"      : B,
        "seed"              : SEED,
        "beta"              : round(beta_obs, 6),
        "se_conv_script36"  : round(se_conv, 6),
        "t_obs"             : round(t_obs, 4),
        "se_wildboot"       : round(se_wb, 6),
        "p_wildboot"        : round(p_wb, 4),
        "sig_wildboot"      : stars(p_wb),
        "beta_script27"     : anchor_beta,
        "se_script27"       : anchor_se_main,
        "p_script27"        : f"< {anchor_p_main}",
        "beta_script36"     : anchor_beta_36,
        "se_script36"       : anchor_se_36,
        "p_script36"        : anchor_p_36,
        "verdict"           : verdict
    }
    return row

log("\n[7/9] Running wild cluster bootstrap")
log(f"  B = {B} iterations per rule. Runtime: expect 20-60 min total.")

row_a = run_rule(
    df_h1,
    treatment_col    = "flood_exposure_ruleA_qt",
    rule_label       = "A",
    anchor_beta      = -0.044500,
    anchor_se_main   = 0.0078,
    anchor_p_main    = "0.001",
    anchor_beta_36   = -0.044468,
    anchor_se_36     = 0.027400,
    anchor_p_36      = 0.105
)

# Rule B: same lights_change_qt NaN structure, Rule B treatment column
df_h1_b = df.dropna(
    subset=["lights_change_qt", "flood_exposure_ruleB_qt"]
).copy().reset_index(drop=True)

row_b = run_rule(
    df_h1_b,
    treatment_col    = "flood_exposure_ruleB_qt",
    rule_label       = "B",
    anchor_beta      = -0.058400,
    anchor_se_main   = 0.0198,
    anchor_p_main    = "0.003",
    anchor_beta_36   = -0.058446,
    anchor_se_36     = 0.046800,
    anchor_p_36      = 0.212
)

# =============================================================================
# [8/9] SAVE OUTPUTS
# =============================================================================

log("\n[8/9] Saving outputs")

results_df = pd.DataFrame([row_a, row_b])
results_df.to_csv(OUTPUT_CSV, index=False)
assert os.path.exists(OUTPUT_CSV), f"CSV not written: {OUTPUT_CSV}"
log(f"  CSV saved:  {OUTPUT_CSV} -- PASS")

total_elapsed = time.time() - script_start

log("")
log("=" * 70)
log("RESULTS SUMMARY")
log("=" * 70)
log("")
log("H1 Rule A:")
log(f"  beta            = {row_a['beta']:.6f}")
log(f"  SE (wild boot)  = {row_a['se_wildboot']:.6f}")
log(f"  t_obs           = {row_a['t_obs']:.4f}")
log(f"  p (wild boot)   = {row_a['p_wildboot']:.4f}  {row_a['sig_wildboot']}")
log(f"  N = {row_a['n_obs']:,} | State clusters = {row_a['n_clusters']} | B = {B}")
log(f"  VERDICT: {row_a['verdict']}")
log("")
log("H1 Rule B:")
log(f"  beta            = {row_b['beta']:.6f}")
log(f"  SE (wild boot)  = {row_b['se_wildboot']:.6f}")
log(f"  t_obs           = {row_b['t_obs']:.4f}")
log(f"  p (wild boot)   = {row_b['p_wildboot']:.4f}  {row_b['sig_wildboot']}")
log(f"  N = {row_b['n_obs']:,} | State clusters = {row_b['n_clusters']} | B = {B}")
log(f"  VERDICT: {row_b['verdict']}")
log("")
log("SE comparison (Rule A):")
log(f"  District-clustered  (Script 27): SE = 0.0078, p < 0.001 ***")
log(f"  State conv. cluster (Script 36): SE = {row_a['se_conv_script36']:.6f}, "
    f"p = {row_a['p_script36']:.3f}")
log(f"  State wild bootstrap(Script 36b): SE = {row_a['se_wildboot']:.6f}, "
    f"p = {row_a['p_wildboot']:.4f}  {row_a['sig_wildboot']}")
log("")
log(f"Total script runtime: {total_elapsed:.1f}s")
log(f"Run timestamp:        {run_ts}")
log("=" * 70)

with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
assert os.path.exists(OUTPUT_LOG), f"Log not written: {OUTPUT_LOG}"
log(f"\n  Log saved: {OUTPUT_LOG} -- PASS")

# =============================================================================
# [9/9] COMPLETE
# =============================================================================

log("\n[9/9] COMPLETE")
log(f"  Outputs:")
log(f"    {OUTPUT_CSV}")
log(f"    {OUTPUT_LOG}")
log(f"  Runtime: {total_elapsed:.1f}s")
log("")
log("  Writing constraint 13 status: see VERDICT lines above.")
log("  Next step: Scripts 27b-30b (linearmodels PanelOLS final tables).")
log("=" * 70)
