# Climate Change, Migration, and Bank Fragility (India)

Causal analysis of climate-induced migration effects on district-level banking stability in India (2015–2024).   
**Status:** Phase 3d in progress: VIIRS test extraction/merge validated; bulk monthly download (2015–2024) underway.   
**Last updated:** 2026-01-13.

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
- **What:** Monthly nighttime lights composites used as an economic-activity / migration proxy.   
- **Where stored:** `01_Data_Raw/VIIRS_NightLights/`   
- **Current status:** Test extraction + merge pipeline validated using Jan 2023; bulk monthly archives (2015–2024) are now being downloaded manually to external storage.
- **Note:** Scripts currently reference 01_Data_Raw/VIIRS_NightLights/ paths; if the bulk files remain outside the repo, scripts must be pointed to the external base path or a symlink must be used.   
- **Tile:** `75N060E` (covers India). 

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

03_Data_Clean/ # Final analysis-ready panels

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

What is completed (as of 2026-01-08)
Phase 2: Data acquisition (completed 2026-01-02)
RBI deposits: 3 consolidated Excel files saved under raw data. 

EM-DAT floods export downloaded and saved under raw data. 

VIIRS: 1-month test tile downloaded and extracted for validation. 

Phase 3a: Literature acquisition (completed 2026-01-05)
Built an initial corpus (~15–18 papers) using Zotero + Harvard HOLLIS access. 

Phase 3b: Gap analysis (completed 2026-01-06)
LiteratureTracker.xlsx populated with a structured novelty/gap map. 

Phase 3c Day 0: Conceptual locking (completed 2026-01-07, mobile-only)
Variables_Codebook_v1.md and Hypotheses_Formal_v1.md created. 

Phase 3c Day 1: Data inspection (completed 2026-01-08)
02_inspect_rbi.py: validated district structure and quarterly columns in the RBI file inspected. 

03_inspect_emdat.py: validated flood event counts and identified mixed geographic precision (district-level vs missing Admin Units). 

04_inspect_viirs.py: validated the VIIRS GeoTIFF integrity and India coverage for the test tile. 

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
Institution: \Harvard University
GitHub: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility


Project Start: December 30, 2025