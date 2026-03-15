"""
37_winsorized_reruns.py
Robustness R3: Winsorized Regression Re-runs -- H2, H3, H4


Purpose:
    Pre-committed R3. Re-run H2, H3, H4 on winsorized panel.
    Script 31 produced regression_panel_final_winsor.csv but
    the regression re-runs have not been executed until now.


H1 is excluded: outcome is lights_change_qt (not deposits).
Winsorization only affects deposit_change_qt. H1 is unaffected.


Winsorization parameters (Script 31, locked):
    Variable:    deposit_change_qt
    Bounds:      lower = -0.162585, upper = 0.230701
    Obs winsorized: 450 (2.01%), symmetric


H2 method (manual 2SLS):
    First stage:  lights_change_qt ~ flood_ruleX_qt + C(district) + C(quarter)
    Second stage: deposit_change_qt_winsor ~ lights_hat + C(district) + C(quarter)
    Rule A and Rule B produce different lights_hat from different instruments.
    Note: Second-stage SEs do not account for first-stage estimation error.
    For robustness purposes (null check), coefficient direction and approximate
    significance are informative. Consistent with Script 28 null result.


Proxy variables (constructed at runtime, same logic as Script 30):
    urban_proxy:          1 if district mean log_lights_qt >= median, else 0
    high_exposure_proxy:  1 if district mean flood_exposure_ruleA_qt > 0, else 0
    monsoon_quarter:      1 if q in [2, 3] (Q2 Apr-Jun, Q3 Jul-Sep), else 0
    These are proxies. Never claim census-based urban/rural classification.


Locked anchors (non-winsorized, Scripts 28/29/30, Rule A):
    H2:     beta = -0.0084, SE = 0.0340, p = 0.805  -- NULL
    H3 t-2: beta = -0.007005, SE = 0.001645, p < 0.001 -- CONFIRMED
    H4b:    p = 0.020 -- supported
    H4c:    p = 0.001 -- supported (Rule A only)


Expected: Results robust. No material change to coefficients.
    450 winsorized obs (2.01%) insufficient to alter structure.


INPUT:  03_Data_Clean/regression_panel_final_winsor.csv  (23,347 x 24)
OUTPUT: 05_Outputs/Tables/13_H2_winsorized.csv
        05_Outputs/Tables/14_H3_winsorized.csv
        05_Outputs/Tables/15_H4_winsorized.csv
        05_Outputs/Logs/37_winsorized_reruns_log.txt
"""


import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import os
from datetime import datetime



# =============================================================================
# CONFIGURATION
# =============================================================================


INPUT_PATH = "03_Data_Clean/regression_panel_final_winsor.csv"
OUT_H2     = "05_Outputs/Tables/13_H2_winsorized.csv"
OUT_H3     = "05_Outputs/Tables/14_H3_winsorized.csv"
OUT_H4     = "05_Outputs/Tables/15_H4_winsorized.csv"
LOG_PATH   = "05_Outputs/Logs/37_winsorized_reruns_log.txt"


# Winsorization bounds (Script 31, locked -- DO NOT CHANGE)
WINSOR_LOWER = -0.162585
WINSOR_UPPER =  0.230701
WINSOR_N     =  450
WINSOR_PCT   =  2.01


# Locked anchors (non-winsorized baseline, Scripts 28/29/30, Rule A)
H2_ANCHOR  = {"beta": -0.0084,   "se": 0.0340,   "p": 0.805}
H3_ANCHOR  = {"beta": -0.007005, "se": 0.001645, "p": 0.000}
H4b_ANCHOR = {"p": 0.020}
H4c_ANCHOR = {"p": 0.001}


# H2 F-stat anchors (Script 28, locked)
H2_F_RULE_A = 34.673   # strong (threshold 16.38)
H2_F_RULE_B =  8.949   # weak   (threshold 10) -- Rule B labeled suggestive



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
log("SCRIPT 37: ROBUSTNESS R3 -- WINSORIZED REGRESSION RE-RUNS")
log("H2, H3, H4 re-run on deposit_change_qt_winsor")
log(f"Run: {run_ts}")
log("=" * 70)
log(f"Winsor bounds: [{WINSOR_LOWER}, {WINSOR_UPPER}]")
log(f"Obs winsorized: {WINSOR_N} ({WINSOR_PCT}%)")
log("H1 excluded: outcome is lights_change_qt -- unaffected by winsorization.")
log("Expected: no material change to coefficients.")
log("=" * 70)



# =============================================================================
# [1/11] LOAD AND ASSERT INPUT
# =============================================================================
log("\n[1/11] Loading winsorized panel...")


df = pd.read_csv(INPUT_PATH)


assert len(df) == 23347,  f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 24, f"Expected 24 cols, got {df.shape[1]}"


required_cols = [
    "district_gadm", "state_gadm", "quarter", "year", "q",
    "deposit_change_qt", "deposit_change_qt_winsor",
    "lights_change_qt", "log_lights_qt",
    "flood_exposure_ruleA_qt", "flood_exposure_ruleB_qt",
    "flood_ruleA_L2", "flood_ruleB_L2"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")


log(f"  Loaded: {len(df):,} rows, {df.shape[1]} cols -- PASS")
log("  Required columns verified -- PASS")
log("  Note: urban_proxy and high_exposure_proxy are not stored columns.")
log("  They will be constructed at runtime (same logic as Script 30).")



# =============================================================================
# [2/11] COMPOSITE KEY
# =============================================================================
log("\n[2/11] Constructing composite key...")


df["district_state_id"] = df["district_gadm"] + "_" + df["state_gadm"]
n_districts = df["district_state_id"].nunique()
n_states    = df["state_gadm"].nunique()


log(f"  district_state_id: {n_districts} (expected 631)")
log(f"  state_gadm:        {n_states} (expected 34)")


assert n_districts == 631, f"Districts = {n_districts}, expected 631"
assert n_states == 34,     f"States = {n_states}, expected 34"


log("  Composite key verified -- PASS")



# =============================================================================
# [3/11] VERIFY WINSOR BOUNDS
# =============================================================================
log("\n[3/11] Verifying winsorization bounds on deposit_change_qt_winsor...")


actual_min = df["deposit_change_qt_winsor"].min()
actual_max = df["deposit_change_qt_winsor"].max()


log(f"  Observed min: {actual_min:.6f}  (expected >= {WINSOR_LOWER})")
log(f"  Observed max: {actual_max:.6f}  (expected <= {WINSOR_UPPER})")


assert actual_min >= WINSOR_LOWER - 1e-6, \
    f"Winsor min = {actual_min:.6f}, below locked lower bound {WINSOR_LOWER}"
assert actual_max <= WINSOR_UPPER + 1e-6, \
    f"Winsor max = {actual_max:.6f}, above locked upper bound {WINSOR_UPPER}"


n_at_lower = (df["deposit_change_qt_winsor"] == actual_min).sum()
n_at_upper = (df["deposit_change_qt_winsor"] == actual_max).sum()
log(f"  Obs at lower bound: {n_at_lower}")
log(f"  Obs at upper bound: {n_at_upper}")
log(f"  Total winsorized:   {n_at_lower + n_at_upper} (expected ~{WINSOR_N})")


log("  Winsor bounds verified -- PASS")



# =============================================================================
# [4/11] CONSTRUCT PROXY VARIABLES (same logic as Script 30)
# =============================================================================
log("\n[4/11] Constructing proxy variables (Script 30 logic)...")


# urban_proxy: 1 if district mean log_lights_qt >= median across all districts
district_mean_lights = (
    df.groupby("district_state_id")["log_lights_qt"]
    .mean()
    .reset_index()
    .rename(columns={"log_lights_qt": "mean_lights"})
)
median_lights = district_mean_lights["mean_lights"].median()
district_mean_lights["urban_proxy"] = (
    district_mean_lights["mean_lights"] >= median_lights
).astype(int)
df = df.merge(
    district_mean_lights[["district_state_id", "urban_proxy"]],
    on="district_state_id", how="left"
)
n_urban = df["urban_proxy"].sum()
log(f"  urban_proxy:         median lights threshold = {median_lights:.4f}")
log(f"  urban_proxy = 1:     {n_urban:,} obs")
log(f"  urban_proxy = 0:     {len(df) - n_urban:,} obs")


# high_exposure_proxy: 1 if district mean flood_exposure_ruleA_qt > 0
district_mean_flood = (
    df.groupby("district_state_id")["flood_exposure_ruleA_qt"]
    .mean()
    .reset_index()
    .rename(columns={"flood_exposure_ruleA_qt": "mean_flood_A"})
)
district_mean_flood["high_exposure_proxy"] = (
    district_mean_flood["mean_flood_A"] > 0
).astype(int)
df = df.merge(
    district_mean_flood[["district_state_id", "high_exposure_proxy"]],
    on="district_state_id", how="left"
)
n_high_exp = df["high_exposure_proxy"].sum()
log(f"  high_exposure_proxy: districts with mean flood exposure > 0")
log(f"  high_exposure_proxy = 1: {n_high_exp:,} obs")
log(f"  high_exposure_proxy = 0: {len(df) - n_high_exp:,} obs")


assert df["urban_proxy"].isna().sum() == 0, \
    "urban_proxy has NaN after merge -- district key mismatch."
assert df["high_exposure_proxy"].isna().sum() == 0, \
    "high_exposure_proxy has NaN after merge -- district key mismatch."


log("  Proxy variables constructed -- PASS")



# =============================================================================
# [5/11] H2 AND H4 COMPLETE CASES
# =============================================================================
log("\n[5/11] H2 / H4 complete cases (N = 22,442)...")


df_h2h4 = df[
    df["deposit_change_qt_winsor"].notna() &
    df["lights_change_qt"].notna() &
    df["flood_exposure_ruleA_qt"].notna()
].copy()


df_h2h4["district_fe"] = pd.Categorical(df_h2h4["district_state_id"])
df_h2h4["quarter_fe"]  = pd.Categorical(df_h2h4["quarter"])
df_h2h4["monsoon_quarter"] = df_h2h4["q"].isin([2, 3]).astype(int)


n_h2h4    = len(df_h2h4)
n_dist_fe = df_h2h4["district_fe"].nunique()
n_qtr_fe  = df_h2h4["quarter_fe"].nunique()


log(f"  N={n_h2h4:,}, Dist FE={n_dist_fe}, Qtr FE={n_qtr_fe}")


assert n_h2h4 == 22442,   f"H2/H4 N={n_h2h4}, expected 22,442"
assert n_dist_fe == 631,  f"Dist FE={n_dist_fe}, expected 631"
assert n_qtr_fe == 36,    f"Qtr FE={n_qtr_fe}, expected 36"


log("  H2/H4 complete cases verified -- PASS")



# =============================================================================
# [6/11] H3 COMPLETE CASES
# =============================================================================
log("\n[6/11] H3 complete cases (N = 21,837)...")


df_h3_base = df[
    df["deposit_change_qt_winsor"].notna() &
    df["flood_ruleA_L2"].notna()
].copy()


n_h3_base = len(df_h3_base)
log(f"  H3 base (Rule A L2 restriction): N={n_h3_base:,} (expected 21,837)")
assert n_h3_base == 21837, f"H3 N={n_h3_base}, expected 21,837"


log("  H3 complete cases verified -- PASS")



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


def _stars(p):
    if   p < 0.01: return "***"
    elif p < 0.05: return "**"
    elif p < 0.10: return "*"
    else:          return "null"


def log_coef(label, coef, se, t, p, ci_lo, ci_hi, sig,
             anchor_beta=None, anchor_p=None):
    anchor_str = ""
    if anchor_beta is not None:
        anchor_str = f" (main beta: {anchor_beta})"
    elif anchor_p is not None:
        anchor_str = f" (main p: {anchor_p})"
    log(f"    [{label}]")
    log(f"      Beta   = {coef:.6f}{anchor_str}")
    log(f"      SE     = {se:.6f}")
    log(f"      t      = {t:.3f}")
    log(f"      p      = {p:.6f}")
    log(f"      95% CI = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log(f"      Status = {sig if sig else 'NOT SIGNIFICANT'}")


def make_row(hyp, rule, outcome, varname, model, n_obs,
             dist_fe_label, qtr_fe, anchor_beta=None,
             anchor_p=None, note=None):
    c, s, t, p, lo, hi, sg = extract_coef(model, varname)
    log_coef(f"{hyp} Rule {rule}", c, s, t, p, lo, hi, sg,
             anchor_beta, anchor_p)
    return {
        "hypothesis":       hyp,
        "rule":             rule,
        "outcome":          outcome,
        "flood_var":        varname,
        "coefficient":      round(c, 6),
        "std_error":        round(s, 6),
        "t_statistic":      round(t, 3),
        "p_value":          round(p, 6),
        "ci_lower_95":      round(lo, 6),
        "ci_upper_95":      round(hi, 6),
        "significance":     sg,
        "n_obs":            n_obs,
        "district_fe":      dist_fe_label,
        "quarter_fe_count": qtr_fe,
        "se_type":          "clustered_by_district_state_id",
        "anchor_beta":      anchor_beta,
        "anchor_p":         anchor_p,
        "note":             note if note else ""
    }



# =============================================================================
# [7/11] H2 -- MANUAL 2SLS WINSORIZED (Rule A and Rule B)
# =============================================================================
log("\n" + "=" * 70)
log("[7/11] H2: Manual 2SLS -- Winsorized (Rule A and Rule B)")
log("=" * 70)
log("  Outcome:       deposit_change_qt_winsor")
log("  First stage:   lights_change_qt ~ flood_ruleX_qt + C(district) + C(quarter)")
log("  Second stage:  deposit_change_qt_winsor ~ lights_hat + C(district) + C(quarter)")
log("  SE:            clustered district_state_id (second-stage only;")
log("                 does not account for first-stage estimation error)")
log("  Rule A and Rule B produce different lights_hat from different instruments.")
log(f"  F Rule A: {H2_F_RULE_A} -- strong instrument (threshold 16.38)")
log(f"  F Rule B: {H2_F_RULE_B} -- weak instrument (< 10, suggestive only)")


h2_results = []

for rule, flood_var, f_stat, anchor_b, anchor_p_val in [
    ("A", "flood_exposure_ruleA_qt", H2_F_RULE_A,
     H2_ANCHOR["beta"], H2_ANCHOR["p"]),
    ("B", "flood_exposure_ruleB_qt", H2_F_RULE_B,
     None,              None)
]:
    log(f"\n  H2 Rule {rule} -- manual 2SLS winsorized")

    # First stage: lights ~ flood + district FE + quarter FE
    fs_formula = (
        f"lights_change_qt ~ {flood_var} + "
        "C(district_state_id) + C(quarter_fe)"
    )
    fs_model = ols(fs_formula, data=df_h2h4).fit()
    df_h2h4["lights_hat"] = fs_model.fittedvalues
    fs_f = fs_model.fvalue
    log(f"    First stage F = {fs_f:.3f}  (locked F = {f_stat})")

    # Second stage: deposit_winsor ~ lights_hat + district FE + quarter FE
    ss_formula = (
        "deposit_change_qt_winsor ~ lights_hat + "
        "C(district_state_id) + C(quarter_fe)"
    )
    ss_model = ols(ss_formula, data=df_h2h4).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_h2h4["district_state_id"]}
    )
    n_obs = int(ss_model.nobs)
    note_str = (
        f"Manual 2SLS. Rule {rule} IV F={f_stat}. "
        + ("Strong instrument." if rule == "A"
           else "Weak instrument (F<10), suggestive only.")
        + " Second-stage SEs do not correct for first-stage estimation."
    )
    row = make_row(
        "H2", rule, "deposit_change_qt_winsor", "lights_hat",
        ss_model, n_obs,
        f"district_state_id ({n_dist_fe})", n_qtr_fe,
        anchor_beta=anchor_b,
        anchor_p=anchor_p_val,
        note=note_str
    )
    h2_results.append(row)

# Drop temporary column
df_h2h4.drop(columns=["lights_hat"], inplace=True)

log(f"\n  H2 winsorized: {len(h2_results)} rows.")



# =============================================================================
# [8/11] H3 -- DISTRIBUTED LAG t-2 WINSORIZED
# =============================================================================
log("\n" + "=" * 70)
log("[8/11] H3: Distributed Lag t-2 -- Winsorized (Rule A and Rule B)")
log("=" * 70)
log("  Outcome: deposit_change_qt_winsor")
log("  FE:      quarter only (NO district FE -- H3 pre-committed spec)")
log("  SE:      clustered district_state_id")


h3_results = []

for rule, flood_var, anchor_b, anchor_p_val in [
    ("A", "flood_ruleA_L2", H3_ANCHOR["beta"], H3_ANCHOR["p"]),
    ("B", "flood_ruleB_L2", None,              None)
]:
    log(f"\n  H3 Rule {rule} t-2 -- winsorized")

    df_h3_rule = df[
        df["deposit_change_qt_winsor"].notna() &
        df[flood_var].notna()
    ].copy()
    df_h3_rule["quarter_fe"]        = pd.Categorical(df_h3_rule["quarter"])
    df_h3_rule["district_state_id"] = (
        df_h3_rule["district_gadm"] + "_" + df_h3_rule["state_gadm"]
    )
    n_rule     = len(df_h3_rule)
    n_qfe_rule = df_h3_rule["quarter_fe"].nunique()
    log(f"    N={n_rule:,}, Qtr FE={n_qfe_rule}")

    formula = f"deposit_change_qt_winsor ~ {flood_var} + C(quarter_fe)"
    model = ols(formula, data=df_h3_rule).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_h3_rule["district_state_id"]}
    )
    row = make_row(
        "H3", rule, "deposit_change_qt_winsor", flood_var,
        model, int(model.nobs),
        "NONE (H3 pre-committed spec)", n_qfe_rule,
        anchor_beta=anchor_b, anchor_p=anchor_p_val
    )
    h3_results.append(row)

log(f"\n  H3 winsorized: {len(h3_results)} rows.")



# =============================================================================
# [9/11] H4 -- HETEROGENEITY WINSORIZED
# =============================================================================
log("\n" + "=" * 70)
log("[9/11] H4: Heterogeneity -- Winsorized (H4a, H4b, H4c x Rule A and B)")
log("=" * 70)
log("  Outcome: deposit_change_qt_winsor")
log("  FE:      district_state_id + quarter (same as Script 30)")
log("  SE:      clustered district_state_id")
log("  Proxies: urban_proxy, high_exposure_proxy (constructed [4/11])")
log("  Note:    monsoon_quarter = 1 if q in [2, 3]")


h4_results = []

for rule in ["A", "B"]:
    flood_var = f"flood_exposure_rule{rule}_qt"
    log(f"\n  H4 Rule {rule} -- winsorized")

    # H4a: urban_proxy interaction
    log(f"    H4a Rule {rule}")
    interact_a = f"{flood_var}:urban_proxy"
    formula_h4a = (
        f"deposit_change_qt_winsor ~ {flood_var} + urban_proxy + "
        f"{flood_var}:urban_proxy + "
        "C(district_state_id) + C(quarter_fe)"
    )
    model_h4a = ols(formula_h4a, data=df_h2h4).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_h2h4["district_state_id"]}
    )
    row_h4a = make_row(
        "H4a", rule, "deposit_change_qt_winsor", interact_a,
        model_h4a, int(model_h4a.nobs),
        f"district_state_id ({n_dist_fe})", n_qtr_fe
    )
    h4_results.append(row_h4a)

    # H4b: high_exposure_proxy interaction
    log(f"    H4b Rule {rule}")
    interact_b = f"{flood_var}:high_exposure_proxy"
    formula_h4b = (
        f"deposit_change_qt_winsor ~ {flood_var} + high_exposure_proxy + "
        f"{flood_var}:high_exposure_proxy + "
        "C(district_state_id) + C(quarter_fe)"
    )
    model_h4b = ols(formula_h4b, data=df_h2h4).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_h2h4["district_state_id"]}
    )
    row_h4b = make_row(
        "H4b", rule, "deposit_change_qt_winsor", interact_b,
        model_h4b, int(model_h4b.nobs),
        f"district_state_id ({n_dist_fe})", n_qtr_fe,
        anchor_p=(H4b_ANCHOR["p"] if rule == "A" else None)
    )
    h4_results.append(row_h4b)

    # H4c: monsoon_quarter interaction
    log(f"    H4c Rule {rule}")
    interact_c = f"{flood_var}:monsoon_quarter"
    formula_h4c = (
        f"deposit_change_qt_winsor ~ {flood_var} + monsoon_quarter + "
        f"{flood_var}:monsoon_quarter + "
        "C(district_state_id) + C(quarter_fe)"
    )
    model_h4c = ols(formula_h4c, data=df_h2h4).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_h2h4["district_state_id"]}
    )
    row_h4c = make_row(
        "H4c", rule, "deposit_change_qt_winsor", interact_c,
        model_h4c, int(model_h4c.nobs),
        f"district_state_id ({n_dist_fe})", n_qtr_fe,
        anchor_p=(H4c_ANCHOR["p"] if rule == "A" else None)
    )
    h4_results.append(row_h4c)

assert len(h4_results) == 6, f"H4 rows = {len(h4_results)}, expected 6."
log(f"\n  H4 winsorized: {len(h4_results)} rows -- PASS")



# =============================================================================
# [10/11] VERDICT SUMMARY
# =============================================================================
log("\n" + "=" * 70)
log("[10/11] VERDICT SUMMARY")
log("=" * 70)


h2_a_p = h2_results[0]["p_value"]
h2_b_p = h2_results[1]["p_value"]
h3_a_p = h3_results[0]["p_value"]
h3_a_b = h3_results[0]["coefficient"]
h3_b_p = h3_results[1]["p_value"]


log(f"\n  H2 Rule A (winsor, 2SLS): p = {h2_a_p:.4f} {_stars(h2_a_p)}"
    f"  (main IV: p = {H2_ANCHOR['p']:.3f} null)")
log(f"  H2 Rule B (winsor, 2SLS): p = {h2_b_p:.4f} {_stars(h2_b_p)}"
    f"  [suggestive only -- F={H2_F_RULE_B} < 10]")
log(f"\n  H3 t-2 Rule A (winsor): beta = {h3_a_b:.6f}, p = {h3_a_p:.4f} "
    f"{_stars(h3_a_p)}  (main: beta = {H3_ANCHOR['beta']}, p < 0.001)")
log(f"  H3 t-2 Rule B (winsor): p = {h3_b_p:.4f} {_stars(h3_b_p)}")

log("")
for row in h4_results:
    log(f"  {row['hypothesis']} Rule {row['rule']} (winsor): "
        f"beta = {row['coefficient']:.6f}, p = {row['p_value']:.4f} "
        f"{row['significance'] if row['significance'] else 'null'}")

h3_robust = h3_a_p < 0.05

if h3_robust:
    log("\n  R3 VERDICT: ROBUST")
    log("  H3 t-2 significant on winsorized outcome.")
    log("  Winsorization does not drive or suppress the main result.")
    log("  Writing unblocked for H3.")
else:
    log("\n  R3 VERDICT: INVESTIGATE")
    log("  H3 t-2 loses significance on winsorized outcome.")
    log("  Main result may be sensitive to extreme observations. Investigate.")



# =============================================================================
# [11/11] SAVE AND COMPLETE
# =============================================================================
log("\n" + "=" * 70)
log("[11/11] SAVING OUTPUTS")
log("=" * 70)


h2_df = pd.DataFrame(h2_results)
assert len(h2_df) == 2, f"H2 table: expected 2 rows, got {len(h2_df)}"
h2_df.to_csv(OUT_H2, index=False)
assert os.path.exists(OUT_H2), f"H2 table not saved: {OUT_H2}"
log(f"\n  H2 table saved: {OUT_H2} ({len(h2_df)} rows) -- PASS")


h3_df = pd.DataFrame(h3_results)
assert len(h3_df) == 2, f"H3 table: expected 2 rows, got {len(h3_df)}"
h3_df.to_csv(OUT_H3, index=False)
assert os.path.exists(OUT_H3), f"H3 table not saved: {OUT_H3}"
log(f"  H3 table saved: {OUT_H3} ({len(h3_df)} rows) -- PASS")


h4_df = pd.DataFrame(h4_results)
assert len(h4_df) == 6, f"H4 table: expected 6 rows, got {len(h4_df)}"
h4_df.to_csv(OUT_H4, index=False)
assert os.path.exists(OUT_H4), f"H4 table not saved: {OUT_H4}"
log(f"  H4 table saved: {OUT_H4} ({len(h4_df)} rows) -- PASS")


with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
assert os.path.exists(LOG_PATH), f"Log not saved: {LOG_PATH}"
log(f"  Log saved:   {LOG_PATH} -- PASS")


log("\n" + "=" * 70)
log("SCRIPT 37 COMPLETE")
log(f"  H2 Rule A (winsor, 2SLS): p = {h2_results[0]['p_value']:.4f}  "
    f"{_stars(h2_results[0]['p_value'])}")
log(f"  H3 t-2 Rule A (winsor):   p = {h3_results[0]['p_value']:.4f}  "
    f"{_stars(h3_results[0]['p_value'])}")
log(f"  H4b Rule A (winsor):      p = {h4_results[1]['p_value']:.4f}  "
    f"{_stars(h4_results[1]['p_value'])}")
log(f"  H4c Rule A (winsor):      p = {h4_results[2]['p_value']:.4f}  "
    f"{_stars(h4_results[2]['p_value'])}")
log(f"  R3 verdict: {'ROBUST' if h3_robust else 'INVESTIGATE'}")
log(f"  Tables: {OUT_H2}, {OUT_H3}, {OUT_H4}")
log(f"  Log:    {LOG_PATH}")
log("=" * 70)
log("NEXT: Scripts 27b-30b -- linearmodels PanelOLS Final Tables")
log("=" * 70)
