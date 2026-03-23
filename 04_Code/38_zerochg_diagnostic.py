"""
38_zerochg_diagnostic.py
Zero-Change Quarters Diagnostic -- deposit_change_qt
Flood Shocks and the Two-Phase Deposit Cycle: A Nighttime Lights Identification

Purpose:
  Profile zero and near-zero deposit_change_qt observations.
  Distinguish copy-forward reporting errors from true stagnation.
  Test H3 t-2 sensitivity to exclusion of zero-change quarters.
  Gate for Section 3.3 (variable construction) writing.

Data:   03_Data_Clean/regressionpanelfinal.csv  (23,347 x 23)
Output: 05_Outputs/Logs/38_zerochg_diagnostic.txt

Locked H3 reference:
  t-2 Rule A: beta=-0.007005, SE=0.001645, p<0.001 (Script 29b)
"""

import os
import sys
import textwrap
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

# ── 1. PATHS ──────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "03_Data_Clean", "regression_panel_final.csv")
LOG_PATH  = os.path.join(BASE_DIR, "05_Outputs", "Logs", "38_zerochg_diagnostic.txt")

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

# ── 2. COLUMN MAP  (edit here if Script 24 used different names) ──────────────
COL_ENTITY  = "district_gadm"
COL_TIME    = "quarter_num"
COL_DEP     = "deposit_change_qt"
COL_F0      = "flood_exposure_ruleA_qt"
COL_FL1     = "flood_ruleA_L1"
COL_FL2     = "flood_ruleA_L2"

# ── 3. LOAD ───────────────────────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    sys.exit(f"ERROR: File not found:\n  {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

print("=" * 70)
print(f"Loaded: {DATA_PATH}")
print(f"Shape : {df.shape}")
print(f"Columns ({len(df.columns)}):")
for c in df.columns:
    print(f"  {c}")
print("=" * 70)

# ── 4. COLUMN ASSERTIONS ─────────────────────────────────────────────────────
required = [COL_ENTITY, COL_TIME, COL_DEP, COL_F0, COL_FL1, COL_FL2]
missing  = [c for c in required if c not in df.columns]
if missing:
    sys.exit(
        f"ERROR: Missing columns: {missing}\n"
        f"Update the COLUMN MAP section.\n"
        f"Available: {df.columns.tolist()}"
    )
print("Column assertions PASS.\n")

# ── 5. CORE ASSERTION: ROW COUNT ─────────────────────────────────────────────
assert len(df) == 23347, (
    f"Expected 23,347 rows. Got {len(df)}. "
    f"Wrong file or file has been modified."
)
print("Row count assertion PASS: 23,347\n")

# ── 6. PROFILE deposit_change_qt ─────────────────────────────────────────────
chg = df[COL_DEP].dropna()
n_total    = len(chg)
n_exact0   = (chg == 0).sum()
n_near0    = (chg.abs() < 0.001).sum()
n_small    = (chg.abs() < 0.003).sum()
pct_exact0 = 100 * n_exact0 / n_total
pct_near0  = 100 * n_near0  / n_total
pct_small  = 100 * n_small  / n_total

desc = chg.describe(percentiles=[.01, .05, .10, .25, .50, .75, .90, .95, .99])

print("── DISTRIBUTION PROFILE ─────────────────────────────────────────────")
print(desc.to_string())
print()
print(f"Exact zero     (== 0.000):  {n_exact0:,}  ({pct_exact0:.2f}%)")
print(f"Near-zero  (|x| < 0.001):  {n_near0:,}  ({pct_near0:.2f}%)")
print(f"Small      (|x| < 0.003):  {n_small:,}  ({pct_small:.2f}%)")
print()

# ── 7. COPY-FORWARD TEST ──────────────────────────────────────────────────────
# Copy-forward: same district has CONSECUTIVE zero-change quarters.
# True stagnation or rounding: zeros are randomly distributed across districts.
df_sorted = df.sort_values([COL_ENTITY, COL_TIME]).copy()
df_sorted["is_zero"] = (df_sorted[COL_DEP] == 0).astype(int)

# Consecutive zero run: within district, previous quarter was also zero
df_sorted["prev_zero"] = df_sorted.groupby(COL_ENTITY)["is_zero"].shift(1)
n_consec_zero = int(
    ((df_sorted["is_zero"] == 1) & (df_sorted["prev_zero"] == 1)).sum()
)

# Districts with ANY exact-zero
zero_by_dist = df[df[COL_DEP] == 0].groupby(COL_ENTITY).size()
n_districts_with_zero = len(zero_by_dist)
max_zeros_one_district = int(zero_by_dist.max()) if len(zero_by_dist) > 0 else 0
median_zeros_per_dist  = float(zero_by_dist.median()) if len(zero_by_dist) > 0 else 0

# Zero rate by quarter (time clustering)
zero_by_qtr = df[df[COL_DEP] == 0].groupby(COL_TIME).size()
max_zeros_one_qtr    = int(zero_by_qtr.max())   if len(zero_by_qtr) > 0 else 0
median_zeros_per_qtr = float(zero_by_qtr.median()) if len(zero_by_qtr) > 0 else 0

print("── COPY-FORWARD TEST ────────────────────────────────────────────────")
print(f"Districts with >= 1 exact zero:         {n_districts_with_zero}")
print(f"Max exact zeros in one district:         {max_zeros_one_district}")
print(f"Median exact zeros per district:         {median_zeros_per_dist:.1f}")
print(f"Consecutive zero pairs (within-dist):    {n_consec_zero}")
print(f"Max exact zeros in one quarter:          {max_zeros_one_qtr}")
print(f"Median exact zeros per quarter:          {median_zeros_per_qtr:.1f}")
print()

# Diagnosis
if n_exact0 == 0:
    zero_diagnosis = "NO EXACT ZEROS -- no copy-forward concern. Section 3.3 unblocked."
elif n_consec_zero > 0.5 * n_exact0:
    zero_diagnosis = (
        "COPY-FORWARD LIKELY: majority of zeros are consecutive within districts. "
        "Disclosure required in Section 3.3."
    )
elif max_zeros_one_district > 4:
    zero_diagnosis = (
        "PARTIAL COPY-FORWARD: some districts show repeated zeros (max="
        f"{max_zeros_one_district}). Monitor. Disclosure recommended in Section 3.3."
    )
else:
    zero_diagnosis = (
        "LOW COPY-FORWARD RISK: zeros not predominantly consecutive. "
        "Consistent with true stagnation or RBI rounding. "
        "Brief disclosure sufficient in Section 3.3."
    )

print(f"DIAGNOSIS: {zero_diagnosis}\n")

# ── 8. H3 t-2 SENSITIVITY ────────────────────────────────────────────────────
# Replicates Script 29b specification:
#   PanelOLS, time_effects=True, entity_effects=False, clustered by district_state_id
# Locked: beta_L2 = -0.007005, SE=0.001645, p<0.001

LOCKED_BETA_L2 = -0.007005
LOCKED_SE_L2   =  0.001645
DELTA_THRESHOLD = 0.001      # material change threshold

print("── H3 t-2 SENSITIVITY (zero-exclusion) ──────────────────────────────")

def run_h3(data, label):
    """Run H3 distributed lag spec on a given subsample."""
    sub = data[[COL_ENTITY, COL_TIME, COL_DEP, COL_F0, COL_FL1, COL_FL2]].dropna()
    n = len(sub)

    # Build panel index
    sub = sub.copy()
    sub["quarter_int_sorted"] = sub[COL_TIME].astype(int)
    panel = sub.set_index([COL_ENTITY, "quarter_int_sorted"])

    y = panel[COL_DEP]
    X = panel[[COL_F0, COL_FL1, COL_FL2]]

    # Add constant (absorbed by time FE, but linearmodels requires no separate const
    # when time_effects=True -- omit)
    mod = PanelOLS(
        dependent   = y,
        exog        = X,
        time_effects  = True,
        entity_effects = False
    )
    clusters = panel[COL_ENTITY] if COL_ENTITY in panel.columns else panel.index.get_level_values(0)
    fit = mod.fit(
        cov_type = "clustered",
        cluster_entity = True
    )

    beta_L2 = fit.params[COL_FL2]
    se_L2   = fit.std_errors[COL_FL2]
    p_L2    = fit.pvalues[COL_FL2]
    delta   = abs(beta_L2 - LOCKED_BETA_L2)
    material = "YES -- INVESTIGATE" if delta > DELTA_THRESHOLD else "NO"

    print(f"\n  Spec: {label}")
    print(f"    N              = {n:,}")
    print(f"    beta_L2        = {beta_L2:+.6f}")
    print(f"    SE_L2          = {se_L2:.6f}")
    print(f"    p_L2           = {p_L2:.6f}")
    print(f"    delta vs locked= {delta:.6f}  (threshold={DELTA_THRESHOLD})")
    print(f"    Material change= {material}")

    return {
        "label": label, "n": n,
        "beta_L2": beta_L2, "se_L2": se_L2, "p_L2": p_L2,
        "delta": delta, "material": material
    }

results = []

# Spec 1: Full sample (replication check -- should match locked exactly)
results.append(run_h3(df, "Full sample (replication of Script 29b)"))

# Spec 2: Exclude exact zeros
df_no0 = df[df[COL_DEP] != 0]
results.append(run_h3(df_no0, "Exclude exact zeros (deposit_change_qt == 0)"))

# Spec 3: Exclude near-zeros
df_nonear = df[df[COL_DEP].abs() >= 0.001]
results.append(run_h3(df_nonear, "Exclude near-zeros (|deposit_change_qt| < 0.001)"))

print()

# ── 9. VERDICT ────────────────────────────────────────────────────────────────
any_material = any(r["material"] == "YES -- INVESTIGATE" for r in results[1:])
if any_material:
    verdict = (
        "WARNING: H3 t-2 coefficient changes materially under zero exclusion. "
        "Investigate before writing Section 5.3."
    )
else:
    verdict = (
        "PASS: H3 t-2 coefficient stable under zero exclusion. "
        "Writing unblocked on this dimension."
    )

print("── VERDICT ──────────────────────────────────────────────────────────")
print(f"  Zero-change concern:  {zero_diagnosis}")
print(f"  H3 sensitivity:       {verdict}")
print()

# ── 10. WRITE LOG ─────────────────────────────────────────────────────────────
lines = []
lines.append("=" * 70)
lines.append("38_zerochg_diagnostic.txt")
lines.append("Zero-Change Quarters Diagnostic -- deposit_change_qt")
lines.append("Flood Shocks and the Two-Phase Deposit Cycle: A Nighttime Lights Identification")
lines.append("=" * 70)
lines.append(f"Data : {DATA_PATH}")
lines.append(f"N    : {len(df):,}")
lines.append("")
lines.append("── DISTRIBUTION PROFILE ─────────────────────────────────────────")
lines.append(desc.to_string())
lines.append("")
lines.append(f"Exact zero     (== 0.000):  {n_exact0:,}  ({pct_exact0:.2f}%)")
lines.append(f"Near-zero  (|x| < 0.001):  {n_near0:,}  ({pct_near0:.2f}%)")
lines.append(f"Small      (|x| < 0.003):  {n_small:,}  ({pct_small:.2f}%)")
lines.append("")
lines.append("── COPY-FORWARD TEST ────────────────────────────────────────────")
lines.append(f"Districts with >= 1 exact zero:       {n_districts_with_zero}")
lines.append(f"Max zeros in one district:            {max_zeros_one_district}")
lines.append(f"Median zeros per district:            {median_zeros_per_dist:.1f}")
lines.append(f"Consecutive zero pairs (within-dist): {n_consec_zero}")
lines.append(f"Max zeros in one quarter:             {max_zeros_one_qtr}")
lines.append(f"Median zeros per quarter:             {median_zeros_per_qtr:.1f}")
lines.append(f"DIAGNOSIS: {zero_diagnosis}")
lines.append("")
lines.append("── H3 t-2 SENSITIVITY ───────────────────────────────────────────")
lines.append(f"Locked reference: beta_L2={LOCKED_BETA_L2}, SE={LOCKED_SE_L2}, p<0.001 (Script 29b)")
for r in results:
    lines.append(f"\n  {r['label']}")
    lines.append(f"    N={r['n']:,}  beta_L2={r['beta_L2']:+.6f}  SE={r['se_L2']:.6f}  "
                 f"p={r['p_L2']:.6f}  delta={r['delta']:.6f}  material={r['material']}")
lines.append("")
lines.append("── VERDICT ──────────────────────────────────────────────────────")
lines.append(f"  {zero_diagnosis}")
lines.append(f"  {verdict}")
lines.append("")
lines.append("── SECTION 3.3 WRITING GATE ─────────────────────────────────────")
if any_material:
    lines.append("  BLOCKED. Investigate H3 sensitivity before writing Section 5.3.")
else:
    lines.append("  UNBLOCKED. Report near-zero frequency in Section 3.3.")
    lines.append("  If copy-forward diagnosed: add one sentence disclosing RBI")
    lines.append("  rounding/copy-forward as a data limitation.")
    lines.append("  If low risk: one sentence noting 25th pct ~0.003, consistent")
    lines.append("  with genuine low-growth quarters in smaller districts.")
lines.append("")
lines.append("=" * 70)

log_text = "\n".join(lines)
print(log_text)

with open(LOG_PATH, "w", encoding="utf-8") as f:
    f.write(log_text)

print(f"\nLog saved: {LOG_PATH}")
print("\nScript 38 COMPLETE.")
print("Paste the VERDICT lines here before committing.")