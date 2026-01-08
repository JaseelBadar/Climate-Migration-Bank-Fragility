# Climate Change, Migration, and Bank Fragility (India)

Causal analysis of climate-induced migration effects on district-level banking stability in India (2015–2024). [file:14]  
**Status:** Phase 3c Day 1 (data inspection completed; harmonization pending). [file:14]  
**Last updated:** 2026-01-08. [file:14]

---

## Research question

Do climate disasters in India trigger migration (proxied by nighttime-lights declines) that causes district-level deposit stress and broader banking fragility? [file:14]

---

## Hypotheses (current working set)

- **H1:** Flood events → decline in nighttime light intensity (VIIRS). [file:14]  
- **H2:** Nighttime light decline → decline in formal bank deposits. [file:14]  
- **H3:** Deposit decline timing is consistent with “shadow-run” style liquidity stress rather than purely credit-loss dynamics. [file:14]  
- **H4:** Banking stress exhibits spatial/network spillovers across districts. [file:14]

---

## Data sources (raw)

This repository follows a strict “raw data is never modified” rule; all transformations go into intermediate/clean folders. [file:14]

### 1) RBI district banking data (BSR-2 style quarterly deposits)
- **What:** District and population-group-wise deposits of scheduled commercial banks, quarterly snapshots. [file:14]  
- **Where stored:** `01_Data_Raw/RBI_Bank_Data/` [file:14]  
- **Files currently present (downloaded):** [file:14]  
  - `RBI_Deposits_2004_2017.xlsx`  
  - `RBI_Deposits_2017_2022.xlsx`  
  - `RBI_Deposits_2023_2024.xlsx`  
- **Notes:** Deposits are split by population group (Rural / Semi-urban / Urban / Metropolitan) and will be aggregated to district totals for analysis. [file:14]

### 2) EM-DAT disasters (floods, India)
- **What:** Flood events in India for the study window (2015–2024). [file:14]  
- **Where stored:** `01_Data_Raw/EMDAT_Disasters/` [file:14]  
- **File currently present:** `public_emdat_custom_request_2026-01-02_c149ea93-8fbf-4f6e-a8f6-3b41cc622ed0.xlsx` [file:14]  
- **Notes:** The raw export initially appears as 70 rows including header, and inspection identifies 69 flood events. [file:14]

### 3) VIIRS nighttime lights (EOG monthly composites)
- **What:** Monthly nighttime lights composites used as an economic-activity / migration proxy. [file:14]  
- **Where stored:** `01_Data_Raw/VIIRS_NightLights/` [file:14]  
- **Current status:** A single test month (Jan 2023) was downloaded to validate processing before any bulk (2015–2024) downloads. [file:14]  
- **Tile:** `75N060E` (covers India). [file:14]

---

## Repository layout

Root directory (local): `E:\Climate-Migration-Bank-Fragility\` [file:14]

00_Admin/
Literature_PDFs/
Core_Claims.docx
Hypotheses_Formal_v1.md
LiteratureTracker.xlsx
Research_Log.txt
Variables_Codebook_v1.md

01_Data_Raw/ # Never modified
RBI_Bank_Data/
EMDAT_Disasters/
VIIRS_NightLights/

02_Data_Intermediate/ # Parsed/reshaped outputs (non-final)
03_Data_Clean/ # Final analysis-ready panels

04_Code/
01_download_viirs.py # Placeholder/script area
02_inspect_rbi.py
03_inspect_emdat.py
04_inspect_viirs.py

05_Outputs/
Figures/
Tables/

06_Drafts/

text
Folder naming and purpose reflect the current project standardization recorded in the research log. [file:14]

---

## Computational environment

- **OS:** Windows 11. [file:14]  
- **Python:** 3.10.19. [file:14]  
- **Environment:** `research_env` (conda). [file:14]  
- **Core packages:** pandas, geopandas, rasterio, matplotlib, statsmodels. [file:14]

### Setup (conda)

```bash
conda create -n research_env python=3.10
conda activate research_env

# install core stack (adjust as needed if conda solves differ on your machine)
conda install pandas geopandas rasterio matplotlib statsmodels
Environment details match the project initialization log. [file:14]

What is completed (as of 2026-01-08)
Phase 2: Data acquisition (completed 2026-01-02)
RBI deposits: 3 consolidated Excel files saved under raw data. [file:14]

EM-DAT floods export downloaded and saved under raw data. [file:14]

VIIRS: 1-month test tile downloaded and extracted for validation. [file:14]

Phase 3a: Literature acquisition (completed 2026-01-05)
Built an initial corpus (~15–18 papers) using Zotero + Harvard HOLLIS access. [file:14]

Phase 3b: Gap analysis (completed 2026-01-06)
LiteratureTracker.xlsx populated with a structured novelty/gap map. [file:14]

Phase 3c Day 0: Conceptual locking (completed 2026-01-07, mobile-only)
Variables_Codebook_v1.md and Hypotheses_Formal_v1.md created. [file:14]

Phase 3c Day 1: Data inspection (completed 2026-01-08)
02_inspect_rbi.py: validated district structure and quarterly columns in the RBI file inspected. [file:14]

03_inspect_emdat.py: validated flood event counts and identified mixed geographic precision (district-level vs missing Admin Units). [file:14]

04_inspect_viirs.py: validated the VIIRS GeoTIFF integrity and India coverage for the test tile. [file:14]

How to reproduce current inspection
Activate the environment and run the inspection scripts: [file:14]

bash
conda activate research_env
python 04_Code/02_inspect_rbi.py
python 04_Code/03_inspect_emdat.py
python 04_Code/04_inspect_viirs.py
Expected outputs are described in Research_Log.txt (Phase 3c Day 1 section). [file:14]

Known constraints (current)
EM-DAT geographic specificity is heterogeneous: roughly half of events have district-level Admin Units while the rest require parsing from free-text location fields. [file:14]

RBI district naming conventions (uppercase, hyphenation, post-renaming) may not match EM-DAT spellings directly, implying a required district-name harmonization layer. [file:14]

VIIRS full-period data (2015–2024 monthly) has not been bulk-downloaded yet; only a test month is currently validated. [file:14]

Documentation
00_Admin/Research_Log.txt: authoritative chronological log of decisions, downloads, scripts, and validation results. [file:14]

00_Admin/LiteratureTracker.xlsx: novelty defense + gap structure (what prior work does not test). [file:14]

00_Admin/Variables_Codebook_v1.md: definitions for variables that will be constructed in code. [file:14]

00_Admin/Hypotheses_Formal_v1.md: testable hypotheses that guide script outputs and regression specs. [file:14]

License & data terms
Code: MIT license (repository-level). [file:14]
Data: Each dataset remains governed by the terms of its original provider; this repo stores raw exports for academic research only. [file:14]


Contact

Researcher: \Jaseel Badar

Email: \jaseelbadar123@gmail.com

Institution: \Harvard University

GitHub: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility



Project Start: December 30, 2025

Last Updated: January 8, 2026, 10:03 PM IST

Phase: 3c (Data Inspection - Day 1 Complete)

