"""
36_state_clustering.py
Robustness R6: State-Level Clustering -- Conservative SE Check


Purpose:
    Pre-committed conservative SE specification test.
    Re-run H1 (first stage) and H3 (distributed lag t-2) with SE clustered
    by state_gadm (34 clusters) instead of district_state_id (631 clusters).


Rationale:
    Cameron and Miller (2015): below 50 clusters, standard clustered SEs
    may be liberal (under-reject H0). 34 state clusters is below threshold.
    If H1 and H3 t-2 survive wider SEs, causal chain is robust to most
    conservative reasonable specification.


H1 locked result (Script 27, Rule A): beta = -0.0445, t = -5.708 ***
H3 locked result (Script 29, Rule A t-2): beta = -0.007005, t = -4.259 ***


Two regressions:
    H1: lights_change_qt ~ flood_exposure_ruleA_qt + C(district_state_id) + C(quarter)
    H3: deposit_change_qt ~ flood_ruleA_L2 + C(quarter)  [t-2 only]
Both x Rule A and Rule B. SE: clustered by state_gadm.


Expected: SEs widen. Both results remain significant (strong effects).


INPUT:  03_Data_Clean/regression_panel_final.csv  (23,347 x 23)
OUTPUT: 05_Outputs/Tables/11_H1_state_clustering.csv
        05_Outputs/Tables/12_H3_state_clustering.csv
        05_Outputs/Logs/36_state_clustering_log.txt
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
OUT_H1     = "05_Outputs/Tables/11_H1_state_clustering.csv"
OUT_H3     = "05_Outputs/Tables/12_H3_state_clustering.csv"
LOG_PATH   = "05_Outputs/Logs/36_state_clustering_log.txt"


# Locked anchors (Scripts 27 and 29, Rule A)
H1_ANCHOR = {"beta": -0.0445, "se": 0.0078, "t": -5.708}
H3_ANCHOR = {"beta": -0.007005, "se": 0.001645, "t": -4.259}



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
log("SCRIPT 36: ROBUSTNESS R6 -- STATE-LEVEL CLUSTERING")
log("H1 and H3 re-run with SE clustered by state_gadm (34 clusters)")
log(f"Run: {run_ts}")
log("=" * 70)
log("Rationale: Cameron/Miller (2015) -- below 50 clusters, standard SEs liberal.")
log("Expected: SEs widen. H1 and H3 t-2 remain significant.")
log("=" * 70)



# =============================================================================
# [1/9] LOAD AND ASSERT
# =============================================================================
log("\n[1/9] Loading panel...")


df = pd.read_csv(INPUT_PATH)


assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23, f"Expected 23 cols, got {df.shape[1]}"


required_cols = [
    "district_gadm", "state_gadm", "quarter", "year", "q",
    "deposit_change_qt", "lights_change_qt",
    "flood_exposure_ruleA_qt", "flood_ruleA_L2",
    "flood_exposure_ruleB_qt", "flood_ruleB_L2"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")


log(f"  Loaded: {len(df):,} rows, {df.shape[1]} cols -- PASS")



# =============================================================================
# [2/9] COMPOSITE KEY AND STATE COUNT
# =============================================================================
log("\n[2/9] Composite key and state verification...")


df["district_state_id"] = df["district_gadm"] + "_" + df["state_gadm"]


n_districts = df["district_state_id"].nunique()
n_states    = df["state_gadm"].nunique()


log(f"  district_state_id: {n_districts} (expected 631)")
log(f"  state_gadm:        {n_states} (expected 34)")
log(f"  Note: 34 = 28 states + 6 union territories (GADM encoding)")
log(f"  Cameron/Miller (2015) threshold = 50. {n_states} clusters below threshold -- warning applies.")


assert n_districts == 631, f"Districts = {n_districts}, expected 631"
assert n_states == 34,     f"States = {n_states}, expected 34"


log("  Keys verified -- PASS")



# =============================================================================
# [3/9] H1 COMPLETE CASES -- RULE A
# =============================================================================
log("\n[3/9] H1 Rule A complete cases...")


df_h1_a = df[
    df["lights_change_qt"].notna() &
    df["flood_exposure_ruleA_qt"].notna()
].copy()


df_h1_a["district_fe"] = pd.Categorical(df_h1_a["district_state_id"])
df_h1_a["quarter_fe"]  = pd.Categorical(df_h1_a["quarter"])


n_h1_a      = len(df_h1_a)
n_dfe_h1_a  = df_h1_a["district_fe"].nunique()
n_qfe_h1_a  = df_h1_a["quarter_fe"].nunique()


log(f"  H1 Rule A: N={n_h1_a:,}, Dist FE={n_dfe_h1_a}, Qtr FE={n_qfe_h1_a}")


assert n_h1_a == 22716,   f"H1 Rule A N={n_h1_a}, expected 22,716"
assert n_dfe_h1_a == 631, f"H1 Dist FE={n_dfe_h1_a}, expected 631"
assert n_qfe_h1_a == 36,  f"H1 Qtr FE={n_qfe_h1_a}, expected 36"


log("  H1 Rule A cases verified -- PASS")



# =============================================================================
# [4/9] H1 COMPLETE CASES -- RULE B
# =============================================================================
log("\n[4/9] H1 Rule B complete cases...")


df_h1_b = df[
    df["lights_change_qt"].notna() &
    df["flood_exposure_ruleB_qt"].notna()
].copy()


df_h1_b["district_fe"] = pd.Categorical(df_h1_b["district_state_id"])
df_h1_b["quarter_fe"]  = pd.Categorical(df_h1_b["quarter"])


n_h1_b      = len(df_h1_b)
n_dfe_h1_b  = df_h1_b["district_fe"].nunique()
n_qfe_h1_b  = df_h1_b["quarter_fe"].nunique()


log(f"  H1 Rule B: N={n_h1_b:,}, Dist FE={n_dfe_h1_b}, Qtr FE={n_qfe_h1_b}")


assert n_dfe_h1_b == 631, f"H1 Rule B Dist FE={n_dfe_h1_b}, expected 631"
assert n_qfe_h1_b == 36,  f"H1 Rule B Qtr FE={n_qfe_h1_b}, expected 36"


log("  H1 Rule B cases verified -- PASS")



# =============================================================================
# [5/9] H3 COMPLETE CASES -- RULE A t-2
# =============================================================================
log("\n[5/9] H3 Rule A t-2 complete cases...")


df_h3_a = df[
    df["deposit_change_qt"].notna() &
    df["flood_ruleA_L2"].notna()
].copy()


df_h3_a["quarter_fe"] = pd.Categorical(df_h3_a["quarter"])


n_h3_a      = len(df_h3_a)
n_qfe_h3_a  = df_h3_a["quarter_fe"].nunique()


log(f"  H3 Rule A t-2: N={n_h3_a:,}, Qtr FE={n_qfe_h3_a}")


assert n_h3_a == 21837,  f"H3 Rule A t-2 N={n_h3_a}, expected 21,837"
assert n_qfe_h3_a == 35, f"H3 Rule A t-2 Qtr FE={n_qfe_h3_a}, expected 35"


log("  H3 Rule A t-2 cases verified -- PASS")



# =============================================================================
# [6/9] H3 COMPLETE CASES -- RULE B t-2
# =============================================================================
log("\n[6/9] H3 Rule B t-2 complete cases...")


df_h3_b = df[
    df["deposit_change_qt"].notna() &
    df["flood_ruleB_L2"].notna()
].copy()


df_h3_b["quarter_fe"] = pd.Categorical(df_h3_b["quarter"])


n_h3_b      = len(df_h3_b)
n_qfe_h3_b  = df_h3_b["quarter_fe"].nunique()


log(f"  H3 Rule B t-2: N={n_h3_b:,}, Qtr FE={n_qfe_h3_b}")


assert n_qfe_h3_b == 35, f"H3 Rule B t-2 Qtr FE={n_qfe_h3_b}, expected 35"


log("  H3 Rule B t-2 cases verified -- PASS")



# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def extract_coef(model, varname):
    coef  = model.params.get(varname, np.nan)
    se    = model.bse.get(varname, np.nan)
    tstat = model.tvalues.get(varname, np.nan)
    pval  = model.pvalues.get(varname, np.nan)
    ci    = model.conf_int()
    ci_lo = ci.loc[varname, 0] if varname in ci.index else np.nan
    ci_hi = ci.loc[varname, 1] if varname in ci.index else np.nan
    if   pval < 0.01: sig = "***"
    elif pval < 0.05: sig = "**"
    elif pval < 0.10: sig = "*"
    else:             sig = ""
    return coef, se, tstat, pval, ci_lo, ci_hi, sig



def log_coef(label, coef, se, t, p, ci_lo, ci_hi, sig, anchor=None):
    anchor_str = f" (main: {anchor['beta']})" if anchor else ""
    log(f"    [{label}]")
    log(f"      Beta   = {coef:.6f}{anchor_str}")
    log(f"      SE     = {se:.6f}")
    log(f"      t      = {t:.3f}")
    log(f"      p      = {p:.6f}")
    log(f"      95% CI = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log(f"      Status = {sig if sig else 'NOT SIGNIFICANT'}")



# =============================================================================
# [7/9] H1 RULE A -- STATE CLUSTERING
# =============================================================================
log("\n" + "=" * 70)
log("[7/9] H1 Rule A -- state_gadm clustering...")
log("=" * 70)


formula_h1_a = "lights_change_qt ~ flood_exposure_ruleA_qt + C(district_state_id) + C(quarter)"


model_h1_a = ols(formula_h1_a, data=df_h1_a).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_h1_a["state_gadm"]}
)


c, s, t, p, lo, hi, sg = extract_coef(model_h1_a, "flood_exposure_ruleA_qt")
log_coef("H1 Rule A", c, s, t, p, lo, hi, sg, H1_ANCHOR)


h1_results_a = [{
    "hypothesis":        "H1",
    "rule":              "A",
    "outcome":           "lights_change_qt",
    "flood_var":         "flood_exposure_ruleA_qt",
    "coefficient":       round(c, 6),
    "std_error":         round(s, 6),
    "t_statistic":       round(t, 3),
    "p_value":           round(p, 6),
    "ci_lower_95":       round(lo, 6),
    "ci_upper_95":       round(hi, 6),
    "significance":      sg,
    "n_obs":             int(model_h1_a.nobs),
    "district_fe_count": n_dfe_h1_a,
    "quarter_fe_count":  n_qfe_h1_a,
    "se_clusters":       "state_gadm (34)",
    "anchor_beta":       H1_ANCHOR["beta"],
    "anchor_se":         H1_ANCHOR["se"],
    "anchor_t":          H1_ANCHOR["t"]
}]



# =============================================================================
# [8/9] H1 RULE B AND H3 BOTH RULES
# =============================================================================
log("\n[8/9] Remaining regressions...")


# H1 Rule B
log("\n  H1 Rule B -- state_gadm clustering")
formula_h1_b = "lights_change_qt ~ flood_exposure_ruleB_qt + C(district_state_id) + C(quarter)"
model_h1_b = ols(formula_h1_b, data=df_h1_b).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_h1_b["state_gadm"]}
)
c, s, t, p, lo, hi, sg = extract_coef(model_h1_b, "flood_exposure_ruleB_qt")
log_coef("H1 Rule B", c, s, t, p, lo, hi, sg)


h1_results_b = [{
    "hypothesis":        "H1",
    "rule":              "B",
    "outcome":           "lights_change_qt",
    "flood_var":         "flood_exposure_ruleB_qt",
    "coefficient":       round(c, 6),
    "std_error":         round(s, 6),
    "t_statistic":       round(t, 3),
    "p_value":           round(p, 6),
    "ci_lower_95":       round(lo, 6),
    "ci_upper_95":       round(hi, 6),
    "significance":      sg,
    "n_obs":             int(model_h1_b.nobs),
    "district_fe_count": n_dfe_h1_b,
    "quarter_fe_count":  n_qfe_h1_b,
    "se_clusters":       "state_gadm (34)",
    "anchor_beta":       None,
    "anchor_se":         None,
    "anchor_t":          None
}]


# H3 Rule A t-2
log("\n  H3 Rule A t-2 -- state_gadm clustering")
formula_h3_a = "deposit_change_qt ~ flood_ruleA_L2 + C(quarter)"
model_h3_a = ols(formula_h3_a, data=df_h3_a).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_h3_a["state_gadm"]}
)
c, s, t, p, lo, hi, sg = extract_coef(model_h3_a, "flood_ruleA_L2")
log_coef("H3 Rule A t-2", c, s, t, p, lo, hi, sg, H3_ANCHOR)


h3_results_a = [{
    "hypothesis":       "H3",
    "rule":             "A",
    "lag":              "t-2",
    "outcome":          "deposit_change_qt",
    "flood_var":        "flood_ruleA_L2",
    "coefficient":      round(c, 6),
    "std_error":        round(s, 6),
    "t_statistic":      round(t, 3),
    "p_value":          round(p, 6),
    "ci_lower_95":      round(lo, 6),
    "ci_upper_95":      round(hi, 6),
    "significance":     sg,
    "n_obs":            int(model_h3_a.nobs),
    "district_fe":      "NONE (H3 spec)",
    "quarter_fe_count": n_qfe_h3_a,
    "se_clusters":      "state_gadm (34)",
    "anchor_beta":      H3_ANCHOR["beta"],
    "anchor_se":        H3_ANCHOR["se"],
    "anchor_t":         H3_ANCHOR["t"]
}]


# H3 Rule B t-2
log("\n  H3 Rule B t-2 -- state_gadm clustering")
formula_h3_b = "deposit_change_qt ~ flood_ruleB_L2 + C(quarter)"
model_h3_b = ols(formula_h3_b, data=df_h3_b).fit(
    cov_type="cluster",
    cov_kwds={"groups": df_h3_b["state_gadm"]}
)
c, s, t, p, lo, hi, sg = extract_coef(model_h3_b, "flood_ruleB_L2")
log_coef("H3 Rule B t-2", c, s, t, p, lo, hi, sg)


h3_results_b = [{
    "hypothesis":       "H3",
    "rule":             "B",
    "lag":              "t-2",
    "outcome":          "deposit_change_qt",
    "flood_var":        "flood_ruleB_L2",
    "coefficient":      round(c, 6),
    "std_error":        round(s, 6),
    "t_statistic":      round(t, 3),
    "p_value":          round(p, 6),
    "ci_lower_95":      round(lo, 6),
    "ci_upper_95":      round(hi, 6),
    "significance":     sg,
    "n_obs":            int(model_h3_b.nobs),
    "district_fe":      "NONE (H3 spec)",
    "quarter_fe_count": n_qfe_h3_b,
    "se_clusters":      "state_gadm (34)",
    "anchor_beta":      None,
    "anchor_se":        None,
    "anchor_t":         None
}]



# =============================================================================
# [9/9] VERDICT AND SAVE
# =============================================================================
log("\n" + "=" * 70)
log("[9/9] VERDICT AND SAVE")
log("=" * 70)


h1_a_sig = h1_results_a[0]["p_value"] < 0.05
h3_a_sig = h3_results_a[0]["p_value"] < 0.05


log("\n  H1 Rule A survives state clustering: " +
    ("YES" if h1_a_sig else "NO -- INVESTIGATE"))
log("  H3 Rule A t-2 survives state clustering: " +
    ("YES" if h3_a_sig else "NO -- INVESTIGATE"))


if h1_a_sig and h3_a_sig:
    log("\n  R6 VERDICT: FULLY ROBUST")
    log("  Causal chain survives most conservative SE specification.")
    log("  34 state clusters (below Cameron/Miller 50-cluster threshold).")
    log("  Writing unblocked.")
else:
    log("\n  R6 VERDICT: PARTIAL FAILURE")
    log("  One or both core results lose significance under state clustering.")
    log("  Liberal SE concern confirmed. Causal claims must be qualified.")


# Save tables
h1_df = pd.DataFrame(h1_results_a + h1_results_b)
h3_df = pd.DataFrame(h3_results_a + h3_results_b)


assert len(h1_df) == 2, f"H1 table: expected 2 rows, got {len(h1_df)}"
assert len(h3_df) == 2, f"H3 table: expected 2 rows, got {len(h3_df)}"


h1_df.to_csv(OUT_H1, index=False)
assert os.path.exists(OUT_H1), f"H1 table not saved: {OUT_H1}"
log(f"\n  H1 table saved: {OUT_H1} ({len(h1_df)} rows) -- PASS")


h3_df.to_csv(OUT_H3, index=False)
assert os.path.exists(OUT_H3), f"H3 table not saved: {OUT_H3}"
log(f"  H3 table saved: {OUT_H3} ({len(h3_df)} rows) -- PASS")


with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
assert os.path.exists(LOG_PATH), f"Log not saved: {LOG_PATH}"
log(f"  Log saved:   {LOG_PATH} -- PASS")


log("\n" + "=" * 70)
log("SCRIPT 36 COMPLETE")
log(f"  H1 Rule A robust:  {'YES' if h1_a_sig else 'NO'}")
log(f"  H3 t-2 robust:     {'YES' if h3_a_sig else 'NO'}")
log(f"  Tables: {OUT_H1}, {OUT_H3}")
log(f"  Log:   {LOG_PATH}")
log("=" * 70)
log("NEXT: Script 37 -- R3 Winsorized Re-runs")
log("=" * 70)