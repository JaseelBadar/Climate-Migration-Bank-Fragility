# Variables Codebook and Coding Protocol
### Flood Shocks and the Two-Phase Deposit Cycle: A Nighttime Lights Identification
### Evidence from Nighttime Lights in India, 2015–2024

**Version:** 2.6 (March 21, 2026)  
**Estimator:** linearmodels PanelOLS / IV2SLS throughout (Scripts 27b–30b).  
All paper tables use these numbers exclusively. statsmodels output files superseded.  
**Status:** Full pipeline verified and clean. All regressions, robustness checks
(R1–R8, R6b), and figures complete. Results locked. Writing phase active.

---

## Changelog

| Version | Date | Change |
|---|---|---|
| v1.x–v2.0 | Dec 2025 – Jan 2026 | Pipeline construction; VIIRS dissolve deduplication; RBI deposit extraction bugs identified and resolved; H3 validated |
| v2.1–v2.2 | Feb 1–6, 2026 | Crosswalk dedup (769→762); VIIRS alignment; regression panel corrected (23,088→23,347 obs); log offset corrected to +0.001 |
| v2.3 | Feb 7, 2026 | District count corrected to 631 composite pairs following composite FE identification |
| v2.4 | Feb 28 – Mar 5, 2026 | Script 8 permanent rewrite; 762-row hard assert added; flood baseline locked |
| v2.5 | Mar 6–18, 2026 | Core regressions 27b–30b executed and locked; H1–H4 results confirmed; FE correction applied throughout |
| **v2.6** | **Mar 19–21, 2026** | **linearmodels final tables locked; wild bootstrap H1 documented (Script 36b, fails at state level); H4b demoted to suggestive (winsorization failure, Script 37, p=0.865); two-phase cycle confirmed (Script 34); longer lags null (Script 35); Northeast robust (Script 33); zero-change diagnostic complete (Script 38); all active issues closed; figures generated** |

**Integrity statement.** Variable definitions and coding protocols do not
change to match results. Every version bump records a measurement
correction, naming fix, or reproducibility update. The composite FE
correction (`district_gadm + '_' + state_gadm`, 631 pairs vs 624) was
identified on February 7, pre-committed before any regression was
re-executed, and is the sole attributed cause of all benchmark changes
from February 6. This is documented in Research_Log.txt.

---

## Non-Negotiable Principles

1. **Raw data is read-only.** Nothing in `01_Data_Raw/` is ever modified.
   All transformations write to `02_Data_Intermediate/` or `03_Data_Clean/`.

2. **No silent drops.** Every dropped row is logged with count and reason.
   A script that changes row counts without logging has failed.

3. **No endogeneity by construction.** VIIRS outcomes never define flood
   treatment. The instrument and the outcome are constructed from
   independent sources.

4. **One script, one output.** Each script produces exactly one named
   dataset and one log file. No script overwrites another script's output.

5. **Composite keys everywhere.** All `groupby`, FE construction, merge,
   dissolve, and cluster operations use `district_gadm + '_' + state_gadm`.
   Using `district_gadm` alone returns 624 unique units instead of 631 —
   collapsing 7 homonymous district pairs and contaminating FE absorption,
   cluster assignments, and heterogeneity variable construction
   simultaneously. All February 6 benchmarks were produced under this
   misspecification.

6. **Log offsets locked.** The offset constant in `log(x + c)` is fixed
   globally per variable, written into logs, and never tuned to improve
   results.

7. **Quarter alignment validated.** RBI extraction validates year-quarter
   labels against source column headers. Row labels are not trusted without
   header verification.

8. **Hard asserts before save.** Every script asserts expected row count
   and column count before writing output. A script that saves output
   without passing all asserts has failed, regardless of whether the output
   appears reasonable.

9. **Proxy discipline.** Any heterogeneity variable constructed from
   observational proxies is labeled "proxy" in all outputs and paper text.
   No causal classification claims.

10. **Estimator discipline.** Final paper tables use linearmodels PanelOLS
    (Scripts 27b–30b). statsmodels and linearmodels results are never mixed
    in the same table or the same sentence.

---

## I. Panel Structure

**Geographic standard.** GADM v4.1 Level-2 district polygons (India).
RBI districts are mapped to GADM via crosswalk. GADM is the authoritative
unit of observation. RBI district names change over time as administrative
boundaries are redrawn; GADM provides stable polygon boundaries as the
harmonisation anchor.

**Analysis period.** 2015Q1–2024Q4 (40 quarters nominal);
**37 quarters retained** after demonetization exclusion.

**Demonetization gap.** 2016Q3, 2016Q4, and 2017Q1 are absent from the
panel. District-level deposit data was unreliable during India's
demonetization (November 8, 2016) and its immediate aftermath. These
three quarters are excluded upstream at the RBI assembly stage — not
dropped by the analysis pipeline. Must be disclosed explicitly in
Section 3.4 (Panel Construction). Never report 2016 or 2017 as
full-year figures.

**On 2015Q1.** 2015Q1 exists in the master panel (contributing to the
23,347 observation count) but carries zero valid `deposit_change_qt`
observations — dropped structurally by all regression-sample `dropna()`
calls. This is why the analysis sample is 37 quarters but regression
quarter FE = 36 throughout. Both figures are correct and not in conflict.

### Index Variables

| Variable | Type | Definition |
|---|---|---|
| `district_gadm` | string | GADM Level-2 district name (UPPERCASE) |
| `state_gadm` | string | GADM Level-1 state name (UPPERCASE) |
| `district_state_id` | string | `district_gadm + '_' + state_gadm` — composite unique identifier |
| `quarter` | string | e.g., `2015Q1` |
| `year` | int | 2015–2024 |
| `q` | int | 1–4 |
| `quarter_num` | int | Sequential 1–40 — for sorting and lag construction only |

**Sorting rule (locked).** Always sort by `district_gadm`, `state_gadm`,
`year`, `q` before constructing lags or differences. Any other sort order
invalidates all time-series operations.

### Panel Dimensions

| Panel | Districts | Quarters | Observations |
|---|---|---|---|
| Master raw (flood panel) | 666 | 40 | 26,640 |
| Analysis sample | **631** | **37** | **23,347** |
| VIIRS quarterly (clean) | 631 | 40 | 25,240 |
| Regression panel (final) | 631 | 37 | 23,347 |
| Winsorized panel | 631 | 37 | 23,347 |

**On 624 vs 631.** `.nunique()` on `district_gadm` alone returns 624 —
undercounts by 7 due to homonymous pairs. The correct district count is
always 631 composite `(district_gadm, state_gadm)` pairs. Any script,
assert, or paper figure that reports 624 is incorrect.

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

| Attribute | Value |
|---|---|
| Definition | Total district-quarter deposits, all population groups aggregated |
| Unit | Indian Rupees, Crores (nominal) |
| Source | RBI BSR-2 (District-wise deposits) |
| Script | 13 — fiscal-to-calendar conversion, state filtering for all homonymous pairs |
| Column offset | `dep_idx = q_idx + 1` (historical files 2004–2022) |
| Verification anchor | AURANGABAD BIHAR 2015Q1 = 4,422 Crores (pre-fix contaminated value: 18,652 Crores — Bug 2 deposit summing artifact) |
| Verified range | min = 28.9979 · max = 1,237,744.34 · mean = 16,425.73 · median = 6,135.58 Crores |

**Nominal INR (locked).** Deposits retained in nominal Rupees.
District-quarter CPI unavailable at required granularity. Quarter FE
absorb national price trends. India CPI averaged approximately 6–7%
annually over the analysis window. Acknowledged as a limitation in the
paper.

### `log_deposits`

- **Construction:** `ln(deposits + 1)` — offset +1 safe at Crore scale
  (all deposit values are positive)
- **Verified range:** min = 3.4011 · max = 14.0288 · mean = 8.7075 ·
  SD = 1.3707

### `deposit_change_qt` *(primary dependent variable)*

- **Construction:** `log_deposits.diff()` within `(district_gadm,
  state_gadm)` groups, sorted by `year`, `q`
- **Missing values:** 905 total — 631 structural first-observation NaNs
  + 274 from `.diff()` propagation across 268 missing deposit quarters
- **Asymmetry with `lights_change_qt`** (631 missing only): reflects 100%
  VIIRS coverage vs 98.9% deposit coverage. Expected and confirmed —
  not a data error
- **Usable N:** 22,442 observations
- **Verified range:** min = −1.9322 · max = 2.0251 · mean = 0.0233 ·
  SD = 0.0743

**2023 anomaly (Script 32b, confirmed).** Raw SD = 0.106 in 2023 —
nearly double adjacent years. Mean = −0.001 (only negative mean year
in panel). Median = 0.017 (normal). Left-tail asymmetry confirmed: 15.4%
of 2023 district-quarters fall below the full-sample 5th percentile
(expected ~5%). Concentrated in Northeast districts where low absolute
deposit levels amplify percentage volatility. Unit error ruled out
(2023/2022 median level ratio = 0.9985). No data corruption confirmed.
TUENSANG (Nagaland) — 2023Q1: −1.453, 2023Q3: +1.758 — is a likely
reporting artifact; must be flagged in a Data section footnote. All
extreme cases handled by winsorization.

**Zero-change diagnostic (Script 38, resolved).** Zero exact zeros
in `deposit_change_qt`. No copy-forward errors in RBI data confirmed.
Near-zero observations (|Δ| < 0.001): 409 obs (1.82%) — genuine
stagnation, not measurement artifact. H3 t₀+2 stable under near-zero
exclusion (δ = 0.000294). Section 3.3 gate unblocked.

### `deposit_change_qt_winsor` *(robustness dependent variable)*

- **Construction:** `np.clip(deposit_change_qt, q01, q99)`. NaN values
  preserved via `np.where` — not clipped to bounds
- **Thresholds (locked, Script 31):** Lower = −0.162585 · Upper =
  +0.230701
- **Clipped observations:** 450 (2.01% of N = 22,442) — symmetric:
  225 low, 225 high
- **Post-winsorization:** Median = 0.020979 (unchanged) · IQR unchanged ·
  SD reduced 30% (0.074 → 0.052) · Mean shift +0.000704 (negligible)
- **Usage:** Robustness re-runs R3 (Scripts 33b–37). Primary results
  use raw `deposit_change_qt`
- **Source file:** `regression_panel_final_winsor.csv` (23,347 × 24)

---

## III. Treatment Variables — Flood Shocks

Flood events sourced from EM-DAT, mapped to calendar quarters, matched
to GADM districts via crosswalk (Scripts 8, 10). Both precision regimes
reported in all core tables (R1).

### `flood_exposure_ruleA_qt` *(primary specification)*

| Attribute | Value |
|---|---|
| Definition | 1 if district directly matched OR district's state matched (fallback) |
| Treatment rate (locked) | 9.59% — 2,238 events · 569 districts ever exposed |
| Interpretation | Conservative lower bound. State fallback introduces false positives, attenuating β̂ toward zero. Rule A estimates are lower bounds on the true local effect |

### `flood_exposure_ruleB_qt` *(precision robustness)*

| Attribute | Value |
|---|---|
| Definition | 1 only when district explicitly identified in EM-DAT location field |
| Treatment rate (locked) | 0.90% — 209 events · 141 districts ever exposed |
| Interpretation | Higher precision; lower power. H2 Rule B instrument is weak (F = 8.949 < 10) — second stage results labeled suggestive throughout without exception |

### Flood Lags — Distributed Lag Models

| Variable | Construction | Used in |
|---|---|---|
| `flood_ruleA_L1` | L1 within composite group | H3 (Script 29b) |
| `flood_ruleA_L2` | L2 within composite group | H3 (Script 29b) |
| `flood_ruleA_L3` | L3 within composite group | R5 (Script 35) |
| `flood_ruleA_L4` | L4 within composite group | R5 (Script 35) |
| `flood_ruleB_L1–L4` | Rule B equivalents | Robustness throughout |

**Lag missing-value arithmetic (locked).** Each lag introduces exactly
631 additional NaNs (one per district — the first observation per group).
Any deviation from 631 × k signals a composite key error or sort-order
violation.

| Lag | Expected missing | Status |
|---|---|---|
| L1 | 631 | PASS |
| L2 | 1,262 | PASS |
| L3 | 1,893 | PASS |
| L4 | 2,524 | PASS |

---

## IV. Displacement Proxy — VIIRS Nighttime Lights

### `mean_radiance`

| Attribute | Value |
|---|---|
| Definition | District-quarter mean VIIRS radiance, pixel-area weighted |
| Unit | nW/cm²/sr |
| Source | VIIRS DNB monthly composites, Colorado School of Mines EOG, tile 75N060E |
| Scripts | 21–22b — monthly extraction, deduplication, quarterly aggregation (mean radiance, sum pixels), composite key groupby throughout |
| Verified range | min = 0.0003 · max = 35.8691 · mean = 0.6955 · median = 0.4266 · SD = 1.6884 |

**Script 26 validation (all 9 checks PASS):** 0 NaN, 0 Inf, 0 negative,
balanced panel (631 × 40 = 25,240). AURANGABAD litmus: BIHAR = 0.7222,
MAHARASHTRA = 0.5094 (Δ = 0.2128) — confirmed distinct. All 7
homonymous pairs produce distinct radiance values, confirming VIIRS
extraction used composite keys correctly.

### `log_lights_qt`

- **Construction:** `ln(mean_radiance + 0.001)`
- **Offset: +0.001 (locked)** — corrected from +0.01 (v2.2) and +1
  (v2.1)
- **Rationale:** Approximately 80% of observations have mean_radiance
  < 1 nW/cm²/sr (rural and semi-urban districts). `log(x + 1)` approximates
  the identity function in this range, eliminating log-scale compression for
  the majority of the sample. `log(x + 0.001)` preserves the intended
  elasticity interpretation throughout the full radiance distribution.
  `log(x + 1)` is reserved for deposits where scale is Crores.
- **Verified range:** min = −6.6447 · max = 3.5559 · mean = −0.8326 ·
  SD = 0.8377

### `lights_change_qt`

- **Construction:** `log_lights_qt.diff()` within `(district_gadm,
  state_gadm)` groups, sorted by `year`, `q`
- **Missing values:** exactly 631 (first observation per district —
  consistent with 100% VIIRS coverage)
- **Usable N:** 22,716 observations
- **Verified range:** min = −2.2385 · max = 1.6938 · mean = 0.0170 ·
  SD = 0.3530

---

## V. Fixed Effects and Standard Errors

### District FE *(H1, H2, H4 only)*

`C(district_state_id)` — composite key, 631 effects.

Using `district_gadm` alone produces 624 FE instead of 631. This
misspecification contaminates FE absorption, cluster assignments, and
heterogeneity variable construction when the same groupby error
propagates to $Z_i$ construction. All pre-March 2026 benchmarks were
produced under this misspecification. All values in this codebook reflect
the corrected specification.

H3 uses quarter FE only. Log-differencing absorbs district-level time
trends; district FE are redundant by construction. Pre-committed before
estimation.

### Quarter FE *(all specifications)*

36 in H1/H2/H4. 35 in H3 (L2 restriction structurally drops 2015Q1–2015Q2 —
correct, not a bug). Quarter FE absorb national seasonality, macroeconomic
shocks, monetary policy shifts, and national-level inflation trends.

### Standard Errors

Clustered by `district_state_id` throughout all specifications.
Clustering on `district_gadm` alone assigns 7 homonymous pairs to
incorrect shared clusters — the same misspecification as the FE error.

---

## VI. Heterogeneity Variables (H4)

All three $Z_i$ variables were pre-committed in Hypotheses_Formal_v2.6.md
before regression execution. Construction uses composite `district_state_id`
groupby throughout. All labeled as proxies where true administrative
classifications are unavailable.

### H4a: `urban_proxy`

- **Construction:** Time-invariant indicator. Above-median district mean
  `log_lights_qt` over the full analysis period, grouped by
  `district_state_id`. Median `log_lights_qt` = −0.8900.
- **Split:** Above-median: 315 districts · At/below: 316 districts
- **Label in paper:** "Urban proxy (lights-based, above-median mean
  radiance)"
- **Result (Script 30b, locked):**

| Rule | Interaction β̂ | SE | p | Status |
|---|---|---|---|---|
| A | −0.001666 | 0.002664 | 0.532 | **Null** |
| B | +0.007479 | 0.006929 | 0.280 | **Null** |

**Mandatory disclosure (Constraint 4).** The February 6 result
(p < 0.001) was spurious — `urban_proxy` constructed on `district_gadm`
alone collapsed AURANGABAD BIHAR and MAHARASHTRA, contaminating the
median `log_lights` threshold. After composite key correction the signal
disappears entirely. Null is the correct and final result. Must be
disclosed explicitly in the paper — paper body or footnote.

### H4b: `high_exposure_proxy`

- **Construction:** Time-invariant indicator. Above-median cumulative
  `flood_exposure_ruleA_qt` over the full period, grouped by
  `district_state_id`. Median = 3.0 cumulative events (integer). Threshold
  is strictly greater: districts with exactly 3.0 events fall in the
  low-exposure group. Disclose in paper.
- **Split:** High-exposure (> 3.0): 255 districts · Low (≤ 3.0): 376
  districts
- **Label in paper:** "High-exposure proxy (above-median cumulative flood
  events)"
- **Result (Script 30b, locked):**

| Rule | Baseline β̂ | Interaction β̂ | SE | p | Status |
|---|---|---|---|---|---|
| A | +0.004700 | −0.006810 | 0.002932 | 0.020 | **Suggestive only ⚠** |
| B | +0.012016 | −0.013419 | 0.007670 | 0.080 | Marginal |

**Winsorization failure — mandatory disclosure (Constraint 12).**
Rule A interaction p = 0.865 on the winsorized panel (Script 37; 2.01%
of observations clipped symmetrically). The baseline significance is
entirely driven by extreme deposit observations. H4b is **demoted** from
supported to suggestive. Cannot be presented as a robust finding under
any framing.

Required language (exact): *"The high flood exposure interaction (H4b)
is significant in the baseline specification (Rule A: β̂ = −0.007,
p = 0.020) but does not survive winsorization of the top and bottom 1%
of deposit growth observations (p = 0.865). The effect is sensitive to
extreme observations and should be interpreted as suggestive evidence
only."*

### H4c: `monsoon_qt`

- **Construction:** Time-varying indicator. `indicator(q == 3)` —
  July–September. Not a proxy; directly observed from the panel structure.
- **Split:** Q3 (monsoon): 5,679 obs · Non-Q3: 17,668 obs
- **Result (Script 30b, locked):**

| Rule | Baseline β̂ | Interaction β̂ | SE | p | Status |
|---|---|---|---|---|---|
| **A** | **−0.004700** | **+0.012495** | **0.002884** | **<0.001** | **Confirmed ★** |
| B | −0.000838 | +0.002287 | 0.007968 | 0.774 | Null |

95% CI on Rule A interaction: [+0.006843, +0.018147]

Net monsoon effect (Rule A): −0.0047 + 0.0125 = +0.0078. Moderate
flood events during the monsoon quarter do not reduce deposits —
anticipated seasonal flooding coincides with agricultural income inflows.
Severe floods (Rule B) override this seasonal buffer entirely.

Required language (exact, Constraint 2): *"Monsoon seasonality moderates
the deposit response to moderate-intensity floods (Rule A: β̂ = +0.012,
p < 0.001) but not to severe flood events (Rule B: p = 0.774). The
heterogeneity result is fragile to flood intensity definition."*

---

## VII. IV Pipeline Variables

### `lights_hat_qt`

- **Definition:** Fitted values from H1 first stage (flood instrument)
- **Rule:** Diagnostic storage only. Never interpreted as observed lights.
  Never used directly as a regressor outside the IV2SLS specification.

### `first_stage_F`

- **Definition:** $F = t^2$ for a single excluded instrument
  (Wooldridge 2010, p. 104)
- **Rationale:** linearmodels `first_stage` F-statistic overflows
  numerically at 666 exogenous columns. For a single excluded instrument,
  $F = t^2$ exactly.
- **Locked values (Script 28b):**

| Rule | First-stage t | F = t² | Threshold | Instrument |
|---|---|---|---|---|
| A | −5.888 | **34.673** | 16.38 (5% maximal size) | **Strong** |
| B | −2.992 | **8.949** | 10.00 | **Weak** |

Rule B second stage labeled suggestive throughout; causal language
removed from abstract and conclusions. $F$-stat reported in every table
containing H2 results.

---

## VIII. Robustness: Final Status

| Check | Script | Outcome |
|---|---|---|
| R1 — Both flood rules | 27b–30b | Complete — both rules reported in all core tables |
| R2 — Placebo timing | 34 | Two-phase cycle confirmed; pre-period p = 0.011, survives district FE (p = 0.019) |
| R3 — Winsorization (1%/99%, 450 obs, 2.01%) | 37 | H3 robust ✓ · **H4b fails (p = 0.865) ✗** |
| R4 — Nominal INR | 32 | Quarter FE absorb national price trends; limitation acknowledged |
| R5 — Longer lags (t₀+3, t₀+4) | 35 | Both null; effect decays at t₀+2 |
| R6 — State clustering (34 clusters) | 36 | H3 p = 0.034 ✓ · H1 p = 0.105 |
| R6b — Wild cluster bootstrap (999 iter.) | 36b | **H1 fails: Rule A p = 0.158 · Rule B p = 0.267** |
| R7 — IV instrument discipline | 28b | Rule B F = 8.949; suggestive label applied throughout |
| R8 — Northeast sensitivity | 33 | H3 t₀+2 robust to NE exclusion ✓ |

**Nine checks complete (R1–R8 + R6b). Zero open items.**

### R2 — Two-Phase Liquidity Cycle (mandatory disclosure)

Placebo test (Script 34, `09_placebo_timing.csv`): flood at $t$ predicts
**higher** deposit growth at $t-1$. Signal is positive and survives
district FE.

| Test | β̂ | SE | p | District FE |
|---|---|---|---|---|
| Test 2 (quarter FE only) | +0.004664 | 0.001841 | 0.011 | No |
| Test 2b (quarter + district FE) | +0.004417 | 0.001881 | 0.019 | Yes |

A pre-existing downward trend in deposits would produce a negative
pre-period signal. The positive sign rules this out. The pattern
identifies a two-phase household liquidity cycle: anticipatory saving
ahead of the predictable flood season (+0.005), followed by post-flood
deposit withdrawal (−0.007) two quarters after the event.

Required language (exact, Constraint 11): *"Flood exposure at time t
predicts higher deposit growth at t−1 (β̂ = +0.005, p = 0.011), a
signal that survives the inclusion of district fixed effects (β̂ =
+0.004, p = 0.019). This pre-period effect is positive and opposite
in sign to the t₀+2 withdrawal effect (−0.007), indicating a two-phase
household liquidity cycle — anticipatory saving ahead of the predictable
flood season followed by post-flood deposit withdrawal — rather than a
pre-existing downward trend in deposits."*

---

## IX. Locked Regression Results

All results from linearmodels PanelOLS, Scripts 27b–30b.
District FE = 631. SE clustered by `district_state_id`.

### H1 — Floods → Lights (Script 27b)

Quarter FE = 36 · N = 22,716

| Rule | β̂ | SE | t | p |
|---|---|---|---|---|
| A | −0.044468 | 0.007784 | −5.7124 | <0.001 |
| B | −0.058446 | 0.019768 | −2.9566 | 0.003 |

Rule B > Rule A in magnitude — attenuation bound confirmed. H1 does
not survive state-level clustering (wild bootstrap Rule A p = 0.158,
Rule B p = 0.267). Coefficient stable across all SE specifications.
See Constraint 13.

### H2 — Lights → Deposits IV 2SLS (Script 28b)

Quarter FE = 36 · N = 22,442 · Iterative demeaning: 8 iterations,
tolerance 1×10⁻¹⁴

| Rule | β̂ | SE | t | p | First-stage F | Instrument |
|---|---|---|---|---|---|---|
| A | −0.008388 | 0.034022 | −0.2465 | 0.805 | 34.673 | Strong |
| B | −0.006776 | 0.059698 | −0.1135 | 0.910 | 8.949 | Weak |

Null. H2 tests the contemporaneous window by construction. H3 confirms
effects are lagged — the IV specification tests a zero-effect window by
design. See Constraint 1.

### H3 — Distributed Lag (Script 29b)

Quarter FE = 35 · N = 21,837 · No district FE (pre-committed)

| Lag | β̂ (Rule A) | SE | t | p | Status |
|---|---|---|---|---|---|
| t₀ — flood quarter | +0.000609 | 0.001462 | +0.4167 | 0.677 | Null |
| t₀+1 — one quarter after | +0.001505 | 0.001114 | +1.3517 | 0.177 | Null |
| **t₀+2 — two quarters after** | **−0.007005** | **0.001644** | **−4.2609** | **<0.001** | **Confirmed ★** |

95% CI at t₀+2: [−0.010227, −0.003783]

Robust to: winsorization (p < 0.001, β̂ = −0.007115, δ = 0.000110),
Northeast exclusion, state-level clustering (p = 0.034), near-zero
exclusion (δ = 0.000294). Longer lags t₀+3 and t₀+4 null (Script 35) —
effect decays at two quarters.

### H4 — Heterogeneity (Script 30b)

Quarter FE = 36 · District FE = 631 · N = 22,442

| Spec | Rule | Baseline β̂ | Interaction β̂ | SE | p | Status |
|---|---|---|---|---|---|---|
| H4a: Urban proxy | A | +0.001207 | −0.001666 | 0.002664 | 0.532 | Null |
| H4a: Urban proxy | B | −0.002890 | +0.007479 | 0.006929 | 0.280 | Null |
| H4b: High exposure | A | +0.004700 | −0.006810 | 0.002932 | 0.020 | **Suggestive only ⚠** |
| H4b: High exposure | B | +0.012016 | −0.013419 | 0.007670 | 0.080 | Marginal |
| **H4c: Monsoon** | **A** | **−0.004700** | **+0.012495** | **0.002884** | **<0.001** | **Confirmed ★** |
| H4c: Monsoon | B | −0.000838 | +0.002287 | 0.007968 | 0.774 | Null |

---

## X. Specification Reference

| Spec | N | Outcome | Key Regressor(s) | District FE | Quarter FE |
|---|---|---|---|---|---|
| H1 | 22,716 | `lights_change_qt` | `flood_exposure_ruleA/B_qt` | Yes (631) | 36 |
| H2 IV | 22,442 | `deposit_change_qt` | `lights_change_qt` (instrumented) | Yes (631) | 36 |
| H3 | 21,837 | `deposit_change_qt` | Flood t₀, t₀+1, t₀+2 | **No** | 35 |
| H4 | 22,442 | `deposit_change_qt` | Flood × Z_i | Yes (631) | 36 |

SE clustered by `district_state_id` in all specifications.

---

## XI. Data State

All files verified clean as of March 21, 2026. Results locked.
Do not re-run.

| File | Rows | Key verification |
|---|---|---|
| `district_crosswalk_draft.csv` | 762 | Hard assert: `len == 762` |
| `flood_exposure_panel.csv` | 26,640 | Rule A: 2,518 raw events · 666 district-state pairs |
| `rbi_deposits_panel.csv` | 50,192 | AURANGABAD BIHAR 2015Q1 = 4,422 Crores |
| `master_panel_raw.csv` | 26,640 | BALOD 2022Q4 = 3,296 Crores |
| `regression_panel_final.csv` | 23,347 | 23 columns · lag arithmetic exact |
| `regression_panel_final_winsor.csv` | 23,347 | 24 columns · 450 obs clipped (2.01%) |
| `viirs_quarterly_panel_clean.csv` | 25,240 | 631 × 40 · all 9 validation checks PASS |

**Final paper table CSVs — linearmodels only. Do not substitute
statsmodels outputs.**

| File | Script | Contents |
|---|---|---|
| `02b_H1_linearmodels.csv` | 27b | H1 first stage, both rules |
| `03b_H2_linearmodels.csv` | 28b | H2 IV 2SLS, both rules |
| `04b_H3_linearmodels.csv` | 29b | H3 distributed lag, both rules |
| `05b_H4_linearmodels.csv` | 30b | H4 heterogeneity, all specifications |
| `09_placebo_timing.csv` | 34 | R2 placebo timing tests |

**Locked analysis sample:** 631 composite pairs × 37 quarters =
**23,347 observations**  
**Rule A:** 2,238 events (9.59%) · 569 districts ever exposed  
**Rule B:** 209 events (0.90%) · 141 districts ever exposed  
**VIIRS coverage:** 100.0% · **Deposit coverage:** 98.9%

---

## XII. Known Issues

### Resolved

| Issue | Script | Resolution |
|---|---|---|
| statsmodels rank warning (Scripts 27–30) | 27b–30b | Resolved: linearmodels PanelOLS throughout |
| Script 32b negative-tail conclusion error | 32b | Resolved: correct conclusion documented in Section II (2023 anomaly); left-tail asymmetry confirmed, NE-concentrated |
| Northeast sensitivity | 33 | Resolved: H3 t₀+2 robust to NE exclusion |
| Composite FE misspecification | All | Resolved: `district_state_id` composite key throughout all scripts (Mar 2026) |
| Crosswalk regression (769→762) | 08 | Resolved: permanent rewrite with row-level dedup + 762-row hard assert |
| Deposit extraction bugs (Script 13) | 13 | Resolved: column offset fix + state-blind merge fix |
| RBI 2016–2017 gap | 17 | Resolved: structural exclusion confirmed; demonetization period documented |
| Zero-change diagnostic | 38 | Resolved: zero exact zeros confirmed; near-zero exclusion δ = 0.000294; H3 stable |

---

## XIII. Script Contract

Every script must, without exception:

1. Assert input file row counts and column counts at load
2. Log input and output file paths with absolute references
3. Log row counts before and after every major transformation
4. Log all constant choices (log offsets, thresholds, winsorization bounds)
5. Assert expected output row count and column count before saving
6. Write a log file to `05_Outputs/Logs/` with `encoding='utf-8'`
7. Use `datetime.now()` for run timestamps — never hardcode dates
8. Use no Unicode symbols in log files — Windows cp1252 encoding risk

---

## XIV. File I/O Contract

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

**GADM as geographic standard.** RBI district naming shifts across
publication years as administrative boundaries are redrawn. GADM v4.1
provides stable polygon boundaries for flood matching and as the
crosswalk anchor. 83.2% of RBI districts match to GADM (threshold: 80%);
128 unmatched districts are excluded and disclosed in the Data section.

**Rule A as primary specification.** 9.59% treatment rate maximises
statistical power. Rule B (0.90%) is the strict precision check. Both
reported in all core tables (R1). Rule A is preferred for power; Rule B
for instrument credibility (where strong — Rule A F = 34.673 only).

**Option 3 sample restriction.** Dropping both unreliable deposit
quarters (2016Q3–2017Q1) and 35 structural-zero districts yields 98.9%
deposit coverage with 100% treatment-outcome overlap. Option 1 (quarters
only) retains 35 structural-zero districts. Option 2 (districts only)
retains the demonetization blackout, creating false breaks in distributed-
lag specifications. Option 3 is the correct choice on both dimensions.

**Log offset +0.001 for VIIRS.** India is predominantly rural.
Approximately 80% of observations have mean_radiance < 1 nW/cm²/sr.
`log(x + 0.001)` preserves the intended elasticity interpretation
throughout the full radiance distribution. `log(x + 1)` is reserved
for deposits at Crore scale.

**Demonetization gap.** 2016Q3–2017Q1 absent from the panel. The
discontinuity is absorbed by quarter FE. Must be disclosed explicitly
in Section 3.4 (Panel Construction). Never report 2016 or 2017 as
full-year figures

**Superseded outputs.** Scripts 27–30 (statsmodels) retained in
`07_Archive/Superseded_Scripts/` as a coefficient-stability audit trail.
All paper tables use Scripts 27b–30b (linearmodels) exclusively.
Coefficients are stable across both estimators.

---

*Version 2.6 — locked March 21, 2026*  
*Principal Investigator: Jaseel Badar, Harvard University*  
*Repository: github.com/JaseelBadar/Climate-Migration-Bank-Fragility*
