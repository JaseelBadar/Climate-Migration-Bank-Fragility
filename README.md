# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India

**Empirical analysis of flood-induced migration effects on district-level banking stability in India, 2015-2024.**

**Status:** Phase 4 Complete. All regressions executed (H1-H4). Results: H1 confirmed (floods reduce lights), H2 null (lights-deposits IV), H3 confirmed (1-quarter lagged effect), H4a confirmed (urban vulnerability). Data validated clean (23,347 obs, 23 variables).

**Last updated:** 2026-02-02
**Project start:** 2025-12-30

---

## Research Question

Do climate disasters trigger migration (proxied by nighttime-lights declines) that causes district-level deposit stress and broader banking fragility in India?

---

## Hypotheses & Current Results

| Hypothesis | Specification | Coefficient | p-value | Result |
|------------|---------------|-------------|---------|--------|
| **H1** | Floods → Lights (first stage) | -0.0149 | <0.001 | Confirmed |
| **H2** | Lights → Deposits (IV 2SLS) | 0.0839 | 0.609 | Null |
| **H3-t0** | Floods → Deposits (current) | 0.0006 | 0.699 | Null |
| **H3-t1** | Floods → Deposits (1Q lag) | -0.0062 | <0.001 | Confirmed |
| **H3-t2** | Floods → Deposits (2Q lag) | -0.0053 | 0.280 | Null |
| **H4a** | Urban × Flood | -0.0111 | <0.001 | Confirmed |
| **H4b** | HighExp × Flood | 0.0021 | 0.360 | Null |
| **H4c** | Monsoon × Flood | -0.0018 | 0.511 | Null |

**Key findings:** Floods reduce economic activity (H1) and cause delayed deposit stress (H3, 1-quarter lag). Effect concentrated in urban districts (H4a). Nighttime lights do not mediate deposit effects via IV (H2 null). All specifications use district-clustered standard errors.

---

## Data Sources

Raw data never modified. All transformations in intermediate/clean folders.

### 1. RBI District Banking Data (BSR-2)
- **Source:** Reserve Bank of India official portal
- **Coverage:** 762 districts, 2004-2024, quarterly
- **Files:** RBI_Deposits_2004_2017.xlsx, RBI_Deposits_2017_2022.xlsx, RBI_Deposits_2023_2024.xlsx
- **Variables:** Deposits by population group (Rural/Semi-urban/Urban/Metropolitan)
- **Status:** CLEAN (forensic audit 2026-01-31, contamination false alarm resolved). Structural gap: 2016Q3, 2016Q4, 2017Q1 (RBI publication schedule, not data error)
- **Location:** 01_Data_Raw/RBI_Bank_Data/

### 2. EM-DAT Disaster Database
- **Source:** CRED (Centre for Research on Epidemiology of Disasters)
- **Coverage:** 69 flood events, India, 2015-2024
- **Variables:** District/state location, dates, affected population, deaths, damage
- **Location:** 01_Data_Raw/EMDAT_Disasters/

### 3. VIIRS Nighttime Lights
- **Source:** Colorado School of Mines Earth Observation Group
- **Coverage:** 120 monthly tiles (2015-01 to 2024-12), tile 75N060E (Phase 3d: processed to regression panel)
- **Variables:** Mean radiance (nW/cm²/sr), pixel counts
- **Usage:** Economic activity / migration proxy
- **Location (bulk):** E:\VIIRS_Raw_Data_75N060E\ (~65 GB external storage)
- **Location (test):** 01_Data_Raw/VIIRS_NightLights/ (Jan 2023 validation tile)

### 4. GADM v4.1 District Boundaries
- **Source:** Global Administrative Areas
- **Coverage:** 676 district polygons (India Level-2)
- **Usage:** VIIRS spatial aggregation, crosswalk harmonization
- **Location:** 01_Data_Raw/District_Boundaries/gadm41_IND_2.shp

---

## Sample Construction

**Panel skeleton:** GADM districts (not RBI) for spatial precision in flood matching.
**Temporal coverage:** 2015Q1-2024Q4 (40 quarters) → 37 quarters after dropping 2016Q3-Q4, 2017Q1 (RBI data blackout).
**Spatial coverage:** 666 districts (10 missing from 676 GADM baseline).
**Final N:** ~23,000 observations (666 districts × 37 quarters, minus lag/missing).

### Phase 3c: Master Panel Construction (Complete 2026-01-31)

**RBI Extraction** (Script 13)
- 50,325 district-quarter observations (624 districts × 84 quarters, 2004Q1-2025Q3)
- Fiscal-to-calendar conversion validated
- Files confirmed clean via forensic audit (contamination false alarm resolved)

**Master Panel** (Script 14)
- 26,640 rows (666 districts × 40 quarters, 2015Q1-2024Q4)
- Deposit coverage: 86.9%
- Flood-deposit overlap: 88.6%

**Analysis Sample** (Script 17)
- 23,347 district-quarters
- 631 districts (excluded 35 zero-coverage)
- 37 quarters (excluded 2016Q3-2017Q1 RBI gap)
- Deposit coverage: 99.1%
- Flood-deposit overlap: 100%
- Treatment rate: 8.50% (1,984 flood events)

### Phase 3d: VIIRS Integration (Complete)

**VIIRS Monthly Extraction** (Scripts 21, 21b)
- 79,920 rows (666 districts × 120 months, 2015-01 to 2024-12)
- Tile overlaps resolved via pixel-weighted averaging (7 Himalayan districts)
- Panel balance: 100% (all districts have 120 months)

**Quarterly Aggregation** (Script 22)
- 26,640 rows (666 districts × 40 quarters)
- Month-to-quarter aggregation complete

**VIIRS-Master Merge** (Script 23)
- 23,347 rows (merged with Phase 3c analysis sample)
- VIIRS coverage: 100% (23,347/23,347) ✓
- Deposit coverage: 99.1% (23,139/23,347) ✓

**Regression Variables** (Script 24)
- 23 total variables (11 raw + 12 engineered)
- Logs: log_deposits, log_lights_qt
- Changes: deposit_change_qt, lights_change_qt
- Lags: flood_ruleA_L1-L4, flood_ruleB_L1-L4

**Validation** (Scripts 25, 26)
- Descriptive statistics generated
- 8-check QA validation passed
- Data quality: Forensically validated clean

**District crosswalk:**
- RBI ↔ GADM: 83.2% fuzzy match (passed 80% threshold)
- EM-DAT ↔ GADM: 81.3% match
- Unmatched: 130 RBI districts dropped

**Flood exposure:**
- Rule A (main): District or state fallback (8.67% exposure, 2,220/26,640 obs)
- Rule B (strict): District-only (1.02% exposure, 272/26,640 obs)

**Key restrictions:**
- Dropped 2016Q3-Q4, 2017Q1 (100% missing RBI deposits)
- Dropped 35 districts with zero deposit coverage
- Growth variables lose first quarter per district (lag construction)

---

## Repository Structure

E:\Climate-Migration-Bank-Fragility\

00_Admin/
├── Literature_PDFs/ - 20 papers (VIIRS, climate, banking, migration)
├── Core_Claims.docx - Novelty positioning
├── Hypotheses_Formal_v1.7.md - H1-H4 specifications, IV strategy
├── Literature_Tracker.xlsx - Gap analysis (20 papers)
├── Research_Log.txt - Chronological log (Dec 2025 - Jan 2026)
├── Variables_Codebook_v1.7.md - Variable definitions, transformations
├── RBI_Format_Change_Confirmation.md - RBI format change evidence
└── RBI_Official_Evidence.txt - Official RBI citations

01_Data_Raw/ - Never modified
├── RBI_Bank_Data/ - 3 Excel files (2004-2024)
├── EMDAT_Disasters/ - 69 flood events
├── VIIRS_NightLights/ - Jan 2023 test tile
└── District_Boundaries/ - GADM v4.1 shapefiles

002_Data_Intermediate/
├── emdat_districts_parsed.csv
├── district_crosswalk_draft.csv
├── flood_exposure_panel.csv (26,640 rows)
├── rbi_deposits_panel.csv (50,325 rows, CLEAN 2026-01-31)
├── master_panel_raw.csv (26,640 rows)
├── master_panel_analysis.csv (23,347 rows, Phase 3c)
├── viirs_monthly_panel.csv (79,920 rows, 666 × 120 months, CLEAN)
├── viirs_quarterly_panel.csv (26,640 rows, 666 × 40 quarters)
└── master_panel_validation_log.txt

03_Data_Clean/
├── analysis_panel_final.csv (23,347 rows, Phase 3d VIIRS merged)
└── regression_panel_final.csv (23,347 rows, 23 variables, regression-ready)

04_Code/
├── 00_diagnose_all_files.py - Comprehensive file scanner
├── 01-07: Inspection, parsing
├── 08-12: Crosswalk, skeleton, flood exposure
├── 13: RBI extraction - Complete (2026-01-31)
├── 14-17: Master panel merge
├── 18-20: VIIRS test extraction
├── 21: VIIRS full extraction (120 months)
├── 21b: Multi-tile deduplication fix
├── 22: Quarterly aggregation
├── 23: VIIRS-master merge
├── 24: Variable engineering
├── 25: Descriptive statistics
├── 26: VIIRS validation
├── 27-30: H1-H4 regressions - Pending (scheduled 2026-02-02)
├── 31: Winsorization (deposits)
└── 32-32b: CPI diagnostic, 2023 spike investigation

NEW:
05_Outputs/
├── Tables/
│   ├── 01_descriptive_stats.csv
│   ├── 02_H1_first_stage.csv
│   ├── 03_H2_iv2sls.csv
│   ├── 04_H3_timing.csv
│   └── 05_H4_heterogeneity.csv
├── Logs/
│   ├── 25_descriptive_summary.txt
│   ├── 27_H1_regression_full.txt
│   ├── 28_H2_regression.txt
│   ├── 29_H3_timing.txt
│   └── 30_H4_heterogeneity.txt
└── Figures/ - (empty)

06_Drafts/ - (empty, pending)

---

## Computational Environment

- **OS:** Windows 11
- **Python:** 3.10.19
- **Environment:** research_env (conda)
- **Packages:** pandas, geopandas, rasterio, matplotlib, statsmodels

### Setup

conda create -n research_env python=3.10
conda activate research_env
conda install pandas geopandas rasterio matplotlib statsmodels
Reproducibility

conda activate research_env

# Phase 1: Data inspection
python 04_Code/02_inspect_rbi.py
python 04_Code/03_inspect_emdat.py
python 04_Code/04_inspect_viirs.py

# Phase 2: Crosswalk and flood exposure
python 04_Code/06_parse_emdat_locations.py
python 04_Code/08_build_district_crosswalk.py
python 04_Code/09_build_quarterly_skeleton.py
python 04_Code/10_build_flood_exposure.py

# Phase 3: RBI extraction
python 04_Code/13_extract_rbi_deposits.py
python 04_Code/14_merge_master_panel.py
python 04_Code/17_prepare_analysis_sample.py

# Phase 3d: VIIRS integration
python 04_Code/21_extract_viirs_full_panel.py
python 04_Code/21b_fix_duplicate_districts.py
python 04_Code/22_aggregate_viirs_quarterly.py
python 04_Code/23_merge_viirs_master.py
python 04_Code/24_engineer_regression_variables.py
python 04_Code/25_descriptive_statistics.py
python 04_Code/26_validate_viirs_monthly.py

# Phase 4: Regressions (Pending, scheduled 2026-02-02)
python 04_Code/27_regression_H1_first_stage.py
python 04_Code/28_regression_H2_iv2sls.py
python 04_Code/29_regression_H3_timing.py
python 04_Code/30_regression_H4_heterogeneity.py

Expected outputs:

Expected outputs:

Phase 3d:
- 02_Data_Intermediate/viirs_monthly_panel.csv (79,920 rows)
- 02_Data_Intermediate/viirs_quarterly_panel.csv (26,640 rows)
- 03_Data_Clean/analysis_panel_final.csv (23,347 rows)
- 03_Data_Clean/regression_panel_final.csv (23,347 rows, 23 variables)

Phase 4:
- 05_Outputs/Tables/01_descriptive_stats.csv
- 05_Outputs/Tables/02_H1_first_stage.csv
- 05_Outputs/Tables/03_H2_iv2sls.csv
- 05_Outputs/Tables/04_H3_timing.csv
- 05_Outputs/Tables/05_H4_heterogeneity.csv
- 05_Outputs/Logs/27_H1_regression_full.txt
- 05_Outputs/Logs/28_H2_regression.txt
- 05_Outputs/Logs/29_H3_timing.txt
- 05_Outputs/Logs/30_H4_heterogeneity.txt

Key Methodological Decisions

1. Geography standard: GADM districts as panel skeleton
Rationale: Spatial precision for flood matching; crosswalk harmonizes RBI to GADM
Consequence: 130 unmatched RBI districts dropped

2. Flood exposure rule: Rule A (state fallback) for main specs

Trade-off: Higher coverage (8.67% vs 1.02%) with measurement error
Robustness: Rule B (district-only) as sensitivity check

3. VIIRS extraction protocol (Phase 3d complete, 2026-02-01):

Removed dissolve(by='NAME_2') to prevent homonymous district merges (Script 21)
Pixel-weighted averaging for 7 Himalayan districts across tile boundaries (Script 21b)
Monthly to quarterly aggregation (Script 22)
100% VIIRS-deposit overlap in analysis sample (Script 23)
Result: 666 districts extracted, 23,347 regression-ready observations

4. Sample restrictions:

Dropped 2016Q3-Q4, 2017Q1 (RBI blackout: 100% missing)
Dropped 35 districts with zero deposit coverage
Growth variables lose first quarter per district (lag construction)

5. Standard errors: District-clustered in all regressions (serial correlation)

## Known Issues & Limitations

### RBI Data Coverage Gaps

**2016-2017 Publication Gap** (Structural RBI Gap, NOT Data Error - Confirmed 2026-01-31)
- Missing quarters: 2016Q3, 2016Q4, 2017Q1 (calendar quarters)
- Root cause: RBI publication schedule gap between File 1 (ends 2016-17:Q1 fiscal = 2016Q2 calendar) and File 2 (starts 2017-18:Q1 fiscal = 2017Q2 calendar)
- Initial concern (2026-01-30): Suspected contamination, resolved as false alarm via forensic audit
- Impact: 100% missing deposit data for 3 quarters (1,998 observations)
- Resolution: Analysis sample excludes gap quarters (Script 17, Option 3)
- Threat to validity: None (sample restriction handles cleanly; no selection bias)

**Zero-Coverage Districts** (n=35, 5.3% of sample)
- Causes: Administrative name changes (Allahabad→Prayagraj), district reorganizations, remote areas (Sikkim, Arunachal Pradesh), crosswalk failures
- Resolution: Excluded from analysis sample (Script 17)
- Threat to validity: LOW (non-random but uncorrelated with flood exposure)

SECONDARY ISSUES:

3. 10 missing districts (676 GADM → 666 VIIRS extraction)
Small islands/UTs outside tile 75N060E coverage
Not recoverable; analysis proceeds with 666 districts

4. VIIRS measurement error
Nighttime lights imperfect migration proxy (standard deviation 0.33 in logs)
May attenuate coefficients or introduce measurement error
H2 null result may reflect proxy limitations rather than true null effect

5. EM-DAT geographic precision
17.4% of flood events require Location text parsing
Free-text parsing introduces typos
Crosswalk cleaning applied, some ambiguity remains

6. RBI-GADM crosswalk
16.8% unmatched (130 RBI districts dropped)
Fuzzy matching threshold (80%) trades precision for coverage

Critical Bug History
Phase 4 VIIRS contamination (resolved):

Bug #1: Homonymous district merge
Root cause: dissolve(by='NAME_2') ignored state boundaries
Impact: 17 district-pairs merged (659 districts instead of 676)
Fix: Removed dissolve block (Script 21 rewrite, 2026-01-20)

Bug #2: Multi-tile duplicates
Root cause: 9 border districts extracted twice across tile boundaries
Impact: 1,080 duplicate observations
Fix: Pixel-weighted averaging (Script 21b, 2026-01-21)

RBI contamination concern (resolved):
- Files confirmed CLEAN via forensic audit
- 2016-2017 gap is structural (RBI publication schedule), not data error
- Impact: Zero (no contamination)

Documentation
- Research_Log.txt: Chronological work log
- Hypotheses_Formal_v1.7.md: H1-H4 specifications, IV strategy
- Variables_Codebook_v1.7.md: Variable definitions, transformations
- Literature_Tracker.xlsx: Gap analysis (20 papers)
- Core_Claims.docx: Project positioning

License & Data Terms
Code: MIT License (repository-level)

Data: Each dataset governed by original provider terms; stored for academic research only.

Contact
Researcher: Jaseel Badar
Email: jaseelbadar123@gmail.com
University Email: jab9733@g.harvard.edu
Institution: Harvard University
GitHub: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

Last updated: 2026-02-02 | Project initiated: December 30, 2025