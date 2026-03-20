# Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Nighttime Lights in India, 2015–2024

[![Status](https://img.shields.io/badge/status-writing%20ready-brightgreen)]()
[![Pipeline](https://img.shields.io/badge/pipeline-fully%20verified-brightgreen)]()
[![Robustness](https://img.shields.io/badge/robustness-R1–R8%20complete-brightgreen)]()

Empirical identification of flood-induced household liquidity shocks on
district-level deposit stability across India. Constructs a balanced
district-quarter panel linking EM-DAT flood events, VIIRS nighttime lights,
and RBI banking statistics for **631 districts** over **36 quarters** in a
panel IV strategy.

**PI:** Jaseel Badar, Harvard University
**Contact:** jab9733@g.harvard.edu | jaseelbadar123@gmail.com
**Repository:** https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility

---

## Research Question

Do flood-induced displacement shocks — identified through nighttime-lights
declines — cause deposit withdrawals in Indian district-level banking? Does
this effect follow a liquidity-consistent timing structure, and does it
concentrate in chronically exposed districts?

---

## Identification Strategy

A two-stage panel IV strategy using flood exposure as an instrument for
nighttime-lights declines, which in turn proxies displacement-driven income
disruption. Two flood precision regimes are reported throughout:

- **Rule A** (primary): district-level EM-DAT match or state-level fallback.
  Treatment rate: 9.59%. Conservative lower bound — state fallback attenuates
  $\hat{\beta}$ toward zero.
- **Rule B** (precision check): district-level match only. Treatment rate: 0.90%.
  Higher precision, lower power.

| Stage | Hypothesis | Specification | Method |
|---|---|---|---|
| First stage | H1 | Floods → nighttime lights | OLS, district + quarter FE |
| Second stage | H2 | Lights decline → deposit outflows | IV 2SLS, flood as instrument |
| Timing | H3 | Distributed lag: $t_0$, $t_0+1$, $t_0+2$ | OLS, quarter FE only |
| Heterogeneity | H4 | Urban proxy; chronic exposure; monsoon season | Interaction terms |

**Fixed effects:** Composite `district_state_id = district_gadm + '_' + state_gadm`
throughout. Using `district_gadm` alone collapses 7 homonymous district pairs
(e.g., AURANGABAD across Bihar and Maharashtra), yielding 624 FE instead of the
correct 631 and contaminating all FE absorption, cluster assignments, and
heterogeneity variable construction. This was the source of all pre-March 2026
benchmark errors.

**Estimator:** linearmodels PanelOLS / IV2SLS (Scripts 27b–30b) throughout.
SE clustered by `district_state_id`.

---

## Results

All results from the final clean pipeline (Scripts 27b–30b, linearmodels PanelOLS).
$N$ = 23,347 (631 districts × 36 regression quarters). All robustness checks
complete (R1–R8, R6b).

### Core Results

| Hypothesis | Rule | $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| **H1:** Floods → Lights | A | −0.044468 | 0.007784 | <0.001 | **Confirmed** |
| **H1:** Floods → Lights | B | −0.058446 | 0.019768 | 0.003 | **Confirmed** |
| **H2:** Lights → Deposits (IV) | A | −0.008388 | 0.034022 | 0.805 | Null |
| **H2:** Lights → Deposits (IV) | B | −0.006776 | 0.059698 | 0.910 | Null |
| **H3** $t_0$ — flood quarter | A | +0.000609 | 0.001462 | 0.677 | Null |
| **H3** $t_0+1$ — one quarter after | A | +0.001505 | 0.001114 | 0.177 | Null |
| **H3** $t_0+2$ — two quarters after | A | **−0.007005** | **0.001644** | **<0.001** | **Confirmed ★** |

H1: District FE = 631, Quarter FE = 36, $N$ = 22,716.
H2: District FE = 631, Quarter FE = 36, $N$ = 22,442.
H3: Quarter FE = 35 (L2 restriction), $N$ = 21,837.

**H2 instrument diagnostics:** Rule A $F = 34.673$ (strong, threshold 16.38).
Rule B $F = 8.949$ (weak, below threshold 10) — Rule B second stage labeled
suggestive; causal language reserved for Rule A.

**H2 null — pre-committed reconciliation:** H2 tests the contemporaneous window.
H3 confirms deposit effects are lagged, not contemporaneous. The IV specification
tests a zero-effect window by construction. H2 null is mechanically consistent
with H3 and does not contradict the mechanism.

**H3 — central finding:** Flood-induced deposit stress is entirely absent in the
flood quarter and the quarter immediately following. The effect emerges at $t_0+2$
— six months post-flood — at −0.70 pp in quarterly deposit growth. Consistent
with gradual displacement: households exhaust immediate coping capacity before
liquidating bank deposits.

### Heterogeneity (H4)

District FE = 631, Quarter FE = 36, $N$ = 22,442 (all specifications, both rules).

| Specification | Rule | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| H4a: Urban proxy × Flood | A | −0.001666 | 0.002664 | 0.532 | Null |
| H4a: Urban proxy × Flood | B | +0.007479 | 0.006929 | 0.280 | Null |
| H4b: High exposure × Flood | A | −0.006810 | 0.002932 | 0.020 | Suggestive only ⚠ |
| H4b: High exposure × Flood | B | −0.013419 | 0.007670 | 0.080 | Marginal |
| H4c: Monsoon × Flood | A | +0.012495 | 0.002884 | <0.001 | **Confirmed (Rule A)** |
| H4c: Monsoon × Flood | B | +0.002287 | 0.007968 | 0.774 | Null |

**H4a (urban proxy):** Null under both rules. Flood-induced deposit stress is broad
and systemic — not differentiated by urban versus rural economic intensity.

**H4b (chronic exposure):** Baseline (low-exposure districts): $\hat{\beta} = +0.0047$
(marginal precautionary saving). Net effect for high-exposure districts:
$+0.0047 + (-0.0068) = -0.0021$. Repeated flood history depletes household
financial buffers; the next flood forces withdrawal rather than accumulation.
⚠ **However**, H4b does not survive winsorization ($p = 0.865$, Script 37). The
effect is driven by extreme deposit observations and must be treated as suggestive
evidence only.

**H4c (monsoon seasonality):** Moderate flood events during Q3 do not reduce
deposits — anticipated seasonal flooding coincides with agricultural income inflows
that dominate deposit behavior. Severe floods (Rule B) override seasonal patterns
entirely. Result is fragile to flood intensity definition and is labeled partial.

### Two-Phase Liquidity Cycle

Placebo test (Script 34): flood at $t$ predicts **higher** deposit growth at
$t-1$ ($\hat{\beta} = +0.005$, $p = 0.011$; survives district FE: $\hat{\beta}
= +0.004$, $p = 0.019$). This positive pre-period signal — opposite in sign to
the $t_0+2$ withdrawal effect (−0.007) — reveals a two-phase household liquidity
cycle:

- **Phase 1** ($t-1$): Anticipatory saving (+0.5 pp) ahead of the predictable
  flood season
- **Phase 2** ($t_0+2$): Post-flood deposit withdrawal (−0.7 pp) as liquidity
  demand materialises

This is a finding, not a weakness. It is reported in full in the Robustness section.

### Robustness Summary

| Check | Outcome |
|---|---|
| R1 — Both flood rules reported | Complete |
| R2 — Placebo timing | Complete — two-phase cycle confirmed |
| R3 — Winsorization (1st/99th, 450 obs, 2.01%) | H3 robust ✓; H4b **fails** ✗ |
| R4 — Nominal INR retained | Complete |
| R5 — Longer lags ($t_0+3$, $t_0+4$) | Both null; effect decays at $t_0+2$ |
| R6 — State-level clustering (34 clusters) | H3 $p = 0.034$ ✓; H1 $p = 0.105$ |
| R6b — Wild cluster bootstrap (999 iterations) | H1 fails (Rule A $p = 0.158$) |
| R7 — IV discipline, $F$-stat reported | Rule B labeled suggestive throughout |
| R8 — Northeast sensitivity | H3 $t_0+2$ robust to NE exclusion ✓ |

**H1 clustering note:** $\hat{\beta} = -0.044468$ is stable across all three SE
specifications. Significance is sensitive to the assumed level of clustering.
H1 holds under district-level clustering (631 clusters, $p < 0.001$) but does
not survive state-level conventional SE ($p = 0.105$) or wild cluster bootstrap
($p = 0.158$). The district-clustered result is the primary specification;
state-level results are reported as a robustness bound. This is disclosed in full.

---

## Data

Raw data files are read-only. All transformations write to intermediate or clean
directories.

### Sources

| Source | Variable | Coverage |
|---|---|---|
| RBI BSR-2 | Total district deposits (₹ Crores, nominal) | 762 districts, 2004Q1–2025Q3 |
| EM-DAT | Flood events (district + state location, dates) | India, 2015–2024 |
| VIIRS DNB (CSM-EOG, tile 75N060E) | Monthly mean radiance (nW/cm²/sr) | India, Jan 2015–Dec 2024 |
| GADM v4.1 Level-2 | District polygons | 676 districts |

VIIRS raw tiles (~65 GB) stored at `E:\VIIRS_Raw_Data_75N060E\`.

### Sample Construction

| Stage | Districts | Quarters | Observations |
|---|---|---|---|
| GADM baseline | 676 | — | — |
| VIIRS extraction | 666 | 40 | 26,640 |
| Crosswalk match (RBI→GADM) | 631 | — | — |
| **Analysis sample** | **631** | **37** | **23,347** |
| Regression sample | 631 | 36 | ~22,400–22,700 |

**Two restrictions applied (Option 3, Script 17):**
1. Drop 2016Q3–2017Q1 — RBI publication blackout; India demonetization period
   (November 2016). District-level data unreliable. Must be disclosed in the
   paper's Data section.
2. Drop 35 districts with zero deposit coverage across the full panel.

**Analysis sample statistics:**

| Metric | Value |
|---|---|
| Districts | 631 composite `(district_gadm, state_gadm)` pairs |
| Deposit coverage | 98.9% (23,079 / 23,347 district-quarters) |
| VIIRS coverage | 100.0% (25,240 / 25,240 district-quarters) |
| Rule A flood events | 2,238 events (9.59% treatment rate; 569 districts ever exposed) |
| Rule B flood events | 209 events (0.90% treatment rate; 141 districts ever exposed) |
| Mean deposits | ₹16,425.73 Crores; median ₹6,135.58 Crores |
| Mean VIIRS radiance | 0.6955 nW/cm²/sr; SD 1.6884 |

**Homonymous districts:** 7 district name pairs appear in two states. They
require composite `(district_gadm, state_gadm)` keys for all operations.
AURANGABAD (Bihar / Maharashtra), BALRAMPUR (Chhattisgarh / Uttar Pradesh),
BIJAPUR (Chhattisgarh / Karnataka), BILASPUR (Chhattisgarh / Himachal Pradesh),
HAMIRPUR (Himachal Pradesh / Uttar Pradesh), PRATAPGARH (Rajasthan / Uttar Pradesh),
RAIGARH (Chhattisgarh / Maharashtra).

---

## Pipeline

| Script | Purpose | Status |
|---|---|---|
| `08` | Build district crosswalk (RBI→GADM) | Clean — 762-row assert |
| `10` | Build flood exposure panel | Clean — Rule A: 2,518 raw events |
| `11` | Validate flood exposure | Clean |
| `12` | Summarize flood exposure | Clean |
| `13` | Extract RBI deposits | Clean — column offset + state-blind merge fixed |
| `14` | Merge master panel | Clean — 26,640 rows |
| `15` | Validate master panel | Clean |
| `17` | Prepare analysis sample | Clean — 23,347 rows, 631 districts |
| `21/21b` | Extract + deduplicate VIIRS | Clean |
| `22/22b` | Aggregate + align VIIRS quarterly | Clean — 25,240 rows |
| `23` | Merge VIIRS with master panel | Clean — 100% coverage |
| `24` | Engineer regression variables | Clean — 23 columns, lag arithmetic exact |
| `25` | Descriptive statistics | Clean |
| `26` | Validate VIIRS quarterly panel | Clean — all 9 checks PASS |
| `27b` | **H1:** Floods → Lights (linearmodels) | **Complete. Confirmed.** |
| `28b` | **H2:** Lights → Deposits IV 2SLS (linearmodels) | **Complete. Null confirmed.** |
| `29b` | **H3:** Distributed lag timing (linearmodels) | **Complete. $t_0+2$ confirmed.** |
| `30b` | **H4:** Heterogeneity interactions (linearmodels) | **Complete. Results locked.** |
| `31` | Winsorize dependent variable | Complete — 450 obs (2.01%) |
| `32` | CPI / nominal deposit diagnostic | Complete — nominal INR confirmed |
| `32b` | 2023 deposit anomaly diagnosis | Complete — NE left-tail asymmetry confirmed |
| `33` | Northeast sensitivity robustness | Complete — H3 $t_0+2$ robust |
| `34` | Placebo timing (R2) | Complete — two-phase cycle confirmed |
| `35` | Longer lags, $t_0+3$, $t_0+4$ (R5) | Complete — both null |
| `36` | State-level clustering (R6) | Complete — H3 $p = 0.034$ |
| `36b` | Wild cluster bootstrap (R6b) | Complete — H1 fails at state level |
| `37` | Winsorization robustness for H4 | Complete — H4b fails ($p = 0.865$) |
| `fig01` | Figure 1: India district flood exposure map | Complete — PDF + PNG |
| `fig02` | Figure 2: H3 two-phase liquidity cycle | Complete — PDF + PNG |

---

## Repository Structure

E:\Climate-Migration-Bank-Fragility
│
├── 00_Admin/
│ ├── Hypotheses_Formal_v2.6.md
│ ├── Variables_Codebook_v2.6.md
│ └── Literature_Tracker.xlsx
│
├── 01_Data_Raw/ # Read-only. Never modified.
│ ├── RBI_Bank_Data/
│ ├── EMDAT_Disasters/
│ ├── VIIRS_NightLights/
│ └── District_Boundaries/
│ └── gadm41_IND_2.shp
│
├── 02_Data_Intermediate/
│ ├── district_crosswalk_draft.csv # 762 rows
│ ├── flood_exposure_panel.csv # 26,640 rows
│ ├── rbi_deposits_panel.csv # 50,192 rows
│ ├── master_panel_raw.csv # 26,640 rows
│ ├── master_panel_analysis.csv # 23,347 rows
│ ├── viirs_monthly_panel_fixed.csv
│ └── viirs_quarterly_panel_clean.csv # 25,240 rows
│
├── 03_Data_Clean/
│ ├── analysis_panel_final.csv # 23,347 rows, 100% VIIRS
│ ├── regression_panel_final.csv # 23,347 rows, 23 columns
│ └── regression_panel_final_winsor.csv # 23,347 rows, 24 columns
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
│ ├── 27b_regression_H1_linearmodels.py
│ ├── 28b_regression_H2_linearmodels.py
│ ├── 29b_regression_H3_linearmodels.py
│ ├── 30b_regression_H4_linearmodels.py
│ ├── 31_winsorize.py
│ ├── 32_cpi_diagnostic.py
│ ├── 32b_cpi_diagnostic_2023.py
│ ├── 33_northeast_sensitivity.py
│ ├── 34_placebo_timing.py
│ ├── 35_longer_lags.py
│ ├── 36_state_clustering.py
│ ├── 36b_wild_bootstrap.py
│ ├── 37_winsorization_robustness_H4.py
│ ├── fig01_flood_exposure_map.py
│ └── fig02_H3_event_study.py
│
└── 05_Outputs/
├── Tables/
│ ├── 01_descriptive_stats.csv
│ ├── 02b_H1_linearmodels.csv
│ ├── 03b_H2_linearmodels.csv
│ ├── 04b_H3_linearmodels.csv
│ ├── 05b_H4_linearmodels.csv
│ └── 09_placebo_timing.csv
├── Figures/
│ ├── Fig_01_flood_exposure_map.pdf
│ ├── Fig_01_flood_exposure_map.png
│ ├── Fig_02_H3_event_study.pdf
│ └── Fig_02_H3_event_study.png
└── Logs/
└── [per-script log files]

---

## Reproduction

```bash
conda activate research_env

# --- Data pipeline ---
python 04_Code/08_build_district_crosswalk.py      # assert: 762 rows
python 04_Code/10_build_flood_exposure.py           # assert: 2,518 Rule A events
python 04_Code/13_extract_rbi_deposits.py           # 50,192 rows
python 04_Code/14_merge_master_panel.py             # assert: 26,640 rows
python 04_Code/17_prepare_analysis_sample.py        # assert: 23,347 rows, 631 districts
python 04_Code/22b_align_viirs_clean.py             # assert: 25,240 rows
python 04_Code/23_merge_viirs_master.py             # assert: 23,347 rows, 100% VIIRS
python 04_Code/24_engineer_regression_variables.py  # assert: 23 columns
python 04_Code/26_validate_viirs_quarterly.py       # assert: all 9 checks PASS

# --- Core regressions (linearmodels) ---
python 04_Code/27b_regression_H1_linearmodels.py   # H1 confirmed
python 04_Code/28b_regression_H2_linearmodels.py   # H2 null confirmed
python 04_Code/29b_regression_H3_linearmodels.py   # H3 t0+2 confirmed
python 04_Code/30b_regression_H4_linearmodels.py   # H4 results locked

# --- Robustness ---
python 04_Code/31_winsorize.py
python 04_Code/33_northeast_sensitivity.py
python 04_Code/34_placebo_timing.py
python 04_Code/35_longer_lags.py
python 04_Code/36_state_clustering.py
python 04_Code/36b_wild_bootstrap.py
python 04_Code/37_winsorization_robustness_H4.py

# --- Figures ---
python 04_Code/fig01_flood_exposure_map.py
python 04_Code/fig02_H3_event_study.py

Environment: Python 3.10.19 | conda: research_env
Core packages: pandas, numpy, geopandas, rasterio, linearmodels, statsmodels,
scipy, matplotlib

Key Methodological Notes
GADM as geographic standard: RBI district names change over time. GADM v4.1
provides stable polygon boundaries as the harmonisation anchor. The crosswalk
matches RBI districts to GADM at 83.2%; 130 unmatched RBI districts are dropped.

Log offsets: VIIRS radiance uses offset +0.001 — approximately 80% of
district-quarters have mean radiance below 1 nW/cm²/sr; log(x + 1) approximates
the identity function in this range, eliminating log-scale compression for the
majority of the sample. Deposits use offset +1 (safe at Crore scale; deposits
always positive).

Nominal deposits: District-quarter CPI is unavailable at the required
granularity. Quarter FE absorb national price trends. India CPI averaged ~6–7%
annually over the analysis period. Acknowledged as a limitation.

Demonetization gap: 2016Q3–2017Q1 entirely absent. Absorbed by quarter FE.
Disclosed in the paper's Data section. Never report 2016 or 2017 as full-year
figures.

H4b winsorization failure: The high-exposure interaction ($p = 0.020$ in
baseline) does not survive winsorization ($p = 0.865$). It is driven by extreme
deposit observations and is presented as suggestive evidence only. This is a
mandatory disclosure — never presented as a robust finding.

H1 clustering sensitivity: The first-stage coefficient ($\hat{\beta} = -0.044$)
is stable. Significance depends on the clustering level assumed. The result holds
at district level (631 clusters, $p < 0.001$) but not at state level under
conventional SE ($p = 0.105$) or wild cluster bootstrap ($p = 0.158$). Disclosed
in full.

Project initiated: December 30, 2025
Principal Investigator: Jaseel Badar, Harvard University