#!/usr/bin/env python3
"""
fig01_flood_exposure_map.py
===========================
Figure 1: India District Flood Exposure Map (Rule A, 2015-2024)

Outputs
-------
  05_Outputs/Figures/Fig_01_flood_exposure_map.pdf   (vector, for LaTeX)
  05_Outputs/Figures/Fig_01_flood_exposure_map.png   (300 DPI, for review)

Run from base directory:
  cd E:\Climate-Migration-Bank-Fragility
  python 04_Code/fig01_flood_exposure_map.py

Dependencies: geopandas, matplotlib, pandas, numpy, shapely
  conda install -c conda-forge geopandas
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd

try:
    import geopandas as gpd
except ImportError:
    sys.exit(
        "ERROR: geopandas not installed.\n"
        "Fix: conda install -c conda-forge geopandas"
    )

import matplotlib
matplotlib.rcParams.update({
    'font.family':        'serif',
    'font.serif':         ['Times New Roman', 'Palatino Linotype', 'DejaVu Serif'],
    'font.size':          9,
    'axes.titlesize':     10,
    'legend.fontsize':    8,
    'figure.dpi':         300,
    'savefig.dpi':        300,
    'savefig.bbox':       'tight',
    'savefig.pad_inches': 0.05,
    'text.usetex':        False,   # Set True if LaTeX (pdflatex) is in PATH
    'pdf.fonttype':       42,      # Embeds fonts in PDF -- required by most journals
    'ps.fonttype':        42,
})
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.colorbar import ColorbarBase

# ==============================================================================
# CONFIGURATION -- edit BASE_DIR if running from a different machine
# ==============================================================================
BASE_DIR  = r"E:\Climate-Migration-Bank-Fragility"
FLOOD_CSV = os.path.join(BASE_DIR, "02_Data_Intermediate", "flood_exposure_panel.csv")
SHP_PATH  = os.path.join(BASE_DIR, "01_Data_Raw", "District_Boundaries", "gadm41_IND_2.shp")
OUT_DIR   = os.path.join(BASE_DIR, "05_Outputs", "Figures")
os.makedirs(OUT_DIR, exist_ok=True)

LOCKED_N_DISTRICTS = 666
LOCKED_H4b_MEDIAN  = 3.0     # median cum floods Rule A (from H4b setup, Script 30b)
ASSERT_TOLERANCE   = 0.5     # tolerance on median assertion

print("=" * 70)
print("SCRIPT: fig01_flood_exposure_map.py")
print("Figure 1: India District Flood Exposure Map")
print("=" * 70)

# ==============================================================================
# [1/6] LOAD FLOOD PANEL
# ==============================================================================
print("\n[1/6] Loading flood exposure panel...")
assert os.path.isfile(FLOOD_CSV), f"File not found: {FLOOD_CSV}"
flood = pd.read_csv(FLOOD_CSV, low_memory=False)
print(f"  Shape: {flood.shape}")
print(f"  Columns: {list(flood.columns)}")

# -- Detect Rule A flood exposure column
ruleA_col = next(
    (c for c in [
        'flood_exposure_ruleA_qt', 'flood_ruleA_qt', 'flood_ruleA',
        'ruleA_qt', 'ruleA'
    ] if c in flood.columns), None
)
assert ruleA_col is not None, (
    f"Rule A column not found. Available columns: {list(flood.columns)}\n"
    "Expected: flood_exposure_ruleA_qt"
)

# -- Detect district identifier column
dist_col = next(
    (c for c in [
        'district_gadm', 'district_name_gadm', 'name_2_gadm', 'district'
    ] if c in flood.columns), None
)
assert dist_col is not None, (
    f"District column not found. Available: {list(flood.columns)}"
)

# -- Detect state identifier column
state_col = next(
    (c for c in [
        'state_gadm', 'state_name_gadm', 'name_1_gadm', 'state'
    ] if c in flood.columns), None
)
assert state_col is not None, (
    f"State column not found. Available: {list(flood.columns)}"
)

print(f"  Rule A column  : '{ruleA_col}'")
print(f"  District column: '{dist_col}'")
print(f"  State column   : '{state_col}'")
print(f"  Rule A dtype   : {flood[ruleA_col].dtype}")
print(f"  Rule A range   : [{flood[ruleA_col].min()}, {flood[ruleA_col].max()}]")

# -- Aggregate to district level: cumulative count of flood-exposed quarters
district_flood = (
    flood
    .groupby([dist_col, state_col])[ruleA_col]
    .sum()
    .reset_index()
    .rename(columns={
        ruleA_col: 'cum_flood_ruleA',
        dist_col:  'district_gadm',
        state_col: 'state_gadm',
    })
)

# Composite merge key -- handles 7 homonymous district pairs correctly
district_flood['merge_key'] = (
    district_flood['district_gadm'].str.strip().str.lower() + '||' +
    district_flood['state_gadm'].str.strip().str.lower()
)

n_dist     = len(district_flood)
med_floods = district_flood['cum_flood_ruleA'].median()
max_floods = district_flood['cum_flood_ruleA'].max()

print(f"\n  Districts aggregated  : {n_dist}")
print(f"  Cumulative floods -- max: {max_floods:.0f} | median: {med_floods:.1f}")

# -- Assertions against locked values
assert abs(n_dist - LOCKED_N_DISTRICTS) <= 5, (
    f"District count {n_dist} deviates from locked {LOCKED_N_DISTRICTS}"
)
print(f"  District count assertion ({n_dist} ~ {LOCKED_N_DISTRICTS}) -- PASS")

assert abs(med_floods - LOCKED_H4b_MEDIAN) <= ASSERT_TOLERANCE, (
    f"Median floods {med_floods:.1f} deviates from locked H4b median "
    f"{LOCKED_H4b_MEDIAN} (tolerance {ASSERT_TOLERANCE})"
)
print(f"  Median assertion ({med_floods:.1f} ~ {LOCKED_H4b_MEDIAN}) -- PASS")

# ==============================================================================
# [2/6] LOAD GADM SHAPEFILE
# ==============================================================================
print("\n[2/6] Loading GADM district shapefile...")
assert os.path.isfile(SHP_PATH), f"Shapefile not found: {SHP_PATH}"
gdf = gpd.read_file(SHP_PATH)
print(f"  Features: {len(gdf)} | CRS: {gdf.crs}")

if gdf.crs is None or str(gdf.crs).find('4326') == -1:
    gdf = gdf.to_crs(epsg=4326)
    print("  Reprojected to EPSG:4326 -- PASS")
else:
    print("  CRS is EPSG:4326 -- PASS")

assert 'NAME_2' in gdf.columns and 'NAME_1' in gdf.columns, (
    f"Expected NAME_1 and NAME_2 in GADM. Got: {list(gdf.columns)}"
)

gdf['merge_key'] = (
    gdf['NAME_2'].str.strip().str.lower() + '||' +
    gdf['NAME_1'].str.strip().str.lower()
)

# ==============================================================================
# [3/6] MERGE FLOOD DATA WITH SHAPEFILE
# ==============================================================================
print("\n[3/6] Merging flood data with shapefile...")
gdf = gdf.merge(
    district_flood[['merge_key', 'cum_flood_ruleA']],
    on='merge_key',
    how='left'
)

n_matched   = gdf['cum_flood_ruleA'].notna().sum()
n_unmatched = gdf['cum_flood_ruleA'].isna().sum()
match_rate  = n_matched / len(gdf)

print(f"  Total GADM districts : {len(gdf)}")
print(f"  Matched              : {n_matched}")
print(f"  Unmatched            : {n_unmatched}")
print(f"  Match rate           : {match_rate:.1%}")

if n_unmatched > 0:
    unmatched_names = gdf.loc[gdf['cum_flood_ruleA'].isna(), ['NAME_2', 'NAME_1']]
    print(f"  Unmatched districts (first 20):")
    for _, row in unmatched_names.head(20).iterrows():
        print(f"    {row['NAME_2']} | {row['NAME_1']}")

assert match_rate >= 0.82, (
    f"Match rate {match_rate:.1%} below 82% floor. "
    "Check district_gadm names in flood_exposure_panel.csv vs GADM NAME_2."
)
print(f"  Match rate assertion (>= 82%) -- PASS")

# ==============================================================================
# [4/6] STATE BOUNDARIES
# ==============================================================================
print("\n[4/6] Dissolving state boundaries...")
state_gdf = gdf[['NAME_1', 'geometry']].dissolve(by='NAME_1').reset_index()
print(f"  States dissolved: {len(state_gdf)} -- PASS")

# ==============================================================================
# [5/6] PLOT
# ==============================================================================
print("\n[5/6] Rendering figure...")

vmax = int(district_flood['cum_flood_ruleA'].max())

# ── Color scheme ──────────────────────────────────────────────────────────────
# Sequential: near-white (no floods) -> deep crimson (high exposure)
# 6 discrete bins. Print-safe. Colorblind-safe.
CMAP_COLORS = [
    '#f7f4ef',   # bin 0: 0 quarters      -- very light warm grey-white
    '#fde0c0',   # bin 1: 1-2 quarters    -- pale peach
    '#f9a96e',   # bin 2: 3-4 quarters    -- soft orange
    '#e96f28',   # bin 3: 5-6 quarters    -- vivid orange
    '#bf3a15',   # bin 4: 7-9 quarters    -- deep red-orange
    '#7a0e0e',   # bin 5: 10+ quarters    -- dark crimson
]
BOUNDS = [0, 1, 3, 5, 7, 10, max(vmax + 1, 11)]
cmap   = ListedColormap(CMAP_COLORS)
norm   = BoundaryNorm(BOUNDS, cmap.N)

# ── Canvas ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.0, 8.5))
ax.set_aspect('equal')
ax.set_axis_off()

# ── Unmatched districts (outside analysis sample) ────────────────────────────
unmatched_mask = gdf['cum_flood_ruleA'].isna()
if unmatched_mask.any():
    gdf[unmatched_mask].plot(
        ax=ax, color='#c8c8c8', edgecolor='white', linewidth=0.05, zorder=1
    )

# ── Flood-exposed districts ───────────────────────────────────────────────────
gdf[~unmatched_mask].plot(
    column='cum_flood_ruleA',
    ax=ax,
    cmap=cmap,
    norm=norm,
    edgecolor='white',
    linewidth=0.05,
    zorder=2,
    missing_kwds={'color': '#f7f4ef', 'edgecolor': 'white', 'linewidth': 0.05},
)

# ── State boundaries on top ───────────────────────────────────────────────────
state_gdf.boundary.plot(
    ax=ax,
    edgecolor='#1a1a1a',
    linewidth=0.55,
    zorder=3,
)

# ── Title ─────────────────────────────────────────────────────────────────────
ax.set_title(
    'Flood Exposure Across Indian Districts, 2015\u20132024',
    fontsize=10, fontweight='normal', loc='left', pad=10,
)

# ── Colorbar ──────────────────────────────────────────────────────────────────
fig.subplots_adjust(left=0.01, right=0.80, top=0.94, bottom=0.09)
cax = fig.add_axes([0.83, 0.20, 0.022, 0.52])

cb = ColorbarBase(
    cax, cmap=cmap, norm=norm, boundaries=BOUNDS,
    ticks=[0.5, 2.0, 4.0, 6.0, 8.5, 10.6],
    orientation='vertical',
)
cb.set_ticklabels(['0', '1\u20132', '3\u20134', '5\u20136', '7\u20139', '10+'])
cb.set_label(
    'Flood-exposed quarters\n(Rule A, cumulative)',
    fontsize=7.5, labelpad=8,
)
cb.ax.tick_params(labelsize=7.5, length=2, width=0.5)
cb.outline.set_linewidth(0.4)

# ── Notes ─────────────────────────────────────────────────────────────────────
fig.text(
    0.01, 0.075,
     'Notes: Each district shaded by cumulative quarters with Rule A flood exposure, '
    '2015Q2\u20132024Q4 (N\u2009=\u2009666 GADM-matched districts; '
    '631 districts in the regression analysis sample after RBI data availability restriction). '
    'Rule A matches EM-DAT flood events to districts by event name and date. '
    'State boundaries from GADM v4.1. '
    'Light grey = districts outside analysis sample (no GADM match).',
    fontsize=6.5, color='#3c3c3c', linespacing=1.6,
    ha='left', va='top', transform=fig.transFigure,
)

# ==============================================================================
# [6/6] SAVE
# ==============================================================================
print("\n[6/6] Saving outputs...")
out_pdf = os.path.join(OUT_DIR, "Fig_01_flood_exposure_map.pdf")
out_png = os.path.join(OUT_DIR, "Fig_01_flood_exposure_map.png")

fig.savefig(out_pdf, format='pdf', bbox_inches='tight')
print(f"  PDF saved: {out_pdf} -- PASS")

fig.savefig(out_png, format='png', dpi=300, bbox_inches='tight')
print(f"  PNG saved: {out_png} -- PASS")

plt.close()

print("\n" + "=" * 70)
print("FIGURE 1 COMPLETE -- fig01_flood_exposure_map.py")
print("=" * 70)