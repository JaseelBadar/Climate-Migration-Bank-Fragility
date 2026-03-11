"""
35_longer_lags.py
Robustness R5: Longer Lags -- H3 Extension to t-3 and t-4 (Rule B Only)

Purpose:
    Pre-committed persistence check for H3 distributed lag result.
    Extend H3 from t-3 and t-4 to test whether the t-2 effect decays
    (temporary displacement) or persists (permanent loss).

Rule B only: district-level match only (higher precision, lower power).
Rule A has statistical power for longer lags, but Rule B precision is
preferred at deeper lag depth where false positives are more likely.

H3 locked result (Script 29, Rule A):
    t0:  beta = +0.000609, p = 0.677 -- null
    t-1: beta = +0.001505, p = 0.177 -- null
    t-2: beta = -0.007005, p < 0.001 *** CONFIRMED

Specification:
    Quarter FE only (NO district FE). Pre-committed H3 design.
    SE: Clustered by district_state_id.
    Regressors: flood_ruleB_L0 + L1 + L2 + L3 + L4 + C(quarter_fe)

L3 and L4 lag arithmetic asserted exactly:
    L3 NaN = 548 districts x 3 = 1,893
    L4 NaN = 548 districts x 4 = 2,524

Expected result: t-3 and t-4 null. Effect decays at t-2.
Significant t-3/t-4 = evidence of persistence beyond 6-8 months.

INPUT:  03_Data_Clean/regression_panel_final.csv  (23,347 x 23)
OUTPUT: 05_Outputs/Tables/10_H3_longer_lags.csv
        05_Outputs/Logs/35_longer_lags_log.txt
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import os
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================

INPUT_PATH = "03_Data_Clean/regression_panel_final.csv"
OUT_TABLE  = "05_Outputs/Tables/10_H3_longer_lags.csv"
LOG_PATH   = "05_Outputs/Logs/35_longer_lags_log.txt"

# H3 t0/t-1/t-2 anchors (Script 29, Rule A) for reference
H3_ANCHORS = {
    "t0":  {"beta": +0.000609, "se": 0.001463, "p": 0.677},
    "t-1": {"beta": +0.001505, "se": 0.001114, "p": 0.177},
    "t-2": {"beta": -0.007005, "se": 0.001645, "p": 0.000}
}


# =============================================================================
# SETUP
# =============================================================================

os.makedirs("05_Outputs/Tables", exist_ok=True)
os.makedirs("05_Outputs/Logs",   exist_ok=True)

run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

log("=" * 70)
log("SCRIPT 35: ROBUSTNESS R5 -- LONGER LAGS (t-3, t-4)")
log("H3 distributed lag extension -- Rule B only (precision priority)")
log(f"Run: {run_ts}")
log("=" * 70)
log("Reference H3 result (Script 29, Rule A):")
log(f"  t0:  beta = {H3_ANCHORS['t0']['beta']:+.6f},  p = {H3_ANCHORS['t0']['p']:.3f}")
log(f"  t-1: beta = {H3_ANCHORS['t-1']['beta']:+.6f},  p = {H3_ANCHORS['t-1']['p']:.3f}")
log(f"  t-2: beta = {H3_ANCHORS['t-2']['beta']:+.6f},  p = {H3_ANCHORS['t-2']['p']:.3f} ***")
log("Expected: t-3 and t-4 null. Effect decays at t-2.")
log("=" * 70)


# =============================================================================
# [1/8] LOAD AND ASSERT INPUT
# =============================================================================
log("\n[1/8] Loading regression panel...")

df = pd.read_csv(INPUT_PATH)

assert len(df) == 23347,     f"Expected 23,347 rows, got {len(df):,}. Check upstream pipeline."
assert df.shape[1] == 23,     f"Expected 23 columns, got {df.shape[1]}. Check upstream pipeline."

required_cols = [
    "district_gadm", "state_gadm", "quarter", "year", "q",
    "deposit_change_qt",
    "flood_exposure_ruleB_qt", "flood_ruleB_L1", "flood_ruleB_L2",
    "flood_ruleB_L3", "flood_ruleB_L4"  # L3 and L4 must exist
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

log(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log("  Required columns verified -- PASS")


# =============================================================================
# [2/8] COMPOSITE KEY
# =============================================================================
log("\n[2/8] Constructing composite key...")

df["district_state_id"] = df["district_gadm"] + "_" + df["state_gadm"]
n_districts = df["district_state_id"].nunique()
log(f"  district_state_id: {n_districts} unique pairs (expected 631)")

if n_districts != 631:
    raise ValueError(f"District count = {n_districts}, expected 631.")

log("  Composite key verified -- PASS")


# =============================================================================
# [3/8] VERIFY PRE-COMPUTED LAG ARITHMETIC (Script 24)
# =============================================================================
log("\n[3/8] Verifying pre-computed lag arithmetic (Script 24 columns)...")

nan_L0 = df["flood_exposure_ruleB_qt"].isna().sum()
nan_L1 = df["flood_ruleB_L1"].isna().sum()
nan_L2 = df["flood_ruleB_L2"].isna().sum()
nan_L3 = df["flood_ruleB_L3"].isna().sum()
nan_L4 = df["flood_ruleB_L4"].isna().sum()

expected_L0 = 0
expected_L1 = 631
expected_L2 = 1262
expected_L3 = 1893
expected_L4 = 2524

log(f"  flood_ruleB_L0 NaN: {nan_L0:,}      (expected {expected_L0:,})")
log(f"  flood_ruleB_L1 NaN: {nan_L1:,}    (expected {expected_L1:,})")
log(f"  flood_ruleB_L2 NaN: {nan_L2:,}  (expected {expected_L2:,})")
log(f"  flood_ruleB_L3 NaN: {nan_L3:,}  (expected {expected_L3:,})")
log(f"  flood_ruleB_L4 NaN: {nan_L4:,}  (expected {expected_L4:,})")

assert nan_L0 == expected_L0, f"L0 NaN = {nan_L0}, expected {expected_L0}."
assert nan_L1 == expected_L1, f"L1 NaN = {nan_L1}, expected {expected_L1}."
assert nan_L2 == expected_L2, f"L2 NaN = {nan_L2}, expected {expected_L2}."
assert nan_L3 == expected_L3, f"L3 NaN = {nan_L3}, expected {expected_L3}."
assert nan_L4 == expected_L4, f"L4 NaN = {nan_L4}, expected {expected_L4}."

log("  Lag arithmetic verified -- PASS")


# =============================================================================
# [4/8] RESTRICT TO COMPLETE CASES (L4 restriction)
# =============================================================================
log("\n[4/8] Restricting to complete cases (L4 restriction)...")

initial_n = len(df)
df_complete = df[
    df["deposit_change_qt"].notna()        &
    df["flood_exposure_ruleB_qt"].notna()  &
    df["flood_ruleB_L1"].notna()           &
    df["flood_ruleB_L2"].notna()           &
    df["flood_ruleB_L3"].notna()           &
    df["flood_ruleB_L4"].notna()
].copy()

final_n = len(df_complete)
dropped_n = initial_n - final_n

log(f"  Initial:         {initial_n:,} obs")
log(f"  L4 complete:     {final_n:,} obs")
log(f"  Dropped:         {dropped_n:,} obs ({dropped_n/initial_n*100:.2f}%)")
log(f"  Expected drop:   >= 2,524 (631 districts x 4 lags)")

assert final_n > 15000,     f"L4 complete cases = {final_n:,}, below minimum threshold 15,000. Catastrophic failure."

log("  L4 complete cases verified -- PASS")


# =============================================================================
# [5/8] ENCODE QUARTER FE
# =============================================================================
log("\n[5/8] Encoding quarter FE...")

df_complete["quarter_fe"] = pd.Categorical(df_complete["quarter"])
n_qfe = df_complete["quarter_fe"].nunique()
log(f"  Quarter FE levels: {n_qfe} (expected 33-35 -- L4 restriction)")

if n_qfe < 30 or n_qfe > 38:
    raise ValueError(f"Quarter FE = {n_qfe}, outside expected range [30, 38].")

log("  Quarter FE verified -- PASS")


# =============================================================================
# HELPER: EXTRACT COEFFICIENT
# =============================================================================
def extract_coef(model, varname):
    coef  = model.params.get(varname, np.nan)
    se    = model.bse.get(varname, np.nan)
    tstat = model.tvalues.get(varname, np.nan)
    pval  = model.pvalues.get(varname, np.nan)
    ci    = model.conf_int()
    ci_lo = ci.loc[varname, 0] if varname in ci.index else np.nan
    ci_hi = ci.loc[varname, 1] if varname in ci.index else np.nan
    if pval < 0.01:   sig = "***"
    elif pval < 0.05: sig = "**"
    elif pval < 0.10: sig = "*"
    else:             sig = ""
    return coef, se, tstat, pval, ci_lo, ci_hi, sig


def log_coef(label, coef, se, tstat, pval, ci_lo, ci_hi, sig):
    log(f"    [{label}]")
    log(f"      Beta   = {coef:.6f}")
    log(f"      SE     = {se:.6f}")
    log(f"      t      = {tstat:.3f}")
    log(f"      p      = {pval:.6f}")
    log(f"      95% CI = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log(f"      Status = {sig if sig else 'NOT SIGNIFICANT'}")


# =============================================================================
# [6/8] RUN REGRESSION -- RULE B LONGER LAGS
# =============================================================================
log("\n" + "=" * 70)
log("[6/8] REGRESSION: Rule B L0 + L1 + L2 + L3 + L4")
log("=" * 70)
log("  Dependent: deposit_change_qt")
log("  Regressors: flood_ruleB_L0 + L1 + L2 + L3 + L4")
log("  FE:         Quarter only (NO district FE -- H3 design)")
log("  SE:         Clustered district_state_id")

formula = (
    "deposit_change_qt ~ flood_exposure_ruleB_qt + flood_ruleB_L1 + "
    "flood_ruleB_L2 + flood_ruleB_L3 + flood_ruleB_L4 + C(quarter_fe)"
)

try:
    model = ols(formula, data=df_complete).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_complete["district_state_id"]}
    )
    n_obs = int(model.nobs)
    r2    = model.rsquared
    log(f"  Model fitted: N={n_obs:,}, R2={r2:.4f} -- PASS")
except Exception as e:
    log(f"  FAILED: {e}")
    raise


# Extract coefficients
lags = ["t0", "t-1", "t-2", "t-3", "t-4"]
lag_vars = [
    "flood_exposure_ruleB_qt",
    "flood_ruleB_L1",
    "flood_ruleB_L2",
    "flood_ruleB_L3",
    "flood_ruleB_L4"
]

results = []
for i, (lag_label, var) in enumerate(zip(lags, lag_vars)):
    coef, se, tstat, pval, ci_lo, ci_hi, sig = extract_coef(model, var)
    log_coef(f"{lag_label:<2} ({var})", coef, se, tstat, pval, ci_lo, ci_hi, sig)

    results.append({
        "hypothesis":     "H3_Longer_Lags",
        "rule":          "B",
        "lag":           lag_label,
        "variable":      var,
        "coefficient":   round(coef, 6),
        "std_error":     round(se, 6),
        "t_statistic":   round(tstat, 3),
        "p_value":       round(pval, 6),
        "ci_lower_95":   round(ci_lo, 6),
        "ci_upper_95":   round(ci_hi, 6),
        "significance":  sig,
        "n_obs":         n_obs,
        "r_squared":     round(model.rsquared, 4),
        "quarter_fe_count": n_qfe,
        "district_fe":   "NONE (pre-committed H3 design)",
        "se_type":       "clustered_by_district_state_id"
    })


# =============================================================================
# [7/8] COMPARISON TO H3 SHORT LAGS
# =============================================================================
log("\n" + "=" * 70)
log("[7/8] COMPARISON: H3 Short Lags vs Longer Lags")
log("=" * 70)

log(f"  {'Lag':<6} {'H3 Rule A':>12} {'H3 p':>10} {'Longer Rule B':>14} {'Longer p':>12}")
log(f"  {'-'*60}")

for i, lag_label in enumerate(lags):
    row = results[i]
    anchor = H3_ANCHORS.get(lag_label, {"beta": np.nan, "p": np.nan})
    direction = "SAME" if (anchor["beta"] * row["coefficient"] > 0) else "REVERSED"
    sig_longer = "***" if row["p_value"] < 0.01 else ("**" if row["p_value"] < 0.05 else "*")
    log(f"  {lag_label:<6} {anchor['beta']:>12.6f} {anchor['p']:>10.3f} {row['coefficient']:>14.6f} {row['p_value']:>12.6f} ({direction}, {sig_longer if row['p_value'] < 0.10 else 'null'})")


# =============================================================================
# [8/8] VERDICT AND SAVE
# =============================================================================
log("\n" + "=" * 70)
log("[8/8] VERDICT AND SAVE")
log("=" * 70)

# Check for persistence beyond t-2
t3_p = results[3]["p_value"]
t4_p = results[4]["p_value"]
t3_sig = t3_p < 0.05
t4_sig = t4_p < 0.05

if not t3_sig and not t4_sig:
    log("  VERDICT: NO PERSISTENCE BEYOND t-2")
    log("    t-3 and t-4 both null (p > 0.05).")
    log("    H3 t-2 effect is temporary (6-month displacement window).")
    log("    Mechanism consistent with acute liquidity stress, not")
    log("    permanent economic damage. WRITING UNBLOCKED.")
elif t3_sig or t4_sig:
    log("  VERDICT: PERSISTENCE BEYOND t-2")
    log(f"    t-3: p = {t3_p:.4f} {'***' if t3_sig else 'null'}")
    log(f"    t-4: p = {t4_p:.4f} {'***' if t4_sig else 'null'}")
    log("    H3 t-2 effect persists 9-12 months post-flood.")
    log("    Mechanism consistent with prolonged displacement or")
    log("    recovery delay. Paper mechanism narrative strengthened.")
    log("    WRITING UNBLOCKED -- update mechanism discussion.")
else:
    log("  VERDICT: MARGINAL PERSISTENCE")
    log("    t-3/t-4 p-values marginal. Monitor in robustness section.")

# Save table
results_df = pd.DataFrame(results)
assert len(results_df) == 5, f"Expected 5 rows, got {len(results_df)}."

results_df.to_csv(OUT_TABLE, index=False)
assert os.path.exists(OUT_TABLE), f"Table not saved: {OUT_TABLE}"
log(f"\n  Table saved: {OUT_TABLE} ({len(results_df)} rows) -- PASS")

# Save log
with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
assert os.path.exists(LOG_PATH), f"Log not saved: {LOG_PATH}"
log(f"  Log saved:   {LOG_PATH} -- PASS")

# === COMPLETION ===
log("\n" + "=" * 70)
log("SCRIPT 35 COMPLETE")
log(f"  L4 complete cases: {final_n:,}")
log(f"  t-3 p-value:       {t3_p:.4f} ({'sig' if t3_sig else 'null'})")
log(f"  t-4 p-value:       {t4_p:.4f} ({'sig' if t4_sig else 'null'})")
log(f"  Verdict:           {'PERSISTENCE' if t3_sig or t4_sig else 'NO PERSISTENCE'}")
log(f"  Table: {OUT_TABLE}")
log(f"  Log:   {LOG_PATH}")
log("=" * 70)
log("NEXT: Script 36 -- R6 State-Level Clustering (H1 + H3)")
log("=" * 70)
