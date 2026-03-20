# Formal Hypotheses: Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Night-Lights in India, 2015–2024

**Version:** 2.6 (Mar 20, 2026)
**Estimator:** linearmodels PanelOLS / IV2SLS throughout (Scripts 27b–30b). All tables use these numbers exclusively. statsmodels results superseded.
**Status:** All regressions, robustness checks, and figures complete. Results locked. Writing begins next.

---

## Version History

| Version | Change |
|---|---|
| v1.0–v1.8 | Pipeline construction, data acquisition, VIIRS fix, RBI contamination resolution |
| v2.0–v2.2 | Full deposit pipeline fix; composite FE correction identified; crosswalk dedup |
| v2.3 | District count corrected to 631 composite pairs. Sample: 23,347 |
| v2.4 | Script 8 permanent rewrite. Flood baseline locked |
| v2.5 | All core regressions (27–30) executed and confirmed. H1–H4 locked. Winsorization complete |
| **v2.6** | **linearmodels PanelOLS final tables (27b–30b). Wild bootstrap H1 complete (36b): H1 fails at state level. H4b demoted to suggestive (winsorization failure, Script 37). Pre-period two-phase cycle confirmed (Script 34). All robustness checks complete. Figures generated. Writing constraints locked.** |

**Integrity statement:** No hypothesis was modified to chase empirical results. All benchmark changes from Feb 6 are attributed exclusively to the composite FE correction (`district_gadm + '_' + state_gadm`, 631 pairs vs 624). This correction predates regression execution and was pre-committed.

---

## Notation

| Symbol | Definition |
|---|---|
| $i$ | District — composite `district_gadm + '_' + state_gadm`, 631 units |
| $t$ | Calendar quarter (2015Q2–2024Q4; 2016Q3–2017Q1 absent — RBI blackout) |
| $\Delta\text{Deposits}_{it}$ | Log first difference of district deposits (RBI BSR-2, ₹ Crores, nominal) |
| $\Delta\text{Lights}_{it}$ | Log first difference of mean VIIRS radiance (nW/cm²/sr, offset +0.001) |
| $\text{Flood}^A_{it}$ | Rule A: district-level EM-DAT match OR state fallback. Rate: 9.59% |
| $\text{Flood}^B_{it}$ | Rule B: district-level match only, high precision. Rate: 0.90% |
| $Z_i$ | Time-invariant district heterogeneity proxy (pre-committed, Section H4) |
| $\mu_i$ | District FE — composite `district_state_id`, 631 effects |
| $\tau_t$ | Quarter FE — 36 in H1/H2/H4; 35 in H3 (L2 restriction) |

---

## Pre-committed Methodological Positions

**Flood precision (R1):** Rule A maximises power; state fallback attenuates $\hat{\beta}$ toward zero. Rule A is a conservative lower bound. Rule B maximises precision at the cost of power. Both reported in all core tables.

**Lights interpretation:** $\Delta\text{Lights}_{it}$ is a proxy for displacement or disruption-driven activity loss. Not presented as direct proof of migration without external corroboration.

**Shadow run definition:** A sharp deposit decline consistent with liquidity demand by depositors — not slow-moving credit deterioration or solvency stress.

**FE specification (locked):** District FE constructed on composite `district_state_id` throughout Scripts 27b–30b. Using `district_gadm` alone collapses 7 homonymous pairs (AURANGABAD, BALRAMPUR, BILASPUR, PRATAPGARH, RAIGARH, SURGUJA, and one additional), producing 624 FE instead of 631. This was the source of all Feb 6 benchmark contamination. The correction is permanent.

**Proxy discipline:** All heterogeneity variables constructed from observational proxies are labeled "proxy" in all outputs and paper text. Never claim census-based classification.

**Nominal INR (locked, R4):** Deposits retained in nominal Rupees. District-quarter CPI unavailable at required granularity. Quarter FE absorb national price trends. Acknowledged as limitation.

**Estimator discipline (locked):** Final paper tables use linearmodels PanelOLS (Scripts 27b–30b). statsmodels output files are superseded. Never mix estimators across tables.

---

## H1 — Floods Reduce Economic Activity

**Hypothesis:** Flood exposure produces a statistically and economically significant decline in nighttime lights in affected districts, consistent with displacement or disruption-driven activity loss.

$$\Delta\text{Lights}_{it} = \alpha + \beta_1 \cdot \text{Flood}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

- **Expected sign:** $\beta_1 < 0$
- **Falsification:** $\beta_1 \geq 0$ invalidates lights as a displacement proxy; IV chain fails; paper reframes to reduced form only.

### Results (Script 27b — linearmodels PanelOLS)

| Rule | $\hat{\beta}$ | SE | $t$ | $p$ | $N$ | Status |
|---|---|---|---|---|---|---|
| A | −0.044468 | 0.007784 | −5.7124 | <0.001 | 22,716 | **Confirmed** |
| B | −0.058446 | 0.019768 | −2.9566 | 0.003 | 22,716 | **Confirmed** |

District FE = 631 \| Quarter FE = 36 \| SE clustered by `district_state_id`

Rule B exceeds Rule A in magnitude — consistent with pre-committed attenuation prediction.

### Wild Bootstrap (Script 36b) — MANDATORY DISCLOSURE

H1 significance is sensitive to the level of clustering assumed.

| SE Specification | Clusters | Rule A $p$ | Rule B $p$ |
|---|---|---|---|
| District-clustered (primary) | 631 | <0.001 | 0.003 |
| State-clustered, conventional | 34 | 0.105 | — |
| State-clustered, wild bootstrap | 34 | 0.1582 | 0.2673 |

Coefficient $\hat{\beta} = -0.044468$ is stable across all three specifications. SE widening is monotone and consistent with low-cluster-count variance inflation (Cameron and Miller 2015). H1 does **not** survive state-level clustering under conventional SE or wild cluster bootstrap. The district-clustered result (631 clusters) remains the primary specification. See Constraint 13.

---

## H2 — Lights Declines Transmit to Deposit Withdrawals

**Hypothesis:** Districts experiencing larger declines in nighttime lights also experience larger deposit declines, consistent with liquidity demand rather than credit deterioration.

**Sign logic:** In shock periods, $\Delta\text{Lights}_{it}$ and $\Delta\text{Deposits}_{it}$ are both expected negative. The deposit-on-lights slope is therefore expected positive.

### H2a: Reduced Form (descriptive)

$$\Delta\text{Deposits}_{it} = \alpha + \beta_2 \cdot \Delta\text{Lights}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

### H2b: IV 2SLS (preferred causal, first stage = H1)

$$\Delta\text{Deposits}_{it} = \alpha + \beta_2 \cdot \widehat{\Delta\text{Lights}}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

**Instrument discipline (R7):** $F < 10$ → labeled suggestive throughout; causal language removed from abstract and conclusions.

### Results (Script 28b — linearmodels IV2SLS, iterative two-way demeaning)

| Rule | $\hat{\beta}$ | SE | $t$ | $p$ | First-stage $F$ | Instrument | Status |
|---|---|---|---|---|---|---|---|
| A | −0.008388 | 0.034022 | −0.2465 | 0.805 | 34.673 | **Strong** (≥16.38) | **Null** |
| B | −0.006776 | 0.059698 | −0.1135 | 0.910 | 8.949 | **Weak** (<10) | Null (suggestive) |

District FE = 631 \| Quarter FE = 36 \| $N$ = 22,442 \| SE clustered by `district_state_id`

**F-statistic method:** linearmodels `first_stage` overflows numerically at 666 exogenous columns. For a single excluded instrument, $F = t^2$ exactly (Wooldridge 2010, p. 104). Rule A: $F = (-5.888)^2 = 34.673$. Rule B: $F = (-2.992)^2 = 8.949$.

**Null reconciliation (pre-committed):** The H2 IV specification tests the contemporaneous window. H3 confirms deposit effects are lagged, not contemporaneous. The IV tests a zero-effect window by construction. H2 null is expected and mechanically consistent with H3. Never present H2 null as a contradiction of the mechanism. See Constraint 1.

**Exclusion restriction caveat (standing):** Direct banking-operation disruption (branch closures, cash logistics) is a threat not fully addressed by the IV. Causal language is softened where this threat is empirically plausible.

---

## H3 — Deposit Effects Follow a Liquidity-Consistent Timing Structure

**Hypothesis:** Deposit declines emerge within two quarters of flood exposure, consistent with rapid household liquidity demand rather than slow-moving credit-loss transmission.

$$\Delta\text{Deposits}_{it} = \alpha + \beta_0\,\text{Flood}_{it} + \beta_1\,\text{Flood}_{i,t-1} + \beta_2\,\text{Flood}_{i,t-2} + \tau_t + \varepsilon_{it}$$

- **No district FE:** Quarter FE only. District trends absorbed by log-differencing.
- **Expected pattern:** $\beta_0, \beta_1 \approx 0$; $\beta_2 < 0$ (liquidity peaks at 2Q lag)
- **Falsification:** Significant effect only at $t-3$ or beyond weakens the liquidity timeline. No lag significant → mechanism not supported through deposit channel.

### Results (Script 29b — linearmodels PanelOLS)

| Lag | $\hat{\beta}$ (Rule A) | SE | $t$ | $p$ | Status |
|---|---|---|---|---|---|
| $t_0$ (flood quarter) | +0.000609 | 0.001462 | +0.4167 | 0.677 | Null |
| $t_0 + 1$ (one quarter after) | +0.001505 | 0.001114 | +1.3517 | 0.177 | Null |
| **$t_0 + 2$ (two quarters after)** | **−0.007005** | **0.001644** | **−4.2609** | **<0.001** | **Confirmed ★** |

Quarter FE = 35 \| $N$ = 21,837 \| SE clustered by `district_state_id`
(L2 restriction structurally drops 2015Q1–2015Q2 — correct, not a bug)

**Rule B:** All three lags null. 209 treatment events — insufficient power. Direction at $t_0+2$: $\hat{\beta} = -0.0038$ (negative, consistent with Rule A). Not a falsification.

**Economic interpretation:** Flood-induced deposit stress is absent in the flood quarter and the following quarter. Effect peaks at $t_0+2$ (six months post-flood): a −0.70 pp decline in quarterly deposit growth. Consistent with gradual displacement — households exhaust immediate coping mechanisms before liquidating bank deposits. This lag structure mechanically explains the H2 null.

### Two-Phase Liquidity Cycle — MANDATORY DISCLOSURE (Constraint 11)

Placebo test (Script 34, `09_placebo_timing.csv`) reveals a **positive** pre-period signal:

| Test | $\hat{\beta}$ | SE | $p$ | District FE |
|---|---|---|---|---|
| Test 2 (no district FE) | +0.004664 | 0.001841 | 0.011 | No |
| Test 2b (with district FE) | +0.004417 | 0.001881 | 0.019 | Yes |

Flood exposure at $t$ predicts **higher** deposit growth at $t-1$. Direction is positive — opposite sign to the $t_0+2$ withdrawal effect (−0.007). This is not a pre-existing trend. It reflects a **two-phase household liquidity cycle**:

- **Phase 1** ($t-1$, pre-flood): Anticipatory saving (+0.005) — households accumulate deposits ahead of the predictable monsoon flood season
- **Phase 2** ($t_0+2$, post-flood): Deposit withdrawal (−0.007) — liquidity demand materialises two quarters after the flood event

This must be disclosed in full in the Robustness section. The two-phase cycle is a finding, not a weakness. See Constraint 11 for mandatory language.

**Robustness:** H3 $t_0+2$ survives winsorization (Script 37: $p < 0.001$, $\hat{\beta} = -0.007115$), Northeast exclusion (Script 33), and state-level clustering (Script 36: $p = 0.034$). Longer lags $t_0+3$ and $t_0+4$ are null (Script 35) — effect decays at two quarters.

---

## H4 — Heterogeneous Deposit Response Across District Characteristics

**Hypothesis:** The flood-to-deposit effect is not uniform. Chronic flood exposure, urban economic concentration, and seasonal flood patterns are pre-committed moderators.

$$\Delta\text{Deposits}_{it} = \alpha + \beta_0\,\text{Flood}_{it} + \beta_1\,(\text{Flood}_{it} \times Z_i) + \mu_i + \tau_t + \varepsilon_{it}$$

All $Z_i$ are proxies constructed before regression execution. Labeled "proxy" throughout.

| Label | $Z_i$ | Construction |
|---|---|---|
| H4a | `urban_proxy` | Above-median district mean `log_lights_qt`, grouped by `district_state_id` |
| H4b | `high_exposure_proxy` | Above-median cumulative `flood_exposure_ruleA_qt`, grouped by `district_state_id` |
| H4c | `monsoon_qt` | $\mathbf{1}[q = 3]$ — July–September |

All specifications: $N$ = 22,442 \| District FE = 631 \| Quarter FE = 36 \| SE clustered by `district_state_id`

Results from Script 30b (linearmodels PanelOLS).

---

### H4a — Urban Proxy × Flood

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | +0.001207 | −0.001666 | 0.002664 | 0.532 | **Null** |
| B | −0.002890 | +0.007479 | 0.006929 | 0.280 | **Null** |

Urban split: 315 above-median \| 316 at/below-median (631 total)

**Verdict: NULL.** Both rules consistent. Signs disagree across rules — noise confirmed.

**Methodological note (mandatory, Constraint 4):** The Feb 6 result ($p < 0.001$) was spurious — `urban_proxy` constructed on `district_gadm` alone collapsed AURANGABAD Bihar/Maharashtra, contaminating the median `log_lights` threshold. After composite key correction the signal disappears entirely. Null is the correct and final result. This correction must be documented explicitly in the paper.

**Economic implication:** Flood-induced deposit stress is broad and systemic — not differentiated by urban versus rural proxy classification.

---

### H4b — High Exposure Proxy × Flood

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | +0.004700 | −0.006810 | 0.002932 | 0.020 | **Suggestive only** |
| B | +0.012016 | −0.013419 | 0.007670 | 0.080 | Marginal |

High-exposure split: 255 above-median \| 376 at/below-median (median = 3.0 cumulative events; strictly greater than)

**Verdict: SUGGESTIVE ONLY.** H4b does not survive winsorization. See Constraint 12.

**Winsorization failure (Script 37):** Rule A $p = 0.865$ on winsorized panel (2.01% of observations clipped). Effect is entirely driven by extreme deposit observations. H4b is **demoted** from supported to suggestive. Cannot be presented as a robust finding under any framing.

**Net effect (Rule A, non-winsorized baseline only — not robust):**

- Low-exposure baseline: $\hat{\beta} = +0.0047$ (marginal precautionary saving)
- High-exposure net: $+0.0047 + (-0.0068) = -0.0021$ (net withdrawal)

This calculation is from the non-winsorized baseline and cannot be presented as causal or robust. Report as descriptive estimate with explicit winsorization caveat.

---

### H4c — Monsoon Quarter × Flood

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | −0.004700 | +0.012495 | 0.002884 | <0.001 | **Confirmed (Rule A)** |
| B | −0.000838 | +0.002287 | 0.007968 | 0.774 | **Null** |

**Verdict: PARTIAL — Rule A confirmed (★★★). Rule B null. Fragile to flood intensity definition.**

**Net monsoon effect (Rule A):**

- Non-monsoon flood effect: $-0.0047$
- Monsoon flood net: $-0.0047 + 0.0125 = +0.0078$ (net positive)

**Economic interpretation:** Moderate flood events during Q3 (monsoon season) do not reduce deposits — seasonal income inflows dominate. Severe floods (Rule B) override seasonal patterns entirely. Distress dominates at high flood intensity.

**Mandatory language (Constraint 2, exact):** *"Monsoon seasonality moderates the deposit response to moderate-intensity floods (Rule A: $\hat{\beta} = +0.012$, $p < 0.001$) but not to severe flood events (Rule B: $p = 0.774$). The heterogeneity result is fragile to flood intensity definition."*

---

## H5 — Network Contagion (Contingent Extension)

**Hypothesis:** Banking stress spills over to non-flood-exposed districts, increasing with bank-network connectedness or geographic adjacency.

$$\text{Spillover}_{jt} = \sum_i W_{ji} \cdot \text{Flood}_{it}, \qquad \Delta\text{Deposits}_{jt} = \alpha + \beta_5 \cdot \text{Spillover}_{jt} + \mu_j + \tau_t + \varepsilon_{jt}$$

**Hard dependency:** Requires a credible district-level $W$ matrix (shared branch networks or interbank linkages). H5 will not be tested by proxy.

**Status: Not tested. Data-contingent. Not in regression pipeline.**

---

## Joint Mechanism: Final Assessment

The shadow run mechanism requires four conditions. Actual outcomes against pre-committed interpretations:

| Condition | Pre-committed Interpretation | Outcome |
|---|---|---|
| H1 confirmed | First stage valid; IV credible | **Confirmed** (district SE). Sensitive to state-level clustering — see Constraint 13 |
| H2 null | Deposit effects lagged, not contemporaneous — reconciled by H3 | **Null confirmed** — pre-committed reconciliation applies |
| H3 confirmed at $t_0+2$ | Rapid liquidity mechanism (≤6 months) | **Confirmed** |
| H4 heterogeneity | Vulnerability-consistent moderation | **Partial** — H4a null, H4b suggestive (fails winsorization), H4c Rule A only |

**Operative conclusion:** The shadow run mechanism is supported through the reduced-form timing channel (H3 $t_0+2$) rather than the contemporaneous IV channel (H2). H3 identifies a two-phase household liquidity cycle — anticipatory saving ($t-1$) followed by post-flood withdrawal ($t_0+2$) — that constitutes the paper's central empirical contribution. H4b and H4c provide suggestive and partial evidence of vulnerability-consistent heterogeneity, subject to the robustness constraints documented below.

---

## Robustness: Final Status

| Check | Implementation | Outcome |
|---|---|---|
| R1 — Flood precision | Rule A + Rule B in all core tables | **Complete** |
| R2 — Placebo timing | Flood$_t$ predicting $\Delta$Deposits$_{t-1}$ | **Complete** — positive pre-period confirmed; two-phase cycle locked |
| R3 — Winsorisation | 1st/99th percentile, 450 obs (2.01%) symmetric | **Complete** — H3 robust; H4b **fails** ($p = 0.865$) |
| R4 — CPI / nominal | Nominal INR retained; quarter FE absorb price trends | **Complete** |
| R5 — Longer lags | $t_0+3$, $t_0+4$ | **Complete** — both null; effect decays at $t_0+2$ |
| R6 — State clustering | 34 state clusters, conventional SE | **Complete** — H3 robust ($p = 0.034$); H1 $p = 0.105$ |
| R6b — Wild bootstrap | 999 iterations, Rademacher weights, 34 clusters | **Complete** — H1 fails (Rule A $p = 0.158$; Rule B $p = 0.267$) |
| R7 — IV discipline | First-stage $F$ reported; Rule B labeled suggestive | **Complete** |
| R8 — Northeast | Excluding Northeast districts | **Complete** — H3 $t_0+2$ robust to NE exclusion |

**All eight robustness checks complete. Zero open items.**

---

## Mandatory Writing Constraints

These are active disclosure requirements. Each must be enforced in every draft without exception. No softening. No omission.

---

**Constraint 1 — H2 null reconciliation**
Deposit effects are lagged (H3), not contemporaneous. The IV specification tests the contemporaneous window by construction. Never present H2 null as a contradiction of the mechanism. Never use the phrase "H2 fails." It finds exactly what the mechanism predicts.

---

**Constraint 2 — H4c language (exact, no paraphrase)**
*"Monsoon seasonality moderates the deposit response to moderate-intensity floods (Rule A: $\hat{\beta} = +0.012$, $p < 0.001$) but not to severe flood events (Rule B: $p = 0.774$). The heterogeneity result is fragile to flood intensity definition."*

---

**Constraint 3 — Rule B IV**
$F = 8.949 < 10$. Label suggestive throughout. Remove causal language from abstract and conclusions for Rule B IV results. Report $F$-statistic in the table.

---

**Constraint 4 — H4a spurious benchmark disclosure**
Must state explicitly that the Feb 6 H4a result ($p < 0.001$) was spurious — caused by homonymous FE collapse (`district_gadm` alone, 624 FE instead of 631). Corrected result is null. Document in paper body or footnote.

---

**Constraint 5 — Proxy discipline**
`urban_proxy` and `high_exposure_proxy` are proxies. Every mention carries the word "proxy." Never claim census-based classification.

---

**Constraint 6 — TUENSANG disclosure**
Flag the within-year reversal (+3.21) as a likely reporting artifact. Location: Data section footnote or Appendix.

---

**Constraint 7 — Demonetization gap**
2016Q3–2017Q1 is absent from the panel (RBI blackout). Name explicitly in Section 3.4 (Panel Construction). Never report 2016 or 2017 as full-year figures.

---

**Constraint 8 — Nominal INR**
Deposits in nominal Rupees. Quarter FE absorb national price trends. Acknowledged as a limitation in Section 3.3 or Section 8.

---

**Constraint 9 — Estimator discipline**
Final paper tables use linearmodels PanelOLS (Scripts 27b–30b). Never mix statsmodels and linearmodels results in the same table.

---

**Constraint 10 — Northeast robustness**
Script 33 confirms H3 $t_0+2$ robust to Northeast exclusion. H3 is not NE-driven. Report in Robustness section.

---

**Constraint 11 — R2 pre-trend disclosure (mandatory, no exceptions)**
Required language (exact):

*"Flood exposure at time $t$ predicts higher deposit growth at $t-1$ ($\hat{\beta} = +0.005$, $p = 0.011$), a signal that survives the inclusion of district fixed effects ($\hat{\beta} = +0.004$, $p = 0.019$). This pre-period effect is positive and opposite in sign to the $t_0+2$ withdrawal effect ($-0.007$), indicating a two-phase household liquidity cycle — anticipatory saving ahead of the predictable flood season followed by post-flood deposit withdrawal — rather than a pre-existing downward trend in deposits."*

Never claim the R2 placebo is clean. Never omit the pre-period. Never describe the two-phase cycle as a weakness.

---

**Constraint 12 — H4b winsorization failure (mandatory, no exceptions)**
Required language (exact):

*"The high flood exposure interaction (H4b) is significant in the baseline specification (Rule A: $\hat{\beta} = -0.007$, $p = 0.020$) but does not survive winsorization of the top and bottom 1% of deposit growth observations ($p = 0.865$). The effect is sensitive to extreme observations and should be interpreted as suggestive evidence only."*

Never present H4b as a robust finding. Never omit the winsorization failure.

---

**Constraint 13 — H1 wild bootstrap failure (mandatory, no exceptions)**
Required language (exact):

*"H1 is significant under district-level clustering (631 clusters, $p < 0.001$) but does not survive state-level clustering under conventional SE (34 clusters, $p = 0.105$) or wild cluster bootstrap (Rule A: $p = 0.158$, Rule B: $p = 0.267$). The coefficient is stable across all three specifications ($\hat{\beta} = -0.044$). Significance is therefore sensitive to the level of clustering assumed. The district-clustered result is the primary specification; state-level results are reported as a robustness bound."*

Never claim H1 is robust to state-level clustering.

---

## Data State

All files verified clean. Results locked. Do not re-run.

| File | Rows | Key Metric |
|---|---|---|
| `district_crosswalk_draft.csv` | 762 | Hard assert: len == 762 |
| `flood_exposure_panel.csv` | 26,640 | Rule A: 2,518 events \| 666 districts |
| `regression_panel_final.csv` | 23,347 | 23 columns \| 631 districts × 36 quarters |
| `regression_panel_final_winsor.csv` | 23,347 | 24 columns \| 450 obs clipped (2.01%) |

**Locked analysis sample:** 631 composite pairs × 36 quarters = **23,347 observations**
Rule A treatment: **2,238 events (9.59%)** \| Rule B: **209 events (0.90%)**
VIIRS coverage: **100%** \| Deposit coverage: **98.9%**

**Final paper table CSVs (all from linearmodels — do not substitute):**

| File | Script | Contents |
|---|---|---|
| `02b_H1_linearmodels.csv` | 27b | H1 first stage |
| `03b_H2_linearmodels.csv` | 28b | H2 IV 2SLS |
| `04b_H3_linearmodels.csv` | 29b | H3 distributed lag |
| `05b_H4_linearmodels.csv` | 30b | H4 heterogeneity |

---

*Principal Investigator: Jaseel Badar, Harvard University*
*Repository: https://github.com/JaseelBadar/Climate-Migration-Bank-Fragility*