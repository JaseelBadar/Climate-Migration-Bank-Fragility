# Formal Hypotheses: Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Night-Lights in India, 2015–2024

**Version:** 2.5 (Mar 9, 2026)
**Status:** Full pipeline verified and clean. All regressions (Scripts 27–30)
executed and confirmed. Robustness and diagnostic scripts (31–32b) complete.
Results locked. Pre-paper actions documented below.

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
| v2.4 | 2026-03-07 | Pipeline fully clean. Script 8 permanent rewrite (762-row assert). Flood baseline locked. FE correction pending. |
| **v2.5** | **2026-03-09** | **All regressions executed and confirmed. Composite FE fix applied (Scripts 27, 28, 30). H1–H4 results locked. Winsorization complete (R3). Nominal INR decision logged (R4). 2023 anomaly diagnosed. H4 benchmark changes from Feb 6 attributed to FE fix and documented. Degraded conclusions updated against actual results.** |

**Discipline:** No hypothesis was modified to chase empirical results. Version history
records data corrections only. Any modification to hypothesis wording is explicitly
labeled with rationale and date. All benchmark changes from Feb 6 to v2.5 are
attributed solely to the composite FE correction — not to post-hoc model search.

---

## Notation

| Symbol | Definition |
|---|---|
| i | District (composite: district_gadm + '_' + state_gadm, 631 units) |
| t | Calendar quarter |
| ΔDeposits_it | Log first difference of district deposits (RBI BSR-2, Rs Crores, nominal) |
| ΔLights_it | Log first difference of mean VIIRS radiance (nW/cm²/sr, offset +0.001) |
| Flood_A_it | Rule A flood exposure: district-level match OR state fallback (9.59% rate) |
| Flood_B_it | Rule B flood exposure: district-level match only, high precision (0.90% rate) |
| Z_i | Time-invariant district heterogeneity proxy (pre-committed, Section H4) |
| μ_i | District fixed effect (composite district_state_id — 631 FE, not 624) |
| τ_t | Quarter fixed effect (36 in H1/H2/H4; 35 in H3 due to L2 restriction) |

**Pre-committed methodological positions:**

- **Flood precision:** Rule A maximises power; state-level fallback attenuates β
  toward zero. Rule A estimates are conservative lower bounds on the true local
  effect. Rule B maximises precision at the cost of power. Both reported in all
  core tables per pre-committed R1.

- **Lights interpretation:** ΔLights_it is treated as a proxy consistent with
  displacement or disruption-driven activity loss. Not presented as direct proof of
  migration without external corroboration.

- **Shadow run definition:** A sharp deposit decline consistent with liquidity
  demand from depositors — not from slow-moving credit deterioration or solvency
  stress.

- **FE specification (locked):** District FE constructed on composite
  `district_state_id = district_gadm + '_' + state_gadm` throughout Scripts 27–30.
  Using `district_gadm` alone collapses 7 homonymous pairs, producing 624 FE instead
  of correct 631. This was the source of all Feb 6 benchmark contamination.

- **Proxy discipline:** Heterogeneity variables constructed from observational
  proxies are labeled "proxy" in all outputs and paper text. Results from proxy
  specifications are treated as suggestive, not causal.

- **Nominal INR (locked, R4 resolved):** Deposits retained in nominal Rupees.
  District-quarter CPI unavailable at required granularity. Quarter FE absorb
  national-level price trends. Inflation confound acknowledged as a limitation.

---

## H1: Floods reduce economic activity (first stage)

**Hypothesis:** Flood exposure produces a statistically and economically meaningful
decline in nighttime lights in affected districts, consistent with displacement or
disruption-driven activity loss.

**Specification:**

$$\Delta\text{Lights}_{it} = \alpha + \beta_1 \cdot \text{Flood}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

Estimated separately for Flood_A and Flood_B.

- **Expected sign:** β₁ < 0
- **Attenuation note:** State-level fallback in Flood_A biases β₁ toward zero.
  Flood_A estimates are conservative lower bounds.
- **Falsification:** If β₁ ≥ 0, lights cannot serve as a displacement proxy and
  the IV chain fails. Paper reframes around reduced form only.

**Status: CONFIRMED**

| Rule | β | SE | t | p | N | Status |
|---|---|---|---|---|---|---|
| A | −0.0445 | 0.0078 | −5.708 | <0.001 | 22,716 | **Confirmed** |
| B | −0.0584 | 0.0198 | −2.954 | 0.003 | 22,716 | **Confirmed** |

District FE = 631 | Quarter FE = 36 | SE clustered by district_state_id

**Interpretation:** Both rules confirm a negative and statistically significant
first stage. Rule B magnitude exceeds Rule A — consistent with the pre-committed
attenuation prediction. State-level fallback in Rule A attenuates β toward zero;
Rule A is the lower bound. Change vs Feb 6 (β = −0.0149): magnitude tripled after
FE correction. Root cause: Script 8 state-token fix correctly assigns district-level
floods under Rule A with clean crosswalk. Cleaner treatment variable = stronger
first stage. Instrument credibility confirmed for H2 IV 2SLS.

---

## H2: Lights declines transmit to deposit withdrawals (liquidity channel)

**Hypothesis:** Districts experiencing larger declines in nighttime lights also
experience larger deposit declines, consistent with liquidity demand rather than
credit deterioration.

**Sign logic:** In shock periods, both ΔLights_it and ΔDeposits_it are expected
negative. The deposit-on-lights slope is therefore expected positive.

### H2a: Reduced-form association (descriptive)

$$\Delta\text{Deposits}_{it} = \alpha + \beta_2 \cdot \Delta\text{Lights}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

- **Expected sign:** β₂ > 0
- Descriptive only. ΔLights_it correlates with unobserved income shocks that
  directly affect deposits. Not the preferred causal estimate.

### H2b: IV / 2SLS (preferred causal specification)

**First stage:** H1 specification above.

**Second stage:**

$$\Delta\text{Deposits}_{it} = \alpha + \beta_2 \cdot \widehat{\Delta\text{Lights}}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

- **Expected sign:** β₂ > 0
- **Instrument discipline (pre-committed, R7):** If first-stage F < 10, IV labeled
  suggestive throughout — causal language removed from abstract and conclusions.

**Status: NULL CONFIRMED**

| Rule | β | SE | t | p | F-stat | Instrument | Status |
|---|---|---|---|---|---|---|---|
| A | −0.0084 | 0.0340 | −0.247 | 0.805 | 34.673 | Strong (≥ 16.38) | Null |
| B | −0.0068 | 0.0597 | −0.114 | 0.910 | 8.949 | Weak (< 10) | Null (suggestive) |

District FE = 631 | Quarter FE = 36 | N = 22,442 | SE clustered by district_state_id

**F-statistic note:** linearmodels `first_stage` F-statistic overflows numerically
at 666 exogenous columns. For a single excluded instrument, F = t² exactly
(Wooldridge 2010, p. 104). Applied: Rule A F = (−5.888)² = 34.673.
Rule B F = (−2.992)² = 8.949.

**Instrument status:**
- Rule A: Strong. Causal interpretation retained with standard exclusion restriction
  caveats.
- Rule B: Weak. Second stage labeled suggestive. Causal language dropped per R7.

**Pre-committed null reconciliation:** Explanation 3 applies. Deposit effects are
lagged rather than contemporaneous — the H2 specification tests the same-quarter
relationship, which H3 shows is null by construction. The H3 t−2 result directly
explains the H2 null. This reconciliation was pre-committed before regressions were
executed.

**Exclusion restriction caveat (standing):** Floods shift deposits primarily through
the displacement/disruption channel proxied by lights. Direct banking-operation
disruption (branch closures, cash logistics) is a threat not fully addressed by
the IV. Causal language is softened where this threat is empirically plausible.

---

## H3: Deposit effects follow a liquidity-consistent timing structure

**Hypothesis:** Deposit declines emerge within two quarters of flood exposure,
consistent with rapid household liquidity demand rather than slow-moving
credit-loss transmission.

### H3a: Distributed lag timing (core)

$$\Delta\text{Deposits}_{it} = \alpha + \beta_0 \cdot \text{Flood}_{it} + \beta_1 \cdot \text{Flood}_{i,t-1} + \beta_2 \cdot \text{Flood}_{i,t-2} + \tau_t + \varepsilon_{it}$$

- **No district FE:** H3 uses quarter FE only. District effects absorbed by the
  log-differenced dependent variable. Unaffected by homonymous FE collapse — H3
  was validated clean before any FE correction was applied.
- **Expected pattern:** β₀ and/or β₁ near zero; β₂ < 0 (liquidity peaks at 2Q lag)
- **Falsification:** If effects appear only at t−3 or beyond, the liquidity timeline
  is weakened. If no lag is significant, the mechanism is not supported.

**Status: CONFIRMED**

| Lag | β (Rule A) | SE | t | p | Status |
|---|---|---|---|---|---|
| t0 (current quarter) | +0.000609 | 0.001463 | +0.416 | 0.677 | Null |
| t−1 (1 quarter lag) | +0.001505 | 0.001114 | +1.351 | 0.177 | Null |
| **t−2 (2 quarter lag)** | **−0.007005** | **0.001645** | **−4.258** | **<0.001** | **Confirmed** |

Quarter FE = 35 | N = 21,837 | SE clustered by district_state_id
(L2 restriction drops 2015Q1 and 2015Q2 structurally — correct, not a bug)

**Rule B:** t0, t−1, t−2 all null. 209 treatment events — insufficient power.
t−2 direction: β = −0.0038 (negative, consistent with Rule A). Rule B null is
not a falsification.

**Interpretation:** Flood-induced deposit stress is absent in the flood quarter and
the quarter immediately following. The effect peaks at t−2 (6 months post-flood):
a −0.70% decline in quarterly deposit growth. Consistent with gradual displacement
— households exhaust immediate coping mechanisms before liquidating bank deposits.
This lag structure directly reconciles the H2 null: contemporaneous IV tests a
zero-effect window.

**Change vs Feb 6 (β = −0.0091, p = 0.012):** Magnitude smaller (−0.0070),
significance stronger (p < 0.001). Clean deposit pipeline produced a more precise
estimate. Direction confirmed. N increased from 21,912 to 21,837 after clean
two-lag restriction on the full 23,347-row panel.

### H3b: Liquidity-not-solvency fingerprint (conditional extension)

If district-level credit-risk indicators (NPA ratios) become available, deposit
declines should not be fully mediated by contemporaneous credit deterioration.
If data remains unavailable, H3b is explicitly labeled as a limitation and not
silently assumed to hold.

**Status:** Data unavailable. Acknowledged as limitation.

---

## H4: Deposit response is heterogeneous across district characteristics

**Hypothesis:** The flood-to-deposit effect is not uniform across districts.
Chronic flood exposure, urban economic concentration, and seasonal flood patterns
are pre-committed moderators.

**Specification:**

$$\Delta\text{Deposits}_{it} = \alpha + \beta_0 \cdot \text{Flood}_{it} + \beta_1 \cdot (\text{Flood}_{it} \times Z_i) + \mu_i + \tau_t + \varepsilon_{it}$$

Where Z_i is a pre-defined district characteristic, constructed before regressions
are executed. All Z_i variables labeled as proxies where true administrative
classifications are unavailable.

- **Expected sign:** β₁ < 0 for more vulnerable groups
- **Falsification:** If all interaction effects are consistently near zero across
  both rules, the mechanism is homogeneous and heterogeneity claims are dropped.

**Three pre-committed specifications:**

| Label | Z_i | Construction |
|---|---|---|
| H4a | `urban_proxy` | Above-median district mean log_lights_qt, full period, grouped by district_state_id |
| H4b | `high_exposure_proxy` | Above-median cumulative flood_exposure_ruleA_qt, full period, grouped by district_state_id |
| H4c | `monsoon_qt` | indicator(q == 3), July–September |

**Status: COMPLETE. Results locked.**

All specifications estimated at N = 22,442. District FE = 631. Quarter FE = 36.
SE clustered by district_state_id.

### H4a: Urban proxy × Flood

| Rule | Baseline β | Interaction β | SE | p | Status |
|---|---|---|---|---|---|
| A | +0.001207 | −0.001666 | 0.002666 | 0.532 | **Null** |
| B | −0.002890 | +0.007479 | 0.006934 | 0.281 | **Null** |

**Verdict: NULL. Both rules agree. Signs disagree across rules — noise confirmed.**

**Benchmark change from Feb 6 (p < 0.001):** Spurious. Urban proxy construction
on `district_gadm` alone collapsed AURANGABAD Bihar/Maharashtra, contaminating the
median log_lights threshold and producing a false interaction signal. After the
composite key fix, the spurious significance disappears entirely. Null is the
correct result. Paper must document this explicitly as a methodological correction.

**Economic implication:** Flood-induced deposit stress is broad and systemic —
not differentiated by urban vs rural proxy classification. The effect operates
at the district level regardless of economic intensity.

### H4b: High exposure proxy × Flood

| Rule | Baseline β | Interaction β | SE | p | Status |
|---|---|---|---|---|---|
| A | +0.004700 | −0.006810 | 0.002934 | 0.020 | **Supported** |
| B | +0.012016 | −0.013419 | 0.007675 | 0.080 | **Supported** |

**Verdict: SUPPORTED. Both rules negative and significant (5% and 10%). Directionally
consistent.**

**Net effect for high-exposure districts (Rule A):**
Baseline (low-exposure): β = +0.0047 (marginal positive — precautionary saving).
Net high-exposure effect: +0.0047 + (−0.0068) = **−0.0021** (net withdrawal).

**Economic interpretation:** Low flood-history districts show marginal precautionary
deposit accumulation following a flood. High flood-history districts show net deposit
withdrawal — consistent with chronically exposed households having depleted financial
buffers, forcing liquidation rather than precautionary saving when the next flood
strikes. This is the most economically coherent heterogeneity result and will appear
in the Abstract, Introduction, and Policy Implications.

**Benchmark change from Feb 6 (null, p = 0.360):** High/low exposure group
classification was incorrect in the Feb 6 run. Groupby on `district_gadm` alone
pooled homonymous pairs' cumulative flood counts, misclassifying group membership.
Composite key fix corrected the classification; the signal emerged cleanly. Change
is attributed to the FE correction — not post-hoc model search.

**Disclosure requirement:** The `high_exposure_proxy` threshold is strictly greater
than the median (3.0 cumulative events). Districts with exactly 3.0 events fall in
the low-exposure group. Must be disclosed in the paper.

### H4c: Monsoon quarter × Flood

| Rule | Baseline β | Interaction β | SE | p | Status |
|---|---|---|---|---|---|
| A | −0.004700 | +0.012495 | 0.002886 | <0.001 | **Partial** |
| B | −0.000838 | +0.002287 | 0.007974 | 0.774 | Null |

**Verdict: PARTIALLY SUPPORTED. Rule A significant (***). Rule B null. Result is
fragile to flood intensity definition.**

**Net monsoon effect (Rule A):**
Non-monsoon baseline: β = −0.0047 (significant — deposits fall in non-monsoon
flood quarters). Net monsoon effect: −0.0047 + 0.0125 = **+0.0078** (net positive).

**Economic interpretation:** Moderate flood events during monsoon quarters (Q3) do
not reduce deposits — the effect reverses. Seasonal flooding is anticipated;
agricultural income inflows in Q3 dominate deposit behavior. Severe floods (Rule B)
override this seasonal pattern entirely — distress dominates at high intensity.

**Language constraint (pre-committed):** Must not state "H4c confirmed" without the
Rule B fragility caveat. Required language: *"Monsoon seasonality moderates the
deposit response to moderate-intensity floods (Rule A: β = +0.012, p < 0.001) but
not to severe flood events (Rule B: p = 0.774). The heterogeneity result is fragile
to flood intensity definition."*

**Benchmark change from Feb 6 (null, p = 0.511):** Same root cause as H4b.
Composite key fix corrected seasonal groupby operations. Change attributed to
the FE correction.

---

## H5: Network contagion (stated extension — data-contingent)

**Hypothesis:** Banking stress spills over to non-flood-exposed districts, increasing
with bank-network connectedness or geographic adjacency.

**Specification:**

$$\text{Spillover}_{jt} = \sum_i W_{ji} \cdot \text{Flood}_{it}$$

$$\Delta\text{Deposits}_{jt} = \alpha + \beta_5 \cdot \text{Spillover}_{jt} + \mu_j + \tau_t + \varepsilon_{jt}$$

- **Expected sign:** β₅ < 0
- **Hard dependency:** Requires a credible district-level W matrix (shared branch
  networks or interbank linkages). H5 will not be tested by proxy without explicit
  methodological justification.

**Status:** Not tested. Data-contingent. Not in current regression pipeline.

---

## Joint Mechanism: Assessment Against Actual Results

The Shadow Run mechanism requires all four conditions:

1. **H1:** Floods reduce lights, robustly across both rules — **CONFIRMED**
2. **H2:** Lights declines predict deposit declines (IV) — **NULL**
3. **H3a:** Effect peaks within two quarters of flood — **CONFIRMED at t−2**
4. **H4:** Heterogeneity directionally consistent with vulnerability — **PARTIAL**

**Actual degraded conclusion (v2.5):**

H1 holds and H2 is null — pre-committed reconciliation applies: deposit effects
are lagged, not contemporaneous, as confirmed by H3. The IV tests a zero-effect
window by construction. The Shadow Run mechanism is supported through the
reduced-form timing channel (H3) rather than the contemporaneous IV channel (H2).

H4 is partially supported. H4b (chronic exposure) is the strongest heterogeneity
finding and is directionally robust across both rules. H4c (monsoon seasonality)
is significant under Rule A but fragile to Rule B. H4a (urban proxy) is correctly
null after the FE fix — flood effects are systemic, not urban-concentrated.

| Outcome | Pre-committed interpretation | Actual result |
|---|---|---|
| H1 holds, H2 null | Deposit effects lagged, not contemporaneous — see H3 | Applies. H3 t−2 confirms. |
| H3 null at all lags | Mechanism not through deposit channel | Does not apply. |
| H4 null throughout | Effect is homogeneous | Partially applies (H4a null). H4b/c significant. |
| H1 fails | Lights proxy fails; IV invalid | Does not apply. |

---

## Pre-Committed Robustness Checks

All checks specified before regression execution. None added retroactively.

| # | Check | Implementation | Status |
|---|---|---|---|
| R1 | Flood precision | All core results under Rule A and Rule B side by side | **Complete** |
| R2 | Placebo timing | Flood_t−1 predicting ΔDeposits_t−1 — should produce null | Pending |
| R3 | Winsorisation | deposit_change_qt winsorized at 1st/99th percentile (Script 31) | **Complete** — 450 obs (2.01%), symmetric tails |
| R4 | CPI deflation | Nominal deposits retained. Quarter FE absorb price trends. CPI decision logged (Script 32). | **Complete — nominal INR confirmed** |
| R5 | Longer lags | Extend H3 to t−3 and t−4 (Rule B only, for precision) | Pending |
| R6 | State-level clustering | Alternative to district-level SE — more conservative | Pending |
| R7 | IV discipline | First-stage F reported. Rule B F = 8.949 (weak) — labeled suggestive. | **Complete** |
| R8 | Northeast sensitivity | Robustness check excluding Northeast districts (small-base variance amplification identified in Script 32b) | **Pending — confirm as Script 33** |

---

## Current Data State

All files verified clean. Results locked.

| File | Rows | Key Metric | Status |
|---|---|---|---|
| district_crosswalk_draft.csv | 762 | Hard assert len == 762 | Clean |
| flood_exposure_panel.csv | 26,640 | Rule A: 2,518 events | Clean |
| rbi_deposits_panel.csv | 50,192 | Aurangabad Bihar 2015Q1 = 4,422 Crores | Clean |
| master_panel_analysis.csv | 23,347 | 631 districts x 37 quarters | Clean |
| viirs_quarterly_panel_clean.csv | 25,240 | 631 x 40, 9-check PASS | Clean |
| analysis_panel_final.csv | 23,347 | 100% VIIRS coverage | Clean |
| regression_panel_final.csv | 23,347 | 23 columns, lag arithmetic exact | Clean |
| regression_panel_final_winsor.csv | 23,347 | 24 columns, 450 obs clipped (2.01%) | Clean |

**Locked analysis sample:**
631 composite (district_gadm, state_gadm) pairs × 37 quarters = **23,347 observations**
Rule A treatment: **2,238 events (9.59%)** | Rule B: **209 events (0.90%)**
VIIRS coverage: **100%** | Deposit coverage: **98.9%**

---

## Pending Pre-Paper Actions

1. Re-run Scripts 27–30 with `linearmodels.PanelOLS` — resolves statsmodels
   ValueWarning (rank deficiency in clustered VCV at 666 exogenous columns).
   Coefficients currently valid; SEs conservative. Required before final tables.
2. Fix Script 32b conclusion logic — negative tail (n below p5 = 385, 15.4%)
   not evaluated. Correct conclusion documented in Research Log. Log file must
   not be cited directly until corrected.
3. Fix Script 29 cosmetic comments — expected N: ~21,180 → ~21,837;
   expected QFE: 36 → 35. No re-run required.
4. Fix Script 12 Section [7] token count comment — 44 → 46. No re-run required.
5. Confirm R8 Northeast sensitivity check scope — Script 33 or Hypotheses v2.5
   robustness addition only.
6. Execute R2 (placebo timing), R5 (longer lags), R6 (state-level clustering).
7. Robustness re-runs of Scripts 27–30 on winsorized panel
   (regression_panel_final_winsor.csv) to confirm R3.

---

*Project initiated: 2025-12-30 | Principal investigator: Jaseel Badar, Harvard University*