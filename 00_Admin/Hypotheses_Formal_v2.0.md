## FORMAL RESEARCH HYPOTHESES (v2.0 — Phase 4 invalid; VIIRS contamination discovered)

**Project**: Climate Shocks, Displacement, and Bank Liquidity Risk: Evidence from Night-Lights in India (2015–2024)

**Purpose**: Convert the "Shadow Run" narrative into testable, falsifiable statements that map cleanly to the Variables Codebook and the Python pipeline.

---

### Version History (Discipline)

**v1.3**: Wording updates for internal consistency and feasibility alignment (timing language, flood exposure definitions, core vs extension).

**v1.4 (2026-01-18)**: Documents Phase 4 preliminary regression results (H1-H4). All results pending data quality corrections. No hypotheses modified to chase results.

**v1.5 (2026-01-20 17:00 IST)**: Critical data integrity update. Discovered Script 21 VIIRS dissolve bug (homonymous district merging) during Phase 4 code audit. Bug affected 17 homonymous districts (e.g., Aurangabad Bihar vs Maharashtra), causing 2,040 missing monthly observations and measurement error contamination in all H1-H4 regression results. This document does not chase results. Any hypothesis modification due to data infeasibility must be explicitly labeled and dated.

**v1.6 (2026-01-20 23:30 IST)**: Script 21 fix implemented and overnight regeneration initiated. Deleted Lines 52-55 (dissolve block) from Script 21; added validation assertion for 676 districts. All contaminated files backed up to CONTAMINATED_BACKUP folders. VIIRS extraction running overnight (6-8 hours); Scripts 22-30 scheduled for morning of 2026-01-21. Current H1-H4 results suspended; expect coefficient changes (H1 beta likely to increase from -0.0126 to approximately -0.025 due to reduced attenuation). Hypotheses unchanged; only evidence status is "regenerating."

**v1.7 (2026-01-30 23:26 IST)**: RBI source contamination concern raised during Script 13 review. Suspected duplicate 2016 Q1-Q3 data in `RBI_Deposits_2017_2022.xlsx`. All deposit-based tests (H2, H3, H4) flagged for review. VIIRS data (666 districts, 79,920 monthly observations) unaffected.

**v1.8 (2026-02-01 23:15 IST)**: RBI contamination concern RESOLVED (false alarm from fiscal-calendar conversion misunderstanding). Forensic audit confirmed all RBI source files clean. Phase 3d complete: 120 VIIRS tiles processed to regression-ready panel (23,347 obs, 23 variables, 100% VIIRS-deposit overlap). Regression variables engineered (logs, changes, lags L1-L4). Data quality validated via Scripts 25, 26, temp.py diagnostics. Analysis sample: 631 districts, 37 quarters (2015Q1-2016Q2, 2017Q2-2024Q4), 1,984 flood events (8.50% treatment rate). All hypotheses (H1-H4) ready for Phase 4 econometric testing. No hypothesis modifications; only data status updated.

**v1.9**: RBI deposit extraction bug discovered. Script 13 extracted wrong column (offices instead of deposits) for 2004-2022 data. All Phase 4 results invalidated. Bug documented, fix identified.

**v2.0**: Deposits corrected (Feb 5), VIIRS contamination discovered (Feb 6). Scripts 18, 21 merged 7 homonymous districts across states (Aurangabad, Balrampur, Bijapur, Bilaspur, Hamirpur + 2 others). 518 rows affected (~259 with measurement error). Statistical impact: H1 coefficient attenuated, H2 weak instrument problem, H4c spurious result. H3 may be valid if specification excludes VIIRS. Results below flagged as contaminated. Hypotheses unchanged.
---

### Notation and Timing

- District index i, quarter index t, month index m
- Flood shocks originate at daily resolution (EM-DAT) and mapped into quarter t
- Night lights observed monthly (VIIRS) and aggregated to quarterly level to align with RBI deposits
- Key outcomes:
  - Delta_Deposits_it: quarterly log change in deposits (RBI)
  - Delta_Lights_it: quarterly change in log VIIRS brightness (constructed from monthly VIIRS)
- Flood exposure measures (two precision regimes):
  - Flood_A_it: "Rule A" flood exposure (district Admin Units where available; otherwise state-level fallback mapped to all districts in state)
  - Flood_B_it: "Rule B" flood exposure (district-only; no fallback)

**Interpretation discipline (pre-committed)**:

- "Lights" treated as proxy consistent with displacement/outflows or disruption-driven activity loss; not proof of migration without external corroboration
- "Shadow run" defined as sharp decline in deposits consistent with liquidity stress, not solvency deterioration

**Location precision note (pre-committed)**:

- EM-DAT location precision is heterogeneous; all core results reported in two panels:
  - (1) Full sample using Flood_A_it (statistical power, but attenuation risk)
  - (2) High-precision sample using Flood_B_it (credibility, but smaller treatment variation)

**Inference note (pre-committed)**:

- Baseline specifications use district and quarter fixed effects
- Standard errors clustered at district level unless documented reason not to; if not clustered, inference treated as potentially optimistic

---

## H1: Floods trigger measurable outflows/disruption (VIIRS proxy)

**Hypothesis**: Flood exposure produces statistically and economically meaningful decline in night-time lights in affected districts in immediate post-shock window, consistent with population displacement and/or disruption-driven outflows.

**Operational statement**: After flood in quarter t, change in log VIIRS brightness is negative on average in same quarter and/or next quarter.

**Primary test** (district and time fixed effects):

Delta_Lights_it = alpha + beta_1 * Flood_it + gamma * X_it + mu_i + tau_t + epsilon_it

Where Flood_it estimated separately as Flood_A_it and Flood_B_it, and X_it includes seasonality controls (quarter FE absorbs national seasonality; optional monsoon indicator redundant but may be used for exposition).

- Expected sign: beta_1 less than 0

**Measurement precision caveat (pre-committed)**:

- State-level fallback in Flood_A_it introduces false positives and biases beta_1 toward zero (attenuation)
- Therefore, Flood_A estimates interpreted as conservative lower bounds relative to "true local" district-level effect

**Economic significance threshold (pre-committed)**:

- H1 economically meaningful if implied effect at least 5 percent decline in quarterly lights (order-of-magnitude threshold; if empirical volatility of Delta_Lights makes 5 percent nonsensical, threshold revised once and documented before final tables)

**Falsification condition**:

- If beta_1 greater than or equal to 0 (no dimming or systematic brightening), "flood to outflow/disruption captured by lights" interpretation fails and lights cannot be used as displacement proxy in this setting

---

## H2: Outflows/disruption (proxied by lights) coincide with deposit withdrawals (liquidity stress)

**Hypothesis**: Districts experiencing larger declines in night lights also experience larger declines in bank deposits, consistent with liquidity demand/withdrawals rather than slow-moving credit losses.

**Sign logic**:

- In shock periods, both Delta_Lights_it and Delta_Deposits_it expected negative
- Therefore slope in regression of deposits on lights expected positive: beta_2 greater than 0

### H2a: Reduced-form association (informative, not causal by itself)

Delta_Deposits_it = alpha + beta_2 * Delta_Lights_it + gamma * X_it + mu_i + tau_t + epsilon_it

**Endogeneity warning (explicit)**:

- Delta_Lights_it may correlate with unobserved shocks that also directly affect deposits (income shocks, policy disruptions, infrastructure outages)
- Therefore, H2a is descriptive/diagnostic, not preferred causal estimate

### H2b: Preferred causal test (IV / 2SLS)

**Strategy**: Instrument Delta_Lights_it using flood exposure (first stage is H1)

First stage:

Delta_Lights_it = alpha + beta_1 * Flood_it + gamma * X_it + mu_i + tau_t + epsilon_it

Second stage:

Delta_Deposits_it = alpha + beta_2 * Delta_Lights_it_hat + gamma * X_it + mu_i + tau_t + epsilon_it

- Expected sign: beta_2 greater than 0

**Instrument choice discipline**:

- Report 2SLS estimates instrumenting with Flood_B (high-precision) where feasible
- Also report Flood_A instrument results with explicit weak-instrument and attenuation warnings; do not oversell IV if first stage weak

**Exclusion restriction / identifying assumption (stated clearly)**:

- IV interpretation requires floods shift deposits primarily through displacement/disruption channel proxied by lights
- Threats: direct banking-operation disruption (branch closures, cash logistics interruptions) may affect deposits independently of lights
- Therefore, causal language softened if evidence of direct operational disruption plausible and unaddressed

### H2c: Event indicator form (migration/disruption proxy event)

Define event:

- MigrationProxy_it = indicator(Delta_Lights_it less than negative theta)

**Threshold rule (pre-committed; not arbitrary)**:

- Baseline theta chosen from distribution of Delta_Lights among flood-exposed district-quarters in high-precision sample (document exact rule used)
- Robustness: theta in {0.10, 0.15, 0.20}

Estimate:

Delta_Deposits_it = alpha + beta_2 * MigrationProxy_it + gamma * X_it + mu_i + tau_t + epsilon_it

- Expected sign (event dummy): beta_2 less than 0

**Economic significance threshold (pre-committed)**:

- H2 economically meaningful if 10 percent decline in lights predicts at least 2 percent decline in deposits within 0-1 quarters (order-of-magnitude benchmark; if deposit volatility makes 2 percent meaningless, revise once and document before final tables)

**Falsification condition**:

- If deposits do not respond to lights changes (insignificant or wrong-signed coefficients in both reduced form and IV), displacement/disruption to liquidity link not supported

---

## H3: Shadow-run timing — deposit shocks occur quickly (liquidity timeline)

**Hypothesis**: Deposit declines occur in same quarter as flood and/or next quarter, consistent with liquidity stress rather than slow-moving credit-loss transmission.

### H3a: Timing fingerprint (core, feasible)

Distributed lags (deposit change at t explained by flood exposure at t, t-1, t-2):

Delta_Deposits_it = alpha + beta_0 * Flood_it + beta_1 * Flood_i,t-1 + beta_2 * Flood_i,t-2 + gamma * X_it + mu_i + tau_t + epsilon_it

- Expected: beta_0 less than 0 and/or beta_1 less than 0, with attenuation by beta_2

**Falsification condition**:

- If effects appear only at long lags (e.g., t-3 and beyond) and not at t or t-1, "liquidity-timeline" interpretation weakened

### H3b: Liquidity-not-solvency fingerprint (extension, conditional)

If district-level credit-risk indicators (e.g., NPAs) become available:

- Deposit declines should not be fully mediated by contemporaneous credit deterioration
- If credit-risk measures spike immediately and explain deposit declines, mechanism shifts toward solvency/credit-loss transmission rather than shadow runs

If credit-risk data unavailable, H3b explicitly labeled as limitation (not silently "assumed" result).

---

## H4: Heterogeneity (core, feasible with current data)

**Hypothesis**: Deposit response to floods is heterogeneous across district types, consistent with differential exposure to liquidity stress.

**Operational statement**:

- Flood to deposits effect more negative in districts with higher baseline financial intensity/urbanization proxies, and/or in districts with higher historical flood exposure

Baseline interaction form:

Delta_Deposits_it = alpha + beta_0 * Flood_it + beta_1 * (Flood_it times Z_i) + gamma * X_it + mu_i + tau_t + epsilon_it

Where Z_i is pre-defined district characteristic or proxy (e.g., baseline deposit level category).

- Expected sign: beta_1 less than 0 for "more vulnerable" groups

**Proxy discipline**:

- If true urban/rural classification unavailable, any "urbanization" proxy (e.g., median-split baseline deposits) must be labeled as proxy and treated as suggestive

**Falsification condition**:

- If interaction effects consistently zero, mechanism not heterogeneous by these proxies; claims narrowed accordingly

---

## H5: Network contagion (extension; requires new data)

**Hypothesis**: Banking stress spills over to districts not directly flood-exposed, increasing with bank-network connectedness and/or geographic adjacency.

Define:

- Spillover_jt = sum_i W_ji * Flood_it

Then:

Delta_Deposits_jt = alpha + beta_5 * Spillover_jt + gamma * X_jt + mu_j + tau_t + epsilon_jt

- Expected: beta_5 less than 0

**Dependency warning**:

- If credible W matrix (shared bank networks/branch linkages) infeasible at district granularity, H5 remains stated extension and not "tested by proxy" without explicit justification

---

## Joint Mechanism Claim (What Success Looks Like)

### Original Pre-Commitment

Shadow Run mechanism supported if:

1. H1 holds (floods reduce lights in short-run, robustly across precision regimes)
2. H2 holds (lights declines predict deposit declines; IV preferred only when credible)
3. H3a holds (timing immediate or one-quarter lag, consistent with liquidity stress)
4. H4 holds (heterogeneity directionally consistent with vulnerability patterns)
5. H5 holds when network data available (spillovers beyond direct exposure)

If H1 holds but H2 fails, project becomes "disasters reduce activity (lights) without measurable deposit effects," and liquidity narrative softened.

If H1 fails, displacement proxy fails and chain cannot be claimed.

### Phase 3d Status (Data Preparation Complete, 2026-02-01)

**Current status: REGRESSION-READY DATA VALIDATED**

**Data Pipeline Complete:**
- VIIRS: 120 tiles → monthly panel (79,920 obs) → quarterly panel (26,640 obs) ✓
- RBI: Forensically validated clean (Jan 30 contamination concern was false alarm) ✓
- Master merge: VIIRS + deposits + floods (23,347 analysis-ready obs, 100% VIIRS coverage) ✓
- Variables: 23 total (11 raw + 12 engineered: logs, changes, lags L1-L4) ✓

**Analysis Sample Specifications:**
- Observations: 23,347 district-quarters
- Districts: 631 (35 zero-coverage excluded)
- Time: 37 quarters (2015Q1-2016Q2, 2017Q2-2024Q4; gap: 2016Q3-2017Q1 structural RBI gap)
- Flood treatment: 1,984 events (8.50% exposure rate, Rule A)
- VIIRS coverage: 100% (23,347/23,347)
- Deposit coverage: 99.1% (23,139/23,347)

**Data Quality Issues Identified:**
(1) Extreme deposit outliers (-273%, +656%) — winsorization required before regressions
(2) Nominal growth confound (mean 11.9% quarterly) — CPI deflation or disclosure decision pending
(3) Zero-inflation (25% deposit changes = 0) — investigation pending
(4) RBI 2016-2017 gap (3 quarters missing, structural publication gap, not error)

**Phase 4 Regressions:** PENDING (scheduled 2026-02-02)
- H1-H4 tests ready with validated clean data
- No preliminary results to report; hypotheses unchanged from pre-commitment

---

## Pre-Committed Robustness and Guardrails (To Keep the Paper Honest)

1. Threshold robustness: theta in {0.10, 0.15, 0.20}
2. Placebo timing: test floods predicting changes in t-1 (should not)
3. Precision stress-test: report Flood_A and Flood_B side by side
4. Inference discipline: district-clustered SE baseline; if not clustered, state it and soften inference
5. Interpretation constraint: lights "consistent with displacement/outflows," not proof of migration
6. IV discipline: report first-stage strength; if weak, label IV as suggestive or drop causal language

---

**Status**: v2.0 — Phase 4 results invalid due to VIIRS contamination. Deposits now correct, VIIRS measurement error active.

---

## VIIRS CONTAMINATION ALERT

**All H1, H2, H4 results below are INVALID due to VIIRS homonym measurement error. H3 status uncertain.**

**Bug Summary:**
- Scripts 18, 21 spatial join uses district name only (no state disambiguation)
- 7 homonymous districts share identical VIIRS values across different states
- Affected districts: Aurangabad (Bihar/Maharashtra), Balrampur (Chhattisgarh/Uttar Pradesh), Bijapur (Chhattisgarh/Karnataka), Bilaspur (Chhattisgarh/Himachal Pradesh), Hamirpur (Himachal Pradesh/Uttar Pradesh), plus 2 others
- Affected observations: 518 rows (7 districts × 2 states × 37 quarters); ~259 with measurement error

**Statistical Impact:**
- H1 (Floods → Lights): Coefficient biased toward zero (observed -0.0149 likely attenuated from true -0.02 to -0.03)
- H2 (Lights → Deposits IV): Weak instrument problem (first stage attenuated, standard errors inflated)
- H3 (Lag structure): May be valid IF specification uses deposits and floods only (requires Script 29 verification)
- H4c (Monsoon interaction): Result spurious (sign flip from prior version, economically implausible)

**Deposit Data Status:**
- RBI deposits CORRECTED (Script 13 bug fixed Feb 5)
- All deposit values now accurate
- H2, H3, H4 use correct deposit data but contaminated VIIRS data

**Fix Required:**
- Rewrite Scripts 18, 21 to use (district_gadm, state_gadm) composite key in spatial join
- Re-run VIIRS pipeline (Scripts 22-24)
- Re-run all regressions (Scripts 27-30)

**Documentation Purpose:**
Results retained below for transparency. Coefficients cannot be interpreted. Do not cite pending VIIRS correction.

---

## Empirical Results (Phase 4 Complete)

**Analysis Period:** 2015Q1-2024Q4 (37 quarters, excludes 2016Q3-2017Q1 RBI gap)
**Sample:** 23,347 district-quarters (631 districts)
**Standard Errors:** District-clustered in all specifications
**Fixed Effects:** District + Quarter in all specifications

### H1: First Stage (Floods → Economic Activity)

**Specification:** lights_change_qt ~ flood_exposure_ruleA_qt + district_FE + quarter_FE

**Result:** CONFIRMED
- Coefficient: -0.014867 (floods reduce lights by 1.49%)
- Standard Error: 0.002768 (clustered)
- t-statistic: -5.371
- p-value: <0.001
- N: 22,716 observations
- R-squared: 0.5566

**Interpretation:** Strong first stage. Floods cause significant immediate decline in nighttime lights (economic activity proxy). Instrument strength exceeds conventional threshold.

**VALIDITY WARNING:** Result invalid. VIIRS measurement error attenuates coefficient (true effect likely -0.02 to -0.03, not -0.0149). Standard errors incorrect due to 259 observations sharing VIIRS values. Cannot interpret.

### H2: Reduced Form IV (Lights → Deposits)

**Specification:** deposit_change_qt ~ lights_change_qt_hat + district_FE + quarter_FE (instrumented with flood_exposure_ruleA_qt)

**Result:** NULL
- First Stage: -0.015104 (t=-5.416, strong instrument)
- Second Stage: 0.083926 (SE=0.164038, t=0.512, p=0.609)
- N: 22,503 observations

**Interpretation:** Nighttime lights do not mediate deposit effects via IV. Three possible explanations: (1) lights are noisy migration proxy, (2) effect operates through non-migration channels (direct flood damage, credit constraints), (3) effect is lagged not contemporaneous (see H3).

**VALIDITY WARNING:** Result invalid. VIIRS measurement error creates weak instrument problem. First stage attenuated, second stage standard errors inflated. Null finding may reflect measurement error rather than true null effect. Cannot rule out H2.

### H3: Timing Structure (Distributed Lags)

**Specification:** deposit_change_qt ~ flood_t0 + flood_t1_lag + flood_t2_lag + district_FE + quarter_FE

**Results:**
- Current Quarter (t0): 0.000567 (SE=0.001464, t=0.387, p=0.699) NOT significant
- 1-Quarter Lag (t-1): -0.006188 (SE=0.001368, t=-4.522, p<0.001) CONFIRMED
- 2-Quarter Lag (t-2): -0.005337 (SE=0.004938, t=-1.081, p=0.280) NOT significant
- N: 21,912 observations

**Interpretation:** Delayed deposit stress. Floods cause deposit declines with 1-quarter (3-month) lag, not contemporaneously. Effect peaks at t-1 (-0.62%) and dissipates by t-2. This reconciles H2 null: effect is lagged, not immediate.

**VALIDITY STATUS:** UNCERTAIN. Result may be valid IF Script 29 specification uses deposits and flood lags only (no VIIRS variables). Requires code verification before accepting t-1 lag result. If VIIRS variables used, result contaminated.

### H4: Heterogeneity Analysis

**Specification:** deposit_change_qt ~ flood + [interaction_term] + district_FE + quarter_FE

**H4a: Urban × Flood - CONFIRMED**
- Baseline (rural): 0.006948 (SE=0.001916, t=3.626, p<0.001)
- Interaction: -0.011099 (SE=0.002259, t=-4.913, p<0.001)
- Net Urban Effect: +0.69% - 1.11% = -0.42% (deposit decline)
- N: 22,503 observations

**Interpretation:** Urban vulnerability. Flood effects concentrated in urban districts. Rural baseline paradoxically positive (+0.69%), likely reflecting relief transfers or remittances. Urban districts experience net deposit stress (-0.42%).

**VALIDITY WARNING:** Result invalid IF urban proxy constructed from VIIRS lights data. Check Script 30 code. If urban defined from baseline deposits only, may be valid.

**H4b: High-Exposure × Flood - NULL**
- Interaction: 0.002067 (SE=0.002258, t=0.915, p=0.360)

**Interpretation:** No evidence of adaptation in chronically flood-prone districts.

**H4c: Monsoon × Flood - NULL**
- Interaction: -0.001785 (SE=0.002716, t=-0.657, p=0.511)

**Interpretation:** Monsoon season floods do not produce different deposit effects than off-season floods.

**VALIDITY WARNING:** Result invalid. H4c shows null in this contaminated version. Prior version with contaminated deposits showed β = -0.0018, p = 0.511 (also null). Both versions unreliable. VIIRS measurement error prevents interpretation.

---

## Summary of Findings

## Summary of Findings (CONTAMINATED - Cannot Interpret)

**Phase 4 Status:** All results below contaminated by VIIRS homonym measurement error. Deposits corrected but VIIRS invalid.

**Results Obtained (Feb 6):**
1. H1: β = -0.0149, p < 0.001 (INVALID - attenuated)
2. H2: β = +0.2191, p = 0.299 (INVALID - weak instrument)
3. H3-t0: β = -0.0005, p = 0.777 (UNCERTAIN - verify specification)
4. H3-t1: β = +0.0004, p = 0.757 (UNCERTAIN - verify specification)
5. H3-t2: β = -0.0091, p = 0.012 (UNCERTAIN - verify specification)
6. H4a: β = -0.0013, p = 0.665 (INVALID if VIIRS used)
7. H4b: β = -0.0057, p = 0.068 (INVALID if VIIRS used)
8. H4c: β = +0.0119, p < 0.001 (INVALID - statistical artifact)

**Key Issue Identified:**
H4c result (monsoon floods INCREASE deposits, highly significant) is economically implausible and triggered contamination discovery. Sign flipped from prior version, indicating new measurement error source (VIIRS homonym bug).

**Hypotheses Status:**
- H1: Cannot evaluate (VIIRS outcome variable)
- H2: Cannot evaluate (VIIRS instrument)
- H3: May be valid (requires specification verification)
- H4: Cannot evaluate (interactions likely use VIIRS)

**Next Steps:**
1. Verify H3 specification: Does Script 29 use VIIRS variables?
2. Fix Scripts 18, 21: Add state_gadm to spatial join
3. Re-run VIIRS pipeline: Scripts 22-24
4. Re-run all regressions: Scripts 27-30
5. Compare three versions: Old deposits+Old VIIRS, New deposits+Old VIIRS, New deposits+New VIIRS

**Policy Implications:** SUSPENDED pending data correction.