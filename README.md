# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India
Causal analysis of climate-induced migration effects on district-level banking stability in India (2015–2024).

**Status:** Phase 4 complete — All regressions run (H1-H4). Two significant findings: Floods reduce nighttime lights (β=-0.011***); Urban districts more vulnerable to flood shocks (β=-1.21**).   
**Last updated:** 2026-01-16.

---

## Research question

Do climate disasters in India trigger migration (proxied by nighttime-lights declines) that causes district-level deposit stress and broader banking fragility? 

---

## Hypotheses (current working set)

- **H1:** Flood events → decline in nighttime light intensity (VIIRS).   
- **H2:** Nighttime light decline → decline in formal bank deposits.   
- **H3:** Deposit decline timing is consistent with “shadow-run” style liquidity stress rather than purely credit-loss dynamics.   
- **H4:** Banking stress exhibits spatial/network spillovers across districts. 

---

## Data sources (raw)

This repository follows a strict “raw data is never modified” rule; all transformations go into intermediate/clean folders. 

### 1) RBI district banking data (BSR-2 style quarterly deposits)
- **What:** District and population-group-wise deposits of scheduled commercial banks, quarterly snapshots.   
- **Where stored:** `01_Data_Raw/RBI_Bank_Data/`   
- **Files currently present (downloaded):**   
  - `RBI_Deposits_2004_2017.xlsx`  
  - `RBI_Deposits_2017_2022.xlsx`  
  - `RBI_Deposits_2023_2024.xlsx`  
- **Notes:** Deposits are split by population group (Rural / Semi-urban / Urban / Metropolitan) and will be aggregated to district totals for analysis. 

### 2) EM-DAT disasters (floods, India)
- **What:** Flood events in India for the study window (2015–2024).   
- **Where stored:** `01_Data_Raw/EMDAT_Disasters/`   
- **File currently present:** `public_emdat_custom_request_2026-01-02_c149ea93-8fbf-4f6e-a8f6-3b41cc622ed0.xlsx`   
- **Notes:** The raw export initially appears as 70 rows including header, and inspection identifies 69 flood events. 

### 3) VIIRS nighttime lights (EOG monthly composites)
- **What:** Monthly nighttime lights composites used as an economic-activity / displacement proxy.   
- **Where stored (test tile):** `01_Data_Raw/VIIRS_NightLights/` (Jan 2023 only).   
- **Where stored (bulk):** `E:\VIIRS_Raw_Data_75N060E\` (~60-70 GB; external storage outside repo).   
- **Current status:** All 120 monthly tiles downloaded (2015–2024); test extraction validated (Scripts 18–20); bulk extraction ready (Script 21).   
- **Tile:** `75N060E` (covers 100% of India; 0°N-75°N, 60°E-180°E). 

### 4) District boundaries (GADM v4.1)
- **What:** India administrative boundaries; district polygons used for VIIRS aggregation and adjacency/spillover construction.
- **Where stored:** `01_Data_Raw/District_Boundaries/`
- **Key file (district level):** `gadm41_IND_2.shp` (676 districts validated in geopandas).

---

## Repository layout

Root directory (local): `E:\Climate-Migration-Bank-Fragility\` 

00_Admin/
Literature_PDFs/
Core_Claims.docx
Hypotheses_Formal_v1.1.md
Literature_Tracker.xlsx
Research_Log.txt
Variables_Codebook_and_Coding_Protocol_v1.1.md

01_Data_Raw/ # Never modified
RBI_Bank_Data/
EMDAT_Disasters/
VIIRS_NightLights/
District_Boundaries/

02_Data_Intermediate/ # Parsed/reshaped outputs (non-final)
emdat_districts_parsed.csv
district_crosswalk_draft.csv
emdat_district_matches.csv
district_quarter_skeleton.csv
flood_exposure_panel.csv
rbi_deposits_panel.csv
master_panel_raw.csv
master_panel_validation_log.txt
master_panel_analysis.csv
viirs_monthly_panel.csv
viirs_quarterly_panel.csv

03_Data_Clean/ # Final analysis-ready panels
analysis_panel_final.csv
regression_panel_final.csv

04_Code/
01_download_viirs.py # Placeholder/script area
02_inspect_rbi.py
03_inspect_emdat.py
04_inspect_viirs.py
05_test_shapefile.py
06_parse_emdat_locations.py
07_check_output.py
08_build_district_crosswalk.py
09_build_quarterly_skeleton.py
10_build_flood_exposure.py
11_validate_flood_events.py
12_summarize_flood_exposure.py
13_extract_rbi_deposits.py
14_merge_master_panel.py
15_validate_master_panel.py
16_diagnose_missing_data.py
17_prepare_analysis_sample.py
18_extract_viirs_district_means.py
19_validate_viirs_extraction.py
20_aggregate_viirs_to_quarterly.py
21_extract_viirs_full_panel.py
22_aggregate_viirs_quarterly.py
23_merge_viirs_master.py
24_engineer_regression_variables.py
25_descriptive_statistics.py
26_validate_viirs_monthly.py
27_regression_H1_first_stage.py
28_regression_H2_iv2sls.py
29_regression_H3_timing.py
30_regression_H4_heterogeneity.py

05_Outputs/
Figures/
Tables/

06_Drafts/

Folder naming and purpose reflect the current project standardization recorded in the research log. 

---

## Computational environment

- **OS:** Windows 11.   
- **Python:** 3.10.19.   
- **Environment:** `research_env` (conda).   
- **Core packages:** pandas, geopandas, rasterio, matplotlib, statsmodels. 

### Setup (conda)

```bash
conda create -n research_env python=3.10
conda activate research_env

# install core stack
conda install pandas geopandas rasterio matplotlib statsmodels
Environment details match the project initialization log. 

## What is completed (as of 2026-01-16)

### Phase 1: Project Initialization (Dec 2025)
- Computational environment configured (Python 3.10, conda, geopandas stack)
- Repository structure established with strict raw/intermediate/clean separation
- GitHub version control initialized

### Phase 2: Data Acquisition (Jan 2026)
- **RBI deposits:** 3 Excel files covering 2004-2024, 762 districts, quarterly snapshots
- **EM-DAT floods:** 69 flood events (2015-2024) with parsed district-level Admin Units
- **VIIRS nighttime lights:** 120 monthly tiles downloaded (2015-2024, tile 75N060E, ~65 GB)
- **GADM boundaries:** India district polygons (v4.1, 676 districts)

### Phase 3: Data Integration & Panel Construction (Jan 2026)
- **Literature review:** 15-18 papers acquired; novelty gaps documented in `LiteratureTracker.xlsx`
- **Hypotheses formalized:** H1-H4 specified in `Hypotheses_Formal_v1.1.md` with IV strategy
- **District crosswalk:** Built RBI-GADM-EM-DAT harmonization (83.2% match rate, passed threshold)
- **Flood exposure panel:** Constructed Rule A (8.3% exposure) and Rule B (1.0% high-precision) indicators
- **RBI deposits panel:** Extracted to district-quarter format; identified 2016Q3-2017Q1 data blackout
- **VIIRS integration:** Extracted district-level nighttime lights; aggregated to quarterly panel
- **Master panel:** Merged deposits + floods + VIIRS → 23,347 observations (631 districts × 37 quarters)

### Phase 4: Hypothesis Testing (Jan 16, 2026) COMPLETE
- **H1 (Floods → Lights):** β = -0.011*** (p < 0.001) — Floods reduce nighttime lights significantly
- **H2 (Lights → Deposits via IV):** Weak instrument (F = 11.9); 2SLS estimates imprecise
- **H3 (Timing analysis):** 1-quarter lag significant (p = 0.013); 2-quarter lag marginal (p = 0.068)
- **H4 (Heterogeneity):** Urban districts MORE vulnerable to floods (β = -1.21**, p = 0.005) — KEY FINDING

**Status:** Regressions complete. Two significant findings ready for paper: H1 (climate shock → migration proxy) and H4a (urban vulnerability). Null results for H2 (weak IV) and H4b/c (no adaptation or seasonality effects). 

How to reproduce current inspection
Activate the environment and run the inspection scripts:

bash
conda activate research_env
python 04_Code/02_inspect_rbi.py
python 04_Code/03_inspect_emdat.py
python 04_Code/04_inspect_viirs.py

# Phase 3c Day 2 additions (EM-DAT district extraction)
python 04_Code/06_parse_emdat_locations.py
python 04_Code/07_check_output.py
python 04_Code/08_build_district_crosswalk.py
python 04_Code/09_build_quarterly_skeleton.py
python 04_Code/10_build_flood_exposure.py
python 04_Code/11_validate_flood_events.py
python 04_Code/12_summarize_flood_exposure.py

# Phase 3d additions (RBI deposits + master panel)
python 04_Code/13_extract_rbi_deposits.py
python 04_Code/14_merge_master_panel.py
python 04_Code/15_validate_master_panel.py
python 04_Code/16_diagnose_missing_data.py
python 04_Code/17_prepare_analysis_sample.py

Expected outputs are described in Research_Log.txt.txt (Phase 3c–Phase 3d sections), and should include:

02_Data_Intermediate/rbi_deposits_panel.csv
02_Data_Intermediate/master_panel_raw.csv
02_Data_Intermediate/master_panel_validation_log.txt
02_Data_Intermediate/master_panel_analysis.csv
02_Data_Intermediate/viirs_monthly_panel.csv
02_Data_Intermediate/viirs_quarterly_panel.csv
03_Data_Clean/analysis_panel_final.csv
03_Data_Clean/regression_ready_panel.csv
05_Outputs/Tables/01_descriptive_stats.csv
05_Outputs/Tables/02_H1_first_stage.csv
05_Outputs/Tables/03_H2_iv2sls.csv
05_Outputs/Tables/04_H3_timing.csv
05_Outputs/Tables/05_H4_heterogeneity.csv

Known constraints (current)
EM-DAT geographic specificity is heterogeneous, but after parsing the `Admin Units` JSON correctly (adm2_name districts + adm1_name states), 57/69 events have usable Admin Units data and only 12/69 require Location text parsing; parsed text still needs manual cleaning and crosswalk harmonization.

RBI district naming conventions (uppercase, hyphenation, post-renaming) may not match EM-DAT spellings directly, implying a required district-name harmonization layer.

RBI deposits coverage has known gaps in parts of the time series; the master panel validation log documents these issues and recommended handling choices.

VIIRS full-period data (2015–2024 monthly) has not been bulk-downloaded yet; only a test month is currently validated.

Documentation
00_Admin/Research_Log.txt.txt: authoritative chronological log of decisions, downloads, scripts, and validation results.
00_Admin/Literature_Tracker.xlsx: novelty defense + gap structure (what prior work does not test).
00_Admin/Variables_Codebook_and_Coding_Protocol_v1.1.md: definitions for variables that will be constructed in code.
00_Admin/Hypotheses_Formal_v1.1.md: testable hypotheses that guide script outputs and regression specs.

License & data terms
Code: MIT license (repository-level). 
Data: Each dataset remains governed by the terms of its original provider; this repo stores raw exports for academic research only. 


Contact

Researcher: \Jaseel Badar
Email: \jaseelbadar123@gmail.com
University Email: \jab9733@g.harvard.edu
Institution: \Harvard University
GitHub: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility


Project Start: December 30, 2025