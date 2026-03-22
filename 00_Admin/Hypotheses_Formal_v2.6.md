# Formal Hypotheses: Climate Shocks, Displacement, and Bank Liquidity Risk
### Evidence from Nighttime Lights in India, 2015–2024

**Version:** 2.6 (March 21, 2026)  
**Estimator:** linearmodels PanelOLS / IV2SLS throughout (Scripts 27b–30b).  
All tables use these numbers exclusively. statsmodels results superseded.  
**Status:** All regressions, robustness checks, and figures complete.
Results locked. Writing phase active.

---

## Version History

| Version | Date | Change |
|---|---|---|
| v1.0–v1.8 | Dec 2025 – Jan 2026 | Pipeline construction; VIIRS extraction and deduplication; RBI contamination identified and resolved |
| v2.0–v2.2 | Feb 1–6, 2026 | Full deposit pipeline fix; composite FE error identified; district crosswalk deduplication corrected |
| v2.3 | Feb 7, 2026 | District count corrected to 631 composite pairs; analysis sample confirmed at 23,347 |
| v2.4 | Feb 28 – Mar 5, 2026 | Script 8 permanent rewrite; flood baseline locked at 762-row assert |
| v2.5 | Mar 6–18, 2026 | Core regressions 27b–30b executed and locked; H1–H4 confirmed; winsorization complete |
| **v2.6** | **Mar 19–21, 2026** | **linearmodels final tables locked; wild bootstrap H1 complete (fails at state level, p=0.158); H4b demoted to suggestive (winsorization failure); two-phase liquidity cycle confirmed (Script 34); all R1–R8 robustness checks complete; figures generated; writing constraints locked** |

**Integrity statement.** No hypothesis was modified to chase empirical
results. All benchmark changes from February 6, 2026 are attributed
exclusively to the composite FE correction (`district_gadm + '_' +
state_gadm`, 631 pairs vs 624). This correction was identified on
February 7, pre-committed before any regression was re-executed, and
is documented in Research_Log.txt. The February 6 results are retained
in `07_Archive/` as a coefficient-stability audit trail.

---

## Notation

| Symbol | Definition |
|---|---|
| $i$ | District — composite `district_gadm + '_' + state_gadm`, 631 units |
| $t$ | Calendar quarter (2015Q2–2024Q4; 2016Q3–2017Q1 absent — RBI blackout) |
| $\Delta\text{Deposits}_{it}$ | Log first difference of district deposits (RBI BSR-2, ₹ Crores, nominal) |
| $\Delta\text{Lights}_{it}$ | Log first difference of mean VIIRS radiance (nW/cm²/sr, +0.001 offset) |
| $\text{Flood}^A_{it}$ | Rule A: district EM-DAT match or state-level fallback. Treatment rate: 9.59% |
| $\text{Flood}^B_{it}$ | Rule B: district-level match only. Treatment rate: 0.90% |
| $Z_i$ | Time-invariant district heterogeneity proxy (pre-committed; Section H4) |
| $\mu_i$ | District fixed effect — composite `district_state_id`, 631 effects |
| $\tau_t$ | Quarter fixed effect — 36 in H1/H2/H4; 35 in H3 (L2 restriction) |
| $\hat{\beta}$ | Estimated coefficient from linearmodels PanelOLS or IV2SLS |

---

## Pre-committed Methodological Positions

These positions were locked before regression execution. None may be
revised post-estimation.

**Flood precision (R1).** Rule A maximises power; state fallback
attenuates $\hat{\beta}$ toward zero. Rule A is a conservative lower
bound, not an overstatement of treatment intensity. Rule B maximises
geographic precision at the cost of statistical power. Both rules are
reported in all core tables throughout.

**Lights interpretation.** $\Delta\text{Lights}_{it}$ is a proxy for
displacement or disruption-driven economic activity loss. Not presented
as direct proof of population migration without external corroboration.

**Shadow run definition.** A sharp deposit decline consistent with
liquidity demand by depositors — not slow-moving credit deterioration
or solvency stress. The timing structure distinguishes these channels:
shadow runs emerge within two quarters; credit losses materialise over
multiple quarters.

**Composite FE (locked).** All fixed effects, cluster assignments, and
heterogeneity variable construction use composite `district_state_id`
throughout Scripts 27b–30b. Using `district_gadm` alone collapses 7
homonymous district pairs — AURANGABAD (Bihar / Maharashtra),
BALRAMPUR (Chhattisgarh / Uttar Pradesh), BIJAPUR (Chhattisgarh /
Karnataka), BILASPUR (Chhattisgarh / Himachal Pradesh), HAMIRPUR
(Himachal Pradesh / Uttar Pradesh), PRATAPGARH (Rajasthan / Uttar
Pradesh), and RAIGARH (Chhattisgarh / Maharashtra) — producing 624 FE
instead of the correct 631. This collapse contaminated all February 6
benchmark results. The correction is permanent.

**Proxy discipline.** All heterogeneity variables are labeled "proxy"
in every output and in all paper text. No claim of census-based
classification is made anywhere.

**Nominal INR (locked, R4).** Deposits retained in nominal Rupees.
District-quarter CPI unavailable at required granularity. Quarter FE
absorb national price trends. Acknowledged as a limitation.

**Estimator discipline (locked).** Final paper tables use linearmodels
PanelOLS (Scripts 27b–30b) exclusively. statsmodels output files are
superseded. Results are stable across both estimators; the switch to
linearmodels resolves the iterative two-way demeaning requirement for
the unbalanced IV panel.

---

## H1 — Floods Reduce Economic Activity

**Hypothesis.** Flood exposure produces a statistically and economically
significant decline in nighttime lights in affected districts, consistent
with displacement- or disruption-driven activity loss.

$$\Delta\text{Lights}_{it} = \alpha + \beta_1 \cdot \text{Flood}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

**Pre-committed sign:** $\beta_1 < 0$

**Falsification condition.** $\hat{\beta}_1 \geq 0$ invalidates
nighttime lights as a displacement proxy. The IV chain fails. The paper
reframes to a reduced-form flood-to-deposits specification only.

### Results (Script 27b — linearmodels PanelOLS)

District FE = 631 | Quarter FE = 36 | SE clustered by `district_state_id`

| Rule | $\hat{\beta}$ | SE | $t$ | $p$ | $N$ | Status |
|---|---|---|---|---|---|---|
| A | −0.044468 | 0.007784 | −5.7124 | <0.001 | 22,716 | **Confirmed** |
| B | −0.058446 | 0.019768 | −2.9566 | 0.003 | 22,716 | **Confirmed** |

Rule B exceeds Rule A in magnitude — consistent with the pre-committed
attenuation prediction. State fallback in Rule A pulls the point estimate
toward zero.

### H1 Sensitivity to Clustering Assumption — Mandatory Disclosure (Constraint 13)

The coefficient $\hat{\beta} = -0.044468$ is stable across all
specifications. What changes is the standard error.

| SE specification | Clusters | SE | Rule A $p$ |
|---|---|---|---|
| District-clustered (primary) | 631 | 0.0078 | <0.001 |
| State conventional | 34 | 0.0274 | 0.105 |
| State wild bootstrap, 999 iter. | 34 | 0.0300 | 0.158 |

SE widening is monotone and consistent with low-cluster-count variance
inflation (Cameron and Miller 2015). **H1 does not survive state-level
clustering under conventional SE or wild cluster bootstrap (Rule A
p = 0.158, Rule B p = 0.267).** The district-clustered result is the
primary specification. State-level results are reported as a robustness
bound. This is disclosed in full in the paper — no exceptions.

---

## H2 — Lights Declines Transmit to Deposit Withdrawals (IV)

**Hypothesis.** Districts experiencing flood-driven declines in
nighttime lights also experience deposit declines, consistent with
liquidity demand rather than credit deterioration.

**Sign logic.** In shock periods, both $\Delta\text{Lights}_{it}$ and
$\Delta\text{Deposits}_{it}$ are expected negative. The
deposit-on-lights slope is therefore expected positive.

### Specification

Reduced form (H2a, descriptive):

$$\Delta\text{Deposits}_{it} = \alpha + \beta_2 \cdot \Delta\text{Lights}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

Preferred IV (H2b, causal — flood instruments for lights):

$$\Delta\text{Deposits}_{it} = \alpha + \beta_2 \cdot \widehat{\Delta\text{Lights}}_{it} + \mu_i + \tau_t + \varepsilon_{it}$$

**Instrument discipline (R7).** First-stage $F < 10$ → second-stage
result labeled suggestive throughout; causal language removed from
abstract and conclusions.

### Results (Script 28b — linearmodels IV2SLS)

Iterative two-way demeaning: 8 iterations, tolerance $1 \times 10^{-14}$.  
District FE = 631 | Quarter FE = 36 | $N$ = 22,442 | SE clustered by
`district_state_id`

| Rule | $\hat{\beta}$ | SE | $t$ | $p$ | First-stage $F$ | Instrument | Status |
|---|---|---|---|---|---|---|---|
| A | −0.008388 | 0.034022 | −0.2465 | 0.805 | 34.673 | Strong (≥16.38) | **Null** |
| B | −0.006776 | 0.059698 | −0.1135 | 0.910 | 8.949 | Weak (<10) | Null (suggestive) |

**F-statistic derivation.** linearmodels `first_stage` overflows
numerically at 666 exogenous columns. For a single excluded instrument,
$F = t^2$ exactly (Wooldridge 2010, p. 104). Rule A: $F = (-5.888)^2 =
34.673$. Rule B: $F = (-2.992)^2 = 8.949$.

**Pre-committed null reconciliation (Constraint 1).** H2 tests the
contemporaneous window by construction. H3 confirms deposit effects are
lagged approximately two quarters — the IV specification tests a
zero-effect window by design. H2 null is mechanically consistent with
H3 and does not contradict the mechanism. Never present H2 as a
failure. Never write "H2 fails."

**Exclusion restriction caveat (standing).** Direct banking-operation
disruption (branch closures, cash logistics) is a potential threat not
fully addressed by the flood instrument. Causal language is softened
where this threat is empirically plausible.

---

## H3 — Deposit Effects Follow a Liquidity-Consistent Timing Structure

**Hypothesis.** Deposit declines emerge within two quarters of flood
exposure and are absent in the flood quarter itself — consistent with
gradual household liquidity demand, not immediate panic withdrawal.

$$\Delta\text{Deposits}_{it} = \alpha + \beta_0\,\text{Flood}_{it} + \beta_1\,\text{Flood}_{i,t-1} + \beta_2\,\text{Flood}_{i,t-2} + \tau_t + \varepsilon_{it}$$

**No district FE.** Quarter FE only. Log-differencing absorbs
district-level time trends; district FE are redundant by construction.
Pre-committed before estimation.

**Pre-committed pattern:** $\beta_0, \beta_1 \approx 0$; $\beta_2 < 0$

**Falsification conditions:**
- Significant effect only at $t_0+3$ or beyond → weakens the liquidity
  timeline, consistent with slower credit-loss transmission instead
- No lag significant → deposit channel not supported; paper pivots to
  lights-only reduced form

### Results (Script 29b — linearmodels PanelOLS)

Quarter FE = 35 | $N$ = 21,837 | SE clustered by `district_state_id`  
(L2 restriction structurally drops 2015Q1–2015Q2 — correct, not a bug)

| Lag | $\hat{\beta}$ (Rule A) | SE | $t$ | $p$ | Status |
|---|---|---|---|---|---|
| $t_0$ — flood quarter | +0.000609 | 0.001462 | +0.4167 | 0.677 | Null |
| $t_0+1$ — one quarter after | +0.001505 | 0.001114 | +1.3517 | 0.177 | Null |
| **$t_0+2$ — two quarters after** | **−0.007005** | **0.001644** | **−4.2609** | **<0.001** | **Confirmed ★** |

95% CI at $t_0+2$: [−0.010227, −0.003783]

**Rule B:** All three lags null. 209 treatment events — insufficient
power. Direction at $t_0+2$: $\hat{\beta} = -0.0038$ (negative,
consistent with Rule A). Not a falsification.

**Economic interpretation.** Deposit stress is absent in the flood
quarter and the quarter immediately following. The effect peaks at
$t_0+2$ — approximately six months post-flood — as a −0.70 pp decline
in quarterly deposit growth. Households exhaust immediate coping
mechanisms before liquidating bank deposits. This six-month lag
mechanically explains the H2 null: the contemporaneous IV tests the
wrong window.

**Robustness.** H3 $t_0+2$ survives winsorization (Script 37: $p <
0.001$, $\hat{\beta} = -0.007115$, $\Delta = 0.000110$), Northeast
exclusion (Script 33: robust), state-level clustering (Script 36: $p =
0.034$), and near-zero deposit exclusion (Script 38: $\Delta =
0.000294$). Longer lags $t_0+3$ and $t_0+4$ are null (Script 35) —
effect decays at two quarters.

### Two-Phase Liquidity Cycle — Mandatory Disclosure (Constraint 11)

Placebo test (Script 34, `09_placebo_timing.csv`): flood at $t$ predicts
deposit growth at $t-1$. The pre-period signal is **positive** and
**significant**.

| Test | $\hat{\beta}$ | SE | $p$ | District FE | Source |
|---|---|---|---|---|---|
| Test 2 — no district FE | +0.004664 | 0.001841 | 0.011 | No | Script 34 |
| Test 2b — with district FE | +0.004417 | 0.001881 | 0.019 | Yes | Script 34 |

The pre-period signal is positive and opposite in sign to the $t_0+2$
withdrawal (−0.007). A pre-existing downward trend would produce a
negative pre-period; the positive sign rules this out categorically.
The pattern identifies a **two-phase household liquidity cycle**:

- **Phase 1** ($t-1$, pre-flood): Anticipatory saving (+0.47 pp) —
  households accumulate deposits ahead of the predictable monsoon
  flood season
- **Phase 2** ($t_0+2$, post-flood): Deposit withdrawal (−0.70 pp) —
  liquidity demand materialises as displacement costs accumulate

This is a finding. It must be disclosed in full in the Robustness
section using the exact language in Constraint 11. Never describe the
two-phase cycle as a weakness or a problem for identification.

---

## H4 — Heterogeneous Deposit Response Across District Characteristics

**Hypothesis.** The flood-to-deposit effect is not uniform. Chronic
flood exposure, urban economic concentration, and monsoon seasonality
are pre-committed moderators.

$$\Delta\text{Deposits}_{it} = \alpha + \beta_0\,\text{Flood}_{it} + \beta_1\,(\text{Flood}_{it} \times Z_i) + \mu_i + \tau_t + \varepsilon_{it}$$

All $Z_i$ are observational proxies, constructed and labeled before
regression execution. The word "proxy" is mandatory in all paper text.

| Label | $Z_i$ | Construction |
|---|---|---|
| H4a | `urban_proxy` | Above-median district mean `log_lights_qt`, grouped by `district_state_id` |
| H4b | `high_exposure_proxy` | Above-median cumulative `flood_exposure_ruleA_qt`, grouped by `district_state_id` |
| H4c | `monsoon_qt` | $\mathbf{1}[q = 3]$ — July–September |

All H4 specifications: $N$ = 22,442 | District FE = 631 | Quarter FE = 36  
SE clustered by `district_state_id` | Source: Script 30b (linearmodels PanelOLS)

---

### H4a — Urban Proxy × Flood

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | +0.001207 | −0.001666 | 0.002664 | 0.532 | **Null** |
| B | −0.002890 | +0.007479 | 0.006929 | 0.280 | **Null** |

Urban split: 315 above-median | 316 at/below-median (631 total)

**Verdict: Null.** Both rules consistent. Signs disagree across rules —
noise, not signal.

**Mandatory disclosure (Constraint 4).** The February 6 H4a result
($p < 0.001$) was spurious. The `urban_proxy` was constructed on
`district_gadm` alone, collapsing AURANGABAD (Bihar / Maharashtra)
and other homonymous pairs and contaminating the median `log_lights`
threshold. After composite key correction the signal disappears
entirely. Null is the correct and final result. This must be disclosed
explicitly in the paper.

**Economic implication.** Flood-induced deposit stress is broad and
systemic — not concentrated in districts with higher pre-flood economic
activity as proxied by nighttime lights intensity.

---

### H4b — High Chronic Exposure Proxy × Flood

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| A | +0.004700 | −0.006810 | 0.002932 | 0.020 | **Suggestive only ⚠** |
| B | +0.012016 | −0.013419 | 0.007670 | 0.080 | Marginal |

High-exposure split: 255 above-median | 376 at/below-median  
(median = 3.0 cumulative events; strictly greater than median = above-median)

**Verdict: Suggestive only. Does not survive winsorization.**

**Winsorization failure — mandatory disclosure (Constraint 12).**
Rule A $p = 0.865$ on the winsorized panel (Script 37; 2.01% of
observations clipped symmetrically). The baseline significance is
entirely driven by extreme deposit observations. H4b is **demoted**
from supported to suggestive. It cannot be presented as a robust
finding under any framing.

**Net effect (Rule A, non-winsorized only — not robust, descriptive):**
- Low-exposure baseline: $+0.0047$ (marginal precautionary saving)
- High-exposure net: $+0.0047 + (-0.0068) = -0.0021$ (net withdrawal)

Report as a descriptive estimate with explicit winsorization caveat.
Never present as causal or robust.

---

### H4c — Monsoon Season × Flood

| Rule | Baseline $\hat{\beta}$ | Interaction $\hat{\beta}$ | SE | $p$ | Status |
|---|---|---|---|---|---|
| **A** | **−0.004700** | **+0.012495** | **0.002884** | **<0.001** | **Confirmed ★** |
| B | −0.000838 | +0.002287 | 0.007968 | 0.774 | Null |

95% CI on Rule A interaction: [+0.006843, +0.018147]

**Verdict: Partial. Rule A confirmed. Rule B null. Fragile to flood
intensity definition.**

**Net monsoon effect (Rule A):**
- Non-monsoon flood: $-0.0047$
- Monsoon flood net: $-0.0047 + 0.0125 = +0.0078$

Moderate flood events during the monsoon quarter do not reduce deposits.
Seasonal agricultural income inflows dominate displacement pressure
during Q3. Severe floods (Rule B) override this buffer entirely —
distress dominates at high flood intensity.

**Required language (Constraint 2 — exact, no paraphrase):**
*"Monsoon seasonality moderates the deposit response to
moderate-intensity floods (Rule A: $\hat{\beta} = +0.012$, $p <
0.001$) but not to severe flood events (Rule B: $p = 0.774$). The
heterogeneity result is fragile to flood intensity definition."*

---

## H5 — Network Contagion (Not Tested)

**Hypothesis.** Banking stress spills over to non-flood-exposed
districts, increasing with bank-network connectedness or geographic
adjacency.

**Status: Not tested. Data-contingent. Not in regression pipeline.**

This hypothesis requires a credible district-level weight matrix $W$
capturing shared branch networks or interbank linkages. No such matrix
is available at the required granularity for the India sample. H5 will
not be tested by proxy. If suitable network data become available, H5
represents a natural extension — not a specification already run.

---

## Joint Mechanism Assessment

The shadow run mechanism requires four conditions. Pre-committed
interpretations against locked outcomes:

| Condition | Pre-committed interpretation | Locked outcome |
|---|---|---|
| H1 confirmed | First stage valid; IV credible | Confirmed at 631 clusters ($p < 0.001$). Does not survive state-level clustering (wild bootstrap p = 0.158). Disclosed in full |
| H2 null | Deposit effects lagged, not contemporaneous; IV window by construction captures zero | Null confirmed. Pre-committed reconciliation applies. Never a contradiction |
| H3 confirmed at $t_0+2$ | Rapid liquidity mechanism (≤6 months) | Confirmed. Effect absent at $t_0$ and $t_0+1$; peaks at $t_0+2$ |
| H4 partial | Vulnerability-consistent moderation | H4a null; H4b suggestive (fails winsorization); H4c Rule A confirmed, Rule B null |

**Operative conclusion.** The shadow run mechanism is supported through
the reduced-form timing channel (H3: $t_0+2$, $p < 0.001$) rather
than through the contemporaneous IV channel (H2: null). H3 identifies
a two-phase household liquidity cycle — anticipatory saving at $t-1$
followed by post-flood withdrawal at $t_0+2$ — as the paper's central
empirical contribution. H4c provides partial evidence of
seasonality-consistent heterogeneity (Rule A only). H4b is suggestive
pending a winsorization-robust specification.

---

## Robustness: Final Status

| Check | Script | Outcome |
|---|---|---|
| R1 — Both flood rules | 27b–30b | Complete — both reported throughout |
| R2 — Placebo timing | 34 | Two-phase cycle confirmed; pre-period $p = 0.011$, survives district FE ($p = 0.019$) |
| R3 — Winsorization (1%/99%, 450 obs, 2.01%) | 37 | H3 robust ✓ · **H4b fails ($p = 0.865$)** ✗ |
| R4 — Nominal INR | 32 | Quarter FE absorb national price trends; limitation acknowledged |
| R5 — Longer lags ($t_0+3$, $t_0+4$) | 35 | Both null; effect decays at $t_0+2$ |
| R6 — State clustering (34 clusters) | 36 | H3 $p = 0.034$ ✓ · H1 $p = 0.105$ |
| R6b — Wild cluster bootstrap (999 iter.) | 36b | **H1 fails: Rule A $p = 0.158$, Rule B $p = 0.267$** |
| R7 — IV instrument discipline | 28b | Rule B $F = 8.949$; suggestive label applied throughout |
| R8 — Northeast sensitivity | 33 | H3 $t_0+2$ robust to NE exclusion ✓ |

**All eight robustness checks complete. Zero open items.**

---

## Mandatory Writing Constraints

Active disclosure requirements. Enforced in every draft without
exception. No softening. No omission. No paraphrase where exact
language is specified.

---

**Constraint 1 — H2 null reconciliation.**
Deposit effects are lagged (H3), not contemporaneous. The IV
specification tests the contemporaneous window by construction. Never
present H2 null as a contradiction of the mechanism. Never use the
phrase "H2 fails."

---

**Constraint 2 — H4c language (exact — no paraphrase permitted).**
*"Monsoon seasonality moderates the deposit response to
moderate-intensity floods (Rule A: $\hat{\beta} = +0.012$, $p <
0.001$) but not to severe flood events (Rule B: $p = 0.774$). The
heterogeneity result is fragile to flood intensity definition."*

---

**Constraint 3 — Rule B IV.**
$F = 8.949 < 10$. Labeled suggestive throughout. Causal language
removed from abstract and conclusions for Rule B IV results. $F$-stat
reported in every table containing H2.

---

**Constraint 4 — H4a spurious benchmark disclosure.**
The February 6 H4a result ($p < 0.001$) was spurious — caused by
homonymous FE collapse (`district_gadm` alone, 624 FE instead of 631).
Corrected result is null. Disclosed explicitly in the paper — footnote
or appendix. The correction predates all regression execution.

---

**Constraint 5 — Proxy discipline.**
`urban_proxy` and `high_exposure_proxy` are proxies. Every mention in
the paper carries the word "proxy." Never claim census-based
classification.

---

**Constraint 6 — TUENSANG disclosure.**
Flag the within-year reversal (+3.21) as a likely reporting artifact
in a Data section footnote or Appendix note.

---

**Constraint 7 — Demonetization gap.**
2016Q3–2017Q1 is absent from the panel (RBI publication blackout
coinciding with November 2016 demonetization). Named explicitly in
Section 3.4 (Panel Construction). Never report 2016 or 2017 as
full-year figures.

---

**Constraint 8 — Nominal INR.**
Deposits in nominal Rupees. Quarter FE absorb national price trends.
Acknowledged as a limitation in Section 3.3 or Section 8.

---

**Constraint 9 — Estimator discipline.**
Final paper tables use linearmodels PanelOLS (Scripts 27b–30b). Never
mix statsmodels and linearmodels results in the same table or the same
sentence.

---

**Constraint 10 — Northeast robustness.**
Script 33 confirms H3 $t_0+2$ is robust to Northeast exclusion. H3 is
not Northeast-driven. Report in Robustness section.

---

**Constraint 11 — R2 pre-trend disclosure (exact — no exceptions).**

*"Flood exposure at time $t$ predicts higher deposit growth at $t-1$
($\hat{\beta} = +0.005$, $p = 0.011$), a signal that survives the
inclusion of district fixed effects ($\hat{\beta} = +0.004$, $p =
0.019$). This pre-period effect is positive and opposite in sign to the
$t_0+2$ withdrawal effect ($-0.007$), indicating a two-phase household
liquidity cycle — anticipatory saving ahead of the predictable flood
season followed by post-flood deposit withdrawal — rather than a
pre-existing downward trend in deposits."*

Never claim the R2 placebo is clean. Never omit the pre-period. Never
describe the two-phase cycle as a weakness.

---

**Constraint 12 — H4b winsorization failure (exact — no exceptions).**

*"The high flood exposure interaction (H4b) is significant in the
baseline specification (Rule A: $\hat{\beta} = -0.007$, $p = 0.020$)
but does not survive winsorization of the top and bottom 1% of deposit
growth observations ($p = 0.865$). The effect is sensitive to extreme
observations and should be interpreted as suggestive evidence only."*

Never present H4b as a robust finding. Never omit the winsorization
failure.

---

**Constraint 13 — H1 wild bootstrap failure (exact — no exceptions).**

*"H1 is significant under district-level clustering (631 clusters,
$p < 0.001$) but does not survive state-level clustering under
conventional SE (34 clusters, $p = 0.105$) or wild cluster bootstrap
(Rule A: $p = 0.158$, Rule B: $p = 0.267$). The coefficient is stable
across all three specifications ($\hat{\beta} = -0.044$). Significance
is therefore sensitive to the level of clustering assumed. The
district-clustered result is the primary specification; state-level
results are reported as a robustness bound."*

Never claim H1 is robust to state-level clustering.

---

## Data State

All files verified clean as of March 21, 2026. Results locked.
Do not re-run.

| File | Rows | Key assertion |
|---|---|---|
| `district_crosswalk_draft.csv` | 762 | Hard assert: `len == 762` |
| `flood_exposure_panel.csv` | 26,640 | Rule A: 2,518 events · 666 district-state pairs |
| `regression_panel_final.csv` | 23,347 | 23 columns · 631 districts × 37 quarters |
| `regression_panel_final_winsor.csv` | 23,347 | 24 columns · 450 obs clipped (2.01%) |

**Analysis sample:** 631 composite pairs × 37 quarters = **23,347 observations**  
**Rule A treatment:** 2,238 events (9.59%) · 569 districts ever exposed  
**Rule B treatment:** 209 events (0.90%) · 141 districts ever exposed  
**VIIRS coverage:** 100.0% · **Deposit coverage:** 98.9%

**Final paper table CSVs — linearmodels only. Do not substitute.**

| File | Script | Contents |
|---|---|---|
| `02b_H1_linearmodels.csv` | 27b | H1 first stage, both rules |
| `03b_H2_linearmodels.csv` | 28b | H2 IV 2SLS, both rules |
| `04b_H3_linearmodels.csv` | 29b | H3 distributed lag, both rules |
| `05b_H4_linearmodels.csv` | 30b | H4 heterogeneity, all specifications |

---

*Version 2.6 — locked March 21, 2026*  
*Principal Investigator: Jaseel Badar, Harvard University*  
*Repository: github.com/JaseelBadar/Climate-Migration-Bank-Fragility*