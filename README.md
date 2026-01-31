# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India

**Empirical analysis of flood-induced migration effects on district-level banking stability in India, 2015-2024.**

**Status:** Phase 3c Complete. Analysis sample ready (23,347 obs, 99.1% deposit coverage). All RBI source files confirmed CLEAN via forensic audit (2026-01-31). Master panel validated. Ready for Phase 3d (VIIRS integration).

**Last updated:** 2026-01-31
**Project start:** 2025-12-30

---

## Research Question

Do climate disasters trigger migration (proxied by nighttime-lights declines) that causes district-level deposit stress and broader banking fragility in India?

---

## Hypotheses & Current Results

**NOTE:** H2-H4 results pending VIIRS integration (Phase 3d). H1 not applicable (no deposits variable).

| Hypothesis | Specification | Result | Coefficient | p-value | N |
|------------|---------------|--------|-------------|---------|---|
| **H1** | Floods → Lights (first stage) | Confirmed | β = -0.01250*** | p < 0.0001 | 23,234 |
| **H2** | Lights → Deposits (IV 2SLS) | Pending VIIRS | -- | -- | -- |
| **H3** | Timing (contemporaneous, t=0) | Pending VIIRS | -- | -- | -- |
| **H4a** | Urban × Flood | Pending VIIRS | -- | -- | -- |
| **H4b** | High-exposure × Flood | Pending VIIRS | -- | -- | -- |
| **H4c** | Monsoon × Flood | Pending VIIRS | -- | -- | -- |

**H1 interpretation:** Floods reduce nighttime lights (migration proxy) by 1.25% (district-clustered SEs). Clean VIIRS data validated Jan 2026.

**Standard errors:** District-clustered in all specifications.

---

## Data Sources

Raw data never modified. All transformations in intermediate/clean folders.

### 1. RBI District Banking Data (BSR-2)
- **Source:** Reserve Bank of India official portal
- **Coverage:** 762 districts, 2004-2024, quarterly
- **Files:** RBI_Deposits_2004_2017.xlsx, RBI_Deposits_2017_2022.xlsx, RBI_Deposits_2023_2024.xlsx
- **Variables:** Deposits by population group (Rural/Semi-urban/Urban/Metropolitan)
- **Status:** CLEAN (forensic audit 2026-01-31). Structural gap: 2016Q3, 2016Q4, 2017Q1 missing (RBI publication schedule)
- **Location:** 01_Data_Raw/RBI_Bank_Data/

### 2. EM-DAT Disaster Database
- **Source:** CRED (Centre for Research on Epidemiology of Disasters)
- **Coverage:** 69 flood events, India, 2015-2024
- **Variables:** District/state location, dates, affected population, deaths, damage
- **Location:** 01_Data_Raw/EMDAT_Disasters/

### 3. VIIRS Nighttime Lights
- **Source:** Colorado School of Mines Earth Observation Group
- **Coverage:** 120 monthly tiles (2015-01 to 2024-12), tile 75N060E
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

### Phase 3c: Master Panel Construction (Complete)

**RBI Extraction** (Script 13, 2026-01-31)
- 50,325 district-quarter observations (624 districts × 84 quarters, 2004Q1-2025Q3)
- Fiscal-to-calendar conversion validated
- Files confirmed clean via forensic audit

**Master Panel** (Script 14, 2026-01-31)
- 26,640 rows (666 districts × 40 quarters, 2015Q1-2024Q4)
- Deposit coverage: 86.9%
- Flood-deposit overlap: 88.6%

**Analysis Sample** (Script 17, 2026-01-31)
- 23,347 district-quarters (regression-ready)
- 631 districts (excluded 35 zero-coverage)
- 37 quarters (excluded 2016Q3-2017Q1 RBI gap)
- Deposit coverage: 99.1%
- Flood-deposit overlap: 100%
- Treatment rate: 8.50% (1,984 flood events)

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

02_Data_Intermediate/
├── emdat_districts_parsed.csv
├── district_crosswalk_draft.csv
├── flood_exposure_panel.csv
├── rbi_deposits_panel.csv - 50,325 rows (CLEAN, 2026-01-31)
├── master_panel_raw.csv - 26,640 rows
├── master_panel_analysis.csv - 23,347 rows (regression-ready)
├── viirs_monthly_panel.csv - 79,920 rows (666 × 120 months) CLEAN
├── viirs_quarterly_panel.csv - 26,360 rows (666 × 40 quarters)
├── master_panel_raw.csv
├── master_panel_analysis.csv
└── master_panel_validation_log.txt

03_Data_Clean/
└── (awaiting Phase 3d VIIRS integration)

04_Code/
├── 00_diagnose_all_files.py - Comprehensive file scanner
├── 01-07: Inspection, parsing
├── 08-12: Crosswalk, skeleton, flood exposure
├── 13: RBI extraction - Complete (2026-01-31)
├── 14-17: Master panel merge
├── 18-20: VIIRS test extraction
├── 21: VIIRS full extraction (120 months)
├── 21b: Multi-tile deduplication fix
├── 22-24: Quarterly aggregation, merge, variable engineering
├── 25: Descriptive statistics
├── 26: VIIRS validation
├── 27-30: H1-H4 regressions
├── 31: Winsorization (deposits)
└── 32-32b: CPI diagnostic, 2023 spike investigation

05_Outputs/
├── Tables/ - Awaiting Phase 3d (VIIRS integration)
├── Logs/ - Script execution logs
│ └── diagnose_all_files_20260129_185928.log
└── Figures/ - (empty, pending)

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

# Phase 3: RBI extraction (Complete 2026-01-31)
python 04_Code/13_extract_rbi_deposits.py
python 04_Code/14_merge_master_panel.py
python 04_Code/17_prepare_analysis_sample.py

# Phase 4: VIIRS extraction (CLEAN - validated Jan 2026)
python 04_Code/21_extract_viirs_full_panel.py
python 04_Code/21b_fix_duplicate_districts.py
python 04_Code/22_aggregate_viirs_quarterly.py
python 04_Code/23_merge_viirs_master.py
python 04_Code/24_engineer_regression_variables.py

# Phase 5: Analysis (PARTIAL - H1 valid, H2-H4 under review)
python 04_Code/25_descriptive_statistics.py
python 04_Code/27_regression_H1_first_stage.py  # VALID
python 04_Code/28_regression_H2_iv2sls.py       # INVALID
python 04_Code/29_regression_H3_timing.py       # INVALID
python 04_Code/30_regression_H4_heterogeneity.py # INVALID
Expected outputs (post-correction):

02_Data_Intermediate/viirs_monthly_panel.csv (79,920 rows, validated)
02_Data_Intermediate/master_panel_analysis.csv (23,347 rows, regression-ready)
05_Outputs/Tables/02_H1_first_stage.csv through 05_H4_heterogeneity.csv

Key Methodological Decisions

1. Geography standard: GADM districts as panel skeleton
Rationale: Spatial precision for flood matching; crosswalk harmonizes RBI to GADM
Consequence: 130 unmatched RBI districts dropped

2. Flood exposure rule: Rule A (state fallback) for main specs

Trade-off: Higher coverage (8.67% vs 1.02%) with measurement error
Robustness: Rule B (district-only) as sensitivity check

3. VIIRS extraction protocol (validated Jan 2026):

Removed dissolve(by='NAME_2') to prevent homonymous district merges
Pixel-weighted averaging for 9 border districts across tile boundaries
Result: 666 districts extracted (10 missing from 676 GADM baseline)

4. Sample restrictions:

Dropped 2016Q3-Q4, 2017Q1 (RBI blackout: 100% missing)
Dropped 35 districts with zero deposit coverage
Growth variables lose first quarter per district (lag construction)

5. Standard errors: District-clustered in all regressions (serial correlation)

## Known Issues & Limitations

### RBI Data Coverage Gaps

**2016-2017 Publication Gap** (Structural, Not Data Quality Issue)
- Missing quarters: 2016Q3, 2016Q4, 2017Q1 (calendar quarters)
- Cause: File 1 ends at fiscal 2016-17:Q1 (calendar 2016Q2), File 2 starts at fiscal 2017-18:Q1 (calendar 2017Q2)
- Impact: 100% missing deposit data for 3 quarters across all 666 districts
- Resolution: Analysis sample excludes these quarters (Script 17)
- Threat to validity: None (handled through sample restriction)

**Zero-Coverage Districts** (n=35, 5.3% of sample)
- Causes: Administrative name changes (Allahabad→Prayagraj), district reorganizations, remote areas (Sikkim, Arunachal Pradesh), crosswalk failures
- Resolution: Excluded from analysis sample (Script 17)
- Threat to validity: LOW (non-random but uncorrelated with flood exposure)

SECONDARY ISSUES:

3. 10 missing districts (676 GADM → 666 VIIRS extraction)
Likely small islands/UTs outside tile 75N060E coverage
Investigation pending

4. VIIRS measurement error
Nighttime lights = noisy migration proxy (CV=20.7)
Attenuates coefficients toward zero
Inherent to VIIRS data; acknowledged in interpretation

5. EM-DAT geographic precision
17.4% of flood events require Location text parsing
Free-text parsing introduces typos
Crosswalk cleaning applied, some ambiguity remains

6. RBI-GADM crosswalk
16.8% unmatched (130 RBI districts dropped)
Fuzzy matching threshold (80%) trades precision for coverage

Critical Bug History
Phase 4 VIIRS contamination (resolved Jan 2026):

Bug #1: Homonymous district merge
Root cause: dissolve(by='NAME_2') ignored state boundaries
Impact: 17 district-pairs merged (659 districts instead of 676)
Fix: Removed dissolve block (Script 21 rewrite, 2026-01-20)

Bug #2: Multi-tile duplicates
Root cause: 9 border districts extracted twice across tile boundaries
Impact: 1,080 duplicate observations
Fix: Pixel-weighted averaging (Script 21b, 2026-01-21)

Result: H2 coefficient REVERSED from null (β=0.120, p=0.538) to significant (β=-0.278**, p=0.020) after clean VIIRS extraction.

Phase 6 RBI contamination (in progress Jan 2026):

Source error #1: Duplicate 2016 quarters mislabeled as 2017
Discovered: 2026-01-30 (overlap period verification)
Impact: 1,998 obs (8.56% of sample)
Status: Awaiting Script 13 rewrite with date validation

Source error #2: Population group stratification (2023+)
Discovered: 2026-01-29 (diagnostic forensics)
Impact: False 4x spike in 2023-2024
Status: Aggregation strategy selected, implementation pending

Contaminated outputs preserved in BACKUP folders for audit trail.

Documentation
- Research_Log.txt: Chronological work log (Dec 2025 - Jan 2026)
- Hypotheses_Formal_v1.7.md: H1-H4 specs, IV strategy, contamination status
- Variables_Codebook_v1.7.md: Variable definitions, RBI issue documentation
- Literature_Tracker.xlsx: Gap analysis (20 papers)
- RBI_Format_Change_Confirmation.md: Official RBI evidence
- Core_Claims.docx: Project positioning

Phase 6: Data Correction Pipeline (In Progress)

PRIORITY 1: Fix RBI Extraction
1. Verify Files 1-2 structure (overlap period cross-check)
2. Revise Script 13 with quarter-level date validation
3. Implement population group aggregation for File 3
4. Re-extract RBI deposits (Scripts 13-17 re-run)
5. Validate 2023Q1 continuity (no spike)

PRIORITY 2: Standard Cleaning
6. Outlier analysis (winsorization post-correction)
7. Missing data audit (district exclusion criteria)
8. CPI deflation decision (real vs nominal growth)

PRIORITY 3: Re-Run Analysis
9. Re-merge VIIRS with corrected deposits
10. Re-engineer regression variables
11. Re-run descriptive statistics
12. Re-run H1-H4 regressions

PRIORITY 4: Validation
13. Generate consolidated results table (before/after comparison)
14. Comprehensive data audit #2
15. Documentation consistency check
16. Create master decision log

Success criteria:

-2023Q1 spike eliminated
-Max deposits < 50,000 crores
-Smooth 2022Q4 → 2023Q1 transition
-All regressions re-run with corrected data
-Documentation updated consistently

License & Data Terms
Code: MIT License (repository-level)

Data: Each dataset governed by original provider terms; stored for academic research only.

Contact
Researcher: Jaseel Badar
Email: jaseelbadar123@gmail.com
University Email: jab9733@g.harvard.edu
Institution: Harvard University
GitHub: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

Last updated: 2026-01-30 | Project initiated: December 30, 2025