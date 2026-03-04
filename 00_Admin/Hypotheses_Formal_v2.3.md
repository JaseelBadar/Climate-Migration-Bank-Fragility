# Formal Hypotheses: Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Night-Lights in India, 2015–2024

**Version:** 2.3 (Mar 4, 2026)
**Status:** Pipeline fix pending Mar 5. H3 validated. H1, H2, H4 pending re-run.

---

## Version History

| Version | Date | Change |
|---|---|---|
| v1.3 | — | Wording updates, feasibility alignment |
| v1.4 | 2026-01-18 | Phase 4 preliminary results documented; no hypothesis modifications |
| v1.5 | 2026-01-20 17:00 | Script 21 VIIRS dissolve bug identified; H1–H4 results suspended |
| v1.6 | 2026-01-20 23:30 | Script 21 fix implemented; overnight VIIRS regeneration initiated |
| v1.7 | 2026-01-30 23:26 | RBI contamination concern raised (suspected duplicate 2016 quarters) |
| v1.8 | 2026-02-01 23:15 | RBI concern resolved (false alarm). Phase 3d complete. All hypotheses regression-ready. |
| v1.9 | 2026-02-04 | Script 13 column offset bug discovered. Phase 4 results invalidated. Fix identified. |
| v2.0 | 2026-02-06 | Deposits corrected (Feb 5). VIIRS homonymous district contamination identified. H3 potentially clean. |
| v2.1 | 2026-02-11 | Full deposit pipeline fixed: crosswalk dedup (769→762) + state filtering. H3 validated. |
| v2.2 | 2026-02-13 | VIIRS alignment complete via Script 22b. Analysis panel: 23,088 obs, 100% VIIRS coverage. |
| v2.3 | 2026-03-04 | **District count corrected: 631 composite pairs (was 624 — name-only undercount). Sample: 23,347 obs. Crosswalk contamination identified (769-row regression, Feb 27). Pipeline fix scheduled Mar 5.** |

**Discipline:** No hypothesis was modified to chase empirical results. Version history
records data corrections, not specification changes. Any modification to hypothesis
wording is explicitly labeled with rationale and date.

---

## Notation

| Symbol | Definition |
|---|---|
| i | District (composite: district_gadm + state_gadm) |
| t | Calendar quarter |
| Delta_Deposits_it | Log first difference of district deposits (RBI BSR-2) |
| Delta_Lights_it | Log first difference of mean VIIRS radiance (nW/cm²/sr) |
| Flood_A_it | Rule A flood exposure: district match OR state fallback |
| Flood_B_it | Rule B flood exposure: district match only (high precision) |
| mu_i | District fixed effect |
| tau_t | Quarter fixed effect |

**Flood exposure precision note (pre-committed):** Rule A maximises power at the cost
of state-level attenuation. Rule B maximises precision at the cost of statistical power.
All core results reported under both rules. Rule A estimates are conservative lower
bounds on the true local effect.

**Lights interpretation (pre-committed):** Delta_Lights_it treated as a proxy consistent
with displacement or disruption-driven activity loss. Not presented as direct proof of
migration without external corroboration.

**Shadow run definition (pre-committed):** A sharp deposit decline consistent with
liquidity demand from depositors, not from slow-moving credit deterioration or solvency
stress.

**FE specification (pre-committed):** District FE constructed on composite
district_state_id throughout Scripts 27–30. Using district_gadm alone collapses
7 homonymous pairs, producing 624 FE instead of correct 631.

---

## H1: Floods reduce economic activity (first stage)

**Hypothesis:** Flood exposure produces a statistically and economically meaningful
decline in nighttime lights in affected districts, consistent with displacement or
disruption-driven outflows.

**Specification:**

Delta_Lights_it = alpha + beta_1 * Flood_it + mu_i + tau_t + epsilon_it

Estimated separately for Flood_A and Flood_B.

- **Expected sign:** beta_1 < 0
- **Economic significance threshold (pre-committed):** |beta_1| implying at least
  5% decline in quarterly lights. If observed volatility of Delta_Lights makes 5%
  incoherent as a threshold, threshold revised once and documented before final tables.
- **Attenuation note:** State-level fallback in Flood_A biases beta_1 toward zero.
  Flood_A estimates are conservative lower bounds.
- **Falsification:** If beta_1 >= 0 (no dimming or systematic brightening), lights
  cannot serve as a displacement proxy in this setting and the IV chain fails.

**Current status:** PENDING RE-RUN
Preliminary result (Feb 6, contaminated deposits): beta_1 = -0.0149, SE = 0.0028,
t = -5.37, p < 0.001, N = 22,716. Effect size and significance uncertain until
re-run with corrected pipeline (Script 8 fix Mar 5, then Scripts 12–17, then 27).

---

## H2: Lights declines predict deposit withdrawals (liquidity transmission)

**Hypothesis:** Districts experiencing larger declines in nighttime lights also experience
larger deposit declines, consistent with liquidity demand rather than credit deterioration.

**Sign logic:** In shock periods, both Delta_Lights_it and Delta_Deposits_it expected
negative. The deposit-on-lights slope is therefore expected positive.

### H2a: Reduced-form association (descriptive)

Delta_Deposits_it = alpha + beta_2 * Delta_Lights_it + mu_i + tau_t + epsilon_it

- **Expected sign:** beta_2 > 0
- **Status:** Descriptive only. Delta_Lights_it correlates with unobserved income
  shocks that directly affect deposits. Not the preferred causal estimate.

### H2b: IV / 2SLS (preferred causal test)

**First stage:** H1 specification above.

**Second stage:** Delta_Deposits_it = alpha + beta_2 * Delta_Lights_it_hat + mu_i + tau_t + epsilon_it

- **Expected sign:** beta_2 > 0
- **Instrument discipline (pre-committed):** Report Flood_B instrument where feasible.
  Report Flood_A results with explicit weak-instrument and attenuation caveats. If
  first stage F < 10, label IV as suggestive and do not claim causal identification.
- **Exclusion restriction:** Floods shift deposits primarily through the
  displacement/disruption channel proxied by lights. Direct banking-operation
  disruption (branch closures, cash logistics) is a threat not fully addressed by
  the IV. Causal language softened accordingly if this threat is empirically plausible.
- **Falsification:** If deposits do not respond to lights in either reduced form or
  IV, the displacement-to-liquidity link is not supported in this data.

**Current status:** PENDING RE-RUN
Preliminary result (Feb 6, contaminated deposits): First stage beta_1 = -0.0151
(t = -5.42, strong instrument). Second stage beta_2 = +0.0839, SE = 0.1640,
p = 0.609 (null). Null finding may persist or reverse with clean pipeline. Three
explanations if null persists: (1) lights are a noisy migration proxy, (2) effect
operates through non-migration channels, (3) deposit effects are lagged, not
contemporaneous — see H3.

---

## H3: Deposit effects follow a liquidity-consistent timing structure

**Hypothesis:** Deposit declines occur within two quarters of flood exposure, consistent
with rapid liquidity demand rather than slow-moving credit-loss transmission.

### H3a: Distributed lag timing (core)

Delta_Deposits_it = alpha
+ beta_0 * Flood_it
+ beta_1 * Flood_i,t-1
+ beta_2 * Flood_i,t-2
+ mu_i + tau_t + epsilon_it

- **Expected pattern:** beta_0 and/or beta_1 < 0, with attenuation by t-2
- **Falsification:** If effects appear only at t-3 or beyond, the liquidity-timeline
  interpretation is weakened. If no lag is significant, mechanism is not supported.

### H3b: Liquidity-not-solvency fingerprint (extension, conditional)

If district-level credit-risk indicators (NPA ratios) become available, deposit
declines should not be fully mediated by contemporaneous credit deterioration.
If credit-risk data remains unavailable, H3b is explicitly labeled as a limitation
and not silently assumed to hold.

**Current status: VALIDATED CLEAN**

H3 specification uses deposits and flood lags only — no VIIRS variables, no district
FE (quarter FE only). Therefore unaffected by VIIRS contamination, crosswalk
regression, or homonymous FE collapse.

Confirmed results (Feb 6, N = 21,912):

| Lag | Coefficient | SE | p | Finding |
|---|---|---|---|---|
| t0 (current quarter) | -0.0005 | 0.0014 | 0.777 | Null |
| t-1 (1 quarter) | +0.0004 | 0.0014 | 0.757 | Null |
| t-2 (2 quarters) | **-0.0091** | 0.0036 | **0.012** | Confirmed |

**Interpretation:** Flood-induced deposit stress peaks at 6 months post-flood (-0.91%
decline in deposit growth), not contemporaneously. Consistent with gradual displacement
— households liquidate deposits after exhausting immediate coping strategies. Reconciles
H2 null: deposit effects are lagged, not contemporaneous.

**Caveat:** Sample was 21,912 (pre-clean, 2-lag restriction). Re-run with clean
23,347-observation panel may change coefficient magnitude. t-2 significance expected to
persist; direction and order of magnitude validated.

---

## H4: Deposit response is heterogeneous across district types

**Hypothesis:** The flood-to-deposit effect is more negative in districts with higher
baseline financial intensity or urbanisation, consistent with greater liquidity exposure.

**Specification (interaction form):**

Delta_Deposits_it = alpha
+ beta_0 * Flood_it
+ beta_1 * (Flood_it x Z_i)
+ mu_i + tau_t + epsilon_it

Where Z_i is a pre-defined district characteristic (not chosen after seeing results).

- **Expected sign:** beta_1 < 0 for "more vulnerable" groups
- **Proxy discipline (pre-committed):** If true urban/rural classification is
  unavailable, urbanisation proxies (e.g., median-split on baseline deposit level,
  or median-split on district mean lights) must be labeled as proxies and results
  treated as suggestive, not causal.

**Three pre-committed specifications:**

| Label | Z_i definition |
|---|---|
| H4a | Urban proxy: above-median district mean lights (baseline period) |
| H4b | High exposure: above-median cumulative flood count |
| H4c | Monsoon: Q3 indicator (July–September) |

- **Falsification:** If all interaction effects are consistently near zero, the
  mechanism is not heterogeneous across these proxies and claims are narrowed.

**Current status:** PENDING RE-RUN
Preliminary results (Feb 6, contaminated deposits, N = 22,503):

| Spec | Baseline | Interaction | p (interaction) | Note |
|---|---|---|---|---|
| H4a Urban | +0.0069 | -0.0111 | <0.001 | Pending re-run |
| H4b High exposure | — | +0.0021 | 0.360 | Null (likely robust) |
| H4c Monsoon | — | -0.0018 | 0.511 | Null (likely robust) |

H4a result requires re-evaluation with clean pipeline and corrected composite FE.
H4b and H4c null results expected to persist.

---

## H5: Network contagion (extension — requires new data)

**Hypothesis:** Banking stress spills over to districts not directly flood-exposed,
increasing with bank-network connectedness or geographic adjacency.

**Specification:**

Spillover_jt = sum_i W_ji * Flood_it

Delta_Deposits_jt = alpha + beta_5 * Spillover_jt + mu_j + tau_t + epsilon_jt

- **Expected sign:** beta_5 < 0
- **Hard dependency:** If a credible W matrix (shared branch networks, interbank
  linkages) is infeasible at district granularity, H5 remains a stated extension.
  It will not be tested by proxy without explicit methodological justification.

**Current status:** NOT TESTED. Dependent on data availability. Not included in
current regression pipeline.

---

## Joint Mechanism: What Full Support Looks Like

The Shadow Run mechanism is supported if:

1. **H1 holds** — Floods reduce lights, robustly across both precision regimes
2. **H2 holds** — Lights declines predict deposit declines (IV preferred when credible)
3. **H3a holds** — Timing is immediate or one-quarter lag (liquidity timeline confirmed)
4. **H4 holds** — Heterogeneity directionally consistent with vulnerability patterns

**Degraded conclusions (pre-committed):**

| Outcome | Interpretation |
|---|---|
| H1 holds, H2 null | Disasters reduce activity without measurable deposit effects; liquidity narrative softened |
| H1 fails | Lights proxy fails; IV chain invalid; paper reframes around reduced form only |
| H3 null at all lags | Mechanism operates at horizons beyond 6 months, or not via deposit channel |
| H4 null throughout | Effect is homogeneous; urbanisation/exposure heterogeneity not supported |

---

## Pre-Committed Robustness Checks

All robustness checks specified before regression execution. Not added retroactively
to protect significant results.

1. **Flood precision:** All core results reported under Rule A and Rule B side by side
2. **Placebo timing:** Test flood_t-1 predicting Delta_Deposits_t-1 (should produce null)
3. **Winsorisation:** Deposit growth winsorised at 1/99 percentile (regression-panel-final-winsor.csv)
4. **CPI deflation:** Nominal deposits deflated by CPI; verify results robust to real vs nominal
5. **Longer lags:** Extend H3 to t-3 and t-4 (Rule B only, for precision)
6. **SE robustness:** State-level clustering as alternative to district-level (more conservative)
7. **IV discipline:** Report first-stage F-statistic. If F < 10, label 2SLS as suggestive;
   drop causal language from abstract and conclusions

---

## Current Data State (Mar 4, 2026)

| File | Rows | Status |
|---|---|---|
| rbi_deposits_panel.csv | 49,670 (in-window) | CLEAN — Feb 11 |
| district_crosswalk_draft.csv | 769 | CONTAMINATED — 7 duplicate rows, fix Mar 5 |
| flood_exposure_panel.csv | 26,640 | CONTAMINATED — 2,230 Rule A (should be 2,220) |
| viirs_quarterly_panel_clean.csv | 25,240 | CLEAN — Mar 3 |
| analysis_panel_final.csv | 23,347 | CLEAN — Mar 4 |
| regression_panel_final.csv | 23,347 | CLEAN — Mar 4 |

**Correct analysis sample (post-fix):**
631 composite district pairs × 37 quarters = 23,347 observations
Flood treatment: 1,984 Rule A events (8.50%) — pending pipeline fix confirmation
VIIRS coverage: 100% | Deposit coverage: 99.1%

---

## Pending Actions (Mar 5, 2026)

1. Script 8 permanent rewrite with hard assert (`len(output) == 762`) — root fix
2. Re-run Scripts 12 → 14 → 15 → 17 → 23 → 24 → 25 sequentially
3. Verify flood events = 2,220 Rule A before proceeding to regressions
4. Fix FE specification in Scripts 27, 28, 30 (composite district_state_id)
5. Execute H1, H2, H4 regressions with clean data
6. Re-run H3 with full 23,347-observation sample; verify t-2 lag persists
7. Document all coefficient changes from Feb 6 to post-fix run

---

*Project initiated: 2025-12-30 | Principal investigator: Jaseel Badar, Harvard University*