**VARIABLES CODEBOOK**    
**Climate Migration, Night Lights, and Bank Fragility in India (2015-2024)**    
**Draft Version 1.0 | January 7, 2026**  
  
***  
  
## I. PANEL STRUCTURE  
  
**Unit of Analysis**: Indian District (administrative level)    
**Expected N**: ~640 districts (verify exact count from RBI data tomorrow)  
  
**Time Dimension**: Quarterly (2015Q1 to 2024Q4)    
**Expected T**: 40 quarters    
**Expected Observations**: ~25,600 district-quarters  
  
**Panel Type**: Balanced (if all districts report all quarters) or Unbalanced (if some districts missing quarters - RBI data will determine this)  
  
**Key Index Variables**:  
- `district_id`: Unique district identifier (construct from RBI district names, ensure consistent across years)  
- `state_code`: State identifier (for state fixed effects)  
- `quarter`: Time variable (format: 2015Q1, 2015Q2, etc.)  
- `year`: Calendar year (2015-2024)  
- `quarter_num`: Sequential time index (1 to 40, for panel regressions)  
  
***  
  
## II. OUTCOME VARIABLES (Dependent Variables - Bank Stress Measures)  
  
### A. Deposit Variables  
  
**Variable**: `total_deposits_qt`    
**Definition**: Total aggregate deposits in district i, quarter t (all scheduled commercial banks)    
**Unit**: Indian Rupees (crores)    
**Source**: RBI District-Level Deposit Statistics (Statement No. 4)    
**Construction**: Direct extraction from RBI Excel files    
**Time**: Quarterly    
**Critical Issue**: Verify if RBI reports nominal or real values. If nominal, deflate using CPI (source: MOSPI).  
  
**Variable**: `log_deposits_qt`    
**Definition**: Natural logarithm of total deposits    
**Unit**: Log points    
**Source**: Constructed from `total_deposits_qt`    
**Construction**: `log_deposits_qt = ln(total_deposits_qt)`    
**Why Log**: Handles skewness, allows interpretation as percentage changes, standard in banking literature.  
  
**Variable**: `deposit_change_qt`    
**Definition**: Quarter-over-quarter change in log deposits    
**Unit**: Log points (≈ percentage change for small values)    
**Source**: Constructed    
**Construction**: `deposit_change_qt = log_deposits_qt - log_deposits_qt-1`    
**Interpretation**: A value of -0.10 means deposits fell approximately 10% from previous quarter.    
**Missing Data Rule**: First quarter per district will be missing (no t-1). Drop or use forward fill? DECIDE TOMORROW.  
  
**Variable**: `deposit_withdrawal_binary`    
**Definition**: Indicator for sharp deposit decline (shadow run proxy)    
**Unit**: Binary (1 = withdrawal event, 0 = no event)    
**Source**: Constructed    
**Construction**: `deposit_withdrawal_binary = 1 if deposit_change_qt < -0.10, else 0`    
**Threshold Justification**: 10% quarterly decline exceeds normal seasonal variation. VERIFY THIS ASSUMPTION by plotting deposit distribution tomorrow.    
**Alternative Thresholds to Test**: -5%, -15%, -20% (robustness checks)  
  
### B. Bank Branch Variables  
  
**Variable**: `branch_count_qt`    
**Definition**: Number of reporting bank branches in district i, quarter t    
**Unit**: Count (integer)    
**Source**: RBI District Statistics (if available in Statement No. 4 - CHECK TOMORROW)    
**Construction**: Direct extraction    
**Warning**: RBI may only report branch counts annually, not quarterly. If annual, carry forward within year.  
  
**Variable**: `branch_closure_qt`    
**Definition**: Net change in branch count (negative = closures)    
**Unit**: Count (integer, can be negative)    
**Source**: Constructed    
**Construction**: `branch_closure_qt = branch_count_qt - branch_count_qt-1`    
**Hypothesis**: Shadow runs may trigger branch rationalization (closures in stressed districts).    
**Data Availability Risk**: HIGH - RBI may not report branch-level closures. If unavailable, DROP this variable.  
  
### C. Per-Capita Adjustments (Optional - Depends on Population Data)  
  
**Variable**: `deposits_per_capita_qt`    
**Definition**: Total deposits divided by district population    
**Unit**: Rupees per person    
**Source**: Constructed from `total_deposits_qt` and population data    
**Construction**: `deposits_per_capita_qt = total_deposits_qt / population_district`    
**Population Source**: Census 2011 (static) OR annual projections (dynamic - PREFERRED but may not exist at district level)    
**Critical Decision**: If only Census 2011 available, assume constant population 2015-2024 (WEAK ASSUMPTION - flag in paper as limitation).  
  
***  
  
## III. TREATMENT VARIABLES (Independent Variables - Shocks)  
  
### A. Disaster Variables  
  
**Variable**: `flood_exposure_qt`    
**Definition**: Binary indicator for flood occurrence in district i, quarter t    
**Unit**: Binary (1 = flood occurred, 0 = no flood)    
**Source**: EM-DAT Disaster Database    
**Construction**: Match EM-DAT flood dates to quarters. If flood start date falls in quarter t, code as 1.    
**Geographic Matching Issue**: EM-DAT reports state or multi-district regions ("North Kerala"). DECISION NEEDED:    
- Option A: Code flood=1 for ALL districts in mentioned state (overinclusive, may dilute effect)    
- Option B: Code flood=1 only if district name explicitly mentioned (underinclusive, may miss events)    
- Option C: Code flood=1 if district name mentioned OR VIIRS shows lights drop >15% in that quarter (endogeneity risk - lights are outcome variable)    
**RECOMMENDED APPROACH**: Option A for main specification, Option B for robustness check. Document explicitly in paper.  
  
**Variable**: `flood_severity_qt`    
**Definition**: Continuous measure of flood intensity    
**Unit**: Log(deaths + affected population + 1)    
**Source**: EM-DAT (Deaths, Affected Population columns)    
**Construction**: `flood_severity_qt = ln(deaths_qt + affected_pop_qt + 1)` [+1 to handle zeros]    
**Interpretation**: Higher values = more severe disaster    
**Alternative Specifications**: Deaths only, affected population only, or damage estimates (if EM-DAT reports economic losses)  
  
**Variable**: `flood_lag1_qt` and `flood_lag2_qt`    
**Definition**: Lagged flood exposure (t-1 and t-2 quarters)    
**Unit**: Binary    
**Source**: Constructed from `flood_exposure_qt`    
**Construction**: `flood_lag1_qt = flood_exposure_qt-1`    
**Why Lags Matter**: Shadow runs may occur with delay. Test if deposits fall in quarter AFTER flood, not same quarter.  
  
### B. Night Lights Variables (Migration Proxy)  
  
**Variable**: `viirs_brightness_mt`    
**Definition**: Average VIIRS DNB radiance in district i, month t    
**Unit**: nanoWatts/cm²/sr (VIIRS native units)    
**Source**: VIIRS Monthly Composites (avg_rade9h.tif files)    
**Construction**: Extract all pixel values within district polygon boundary, calculate mean.    
**GIS Requirement**: Need district shapefiles (source: GADM or India govt GIS portal - OBTAIN TOMORROW).    
**Cloud Filtering**: Use only cloud-free composite values (cf_cvg.tif threshold >50% cloud-free? DECIDE BASED ON DATA INSPECTION).  
  
**Variable**: `log_viirs_brightness_mt`    
**Definition**: Natural log of VIIRS brightness    
**Unit**: Log(nanoWatts/cm²/sr)    
**Source**: Constructed    
**Construction**: `log_viirs_brightness_mt = ln(viirs_brightness_mt + 0.01)` [small constant to handle near-zero values in rural areas]    
**Why Log**: Standard in night lights literature (Henderson 2012, Chen & Nordhaus 2011), handles right-skewed distribution.  
  
**Variable**: `lights_change_mt`    
**Definition**: Month-over-month change in log brightness    
**Unit**: Log points    
**Source**: Constructed    
**Construction**: `lights_change_mt = log_viirs_brightness_mt - log_viirs_brightness_mt-1`    
**Interpretation**: Negative values indicate dimming (population outflow hypothesis).  
  
**Variable**: `lights_change_qt`    
**Definition**: Quarterly aggregation of lights change (to match RBI frequency)    
**Unit**: Log points    
**Source**: Constructed from monthly data    
**Construction**: `lights_change_qt = (lights_change_m1 + lights_change_m2 + lights_change_m3) / 3` [average of 3 monthly changes within quarter]    
**Alternative Construction**: Use end-of-quarter snapshot instead of average? TEST BOTH APPROACHES.  
  
**Variable**: `migration_proxy_qt`    
**Definition**: Binary indicator for significant brightness decline (migration event)    
**Unit**: Binary (1 = migration detected, 0 = no migration)    
**Source**: Constructed    
**Construction**: `migration_proxy_qt = 1 if lights_change_qt < -0.15, else 0`    
**Threshold Justification**: -15% quarterly lights drop exceeds normal seasonal/agricultural variation. VALIDATE by:    
1. Plot lights distribution in non-flood districts (baseline volatility)    
2. Check if -15% threshold distinguishes flood vs. non-flood districts    
**Critical Weakness**: This is a PROXY, not direct migration measurement. Power outages, industrial shutdowns, agricultural cycles all affect lights. MUST control for these confounds (see Control Variables section).  
  
### C. Interaction Terms (Causal Mechanism Tests)  
  
**Variable**: `flood_x_lights_qt`    
**Definition**: Interaction of flood exposure and lights change    
**Unit**: Continuous (product of binary × continuous)    
**Source**: Constructed    
**Construction**: `flood_x_lights_qt = flood_exposure_qt × lights_change_qt`    
**Hypothesis Test**: If coefficient on this interaction is negative and significant, it confirms floods cause deposit withdrawals THROUGH the migration channel (lights drop), not just direct flood damage.  
  
***  
  
## IV. CONTROL VARIABLES (Confounds)  
  
### A. Weather Controls (Non-Migration Explanations for Lights)  
  
**Variable**: `rainfall_qt`    
**Definition**: Total rainfall in district i, quarter t    
**Unit**: Millimeters    
**Source**: India Meteorological Department (IMD) gridded rainfall data OR district-level reports    
**Construction**: Extract rainfall totals from IMD, match to district boundaries    
**Why Critical**: Heavy monsoon rains cause floods BUT also reduce lights via cloud cover (confound). Must separate flood-induced migration from weather-induced measurement error.    
**Data Availability**: IMD provides 0.25° gridded data. Can be matched to districts using GIS. OBTAIN TOMORROW OR SKIP IF UNAVAILABLE.  
  
**Variable**: `monsoon_quarter`    
**Definition**: Binary indicator for monsoon season (June-September)    
**Unit**: Binary (1 = Q2/Q3, 0 = Q1/Q4)    
**Source**: Constructed from calendar    
**Construction**: `monsoon_quarter = 1 if quarter in {Q2, Q3}, else 0`    
**Why**: Agricultural activity and lights have strong seasonal patterns. Control for this to isolate disaster shocks.  
  
### B. Economic Controls  
  
**Variable**: `gdp_district_annual`    
**Definition**: District-level GDP (if available)    
**Unit**: Rupees (crores) or log(rupees)    
**Source**: TBD - CHECK IF EXISTS    
**Data Availability Risk**: VERY HIGH - India does not publish quarterly district GDP. Annual GDP may exist from some states (e.g., Kerala, Karnataka) but not nationally.    
**Fallback Option**: Use VIIRS brightness as GDP proxy (à la Henderson 2012), but creates circularity problem if lights are also your migration proxy. ALTERNATIVE: Use state-level GDP and interact with district characteristics.  
  
**Variable**: `agriculture_share_static`    
**Definition**: Percentage of workforce in agriculture (district-level)    
**Unit**: Percentage (0-100)    
**Source**: Census 2011 (static variable)    
**Construction**: Direct extraction from Census data    
**Why**: Agricultural districts may have higher flood vulnerability, different banking behavior, and different lights-GDP relationships (subsistence farming has low lights intensity).    
**Limitation**: Static (2011 value used for all years 2015-2024). Agricultural shares likely changed, but no annual data available.  
  
**Variable**: `urbanization_rate_static`    
**Definition**: Percentage of population living in urban areas    
**Unit**: Percentage (0-100)    
**Source**: Census 2011    
**Construction**: Direct extraction    
**Why**: Urban districts have higher bank density, different migration patterns (may receive flood refugees from rural areas), higher baseline lights intensity.  
  
### C. Banking Structure Controls  
  
**Variable**: `bank_density_qt`    
**Definition**: Number of bank branches per 100,000 population    
**Unit**: Branches per 100k population    
**Source**: Constructed from RBI branch counts and population    
**Construction**: `bank_density_qt = (branch_count_qt / population_district) × 100000`    
**Hypothesis**: Higher bank density may provide resilience (more liquidity sources) OR vulnerability (more withdrawal points).  
  
**Variable**: `public_bank_share_qt`    
**Definition**: Percentage of deposits in public sector banks (vs. private banks)    
**Unit**: Percentage (0-100)    
**Source**: RBI (if Statement No. 4 disaggregates by bank type - CHECK TOMORROW)    
**Why**: Public banks may be more stable during disasters (govt implicit guarantee), affecting deposit behavior.    
**Data Availability**: UNCERTAIN - RBI may only report aggregate deposits. If unavailable, DROP.  
  
***  
  
## V. NETWORK VARIABLES (Contagion Mechanisms)  
  
### A. Spatial Network  
  
**Variable**: `spatial_distance_ij`    
**Definition**: Geographic distance between district i and district j centroids    
**Unit**: Kilometers    
**Source**: Constructed using GIS    
**Construction**: Calculate Euclidean distance between district polygon centroids    
**Use**: Spatial spillover regressions (test if nearby floods affect deposits in non-flooded districts)    
**Data Structure**: This creates a 640×640 distance matrix, not a panel variable. Used in network regression specifications.  
  
**Variable**: `spatial_adjacency_ij`    
**Definition**: Binary indicator for shared border    
**Unit**: Binary (1 = districts share border, 0 = no border)    
**Source**: Constructed using GIS    
**Construction**: Check if district polygons intersect    
**Use**: Test if contiguous districts show correlated deposit shocks (geographic contagion).  
  
### B. Banking Network  
  
**Variable**: `shared_banks_ij`    
**Definition**: Count of banks operating in BOTH district i and district j    
**Unit**: Count (integer)    
**Source**: Constructed from RBI branch data (if bank-level data available)    
**Construction**: For each pair of districts, count banks with branches in both    
**Hypothesis**: Districts connected via same banks may experience contagion (District A flood → Bank withdrawals → Bank reduces lending in District B).    
**Data Availability Risk**: HIGH - Requires bank-level branch locations, not just aggregate counts. RBI *may* provide this in detailed annexures. CHECK TOMORROW.  
  
**Variable**: `bank_connectedness_i`    
**Definition**: Number of other districts connected to district i via shared banks    
**Unit**: Count    
**Source**: Constructed from `shared_banks_ij` matrix    
**Construction**: For district i, count how many other districts share at least 1 bank    
**Interpretation**: Higher values = more integrated into banking network = higher contagion risk.  
  
***  
  
## VI. CONSTRUCTED INDICES (Advanced Variables)  
  
**Variable**: `flood_risk_index_static`    
**Definition**: Historical flood frequency (2000-2014 baseline, pre-sample)    
**Unit**: Count of floods per year    
**Source**: EM-DAT historical data (request earlier years from EM-DAT if not already downloaded)    
**Construction**: Count floods in district 2000-2014, divide by 15 years    
**Use**: Control for time-invariant flood proneness. Districts with high historical risk may have adapted (better drainage, flood insurance), affecting deposit behavior.  
  
**Variable**: `financial_inclusion_static`    
**Definition**: Percentage of population with bank accounts    
**Unit**: Percentage (0-100)    
**Source**: RBI Financial Inclusion Index OR Census 2011 banking access data    
**Why**: Districts with low banking penetration may show different deposit dynamics (fewer people have deposits to withdraw).    
**Data Availability**: RBI publishes state-level inclusion metrics. District-level exists in some reports but may be incomplete.  
  
***  
  
## VII. DATA SOURCES SUMMARY  
  
| Dataset | Variables Provided | Time Coverage | Geographic Unit | File Format | Status |  
|---------|-------------------|---------------|-----------------|-------------|--------|  
| **RBI District Deposits** | total_deposits, branch_count (maybe), bank types (maybe) | 2004-2024 quarterly | District (~640) | Excel (.xls/.xlsx) | ✅ Downloaded (3 files) |  
| **EM-DAT Disasters** | flood_exposure, deaths, affected_pop, dates, locations | 2015-2024 | State/district (inconsistent) | Excel (.xlsx) | ✅ Downloaded (70 events) |  
| **VIIRS Night Lights** | viirs_brightness (avg_rade9h) | 2012-present monthly | 15 arc-second pixels | GeoTIFF (.tif) | ⚠️ 1 month downloaded, need 120 months |  
| **District Shapefiles** | Polygon boundaries for GIS | Static (2011 boundaries) | District | Shapefile (.shp) | ❌ NOT OBTAINED - Priority for tomorrow |  
| **IMD Rainfall** | rainfall_qt | 1901-present daily | 0.25° grid | NetCDF or CSV | ❌ NOT OBTAINED - Medium priority |  
| **Census 2011** | population, agriculture_share, urbanization_rate | 2011 (static) | District | CSV/Excel | ❌ NOT OBTAINED - Low priority (can download as needed) |  
  
***  
  
## VIII. CRITICAL MEASUREMENT DECISIONS (MUST RESOLVE BEFORE CODING)  
  
### Decision 1: Time Granularity  
**Problem**: VIIRS is monthly, RBI is quarterly, EM-DAT is daily.  
  
**Options**:  
- A) Keep VIIRS monthly, match to RBI quarters using leads/lags (complex but retains precision)  
- B) Aggregate VIIRS to quarterly averages (simple, loses timing information)  
  
**RECOMMENDATION**: Start with Option B (quarterly aggregation) for simplicity. If results are weak, try Option A in robustness checks.  
  
**Action Tomorrow**: Write Python function to aggregate monthly VIIRS to quarterly.  
  
***  
  
### Decision 2: Migration Proxy Threshold  
**Problem**: What lights drop threshold defines "migration event"?  
  
**Options**:  
- 10% drop (more events detected, noisier signal)  
- 15% drop (moderate, recommended for baseline)  
- 20% drop (fewer events, higher precision)  
  
**RECOMMENDATION**: Use 15% for main results. Test 10% and 20% as robustness checks. Report all three in Appendix Table.  
  
**Action Tomorrow**: Create three versions of `migration_proxy_qt` with different thresholds.  
  
***  
  
### Decision 3: Flood Geographic Matching  
**Problem**: EM-DAT says "Kerala Flood Aug 2018" but doesn't list exact districts.  
  
**Options**:  
- A) Code flood=1 for entire Kerala (14 districts)  
- B) Manually research which Kerala districts were affected (time-intensive but accurate)  
- C) Use VIIRS to define affected districts (>15% lights drop) - but this is endogenous  
  
**RECOMMENDATION**: Option A for speed, acknowledge limitation in paper. State: "Flood exposure coded at state level due to EM-DAT geographic imprecision. This may attenuate treatment effects."  
  
**Action Tomorrow**: Parse EM-DAT location strings, create state-to-district mapping table.  
  
***  
  
### Decision 4: Deposit Deflation  
**Problem**: Nominal deposits rose 2015-2024 due to inflation (~5-6% annually). This confounds real liquidity changes.  
  
**Options**:  
- A) Use nominal deposits, include year fixed effects (absorbs inflation, standard approach)  
- B) Deflate by CPI (Consumer Price Index, requires downloading CPI data)  
- C) Use log changes (percentage terms, partially handles inflation)  
  
**RECOMMENDATION**: Option A (nominal + year FE) for main spec. Option C already planned via `deposit_change_qt`.  
  
**Action Tomorrow**: Verify RBI deposits are nominal. Include year fixed effects in all regressions.  
  
***  
  
### Decision 5: Sample Period Boundary  
**Problem**: Your hypothesis is about 2015-2024, but VIIRS data starts 2012, RBI data goes back to 2004.  
  
**Options**:  
- A) Use full RBI data 2004-2024 (more observations, but pre-2012 has no VIIRS)  
- B) Restrict to 2015-2024 (cleaner, matches EM-DAT flood sample)  
- C) Use 2012-2024 (max VIIRS coverage)  
  
**RECOMMENDATION**: Option B (2015-2024) for internal consistency. Use 2012-2014 VIIRS data to construct pre-treatment lights trends (placebo test: did deposits already declining before floods?).  
  
**Action Tomorrow**: Filter all datasets to 2015Q1–2024Q4 when merging.  
  
***  
  
## IX. VARIABLE NAMING CONVENTIONS (Coding Standards)  
  
To maintain clean code tomorrow:  
  
**Suffixes**:  
- `_qt` = quarterly variable  
- `_mt` = monthly variable    
- `_static` = time-invariant variable (e.g., Census 2011 values)  
- `_binary` = 0/1 indicator  
- `_log` = natural logarithm  
- `_lag1`, `_lag2` = lagged variables  
  
**Examples**:  
- `deposit_change_qt` (quarterly deposit change)  
- `flood_exposure_lag1_qt` (flood exposure lagged 1 quarter)  
- `agriculture_share_static` (2011 Census agriculture share)  
  
**Forbidden**: Generic names like `var1`, `x`, `temp`, `data_final`. Every variable name must be self-documenting.  
  
***  
  
## X. MISSING DATA PROTOCOL  
  
**Rule 1**: Never drop observations silently. Document all drops.  
  
**Rule 2**: For critical variables (deposits, floods, lights), missing data means DROP that district-quarter.  
  
**Rule 3**: For control variables (rainfall, GDP), missing data options:  
- A) Drop observation (reduces sample size)  
- B) Forward-fill last available value (introduces measurement error)  
- C) Impute with district average (biased if missing not random)  
  
**RECOMMENDATION**: Use Option A (drop) for main results. Use Option B for robustness check with larger sample.  
  
**Action Tomorrow**: Write Python function to generate missingness summary table (% missing for each variable by year).  
  
***  
  
## XI. VARIABLES NOT INCLUDED (Explicitly Rejected)  
  
**Stock Market Data**: Could proxy investor confidence, but not available at district level in India.  
  
**Interest Rates**: RBI district data unlikely to have district-level lending/deposit rates. Rates are set nationally.  
  
**Migration Survey Data**: Census migration data exists but only decadal (2001, 2011). Too coarse for your quarterly analysis.  
  
**Mobile Phone Data**: Ideal migration proxy but proprietary (Airtel, Jio won't share). VIIRS is best available alternative.  
  
**Social Media Activity**: Could proxy population presence but no systematic district-level data.  
  
***  
  
## XII. NEXT STEPS (Tomorrow's Python Workflow)  
  
1. **Inspect RBI Excel files**: Identify exact sheet names, column headers, district name formats → Extract deposits and branch counts → Save as `rbi_clean.csv`  
  
2. **Parse EM-DAT**: Match flood dates to quarters → Create state-to-district flood exposure mapping → Save as `floods_clean.csv`  
  
3. **Test VIIRS extraction**: Load one .tif file → Extract mean brightness for 5 test districts (manually selected) → Verify values are reasonable (not all zeros) → Document extraction process  
  
4. **District name harmonization**: Compare district names in RBI vs. EM-DAT vs. shapefile GIS data → Create crosswalk table for mismatches (e.g., "Bangalore" vs. "Bengaluru") → Save as `district_crosswalk.csv`  
  
5. **Merge feasibility test**: Can you match at least 80% of RBI districts to GIS boundaries? If no, problem. If yes, proceed to full data processing.  
  
***  
  
**END OF CODEBOOK v1.0**  
  
**Document Status**: Draft for review. Update after inspecting raw data tomorrow.    
**Author**: Research Project Lead    
**Date Created**: January 7, 2026    
**Next Review**: January 8, 2026 (post-data inspection)  
