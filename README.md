# Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India

**Empirical analysis of flood-induced migration effects on district-level banking stability in India, 2015–2024.**

**Status:** Analysis complete. H1-H4 tested with clean VIIRS data (666 districts, 37 quarters, N≈23,000). H2 mechanism validated: floods reduce nighttime lights by 1.25% (p<0.001), instrumented lights decline reduces deposits by 27.8% (p=0.020). Data corrections pending (outliers, CPI deflation).  
**Last updated:** 2026-01-27  
**Project start:** 2025-12-30

---

## Research question

Do climate disasters trigger migration (proxied by nighttime-lights declines) that causes district-level deposit stress and broader banking fragility in India?

---

## Hypotheses & results

| Hypothesis | Specification | Result | Coefficient | p-value | N |
|------------|---------------|--------|-------------|---------|---|
| **H1** | Floods → Lights (first stage) | Confirmed | β = -0.01250*** | p < 0.0001 | 23,234 |
| **H2** | Lights → Deposits (IV 2SLS) | Confirmed | β = -0.27772** | p = 0.0198 | 23,021 |
| **H3** | Timing (contemporaneous, t=0) | Unexpected | β = +0.00525** | p = 0.012 | 22,423 |
| **H4a** | Urban × Flood | Confirmed | β = -0.01249** | p = 0.010 | 23,021 |
| **H4b** | High-exposure × Flood | Confirmed | β = +0.01049*** | p = 0.007 | 23,021 |
| **H4c** | Monsoon × Flood | Rejected | β = -0.00121 | p = 0.732 | 23,021 |

**Key finding:** Floods reduce nighttime lights (migration proxy) by 1.25%, which reduces bank deposits by 27.8% when instrumented. Urban districts show larger deposit stress; chronically exposed districts exhibit adaptation. Clean VIIRS measurement critical for detecting this channel.

**Standard errors:** District-clustered in all specifications.

---

## Data sources

This repository follows a strict **"raw data is never modified"** rule. All transformations occur in intermediate/clean folders.

### 1. RBI district banking data (BSR-2 quarterly deposits)
- **Source:** Reserve Bank of India official portal  
- **Coverage:** 762 districts, 2004–2024, quarterly snapshots  
- **Variables:** Deposits by population group (Rural/Semi-urban/Urban/Metropolitan), aggregated to district totals  
- **Location:** `01_Data_Raw/RBI_Bank_Data/`  
- **Files:** `RBI_Deposits_2004_2017.xlsx`, `RBI_Deposits_2017_2022.xlsx`, `RBI_Deposits_2023_2024.xlsx`

### 2. EM-DAT disaster database (floods, India)
- **Source:** Centre for Research on Epidemiology of Disasters (CRED)  
- **Coverage:** 69 flood events, 2015–2024, India only  
- **Variables:** Location (district/state), dates, affected population, deaths, damage estimates  
- **Location:** `01_Data_Raw/EMDAT_Disasters/`  
- **File:** `public_emdat_custom_request_2026-01-02_*.xlsx`

### 3. VIIRS nighttime lights (EOG monthly composites)
- **Source:** Colorado School of Mines Earth Observation Group  
- **Coverage:** 120 monthly tiles, 2015-01 to 2024-12, tile 75N060E (covers 100% of India)  
- **Variables:** Mean radiance (nW/cm²/sr), pixel counts  
- **Usage:** Economic activity / migration proxy  
- **Location (bulk):** `E:\VIIRS_Raw_Data_75N060E\` (~65 GB, external storage)  
- **Location (test):** `01_Data_Raw/VIIRS_NightLights/` (Jan 2023 single-month validation)

### 4. GADM v4.1 district boundaries (India)
- **Source:** Global Administrative Areas (GADM)  
- **Coverage:** 676 district polygons  
- **Usage:** VIIRS spatial aggregation, crosswalk harmonization  
- **Location:** `01_Data_Raw/District_Boundaries/`  
- **Key file:** `gadm41_IND_2.shp`

---

## Sample construction

**Panel skeleton:** GADM districts (not RBI) to ensure spatial precision for flood exposure matching.  
**Temporal coverage:** 2015Q1–2024Q4 (40 quarters) → 37 quarters after dropping 2016Q3–Q4, 2017Q1 (RBI data blackout).  
**Spatial coverage:** 666 districts (10 missing from 676 GADM baseline; investigation pending).  
**Final N:** ~23,000 observations (666 districts × 37 quarters, minus lag/missing observations).

**District crosswalk:**
- RBI ↔ GADM: 83.2% fuzzy match rate (passed 80% threshold)
- EM-DAT ↔ GADM: 81.3% match rate
- Unmatched districts: 130 RBI districts dropped (no GADM match)

**Flood exposure:**
- **Rule A (main):** District-level or state-level fallback (8.67% exposure rate, 2,220/26,640 obs)
- **Rule B (strict):** District-level only (1.02% exposure rate, 272/26,640 obs)
- EM-DAT parsed district labels from JSON `Admin Units` field (82.6% coverage) and free-text `Location` field (17.4%)

**Key restrictions:**
- Dropped 2016Q3–Q4, 2017Q1 (RBI deposit data 100% missing)
- Dropped 35 districts with zero deposit coverage across full window
- Growth variables (deposit_change, lights_change) lose first quarter per district (lag construction)

---

## Repository structure

E:\Climate-Migration-Bank-Fragility\

00_Admin/
├── Literature_PDFs/ # 20 papers (VIIRS methods, climate impacts, banking, migration)
├── Core_Claims.docx # Novelty positioning
├── Hypotheses_Formal_v1.6.md # H1-H4 specifications, IV strategy
├── Literature_Tracker.xlsx # Gap analysis matrix
├── Research_Log.txt # Chronological log (Dec 2025 - Jan 2026)
└── Variables_Codebook_v1.6.md # Variable definitions, transformations

01_Data_Raw/ # Never modified
├── RBI_Bank_Data/ # 3 Excel files, 2004-2024
├── EMDAT_Disasters/ # 69 flood events
├── VIIRS_NightLights/ # Jan 2023 test tile only (bulk on external drive)
└── District_Boundaries/ # GADM v4.1 shapefiles

02_Data_Intermediate/ # Processed outputs (non-final)
├── emdat_districts_parsed.csv
├── district_crosswalk_draft.csv
├── flood_exposure_panel.csv
├── rbi_deposits_panel.csv
├── viirs_monthly_panel.csv # 79,920 rows (666 districts × 120 months)
├── viirs_quarterly_panel.csv # 26,360 rows (666 districts × 40 quarters)
├── master_panel_raw.csv
├── master_panel_analysis.csv
└── master_panel_validation_log.txt

03_Data_Clean/ # Final analysis-ready panels
├── analysis_panel_final.csv # Master panel + VIIRS (23,347 rows)
└── regression_panel_final.csv # With engineered variables (logs, lags, changes)

04_Code/ # 30 Python scripts (01-30)
├── 01-07: Inspection, parsing
├── 08-12: Crosswalk, skeleton, flood exposure
├── 13-17: RBI extraction, master panel merge, validation
├── 18-20: VIIRS test extraction (single month)
├── 21: VIIRS full extraction (120 months)
├── 21b: Multi-tile deduplication fix
├── 22-24: Quarterly aggregation, merge, variable engineering
├── 25: Descriptive statistics
├── 26: VIIRS validation
└── 27-30: H1-H4 regressions

05_Outputs/
├── Tables/ # Regression results CSVs
│ ├── 01_descriptive_stats.csv
│ ├── 02_H1_first_stage.csv
│ ├── 03_H2_iv2sls.csv
│ ├── 04_H3_timing.csv
│ └── 05_H4_heterogeneity.csv
├── Logs/ # Script execution logs
└── Figures/ # (empty, pending writing phase)

06_Drafts/ # Paper drafts (pending)

---

## Computational environment

- **OS:** Windows 11  
- **Python:** 3.10.19  
- **Environment:** `research_env` (conda)  
- **Core packages:** pandas, geopandas, rasterio, matplotlib, statsmodels

### Setup

```bash
conda create -n research_env python=3.10
conda activate research_env
conda install pandas geopandas rasterio matplotlib statsmodels
Reproducibility
Full pipeline execution
bash
conda activate research_env

# 1. Data inspection (Scripts 02-04)
python 04_Code/02_inspect_rbi.py
python 04_Code/03_inspect_emdat.py
python 04_Code/04_inspect_viirs.py

# 2. District crosswalk & flood exposure (Scripts 06-12)
python 04_Code/06_parse_emdat_locations.py
python 04_Code/08_build_district_crosswalk.py
python 04_Code/09_build_quarterly_skeleton.py
python 04_Code/10_build_flood_exposure.py

# 3. RBI deposits & master panel (Scripts 13-17)
python 04_Code/13_extract_rbi_deposits.py
python 04_Code/14_merge_master_panel.py
python 04_Code/15_validate_master_panel.py
python 04_Code/17_prepare_analysis_sample.py

# 4. VIIRS extraction with bug fixes (Scripts 21, 21b, 22-24)
python 04_Code/21_extract_viirs_full_panel.py    # Output: 81,120 rows (676 districts × 120 months + 1,080 duplicates)
python 04_Code/21b_fix_duplicate_districts.py    # Pixel-weighted deduplication → 79,920 rows (666 districts × 120 months)
python 04_Code/22_aggregate_viirs_quarterly.py
python 04_Code/23_merge_viirs_master.py
python 04_Code/24_engineer_regression_variables.py

# 5. Regressions (Scripts 25, 27-30)
python 04_Code/25_descriptive_statistics.py
python 04_Code/27_regression_H1_first_stage.py
python 04_Code/28_regression_H2_iv2sls.py
python 04_Code/29_regression_H3_timing.py
python 04_Code/30_regression_H4_heterogeneity.py

**Expected outputs:**
- `02_Data_Intermediate/viirs_monthly_panel.csv` (79,920 rows, validated)
- `03_Data_Clean/regression_panel_final.csv (23,347 rows, analysis-ready)
- `05_Outputs/Tables/02_H1_first_stage.csv through 05_H4_heterogeneity.csv

Key methodological decisions

**1. Geography standard:** GADM districts (not RBI) as panel skeleton  
- **Rationale:** Ensures flood exposure matching precision; crosswalk harmonizes RBI deposits to GADM  
- **Consequence:** 130 unmatched RBI districts dropped

**2. Flood exposure rule:** Rule A (state fallback) for main specifications
- **Trade-off:** Higher coverage (8.67% vs 1.02%) at cost of measurement error (state-level floods assigned to all districts)
- **Robustness:** Rule B (district-only) as sensitivity check

**3. VIIRS extraction protocol:**
Critical fix (Script 21): Removed dissolve(by='NAME_2') to prevent homonymous district merges (e.g., Aurangabad Bihar vs Maharashtra)
Multi-tile fix (Script 21b): Pixel-weighted averaging for 9 border districts straddling tile boundaries
Validation: 666 districts extracted (10 missing from 676 GADM baseline; small islands/UTs outside tile coverage)

**4. Sample restrictions:**
Dropped 2016Q3–Q4, 2017Q1 (RBI data blackout: 100% missing deposits)
Dropped 35 districts with zero deposit coverage across entire window
Growth variables lose first quarter per district (lag construction)

**5. Standard errors: District-clustered in all regressions (accounts for serial correlation)**

Known issues & limitations

1. 10 missing districts (676 GADM baseline → 666 VIIRS extraction)
Likely small islands, Union Territories outside tile 75N060E coverage
Investigation pending

2. Extreme deposit outliers (-273%, +656% quarterly growth)
Potential causes: District boundary changes, bank branch reclassifications, RBI data entry errors
Winsorization scheduled (Phase 6)

3. Nominal growth confound (47.6% annualized deposit growth, no CPI deflation)
Inflation trends may confound flood treatment effects
Decision pending: (a) deflate by India CPI, or (b) disclose limitation explicitly

4. Zero-inflation in deposit changes (25% of observations have Δ=0)
Potential measurement error or genuine stasis in rural districts
Diagnosis pending

5. VIIRS measurement error: Nighttime lights are a noisy proxy for migration
High coefficient of variation (20.7) attenuates effects toward zero
Inherent to VIIRS data; cannot be "fixed" but acknowledged in interpretation

6. EM-DAT geographic precision: 17.4% of flood events require Location text parsing
Free-text parsing introduces typos, non-district tokens
Crosswalk cleaning applied but some ambiguity remains

7. RBI-GADM crosswalk: 16.8% unmatched (130 RBI districts dropped)
Fuzzy matching threshold (80%) trades precision for coverage
Manual validation log available in 08_build_crosswalk_log.txt

Critical bug history (resolved)
Bug discovered: 2026-01-19 (file audit)
Bug fixed: 2026-01-20 (Script 21), 2026-01-21 (Script 21b)
Impact: All Phase 4 regression results (Jan 17-18) invalidated due to contaminated VIIRS data

Bug #1: Homonymous district merge
Root cause: Script 21 Line 53 used dissolve(by='NAME_2') which grouped by district name alone, ignoring state boundaries
Impact: 17 homonymous district-pairs (e.g., Aurangabad Bihar + Aurangabad Maharashtra) merged into single observations → 659 districts instead of 676
Measurement error: 7 remaining homonymous districts shared identical VIIRS values across different states (518 contaminated observations)
Fix: Deleted dissolve block; rasterio.mask() handles multipolygons natively

Bug #2: Multi-tile overlap duplicates
Root cause: 9 Himalayan/Northeast border districts straddled VIIRS tile boundaries → each district extracted twice
Impact: 1,080 duplicate observations (9 districts × 2 tiles × 120 months)
Fix: Script 21b applies pixel-weighted averaging to aggregate multi-tile extractions

Result: H2 coefficient REVERSED from null (β=0.120, p=0.538, contaminated) to significant (β=-0.278**, p=0.020, clean). Clean VIIRS measurement critical for detecting migration channel.

Contaminated data preserved in 02_Data_Intermediate_CONTAMINATED_BACKUP/ and 05_Outputs_CONTAMINATED_BACKUP/ for comparison.

Documentation
Research_Log.txt: Authoritative chronological log of daily work (Dec 2025 – Jan 2026)
Hypotheses_Formal_v1.6.md: H1-H4 specifications, IV identification strategy, exclusion restrictions
Variables_Codebook_v1.6.md: Variable definitions, transformations, coding protocols
Literature_Tracker.xlsx: Novelty defense matrix (20 papers), gap analysis
Core_Claims.docx: Project positioning, contribution statement

Next steps (Phase 6)
Scheduled: 2026-01-28

Data corrections (Scripts 31-33):
Diagnose outliers, zeros, missing districts
Apply winsorization (1st/99th percentile)
Decide on CPI deflation or disclose nominal-growth limitation
Re-run regressions with corrected data:
Generate consolidated results table (all H1-H4 coefficients, SEs, t-stats, p-values, N)
Compare before/after correction coefficients (quantify outlier impact)

Comprehensive Audit #2:
Consolidate all values (match rates, exposure rates, coverage %, regression results)
Cross-validate file dimensions, column names across all 31 files
Verify documentation consistency (README, Hypotheses, Codebook cite same values)
Create master decision log for writing phase
Begin Results section writing with finalized, publication-ready numbers

License & data terms
Code: MIT License (repository-level)
Data: Each dataset governed by original provider terms; stored for academic research only

Contact
Researcher: Jaseel Badar
Email: jaseelbadar123@gmail.com
University Email: jab9733@g.harvard.edu
Institution: Harvard University
GitHub: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

Last updated: 2026-01-27 | Project initiated: December 30, 2025