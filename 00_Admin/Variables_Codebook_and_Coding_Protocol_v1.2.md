# VARIABLES CODEBOOK + CODING PROTOCOL (v1.3)
**Project**: Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India (2015–2024)  
**Document Type**: Variables codebook + enforceable coding protocol  
**Version**: 1.3 (post Phase 3d/Phase 4 pipeline implementation; naming aligned to current scripts)  
**Date**: January 16, 2026  

---

## 0) Non-negotiable principles (read first)

1. **Raw data is read-only**: Never modify anything inside `01_Data_Raw/`. All transformations must write to `02_Data_Intermediate/` or `03_Data_Clean/`.  
2. **No silent drops**: Any row/observation dropped must be logged with counts and reasons.  
3. **No endogeneity by construction**: Never use VIIRS outcomes to define flood treatment. (No “flood = 1 if lights drop”.)  
4. **One script = one responsibility**: Each script produces one named output dataset and one log file.  
5. **Reproducibility beats cleverness**: Prefer simple, auditable transformations over complex heuristics.  
6. **Do not overclaim**: If a variable is a proxy (urban, migration, exposure), label it as such in outputs + paper.

---

## I) Panel structure

**Canonical unit**: Indian district polygons from **GADM v4.1 Level-2**.  
RBI districts are mapped to GADM using a crosswalk (RBI is not the canonical geography).  

**Target period**: Quarterly, 2015Q1 to 2024Q4 (40 quarters).  

**Important implementation reality (must be documented, not hidden)**:
- The “analysis sample” may drop quarters with missing deposits and may drop districts with zero deposit coverage (this is a sample restriction, not a data “feature”).  

**Key index variables (must exist in final analysis panel)**  
(Names are aligned to the implemented pipeline / Script 24 conventions.)
- `districtgadm`: canonical district name (GADM).
- `stategadm`: canonical state name (GADM).
- `quarter`: string like `2015Q1`.
- `year`: 2015–2024.
- `q`: 1–4.
- `quarternum`: sequential index (1–40) used for sorting/lags.

**Sorting rule (locked)**:
- Always sort by `districtgadm`, `stategadm`, `quarternum` before constructing lags/differences.

---

## II) Outcome variables (banking)

### A) Deposits (levels)
**Variable**: `depositscrores`  
- **Definition**: Total deposits in district-quarter.  
- **Unit**: ₹ crores (verify from RBI tables; treat as nominal unless deflated).  
- **Construction**: RBI extraction aggregates across population groups where needed.

**Variable**: `logdepositscrores`  
- **Definition**: natural log of deposits.  
- **Construction**: `logdepositscrores = ln(depositscrores)`  
- **Rule**: Do not add arbitrary constants unless deposits can be zero; if a constant is used, it must be fixed and logged.

### B) Deposits (growth)
**Variable**: `depositchangeqt`  
- **Definition**: quarter-over-quarter log change in deposits (approx % change).  
- **Construction**: within district,
  - `depositchangeqt = logdepositscrores - L1(logdepositscrores)`  
- **Missingness rule**: first observed quarter per district will have missing change by construction.

### C) Optional “withdrawal event” proxy (only if used in paper)
**Variable**: `depositwithdrawalbinary` (optional)  
- **Definition**: indicator for unusually large deposit decline (shadow-run proxy).  
- **Pre-commitment rule**:
  - Define threshold `k` from a baseline distribution BEFORE any mechanism regressions.
  - Example baseline: bottom decile of `depositchangeqt` among non-flood observations OR a fixed −10% rule, whichever is more conservative.
- **Construction**: `1[depositchangeqt < k]`.

---

## III) Treatment variables (flood shocks)

Flood exposure is constructed from EM-DAT and mapped into quarters, then into districts using a documented rule set.  

### A) Exposure indicators (two precision regimes; both required)
**Variable**: `floodexposureruleAqt`  
- **Rule A (full sample / lower-bound)**: if event location is only state-level, code flood exposure for **all districts in that state** for that quarter.  
- **Interpretation constraint**: attenuation bias is expected due to false positives.

**Variable**: `floodexposureruleBqt`  
- **Rule B (high-precision / credibility spec)**: code exposure only when districts are explicitly identified (Admin Units and/or verified parsing).  
- **Interpretation constraint**: smaller effective treatment variation; may weaken power.

### B) Lags (timing tests)
**Variable**: `floodlag1qt`  
- **Definition**: one-quarter lag of flood exposure (baseline: Rule A unless explicitly running Rule B spec).  
- **Construction**: `L1(floodexposureruleAqt)` within district.

**Variable**: `floodlag2qt` (optional if used)  
- **Construction**: `L2(floodexposureruleAqt)` within district.

### C) Severity (optional; only if available and logged cleanly)
**Variable**: `floodseverityqt` (optional)  
- **Preferred construction**: `ln(affected + deaths + 1)` if both are available with acceptable completeness.  
- If missingness is large, severity must be treated as exploratory (not a main result).

---

## IV) Migration / disruption proxy (VIIRS night lights)

### A) Quarterly lights level
**Variable**: `meanradiance`  
- **Definition**: district-quarter mean VIIRS radiance (after monthly extraction and quarterly aggregation).  
- **Rule**: This variable must be constructed only from VIIRS (never influenced by flood coding).

**Variable**: `loglightsqt`  
- **Definition**: log-transformed quarterly lights level.  
- **Construction (as implemented in Script 24)**: `loglightsqt = ln(meanradiance + c)` with a fixed constant.  
- **Constant rule (locked)**:
  - If a constant `c` is used to handle zeros, it must be fixed globally and written into logs; never tuned for results.
  - Current pipeline uses a +1 offset (record and keep fixed unless a formal change is logged).

### B) Quarterly lights change
**Variable**: `lightschangeqt`  
- **Definition**: quarter-over-quarter change in log lights (approx % change).  
- **Construction**: within district,
  - `lightschangeqt = loglightsqt - L1(loglightsqt)`.

### C) Optional migration/disruption event indicator (only if used)
**Variable**: `migrationproxyqt` (optional)  
- **Definition**: indicator for a large negative lights shock.  
- **Construction**: `1[lightschangeqt < -theta]`.  
- **Threshold discipline**:
  - `theta` must be chosen from the empirical distribution in flood-exposed district-quarters in the high-precision sample (Rule B), and recorded before estimating final H2 event-spec regressions.
  - Robustness: theta ∈ {0.10, 0.15, 0.20}.

---

## V) Controls and fixed effects

### A) Minimum viable controls (baseline)
- **District fixed effects**: absorb time-invariant district differences.
- **Quarter fixed effects**: absorb national seasonality and macro shocks.

### B) Optional seasonality marker (redundant but sometimes useful)
**Variable**: `monsoonquarter` (optional)  
- **Construction**: `1[q == 3]` (Jul–Sep), else 0.  
- **Rule**: If quarter FE are included, monsoon indicator is not required for identification; use only for exposition or robustness.

### C) Weather controls (preferred extension)
**Variable**: `rainfallqt` (optional)  
- Must be spatially aggregated to district polygons and then to quarters with a documented method.

---

## VI) Heterogeneity variables (core only if actually used)

Heterogeneity variables must be defined **pre-treatment** (time-invariant or baseline-period constructs) or explicitly lagged so they are not mechanically affected by contemporaneous floods.

Examples (choose only if defensible + logged):
- “Urban proxy” based on baseline deposits (time-invariant classification).
- “High exposure” based on pre-period flood history.

Rule: any proxy must be labeled a proxy; do not rewrite it as “urbanization” without census validation.

---

## VII) IV / causal pipeline constructs (audit variables)

These are not “nice to have.” They exist to keep the IV pipeline auditable.

**Variable**: `lightshatqt` (optional storage, but recommended)  
- **Definition**: fitted values from first stage (flood → lights).  
- **Rule**: store for diagnostics only; do not interpret as observed lights.

**Metric**: `firststageF`  
- **Definition**: first-stage instrument strength statistic.  
- **Rule**: weak-IV risk must be reported; never buried.

---

## VIII) File IO contract (locked)

- Inputs: only from `01_Data_Raw/`  
- Intermediate outputs: `02_Data_Intermediate/`  
- Final analysis panels: `03_Data_Clean/`  
- Figures/tables: `05_Outputs/Figures/`, `05_Outputs/Tables/`  
- Logs: `05_Outputs/Logs/`

---

## IX) Script contract (locked)

Every script must:
1. Log start/end time.
2. Log exact input file paths and output file paths.
3. Log row counts before/after major steps.
4. Log any constant choices (e.g., lights log offset `c`).
5. Write a log file to `05_Outputs/Logs/`.

---

## X) Versioning rule

- The codebook is allowed to evolve, but **only** via version bumps with explicit changelogs.
- Hypotheses are not allowed to drift to match results; codebook updates must be about measurement feasibility, naming consistency, or reproducibility discipline.

---

## END OF DOCUMENT
**Status**: v1.3 aligns variable names to the implemented regression pipeline (Script 24 conventions) and to the two-precision flood exposure design.  
**Next review trigger**: any change to (a) flood exposure rules, (b) lights log offset constant, or (c) analysis-sample drops requires a new version bump and a logged justification.