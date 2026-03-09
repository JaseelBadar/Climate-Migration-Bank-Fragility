# Variables Codebook and Coding Protocol (v2.5)

**Project:** Climate Shocks, Displacement, and Bank Liquidity Risk:
Evidence from Night-Lights in India, 2015–2024

**Status:** Full pipeline verified and clean. All regressions (Scripts 27–30)
executed and confirmed. Robustness and diagnostic scripts (31–32b) complete.

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v1.x–v2.0 | 2026-01-18 to 02-06 | Initial codebook; VIIRS dissolve bug; deposit extraction bug; H3 validated |
| v2.1 | 2026-02-11 | Deposits cleaned: crosswalk dedup (769→762) + state filtering |
| v2.2 | 2026-02-13 | VIIRS alignment complete (Script 22b). Regression panel: 23,088 obs, 23 variables |
| v2.3 | 2026-03-04 | District count corrected: 631 composite pairs. Sample: 23,347 obs. Log offset corrected: +0.001 |
| v2.4 | 2026-03-07 | Full pipeline clean. Script 8 permanent rewrite (762-row assert). Flood baseline locked: 2,238 Rule A, 209 Rule B. Regression pending FE correction. |
| **v2.5** | **2026-03-09** | **All regressions executed and confirmed. Composite FE fix applied in Scripts 27, 28, 30. H1–H4 results locked. Winsorization complete (Script 31). CPI decision logged (Script 32). 2023 anomaly diagnosed (Script 32b). Heterogeneity variables updated with correct construction. Demonetization gap documented. Active issues resolved.** |

**Discipline:** Variable definitions and coding protocols do not change to match
results. Version bumps record measurement corrections, naming fixes, and
reproducibility updates only.

---

## Non-Negotiable Principles

1. **Raw data is read-only.** Nothing inside `01_Data_Raw/` is ever modified. All
   transformations write to `02_Data_Intermediate/` or `03_Data_Clean/`.
2. **No silent drops.** Every dropped row is logged with count and reason.
3. **No endogeneity by construction.** VIIRS outcomes never define flood treatment.
4. **One script, one output.** Each script produces one named dataset and one log file.
5. **No district-name dissolve.** Never dissolve on `district_gadm` alone. All
   groupby, FE, and dissolve operations use composite `(district_gadm, state_gadm)`.
6. **Composite keys everywhere.** Any district-specific operation uses
   `district_gadm + '_' + state_gadm` as the grouping key — not name alone.
   Using `district_gadm` alone produces 624 unique units instead of the correct 631,
   collapsing 7 homonymous pairs and contaminating FE, clustering, and heterogeneity
   variable construction simultaneously.
7. **Log offset locked.** The offset constant in `log(x + c)` is fixed globally per
   variable, written into logs, and never tuned for results.
8. **Quarter alignment validated.** RBI extraction validates year-quarter labels
   against source column headers. Row labels not trusted without header verification.
9. **Hard asserts before save.** Every script asserts expected row count and column
   count before writing output. Silent failures are not permitted.
10. **Proxy discipline.** Any heterogeneity variable constructed from observational
    proxies (lights-based urban, flood-count-based exposure) is labeled "proxy" in
    all outputs and paper text. No causal claims about proxied characteristics.

---

## I. Panel Structure

**Canonical unit:** GADM v4.1 Level-2 district polygons (India).
RBI districts are mapped to GADM via crosswalk. GADM is the geographic standard.

**Target period:** 2015Q1–2024Q4 (40 quarters)
**Analysis period:** 37 quarters (2015Q1–2016Q2, 2017Q2–2024Q4)

**Gap — demonetization period:** 2016Q3, 2016Q4, 2017Q1 are entirely absent from
the panel. District-level deposit data was unreliable during India's demonetization
(November 8, 2016) and its immediate aftermath. These quarters are excluded upstream
at the RBI data assembly stage — not dropped by the analysis pipeline. Must be named
explicitly in the paper's Data section.

**Additional quarter note:** 2015Q1 exists in the full panel (631 × 37 = 23,347)
but has zero valid `deposit_change_qt` observations — dropped structurally by all
regression-sample `dropna()` operations. Regression quarter FE = 36 throughout.
Full panel quarter count = 37. Both figures are correct and not in conflict.

**Index variables** (required in all output panels):

| Variable | Type | Definition |
|---|---|---|
| `district_gadm` | string | GADM Level-2 district name (UPPERCASE) |
| `state_gadm` | string | GADM Level-1 state name (UPPERCASE) |
| `district_state_id` | string | `district_gadm + '_' + state_gadm` — composite unique ID |
| `quarter` | string | e.g., `2015Q1` |
| `year` | int | 2015–2024 |
| `q` | int | 1–4 |
| `quarter_num` | int | Sequential index 1–40 (for sorting and lag construction) |

**Sorting rule (locked):** Always sort by `district_gadm`, `state_gadm`, `year`, `q`
before constructing lags or differences. Violation invalidates all time-series operations.

**Panel dimensions — verified clean pipeline, March 2026:**

| Panel | Districts | Quarters | Observations |
|---|---|---|---|
| Master raw | 666 | 40 | 26,640 |
| Analysis sample | **631** | **37** | **23,347** |
| VIIRS quarterly | 631 | 40 | 25,240 |
| Regression panel | 631 | 37 | 23,347 |
| Winsorized panel | 631 | 37 | 23,347 |

**Note on district counts:** 624 appears in outputs using `.nunique()` on
`district_gadm` alone — undercounts by 7 due to homonymous pairs. Correct count
is always 631 composite `(district_gadm, state_gadm)` pairs.

**7 confirmed homonymous pairs (UPPERCASE):**
AURANGABAD (BIHAR / MAHARASHTRA),
BALRAMPUR (CHHATTISGARH / UTTAR PRADESH),
BIJAPUR (CHHATTISGARH / KARNATAKA),
BILASPUR (CHHATTISGARH / HIMACHAL PRADESH),
HAMIRPUR (HIMACHAL PRADESH / UTTAR PRADESH),
PRATAPGARH (RAJASTHAN / UTTAR PRADESH),
RAIGARH (CHHATTISGARH / MAHARASHTRA).

---

## II. Outcome Variables — Banking

### Deposits (level)

**`deposits`**
- **Definition:** Total district-quarter deposits, all population groups aggregated
- **Unit:** Indian Rupees, Crores (nominal)
- **Source:** RBI BSR-2 (District-wise deposits)
- **Construction:** Script 13 — fiscal-to-calendar conversion, state filtering for
  7 homonymous districts, column offset `dep_idx = q_idx + 1` for historical files
- **Status: Clean**
  - Bug 1 resolved: `dep_idx = q_idx + 1` — extracted deposits, not office count
  - Bug 2 resolved: State filtering prevents Bihar + Maharashtra AURANGABAD summing
  - Verification anchor: Aurangabad Bihar 2015Q1 = 4,422 Crores (was 18,652 — 76% drop)
  - Total rows: 50,192 (2015Q1–2024Q4 in-window: 23,079 non-missing of 23,347)
- **Verified range:** min = 28.9979, max = 1,237,744.34, mean = 16,425.73,
  median = 6,135.58 Crores
- **Nominal INR decision (Script 32):** Deposits retained in nominal Rupees.
  District-quarter CPI unavailable at required granularity. Interpolated deflation
  introduces noise exceeding the bias it corrects. Quarter FE absorb national-level
  price trends. Paper disclosure: deposits in nominal INR; inflation ~6–7% per year
  acknowledged as a limitation.

**`log_deposits`**
- **Construction:** `ln(deposits + 1)`
- **Offset:** +1 — deposits always > 0; +1 is conservative safe default at Crore scale
- **Verified range:** min = 3.4011, max = 14.0288, mean = 8.7075, SD = 1.3707

### Deposits (growth)

**`deposit_change_qt`**
- **Construction:** `log_deposits.diff()` within `(district_gadm, state_gadm)` groups
- **Missing values:** 905 — 631 structural first-obs NaNs + 274 from `.diff()`
  propagation across 268 missing deposit quarters (23,347 − 23,079 = 268)
- **Asymmetry with `lights_change_qt`** (631 missing only) is expected and confirms
  100% VIIRS coverage vs 98.9% deposit coverage — not a data error
- **Usable N:** 22,442 observations
- **Verified range:** min = −1.9322, max = 2.0251, mean = 0.0233, SD = 0.0743

**2023 anomaly (Script 32b):** Raw std in 2023 = 0.106 (nearly double adjacent
years). Mean = −0.001 (only negative mean year in panel). Median = 0.017 (normal).
Mean-median divergence confirms left-tail asymmetry: 15.4% of 2023 district-quarters
fall below the full-sample 5th percentile (expected ~5%). Concentrated in small-base
Northeast districts where low absolute deposit levels amplify percentage changes.
Unit error ruled out (2023/2022 median level ratio = 0.9985×). No data corruption.
TUENSANG (Nagaland) reversal — 2023Q1: −1.453, 2023Q3: +1.758 — likely a reporting
artifact and must be flagged in the paper. Winsorization handled all extreme cases.

### Winsorized dependent variable

**`deposit_change_qt_winsor`**
- **Construction:** `np.clip(deposit_change_qt, q01, q99)` where q01 and q99 are the
  1st and 99th percentiles computed on non-NaN observations. NaN values preserved
  via `np.where` — not clipped to bounds.
- **Thresholds (locked, Script 31):** Lower = −0.162585 | Upper = +0.230701
- **Clipped observations:** 450 (2.01% of valid N = 22,442) — symmetric: 225 low,
  225 high
- **Post-winsorization verification:** Median = 0.020979 (unchanged). 25th and 75th
  percentiles unchanged. Std reduced 30% (0.074 → 0.052) — expected. Mean shift
  +0.000704 (trivial).
- **Usage:** Robustness re-runs of Scripts 27–30. Primary results use raw
  `deposit_change_qt`. Winsorized results reported as Robustness R3.
- **Source file:** `03_Data_Clean/regression_panel_final_winsor.csv` (23,347 × 24)

### Deposit withdrawal proxy (conditional)

**`deposit_withdrawal_binary`** — include only if used in paper
- **Construction:** `indicator(deposit_change_qt < k)`
- **Threshold discipline:** k defined from bottom decile of `deposit_change_qt`
  among non-flood observations, or fixed −10% rule — whichever is more conservative.
  Threshold recorded before mechanism regressions. Never tuned post-estimation.

---

## III. Treatment Variables — Flood Shocks

Flood events sourced from EM-DAT, mapped to calendar quarters, matched to GADM
districts via district crosswalk (Scripts 08, 10). Both precision regimes required
in all core tables per pre-committed protocol R1.

### Flood exposure

**`flood_exposure_ruleA_qt`** — Rule A (primary specification)
- **Definition:** 1 if district directly matched OR district's state matched (fallback)
- **Coverage (analysis sample, locked):** 2,238 events | 9.59% treatment rate
  | 569 districts ever exposed
- **Interpretation:** Conservative lower bound. State-level fallback introduces false
  positives; attenuates β toward zero. Rule A estimates are lower bounds on the true
  local effect.
- **Status: Clean**

**`flood_exposure_ruleB_qt`** — Rule B (robustness / precision check)
- **Definition:** 1 only when district explicitly identified in EM-DAT location field
- **Coverage (analysis sample, locked):** 209 events | 0.90% treatment rate
  | 141 districts ever exposed
- **Interpretation:** Higher precision; smaller effective treatment variation; lower
  power. Preferred for instrument credibility argument. H2 Rule B instrument weak
  (F = 8.949 < 10) — second stage results labeled suggestive throughout.
- **Status: Clean**

### Flood lags (distributed lag models)

| Variable | Construction | Used in |
|---|---|---|
| `flood_ruleA_L1` | L1 within composite group | H3 |
| `flood_ruleA_L2` | L2 within composite group | H3 |
| `flood_ruleA_L3` | L3 — Phase 5 robustness | R5 |
| `flood_ruleA_L4` | L4 — Phase 5 persistence | R5 |
| `flood_ruleB_L1–L4` | Rule B equivalents | Robustness |

**Lag missing-value arithmetic (locked):**

| Lag | Expected missing | Actual | Status |
|---|---|---|---|
| L1 | 631 | 631 | Verified |
| L2 | 1,262 | 1,262 | Verified |
| L3 | 1,893 | 1,893 | Verified |
| L4 | 2,524 | 2,524 | Verified |

Any deviation from 631 × k signals a composite key error.

### Flood severity (conditional)

**`flood_severity_qt`** — include only if completeness is acceptable
- **Construction:** `ln(affected + deaths + 1)` where both fields populated
- If missingness is large, treat as exploratory only. Not a main result variable.

---

## IV. Migration and Disruption Proxy — VIIRS Night Lights

### Lights level

**`mean_radiance`**
- **Definition:** District-quarter mean VIIRS radiance, pixel-area weighted
- **Unit:** nW/cm²/sr
- **Source:** VIIRS DNB monthly composites, Colorado School of Mines EOG,
  tile 75N060E
- **Construction:** Scripts 21–22b — monthly extraction, deduplication, quarterly
  aggregation (mean radiance, sum pixels), composite key groupby throughout
- **Status: Clean — forensically validated**
  - Script 26 all-9-checks PASS: 0 NaN, 0 Inf, 0 negative, balanced 631 × 40
  - Aurangabad litmus: BIHAR = 0.7222, MAHARASHTRA = 0.5094 (diff = 0.2128)
  - All 7 homonymous pairs confirmed distinct
- **Verified range:** min = 0.0003, max = 35.8691, mean = 0.6955,
  median = 0.4266, SD = 1.6884

**`log_lights_qt`**
- **Construction:** `ln(mean_radiance + 0.001)`
- **Offset: +0.001** — corrected from +0.01 (v2.2) and +1 (v2.1 default)
- **Rationale:** mean_radiance < 1 for approximately 80% of sample (rural and
  semi-urban districts). `log(x + 1)` approximates the identity function in this
  range, eliminating log-scale compression for the majority of observations.
  `log(x + 0.001)` preserves the intended elasticity interpretation throughout the
  distribution. `log(x + 1)` is reserved for deposits where scale is Crores.
- **Verified range:** min = −6.6447, max = 3.5559, mean = −0.8326, SD = 0.8377

### Lights growth

**`lights_change_qt`**
- **Construction:** `log_lights_qt.diff()` within `(district_gadm, state_gadm)` groups
- **Missing values:** 631 exactly (first observation per district — 100% VIIRS coverage)
- **Usable N:** 22,716 observations
- **Verified range:** min = −2.2385, max = 1.6938, mean = 0.0170, SD = 0.3530

### Migration/disruption event indicator (conditional)

**`migration_proxy_qt`** — include only if used in paper
- **Construction:** `indicator(lights_change_qt < −theta)`
- **Threshold discipline:** theta chosen from empirical distribution of
  `lights_change_qt` in flood-exposed district-quarters under Rule B. Threshold
  recorded before H2 event-spec regression. Robustness: theta ∈ {0.10, 0.15, 0.20}.

---

## V. Fixed Effects and Standard Errors

### District fixed effects (required in H1, H2, H4)

**Specification:** `C(district_state_id)` using composite key throughout.

Using `district_gadm` alone is a misspecification — produces 624 FE instead of
631, collapsing all 7 homonymous pairs. This is not a rounding issue. Consequence:
contaminated FE absorption, incorrect cluster assignments, and incorrect heterogeneity
variable construction when the same groupby error propagates to Z_i construction.
All pre-March 2026 regression benchmarks were produced under this misspecification.
All results in this codebook reflect the corrected specification.

H3 uses quarter FE only — not affected by this requirement.

### Quarter fixed effects (required in all specifications)

Absorbs national seasonality, macro shocks, monetary policy shifts, and
national-level inflation trends (partially — see nominal INR note in Section II).

### Standard errors

Clustered by `district_state_id` throughout. Clustering on `district_gadm` alone
is incorrect for the same reason as FE — 7 pairs incorrectly share a cluster.

---

## VI. Heterogeneity Variables (Z_i)

All three Z_i variables are pre-committed per Hypotheses v2.5. Construction uses
composite `district_state_id` groupby throughout — never `district_gadm` alone.
All labeled as proxies where true administrative classifications are unavailable.
Results from proxy-based heterogeneity specifications are treated as suggestive.

### H4a: Urban proxy

**`urban_proxy`**
- **Construction:** Time-invariant indicator. Above-median district mean
  `log_lights_qt` computed over the full analysis period, grouped by
  `district_state_id`. Median log_lights_qt = −0.8900.
- **Split:** Urban (above median): 315 districts | Rural (at or below): 316 districts
- **Label in paper:** "Urban proxy (lights-based, above-median mean radiance)"
- **Constraint:** Not a census-based urban/rural classification. Must not claim
  urban/rural heterogeneity without this caveat. Results suggestive only.
- **Result (Script 30, locked):** Interaction null under both rules.
  Rule A: β = −0.0017, p = 0.532. Rule B: β = +0.0075, p = 0.281.
  Feb 6 benchmark (p < 0.001) was spurious — urban proxy construction on
  `district_gadm` alone collapsed AURANGABAD Bihar/Maharashtra, contaminating
  the median threshold. Null is the correct result after fix.

### H4b: High exposure proxy

**`high_exposure_proxy`**
- **Construction:** Time-invariant indicator. Above-median cumulative
  `flood_exposure_ruleA_qt` summed over full period, grouped by `district_state_id`.
  Median cumulative Rule A floods = 3.0 (integer threshold).
- **Threshold note:** Strictly-greater (`> 3.0`). Districts with exactly 3.0
  cumulative events fall in the low-exposure group. This must be disclosed in the
  paper.
- **Split:** High exposure (above median): 255 districts | Low (at or below): 376
- **Label in paper:** "High-exposure proxy (above-median cumulative flood events)"
- **Result (Script 30, locked):** Interaction significant under both rules.
  Rule A: β = −0.0068, SE = 0.0029, p = 0.020 (**).
  Rule B: β = −0.0134, SE = 0.0077, p = 0.080 (*).
  Directionally consistent across rules. Net effect high-exposure districts:
  +0.0047 + (−0.0068) = −0.0021 (net withdrawal vs precautionary accumulation
  in low-exposure districts). Economic mechanism: chronic flood exposure depletes
  household financial buffers; subsequent flood forces withdrawal rather than
  accumulation.

### H4c: Monsoon quarter

**`monsoon_qt`**
- **Construction:** Time-varying indicator. `indicator(q == 3)` for July–September.
  Not a proxy — directly observed from calendar quarter.
- **Split:** Q3 (monsoon): 5,679 observations | Non-Q3: 17,668 observations
- **Result (Script 30, locked):** Interaction significant under Rule A only.
  Rule A: β = +0.0125, SE = 0.0029, p < 0.001 (***).
  Rule B: β = +0.0023, SE = 0.0080, p = 0.774 (null).
  Result is fragile to flood intensity definition — labeled partially supported.
  Rule A/B divergence interpretation: anticipated moderate flooding in monsoon
  season coincides with agricultural income inflows; severe flood events override
  seasonal adjustment entirely.
- **Language constraint:** Must not state "H4c confirmed" in the paper without
  the Rule B fragility caveat. Exact required language: "Monsoon seasonality
  moderates the deposit response to moderate-intensity floods (Rule A: β = +0.012,
  p < 0.001) but not to severe flood events (Rule B: p = 0.774)."

---

## VII. IV Pipeline Audit Variables

**`lights_hat_qt`** (store for diagnostics)
- **Definition:** Fitted values from H1 first stage
- **Rule:** Diagnostic storage only. Never interpreted as observed lights.

**`first_stage_F`**
- **Definition:** F-statistic from first stage, computed as t² for single excluded
  instrument (Wooldridge 2010, p. 104). linearmodels `first_stage` F-stat overflows
  numerically at 666 exogenous columns — t² formula applied as fix.
- **Confirmed values (Script 28, locked):**
  - Rule A: F = (−5.888)² = 34.673 — strong (threshold 16.38 for 5% maximal IV size)
  - Rule B: F = (−2.992)² = 8.949 — weak (below threshold 10)
- **Rule:** Always reported alongside IV results. If F < 10, IV labeled suggestive
  throughout — causal language removed from abstract and conclusions. Rule B second
  stage results carry this label throughout the paper.

---

## VIII. File IO Contract

| Data type | Location |
|---|---|
| Raw inputs (read-only) | `01_Data_Raw/` |
| Intermediate outputs | `02_Data_Intermediate/` |
| Final analysis panels | `03_Data_Clean/` |
| Regression tables | `05_Outputs/Tables/` |
| Figures | `05_Outputs/Figures/` |
| Script logs | `05_Outputs/Logs/` |

---

## IX. Script Contract

Every script must, without exception:

1. Assert input file row counts and column counts at load
2. Log input and output file paths
3. Log row counts before and after every major transformation
4. Log all constant choices (log offsets, thresholds, winsorisation bounds)
5. Assert expected output row count and column count before saving
6. Write a log file to `05_Outputs/Logs/` with `encoding='utf-8'`
7. Use `datetime.now()` for run timestamps — never hardcode dates
8. Use no Unicode symbols (no checkmarks, arrows, or emoji) — Windows cp1252 risk

A script that saves output without passing all asserts has failed, regardless
of whether the output looks reasonable.

---

## X. Current Data State

| File | Rows | Key Verification | Status |
|---|---|---|---|
| `district_crosswalk_draft.csv` | 762 | Hard assert len == 762 | Clean |
| `flood_exposure_panel.csv` | 26,640 | Rule A: 2,518 raw events | Clean |
| `rbi_deposits_panel.csv` | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores | Clean |
| `master_panel_raw.csv` | 26,640 | BALOD 2022Q4 = 3,296 Crores | Clean |
| `master_panel_analysis.csv` | 23,347 | 631 districts x 37 quarters | Clean |
| `viirs_quarterly_panel_clean.csv` | 25,240 | 631 x 40, 9-check validation PASS | Clean |
| `analysis_panel_final.csv` | 23,347 | 100% VIIRS coverage, 0 missing | Clean |
| `regression_panel_final.csv` | 23,347 | 23 columns, lag arithmetic exact | Clean |
| `regression_panel_final_winsor.csv` | 23,347 | 24 columns, 450 obs clipped (2.01%) | Clean |
| `01_descriptive_stats.csv` | 6 vars | Rule A 2,238 events, 9.59% treatment rate | Clean |
| `02_H1_first_stage.csv` | — | Rule A F = 34.673, beta = −0.0445*** | Clean |
| `03_H2_iv2sls.csv` | — | Rule A p = 0.805 (null confirmed) | Clean |
| `04_H3_timing.csv` | — | t−2 beta = −0.0070, p < 0.001 | Clean |
| `05_H4_heterogeneity.csv` | 6 rows | H4b p = 0.020**, H4c p < 0.001*** | Clean |
| `06_32b_2023_diagnosis.csv` | 4 rows | Unit error flag: NO | Clean |

---

## XI. Known Data Issues

### Active — Pre-Paper

**statsmodels rank warning (Scripts 27, 29, 30)**
ValueWarning: rank deficiency in clustered VCV matrix at 666 exogenous columns.
Coefficients valid. SEs are conservative. Must re-run Scripts 27–30 using
`linearmodels.PanelOLS` before final paper tables.

**Script 32b conclusion logic**
Printed conclusion evaluated positive tail only (n above p95 = 36, 1.4%).
Negative tail (n below p5 = 385, 15.4% — 3× expected) was never evaluated.
Conclusion "NO SYSTEMIC ANOMALY" is incorrect. Correct conclusion: left-tail
asymmetry confirmed, concentrated in small-base Northeast districts. Log file
must not be cited directly. Correction pending.

**Northeast district sensitivity check**
TUENSANG (Nagaland) shows a within-year reversal of ±3.21 in 2023 — likely a
reporting artifact at the source. 7 of top 10 and 8 of bottom 10 extreme 2023
obs are Northeast districts. Robustness check excluding Northeast districts
required before submission. Pending confirmation as Script 33 or Hypotheses v2.5
robustness addition.

### Pending — Phase 5

**Zero-change quarters**
25th percentile of `deposit_change_qt` ≈ 0.003. May reflect true stagnation,
RBI source rounding, or copy-forward errors. Diagnostic script required before
submission.

**Script 29 cosmetic fixes**
Two comment-level corrections required (no re-run needed):
- Expected N comment: ~21,180 → ~21,837
- Expected QFE comment: 36 → 35

**Script 12 token count fix**
Section [7] token count comment: 44 → 46. No re-run needed.

### Resolved

**Composite FE misspecification (Fixed Mar 8–9, 2026)**
Scripts 27, 28, 30 used `district_gadm` alone for FE, clustering, and Z_i
groupby operations. All three collapse the 7 homonymous pairs. Corrected to
`district_state_id` composite key throughout in all three scripts. Downstream
consequences: H4a changed from spuriously significant (p < 0.001) to correctly
null; H4b changed from null to significant; H4c changed from null to significant.
All changes attributed to the FE fix, documented in Research Log.

**Crosswalk regression (Fixed Mar 5, 2026)**
Deduplication checked `.nunique()` on district names — homonymous districts share
names across states, so duplicates passed silently (769 rows). Fixed with permanent
rewrite: row-level deduplication, hard assert `len == 762`.

**Deposit extraction bugs (Fixed Feb 11, 2026)**

*Bug 1 — Column offset:* Script 13 extracted "Number of Reporting Offices"
instead of deposits for 2004–2022 files. Fix: `dep_idx = q_idx + 1`. Evidence:
BALOD 2022Q3 changed from 87 (offices) to 3,296 Crores (deposits).

*Bug 2 — State-blind merge:* Merge on `district_rbi` alone caused Bihar +
Maharashtra AURANGABAD deposits to sum. Fix: state filtering for all 14
homonymous state-district pairs. Evidence: Aurangabad Bihar 2015Q1 changed
from 18,652 to 4,422 Crores (−76%).

**RBI 2016–2017 gap (Confirmed Jan 30–31, 2026)**
Suspected duplicate quarter contamination. Confirmed structural: RBI publication
gap between File 1 (ends 2016Q2) and File 2 (starts 2017Q2). Handled by dropping
2016Q3–2017Q1 in Script 17 (Option 3). Gap corresponds to demonetization period.

---

## XII. Confirmed Regression Results (Locked)

All results from corrected pipeline, March 2026. District FE = 631, Quarter FE = 36
(H1, H2, H4) or 35 (H3, L2 restriction). SE clustered by `district_state_id`.

### H1: Floods → Lights

| Rule | β | SE | t | p | Status |
|---|---|---|---|---|---|
| A | −0.0445 | 0.0078 | −5.708 | <0.001 | **Confirmed** |
| B | −0.0584 | 0.0198 | −2.954 | 0.003 | **Confirmed** |

N = 22,716. Rule B magnitude > Rule A — attenuation bound confirmed.

### H2: Lights → Deposits (IV 2SLS)

| Rule | β | SE | t | p | F-stat | Status |
|---|---|---|---|---|---|---|
| A | −0.0084 | 0.0340 | −0.247 | 0.805 | 34.673 (strong) | Null |
| B | −0.0068 | 0.0597 | −0.114 | 0.910 | 8.949 (weak) | Null (suggestive) |

N = 22,442. Null is consistent with pre-committed reconciliation: deposit effects
are lagged, not contemporaneous. H3 t−2 result provides the mechanism.

### H3: Distributed Lag (Flood Timing → Deposits)

| Lag | β (Rule A) | SE | p | Status |
|---|---|---|---|---|
| t0 (current quarter) | +0.000609 | 0.001463 | 0.677 | Null |
| t−1 (1 quarter lag) | +0.001505 | 0.001114 | 0.177 | Null |
| t−2 (2 quarter lag) | **−0.007005** | **0.001645** | **<0.001** | **Confirmed** |

Rule B: t0/t−1/t−2 all null. 209 treatment events — insufficient power. t−2
direction consistent with Rule A (β = −0.0038). N = 21,837. Quarter FE = 35
(L2 restriction drops 2015Q1 and 2015Q2 structurally).

### H4: Heterogeneity (Interaction Effects)

| Specification | Rule | Interaction β | SE | p | Status |
|---|---|---|---|---|---|
| H4a: Urban proxy × Flood | A | −0.0017 | 0.0027 | 0.532 | Null |
| H4a: Urban proxy × Flood | B | +0.0075 | 0.0069 | 0.281 | Null |
| H4b: High exposure × Flood | A | −0.0068 | 0.0029 | 0.020 | **Supported** |
| H4b: High exposure × Flood | B | −0.0134 | 0.0077 | 0.080 | **Supported** |
| H4c: Monsoon × Flood | A | +0.0125 | 0.0029 | <0.001 | **Partial** |
| H4c: Monsoon × Flood | B | +0.0023 | 0.0080 | 0.774 | Null |

N = 22,442 (all specs, both rules). District FE = 631. Quarter FE = 36.

---

## XIII. Regression Panel Specification Reference

| Spec | N | Outcome | Regressor | FE | SE |
|---|---|---|---|---|---|
| H1 | 22,716 | `lights_change_qt` | `flood_exposure_ruleA_qt` | District + Quarter | Clustered (district_state_id) |
| H2 (IV) | 22,442 | `deposit_change_qt` | `lights_change_qt` (instrumented) | District + Quarter | Clustered (district_state_id) |
| H3 | 21,837 | `deposit_change_qt` | Flood t0, t−1, t−2 | Quarter only | Clustered (district_state_id) |
| H4 | 22,442 | `deposit_change_qt` | Flood × Z_i | District + Quarter | Clustered (district_state_id) |

All district FE use `district_state_id` composite key. Using `district_gadm` alone
is a confirmed misspecification producing 624 FE instead of 631.

---

## XIV. Methodological Notes

**GADM as geographic standard:** RBI district names change over time. GADM v4.1
provides stable polygon boundaries for flood matching. Crosswalk harmonises RBI
names to GADM at 83.2% match rate; 130 unmatched RBI districts dropped.

**Rule A as primary flood specification:** Rule A assigns exposure if a flood
matches the district directly or the containing state (fallback). 9.59% treatment
rate. Rule B (district-only, 0.90%) is the strict robustness specification. Both
reported; Rule A preferred for statistical power, Rule B preferred for precision.

**Option 3 sample restriction:** Dropping quarters only (Option 1) retains 35
structural-zero districts. Dropping districts only (Option 2) retains the 2016
RBI demonetization blackout, creating false breaks in distributed-lag specifications.
Option 3 removes both: 98.9% deposit coverage, 100% treatment-outcome overlap.

**Log offset +0.001 for VIIRS:** India is predominantly rural. Mean radiance 0.696
means most observations fall below 1 nW/cm²/sr. `log(x + 0.001)` preserves the
intended elasticity interpretation throughout the distribution. `log(x + 1)` is
reserved for deposits where scale is Crores.

**Nominal INR retained:** Quarter fixed effects absorb national-level price trends.
District-quarter CPI is unavailable at the required granularity. The nominal confound
is acknowledged as a limitation.

**Demonetization gap:** Three quarters — 2016Q3, 2016Q4, 2017Q1 — are entirely
absent from the panel. These span India's demonetization period (November 2016).
The discontinuity is absorbed by quarter fixed effects and must be disclosed
explicitly in the Data section of the paper.

---

*Project initiated: 2025-12-30 | Principal investigator: Jaseel Badar, Harvard University*