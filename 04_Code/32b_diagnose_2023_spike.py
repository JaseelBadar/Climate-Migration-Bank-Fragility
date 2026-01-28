import pandas as pd
import numpy as np

df = pd.read_csv('03_Data_Clean/regression_panel_final_winsor.csv')
print(f'Loaded {len(df)} obs\n')

# Extract year
df['year'] = df['quarter'].str[:4].astype(int)

# Use 'deposits' column (found in column list)
deposit_col = 'deposits'
print(f'Using deposit column: {deposit_col}\n')

# Check 2022-2024 levels
focus = df[df['year'].isin([2022, 2023, 2024])].copy()

print('=== DEPOSITS LEVELS (Median by Year, Crores INR) ===')
level_check = focus.groupby('year')[deposit_col].agg(['median', 'mean', 'min', 'max', 'count'])
print(level_check)
print()

# Check if 2023 levels are 10x higher (unit error)
median_2022 = focus[focus['year'] == 2022][deposit_col].median()
median_2023 = focus[focus['year'] == 2023][deposit_col].median()
median_2024 = focus[focus['year'] == 2024][deposit_col].median()
print(f'Median deposits: 2022={median_2022:.0f}, 2023={median_2023:.0f}, 2024={median_2024:.0f}')
print(f'2023 vs 2022 ratio: {median_2023/median_2022:.2f}x\n')

# Check deposit_change_qt_winsor distribution
print('=== DEPOSIT CHANGE DISTRIBUTION (2023 vs 2022/2024) ===')
for yr in [2022, 2023, 2024]:
    print(f'\nYear {yr}:')
    print(focus[focus['year'] == yr]['deposit_change_qt_winsor'].describe())

# Sample extreme 2023 changes
print('\n=== TOP 10 EXTREME 2023 CHANGES ===')
extreme_2023 = focus[focus['year'] == 2023].nlargest(10, 'deposit_change_qt_winsor')
print(extreme_2023[['district_gadm', 'quarter', deposit_col, 'deposit_change_qt_winsor']].to_string())
print()

# Check if specific districts driving spike
print('=== 2023 HIGH-GROWTH DISTRICTS (>50% quarterly growth) ===')
high_growth = focus[(focus['year'] == 2023) & (focus['deposit_change_qt_winsor'] > 0.5)]
print(f'Count: {len(high_growth)} district-quarters')
if len(high_growth) > 0:
    print(high_growth[['district_gadm', 'quarter', deposit_col, 'deposit_change_qt_winsor']].head(20).to_string())
print()

# CONCLUSION
print('=== DIAGNOSTIC CONCLUSION ===')
if median_2023 / median_2022 > 5:
    print('❌ UNIT ERROR: 2023 deposit levels are 5x+ higher → RBI file unit mismatch')
elif len(high_growth) > 1000:
    print('❌ SYSTEMIC SPIKE: >1000 districts show >50% growth in 2023 → data corruption')
elif len(high_growth) > 100:
    print('⚠️  WIDESPREAD ANOMALY: 100+ districts show >50% growth in 2023 → investigate raw RBI file')
else:
    print(f'✓ OUTLIER-DRIVEN: Only {len(high_growth)} extreme cases → winsorization worked, but re-check threshold')