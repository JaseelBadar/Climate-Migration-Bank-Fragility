\# Climate Change, Migration, and Banking Sector Fragility in India



\*\*Research Project\*\*: Causal analysis of climate-induced migration effects on district-level banking stability  

\*\*Period\*\*: 2015-2024 (10-year panel)  

\*\*Status\*\*: Phase 3c - Data Inspection (In Progress)  

\*\*Last Updated\*\*: January 8, 2026



---



\## Research Question



Does climate-induced migration (proxied by flood events and nighttime light intensity changes) causally affect banking sector fragility at the district level in India?



\### Hypotheses



\*\*H1\*\*: Flood events → Decline in nighttime light intensity (VIIRS)  

\*\*H2\*\*: Nighttime light decline → Decline in formal bank deposits  

\*\*H3\*\*: Deposit decline → Increased reliance on shadow banking (timing analysis)  

\*\*H4\*\*: Banking stress exhibits spatial contagion through district networks



---



\## Data Sources



\### 1. Reserve Bank of India (RBI) - District Banking Statistics (BSR-2)

\- \*\*Coverage\*\*: 762 districts, quarterly frequency (2015-2024)

\- \*\*Variables\*\*: Deposits by population group (Rural, Semi-urban, Urban, Metropolitan)

\- \*\*Files\*\*: 3 files covering 2004-2017, 2017-2022, 2023-2024

\- \*\*Source\*\*: https://rbi.org.in/Scripts/AnnualPublications.aspx



\### 2. EM-DAT International Disaster Database

\- \*\*Coverage\*\*: 69 flood events in India (2015-2024)

\- \*\*Variables\*\*: Location, dates, deaths, affected population, economic damage

\- \*\*Geographic Precision\*\*: 51% district-level, 49% state-level

\- \*\*Source\*\*: Centre for Research on Epidemiology of Disasters (CRED)



\### 3. VIIRS Nighttime Lights (NASA/NOAA)

\- \*\*Coverage\*\*: Monthly composites, Tile 75N060E (covers all of India)

\- \*\*Resolution\*\*: 15 arc-seconds (~463m at equator)

\- \*\*Period\*\*: January 2015 - December 2024 (120 months)

\- \*\*File Size\*\*: ~240 GB total (2 GB per month)

\- \*\*Source\*\*: Colorado School of Mines Earth Observation Group



---



\## Project Structure



E:\\Climate-Migration-Bank-Fragility

│

├── 00\_Admin/

│ ├── Literature\_PDFs/ # Reference papers and literature

│ ├── Core\_Claims.docx # Core argument structure

│ ├── Hypotheses\_Formal\_v1.md # Formal hypothesis statements

│ ├── Literature\_Tracker.xlsx # Paper tracking spreadsheet

│ ├── Research\_Log.txt # Detailed research journal

│ └── Variables\_Codebook\_v1.md # Variable definitions and codebook

│

├── 01\_Data\_Raw/ # Original data (never modified)

│ ├── RBI\_Bank\_Data/ # District banking statistics (3 files)

│ ├── EMDAT\_Disasters/ # Flood event database (1 file)

│ └── VIIRS\_NightLights/ # Nighttime lights tiles (120 when complete)

│

├── 02\_Data\_Intermediate/ # Intermediate processing outputs

├── 03\_Data\_Clean/ # Cleaned datasets ready for analysis

│

├── 04\_Code/ # All Python scripts

│ ├── 01\_download\_viirs.py # Placeholder for Phase 3d batch download

│ ├── 02\_inspect\_rbi.py # RBI structure inspection

│ ├── 03\_inspect\_emdat.py # EM-DAT Admin Units parsing

│ ├── 04\_inspect\_viirs.py # VIIRS validation

│ └── (future scripts for cleaning, merging, analysis)

│

├── 05\_Outputs/ # Analysis outputs

│ ├── Figures/ # Publication-ready plots

│ └── Tables/ # Regression tables and summaries

│

└── 06\_Drafts/ # Paper drafts and manuscripts



text



---



\## Computational Environment



\### System Requirements

\- \*\*OS\*\*: Windows 11

\- \*\*Python\*\*: 3.10.19

\- \*\*Memory\*\*: Minimum 16 GB RAM (for VIIRS processing)

\- \*\*Storage\*\*: 300 GB free space (240 GB for VIIRS + processing overhead)



\### Dependencies

\- \*\*Core\*\*: pandas, numpy

\- \*\*Geospatial\*\*: geopandas, rasterio, shapely, fiona

\- \*\*Statistical\*\*: statsmodels, scipy

\- \*\*Visualization\*\*: matplotlib, seaborn

\- \*\*File I/O\*\*: openpyxl (Excel reading)



\### Setup Instructions



```bash

\# Create conda environment

conda create -n research\_env python=3.10



\# Activate environment

conda activate research\_env



\# Install all dependencies

conda install pandas numpy geopandas rasterio statsmodels matplotlib seaborn openpyxl scipy shapely fiona

Current Status (Phase 3c Day 1 - January 8, 2026)

✅ Completed

&nbsp;Project structure created (Dec 30-31)



&nbsp;Computational environment configured (conda research\_env)



&nbsp;RBI data downloaded (3 files, 2004-2024, ~1.5 GB total)



&nbsp;EM-DAT data downloaded (69 flood events, 2015-2024)



&nbsp;VIIRS test tile downloaded (Jan 2023, 1.93 GB)



&nbsp;Data inspection scripts written and validated (3 scripts)



Script 1 - RBI Inspection (02\_inspect\_rbi.py):



762 unique districts identified



11 quarters of data (2023Q1-2025Q2)



4 population groups per district (Rural, Semi-urban, Urban, Metropolitan)



Deposit columns validated at indices 7,10,13,16,19,22,25,28,31,34,37



District naming: UPPERCASE, hyphenated format (e.g., BALOD, GAURELA-PENDRA-MARWAHI)



Script 2 - EM-DAT Inspection (03\_inspect\_emdat.py):



69 flood events (2015-2024)



147 unique districts extracted from Admin Units JSON



Geographic precision: 35 events (50.7%) district-level, 34 events (49.3%) state-level only



Severity measure: No. Affected (73.9% coverage, range 5-23M people)



Date structure: Complete, convertible to quarters



Script 3 - VIIRS Inspection (04\_inspect\_viirs.py):



File validated: 1.93 GB GeoTIFF, 28,800 × 18,000 pixels



India fully covered within tile extent (60-180°E, 0-75°N)



Radiance range: 0-57.24 nW/cm²/sr (mean 0.87, median 0.50)



Resolution: 15 arc-seconds (~463m at equator)



Data quality: CONFIRMED (all sample pixels valid)



🚧 Next Steps (Phase 3c Day 2 - January 9, 2026)

&nbsp;Parse EM-DAT Location text for 34 events with empty Admin Units



&nbsp;Build district name harmonization crosswalk (EM-DAT ↔ RBI fuzzy matching)



&nbsp;Create state-to-district mapping table for state-level events



&nbsp;Test VIIRS spatial subsetting (extract India bounding box only)



&nbsp;Decision: Proceed to Phase 3d download or refine merge logic



📋 Upcoming (Phase 3d - January 9-12, 2026)

&nbsp;Batch download remaining 119 VIIRS monthly tiles (~230 GB)



&nbsp;Clean and concatenate RBI files (create 2015-2024 quarterly panel)



&nbsp;Clean EM-DAT data (harmonize district names, parse Location text)



&nbsp;Aggregate VIIRS radiance to district level (spatial join with district boundaries)



&nbsp;Merge all three datasets into final analysis panel



📊 Future (Phase 4 - January 13-20, 2026)

&nbsp;H1 regression: Floods → VIIRS decline (difference-in-differences)



&nbsp;H2 regression: VIIRS → Deposit decline (instrumental variable approach)



&nbsp;H3 analysis: Shadow banking timing (quarterly lags)



&nbsp;H4 analysis: Spatial contagion (spatial lag models)



&nbsp;Robustness checks and sensitivity analysis



Key Findings (Data Inspection Phase)

Merge Feasibility Assessment

RBI Districts (n=762):



Standardized naming convention (UPPERCASE, hyphenated)



Quarterly frequency (2015-2024 expected after concatenation)



Complete deposit data across 4 population groups



Ready for district-level merge



EM-DAT Floods (n=69 events, 147 unique districts):



Geographic precision heterogeneous:



35 events (50.7%) have district-level Admin Units data



34 events (49.3%) have state-level only (requires fallback strategy)



Treatment/control split: ~150 treated districts, ~600 control districts (good for identification)



Merge strategy:



District-level events: Direct fuzzy match to RBI districts



State-level events: Map to all districts in that state (measurement error acknowledged)



VIIRS Coverage:



Single tile covers entire India (no mosaicking required)



Spatial resolution sufficient for city-level economic activity detection



Ready for district-level aggregation via spatial overlay



Data Quality Issues Identified

District Name Spelling Mismatches (EM-DAT vs RBI):



Example: "Belgaum" (EM-DAT) vs "BELAGAVI" (RBI)



Example: "Cuddapah" (EM-DAT) vs likely "KADAPA" (RBI)



Solution: Fuzzy string matching (Levenshtein distance) + manual verification



Geographic Measurement Error:



34 EM-DAT events (49.3%) only specify state, not district



Coding all districts in a state as "flooded" creates false positives



Implication: Attenuation bias in H1 (treatment effects diluted)



Paper disclosure: "Flood exposure measured at district level where available (51%), state level otherwise (49%) due to EM-DAT data structure"



EM-DAT Location Text Parsing Required:



Some events have district names in Location field but empty Admin Units JSON



Example: "Itanagar district (Arunachal Pradesh)" → Need to extract "Itanagar"



Solution: Regex parsing + manual verification for 34 events



VIIRS NoData Encoding:



No explicit NoData value in metadata



Need to check for negative values or -999.9 during processing



Ocean pixels expected to have very low radiance (near 0)



Research Design Validation

✓ H1 Testable: Flood-VIIRS linkage feasible at district level

✓ H2 Testable: VIIRS radiance has sufficient variance (0-57 nW/cm²/sr range, right-skewed distribution)

✓ H3 Testable: Quarterly RBI data enables timing analysis (shadow banking lag identification)

✓ H4 Testable: District IDs enable spatial adjacency matrix construction (district borders from GADM)



Critical validation: If VIIRS tile had been corrupted or RBI had <500 districts, the paper would not be viable. All three datasets are production-ready.



Replication Instructions

Phase 1: Environment Setup (30 minutes)

bash

\# Clone repository

git clone https://github.com/\[username]/Climate-Migration-Bank-Fragility.git

cd Climate-Migration-Bank-Fragility



\# Create conda environment

conda create -n research\_env python=3.10

conda activate research\_env



\# Install dependencies

conda install pandas numpy geopandas rasterio statsmodels matplotlib seaborn openpyxl scipy shapely fiona

Phase 2: Data Download (Manual - 2 hours)

Step 1 - RBI Data:



Visit: https://rbi.org.in/Scripts/AnnualPublications.aspx



Download "District-wise Deposits and Credit (BSR-2)" for:



2004-2017 (historical baseline)



2017-2022 (mid-period)



2023-2024 (recent)



Place in 01\_Data\_Raw/RBI\_Bank\_Data/



Step 2 - EM-DAT Data:



Visit: https://www.emdat.be/



Create account (free for academic use)



Request custom data: Country=India, Disaster Type=Flood, Period=2015-2024



Download Excel file, place in 01\_Data\_Raw/EMDAT\_Disasters/



Step 3 - VIIRS Data:



Visit: https://eogdata.mines.edu/nighttime\_light/monthly/v10/



Download Tile 75N060E for Jan 2015 - Dec 2024 (120 files)



Extract .avg\_rade9h.tif files, place in 01\_Data\_Raw/VIIRS\_NightLights/



Total download: ~240 GB, ~2 hours on fast connection



Phase 3: Data Inspection (15 minutes)

bash

\# Activate environment

conda activate research\_env



\# Run inspection scripts

python 04\_Code/02\_inspect\_rbi.py

python 04\_Code/03\_inspect\_emdat.py

python 04\_Code/04\_inspect\_viirs.py

Expected output: Confirmation that 762 districts (RBI), 69 floods (EM-DAT), and India coverage (VIIRS) are validated.



Phase 4: Data Processing (To Be Implemented)

bash

\# Clean and merge datasets

python 04\_Code/05\_clean\_rbi.py        # Concatenate RBI files, create quarterly panel

python 04\_Code/06\_clean\_emdat.py      # Parse Location text, harmonize district names

python 04\_Code/07\_aggregate\_viirs.py  # District-level VIIRS aggregation

python 04\_Code/08\_merge\_panel.py      # Final merged dataset



\# Output: 02\_Data\_Clean/merged\_panel.csv

Phase 5: Analysis (To Be Implemented)

bash

\# Test hypotheses

python 04\_Code/09\_h1\_regression.py    # Floods → VIIRS (diff-in-diff)

python 04\_Code/10\_h2\_regression.py    # VIIRS → Deposits (IV regression)

python 04\_Code/11\_h3\_analysis.py      # Shadow banking timing

python 04\_Code/12\_h4\_spatial.py       # Spatial contagion



\# Outputs: 05\_Outputs/Tables/\*.txt, 05\_Outputs/Figures/\*.png

Methodology Notes

Identification Strategy

H1 (Floods → VIIRS):



Design: Difference-in-differences with staggered treatment



Treatment: District experienced flood in quarter t (binary)



Control group: Districts with no floods in study period



Specification: VIIRS\_it = β1·Flood\_it + α\_i + γ\_t + ε\_it



Challenge: Measurement error from state-level events (49% of sample)



H2 (VIIRS → Deposits):



Design: Instrumental variable (flood as instrument for VIIRS decline)



First stage: Flood → VIIRS decline (H1)



Second stage: Predicted VIIRS → Deposit decline



Validity: Floods affect deposits only through economic activity (exclusion restriction)



H3 (Shadow Banking):



Design: Event study around deposit decline timing



Outcome: Shadow banking indicators (if available from RBI)



Alternative: Deposit composition shifts (rural vs urban)



H4 (Spatial Contagion):



Design: Spatial lag model with district adjacency matrix



Specification: Deposit\_it = ρW·Deposit\_it + β·X\_it + ε\_it



W matrix: Row-standardized contiguity matrix (GADM district boundaries)



Measurement Error Disclosure

Geographic precision limitation:



51% of flood events matched at district level (precise)



49% of flood events matched at state level (all districts coded as treated)



Consequence: Classical measurement error → Attenuation bias in H1



Robustness check: Separate regressions for district-only vs full sample



Timeline

Phase	Period	Status	Deliverables

3a - Data Download	Jan 2, 2026	✅ Complete	RBI (3 files), EM-DAT (1 file), VIIRS (1 test tile)

3c - Data Inspection	Jan 8, 2026	✅ Complete	3 inspection scripts, merge feasibility confirmed

3c - Data Harmonization	Jan 9, 2026	🚧 In Progress	District crosswalk, Location parsing

3d - Full Data Download	Jan 9-12, 2026	⏳ Pending	119 VIIRS tiles (~230 GB)

3d - Data Cleaning	Jan 12-13, 2026	⏳ Pending	Clean RBI, EM-DAT, VIIRS; create merged panel

4 - Analysis	Jan 13-20, 2026	⏳ Pending	H1-H4 regressions, robustness checks

5 - Writing	Jan 20-31, 2026	⏳ Pending	First draft manuscript

Citation

If you use this code, data, or methodology, please cite:



text

\[Author Name]. (2026). Climate Change, Migration, and Banking Sector Fragility in India: 

Evidence from District-Level Panel Data. Working Paper. \[Institution].

License

This project is for academic research purposes. Data sources retain their original licenses:



RBI data: Public domain (Government of India)



EM-DAT data: Academic use license (Centre for Research on Epidemiology of Disasters)



VIIRS data: Public domain (NASA/NOAA Earth Observation Group)



Code is released under MIT License for academic replication.



Contact

Researcher: \[Your Name]

Email: \[Your Email]

Institution: \[Your Institution]

GitHub: https://github.com/\[username]/Climate-Migration-Bank-Fragility



Project Start: December 30, 2025

Last Updated: January 8, 2026, 10:03 PM IST

Phase: 3c (Data Inspection - Day 1 Complete)

