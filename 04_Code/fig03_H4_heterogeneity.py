"""
fig03_H4_heterogeneity.py
Figure C -- H4 Heterogeneity Coefficient Plot
Flood Shocks and the Two-Phase Deposit Cycle: A Nighttime Lights Identification
Evidence from Night-Lights in India, 2015-2024

Data:   05_Outputs/Tables/05b_H4_linearmodels.csv  (Script 30b)
Output: 05_Outputs/Figures/Fig_03_H4_heterogeneity.png

Writing constraints enforced:
  Constraint  2: H4c exact language enforced in footnote.
  Constraint  3: Rule B labeled suggestive throughout (F=8.949 < 10).
  Constraint  5: Proxy labels only -- no census urban/rural language.
  Constraint 12: H4b hollow markers + dagger footnote. Winsorization
                 failure (p=0.865, Script 37) disclosed. Never robust.
"""

import os
import sys
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# ── 1. PATHS ─────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "05_Outputs", "Tables", "05b_H4_linearmodels.csv")
OUT_PATH  = os.path.join(BASE_DIR, "05_Outputs", "Figures", "Fig_03_H4_heterogeneity.png")
META_PATH = OUT_PATH + ".meta.json"

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

# ── 2. LOAD ───────────────────────────────────────────────────────────────────
if not os.path.exists(DATA_PATH):
    sys.exit(
        f"ERROR: File not found:\n  {DATA_PATH}\n"
        f"Confirm Script 30b has been executed and path is correct."
    )

df = pd.read_csv(DATA_PATH)

# ── 3. COLUMN MAP ─────────────────────────────────────────────────────────────
COL_SPEC  = "hypothesis"
COL_RULE  = "rule"
COL_COEF  = "interaction_coef"
COL_CI_LO = "interaction_ci_lower_95"
COL_CI_HI = "interaction_ci_upper_95"
COL_PVAL  = "interaction_p"

for col in [COL_SPEC, COL_RULE, COL_COEF, COL_CI_LO, COL_CI_HI, COL_PVAL]:
    if col not in df.columns:
        sys.exit(
            f"ERROR: Expected column '{col}' not found.\n"
            f"Available: {df.columns.tolist()}"
        )

# ── 4. ASSERTIONS ─────────────────────────────────────────────────────────────
assert len(df) == 6, (
    f"Expected 6 rows (3 specs x 2 rules). Got {len(df)}."
)
assert set(df[COL_SPEC].unique()) == {"H4a", "H4b", "H4c"}, (
    f"Unexpected hypothesis values: {df[COL_SPEC].unique()}"
)
assert set(df[COL_RULE].unique()) == {"A", "B"}, (
    f"Unexpected rule values: {df[COL_RULE].unique()}"
)
print("All assertions PASS.")

# ── 5. SIGNIFICANCE MARKERS ───────────────────────────────────────────────────
def sig_marker(p):
    if   p < 0.01: return "***"
    elif p < 0.05: return "**"
    elif p < 0.10: return "*"
    else:          return ""

df["sig"] = df[COL_PVAL].apply(sig_marker)

# ── 6. SPLIT BY RULE ──────────────────────────────────────────────────────────
ra = df[df[COL_RULE] == "A"].set_index(COL_SPEC)
rb = df[df[COL_RULE] == "B"].set_index(COL_SPEC)

specs = ["H4a", "H4b", "H4c"]

# Plotly uses <br> for tick label line breaks
spec_labels = [
    "H4a: Urban<br>Proxy",
    "H4b: High<br>Exposure \u2020",   # dagger: suggestive-only
    "H4c: Monsoon<br>Quarter"
]

# x positions: each group 1.0 apart; Rule A left, Rule B right
gap   = 0.20
x_a   = [0 - gap, 1 - gap, 2 - gap]
x_b   = [0 + gap, 1 + gap, 2 + gap]

# ── 7. COLORS AND MARKERS ─────────────────────────────────────────────────────
COLOR_A = "#1f77b4"   # blue  -- Rule A
COLOR_B = "#d62728"   # red   -- Rule B

# H4b = hollow (open) markers to signal suggestive-only (writing constraint 12)
def sym_a(spec): return "circle-open" if spec == "H4b" else "circle"
def sym_b(spec): return "square-open" if spec == "H4b" else "square"

# ── 8. BUILD FIGURE ───────────────────────────────────────────────────────────
pio.templates.default = "plotly_white"
fig = go.Figure()

# Reference line at zero
fig.add_hline(y=0, line_width=1.2, line_dash="dash", line_color="#444444")

# Rule A
for i, spec in enumerate(specs):
    row = ra.loc[spec]
    fig.add_trace(go.Scatter(
        x=[x_a[i]],
        y=[row[COL_COEF]],
        error_y=dict(
            type="data",
            symmetric=False,
            array=[row[COL_CI_HI] - row[COL_COEF]],
            arrayminus=[row[COL_COEF] - row[COL_CI_LO]],
            color=COLOR_A,
            thickness=2.0,
            width=7
        ),
        mode="markers+text",
        marker=dict(
            symbol=sym_a(spec),
            size=12,
            color=COLOR_A,
            line=dict(color=COLOR_A, width=2.2)
        ),
        text=[row["sig"]],
        textposition="top center",
        textfont=dict(size=12, color=COLOR_A),
        name="Rule A" if i == 0 else None,
        showlegend=(i == 0),
        legendgroup="ruleA"
    ))

# Rule B
for i, spec in enumerate(specs):
    row = rb.loc[spec]
    fig.add_trace(go.Scatter(
        x=[x_b[i]],
        y=[row[COL_COEF]],
        error_y=dict(
            type="data",
            symmetric=False,
            array=[row[COL_CI_HI] - row[COL_COEF]],
            arrayminus=[row[COL_COEF] - row[COL_CI_LO]],
            color=COLOR_B,
            thickness=2.0,
            width=7
        ),
        mode="markers+text",
        marker=dict(
            symbol=sym_b(spec),
            size=11,
            color=COLOR_B,
            line=dict(color=COLOR_B, width=2.2)
        ),
        text=[row["sig"]],
        textposition="top center",
        textfont=dict(size=12, color=COLOR_B),
        name="Rule B (suggestive, F<10)" if i == 0 else None,
        showlegend=(i == 0),
        legendgroup="ruleB"
    ))

# ── 9. LAYOUT ─────────────────────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text=(
            "H4 Heterogeneity: Flood Exposure and Deposit Response"
            "<br><span style='font-size:12px;font-weight:normal;color:#555;'>"
            "linearmodels PanelOLS | District + Quarter FE | 631 clusters | 95% CI"
            "<br>\u2020 H4b does not survive winsorization (p=0.865, Script 37) "
            "-- interpret as suggestive only"
            "</span>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=15)
    ),
    xaxis=dict(
        tickmode="array",
        tickvals=[0, 1, 2],
        ticktext=spec_labels,
        tickfont=dict(size=13),
        showgrid=False,
        zeroline=False,
        title_text="",
        range=[-0.6, 2.6]
    ),
    yaxis=dict(
        title_text="Coefficient",
        title_font=dict(size=13),
        tickfont=dict(size=12),
        showgrid=True,
        gridcolor="#ebebeb",
        zeroline=False
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.12,
        xanchor="center",
        x=0.5,
        font=dict(size=12)
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=130, b=90, l=75, r=40),
    width=850,
    height=540
)

fig.update_traces(cliponaxis=False)

# ── 10. SAVE ──────────────────────────────────────────────────────────────────
fig.write_image(OUT_PATH, scale=2)
print(f"\nSaved: {OUT_PATH}")

with open(META_PATH, "w") as f:
    json.dump({
        "caption": (
            "Figure C: H4 Heterogeneity -- Flood Exposure and Deposit Response. "
            "Rule A (circle, blue) and Rule B (square, red) side by side. "
            "Open/hollow markers on H4b indicate suggestive-only status "
            "(winsorization failure, Script 37, p=0.865)."
        ),
        "description": (
            "Coefficient plot for three heterogeneity interactions. "
            "H4a (urban proxy): null both rules. "
            "H4b (high exposure): Rule A p=0.020, Rule B p=0.080, "
            "demoted to suggestive -- does not survive winsorization. "
            "H4c (monsoon quarter): Rule A p<0.001 ***, Rule B null p=0.774. "
            "Data: 05b_H4_linearmodels.csv (Script 30b). "
            "Writing constraints 2, 3, 5, 12 enforced."
        )
    }, f, indent=2)
print(f"Saved: {META_PATH}")

# ── 11. POST-RUN VERIFICATION ─────────────────────────────────────────────────
print("\n── POST-RUN CHECKS ─────────────────────────────────────")
for spec in specs:
    for rule, tbl in [("A", ra), ("B", rb)]:
        row = tbl.loc[spec]
        print(
            f"  {spec} Rule {rule}: "
            f"beta={row[COL_COEF]:+.6f}  "
            f"CI=[{row[COL_CI_LO]:+.6f}, {row[COL_CI_HI]:+.6f}]  "
            f"p={row[COL_PVAL]:.6f}  sig='{row['sig']}'"
        )

print("\nFig_03 COMPLETE.")
print("Visual checks required before committing:")
print("  [ ] H4b markers are HOLLOW (open circle/square) on both rules.")
print("  [ ] H4a: both rules unmarked, CIs straddle zero.")
print("  [ ] H4b: Rule A marked **, Rule B marked *.")
print("  [ ] H4c: Rule A marked ***, Rule B unmarked.")
print("  [ ] Dagger footnote visible in subtitle.")
print("  [ ] Zero reference line visible.")