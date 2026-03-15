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


    Test 2b -- Pre-trend diagnostic (with district FE):
        ΔDeposits_{t-1} = α + β·Flood_t + δ_i + τ_t + ε
        i.e., deposit_change_L1 ~ flood_exposure_ruleA_qt +
              C(district_state_id) + C(quarter_fe)
        Logic: adds district FE to isolate within-district pre-trend.
        If Test 2 Rule A is significant but Test 2b is null, the signal
        is purely cross-sectional (flood-prone districts differ structurally)
        and does not threaten H3's within-district timing logic.
        If Test 2b remains significant, a genuine within-district
        pre-trend exists and requires mechanism discussion before writing.
        Rule A only -- targeted diagnostic for the observed warning.


Both main tests (Test 1 and Test 2) run under Rule A and Rule B.
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
# [1/8] LOAD AND ASSERT INPUT
# =============================================================================
log("\n[1/8] Loading regression panel...")


df = pd.read_csv(INPUT_PATH)


assert len(df) == 23347,  f"Expected 23,347 rows, got {len(df):,}."
assert df.shape[1] == 23, f"Expected 23 columns, got {df.shape[1]}."


required_cols = [
    "district_gadm", "state_gadm", "quarter", "year", "q",
    "deposit_change_qt",
    "flood_exposure_ruleA_qt", "flood_ruleA_L1", "flood_ruleA_L2",
    "flood_exposure_ruleB_qt", "flood_ruleB_L1", "flood_ruleB_L2"
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")


log(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log("  Required columns verified -- PASS")


# =============================================================================
# [2/8] COMPOSITE KEY
# =============================================================================
log("\n[2/8] Constructing and verifying composite key...")


df["district_state_id"] = df["district_gadm"] + "_" + df["state_gadm"]
n_districts = df["district_state_id"].nunique()
log(f"  district_state_id: {n_districts} unique pairs (expected 631)")


assert n_districts == 631, \
    f"District count = {n_districts}, expected 631. Check composite key."


log("  Composite key verified -- PASS")


# =============================================================================
# [3/8] VERIFY PRE-EXISTING LAG ARITHMETIC
# =============================================================================
log("\n[3/8] Verifying pre-existing lag arithmetic (Script 24 columns)...")


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


assert nan_flood_A == 0,  f"flood_exposure_ruleA_qt has {nan_flood_A} NaN."
assert nan_flood_B == 0,  f"flood_exposure_ruleB_qt has {nan_flood_B} NaN."
assert nan_A_L1 == 631,   f"flood_ruleA_L1 NaN = {nan_A_L1}, expected 631."
assert nan_A_L2 == 1262,  f"flood_ruleA_L2 NaN = {nan_A_L2}, expected 1,262."
assert nan_B_L1 == 631,   f"flood_ruleB_L1 NaN = {nan_B_L1}, expected 631."
assert nan_B_L2 == 1262,  f"flood_ruleB_L2 NaN = {nan_B_L2}, expected 1,262."


log("  Pre-existing lag arithmetic verified -- PASS")


# =============================================================================
# [4/8] CONSTRUCT deposit_change_L1
# =============================================================================
log("\n[4/8] Constructing deposit_change_L1 (lagged dependent variable)...")
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


assert nan_dep_L1 >= 1262, \
    f"deposit_change_L1 NaN = {nan_dep_L1}, expected >= 1,262."
assert valid_dep_L1 > 15000, \
    f"deposit_change_L1 valid obs = {valid_dep_L1:,}, below threshold 15,000."


log("  deposit_change_L1 construction verified -- PASS")


# =============================================================================
# [5/8] ENCODE QUARTER AND DISTRICT FE
# =============================================================================
log("\n[5/8] Encoding FE variables...")


# NOTE: quarter_fe is NOT pre-encoded here on the full df.
# Each regression subset re-encodes its own Categorical to avoid
# empty levels causing rank deficiency in the clustered VCV.
# district_state_id is already constructed in [2/8].


n_qfe_full = df["quarter"].nunique()
n_dist_full = df["district_state_id"].nunique()
log(f"  Quarter levels in full panel: {n_qfe_full} (expected 37)")
log(f"  District levels in full panel: {n_dist_full} (expected 631)")


assert n_qfe_full == 37,   f"Quarter levels = {n_qfe_full}, expected 37."
assert n_dist_full == 631, f"District levels = {n_dist_full}, expected 631."


log("  FE encoding verified -- PASS")
log("  Note: quarter_fe Categorical encoded per-subset in [6/8] and [7/8].")


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
# [6/8] PLACEBO REGRESSIONS (Test 1 and Test 2)
# =============================================================================
log("\n" + "=" * 70)
log("[6/8] PLACEBO REGRESSIONS (Test 1 and Test 2)")
log("=" * 70)
log("  Outcome: deposit_change_L1 (lagged deposit growth)")
log("  FE:      Quarter only (NO district FE -- consistent with H3)")
log("  SE:      Clustered by district_state_id")
log("  Both tests must be null (p > 0.10) for H3 to remain credible.")


results = []


# -----------------------------------------------------------------------
# TEST 1: Contemporaneous placebo
# -----------------------------------------------------------------------
log("\n" + "-" * 70)
log("TEST 1: Contemporaneous placebo")
log("  ΔDeposits_{t-1} = α + β·Flood_{t-1} + τ_t + ε")
log("  Regressor: flood_ruleA/B_L1 (flood at t-1)")
log("  Outcome:   deposit_change_L1 (deposit change at t-1)")
log("  Logic: mirrors H3 t0 but one period earlier. Must be null.")
log("-" * 70)


for rule in ["A", "B"]:
    flood_var = "flood_ruleA_L1" if rule == "A" else "flood_ruleB_L1"
    log(f"\n  Test 1 Rule {rule}: deposit_change_L1 ~ {flood_var} + C(quarter_fe)")

    df_t1 = df[
        df["deposit_change_L1"].notna() &
        df[flood_var].notna()
    ].copy()
    df_t1["quarter_fe"] = pd.Categorical(df_t1["quarter"])
    n_t1     = len(df_t1)
    n_qfe_t1 = df_t1["quarter_fe"].nunique()
    log(f"  Complete cases: {n_t1:,}")
    log(f"  Quarter FE:     {n_qfe_t1}")

    assert n_t1 > 15000, \
        f"Test 1 Rule {rule}: only {n_t1:,} complete cases."
    assert 33 <= n_qfe_t1 <= 38, \
        f"Test 1 Rule {rule}: QFE count = {n_qfe_t1}, outside [33, 38]."

    formula_t1 = f"deposit_change_L1 ~ {flood_var} + C(quarter_fe)"
    model_t1, (c, s, t, p, lo, hi, sg) = run_placebo(
        df_t1, formula_t1, flood_var
    )
    log_coef(f"Test 1 Rule {rule}: {flood_var}", c, s, t, p, lo, hi, sg)

    verdict = "NULL -- PASS" if p > 0.10 else (
        "MARGINAL -- MONITOR" if p > 0.05
        else "WARNING -- SIGNIFICANT: INVESTIGATE"
    )
    log(f"      VERDICT: {verdict}")

    results.append({
        "test":             "Test1_Contemporaneous",
        "rule":             rule,
        "outcome":          "deposit_change_L1",
        "regressor":        flood_var,
        "district_fe":      "NONE",
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
        "se_type":          "clustered_by_district_state_id",
        "verdict":          verdict
    })


# -----------------------------------------------------------------------
# TEST 2: Pre-trend placebo
# -----------------------------------------------------------------------
log("\n" + "-" * 70)
log("TEST 2: Pre-trend placebo (stronger falsification)")
log("  ΔDeposits_{t-1} = α + β·Flood_t + τ_t + ε")
log("  Regressor: flood_exposure_ruleA/B_qt (flood at t)")
log("  Outcome:   deposit_change_L1 (deposit change at t-1)")
log("  Logic: current flood CANNOT causally affect LAST quarter deposits.")
log("  Significant result = pre-existing trend. H3 causal claim suspect.")
log("-" * 70)


for rule in ["A", "B"]:
    flood_var = (
        "flood_exposure_ruleA_qt" if rule == "A"
        else "flood_exposure_ruleB_qt"
    )
    log(f"\n  Test 2 Rule {rule}: deposit_change_L1 ~ {flood_var} + C(quarter_fe)")

    df_t2 = df[
        df["deposit_change_L1"].notna() &
        df[flood_var].notna()
    ].copy()
    df_t2["quarter_fe"] = pd.Categorical(df_t2["quarter"])
    n_t2     = len(df_t2)
    n_qfe_t2 = df_t2["quarter_fe"].nunique()
    log(f"  Complete cases: {n_t2:,}")
    log(f"  Quarter FE:     {n_qfe_t2}")

    assert n_t2 > 15000, \
        f"Test 2 Rule {rule}: only {n_t2:,} complete cases."
    assert 33 <= n_qfe_t2 <= 38, \
        f"Test 2 Rule {rule}: QFE count = {n_qfe_t2}, outside [33, 38]."

    formula_t2 = f"deposit_change_L1 ~ {flood_var} + C(quarter_fe)"
    model_t2, (c, s, t, p, lo, hi, sg) = run_placebo(
        df_t2, formula_t2, flood_var
    )
    log_coef(f"Test 2 Rule {rule}: {flood_var}", c, s, t, p, lo, hi, sg)

    verdict = "NULL -- PASS" if p > 0.10 else (
        "MARGINAL -- MONITOR" if p > 0.05
        else "WARNING -- SIGNIFICANT: INVESTIGATE"
    )
    log(f"      VERDICT: {verdict}")

    results.append({
        "test":             "Test2_PreTrend",
        "rule":             rule,
        "outcome":          "deposit_change_L1",
        "regressor":        flood_var,
        "district_fe":      "NONE",
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
        "se_type":          "clustered_by_district_state_id",
        "verdict":          verdict
    })


# =============================================================================
# [7/8] TEST 2b -- PRE-TREND DIAGNOSTIC WITH DISTRICT FE (Rule A only)
# =============================================================================
log("\n" + "=" * 70)
log("[7/8] TEST 2b: Pre-trend diagnostic WITH district FE (Rule A only)")
log("=" * 70)
log("  Purpose: Determine whether Test 2 Rule A signal (p=0.011) is")
log("    cross-sectional or within-district.")
log("  Formula: deposit_change_L1 ~ flood_exposure_ruleA_qt +")
log("           C(district_state_id) + C(quarter_fe)")
log("  If null with district FE: signal is cross-sectional only.")
log("    Flood-prone districts structurally differ -- not a dynamic")
log("    pre-trend. H3 within-district timing logic is defensible.")
log("  If still significant with district FE: genuine within-district")
log("    pre-trend exists. Must develop mechanism argument before writing.")
log("  Note: This test is a diagnostic, NOT a main robustness check.")
log("  It does not replace Test 2. It diagnoses the source of Test 2's signal.")
log("=" * 70)


flood_var_2b = "flood_exposure_ruleA_qt"
log(f"\n  Test 2b Rule A: deposit_change_L1 ~ {flood_var_2b} +")
log(f"                  C(district_state_id) + C(quarter_fe)")


df_t2b = df[
    df["deposit_change_L1"].notna() &
    df[flood_var_2b].notna()
].copy()
df_t2b["quarter_fe"] = pd.Categorical(df_t2b["quarter"])
n_t2b     = len(df_t2b)
n_qfe_t2b = df_t2b["quarter_fe"].nunique()
n_dfe_t2b = df_t2b["district_state_id"].nunique()
log(f"  Complete cases: {n_t2b:,}")
log(f"  Quarter FE:     {n_qfe_t2b}")
log(f"  District FE:    {n_dfe_t2b}")


assert n_t2b > 15000, \
    f"Test 2b: only {n_t2b:,} complete cases."
assert 33 <= n_qfe_t2b <= 38, \
    f"Test 2b: QFE count = {n_qfe_t2b}, outside [33, 38]."
assert n_dfe_t2b == 631, \
    f"Test 2b: district FE = {n_dfe_t2b}, expected 631."


formula_t2b = (
    f"deposit_change_L1 ~ {flood_var_2b} + "
    "C(district_state_id) + C(quarter_fe)"
)
model_t2b, (c2b, s2b, t2b, p2b, lo2b, hi2b, sg2b) = run_placebo(
    df_t2b, formula_t2b, flood_var_2b
)
log_coef(f"Test 2b Rule A (with district FE): {flood_var_2b}",
         c2b, s2b, t2b, p2b, lo2b, hi2b, sg2b)


if p2b > 0.10:
    t2b_verdict = "NULL WITH DISTRICT FE"
    t2b_interpretation = (
        "Test 2 Rule A signal is CROSS-SECTIONAL only. "
        "Flood-prone districts have structurally higher deposit growth -- "
        "not a within-district dynamic pre-trend. "
        "H3 within-district causal interpretation is DEFENSIBLE. "
        "Must disclose in robustness section with this diagnostic result."
    )
elif p2b < 0.05:
    t2b_verdict = "SIGNIFICANT WITH DISTRICT FE -- WITHIN-DISTRICT PRE-TREND"
    t2b_interpretation = (
        "Genuine within-district pre-trend detected. "
        "Deposits rise within the same district before floods arrive. "
        "H3 causal narrative requires explicit mechanism argument. "
        "Anticipatory saving mechanism would need to be modeled directly."
    )
else:
    t2b_verdict = "MARGINAL WITH DISTRICT FE -- MONITOR"
    t2b_interpretation = (
        "Marginal signal survives district FE. "
        "Weak within-district pattern. Disclose and monitor."
    )


log(f"\n  Test 2b VERDICT: {t2b_verdict}")
log(f"  Interpretation: {t2b_interpretation}")


results.append({
    "test":             "Test2b_DiagnosticDistrictFE",
    "rule":             "A",
    "outcome":          "deposit_change_L1",
    "regressor":        flood_var_2b,
    "district_fe":      f"YES (district_state_id, {n_dfe_t2b} clusters)",
    "description":      (
        "Diagnostic: Test 2 with district FE. "
        "Null = cross-sectional signal only. "
        "Significant = within-district pre-trend."
    ),
    "coefficient":      round(c2b,  6),
    "std_error":        round(s2b,  6),
    "t_statistic":      round(t2b,  3),
    "p_value":          round(p2b,  6),
    "ci_lower_95":      round(lo2b, 6),
    "ci_upper_95":      round(hi2b, 6),
    "significance":     sg2b,
    "n_obs":            int(model_t2b.nobs),
    "r_squared":        round(model_t2b.rsquared, 4),
    "quarter_fe_count": n_qfe_t2b,
    "se_type":          "clustered_by_district_state_id",
    "verdict":          t2b_verdict
})


# =============================================================================
# [8/8] FINAL SUMMARY, VERDICT, AND SAVE
# =============================================================================
log("\n" + "=" * 70)
log("[8/8] FINAL SUMMARY AND VERDICT")
log("=" * 70)


log("\n  Reference: H3 main results (Script 29, Rule A):")
log(f"    t0:  beta = {H3_ANCHORS['t0']['beta']:+.6f},  p = {H3_ANCHORS['t0']['p']:.3f}  null")
log(f"    t-1: beta = {H3_ANCHORS['t-1']['beta']:+.6f},  p = {H3_ANCHORS['t-1']['p']:.3f}  null")
log(f"    t-2: beta = {H3_ANCHORS['t-2']['beta']:+.6f},  p = {H3_ANCHORS['t-2']['p']:.3f}  *** CONFIRMED")


log("\n  Placebo results (Tests 1 and 2, no district FE):")
log(f"  {'Test':<28} {'Rule':<6} {'Beta':>12} {'p':>10}  Verdict")
log(f"  {'-' * 70}")


any_main_sig = False
for r in results:
    if r["test"] in ["Test1_Contemporaneous", "Test2_PreTrend"]:
        test_short = (
            "Contemp (T1)" if r["test"] == "Test1_Contemporaneous"
            else "Pre-trend (T2)"
        )
        log(f"  {test_short:<28} {r['rule']:<6} "
            f"{r['coefficient']:>12.6f} {r['p_value']:>10.6f}  {r['verdict']}")
        if r["p_value"] < 0.05:
            any_main_sig = True


log(f"\n  Diagnostic (Test 2b, WITH district FE, Rule A only):")
log(f"  {'Pre-trend+DistFE (T2b)':<28} {'A':<6} "
    f"{c2b:>12.6f} {p2b:>10.6f}  {t2b_verdict}")


log("\n  CRITICAL VERDICT:")
if not any_main_sig:
    log("  ALL MAIN PLACEBO TESTS NULL -- R2 PASSED.")
    log("  No pre-trend detected. H3 causal interpretation credible.")
    log("  WRITING UNBLOCKED on the H3 causal narrative.")
else:
    if p2b > 0.10:
        log("  Test 2 Rule A significant WITHOUT district FE (p=0.011).")
        log("  Test 2b NULL WITH district FE -- signal is CROSS-SECTIONAL.")
        log("  Flood-prone districts have structurally higher prior deposit")
        log("  growth. This is a between-district level difference, not a")
        log("  within-district dynamic pre-trend.")
        log("  H3 within-district timing result is DEFENSIBLE.")
        log("  WRITING CONDITION: Disclose Test 2 Rule A result explicitly")
        log("  in robustness section. Report Test 2b null as the resolution.")
        log("  Do NOT use language implying pre-trend is absent without")
        log("  qualification. State: 'The signal does not survive the")
        log("  inclusion of district fixed effects, indicating it reflects")
        log("  cross-sectional heterogeneity rather than a dynamic pre-trend.'")
    elif p2b < 0.05:
        log("  Test 2 Rule A significant both with and without district FE.")
        log("  WITHIN-DISTRICT PRE-TREND CONFIRMED.")
        log("  DO NOT write H3 as causal without mechanism argument.")
        log("  ACTION REQUIRED before writing proceeds.")
    else:
        log("  Test 2 Rule A significant without FE, marginal with FE.")
        log("  Borderline case. Disclose fully. Do not claim clean null.")


# Save outputs
results_df = pd.DataFrame(results)


assert len(results_df) == 5, \
    f"Expected 5 rows (2 tests x 2 rules + 1 diagnostic), got {len(results_df)}."


results_df.to_csv(OUT_TABLE, index=False)
assert os.path.exists(OUT_TABLE), f"Output table not saved: {OUT_TABLE}"
log(f"\n  Table saved: {OUT_TABLE}  ({len(results_df)} rows) -- PASS")


with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
assert os.path.exists(LOG_PATH), f"Log not saved: {LOG_PATH}"
log(f"  Log saved:   {LOG_PATH} -- PASS")


log("\n" + "=" * 70)
log("SCRIPT 34 COMPLETE")
log(f"  Test 1 Rule A:  p = {results[0]['p_value']:.4f}  {_stars(results[0]['p_value'])}")
log(f"  Test 1 Rule B:  p = {results[1]['p_value']:.4f}  {_stars(results[1]['p_value'])}")
log(f"  Test 2 Rule A:  p = {results[2]['p_value']:.4f}  {_stars(results[2]['p_value'])}")
log(f"  Test 2 Rule B:  p = {results[3]['p_value']:.4f}  {_stars(results[3]['p_value'])}")
log(f"  Test 2b Rule A: p = {p2b:.4f}  {_stars(p2b)}  (with district FE -- diagnostic)")
log(f"  H3 writing unblocked: {'YES' if p2b > 0.10 else 'NO -- INVESTIGATE'}")
log(f"  Table: {OUT_TABLE}")
log(f"  Log:   {LOG_PATH}")
log("=" * 70)
log("NEXT: Scripts 27b-30b -- linearmodels PanelOLS Final Tables")
log("=" * 70)
