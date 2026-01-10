## FORMAL RESEARCH HYPOTHESES (v1.1 — Edited)  
**Project**: Climate Migration, Night Lights, and Bank Fragility in India (2015–2024)  
**Purpose**: Convert the “Shadow Run” narrative into testable, falsifiable statements that map cleanly to the Variables Codebook and the Python pipeline.

***

### 0) Notation and timing (so tests don’t drift)
- District index \(i\), quarter index \(t\), month index \(m\).
- Flood shocks originate at daily resolution (EM‑DAT) and are mapped into quarter \(t\).
- Night lights are observed monthly (VIIRS) and will be aggregated to the quarter level to align with RBI deposits.
- Key outcomes:
  - \(\Delta Deposits_{it}\): quarterly log change in deposits (RBI).
  - \(\Delta Lights_{it}\): quarterly change in log VIIRS brightness (constructed from monthly VIIRS).
  - \(Flood_{it}\): indicator for flood exposure in district-quarter (EM‑DAT mapping).
- A “shadow run” is defined as a sharp decline in deposits without evidence that the mechanism is credit deterioration (the stress is liquidity, not solvency).

**Location precision note (pre-committed)**:
- EM‑DAT flood location precision is heterogeneous: some events include district-level Admin Units; some do not.
- We pre-commit to running a “high-precision” sample using only district-identified events (where possible), and a “full” sample that uses fallback mapping rules (with explicit measurement-error disclosure).
- This is not optional: results must be presented for both samples, because measurement error in \(Flood_{it}\) mechanically attenuates coefficients.

***

## H1 — Floods trigger measurable outflows (VIIRS migration proxy)
**Hypothesis (H1)**: Flood exposure produces a statistically and economically meaningful decline in night-time lights in affected districts in the immediate post-shock window, consistent with population displacement and/or disruption-driven outflows.

**Operational statement**: For district \(i\), after a flood in quarter \(t\), the change in log VIIRS brightness in that same quarter or the next quarter is negative on average:
- Expected sign: \(\beta_1 < 0\)

**Primary test** (district and time fixed effects):
\[
\Delta Lights_{it} = \alpha + \beta_1 Flood_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]
Where \(X_{it}\) includes (at minimum) monsoon/seasonality controls; rainfall controls are added if available.

**Measurement precision caveat (pre-committed)**:
- When flood location is only available at state level (not district), coding \(Flood_{it}=1\) for all districts in the state introduces false positives.
- This creates classical measurement error in the treatment variable and biases \(\beta_1\) toward zero (attenuation).
- Therefore, the “full sample” \(\beta_1\) should be interpreted as a conservative lower bound on the local effect, and a district-identified (“high-precision”) estimate will be reported separately.

**Economic significance threshold (pre-committed)**:
- H1 is economically meaningful if the implied effect is at least a 5% decline in quarterly lights in the post-flood window (a detectable district-scale shock), not merely statistically different from zero.

**Falsification condition**:
- If \(\beta_1 \ge 0\) (no dimming, or systematic brightening), the interpretation “flood → outflow/disruption captured by lights” fails and lights cannot be used as the migration/displacement proxy in this setting.

**Interpretation discipline**:
- H1 does not claim “people moved” with certainty.
- It claims floods create a measurable luminosity shock consistent with outflows/disruption, which becomes a usable empirical proxy if it is systematic, directional, and temporally aligned.

***

## H2 — Outflows (proxied by lights) coincide with deposit withdrawals (liquidity shock)
**Hypothesis (H2)**: Districts experiencing larger declines in night lights also experience larger declines in bank deposits, consistent with migration-induced liquidity demand (withdrawals) rather than slow-moving credit losses.

**Operational statement**:
- \(\Delta Deposits_{it}\) co-moves positively with \(\Delta Lights_{it}\) because both become negative during outflow episodes.
- Expected sign (continuous specification): \(\beta_2 > 0\) (since both changes are negative in shock periods)

### H2a — Reduced-form association (informative, not causal by itself)
\[
\Delta Deposits_{it} = \alpha + \beta_2 \Delta Lights_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

**Endogeneity warning (explicit)**:
- \(\Delta Lights_{it}\) may be correlated with unobserved shocks that also directly affect deposits (e.g., agricultural income shocks, localized power outages, policy disruptions).
- Therefore, H2a is treated as descriptive / diagnostic, not the preferred causal estimate.

### H2b — Preferred causal test (IV / 2SLS)
**Strategy**: instrument \(\Delta Lights_{it}\) using \(Flood_{it}\) (first stage is H1).

**First stage**:
\[
\Delta Lights_{it} = \alpha + \beta_1 Flood_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

**Second stage**:
\[
\Delta Deposits_{it} = \alpha + \beta_2 \widehat{\Delta Lights}_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]

**Expected sign**:
- \(\beta_2 > 0\) (lights fall → deposits fall; both negative changes imply a positive slope).

**Exclusion restriction / identifying assumption (stated clearly)**:
- The IV interpretation requires that floods shift deposits primarily through district-level economic disruption/outflows proxied by lights.
- Threats: floods may also affect deposits directly via banking operations (e.g., branch disruption, cash logistics interruptions, local payment system outages) in ways not fully captured by lights.
- Therefore, IV results must be interpreted with discipline: H3 (timing) strengthens the liquidity narrative but does not “prove” exclusion; any evidence of direct operational disruption requires softening causal language.

### H2c — Event indicator form (migration proxy event)
Define a migration proxy event:
- \(MigrationProxy_{it} = 1[\Delta Lights_{it} < -\theta]\)

**Threshold rule (pre-committed; not arbitrary)**:
- The baseline threshold \(\theta\) will be chosen **data-driven** from the distribution of \(\Delta Lights\) in flood-exposed district-quarters in the high-precision sample (e.g., median or 75th percentile of negative changes—decision recorded before estimating H2c).
- Robustness checks will evaluate \(\theta \in \{0.10, 0.15, 0.20\}\).

Then estimate:
\[
\Delta Deposits_{it} = \alpha + \beta_2 MigrationProxy_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]
- Expected sign (event dummy): \(\beta_2 < 0\)

**Economic significance threshold (pre-committed)**:
- H2 is economically meaningful if a 10% decline in lights predicts at least a 2% decline in deposits in the same quarter or next quarter (order-of-magnitude threshold; updated if deposit volatility suggests a different natural scale, recorded before final regressions).

**Falsification condition**:
- If deposits do not respond to lights changes (insignificant or wrong-signed coefficients in both reduced form and IV), the “outflow/disruption → liquidity” link is not supported.
- That would force a redesign: either deposits are not the correct banking stress channel, or lights are not capturing migration-like shocks.

***

## H3 — The “shadow run” signature: deposit shocks occur on a liquidity timeline, not a credit-loss timeline
**Hypothesis (H3)**: The deposit response is immediate (same quarter or next quarter) and is not primarily explained by slow-moving credit deterioration.

This is a mechanism statement, so it has two empirical fingerprints:

### H3a (Timing fingerprint)
Deposit withdrawals occur quickly relative to flood timing.
- Expected pattern: strongest effects in \(t\) and \(t+1\), attenuating afterward.

**Test (distributed lags)**:
\[
\Delta Deposits_{it} = \alpha + \beta_0 Flood_{it} + \beta_1 Flood_{i,t-1} + \beta_2 Flood_{i,t-2} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}
\]
- Expected: \(\beta_0\) and/or \(\beta_1 < 0\), and effects weaken for longer lags.

### H3b (Liquidity-not-solvency fingerprint; conditional on data availability)
Where credit-risk indicators exist (later, if we obtain them), deposit withdrawals should not be fully explained by contemporaneous increases in credit distress.
- Expected: deposit effects persist even after controlling for credit-risk proxies; and/or credit-risk proxies do not spike immediately in the same window as deposits.

**Falsification condition**:
- If deposit declines appear only with long lags (e.g., \(t+3\) or later), or if they are fully mediated by credit-risk deterioration, the phenomenon is not a “shadow run” as defined here; it becomes standard credit-loss transmission after disasters.

**Practical note**:
- If district-level credit-risk measures (e.g., NPAs) are unavailable, we retain H3a (timing) as the core shadow-run signature and explicitly label the credit-risk separation as a limitation.

***

## H4 — Contagion: shocks propagate through banking networks beyond the flood footprint
**Hypothesis (H4)**: Banking stress spills over to districts that are not directly flood-exposed, with intensity increasing in bank-network connectedness (shared bank presence / shared branch networks) and/or geographic adjacency.

**Operational statement**:
- Deposits decline in district \(j\) when it is connected to flood-exposed districts \(i\), even if \(Flood_{jt}=0\).
- Expected sign: connectedness spillover coefficient \(< 0\)

**Primary test concept (network spillover)**:
Let \(Spillover_{jt} = \sum_i W_{ji} Flood_{it}\), where \(W_{ji}\) captures connectedness (shared banks, or adjacency). Then:
\[
\Delta Deposits_{jt} = \alpha + \beta_4 Spillover_{jt} + \gamma X_{jt} + \mu_j + \tau_t + \varepsilon_{jt}
\]
- Expected: \(\beta_4 < 0\)

**Falsification condition**:
- If spillovers are zero after controlling for time fixed effects and location fixed effects, then the mechanism is localized.
- That is not a failure of the paper, but it narrows the claim to “local shadow runs,” not “systemic propagation.”

**Dependency warning**:
- H4 requires network variables we may or may not have at district granularity.
- If network data are infeasible, H4 becomes an explicit extension rather than a core claim.

***

## Joint mechanism claim (what “success” looks like)
The Shadow Run mechanism is supported if:
1. **H1 holds** (floods reliably shift lights downward in the short-run), and
2. **H2 holds** (lights declines predict deposit declines; preferred estimate via IV), and
3. **H3a holds** (timing is immediate, consistent with liquidity stress), and
4. **H4 holds** *when network data are available* (spillovers exist beyond direct exposure).

If H1 and H2 hold but H3a fails, the chain becomes “disasters affect local economies and later deposits,” which is a different story and must be written as such.  
If H1 fails, the empirical migration proxy must be redesigned before proceeding.

***

## Pre-committed robustness and “anti-hallucination” checks (to keep the paper honest)
These are not decorative. They are guardrails against overclaiming.

1. **Threshold robustness**: Re-estimate \(MigrationProxy_{it}\) under \(\theta \in \{0.10, 0.15, 0.20\}\).
2. **Placebo timing / pre-trends**: Test whether floods “predict” lights/deposit changes in \(t-1\) (they should not).
3. **Seasonality controls**: Always include quarter fixed effects (or monsoon indicator) so agricultural cycles don’t masquerade as migration/outflows.
4. **Geographic precision stress-test**: Re-run all main tests using only floods with explicit district-level mentions (high-precision sample), and report alongside full-sample results.
5. **Interpretation constraint**: Throughout, refer to lights as a “proxy consistent with displacement/outflows,” not proof of migration, unless corroborated by an external migration dataset later.
6. **Exclusion restriction discipline (IV)**: If evidence emerges that floods directly disrupt banking operations independent of the lights channel (e.g., branch closures, cash logistics interruptions), IV claims must be softened and presented as suggestive rather than causal.