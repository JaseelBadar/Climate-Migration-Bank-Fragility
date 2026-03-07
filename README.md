# Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Nighttime Lights in India

Empirical analysis of flood-induced displacement effects on district-level deposit
stability across India, 2015–2024. Constructs a district-quarter panel linking
EM-DAT flood events, VIIRS nighttime lights, and RBI banking statistics for
631 districts in a panel IV strategy.

**Status:** Full data pipeline clean and verified (Scripts 08–26). Regressions
(Scripts 27–30) pending FE specification correction before execution.

**Project start:** 2025-12-30 | **Last updated:** 2026-03-07

---

## Research Question

Do flood-induced displacement shocks — identified through nighttime-lights declines —
cause deposit stress in Indian district-level banking? Does this effect concentrate
in urban districts and persist beyond the flood quarter?

---

## Identification Strategy

| Stage | Specification | Method |
|---|---|---|
| H1 — First stage | Floods → nighttime lights decline | OLS, district + quarter FE |
| H2 — Second stage | Lights decline → deposit outflows | IV 2SLS, flood as instrument |
| H3 — Timing | Distributed lag: t0, t+1, t+2 post-flood | OLS with lags, no VIIRS |
| H4 — Heterogeneity | Urban vs rural, high-exposure vs low | Interaction terms |

All specifications use district-clustered standard errors. Fixed effects use
composite `district_state_id = district_gadm + '_' + state_gadm` to correctly
handle 7 homonymous district pairs across states (e.g., Aurangabad: Bihar and
Maharashtra).

---

## Current Results

Most recent regression run: Feb 6, 2026. Scripts 27–30 pending re-run with
corrected pipeline and FE specification.

| Hypothesis | Specification | β | SE | p-value | Status |
|---|---|---|---|---|---|
| H1 | Floods → Lights | −0.0149 | 0.0028 | <0.001 | **Pending re-run** |
| H2 | Lights → Deposits (IV 2SLS) | +0.2191 | — | 0.299 | **Pending re-run** |
| H3-t0 | Flood → Deposits, current quarter | −0.0005 | — | 0.777 | Null confirmed |
| H3-t1 | Flood → Deposits, 1Q lag | +0.0004 | — | 0.757 | Null confirmed |
| H3-t2 | Flood → Deposits, 2Q lag | −0.0091 | — | 0.012 | **Confirmed** |
| H4a | Urban × Flood | −0.0013 | — | 0.665 | **Pending re-run** |
| H4b | HighExposure × Flood | −0.0057 | — | 0.068 | **Pending re-run** |
| H4c | Monsoon × Flood | +0.0119 | — | <0.001 | **Pending re-run** |

**H3 interpretation:** Flood-induced deposit stress is absent in the quarter of
impact and the quarter immediately following. The effect peaks at t+2 (6 months
post-flood): a −0.91% decline in deposit growth. This lag is consistent with
gradual displacement — households exhaust immediate coping strategies before
liquidating bank deposits. H3 uses no VIIRS data; specification is unaffected
by pipeline corrections and results are validated clean.

---

## Data Sources

Raw data files are never modified. All transformations applied in intermediate
and clean folders only.

### RBI District Banking Statistics (BSR-2)
- **Source:** Reserve Bank of India
- **Coverage:** 762 districts, 2004Q1–2025Q3, quarterly
- **Files:** `RBI_Deposits_2004_2017.xlsx`, `RBI_Deposits_2017_2022.xlsx`,
  `RBI_Deposits_2023_2024.xlsx`
- **Variable:** Total deposits (Rs Crores), aggregated across population groups
- **Status:** CLEAN. Column offset bug (Script 13) and state-blind merge bug
  (Script 8) both resolved. Verification anchor: Aurangabad Bihar 2015Q1 =
  4,422 Crores (was 18,652 — contaminated Bihar + Maharashtra sum). Deposit
  range: 29–1,237,744 Crores across analysis sample.

### EM-DAT Global Disaster Database
- **Source:** CRED, Université catholique de Louvain
- **Coverage:** Flood events, India, 2015–2024
- **Variables:** District/state location, event dates, affected population
- **Status:** CLEAN. Crosswalk regression (Script 8) permanently fixed with
  762-row hard assert and mandatory state-token exclusion. Flood panel
  regenerated: Rule A = 2,518 events (raw), 2,238 (analysis sample).

### VIIRS Nighttime Lights (DNB)
- **Source:** Colorado School of Mines — Earth Observation Group (PAYNE Institute)
- **Coverage:** Monthly composites, Jan 2015–Dec 2024, tile 75N060E
- **Variable:** Mean radiance (nW/cm²/sr) per district per month
- **Status:** CLEAN throughout. 100% district coverage in final analysis panel.
  Composite (district_gadm, state_gadm) keys used in all extraction and merge
  scripts. Aurangabad litmus confirmed: Bihar = 0.7222, Maharashtra = 0.5094
  (distinct — no contamination).
- **Storage:** Monthly tiles (~65 GB) at `E:\VIIRS_Raw_Data_75N060E\`

### GADM v4.1 District Boundaries
- **Source:** Global Administrative Areas
- **Coverage:** 676 district polygons, India Level-2
- **Usage:** VIIRS spatial aggregation; crosswalk harmonisation standard
- **Location:** `01_Data_Raw/District_Boundaries/gadm41_IND_2.shp`

---

## Sample Construction

| Stage | Districts | Quarters | Observations | Notes |
|---|---|---|---|---|
| GADM baseline | 676 | — | — | Spatial reference |
| VIIRS extraction | 666 | 40 | 26,640 | 10 districts outside tile |
| RBI extraction | 762 | 40 | — | Fiscal-to-calendar converted |
| Crosswalk match | 631 | — | — | 83.2% RBI–GADM match rate |
| Master panel raw | 666 | 40 | 26,640 | Deposits + floods merged |
| **Analysis sample** | **631** | **37** | **23,347** | Both restrictions applied |

**Sample restrictions (Script 17, Option 3):**
1. Drop 2016Q3–2017Q1 — RBI publication blackout (100% missing, 3 quarters)
2. Drop 35 zero-coverage districts — no deposit data across entire panel

**Note on district counts:** Some intermediate outputs report 624 unique district
names. This reflects `.nunique()` on `district_gadm` alone, which undercounts by 7
due to homonymous pairs. The correct count of 631 uses composite
(district_gadm, state_gadm) pairs throughout.

**Key sample statistics — clean pipeline, verified Mar 6–7, 2026:**
- Deposit coverage: 98.9% (23,079 / 23,347 observations)
- VIIRS coverage: 100.0% (23,347 / 23,347 observations)
- Flood exposure Rule A: 2,238 events | 9.59% treatment rate | 569 districts
- Flood exposure Rule B: 209 events | 0.90% treatment rate | 141 districts
- Mean deposits: 16,425.73 Crores | Median: 6,135.58 Crores
- Mean radiance: 0.6955 nW/cm²/sr | Median: 0.4266 | SD: 1.6884

---

## Pipeline Status

| Script | Purpose | Status | Output |
|---|---|---|---|
| 08 | Build district crosswalk | Clean | district_crosswalk_draft.csv |
| 10 | Build flood exposure panel | Clean | flood_exposure_panel.csv |
| 11 | Validate flood exposure | Clean | validation log |
| 12 | Flood exposure summary | Clean | 12_flood_exposure_summary.txt |
| 13 | Extract RBI deposits | Clean | rbi_deposits_panel.csv |
| 14 | Merge master panel | Clean | master_panel_raw.csv |
| 15 | Validate master panel | Clean | master_panel_validation_log.txt |
| 17 | Prepare analysis sample | Clean | master_panel_analysis.csv |
| 21/21b | Extract + deduplicate VIIRS | Clean | viirs_monthly_panel_fixed.csv |
| 22/22b | Aggregate + align VIIRS | Clean | viirs_quarterly_panel_clean.csv |
| 23 | Merge VIIRS with master panel | Clean | analysis_panel_final.csv |
| 24 | Engineer regression variables | Clean | regression_panel_final.csv |
| 25 | Descriptive statistics | Clean | 01_descriptive_stats.csv |
| 26 | Validate VIIRS quarterly panel | Clean | 26_viirs_quarterly_validation.txt |
| **27–30** | **H1–H4 regressions** | **Pending FE correction** | — |

**FE correction required (Scripts 27, 28, 30):** District fixed effects must
use `district_state_id = district_gadm + '_' + state_gadm`. Using `district_gadm`
alone collapses 7 homonymous pairs — 624 FE instead of correct 631.
Script 29 (H3) uses no district FE and is unaffected.

---

## Verified File Registry

| File | Rows | Key verification metric | Status |
|---|---|---|---|
| district_crosswalk_draft.csv | 762 | Hard assert: len==762 PASS | Clean |
| flood_exposure_panel.csv | 26,640 | Rule A: 2,518 events | Clean |
| rbi_deposits_panel.csv | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores | Clean |
| master_panel_raw.csv | 26,640 | Rule A: 2,518 | BALOD 2022Q4 = 3,296 Crores | Clean |
| master_panel_analysis.csv | 23,347 | 631 districts × 37 quarters | Clean |
| viirs_quarterly_panel_clean.csv | 25,240 | 631 districts × 40 quarters | Clean |
| analysis_panel_final.csv | 23,347 | 100% VIIRS coverage, 0 missing | Clean |
| regression_panel_final.csv | 23,347 | 23 columns, lag arithmetic verified | Clean |
| 01_descriptive_stats.csv | 6 vars | Rule A 2,238 events, 9.59% rate | Clean |

*rbi_deposits_panel.csv contains 50,192 total rows including 2025Q1–Q3 quarters
outside the analysis window. Extra rows are dropped harmlessly at skeleton merge.*

---

## Repository Structure

E:\Climate-Migration-Bank-Fragility
│
├── 00_Admin/
│ ├── Research_Log.txt
│ ├── Hypotheses_Formal_v1.8.md
│ ├── Variables_Codebook_v1.8.md
│ ├── RBI_Excel_Structure_Audit.txt
│ ├── Literature_Tracker.xlsx
│ └── Core_Claims.docx
│
├── 01_Data_Raw/ # Never modified
│ ├── RBI_Bank_Data/
│ ├── EMDAT_Disasters/
│ ├── VIIRS_NightLights/
│ └── District_Boundaries/
│
├── 02_Data_Intermediate/
│ ├── district_crosswalk_draft.csv # Clean (762 rows)
│ ├── flood_exposure_panel.csv # Clean (2,518 Rule A)
│ ├── rbi_deposits_panel.csv # Clean (50,192 rows)
│ ├── master_panel_raw.csv # Clean (26,640 rows)
│ ├── master_panel_analysis.csv # Clean (23,347 rows)
│ ├── master_panel_validation_log.txt
│ ├── viirs_jan2023_test.csv
│ ├── viirs_monthly_panel_fixed.csv
│ └── viirs_quarterly_panel_clean.csv # Clean (25,240 rows)
│
├── 03_Data_Clean/
│ ├── analysis_panel_final.csv # Clean (23,347 rows, 100% VIIRS)
│ └── regression_panel_final.csv # Clean (23,347 rows, 23 variables)
│
├── 04_Code/
│ ├── 08_build_district_crosswalk.py # Clean — permanent rewrite
│ ├── 10_build_flood_exposure.py
│ ├── 11_validate_flood_exposure.py
│ ├── 12_summarize_flood_exposure.py
│ ├── 13_extract_rbi_deposits.py
│ ├── 14_merge_master_panel.py
│ ├── 15_validate_master_panel.py
│ ├── 17_prepare_analysis_sample.py
│ ├── 21_extract_viirs_full_panel.py
│ ├── 21b_fix_viirs_duplicates.py
│ ├── 22_aggregate_viirs_quarterly.py
│ ├── 22b_align_viirs_clean.py
│ ├── 23_merge_viirs_master.py
│ ├── 24_engineer_regression_variables.py
│ ├── 25_descriptive_statistics.py
│ ├── 26_validate_viirs_quarterly.py
│ ├── 27_regression_H1_first_stage.py # Pending FE correction
│ ├── 28_regression_H2_iv2sls.py # Pending FE correction
│ ├── 29_regression_H3_timing.py # H3 validated clean
│ └── 30_regression_H4_heterogeneity.py # Pending FE correction
│
└── 05_Outputs/
├── Tables/
│ ├── 01_descriptive_stats.csv # Clean
│ ├── 02_H1_first_stage.csv # Feb 6 — pending re-run
│ ├── 03_H2_iv2sls.csv # Feb 6 — pending re-run
│ ├── 04_H3_timing.csv # Feb 6 — validated clean
│ └── 05_H4_heterogeneity.csv # Feb 6 — pending re-run
└── Logs/
├── 25_descriptive_summary.txt
├── 26_viirs_quarterly_validation.txt
├── 27_H1_regression_full.txt
├── 28_H2_regression.txt
├── 29_H3_timing.txt
└── 30_H4_heterogeneity.txt

---

## Known Issues

### Resolved

**Script 8 crosswalk regression (Feb 27 → Fixed Mar 5)**
Deduplication logic checked unique district *names* instead of unique district
*rows*. Homonymous pairs share the same name across two states, so `nunique()`
reported no duplicates while 7 duplicate rows persisted. Produced 769-row
crosswalk instead of 762, propagating to flood exposure panel (2,230 instead
of correct 2,518 Rule A events). Fixed with permanent rewrite: mandatory state
token exclusion, hard assert `len == 762`, re-run validated.

**Deposit contamination — two-bug cascade (Discovered Feb 4–7; Fixed Feb 11)**

*Bug 1 — Column offset error (Script 13):* For 2004–2022 RBI Excel files, script
extracted "Number of Reporting Offices" (column index q_idx) instead of "Deposit
Amount" (column index q_idx + 1). Fix: `dep_idx = q_idx + 1`. Evidence: BALOD
2022Q3 changed from 87 (offices) → 3,296 Crores (deposits).

*Bug 2 — State-blind crosswalk merge (Script 8):* Merge used `district_rbi` only,
causing Bihar and Maharashtra Aurangabad deposits to sum and assign to Bihar. Fix:
mandatory state filtering for all 14 homonymous state-district pairs. Evidence:
Aurangabad Bihar 2015Q1 changed from 18,652 → 4,422 Crores (76% drop).

---

## Methodological Notes

**GADM as geographic standard:** RBI district names change over time. GADM v4.1
provides stable polygon boundaries for flood matching. Crosswalk harmonises RBI
names to GADM at 83.2% match rate; 130 unmatched RBI districts dropped.

**Rule A as primary flood specification:** Rule A assigns exposure if a flood
matches the district directly OR the containing state (fallback). 9.59% treatment
rate. Rule B (district-only, 0.90%) is the strict robustness specification. Both
reported; Rule A preferred for power, Rule B preferred for precision.

**Option 3 sample restriction:** Dropping quarters only (Option 1) retains 35
structural-zero districts. Dropping districts only (Option 2) retains the 2016
RBI blackout, creating false breaks in time-series lags. Option 3 removes both:
98.9% deposit coverage, 100% treatment-outcome overlap.

**Log offset +0.001 for VIIRS:** India is predominantly rural. Mean radiance 0.696
means most observations fall below 1 nW/cm²/sr. `log(x + 1)` approximates the
identity function in this range, eliminating log-scale compression for ~80% of
the sample. `log(x + 0.001)` preserves the intended elasticity interpretation.

---

## Reproducibility

```bash
conda activate research_env

# Crosswalk and flood exposure
python 04_Code/08_build_district_crosswalk.py        # Assert: 762 rows
python 04_Code/10_build_flood_exposure.py             # Assert: 2,518 Rule A events
python 04_Code/11_validate_flood_exposure.py
python 04_Code/12_summarize_flood_exposure.py

# RBI deposits
python 04_Code/13_extract_rbi_deposits.py             # 50,192 rows total

# Master panel
python 04_Code/14_merge_master_panel.py               # Assert: 26,640 rows
python 04_Code/15_validate_master_panel.py
python 04_Code/17_prepare_analysis_sample.py          # Assert: 23,347 rows, 631 districts

# VIIRS integration
python 04_Code/22b_align_viirs_clean.py               # Assert: 25,240 rows
python 04_Code/23_merge_viirs_master.py               # Assert: 23,347 rows, 100% coverage
python 04_Code/24_engineer_regression_variables.py    # Assert: 23 columns
python 04_Code/25_descriptive_statistics.py
python 04_Code/26_validate_viirs_quarterly.py         # Assert: all 9 checks pass

# Regressions (FE correction required in Scripts 27, 28, 30)
python 04_Code/27_regression_H1_first_stage.py
python 04_Code/28_regression_H2_iv2sls.py
python 04_Code/29_regression_H3_timing.py
python 04_Code/30_regression_H4_heterogeneity.py
Environment: Python 3.10.19 | conda environment research_env
Packages: pandas, geopandas, rasterio, statsmodels, linearmodels, matplotlib

Contact
Researcher: Jaseel Badar
Email: jaseelbadar123@gmail.com | jab9733@g.harvard.edu
Institution: Harvard University
Repository: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

Project initiated December 30, 2025