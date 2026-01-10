# VARIABLES CODEBOOK + CODING PROTOCOL (v1.1)
**Project**: Climate Migration, Night Lights, and Bank Fragility in India (2015–2024)  
**Document Type**: Variables codebook + enforceable coding protocol  
**Version**: 1.1 (post Phase 3c Day 1 inspection)  
**Date**: January 8, 2026

---

## 0. Non-negotiable principles (read first)

1. **Raw data is read-only**: Never modify anything inside `01_Data_Raw/`. All transformations must write to `02_Data_Intermediate/` or `03_Data_Clean/`. 
2. **No silent drops**: Any row/observation dropped must be logged with counts and reasons.
3. **No endogeneity by construction**: Never use VIIRS outcomes to define flood treatment. (No “flood = 1 if lights drop”.)
4. **One script = one responsibility**: Each script produces one named output dataset and one log file.
5. **Reproducibility beats cleverness**: Prefer simple, auditable transformations over complex heuristics.

---

## I. PANEL STRUCTURE

**Unit of analysis**: Indian District (administrative unit as represented in RBI district strings).   

**Target period**: Quarterly, 2015Q1 to 2024Q4 (40 quarters).   

**Expected N**: TBD. Prior expectation “~640” is obsolete; RBI inspection indicates ~762 district strings in the 2023–2024 workbook, and the final N depends on:  
- district splits/renames across years,  
- whether RBI historical files use different district naming conventions,  
- harmonization success with district boundary shapefiles. 

**Panel type**: Unbalanced until proven balanced (do not assume complete coverage). 

**Key index variables (must exist in the final panel)**:
- `district_name_raw`: district label exactly as in RBI source.
- `district_id`: stable district identifier (constructed via crosswalk).
- `state_name`: state/UT name (constructed from district crosswalk/shapefile join).
- `quarter`: string like `2015Q1`.
- `year`: 2015–2024
- `q`: 1–4
- `quarter_num`: 1–40 sequential index for panel lags.

---

## II. OUTCOME VARIABLES (bank stress measures)

### A. Deposit variables

**Variable**: `total_deposits_qt`  
**Definition**: Total aggregate deposits in district i, quarter t (all SCBs).   
**Unit**: Nominal INR (as reported by RBI; verify unit scaling once headers are parsed).  
**Source**: RBI district-level deposit statistics workbook(s).   
**Construction**: Extract RBI deposits and (if required) aggregate across population groups.

**Variable**: `log_deposits_qt`  
**Definition**: Natural log of deposits.   
**Construction**: `log_deposits_qt = ln(total_deposits_qt)`  
**Rule**: If deposits can be zero/missing, handle using missingness rules (do not add arbitrary constants unless absolutely required and justified).

**Variable**: `deposit_change_qt`  
**Definition**: Quarter-over-quarter change in log deposits.   
**Construction**: `deposit_change_qt = log_deposits_qt - L1(log_deposits_qt)`  
**Interpretation**: approximately percentage change.

**Variable**: `deposit_withdrawal_binary`  
**Definition**: “Withdrawal event” indicator (shadow-run proxy).   
**Construction (data-driven, pre-committed)**:
- Define threshold \(k\) using a baseline distribution (e.g., non-flood district-quarters) **before** estimating main regressions.
- Baseline rule: `k = min(-0.10, P10(deposit_change_qt | Flood=0))` (i.e., at least 10% decline OR bottom decile if more extreme).  
Then: `deposit_withdrawal_binary = 1 if deposit_change_qt < k else 0`.  
**Robustness**: also test thresholds at {5%, 10%, 15%, 20%} declines.

### B. Branch / banking structure (only if RBI supports it)
These variables are conditional on availability in the RBI tables actually downloaded.

**Variable**: `branch_count_qt`  
**Definition**: number of reporting offices/branches in district-quarter.   
**Status**: uncertain; only include if explicitly present.

**Variable**: `branch_change_qt`  
**Construction**: `branch_change_qt = branch_count_qt - L1(branch_count_qt)`  
**Status**: include only if `branch_count_qt` exists and has consistent reporting.

### C. Per-capita adjustments (optional)
**Variable**: `deposits_per_capita_qt`  
**Definition**: deposits divided by population.   
**Warning**: district-year population is hard; if only Census 2011 exists, treat as static and disclose limitation.

---

## III. TREATMENT VARIABLES (shocks)

### A. Flood exposure (EM-DAT)

**Variable**: `flood_exposure_qt`  
**Definition**: indicator for flood exposure in district i, quarter t.   
**Source**: EM-DAT floods (India, 2015–2024).   
**Date-to-quarter mapping rule**: If flood start date falls in quarter t, code exposure in t (primary). Lags will be used for timing tests.

**Geographic matching problem (must be explicit)**:
- EM-DAT location precision is heterogeneous (some events list districts, some are state-only or vague regions). 
- This creates unavoidable measurement error in `flood_exposure_qt` in the “full sample.”

**Pre-committed mapping rule set (NO improvisation during coding)**:
- **Rule A (Full sample / lower-bound)**: If event location is state-level, code `flood_exposure_qt=1` for **all districts in that state** for that quarter. (Overinclusive → attenuation bias.) 
- **Rule B (High-precision sample / credibility spec)**: Only code district exposure when the district is explicitly named (Admin Units JSON OR parseable district in free-text location). 
- Report both. Rule B is the identification credibility check; Rule A is the “broad exposure” version.

**FORBIDDEN RULE (explicitly rejected)**:
- **Never** define flood exposure using VIIRS lights drops. This is mechanical endogeneity (post-treatment conditioning). 

**Variable**: `flood_severity_qt`  
**Definition**: continuous measure of intensity.   
**Preferred construction**:  
- `flood_severity_qt = ln(affected + deaths + 1)` (if both exist)  
- Alternative: `ln(affected + 1)` only (if deaths missing frequently).

**Variables**: `flood_lag1_qt`, `flood_lag2_qt`  
**Construction**: lagged indicators derived from `flood_exposure_qt`.

---

## IV. MIGRATION / DISRUPTION PROXY VARIABLES (VIIRS night lights)

### A. Monthly district-level radiance

**Variable**: `viirs_brightness_mt`  
**Definition**: mean VIIRS radiance within district boundary for month m.   
**Unit**: VIIRS native radiance units.  
**Input file**: `.avg_rade9h.tif` monthly composite(s).   
**GIS requirement**: district polygons (source TBD; must be recorded once chosen). 

**Quality companion variables (recommended)**:
- `viirs_cvg_mt`: coverage count/weight from `cvg.tif` (if available for each month).  
- `viirs_cf_cvg_mt`: cloud-free coverage from `cf_cvg.tif`.  
These are used for quality flags, not to “fix” outcomes.

**Variable**: `log_viirs_brightness_mt`  
**Construction**: `log_viirs_brightness_mt = ln(viirs_brightness_mt + c)`  
**Constant rule**:
- Choose a small constant `c` only if zeros exist; record chosen `c` in the log and keep fixed.
- Do not tune `c` for results.

### B. Quarterly aggregation (baseline definition)

**Variable**: `log_lights_qt`  
**Definition**: quarterly mean of `log_viirs_brightness_mt` across months in the quarter.  
**Construction**: `log_lights_qt = mean(log_viirs_brightness_mt over 3 months)`.

**Variable**: `lights_change_qt`  
**Definition**: quarter-over-quarter change in quarterly mean log lights.  
**Construction (baseline)**: `lights_change_qt = log_lights_qt - L1(log_lights_qt)`.

**Alternative (robustness only)**:
- average of monthly changes within quarter.
- end-of-quarter snapshot.
These can be tested later but must not replace the baseline silently.

### C. Migration proxy event

**Variable**: `migration_proxy_qt`  
**Definition**: binary indicator for significant lights decline.   
**Construction (data-driven, aligned with hypotheses)**:
- `migration_proxy_qt = 1 if lights_change_qt < -theta else 0`
- Baseline `theta` must be chosen **from the empirical distribution** (e.g., median or 75th percentile of negative `lights_change_qt` among flood-exposed district-quarters in the high-precision sample), recorded before final H2 estimation.
- Robustness: `theta ∈ {0.10, 0.15, 0.20}`. 

---

## V. CONTROL VARIABLES (confounds)

Controls are not decorative: they exist to prevent false “migration” signals driven by seasonality/weather/economic cycles. 

### A. Seasonality controls (minimum viable)
**Variable**: `monsoon_quarter`  
**Construction**: `1 if quarter overlaps monsoon season else 0` (exact mapping must be defined once and fixed). 

### B. Weather controls (preferred; may be missing initially)
**Variable**: `rainfall_qt`  
**Source**: IMD gridded rainfall (if obtained).   
**Construction**: spatial aggregation of rainfall grid to district polygons, then quarterly sum/mean.

### C. Static district characteristics (optional but helpful)
**Variable**: `agriculture_share_static` (Census 2011)   
**Variable**: `urbanization_rate_static` (Census 2011)   
If used, explicitly state they are time-invariant proxies.

---

## VI. NETWORK / SPILLOVER VARIABLES (extensions)

### A. Spatial network (feasible with shapefiles)
**Variable**: `spatial_adjacency_ij`  
**Definition**: 1 if districts share a border, else 0. 

**Variable**: `spillover_adjacent_flood_qt`  
**Construction**:
- `spillover_adjacent_flood_qt = sum over neighbors j of Flood_{jt}`
- Requires adjacency list.

### B. Banking network (high risk; only if data exists)
**Variable**: `shared_banks_ij`  
**Status**: high risk; requires bank-level presence data not confirmed. 

---

## VII. IV / CAUSAL PIPELINE CONSTRUCTS (explicit)

These variables exist so the coding matches the causal story and can be audited.

**Variable**: `lights_hat_qt`  
**Definition**: predicted lights change from the first-stage flood → lights regression (with FE and controls).  
**Construction**: produced by the IV/2SLS routine; stored for diagnostics only.

**Metric**: `first_stage_F`  
**Definition**: first-stage F-statistic for the instrument strength check.  
**Rule**: Always report weak-IV risk; do not hide it.

---

## VIII. DATA SOURCES SUMMARY (current)

| Dataset | What it provides | Coverage | Unit | Format | Status |
|--------|------------------|----------|------|--------|--------|
| RBI deposits | deposits (and maybe offices) | 2004–2024 quarterly | district | Excel | downloaded (3 files) |
| EM-DAT floods | dates, location text/admin units, affected/deaths | 2015–2024 | event | Excel | downloaded (1 file) |
| VIIRS lights | monthly radiance composites (+ quality layers) | monthly | pixel → district | GeoTIFF | only 1 month validated so far |
| District polygons | boundaries for district aggregation (GADM v4.1; Level 2) | static | district | shapefile | downloaded + load-tested (676 districts) |

---

## IX. CRITICAL MEASUREMENT DECISIONS (locked vs pending)

### Locked (must not drift)
1. **Raw data read-only**.  
2. **Flood coding never depends on VIIRS**.  
3. **Baseline quarterly lights change = quarterly mean log level difference**.

### Pending (must be decided with explicit log entry)
1. District boundary dataset chosen: GADM v4.1 (Level 2). Pending: harmonize RBI district strings to GADM district names via crosswalk; document unavoidable splits/renames. 
2. How to handle district splits/renames across years (crosswalk design).
3. Whether to deflate deposits (nominal vs real). 

---

## X. VARIABLE NAMING CONVENTIONS (strict)

Suffixes:
- `_qt` quarterly
- `_mt` monthly
- `_static` time-invariant
- `_binary` 0/1
- `_log` log transform
- `_lag1`, `_lag2` lags
- `_raw` directly from source before cleaning

Forbidden:
- `var1`, `x`, `temp`, `final_data`, `data2`, `new_new_final`.

---

## XI. MISSING DATA PROTOCOL (enforceable)

**Rule 1: Always generate a missingness report** before regressions:
- `% missing by variable`
- `% missing by year`
- `% missing by district`

**Rule 2: Never forward-fill outcomes** (`total_deposits_qt`, `log_deposits_qt`, `log_lights_qt`).
- If missing: the district-quarter is missing. Drop only with log entry.

**Rule 3: Controls can be missing**, but strategy must be pre-committed per control:
- Main spec: drop rows missing key controls (transparent, smaller sample).
- Robustness: simple imputations can be tested, but clearly labeled.

---

## XII. CODING PROTOCOL (the actual “coding guidelines”)

### A. Folder IO contract (must be followed)
- Inputs: only from `01_Data_Raw/`
- Intermediate outputs: `02_Data_Intermediate/`
- Final analysis panel(s): `03_Data_Clean/`
- Figures/tables: `05_Outputs/Figures/`, `05_Outputs/Tables/`
- Logs: `05_Outputs/Logs/` (create this folder if missing)

### B. Script contract
Every script must:
1. Print (and log) start/end time.
2. Print input filenames and output filenames.
3. Print row counts before/after major steps.
4. Write a machine-readable log (CSV or TXT) to `05_Outputs/Logs/`.

### C. Canonical pipeline (planned)
Names below are placeholders, but the responsibilities are fixed.

1. `05_extract_rbi.py`  
   Output: `02_Data_Intermediate/rbi_deposits_long.csv`

2. `06_extract_emdat.py`  
   Output: `02_Data_Intermediate/emdat_flood_events.csv`

3. `07_build_district_crosswalk.py`  
   Output: `02_Data_Intermediate/district_crosswalk.csv`

4. `08_build_flood_panel.py`  
   Output: `02_Data_Intermediate/flood_exposure_panel.csv`  
   Must output BOTH:
   - `flood_exposure_ruleA_qt` (state-wide coding)
   - `flood_exposure_ruleB_qt` (district-only coding)

5. `09_aggregate_viirs_to_district.py`  
   Output: `02_Data_Intermediate/viirs_district_monthly.csv`  
   Then `02_Data_Intermediate/viirs_district_quarterly.csv`

6. `10_merge_panel.py`  
   Output: `03_Data_Clean/panel_district_quarter_2015_2024.csv`

### D. Versioning and “stop conditions”
- If the crosswalk match rate (RBI districts → shapefile districts) < 80%, STOP and fix crosswalk methodology before running regressions.
- If first-stage (flood → lights) is extremely weak in the high-precision sample, STOP and reconsider the proxy story (do not “push through” with weak instruments).

---

## END OF DOCUMENT
**Status**: v1.1 ready for implementation.  
**Next review**: After district polygons chosen + after RBI historical file structure is parsed.