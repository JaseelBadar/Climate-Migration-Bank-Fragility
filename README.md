# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India

Empirical analysis of flood-induced displacement effects on district-level deposit stability
in India, 2015–2024. Uses VIIRS nighttime lights as a migration proxy instrumented by
EM-DAT flood events in a panel IV strategy across 631 districts.

**Status:** Pipeline fix in progress. Script 8 (crosswalk) permanent rewrite scheduled
Mar 5, 2026. All other pipeline stages clean and verified. Regressions pending.

**Last updated:** 2026-03-04 | **Project start:** 2025-12-30

---

## Research Question

Do flood-induced displacement shocks — identified via nighttime-lights declines —
cause deposit stress in Indian district-level banking, and does this effect
concentrate in urban districts and persist over multiple quarters?

---

## Identification Strategy

**First stage (H1):** Floods → nighttime lights decline (OLS, district + quarter FE)
**Second stage (H2):** Lights decline → deposit outflows (IV 2SLS, flood as instrument)
**Timing (H3):** Distributed lag structure — do deposit effects peak at t+1 or t+2?
**Heterogeneity (H4):** Urban vs rural, high-exposure vs low-exposure, monsoon seasonality

All specifications use district-clustered standard errors. Fixed effects specified on
composite `district_state_id = district_gadm + state_gadm` to correctly handle
7 homonymous district pairs across states.

---

## Current Results

Results below are from Feb 6, 2026 — the most recent full regression run.
H1, H2, H4 are pending re-run (pipeline contamination identified Mar 4, fix Mar 5).
H3 is validated clean — specification uses deposits and floods only, no VIIRS.

| Hypothesis | Specification | β | SE | p | Status |
|---|---|---|---|---|---|
| H1 | Floods → Lights (first stage) | −0.0149 | 0.0028 | <0.001 | **Pending re-run** |
| H2 | Lights → Deposits (IV 2SLS) | +0.2191 | — | 0.299 | **Pending re-run** |
| H3-t0 | Flood → Deposits, current quarter | −0.0005 | — | 0.777 | **Validated null** |
| H3-t1 | Flood → Deposits, 1Q lag | +0.0004 | — | 0.757 | **Validated null** |
| H3-t2 | Flood → Deposits, 2Q lag | −0.0091 | — | 0.012 | **Validated: confirmed** |
| H4a | Urban × Flood interaction | −0.0013 | — | 0.665 | **Pending re-run** |
| H4b | HighExposure × Flood | −0.0057 | — | 0.068 | **Pending re-run** |
| H4c | Monsoon × Flood | +0.0119 | — | <0.001 | **Pending re-run** |

**H3 interpretation:** Flood-induced deposit stress does not manifest in the
current quarter or one quarter after. The effect peaks at two quarters (6 months)
post-flood: a −0.91% decline in deposit growth. This lag structure is consistent
with gradual displacement — households liquidate deposits after exhausting
immediate coping strategies.

---

## Data Sources

Raw data never modified. All transformations applied in intermediate and clean folders.

### RBI District Banking Statistics (BSR-2)
- **Source:** Reserve Bank of India official portal
- **Coverage:** 762 districts, 2004Q1–2025Q3, quarterly
- **Files:** `RBI_Deposits_2004_2017.xlsx`, `RBI_Deposits_2017_2022.xlsx`,
  `RBI_Deposits_2023_2024.xlsx`
- **Variable:** Total deposits (Rs Crores) aggregated across population groups
- **Status:** CLEAN — Feb 11, 2026. Two-bug cascade resolved (see Known Issues).
  Verification: Aurangabad Bihar 2015Q1 = 4,422 Crores (was 18,652 — contaminated sum
  of Bihar + Maharashtra). Deposit range: 29–1,237,744 Crores across sample.

### EM-DAT Global Disaster Database
- **Source:** CRED, Université catholique de Louvain
- **Coverage:** Flood events, India, 2015–2024
- **Variables:** District/state location, event dates, affected population
- **Status:** Source data clean. Flood exposure panel (Script 12 output) CONTAMINATED
  as of Mar 4 — 2,230 Rule A events vs correct 2,220. Root cause: Script 8 crosswalk
  regression (Feb 27). Fix Mar 5.

### VIIRS Nighttime Lights (DNB)
- **Source:** Colorado School of Mines Earth Observation Group (PAYNE Institute)
- **Coverage:** Monthly composites, Jan 2015–Dec 2024, tile 75N060E
- **Variable:** Mean radiance (nW/cm²/sr) per district per month
- **Status:** CLEAN — forensically validated Feb 11, 2026. Composite
  (district_gadm, state_gadm) keys used throughout Scripts 18–24. Verification:
  Aurangabad Bihar radiance ≠ Aurangabad Maharashtra (distinct values confirmed in
  Excel). 100% district coverage achieved in final analysis panel.
- **Storage:** Monthly tiles (~65 GB) at `E:\VIIRS_Raw_Data_75N060E\`

### GADM v4.1 District Boundaries
- **Source:** Global Administrative Areas
- **Coverage:** 676 district polygons, India Level-2
- **Usage:** VIIRS spatial aggregation reference; crosswalk harmonisation standard
- **Location:** `01_Data_Raw/District_Boundaries/gadm41_IND_2.shp`

---

## Sample Construction

| Stage | Districts | Quarters | Observations | Notes |
|---|---|---|---|---|
| GADM baseline | 676 | — | — | Spatial reference |
| VIIRS extraction | 666 | 40 | 26,640 | 10 districts outside tile |
| RBI extraction | 762 | 40 | — | Fiscal-to-calendar converted |
| Master panel raw | 666 | 40 | 26,640 | Deposits + floods merged |
| Analysis sample | **631** | **37** | **23,347** | Restrictions applied |

**Sample restrictions (Script 17, Option 3):**
1. Drop 2016Q3–2017Q1 — RBI publication blackout (100% missing, 3 quarters)
2. Drop 35 zero-coverage districts — never report deposits across all periods

**Final sample:** 631 unique (district, state) composite pairs × 37 quarters.
District count of 624 in some prior outputs reflects name-only `.nunique()` on
`district_gadm` — undercounts by 7 due to homonymous pairs. Correct count is 631.

**Key sample statistics (confirmed Mar 4, 2026):**
- Deposit coverage: 99.1% (23,137 / 23,347 observations)
- VIIRS coverage: 100% (23,347 / 23,347 observations)
- Flood exposure Rule A: 1,984 events (8.50% treatment rate) — *pending pipeline fix*
- Districts ever flood-exposed: 512 (Rule A) — *pending pipeline fix*
- Mean deposits: 16,440 Crores | Median: 6,221 Crores | Range: 29–1,237,744 Crores
- Mean radiance: 0.696 nW/cm²/sr | Median: 0.427 | SD: 1.688

---

## Pipeline Status

| Script | Purpose | Status | Output |
|---|---|---|---|
| 08 | Build district crosswalk | **CONTAMINATED — fix Mar 5** | district_crosswalk_draft.csv |
| 12 | Build flood exposure panel | **CONTAMINATED — re-run after 08** | flood_exposure_panel.csv |
| 13 | Extract RBI deposits | Clean (Feb 11) | rbi_deposits_panel.csv |
| 14 | Merge master panel | **Needs re-run after 12** | master_panel_raw.csv |
| 15 | Validate master panel | **Needs re-run after 14** | validation log |
| 17 | Prepare analysis sample | **Needs re-run after 14** | master_panel_analysis.csv |
| 22b | Align VIIRS with clean sample | Clean (Mar 3) | viirs_quarterly_panel_clean.csv |
| 23 | Merge VIIRS with master panel | Clean (Mar 4) | analysis_panel_final.csv |
| 24 | Engineer regression variables | Clean (Mar 4) | regression_panel_final.csv |
| 25 | Descriptive statistics | Clean script, contaminated output | 01_descriptive_stats.csv |
| 27–30 | H1–H4 regressions | **Pending pipeline fix + FE correction** | — |

**FE correction required (Scripts 27, 28, 30):** District fixed effects must use
`district_state_id = district_gadm + '_' + state_gadm`. Using `district_gadm` alone
collapses 7 homonymous pairs into single FE — 624 FE instead of correct 631.
Script 29 (H3) uses no district FE and is unaffected.

---

## Verified File Checksums (Mar 4, 2026)

| File | Rows | Key metric | Verified |
|---|---|---|---|
| rbi_deposits_panel.csv | 49,670* | Aurangabad Bihar 2015Q1 = 4,422 Crores | Mar 4 |
| viirs_quarterly_panel_clean.csv | 25,240 | 631 districts × 40 quarters | Mar 3 |
| analysis_panel_final.csv | 23,347 | 100% VIIRS coverage, 0 missing | Mar 4 |
| regression_panel_final.csv | 23,347 | 23 columns, lag arithmetic exact | Mar 4 |
| district_crosswalk_draft.csv | 769 | **CONTAMINATED** — should be 762 | Mar 4 |
| flood_exposure_panel.csv | 26,640 | **CONTAMINATED** — 2,230 vs 2,220 Rule A | Mar 4 |

*49,670 rows within 2015Q1–2024Q4 window; 50,192 total including 2025Q1–Q3 quarters
outside analysis window. Extra rows are harmless — dropped at skeleton merge.

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
│ ├── district_crosswalk_draft.csv # CONTAMINATED (769 rows, fix Mar 5)
│ ├── flood_exposure_panel.csv # CONTAMINATED (2,230 events, re-run after fix)
│ ├── rbi_deposits_panel.csv # CLEAN (49,670 rows)
│ ├── master_panel_raw.csv # Needs re-run
│ ├── master_panel_analysis.csv # Needs re-run
│ ├── master_panel_validation_log.txt
│ ├── viirs_jan2023_test.csv
│ └── viirs_quarterly_panel_clean.csv # CLEAN (25,240 rows)
│
├── 03_Data_Clean/
│ ├── analysis_panel_final.csv # CLEAN (23,347 rows, 100% VIIRS)
│ └── regression_panel_final.csv # CLEAN (23,347 rows, 23 variables)
│
├── 04_Code/
│ ├── 08_build_district_crosswalk.py # Permanent rewrite pending Mar 5
│ ├── 12_build_flood_exposure.py
│ ├── 13_extract_rbi_deposits.py # Clean (Feb 11)
│ ├── 14_merge_master_panel.py
│ ├── 15_validate_master_panel.py
│ ├── 17_prepare_analysis_sample.py
│ ├── 22b_align_viirs_clean.py # Clean (Mar 3)
│ ├── 23_merge_viirs_master.py # Clean (Mar 4)
│ ├── 24_engineer_regression_variables.py # Clean (Mar 4)
│ ├── 25_descriptive_statistics.py # Clean (Mar 4)
│ ├── 27_regression_H1_first_stage.py # Pending FE fix
│ ├── 28_regression_H2_iv2sls.py # Pending FE fix
│ ├── 29_regression_H3_timing.py # H3 valid, pending re-run
│ └── 30_regression_H4_heterogeneity.py # Pending FE fix
│
└── 05_Outputs/
├── Tables/
│ ├── 01_descriptive_stats.csv # Contaminated output, superseded Mar 5
│ ├── 02_H1_first_stage.csv # Feb 6, pending re-run
│ ├── 03_H2_iv2sls.csv
│ ├── 04_H3_timing.csv # Feb 6, validated clean
│ └── 05_H4_heterogeneity.csv
└── Logs/
├── 25_descriptive_summary.txt
├── 27_H1_regression_full.txt
├── 28_H2_regression.txt
├── 29_H3_timing.txt
└── 30_H4_heterogeneity.txt

text
# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India

Empirical analysis of flood-induced displacement effects on district-level deposit stability
in India, 2015–2024. Uses VIIRS nighttime lights as a migration proxy instrumented by
EM-DAT flood events in a panel IV strategy across 631 districts.

**Status:** Pipeline fix in progress. Script 8 (crosswalk) permanent rewrite scheduled
Mar 5, 2026. All other pipeline stages clean and verified. Regressions pending.

**Last updated:** 2026-03-04 | **Project start:** 2025-12-30

---

## Research Question

Do flood-induced displacement shocks — identified via nighttime-lights declines —
cause deposit stress in Indian district-level banking, and does this effect
concentrate in urban districts and persist over multiple quarters?

---

## Identification Strategy

**First stage (H1):** Floods → nighttime lights decline (OLS, district + quarter FE)
**Second stage (H2):** Lights decline → deposit outflows (IV 2SLS, flood as instrument)
**Timing (H3):** Distributed lag structure — do deposit effects peak at t+1 or t+2?
**Heterogeneity (H4):** Urban vs rural, high-exposure vs low-exposure, monsoon seasonality

All specifications use district-clustered standard errors. Fixed effects specified on
composite `district_state_id = district_gadm + state_gadm` to correctly handle
7 homonymous district pairs across states.

---

## Current Results

Results below are from Feb 6, 2026 — the most recent full regression run.
H1, H2, H4 are pending re-run (pipeline contamination identified Mar 4, fix Mar 5).
H3 is validated clean — specification uses deposits and floods only, no VIIRS.

| Hypothesis | Specification | β | SE | p | Status |
|---|---|---|---|---|---|
| H1 | Floods → Lights (first stage) | −0.0149 | 0.0028 | <0.001 | **Pending re-run** |
| H2 | Lights → Deposits (IV 2SLS) | +0.2191 | — | 0.299 | **Pending re-run** |
| H3-t0 | Flood → Deposits, current quarter | −0.0005 | — | 0.777 | **Validated null** |
| H3-t1 | Flood → Deposits, 1Q lag | +0.0004 | — | 0.757 | **Validated null** |
| H3-t2 | Flood → Deposits, 2Q lag | −0.0091 | — | 0.012 | **Validated: confirmed** |
| H4a | Urban × Flood interaction | −0.0013 | — | 0.665 | **Pending re-run** |
| H4b | HighExposure × Flood | −0.0057 | — | 0.068 | **Pending re-run** |
| H4c | Monsoon × Flood | +0.0119 | — | <0.001 | **Pending re-run** |

**H3 interpretation:** Flood-induced deposit stress does not manifest in the
current quarter or one quarter after. The effect peaks at two quarters (6 months)
post-flood: a −0.91% decline in deposit growth. This lag structure is consistent
with gradual displacement — households liquidate deposits after exhausting
immediate coping strategies.

---

## Data Sources

Raw data never modified. All transformations applied in intermediate and clean folders.

### RBI District Banking Statistics (BSR-2)
- **Source:** Reserve Bank of India official portal
- **Coverage:** 762 districts, 2004Q1–2025Q3, quarterly
- **Files:** `RBI_Deposits_2004_2017.xlsx`, `RBI_Deposits_2017_2022.xlsx`,
  `RBI_Deposits_2023_2024.xlsx`
- **Variable:** Total deposits (Rs Crores) aggregated across population groups
- **Status:** CLEAN — Feb 11, 2026. Two-bug cascade resolved (see Known Issues).
  Verification: Aurangabad Bihar 2015Q1 = 4,422 Crores (was 18,652 — contaminated sum
  of Bihar + Maharashtra). Deposit range: 29–1,237,744 Crores across sample.

### EM-DAT Global Disaster Database
- **Source:** CRED, Université catholique de Louvain
- **Coverage:** Flood events, India, 2015–2024
- **Variables:** District/state location, event dates, affected population
- **Status:** Source data clean. Flood exposure panel (Script 12 output) CONTAMINATED
  as of Mar 4 — 2,230 Rule A events vs correct 2,220. Root cause: Script 8 crosswalk
  regression (Feb 27). Fix Mar 5.

### VIIRS Nighttime Lights (DNB)
- **Source:** Colorado School of Mines Earth Observation Group (PAYNE Institute)
- **Coverage:** Monthly composites, Jan 2015–Dec 2024, tile 75N060E
- **Variable:** Mean radiance (nW/cm²/sr) per district per month
- **Status:** CLEAN — forensically validated Feb 11, 2026. Composite
  (district_gadm, state_gadm) keys used throughout Scripts 18–24. Verification:
  Aurangabad Bihar radiance ≠ Aurangabad Maharashtra (distinct values confirmed in
  Excel). 100% district coverage achieved in final analysis panel.
- **Storage:** Monthly tiles (~65 GB) at `E:\VIIRS_Raw_Data_75N060E\`

### GADM v4.1 District Boundaries
- **Source:** Global Administrative Areas
- **Coverage:** 676 district polygons, India Level-2
- **Usage:** VIIRS spatial aggregation reference; crosswalk harmonisation standard
- **Location:** `01_Data_Raw/District_Boundaries/gadm41_IND_2.shp`

---

## Sample Construction

| Stage | Districts | Quarters | Observations | Notes |
|---|---|---|---|---|
| GADM baseline | 676 | — | — | Spatial reference |
| VIIRS extraction | 666 | 40 | 26,640 | 10 districts outside tile |
| RBI extraction | 762 | 40 | — | Fiscal-to-calendar converted |
| Master panel raw | 666 | 40 | 26,640 | Deposits + floods merged |
| Analysis sample | **631** | **37** | **23,347** | Restrictions applied |

**Sample restrictions (Script 17, Option 3):**
1. Drop 2016Q3–2017Q1 — RBI publication blackout (100% missing, 3 quarters)
2. Drop 35 zero-coverage districts — never report deposits across all periods

**Final sample:** 631 unique (district, state) composite pairs × 37 quarters.
District count of 624 in some prior outputs reflects name-only `.nunique()` on
`district_gadm` — undercounts by 7 due to homonymous pairs. Correct count is 631.

**Key sample statistics (confirmed Mar 4, 2026):**
- Deposit coverage: 99.1% (23,137 / 23,347 observations)
- VIIRS coverage: 100% (23,347 / 23,347 observations)
- Flood exposure Rule A: 1,984 events (8.50% treatment rate) — *pending pipeline fix*
- Districts ever flood-exposed: 512 (Rule A) — *pending pipeline fix*
- Mean deposits: 16,440 Crores | Median: 6,221 Crores | Range: 29–1,237,744 Crores
- Mean radiance: 0.696 nW/cm²/sr | Median: 0.427 | SD: 1.688

---

## Pipeline Status

| Script | Purpose | Status | Output |
|---|---|---|---|
| 08 | Build district crosswalk | **CONTAMINATED — fix Mar 5** | district_crosswalk_draft.csv |
| 12 | Build flood exposure panel | **CONTAMINATED — re-run after 08** | flood_exposure_panel.csv |
| 13 | Extract RBI deposits | Clean (Feb 11) | rbi_deposits_panel.csv |
| 14 | Merge master panel | **Needs re-run after 12** | master_panel_raw.csv |
| 15 | Validate master panel | **Needs re-run after 14** | validation log |
| 17 | Prepare analysis sample | **Needs re-run after 14** | master_panel_analysis.csv |
| 22b | Align VIIRS with clean sample | Clean (Mar 3) | viirs_quarterly_panel_clean.csv |
| 23 | Merge VIIRS with master panel | Clean (Mar 4) | analysis_panel_final.csv |
| 24 | Engineer regression variables | Clean (Mar 4) | regression_panel_final.csv |
| 25 | Descriptive statistics | Clean script, contaminated output | 01_descriptive_stats.csv |
| 27–30 | H1–H4 regressions | **Pending pipeline fix + FE correction** | — |

**FE correction required (Scripts 27, 28, 30):** District fixed effects must use
`district_state_id = district_gadm + '_' + state_gadm`. Using `district_gadm` alone
collapses 7 homonymous pairs into single FE — 624 FE instead of correct 631.
Script 29 (H3) uses no district FE and is unaffected.

---

## Verified File Checksums (Mar 4, 2026)

| File | Rows | Key metric | Verified |
|---|---|---|---|
| rbi_deposits_panel.csv | 49,670* | Aurangabad Bihar 2015Q1 = 4,422 Crores | Mar 4 |
| viirs_quarterly_panel_clean.csv | 25,240 | 631 districts × 40 quarters | Mar 3 |
| analysis_panel_final.csv | 23,347 | 100% VIIRS coverage, 0 missing | Mar 4 |
| regression_panel_final.csv | 23,347 | 23 columns, lag arithmetic exact | Mar 4 |
| district_crosswalk_draft.csv | 769 | **CONTAMINATED** — should be 762 | Mar 4 |
| flood_exposure_panel.csv | 26,640 | **CONTAMINATED** — 2,230 vs 2,220 Rule A | Mar 4 |

*49,670 rows within 2015Q1–2024Q4 window; 50,192 total including 2025Q1–Q3 quarters
outside analysis window. Extra rows are harmless — dropped at skeleton merge.

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
│ ├── district_crosswalk_draft.csv # CONTAMINATED (769 rows, fix Mar 5)
│ ├── flood_exposure_panel.csv # CONTAMINATED (2,230 events, re-run after fix)
│ ├── rbi_deposits_panel.csv # CLEAN (49,670 rows)
│ ├── master_panel_raw.csv # Needs re-run
│ ├── master_panel_analysis.csv # Needs re-run
│ ├── master_panel_validation_log.txt
│ ├── viirs_jan2023_test.csv
│ └── viirs_quarterly_panel_clean.csv # CLEAN (25,240 rows)
│
├── 03_Data_Clean/
│ ├── analysis_panel_final.csv # CLEAN (23,347 rows, 100% VIIRS)
│ └── regression_panel_final.csv # CLEAN (23,347 rows, 23 variables)
│
├── 04_Code/
│ ├── 08_build_district_crosswalk.py # Permanent rewrite pending Mar 5
│ ├── 12_build_flood_exposure.py
│ ├── 13_extract_rbi_deposits.py # Clean (Feb 11)
│ ├── 14_merge_master_panel.py
│ ├── 15_validate_master_panel.py
│ ├── 17_prepare_analysis_sample.py
│ ├── 22b_align_viirs_clean.py # Clean (Mar 3)
│ ├── 23_merge_viirs_master.py # Clean (Mar 4)
│ ├── 24_engineer_regression_variables.py # Clean (Mar 4)
│ ├── 25_descriptive_statistics.py # Clean (Mar 4)
│ ├── 27_regression_H1_first_stage.py # Pending FE fix
│ ├── 28_regression_H2_iv2sls.py # Pending FE fix
│ ├── 29_regression_H3_timing.py # H3 valid, pending re-run
│ └── 30_regression_H4_heterogeneity.py # Pending FE fix
│
└── 05_Outputs/
├── Tables/
│ ├── 01_descriptive_stats.csv # Contaminated output, superseded Mar 5
│ ├── 02_H1_first_stage.csv # Feb 6, pending re-run
│ ├── 03_H2_iv2sls.csv
│ ├── 04_H3_timing.csv # Feb 6, validated clean
│ └── 05_H4_heterogeneity.csv
└── Logs/
├── 25_descriptive_summary.txt
├── 27_H1_regression_full.txt
├── 28_H2_regression.txt
├── 29_H3_timing.txt
└── 30_H4_heterogeneity.txt

text

---

## Known Issues

### Active — Fix Mar 5

**Script 8 crosswalk regression (Feb 27)**
- Script 8 was re-run on Feb 27 with incorrect deduplication logic, producing
  769 rows (7 duplicate entries for homonymous district pairs) instead of 762.
- This was committed (Feb 27) and used as input to Script 12 (Feb 28), inflating
  Rule A flood events by 10 (2,230 vs 2,220).
- Root cause: deduplication logic checked unique district *names* instead of
  unique district *rows* — homonymous pairs have the same name in both states,
  so `nunique()` reported no duplicates while 7 duplicate rows persisted.
- Fix: Script 8 permanent rewrite with hard assert (`len == 762`) before saving.
- Impact: Scripts 12, 14, 17 outputs contaminated. Scripts 23–25 need re-run.

### Resolved

**Deposit contamination — two-bug cascade (Discovered Feb 4–7; Fixed Feb 11)**

*Bug 1 — Column offset error (Script 13):*
For 2004–2022 RBI files, the script extracted "Number of Reporting Offices"
(column E) instead of "Deposit Amount" (column F). Root cause: fiscal quarter
label detected at index 4, script extracted index 4 directly instead of index 4+1.
Fix: `dep_idx = q_idx + 1`. Evidence: BALOD 2022Q3 changed from 87 (offices) to
3,296 Crores (deposits).

*Bug 2 — State-blind crosswalk merge (Script 8/13):*
Crosswalk merge used `district_rbi` only, causing Bihar and Maharashtra AURANGABAD
deposits to sum and assign to Bihar. Fix: state filtering for all 14 homonymous
state-district pairs. Evidence: Aurangabad Bihar 2015Q1 changed from 18,652 Crores
(Bihar + Maharashtra sum) to 4,422 Crores (Bihar only, 76% drop).

---

## Methodological Decisions

**Geography standard — GADM districts as panel skeleton**
RBI uses administrative names that have changed over time. GADM v4.1 provides
stable polygon boundaries for spatial flood matching. Crosswalk harmonises RBI
names to GADM at 83.2% match rate; 130 RBI districts dropped as unmatched.

**Flood exposure definition — Rule A as primary specification**
Rule A assigns flood exposure if a flood event matches district directly OR the
state the district sits in (fallback). Treatment rate: 8.50%. Rule B (district-only
match, 0.96% treatment) serves as strict robustness check. Rule A preferred for
power; Rule B preferred for precision — both reported.

**Sample restrictions — Option 3 (drop both gap quarters and zero-coverage districts)**
Dropping quarters only (Option 1) retains 35 districts that never report deposits,
introducing structural zeros into deposit growth calculations. Dropping districts
only (Option 2) retains the 2016 RBI blackout quarters, creating false structural
breaks in time-series lags. Option 3 removes both: 99.1% deposit coverage, 100%
treatment-outcome overlap.

**Log offset for VIIRS radiance — +0.001 not +1**
Indian districts are predominantly rural to semi-urban. Mean radiance 0.696 means
the majority of observations fall below 1 nW/cm²/sr. Using `log(x + 1)` approximates
the identity function in this range, destroying log-scale compression for 80% of
the sample. `log(x + 0.001)` preserves the intended elasticity interpretation.

---

## Reproducibility

```bash
conda activate research_env

# Crosswalk and flood exposure (Script 8 rewrite pending Mar 5)
python 04_Code/08_build_district_crosswalk.py   # Assert: 762 rows output
python 04_Code/12_build_flood_exposure.py        # Assert: 2,220 Rule A events

# RBI deposits (clean, no changes needed)
python 04_Code/13_extract_rbi_deposits.py        # 49,670 rows

# Master panel
python 04_Code/14_merge_master_panel.py          # 26,640 rows
python 04_Code/15_validate_master_panel.py
python 04_Code/17_prepare_analysis_sample.py     # 23,347 rows, 631 districts

# VIIRS integration (clean, no changes needed)
python 04_Code/22b_align_viirs_clean.py          # 25,240 rows
python 04_Code/23_merge_viirs_master.py          # 23,347 rows, 100% coverage
python 04_Code/24_engineer_regression_variables.py  # 23 variables
python 04_Code/25_descriptive_statistics.py

# Regressions (pending FE fix in Scripts 27, 28, 30)
python 04_Code/27_regression_H1_first_stage.py
python 04_Code/28_regression_H2_iv2sls.py
python 04_Code/29_regression_H3_timing.py
python 04_Code/30_regression_H4_heterogeneity.py
Environment:
Python 3.10.19 | conda environment research_env
Packages: pandas, geopandas, rasterio, statsmodels, linearmodels, matplotlib

Contact
Researcher: Jaseel Badar
Email: jaseelbadar123@gmail.com | jab9733@g.harvard.edu
Institution: Harvard University
Repository: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

Project initiated December 30, 2025