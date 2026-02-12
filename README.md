# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India

**Empirical analysis of flood-induced migration effects on district-level banking stability in India, 2015-2024.**

**Status:** Phase 3d master panel reconstruction complete (Feb 12, 2026). Scripts 13-17 re-run with clean deposits verified. Analysis sample finalized: 23,088 observations (624 districts). VIIRS test extraction successful (Script 18). Ready for full VIIRS integration (Scripts 21-24, 6-8 hour runtime). Regression pipeline pending (Scripts 27-30 require FE corrections).

**Last updated:** 2026-02-12
**Project start:** 2025-12-30

---

## Research Question

Do climate disasters trigger migration (proxied by nighttime-lights declines) that causes district-level deposit stress and broader banking fragility in India?

## Data Quality Status

**All data sources verified clean as of Feb 11, 2026.**

**Deposit contamination (RESOLVED Feb 11-12):** Two-bug cascade identified and fixed. (1) Script 8 crosswalk duplicates: 7 homonymous districts (Aurangabad, Balrampur, etc.) mapped to multiple states. Fixed via deduplication keeping first match per district (769→762 rows). (2) Script 13 merge logic: State-blind merge caused Bihar and Maharashtra AURANGABAD deposits to sum. Fixed via state filtering for homonymous districts. Verification: Aurangabad Bihar 2015Q1 changed from 18652 (contaminated sum) to 4422 (Bihar only, 76% drop). Scripts 13-17 pipeline re-run complete.

**VIIRS pipeline (VERIFIED CLEAN):** Scripts 18-24 use composite (district_gadm, state_gadm) keys throughout. Excel verification confirms distinct radiance values for homonymous districts. No contamination found.

**Regression fixed effects (FIX PENDING):** Scripts 27, 28, 30 create district FE using district name only, collapsing 7 homonymous pairs. Requires composite district_state_id before re-run.

**H3 validation (CONFIRMED CLEAN):** Feb 6 H3 results defensible. Specification uses deposits and floods only (no VIIRS variables). t2 lag effect (β = -0.009, p = 0.012) unaffected by contamination.

---

## Hypotheses & Current Results

| Hypothesis | Specification | Coefficient | p-value | Status |
|------------|---------------|-------------|---------|--------|
| **H1** | Floods → Lights (first stage) | -0.0149 | <0.001 | INVALID (VIIRS outcome) |
| **H2** | Lights → Deposits (IV 2SLS) | +0.2191 | 0.299 | INVALID (weak instrument) |
| **H3-t0** | Floods → Deposits (current) | -0.0005 | 0.777 | UNCERTAIN (verify spec) |
| **H3-t1** | Floods → Deposits (1Q lag) | +0.0004 | 0.757 | UNCERTAIN (verify spec) |
| **H3-t2** | Floods → Deposits (2Q lag) | -0.0091 | 0.012 | UNCERTAIN (verify spec) |
| **H4a** | Urban × Flood | -0.0013 | 0.665 | INVALID (if VIIRS used) |
| **H4b** | HighExp × Flood | -0.0057 | 0.068 | INVALID (if VIIRS used) |
| **H4c** | Monsoon × Flood | +0.0119 | <0.001 | INVALID (statistical artifact) |

**Note: Feb 6 results pending re-run with clean deposits (fixed Feb 11). H3 results validated clean.**

---

## Data Sources

Raw data never modified. All transformations in intermediate/clean folders.

### 1. RBI District Banking Data (BSR-2)
- **Source:** Reserve Bank of India official portal
- **Coverage:** 762 districts, 2004-2024, quarterly
- **Files:** RBI_Deposits_2004_2017.xlsx, RBI_Deposits_2017_2022.xlsx, RBI_Deposits_2023_2024.xlsx
- **Variables:** Deposits by population group (Rural/Semi-urban/Urban/Metropolitan)
- **Status:** CLEAN (Feb 11, 2026). Two-bug fix complete: (1) Column offset corrected (Feb 5), (2) State filtering added for 7 homonymous districts (Feb 11). Verification: Aurangabad Bihar deposits no longer contaminated with Maharashtra values. Structural gap remains: 2016Q3-Q4, 2017Q1 (RBI publication schedule).
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
- **Status:** CLEAN (verified Feb 11, 2026). Scripts 18-24 use composite (district_gadm, state_gadm) keys. Excel verification confirms Aurangabad Bihar and Maharashtra have distinct radiance values. No contamination found.
- **Location (bulk):** E:\\VIIRS_Raw_Data_75N060E\\ (~65 GB external storage)
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
**Final N:** 23,088 observations (624 districts × 37 quarters with complete deposit-flood coverage). VIIRS integration pending (Scripts 21-24).

### Phase 3c: Master Panel Construction (Complete 2026-01-31)

**RBI Extraction** (Script 13)
- 50,325 district-quarter observations (624 districts × 84 quarters, 2004Q1-2025Q3)
- Fiscal-to-calendar conversion validated
- Files structure documented; critical extraction bug discovered 2026-02-04 (wrong column extracted)

**Master Panel** (Script 14)
- 26,640 rows (666 districts × 40 quarters, 2015Q1-2024Q4)
- Deposit coverage: 86.9%
- Flood-deposit overlap: 88.6%

**Analysis Sample** (Script 17)
- 23,088 district-quarters
- 624 districts (excluded 42 zero-coverage)
- 37 quarters (excluded 2016Q3-2017Q1 RBI gap)
- Deposit coverage: 99.1%
- Flood-deposit overlap: 100% (1,941 flood events)
- Treatment rate: 8.41%

### Phase 3d: VIIRS Integration (In Progress)

**VIIRS Test Extraction** (Script 18, Complete Feb 12)
- Test tile: Jan 2023, 676 districts processed
- Success rate: 100% (676/676 districts with valid data)
- Mean radiance: 0.85 nW/cm²/sr (range: 0.0006 to 29.1)
- Top districts: Hyderabad (29.1), Kolkata (21.6), Chennai (21.5)
- Geographic validation: Major metros correctly identified
- Column names corrected: district_gadm, state_gadm (matches master panel)
- Status: Test successful, ready for full extraction

**VIIRS Full Extraction** (Scripts 21-24, Pending)
- Target: 120 monthly tiles (2015-01 to 2024-12)
- Expected output: 79,920 rows (666 districts × 120 months)
- Quarterly aggregation: 26,640 rows (666 × 40 quarters)
- Master merge target: 23,088 rows (matches analysis sample)
- Estimated runtime: 6-8 hours (Script 21)
- Status: Awaiting execution (Feb 13)

**Note:** Previous VIIRS files (dated Feb 1-5) incompatible with new 624-district sample (based on contaminated deposits). Must regenerate entire pipeline.

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
├── district_crosswalk_draft.csv (762 rows, Feb 11 dedup)
├── flood_exposure_panel.csv (26,640 rows)
├── rbi_deposits_panel.csv (49,670 rows, clean Feb 12)
├── master_panel_raw.csv (26,640 rows, 666 districts × 40 quarters)
├── master_panel_analysis.csv (23,088 rows, 624 districts × 37 quarters)
├── viirs_jan2023_test.csv (676 rows, test extraction)
├── master_panel_validation_log.txt
└── [viirs_monthly_panel.csv - pending regeneration]

03_Data_Clean/
├── analysis_panel_final.csv (23,347 rows, Phase 3d VIIRS merged)
└── regression_panel_final.csv (23,347 rows, 23 variables, regression-ready)

04_Code/
├── 00_diagnose_all_files.py - Comprehensive file scanner
├── 01-07: Inspection, parsing
├── 08-12: Crosswalk, skeleton, flood exposure
├── 13: RBI extraction - Complete (clean deposits, Feb 12)
├── 14-17: Master panel merge - Complete (Feb 12)
├── 18: VIIRS test extraction - Complete (Feb 12)
├── 19-20: VIIRS validation (optional, skipped)
├── 21: VIIRS full extraction (120 months) - Pending
├── 21b: Multi-tile deduplication fix
├── 22: Quarterly aggregation
├── 23: VIIRS-master merge
├── 24: Variable engineering
├── 25: Descriptive statistics
├── 26: VIIRS validation
├── 27-30: H1-H4 regressions - Pending 
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

# Phase 3c: RBI extraction and master panel (Complete Feb 12)
python 04_Code/13_extract_rbi_deposits.py  # Clean deposits: 49,670 rows
python 04_Code/14_merge_master_panel.py     # Master panel: 26,640 rows
python 04_Code/15_validate_master_panel.py  # Validation (optional)
python 04_Code/17_prepare_analysis_sample.py # Analysis sample: 23,088 rows

# Phase 3d: VIIRS integration
python 04_Code/21_extract_viirs_full_panel.py
python 04_Code/21b_fix_duplicate_districts.py
python 04_Code/22_aggregate_viirs_quarterly.py
python 04_Code/23_merge_viirs_master.py
python 04_Code/24_engineer_regression_variables.py
python 04_Code/25_descriptive_statistics.py
python 04_Code/26_validate_viirs_monthly.py

# Phase 4: Regressions (Complete but CONTAMINATED by VIIRS error, re-run pending)
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

**Zero-Coverage Districts** (n=42, 6.3% of sample)
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

- **Status:** NOT FIXED (pipeline re-run pending)

### Critical Bugs (Resolved)

**Deposit Contamination - Two-Bug Cascade** (Discovered Feb 4-11, 2026; Resolved Feb 11, 2026)

Bug 1: Crosswalk Duplicates (Script 8)
- **Issue:** 7 homonymous districts matched multiple GADM states (AURANGABAD → Bihar + Maharashtra)
- **Root cause:** Merge used district_gadm only, created 769 rows (should be 762)
- **Discovery:** Feb 7 dedup logic reported "0 duplicates" (counted unique names not rows), manual Excel check revealed 2 Aurangabad entries
- **Fix:** Corrected logic to merge first, then count rows per district. Deduplication keeps first match.
- **Result:** 769→762 rows, 7 duplicates removed

Bug 2: State-Blind Merge (Script 13)
- **Issue:** Merge used district_rbi only, ignoring state_rbi column
- **Impact:** Bihar and Maharashtra AURANGABAD deposits summed and assigned to single state (18652 = 4422 Bihar + 14230 Maharashtra)
- **Discovery:** Deposits unchanged after crosswalk fix, traced to merge logic
- **Fix:** Manual state filtering for 7 homonymous districts (14 state-district pairs)
- **Validation:** Aurangabad Bihar 2015Q1: 18652→4422 (76% drop), 2023Q1: 45345→7673 (83% drop)
- **Result:** 67 duplicate rows removed, 1.8B Crores contamination eliminated
- **Status:** RESOLVED (deposits analysis-ready)

### Pending Work

**VIIRS Full Integration** (Scripts 21-24, Est. 8-10 hours total)
- Script 21: Full 120-month extraction (6-8 hours, requires E:\RawData\75N060E\ access)
- Script 21b: Multi-tile deduplication (if needed)
- Script 22: Quarterly aggregation
- Script 23: VIIRS-master merge (target: 23,088 rows)
- Script 24: Regression variable engineering

**Regression Fixed Effects Correction** (Scripts 27-30)
- **Issue:** District FE uses district_gadm only, collapsing 7 homonymous pairs (617 FE instead of 624)
- **Fix required:** Composite district_state_id for fixed effects
- **Impact:** H1, H2, H4 results from Feb 6 invalid (contaminated deposits + wrong FE)
- **H3 status:** Feb 6 results VALID (specification uses deposits+floods only, no FE)
- **Timeline:** VIIRS integration first (Feb 13), then regressions (Feb 14-15)

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

Last updated: 2026-02-12 | Project initiated: December 30, 2025