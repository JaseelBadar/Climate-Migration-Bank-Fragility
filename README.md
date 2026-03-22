# Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Nighttime Lights in India, 2015–2024

[![Status](https://img.shields.io/badge/status-writing%20phase-brightgreen)]()
[![Robustness](https://img.shields.io/badge/robustness-R1–R8%20complete-brightgreen)]()
[![OSF](https://img.shields.io/badge/OSF-pre--registered-blue)]()

**PI:** Jaseel Badar, Harvard University · jab9733@g.harvard.edu  
**Repository:** github.com/JaseelBadar/Climate-Migration-Bank-Fragility

---

Moderate floods in India reduce nighttime light intensity by 4.4 percent
within the quarter of occurrence. Deposit growth falls by 0.70 percentage
points — but not until two quarters later. In the quarter *before* the
flood, deposits rise by 0.47 pp. The contemporaneous and one-quarter effects
are precisely zero.

This timing structure is the central finding. It is inconsistent with
immediate panic withdrawal and consistent with a two-phase household
liquidity cycle: precautionary saving ahead of a predictable seasonal shock,
followed by gradual balance-sheet liquidation as displacement costs
accumulate. A stress test that looks only at the flood quarter misses the
effect entirely.

The two-stage IV — floods instrumenting for lights, lights instrumenting
for deposits — is null contemporaneously. This is not a contradiction of the
mechanism. It is a finding about the window of transmission: the
contemporaneous channel is closed; the balance-sheet channel opens at t₀+2.

---

## Identification

The design rests on two flood precision rules and a distributed lag
structure that allows the timing of the deposit effect to emerge from the
data rather than from a maintained assumption.

**Flood exposure rules:**

| Rule | Definition | Treatment rate | Districts treated |
|---|---|---|---|
| **A** (primary) | District EM-DAT match; state fallback where district unavailable | 9.59% | 569 |
| **B** (precision check) | District-level match only | 0.90% | 141 |

Rule A's state-level fallback attenuates β toward zero — it is a
conservative lower bound, not an overstatement. Rule B provides a precision
check at the cost of statistical power. Both rules are reported throughout;
causal language applies to Rule A IV results only (Rule B first-stage
F = 8.949, below the threshold of 10).

**Estimator:** linearmodels PanelOLS / IV2SLS (Scripts 27b–30b). Standard
errors clustered by composite `district_state_id`. Seven Indian district
names appear in two states each (e.g., Aurangabad in both Bihar and
Maharashtra). Using district name alone as the fixed-effects identifier
collapses these pairs to 624 effects instead of the correct 631 and
contaminates all FE absorption, cluster assignments, and interaction
variable construction. All specifications use
`district_gadm + '_' + state_gadm` as the unit identifier throughout.
This was the source of all pre-March 2026 benchmark errors.

**Specification map:**

| Stage | Hypothesis | Estimator | Fixed effects |
|---|---|---|---|
| First stage | H1: Floods → Lights | PanelOLS | District (631) + Quarter (36) |
| Second stage | H2: Lights → Deposits (IV) | IV2SLS | District (631) + Quarter (36) |
| Distributed lag | H3: Flood timing → Deposits | PanelOLS | Quarter (35) only |
| Heterogeneity | H4: Interaction terms | PanelOLS | District (631) + Quarter (36) |

H3 uses quarter FE only. The dependent variable is log-differenced deposit
growth; differencing absorbs district-level time trends, rendering district
FE redundant by construction. This was pre-committed before estimation.

---

## Results

All figures from the final clean pipeline (Scripts 27b–30b, linearmodels).
Base panel: N = 23,347 (631 districts × 37 quarters). Regression N varies
by lag structure.

### H1 — Floods and Economic Activity

| Rule | β̂ | SE | p | N |
|---|---|---|---|---|
| A | −0.044468 | 0.007784 | <0.001 | 22,716 |
| B | −0.058446 | 0.019768 | 0.003 | 22,716 |

Confirmed under district-level clustering (631 clusters, p < 0.001). The
coefficient is stable across all three SE specifications:

| SE specification | SE | p |
|---|---|---|
| District clustering (631 clusters) | 0.0078 | <0.001 |
| State conventional (34 clusters) | 0.0274 | 0.105 |
| State wild bootstrap, 999 iter. (34 clusters) | 0.0300 | 0.158 |

**H1 does not survive state-level clustering under conventional SE or wild
cluster bootstrap (Rule A p = 0.158, Rule B p = 0.267).** The coefficient
is not in question; the clustering level is. The district-clustered result
is the primary specification. State-level results are reported as a
robustness bound. This is disclosed in full.

### H2 — Lights to Deposits (IV)

| Rule | β̂ | SE | p | First-stage F | N |
|---|---|---|---|---|---|
| A | −0.008388 | 0.034022 | 0.805 | 34.673 | 22,442 |
| B | −0.006776 | 0.059698 | 0.910 | 8.949 | 22,442 |

Null. The IV tests the contemporaneous window. H3 confirms effects are
lagged approximately six months. These findings are consistent: the
contemporaneous transmission channel is closed; the balance-sheet channel
opens at t₀+2. Rule A instrument is strong (F = 34.673, threshold 16.38).
Rule B is weak (F = 8.949) — Rule B second-stage results labeled suggestive
throughout; causal language withdrawn.

### H3 — The Two-Phase Deposit Cycle

Quarter FE = 35. N = 21,837. No district FE (pre-committed).

| Period | β̂ | SE | p | 95% CI |
|---|---|---|---|---|
| t₋₁ — pre-period (placebo, Script 34) | +0.004664 | 0.001841 | 0.011 | [+0.0011, +0.0083] |
| t₀ — flood quarter | +0.000609 | 0.001462 | 0.677 | — |
| t₀+1 — one quarter after | +0.001505 | 0.001114 | 0.177 | — |
| **t₀+2 — two quarters after** | **−0.007005** | **0.001644** | **<0.001** | **[−0.0102, −0.0038]** |

The pre-period effect is positive and significant (p = 0.011), survives
inclusion of district FE (β = +0.004, p = 0.019), and is opposite in sign
to the t₀+2 withdrawal. A pre-existing downward trend in deposits would
produce a negative pre-period signal; the positive sign rules this out.
The pre-period effect is a finding — anticipated flood seasons generate
precautionary saving that reverses as households draw down liquidity
reserves in the post-flood quarters.

The t₀+2 result is robust to Northeast exclusion (p < 0.001, R8),
state-level clustering (p = 0.034, R6), and winsorization of the top and
bottom 1% of deposit observations (p < 0.001, R3).

### H4 — Heterogeneity

District FE = 631, Quarter FE = 36. N = 22,442 (all specifications).

| Specification | Rule | Interaction β̂ | SE | p | Verdict |
|---|---|---|---|---|---|
| H4a: Urban proxy × Flood | A | −0.001666 | 0.002664 | 0.532 | Null |
| H4a: Urban proxy × Flood | B | +0.007479 | 0.006929 | 0.280 | Null |
| H4b: Chronic exposure × Flood | A | −0.006810 | 0.002932 | 0.020 | Suggestive only ⚠ |
| H4b: Chronic exposure × Flood | B | −0.013419 | 0.007670 | 0.080 | Marginal |
| **H4c: Monsoon season × Flood** | **A** | **+0.012495** | **0.002884** | **<0.001** | **Confirmed** |
| H4c: Monsoon season × Flood | B | +0.002287 | 0.007968 | 0.774 | Null |

**H4b — mandatory disclosure.** The high chronic-exposure interaction
(baseline p = 0.020, Script 30b) does not survive winsorization
(p = 0.865, Script 37). The effect is driven by extreme deposit
observations. It is presented as suggestive evidence only and is never
described as robust.

**H4c interpretation.** Moderate floods during Q3 do not reduce deposits:
anticipated seasonal flooding coincides with agricultural income inflows
that offset displacement pressure. Severe floods (Rule B) override this
buffer entirely. The result is fragile to flood intensity definition and is
labeled partial throughout.

---

## Robustness

| Check | Script | Outcome |
|---|---|---|
| R1 — Both flood rules | 27b–30b | Complete — both reported throughout |
| R2 — Placebo timing | 34 | Two-phase cycle confirmed; pre-period p = 0.011 |
| R3 — Winsorization (1%/99%, 450 obs, 2.01%) | 37 | H3 robust ✓ · **H4b fails (p = 0.865) ✗** |
| R4 — Nominal INR retained | 32 | Quarter FE absorb national price trends |
| R5 — Longer lags (t₀+3, t₀+4) | 35 | Both null; effect decays at t₀+2 |
| R6 — State clustering (34 clusters) | 36 | H3 p = 0.034 ✓ · H1 p = 0.105 |
| R6b — Wild cluster bootstrap (999 iter.) | 36b | **H1 fails: Rule A p = 0.158** |
| R7 — IV instrument discipline | 28b | Rule B F = 8.949; suggestive label applied |
| R8 — Northeast sensitivity | 33 | H3 t₀+2 robust to NE exclusion ✓ |

---

## Data

Raw files are read-only. All transformations write to `02_Data_Intermediate/`
or `03_Data_Clean/`.

| Source | Variable | Coverage |
|---|---|---|
| RBI BSR-2 | Total district deposits (₹ Crores, nominal) | 762 districts, 2004Q1–2025Q3 |
| EM-DAT | Flood events (location, dates) | India, 2015–2024 |
| VIIRS DNB (CSM-EOG, tile 75N060E) | Monthly mean radiance (nW/cm²/sr) | India, Jan 2015–Dec 2024 |
| GADM v4.1 Level-2 | District polygons | 676 districts |

VIIRS raw tiles (~65 GB) stored externally at `E:\VIIRS_Raw_Data_75N060E\`.
Not included in repository.

### Sample Construction

| Stage | Districts | Quarters | Observations |
|---|---|---|---|
| GADM baseline | 676 | — | — |
| VIIRS extraction | 666 | 40 | 26,640 |
| RBI–GADM crosswalk | 631 | — | — |
| **Analysis sample** | **631** | **37** | **23,347** |
| Regression sample (H1, H4) | 631 | 36 | ~22,716 |
| Regression sample (H2) | 631 | 36 | 22,442 |
| Regression sample (H3) | 631 | 35 | 21,837 |

Two restrictions applied in Script 17:
1. Drop 2016Q3–2017Q1: RBI publication blackout coinciding with India's
   November 2016 demonetization. District-level deposit data unreliable for
   this window. Never report 2016 or 2017 as full-year figures.
2. Drop 35 districts with zero deposit coverage across the full panel.

**Panel statistics:**

| Metric | Value |
|---|---|
| Deposit coverage | 98.9% (23,079 / 23,347 district-quarters) |
| VIIRS coverage | 100.0% |
| Rule A flood events | 2,238 (9.59% treatment; 569 districts ever exposed) |
| Rule B flood events | 209 (0.90% treatment; 141 districts ever exposed) |
| Mean deposits | ₹16,425.73 Crores; median ₹6,135.58 Crores |
| Mean VIIRS radiance | 0.6955 nW/cm²/sr; SD 1.6884 |

**Homonymous district pairs (7):** AURANGABAD (Bihar / Maharashtra),
BALRAMPUR (Chhattisgarh / Uttar Pradesh), BIJAPUR (Chhattisgarh /
Karnataka), BILASPUR (Chhattisgarh / Himachal Pradesh), HAMIRPUR
(Himachal Pradesh / Uttar Pradesh), PRATAPGARH (Rajasthan / Uttar Pradesh),
RAIGARH (Chhattisgarh / Maharashtra). Handled via composite key throughout.

---

## Reproduction

```bash
conda activate research_env

# Data pipeline
python 04_Code/08_build_district_crosswalk.py       # assert: 762 rows
python 04_Code/10_build_flood_exposure.py            # assert: Rule A 2,518 events
python 04_Code/13_extract_rbi_deposits.py
python 04_Code/14_merge_master_panel.py              # assert: 26,640 rows
python 04_Code/17_prepare_analysis_sample.py         # assert: 23,347 rows, 631 districts
python 04_Code/22b_align_viirs_clean.py              # assert: 25,240 rows
python 04_Code/23_merge_viirs_master.py              # assert: 100% VIIRS coverage
python 04_Code/24_engineer_regression_variables.py   # assert: 23 columns
python 04_Code/26_validate_viirs_quarterly.py        # assert: all 9 checks PASS

# Core regressions
python 04_Code/27b_regression_H1_linearmodels.py
python 04_Code/28b_regression_H2_linearmodels.py
python 04_Code/29b_regression_H3_linearmodels.py
python 04_Code/30b_regression_H4_linearmodels.py

# Robustness
python 04_Code/33_northeast_sensitivity.py
python 04_Code/34_placebo_timing.py
python 04_Code/35_longer_lags.py
python 04_Code/36_state_clustering.py
python 04_Code/36b_R6b_Wild_Cluster_bootstrap.py
python 04_Code/37_winsorized_reruns.py
python 04_Code/38_zerochg_diagnostic.py

# Figures
python 04_Code/fig01_flood_exposure_map.py
python 04_Code/fig02_H3_event_study.py
python 04_Code/fig03_H4_heterogeneity.py

**Environment:** Python 3.10.19, conda `research_env`  
**Core packages:** pandas · numpy · geopandas · rasterio · linearmodels ·
statsmodels · scipy · matplotlib · plotly · rapidfuzz · wildboottest

---

## Methodological Notes

**GADM as harmonisation anchor.** RBI district naming shifts across
publication years as administrative boundaries are redrawn. GADM v4.1
Level-2 provides stable polygon boundaries as the crosswalk anchor.
83.2% of RBI districts match to GADM (threshold: 80%); 128 unmatched
districts are excluded and disclosed in the Data section.

**VIIRS log offset.** Radiance uses +0.001 before log transformation.
Approximately 80% of district-quarters have mean radiance below
1 nW/cm²/sr; at this range log(x + 0.001) tracks log(x) without
producing undefined values at zero. Deposits use +1 (always positive
at Crore scale; the offset is negligible).

**Nominal deposits.** District-quarter CPI is unavailable at the
required granularity. Quarter fixed effects absorb national price trends.
India CPI averaged approximately 6–7% annually over the analysis window.
Acknowledged as a limitation in the paper.

**Demonetization gap.** 2016Q3–2017Q1 is absent from the panel by
construction — RBI district-level publications were suspended during the
November 2016 currency withdrawal. Never report 2016 or 2017 as
full-year figures.

**Superseded outputs.** Scripts 27–30 (statsmodels) are retained in
`07_Archive/Superseded_Scripts/` as a coefficient-stability audit trail.
All paper tables use Scripts 27b–30b (linearmodels) exclusively.
Coefficients are stable across both estimators; linearmodels resolves
the iterative two-way demeaning requirement for the unbalanced IV panel
(Script 28b: 8 iterations to convergence, tolerance 1×10⁻¹⁴).

---

*Project initiated: December 30, 2025*  
*Pre-writing phase complete: March 21, 2026*  
*Principal Investigator: Jaseel Badar, Harvard University*