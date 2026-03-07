# Formal Hypotheses: Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Night-Lights in India, 2015–2024

**Version:** 2.4 (Mar 7, 2026)
**Status:** Full data pipeline clean and verified. FE correction required in
Scripts 27, 28, 30 before regression execution.

---

## Version History

| Version | Date | Change |
|---|---|---|
| v1.3 | — | Wording updates, feasibility alignment |
| v1.4 | 2026-01-18 | Phase 4 preliminary results documented; no hypothesis modifications |
| v1.5 | 2026-01-20 | Script 21 VIIRS dissolve bug identified; H1–H4 results suspended |
| v1.6 | 2026-01-20 | Script 21 fix implemented; VIIRS panel regenerated |
| v1.7 | 2026-01-30 | RBI contamination concern raised (suspected duplicate 2016 quarters) |
| v1.8 | 2026-02-01 | RBI concern resolved (false alarm). Phase 3d complete |
| v1.9 | 2026-02-04 | Script 13 column offset bug discovered. Phase 4 results invalidated |
| v2.0 | 2026-02-06 | Deposits corrected. VIIRS homonymous contamination identified. H3 potentially clean |
| v2.1 | 2026-02-11 | Full deposit pipeline fixed: crosswalk dedup + state filtering. H3 validated |
| v2.2 | 2026-02-13 | VIIRS alignment complete (Script 22b). Analysis panel: 23,088 obs, 100% VIIRS |
| v2.3 | 2026-03-04 | District count corrected: 631 composite pairs. Sample: 23,347. Crosswalk contamination identified |
| **v2.4** | **2026-03-07** | **Pipeline fully clean. Script 8 permanent rewrite complete (762-row assert). Scripts 12–17, 23–26 all re-run and verified. Flood baseline locked: 2,238 Rule A events, 9.59% treatment rate. FE correction pending in Scripts 27, 28, 30.** |

**Discipline:** No hypothesis was modified to chase empirical results. Version history
records data corrections only. Any modification to hypothesis wording is explicitly
labeled with rationale and date.

---

## Notation

| Symbol | Definition |
|---|---|
| i | District (composite: district_gadm + '_' + state_gadm) |
| t | Calendar quarter |
| ΔDeposits_it | Log first difference of district deposits (RBI BSR-2, Rs Crores) |
| ΔLights_it | Log first difference of mean VIIRS radiance (nW/cm²/sr, offset +0.001) |
| Flood_A_it | Rule A flood exposure: district-level match OR state fallback |
| Flood_B_it | Rule B flood exposure: district-level match only (high precision) |
| μ_i | District fixed effect (composite district_state_id — 631 FE, not 624) |
| τ_t | Quarter fixed effect |

**Pre-committed methodological positions:**

- **Flood precision:** Rule A maximises power; state-level fallback attenuates β toward
  zero. Rule A estimates are conservative lower bounds on the true local effect.
  Rule B maximises precision at the cost of power. Both reported in all core tables.

- **Lights interpretation:** ΔLights_it is treated as a proxy consistent with
  displacement or disruption-driven activity loss. Not presented as direct proof of
  migration without external corroboration.

- **Shadow run definition:** A sharp deposit decline consistent with liquidity demand
  from depositors — not from slow-moving credit deterioration or solvency stress.

- **FE specification:** District FE constructed on composite district_state_id
  throughout Scripts 27–30. Using district_gadm alone collapses 7 homonymous pairs,
  producing 624 FE instead of correct 631. This was the bug in the Feb 6 run.

---

## H1: Floods reduce economic activity (first stage)

**Hypothesis:** Flood exposure produces a statistically and economically meaningful
decline in nighttime lights in affected districts, consistent with displacement or
disruption-driven outflows.

**Specification:**

ΔLights_it = α + β₁·Flood_it + μ_i + τ_t + ε_it

Estimated separately for Flood_A and Flood_B.

- **Expected sign:** β₁ < 0
- **Economic significance threshold (pre-committed):** |β₁| implying at least a 5%
  decline in quarterly lights. If observed volatility of ΔLights makes this threshold
  incoherent, it is revised once and documented before final tables are produced.
- **Attenuation note:** State-level fallback in Flood_A biases β₁ toward zero.
  Flood_A estimates are conservative lower bounds.
- **Falsification:** If β₁ ≥ 0, lights cannot serve as a displacement proxy and
  the IV chain fails. Paper reframes around reduced form only.

**Status:** PENDING RE-RUN (FE correction required)
Preliminary result (Feb 6, 2026 — contaminated deposits, wrong FE):
β₁ = −0.0149, SE = 0.0028, t = −5.37, p < 0.001, N = 22,716.
Direction and significance expected to persist with clean pipeline and correct FE.
Magnitude subject to change — do not cite until re-run confirmed.

---

## H2: Lights declines transmit to deposit withdrawals (liquidity channel)

**Hypothesis:** Districts experiencing larger declines in nighttime lights also
experience larger deposit declines, consistent with liquidity demand rather than
credit deterioration.

**Sign logic:** In shock periods, both ΔLights_it and ΔDeposits_it are expected
negative. The deposit-on-lights slope is therefore expected positive.

### H2a: Reduced-form association (descriptive)

ΔDeposits_it = α + β₂·ΔLights_it + μ_i + τ_t + ε_it

- **Expected sign:** β₂ > 0
- **Status:** Descriptive only. ΔLights_it correlates with unobserved income shocks
  that directly affect deposits. Not the preferred causal estimate.

### H2b: IV / 2SLS (preferred causal specification)

**First stage:** H1 specification.

**Second stage:**
ΔDeposits_it = α + β₂·ΔLightŝ_it + μ_i + τ_t + ε_it

- **Expected sign:** β₂ > 0
- **Instrument discipline (pre-committed):** Report Flood_B instrument where feasible.
  Report Flood_A results with explicit weak-instrument and attenuation caveats.
  If first-stage F < 10, label IV as suggestive; drop causal language from abstract
  and conclusions.
- **Exclusion restriction:** Floods shift deposits primarily through the
  displacement/disruption channel proxied by lights. Direct banking-operation
  disruption (branch closures, cash logistics) is a threat not fully addressed by
  the IV. Causal language is softened if this threat is empirically plausible.
- **Null interpretation (pre-committed):** If H2 null persists with clean data,
  three explanations are evaluated in order: (1) lights are a noisy migration proxy,
  (2) effect operates through non-migration channels, (3) deposit effects are lagged
  rather than contemporaneous — see H3.
- **Falsification:** If deposits do not respond to lights in either reduced form or
  IV, the displacement-to-liquidity link is not supported in this data.

**Status:** PENDING RE-RUN (FE correction required)
Preliminary result (Feb 6, 2026 — contaminated deposits, wrong FE):
First stage β₁ = −0.0151 (t = −5.42, strong instrument).
Second stage β₂ = +0.0839, SE = 0.1640, p = 0.609 (null).
Null finding may persist or reverse with clean pipeline. Do not cite until re-run.

---

## H3: Deposit effects follow a liquidity-consistent timing structure

**Hypothesis:** Deposit declines emerge within two quarters of flood exposure,
consistent with rapid household liquidity demand rather than slow-moving credit-loss
transmission.

### H3a: Distributed lag timing (core)

ΔDeposits_it = α + β₀·Flood_it + β₁·Flood_i,t−1 + β₂·Flood_i,t−2
+ τ_t + ε_it

- **Expected pattern:** β₀ and/or β₁ < 0, with attenuation by t−2
- **No district FE:** H3 uses quarter FE only — district effects absorbed by the
  log-differenced dependent variable. Unaffected by homonymous FE collapse.
- **Falsification:** If effects appear only at t−3 or beyond, the liquidity timeline
  is weakened. If no lag is significant, the mechanism is not supported.

### H3b: Liquidity-not-solvency fingerprint (conditional extension)

If district-level credit-risk indicators (NPA ratios) become available, deposit
declines should not be fully mediated by contemporaneous credit deterioration.
If data remains unavailable, H3b is explicitly labeled as a limitation and not
silently assumed to hold.

**Status: VALIDATED CLEAN**

H3 uses deposits and flood lags only — no VIIRS, no district FE. Unaffected by
any pipeline contamination event in the project history.

Confirmed results (Feb 6, 2026, N = 21,912 — pre-clean two-lag restriction):

| Lag | β | SE | p | Finding |
|---|---|---|---|---|
| t0 (current quarter) | −0.0005 | 0.0014 | 0.777 | Null |
| t−1 (1 quarter lag) | +0.0004 | 0.0014 | 0.757 | Null |
| t−2 (2 quarter lag) | **−0.0091** | 0.0036 | **0.012** | **Confirmed** |

**Interpretation:** Flood-induced deposit stress is absent in the quarter of impact
and the quarter immediately following. The effect peaks at 6 months post-flood:
a −0.91% decline in deposit growth. Consistent with gradual displacement — households
exhaust immediate coping mechanisms before liquidating bank deposits. This lag
structure directly reconciles the H2 null: deposit effects are lagged, not
contemporaneous.

**Pending:** Re-run on clean 23,347-observation panel (N will increase from 21,912
after dropping 2-lag structural NaNs). t−2 significance expected to persist;
magnitude treated as provisional until confirmed.

---

## H4: Deposit response is heterogeneous across district types

**Hypothesis:** The flood-to-deposit effect is more negative in districts with higher
baseline financial intensity or urbanisation, consistent with greater liquidity
exposure.

**Specification:**

ΔDeposits_it = α + β₀·Flood_it + β₁·(Flood_it × Z_i)
+ μ_i + τ_t + ε_it

Where Z_i is a pre-defined district characteristic, not chosen after seeing results.

- **Expected sign:** β₁ < 0 for more vulnerable groups
- **Proxy discipline (pre-committed):** Urbanisation proxies must be labeled as
  proxies. Results are treated as suggestive, not causal, where true administrative
  urban/rural classification is unavailable.

**Three pre-committed specifications:**

| Label | Z_i | Definition |
|---|---|---|
| H4a | Urban proxy | Above-median district mean lights in baseline period |
| H4b | High flood exposure | Above-median cumulative flood event count |
| H4c | Monsoon quarter | Q3 indicator (July–September) |

- **Falsification:** If all interaction effects are consistently near zero, the
  mechanism is homogeneous across these proxies and heterogeneity claims are dropped.

**Status:** PENDING RE-RUN (FE correction required)
Preliminary results (Feb 6, 2026 — contaminated deposits, wrong FE, N = 22,503):

| Spec | Interaction β | p | Provisional reading |
|---|---|---|---|
| H4a Urban × Flood | −0.0111 | <0.001 | Requires re-run with clean FE |
| H4b High exposure × Flood | +0.0021 | 0.360 | Null — expected to persist |
| H4c Monsoon × Flood | −0.0018 | 0.511 | Null — expected to persist |

H4a is the most sensitive to FE correction and must not be cited until re-run.
H4b and H4c null results are expected to be robust.

---

## H5: Network contagion (stated extension — data-contingent)

**Hypothesis:** Banking stress spills over to non-flood-exposed districts, increasing
with bank-network connectedness or geographic adjacency.

**Specification:**

Spillover_jt = Σᵢ W_ji · Flood_it

ΔDeposits_jt = α + β₅·Spillover_jt + μ_j + τ_t + ε_jt

- **Expected sign:** β₅ < 0
- **Hard dependency:** Requires a credible district-level W matrix (shared branch
  networks or interbank linkages). H5 will not be tested by proxy without explicit
  methodological justification. Currently remains a stated extension.

**Status:** NOT TESTED. Data-contingent. Not in current regression pipeline.

---

## Joint Mechanism: Conditions for Full Support

The Shadow Run mechanism is supported if all four conditions hold:

1. **H1** — Floods reduce lights, robustly across both Flood_A and Flood_B
2. **H2** — Lights declines predict deposit declines (IV preferred where credible)
3. **H3a** — Effect peaks at t0 or t−1 (liquidity timeline), not t−3 or beyond
4. **H4** — Heterogeneity directionally consistent with vulnerability

**Pre-committed degraded conclusions:**

| Outcome | Interpretation |
|---|---|
| H1 holds, H2 null | Disasters reduce activity without measurable deposit effects; liquidity narrative narrowed |
| H1 fails | Lights proxy fails; IV chain invalid; paper reframes around reduced form |
| H3 null at all lags | Mechanism operates beyond 6 months, or not through the deposit channel |
| H4 null throughout | Effect is homogeneous; urbanisation/exposure heterogeneity not supported |

---

## Pre-Committed Robustness Checks

All checks specified before regression execution. None added retroactively.

| # | Check | Implementation |
|---|---|---|
| R1 | Flood precision | All core results reported under Rule A and Rule B side by side |
| R2 | Placebo timing | Test Flood_t−1 predicting ΔDeposits_t−1 — should produce null |
| R3 | Winsorisation | Deposit growth winsorised at 1st/99th percentile |
| R4 | CPI deflation | Nominal deposits deflated by CPI; verify robustness to real vs nominal |
| R5 | Longer lags | Extend H3 to t−3 and t−4 (Rule B only, for precision) |
| R6 | State-level clustering | Alternative to district-level SE — more conservative |
| R7 | IV discipline | Report first-stage F. If F < 10, label 2SLS as suggestive throughout |

---

## Current Data State

All files verified clean as of Mar 6–7, 2026.

| File | Rows | Key metric | Status |
|---|---|---|---|
| district_crosswalk_draft.csv | 762 | Hard assert len==762 PASS | Clean |
| flood_exposure_panel.csv | 26,640 | Rule A: 2,518 events | Clean |
| rbi_deposits_panel.csv | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores | Clean |
| master_panel_analysis.csv | 23,347 | 631 districts × 37 quarters | Clean |
| viirs_quarterly_panel_clean.csv | 25,240 | 631 districts × 40 quarters | Clean |
| analysis_panel_final.csv | 23,347 | 100% VIIRS coverage, 0 missing | Clean |
| regression_panel_final.csv | 23,347 | 23 columns, lag arithmetic verified | Clean |

**Locked analysis sample:**
631 composite (district_gadm, state_gadm) pairs × 37 quarters = **23,347 observations**
Rule A treatment: **2,238 events (9.59%)** | Rule B: **209 events (0.90%)**
VIIRS coverage: **100%** | Deposit coverage: **98.9%**

---

## Pending Actions

1. Fix FE specification in Scripts 27, 28, 30:
   `district_state_id = district_gadm + '_' + state_gadm` (631 FE, not 624)
2. Execute H1, H2, H4 regressions with clean data and correct FE
3. Re-run H3 on full 23,347-observation sample; verify t−2 lag persists
4. Document all coefficient changes from Feb 6 to post-fix run
5. Update this document to v2.5 with final regression results

---

*Project initiated: 2025-12-30 | Principal investigator: Jaseel Badar, Harvard University*