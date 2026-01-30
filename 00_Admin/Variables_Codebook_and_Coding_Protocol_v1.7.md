# VARIABLES CODEBOOK AND CODING PROTOCOL (v1.7)

**Project**: Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India (2015-2024)

**Document Type**: Variables codebook and enforceable coding protocol

**Version**: 1.7 (RBI source contamination discovered; deposit extraction under review)

**Status**: RBI source data audit in progress (2026-01-30). File `RBI_Deposits_2017_2022.xlsx` contains duplicate 2016 Q1-Q3 data mislabeled as 2017 Q1-Q3. Script 13 flagged for rewrite with quarter-level validation. Clean VIIRS panel (666 districts, 79,920 monthly observations) unaffected. H1 results valid; H2, H3, H4 under review pending corrected deposit extraction.

**Date**: January 30, 2026

---

## Non-Negotiable Principles

1. Raw data is read-only: Never modify anything inside `01_Data_Raw/`. All transformations write to `02_Data_Intermediate/` or `03_Data_Clean/`.

2. No silent drops: Any row or observation dropped must be logged with counts and reasons.

3. No endogeneity by construction: Never use VIIRS outcomes to define flood treatment (no "flood = 1 if lights drop").

4. One script one responsibility: Each script produces one named output dataset and one log file.

5. Reproducibility beats cleverness: Prefer simple, auditable transformations over complex heuristics.

6. Do not overclaim: If a variable is proxy (urban, migration, exposure), label it as such in outputs and paper.

7. No district-name dissolve: Never dissolve GADM districts using NAME_2 alone (homonymous districts across states will merge). If dissolve needed, must include state (NAME_1) or stable unique ID; otherwise, do not dissolve.

8. Quarter-level date validation: All RBI extraction must validate year-quarter alignment against source file column headers. Never trust row labels without verification against actual data columns.

---

## I. Panel Structure

**Canonical unit**: Indian district polygons from GADM v4.1 Level-2

RBI districts mapped to GADM using crosswalk (RBI not canonical geography).

**Target period**: Quarterly, 2015Q1 to 2024Q4 (40 quarters)

**Implementation reality** (must be documented, not hidden):

- Analysis sample may drop quarters with missing deposits and districts with zero deposit coverage (this is sample restriction, not data "feature")

**Key index variables** (must exist in final analysis panel):

Names aligned to implemented pipeline / Script 24 conventions.

- `districtgadm`: canonical district name (GADM)
- `stategadm`: canonical state name (GADM)
- `quarter`: string like `2015Q1`
- `year`: 2015-2024
- `q`: 1-4
- `quarternum`: sequential index (1-40) used for sorting/lags

**Sorting rule** (locked):

Always sort by `districtgadm`, `stategadm`, `quarternum` before constructing lags or differences.

---

## II. Outcome Variables (Banking)

### A. Deposits (levels)

**Variable**: `depositscrores`

- Definition: Total deposits in district-quarter
- Unit: Rupees crores (verify from RBI tables; treat as nominal unless deflated)
- Construction: RBI extraction aggregates across population groups where needed
- Data quality warning: RBI source file `RBI_Deposits_2017_2022.xlsx` contains duplicate 2016 Q1-Q3 data mislabeled as 2017 Q1-Q3. Script 13 rewrite required with explicit quarter-level validation before extraction.

**Variable**: `logdepositscrores`

- Definition: natural log of deposits
- Construction: `logdepositscrores = ln(depositscrores)`
- Rule: Do not add arbitrary constants unless deposits can be zero; if constant used, must be fixed and logged

### B. Deposits (growth)

**Variable**: `depositchangeqt`

- Definition: quarter-over-quarter log change in deposits (approximate percent change)
- Construction: within district, `depositchangeqt = logdepositscrores - L1(logdepositscrores)`
- Missingness rule: first observed quarter per district will have missing change by construction

### C. Optional withdrawal event proxy (only if used in paper)

**Variable**: `depositwithdrawalbinary` (optional)

- Definition: indicator for unusually large deposit decline (shadow-run proxy)
- Pre-commitment rule: Define threshold k from baseline distribution BEFORE mechanism regressions. Example: bottom decile of `depositchangeqt` among non-flood observations OR fixed -10 percent rule, whichever more conservative.
- Construction: indicator(depositchangeqt less than k)

---

## III. Treatment Variables (Flood Shocks)

Flood exposure constructed from EM-DAT and mapped into quarters, then into districts using documented rule set.

### A. Exposure indicators (two precision regimes; both required)

**Variable**: `floodexposureruleAqt`

- Rule A (full sample / lower-bound): if event location only state-level, code flood exposure for all districts in that state for that quarter
- Interpretation constraint: attenuation bias expected due to false positives

**Variable**: `floodexposureruleBqt`

- Rule B (high-precision / credibility spec): code exposure only when districts explicitly identified (Admin Units and/or verified parsing)
- Interpretation constraint: smaller effective treatment variation; may weaken power

### B. Lags (timing tests)

**Variable**: `floodlag1qt`

- Definition: one-quarter lag of flood exposure (baseline: Rule A unless explicitly running Rule B spec)
- Construction: L1(floodexposureruleAqt) within district

**Variable**: `floodlag2qt` (optional if used)

- Construction: L2(floodexposureruleAqt) within district

### C. Severity (optional; only if available and logged cleanly)

**Variable**: `floodseverityqt` (optional)

- Preferred construction: ln(affected + deaths + 1) if both available with acceptable completeness
- If missingness large, severity treated as exploratory (not main result)

---

## IV. Migration and Disruption Proxy (VIIRS Night Lights)

### A. Quarterly lights level

**Variable**: `meanradiance`

- Definition: district-quarter mean VIIRS radiance (after monthly extraction and quarterly aggregation)
- Rule: Variable constructed only from VIIRS (never influenced by flood coding)
- Data quality status: CLEAN (Phase 5 complete, 2026-01-27). Script 21 dissolve bug fixed; multi-tile duplicates resolved via Script 21b pixel-weighted averaging. 666 districts, 79,920 monthly observations validated.

**Variable**: `loglightsqt`

- Definition: log-transformed quarterly lights level
- Construction (as implemented in Script 24): `loglightsqt = ln(meanradiance + c)` with fixed constant
- Constant rule (locked): If constant c used to handle zeros, must be fixed globally and written into logs; never tuned for results. Current pipeline uses +1 offset (record and keep fixed unless formal change logged).

### B. Quarterly lights change

**Variable**: `lightschangeqt`

- Definition: quarter-over-quarter change in log lights (approximate percent change)
- Construction: within district, `lightschangeqt = loglightsqt - L1(loglightsqt)`

### C. Optional migration/disruption event indicator (only if used)

**Variable**: `migrationproxyqt` (optional)

- Definition: indicator for large negative lights shock
- Construction: indicator(lightschangeqt less than negative theta)
- Threshold discipline: theta chosen from empirical distribution in flood-exposed district-quarters in high-precision sample (Rule B), recorded before estimating final H2 event-spec regressions. Robustness: theta in {0.10, 0.15, 0.20}.

---

## V. Controls and Fixed Effects

### A. Minimum viable controls (baseline)

- District fixed effects: absorb time-invariant district differences
- Quarter fixed effects: absorb national seasonality and macro shocks

### B. Optional seasonality marker (redundant but sometimes useful)

**Variable**: `monsoonquarter` (optional)

- Construction: indicator(q == 3) for Jul-Sep, else 0
- Rule: If quarter FE included, monsoon indicator not required for identification; use only for exposition or robustness

### C. Weather controls (preferred extension)

**Variable**: `rainfallqt` (optional)

- Must be spatially aggregated to district polygons then to quarters with documented method

---

## VI. Heterogeneity Variables (core only if actually used)

Heterogeneity variables must be defined pre-treatment (time-invariant or baseline-period constructs) or explicitly lagged so not mechanically affected by contemporaneous floods.

Examples (choose only if defensible and logged):

- Urban proxy based on baseline deposits (time-invariant classification)
- High exposure based on pre-period flood history

Rule: any proxy must be labeled proxy; do not rewrite as "urbanization" without census validation.

---

## VII. IV and Causal Pipeline Constructs (audit variables)

Variables exist to keep IV pipeline auditable.

**Variable**: `lightshatqt` (optional storage, recommended)

- Definition: fitted values from first stage (flood to lights)
- Rule: store for diagnostics only; do not interpret as observed lights

**Metric**: `firststageF`

- Definition: first-stage instrument strength statistic
- Rule: weak-IV risk must be reported; never buried

---

## VIII. File IO Contract (locked)

- Inputs: only from `01_Data_Raw/`
- Intermediate outputs: `02_Data_Intermediate/`
- Final analysis panels: `03_Data_Clean/`
- Figures and tables: `05_Outputs/Figures/`, `05_Outputs/Tables/`
- Logs: `05_Outputs/Logs/`

---

## IX. Script Contract (locked)

Every script must:

1. Log start and end time
2. Log exact input file paths and output file paths
3. Log row counts before and after major steps
4. Log any constant choices (e.g., lights log offset c)
5. Write log file to `05_Outputs/Logs/`

---

## X. Versioning Rule

Codebook allowed to evolve, but only via version bumps with explicit changelogs.

Hypotheses not allowed to drift to match results; codebook updates must be about measurement feasibility, naming consistency, or reproducibility discipline.

---

## XI. Data Quality Issues Identified

### Issue 1: Extreme outliers in deposit changes

**Variable affected**: `depositchangeqt`

**Problem**: Min = -2.73 (93 percent decline), Max = +6.56 (656 percent increase) in single quarters

**Likely causes**: District boundary changes or mergers (administrative), bank branch reclassification between districts (RBI reporting), data entry errors in RBI source Excel files

**Impact**: Outliers bias OLS coefficients and inflate standard errors

**Correction required**: Winsorize at 1st/99th percentile before final regressions

**Status**: Pending Phase 6 (scheduled 2026-01-31)

### Issue 2: Nominal growth confound (no deflation applied)

**Variable affected**: `depositscrores`, `depositchangeqt`

**Problem**: Mean deposit growth = 11.9 percent quarterly (47.6 percent annualized, compounded)

**Root cause**: RBI deposits measured in nominal rupees; no CPI deflation applied

**Impact**: Inflation trends confound flood treatment effects; cannot distinguish real shock from price growth

**Correction options**: (1) Deflate deposits by CPI (preferred if district-level deflator available), (2) Disclose limitation explicitly in paper and interpret coefficients as nominal effects

**Status**: Pending Phase 6 decision

### Issue 3: Zero-inflation in deposit changes

**Variable affected**: `depositchangeqt`

**Problem**: 25th percentile = 0.00, meaning 25 percent of district-quarters have exactly zero deposit change

**Possible causes**: Rounding in RBI source data (deposits reported in crores), static rural districts with no actual banking activity, copy-forward errors (same value repeated across quarters)

**Impact**: Potential measurement error; may reflect true absence of activity OR data quality issue

**Investigation required**: Identify which districts, which periods, whether systematic pattern exists

**Status**: Pending Phase 6

### Issue 4: RBI source data contamination - CRITICAL

**Variables affected**: `depositscrores`, `logdepositscrores`, `depositchangeqt`, all deposit-based analyses

**Problem discovered**: File `RBI_Deposits_2017_2022.xlsx` contains duplicate 2016 Q1-Q2-Q3 data incorrectly labeled as 2017 Q1-Q2-Q3

**Contamination details**:

- January-September 2016 appears twice in dataset: once correctly labeled 2016, once mislabeled 2017
- Double-counting causes systematic inflation in extracted deposit panel for 2017 Q1-Q3 period
- Script 13 (`13_extract_rbi_deposits.py`) lacks quarter-level date validation; trusts row labels without verifying column headers
- All downstream analyses (Scripts 14-17, 22-30) affected by contaminated deposit data

**Root cause**: RBI source file construction error combined with Script 13 insufficient validation

**Impact**: All deposit-based hypothesis tests (H2, H3, H4) contaminated. H1 (floods to lights) unaffected as uses only VIIRS data.

**Fix required**: Complete rewrite of Script 13 with explicit quarter-level validation: (1) Parse column headers to extract actual year-quarter, (2) Cross-validate against row labels, (3) Flag mismatches before extraction, (4) Log all date mappings to audit trail

**Status**: Script 13 flagged for rewrite (scheduled 2026-01-31). All deposit-based results under formal review. VIIRS data (Phase 5 clean) unaffected.

**Transparency note**: Issue discovered through systematic forensic data audit (Jan 30, 2026), not coefficient hunting. All contaminated outputs will be archived (not deleted) to maintain scientific integrity audit trail.

---

## XII. Audit Checklist

### VIIRS Bug Fix (Priority 1) - COMPLETED 2026-01-27

- [x] Identify Script 21 dissolve bug (2026-01-20 17:00 IST)
- [x] Delete dissolve block (Lines 52-55) from Script 21
- [x] Add district count validation (assert 676 districts loaded)
- [x] Backup all contaminated files to CONTAMINATED_BACKUP folders
- [x] Delete contaminated VIIRS panels, analysis files, regression outputs
- [x] Script 21 extraction completed (2026-01-21)
- [x] Verify output: 79,920 rows (666 districts times 120 months; 10 districts missing from GADM baseline)
- [x] Script 21b: Fix multi-tile overlap duplicates (1,080 observations removed via pixel-weighted averaging)
- [x] Run Script 22: Aggregate to quarterly
- [x] Run Scripts 23-30: Merge, engineer, validate, regress (all completed 2026-01-27)

### RBI Source Contamination Fix (Priority 1) - IN PROGRESS 2026-01-30

- [x] Discover duplicate 2016 Q1-Q3 data in RBI_Deposits_2017_2022.xlsx (2026-01-30 17:00 IST)
- [x] Document contamination details in Research_Log.txt (2026-01-30)
- [ ] Rewrite Script 13 with quarter-level date validation - PENDING
- [ ] Backup all contaminated deposit-based outputs - PENDING
- [ ] Re-run Scripts 13-17: Extract, merge, validate, prepare analysis sample - PENDING
- [ ] Re-run Scripts 22-30: Merge VIIRS, engineer variables, regenerate descriptive stats, re-run H2/H3/H4 regressions - PENDING
- [ ] Compare contaminated vs clean deposit-based coefficients - PENDING
- [ ] Update all documentation with corrected results - PENDING

### Data Quality Corrections (Priority 2) - PENDING Phase 6

- [ ] Apply winsorization to `depositchangeqt` (1 percent / 99 percent)
- [ ] Decide on CPI deflation vs disclosure strategy
- [ ] Investigate zero-change quarters (run diagnostic script)
- [ ] Diagnose 10 missing GADM districts (676 to 666)

---

## XIII. Clean Results Status

### VIIRS Data (Phase 5 Clean, 2026-01-27)

- H1 CONFIRMED: beta = -0.01250*** (p less than 0.0001, t = -31.1, N = 23,234) - Floods reduce nighttime lights by 1.25 percent
- Script 21 dissolve bug fixed; multi-tile duplicates resolved
- 666 districts, 79,920 monthly observations validated
- Measurement error quantified: Contaminated data caused H2 coefficient reversal from null (beta=0.120, p=0.538) to significant (beta=-0.278**, p=0.020)

### Deposit Data (Under Review, 2026-01-30)

- H2, H3, H4 results SUSPENDED pending Script 13 rewrite
- RBI source contamination affects 2017 Q1-Q3 period (double-counted 2016 data)
- All deposit-based coefficients require regeneration after corrected extraction
- H1 results (floods to lights) remain valid as independent of deposit data

---

## END OF DOCUMENT

**Status**: v1.7 updated with RBI source contamination discovery (2026-01-30 23:30 IST). Script 13 flagged for complete rewrite with quarter-level validation. All deposit-based analyses (H2, H3, H4) under formal review. VIIRS data (Phase 5 clean, 666 districts, 79,920 monthly observations) unaffected; H1 results remain valid. Phase 6 scheduled 2026-01-31 for Script 13 rewrite and deposit pipeline regeneration.

**Changelog (v1.6 to v1.7)**:

- Added Principle 8: Quarter-level date validation requirement for all RBI extraction
- Updated Issue 4: Changed from "VIIRS data contamination" to "RBI source data contamination" (VIIRS now clean; new issue discovered)
- Documented RBI_Deposits_2017_2022.xlsx duplicate 2016 Q1-Q3 data problem
- Added new audit checklist section: "RBI Source Contamination Fix (Priority 1)"
- Updated data quality status: VIIRS clean (Phase 5 complete), deposits under review
- Updated clean results section: H1 valid, H2/H3/H4 suspended pending regeneration
- Added transparency note: Issue discovered through forensic audit, not result-chasing

**Next review trigger**: Post Script 13 rewrite completion and deposit pipeline regeneration (2026-01-31). After verifying corrected RBI extraction, re-execute Scripts 14-17 and 22-30. Update to v1.8 with corrected deposit-based coefficients and comprehensive comparison of contaminated vs clean results.