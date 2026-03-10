"""
33_northeast_sensitivity.py
Robustness R8: Northeast Sensitivity Check

Purpose:
    Re-run H3 (Distributed Lag) and H4 (Heterogeneity) excluding all
    8 Northeast states. Script 32b confirmed that the 2023 left-tail
    anomaly is concentrated in Northeast districts:
      - 8 of bottom 10 extreme 2023 obs are NE districts
      - TUENSANG (Nagaland) within-year 2023 swing = +-3.21
      - 385 of 2,507 2023 obs (15.4%) below full-sample 5th percentile
    This script determines whether main results are driven by NE districts
    or are robust to their exclusion.

Northeast states excluded (8):
    ARUNACHAL PRADESH, ASSAM, MANIPUR, MEGHALAYA,
    MIZORAM, NAGALAND, SIKKIM, TRIPURA
    (All UPPERCASE -- matches GADM state_gadm field)

Specification:
    H3: Quarter FE only (NO district FE). Pre-committed H3 design.
        Identical to Script 29 except NE districts excluded.
    H4: District FE + Quarter FE. Pre-committed H4 design.
        Identical to Script 30 except NE districts excluded.
    Both: SE clustered by district_state_id throughout.

Z_i proxy construction:
    CRITICAL: Z_i proxies (urban_proxy, high_exposure_proxy) are
    constructed on the FULL sample BEFORE NE exclusion. This ensures
    thresholds are identical to Script 30 and the comparison is clean.
    A change in results here means NE districts drive the main result.
    A stable result confirms robustness.

Comparison anchors (Script 29/30 locked results, Rule A):
    H3 t0:            beta = +0.000609, SE = 0.001463, p = 0.677  null
    H3 t-1:           beta = +0.001505, SE = 0.001114, p = 0.177  null
    H3 t-2:           beta = -0.007005, SE = 0.001645, p < 0.001  ***
    H4a interaction:  beta = -0.001666, SE = 0.002666, p = 0.532  null
    H4b interaction:  beta = -0.006810, SE = 0.002934, p = 0.020  **
    H4c interaction:  beta = +0.012495, SE = 0.002886, p < 0.001  ***

INPUT:  03_Data_Clean/regression_panel_final.csv  (23,347 x 23)
OUTPUT: 05_Outputs/Tables/07_H3_northeast_sensitivity.csv
        05_Outputs/Tables/08_H4_northeast_sensitivity.csv
        05_Outputs/Logs/33_northeast_sensitivity_log.txt
"""

import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
import os
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================

NE_STATES = [
    'ARUNACHAL PRADESH',
    'ASSAM',
    'MANIPUR',
    'MEGHALAYA',
    'MIZORAM',
    'NAGALAND',
    'SIKKIM',
    'TRIPURA'
]

# Locked comparison anchors from Scripts 29 and 30 (Rule A)
ANCHORS_H3 = {
    't0':  {'beta': +0.000609, 'se': 0.001463, 'p': 0.677},
    't-1': {'beta': +0.001505, 'se': 0.001114, 'p': 0.177},
    't-2': {'beta': -0.007005, 'se': 0.001645, 'p': 0.000}
}

ANCHORS_H4_INTERACTION = {
    'H4a': {'beta': -0.001666, 'se': 0.002666, 'p': 0.532},
    'H4b': {'beta': -0.006810, 'se': 0.002934, 'p': 0.020},
    'H4c': {'beta': +0.012495, 'se': 0.002886, 'p': 0.000}
}

INPUT_PATH = '03_Data_Clean/regression_panel_final.csv'
OUT_H3     = '05_Outputs/Tables/07_H3_northeast_sensitivity.csv'
OUT_H4     = '05_Outputs/Tables/08_H4_northeast_sensitivity.csv'
LOG_PATH   = '05_Outputs/Logs/33_northeast_sensitivity_log.txt'


# =============================================================================
# SETUP
# =============================================================================

os.makedirs('05_Outputs/Tables', exist_ok=True)
os.makedirs('05_Outputs/Logs',   exist_ok=True)

run_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

log_lines = []
def log(msg=''):
    print(msg)
    log_lines.append(str(msg))

log('=' * 70)
log('SCRIPT 33: ROBUSTNESS R8 -- NORTHEAST SENSITIVITY')
log('H3 and H4 re-run excluding 8 Northeast states')
log(f'Run: {run_ts}')
log('=' * 70)
log('MOTIVATION: Script 32b -- 2023 left-tail anomaly concentrated in NE.')
log('  385 of 2,507 2023 obs (15.4%) below p5 (expected 5%).')
log('  TUENSANG 2023 swing = +-3.21. 8 of bottom 10 extreme obs are NE.')
log('  This check: do main results survive NE exclusion?')
log('=' * 70)


# =============================================================================
# [1/9] LOAD AND ASSERT INPUT
# =============================================================================
log('\n[1/9] Loading regression panel...')

df = pd.read_csv(INPUT_PATH)

assert len(df) == 23347, \
    f'Expected 23,347 rows, got {len(df):,}. Check upstream pipeline.'
assert df.shape[1] == 23, \
    f'Expected 23 columns, got {df.shape[1]}. Check upstream pipeline.'

required_cols = [
    'district_gadm', 'state_gadm', 'quarter', 'year', 'q',
    'deposit_change_qt',
    'flood_exposure_ruleA_qt', 'flood_ruleA_L1', 'flood_ruleA_L2',
    'flood_exposure_ruleB_qt', 'flood_ruleB_L1', 'flood_ruleB_L2',
    'log_lights_qt'
]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f'Missing required columns: {missing}')

log(f'  Loaded: {len(df):,} rows, {df.shape[1]} columns -- PASS')
log(f'  Required columns verified -- PASS')


# =============================================================================
# [2/9] COMPOSITE KEY -- VERIFY FULL SAMPLE
# =============================================================================
log('\n[2/9] Constructing and verifying composite key on full sample...')

df['district_state_id'] = df['district_gadm'] + '_' + df['state_gadm']

n_districts_full = df['district_state_id'].nunique()
log(f'  Full sample: {n_districts_full} unique district_state_id pairs (expected 631)')

if n_districts_full != 631:
    raise ValueError(
        f'Full sample district count = {n_districts_full}, expected 631. ' 
        f'Check composite key or upstream pipeline.'
    )
log('  Full sample composite key verified -- PASS')


# =============================================================================
# [3/9] VERIFY NE STATES PRESENT BEFORE FILTER
# =============================================================================
log('\n[3/9] Verifying all 8 Northeast states present before exclusion...')

states_in_data = df['state_gadm'].unique().tolist()
ne_states_found     = [s for s in NE_STATES if s in states_in_data]
ne_states_not_found = [s for s in NE_STATES if s not in states_in_data]

log(f'  NE states found in data:     {len(ne_states_found)} of 8')
log(f'  NE states not found in data: {len(ne_states_not_found)}')

if ne_states_not_found:
    log(f'  WARNING: These NE states not found: {ne_states_not_found}')
    log(f'  Check state_gadm field spelling. Filter will proceed.')
    log(f'  States present in data sample: {sorted(states_in_data)[:10]}...')
else:
    log('  All 8 NE states confirmed present -- PASS')

ne_obs_count = df[df['state_gadm'].isin(NE_STATES)].shape[0]
ne_dist_count = df[df['state_gadm'].isin(NE_STATES)]['district_state_id'].nunique()
log(f'  NE district-quarters (to be excluded): {ne_obs_count:,}')
log(f'  NE unique districts (to be excluded):  {ne_dist_count}')


# =============================================================================
# [4/9] CONSTRUCT Z_i PROXIES ON FULL SAMPLE (before NE filter)
# =============================================================================
log('\n[4/9] Constructing Z_i proxies on FULL sample (before NE exclusion)...')
log('  CRITICAL: Thresholds must match Script 30 exactly.')
log('  Proxies computed on full sample -> same classification as main results.')

# -- urban_proxy --
district_mean_lights = (
    df.groupby('district_state_id')['log_lights_qt']
    .mean()
    .rename('mean_log_lights')
)
median_lights = district_mean_lights.median()
urban_map = (district_mean_lights > median_lights).astype(int)
df['urban_proxy'] = df['district_state_id'].map(urban_map)

n_urban   = urban_map.sum()
n_rural   = (urban_map == 0).sum()
log(f'  urban_proxy: full-sample median log_lights_qt = {median_lights:.4f}')
log(f'    Urban (above median): {n_urban} districts')
log(f'    Rural (at/below):     {n_rural} districts')

assert df['urban_proxy'].isna().sum() == 0, \
    'urban_proxy has NaN values after construction. Check district_state_id alignment.'
log('  urban_proxy: 0 NaN -- PASS')

# -- high_exposure_proxy --
district_flood_cum = (
    df.groupby('district_state_id')['flood_exposure_ruleA_qt']
    .sum()
    .rename('cumulative_floods')
)
median_flood_cum = district_flood_cum.median()
high_exp_map = (district_flood_cum > median_flood_cum).astype(int)
df['high_exposure_proxy'] = df['district_state_id'].map(high_exp_map)

n_high = high_exp_map.sum()
n_low  = (high_exp_map == 0).sum()
log(f'  high_exposure_proxy: full-sample median cumulative floods = {median_flood_cum:.1f}')
log(f'    High exposure (strictly above median): {n_high} districts')
log(f'    Low  exposure (at/below median):       {n_low} districts')
log(f'    Note: threshold strictly > {median_flood_cum:.1f} (consistent with Script 30)')

assert df['high_exposure_proxy'].isna().sum() == 0, \
    'high_exposure_proxy has NaN values. Check district_state_id alignment.'
log('  high_exposure_proxy: 0 NaN -- PASS')

# -- monsoon_qt --
df['monsoon_qt'] = (df['q'] == 3).astype(int)
monsoon_count = df['monsoon_qt'].sum()
log(f'  monsoon_qt: {monsoon_count:,} Q3 obs (expected ~23,347 / 4 = ~5,837)')
log('  Z_i construction on full sample complete -- PASS')


# =============================================================================
# [5/9] FILTER OUT NORTHEAST STATES
# =============================================================================
log('\n[5/9] Applying Northeast exclusion filter...')

initial_n = len(df)
df_ne = df[~df['state_gadm'].isin(NE_STATES)].copy()
excluded_n  = initial_n - len(df_ne)
remaining_n = len(df_ne)

assert excluded_n > 0, \
    'No NE observations excluded. Check NE_STATES list and state_gadm field.'
assert remaining_n == initial_n - excluded_n, \
    f'Row count mismatch after filter: {remaining_n} + {excluded_n} != {initial_n}.'

log(f'  Initial:   {initial_n:,} obs')
log(f'  Excluded:  {excluded_n:,} obs ({100*excluded_n/initial_n:.2f}% of panel)')
log(f'  Remaining: {remaining_n:,} obs')

n_districts_ne = df_ne['district_state_id'].nunique()
log(f'  Districts remaining: {n_districts_ne} (from 631 full sample)')
log(f'  Districts excluded:  {631 - n_districts_ne}')


# =============================================================================
# [6/9] VERIFY NE EXCLUSION COMPLETE
# =============================================================================
log('\n[6/9] Verifying NE exclusion is complete...')

ne_remaining = df_ne[df_ne['state_gadm'].isin(NE_STATES)].shape[0]
assert ne_remaining == 0, \
    f'NE exclusion failed: {ne_remaining} NE obs remain after filter.'
log(f'  NE obs remaining after filter: {ne_remaining} -- PASS')

states_remaining = df_ne['state_gadm'].unique()
ne_in_remaining  = [s for s in NE_STATES if s in states_remaining]
assert len(ne_in_remaining) == 0, \
    f'NE states still present after filter: {ne_in_remaining}'
log(f'  NE states in filtered sample: {len(ne_in_remaining)} -- PASS')
log(f'  Non-NE states in filtered sample: {len(states_remaining)}')


# =============================================================================
# [7/9] VERIFY LAG ARITHMETIC ON FILTERED SAMPLE
# =============================================================================
log('\n[7/9] Verifying lag arithmetic on NE-excluded sample...')

nan_A_L1 = df_ne['flood_ruleA_L1'].isna().sum()
nan_A_L2 = df_ne['flood_ruleA_L2'].isna().sum()
nan_B_L1 = df_ne['flood_ruleB_L1'].isna().sum()
nan_B_L2 = df_ne['flood_ruleB_L2'].isna().sum()

# Expected: exactly n_districts_ne per lag level (structural first-obs NaN)
expected_L1 = n_districts_ne
expected_L2 = 2 * n_districts_ne

log(f'  Rule A L1 NaN: {nan_A_L1:,}  (expected {expected_L1:,} = {n_districts_ne} districts x 1)')
log(f'  Rule A L2 NaN: {nan_A_L2:,}  (expected {expected_L2:,} = {n_districts_ne} districts x 2)')
log(f'  Rule B L1 NaN: {nan_B_L1:,}  (expected {expected_L1:,})')
log(f'  Rule B L2 NaN: {nan_B_L2:,}  (expected {expected_L2:,})')

assert nan_A_L1 == expected_L1, \
    f'Rule A L1 NaN = {nan_A_L1}, expected {expected_L1}. Composite key error in lag construction.'
assert nan_A_L2 == expected_L2, \
    f'Rule A L2 NaN = {nan_A_L2}, expected {expected_L2}. Composite key error in lag construction.'
assert nan_B_L1 == expected_L1, \
    f'Rule B L1 NaN = {nan_B_L1}, expected {expected_L1}.'
assert nan_B_L2 == expected_L2, \
    f'Rule B L2 NaN = {nan_B_L2}, expected {expected_L2}.'

log('  Lag arithmetic on NE-excluded sample -- PASS')

n_quarters_ne   = df_ne['quarter'].nunique()
n_ruleA_ne      = int(df_ne['flood_exposure_ruleA_qt'].sum())
n_ruleB_ne      = int(df_ne['flood_exposure_ruleB_qt'].sum())

log(f'\n  Filtered sample summary:')
log(f'    Obs:              {remaining_n:,}')
log(f'    Districts:        {n_districts_ne}')
log(f'    Quarters:         {n_quarters_ne}')
log(f'    Rule A events:    {n_ruleA_ne:,}')
log(f'    Rule B events:    {n_ruleB_ne:,}')


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
    if pval < 0.01:   sig = '***'
    elif pval < 0.05: sig = '**'
    elif pval < 0.10: sig = '*'
    else:             sig = ''
    return coef, se, tstat, pval, ci_lo, ci_hi, sig


def print_coef(label, coef, se, tstat, pval, ci_lo, ci_hi, sig, anchor=None):
    print(f'    [{label}]')
    print(f'      Beta    = {coef:.6f}  (main: {anchor["beta"]:+.6f})' if anchor else
          f'      Beta    = {coef:.6f}')
    print(f'      SE      = {se:.6f}')
    print(f'      t       = {tstat:.3f}')
    print(f'      p       = {pval:.6f}  (main: {anchor["p"]:.3f})' if anchor else
          f'      p       = {pval:.6f}')
    print(f'      95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]')
    print(f'      Status  = {sig if sig else "NOT SIGNIFICANT"}')


def log_coef(label, coef, se, tstat, pval, ci_lo, ci_hi, sig, anchor=None):
    log(f'  [{label}]')
    log(f'    Beta    = {coef:.6f}  (main: {anchor["beta"]:+.6f})' if anchor else
        f'    Beta    = {coef:.6f}')
    log(f'    SE      = {se:.6f}')
    log(f'    t       = {tstat:.3f}')
    log(f'    p       = {pval:.6f}  (main: {anchor["p"]:.3f})' if anchor else
        f'    p       = {pval:.6f}')
    log(f'    95% CI  = [{ci_lo:.6f}, {ci_hi:.6f}]')
    log(f'    Status  = {sig if sig else "NOT SIGNIFICANT"}')


# =============================================================================
# [8/9] H3: DISTRIBUTED LAG ON NE-EXCLUDED SAMPLE
# =============================================================================
log('\n' + '=' * 70)
log('[8/9] H3: DISTRIBUTED LAG -- NE-EXCLUDED SAMPLE')
log('=' * 70)
log('  Spec: quarter FE only (NO district FE). SE: clustered district_state_id.')
log('  Pre-committed H3 design. Identical to Script 29 except NE excluded.')

# Encode quarter FE
df_ne['quarter_fe'] = pd.Categorical(df_ne['quarter'])

# --- H3 Rule A: restrict to complete cases ---
df_H3_A = df_ne[
    df_ne['deposit_change_qt'].notna()       &
    df_ne['flood_exposure_ruleA_qt'].notna() &
    df_ne['flood_ruleA_L1'].notna()           &
    df_ne['flood_ruleA_L2'].notna()
].copy()

# --- H3 Rule B: restrict to complete cases ---
df_H3_B = df_ne[
    df_ne['deposit_change_qt'].notna()       &
    df_ne['flood_exposure_ruleB_qt'].notna() &
    df_ne['flood_ruleB_L1'].notna()           &
    df_ne['flood_ruleB_L2'].notna()
].copy()

n_qfe_H3_A = df_H3_A['quarter_fe'].nunique()
n_qfe_H3_B = df_H3_B['quarter_fe'].nunique()

log(f'\n  Rule A complete cases: {len(df_H3_A):,}  (expected ~35)')
log(f'  Rule B complete cases: {len(df_H3_B):,}')
log(f'  Quarter FE (Rule A):   {n_qfe_H3_A}  (expected 35)')
log(f'  Quarter FE (Rule B):   {n_qfe_H3_B}  (expected 35)')

if n_qfe_H3_A < 33 or n_qfe_H3_A > 37:
    raise ValueError(
        f'H3 Quarter FE = {n_qfe_H3_A}, outside expected range [33, 37]. ' 
        f'Check sample restriction.'
    )

# --- H3 Rule A regression ---
log('\n  H3 Rule A:')
log(f'  Dependent: deposit_change_qt')
log(f'  Regressors: flood_ruleA t0, t-1, t-2 | Quarter FE | Clustered SE')

formula_H3_A = ('deposit_change_qt ~ flood_exposure_ruleA_qt + '
                'flood_ruleA_L1 + flood_ruleA_L2 + C(quarter_fe)')

try:
    model_H3_A = ols(formula_H3_A, data=df_H3_A).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_H3_A['district_state_id']}
    )
    log(f'  Model fitted: N={model_H3_A.nobs:,.0f}, R2={model_H3_A.rsquared:.4f} -- PASS')
except Exception as e:
    log(f'  FAILED: {e}')
    raise

c_H3A_t0, s_H3A_t0, t_H3A_t0, p_H3A_t0, lo_H3A_t0, hi_H3A_t0, sg_H3A_t0 = extract_coef(model_H3_A, 'flood_exposure_ruleA_qt')
c_H3A_t1, s_H3A_t1, t_H3A_t1, p_H3A_t1, lo_H3A_t1, hi_H3A_t1, sg_H3A_t1 = extract_coef(model_H3_A, 'flood_ruleA_L1')
c_H3A_t2, s_H3A_t2, t_H3A_t2, p_H3A_t2, lo_H3A_t2, hi_H3A_t2, sg_H3A_t2 = extract_coef(model_H3_A, 'flood_ruleA_L2')

log_coef('t0  Current quarter', c_H3A_t0, s_H3A_t0, t_H3A_t0, p_H3A_t0, lo_H3A_t0, hi_H3A_t0, sg_H3A_t0, ANCHORS_H3['t0'])
log_coef('t-1 One quarter lag', c_H3A_t1, s_H3A_t1, t_H3A_t1, p_H3A_t1, lo_H3A_t1, hi_H3A_t1, sg_H3A_t1, ANCHORS_H3['t-1'])
log_coef('t-2 Two quarter lag', c_H3A_t2, s_H3A_t2, t_H3A_t2, p_H3A_t2, lo_H3A_t2, hi_H3A_t2, sg_H3A_t2, ANCHORS_H3['t-2'])

# --- H3 Rule B regression ---
log('\n  H3 Rule B:')

formula_H3_B = ('deposit_change_qt ~ flood_exposure_ruleB_qt + '
                'flood_ruleB_L1 + flood_ruleB_L2 + C(quarter_fe)')

try:
    model_H3_B = ols(formula_H3_B, data=df_H3_B).fit(
        cov_type='cluster',
        cov_kwds={'groups': df_H3_B['district_state_id']}
    )
    log(f'  Model fitted: N={model_H3_B.nobs:,.0f}, R2={model_H3_B.rsquared:.4f} -- PASS')
except Exception as e:
    log(f'  FAILED: {e}')
    raise

c_H3B_t0, s_H3B_t0, t_H3B_t0, p_H3B_t0, lo_H3B_t0, hi_H3B_t0, sg_H3B_t0 = extract_coef(model_H3_B, 'flood_exposure_ruleB_qt')
c_H3B_t1, s_H3B_t1, t_H3B_t1, p_H3B_t1, lo_H3B_t1, hi_H3B_t1, sg_H3B_t1 = extract_coef(model_H3_B, 'flood_ruleB_L1')
c_H3B_t2, s_H3B_t2, t_H3B_t2, p_H3B_t2, lo_H3B_t2, hi_H3B_t2, sg_H3B_t2 = extract_coef(model_H3_B, 'flood_ruleB_L2')

log_coef('t0  Current quarter', c_H3B_t0, s_H3B_t0, t_H3B_t0, p_H3B_t0, lo_H3B_t0, hi_H3B_t0, sg_H3B_t0)
log_coef('t-1 One quarter lag', c_H3B_t1, s_H3B_t1, t_H3B_t1, p_H3B_t1, lo_H3B_t1, hi_H3B_t1, sg_H3B_t1)
log_coef('t-2 Two quarter lag', c_H3B_t2, s_H3B_t2, t_H3B_t2, p_H3B_t2, lo_H3B_t2, hi_H3B_t2, sg_H3B_t2)


# =============================================================================
# H4: HETEROGENEITY ON NE-EXCLUDED SAMPLE
# =============================================================================
log('\n' + '=' * 70)
log('H4: HETEROGENEITY -- NE-EXCLUDED SAMPLE')
log('=' * 70)
log('  Spec: district FE + quarter FE. SE: clustered district_state_id.')
log('  Z_i thresholds from FULL sample (Script 30 consistent).')
log(f'  urban_proxy median threshold:         {median_lights:.4f}')
log(f'  high_exposure_proxy median threshold: {median_flood_cum:.1f}')

# Complete cases for H4 (deposit + flood, no lag restriction)
df_H4 = df_ne[
    df_ne['deposit_change_qt'].notna()       &
    df_ne['flood_exposure_ruleA_qt'].notna() &
    df_ne['flood_exposure_ruleB_qt'].notna()
].copy()

df_H4['quarter_fe'] = pd.Categorical(df_H4['quarter'])
n_qfe_H4  = df_H4['quarter_fe'].nunique()
n_dfe_H4  = df_H4['district_state_id'].nunique()

log(f'\n  H4 complete cases: {len(df_H4):,}')
log(f'  District FE:       {n_dfe_H4}  (from {n_districts_ne} NE-excluded)')
log(f'  Quarter FE:        {n_qfe_H4}  (expected 36)')

if n_qfe_H4 < 34 or n_qfe_H4 > 38:
    raise ValueError(
        f'H4 Quarter FE = {n_qfe_H4}, outside expected range [34, 38].'
    )

H4_specs = [
    ('H4a', 'urban_proxy',         'flood_exposure_ruleA_qt:urban_proxy',         'A'),
    ('H4a', 'urban_proxy',         'flood_exposure_ruleB_qt:urban_proxy',         'B'),
    ('H4b', 'high_exposure_proxy', 'flood_exposure_ruleA_qt:high_exposure_proxy', 'A'),
    ('H4b', 'high_exposure_proxy', 'flood_exposure_ruleB_qt:high_exposure_proxy', 'B'),
    ('H4c', 'monsoon_qt',          'flood_exposure_ruleA_qt:monsoon_qt',          'A'),
    ('H4c', 'monsoon_qt',          'flood_exposure_ruleB_qt:monsoon_qt',          'B'),
]

H4_results = []

for spec, proxy_var, interaction_term, rule in H4_specs:
    flood_var = f'flood_exposure_rule{rule}_qt'
    formula = (
        f'deposit_change_qt ~ {flood_var} + {flood_var}:{proxy_var} + '
        f'C(district_state_id) + C(quarter_fe)'
    )
    log(f'\n  {spec} Rule {rule}: {interaction_term}')
    log(f'  Formula: deposit ~ {flood_var} + {flood_var}:{proxy_var} + distFE + qtrFE')

    try:
        model_H4 = ols(formula, data=df_H4).fit(
            cov_type='cluster',
            cov_kwds={'groups': df_H4['district_state_id']}
        )
        log(f'  Model fitted: N={model_H4.nobs:,.0f}, R2={model_H4.rsquared:.4f} -- PASS')
    except Exception as e:
        log(f'  FAILED: {e}')
        raise

    # Baseline flood coefficient
    c_base, s_base, t_base, p_base, lo_base, hi_base, sg_base = extract_coef(model_H4, flood_var)
    # Interaction coefficient
    c_int,  s_int,  t_int,  p_int,  lo_int,  hi_int,  sg_int  = extract_coef(model_H4, interaction_term)

    anchor = ANCHORS_H4_INTERACTION.get(spec) if rule == 'A' else None

    log(f'  Baseline flood (beta0): {c_base:+.6f}, SE={s_base:.6f}, p={p_base:.4f} {sg_base}')
    if anchor:
        log(f'  Interaction (beta1):    {c_int:+.6f}, SE={s_int:.6f}, p={p_int:.4f} {sg_int}')
        log(f'    Main result anchor:   {anchor["beta"]:+.6f}, p={anchor["p"]:.3f}')
    else:
        log(f'  Interaction (beta1):    {c_int:+.6f}, SE={s_int:.6f}, p={p_int:.4f} {sg_int}')

    H4_results.append({
        'hypothesis':        spec,
        'rule':              rule,
        'proxy_variable':    proxy_var,
        'baseline_coef':     round(c_base, 6),
        'baseline_se':       round(s_base, 6),
        'baseline_p':        round(p_base, 6),
        'interaction_coef':  round(c_int,  6),
        'interaction_se':    round(s_int,  6),
        'interaction_t':     round(t_int,  3),
        'interaction_p':     round(p_int,  6),
        'ci_lower_95':       round(lo_int, 6),
        'ci_upper_95':       round(hi_int, 6),
        'significance':      sg_int,
        'n_obs':             int(model_H4.nobs),
        'district_fe_count': n_dfe_H4,
        'quarter_fe_count':  n_qfe_H4,
        'se_type':           'clustered_by_district_state_id',
        'sample':            'NE_excluded',
        'ne_states_excluded': '|'.join(NE_STATES),
        'n_districts_excluded': 631 - n_districts_ne
    })


# =============================================================================
# [9/9] SIDE-BY-SIDE COMPARISON AND SAVE
# =============================================================================
log('\n' + '=' * 70)
log('[9/9] SIDE-BY-SIDE COMPARISON: MAIN vs NE-EXCLUDED')
log('=' * 70)

log('\n  H3 Rule A:')
log(f'  {"Lag":<6} {"Main beta":>12} {"Main p":>10} {"NE-excl beta":>14} {"NE-excl p":>12} {"Direction":>10}')
log(f'  {"-"*68}')

for lag_label, c_main, p_main, c_ne, p_ne in [
    ('t0',  ANCHORS_H3['t0']['beta'],  ANCHORS_H3['t0']['p'],  c_H3A_t0, p_H3A_t0),
    ('t-1', ANCHORS_H3['t-1']['beta'], ANCHORS_H3['t-1']['p'], c_H3A_t1, p_H3A_t1),
    ('t-2', ANCHORS_H3['t-2']['beta'], ANCHORS_H3['t-2']['p'], c_H3A_t2, p_H3A_t2),
]:
    direction = 'SAME' if (c_main * c_ne > 0) else 'REVERSED'
    sig_change = 'SIG' if p_ne < 0.05 else 'null'
    log(f'  {lag_label:<6} {c_main:>12.6f} {p_main:>10.4f} {c_ne:>14.6f} {p_ne:>12.6f} {direction:>10} ({sig_change})')

log('\n  H4 Interactions (Rule A):')
log(f'  {"Spec":<6} {"Main beta":>12} {"Main p":>10} {"NE-excl beta":>14} {"NE-excl p":>12} {"Direction":>10}')
log(f'  {"-"*68}')

for res in H4_results:
    if res['rule'] == 'A':
        anchor = ANCHORS_H4_INTERACTION[res['hypothesis']]
        c_main  = anchor['beta']
        p_main  = anchor['p']
        c_ne    = res['interaction_coef']
        p_ne    = res['interaction_p']
        direction = 'SAME' if (c_main * c_ne > 0) else 'REVERSED'
        sig_change = 'SIG' if p_ne < 0.05 else 'null'
        log(f'  {res["hypothesis"]:<6} {c_main:>12.6f} {p_main:>10.4f} '
            f'{c_ne:>14.6f} {p_ne:>12.6f} {direction:>10} ({sig_change})')

# Conclusion
log('\n  CRITICAL VERDICT:')
t2_robust  = p_H3A_t2 < 0.05 and c_H3A_t2 < 0
h4b_robust = next((r['interaction_p'] < 0.10 for r in H4_results
                   if r['hypothesis'] == 'H4b' and r['rule'] == 'A'), False)

if t2_robust:
    log('  H3 t-2: ROBUST to NE exclusion. Effect not driven by NE districts.')
else:
    log('  H3 t-2: NOT ROBUST. Effect disappears after NE exclusion.')
    log('  ACTION REQUIRED: Results section must note NE district sensitivity.')
    log('  DO NOT begin Results writing until this is documented.')

if h4b_robust:
    log('  H4b: ROBUST to NE exclusion. High-exposure heterogeneity not NE-driven.')
else:
    log('  H4b: NOT ROBUST to NE exclusion. Investigate before writing H4 results.')


# --- Save H3 output ---
h3_rows = []
for rule, lags, coefs, ses, tstats, pvals, cilos, cihis, sigs, n_obs in [
    ('A', ['t0', 't-1', 't-2'],
     [c_H3A_t0, c_H3A_t1, c_H3A_t2],
     [s_H3A_t0, s_H3A_t1, s_H3A_t2],
     [t_H3A_t0, t_H3A_t1, t_H3A_t2],
     [p_H3A_t0, p_H3A_t1, p_H3A_t2],
     [lo_H3A_t0, lo_H3A_t1, lo_H3A_t2],
     [hi_H3A_t0, hi_H3A_t1, hi_H3A_t2],
     [sg_H3A_t0, sg_H3A_t1, sg_H3A_t2],
     int(model_H3_A.nobs)),
    ('B', ['t0', 't-1', 't-2'],
     [c_H3B_t0, c_H3B_t1, c_H3B_t2],
     [s_H3B_t0, s_H3B_t1, s_H3B_t2],
     [t_H3B_t0, t_H3B_t1, t_H3B_t2],
     [p_H3B_t0, p_H3B_t1, p_H3B_t2],
     [lo_H3B_t0, lo_H3B_t1, lo_H3B_t2],
     [hi_H3B_t0, hi_H3B_t1, hi_H3B_t2],
     [sg_H3B_t0, sg_H3B_t1, sg_H3B_t2],
     int(model_H3_B.nobs))
]:
    for i, lag in enumerate(lags):
        h3_rows.append({
            'hypothesis':         'H3',
            'rule':               rule,
            'lag':                lag,
            'coefficient':        round(coefs[i],  6),
            'std_error':          round(ses[i],    6),
            't_statistic':        round(tstats[i], 3),
            'p_value':            round(pvals[i],  6),
            'ci_lower_95':        round(cilos[i],  6),
            'ci_upper_95':        round(cihis[i],  6),
            'significance':       sigs[i],
            'n_obs':              n_obs,
            'quarter_fe_count':   n_qfe_H3_A,
            'district_fe':        'NONE (pre-committed H3 design)',
            'se_type':            'clustered_by_district_state_id',
            'sample':             'NE_excluded',
            'ne_states_excluded': '|'.join(NE_STATES),
            'n_ne_districts_excl': 631 - n_districts_ne
        })

h3_df = pd.DataFrame(h3_rows)
h4_df = pd.DataFrame(H4_results)

assert len(h3_df) == 6,  f'H3 output: expected 6 rows (3 lags x 2 rules), got {len(h3_df)}.'
assert len(h4_df) == 6,  f'H4 output: expected 6 rows (3 specs x 2 rules), got {len(h4_df)}.'

h3_df.to_csv(OUT_H3, index=False)
h4_df.to_csv(OUT_H4, index=False)

assert os.path.exists(OUT_H3), f'H3 output not saved: {OUT_H3}'
assert os.path.exists(OUT_H4), f'H4 output not saved: {OUT_H4}'

log(f'\n  H3 table saved: {OUT_H3}  ({len(h3_df)} rows) -- PASS')
log(f'  H4 table saved: {OUT_H4}  ({len(h4_df)} rows) -- PASS')

# Write log
with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))
assert os.path.exists(LOG_PATH), f'Log not saved: {LOG_PATH}'
log(f'  Log saved:   {LOG_PATH} -- PASS')


# === COMPLETION ===
log('\n' + '=' * 70)
log('SCRIPT 33 COMPLETE')
log(f'  NE districts excluded:  {631 - n_districts_ne} (of 631)')
log(f'  NE obs excluded:        {excluded_n:,} (of 23,347)')
log(f'  H3 t-2 robust:          {"YES" if t2_robust else "NO -- ACTION REQUIRED"}')
log(f'  H4b robust:             {"YES" if h4b_robust else "NO -- INVESTIGATE"}')
log(f'  Tables: {OUT_H3}')
log(f'          {OUT_H4}')
log(f'  Log:    {LOG_PATH}')
log('=' * 70)
log('NEXT: Script 34 -- R2 Placebo Timing')
log('=' * 70)
