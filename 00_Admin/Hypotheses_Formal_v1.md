## FORMAL RESEARCH HYPOTHESES (v1.0 — Draft)  
**Project**: Climate Migration, Night Lights, and Bank Fragility in India (2015–2024)    
**Purpose**: Convert the “Shadow Run” narrative into testable, falsifiable statements that map cleanly to the Variables Codebook and tomorrow’s Python pipeline.  
  
***  
  
### 0) Notation and timing (so tests don’t drift)  
- District index $$i$$, quarter index $$t$$, month index $$m$$.    
- Flood shocks originate at daily resolution (EM‑DAT) and are mapped into quarter $$t$$.    
- Night lights are observed monthly (VIIRS) and will be aggregated to the quarter level to align with RBI deposits.    
- Key outcomes:    
  - $$ \Delta Deposits_{it} $$: quarterly log change in deposits (RBI).    
  - $$ \Delta Lights_{it} $$: quarterly change in log VIIRS brightness (constructed from monthly VIIRS).    
  - $$ Flood_{it} $$: indicator for flood exposure in district-quarter (EM‑DAT mapping).    
- A “shadow run” is defined as a sharp decline in deposits without evidence that the mechanism is credit deterioration (the stress is liquidity, not solvency).  
  
***  
  
## H1 — Floods trigger measurable outflows (VIIRS migration proxy)  
**Hypothesis (H1)**: Flood exposure produces a statistically and economically meaningful decline in night-time lights in affected districts in the immediate post-shock window, consistent with population displacement or disruption-driven outflows.  
  
**Operational statement**: For district $$i$$, after a flood in quarter $$t$$, the change in log VIIRS brightness in that same quarter or the next quarter is negative on average:    
- Expected sign: $$ \beta_1 < 0 $$  
  
**Primary test** (district and time fixed effects):    
$$  
\Delta Lights_{it} = \alpha + \beta_1 Flood_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}  
$$    
Where $$X_{it}$$ includes at minimum monsoon-quarter controls and (if available later) rainfall.  
  
**Falsification condition**: If $$ \beta_1 \ge 0 $$ (no dimming, or brightening), the interpretation “flood → outflow captured by lights” fails and lights cannot be used as the migration/displacement proxy in this setting.  
  
**Interpretation discipline**: H1 does not claim “people moved” with certainty; it claims floods create a measurable luminosity shock consistent with outflows/disruption, which becomes a usable empirical proxy if it is systematic, directional, and temporally aligned.  
  
***  
  
## H2 — Outflows (proxied by lights) coincide with deposit withdrawals (liquidity shock)  
**Hypothesis (H2)**: Districts experiencing larger declines in night lights also experience larger declines in bank deposits, consistent with migration-induced liquidity demand (withdrawals) rather than slow-moving credit losses.  
  
**Operational statement**: $$ \Delta Deposits_{it} $$ co-moves positively with $$ \Delta Lights_{it} $$ because both become negative during outflow episodes. In other words, as lights fall, deposits fall.    
- Expected sign: $$ \beta_2 > 0 $$ (since both changes are negative in shock periods)  
  
**Primary test**:    
$$  
\Delta Deposits_{it} = \alpha + \beta_2 \Delta Lights_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}  
$$  
  
**Secondary test (event indicator form)**: Define a migration proxy event $$ MigrationProxy_{it} = 1[\Delta Lights_{it} < -\theta] $$ (baseline $$\theta = 0.15$$). Then test:    
$$  
\Delta Deposits_{it} = \alpha + \beta_2 MigrationProxy_{it} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}  
$$    
- Expected sign: $$ \beta_2 < 0 $$ (because the regressor is an event dummy)  
  
**Falsification condition**: If deposits do not respond to lights changes (insignificant or wrong-signed coefficients), the “migration → liquidity” link is not supported. That would force a redesign: either deposits are not the right banking stress channel, or lights are not capturing migration-like shocks.  
  
***  
  
## H3 — The “shadow run” signature: deposit shocks occur on a liquidity timeline, not a credit-loss timeline  
**Hypothesis (H3)**: The deposit response is immediate (same quarter or next quarter) and is not primarily explained by slow-moving credit deterioration.  
  
This is a mechanism statement, so it has two empirical fingerprints:  
  
### H3a (Timing fingerprint)  
Deposit withdrawals occur quickly relative to flood timing.    
- Expected pattern: strongest effects in $$t$$ and $$t+1$$, attenuating afterward.  
  
**Test (distributed lags)**:    
$$  
\Delta Deposits_{it} = \alpha + \beta_0 Flood_{it} + \beta_1 Flood_{i,t-1} + \beta_2 Flood_{i,t-2} + \gamma X_{it} + \mu_i + \tau_t + \varepsilon_{it}  
$$    
- Expected: $$\beta_0$$ and/or $$\beta_1 < 0$$, and effects weaken for longer lags.  
  
### H3b (Liquidity-not-solvency fingerprint)  
Where credit-risk indicators exist (later, if we obtain them), deposit withdrawals should not be fully explained by contemporaneous increases in credit distress.    
- Expected: deposit effects persist even after controlling for credit-risk proxies; and/or credit-risk proxies do not spike immediately in the same window as deposits.  
  
**Falsification condition**: If the deposit declines appear only with long lags (e.g., $$t+3$$ or later), or if they are fully mediated by credit-risk deterioration, the phenomenon is no longer a “shadow run” in the sense we mean—it becomes standard credit-loss transmission after disasters.  
  
**Practical note**: If district-level NPAs are unavailable, we still retain H3a (timing) as the core shadow-run signature and explicitly label the credit-risk separation as a limitation rather than pretending we tested it.  
  
***  
  
## H4 — Contagion: shocks propagate through banking networks beyond the flood footprint  
**Hypothesis (H4)**: Banking stress spills over to districts that are not directly flood-exposed, with intensity increasing in bank-network connectedness (shared bank presence, shared branch networks) and/or geographic adjacency.  
  
**Operational statement**: Deposits decline in district $$j$$ when it is connected to flood-exposed districts $$i$$, even if $$Flood_{jt}=0$$.    
- Expected sign: connectedness spillover coefficient $$< 0$$  
  
**Primary test concept (network spillover)**:    
Let $$ Spillover_{jt} = \sum_i W_{ji} Flood_{it} $$, where $$W_{ji}$$ captures connectedness (shared banks, or adjacency). Then:    
$$  
\Delta Deposits_{jt} = \alpha + \beta_4 Spillover_{jt} + \gamma X_{jt} + \mu_j + \tau_t + \varepsilon_{jt}  
$$    
- Expected: $$ \beta_4 < 0 $$  
  
**Falsification condition**: If spillovers are zero after controlling for time fixed effects and location fixed effects, then the mechanism is localized. That is not a failure of the paper, but it narrows the claim to “local shadow runs,” not “systemic propagation.”  
  
**Dependency warning**: H4 requires network variables we may or may not have at district granularity. If network data are infeasible, H4 becomes an explicit “extension” rather than a core claim.  
  
***  
  
## Joint mechanism claim (what “success” looks like)  
The Shadow Run mechanism is supported if:  
1. **H1 holds** (floods reliably shift lights downward in the short-run), and    
2. **H2 holds** (lights declines predict deposit declines), and    
3. **H3a holds** (timing is immediate, consistent with liquidity stress), and    
4. **H4 holds** *when network data are available* (spillovers exist beyond direct exposure).  
  
If H1 and H2 hold but H3a fails, the chain becomes “disasters affect local economies and later deposits,” which is a different story and must be written as such. If H1 fails, the empirical migration proxy must be redesigned before proceeding.  
  
***  
  
## Pre-committed robustness and “anti-hallucination” checks (to keep the paper honest)  
These are not decorative. They are guardrails against overclaiming.  
  
1. **Threshold robustness**: Re-estimate $$MigrationProxy_{it}$$ under $$\theta \in \{0.10, 0.15, 0.20\}$$.    
2. **Placebo timing**: Test for pre-trends by checking whether floods “predict” lights/deposit changes in $$t-1$$ (they should not).    
3. **Seasonality controls**: Always include quarter fixed effects (or monsoon indicator) so agricultural cycles don’t masquerade as migration.    
4. **Geographic precision stress-test**: If EM‑DAT is state-level, run a stricter version using only events with explicit district mentions (even if sample shrinks).    
5. **Interpretation constraint**: Throughout, refer to lights as a “proxy consistent with displacement/outflows,” not proof of migration, unless corroborated by an external migration dataset later.  
