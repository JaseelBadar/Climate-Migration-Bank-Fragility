#!/usr/bin/env python3
"""
fig02_H3_event_study.py
=======================
Figure 2: Two-Phase Household Liquidity Cycle -- H3 Distributed Lag (Rule A)

Four-point event-study plot showing flood exposure coefficients on quarterly
deposit growth across event time. Pre-period estimate (x = -1) from placebo
test (Script 34, 09_placebo_timing.csv). H3 lag estimates (x = 0, +1, +2)
from linearmodels PanelOLS (Script 29b, 04b_H3_linearmodels.csv).

Outputs
-------
  05_Outputs/Figures/Fig_02_H3_event_study.pdf   (vector, for LaTeX)
  05_Outputs/Figures/Fig_02_H3_event_study.png   (300 DPI, for review)

Run from base directory:
  cd E:\Climate-Migration-Bank-Fragility
  python 04_Code/fig02_H3_event_study.py

Dependencies: matplotlib, pandas, numpy
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.ticker
matplotlib.rcParams.update({
    'font.family':        'serif',
    'font.serif':         ['Times New Roman', 'Palatino Linotype', 'DejaVu Serif'],
    'font.size':          9,
    'axes.labelsize':     9,
    'axes.titlesize':     10,
    'xtick.labelsize':    8.5,
    'ytick.labelsize':    8.5,
    'legend.fontsize':    8,
    'figure.dpi':         300,
    'savefig.dpi':        300,
    'savefig.bbox':       'tight',
    'savefig.pad_inches': 0.05,
    'text.usetex':        False,   # Set True if LaTeX (pdflatex) is in PATH
    'pdf.fonttype':       42,      # Embeds fonts -- required by most journals
    'ps.fonttype':        42,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'axes.linewidth':     0.7,
    'xtick.major.width':  0.7,
    'ytick.major.width':  0.7,
    'xtick.major.size':   3.5,
    'ytick.major.size':   3.5,
})
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR    = r"E:\Climate-Migration-Bank-Fragility"
H3_CSV      = os.path.join(BASE_DIR, "05_Outputs", "Tables", "04b_H3_linearmodels.csv")
PLACEBO_CSV = os.path.join(BASE_DIR, "05_Outputs", "Tables", "09_placebo_timing.csv")
OUT_DIR     = os.path.join(BASE_DIR, "05_Outputs", "Figures")
os.makedirs(OUT_DIR, exist_ok=True)

# Locked values (Scripts 29b and 34) -- used for assertion only, never plotted directly
LOCKED = {
    'pre': {'beta':  0.004664, 'se': 0.001841, 'p': 0.011298,
            'ci_lo': 0.001056, 'ci_hi': 0.008273},
    'L0':  {'beta':  0.000609, 'se': 0.001462, 'p': 0.677000},
    'L1':  {'beta':  0.001505, 'se': 0.001114, 'p': 0.177000},
    'L2':  {'beta': -0.007005, 'se': 0.001644, 'p': 0.000100},
}
ASSERT_TOL = 0.00005   # tolerance for floating-point comparison

# Design colors (print-safe, colorblind-safe -- no red/green pairing)
COLOR_PRE  = '#8b1a1a'   # dark crimson  -- pre-period (placebo)
COLOR_H3   = '#1a3d6b'   # dark navy     -- H3 distributed lag
COLOR_ZERO = '#555555'   # zero reference line
COLOR_SEP  = '#999999'   # vertical separator

print("=" * 70)
print("SCRIPT: fig02_H3_event_study.py")
print("Figure 2: H3 Two-Phase Household Liquidity Cycle")
print("=" * 70)

# ==============================================================================
# [1/4] LOAD PLACEBO DATA (pre-period estimate)
# ==============================================================================
print("\n[1/4] Loading placebo timing data (09_placebo_timing.csv)...")
assert os.path.isfile(PLACEBO_CSV), f"File not found: {PLACEBO_CSV}"

placebo_df = pd.read_csv(PLACEBO_CSV)
print(f"  Shape: {placebo_df.shape}")
print(f"  Columns: {list(placebo_df.columns)}")

# Select: Test2_PreTrend, Rule A
pre_row = placebo_df[
    (placebo_df['test'].str.strip() == 'Test2_PreTrend') &
    (placebo_df['rule'].astype(str).str.strip().str.upper() == 'A')
]
assert len(pre_row) == 1, (
    f"Expected exactly 1 row for Test2_PreTrend Rule A. Got {len(pre_row)}.\n"
    f"Available tests: {placebo_df['test'].unique()}\n"
    f"Available rules: {placebo_df['rule'].unique()}"
)
pre = pre_row.iloc[0]

pre_beta  = float(pre['coefficient'])
pre_se    = float(pre['std_error'])
pre_p     = float(pre['p_value'])
pre_ci_lo = float(pre['ci_lower_95'])
pre_ci_hi = float(pre['ci_upper_95'])

print(f"  Pre-period: beta={pre_beta:+.6f} | se={pre_se:.6f} | p={pre_p:.6f}")
print(f"  95% CI: [{pre_ci_lo:+.6f}, {pre_ci_hi:+.6f}]")

# Assert against locked values
assert abs(pre_beta  - LOCKED['pre']['beta'])  < ASSERT_TOL,  f"pre beta mismatch: {pre_beta}"
assert abs(pre_se    - LOCKED['pre']['se'])    < ASSERT_TOL,  f"pre se mismatch: {pre_se}"
assert abs(pre_p     - LOCKED['pre']['p'])     < 0.0002,       f"pre p mismatch: {pre_p}"
assert abs(pre_ci_lo - LOCKED['pre']['ci_lo']) < ASSERT_TOL,  f"pre ci_lo mismatch: {pre_ci_lo}"
assert abs(pre_ci_hi - LOCKED['pre']['ci_hi']) < ASSERT_TOL,  f"pre ci_hi mismatch: {pre_ci_hi}"
print(f"  All locked value assertions -- PASS")

# ==============================================================================
# [2/4] LOAD H3 DISTRIBUTED LAG DATA (04b_H3_linearmodels.csv)
# ==============================================================================
print("\n[2/4] Loading H3 linearmodels results (04b_H3_linearmodels.csv)...")
assert os.path.isfile(H3_CSV), f"File not found: {H3_CSV}"

h3_df = pd.read_csv(H3_CSV)
print(f"  Shape: {h3_df.shape}")
print(f"  Columns: {list(h3_df.columns)}")

# -- Detect rule column
rule_col = next(
    (c for c in ['rule', 'Rule', 'spec', 'Spec'] if c in h3_df.columns), None
)
assert rule_col, f"Rule column not found. Available: {list(h3_df.columns)}"

# -- Filter to Rule A
h3_ruleA = h3_df[h3_df[rule_col].astype(str).str.strip().str.upper() == 'A'].copy()
assert len(h3_ruleA) >= 3, (
    f"Expected >= 3 Rule A rows (t0, t-1, t-2). Got {len(h3_ruleA)}.\n"
    f"Rule values in CSV: {h3_df[rule_col].unique()}"
)
print(f"  Rule A rows: {len(h3_ruleA)}")

# -- Detect beta/coefficient column
beta_col = next(
    (c for c in ['beta', 'coefficient', 'coef', 'estimate', 'Coefficient']
     if c in h3_ruleA.columns), None
)
assert beta_col, f"Coefficient column not found. Available: {list(h3_ruleA.columns)}"

# -- Detect SE column
se_col = next(
    (c for c in ['se', 'std_error', 'SE', 'std_err', 'stderr', 'standard_error']
     if c in h3_ruleA.columns), None
)
assert se_col, f"SE column not found. Available: {list(h3_ruleA.columns)}"

# -- Detect p-value column
p_col = next(
    (c for c in ['p_value', 'p', 'pvalue', 'P', 'prob', 'p_val']
     if c in h3_ruleA.columns), None
)
assert p_col, f"P-value column not found. Available: {list(h3_ruleA.columns)}"

# -- Detect CI columns (optional -- computed from SE if absent)
ci_lo_col = next(
    (c for c in ['ci_lower_95', 'ci_lo', 'ci_lower', 'lower_95', 'lb']
     if c in h3_ruleA.columns), None
)
ci_hi_col = next(
    (c for c in ['ci_upper_95', 'ci_hi', 'ci_upper', 'upper_95', 'ub']
     if c in h3_ruleA.columns), None
)

print(f"  beta col: '{beta_col}' | se col: '{se_col}' | p col: '{p_col}'")
print(f"  CI cols: lo='{ci_lo_col}' hi='{ci_hi_col}'")

# -- Match rows to L0/L1/L2 by proximity to locked beta values
h3_ruleA  = h3_ruleA.reset_index(drop=True)
h3_betas  = h3_ruleA[beta_col].astype(float).values
locked_b  = [LOCKED['L0']['beta'], LOCKED['L1']['beta'], LOCKED['L2']['beta']]
matched   = {}
used_idx  = set()

for lag_key, lb in zip(['L0', 'L1', 'L2'], locked_b):
    avail_idx  = [i for i in range(len(h3_betas)) if i not in used_idx]
    avail_beta = [h3_betas[i] for i in avail_idx]
    best       = avail_idx[int(np.argmin([abs(b - lb) for b in avail_beta]))]
    matched[lag_key] = best
    used_idx.add(best)

# -- Extract, assert, store
h3_data = {}
for lag_key in ['L0', 'L1', 'L2']:
    idx  = matched[lag_key]
    row  = h3_ruleA.iloc[idx]
    beta = float(row[beta_col])
    se   = float(row[se_col])
    p    = float(row[p_col])

    if ci_lo_col and ci_hi_col:
        ci_lo = float(row[ci_lo_col])
        ci_hi = float(row[ci_hi_col])
    else:
        ci_lo = beta - 1.96 * se
        ci_hi = beta + 1.96 * se

    h3_data[lag_key] = {'beta': beta, 'se': se, 'p': p,
                        'ci_lo': ci_lo, 'ci_hi': ci_hi}

    print(f"  {lag_key}: beta={beta:+.6f} | se={se:.6f} | p={p:.6f}")

    assert abs(beta - LOCKED[lag_key]['beta']) < ASSERT_TOL, (
        f"{lag_key} beta mismatch: got {beta:.6f}, expected {LOCKED[lag_key]['beta']:.6f}"
    )
    assert abs(se - LOCKED[lag_key]['se']) < ASSERT_TOL, (
        f"{lag_key} se mismatch: got {se:.6f}, expected {LOCKED[lag_key]['se']:.6f}"
    )

print(f"  All locked value assertions -- PASS")

# ==============================================================================
# [3/4] ASSEMBLE PLOT DATA
# ==============================================================================
print("\n[3/4] Assembling plot data...")

# Event-time x-coordinates:
#   x = -1 : pre-period (one quarter BEFORE flood, from placebo regression)
#   x =  0 : flood quarter -- contemporaneous (H3 L0)
#   x = +1 : one quarter AFTER flood (H3 L1)
#   x = +2 : two quarters AFTER flood (H3 L2)

plot_data = [
    {
        'x':      -1,
        'beta':    pre_beta,
        'ci_lo':   pre_ci_lo,
        'ci_hi':   pre_ci_hi,
        'p':       pre_p,
        'source':  'placebo',
        'xtick':   'Pre-period\n(t \u2212 1)\u2020',
    },
    {
        'x':      0,
        'beta':    h3_data['L0']['beta'],
        'ci_lo':   h3_data['L0']['ci_lo'],
        'ci_hi':   h3_data['L0']['ci_hi'],
        'p':       h3_data['L0']['p'],
        'source':  'h3',
        'xtick':   'Flood quarter\n(t\u2080)\u2021',
    },
    {
        'x':      1,
        'beta':    h3_data['L1']['beta'],
        'ci_lo':   h3_data['L1']['ci_lo'],
        'ci_hi':   h3_data['L1']['ci_hi'],
        'p':       h3_data['L1']['p'],
        'source':  'h3',
        'xtick':   'One quarter\nafter (t\u2080+1)\u2021',
    },
    {
        'x':      2,
        'beta':    h3_data['L2']['beta'],
        'ci_lo':   h3_data['L2']['ci_lo'],
        'ci_hi':   h3_data['L2']['ci_hi'],
        'p':       h3_data['L2']['p'],
        'source':  'h3',
        'xtick':   'Two quarters\nafter (t\u2080+2)\u2021',
    },
]

for d in plot_data:
    d['sig'] = ('***' if d['p'] < 0.001 else
                '**'  if d['p'] < 0.01  else
                '*'   if d['p'] < 0.05  else
                '\u2020'  if d['p'] < 0.10  else '')
    print(f"  x={d['x']:+d}: beta={d['beta']:+.4f} | "
          f"CI [{d['ci_lo']:+.4f}, {d['ci_hi']:+.4f}] | "
          f"p={d['p']:.4f} {d['sig']}")

# ==============================================================================
# [4/4] RENDER FIGURE
# ==============================================================================
print("\n[4/4] Rendering figure...")

fig, ax = plt.subplots(figsize=(6.0, 4.2))

# ── Zero reference line ────────────────────────────────────────────────────────
ax.axhline(0, color=COLOR_ZERO, linewidth=0.8, linestyle='--',
           dashes=(4, 3), zorder=1)

# ── Vertical separator: pre-period vs H3 specification ────────────────────────
ax.axvline(-0.5, color=COLOR_SEP, linewidth=0.6, linestyle=':',
           dashes=(2, 3), zorder=1, alpha=0.8)

# ── Null window shading (t0 and t+1, both near zero) ─────────────────────────
ax.axvspan(-0.45, 1.45, color='#f0f0f0', alpha=0.45, zorder=0)

# ── CI bars ───────────────────────────────────────────────────────────────────
CAP_W = 0.055   # half-width of CI cap ticks

for d in plot_data:
    col = COLOR_PRE if d['source'] == 'placebo' else COLOR_H3
    ax.plot([d['x'], d['x']], [d['ci_lo'], d['ci_hi']],
            color=col, linewidth=1.1, zorder=3, solid_capstyle='butt')
    ax.plot([d['x'] - CAP_W, d['x'] + CAP_W], [d['ci_lo'], d['ci_lo']],
            color=col, linewidth=1.1, zorder=3)
    ax.plot([d['x'] - CAP_W, d['x'] + CAP_W], [d['ci_hi'], d['ci_hi']],
            color=col, linewidth=1.1, zorder=3)

# ── H3 connecting line (x=0,1,2 only -- same specification) ──────────────────
h3_x = [d['x'] for d in plot_data if d['source'] == 'h3']
h3_y = [d['beta'] for d in plot_data if d['source'] == 'h3']
ax.plot(h3_x, h3_y, color=COLOR_H3, linewidth=1.0,
        linestyle='-', zorder=4, alpha=0.6)

# ── Data points ───────────────────────────────────────────────────────────────
for d in plot_data:
    if d['source'] == 'placebo':
        ax.scatter(d['x'], d['beta'], marker='D', s=52,
                   color=COLOR_PRE, edgecolors='white',
                   linewidths=0.8, zorder=5)
    else:
        ax.scatter(d['x'], d['beta'], marker='o', s=46,
                   color=COLOR_H3, edgecolors='white',
                   linewidths=0.8, zorder=5)

# ── Significance labels above CI bars ─────────────────────────────────────────
for d in plot_data:
    if d['sig']:
        ax.text(d['x'], d['ci_hi'] + 0.00045,
                d['sig'],
                ha='center', va='bottom', fontsize=8.5,
                color=COLOR_PRE if d['source'] == 'placebo' else COLOR_H3,
                fontweight='bold')

# ── Phase 1 annotation (pre-period) ───────────────────────────────────────────
ax.annotate(
    'Phase 1\nAnticipatory\nsaving',
    xy=(-1, pre_beta),
    xytext=(-1.48, 0.0068),
    fontsize=7.0, color=COLOR_PRE, ha='center',
    arrowprops=dict(arrowstyle='->', color=COLOR_PRE,
                    lw=0.8, connectionstyle='arc3,rad=0.1'),
    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
              edgecolor=COLOR_PRE, linewidth=0.5, alpha=0.92),
)

# ── Phase 2 annotation (t+2 withdrawal) ───────────────────────────────────────
ax.annotate(
    'Phase 2\nPost-flood\nwithdrawal',
    xy=(2, h3_data['L2']['beta']),
    xytext=(2.48, -0.0025),
    fontsize=7.0, color=COLOR_H3, ha='center',
    arrowprops=dict(arrowstyle='->', color=COLOR_H3,
                    lw=0.8, connectionstyle='arc3,rad=-0.1'),
    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
              edgecolor=COLOR_H3, linewidth=0.5, alpha=0.92),
)

# ── Axes ──────────────────────────────────────────────────────────────────────
ax.set_xlim(-1.90, 2.90)

all_ci_lo = [d['ci_lo'] for d in plot_data]
all_ci_hi = [d['ci_hi'] for d in plot_data]
y_margin  = 0.0030
ax.set_ylim(min(all_ci_lo) - y_margin,
            max(all_ci_hi) + y_margin * 3)

ax.set_xticks([-1, 0, 1, 2])
ax.set_xticklabels([d['xtick'] for d in plot_data], fontsize=8.0)

ax.yaxis.set_major_formatter(
    matplotlib.ticker.FuncFormatter(lambda x, _: f'{x:+.3f}')
)

ax.set_xlabel('Event time (quarters relative to flood)',
              fontsize=9, labelpad=8)
ax.set_ylabel('Coefficient on flood exposure\n(deposit growth, Rule A)',
              fontsize=9, labelpad=6)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    mlines.Line2D([], [], color=COLOR_PRE, marker='D', markersize=5.5,
                  linewidth=0, markeredgecolor='white', markeredgewidth=0.6,
                  label='\u2020 Pre-period (placebo test, Script 34)'),
    mlines.Line2D([], [], color=COLOR_H3, marker='o', markersize=5,
                  linewidth=1.0, markeredgecolor='white', markeredgewidth=0.6,
                  label='\u2021 H3 distributed lag (Script 29b)'),
]
ax.legend(handles=legend_handles, loc='lower left', fontsize=7.5,
          frameon=True, framealpha=0.92, edgecolor='#bbbbbb',
          borderpad=0.6, handletextpad=0.5)

# ── Bottom note ───────────────────────────────────────────────────────────────
fig.text(
    0.01, 0.005,
    '*** p\u2009<\u20090.001\u2003** p\u2009<\u20090.01\u2003'
    '* p\u2009<\u20090.05\u2003\u2020 p\u2009<\u20090.10\u2003|\u2003'
    '95% confidence intervals shown. '
    'Pre-period estimate: flood at t predicts deposit change at t\u22121 '
    '(placebo causal impossibility test). '
    'H3 estimates: linearmodels PanelOLS, quarter FE only, '
    'SE clustered by district (N\u2009=\u200921,837).',
    fontsize=5.8, color='#3c3c3c', linespacing=1.5,
    ha='left', va='bottom', transform=fig.transFigure,
)

plt.tight_layout(rect=[0, 0.06, 1, 1])

# ==============================================================================
# SAVE
# ==============================================================================
print("\n  Saving outputs...")
out_pdf = os.path.join(OUT_DIR, "Fig_02_H3_event_study.pdf")
out_png = os.path.join(OUT_DIR, "Fig_02_H3_event_study.png")

fig.savefig(out_pdf, format='pdf', bbox_inches='tight')
print(f"  PDF saved: {out_pdf} -- PASS")

fig.savefig(out_png, format='png', dpi=300, bbox_inches='tight')
print(f"  PNG saved: {out_png} -- PASS")

plt.close()

print("\n" + "=" * 70)
print("FIGURE 2 COMPLETE -- fig02_H3_event_study.py")
print("=" * 70)