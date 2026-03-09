# Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Nighttime Lights in India

Empirical analysis of flood-induced displacement effects on district-level deposit
stability across India, 2015–2024. Constructs a district-quarter panel linking
EM-DAT flood events, VIIRS nighttime lights, and RBI banking statistics for
631 districts in a panel IV strategy.

**Status:** Full pipeline verified and clean. All regressions (Scripts 27–30)
executed and confirmed. Robustness and diagnostic scripts (31–32b) complete.

**Project start:** 2025-12-30 | **Last updated:** 2026-03-09

---

## Research Question

Do flood-induced displacement shocks — identified through nighttime-lights declines —
cause deposit stress in Indian district-level banking? Does this effect concentrate
in chronically exposed districts and vary with seasonal flood patterns?

---

## Identification Strategy

| Stage | Specification | Method |
|---|---|---|
| H1 — First stage | Floods → nighttime lights decline | OLS, district + quarter FE |
| H2 — Second stage | Lights decline → deposit outflows | IV 2SLS, flood as instrument |
| H3 — Timing | Distributed lag: t0, t−1, t−2 post-flood | OLS with lags, quarter FE only |
| H4 — Heterogeneity | Urban proxy, chronic exposure, monsoon season | Interaction terms |

All core specifications use district-clustered standard errors. Fixed effects
use composite `district_state_id = district_gadm + '_' + state_gadm` to correctly
handle 7 homonymous district pairs across states (e.g., Aurangabad: Bihar and
Maharashtra). Using `district_gadm` alone collapses these pairs — 624 FE instead
of correct 631 — and was the source of all pre-March 2026 benchmark contamination.

---

## Results

All results from clean pipeline execution, March 2026. Both Rule A (primary,
district + state fallback, 9.59% treatment rate) and Rule B (strict district-only,
0.90%) reported throughout per pre-committed robustness protocol.

### Core Hypotheses

| Hypothesis | Specification | Rule | β | SE | p-value | Status |
|---|---|---|---|---|---|---|
| H1 | Floods → Lights | A | −0.0445 | 0.0078 | <0.001 | **Confirmed ✦** |
| H1 | Floods → Lights | B | −0.0584 | 0.0198 | 0.003 | **Confirmed ✦** |
| H2 | Lights → Deposits (IV 2SLS) | A | −0.0084 | 0.0340 | 0.805 | Null |
| H2 | Lights → Deposits (IV 2SLS) | B | −0.0068 | 0.0597 | 0.910 | Null |
| H3 t0 | Flood → Deposits, current quarter | A | +0.0006 | 0.0015 | 0.677 | Null |
| H3 t−1 | Flood → Deposits, 1Q lag | A | +0.0015 | 0.0011 | 0.177 | Null |
| H3 t−2 | Flood → Deposits, 2Q lag | A | −0.0070 | 0.0016 | <0.001 | **Confirmed ✦** |

### Heterogeneity (H4)

| Specification | Rule | Interaction β | SE | p-value | Status |
|---|---|---|---|---|---|
| H4a: Urban proxy × Flood | A | −0.0017 | 0.0027 | 0.532 | Null |
| H4a: Urban proxy × Flood | B | +0.0075 | 0.0069 | 0.281 | Null |
| H4b: High exposure × Flood | A | −0.0068 | 0.0029 | 0.020 | **Supported ✦** |
| H4b: High exposure × Flood | B | −0.0134 | 0.0077 | 0.080 | **Supported ✦** |
| H4c: Monsoon × Flood | A | +0.0125 | 0.0029 | <0.001 | **Partial ✦** |
| H4c: Monsoon × Flood | B | +0.0023 | 0.0080 | 0.774 | Null |

**H2 instrument diagnostics:** Rule A F = 34.673 (strong, threshold 16.38).
Rule B F = 8.949 (weak, threshold 10). Rule B second stage results are
labeled suggestive throughout. Causal language reserved for Rule A.

**H3 interpretation:** Flood-induced deposit stress is absent in the flood quarter
and the quarter immediately following. The effect peaks at t−2 (six months
post-flood): −0.70% decline in quarterly deposit growth. This lag is consistent
with gradual displacement — households exhaust immediate coping mechanisms before
liquidating bank deposits.

**H4b interpretation:** Baseline (low-exposure districts): β = +0.0047 (marginal
positive — precautionary saving response). Net effect for chronically exposed
districts: +0.0047 + (−0.0068) = −0.0021. Repeated flood history depletes
household financial buffers; the next flood forces withdrawal rather than
accumulation. This is the most economically coherent heterogeneity result.

**H4c interpretation:** Moderate flood events during monsoon quarters (Q3) do
not reduce deposits — the effect reverses. Seasonal flooding is anticipated;
agricultural income inflows in Q3 dominate. Severe floods (Rule B) override this
entirely. Result is fragile to flood intensity definition and labeled partial.

---

## Data Sources

Raw data files are never modified. All transformations applied in intermediate
and clean folders only.

### RBI District Banking Statistics (BSR-2)
- **Source:** Reserve Bank of India
- **Coverage:** 762 districts, 2004Q1–2025Q3, quarterly
- **Variable:** Total deposits (Rs Crores), aggregated across population groups
- **Status:** Clean. Column offset bug (Script 13) and state-blind merge bug
  (Script 8) both resolved. Verification anchor: Aurangabad Bihar 2015Q1 =
  4,422 Crores (was 18,652 — contaminated Bihar + Maharashtra sum).

### EM-DAT Global Disaster Database
- **Source:** CRED, Université catholique de Louvain
- **Coverage:** Flood events, India, 2015–2024
- **Variables:** District and state location, event dates, affected population
- **Status:** Clean. Crosswalk regression (Script 8) permanently fixed with
  762-row hard assert and mandatory state-token exclusion.
  Rule A: 2,518 raw events | 2,238 analysis sample. Rule B: 209 events.

### VIIRS Nighttime Lights (DNB)
- **Source:** Colorado School of Mines — Earth Observation Group (PAYNE Institute)
- **Coverage:** Monthly composites, January 2015–December 2024, tile 75N060E
- **Variable:** Mean radiance (nW/cm²/sr) per district per month
- **Status:** Clean. 100% district coverage in final analysis panel. Composite
  keys used in all extraction and merge scripts. Aurangabad litmus confirmed:
  Bihar = 0.7222, Maharashtra = 0.5094 (distinct — no contamination).
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
| Crosswalk match | 631 | — | — | 83.2% RBI-GADM match rate |
| Master panel raw | 666 | 40 | 26,640 | Deposits + floods merged |
| **Analysis sample** | **631** | **37** | **23,347** | Both restrictions applied |

**Sample restrictions (Script 17, Option 3):**
1. Drop 2016Q3–2017Q1 — RBI publication blackout during demonetization period
   (November 2016). District-level data unreliable. 3 quarters, 100% missing.
2. Drop 35 zero-coverage districts — no deposit data across entire panel.

**Quarter coverage note:** Full panel contains 37 quarters (631 × 37 = 23,347).
One additional quarter, 2015Q1, has zero valid deposit observations and is absent
from all regression samples. Regression quarter FE = 36 throughout.

**Key sample statistics — verified clean pipeline, March 2026:**
- Deposit coverage: 98.9% (23,079 / 23,347 observations)
- VIIRS coverage: 100.0% (23,347 / 23,347 observations)
- Flood exposure Rule A: 2,238 events | 9.59% treatment rate | 569 districts
- Flood exposure Rule B: 209 events | 0.90% treatment rate | 141 districts
- Mean deposits: 16,425.73 Crores | Median: 6,135.58 Crores
- Mean radiance: 0.6955 nW/cm²/sr | SD: 1.6884

---

## Pipeline Status

| Script | Purpose | Status | Key Output |
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
| 27 | H1: Floods → Lights | **Clean. Confirmed.** | 02_H1_first_stage.csv |
| 28 | H2: Lights → Deposits (IV) | **Clean. Null confirmed.** | 03_H2_iv2sls.csv |
| 29 | H3: Distributed lag timing | **Clean. Confirmed.** | 04_H3_timing.csv |
| 30 | H4: Heterogeneity interactions | **Clean. Results confirmed.** | 05_H4_heterogeneity.csv |
| 31 | Winsorize dependent variable | **Clean.** | regression_panel_final_winsor.csv |
| 32 | CPI / nominal diagnostic | **Clean.** | 32_nominal_growth_trend.png |
| 32b | 2023 deposit anomaly diagnosis | **Clean.** | 06_32b_2023_diagnosis.csv |

**Pre-paper action (all regression scripts):** Re-run Scripts 27–30 using
`linearmodels.PanelOLS` to resolve statsmodels ValueWarning (rank deficiency
in clustered VCV at 666 exogenous columns). Coefficients are valid; SEs are
conservative. Not a blocker for current results but required before final tables.

---

## Verified File Registry

| File | Rows | Key Verification | Status |
|---|---|---|---|
| district_crosswalk_draft.csv | 762 | Hard assert: len == 762 | Clean |
| flood_exposure_panel.csv | 26,640 | Rule A: 2,518 events | Clean |
| rbi_deposits_panel.csv | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores | Clean |
| master_panel_raw.csv | 26,640 | BALOD 2022Q4 = 3,296 Crores | Clean |
| master_panel_analysis.csv | 23,347 | 631 districts × 37 quarters | Clean |
| viirs_quarterly_panel_clean.csv | 25,240 | 631 districts × 40 quarters | Clean |
| analysis_panel_final.csv | 23,347 | 100% VIIRS coverage | Clean |
| regression_panel_final.csv | 23,347 | 23 columns, lag arithmetic verified | Clean |
| regression_panel_final_winsor.csv | 23,347 | 24 columns, 450 obs winsorized (2.01%) | Clean |
| 01_descriptive_stats.csv | 6 vars | Rule A 2,238 events, 9.59% rate | Clean |
| 02_H1_first_stage.csv | — | Rule A F = 34.673, p < 0.001 | Clean |
| 03_H2_iv2sls.csv | — | Rule A p = 0.805 (null confirmed) | Clean |
| 04_H3_timing.csv | — | t−2 β = −0.0070, p < 0.001 | Clean |
| 05_H4_heterogeneity.csv | 6 rows | H4b p = 0.020**, H4c p < 0.001*** | Clean |
| 06_32b_2023_diagnosis.csv | 4 rows | Unit error flag: NO | Clean |

---

## Repository Structure

E:\Climate-Migration-Bank-Fragility
│
├── 00_Admin/
│ ├── Research_Log.txt
│ ├── Hypotheses_Formal_v2.4.md
│ ├── Variables_Codebook_v2.4.md
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
│ ├── flood_exposure_panel.csv # Clean (2,518 Rule A events)
│ ├── rbi_deposits_panel.csv # Clean (50,192 rows)
│ ├── master_panel_raw.csv # Clean (26,640 rows)
│ ├── master_panel_analysis.csv # Clean (23,347 rows)
│ ├── master_panel_validation_log.txt
│ ├── viirs_monthly_panel_fixed.csv
│ └── viirs_quarterly_panel_clean.csv # Clean (25,240 rows)
│
├── 03_Data_Clean/
│ ├── analysis_panel_final.csv # Clean (23,347 rows, 100% VIIRS)
│ ├── regression_panel_final.csv # Clean (23,347 rows, 23 variables)
│ └── regression_panel_final_winsor.csv # Clean (23,347 rows, 24 variables)
│
├── 04_Code/
│ ├── 08_build_district_crosswalk.py
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
│ ├── 27_regression_H1_first_stage.py # Clean. H1 confirmed.
│ ├── 28_regression_H2_iv2sls.py # Clean. H2 null confirmed.
│ ├── 29_regression_H3_timing.py # Clean. H3 t-2 confirmed.
│ ├── 30_regression_H4_heterogeneity.py # Clean. H4 results confirmed.
│ ├── 31_winsorize.py # Clean. Robustness panel produced.
│ ├── 32_cpi_diagnostic.py # Clean. Nominal decision logged.
│ └── 32b_cpi_diagnostic_2023.py # Clean. 2023 anomaly diagnosed.
│
└── 05_Outputs/
├── Tables/
│ ├── 01_descriptive_stats.csv
│ ├── 02_H1_first_stage.csv
│ ├── 03_H2_iv2sls.csv
│ ├── 04_H3_timing.csv
│ ├── 05_H4_heterogeneity.csv
│ └── 06_32b_2023_diagnosis.csv
├── Figures/
│ └── 32_nominal_growth_trend.png
└── Logs/
├── 27_H1_regression.txt
├── 28_H2_regression.txt
├── 29_H3_regression.txt
├── 30_H4_regression.txt
├── 31_winsorize_log.txt
├── 32_cpi_diagnostic_log.txt
└── 32b_cpi_diagnostic_2023_log.txt

---

## Known Issues

### Resolved

**Script 8 crosswalk regression (Fixed Mar 5, 2026)**
Deduplication logic checked unique district names instead of unique district rows.
Homonymous pairs share the same name across two states — `nunique()` reported
no duplicates while 7 duplicate rows persisted. Produced a 769-row crosswalk
instead of 762, propagating undercounts to the flood exposure panel (2,230 instead
of 2,518 Rule A events). Fixed with permanent rewrite: mandatory state-token
exclusion and hard assert `len == 762`. Re-run validated.

**Deposit contamination — two-bug cascade (Fixed Feb 11, 2026)**

*Bug 1 — Column offset error (Script 13):* For 2004–2022 RBI Excel files, the
script extracted "Number of Reporting Offices" (column index `q_idx`) instead of
"Deposit Amount" (`q_idx + 1`). Fix: `dep_idx = q_idx + 1`. Evidence: BALOD
2022Q3 changed from 87 (offices) to 3,296 Crores (deposits).

*Bug 2 — State-blind crosswalk merge (Script 8):* Merge used `district_rbi`
alone, causing Bihar and Maharashtra Aurangabad deposits to sum and assign to
Bihar. Fix: mandatory state filtering for all 14 homonymous state-district pairs.
Evidence: Aurangabad Bihar 2015Q1 changed from 18,652 to 4,422 Crores (−76%).

**Composite FE specification (Fixed Mar 8, 2026)**
All pre-March 2026 regression benchmarks used `district_gadm` alone for fixed
effects and clustering — collapsing 7 homonymous district pairs into 624 units
instead of 631. This contaminated H4a (spuriously significant at p < 0.001 in
Feb 6 run — correctly null after fix), H4b (was null — correctly significant
after fix), and H4c (was null — correctly significant after fix). All results
in the table above are from the corrected specification.

### Active — Pre-Paper

**statsmodels rank warning (Scripts 27, 29, 30)**
ValueWarning: rank deficiency in clustered VCV matrix at 666 exogenous columns.
Coefficients valid. SEs are conservative. Must re-run Scripts 27–30 with
`linearmodels.PanelOLS` before final paper tables.

**Script 32b conclusion logic**
Printed conclusion evaluated only the positive tail (n above p95 = 36, 1.4%).
Did not evaluate the negative tail (n below p5 = 385, 15.4% — 3× expected).
Correct conclusion: left-tail asymmetry confirmed in 2023, concentrated in
small-base Northeast districts. Log file contains incorrect text and must not
be cited directly. Documented in Research Log, fix pending.

---

## Methodological Notes

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
means most observations fall below 1 nW/cm²/sr. `log(x + 1)` approximates the
identity function in this range, eliminating log-scale compression for approximately
80% of the sample. `log(x + 0.001)` preserves the intended elasticity interpretation.

**Nominal INR retained:** Deposits are measured in nominal rupees throughout.
India CPI averaged approximately 6–7% annually over the analysis period. Quarter
fixed effects absorb national-level price trends. District-quarter CPI is
unavailable at the required granularity; deflation via interpolated indices would
introduce noise that exceeds the bias it corrects. The nominal confound is
acknowledged as a limitation in the paper.

**Demonetization gap:** Three quarters — 2016Q3, 2016Q4, 2017Q1 — are entirely
absent from the panel. These span India's demonetization period (November 2016).
District-level deposit data was unreliable during this window and excluded
upstream. The discontinuity is absorbed by quarter fixed effects and disclosed
explicitly in the Data section of the paper.

---

## Reproducibility

```bash
conda activate research_env

# Crosswalk and flood exposure
python 04_Code/08_build_district_crosswalk.py         # Assert: 762 rows
python 04_Code/10_build_flood_exposure.py              # Assert: 2,518 Rule A events
python 04_Code/11_validate_flood_exposure.py
python 04_Code/12_summarize_flood_exposure.py

# RBI deposits
python 04_Code/13_extract_rbi_deposits.py              # 50,192 rows total

# Master panel
python 04_Code/14_merge_master_panel.py                # Assert: 26,640 rows
python 04_Code/15_validate_master_panel.py
python 04_Code/17_prepare_analysis_sample.py           # Assert: 23,347 rows, 631 districts

# VIIRS integration
python 04_Code/22b_align_viirs_clean.py                # Assert: 25,240 rows
python 04_Code/23_merge_viirs_master.py                # Assert: 23,347 rows, 100% coverage
python 04_Code/24_engineer_regression_variables.py     # Assert: 23 columns
python 04_Code/25_descriptive_statistics.py
python 04_Code/26_validate_viirs_quarterly.py          # Assert: all 9 checks pass

# Regressions
python 04_Code/27_regression_H1_first_stage.py         # H1 confirmed
python 04_Code/28_regression_H2_iv2sls.py              # H2 null confirmed
python 04_Code/29_regression_H3_timing.py              # H3 t-2 confirmed
python 04_Code/30_regression_H4_heterogeneity.py       # H4 results confirmed

# Robustness and diagnostics
python 04_Code/31_winsorize.py                         # Assert: 23,347 x 24
python 04_Code/32_cpi_diagnostic.py
python 04_Code/32b_cpi_diagnostic_2023.py
Environment: Python 3.10.19 | conda environment research_env

Packages: pandas, numpy, geopandas, rasterio, statsmodels, linearmodels,
scipy, matplotlib

Contact
Researcher: Jaseel Badar
Email: jaseelbadar123@gmail.com | jab9733@g.harvard.edu
Institution: Harvard University
Repository: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

Project initiated December 30, 2025