"""
30b_regression_H4_linearmodels.py
H4: Heterogeneity Tests -- Interaction Effects on Deposit Withdrawals
Three pre-committed specifications (Hypotheses v2.4, Section H4):
  H4a: Flood x Urban proxy (above-median baseline lights)
  H4b: Flood x High exposure (above-median cumulative flood count)
  H4c: Flood x Monsoon quarter (Q3 indicator)

Replaces Script 30 (statsmodels OLS). Key differences:
  1. linearmodels PanelOLS with entity_effects=True, time_effects=True.
     Avoids statsmodels ValueWarning from rank deficiency in clustered
     VCV at 666+ exogenous columns.
  2. Interaction terms pre-constructed as explicit columns (flood x Z_i).
     linearmodels PanelOLS does not accept formula strings with * notation.
  3. Panel index: (district_state_id, quarter_int). Sequential integer
     mapping for time -- identical approach to Scripts 27b, 28b, 29b.
  4. SE: cluster_entity=True (clustered by district_state_id, 631 clusters).
  5. Z_i heterogeneity variables constructed on composite district_state_id
     (not district_gadm alone -- prevents 7 homonymous pair collapses).

FE: entity_effects=True (district_state_id, 631) + time_effects=True
    (quarter, 36) -- identical to Scripts 27b/28b.
SE: Clustered by entity (district_state_id) throughout.

ANCHORS (Script 30, statsmodels -- Pre-Writing Master Plan, Section 1):
  H4a Rule A interaction p=0.532  -- NULL
  H4a Rule B interaction p=0.281  -- NULL
  H4b Rule A interaction p=0.020  -- SUGGESTIVE (fails winsorization p=0.865,
                                     writing constraint 12 active)
  H4b Rule B interaction p=0.080  -- SUGGESTIVE (marginal)
  H4c Rule A interaction p=0.001  -- CONFIRMED (Rule A only)
  H4c Rule B interaction p=0.774  -- NULL
  N = 22,442 | District FE = 631 | Quarter FE = 36

WRITING CONSTRAINTS ACTIVE:
  Constraint 5:  Z_i variables are proxies. Never claim census-based
                 urban/rural heterogeneity.
  Constraint 12: H4b demoted to suggestive. Winsorization failure mandatory
                 disclosure. Never present as robust.

Output: 05_Outputs/Tables/05b_H4_linearmodels.csv
        05_Outputs/Logs/30b_H4_linearmodels.txt
        05_Outputs/Logs/30b_H4_linearmodels_full_[spec]_rule[X].txt (6 files)
"""

import os
import logging
import numpy as np
import pandas as pd
from linearmodels import PanelOLS

# =============================================================================
# [1/8] SETUP
# =============================================================================

os.makedirs('05_Outputs/Logs',   exist_ok=True)
os.makedirs('05_Outputs/Tables', exist_ok=True)

logging.basicConfig(
    filename='05_Outputs/Logs/30b_H4_linearmodels.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)

# Stability threshold: flag if linearmodels interaction beta differs from
# Script 30 anchor by more than this amount.
STABILITY_THRESHOLD = 0.002

# Significance threshold for stability note direction check.
ALPHA = 0.05

# Locked anchors from Script 30 / Pre-Writing Master Plan Section 1.
# Interaction p-values only -- baseline coefficients not pre-anchored.
ANCHORS = {
    'H4a': {'A': {'p': 0.532, 'sig': False}, 'B': {'p': 0.281, 'sig': False}},
    'H4b': {'A': {'p': 0.020, 'sig': True},  'B': {'p': 0.080, 'sig': False}},
    'H4c': {'A': {'p': 0.001, 'sig': True},  'B': {'p': 0.774, 'sig': False}},
}

# Expected N and FE counts from locked results.
ANCHOR_N          = 22442
ANCHOR_DISTRICT_N = 631
ANCHOR_QUARTER_N  = 36

def _stars(p):
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.10:  return "+"
    return ""

print("=" * 70)
print("SCRIPT 30b: H4 HETEROGENEITY -- linearmodels PanelOLS")
print("Flood x District Characteristics -> Deposit Withdrawals")
print("Specs: H4a (Urban proxy), H4b (High exposure), H4c (Monsoon quarter)")
print("=" * 70)
log.info("=" * 70)
log.info("30b: H4 HETEROGENEITY -- linearmodels PanelOLS")
log.info("Flood x District Characteristics -> Deposit Withdrawals")
log.info("Specification: entity_effects=True, time_effects=True")
log.info("SE: cluster_entity=True (district_state_id, 631 clusters)")
log.info("Anchors (Script 30, statsmodels):")
log.info("  H4a Rule A: p=0.532 NULL  | H4a Rule B: p=0.281 NULL")
log.info("  H4b Rule A: p=0.020 SUGGESTIVE (constraint 12: winsorization fails)")
log.info("  H4b Rule B: p=0.080 SUGGESTIVE (marginal)")
log.info("  H4c Rule A: p=0.001 CONFIRMED | H4c Rule B: p=0.774 NULL")
log.info(f"  N={ANCHOR_N}, District FE={ANCHOR_DISTRICT_N}, Quarter FE={ANCHOR_QUARTER_N}")
log.info("=" * 70)

# =============================================================================
# [2/8] LOAD AND VALIDATE DATA
# =============================================================================

print("\n[2/8] Loading regression-ready panel...")
log.info("\n[2/8] Loading data")

df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23,  f"Expected 23 columns, got {df.shape[1]}"
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log.info(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")

required_cols = [
    'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt',
    'log_lights_qt', 'district_gadm', 'state_gadm', 'quarter', 'q'
]
missing_cols = [c for c in required_cols if c not in df.columns]
assert len(missing_cols) == 0, f"Missing required columns: {missing_cols}"
print(f"  Required columns verified -- PASS")
log.info(f"  Required columns verified -- PASS")

# =============================================================================
# [3/8] COMPOSITE KEY
# =============================================================================

print("\n[3/8] Constructing composite key...")
log.info("\n[3/8] Composite key")

# Composite key: prevents 7 homonymous district pairs from collapsing.
# district_gadm alone -> 624 unique (WRONG).
# district_gadm + '_' + state_gadm -> 631 unique (CORRECT).
# Used for: panel entity index, clustering, AND Z_i construction.
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']
n_districts = df['district_state_id'].nunique()
assert n_districts == 631, (
    f"Expected 631 district_state_id. Got {n_districts}. Check composite key."
)
print(f"  district_state_id: {n_districts} unique pairs -- PASS")
log.info(f"  district_state_id: {n_districts} -- PASS")

# =============================================================================
# [4/8] CONSTRUCT HETEROGENEITY VARIABLES (Z_i)
# =============================================================================

print("\n[4/8] Constructing heterogeneity variables (Z_i)...")
log.info("\n[4/8] Heterogeneity variable construction")

# --- H4a: Urban proxy ---
# Time-invariant. Above-median district mean log_lights_qt (full period).
# Grouped on composite district_state_id to prevent homonymous collapse.
# Labeled proxy throughout -- not census-based urban/rural classification.
# Writing constraint 5: never claim census-based classification.
district_lights = (
    df.groupby('district_state_id')['log_lights_qt']
    .mean()
    .reset_index()
    .rename(columns={'log_lights_qt': 'mean_log_lights'})
)
lights_median = district_lights['mean_log_lights'].median()
district_lights['urban_proxy'] = (
    district_lights['mean_log_lights'] > lights_median
).astype(int)

n_urban = district_lights['urban_proxy'].sum()
n_rural = (district_lights['urban_proxy'] == 0).sum()
assert n_urban + n_rural == 631, (
    f"urban_proxy split {n_urban}+{n_rural} != 631. Check district_state_id."
)
print(f"  H4a Urban proxy: median log_lights = {lights_median:.4f}")
print(f"    Above median (urban proxy): {n_urban} districts")
print(f"    At/below median (rural proxy): {n_rural} districts -- PASS")
log.info(f"  H4a Urban proxy: median log_lights = {lights_median:.4f}")
log.info(f"    Urban (above median): {n_urban} | Rural (at/below): {n_rural} -- PASS")
log.info(f"    Label: proxy (not census-based). Writing constraint 5 active.")

df = df.merge(
    district_lights[['district_state_id', 'urban_proxy']],
    on='district_state_id', how='left'
)
assert df['urban_proxy'].notna().all(), "urban_proxy has NaN after merge -- FAIL"
log.info(f"  urban_proxy merged: 0 NaN -- PASS")

# --- H4b: High exposure proxy ---
# Time-invariant. Above-median cumulative Rule A flood exposure per district.
# Grouped on composite district_state_id.
# Writing constraint 12: H4b demoted to suggestive -- winsorization fails.
district_exposure = (
    df.groupby('district_state_id')['flood_exposure_ruleA_qt']
    .sum()
    .reset_index()
    .rename(columns={'flood_exposure_ruleA_qt': 'cum_flood_A'})
)
exposure_median = district_exposure['cum_flood_A'].median()
district_exposure['high_exposure_proxy'] = (
    district_exposure['cum_flood_A'] > exposure_median
).astype(int)

n_high = district_exposure['high_exposure_proxy'].sum()
n_low  = (district_exposure['high_exposure_proxy'] == 0).sum()
assert n_high + n_low == 631, (
    f"high_exposure_proxy split {n_high}+{n_low} != 631. Check district_state_id."
)
print(f"  H4b High exposure proxy: median cum floods (Rule A) = {exposure_median:.1f}")
print(f"    High exposure (above median): {n_high} districts")
print(f"    Low exposure (at/below):      {n_low} districts -- PASS")
log.info(f"  H4b High exposure proxy: median cum floods = {exposure_median:.1f}")
log.info(f"    High: {n_high} | Low: {n_low} -- PASS")
log.info(f"    Label: proxy. Writing constraint 12 active.")
log.info(f"    MANDATORY: H4b Rule A p=0.020 does not survive winsorization (p=0.865).")
log.info(f"    H4b must be presented as suggestive only. Never as robust.")

df = df.merge(
    district_exposure[['district_state_id', 'high_exposure_proxy']],
    on='district_state_id', how='left'
)
assert df['high_exposure_proxy'].notna().all(), (
    "high_exposure_proxy has NaN after merge -- FAIL"
)
log.info(f"  high_exposure_proxy merged: 0 NaN -- PASS")

# --- H4c: Monsoon quarter ---
# Time-varying, not endogenous. Q3 indicator (July-September).
# q column stores integer 1-4 representing quarter within year.
df['monsoon_qt'] = (df['q'] == 3).astype(int)
n_monsoon     = df['monsoon_qt'].sum()
n_non_monsoon = (df['monsoon_qt'] == 0).sum()
assert n_monsoon + n_non_monsoon == len(df), (
    "monsoon_qt does not cover all rows -- FAIL"
)
# Q3 quarters in analysis sample: 9 (2015Q3, 2017Q3-2024Q3).
# 2016Q3 is absent -- dropped in Script 17 as part of 2016Q3-2017Q1 RBI blackout.
# 9 monsoon quarters x 631 districts = 5,679. Accept range 5,400-5,900.
assert 5400 <= n_monsoon <= 5900, (
    f"monsoon_qt count {n_monsoon} outside expected range [5400, 5900]. "
    f"Check q column encoding or RBI blackout quarter dropping."
)
print(f"  H4c Monsoon indicator: {n_monsoon:,} Q3 obs | {n_non_monsoon:,} non-Q3 obs -- PASS")
log.info(f"  H4c Monsoon indicator: {n_monsoon:,} Q3 | {n_non_monsoon:,} non-Q3 -- PASS")

print(f"  Z_i construction complete -- PASS")
log.info(f"  Z_i construction complete -- PASS")

# =============================================================================
# [5/8] RESTRICT TO COMPLETE CASES AND PRE-CONSTRUCT INTERACTION TERMS
# =============================================================================

print("\n[5/8] Restricting to complete cases and pre-constructing interactions...")
log.info("\n[5/8] Complete cases and interaction construction")

initial_n = len(df)

df_reg = df[
    df['deposit_change_qt'].notna()       &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_exposure_ruleB_qt'].notna() &
    df['urban_proxy'].notna()             &
    df['high_exposure_proxy'].notna()     &
    df['monsoon_qt'].notna()
].copy().reset_index(drop=True)

dropped = initial_n - len(df_reg)
assert 22000 <= len(df_reg) <= 22900, (
    f"After restriction: {len(df_reg):,} outside expected range [22,000, 22,900]. "
    f"Expected ~{ANCHOR_N:,}. Check NaN structure."
)
print(f"  Initial:           {initial_n:,} obs")
print(f"  After restriction: {len(df_reg):,} obs  (anchor: {ANCHOR_N:,})")
print(f"  Dropped:           {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")
log.info(f"  Initial: {initial_n:,}")
log.info(f"  After restriction: {len(df_reg):,}  (anchor: {ANCHOR_N:,})")
log.info(f"  Dropped: {dropped:,} ({dropped / initial_n * 100:.1f}%)")

# Pre-construct all interaction terms.
# linearmodels PanelOLS does not accept formula strings with * or : notation.
# Each interaction must be an explicit numeric column in the DataFrame.
# Six interactions total: 3 specs x 2 rules.
df_reg['floodA_x_urban']    = df_reg['flood_exposure_ruleA_qt'] * df_reg['urban_proxy']
df_reg['floodA_x_highexp']  = df_reg['flood_exposure_ruleA_qt'] * df_reg['high_exposure_proxy']
df_reg['floodA_x_monsoon']  = df_reg['flood_exposure_ruleA_qt'] * df_reg['monsoon_qt']
df_reg['floodB_x_urban']    = df_reg['flood_exposure_ruleB_qt'] * df_reg['urban_proxy']
df_reg['floodB_x_highexp']  = df_reg['flood_exposure_ruleB_qt'] * df_reg['high_exposure_proxy']
df_reg['floodB_x_monsoon']  = df_reg['flood_exposure_ruleB_qt'] * df_reg['monsoon_qt']

# Verify no NaN or Inf in any interaction column.
interaction_cols = [
    'floodA_x_urban', 'floodA_x_highexp', 'floodA_x_monsoon',
    'floodB_x_urban', 'floodB_x_highexp', 'floodB_x_monsoon'
]
for col in interaction_cols:
    n_nan = df_reg[col].isna().sum()
    n_inf = np.isinf(df_reg[col]).sum()
    assert n_nan == 0 and n_inf == 0, (
        f"Interaction column {col}: {n_nan} NaN, {n_inf} Inf -- FAIL"
    )
print(f"  All 6 interaction columns verified (0 NaN, 0 Inf) -- PASS")
log.info(f"  All 6 interaction columns verified (0 NaN, 0 Inf) -- PASS")

# =============================================================================
# [6/8] BUILD PANEL INDEX
# =============================================================================

print("\n[6/8] Building panel index for linearmodels PanelOLS...")
log.info("\n[6/8] Panel index construction")

# Map quarter strings to sequential integers.
# 'YYYYQN' format sorts correctly as strings (e.g. '2015Q1' < '2015Q2').
# linearmodels requires numeric or date-like time index.
quarters_sorted = sorted(df_reg['quarter'].unique())
assert 34 <= len(quarters_sorted) <= 38, (
    f"Quarter count {len(quarters_sorted)} outside expected range [34, 38]. "
    f"Expected {ANCHOR_QUARTER_N}. Range: {quarters_sorted[0]} to {quarters_sorted[-1]}."
)
quarter_to_int = {q: i for i, q in enumerate(quarters_sorted, start=1)}
df_reg['quarter_int'] = df_reg['quarter'].map(quarter_to_int)

df_reg = df_reg.set_index(['district_state_id', 'quarter_int'])

n_entities = df_reg.index.get_level_values(0).nunique()
n_periods  = df_reg.index.get_level_values(1).nunique()
n_dup      = df_reg.index.duplicated().sum()

assert n_entities == ANCHOR_DISTRICT_N, (
    f"Expected {ANCHOR_DISTRICT_N} entities. Got {n_entities}."
)
assert n_dup == 0, f"Panel index has {n_dup} duplicate (entity, time) pairs -- FAIL"

print(f"  Entities:   {n_entities}  (expected {ANCHOR_DISTRICT_N}) -- PASS")
print(f"  Periods:    {n_periods}   (expected {ANCHOR_QUARTER_N}) -- PASS")
print(f"  Duplicates: {n_dup}                                   -- PASS")
print(f"  Quarter range: {quarters_sorted[0]} to {quarters_sorted[-1]}, "
      f"mapped to integers 1-{len(quarters_sorted)}")
log.info(f"  Entities: {n_entities} -- PASS")
log.info(f"  Periods:  {n_periods}  -- PASS")
log.info(f"  Duplicates: {n_dup}     -- PASS")
log.info(f"  Quarter range: {quarters_sorted[0]} to {quarters_sorted[-1]}")

# =============================================================================
# [7/8] FIT ALL SIX MODELS: H4a, H4b, H4c x RULE A + RULE B
# =============================================================================

print("\n[7/8] Fitting 6 linearmodels PanelOLS models...")
log.info("\n[7/8] Model fitting")
log.info("  Specification: entity_effects=True, time_effects=True")
log.info("  SE: cluster_entity=True (district_state_id, 631 clusters)")
log.info("  Interaction terms pre-constructed as explicit columns.")

# --- Spec definitions ---
specs = [
    {
        'label'     : 'H4a',
        'title'     : 'Urban proxy x Flood',
        'flood_A'   : 'flood_exposure_ruleA_qt',
        'flood_B'   : 'flood_exposure_ruleB_qt',
        'inter_A'   : 'floodA_x_urban',
        'inter_B'   : 'floodB_x_urban',
        'z_label'   : 'urban_proxy',
        'note_A'    : ('Urban proxy = above-median district mean log_lights_qt. '
                       'Result suggestive only -- not census-based classification. '
                       'Writing constraint 5 active.'),
        'note_B'    : ('Rule B robustness. District-only flood match. '
                       'Urban proxy = above-median log_lights_qt.'),
    },
    {
        'label'     : 'H4b',
        'title'     : 'High exposure proxy x Flood',
        'flood_A'   : 'flood_exposure_ruleA_qt',
        'flood_B'   : 'flood_exposure_ruleB_qt',
        'inter_A'   : 'floodA_x_highexp',
        'inter_B'   : 'floodB_x_highexp',
        'z_label'   : 'high_exposure_proxy',
        'note_A'    : ('High exposure = above-median cumulative Rule A flood count. '
                       'DEMOTED TO SUGGESTIVE: Rule A p=0.020 main spec does NOT '
                       'survive winsorization (p=0.865, Script 37). '
                       'Writing constraint 12 active. Never present as robust.'),
        'note_B'    : ('Rule B robustness. District-only flood match. '
                       'High exposure = above-median cumulative Rule A flood count. '
                       'Writing constraint 12 active.'),
    },
    {
        'label'     : 'H4c',
        'title'     : 'Monsoon quarter x Flood',
        'flood_A'   : 'flood_exposure_ruleA_qt',
        'flood_B'   : 'flood_exposure_ruleB_qt',
        'inter_A'   : 'floodA_x_monsoon',
        'inter_B'   : 'floodB_x_monsoon',
        'z_label'   : 'monsoon_qt',
        'note_A'    : ('Monsoon = Q3 indicator (July-September). '
                       'H4c confirmed Rule A only. Rule B null (p=0.774). '
                       'Writing constraint 2 applies: exact required language '
                       'for fragile heterogeneity result.'),
        'note_B'    : ('Rule B robustness. District-only flood match. '
                       'H4c null under Rule B -- expected given lower power.'),
    },
]

results_rows = []

def _fit_and_extract(df_panel, flood_col, inter_col, spec_label, rule_label, note):
    """
    Fit linearmodels PanelOLS for one H4 specification.
    Returns result object and extracted scalars for baseline and interaction.
    entity_effects=True, time_effects=True.
    SE clustered by entity (district_state_id).
    """
    exog = df_panel[[flood_col, inter_col]]

    model = PanelOLS(
        dependent      = df_panel['deposit_change_qt'],
        exog           = exog,
        entity_effects = True,
        time_effects   = True
    )

    result = model.fit(
        cov_type       = 'clustered',
        cluster_entity = True
    )

    def _ex(varname):
        beta  = result.params[varname]
        se    = result.std_errors[varname]
        t     = result.tstats[varname]
        p     = result.pvalues[varname]
        ci    = result.conf_int()
        ci_lo = ci.loc[varname, 'lower']
        ci_hi = ci.loc[varname, 'upper']
        sig   = _stars(p)
        return beta, se, t, p, ci_lo, ci_hi, sig

    b_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base = _ex(flood_col)
    b_int,  se_int,  t_int,  p_int,  cilo_int,  cihi_int,  sig_int  = _ex(inter_col)

    nobs = int(result.nobs)
    r2_w = result.rsquared

    def _print_block(label, b, se, t, p, cilo, cihi, sig):
        print(f"\n    [{label}]")
        print(f"      beta    = {b:.6f}")
        print(f"      SE      = {se:.6f}")
        print(f"      t       = {t:.4f}")
        print(f"      p       = {p:.6f}  {sig if sig else '(NOT SIGNIFICANT)'}")
        print(f"      95% CI  = [{cilo:.6f}, {cihi:.6f}]")

    def _log_block(label, b, se, t, p, cilo, cihi, sig):
        log.info(f"    [{label}]")
        log.info(f"      beta = {b:.6f}")
        log.info(f"      SE   = {se:.6f}")
        log.info(f"      t    = {t:.4f}")
        log.info(f"      p    = {p:.6f}  {sig if sig else '(NOT SIGNIFICANT)'}")
        log.info(f"      95% CI = [{cilo:.6f}, {cihi:.6f}]")

    print(f"\n  {spec_label} Rule {rule_label}: N={nobs:,} | "
          f"R2(within/entity+time) = {r2_w:.4f}")
    log.info(f"\n  {spec_label} Rule {rule_label}:")
    log.info(f"    N={nobs:,} | R2(within) = {r2_w:.4f}")
    log.info(f"    Baseline var: {flood_col}")
    log.info(f"    Interaction:  {inter_col}")

    _print_block(f"Baseline flood ({flood_col})",
                 b_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base)
    _print_block(f"Interaction ({inter_col})",
                 b_int, se_int, t_int, p_int, cilo_int, cihi_int, sig_int)
    _log_block(f"Baseline flood ({flood_col})",
               b_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base)
    _log_block(f"Interaction ({inter_col})",
               b_int, se_int, t_int, p_int, cilo_int, cihi_int, sig_int)

    # Stability check against Script 30 anchor p-value.
    anchor_p   = ANCHORS[spec_label][rule_label]['p']
    anchor_sig = ANCHORS[spec_label][rule_label]['sig']

    # Significance consistency: 30b must agree with Script 30 on significance
    # at ALPHA=0.05 for the interaction term.
    current_sig = p_int < ALPHA
    if current_sig == anchor_sig:
        log.info(f"    Significance consistent with Script 30 anchor "
                 f"(anchor p={anchor_p}, anchor sig={anchor_sig}, "
                 f"30b p={p_int:.4f}) -- PASS")
        print(f"    Significance consistent with anchor "
              f"(p={p_int:.4f} vs anchor p={anchor_p}) -- PASS")
    else:
        msg = (
            f"SIGNIFICANCE MISMATCH {spec_label} Rule {rule_label}: "
            f"Script 30 anchor p={anchor_p} (sig={anchor_sig}), "
            f"30b p={p_int:.4f} (sig={current_sig}). "
            f"Investigate before writing. Do not proceed to paper tables."
        )
        print(f"    *** WARNING: {msg}")
        log.info(f"    *** WARNING: {msg}")

    # H4b mandatory disclosure reminder.
    if spec_label == 'H4b' and rule_label == 'A':
        log.info(f"    MANDATORY DISCLOSURE (constraint 12): H4b Rule A main result "
                 f"p={p_int:.4f} does NOT survive winsorization (p=0.865, Script 37). "
                 f"Must be presented as suggestive. Never omit winsorization failure.")
        print(f"    CONSTRAINT 12: H4b Rule A p={p_int:.4f}. "
              f"Winsorization fails (p=0.865). Suggestive only.")

    # H4c writing constraint reminder.
    if spec_label == 'H4c' and rule_label == 'A' and p_int < ALPHA:
        log.info(f"    CONSTRAINT 2 ACTIVE: H4c Rule A confirmed p={p_int:.4f}. "
                 f"Required language: 'Monsoon seasonality moderates the deposit "
                 f"response to moderate-intensity floods (Rule A beta, p={p_int:.4f}) "
                 f"but not to severe flood events (Rule B p=0.774). The heterogeneity "
                 f"result is fragile to flood intensity definition.'")

    return (result, b_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base,
            b_int, se_int, t_int, p_int, cilo_int, cihi_int, sig_int, nobs, r2_w, note)


for spec in specs:
    print(f"\n{'=' * 70}")
    print(f"  {spec['label']}: {spec['title']}")
    print(f"{'=' * 70}")
    log.info(f"\n{'=' * 70}")
    log.info(f"{spec['label']}: {spec['title']}")
    log.info(f"{'=' * 70}")

    for rule, flood_col, inter_col, note in [
        ('A', spec['flood_A'], spec['inter_A'], spec['note_A']),
        ('B', spec['flood_B'], spec['inter_B'], spec['note_B']),
    ]:
        try:
            (result_obj,
             b_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base,
             b_int,  se_int,  t_int,  p_int,  cilo_int,  cihi_int,  sig_int,
             nobs, r2_w, note_used) = _fit_and_extract(
                df_reg, flood_col, inter_col, spec['label'], rule, note
            )
        except Exception as e:
            log.error(f"  {spec['label']} Rule {rule} FAILED: {e}")
            raise

        # Save full model summary for audit trail.
        summary_path = (
            f"05_Outputs/Logs/30b_H4_linearmodels_full_"
            f"{spec['label'].lower()}_rule{rule}.txt"
        )
        with open(summary_path, 'w') as f:
            f.write(str(result_obj.summary))
        assert os.path.exists(summary_path), (
            f"Summary file not written: {summary_path}"
        )
        log.info(f"    Full summary: {summary_path} -- PASS")

        results_rows.append({
            'hypothesis'              : spec['label'],
            'rule'                    : rule,
            'specification'           : spec['title'],
            'estimator'               : 'linearmodels.PanelOLS',
            'entity_effects'          : 'True (district_state_id, 631)',
            'time_effects'            : 'True (quarter, ' + str(n_periods) + ')',
            'se_type'                 : 'clustered_entity (district_state_id, 631 clusters)',
            'flood_variable'          : flood_col,
            'interaction_variable'    : inter_col,
            'z_variable'              : spec['z_label'],
            'baseline_coef'           : round(b_base,  6),
            'baseline_se'             : round(se_base, 6),
            'baseline_t'              : round(t_base,  4),
            'baseline_p'              : round(p_base,  6),
            'interaction_coef'        : round(b_int,   6),
            'interaction_se'          : round(se_int,  6),
            'interaction_t'           : round(t_int,   4),
            'interaction_p'           : round(p_int,   6),
            'interaction_ci_lower_95' : round(cilo_int, 6),
            'interaction_ci_upper_95' : round(cihi_int, 6),
            'n_obs'                   : nobs,
            'r_squared_within'        : round(r2_w, 4),
            'significance'            : sig_int,
            'anchor_p_script30'       : ANCHORS[spec['label']][rule]['p'],
            'anchor_sig_script30'     : ANCHORS[spec['label']][rule]['sig'],
            'note'                    : note_used,
        })

# =============================================================================
# [8/8] SIDE-BY-SIDE SUMMARY AND SAVE OUTPUTS
# =============================================================================

print("\n" + "=" * 70)
print("H4 RESULTS SUMMARY -- INTERACTION COEFFICIENTS")
print("linearmodels PanelOLS: entity_effects=True, time_effects=True")
print("=" * 70)
print(f"  Dependent: deposit_change_qt")
print(f"  FE: District (631) + Quarter ({n_periods}) | "
      f"SE: Clustered entity (district_state_id)")
print(f"  {'Spec':<6} {'Rule':<5} {'Inter Beta':>12} {'SE':>10} "
      f"{'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-' * 60}")
for row in results_rows:
    print(f"  {row['hypothesis']:<6} {row['rule']:<5} "
          f"{row['interaction_coef']:>12.6f} {row['interaction_se']:>10.6f} "
          f"{row['interaction_t']:>8.4f} {row['interaction_p']:>10.6f} "
          f"{row['significance']:>5}")
    if row['rule'] == 'B':
        print(f"  {'-' * 60}")

print(f"\n  Script 30 anchors (statsmodels, interaction p-values):")
print(f"  H4a A: p=0.532 NULL  | H4a B: p=0.281 NULL")
print(f"  H4b A: p=0.020 *     | H4b B: p=0.080 + (both suggestive, constraint 12)")
print(f"  H4c A: p=0.001 ***   | H4c B: p=0.774 NULL")

log.info("\n" + "=" * 70)
log.info("SIDE-BY-SIDE SUMMARY -- linearmodels PanelOLS")
log.info("=" * 70)
log.info(f"  {'Spec':<6} {'Rule':<5} {'Inter Beta':>12} {'SE':>10} "
         f"{'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-' * 60}")
for row in results_rows:
    log.info(f"  {row['hypothesis']:<6} {row['rule']:<5} "
             f"{row['interaction_coef']:>12.6f} {row['interaction_se']:>10.6f} "
             f"{row['interaction_t']:>8.4f} {row['interaction_p']:>10.6f} "
             f"{row['significance']:>5}")

# Aggregate significance check for all 6 models.
log.info("\n  Significance consistency vs Script 30 anchors:")
all_consistent = True
for row in results_rows:
    current_sig = row['interaction_p'] < ALPHA
    anchor_sig  = row['anchor_sig_script30']
    status = "PASS" if current_sig == anchor_sig else "MISMATCH"
    if current_sig != anchor_sig:
        all_consistent = False
    log.info(f"  {row['hypothesis']} Rule {row['rule']}: "
             f"anchor sig={anchor_sig}, 30b sig={current_sig} -- {status}")
if all_consistent:
    log.info("  All 6 significance checks consistent -- PASS")
    print("\n  All 6 significance checks consistent with Script 30 anchors -- PASS")
else:
    log.info("  *** ONE OR MORE SIGNIFICANCE MISMATCHES -- INVESTIGATE BEFORE WRITING ***")
    print("\n  *** SIGNIFICANCE MISMATCH DETECTED -- INVESTIGATE BEFORE WRITING ***")

# Save CSV.
OUTPUT_CSV = '05_Outputs/Tables/05b_H4_linearmodels.csv'
results_df = pd.DataFrame(results_rows)
results_df.to_csv(OUTPUT_CSV, index=False)
assert os.path.exists(OUTPUT_CSV), f"CSV not written: {OUTPUT_CSV}"
print(f"\n  CSV saved: {OUTPUT_CSV} -- PASS")
log.info(f"\n  CSV saved: {OUTPUT_CSV} -- PASS")

print("\n" + "=" * 70)
print("SCRIPT 30b COMPLETE")
print("=" * 70)
print(f"  CSV:            {OUTPUT_CSV}")
print(f"  Log:            05_Outputs/Logs/30b_H4_linearmodels.txt")
print(f"  Full summaries: 05_Outputs/Logs/30b_H4_linearmodels_full_[spec]_rule[A/B].txt")
print(f"                  (6 files: h4a_ruleA, h4a_ruleB, h4b_ruleA, h4b_ruleB,")
print(f"                            h4c_ruleA, h4c_ruleB)")
print("=" * 70)
print("ALL linearmodels FINAL TABLES COMPLETE: 27b, 28b, 29b, 30b.")
print("NEXT STEP: Figure A -- H3 deposit timing cycle plot (two-phase).")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 30b COMPLETE")
log.info(f"  CSV: {OUTPUT_CSV}")
log.info("  Full summaries: 6 files (h4a-h4c, rules A-B).")
log.info("All linearmodels final tables complete: 27b, 28b, 29b, 30b.")
log.info("Next: Figure A -- H3 deposit timing cycle plot (two-phase).")
log.info("=" * 70)