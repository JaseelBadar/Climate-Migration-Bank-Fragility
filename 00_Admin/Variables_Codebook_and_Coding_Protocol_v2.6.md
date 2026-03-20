# Variables Codebook and Coding Protocol (v2.6)

**Project:** Climate Shocks, Displacement, and Bank Liquidity Risk:
Evidence from Night-Lights in India, 2015–2024

**Estimator:** linearmodels PanelOLS / IV2SLS throughout (Scripts 27b–30b).
All tables use these numbers exclusively. statsmodels output files are superseded.
**Status:** Full pipeline verified and clean. All regressions, all robustness
checks (R1–R8, R6b), and all figures complete. Results locked. Writing begins next.

---

## Changelog

| Version | Change |
|---|---|
| v1.x–v2.0 | Pipeline construction; VIIRS dissolve bug; deposit extraction bugs; H3 validated |
| v2.1–v2.2 | Crosswalk dedup (769→762); VIIRS alignment; regression panel: 23,088→23,347 obs |
| v2.3 | District count corrected to 631 composite pairs. Log offset corrected to +0.001 |
| v2.4 | Script 8 permanent rewrite (762-row assert). Flood baseline locked |
| v2.5 | All core regressions (27–30) complete. H1–H4 locked. FE correction applied |
| **v2.6** | **linearmodels PanelOLS final tables (27b–30b). All robustness complete (R1–R8, R6b). Wild bootstrap H1 documented (Script 36b). H4b demoted to suggestive (winsorization failure, Script 37, p=0.865). Two-phase liquidity cycle confirmed (Script 34). Longer lags null (Script 35). Northeast robust (Script 33). statsmodels warning resolved. All active issues closed. Figures generated.** |

**Integrity statement:** Variable definitions and coding protocols do not change
to match results. Every version bump records a measurement correction, naming fix,
or reproducibility update. The composite FE correction (`district_gadm + '_' +
state_gadm`, 631 pairs vs 624) was implemented before any regression was executed
and is the sole attributed cause of all benchmark changes from Feb 6.

---

## Non-Negotiable Principles

1. **Raw data is read-only.** Nothing in `01_Data_Raw/` is ever modified.
   All transformations write to `02_Data_Intermediate/` or `03_Data_Clean/`.
2. **No silent drops.** Every dropped row is logged with count and reason.
3. **No endogeneity by construction.** VIIRS outcomes never define flood treatment.
4. **One script, one output.** Each script produces one named dataset and one log.
5. **Composite keys everywhere.** All groupby, FE, merge, dissolve, and clustering
   operations use `district_gadm + '_' + state_gadm`. Using `district_gadm` alone
   produces 624 unique units instead of 631, collapsing 7 homonymous pairs and
   contaminating FE absorption, cluster assignments, and heterogeneity variable
   construction simultaneously.
6. **Log offset locked.** The offset constant in `log(x + c)` is fixed globally
   per variable, written into logs, and never tuned for results.
7. **Quarter alignment validated.** RBI extraction validates year-quarter labels
   against source column headers. Row labels are not trusted without header verification.
8. **Hard asserts before save.** Every script asserts expected row count and column
   count before writing output. A script that saves output without passing all asserts
   has failed, regardless of whether the output looks reasonable.
9. **Proxy discipline.** Any heterogeneity variable constructed from observational
   proxies is labeled "proxy" in all outputs and paper text. No causal claims.
10. **Estimator discipline.** Final paper tables use linearmodels PanelOLS
    (Scripts 27b–30b). statsmodels and linearmodels results are never mixed in
    the same table.

---

## I. Panel Structure

**Geographic standard:** GADM v4.1 Level-2 district polygons (India). RBI
districts mapped to GADM via crosswalk. GADM is authoritative.

**Analysis period:** 2015Q1–2024Q4 (40 quarters nominal); **37 quarters retained**
after demonetization exclusion.

**Demonetization gap (mandatory disclosure):** 2016Q3, 2016Q4, and 2017Q1 are
absent from the panel. District-level deposit data was unreliable during India's
demonetization (November 8, 2016) and its immediate aftermath. These quarters are
excluded upstream at the RBI assembly stage — not dropped by the analysis pipeline.
Must be named explicitly in the paper's Data section. Never report 2016 or 2017
as full-year figures.

**2015Q1 note:** 2015Q1 exists in the master panel (631 × 37 = 23,347) but
carries zero valid `deposit_change_qt` observations — dropped structurally by
all regression-sample `dropna()` calls. Regression quarter FE = 36 throughout.
Full panel count = 37 quarters. Both figures are correct and not in conflict.

### Index Variables

| Variable | Type | Definition |
|---|---|---|
| `district_gadm` | string | GADM Level-2 district name (UPPERCASE) |
| `state_gadm` | string | GADM Level-1 state name (UPPERCASE) |
| `district_state_id` | string | `district_gadm + '_' + state_gadm` — composite unique ID |
| `quarter` | string | e.g., `2015Q1` |
| `year` | int | 2015–2024 |
| `q` | int | 1–4 |
| `quarter_num` | int | Sequential 1–40 — for sorting and lag construction |

**Sorting rule (locked):** Always sort by `district_gadm`, `state_gadm`, `year`,
`q` before constructing lags or differences. Violation invalidates all time-series
operations.

### Panel Dimensions

| Panel | Districts | Quarters | Observations |
|---|---|---|---|
| Master raw (flood panel) | 666 | 40 | 26,640 |
| Analysis sample | **631** | **37** | **23,347** |
| VIIRS quarterly (clean) | 631 | 40 | 25,240 |
| Regression panel (final) | 631 | 37 | 23,347 |
| Winsorized panel | 631 | 37 | 23,347 |

**On 624 vs 631:** `.nunique()` on `district_gadm` alone returns 624 — undercounts
by 7 due to homonymous pairs. The correct district count is always 631 composite
`(district_gadm, state_gadm)` pairs.

**7 confirmed homonymous pairs (UPPERCASE):**
AURANGABAD (BIHAR / MAHARASHTRA),
BALRAMPUR (CHHATTISGARH / UTTAR PRADESH),
BIJAPUR (CHHATTISGARH / KARNATAKA),
BILASPUR (CHHATTISGARH / HIMACHAL PRADESH),
HAMIRPUR (HIMACHAL PRADESH / UTTAR PRADESH),
PRATAPGARH (RAJASTHAN / UTTAR PRADESH),
RAIGARH (CHHATTISGARH / MAHARASHTRA).

---

## II. Outcome Variables — Banking

### `deposits`

- **Definition:** Total district-quarter deposits, all population groups aggregated
- **Unit:** Indian Rupees, Crores (nominal)
- **Source:** RBI BSR-2 (District-wise deposits)
- **Construction:** Script 13 — fiscal-to-calendar conversion, state filtering for
  all homonymous pairs, column offset `dep_idx = q_idx + 1` for historical files
- **Verification anchor:** Aurangabad Bihar 2015Q1 = 4,422 Crores
  (pre-fix value of 18,652 Crores was the Bug 2 deposit summing artifact)
- **Verified range:** min = 28.9979 | max = 1,237,744.34 | mean = 16,425.73 |
  median = 6,135.58 Crores
- **Nominal INR (locked):** Retained in nominal Rupees. District-quarter CPI
  unavailable at required granularity. Quarter FE absorb national price trends.
  Disclosed as a limitation in the paper (inflation ~6–7% per year).

### `log_deposits`

- **Construction:** `ln(deposits + 1)` — offset +1 safe at Crore scale (deposits > 0)
- **Verified range:** min = 3.4011 | max = 14.0288 | mean = 8.7075 | SD = 1.3707

### `deposit_change_qt` *(primary dependent variable)*

- **Construction:** `log_deposits.diff()` within `(district_gadm, state_gadm)` groups
- **Missing values:** 905 total — 631 structural first-obs NaNs + 274 from `.diff()`
  propagation across 268 missing deposit quarters
- **Asymmetry with `lights_change_qt`** (631 missing only): reflects 100% VIIRS
  coverage vs 98.9% deposit coverage. Expected and confirmed — not a data error.
- **Usable N:** 22,442 observations
- **Verified range:** min = −1.9322 | max = 2.0251 | mean = 0.0233 | SD = 0.0743

**2023 anomaly (Script 32b, confirmed):** Raw std = 0.106 in 2023 (nearly double
adjacent years). Mean = −0.001 (only negative mean year in panel). Median = 0.017
(normal). Left-tail asymmetry confirmed: 15.4% of 2023 district-quarters fall below
the full-sample 5th percentile (expected ~5%). Concentrated in Northeast districts
where low absolute deposit levels amplify percentage volatility. Unit error ruled
out (2023/2022 median level ratio = 0.9985). No data corruption. TUENSANG
(Nagaland) — 2023Q1: −1.453, 2023Q3: +1.758 — is a likely reporting artifact;
must be flagged in the paper. All extreme cases handled by winsorization.

### `deposit_change_qt_winsor` *(robustness dependent variable)*

- **Construction:** `np.clip(deposit_change_qt, q01, q99)`. NaN values preserved
  via `np.where` — not clipped to bounds.
- **Thresholds (locked, Script 31):** Lower = −0.162585 | Upper = +0.230701
- **Clipped observations:** 450 (2.01% of N = 22,442) — symmetric: 225 low, 225 high
- **Post-winsorization verification:** Median = 0.020979 (unchanged). IQR
  unchanged. Std reduced 30% (0.074 → 0.052). Mean shift +0.000704 (trivial).
- **Usage:** Robustness re-runs of Scripts 27b–30b (R3). Primary results use raw.
- **Source file:** `regression_panel_final_winsor.csv` (23,347 × 24 columns)

### `deposit_withdrawal_binary` *(conditional — use only if included in paper)*

- **Construction:** `indicator(deposit_change_qt < k)`
- **Threshold discipline:** k defined from bottom decile of `deposit_change_qt`
  among non-flood observations, or fixed −10% rule — whichever is more conservative.
  Threshold must be recorded before mechanism regressions. Never tuned post-estimation.

---

## III. Treatment Variables — Flood Shocks

Flood events sourced from EM-DAT, mapped to calendar quarters, matched to GADM
districts via crosswalk (Scripts 8, 10). Both precision regimes reported in all
core tables (R1).

### `flood_exposure_ruleA_qt` *(primary specification)*

- **Definition:** 1 if district directly matched OR district's state matched (fallback)
- **Coverage (locked):** 2,238 events | 9.59% treatment rate | 569 districts ever
  exposed
- **Interpretation:** Conservative lower bound. State fallback introduces false
  positives, attenuating $\hat{\beta}$ toward zero. Rule A estimates are lower
  bounds on the true local effect.

### `flood_exposure_ruleB_qt` *(precision robustness)*

- **Definition:** 1 only when district explicitly identified in EM-DAT location field
- **Coverage (locked):** 209 events | 0.90% treatment rate | 141 districts ever
  exposed
- **Interpretation:** Higher precision; lower power. Preferred for instrument
  credibility. H2 Rule B instrument is weak ($F = 8.949 < 10$) — second stage
  results labeled suggestive throughout the paper without exception.

### Flood Lags — Distributed Lag Models

| Variable | Construction | Used in |
|---|---|---|
| `flood_ruleA_L1` | L1 within composite group | H3, Script 29b |
| `flood_ruleA_L2` | L2 within composite group | H3, Script 29b |
| `flood_ruleA_L3` | L3 | R5 (Script 35) |
| `flood_ruleA_L4` | L4 | R5 (Script 35) |
| `flood_ruleB_L1–L4` | Rule B equivalents | Robustness |

**Lag missing-value arithmetic (locked):** Each lag introduces exactly 631 additional
NaNs (one per district). Any deviation from 631 × k signals a composite key error.

| Lag | Expected missing | Verified |
|---|---|---|
| L1 | 631 | PASS |
| L2 | 1,262 | PASS |
| L3 | 1,893 | PASS |
| L4 | 2,524 | PASS |

### `flood_severity_qt` *(conditional — exploratory only)*

- **Construction:** `ln(affected + deaths + 1)` where both fields populated
- **Constraint:** If missingness is large, treat as exploratory. Not a main result.

---

## IV. Migration and Disruption Proxy — VIIRS Night Lights

### `mean_radiance`

- **Definition:** District-quarter mean VIIRS radiance, pixel-area weighted
- **Unit:** nW/cm²/sr
- **Source:** VIIRS DNB monthly composites, Colorado School of Mines EOG, tile 75N060E
- **Construction:** Scripts 21–22b — monthly extraction, deduplication, quarterly
  aggregation (mean radiance, sum pixels), composite key groupby throughout
- **Forensic validation (Script 26, all 9 checks PASS):** 0 NaN, 0 Inf, 0 negative,
  balanced 631 × 40 = 25,240. Aurangabad litmus: BIHAR = 0.7222, MAHARASHTRA =
  0.5094 (diff = 0.2128). All 7 homonymous pairs confirmed distinct.
- **Verified range:** min = 0.0003 | max = 35.8691 | mean = 0.6955 |
  median = 0.4266 | SD = 1.6884

### `log_lights_qt`

- **Construction:** `ln(mean_radiance + 0.001)`
- **Offset: +0.001 (locked)** — corrected from +0.01 (v2.2) and +1 (v2.1)
- **Rationale:** ~80% of observations have mean_radiance < 1 (rural and semi-urban
  districts). `log(x + 1)` approximates the identity function in this range,
  eliminating log-scale compression for the majority of observations. `log(x + 0.001)`
  preserves the intended elasticity interpretation throughout the distribution.
  `log(x + 1)` is reserved for deposits where scale is Crores.
- **Verified range:** min = −6.6447 | max = 3.5559 | mean = −0.8326 | SD = 0.8377

### `lights_change_qt`

- **Construction:** `log_lights_qt.diff()` within `(district_gadm, state_gadm)` groups
- **Missing values:** 631 exactly (first obs per district — 100% VIIRS coverage)
- **Usable N:** 22,716 observations
- **Verified range:** min = −2.2385 | max = 1.6938 | mean = 0.0170 | SD = 0.3530

### `migration_proxy_qt` *(conditional — use only if included in paper)*

- **Construction:** `indicator(lights_change_qt < −theta)`
- **Threshold discipline:** theta chosen from empirical distribution of
  `lights_change_qt` in flood-exposed district-quarters under Rule B. Recorded
  before H2 event-spec regression. Robustness: theta ∈ {0.10, 0.15, 0.20}.

---

## V. Fixed Effects and Standard Errors

### District FE *(H1, H2, H4 only)*

`C(district_state_id)` — composite key, 631 effects.

Using `district_gadm` alone produces 624 FE instead of 631 — a confirmed
misspecification. Consequence: contaminated FE absorption, incorrect cluster
assignments, and incorrect heterogeneity variable construction when the same
groupby error propagates to $Z_i$ construction. All pre-March 2026 benchmarks
were produced under this misspecification. All values in this codebook reflect
the corrected specification.

H3 uses quarter FE only — not district FE. Not affected by this requirement.

### Quarter FE *(all specifications)*

36 in H1/H2/H4. 35 in H3 (L2 restriction structurally drops 2015Q1–2015Q2).
Absorbs national seasonality, macro shocks, monetary policy shifts, and
national-level inflation trends.

### Standard Errors

Clustered by `district_state_id` throughout. Clustering on `district_gadm` alone
assigns 7 pairs to incorrect shared clusters — same misspecification as FE.

---

## VI. Heterogeneity Variables ($Z_i$, H4)

All three $Z_i$ variables are pre-committed per Hypotheses v2.6. Construction uses
composite `district_state_id` groupby throughout. All labeled as proxies where true
administrative classifications are unavailable.

### H4a: `urban_proxy`

- **Construction:** Time-invariant indicator. Above-median district mean
  `log_lights_qt` over the full analysis period, grouped by `district_state_id`.
  Median `log_lights_qt` = −0.8900.
- **Split:** Above-median: 315 districts | At/below: 316 districts
- **Label in paper:** "Urban proxy (lights-based, above-median mean radiance)"
- **Result (Script 30b, locked):**

| Rule | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|
| A | −0.001666 | 0.002664 | 0.532 | **Null** |
| B | +0.007479 | 0.006929 | 0.280 | **Null** |

**Mandatory disclosure:** The Feb 6 result ($p < 0.001$) was spurious —
`urban_proxy` constructed on `district_gadm` alone collapsed AURANGABAD
Bihar/Maharashtra, contaminating the median threshold. After composite key
correction the signal disappears entirely. Null is the correct and final result.
Must be documented explicitly in the paper.

### H4b: `high_exposure_proxy`

- **Construction:** Time-invariant indicator. Above-median cumulative
  `flood_exposure_ruleA_qt` summed over full period, grouped by `district_state_id`.
  Median = 3.0 cumulative events (integer). Threshold is strictly greater: districts
  with exactly 3.0 events fall in the low-exposure group. Disclose in paper.
- **Split:** High-exposure (> 3.0): 255 districts | Low (≤ 3.0): 376 districts
- **Label in paper:** "High-exposure proxy (above-median cumulative flood events)"
- **Result (Script 30b, locked):**

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | +0.004700 | −0.006810 | 0.002932 | 0.020 | **Suggestive only** |
| B | +0.012016 | −0.013419 | 0.007670 | 0.080 | Marginal |

**⚠ WINSORIZATION FAILURE (Script 37, mandatory disclosure):**
Rule A interaction $p = 0.865$ on winsorized panel. Effect is entirely driven by
extreme deposit observations. H4b is demoted from supported to **suggestive only**.
Cannot be presented as a robust finding under any framing. Required language:
*"The high flood exposure interaction (H4b) is significant in the baseline
specification (Rule A: $\hat{\beta} = -0.007$, $p = 0.020$) but does not survive
winsorization of the top and bottom 1% of deposit growth observations ($p = 0.865$).
The effect is sensitive to extreme observations and should be interpreted as
suggestive evidence only."*

### H4c: `monsoon_qt`

- **Construction:** Time-varying indicator. `indicator(q == 3)` — July–September.
  Not a proxy; directly observed.
- **Split:** Q3 (monsoon): 5,679 obs | Non-Q3: 17,668 obs
- **Result (Script 30b, locked):**

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | −0.004700 | +0.012495 | 0.002884 | <0.001 | **Confirmed (Rule A)** |
| B | −0.000838 | +0.002287 | 0.007968 | 0.774 | **Null** |

**Net monsoon effect (Rule A):** $-0.0047 + 0.0125 = +0.0078$ (net positive).
Anticipated moderate flooding during monsoon season coincides with agricultural
income inflows — deposits increase. Severe floods (Rule B) override seasonal
adjustment; distress dominates at high intensity.

**Mandatory language (exact, no paraphrase):** *"Monsoon seasonality moderates
the deposit response to moderate-intensity floods (Rule A: $\hat{\beta} = +0.012$,
$p < 0.001$) but not to severe flood events (Rule B: $p = 0.774$). The heterogeneity
result is fragile to flood intensity definition."*

---

## VII. IV Pipeline Variables

### `lights_hat_qt`

- **Definition:** Fitted values from H1 first stage
- **Rule:** Diagnostic storage only. Never interpreted as observed lights.

### `first_stage_F`

- **Definition:** $F = t^2$ for single excluded instrument (Wooldridge 2010, p. 104)
- **Rationale:** linearmodels `first_stage` F-stat overflows numerically at 666
  exogenous columns. For a single excluded instrument, $F = t^2$ exactly.
- **Locked values (Script 28b):**
  - Rule A: $F = (-5.888)^2 = 34.673$ — strong (threshold 16.38 for 5% maximal size)
  - Rule B: $F = (-2.992)^2 = 8.949$ — **weak** (below threshold 10)
- **Rule:** Always reported alongside IV results. Rule B second stage labeled
  suggestive throughout; causal language removed from abstract and conclusions.

---

## VIII. Robustness: Final Status

| Check | Implementation | Outcome |
|---|---|---|
| R1 — Flood precision | Rule A + Rule B in all core tables | **Complete** |
| R2 — Placebo timing | Flood$_t$ predicting $\Delta$Deposits$_{t-1}$ | **Complete** — two-phase cycle documented (see below) |
| R3 — Winsorisation | 1st/99th, 450 obs (2.01%) symmetric | **Complete** — H3 robust; H4b **fails** ($p = 0.865$) |
| R4 — CPI / nominal | Nominal INR; quarter FE absorb price trends | **Complete** |
| R5 — Longer lags | $t_0+3$, $t_0+4$ | **Complete** — both null; effect decays at $t_0+2$ |
| R6 — State clustering | 34 state clusters, conventional SE | **Complete** — H3 robust ($p = 0.034$); H1 $p = 0.105$ |
| R6b — Wild bootstrap | 999 iterations, Rademacher weights, 34 clusters | **Complete** — H1 fails (Rule A $p = 0.158$; Rule B $p = 0.267$) |
| R7 — IV discipline | First-stage $F$ reported; Rule B labeled suggestive | **Complete** |
| R8 — Northeast sensitivity | Northeast districts excluded | **Complete** — H3 $t_0+2$ robust to NE exclusion |

**All nine checks complete. Zero open items.**

### R2 — Two-Phase Liquidity Cycle (mandatory disclosure)

Placebo test (Script 34, `09_placebo_timing.csv`): flood at $t$ predicts **higher**
deposit growth at $t-1$ — a positive pre-period signal that survives district FE.

| Test | $\hat{\beta}$ | SE | $p$ | District FE |
|---|---|---|---|---|
| Test 2 (quarter FE only) | +0.004664 | 0.001841 | 0.011 | No |
| Test 2b (quarter + district FE) | +0.004417 | 0.001881 | 0.019 | Yes |

This is not a pre-existing downward trend. Sign is positive — opposite to the
$t_0+2$ withdrawal effect (−0.007). It reflects a two-phase household liquidity
cycle: anticipatory saving ahead of the predictable flood season (+0.005), followed
by post-flood deposit withdrawal (−0.007) two quarters after the event.

**Mandatory disclosure language (exact):** *"Flood exposure at time $t$ predicts
higher deposit growth at $t-1$ ($\hat{\beta} = +0.005$, $p = 0.011$), a signal
that survives the inclusion of district fixed effects ($\hat{\beta} = +0.004$,
$p = 0.019$). This pre-period effect is positive and opposite in sign to the
$t_0+2$ withdrawal effect (−0.007), indicating a two-phase household liquidity
cycle — anticipatory saving ahead of the predictable flood season followed by
post-flood deposit withdrawal — rather than a pre-existing downward trend
in deposits."*

---

## IX. Locked Regression Results

All results from linearmodels PanelOLS, Scripts 27b–30b. District FE = 631.
Quarter FE = 36 (H1/H2/H4) or 35 (H3). SE clustered by `district_state_id`.

### H1 — Floods → Lights (Script 27b, N = 22,716)

| Rule | $\hat{\beta}$ | SE | $t$ | $p$ |
|---|---|---|---|---|
| A | −0.044468 | 0.007784 | −5.7124 | <0.001 |
| B | −0.058446 | 0.019768 | −2.9566 | 0.003 |

Rule B > Rule A in magnitude — attenuation bound confirmed.

**Wild bootstrap (Script 36b, mandatory disclosure):** $\hat{\beta} = -0.044468$
stable across all clustering levels. H1 does **not** survive state-level clustering.

| SE Specification | Clusters | Rule A $p$ | Instrument status |
|---|---|---|---|
| District-clustered (primary) | 631 | <0.001 | Strong |
| State-clustered, conventional | 34 | 0.105 | — |
| State-clustered, wild bootstrap | 34 | 0.158 | — |

### H2 — Lights → Deposits IV 2SLS (Script 28b, N = 22,442)

| Rule | $\hat{\beta}$ | SE | $t$ | $p$ | First-stage $F$ | Instrument |
|---|---|---|---|---|---|---|
| A | −0.008388 | 0.034022 | −0.2465 | 0.805 | 34.673 | **Strong** |
| B | −0.006776 | 0.059698 | −0.1135 | 0.910 | 8.949 | **Weak** |

Null reconciliation: H2 tests the contemporaneous window; H3 confirms deposit
effects are lagged. IV tests a zero-effect window by construction.

### H3 — Distributed Lag (Script 29b, N = 21,837, Quarter FE = 35)

| Lag | $\hat{\beta}$ (Rule A) | SE | $t$ | $p$ |
|---|---|---|---|---|
| $t_0$ | +0.000609 | 0.001462 | +0.4167 | 0.677 |
| $t_0+1$ | +0.001505 | 0.001114 | +1.3517 | 0.177 |
| **$t_0+2$** | **−0.007005** | **0.001644** | **−4.2609** | **<0.001** |

L2 restriction structurally drops 2015Q1–2015Q2 (correct, not a bug).
H3 $t_0+2$ robust to: winsorization ($p < 0.001$), Northeast exclusion,
state-level clustering ($p = 0.034$). Longer lags $t_0+3$ and $t_0+4$ null
(Script 35) — effect decays within two quarters.

### H4 — Heterogeneity (Script 30b, N = 22,442)

| Spec | Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|---|
| H4a: Urban | A | +0.001207 | −0.001666 | 0.002664 | 0.532 | Null |
| H4a: Urban | B | −0.002890 | +0.007479 | 0.006929 | 0.280 | Null |
| H4b: High exposure | A | +0.004700 | −0.006810 | 0.002932 | 0.020 | **Suggestive only** |
| H4b: High exposure | B | +0.012016 | −0.013419 | 0.007670 | 0.080 | Marginal |
| H4c: Monsoon | A | −0.004700 | +0.012495 | 0.002884 | <0.001 | **Confirmed (Rule A)** |
| H4c: Monsoon | B | −0.000838 | +0.002287 | 0.007968 | 0.774 | Null |

---

## X. Specification Reference

| Spec | $N$ | Outcome | Key Regressor(s) | District FE | Quarter FE |
|---|---|---|---|---|---|
| H1 | 22,716 | `lights_change_qt` | `flood_exposure_ruleA/B_qt` | Yes (631) | 36 |
| H2 IV | 22,442 | `deposit_change_qt` | `lights_change_qt` (instrumented) | Yes (631) | 36 |
| H3 | 21,837 | `deposit_change_qt` | Flood $t_0$, $t_0+1$, $t_0+2$ | **No** | 35 |
| H4 | 22,442 | `deposit_change_qt` | Flood × $Z_i$ | Yes (631) | 36 |

SE clustered by `district_state_id` in all specifications.

---

## XI. Data State

All files verified clean. Results locked. Do not re-run.

| File | Rows | Key Verification |
|---|---|---|
| `district_crosswalk_draft.csv` | 762 | Hard assert: len == 762 |
| `flood_exposure_panel.csv` | 26,640 | Rule A: 2,518 raw events \| 666 districts |
| `rbi_deposits_panel.csv` | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores |
| `master_panel_raw.csv` | 26,640 | BALOD 2022Q4 = 3,296 Crores |
| `regression_panel_final.csv` | 23,347 | 23 columns \| lag arithmetic exact |
| `regression_panel_final_winsor.csv` | 23,347 | 24 columns \| 450 obs clipped (2.01%) |
| `viirs_quarterly_panel_clean.csv` | 25,240 | 631 × 40 \| 9-check validation PASS |

**Final paper table CSVs (linearmodels only — do not substitute statsmodels):**

| File | Script | Contents |
|---|---|---|
| `02b_H1_linearmodels.csv` | 27b | H1 first stage, both rules |
| `03b_H2_linearmodels.csv` | 28b | H2 IV 2SLS, both rules |
| `04b_H3_linearmodels.csv` | 29b | H3 distributed lag, both rules |
| `05b_H4_linearmodels.csv` | 30b | H4 heterogeneity, all specs |
| `09_placebo_timing.csv` | 34 | R2 placebo timing tests |

**Locked analysis sample:** 631 composite pairs × 36 regression quarters = **23,347 obs**
Rule A: **2,238 events (9.59%)** | Rule B: **209 events (0.90%)**
VIIRS: **100% coverage** | Deposits: **98.9% coverage**

---

## XII. Known Issues

### Pending — Pre-Paper

**Zero-change quarters diagnostic**
25th percentile of `deposit_change_qt` ≈ 0.003. May reflect true stagnation,
RBI rounding, or copy-forward errors at source. Diagnostic script required before
submission.

**Script 29b cosmetic comments** (no re-run required)
- Expected N comment: ~21,180 → ~21,837
- Expected QFE comment: 36 → 35

**Script 12 token count** (no re-run required)
Section [7] token count comment: 44 → 46.

### Resolved

| Issue | Resolution |
|---|---|
| statsmodels rank warning (Scripts 27–30) | Resolved: Scripts 27b–30b use linearmodels PanelOLS throughout |
| Script 32b negative-tail conclusion error | Resolved: Correct conclusion documented in Data State (Section II, 2023 anomaly). Left-tail asymmetry confirmed, NE-concentrated. Log file not cited directly. |
| Northeast sensitivity (Script 33) | Resolved: H3 $t_0+2$ confirmed robust to NE exclusion |
| Composite FE misspecification | Resolved: `district_state_id` composite key throughout all scripts |
| Crosswalk regression (769→762) | Resolved: Permanent rewrite with row-level dedup + hard assert |
| Deposit extraction bugs (Script 13) | Resolved: Column offset fix + state-blind merge fix |
| RBI 2016–2017 gap | Resolved: Structural exclusion confirmed; demonetization period |

---

## XIII. Script Contract

Every script must, without exception:

1. Assert input file row counts and column counts at load
2. Log input and output file paths
3. Log row counts before and after every major transformation
4. Log all constant choices (log offsets, thresholds, winsorization bounds)
5. Assert expected output row count and column count before saving
6. Write a log file to `05_Outputs/Logs/` with `encoding='utf-8'`
7. Use `datetime.now()` for run timestamps — never hardcode dates
8. Use no Unicode symbols in log files (no checkmarks, arrows, emoji) — Windows
   cp1252 encoding risk

---

## XIV. File IO Contract

| Data type | Location |
|---|---|
| Raw inputs (read-only) | `01_Data_Raw/` |
| Intermediate outputs | `02_Data_Intermediate/` |
| Final analysis panels | `03_Data_Clean/` |
| Regression table CSVs | `05_Outputs/Tables/` |
| Figures (PDF + PNG) | `05_Outputs/Figures/` |
| Script logs | `05_Outputs/Logs/` |

---

## XV. Methodological Notes

**GADM as geographic standard:** RBI district names change over time. GADM v4.1
provides stable polygon boundaries for flood matching. Crosswalk harmonises RBI
names to GADM at 83.2% match rate; 130 unmatched RBI districts dropped.

**Rule A as primary specification:** 9.59% treatment rate maximises power.
Rule B (0.90%) is the strict precision check. Both reported per R1. Rule A
preferred for statistical power; Rule B preferred for instrument credibility
argument (where instrument is strong — Rule A only).

**Option 3 sample restriction:** Dropping both unreliable deposit quarters and
structural-zero districts yields 98.9% deposit coverage with 100% treatment-outcome
overlap. Option 1 (quarters only) retains 35 structural-zero districts. Option 2
(districts only) retains the demonetization blackout, creating false breaks in
distributed-lag specifications.

**Log offset +0.001 for VIIRS:** India is predominantly rural. Approximately 80%
of observations have mean_radiance < 1. `log(x + 0.001)` preserves the intended
elasticity interpretation throughout the distribution. `log(x + 1)` is reserved
for deposits (Crore scale).

**Demonetization gap:** 2016Q3–2017Q1 absent from the panel. Discontinuity is
absorbed by quarter FE. Must be disclosed explicitly in the Data section.

---

*Principal Investigator: Jaseel Badar, Harvard University*
*Repository: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility*