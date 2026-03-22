"""
30_regression_H4_heterogeneity.py
H4: Heterogeneity Tests -- Interaction Effects on Deposit Withdrawals
Three pre-committed specifications (Hypotheses v2.4, Section H4):
  H4a: Flood x Urban proxy (above-median baseline lights)
  H4b: Flood x High exposure (above-median cumulative flood count)
  H4c: Flood x Monsoon quarter (Q3 indicator)

FE: district_state_id composite (631) + quarter (36) -- same as Scripts 27/28.
SE: Clustered by district_state_id throughout.
Both Rule A (primary) and Rule B (robustness) estimated for all three specs.

PROXY DISCIPLINE (pre-committed, Hypotheses v2.4):
  Z_i variables are time-invariant district characteristics constructed
  from baseline period or full-period aggregates. All labeled as proxies
  in outputs. Results treated as suggestive, not causal, where true
  administrative classification is unavailable.

CRITICAL FIXES vs prior version:
  1. FE: district_gadm alone -> district_state_id composite (631, not 624)
  2. Clustering: district_gadm alone -> district_state_id composite
  3. H4a urban groupby: district_gadm alone -> district_state_id composite
     (AURANGABAD Bihar/Maharashtra collapsed without state -- wrong)
  4. H4b high_exposure groupby: same fix
  5. Rule B: added per pre-committed R1
  6. Unicode checkmarks removed (Windows cp1252 risk)
  7. Hard asserts at load
  8. statsmodels OLS replacing manual numpy (consistent with Script 27)
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import logging
import os


# === SETUP ===
os.makedirs('05_Outputs/Logs', exist_ok=True)
os.makedirs('05_Outputs/Tables', exist_ok=True)

logging.basicConfig(
    filename='05_Outputs/Logs/30_H4_regression.txt',
    level=logging.INFO,
    format='%(message)s',
    filemode='w'
)
log = logging.getLogger(__name__)


print("=" * 70)
print("PHASE 4: H4 HETEROGENEITY REGRESSIONS (Interaction Effects)")
print("=" * 70)
log.info("=" * 70)
log.info("H4: HETEROGENEITY REGRESSIONS")
log.info("Flood x District Characteristics -> Deposit Withdrawals")
log.info("Specs: H4a (Urban), H4b (High Exposure), H4c (Monsoon)")
log.info("=" * 70)


# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================
print("\n[1/6] Loading regression-ready panel...")
df = pd.read_csv('03_Data_Clean/regression_panel_final.csv')
assert len(df) == 23347, f"Expected 23,347 rows, got {len(df):,}"
assert df.shape[1] == 23,  f"Expected 23 columns, got {df.shape[1]}"
print(f"  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS")
log.info(f"\nPanel loaded: {len(df):,} rows, {df.shape[1]} columns")

required_cols = [
    'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_exposure_ruleB_qt',
    'log_lights_qt', 'district_gadm', 'state_gadm', 'quarter', 'q'
]
missing_cols = [c for c in required_cols if c not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
print(f"  Required columns verified -- PASS")
log.info("Required columns verified -- PASS")


# =============================================================================
# STEP 2: COMPOSITE KEY
# =============================================================================
print("\n[2/6] Constructing composite key...")

# CRITICAL: composite key prevents 7 homonymous pairs from collapsing.
# district_gadm alone -> 624 unique districts (WRONG).
# district_gadm + '_' + state_gadm -> 631 unique pairs (CORRECT).
# Used for: FE encoding, clustering, AND heterogeneity variable construction.
df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']

n_districts = df['district_state_id'].nunique()
print(f"  district_state_id: {n_districts} unique pairs  (expected 631)")
log.info(f"\ndistrict_state_id: {n_districts} unique pairs  (expected 631)")

if n_districts != 631:
    raise ValueError(
        f"District count {n_districts} != 631. "
        f"Check composite key or upstream pipeline."
    )
print(f"  Composite key verified -- PASS")
log.info("Composite key verified -- PASS")


# =============================================================================
# STEP 3: CONSTRUCT HETEROGENEITY VARIABLES (Z_i)
# =============================================================================
print("\n[3/6] Constructing heterogeneity variables (Z_i)...")
log.info("\n" + "=" * 70)
log.info("HETEROGENEITY VARIABLE CONSTRUCTION")
log.info("=" * 70)

# --- H4a: Urban proxy ---
# Above-median district mean log_lights_qt (full period, time-invariant)
# Groupby on composite district_state_id -- prevents homonymous pair collapse.
# Labeled as proxy: not a census-based urban/rural classification.
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

n_urban   = district_lights['urban_proxy'].sum()
n_rural   = (district_lights['urban_proxy'] == 0).sum()
print(f"  H4a Urban proxy: median log_lights = {lights_median:.4f}")
print(f"    Urban (above median): {n_urban} districts")
print(f"    Rural (at/below):     {n_rural} districts")
log.info(f"\nH4a Urban proxy:")
log.info(f"  Median log_lights_qt: {lights_median:.4f}")
log.info(f"  Urban (above median): {n_urban} districts")
log.info(f"  Rural (at/below):     {n_rural} districts")
log.info(f"  Label: proxy (not census-based). Results treated as suggestive.")

df = df.merge(
    district_lights[['district_state_id', 'urban_proxy']],
    on='district_state_id', how='left'
)
assert df['urban_proxy'].notna().all(), "urban_proxy has NaN after merge"

# --- H4b: High exposure proxy ---
# Above-median cumulative flood count (full period, time-invariant)
# Groupby on composite district_state_id.
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
print(f"  H4b High exposure proxy: median cum floods = {exposure_median:.1f}")
print(f"    High exposure (above median): {n_high} districts")
print(f"    Low exposure (at/below):      {n_low} districts")
log.info(f"\nH4b High exposure proxy:")
log.info(f"  Median cumulative Rule A floods: {exposure_median:.1f}")
log.info(f"  High exposure (above median): {n_high} districts")
log.info(f"  Low exposure (at/below):      {n_low} districts")
log.info(f"  Label: proxy. Results treated as suggestive.")

df = df.merge(
    district_exposure[['district_state_id', 'high_exposure_proxy']],
    on='district_state_id', how='left'
)
assert df['high_exposure_proxy'].notna().all(), "high_exposure_proxy has NaN after merge"

# --- H4c: Monsoon quarter ---
# Q3 indicator (July-September). Time-varying but not endogenous.
# q column already in panel (integer 1-4).
df['monsoon_qt'] = (df['q'] == 3).astype(int)
n_monsoon     = df['monsoon_qt'].sum()
n_non_monsoon = (df['monsoon_qt'] == 0).sum()
print(f"  H4c Monsoon indicator: {n_monsoon:,} Q3 obs | {n_non_monsoon:,} non-Q3 obs")
log.info(f"\nH4c Monsoon indicator:")
log.info(f"  Q3 (monsoon) obs:     {n_monsoon:,}")
log.info(f"  Non-Q3 obs:           {n_non_monsoon:,}")

print(f"  Heterogeneity variables constructed -- PASS")
log.info("\nHeterogeneity variables constructed -- PASS")


# =============================================================================
# STEP 4: RESTRICT TO COMPLETE CASES + ENCODE FE
# =============================================================================
print("\n[4/6] Restricting to complete cases and encoding FE...")
initial_n = len(df)

df_reg = df[
    df['deposit_change_qt'].notna()       &
    df['flood_exposure_ruleA_qt'].notna() &
    df['flood_exposure_ruleB_qt'].notna() &
    df['urban_proxy'].notna()             &
    df['high_exposure_proxy'].notna()     &
    df['monsoon_qt'].notna()
].copy()

dropped = initial_n - len(df_reg)
print(f"  Initial:           {initial_n:,} obs")
print(f"  After restriction: {len(df_reg):,} obs  (expected ~22,442)")
print(f"  Dropped:           {dropped:,} obs ({dropped / initial_n * 100:.1f}%)")
log.info(f"\nInitial: {initial_n:,} obs")
log.info(f"After restriction: {len(df_reg):,} obs  (expected ~22,442)")
log.info(f"Dropped: {dropped:,} ({dropped / initial_n * 100:.1f}%)")

# Encode interaction terms explicitly (statsmodels formula handles this
# via C() but explicit columns are cleaner for logging)
df_reg['flood_x_urban']    = df_reg['flood_exposure_ruleA_qt'] * df_reg['urban_proxy']
df_reg['flood_x_highexp']  = df_reg['flood_exposure_ruleA_qt'] * df_reg['high_exposure_proxy']
df_reg['flood_x_monsoon']  = df_reg['flood_exposure_ruleA_qt'] * df_reg['monsoon_qt']
df_reg['floodB_x_urban']   = df_reg['flood_exposure_ruleB_qt'] * df_reg['urban_proxy']
df_reg['floodB_x_highexp'] = df_reg['flood_exposure_ruleB_qt'] * df_reg['high_exposure_proxy']
df_reg['floodB_x_monsoon'] = df_reg['flood_exposure_ruleB_qt'] * df_reg['monsoon_qt']

# FE encoding -- composite key
df_reg['district_fe'] = pd.Categorical(df_reg['district_state_id'])
df_reg['quarter_fe']  = pd.Categorical(df_reg['quarter'])

n_district_fe = df_reg['district_fe'].nunique()
n_quarter_fe  = df_reg['quarter_fe'].nunique()

print(f"  District FE: {n_district_fe}  (expected 631)")
print(f"  Quarter FE:  {n_quarter_fe}  (expected 36)")
log.info(f"\nDistrict FE: {n_district_fe}  (expected 631)")
log.info(f"Quarter FE:  {n_quarter_fe}  (expected 36)")

if n_district_fe < 620 or n_district_fe > 640:
    raise ValueError(
        f"District FE count {n_district_fe} outside expected range [620, 640]. "
        f"Check composite key construction."
    )
print(f"  FE counts verified -- PASS")
log.info("FE counts verified -- PASS")


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


def print_coef(label, coef, se, tstat, pval, ci_lo, ci_hi, sig):
    print(f"    {label}")
    print(f"      Beta    = {coef:.6f}")
    print(f"      SE      = {se:.6f}")
    print(f"      t       = {tstat:.3f}")
    print(f"      p       = {pval:.6f}")
    print(f"      95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]")
    print(f"      Status  = {sig if sig else 'NOT SIGNIFICANT'}")


def log_coef(label, coef, se, tstat, pval, ci_lo, ci_hi, sig):
    log.info(f"  {label}")
    log.info(f"    Beta    = {coef:.6f}")
    log.info(f"    SE      = {se:.6f}")
    log.info(f"    t       = {tstat:.3f}")
    log.info(f"    p       = {pval:.6f}")
    log.info(f"    95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]")
    log.info(f"    Status  = {sig if sig else 'NOT SIGNIFICANT'}")


# =============================================================================
# STEP 5: RUN ALL SIX REGRESSIONS (3 specs x 2 rules)
# =============================================================================
print("\n[5/6] Running H4a, H4b, H4c -- Rule A and Rule B...")

results_rows = []

specs = [
    {
        'label':        'H4a',
        'title':        'Urban proxy x Flood',
        'flood_A':      'flood_exposure_ruleA_qt',
        'flood_B':      'flood_exposure_ruleB_qt',
        'inter_A':      'flood_x_urban',
        'inter_B':      'floodB_x_urban',
        'z_label':      'urban_proxy',
        'baseline_A':   'Non-urban (rural proxy)',
        'baseline_B':   'Non-urban (rural proxy)',
        'note':         'Urban proxy = above-median district mean log_lights_qt. '
                        'Results suggestive only -- not census-based classification. '
                        'Feb 6 benchmark: interaction p<0.001 (contaminated FE).'
    },
    {
        'label':        'H4b',
        'title':        'High exposure proxy x Flood',
        'flood_A':      'flood_exposure_ruleA_qt',
        'flood_B':      'flood_exposure_ruleB_qt',
        'inter_A':      'flood_x_highexp',
        'inter_B':      'floodB_x_highexp',
        'z_label':      'high_exposure_proxy',
        'baseline_A':   'Low exposure (below median)',
        'baseline_B':   'Low exposure (below median)',
        'note':         'High exposure = above-median cumulative Rule A flood count. '
                        'Feb 6 benchmark: null (p=0.360). Expected to persist.'
    },
    {
        'label':        'H4c',
        'title':        'Monsoon quarter x Flood',
        'flood_A':      'flood_exposure_ruleA_qt',
        'flood_B':      'flood_exposure_ruleB_qt',
        'inter_A':      'flood_x_monsoon',
        'inter_B':      'floodB_x_monsoon',
        'z_label':      'monsoon_qt',
        'baseline_A':   'Non-monsoon quarters',
        'baseline_B':   'Non-monsoon quarters',
        'note':         'Monsoon = Q3 (July-September). '
                        'Feb 6 benchmark: null (p=0.511). Expected to persist.'
    }
]

for spec in specs:
    print(f"\n  --- {spec['label']}: {spec['title']} ---")
    log.info("\n" + "=" * 70)
    log.info(f"{spec['label']}: {spec['title']}")
    log.info("=" * 70)
    log.info(f"  Note: {spec['note']}")

    for rule, flood_var, inter_var in [
        ('A', spec['flood_A'], spec['inter_A']),
        ('B', spec['flood_B'], spec['inter_B'])
    ]:
        formula = (
            f"deposit_change_qt ~ {flood_var} + {inter_var} + "
            f"C(district_fe) + C(quarter_fe)"
        )

        log.info(f"\n  Rule {rule}:")
        log.info(f"    Formula: {formula}")
        log.info(f"    FE: district_state_id (631) + quarter (36)")
        log.info(f"    SE: Clustered by district_state_id")

        try:
            model = ols(formula, data=df_reg).fit(
                cov_type='cluster',
                cov_kwds={'groups': df_reg['district_state_id']}
            )
        except Exception as e:
            log.error(f"    {spec['label']} Rule {rule} failed: {e}")
            raise

        coef_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base = \
            extract_coef(model, flood_var)
        coef_int,  se_int,  t_int,  p_int,  cilo_int,  cihi_int,  sig_int  = \
            extract_coef(model, inter_var)

        print(f"\n    Rule {rule} | N = {model.nobs:,.0f} | R2 = {model.rsquared:.4f}")
        print_coef(f"Baseline ({spec['baseline_A']}):",
                   coef_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base)
        print_coef(f"Interaction ({spec['z_label']} x Flood):",
                   coef_int,  se_int,  t_int,  p_int,  cilo_int,  cihi_int,  sig_int)

        log_coef(f"Baseline ({spec['baseline_A']}):",
                 coef_base, se_base, t_base, p_base, cilo_base, cihi_base, sig_base)
        log_coef(f"Interaction ({spec['z_label']} x Flood):",
                 coef_int,  se_int,  t_int,  p_int,  cilo_int,  cihi_int,  sig_int)

        if rule == 'A':
            if p_int < 0.05 and coef_int < 0:
                conclusion = f"{spec['label']} SUPPORTED. Interaction negative and significant."
            elif p_int >= 0.05:
                conclusion = f"{spec['label']} NULL. No significant heterogeneity."
            else:
                conclusion = f"{spec['label']} SIGNIFICANT but unexpected sign. Review."
            log.info(f"\n  Conclusion (Rule A): {conclusion}")

        results_rows.append({
            'hypothesis':        spec['label'],
            'rule':              rule,
            'specification':     spec['title'],
            'flood_variable':    flood_var,
            'interaction_term':  inter_var,
            'z_variable':        spec['z_label'],
            'baseline_coef':     round(coef_base, 6),
            'baseline_se':       round(se_base,   6),
            'baseline_t':        round(t_base,    3),
            'baseline_p':        round(p_base,    6),
            'interaction_coef':  round(coef_int,  6),
            'interaction_se':    round(se_int,    6),
            'interaction_t':     round(t_int,     3),
            'interaction_p':     round(p_int,     6),
            'interaction_ci_lo': round(cilo_int,  6),
            'interaction_ci_hi': round(cihi_int,  6),
            'n_obs':             int(model.nobs),
            'r_squared':         round(model.rsquared,     4),
            'r_squared_adj':     round(model.rsquared_adj, 4),
            'district_fe_count': n_district_fe,
            'quarter_fe_count':  n_quarter_fe,
            'se_type':           'clustered_by_district_state_id',
            'significance':      sig_int,
            'note':              spec['note']
        })


# =============================================================================
# SUMMARY TABLE
# =============================================================================
print("\n" + "=" * 70)
print("H4 RESULTS SUMMARY -- INTERACTION COEFFICIENTS")
print("=" * 70)
print(f"  Dependent: deposit_change_qt")
print(f"  FE: District (631) + Quarter (36) | SE: Clustered district_state_id")
print(f"  {'Spec':<6} {'Rule':<5} {'Inter Beta':>12} {'SE':>10} {'t':>8} {'p':>10} {'Sig':>5}")
print(f"  {'-'*60}")

for row in results_rows:
    print(f"  {row['hypothesis']:<6} {row['rule']:<5} "
          f"{row['interaction_coef']:>12.6f} {row['interaction_se']:>10.6f} "
          f"{row['interaction_t']:>8.3f} {row['interaction_p']:>10.6f} "
          f"{row['significance']:>5}")
    if row['rule'] == 'B':
        print(f"  {'-'*60}")

log.info("\n" + "=" * 70)
log.info("SUMMARY -- INTERACTION COEFFICIENTS")
log.info("=" * 70)
log.info(f"  {'Spec':<6} {'Rule':<5} {'Inter Beta':>12} {'SE':>10} "
         f"{'t':>8} {'p':>10} {'Sig':>5}")
log.info(f"  {'-'*60}")
for row in results_rows:
    log.info(f"  {row['hypothesis']:<6} {row['rule']:<5} "
             f"{row['interaction_coef']:>12.6f} {row['interaction_se']:>10.6f} "
             f"{row['interaction_t']:>8.3f} {row['interaction_p']:>10.6f} "
             f"{row['significance']:>5}")


# =============================================================================
# STEP 6: SAVE OUTPUTS
# =============================================================================
print("\n[6/6] Saving outputs...")

results_df = pd.DataFrame(results_rows)
results_df.to_csv('05_Outputs/Tables/05_H4_heterogeneity.csv', index=False)
print(f"  Table saved: 05_Outputs/Tables/05_H4_heterogeneity.csv")
log.info(f"\nTable saved: 05_Outputs/Tables/05_H4_heterogeneity.csv")


# === COMPLETION ===
print("\n" + "=" * 70)
print("H4 HETEROGENEITY COMPLETE")
print("=" * 70)
print(f"  Table: 05_Outputs/Tables/05_H4_heterogeneity.csv")
print(f"  Log:   05_Outputs/Logs/30_H4_regression.txt")
print("=" * 70)
print("NEXT STEP: Phase 4 complete. Update Hypotheses v2.5 and Codebook v2.5.")
print("=" * 70)

log.info("\n" + "=" * 70)
log.info("SCRIPT 30 COMPLETE")
log.info("Next: Update Hypotheses v2.5 and Codebook v2.5 with all results.")
log.info("=" * 70)