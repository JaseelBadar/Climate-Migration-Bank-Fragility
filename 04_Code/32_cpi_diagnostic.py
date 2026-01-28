import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

log_path = '05_Outputs/Logs/32_cpi_diagnostic_log.txt'
os.makedirs(os.path.dirname(log_path), exist_ok=True)

df = pd.read_csv('03_Data_Clean/regression_panel_final_winsor.csv')
print(f'Loaded {len(df)} obs')

# Extract year from quarter (format: "2015Q1")
df['year'] = df['quarter'].str[:4].astype(int)
print(f'Years: {df["year"].min()} - {df["year"].max()}')

# Nominal growth diagnostic
growth_by_year = df.groupby('year')['deposit_change_qt_winsor'].agg(['mean', 'std', 'count']).round(4)
annualized = (1 + growth_by_year['mean']) ** 4 - 1  # Quarterly to annual
growth_by_year['annualized_pct'] = (annualized * 100).round(2)  # %

print('\nNominal quarterly growth by year:')
print(growth_by_year)

# Mean annualized growth
mean_annualized = growth_by_year['annualized_pct'].mean()
print(f'\nMean annualized growth: {mean_annualized:.1f}%')

# Trend plot
plt.figure(figsize=(10, 6))
plt.plot(growth_by_year.index, growth_by_year['annualized_pct'], marker='o', linewidth=2, markersize=8)
plt.axhline(mean_annualized, color='red', linestyle='--', alpha=0.5, label=f'Mean: {mean_annualized:.1f}%')
plt.title('Annualized Nominal Deposit Growth (%)', fontsize=14, fontweight='bold')
plt.xlabel('Year', fontsize=12)
plt.ylabel('Annualized Growth (%)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('05_Outputs/Figures/32_nominal_growth_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# Decision log: Nominal (no CPI) - disclose limitation
with open(log_path, 'w') as f:
    f.write(f'2026-01-28 Phase 6 Step 2: Nominal growth diagnostic.\n')
    f.write(f'Total obs: {len(df)}\n')
    f.write(f'Mean annualized growth: {mean_annualized:.1f}%\n')
    f.write('Decision: Keep nominal rupees. Disclose: "Deposits in nominal INR; inflation ~6-8% confounds trends."\n\n')
    f.write('Growth summary:\n')
    f.write(growth_by_year.to_string())
    f.write('\n')

print('\nOutput: 05_Outputs/Figures/32_nominal_growth_trend.png')
print('Log: 05_Outputs/Logs/32_cpi_diagnostic_log.txt')
print('DECISION LOGGED: Nominal (no CPI deflation). Ready for H1-H4 re-runs.')