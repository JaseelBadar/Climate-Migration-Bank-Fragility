"""
34_placebo_timing.py
Robustness R2: Placebo Timing -- Pre-Trend Falsification Check


Purpose:
    Pre-committed falsification check for H3 (Distributed Lag).
    Tests whether floods predict deposit changes that happened BEFORE
    the flood. Must return null for H3 t-2 result to be credible.


Two placebo tests:


    Test 1 -- Contemporaneous placebo:
        ΔDeposits_{t-1} = α + β·Flood_{t-1} + τ_t + ε
        i.e., deposit_change_L1 ~ flood_ruleA_L1 + C(quarter_fe)
        Logic: mirrors H3 t0 but shifted one period back. If H3 t0 is
        null (contemporaneous no-effect), this should also be null.
        Significant result = systematic pattern in data, not causal effect.


    Test 2 -- Pre-trend placebo:
        ΔDeposits_{t-1} = α + β·Flood_t + τ_t + ε
        i.e., deposit_change_L1 ~ flood_exposure_ruleA_qt + C(quarter_fe)
        Logic: current-quarter flood cannot causally affect last-quarter
        deposits. Significant result = pre-existing deposit trend coincides
        with flood timing. This directly falsifies H3 causal interpretation.


Both tests run under Rule A (primary) and Rule B (robustness).
Both must return null (p > 0.10) for H3 to remain credible.


Specification:
    Quarter FE only (NO district FE). Consistent with H3 design.
    SE: Clustered by district_state_id.


Reference: H3 locked result (Script 29, Rule A):
    t0:  beta = +0.000609, p = 0.677 -- null
    t-1: beta = +0.001505, p = 0.177 -- null
    t-2: beta = -0.007005, p < 0.001 *** CONFIRMED


If any placebo coefficient is significant at 5%, a warning is logged
and the result must be investigated before writing proceeds.


INPUT:  03_Data_Clean/regression_panel_final.csv  (23,347 x 23)
OUTPUT: 05_Outputs/Tables/09_placebo_timing.csv
        05_Outputs/Logs/34_placebo_timing_log.txt
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
OUT_TABLE  = "05_Outputs/Tables/09_placebo_timing.csv"
LOG_PATH   = "05_Outputs/Logs/34_placebo_timing_log.txt"


# H3 locked results for comparison (Script 29, Rule A)
H3_ANCHORS = {
    "t0":  {"beta": +0.000609, "p": 0.677},
    "t-1": {"beta": +0.001505, "p": 0.177},
    "t-2": {"beta": -0.007005, "p": 0.000}
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
log("SCRIPT 34: ROBUSTNESS R2 -- PLACEBO TIMING")
log("Pre-trend falsification check for H3 distributed lag result.")
log(f"Run: {run_ts}")
log("=" * 70)
log("LOGIC: If H3 t-2 is causal (floods -> deposits 2Q later),")
log("  floods must NOT predict deposit changes that already occurred.")
log("  Both placebo tests must return null (p > 0.10).")
log("  If significant: pre-existing trend problem. H3 result suspect.")
log("=" * 70)



# =============================================================================
# [1/7] LOAD AND ASSERT INPUT
# =============================================================================
log("\n[1/7] Loading regression panel...")


df = pd.read_csv(INPUT_PATH)


assert len(df) == 23347,  f"Expected 23,347 rows, got {len(df):,}. Check upstream pipeline."
assert df.shape[1] == 23, f"Expected 23 columns, got {df.shape[1]}. Check upstream pipeline."


required_cols = [
    "district_gadm", "state_gadm", "quarter", "year", "q",
    "deposit_change_qt",
    "flood_exposure_ruleA_qt", "flood_ruleA_L1", "flood_ruleA_L2",
    "flood_exposure_ruleB_qt", "flood_ruleB_L1", "flood_ruleB_L2"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")


n_rows = len(df)
n_cols = df.shape[1]
log(f"  Loaded: {n_rows:,} rows, {n_cols} columns -- PASS")
log("  Required columns verified -- PASS")



# =============================================================================
# [2/7] COMPOSITE KEY
# =============================================================================
log("\n[2/7] Constructing and verifying composite key...")


df["district_state_id"] = df["district_gadm"] + "_" + df["state_gadm"]
n_districts = df["district_state_id"].nunique()
log(f"  district_state_id: {n_districts} unique pairs (expected 631)")


if n_districts != 631:
    raise ValueError(
        f"District count = {n_districts}, expected 631. "
        f"Check composite key or upstream pipeline."
    )
log("  Composite key verified -- PASS")



# =============================================================================
# [3/7] VERIFY PRE-EXISTING LAG ARITHMETIC
# =============================================================================
log("\n[3/7] Verifying pre-existing lag arithmetic (Script 24 columns)...")


nan_A_L1    = df["flood_ruleA_L1"].isna().sum()
nan_A_L2    = df["flood_ruleA_L2"].isna().sum()
nan_B_L1    = df["flood_ruleB_L1"].isna().sum()
nan_B_L2    = df["flood_ruleB_L2"].isna().sum()
nan_flood_A = df["flood_exposure_ruleA_qt"].isna().sum()
nan_flood_B = df["flood_exposure_ruleB_qt"].isna().sum()


log(f"  flood_exposure_ruleA_qt NaN: {nan_flood_A}        (expected 0)")
log(f"  flood_exposure_ruleB_qt NaN: {nan_flood_B}        (expected 0)")
log(f"  flood_ruleA_L1          NaN: {nan_A_L1}      (expected 631)")
log(f"  flood_ruleA_L2          NaN: {nan_A_L2}    (expected 1,262)")
log(f"  flood_ruleB_L1          NaN: {nan_B_L1}      (expected 631)")
log(f"  flood_ruleB_L2          NaN: {nan_B_L2}    (expected 1,262)")


assert nan_flood_A == 0,   f"flood_exposure_ruleA_qt has {nan_flood_A} NaN. Expected 0."
assert nan_flood_B == 0,   f"flood_exposure_ruleB_qt has {nan_flood_B} NaN. Expected 0."
assert nan_A_L1 == 631,    f"flood_ruleA_L1 NaN = {nan_A_L1}, expected 631. Composite key error."
assert nan_A_L2 == 1262,   f"flood_ruleA_L2 NaN = {nan_A_L2}, expected 1,262. Composite key error."
assert nan_B_L1 == 631,    f"flood_ruleB_L1 NaN = {nan_B_L1}, expected 631."
assert nan_B_L2 == 1262,   f"flood_ruleB_L2 NaN = {nan_B_L2}, expected 1,262."


log("  Pre-existing lag arithmetic verified -- PASS")



# =============================================================================
# [4/7] CONSTRUCT deposit_change_L1
# =============================================================================
log("\n[4/7] Constructing deposit_change_L1 (lagged dependent variable)...")
log("  Method: deposit_change_qt.shift(1) within composite groups.")
log("  Sort: district_gadm, state_gadm, year, q (pre-committed sort order).")
log("  CRITICAL: sort applied before shift -- matches Script 24 sort convention.")


df = df.sort_values(
    ["district_gadm", "state_gadm", "year", "q"]
).reset_index(drop=True)


df["deposit_change_L1"] = (
    df.groupby("district_state_id")["deposit_change_qt"]
    .shift(1)
)


nan_dep_L1   = df["deposit_change_L1"].isna().sum()
nan_dep_qt   = df["deposit_change_qt"].isna().sum()
valid_dep_L1 = df["deposit_change_L1"].notna().sum()


log(f"  deposit_change_qt   NaN: {nan_dep_qt:,}   (reference: 905 expected)")
log(f"  deposit_change_L1   NaN: {nan_dep_L1:,}   (expected >= 1,262)")
log(f"  deposit_change_L1 valid: {valid_dep_L1:,}")


# Row 1 per district: shift always NaN (631 structural).
# Row 2 per district: shift(1) of row 1 = NaN if row 1 was NaN (631 more).
# Minimum structural NaN = 1,262 = 631 x 2.
assert nan_dep_L1 >= 1262, (
    f"deposit_change_L1 NaN = {nan_dep_L1}, expected >= 1,262. "
    f"Sort or shift error -- check composite group sort order."
)


# Sanity bound: valid obs must be > 15,000 to catch catastrophic failure.
assert valid_dep_L1 > 15000, (
    f"deposit_change_L1 valid obs = {valid_dep_L1:,}, below catastrophic "
    f"failure threshold 15,000. Check shift construction."
)


log("  deposit_change_L1 construction verified -- PASS")



# =============================================================================
# [5/7] ENCODE QUARTER FE
# =============================================================================
log("\n[5/7] Encoding quarter FE...")


df["quarter_fe"] = pd.Categorical(df["quarter"])
n_qfe = df["quarter_fe"].nunique()
log(f"  Quarter FE levels: {n_qfe} (expected 37 -- full analysis period)")


# Unlike H3 (QFE=35 due to L2 restriction), this placebo has outcome=
# deposit_change_L1 and does NOT impose a 2-lag restriction.
# QFE will be 37 or 36 depending on which quarters survive dropna().
if n_qfe < 33 or n_qfe > 38:
    raise ValueError(
        f"Quarter FE count = {n_qfe}, outside expected range [33, 38]."
    )
log("  Quarter FE verified -- PASS")



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


def log_coef(label, coef, se, tstat, pval, ci_lo, ci_hi, sig):
    log(f"    [{label}]")
    log(f"      Beta   = {coef:.6f}")
    log(f"      SE     = {se:.6f}")
    log(f"      t      = {tstat:.3f}")
    log(f"      p      = {pval:.6f}")
    log(f"      95% CI = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log(f"      Status = {sig if sig else 'NOT SIGNIFICANT'}")


def run_placebo(df_sub, formula, regressor_var):
    try:
        model = ols(formula, data=df_sub).fit(
            cov_type="cluster",
            cov_kwds={"groups": df_sub["district_state_id"]}
        )
        n_obs = int(model.nobs)
        r2    = model.rsquared
        log(f"  Model fitted: N={n_obs:,}, R2={r2:.4f} -- PASS")
    except Exception as e:
        log(f"  FAILED: {e}")
        raise
    return model, extract_coef(model, regressor_var)



# =============================================================================
# [6/7] RUN PLACEBO REGRESSIONS
# =============================================================================
log("\n" + "=" * 70)
log("[6/7] PLACEBO REGRESSIONS")
log("=" * 70)
log("  Outcome: deposit_change_L1 (lagged deposit growth)")
log("  FE:      Quarter only (NO district FE -- consistent with H3)")
log("  SE:      Clustered by district_state_id")
log("  Both tests must be null (p > 0.10) for H3 to remain credible.")


results = []


# -----------------------------------------------------------------------
# TEST 1: Contemporaneous placebo -- flood_{t-1} -> deposit_change_{t-1}
# -----------------------------------------------------------------------
log("\n" + "-" * 70)
log("TEST 1: Contemporaneous placebo")
log("  ΔDeposits_{t-1} = α + β·Flood_{t-1} + τ_t + ε")
log("  Regressor: flood_ruleA_L1 (flood at t-1)")
log("  Outcome:   deposit_change_L1 (deposit change at t-1)")
log("  Logic: mirrors H3 t0 but one period earlier. Must be null.")
log("-" * 70)


for rule in ["A", "B"]:
    flood_var = "flood_ruleA_L1" if rule == "A" else "flood_ruleB_L1"
    log(f"\n  Test 1 Rule {rule}: deposit_change_L1 ~ {flood_var} + C(quarter_fe)")

    df_t1    = df[df["deposit_change_L1"].notna() & df[flood_var].notna()].copy()
    n_t1     = len(df_t1)
    n_qfe_t1 = df_t1["quarter_fe"].nunique()
    log(f"  Complete cases: {n_t1:,}")
    log(f"  Quarter FE:     {n_qfe_t1}")

    assert n_t1 > 15000, f"Test 1 Rule {rule}: only {n_t1:,} complete cases. Check pipeline."

    formula_t1 = f"deposit_change_L1 ~ {flood_var} + C(quarter_fe)"
    model_t1, (c, s, t, p, lo, hi, sg) = run_placebo(df_t1, formula_t1, flood_var)
    log_coef(f"Test 1 Rule {rule}: {flood_var}", c, s, t, p, lo, hi, sg)

    verdict = "NULL -- PASS" if p > 0.10 else (
        "MARGINAL -- MONITOR" if p > 0.05 else "WARNING -- SIGNIFICANT: INVESTIGATE"
    )
    log(f"      VERDICT: {verdict}")

    results.append({
        "test":             "Test1_Contemporaneous",
        "rule":             rule,
        "outcome":          "deposit_change_L1",
        "regressor":        flood_var,
        "description":      "Flood_t-1 predicts DepositChange_t-1 (must be null)",
        "coefficient":      round(c,  6),
        "std_error":        round(s,  6),
        "t_statistic":      round(t,  3),
        "p_value":          round(p,  6),
        "ci_lower_95":      round(lo, 6),
        "ci_upper_95":      round(hi, 6),
        "significance":     sg,
        "n_obs":            int(model_t1.nobs),
        "r_squared":        round(model_t1.rsquared, 4),
        "quarter_fe_count": n_qfe_t1,
        "district_fe":      "NONE (consistent with H3 pre-committed spec)",
        "se_type":          "clustered_by_district_state_id",
        "verdict":          verdict
    })


# -----------------------------------------------------------------------
# TEST 2: Pre-trend placebo -- flood_t -> deposit_change_{t-1}
# -----------------------------------------------------------------------
log("\n" + "-" * 70)
log("TEST 2: Pre-trend placebo (stronger falsification)")
log("  ΔDeposits_{t-1} = α + β·Flood_t + τ_t + ε")
log("  Regressor: flood_exposure_ruleA_qt (flood at t)")
log("  Outcome:   deposit_change_L1 (deposit change at t-1)")
log("  Logic: current flood CANNOT causally affect LAST quarter deposits.")
log("  Significant result = pre-existing trend. H3 causal claim fails.")
log("-" * 70)


for rule in ["A", "B"]:
    flood_var = "flood_exposure_ruleA_qt" if rule == "A" else "flood_exposure_ruleB_qt"
    log(f"\n  Test 2 Rule {rule}: deposit_change_L1 ~ {flood_var} + C(quarter_fe)")

    df_t2    = df[df["deposit_change_L1"].notna() & df[flood_var].notna()].copy()
    n_t2     = len(df_t2)
    n_qfe_t2 = df_t2["quarter_fe"].nunique()
    log(f"  Complete cases: {n_t2:,}")
    log(f"  Quarter FE:     {n_qfe_t2}")

    assert n_t2 > 15000, f"Test 2 Rule {rule}: only {n_t2:,} complete cases. Check pipeline."

    formula_t2 = f"deposit_change_L1 ~ {flood_var} + C(quarter_fe)"
    model_t2, (c, s, t, p, lo, hi, sg) = run_placebo(df_t2, formula_t2, flood_var)
    log_coef(f"Test 2 Rule {rule}: {flood_var}", c, s, t, p, lo, hi, sg)

    verdict = "NULL -- PASS" if p > 0.10 else (
        "MARGINAL -- MONITOR" if p > 0.05 else "WARNING -- SIGNIFICANT: INVESTIGATE"
    )
    log(f"      VERDICT: {verdict}")

    results.append({
        "test":             "Test2_PreTrend",
        "rule":             rule,
        "outcome":          "deposit_change_L1",
        "regressor":        flood_var,
        "description":      "Flood_t predicts DepositChange_t-1 (causal impossibility test)",
        "coefficient":      round(c,  6),
        "std_error":        round(s,  6),
        "t_statistic":      round(t,  3),
        "p_value":          round(p,  6),
        "ci_lower_95":      round(lo, 6),
        "ci_upper_95":      round(hi, 6),
        "significance":     sg,
        "n_obs":            int(model_t2.nobs),
        "r_squared":        round(model_t2.rsquared, 4),
        "quarter_fe_count": n_qfe_t2,
        "district_fe":      "NONE (consistent with H3 pre-committed spec)",
        "se_type":          "clustered_by_district_state_id",
        "verdict":          verdict
    })



# =============================================================================
# [7/7] SIDE-BY-SIDE SUMMARY, VERDICT, AND SAVE
# =============================================================================
log("\n" + "=" * 70)
log("[7/7] FINAL SUMMARY AND VERDICT")
log("=" * 70)


log("\n  Reference: H3 main results (Script 29, Rule A):")
log(f"    t0:  beta = {H3_ANCHORS['t0']['beta']:+.6f},  p = {H3_ANCHORS['t0']['p']:.3f}  null")
log(f"    t-1: beta = {H3_ANCHORS['t-1']['beta']:+.6f},  p = {H3_ANCHORS['t-1']['p']:.3f}  null")
log(f"    t-2: beta = {H3_ANCHORS['t-2']['beta']:+.6f},  p = {H3_ANCHORS['t-2']['p']:.3f}  *** CONFIRMED")


log("\n  Placebo results:")
log(f"  {'Test':<28} {'Rule':<6} {'Beta':>12} {'p':>10} {'Verdict'}")
log(f"  {'-'*72}")


all_null = True
any_sig  = False


for r in results:
    test_short = "Contemp (T1)" if r["test"] == "Test1_Contemporaneous" else "Pre-trend (T2)"
    beta_val   = r["coefficient"]
    p_val      = r["p_value"]
    verdict    = r["verdict"]
    rule_label = r["rule"]
    log(f"  {test_short:<28} {rule_label:<6} {beta_val:>12.6f} {p_val:>10.6f}  {verdict}")
    if p_val < 0.05:
        all_null = False
        any_sig  = True


log("\n  CRITICAL VERDICT:")
if all_null:
    log("  ALL PLACEBO TESTS NULL -- PASS")
    log("  No pre-trend detected. H3 t-2 result is not driven by pre-existing")
    log("  deposit trends or reverse causality. Causal interpretation credible.")
    log("  WRITING IS UNBLOCKED on the H3 causal narrative.")
else:
    log("  WARNING: ONE OR MORE PLACEBO TESTS SIGNIFICANT.")
    log("  Pre-trend problem detected. H3 t-2 causal interpretation is suspect.")
    log("  DO NOT write H3 results as causal until this is investigated.")
    log("  ACTION REQUIRED: Check for deposit autocorrelation, flood clustering,")
    log("  or structural breaks that coincide with flood timing.")


# Save outputs
results_df = pd.DataFrame(results)


assert len(results_df) == 4, (
    f"Expected 4 rows in output (2 tests x 2 rules), got {len(results_df)}."
)


results_df.to_csv(OUT_TABLE, index=False)
assert os.path.exists(OUT_TABLE), f"Output table not saved: {OUT_TABLE}"
log(f"\n  Table saved: {OUT_TABLE}  ({len(results_df)} rows) -- PASS")


with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
assert os.path.exists(LOG_PATH), f"Log not saved: {LOG_PATH}"
log(f"  Log saved:   {LOG_PATH} -- PASS")


# === COMPLETION ===
log("\n" + "=" * 70)
log("SCRIPT 34 COMPLETE")
log(f"  All null:    {'YES -- R2 PASSED' if all_null else 'NO -- INVESTIGATE'}")
log(f"  Any sig:     {'NO' if not any_sig else 'YES -- WARNING'}")
log(f"  Table: {OUT_TABLE}")
log(f"  Log:   {LOG_PATH}")
log("=" * 70)
log("NEXT: Script 35 -- R5 Longer Lags (t-3, t-4, Rule B)")
log("=" * 70)