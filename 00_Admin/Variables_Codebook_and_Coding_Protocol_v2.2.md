# Variables Codebook and Coding Protocol (v2.3)

**Project:** Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from
Night-Lights in India, 2015–2024

**Status:** Pipeline fix pending Mar 5. Analysis panel clean (Mar 4). Regressions pending.
**Last updated:** 2026-03-04

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v1.x–v2.0 | 2026-01-18 to 02-06 | Initial codebook; VIIRS dissolve bug; deposit extraction bug; H3 validated |
| v2.1 | 2026-02-11 | Deposits cleaned: crosswalk dedup (769→762) + state filtering. VIIRS pipeline verified. |
| v2.2 | 2026-02-13 | VIIRS alignment complete (Script 22b). Regression panel ready: 23,088 obs, 23 variables. |
| **v2.3** | **2026-03-04** | **District count corrected: 631 composite pairs (was 624). Sample: 23,347 obs. Log offset corrected: +0.001 (was +0.01). Crosswalk contamination documented (769-row regression, Feb 27). Fix Mar 5.** |

**Discipline:** Variable definitions and coding protocols do not change to match results.
Version bumps record measurement corrections, naming fixes, and reproducibility updates only.

---

## Non-Negotiable Principles

1. **Raw data is read-only.** Nothing inside `01_Data_Raw/` is ever modified. All
   transformations write to `02_Data_Intermediate/` or `03_Data_Clean/`.
2. **No silent drops.** Every dropped row is logged with count and reason.
3. **No endogeneity by construction.** VIIRS outcomes never define flood treatment.
4. **One script, one output.** Each script produces one named dataset and one log file.
5. **No district-name dissolve.** Never dissolve on `district_gadm` alone. Homonymous
   districts across states will merge. All groupby, FE, and dissolve operations use
   composite `(district_gadm, state_gadm)`.
6. **Composite keys everywhere.** Any operation on the panel that is district-specific
   must use `district_gadm + state_gadm` as the grouping key — not name alone.
7. **Log offset locked.** The offset constant in `log(x + c)` is fixed globally per
   variable, written into logs, and never tuned for results.
8. **Quarter alignment validated.** RBI extraction validates year-quarter labels against
   source column headers. Row labels not trusted without header verification.
9. **Hard asserts before save.** Every script asserts expected row count and column count
   before writing output to disk. Silent failures are not permitted.

---

## I. Panel Structure

**Canonical unit:** GADM v4.1 Level-2 district polygons (India)
RBI districts are mapped to GADM via crosswalk. GADM is the spatial standard.

**Target period:** 2015Q1–2024Q4 (40 quarters)
**Analysis period:** 37 quarters (2015Q1–2016Q2, 2017Q2–2024Q4)
Gap: 2016Q3–2017Q1 — RBI publication blackout, confirmed structural (not contamination)

**Index variables** (required in all output panels):

| Variable | Type | Definition |
|---|---|---|
| `district_gadm` | string | GADM Level-2 district name |
| `state_gadm` | string | GADM Level-1 state name |
| `district_state_id` | string | `district_gadm + '_' + state_gadm` — composite unique ID |
| `quarter` | string | e.g., `2015Q1` |
| `year` | int | 2015–2024 |
| `q` | int | 1–4 |
| `quarter_num` | int | Sequential index 1–40 (for sorting and lag construction) |

**Sorting rule (locked):** Always sort by `district_gadm`, `state_gadm`, `year`, `q`
before constructing lags or differences. Violation invalidates all time-series operations.

**Panel dimensions (Mar 4, 2026 verified):**

| Panel | Districts | Quarters | Observations |
|---|---|---|---|
| Master raw | 666 | 40 | 26,640 |
| Analysis sample | **631** | **37** | **23,347** |
| VIIRS quarterly | 631 | 40 | 25,240 |
| Regression panel | 631 | 37 | 23,347 |

Note: 624 appears in outputs using `.nunique()` on `district_gadm` alone. This
undercounts by 7 (homonymous pairs). Correct district count is always 631 composite pairs.

---

## II. Outcome Variables — Banking

### Deposits (level)

**`deposits`**
- Definition: Total district-quarter deposits, all population groups aggregated
- Unit: Indian Rupees, Crores (nominal)
- Source: RBI BSR-2 (District-wise deposits)
- Construction: Script 13 — fiscal-to-calendar conversion, state filtering for
  7 homonymous districts, column offset +1 for historical files (2004–2022)
- Status: **CLEAN (Feb 11, 2026)**
  - Bug 1 resolved: Column offset corrected (`dep_idx = q_idx + 1`)
  - Bug 2 resolved: State filtering prevents Bihar + Maharashtra AURANGABAD summing
  - Verification: Aurangabad Bihar 2015Q1 = 4,422 Crores (was 18,652 — 76% drop)
  - In-window rows: 49,670 (2015Q1–2024Q4); 50,192 total including 2025Q1–Q3 (harmless)

**`log_deposits`**
- Construction: `ln(deposits + 1)`
- Offset: +1 (deposits always > 0 in sample; +1 is conservative safe default)
- Verified range (Mar 4): min = 3.4011, max = 14.0288, mean = 8.7075

### Deposits (growth)

**`deposit_change_qt`**
- Construction: `log_deposits.diff()` within `(district_gadm, state_gadm)` groups
- Missing values: 905 (631 first-observation NaNs + 274 from 0.9% missing deposits)
  Asymmetry with `lights_change_qt` (631 only) is expected and confirms 100% VIIRS
  coverage vs 99.1% deposit coverage — not a bug
- Usable N: 22,442 observations

### Deposit withdrawal proxy (optional)

**`deposit_withdrawal_binary`** (use only if included in paper)
- Construction: `indicator(deposit_change_qt < k)`
- Threshold discipline: k defined from bottom decile of `deposit_change_qt` among
  non-flood observations, or fixed −10% rule — whichever more conservative.
  Threshold recorded before mechanism regressions. Not tuned post-estimation.

---

## III. Treatment Variables — Flood Shocks

Flood events sourced from EM-DAT, mapped to calendar quarters, then matched to
GADM districts via the district crosswalk (Script 12).

### Flood exposure (two precision regimes — both required)

**`flood_exposure_ruleA_qt`** — Rule A (primary specification)
- Definition: 1 if district directly matched OR district's state matched (fallback)
- Coverage: ~8.50% treatment rate (1,984 events — pending pipeline fix)
- Interpretation: Conservative lower bound. State-level fallback introduces false
  positives; attenuates beta toward zero.
- Status: **CONTAMINATED** — 2,230 events on disk (should be 2,220). Root cause:
  Script 12 re-run Feb 28 with 769-row crosswalk. Fix Mar 5.

**`flood_exposure_ruleB_qt`** — Rule B (robustness / credibility check)
- Definition: 1 only when district explicitly identified in EM-DAT location field
- Coverage: ~0.96% treatment rate (272 events — contaminated, same root cause)
- Interpretation: Higher precision; smaller effective treatment variation; lower power.

### Flood lags (distributed lag models)

| Variable | Construction | Used in |
|---|---|---|
| `flood_ruleA_L1` | L1 of `flood_exposure_ruleA_qt` within composite group | H3, H2 timing |
| `flood_ruleA_L2` | L2 of `flood_exposure_ruleA_qt` | H3 |
| `flood_ruleA_L3` | L3 — reserved for robustness (Phase 5) | — |
| `flood_ruleA_L4` | L4 — reserved for persistence testing (Phase 5) | — |
| `flood_ruleB_L1–L4` | Rule B equivalents of above | Robustness checks |

**Lag missing-value arithmetic (locked):**
631 × k observations missing for lag Lk. Any deviation signals composite key error.

| Lag | Expected missing |
|---|---|
| L1 | 631 |
| L2 | 1,262 |
| L3 | 1,893 |
| L4 | 2,524 |

### Flood severity (optional)

**`flood_severity_qt`** — use only if completeness is acceptable
- Construction: `ln(affected + deaths + 1)` where both fields populated
- If missingness is large, treat as exploratory only. Not a main result.

---

## IV. Migration and Disruption Proxy — VIIRS Night Lights

### Lights level

**`mean_radiance`**
- Definition: District-quarter mean VIIRS radiance, pixel-area weighted
- Unit: nW/cm²/sr
- Source: VIIRS DNB monthly composites, Colorado School of Mines EOG
- Construction: Scripts 21–22b — monthly extraction, quarterly aggregation
  (mean radiance, sum pixels), composite key groupby throughout
- Status: **CLEAN (Mar 3, 2026)**
  - Forensic validation: Aurangabad Bihar 0.681 ≠ Aurangabad Maharashtra 0.433
  - All Scripts 18–24 use composite `(district_gadm, state_gadm)` keys
  - Panel: 25,240 rows (631 districts × 40 quarters), 100% coverage
- Verified range (Mar 4): min = 0.0003, max = 35.02, mean = 0.696, SD = 1.688

**`log_lights_qt`**
- Construction: `ln(mean_radiance + 0.001)`
- **Offset: +0.001 (not +0.01 as stated in v2.2 — corrected Mar 4)**
- Rationale: VIIRS mean_radiance < 1 for ~80% of sample (rural and semi-urban
  districts). Using +1 makes `log(x+1) ≈ x` in this range — the transform
  is no longer logarithmic for the majority of observations. Using +0.001
  preserves log-scale compression and the intended elasticity interpretation.
  `log(x + 1)` is reserved for deposits where the scale is thousands of Crores.
- Verified range (Mar 4): min = −6.6447, max = 3.5559, mean = −0.8326

### Lights growth

**`lights_change_qt`**
- Construction: `log_lights_qt.diff()` within `(district_gadm, state_gadm)` groups
- Missing values: 631 (first observation per district only — 100% VIIRS coverage)
- Usable N: 22,716 observations

### Migration/disruption event indicator (optional)

**`migration_proxy_qt`** — use only if included in paper
- Construction: `indicator(lights_change_qt < −theta)`
- Threshold discipline: theta chosen from empirical distribution of `lights_change_qt`
  in flood-exposed district-quarters under Rule B (high-precision sample).
  Threshold recorded before H2 event-spec regression. Robustness: theta ∈ {0.10, 0.15, 0.20}.

---

## V. Controls and Fixed Effects

### Baseline (required in all specifications)

- **District FE:** Must use `district_state_id = district_gadm + '_' + state_gadm`.
  Using `district_gadm` alone produces 624 FE instead of 631 — collapses
  7 homonymous pairs. This is a misspecification, not a minor rounding issue.
- **Quarter FE:** Absorbs national seasonality, macro shocks, monetary policy.

### Seasonality marker (optional)

**`monsoon_quarter`**
- Construction: `indicator(q == 3)` for July–September
- Note: Quarter FE already absorbs national seasonal patterns. Use only for
  exposition or robustness, not for identification.

### Weather controls (preferred extension)

**`rainfall_qt`** — if available
- Must be spatially aggregated to GADM district polygons, then to quarters.
  Aggregation method documented before use.

---

## VI. Heterogeneity Variables

All heterogeneity variables must be:
- Pre-treatment (time-invariant or baseline-period constructs), OR
- Explicitly lagged to avoid mechanical correlation with contemporaneous floods.

Any proxy variable is labeled "proxy" in outputs and paper. No census-based
urbanisation claims without census data.

| Variable | Construction | Label in paper |
|---|---|---|
| `urban` | Above-median district mean `log_lights_qt` (pre-2018 baseline) | Urban proxy (lights-based) |
| `high_exposure` | Above-median cumulative flood count (full period) | High-exposure proxy |
| `monsoon` | `indicator(q == 3)` | Monsoon quarter |

---

## VII. IV Pipeline Audit Variables

**`lights_hat_qt`** (store for diagnostics)
- Definition: Fitted values from H1 first stage
- Rule: Diagnostic storage only. Never interpreted as observed lights.

**`first_stage_F`**
- Definition: Kleibergen-Paap or Cragg-Donald F-statistic from first stage
- Rule: Always reported alongside IV results. If F < 10, IV labeled suggestive.
  Causal language removed from abstract and conclusions.

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

## X. Current Data State (Mar 4, 2026)

| File | Rows | Status | Last verified |
|---|---|---|---|
| `rbi_deposits_panel.csv` | 49,670 (in-window) | **CLEAN** | Mar 4 — Aurangabad Bihar 4,422 confirmed |
| `district_crosswalk_draft.csv` | 769 | **CONTAMINATED** | Mar 4 — 7 duplicate rows, fix Mar 5 |
| `flood_exposure_panel.csv` | 26,640 | **CONTAMINATED** | Mar 4 — 2,230 Rule A (should be 2,220) |
| `viirs_quarterly_panel_clean.csv` | 25,240 | **CLEAN** | Mar 3 — 631 districts × 40 quarters |
| `analysis_panel_final.csv` | 23,347 | **CLEAN** | Mar 4 — 100% VIIRS coverage |
| `regression_panel_final.csv` | 23,347 | **CLEAN** | Mar 4 — 23 columns, lag arithmetic exact |

**Contamination root cause (confirmed Mar 4):**
Script 8 re-run on Feb 27 with pre-dedup logic → crosswalk reverted to 769 rows →
Script 12 re-run Feb 28 using contaminated crosswalk → 10 artificial flood events
added → downstream panels (Scripts 14–17) inherit the error.
Fix: Script 8 permanent rewrite with hard assert `len(output) == 762` — Mar 5.

---

## XI. Known Data Issues

### Active — Fix Mar 5

**Crosswalk regression (Script 8, Feb 27)**
Deduplication logic checked `.nunique()` on district names — homonymous districts
have the same name in both states, so duplicates reported zero while 7 duplicate
rows persisted. Fix: rewrite Script 8 with row-level deduplication and assert.

### Pending — Phase 5

**Outliers in deposit growth**
Min = −1.93, Max = +2.03 (log scale) in regression panel. Likely causes: boundary
changes, branch reclassification, data entry errors. Correction: winsorise at 1st/99th
percentile before final publication regressions.

**Nominal deposit growth**
Deposits measured in nominal Rupees. Mean growth ~11.9% quarterly is implausibly high
in real terms. Decision required: (1) CPI deflation, or (2) explicit disclosure that
coefficients reflect nominal effects. Decision before Phase 5 regression tables.

**Zero-change quarters**
25th percentile of `deposit_change_qt` = 0.00. May reflect true stagnation, rounding
in RBI source data, or copy-forward errors. Diagnostic script required.

### Resolved

**Deposit extraction bug (Feb 4–11):** Column offset error in Script 13 extracted
"Number of Reporting Offices" instead of deposits for 2004–2022 data. Fixed with
`dep_idx = q_idx + 1`. Verified: BALOD 2022Q3 changed from 87 (offices) to 3,296 Crores.

**State-blind crosswalk merge (Feb 7–11):** Merge on `district_rbi` alone caused
Bihar + Maharashtra AURANGABAD deposits to sum. Fixed with state filtering for all
14 homonymous state-district pairs. Verified: Aurangabad Bihar 2015Q1 = 4,422 Crores.

**RBI 2016–2017 gap (Jan 30–31):** Suspected duplicate quarter contamination.
Confirmed structural: RBI publication gap between File 1 (ends 2016-17:Q1 = 2016Q2)
and File 2 (starts 2017-18:Q1 = 2017Q2). No contamination. Gap handled by dropping
2016Q3–2017Q1 in Script 17.

---

## XII. Regression Panel Specification Reference

| Specification | N | Outcome | Regressor | FE | SE |
|---|---|---|---|---|---|
| H1 | ~22,716 | `lights_change_qt` | `flood_exposure_ruleA_qt` | District + Quarter | Clustered (district) |
| H2 (IV) | ~22,442 | `deposit_change_qt` | `lights_change_qt` (instrumented) | District + Quarter | Clustered (district) |
| H3 | ~21,812 | `deposit_change_qt` | Flood t0, t-1, t-2 | Quarter only | Clustered (district) |
| H4 | ~22,442 | `deposit_change_qt` | Flood × Z_i | District + Quarter | Clustered (district) |

H3 N is 2-quarter-lag restricted (loses 631 × 2 = 1,262 observations from changes sample).
All N values approximate pending clean pipeline re-run.
All district FE use `district_state_id`. Using `district_gadm` alone is a misspecification.

---

## XIII. H3 Validated Results (Feb 6 — Specification Confirmed Clean)

H3 specification uses deposits and flood lags only. No VIIRS variables. Quarter FE only
(no district FE). Unaffected by crosswalk contamination, VIIRS pipeline issues, or
homonymous FE collapse.

| Lag | β | SE | p | Finding |
|---|---|---|---|---|
| t0 (current quarter) | −0.0005 | 0.0014 | 0.777 | Null |
| t-1 (one quarter) | +0.0004 | 0.0014 | 0.757 | Null |
| t-2 (two quarters) | **−0.0091** | 0.0036 | **0.012** | Confirmed |

Sample: 21,912 obs (pre-clean, pre-full-pipeline). Effect size may change with
23,347-observation clean panel; direction and significance expected to persist.

---

*Project initiated: 2025-12-30 | Principal investigator: Jaseel Badar, Harvard University*