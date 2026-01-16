## FORMAL RESEARCH HYPOTHESES (v1.3 — Feasibility-aligned)
**Project**: Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India (2015–2024)  
**Purpose**: Convert the “Shadow Run” narrative into testable, falsifiable statements that map cleanly to the Variables Codebook and the Python pipeline.

**Version note (discipline)**:
- v1.3 updates wording for internal consistency and feasibility alignment (timing language, flood exposure definitions, and what is “core” vs “extension”).  
- This document is not allowed to “chase results.” If any hypothesis is modified due to data infeasibility, the modification must be explicitly labeled as such (and dated) rather than silently rewriting the theory.

---

### 0) Notation and timing (so tests don’t drift)
- District index \(i\), quarter index \(t\), month index \(m\).
- Flood shocks originate at daily resolution (EM-DAT) and are mapped into quarter \(t\).
- Night lights are observed monthly (VIIRS) and aggregated to the quarter level to align with RBI deposits.
- Key outcomes:
  - \(\Delta Deposits_{it}\): quarterly log change in deposits (RBI).
  - \(\Delta Lights_{it}\): quarterly change in log VIIRS brightness (constructed from monthly VIIRS).
- Flood exposure measures (two precision regimes):
  - \(Flood^{A}_{it}\): “Rule A” flood exposure (district Admin Units where available; otherwise state-level fallback mapped to all districts in the state).
  - \(Flood^{B}_{it}\): “Rule B” flood exposure (district-only; no fallback).

**Interpretation discipline (pre-committed)**:
- “Lights” is treated as a proxy consistent with displacement/outflows or disruption-driven activity loss; it is not proof of migration without external corroboration.
- “Shadow run” is defined as a sharp decline in deposits consistent with liquidity stress, not solvency deterioration.

**Location precision note (pre-committed)**:
- EM-DAT location precision is heterogeneous, so all core results must be reported in two panels:
  1) Full sample using \(Flood^{A}_{it}\) (power, but attenuation risk).
  2) High-precision sample using \(Flood^{B}_{it}\) (credibility, but smaller effective treatment variation).

**Inference note (pre-committed)**:
- Baseline specifications use district and quarter fixed effects.
- Standard errors should be clustered at the district level unless there is a documented reason not to; if not clustered, inference must be treated as potentially optimistic.

---

## H1 — Floods trigger measurable outflows/disruption (VIIRS proxy)
**Hypothesis (H1)**: Flood exposure produces a statistically and economically meaningful decline in night-time lights in affected districts in the immediate post-shock window, consistent with population displacement and/or disruption-driven outflows.

**Operational statement**: After a flood in quarter \(t\), the change in log VIIRS brightness is negative on average in the same quarter and/or the next quarter.

**Primary test** (district and time fixed effects):
\[
\Delta Lights_{it} = \alpha + \beta_1 Flood_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]
Where \(Flood_{it}\) is estimated separately as \(Flood^{A}_{it}\) and \(Flood^{B}_{it}\), and \(X_{it}\) includes (at minimum) seasonality controls (quarter FE already absorbs national seasonality; optional monsoon indicator is redundant but may be used for exposition).

- Expected sign: \(\beta_1 < 0\).

**Measurement precision caveat (pre-committed)**:
- State-level fallback in \(Flood^{A}_{it}\) introduces false positives and biases \(\beta_1\) toward zero (attenuation).
- Therefore, \(Flood^{A}\) estimates are interpreted as conservative lower bounds relative to a “true local” district-level effect.

**Economic significance threshold (pre-committed)**:
- H1 is economically meaningful if the implied effect is at least a 5% decline in quarterly lights (order-of-magnitude threshold; if the empirical volatility of \(\Delta Lights\) makes 5% nonsensical, the threshold must be revised *once* and documented before final tables).

**Falsification condition**:
- If \(\beta_1 \ge 0\) (no dimming or systematic brightening), the “flood → outflow/disruption captured by lights” interpretation fails and lights cannot be used as the displacement proxy in this setting.

---

## H2 — Outflows/disruption (proxied by lights) coincide with deposit withdrawals (liquidity stress)
**Hypothesis (H2)**: Districts experiencing larger declines in night lights also experience larger declines in bank deposits, consistent with liquidity demand / withdrawals rather than slow-moving credit losses.

**Sign logic**:
- In shock periods, both \(\Delta Lights_{it}\) and \(\Delta Deposits_{it}\) are expected to be negative.
- Therefore the slope in a regression of deposits on lights is expected to be positive: \(\beta_2 > 0\).

### H2a — Reduced-form association (informative, not causal by itself)
\[
\Delta Deposits_{it} = \alpha + \beta_2 \Delta Lights_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

**Endogeneity warning (explicit)**:
- \(\Delta Lights_{it}\) may correlate with unobserved shocks that also directly affect deposits (income shocks, policy disruptions, infrastructure outages).
- Therefore, H2a is descriptive/diagnostic, not the preferred causal estimate.

### H2b — Preferred causal test (IV / 2SLS)
**Strategy**: instrument \(\Delta Lights_{it}\) using flood exposure (first stage is H1).

First stage:
\[
\Delta Lights_{it} = \alpha + \beta_1 Flood_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

Second stage:
\[
\Delta Deposits_{it} = \alpha + \beta_2 \widehat{\Delta Lights}_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

- Expected sign: \(\beta_2 > 0\).

**Instrument choice discipline**:
- Report 2SLS estimates instrumenting with \(Flood^{B}\) (high-precision) where feasible.
- Also report \(Flood^{A}\) instrument results with explicit weak-instrument and attenuation warnings; do not “sell” the IV if the first stage is weak.

**Exclusion restriction / identifying assumption (stated clearly)**:
- The IV interpretation requires floods shift deposits primarily through the displacement/disruption channel proxied by lights.
- Threats: direct banking-operation disruption (branch closures, cash logistics interruptions) may affect deposits independently of lights.
- Therefore, causal language must be softened if evidence of direct operational disruption is plausible and unaddressed.

### H2c — Event indicator form (migration/disruption proxy event)
Define an event:
- \(MigrationProxy_{it} = 1[\Delta Lights_{it} < -\theta]\)

**Threshold rule (pre-committed; not arbitrary)**:
- Baseline \(\theta\) must be chosen from the distribution of \(\Delta Lights\) among flood-exposed district-quarters in the high-precision sample (document the exact rule used).
- Robustness: \(\theta \in \{0.10, 0.15, 0.20\}\).

Estimate:
\[
\Delta Deposits_{it} = \alpha + \beta_2 MigrationProxy_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

- Expected sign (event dummy): \(\beta_2 < 0\).

**Economic significance threshold (pre-committed)**:
- H2 is economically meaningful if a 10% decline in lights predicts at least a 2% decline in deposits within 0–1 quarters (order-of-magnitude benchmark; if deposit volatility makes 2% meaningless, revise once and document before final tables).

**Falsification condition**:
- If deposits do not respond to lights changes (insignificant or wrong-signed coefficients in both reduced form and IV), the displacement/disruption → liquidity link is not supported.

---

## H3 — Shadow-run timing: deposit shocks occur quickly (liquidity timeline)
**Hypothesis (H3)**: Deposit declines occur in the same quarter as the flood and/or the next quarter, consistent with liquidity stress rather than slow-moving credit-loss transmission.

### H3a — Timing fingerprint (core, feasible)
Distributed lags (deposit change at \(t\) explained by flood exposure at \(t, t-1, t-2\)):
\[
\Delta Deposits_{it} = \alpha + \beta_0 Flood_{it} + \beta_1 Flood_{i,t-1} + \beta_2 Flood_{i,t-2} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

- Expected: \(\beta_0 < 0\) and/or \(\beta_1 < 0\), with attenuation by \(\beta_2\).

**Falsification condition**:
- If effects appear only at long lags (e.g., \(t-3\) and beyond) and not at \(t\) or \(t-1\), the “liquidity-timeline” interpretation is weakened.

### H3b — Liquidity-not-solvency fingerprint (extension, conditional)
If district-level credit-risk indicators (e.g., NPAs) become available:
- Deposit declines should not be fully mediated by contemporaneous credit deterioration.
- If credit-risk measures spike immediately and explain deposit declines, the mechanism shifts toward solvency/credit-loss transmission rather than shadow runs.

If credit-risk data are unavailable, H3b is explicitly labeled as a limitation (not a silently “assumed” result).

---

## H4 — Heterogeneity (core, feasible with current data)
**Hypothesis (H4)**: The deposit response to floods is heterogeneous across district types, consistent with differential exposure to liquidity stress.

**Operational statement**:
- The flood → deposits effect is more negative in districts with higher baseline financial intensity / urbanization proxies, and/or in districts with higher historical flood exposure.

Baseline interaction form:
\[
\Delta Deposits_{it} = \alpha + \beta_0 Flood_{it} + \beta_1 (Flood_{it} \times Z_i) + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]
Where \(Z_i\) is a pre-defined district characteristic or proxy (e.g., baseline deposit level category).

- Expected sign: \(\beta_1 < 0\) for “more vulnerable” groups.

**Proxy discipline**:
- If true urban/rural classification is unavailable, any “urbanization” proxy (e.g., median-split baseline deposits) must be labeled as a proxy and treated as suggestive.

**Falsification condition**:
- If interaction effects are consistently zero, the mechanism is not heterogeneous by these proxies; claims must be narrowed accordingly.

---

## H5 — Network contagion (extension; requires new data)
**Hypothesis (H5)**: Banking stress spills over to districts not directly flood-exposed, increasing with bank-network connectedness and/or geographic adjacency.

Define:
- \(Spillover_{jt} = \sum_i W_{ji} Flood_{it}\)

Then:
\[
\Delta Deposits_{jt} = \alpha + \beta_5 Spillover_{jt} + \gamma X_{jt} + \mu_j + \tau_t + \varepsilon_{jt}
\]

- Expected: \(\beta_5 < 0\).

**Dependency warning**:
- If a credible \(W\) matrix (shared bank networks / branch linkages) is infeasible at district granularity, H5 remains a stated extension and is not “tested by proxy” without explicit justification.

---

## Joint mechanism claim (what “success” looks like)
The Shadow Run mechanism is supported if:
1. **H1 holds** (floods reduce lights in the short-run, robustly across precision regimes),
2. **H2 holds** (lights declines predict deposit declines; IV preferred only when credible),
3. **H3a holds** (timing is immediate or one-quarter lag, consistent with liquidity stress),
4. **H4 holds** (heterogeneity is directionally consistent with vulnerability patterns),
5. **H5 holds** when network data are available (spillovers beyond direct exposure).

If H1 holds but H2 fails, the project becomes “disasters reduce activity (lights) without measurable deposit effects,” and the liquidity narrative must be softened.
If H1 fails, the displacement proxy fails and the chain cannot be claimed.

---

## Pre-committed robustness and guardrails (to keep the paper honest)
1. Threshold robustness: \(\theta \in \{0.10, 0.15, 0.20\}\).
2. Placebo timing: test floods predicting changes in \(t-1\) (should not).
3. Precision stress-test: report \(Flood^{A}\) and \(Flood^{B}\) side by side.
4. Inference discipline: district-clustered SE baseline; if not clustered, state it and soften inference.
5. Interpretation constraint: lights are “consistent with displacement/outflows,” not proof of migration.
6. IV discipline: report first-stage strength; if weak, label IV as suggestive or drop causal language.