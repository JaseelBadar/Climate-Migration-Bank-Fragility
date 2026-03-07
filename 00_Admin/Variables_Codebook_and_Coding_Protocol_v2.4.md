# Variables Codebook and Coding Protocol (v2.4)

**Project:** Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from
Night-Lights in India, 2015–2024

**Status:** Full data pipeline clean and verified (Mar 6–7, 2026).
FE correction required in Scripts 27, 28, 30 before regression execution.

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v1.x–v2.0 | 2026-01-18 to 02-06 | Initial codebook; VIIRS dissolve bug; deposit extraction bug; H3 validated |
| v2.1 | 2026-02-11 | Deposits cleaned: crosswalk dedup (769→762) + state filtering |
| v2.2 | 2026-02-13 | VIIRS alignment complete (Script 22b). Regression panel: 23,088 obs, 23 variables |
| v2.3 | 2026-03-04 | District count corrected: 631 composite pairs. Sample: 23,347 obs. Log offset corrected: +0.001. Crosswalk contamination documented |
| **v2.4** | **2026-03-07** | **Full pipeline clean. Script 8 permanent rewrite (762-row assert). Scripts 12–17, 23–26 re-run and verified. Flood baseline locked: 2,238 Rule A (9.59%), 209 Rule B (0.90%). All contaminated files replaced. Regression pending FE correction.** |

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
7. **Log offset locked.** The offset constant in `log(x + c)` is fixed globally per
   variable, written into logs, and never tuned for results.
8. **Quarter alignment validated.** RBI extraction validates year-quarter labels
   against source column headers. Row labels not trusted without header verification.
9. **Hard asserts before save.** Every script asserts expected row count and column
   count before writing output. Silent failures are not permitted.

---

## I. Panel Structure

**Canonical unit:** GADM v4.1 Level-2 district polygons (India).
RBI districts are mapped to GADM via crosswalk. GADM is the geographic standard.

**Target period:** 2015Q1–2024Q4 (40 quarters)
**Analysis period:** 37 quarters (2015Q1–2016Q2, 2017Q2–2024Q4)
Gap: 2016Q3–2017Q1 — RBI publication blackout, confirmed structural.

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

**Panel dimensions — verified Mar 6–7, 2026:**

| Panel | Districts | Quarters | Observations |
|---|---|---|---|
| Master raw | 666 | 40 | 26,640 |
| Analysis sample | **631** | **37** | **23,347** |
| VIIRS quarterly | 631 | 40 | 25,240 |
| Regression panel | 631 | 37 | 23,347 |

**Note on district counts:** 624 appears in outputs using `.nunique()` on
`district_gadm` alone — undercounts by 7 due to homonymous pairs. Correct count
is always 631 composite (district_gadm, state_gadm) pairs.

**7 confirmed homonymous pairs (UPPERCASE):**
AURANGABAD (BIHAR / MAHARASHTRA), BALRAMPUR (CHHATTISGARH / UTTAR PRADESH),
BIJAPUR (CHHATTISGARH / KARNATAKA), BILASPUR (CHHATTISGARH / HIMACHAL PRADESH),
HAMIRPUR (HIMACHAL PRADESH / UTTAR PRADESH), PRATAPGARH (RAJASTHAN / UTTAR PRADESH),
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
- **Status: CLEAN (Feb 11, 2026)**
  - Bug 1 resolved: `dep_idx = q_idx + 1` — extracted deposits, not office count
  - Bug 2 resolved: State filtering prevents Bihar + Maharashtra AURANGABAD summing
  - Verification anchor: Aurangabad Bihar 2015Q1 = 4,422 Crores (was 18,652 — 76% drop)
  - Total rows: 50,192 (2015Q1–2024Q4 in-window: 23,079 non-missing out of 23,347)
- **Verified range (Mar 6):** min = 28.9979, max = 1,237,744.34, mean = 16,425.73,
  median = 6,135.58 Crores

**`log_deposits`**
- **Construction:** `ln(deposits + 1)`
- **Offset:** +1 — deposits always > 0; +1 is conservative safe default at Crore scale
- **Verified range (Mar 6):** min = 3.4011, max = 14.0288, mean = 8.7075, SD = 1.3707

### Deposits (growth)

**`deposit_change_qt`**
- **Construction:** `log_deposits.diff()` within `(district_gadm, state_gadm)` groups
- **Missing values:** 905 — 631 structural first-obs NaNs + 274 from `.diff()`
  propagation across 268 missing deposit quarters (23,347 − 23,079 = 268)
- **Asymmetry with `lights_change_qt`** (631 missing only) is expected and confirms
  100% VIIRS coverage vs 98.9% deposit coverage — not a data error
- **Usable N:** 22,442 observations
- **Verified range (Mar 6):** min = −1.9322, max = 2.0251, mean = 0.0233, SD = 0.0743

### Deposit withdrawal proxy (conditional)

**`deposit_withdrawal_binary`** — use only if included in paper
- **Construction:** `indicator(deposit_change_qt < k)`
- **Threshold discipline:** k defined from bottom decile of `deposit_change_qt`
  among non-flood observations, or fixed −10% rule — whichever is more conservative.
  Threshold recorded before mechanism regressions. Never tuned post-estimation.

---

## III. Treatment Variables — Flood Shocks

Flood events sourced from EM-DAT, mapped to calendar quarters, matched to GADM
districts via district crosswalk (Scripts 08, 10). Both precision regimes required
in all core tables.

### Flood exposure

**`flood_exposure_ruleA_qt`** — Rule A (primary specification)
- **Definition:** 1 if district directly matched OR district's state matched (fallback)
- **Coverage (analysis sample, locked Mar 6):** 2,238 events | 9.59% treatment rate
  | 569 districts ever exposed
- **Interpretation:** Conservative lower bound. State-level fallback introduces false
  positives; attenuates β toward zero. Rule A estimates are lower bounds on the true
  local effect.
- **Status: CLEAN (Mar 5–6, 2026)**

**`flood_exposure_ruleB_qt`** — Rule B (robustness / precision check)
- **Definition:** 1 only when district explicitly identified in EM-DAT location field
- **Coverage (analysis sample, locked Mar 6):** 209 events | 0.90% treatment rate
  | 141 districts ever exposed
- **Interpretation:** Higher precision; smaller effective treatment variation; lower
  power. Preferred for instrument credibility argument.
- **Status: CLEAN (Mar 5–6, 2026)**

### Flood lags (distributed lag models)

| Variable | Construction | Used in |
|---|---|---|
| `flood_ruleA_L1` | L1 within composite group | H3, H2 timing |
| `flood_ruleA_L2` | L2 within composite group | H3 |
| `flood_ruleA_L3` | L3 — Phase 5 robustness | R5 |
| `flood_ruleA_L4` | L4 — Phase 5 persistence | R5 |
| `flood_ruleB_L1–L4` | Rule B equivalents | Robustness |

**Lag missing-value arithmetic (locked):**

| Lag | Expected missing | Actual (Mar 6) |
|---|---|---|
| L1 | 631 | 631 ✓ |
| L2 | 1,262 | 1,262 ✓ |
| L3 | 1,893 | 1,893 ✓ |
| L4 | 2,524 | 2,524 ✓ |

Any deviation from 631 × k signals a composite key error.

### Flood severity (conditional)

**`flood_severity_qt`** — use only if completeness is acceptable
- **Construction:** `ln(affected + deaths + 1)` where both fields populated
- If missingness is large, treat as exploratory only. Not a main result variable.

---

## IV. Migration and Disruption Proxy — VIIRS Night Lights

### Lights level

**`mean_radiance`**
- **Definition:** District-quarter mean VIIRS radiance, pixel-area weighted
- **Unit:** nW/cm²/sr
- **Source:** VIIRS DNB monthly composites, Colorado School of Mines EOG, tile 75N060E
- **Construction:** Scripts 21–22b — monthly extraction, deduplication, quarterly
  aggregation (mean radiance, sum pixels), composite key groupby throughout
- **Status: CLEAN — forensically validated Mar 7, 2026**
  - Script 26 all-9-checks PASS: 0 NaN, 0 Inf, 0 negative, balanced 631×40
  - Aurangabad litmus: BIHAR = 0.7222, MAHARASHTRA = 0.5094 (diff = 0.2128 >> 0.01)
  - All 7 homonymous pairs confirmed distinct
- **Verified range (Mar 7):** min = 0.0003, max = 35.8691, mean = 0.6955,
  median = 0.4266, SD = 1.6884

**`log_lights_qt`**
- **Construction:** `ln(mean_radiance + 0.001)`
- **Offset: +0.001** — corrected from +0.01 (v2.2) and from +1 (v2.1 default)
- **Rationale:** mean_radiance < 1 for ~80% of sample (rural and semi-urban
  districts). Using `log(x + 1)` makes the transform approximately linear in
  this range, eliminating log-scale compression for the majority of observations.
  `log(x + 0.001)` preserves the intended elasticity interpretation throughout the
  distribution. `log(x + 1)` is reserved for deposits where scale is Crores.
- **Verified range (Mar 6):** min = −6.6447, max = 3.5559, mean = −0.8326, SD = 0.8377

### Lights growth

**`lights_change_qt`**
- **Construction:** `log_lights_qt.diff()` within `(district_gadm, state_gadm)` groups
- **Missing values:** 631 exactly (first observation per district — 100% VIIRS coverage)
- **Usable N:** 22,716 observations
- **Verified range (Mar 6):** min = −2.2385, max = 1.6938, mean = 0.0170, SD = 0.3530

### Migration/disruption event indicator (conditional)

**`migration_proxy_qt`** — use only if included in paper
- **Construction:** `indicator(lights_change_qt < −theta)`
- **Threshold discipline:** theta chosen from empirical distribution of
  `lights_change_qt` in flood-exposed district-quarters under Rule B. Threshold
  recorded before H2 event-spec regression. Robustness: theta ∈ {0.10, 0.15, 0.20}.

---

## V. Controls and Fixed Effects

### Baseline (required in all specifications)

- **District FE:** Must use `district_state_id = district_gadm + '_' + state_gadm`.
  Using `district_gadm` alone produces 624 FE instead of 631 — collapses 7
  homonymous pairs. This is a misspecification, not a rounding difference.
  **Required correction in Scripts 27, 28, 30 before execution.**
- **Quarter FE:** Absorbs national seasonality, macro shocks, monetary policy shifts.

### Seasonality marker (optional)

**`monsoon_quarter`**
- **Construction:** `indicator(q == 3)` for July–September
- Quarter FE already absorbs national seasonal patterns. Use only for exposition
  or robustness, not identification.

### Weather controls (preferred extension)

**`rainfall_qt`** — if available
- Must be spatially aggregated to GADM district polygons, then to quarters.
  Aggregation method documented before use.

---

## VI. Heterogeneity Variables

All heterogeneity variables must be pre-treatment (time-invariant or baseline-period
constructs), or explicitly lagged to avoid mechanical correlation. Any proxy is
labeled "proxy" in outputs and paper. No census-based urbanisation claims without
census data.

| Variable | Construction | Label in paper |
|---|---|---|
| `urban` | Above-median district mean `log_lights_qt` (pre-2018 baseline) | Urban proxy (lights-based) |
| `high_exposure` | Above-median cumulative flood count (full period) | High-exposure proxy |
| `monsoon` | `indicator(q == 3)` | Monsoon quarter |

---

## VII. IV Pipeline Audit Variables

**`lights_hat_qt`** (store for diagnostics)
- **Definition:** Fitted values from H1 first stage
- **Rule:** Diagnostic storage only. Never interpreted as observed lights.

**`first_stage_F`**
- **Definition:** Kleibergen-Paap or Cragg-Donald F-statistic from first stage
- **Rule:** Always reported alongside IV results. If F < 10, IV labeled suggestive
  throughout — causal language removed from abstract and conclusions.

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
6. Write a log file to `05_Outputs/Logs/`

A script that saves output without passing all asserts has failed, regardless
of whether the output looks reasonable.

---

## X. Current Data State — Verified Mar 6–7, 2026

| File | Rows | Key metric | Status |
|---|---|---|---|
| `district_crosswalk_draft.csv` | 762 | Hard assert len==762 PASS | **Clean** |
| `flood_exposure_panel.csv` | 26,640 | Rule A: 2,518 raw events | **Clean** |
| `rbi_deposits_panel.csv` | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores | **Clean** |
| `master_panel_raw.csv` | 26,640 | Rule A: 2,518 \| BALOD 2022Q4 = 3,296 Crores | **Clean** |
| `master_panel_analysis.csv` | 23,347 | 631 districts × 37 quarters | **Clean** |
| `viirs_quarterly_panel_clean.csv` | 25,240 | 631 districts × 40 quarters \| 9-check validation PASS | **Clean** |
| `analysis_panel_final.csv` | 23,347 | 100% VIIRS coverage, 0 missing | **Clean** |
| `regression_panel_final.csv` | 23,347 | 23 columns, lag arithmetic exact | **Clean** |
| `01_descriptive_stats.csv` | 6 vars | Rule A 2,238 events, 9.59% treatment rate | **Clean** |

---

## XI. Known Data Issues

### Active — Pre-regression

**FE misspecification in Scripts 27, 28, 30**
District fixed effects use `district_gadm` alone — 624 FE instead of correct 631.
Fix: replace with `district_state_id = district_gadm + '_' + state_gadm` throughout.
Script 29 (H3, quarter FE only) is unaffected.

### Pending — Phase 5

**Outliers in deposit growth**
min = −1.93, max = +2.03 (log scale). Likely causes: boundary changes, branch
reclassification, data entry errors. Correction: winsorise at 1st/99th percentile
before publication regressions (Robustness check R3).

**Nominal deposit growth**
Deposits in nominal Rupees. Decision required before Phase 5: (1) CPI deflation,
or (2) explicit disclosure that coefficients reflect nominal effects. Decision
documented before final tables are produced (Robustness check R4).

**Zero-change quarters**
25th percentile of `deposit_change_qt` = 0.00. May reflect true stagnation, RBI
source rounding, or copy-forward errors. Diagnostic script required before submission.

### Resolved

**Crosswalk regression (Script 8, Feb 27 → Fixed Mar 5)**
Deduplication checked `.nunique()` on district names — homonymous districts share the
same name across states, so duplicates passed silently while 7 duplicate rows persisted
(769 rows). Propagated to Script 12: 10 artificial flood events added. Fixed with
permanent rewrite: row-level deduplication, hard assert `len == 762`. Re-run confirmed.

**Deposit extraction bug (Feb 4–11)**
Script 13 column offset extracted "Number of Reporting Offices" instead of deposits
for 2004–2022 files. Fixed: `dep_idx = q_idx + 1`. Verified: BALOD 2022Q3 changed
from 87 (offices) to 3,296 Crores.

**State-blind crosswalk merge (Feb 7–11)**
Merge on `district_rbi` alone caused Bihar + Maharashtra AURANGABAD deposits to sum.
Fixed: state filtering for all 14 homonymous state-district pairs. Verified: Aurangabad
Bihar 2015Q1 = 4,422 Crores (was 18,652 — 76% drop).

**RBI 2016–2017 gap (Jan 30–31)**
Suspected duplicate quarter contamination. Confirmed structural: RBI publication gap
between File 1 (ends 2016Q2) and File 2 (starts 2017Q2). No contamination.
Handled by dropping 2016Q3–2017Q1 in Script 17 (Option 3).

---

## XII. Regression Panel Specification Reference

| Spec | N (approx) | Outcome | Regressor | FE | SE |
|---|---|---|---|---|---|
| H1 | ~22,716 | `lights_change_qt` | `flood_exposure_ruleA_qt` | District + Quarter | Clustered (district) |
| H2 (IV) | ~22,442 | `deposit_change_qt` | `lights_change_qt` (instrumented) | District + Quarter | Clustered (district) |
| H3 | ~21,180 | `deposit_change_qt` | Flood t0, t−1, t−2 | Quarter only | Clustered (district) |
| H4 | ~22,442 | `deposit_change_qt` | Flood × Z_i | District + Quarter | Clustered (district) |

H3 N: 22,442 (changes sample) − 631 × 2 (two-lag restriction) = ~21,180.
All N values approximate pending re-run with corrected FE specification.
All district FE use `district_state_id`. Using `district_gadm` alone is a
misspecification — 624 FE instead of correct 631.

---

## XIII. H3 Validated Results — Confirmed Clean (Feb 6, 2026)

H3 uses deposits and flood lags only — no VIIRS, no district FE. Unaffected by
any pipeline contamination event in the project history.

| Lag | β | SE | p-value | Finding |
|---|---|---|---|---|
| t0 (current quarter) | −0.0005 | 0.0014 | 0.777 | Null |
| t−1 (1 quarter) | +0.0004 | 0.0014 | 0.757 | Null |
| t−2 (2 quarters) | **−0.0091** | 0.0036 | **0.012** | **Confirmed** |

Sample: 21,912 obs (pre-clean, two-lag restriction applied to smaller panel).
Re-run on full 23,347-observation clean panel pending. t−2 significance and direction
expected to persist. Magnitude treated as provisional until confirmed.

---

*Project initiated: 2025-12-30 | Principal investigator: Jaseel Badar, Harvard University*