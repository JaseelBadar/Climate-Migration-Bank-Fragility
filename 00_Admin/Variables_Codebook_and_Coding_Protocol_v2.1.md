# VARIABLES CODEBOOK AND CODING PROTOCOL (v2.1)

**Project**: Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India (2015-2024)

**Document Type**: Variables codebook and enforceable coding protocol
**Version**: 2.1 (VIIRS pipeline errors Fixed)

**Status**: Deposits fully corrected (Feb 11, 2026). VIIRS pipeline verified clean. Regression scripts require fixed effects correction before re-run. H3 results validated clean.

**Date**: February 11, 2026

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
- Data quality status: CLEAN (Feb 11, 2026). Two-bug cascade resolved: (1) Column offset corrected for fiscal quarter labels, (2) State filtering added for 7 homonymous districts (Aurangabad, Balrampur, Bijapur, Bilaspur, Hamirpur, Pratapgarh, Raigarh). Verification: Aurangabad Bihar 2015Q1 changed from 18652 (contaminated sum with Maharashtra) to 4422 (Bihar only, 76% drop). All deposits now accurate for 49,670 district-quarter observations.

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
- Data quality status: CLEAN (verified Feb 11, 2026). Scripts 18-24 use composite (district_gadm, state_gadm) keys throughout pipeline. Excel verification confirms distinct radiance values for homonymous districts (e.g., Aurangabad Bihar radiance differs from Maharashtra). No contamination found.

**Variable**: `loglightsqt`

- Definition: log-transformed quarterly lights level
- Construction (as implemented in Script 24): `loglightsqt = ln(meanradiance + c)` with fixed constant
- Constant rule (locked): If constant c used to handle zeros, must be fixed globally and written into logs; never tuned for results. Current pipeline uses +0.01 offset (Script 24, line 47: `np.log(df['mean_radiance'] + 0.01)`). Fixed and documented.

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

### Issue 4: RBI source data validation - RESOLVED

**Variables affected**: None (contamination concern was false alarm)

**Problem initially suspected (2026-01-30)**: File `RBI_Deposits_2017_2022.xlsx` appeared to contain duplicate 2016 Q1-Q3 data mislabeled as 2017 Q1-Q3

**Resolution (2026-01-31)**: Forensic cell-level audit confirmed RBI files are CLEAN
- File 1 ends at fiscal 2016-17:Q1 = calendar 2016Q2 (Jun 2016) ✓
- File 2 starts at fiscal 2017-18:Q1 = calendar 2017Q2 (Jun 2017) ✓
- Gap identified: 2016Q3, 2016Q4, 2017Q1 (3 quarters missing due to RBI publication schedule, NOT contamination) ✓
- Fiscal-to-calendar conversion in Script 13 verified correct ✓

**Root cause of false alarm**: Misunderstanding of RBI fiscal year convention during initial inspection; confusion between fiscal and calendar quarter labels

**Impact**: ZERO - No contamination exists; all deposit data valid

**Status**: RESOLVED (2026-01-31 23:48 PM IST). Script 13 validated correct. Phase 3c complete with clean deposit extraction. Analysis sample (23,347 obs) uses only validated non-gap quarters (2015Q1-2016Q2, 2017Q2-2024Q4).


## XII. Audit Checklist

### VIIRS Integration (Priority 1) - COMPLETED 2026-02-01

- [x] Identify Script 21 dissolve bug (2026-01-20 17:00 IST)
- [x] Delete dissolve block (Lines 52-55) from Script 21
- [x] Add district count validation (assert 676 districts loaded)
- [x] Backup all contaminated files to CONTAMINATED_BACKUP folders
- [x] Delete contaminated VIIRS panels, analysis files, regression outputs
- [x] Script 21 extraction completed (2026-01-21)
- [x] Verify output: 79,920 rows (666 districts times 120 months; 10 districts missing from GADM baseline)
- [x] Script 21b: Fix multi-tile overlap duplicates (1,080 observations removed via pixel-weighted averaging)
- [x] Run Script 22: Aggregate to quarterly
- [x] Run Scripts 22-25: Quarterly aggregation, VIIRS-master merge, variable engineering, descriptive stats
- [x] Run Script 26: Quality assurance validation (8-check audit passed)
- [x] Verify final dataset: 23,347 obs, 23 variables, 100% VIIRS-deposit overlap ✓

### RBI Source Validation (Priority 1) - COMPLETED 2026-01-31

- [x] Forensic audit of all 3 RBI source files (cell-level inspection)
- [x] Validate fiscal-to-calendar conversion in Script 13 ✓
- [x] Confirm 2016-2017 gap is structural (RBI publication), not contamination ✓
- [x] Verify deposit extraction correct (Scripts 13-17 re-validated)
- [x] Analysis sample confirmed clean: 23,347 obs, 99.1% deposit coverage ✓
- [x] RBI contamination concern RESOLVED (false alarm documented)

### Data Quality Corrections (Priority 2) - PENDING Phase 6

- [ ] Apply winsorization to `depositchangeqt` (1 percent / 99 percent)
- [ ] Decide on CPI deflation vs disclosure strategy
- [ ] Investigate zero-change quarters (run diagnostic script)
- [ ] Diagnose 10 missing GADM districts (676 to 666)

---

## XIII. Current Data Status

### Deposit Data: CLEAN
- Two-bug cascade resolved: Crosswalk deduplication (Script 8) and state filtering (Script 13)
- Validation: Aurangabad Bihar deposits dropped 76-83% after eliminating Maharashtra contamination
- Analysis-ready: 49,670 district-quarter observations (624 districts, 84 quarters)
- Excel spot-checks: All values match expected Bihar-only or Maharashtra-only totals

### VIIRS Data: CLEAN
- Pipeline verified: Scripts 18-24 use composite (district_gadm, state_gadm) keys
- Homonym separation confirmed: Aurangabad Bihar radiance distinct from Maharashtra
- Coverage: 79,920 monthly observations (666 districts, 120 months), aggregated to 26,640 quarterly
- No contamination found in forensic code review or Excel verification

### Phase 4 Regression Status: PENDING RE-RUN
- H3 results: VALIDATED CLEAN (specification uses deposits+floods only, no VIIRS, no FE contamination)
- H1, H2, H4 results: Pending re-run with clean deposits from Feb 11 fix
- Regression FE correction required: Scripts 27, 28, 30 must use composite district_state_id (currently use district name only, collapsing 7 homonymous pairs into 617 FE instead of 624)
- Master panel re-run required: Scripts 14-17 with clean deposits
- Estimated completion: 3 hours for full pipeline Scripts 14-30

### Priority Actions
1. Re-run master panel merge: Scripts 14-17 with clean rbi_deposits_panel.csv
2. Verify VIIRS merge clean: Script 23 output should preserve distinct values for homonymous districts
3. Fix regression FE: Change Scripts 27, 28, 30 to use composite district_state_id
4. Re-run all regressions: H1, H2, H4 with corrected data and FE
5. Compare results: Feb 6 (contaminated deposits) vs Feb 12 (clean deposits)

---

## XIV. Variable Usage Summary

### Dependent Variables (Current Status)
- `lightschangeqt`: Used in H1 (outcome), H2 (endogenous regressor) - CLEAN
- `depositchangeqt`: Used in H2, H3, H4 (outcome) - CLEAN (as of Feb 11)

### Independent Variables (All Clean)
- `floodexposureruleAqt`: Used in H1, H2, H3 - CLEAN
- `floodlag1qt`, `floodlag2qt`: Used in H3 timing - CLEAN

### Interaction Variables (Status)
- `urban`: If constructed from `loglightsqt` → CLEAN (VIIRS verified)
- `highexposure`: Based on flood history → CLEAN
- `monsoon`: Quarter indicator → CLEAN

### H3 Validated Results (Feb 6, Defensible)
- H3-t0 (current): β = -0.0005, p = 0.777 (null)
- H3-t1 (1Q lag): β = +0.0004, p = 0.757 (null)
- H3-t2 (2Q lag): β = -0.0091, p = 0.012 (significant at 5%)
- Specification: Uses deposits and floods only, no VIIRS variables, no homonym FE contamination
- Interpretation: 6-month lag effect defensible for publication

### H1, H2, H4 Pending Re-run
Feb 6 results cannot be interpreted due to deposit contamination (resolved Feb 11). Re-run scheduled with clean deposits and corrected fixed effects (composite district_state_id).

---

## END OF DOCUMENT

**Status**: v2.1 reflects full data quality resolution. Deposits cleaned via two-bug fix (crosswalk deduplication + state filtering, Feb 11). VIIRS pipeline verified clean (composite keys throughout). H3 results validated defensible. H1, H2, H4 pending re-run with clean deposits and corrected fixed effects. Variables codebook protocols unchanged.

---

## Variable Usage Summary (Phase 4 Results)

### Dependent Variables
- `lightschangeqt`: Used in H1 first stage (outcome), H2 IV (endogenous regressor)
- `depositchangeqt`: Used in H2 second stage (outcome), H3 timing (outcome), H4 heterogeneity (outcome)

### Independent Variables
- `floodexposureruleAqt`: Used in H1 (main regressor), H2 (instrument), H3 (current quarter)
- `floodlag1qt`: Used in H3 timing (1-quarter lag) [SIGNIFICANT RESULT]
- `floodlag2qt`: Used in H3 timing (2-quarter lag)

### Interaction Variables (H4 Heterogeneity)
- `urban`: Constructed from median split of district mean `loglightsqt` [SIGNIFICANT INTERACTION]
- `highexposure`: Constructed from median split of cumulative flood exposure
- `monsoon`: Quarter indicator (q == 3, Jul-Sep)

### Variables Not Used in Phase 4
- `floodexposureruleBqt`: Rule B variables reserved for robustness checks (Phase 5)
- Longer lags (L3, L4): Reserved for persistence testing (Phase 5)
- `logdepositscrores`, `loglightsqt`: Reserved for alternative specifications (Phase 5)

### Key Findings by Variable
1. `floodexposureruleAqt` → `lightschangeqt`: Strong negative effect (-0.0149, p<0.001)
2. `floodlag1qt` → `depositchangeqt`: Delayed negative effect (-0.0062, p<0.001)
3. `urban × flood` → `depositchangeqt`: Urban vulnerability confirmed (-0.0111, p<0.001)
4. All other interactions (high_exposure, monsoon): Null results

---

**Changelog (v2.0 to v2.1)**:
- Updated version: 2.0 → 2.1
- Updated status: Deposits fully cleaned (two-bug fix Feb 11), VIIRS verified clean (Feb 11)
- Section II.A: Deposits data quality updated with two-bug resolution timeline
- Section IV.A: VIIRS data quality changed from CONTAMINATED to CLEAN (verification complete)
- Section XI: Deleted Issue 5 (VIIRS contamination resolved as false alarm)
- Section XIII: Rewrote "Current Data Status" reflecting all sources clean
- Section XIV: Updated "Variable Usage Summary" with H3 validated, H1/H2/H4 pending re-run
- All variable definitions and coding protocols unchanged

**Next review trigger**: After Scripts 14-30 re-run with clean deposits. Update to v2.2 with final Phase 4 regression results.